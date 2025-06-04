# 🛡️ Anveksha

**Anveksha** is a desktop activity monitoring and logging application built using Python and PyQt. It is designed for secure user activity tracking with features like facial recognition login, real-time screenshot capturing, OCR-based text extraction, and keylogging — all managed from a user-friendly GUI.

---

## 📌 Features

- 🔐 **Facial Recognition Login**
  - First-time launch: Admin face registration.
  - Later logins: Face recognition-based authentication.

- 🖼️ **Screenshot Capture**
  - Periodically captures desktop screenshots.
  - Works silently in the background.

- 🧠 **OCR (Optical Character Recognition)**
  - Extracts readable text from screenshots.
  - Dependent on screenshot capture being enabled.

- ⌨️ **Keylogger**
  - Captures and logs all keystrokes securely.
  - Can be toggled on/off from the GUI.

- 🗂️ **Logs Section**
  - Displays logs of previous sessions, including timestamps, keys logged, and OCR content.

- ⚙️ **Settings Page**
  - Toggle features like:
    - Enable/Disable Keylogger
    - Enable/Disable Screenshots (SS)
    - Enable/Disable OCR (OCR depends on SS being enabled)

---

## 🛠️ Technologies Used

- **Frontend:** PyQt5
- **Backend:** Python
- **Libraries:** OpenCV, Pytesseract, Keyboard, Pillow, SQLite3

---

## 🚀 Getting Started

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/anveksha.git
    cd anveksha
    ```

2. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python main.py
    ```

---

## 📁 Project Structure

```
anveksha/
│
├── assets/               # Images, icons, and model files
├── modules/              # Keylogger, OCR, Screenshot, FaceAuth
├── logs/                 # Saved logs and extracted OCR text
├── gui/                  # PyQt5 UI files
├── main.py               # Entry point
└── README.md
```

---

## 🔐 Security Notes

- All data is stored locally.
- Ensure appropriate permissions are set for sensitive files.
- Do not run this application on systems without user consent.

---

## 📃 License

This project is for educational and ethical use only. Licensed under the MIT License.

---

## ✍️ Author

**Rishi Desai**  
[GitHub](https://github.com/rishidesai2545) | [LinkedIn](https://linkedin.com/in/rishidesai2545)

