import tkinter as tk
from tkinter import scrolledtext
import pyttsx3
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pickle
import json
import datetime
import webbrowser
import wikipedia
import re
import requests


# ------------------ Load ML Model ------------------
with open("intent_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

with open("intents.json", "r") as f:
    INTENTS = json.load(f)

# ------------------ Text to Speech ------------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    chat_box.insert(tk.END, "Jarvis: " + text + "\n")
    chat_box.yview(tk.END)
    engine.say(text)
    engine.runAndWait()


# ------------------ Voice Input ------------------
recognizer = sr.Recognizer()

def listen_voice():
    try:
        duration = 4  # seconds
        sample_rate = 16000
        speak("Listening...")

        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()

        temp = "temp_voice.wav"
        sf.write(temp, recording, sample_rate)

        with sr.AudioFile(temp) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        chat_box.insert(tk.END, "You: " + text + "\n")
        chat_box.yview(tk.END)

        process_input(text.lower())

    except:
        speak("Sorry, I couldn't understand. Please try again.")


# ------------------ Predict Intent ------------------
def predict_intent(text):
    X = vectorizer.transform([text])
    return model.predict(X)[0]

# ------------------ Actions ------------------
def tell_time():
    return datetime.datetime.now().strftime("The time is %I:%M %p")

def tell_date():
    return datetime.date.today().strftime("Today is %A, %d %B %Y")

def open_yt():
    webbrowser.open("https://youtube.com")
    return "Opening YouTube"

def open_google():
    webbrowser.open("https://google.com")
    return "Opening Google"

def google_search(text):
    query = text.replace("google", "").replace("search", "").strip()
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return "Searching Google for " + query

def youtube_search(text):
    query = text.replace("youtube", "").replace("search", "").strip()
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return "Searching YouTube for " + query

def wiki_search(text):
    try:
        text = re.sub(r"(who is|what is|tell me about)", "", text).strip()
        return wikipedia.summary(text, sentences=2)
    except:
        return "Wikipedia has no results."

def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current_weather=true"
        data = requests.get(url).json()
        temp = data["current_weather"]["temperature"]
        wind = data["current_weather"]["windspeed"]
        return f"The temperature is {temp}°C and wind speed is {wind} km/h."
    except:
        return "Unable to fetch weather."

# ------------------ Process Input ------------------
def process_input(user_text):
    intent = predict_intent(user_text)

    if intent == "greet":
        speak("Hello Sai, how can I help you?")
    elif intent == "time":
        speak(tell_time())
    elif intent == "date":
        speak(tell_date())
    elif intent == "open_youtube":
        speak(open_yt())
    elif intent == "open_google":
        speak(open_google())
    elif intent == "google_search":
        speak(google_search(user_text))
    elif intent == "youtube_search":
        speak(youtube_search(user_text))
    elif intent == "wikipedia_search":
        speak(wiki_search(user_text))
    elif intent == "weather":
        speak(get_weather())
    elif intent == "goodbye":
        speak("Goodbye Sai!")
        window.destroy()
    else:
        speak("I am still learning. Please repeat.")



# ------------------ GUI Setup ------------------
window = tk.Tk()
window.title("Jarvis AI Assistant - GUI Version")
window.geometry("600x700")
window.configure(bg="#101820")

title = tk.Label(window, text="Jarvis AI Assistant", font=("Arial", 22, "bold"), bg="#101820", fg="#00FFC6")
title.pack(pady=10)

chat_box = scrolledtext.ScrolledText(window, width=70, height=25, font=("Arial", 12))
chat_box.pack(pady=10)

entry = tk.Entry(window, width=40, font=("Arial", 14))
entry.pack(pady=10)

def send_text():
    text = entry.get()
    if text.strip() == "":
        return
    chat_box.insert(tk.END, "You: " + text + "\n")
    chat_box.yview(tk.END)
    entry.delete(0, tk.END)
    process_input(text.lower())

send_btn = tk.Button(window, text="Send", font=("Arial", 14), bg="#00FFC6", command=send_text)
send_btn.pack(pady=5)

voice_btn = tk.Button(window, text="🎤 Speak", font=("Arial", 14), bg="#00A8FF", fg="white", command=listen_voice)
voice_btn.pack(pady=5)

clear_btn = tk.Button(window, text="Clear Chat", font=("Arial", 14), bg="#FFAA00", command=lambda: chat_box.delete(1.0, tk.END))
clear_btn.pack(pady=5)

exit_btn = tk.Button(window, text="Exit", font=("Arial", 14), bg="#FF4C4C", fg="white", command=window.destroy)
exit_btn.pack(pady=5)

speak("Hello Sai, Jarvis GUI is now active.")

window.mainloop()
