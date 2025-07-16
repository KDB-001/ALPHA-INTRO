import serial
import serial.tools.list_ports
import speech_recognition as sr
import time
import pyttsx3
import sys
import threading
from playsound import playsound
import tkinter as tk
import os

# === Absolute path to sound folder ===
BASE_AUDIO_PATH = r"C:\Users\Administrator\Desktop\IT\my project\alphas voice"

def play_audio(filename):
    path = os.path.join(BASE_AUDIO_PATH, filename)
    playsound(path)

# Global state
arduino = None
was_connected = False
continuous_mode = False
background_thread = None

# TTS setup
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def update_status(message, color):
    status_label.config(text=message, fg=color)
    root.update()

def find_arduino_port():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Arduino" in port.description or "USB-SERIAL" in port.description or "CH340" in port.description:
            return port.device
    return None

def try_connect_arduino():
    global arduino, was_connected
    while True:
        if arduino is not None:
            try:
                _ = arduino.in_waiting
            except (serial.SerialException, OSError):
                if was_connected:
                    play_audio('arduino_has_been_disconnected.wav')
                    update_status("❌ Arduino disconnected.", "#ff5555")
                    was_connected = False
                arduino = None

        if arduino is None:
            try:
                port = find_arduino_port()
                if port:
                    arduino = serial.Serial(port, 9600, timeout=1)
                    play_audio("arduino_is_connected.wav")
                    update_status(f"✅ Arduino connected on {port}", "#50fa7b")
                    was_connected = True
            except serial.SerialException:
                if was_connected:
                    play_audio("arduino_is_disconnected.wav")
                    update_status("❌ Arduino not connected.", "#ff5555")
                    was_connected = False
                arduino = None
        time.sleep(5)

def listen_once():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        update_status("🎤 Listening...", "#ffb86b")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
            command = recognizer.recognize_google(audio).lower()
            update_status(f"✅ You said: {command}", "#50fa7b")
            process_command(command)
        except sr.WaitTimeoutError:
            update_status("⌛ Listening timed out", "#ffb86b")
            play_audio("timed_out.wav")
        except sr.UnknownValueError:
            update_status("❌ Could not understand audio", "#ff5555")
            play_audio("please_repeat_your_command.wav")
        except sr.RequestError:
            update_status("❌ Could not request results", "#ff5555")
            play_audio("could_not_connect_to_speech_service.wav")
        except Exception as e:
            update_status("❌ Error during recognition", "#ff5555")
            print(e)

def listen_continuous():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while continuous_mode:
            try:
                update_status("🎧 Continuous Listening...", "#ffb86b")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
                command = recognizer.recognize_google(audio).lower()
                update_status(f"✅ You said: {command}", "#50fa7b")
                process_command(command)
            except sr.UnknownValueError:
                update_status("❌ Could not understand audio", "#ff5555")
            except sr.RequestError:
                update_status("❌ Could not request results", "#ff5555")
            except sr.WaitTimeoutError:
                update_status("⌛ Listening timed out", "#ffb86b")
            except OSError:
                update_status("❌ Microphone Error", "#ff5555")
                play_audio("microphone_error.wav")
                break

def start_continuous():
    global continuous_mode, background_thread
    if not continuous_mode:
        continuous_mode = True
        background_thread = threading.Thread(target=listen_continuous, daemon=True)
        background_thread.start()
        play_audio("continous_listenining_activated.wav")
        update_status("🎧 Continuous mode is ON", "#8be9fd")

def stop_continuous():
    global continuous_mode
    if continuous_mode:
        continuous_mode = False
        play_audio("continous_listenining_deactivated.wav")
        update_status("🛑 Continuous mode is OFF", "#ff5555")

def process_command(command):
    with open("alpha_log.txt", "a") as f:
        f.write(f"{time.ctime()} - {command}\n")

    if "start continuous" in command or "activate continuous" in command or "enable background" in command:
        start_continuous()
    elif "stop continuous" in command or "deactivate continuous" in command or "disable background" in command:
        stop_continuous()
    elif "your name" in command or "who are you" in command:
        play_audio("my_name_is_alpha2.wav")
        update_status("🤖 My name is Alpha, What can I do for you?", "#8be9fd")
    elif any(phrase in command for phrase in ["stop", "exit", "shut down", "shutdown", "terminate", "power off"]):
        play_audio("alpha_is_shutting_down.wav")
        update_status("🛑 Program stopped by user command.", "#ff5555")
        try:
            if arduino:
                arduino.close()
        except:
            pass
        root.after(1000, root.destroy)
        sys.exit()
    elif "on" in command and "light" in command:
        if arduino and arduino.is_open:
            arduino.write(b'LIGHTS_ON\n')
            play_audio("turning_lights_on.wav")
            update_status("💡 Sent: LIGHTS_ON", "#f1fa8c")
    elif "on" in command and "everything" in command:
        if arduino and arduino.is_open:
            arduino.write(b'EVERYTHING_ON\n')
            play_audio("everything_is_on.wav")
            update_status("💡 Sent: EVERYTHING_ON", "#f1fa8c")
    elif "off" in command and "everything" in command:
        if arduino and arduino.is_open:
            arduino.write(b'EVERYTHING_OFF\n')
            play_audio("everything_is_off.wav")
            update_status("💡 Sent: EVERYTHING_OFF", "#f1fa8c")
    elif "off" in command and "light" in command:
        if arduino and arduino.is_open:
            arduino.write(b'LIGHTS_OFF\n')
            play_audio("turning_lights_off.wav")
            update_status("💡 Sent: LIGHTS_OFF", "#f1fa8c")
    elif "on" in command and "switch" in command:
        if arduino and arduino.is_open:
            arduino.write(b'SWITCH_ON\n')
            play_audio("turning_switch_on.wav")
            update_status("🔌 Sent: SWITCH_ON", "#8be9fd")
    elif "off" in command and "switch" in command:
        if arduino and arduino.is_open:
            arduino.write(b'SWITCH_OFF\n')
            play_audio("turning_switch_off.wav")
            update_status("🔌 Sent: SWITCH_OFF", "#8be9fd")
    else:
        play_audio("no_valid_command_found.wav")
        update_status("❓ No valid command found.", "#ff5555")

# === GUI SETUP
root = tk.Tk()
root.title("Alpha Voice Controller")
root.geometry("440x360")
root.configure(bg="#0f0f0f")

main_frame = tk.Frame(root, bg="#0f0f0f", bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=320)

title_label = tk.Label(
    main_frame,
    text="ALPHA Voice Controller",
    font=("Segoe UI", 20, "bold"),
    bg="#0f0f0f",
    fg="#00ffff"
)
title_label.pack(pady=(25, 10))

speak_button = tk.Button(
    main_frame,
    text="🎤 Speak",
    font=("Segoe UI", 16, "bold"),
    bg="#1a1a1a",
    fg="#00ffcc",
    activebackground="#00ffaa",
    activeforeground="#0f0f0f",
    command=listen_once,
    relief="flat",
    bd=0,
    width=14,
    height=2,
    cursor="hand2",
    highlightthickness=0
)
speak_button.pack(pady=25)

status_label = tk.Label(
    main_frame,
    text="Initializing Alpha...",
    font=("Segoe UI", 12),
    bg="#0f0f0f",
    fg="#e6e6e6",
    wraplength=350,
    justify="center"
)
status_label.pack(pady=(10, 0))

footer = tk.Label(
    root,
    text="ALPHA VOICE CONTROL SYSTEM",
    font=("Segoe UI", 9),
    bg="#0f0f0f",
    fg="#00ffcc"
)
footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

def on_enter(e):
    speak_button.config(bg="#00ffaa", fg="#0f0f0f")

def on_leave(e):
    speak_button.config(bg="#1a1a1a", fg="#00ffcc")

speak_button.bind("<Enter>", on_enter)
speak_button.bind("<Leave>", on_leave)

# Arduino check at startup
startup_port = find_arduino_port()
if startup_port:
    try:
        arduino = serial.Serial(startup_port, 9600, timeout=1)
        was_connected = True
        play_audio("alpha_is_online.wav")
        update_status(f"✅ Arduino connected on {startup_port}", "#50fa7b")
    except serial.SerialException:
        play_audio("arduino_is_detected_but_could_not_connect.wav")
        update_status("⚠️ Arduino detected but failed to connect.", "#ffb86b")
else:
    play_audio("arduino_is_not_connected.wav")
    update_status("❌ Arduino not connected.", "#ff5555")

# Reconnection thread
threading.Thread(target=try_connect_arduino, daemon=True).start()

def on_closing():
    global continuous_mode
    continuous_mode = False
    try:
        if arduino:
            arduino.close()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
