import multiprocessing

# ✅ Start Jarvis assistant
def startJarvis():
    print("Process 1 is running.")
    from main import start  # Importing from main.py directly in en-main
    start()

# ✅ Start hotword detection
def listenHotword():
    print("Process 2 is running.")
    from engine.features import hotword
    hotword()

# ✅ Launch both processes
if __name__ == '__main__':
    p1 = multiprocessing.Process(target=startJarvis)
    p2 = multiprocessing.Process(target=listenHotword)

    p1.start()
    p2.start()

    p1.join()

    if p2.is_alive():
        p2.terminate()
        p2.join()

    print("System stopped.")
