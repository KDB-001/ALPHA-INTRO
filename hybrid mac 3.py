import serial
import serial.tools.list_ports
import speech_recognition as sr
import google.generativeai as genai
import pywhatkit
import pyjokes
import os
import time
from datetime import datetime
import sys
import threading
import tkinter as tk
import pyttsx3

# Global
AI_NAME = "Alpha"
arduino = None
was_connected = False
continuous_mode = False
background_thread = None

# TTS - Persistent global engine
engine = pyttsx3.init()
engine.setProperty("rate", 175)
tts_thread = None
tts_interrupted = False

def speak(text: str):
    global tts_thread, tts_interrupted, engine

    def run():
        global tts_interrupted
        try:
            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            pass

    if tts_thread and tts_thread.is_alive():
        tts_interrupted = True
        try:
            engine.stop()
        except:
            pass
        time.sleep(0.2)

    tts_interrupted = False
    tts_thread = threading.Thread(target=run, daemon=True)
    tts_thread.start()

# Gemini AI
genai.configure(api_key='AIzaSyD-hewkWJnp4BJ3vuYHEnDTp5fW1VxpYDI')
model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")

# Utilities
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
                    speak("Arduino has been disconnected.")
                    update_status("❌ Arduino disconnected.", "red")
                    was_connected = False
                arduino = None

        if arduino is None:
            try:
                port = find_arduino_port()
                if port:
                    arduino = serial.Serial(port, 9600, timeout=1)
                    speak(f"Arduino connected on {port}.")
                    update_status(f"✅ Arduino connected on {port}", "spring green")
                    was_connected = True
            except serial.SerialException:
                if was_connected:
                    speak("Arduino is disconnected.")
                    update_status("❌ Arduino not connected.", "red")
                    was_connected = False
                arduino = None
        time.sleep(5)

# GUI Updater
def update_status(message, color):
    status_label.config(text=message, fg=color)
    root.update()

# Command Actions
def get_date():
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"The current time is {now}")
    return now

def open_app(app_name):
    app = app_name.lower()
    if 'chrome' in app:
        os.system('start chrome')
    elif 'visual studio code' in app or 'vscode' in app:
        os.system('code')
    elif 'whatsapp' in app:
        os.system('start whatsapp')
    else:
        speak(f"Sorry, {AI_NAME} couldn't find that app.")

def play_music(song_name):
    speak(f"Playing {song_name} on YouTube")
    pywhatkit.playonyt(song_name)

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

# Voice
def listen_once():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        update_status("🎤 Listening...", "orange")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
            command = recognizer.recognize_google(audio).lower()
            update_status(f"✅ You said: {command}", "spring green")
            process_command(command)
        except sr.WaitTimeoutError:
            update_status("⌛ Listening timed out", "orange")
            speak("Listening timed out.")
        except sr.UnknownValueError:
            update_status("❌ Could not understand audio", "red")
            speak("Please repeat your command.")
        except sr.RequestError:
            update_status("❌ Could not request results", "red")
            speak("Could not connect to speech service.")
        except Exception as e:
            update_status("❌ Error during recognition", "red")
            print(e)

def interrupt_and_listen():
    global tts_thread, tts_interrupted

    if tts_thread and tts_thread.is_alive():
        tts_interrupted = True
        try:
            engine.stop()
        except:
            pass
        update_status("⏹ Speech interrupted. Listening again...", "orange")
        time.sleep(0.2)

    listen_once()

def listen_continuous():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        while continuous_mode:
            try:
                update_status("🎧 Continuous Listening...", "orange")
                audio = recognizer.listen(source, timeout=10, phrase_time_limit=6)
                command = recognizer.recognize_google(audio).lower()
                update_status(f"✅ You said: {command}", "spring green")
                process_command(command)
            except sr.UnknownValueError:
                update_status("❌ Could not understand audio", "red")
            except sr.RequestError:
                update_status("❌ Could not request results", "red")
            except sr.WaitTimeoutError:
                update_status("⌛ Listening timed out", "orange")
            except OSError:
                update_status("❌ Microphone Error", "red")
                speak("Microphone error")
                break

def start_continuous():
    global continuous_mode, background_thread
    if not continuous_mode:
        continuous_mode = True
        background_thread = threading.Thread(target=listen_continuous, daemon=True)
        background_thread.start()
        speak("Continuous listening activated.")
        update_status("🎧 Continuous mode is ON", "light cyan")

def stop_continuous():
    global continuous_mode
    if continuous_mode:
        continuous_mode = False
        speak("Continuous listening deactivated.")
        update_status("🛑 Continuous mode is OFF", "red")

# Command Handling
def process_command(command):
    with open("alpha_log.txt", "a") as f:
        f.write(f"{time.ctime()} - {command}\n")

    if "start continuous" in command:
        start_continuous()
    elif "stop continuous" in command:
        stop_continuous()
    elif "your name" in command or "who are you" in command:
        speak(f"My name is {AI_NAME}. I am your voice assistant.")
        update_status(f"🤖 My name is {AI_NAME}", "light cyan")
    elif any(word in command for word in ["exit", "stop", "shutdown", "terminate"]):
        speak(f"{AI_NAME} is shutting down.")
        update_status("🛑 Exiting...", "red")
        try:
            if arduino:
                arduino.close()
        except:
            pass
        root.after(1000, root.destroy)
        sys.exit()
    elif "light" in command:
        if "on" in command:
            if arduino and arduino.is_open:
                arduino.write(b'LIGHTS_ON\n')
            speak("Turning lights on.")
            update_status("💡 Sent: LIGHTS_ON", "light yellow")
        elif "off" in command:
            if arduino and arduino.is_open:
                arduino.write(b'LIGHTS_OFF\n')
            speak("Turning lights off.")
            update_status("💡 Sent: LIGHTS_OFF", "light yellow")
    elif "switch" in command or "charge" in command:
        if "on" in command:
            if arduino and arduino.is_open:
                arduino.write(b'SWITCH_ON\n')
            speak("Turning switch on.")
            update_status("🔌 Sent: SWITCH_ON", "light cyan")
        elif "off" in command:
            if arduino and arduino.is_open:
                arduino.write(b'SWITCH_OFF\n')
            speak("Turning switch off.")
            update_status("🔌 Sent: SWITCH_OFF", "light cyan")
    elif "everything" in command:
        if "on" in command:
            if arduino and arduino.is_open:
                arduino.write(b'EVERYTHING_ON\n')
            speak("Turning everything on.")
            update_status("✅ Sent: EVERYTHING_ON", "light yellow")
        elif "off" in command:
            if arduino and arduino.is_open:
                arduino.write(b'EVERYTHING_OFF\n')
            speak("Turning everything off.")
            update_status("✅ Sent: EVERYTHING_OFF", "light yellow")
    elif "joke" in command:
        tell_joke()
    elif "time" in command or "date" in command:
        get_date()
    elif "play" in command:
        song = command.replace("play", "").strip()
        if song:
            play_music(song)
        else:
            speak("Please specify a song.")
    elif "open" in command:
        app = command.replace("open", "").strip()
        if app:
            open_app(app)
        else:
            speak("Please specify the app.")
    else:
        try:
            response = model.generate_content(f"You are a helpful assistant named {AI_NAME}. Respond to: {command}")
            reply = response.text.strip()
        except Exception as e:
            reply = f"Sorry, {AI_NAME} couldn't process that right now."
            print(f"Gemini error: {e}")
        speak(reply)
        update_status(f"🤖 {AI_NAME}: {reply}", "#00bfff")

# GUI Setup
root = tk.Tk()
root.title(f"{AI_NAME} Voice Controller")
root.geometry("700x600")
root.configure(bg="midnight blue")

main_frame = tk.Frame(root, bg="midnight blue", bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

title_label = tk.Label(main_frame, text=f"{AI_NAME} Voice Controller", font=("Segoe UI", 20, "bold"), bg="midnight blue", fg="light pink")
title_label.pack(pady=(25, 10))

speak_button = tk.Button(
    main_frame,
    text="🎤 Speak",
    font=("Segoe UI", 16, "bold"),
    bg="light pink",
    fg="midnight blue",
    activebackground="light steel blue",
    activeforeground="midnight blue",
    command=interrupt_and_listen,
    relief="flat",
    bd=0,
    width=14,
    height=2,
    cursor="hand2"
)
speak_button.pack(pady=25)

status_label = tk.Label(main_frame, text="Starting system...", font=("Segoe UI", 12), bg="midnight blue", fg="light steel blue", wraplength=350, justify="center")
status_label.pack(pady=(10, 0))

footer = tk.Label(root, text=f"{AI_NAME} Voice Control", font=("Segoe UI", 9), bg="midnight blue", fg="light steel blue")
footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

def on_enter(e):
    speak_button.config(bg="light yellow", fg="midnight blue")

def on_leave(e):
    speak_button.config(bg="light pink", fg="midnight blue")

speak_button.bind("<Enter>", on_enter)
speak_button.bind("<Leave>", on_leave)

# Startup Arduino check
startup_port = find_arduino_port()
if startup_port:
    try:
        arduino = serial.Serial(startup_port, 9600, timeout=1)
        was_connected = True
        speak(f"{AI_NAME} is online. Arduino is connected on {startup_port}.")
        update_status(f"✅ Arduino connected on {startup_port}", "spring green")
    except serial.SerialException:
        speak(f"{AI_NAME} is online. Arduino is detected but could not connect.")
        update_status("⚠️ Arduino detected but failed to connect.", "orange")
else:
    speak(f"{AI_NAME} is online. Arduino is not connected.")
    update_status("❌ Arduino not connected.", "red")

# Background reconnect thread
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
