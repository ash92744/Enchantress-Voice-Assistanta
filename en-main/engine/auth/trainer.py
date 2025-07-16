import cv2
import numpy as np
from PIL import Image
import os

# Paths
samples_path = './engine/auth/samples'
trainer_dir = './engine/auth/trainer'
trainer_path = os.path.join(trainer_dir, 'trainer.yml')
cascade_path = './engine/auth/haarcascade_frontalface_default.xml'

# Create LBPH recognizer and face detector
recognizer = cv2.face.LBPHFaceRecognizer_create()
detector = cv2.CascadeClassifier(cascade_path)

def Images_And_Labels(path):
    imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
    faceSamples = []
    ids = []

    for imagePath in imagePaths:
        gray_img = Image.open(imagePath).convert('L')
        img_arr = np.array(gray_img, 'uint8')

        try:
            id = int(os.path.split(imagePath)[-1].split(".")[1])
        except (IndexError, ValueError):
            print(f"⚠️ Skipping invalid file name: {imagePath}")
            continue

        faces = detector.detectMultiScale(img_arr)

        for (x, y, w, h) in faces:
            faceSamples.append(img_arr[y:y+h, x:x+w])
            ids.append(id)

    return faceSamples, ids

print("⚙️ Training faces. It may take a few seconds...")

faces, ids = Images_And_Labels(samples_path)
recognizer.train(faces, np.array(ids))

# Ensure the directory exists
os.makedirs(trainer_dir, exist_ok=True)

# Save the trained model
recognizer.write(trainer_path)

print(f"✅ Model trained and saved to: {trainer_path}")
