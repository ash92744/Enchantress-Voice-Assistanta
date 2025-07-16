import cv2
import os
import pyautogui as p

def AuthenticateFace():
    flag = ""
    
    # Get absolute paths based on this file's location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    TRAINER_PATH = os.path.join(BASE_DIR, 'trainer', 'trainer.yml')
    CASCADE_PATH = os.path.join(BASE_DIR, 'haarcascade_frontalface_default.xml')

    # Check if trainer file exists
    print(f"🔍 Looking for trainer.yml at: {TRAINER_PATH}")
    if not os.path.exists(TRAINER_PATH):
        print("❌ trainer.yml file NOT found!")
        return 0
    
    # Load recognizer and cascade
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read(TRAINER_PATH)

    faceCascade = cv2.CascadeClassifier(CASCADE_PATH)
    font = cv2.FONT_HERSHEY_SIMPLEX

    names = ['', 'User']  # id 1 = user
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1 * cam.get(3)
    minH = 0.1 * cam.get(4)

    while True:
        ret, img = cam.read()
        if not ret:
            print("❌ Failed to capture video frame.")
            breakz

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.2,
            minNeighbors=5,
            minSize=(int(minW), int(minH))
        )

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
            id, confidence = recognizer.predict(gray[y:y+h, x:x+w])

            if confidence < 100:
                name = names[id]
                confidence_text = f"  {round(100 - confidence)}%"
                flag = 1
            else:
                name = "unknown"
                confidence_text = f"  {round(100 - confidence)}%"
                flag = 0

            cv2.putText(img, str(name), (x+5, y-5), font, 1, (255, 255, 255), 2)
            cv2.putText(img, str(confidence_text), (x+5, y+h-5), font, 1, (255, 255, 0), 1)

        cv2.imshow('camera', img)

        k = cv2.waitKey(10) & 0xff
        if k == 27 or flag == 1:  # ESC or face authenticated
            break

    cam.release()
    cv2.destroyAllWindows()
    return flag
