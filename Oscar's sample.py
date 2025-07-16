import serial
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import pywhatkit
import pyjokes
import os 
from datetime import datetime
import sys 
import tkinter as tk

genai.configure(api_key = 'AIzaSyD-hewkWJnp4BJ3vuYHEnDTp5fW1VxpYDI')
model = genai.GenerativeModel(model_name='gemini-pro')

engine = pyttsx3.init()
def speak(text):
    engine.say(text)
    engine.runAndWait()

def get_date():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    speak(f'The current time is {current_time}') 
    return current_time   

def open_app(app_name):
    if 'chrome' in app_name:
        os.system('start chrome')
    elif 'visual studio code' in app_name:
        os.system('visual studio code')  
    elif  'whatsapp' in app_name:
        os.system('whatsapp')
    else:
        speak("Sorry,I couldn't find that app.")

def play_music(song_name):
    speak(f'Playing {song_name} on YouTube')
    pywhatkit.playonyt(song_name)

def tell_joke():
    joke = pyjokes.get_joke()
    speak(joke)

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
    
arduino = serial.Serial('COM7',9600, timeout=1)
# Process command intelligently
def process_command(command):
    if "exit" in command:
        speak("Shutting down.")
        status_label.config(text="🛑 Exiting...", fg="#ff5555")
        arduino.close()
        root.after(1000, root.destroy)
        sys.exit()

    elif "light" in command:
        if "on" in command:
            arduino.write(b'LIGHTS_ON\n')
            speak("Lights on.")
            status_label.config(text="💡 Sent: LIGHTS_ON", fg="#f1fa8c")
        elif "off" in command:
            arduino.write(b'LIGHTS_OFF\n')
            speak("Lights off.")
            status_label.config(text="💡 Sent: LIGHTS_OFF", fg="#f1fa8c")

    elif "switch" in command or "charge" in command:
        if "on" in command:
            arduino.write(b'SWITCH_ON\n')
            speak("Switch on.")
            status_label.config(text="🔌 Sent: SWITCH_ON", fg="#8be9fd")
        elif "off" in command:
            arduino.write(b'SWITCH_OFF\n')
            speak("Switch off.")
            status_label.config(text="🔌 Sent: SWITCH_OFF", fg="#8be9fd")

    elif "everything on" in command:
        arduino.write(b'EVERYTHING_ON\n')
        speak("Everything on.")
        status_label.config(text="✅ Sent: EVERYTHING_ON", fg="#f1fa8c")

    elif "everything off" in command:
        arduino.write(b'EVERYTHING_OFF\n')
        speak("Turning everything off.")
        status_label.config(text="✅ Sent: EVERYTHING_OFF", fg="#f1fa8c")

    elif "joke" in command:
        tell_joke()

    elif "time" in command:
        speak(get_date())

    elif "play" in command:
        song = command.replace("play", "").strip()
        play_music(song)

    elif "open" in command:
        app = command.replace("open", "").strip()
        open_app(app)
    else:
        # Unknown: Ask Gemini
        response = model.generate_content(f"You are a helpful assistant. Respond to: {command}")
        reply = response.text.strip()
        speak(reply)
        status_label.config(text=f"🤖 Alpha: {reply}", fg="#00bfff")

# GUI + Voice button
def on_speak():
    status_label.config(text="Say your command...", fg="#b8c1ec")
    root.update()
    cmd = listen_for_command()
    if cmd:
        process_command(cmd)

# --- GUI ---
root = tk.Tk()
root.title("ALPHA AI")
root.geometry("500x400")
root.configure(bg="#232946")

main_frame = tk.Frame(root, bg="#232946", bd=2, relief="groove")
main_frame.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

title_label = tk.Label(main_frame, text="ALPHA AI", font=("Segoe UI", 20, "bold"), bg="#232946", fg="#eebbc3")
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

status_label = tk.Label(main_frame, text="Press 'Speak' and say your command.", font=("Segoe UI", 12), bg="#232946", fg="#b8c1ec", wraplength=350, justify="center")
status_label.pack(pady=(10, 0))

footer = tk.Label(root, text="Smart Home + Gemini AI", font=("Segoe UI", 9), bg="#232946", fg="#b8c1ec")
footer.place(relx=1.0, rely=1.0, anchor="se", x=-10, y=-5)

def on_enter(e): speak_button.config(bg="#f1fa8c", fg="#232946")
def on_leave(e): speak_button.config(bg="#eebbc3", fg="#232946")

speak_button.bind("<Enter>", on_enter)
speak_button.bind("<Leave>", on_leave)

def on_closing():
    try: arduino.close()
    except: pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()