import os
import cv2
import numpy as np

FACE_MODEL_PATH = "face_data.npy"


def mse(imageA, imageB):
    return np.mean((imageA - imageB) ** 2)


def capture_and_train():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    face_encodings_list = []
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    print("Capturing face. Look at the camera...")
    for _ in range(10):  # Capture multiple frames
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_region = gray[y:y + h, x:x + w]
            face_resized = cv2.resize(face_region, (100, 100)).astype("float32") / 255.0  # Normalize
            face_encodings_list.append(face_resized.flatten())

            # Draw rectangle around face and show frame
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow("Capturing Face", frame)
            cv2.waitKey(200)  # Show for 200ms per frame

    cap.release()
    cv2.destroyAllWindows()

    if face_encodings_list:
        face_encodings_array = np.array(face_encodings_list)  # Store multiple unique encodings
        np.save(FACE_MODEL_PATH, face_encodings_array)  # Save as multiple encodings
        print(f"Face model saved successfully as {FACE_MODEL_PATH}")
    else:
        print("No face detected. Try again.")


if __name__ == "__main__":
    capture_and_train()
