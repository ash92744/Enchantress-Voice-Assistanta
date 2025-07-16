import os
import eel

from engine.features import *
from engine.command import *
from engine.auth import recoganize

def start():
    
    web_dir = os.path.join(os.path.dirname(__file__), "www")
    eel.init(web_dir)

    playAssistantSound()
    @eel.expose
    def init():
        # subprocess.call([r'device.bat'])
        eel.hideLoader()
        speak("Ready for Face Authentication")
        flag = recoganize.AuthenticateFace()
        if flag == 1:
            eel.hideFaceAuth()
            speak("Face Authentication Completed")
            eel.hideFaceAuthSuccess()
            speak("Welcome Boss, How can I Help You ?")
            eel.hideStart()
            playAssistantSound()
        else:
            speak("Face Authentication Fail")
    os.system('start msedge.exe --app="http://localhost:8000/index.html"')

    eel.start('index.html', mode=None, host='localhost', block=True)