import serial
import speech_recognition as sr
import google.generativeai as genai
import pywhatkit
import pyjokes
import os
from datetime import datetime
import sys
import tkinter as tk
import pyttsx3  # Use pyttsx3 for TTS

# I NAMED MY PYTHON ALPHA
AI_NAME = "Alpha"

# I ACTIVATED pyttsx3 engine
engine = pyttsx3.init()

def speak(text: str) -> None:
    engine.say(text)
    engine.runAndWait()

# Configure Gemini AI with your API key
genai.configure(api_key='AIzaSyD-hewkWJnp4BJ3vuYHEnDTp5fW1VxpYDI')

# I initialized the gemini model ie Gemini 2.5 Pro
model = genai.GenerativeModel(model_name="models/gemini-2.5-pro")

def get_date() -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f"The current time is {now}")
    return now

def open_app(app_name: str) -> None:
    app_name_lower = app_name.lower()
    if 'chrome' in app_name_lower:
        os.system('start chrome')
    elif 'visual studio code' in app_name_lower or 'vscode' in app_name_lower:
        os.system('code')
    elif 'whatsapp' in app_name_lower:
        os.system('start whatsapp')
    else:
        speak(f"Sorry, {AI_NAME} couldn't find that app.")

def play_music(song_name: str) -> None:
    speak(f"Playing {song_name} on YouTube")
    pywhatkit.playonyt(song_name)

def tell_joke() -> None:
    joke = pyjokes.get_joke()
    speak(joke)

def listen_for_command() -> str:
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        recognizer.pause_threshold = 1.0
        status_label.config(text="🎤 Listening...", fg="#ffb86b")
        root.update()
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=8)
            command = recognizer.recognize_google(audio).lower()
            status_label.config(text=f"✅ You said: {command}", fg="#50fa7b")
            root.update()
            return command
        except sr.UnknownValueError:
            speak(f"{AI_NAME} couldn't understand. Please repeat your command.")
            status_label.config(text="❌ Could not understand audio", fg="#ff5555")
            root.update()
            return ""
        except sr.RequestError:
            speak(f"{AI_NAME} couldn't request results.")
            status_label.config(text="❌ Could not request results", fg="#ff5555")
            root.update()
            return ""
        except sr.WaitTimeoutError:
            speak(f"{AI_NAME} listening timed out.")
            status_label.config(text="❌ Listening timed out", fg="#ff5555")
            root.update()
            return ""

def connect_arduino(port: str = 'COM6', baudrate: int = 9600):
    try:
        return serial.Serial(port, baudrate, timeout=1)
    except serial.SerialException:
        speak(f"{AI_NAME} could not connect to Arduino. Arduino is disconnected")
        return None

arduino = connect_arduino()

def process_command(command: str) -> None:
    if not command:
        return

    if "exit" in command or "stop" in command:
        speak(f"{AI_NAME} is Shutting down.")
        status_label.config(text="🛑 Exiting...", fg="#ff5555")
        if arduino:
            arduino.close()
        root.after(1000, root.destroy)
        sys.exit()

    elif "light" in command:
        if "on" in command:
            if arduino:
                arduino.write(b'LIGHTS_ON\n')
            speak(f"turning lights on.")
            status_label.config(text="💡 Sent: LIGHTS_ON", fg="#f1fa8c")
        elif "off" in command:
            if arduino:
                arduino.write(b'LIGHTS_OFF\n')
            speak(f"turning lights off.")
            status_label.config(text="💡 Sent: LIGHTS_OFF", fg="#f1fa8c")

    elif "switch" in command or "charge" in command:
        if "on" in command:
            if arduino:
                arduino.write(b'SWITCH_ON\n')
            speak(f"turning switch on.")
            status_label.config(text="🔌 Sent: SWITCH_ON", fg="#8be9fd")
        elif "off" in command:
            if arduino:
                arduino.write(b'SWITCH_OFF\n')
            speak(f"turning switch off.")
            status_label.config(text="🔌 Sent: SWITCH_OFF", fg="#8be9fd")

    elif "everything" in command:
        if "on" in command:
            if arduino:
                arduino.write(b'EVERYTHING_ON\n')
            speak(f"turning everything on.")
            status_label.config(text="✅ Sent: EVERYTHING_ON", fg="#f1fa8c")
        elif "off" in command:
            if arduino:
                arduino.write(b'EVERYTHING_OFF\n')
            speak(f"turning everything off.")
            status_label.config(text="✅ Sent: EVERYTHING_OFF", fg="#f1fa8c")
    elif "joke" in command:
        tell_joke()

    elif "time" in command or "date" in command:
        get_date()

    elif "play" in command:
        song = command.replace("play", "").strip()
        if song:
            play_music(song)
        else:
            speak(f"Please specify the song name to play, {AI_NAME}.")

    elif "open" in command:
        app = command.replace("open", "").strip()
        if app:
            open_app(app)
        else:
            speak(f"Please specify the app name, {AI_NAME}.")

    else:
        # Unknown command: Use Gemini AI to answer with AI name included
        try:
            response = model.generate_content(f"You are a helpful assistant named {AI_NAME}. Respond to: {command}")
            reply = response.text.strip()
        except Exception as e:
            reply = f"Sorry, {AI_NAME} couldn't process that right now."
            print(f"Error in AI call: {e}")
        speak(reply)
        status_label.config(text=f"🤖 {AI_NAME}: {reply}", fg="#00bfff")

def on_speak() -> None:
    status_label.config(text="Say your command...", fg="#b8c1ec")
    root.update()
    cmd = listen_for_command()
    if cmd:
        process_command(cmd)

# --- GUI Setup ---
root = tk.Tk()
root.title(f"{AI_NAME} AI")
root.geometry("700x700")
root.configure(bg="#232946")

main_frame = tk.Frame(root, bg="#232946", bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

title_label = tk.Label(main_frame, text=f"{AI_NAME} AI", font=("Segoe UI", 20, "bold"), bg="#232946", fg="#eebbc3")
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
    cursor="hand2"
)
speak_button.pack(pady=25)

status_label = tk.Label(main_frame, text=f"Press 'Speak' and say your command.", font=("Segoe UI", 12), bg="#232946", fg="#b8c1ec", wraplength=420, justify="center")
status_label.pack(pady=(10, 0))

footer = tk.Label(root, text=f"{AI_NAME} AI", font=("Segoe UI", 9), bg="#232946", fg="#b8c1ec")
footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

def on_enter(e: tk.Event) -> None:
    speak_button.config(bg="#f1fa8c", fg="#232946")

def on_leave(e: tk.Event) -> None:
    speak_button.config(bg="#eebbc3", fg="#232946")

speak_button.bind("<Enter>", on_enter)
speak_button.bind("<Leave>", on_leave)

def on_closing() -> None:
    if arduino:
        try:
            arduino.close()
        except Exception:
            pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

# Greet user on start
speak(f"{AI_NAME} is online!!!")

root.mainloop()
