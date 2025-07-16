import serial
import speech_recognition as sr
import time
import pyttsx3
import sys
import tkinter as tk
from tkinter import ttk

# Set up serial connection to Arduino
arduino = serial.Serial('COM6', 9600, timeout=1)

# Set up text-to-speech engine
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen_for_command():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 1.0
        status_label.config(text="🎤 Listening...", fg="#ffb86b")
        root.update()
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
    try:
        command = recognizer.recognize_google(audio).lower()
        status_label.config(text=f"✅ You said: {command}", fg="#50fa7b")
        root.update()
        return command
    except sr.UnknownValueError:
        speak("Please repeat your command.")
        status_label.config(text="❌ Could not understand audio", fg="#ff5555")
        root.update()
        return ""
    except sr.RequestError:
        speak("Could not request results.")
        status_label.config(text="❌ Could not request results", fg="#ff5555")
        root.update()
        return ""
    except sr.WaitTimeoutError:
        status_label.config(text="❌ Listening timed out", fg="#ff5555")
        speak("Listening timed out.")
        return ""


def process_command(command):
    if "stop" in command or "exit" in command:
        speak("Shutting down the system.")
        status_label.config(text="🛑 Program stopped by user command.", fg="#ff5555")
        arduino.close()
        root.after(1000, root.destroy)
        sys.exit()

    elif "on" in command and "light" in command:
        arduino.write(b'LIGHTS_ON\n')
        speak("Turning lights on.")
        status_label.config(text="💡 Sent: LIGHTS_ON", fg="#f1fa8c")

    elif "on" in command and "everything" in command:
        arduino.write(b'EVERYTHING_ON\n')
        speak("Everything is on.")
        status_label.config(text="💡 Sent: LIGHTS_ON and SWITCH_ON", fg="#f1fa8c")

    elif "off" in command and "everything" in command:
        arduino.write(b'EVERYTHING_OFF\n')
        speak("Everything is off.")
        status_label.config(text="💡 Sent: LIGHTS_OFF and SWITCH_OFF", fg="#f1fa8c")

    elif "off" in command and "light" in command:
        arduino.write(b'LIGHTS_OFF\n')
        speak("Turning lights off.")
        status_label.config(text="💡 Sent: LIGHTS_OFF", fg="#f1fa8c")

    elif "on" in command and "switch" in command:
        arduino.write(b'SWITCH_ON\n')
        speak("Turning switch on.")
        status_label.config(text="🔌 Sent: SWITCH_ON", fg="#8be9fd")

    elif "off" in command and "switch" in command:
        arduino.write(b'SWITCH_OFF\n')
        speak("Turning switch off.")
        status_label.config(text="🔌 Sent: SWITCH_OFF", fg="#8be9fd")

    else:
        speak("No valid command found.")
        status_label.config(text="❓ No valid command found.", fg="#ff5555")

def on_speak():
    status_label.config(text="Say your command...", fg="#b8c1ec")
    root.update()
    cmd = listen_for_command()
    if cmd:
        process_command(cmd)

# --- GUI Setup ---
root = tk.Tk()
root.title("Voice Command Arduino Controller")
root.geometry("440x360")
root.configure(bg="#232946")

# Add a frame for rounded corners and shadow effect
main_frame = tk.Frame(root, bg="#232946", bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=400, height=320)

title_label = tk.Label(main_frame, text="ALPHA Voice Controller", font=("Segoe UI", 20, "bold"), bg="#232946", fg="#eebbc3")
title_label.pack(pady=(25, 10))

speak_button = tk.Button(
    main_frame,
    text="🎤 Speak",
    font=("Segoe UI", 16, "bold"),
    bg="#eebbc3",
    fg="#232946",
    activebackground="#b8c1ec",
    activeforeground="#232946",
    command=on_speak,
    relief="flat",
    bd=0,
    width=14,
    height=2,
    cursor="hand2",
    highlightthickness=0
)
speak_button.pack(pady=25)

status_label = tk.Label(main_frame, text="Press 'Speak' and say your command.", font=("Segoe UI", 12), bg="#232946", fg="#b8c1ec", wraplength=350, justify="center")
status_label.pack(pady=(10, 0))

# Add a subtle footer
footer = tk.Label(root, text="ALPHA VOICE CONTROL", font=("Segoe UI", 9), bg="#232946", fg="#b8c1ec")
footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

def on_enter(e):
    speak_button.config(bg="#f1fa8c", fg="#232946")

def on_leave(e):
    speak_button.config(bg="#eebbc3", fg="#232946")

speak_button.bind("<Enter>", on_enter)
speak_button.bind("<Leave>", on_leave)

def on_closing():
    try:
        arduino.close()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()