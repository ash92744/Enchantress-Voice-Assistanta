import os
import re
import sqlite3
import struct
import subprocess
import time
import webbrowser
import requests

import eel
import pyaudio
import pyautogui
import pywhatkit as kit
import pvporcupine

from playsound import playsound
from urllib.parse import quote
from engine.command import speak
from engine.config import ASSISTANT_NAME
from engine.helper import extract_yt_term, remove_words


# ✅ Database connection
con = sqlite3.connect("jarvis.db")
cursor = con.cursor()

# ✅ Gemini API
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=AIzaSyB7oeKcr32-7Q-7d4uKNB-oJqspaa7Yd7E"

# ✅ Chat memory for context
chat_history = []


@eel.expose
def playAssistantSound():
    music_path = os.path.join(os.path.dirname(__file__), "..", "www", "assets", "audio", "start_sound.mp3")
    try:
        playsound(music_path)
    except Exception as e:
        print(f"❌ Error playing assistant sound: {e}")


def openCommand(query):
    query = query.replace(ASSISTANT_NAME, "").replace("open", "").lower().strip()

    try:
        cursor.execute('SELECT path FROM sys_command WHERE name=?', (query,))
        result = cursor.fetchone()
        if result:
            speak("Opening " + query)
            os.startfile(result[0])
            return

        cursor.execute('SELECT url FROM web_command WHERE name=?', (query,))
        result = cursor.fetchone()
        if result:
            speak("Opening " + query)
            webbrowser.open(result[0])
            return

        # Fallback
        speak("Opening " + query)
        os.system('start ' + query)

    except Exception as e:
        print(f"❌ openCommand error: {e}")
        speak("Something went wrong while trying to open that.")


def PlayYoutube(query):
    search_term = extract_yt_term(query)
    speak(f"Playing {search_term} on YouTube")
    kit.playonyt(search_term)


def hotword():
    porcupine = None
    paud = None
    audio_stream = None

    try:
        access_key = "x4KmWNI9e/a1HQERN9hSChRJD6U8DTIsFqdK7/kt4bnMiXfwgdyL/Q=="
        porcupine = pvporcupine.create(
            access_key=access_key,
            keywords=["jarvis", "alexa"]
        )
        paud = pyaudio.PyAudio()
        audio_stream = paud.open(
            rate=porcupine.sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            frames_per_buffer=porcupine.frame_length
        )

        while True:
            data = audio_stream.read(porcupine.frame_length, exception_on_overflow=False)
            frame = struct.unpack_from("h" * porcupine.frame_length, data)
            result = porcupine.process(frame)

            if result >= 0:
                print("🔊 Hotword detected")
                return True

    except Exception as e:
        print(f"❌ Hotword detection failed: {e}")
        return False

    finally:
        if porcupine:
            porcupine.delete()
        if audio_stream:
            audio_stream.close()
        if paud:
            paud.terminate()


def findContact(query):
    try:
        query = remove_words(query, [ASSISTANT_NAME, 'make', 'a', 'to', 'phone', 'call', 'send', 'message', 'whatsapp', 'video']).strip().lower()
        cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
        result = cursor.fetchone()

        if result:
            mobile_number = str(result[0])
            if not mobile_number.startswith("+91"):
                mobile_number = "+91" + mobile_number
            return mobile_number, query

        speak("Contact does not exist.")
        return 0, 0

    except Exception as e:
        print(f"❌ findContact error: {e}")
        speak("Failed to find contact.")
        return 0, 0


def whatsApp(mobile_no, message, flag, name):
    try:
        if flag == "message":
            target_tab = 12
            jarvis_message = f"Message sent successfully to {name}"
        elif flag == "call":
            target_tab = 7
            message = ''
            jarvis_message = f"Calling {name}"
        else:  # video call
            target_tab = 6
            message = ''
            jarvis_message = f"Starting video call with {name}"

        encoded_message = quote(message)
        whatsapp_url = f"whatsapp://send?phone={mobile_no}&text={encoded_message}"
        subprocess.run(f'start "" "{whatsapp_url}"', shell=True)
        time.sleep(5)

        pyautogui.hotkey('ctrl', 'f')
        for _ in range(1, target_tab):
            pyautogui.hotkey('tab')
        pyautogui.hotkey('enter')

        speak(jarvis_message)

    except Exception as e:
        print(f"❌ WhatsApp action failed: {e}")
        speak("Failed to perform WhatsApp action.")


def chatBot(query):
    global chat_history

    chat_history.append({"role": "user", "parts": [{"text": query}]})
    payload = {"contents": chat_history}

    try:
        response = requests.post(GEMINI_API_URL, headers={"Content-Type": "application/json"}, json=payload)
        response.raise_for_status()

        result = response.json()
        reply = result["candidates"][0]["content"]["parts"][0]["text"]
        chat_history.append({"role": "model", "parts": [{"text": reply}]})

        print(reply)
        speak(reply)
        return reply

    except Exception as e:
        print(f"❌ Gemini Chat Error: {e}")
        fallback = "Sorry, Gemini is not responding right now."
        speak(fallback)
        return fallback


def makeCall(name, mobile_no):
    try:
        mobile_no = mobile_no.replace(" ", "")
        speak(f"Calling {name}")
        os.system(f'adb shell am start -a android.intent.action.CALL -d tel:{mobile_no}')
    except Exception as e:
        print(f"❌ makeCall error: {e}")
        speak("Call failed.")


def sendMessage(message, mobile_no, name):
    try:
        from engine.helper import replace_spaces_with_percent_s, goback, keyEvent, tapEvents, adbInput

        message = replace_spaces_with_percent_s(message)
        mobile_no = replace_spaces_with_percent_s(mobile_no)

        speak("Sending message")
        goback(4)
        time.sleep(1)
        keyEvent(3)
        tapEvents(136, 2220)
        tapEvents(819, 2192)
        adbInput(mobile_no)
        tapEvents(601, 574)
        tapEvents(390, 2270)
        adbInput(message)
        tapEvents(957, 1397)

        speak(f"Message sent successfully to {name}")

    except Exception as e:
        print(f"❌ sendMessage error: {e}")
        speak("Failed to send message.")
