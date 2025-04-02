import cv2
import threading
from tkinter import messagebox
import PHASE1  # Import PHASE1 as a module
import train_face_model  # Import train_face_model as a module
import database_manager
import os
import sqlite3
import tkinter as tk
import numpy as np
from datetime import datetime

# Global variables
FACE_MODEL_PATH = "face_data.npy"
stop_event = threading.Event()
phase1_thread = None


def check_database():
    if not os.path.exists('anveksha.db'):
        # Initialize database if it doesn't exist
        database_manager.setup_database()
        database_manager.index_existing_files()
        messagebox.showinfo("Database Check", "Database initialized with existing files.")
    else:
        # Update database with any new files
        database_manager.index_existing_files()

    # Open the database viewer
    database_manager.view_database()


def load_trained_faces():
    # Get the model path from database
    face_model_path = database_manager.get_latest_face_model()

    # If not found in database, try the default path
    if face_model_path is None:
        if os.path.exists(FACE_MODEL_PATH):
            return np.load(FACE_MODEL_PATH, allow_pickle=True)
        return None

    # Load the model from the path provided by the database
    return np.load(face_model_path, allow_pickle=True)

def recognize_face():
    known_face_data = load_trained_faces()
    if known_face_data is None:
        print("No trained face model found. Training now...")
        train_face_model.capture_and_train()
        known_face_data = load_trained_faces()
        if known_face_data is None:
            print("Face training failed. Exiting.")
            return False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return False

    print("Scanning face...")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    match_found = False

    for _ in range(20):
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_region = gray[y:y + h, x:x + w]
            face_resized = cv2.resize(face_region, (100, 100)).astype("float32") / 255.0

            for stored_face in known_face_data:
                diff = np.mean((stored_face - face_resized.flatten()) ** 2)
                if diff < 10:
                    match_found = True
                    break

        if match_found:
            break

    cap.release()
    cv2.destroyAllWindows()
    return match_found

def run_phase1():
    global stop_event
    print("Starting Phase 1...")
    PHASE1.main(stop_event)
    print("Phase 1 ended.")

def start_phase1():
    global phase1_thread
    if recognize_face():
        print("Face recognized. Starting Phase 1...")
        stop_event.clear()
        phase1_thread = threading.Thread(target=run_phase1)
        phase1_thread.start()
    else:
        messagebox.showerror("Authentication Failed", "Face not recognized. Access denied.")

def stop_phase1():
    global stop_event, phase1_thread
    print("Stopping Phase 1...")
    stop_event.set()
    if phase1_thread and phase1_thread.is_alive():
        phase1_thread.join(timeout=5)  # Wait up to 5 seconds
        if phase1_thread.is_alive():
            print("Warning: Phase 1 thread didn't exit cleanly")
    print("Phase 1 stopped.")


def train_face():
    print("Training face model...")
    train_face_model.capture_and_train()

    # After training, register the new model in the database
    if os.path.exists(FACE_MODEL_PATH):
        conn = sqlite3.connect('anveksha.db')
        cursor = conn.cursor()

        # Get current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # Check if this model is already in the database
        cursor.execute("SELECT COUNT(*) FROM face_models WHERE filepath = ?", (FACE_MODEL_PATH,))
        if cursor.fetchone()[0] == 0:
            # Add new record
            cursor.execute("INSERT INTO face_models (filepath, timestamp, description) VALUES (?, ?, ?)",
                           (FACE_MODEL_PATH, timestamp, "Face model trained via UI"))
        else:
            # Update existing record
            cursor.execute("UPDATE face_models SET timestamp = ? WHERE filepath = ?",
                           (timestamp, FACE_MODEL_PATH))

        conn.commit()
        conn.close()

    messagebox.showinfo("Training Complete", "Your face model has been trained and registered in the database.")


def anveksha():
    root = tk.Tk()
    root.title("Anveksha")
    root.geometry("300x400")  # Made taller to accommodate the new button

    train_btn = tk.Button(root, text="Train Your Face Model", command=train_face)
    train_btn.pack(pady=10)

    check_db_btn = tk.Button(root, text="Check Database", command=check_database)
    check_db_btn.pack(pady=10)

    cleanup_db_btn = tk.Button(root, text="Delete All Records & Files",
                               command=database_manager.delete_files_from_database)
    cleanup_db_btn.pack(pady=10)

    delete_files_btn = tk.Button(root, text="Delete Physical Files (Keep Records)",
                                 command=database_manager.delete_physical_files)
    delete_files_btn.pack(pady=10)

    start_btn = tk.Button(root, text="Start", command=start_phase1)
    start_btn.pack(pady=10)

    stop_btn = tk.Button(root, text="Stop", command=stop_phase1)
    stop_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    anveksha()
