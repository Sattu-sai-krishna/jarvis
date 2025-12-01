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
import threading
import time
import math

# ================== LOAD ML MODEL & INTENTS ==================

with open("intent_model.pkl", "rb") as f:
    model, vectorizer = pickle.load(f)

with open("intents.json", "r") as f:
    INTENTS = json.load(f)

# ================== TEXT TO SPEECH ==================

engine = pyttsx3.init()
engine.setProperty("rate", 175)


def typing_animation(prefix, message):
    """Show Jarvis text with typing effect."""
    chat_box.insert(tk.END, "\n" + prefix)
    chat_box.update()

    for ch in message:
        chat_box.insert(tk.END, ch)
        chat_box.update()
        time.sleep(0.015)

    chat_box.insert(tk.END, "\n\n")
    chat_box.yview(tk.END)


def speak(text):
    typing_animation("Jarvis: ", text)
    engine.say(text)
    engine.runAndWait()


# ================== VOICE INPUT (NO PYAUDIO) ==================

recognizer = sr.Recognizer()


def listen_voice():
    try:
        set_status("Listening... 🎤")
        glow_mic(True)

        duration = 4  # seconds
        sample_rate = 16000

        recording = sd.rec(int(duration * sample_rate),
                           samplerate=sample_rate,
                           channels=1)
        sd.wait()

        temp_file = "temp_voice.wav"
        sf.write(temp_file, recording, sample_rate)

        with sr.AudioFile(temp_file) as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)
        add_chat_bubble("You", text)
        process_input(text.lower())

    except Exception as e:
        print("Voice error:", e)
        speak("Sorry Sai, I couldn't understand that.")
    finally:
        glow_mic(False)
        set_status("Idle")


# ================== INTENT + ACTIONS ==================

def predict_intent(text):
    X = vectorizer.transform([text])
    return model.predict(X)[0]


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
    query = text.replace("search", "").replace("google", "").strip()
    if not query:
        return "What should I search on Google, Sai?"
    webbrowser.open(f"https://www.google.com/search?q={query}")
    return f"Searching Google for {query}."


def youtube_search(text):
    query = text.replace("search", "").replace("youtube", "").strip()
    if not query:
        return "What should I search on YouTube, Sai?"
    webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
    return f"Searching YouTube for {query}."


def wiki_search(text):
    try:
        text = re.sub(r"(who is|what is|tell me about)", "", text).strip()
        if not text:
            return "What topic should I search on Wikipedia?"
        return wikipedia.summary(text, sentences=2)
    except Exception:
        return "I couldn't find any information on Wikipedia."


def get_weather():
    try:
        url = "https://api.open-meteo.com/v1/forecast?latitude=13.0827&longitude=80.2707&current_weather=true"
        data = requests.get(url).json()
        temp = data["current_weather"]["temperature"]
        wind = data["current_weather"]["windspeed"]
        return f"Current temperature is {temp}°C with wind speed {wind} km/h."
    except Exception:
        return "I cannot fetch the weather right now."


def process_input(text):
    set_status("Processing…")
    intent = predict_intent(text)

    if intent == "greet":
        speak("Hello Sai, how can I assist you today?")
    elif intent == "time":
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
        speak("Powering down. Goodbye Sai.")
        window.after(1000, window.destroy)
    else:
        speak("I'm still learning, please say it again in another way.")
    set_status("Idle")


# ================== GUI HELPERS ==================

def add_chat_bubble(sender, text):
    bubble = f"\n{sender}: {text}\n"
    chat_box.insert(tk.END, bubble)
    chat_box.yview(tk.END)


def on_send_click():
    text = entry.get().strip()
    if not text:
        return
    add_chat_bubble("You", text)
    entry.delete(0, tk.END)
    threading.Thread(target=process_input, args=(text.lower(),), daemon=True).start()


def start_voice_thread():
    threading.Thread(target=listen_voice, daemon=True).start()


def set_status(text):
    status_label.config(text=f"Status: {text}")


# ================== HUD / JARVIS EYE ANIMATION ==================

rotation_angle = 0
mic_glow = False


def glow_mic(state: bool):
    global mic_glow
    mic_glow = state


def draw_hud():
    """Draws Jarvis AI eye + rotating HUD rings."""
    global rotation_angle
    hud_canvas.delete("all")

    w = hud_canvas.winfo_width()
    h = hud_canvas.winfo_height()
    cx, cy = w // 2, h // 2
    radius_outer = min(w, h) // 2 - 10

    # Background faint ring
    hud_canvas.create_oval(cx - radius_outer, cy - radius_outer,
                           cx + radius_outer, cy + radius_outer,
                           outline="#0A3758", width=3)

    # Multiple inner rings
    for i, r_mult in enumerate([0.8, 0.6, 0.4]):
        hud_canvas.create_oval(cx - radius_outer * r_mult,
                               cy - radius_outer * r_mult,
                               cx + radius_outer * r_mult,
                               cy + radius_outer * r_mult,
                               outline="#0AF0FF" if i == 0 else "#066D99",
                               width=2)

    # Rotating arcs – Jarvis style
    for offset, arc_len, color in [
        (0, 60, "#00E5FF"),
        (140, 40, "#00B7FF"),
        (230, 55, "#00FFFF")
    ]:
        start_angle = (rotation_angle + offset) % 360
        hud_canvas.create_arc(cx - radius_outer, cy - radius_outer,
                              cx + radius_outer, cy + radius_outer,
                              start=start_angle, extent=arc_len,
                              style=tk.ARC, outline=color, width=4)

    # Central AI eye – glowing blue ring
    eye_r1 = radius_outer * 0.25
    eye_r2 = radius_outer * 0.13

    hud_canvas.create_oval(cx - eye_r1, cy - eye_r1,
                           cx + eye_r1, cy + eye_r1,
                           outline="#00E5FF", width=4)
    hud_canvas.create_oval(cx - eye_r2, cy - eye_r2,
                           cx + eye_r2, cy + eye_r2,
                           outline="#00FFFF", width=3, fill="#031421")

    # Blue glow lines (like rays)
    for i in range(12):
        angle_deg = i * 30 + rotation_angle * 0.5
        angle_rad = math.radians(angle_deg)
        x1 = cx + eye_r1 * math.cos(angle_rad)
        y1 = cy + eye_r1 * math.sin(angle_rad)
        x2 = cx + (eye_r1 + 12) * math.cos(angle_rad)
        y2 = cy + (eye_r1 + 12) * math.sin(angle_rad)
        hud_canvas.create_line(x1, y1, x2, y2, fill="#00E5FF")

    # Mic glow ring
    mic_r = radius_outer * 0.05
    color = "#00FF9D" if mic_glow else "#007A52"
    hud_canvas.create_oval(cx - mic_r, cy + radius_outer * 0.6 - mic_r,
                           cx + mic_r, cy + radius_outer * 0.6 + mic_r,
                           outline=color, width=3)
    hud_canvas.create_text(cx, cy + radius_outer * 0.6 + 20,
                           text="MIC", fill="#00E5FF", font=("Consolas", 9))

    # AI label
    hud_canvas.create_text(cx, cy - radius_outer * 0.75,
                           text="J.A.R.V.I.S CORE ONLINE",
                           fill="#00E5FF", font=("Consolas", 9))

    rotation_angle = (rotation_angle + 3) % 360
    hud_canvas.after(40, draw_hud)


# ================== BUILD GUI LAYOUT ==================

window = tk.Tk()
window.title("JARVIS HUD Interface")
window.geometry("1000x700")
window.configure(bg="#040812")

# --- Top Title ---
title_label = tk.Label(
    window,
    text="J.A.R.V.I.S – Holographic HUD Interface",
    font=("Segoe UI", 20, "bold"),
    bg="#040812",
    fg="#00E5FF"
)
title_label.pack(pady=10)

# --- Main Frame (Left HUD + Right Chat) ---
main_frame = tk.Frame(window, bg="#040812")
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

# Left HUD canvas
hud_frame = tk.Frame(main_frame, bg="#040812")
hud_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 10))

hud_canvas = tk.Canvas(hud_frame, width=360, height=360,
                       bg="#02040A", highlightthickness=0)
hud_canvas.pack(pady=10)

status_label = tk.Label(
    hud_frame,
    text="Status: Idle",
    font=("Consolas", 11),
    bg="#040812",
    fg="#00E5FF"
)
status_label.pack(pady=5)

# Right Chat Section
chat_frame = tk.Frame(main_frame, bg="#040812")
chat_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

chat_box = scrolledtext.ScrolledText(
    chat_frame,
    width=60,
    height=25,
    font=("Consolas", 12),
    bg="#050B1B",
    fg="#00E5FF",
    insertbackground="#00E5FF",
    wrap=tk.WORD,
    borderwidth=0
)
chat_box.pack(fill=tk.BOTH, expand=True, pady=5)

# --- Bottom Input + Buttons ---
bottom_frame = tk.Frame(window, bg="#040812")
bottom_frame.pack(fill=tk.X, pady=10)

entry = tk.Entry(
    bottom_frame,
    width=50,
    font=("Segoe UI", 13),
    bg="#07152D",
    fg="#FFFFFF",
    insertbackground="#00E5FF",
    relief="flat"
)
entry.pack(side=tk.LEFT, padx=(20, 10), ipady=6)


def on_enter_press(event):
    on_send_click()


entry.bind("<Return>", on_enter_press)

send_button = tk.Button(
    bottom_frame,
    text="Send",
    font=("Segoe UI", 12, "bold"),
    bg="#00E5FF",
    fg="#000000",
    relief="flat",
    padx=16,
    pady=6,
    command=on_send_click
)
send_button.pack(side=tk.LEFT, padx=5)

voice_button = tk.Button(
    bottom_frame,
    text="🎤 Speak",
    font=("Segoe UI", 12, "bold"),
    bg="#0066FF",
    fg="#FFFFFF",
    relief="flat",
    padx=16,
    pady=6,
    command=start_voice_thread
)
voice_button.pack(side=tk.LEFT, padx=5)

clear_button = tk.Button(
    bottom_frame,
    text="Clear",
    font=("Segoe UI", 11),
    bg="#FFAA00",
    fg="#000000",
    relief="flat",
    padx=12,
    pady=5,
    command=lambda: chat_box.delete(1.0, tk.END)
)
clear_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(
    bottom_frame,
    text="Exit",
    font=("Segoe UI", 11),
    bg="#FF4444",
    fg="#FFFFFF",
    relief="flat",
    padx=12,
    pady=5,
    command=window.destroy
)
exit_button.pack(side=tk.RIGHT, padx=(5, 20))

# Start HUD animation + welcome message
draw_hud()
threading.Thread(
    target=lambda: speak("JARVIS HUD online. Hello Sai, how can I assist you?"),
    daemon=True
).start()

window.mainloop()
