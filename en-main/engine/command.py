import pyttsx3
import speech_recognition as sr
import eel
import time


def speak(text):
    text = str(text)
    print("🤖:", text)
    try:
        engine = pyttsx3.init('sapi5')
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[2].id)
        engine.setProperty('rate', 174)

        eel.DisplayMessage(text)
        engine.say(text)
        eel.receiverText(text)
        engine.runAndWait()
    except Exception as e:
        print("❌ Error in speak():", str(e))


def takecommand():
    r = sr.Recognizer()

    # 🔍 Set your correct microphone index here
    mic_index = 1  # <- Change this after checking your mic index with the test script

    try:
        with sr.Microphone(device_index=mic_index) as source:
            print('🎙️ Listening...')
            eel.DisplayMessage('🎙️ Listening...')
            r.pause_threshold = 1
            r.adjust_for_ambient_noise(source, duration=1)

            try:
                audio = r.listen(source, timeout=10, phrase_time_limit=6)
            except sr.WaitTimeoutError:
                print("❌ Timeout: No speech detected.")
                speak("I didn't hear anything. Please try again.")
                return ""

        print('🧠 Recognizing...')
        eel.DisplayMessage('🧠 Recognizing...')
        query = r.recognize_google(audio, language='en-in')
        print(f"🗣️ User said: {query}")
        eel.DisplayMessage(query)
        time.sleep(1)
        return query.lower()

    except sr.UnknownValueError:
        print("❌ Speech not understood.")
        speak("Sorry, I didn't catch that.")
    except sr.RequestError as e:
        print(f"❌ Could not request results; {e}")
        speak("There was a problem connecting to the speech service.")
    except Exception as e:
        print("❌ General error in takecommand():", str(e))
        speak("An error occurred while trying to understand you.")

    return ""


@eel.expose
def allCommands(message=1):
    try:
        if message == 1:
            query = takecommand()
        else:
            query = message.lower()

        if not query or query.strip() == "":
            speak("No command detected. Please try again.")
            query = takecommand()  # 🔁 Try once more
            if not query or query.strip() == "":
                return

        eel.senderText(query)

        # --- Commands Section ---
        if "open" in query:
            from engine.features import openCommand
            openCommand(query)

        elif "on youtube" in query:
            from engine.features import PlayYoutube
            PlayYoutube(query)

        elif "send message" in query or "phone call" in query or "video call" in query:
            from engine.features import findContact, whatsApp, makeCall, sendMessage
            contact_no, name = findContact(query)
            if contact_no != 0:
                speak("Which mode do you want to use: WhatsApp or Mobile?")
                preference = takecommand()

                if "mobile" in preference:
                    if "send message" in query or "send sms" in query:
                        speak("What message should I send?")
                        message = takecommand()
                        sendMessage(message, contact_no, name)
                    elif "phone call" in query:
                        makeCall(name, contact_no)
                    else:
                        speak("Please try again.")
                elif "whatsapp" in preference:
                    if "send message" in query:
                        speak("What message should I send?")
                        message = takecommand()
                        whatsApp(contact_no, message, "message", name)
                    elif "video call" in query:
                        whatsApp(contact_no, "", "video call", name)
                    else:
                        whatsApp(contact_no, "", "call", name)
                else:
                    speak("Invalid preference. Please say WhatsApp or Mobile.")
            else:
                speak("Contact not found.")

        else:
            from engine.features import chatBot
            chatBot(query)

    except Exception as e:
        print("🔥 ERROR in allCommands():", str(e))
        speak("Something went wrong while processing your command.")

    eel.ShowHood()
