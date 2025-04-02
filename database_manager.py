import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import numpy as np
from datetime import datetime

# Define constants directly
BASE_DIR = os.path.join(os.getcwd(), "Anveksha_Data")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "Screenshots")
VIDEOS_DIR = os.path.join(BASE_DIR, "Webcam_Videos")
LOGS_DIR = os.path.join(BASE_DIR, "Logs")
FACE_MODEL_PATH = "face_data.npy"

# Ensure directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(VIDEOS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)


def setup_database():
    """Initialize SQLite database with tables for different data types"""
    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    # Create tables for different data types
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS screenshots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        duration INTEGER,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        log_type TEXT NOT NULL,
        description TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS face_models (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filepath TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        description TEXT
    )
    ''')

    conn.commit()
    conn.close()


def index_existing_files():
    """Index existing files in the Anveksha_Data directory into the database"""
    # Ensure directories exist
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(VIDEOS_DIR, exist_ok=True)
    os.makedirs(LOGS_DIR, exist_ok=True)

    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    # Index screenshots
    for file in os.listdir(SCREENSHOTS_DIR):
        if file.endswith('.png') or file.endswith('.jpg'):
            filepath = os.path.join(SCREENSHOTS_DIR, file)
            # Try to parse timestamp from filename
            try:
                if '-' in file:
                    timestamp = file.split('-')[1].split('.')[0]
                else:
                    timestamp = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d_%H-%M-%S")

                # Check if this file is already in the database
                cursor.execute("SELECT COUNT(*) FROM screenshots WHERE filepath = ?", (filepath,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO screenshots (filepath, timestamp) VALUES (?, ?)",
                                   (filepath, timestamp))
            except:
                # Fallback to file modification time if parsing fails
                timestamp = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d_%H-%M-%S")
                cursor.execute("SELECT COUNT(*) FROM screenshots WHERE filepath = ?", (filepath,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO screenshots (filepath, timestamp) VALUES (?, ?)",
                                   (filepath, timestamp))

    # Index videos
    for file in os.listdir(VIDEOS_DIR):
        if file.endswith('.avi'):
            filepath = os.path.join(VIDEOS_DIR, file)
            try:
                if '_' in file:
                    timestamp = file.split('_')[1].split('.')[0]
                else:
                    timestamp = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d_%H-%M-%S")

                cursor.execute("SELECT COUNT(*) FROM videos WHERE filepath = ?", (filepath,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO videos (filepath, timestamp) VALUES (?, ?)",
                                   (filepath, timestamp))
            except:
                timestamp = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d_%H-%M-%S")
                cursor.execute("SELECT COUNT(*) FROM videos WHERE filepath = ?", (filepath,))
                if cursor.fetchone()[0] == 0:
                    cursor.execute("INSERT INTO videos (filepath, timestamp) VALUES (?, ?)",
                                   (filepath, timestamp))

    # Index logs
    for file in os.listdir(LOGS_DIR):
        filepath = os.path.join(LOGS_DIR, file)
        if os.path.isfile(filepath):
            timestamp = datetime.fromtimestamp(os.path.getmtime(filepath)).strftime("%Y-%m-%d_%H-%M-%S")
            log_type = "general"
            if "ocr" in file:
                log_type = "ocr"
            elif "process" in file.lower():
                log_type = "process"

            cursor.execute("SELECT COUNT(*) FROM logs WHERE filepath = ?", (filepath,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO logs (filepath, timestamp, log_type) VALUES (?, ?, ?)",
                               (filepath, timestamp, log_type))

    # Index face model
    if os.path.exists(FACE_MODEL_PATH):
        timestamp = datetime.fromtimestamp(os.path.getmtime(FACE_MODEL_PATH)).strftime("%Y-%m-%d_%H-%M-%S")
        cursor.execute("SELECT COUNT(*) FROM face_models WHERE filepath = ?", (FACE_MODEL_PATH,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO face_models (filepath, timestamp) VALUES (?, ?)",
                           (FACE_MODEL_PATH, timestamp))

    conn.commit()
    conn.close()


def view_database():
    """Open a window to view and interact with the database contents"""
    db_window = tk.Toplevel()
    db_window.title("Anveksha Database Viewer")
    db_window.geometry("800x600")

    notebook = ttk.Notebook(db_window)
    notebook.pack(fill='both', expand=True, padx=10, pady=10)

    # Create tabs for different data types
    screenshots_tab = ttk.Frame(notebook)
    videos_tab = ttk.Frame(notebook)
    logs_tab = ttk.Frame(notebook)
    face_models_tab = ttk.Frame(notebook)

    notebook.add(screenshots_tab, text="Screenshots")
    notebook.add(videos_tab, text="Videos")
    notebook.add(logs_tab, text="Logs")
    notebook.add(face_models_tab, text="Face Models")

    # Configure each tab
    setup_screenshots_tab(screenshots_tab)
    setup_videos_tab(videos_tab)
    setup_logs_tab(logs_tab)
    setup_face_models_tab(face_models_tab)


def setup_screenshots_tab(tab):
    # Create treeview for screenshots
    columns = ("ID", "Timestamp", "Filepath", "Description")
    tree = ttk.Treeview(tab, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Add buttons for actions
    button_frame = ttk.Frame(tab)
    button_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(button_frame, text="View", command=lambda: view_file(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Delete", command=lambda: delete_file(tree, "screenshots")).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: load_data(tree, "screenshots")).pack(side="left", padx=5)

    # Load initial data
    load_data(tree, "screenshots")


def setup_videos_tab(tab):
    # Similar to screenshots tab with video-specific options
    columns = ("ID", "Timestamp", "Filepath", "Duration", "Description")
    tree = ttk.Treeview(tab, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    button_frame = ttk.Frame(tab)
    button_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(button_frame, text="Play", command=lambda: play_video(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Delete", command=lambda: delete_file(tree, "videos")).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: load_data(tree, "videos")).pack(side="left", padx=5)

    load_data(tree, "videos")


def setup_logs_tab(tab):
    # Similar setup for logs
    columns = ("ID", "Timestamp", "Log Type", "Filepath", "Description")
    tree = ttk.Treeview(tab, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    button_frame = ttk.Frame(tab)
    button_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(button_frame, text="View", command=lambda: view_file(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Delete", command=lambda: delete_file(tree, "logs")).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: load_data(tree, "logs")).pack(side="left", padx=5)

    load_data(tree, "logs")


def setup_face_models_tab(tab):
    # Setup for face models
    columns = ("ID", "Timestamp", "Filepath", "Description")
    tree = ttk.Treeview(tab, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)

    tree.pack(fill="both", expand=True, padx=10, pady=10)

    button_frame = ttk.Frame(tab)
    button_frame.pack(fill="x", padx=10, pady=5)

    ttk.Button(button_frame, text="View Info", command=lambda: view_model_info(tree)).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Delete", command=lambda: delete_file(tree, "face_models")).pack(side="left", padx=5)
    ttk.Button(button_frame, text="Refresh", command=lambda: load_data(tree, "face_models")).pack(side="left", padx=5)

    load_data(tree, "face_models")


def load_data(tree, table_name):
    """Load data from database into the treeview"""
    # Clear existing items
    for item in tree.get_children():
        tree.delete(item)

    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    if table_name == "screenshots":
        cursor.execute("SELECT id, timestamp, filepath, description FROM screenshots ORDER BY timestamp DESC")
    elif table_name == "videos":
        cursor.execute("SELECT id, timestamp, filepath, duration, description FROM videos ORDER BY timestamp DESC")
    elif table_name == "logs":
        cursor.execute("SELECT id, timestamp, log_type, filepath, description FROM logs ORDER BY timestamp DESC")
    elif table_name == "face_models":
        cursor.execute("SELECT id, timestamp, filepath, description FROM face_models ORDER BY timestamp DESC")

    for row in cursor.fetchall():
        tree.insert("", "end", values=row)

    conn.close()


def view_file(tree):
    """Open the selected file with the default program"""
    selected = tree.selection()
    if not selected:
        return

    item = tree.item(selected[0])
    values = item['values']

    # Find the filepath column (it can be at different indices depending on the tab)
    filepath = None
    for value in values:
        if isinstance(value, str) and (os.path.exists(value) or value.startswith(os.getcwd())):
            filepath = value
            break

    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Could not find the file")
        return

    if filepath.endswith(('.txt', '.log')):
        # Open text files in a new window
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()
            text_window = tk.Toplevel()
            text_window.title(f"File: {os.path.basename(filepath)}")
            text_window.geometry("800x600")

            text_area = tk.Text(text_window, wrap=tk.WORD)
            text_area.insert(tk.END, content)
            text_area.config(state=tk.DISABLED)
            text_area.pack(fill=tk.BOTH, expand=True)
    else:
        # Use system default program for other files
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(('xdg-open', filepath))
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {e}")


def play_video(tree):
    """Play the selected video file"""
    selected = tree.selection()
    if not selected:
        return

    item = tree.item(selected[0])
    values = item['values']

    # Find the filepath column
    filepath = None
    for value in values:
        if isinstance(value, str) and os.path.exists(value) and value.endswith('.avi'):
            filepath = value
            break

    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Could not find the video file")
        return

    try:
        if os.name == 'nt':  # Windows
            os.startfile(filepath)
        elif os.name == 'posix':  # macOS and Linux
            subprocess.call(('xdg-open', filepath))
    except Exception as e:
        messagebox.showerror("Error", f"Could not play video: {e}")


def view_model_info(tree):
    """Display information about the face model"""
    selected = tree.selection()
    if not selected:
        return

    item = tree.item(selected[0])
    values = item['values']

    # Find the filepath column
    filepath = None
    for value in values:
        if isinstance(value, str) and os.path.exists(value) and value.endswith('.npy'):
            filepath = value
            break

    if not filepath or not os.path.exists(filepath):
        messagebox.showerror("Error", "Could not find the face model file")
        return

    try:
        face_data = np.load(filepath, allow_pickle=True)
        info_window = tk.Toplevel()
        info_window.title("Face Model Information")
        info_window.geometry("400x300")

        info_text = f"File: {os.path.basename(filepath)}\n"
        info_text += f"Size: {os.path.getsize(filepath)} bytes\n"
        info_text += f"Created: {datetime.fromtimestamp(os.path.getctime(filepath))}\n"
        info_text += f"Modified: {datetime.fromtimestamp(os.path.getmtime(filepath))}\n"
        info_text += f"Number of face samples: {len(face_data)}\n"

        text_area = tk.Text(info_window, wrap=tk.WORD)
        text_area.insert(tk.END, info_text)
        text_area.config(state=tk.DISABLED)
        text_area.pack(fill=tk.BOTH, expand=True)
    except Exception as e:
        messagebox.showerror("Error", f"Could not load face model: {e}")


def delete_file(tree, table_name):
    """Delete the selected file from disk and database"""
    selected = tree.selection()
    if not selected:
        return

    item = tree.item(selected[0])
    values = item['values']

    if len(values) < 1:
        messagebox.showerror("Error", "No item selected")
        return

    item_id = values[0]  # ID is always the first column

    # Find the filepath column
    filepath = None
    for value in values:
        if isinstance(value, str) and (os.path.exists(value) or value.startswith(os.getcwd())):
            filepath = value
            break

    if not filepath:
        messagebox.showerror("Error", "Could not determine file path")
        return

    if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete this {table_name[:-1]}?"):
        # Delete from database
        conn = sqlite3.connect('anveksha.db')
        cursor = conn.cursor()
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
        conn.commit()
        conn.close()

        # Delete file from disk if it exists
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                messagebox.showinfo("Success", "File deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {e}")
        else:
            # Just remove from database if file doesn't exist
            messagebox.showinfo("Success", "Entry removed from database (file not found on disk)")

        # Refresh the treeview
        load_data(tree, table_name)


def delete_files_from_database():
    """
    Delete files from the database and their physical files from disk
    """
    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    # Only delete if user confirms
    if not messagebox.askyesno("Confirm Database Cleanup",
                               "Are you sure you want to delete all files from the database and disk?"):
        conn.close()
        return

    # Get all files from database
    cursor.execute("SELECT filepath FROM screenshots")
    screenshot_files = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT filepath FROM videos")
    video_files = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT filepath FROM logs")
    log_files = [row[0] for row in cursor.fetchall()]

    # Delete physical files first
    deleted_count = 0
    for filepath in screenshot_files + video_files + log_files:
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {filepath}: {e}")

    # Delete all records from database tables
    cursor.execute("DELETE FROM screenshots")
    cursor.execute("DELETE FROM videos")
    cursor.execute("DELETE FROM logs")

    conn.commit()
    conn.close()

    messagebox.showinfo("Database Cleanup Complete",
                        f"Deleted {deleted_count} physical files and cleared all database records.")


def get_latest_face_model():
    """
    Retrieve the most recent face model from the database
    Returns: filepath to the face model, or None if not found
    """
    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    # Get the most recent face model
    cursor.execute("SELECT filepath FROM face_models ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()

    conn.close()

    if result:
        filepath = result[0]
        if os.path.exists(filepath):
            return filepath

    return None


def delete_physical_files(keep_database_records=True):
    """
    Delete physical files from disk but keep their records in the database
    """
    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    # Get all files from database
    cursor.execute("SELECT id, filepath FROM screenshots")
    screenshot_files = cursor.fetchall()

    cursor.execute("SELECT id, filepath FROM videos")
    video_files = cursor.fetchall()

    cursor.execute("SELECT id, filepath FROM logs")
    log_files = cursor.fetchall()

    # Only delete if user confirms
    if not messagebox.askyesno("Confirm File Deletion",
                               "Are you sure you want to delete all physical files while keeping their database records?"):
        conn.close()
        return

    deleted_count = 0

    # Process all file types
    for file_type, files in [
        ("screenshots", screenshot_files),
        ("videos", video_files),
        ("logs", log_files)
    ]:
        for file_id, filepath in files:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                    deleted_count += 1

                    # Update database to mark file as deleted but keep the record
                    if keep_database_records:
                        cursor.execute(
                            f"UPDATE {file_type} SET description = COALESCE(description, '') || ' [Physical file deleted]' WHERE id = ?",
                            (file_id,))
                except Exception as e:
                    print(f"Error deleting {filepath}: {e}")

    conn.commit()
    conn.close()

    messagebox.showinfo("Cleanup Complete",
                        f"Deleted {deleted_count} physical files. Database records have been maintained and marked.")


def save_face_model_to_db(model_data):
    """Save face model data directly to database as binary data"""
    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    # Convert numpy array to binary
    model_binary = model_data.tobytes()

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Store model in database
    cursor.execute('''
    INSERT INTO face_models (model_data, timestamp, description) 
    VALUES (?, ?, ?)
    ''', (model_binary, timestamp, "Face model trained"))

    conn.commit()
    conn.close()

    return True


def get_latest_face_model_from_db():
    """Retrieve the latest face model directly from database"""
    conn = sqlite3.connect('anveksha.db')
    cursor = conn.cursor()

    cursor.execute("SELECT model_data FROM face_models ORDER BY timestamp DESC LIMIT 1")
    result = cursor.fetchone()

    conn.close()

    if result:
        # Convert binary data back to numpy array
        model_binary = result[0]
        model_shape = (-1, 100 * 100)  # Assuming 100x100 face images flattened

        # Convert bytes back to numpy array
        face_data = np.frombuffer(model_binary, dtype=np.float32).reshape(model_shape)
        return face_data

    return None