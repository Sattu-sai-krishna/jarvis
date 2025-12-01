import speech_recognition as sr
import pyttsx3
import datetime
import webbrowser
import wikipedia
import requests
import json
import pickle
import re
import os

# ------------------------- LOAD MODEL -------------------------
with open("intent_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

with open("intents.json", "r") as f:
    INTENTS = json.load(f)

# ------------------------- TTS ENGINE -------------------------
engine = pyttsx3.init()
engine.setProperty("rate", 170)

def speak(text):
    print("Jarvis:", text)
    engine.say(text)
    engine.runAndWait()

# ------------------------- STT INPUT -------------------------
recognizer = sr.Recognizer()

import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

recognizer = sr.Recognizer()

def listen():
    try:
        print("Listening...")

        duration = 4  # seconds
        sample_rate = 16000

        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
        sd.wait()

        temp_file = "temp_audio.wav"
        sf.write(temp_file, recording, sample_rate)

        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            print("You:", text)
            return text.lower()

    except Exception as e:
        print("Error:", e)
        return ""


# ------------------------- INTENT FUNCTION -------------------------
def predict_intent(text):
    X = vectorizer.transform([text])
    intent = model.predict(X)[0]
    return intent

# ------------------------- ACTIONS -------------------------
def tell_time():
    return datetime.datetime.now().strftime("The time is %I:%M %p")

def tell_date():
    return datetime.date.today().strftime("Today is %A, %d %B %Y")

def open_youtube():
    webbrowser.open("https://youtube.com")
    return "Opening YouTube."

def open_google():
    webbrowser.open("https://google.com")
    return "Opening Google."

def google_search(text):
    query = text.replace("google", "").replace("search", "").strip()
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for {query}"

def youtube_search(text):
    query = text.replace("youtube", "").replace("search", "").strip()
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Searching YouTube for {query}"

def wiki_search(text):
    try:
        t = re.sub(r"(who is|what is|tell me about)", "", text).strip()
        return wikipedia.summary(t, sentences=2)
    except:
        return "I couldn't find results on Wikipedia."

# ------------------------- WEATHER FEATURE -------------------------
API_KEY = "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current_weather=true"

def get_weather():
    try:
        res = requests.get(API_KEY).json()
        temp = res["current_weather"]["temperature"]
        wind = res["current_weather"]["windspeed"]
        return f"The temperature is {temp}°C with wind speed {wind} km/h."
    except:
        return "Unable to fetch weather now."

# ------------------------- HANDLE INTENT -------------------------
def handle_intent(intent, text):
    if intent in INTENTS:
        if INTENTS[intent]["responses"][0] != "":
            speak(INTENTS[intent]["responses"][0])

    if intent == "time":
        speak(tell_time())

    elif intent == "date":
        speak(tell_date())

    elif intent == "open_youtube":
        speak(open_youtube())

    elif intent == "open_google":
        speak(open_google())

    elif intent == "google_search":
        speak(google_search(text))

    elif intent == "youtube_search":
        speak(youtube_search(text))

    elif intent == "wikipedia_search":
        speak(wiki_search(text))

    elif intent == "weather":
        speak(get_weather())

    elif intent == "goodbye":
        speak("Goodbye Sir!")
        exit()

    else:
        speak("I am still learning. Can you say it again?")

# ------------------------- RUN JARVIS -------------------------
def run_jarvis():
    speak("Hello Sai, Jarvis at your service. How can I assist you?")

    while True:
        text = listen()
        if not text:
            continue

        text = re.sub(r"jarvis", "", text).strip()

        intent = predict_intent(text)
        handle_intent(intent, text)

run_jarvis()
