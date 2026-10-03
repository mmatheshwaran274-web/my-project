# BLIND ASSIST 👁️
> **“Smart Assistance for Independent Living”**

Blind Assist is a full-stack, accessible web application designed to empower visually impaired individuals. The platform integrates voice recognition, optical character recognition (OCR), computer vision object detection, GPS geolocation assistance, and instant emergency dispatch — all built with WCAG AAA accessibility standards, high-contrast modes, dynamic font scaling, bilingual English & Tamil support, and screen-reader optimizations.

---

## 🌟 Key Features

1. **🎤 Voice Assistant (Web Speech API)**
   - Fully interactive microphone interface with voice command interpretation.
   - Natural spoken feedback via the browser `SpeechSynthesis` API.
   - Commands: *"Open dashboard"*, *"Read text"*, *"Detect object"*, *"My location"*, *"Emergency"*, *"Open settings"*, *"Show history"*.
   - Graceful fallback input for environments without Web Speech recognition.

2. **📷 Object Detection (OpenCV & Computer Vision)**
   - Live camera capture (`getUserMedia`) and image file upload.
   - Modular AI service (`services/vision_service.py`) supporting real YOLOv8 models alongside a realistic, zero-dependency demo fallback.
   - Natural voice descriptions (e.g., *"I can see a person, chair, laptop, and bottle"*).

3. **📖 Text Reader / OCR (Tesseract OCR & Pillow)**
   - Document scanning via device camera or photo upload.
   - Preprocessing with OpenCV (bilateral filtering, adaptive thresholding) for crisp text capture.
   - Audio playback controls: Read Aloud, Pause, Resume, and Stop.
   - Fallback engine providing sample text output if Tesseract is not yet installed on the host machine.

4. **📍 Location Assistance (Browser Geolocation API)**
   - High-accuracy GPS coordinate extraction.
   - Spoken location summaries informing users of their latitude, longitude, and accuracy radius.
   - Direct OpenStreetMap navigation link.

5. **🚨 Emergency Assistance System**
   - High-visibility tactile panic button with accessible modal confirmation.
   - GPS coordinate logging into the database.
   - Displays registered family/caregiver emergency contact and immediate safety guidelines.
   - Modular backend SMS hook for future Twilio / GSM integration.

6. **📜 Activity History & User Profile**
   - Persistent audit log of all voice commands, scans, readings, and emergencies.
   - Editable profile details with phone and emergency contact updates.

7. **⚙️ Universal Accessibility & Tamil Language Support (தமிழ்)**
   - Strict WCAG AAA High-Contrast Mode (pure black `#000000` & yellow `#FFFF00`).
   - Dynamic font scaling (Small, Medium, Large, Extra Large).
   - Adjustable speech rate (0.5x, 1.0x, 1.5x, 2.0x).
   - Instant language switching between English and Tamil (தமிழ்).
   - Global keyboard shortcuts:
     - `Alt + H`: Toggle High-Contrast Mode
     - `Alt + M`: Open Voice Assistant
     - `Alt + E`: Open Emergency Screen
     - `Alt + D`: Return to Dashboard
     - `Alt + S`: Stop Audio Speech

---

## 🛠️ Technology Stack

- **Frontend**: HTML5, Vanilla CSS3 (custom accessibility design system), Vanilla JavaScript (ES6+), Web Speech API, SpeechSynthesis API, MediaDevices Camera API, Geolocation API.
- **Backend**: Python 3.11+, Flask, Flask-SQLAlchemy, Flask-Login, Werkzeug (PBKDF2/scrypt password hashing).
- **Database**: SQLite, SQLAlchemy ORM.
- **Computer Vision & OCR**: Pillow (PIL), OpenCV (`opencv-python-headless`), Tesseract OCR (`pytesseract`).
- **Testing**: `pytest`.

---

## 📂 Project Structure

```
blind-assist/
│
├── app.py                     # Flask application factory & server entry point
├── config.py                  # Environment & database configurations
├── requirements.txt           # Project dependencies
├── README.md                  # Documentation and setup instructions
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
│
├── instance/
│ └── blind_assist.db          # Auto-generated SQLite database
│
├── database/
│ ├── __init__.py              # Database package exports
│ ├── database.py              # SQLAlchemy extension & init_db()
│ └── models.py                # User, UserSettings, ActivityHistory, EmergencyEvent
│
├── routes/
│ ├── __init__.py              # Activity recording helper
│ ├── auth.py                  # Login, registration, logout routes & API
│ ├── dashboard.py             # Dashboard, landing, and profile routes
│ ├── voice.py                 # Voice assistant routes & API
│ ├── vision.py                # Object detection routes & API
│ ├── ocr.py                   # OCR text reader routes & API
│ ├── location.py              # Geolocation routes & API
│ ├── emergency.py             # Emergency activation routes & API
│ ├── history.py               # Activity history routes & API
│ └── settings.py              # Accessibility settings routes & API
│
├── services/
│ ├── __init__.py              # Services package exports
│ ├── voice_service.py         # Voice command parser & bilingual mapper
│ ├── vision_service.py        # Object detection service (YOLO hook + fallback)
│ ├── ocr_service.py           # OCR text extraction & preprocessing
│ └── location_service.py      # GPS formatting & OSM links
│
├── templates/
│ ├── base.html                # Main layout with header, footer, a11y skip links
│ ├── index.html               # Home landing page with hero & features
│ ├── login.html               # Accessible sign-in page
│ ├── register.html            # Registration with emergency contact
│ ├── dashboard.html           # Assistive dashboard with large clickable cards
│ ├── profile.html             # Profile & contact management
│ ├── settings.html            # Accessibility configuration panel
│ ├── voice.html               # Voice assistant microphone interface
│ ├── vision.html              # Object detection with camera feed
│ ├── ocr.html                 # Text reader with audio speech playback
│ ├── location.html            # Geolocation readout
│ ├── emergency.html           # Emergency panic button & confirmation
│ ├── history.html             # Activity audit log table
│ └── 404.html                 # Accessible 404 & error page
│
├── static/
│ ├── css/
│ │ ├── style.css              # Main modern accessible stylesheet
│ │ └── accessibility.css      # High-contrast, font scaling, screen reader styles
│ │
│ ├── js/
│ │ ├── main.js                # App initialization & card focus feedback
│ │ ├── accessibility.js       # SpeechSynthesis engine & Tamil translations
│ │ ├── voice.js               # Web Speech API recognition & routing
│ │ ├── vision.js              # Camera streaming & object detection
│ │ ├── ocr.js                 # Image snapshot & text reading audio controls
│ │ ├── location.js            # Geolocation GPS handler
│ │ └── emergency.js           # Emergency modal & dispatch logic
│ │
│ └── images/                  # Application graphic assets
│
├── uploads/                   # Runtime temporary image uploads
│
└── tests/
    ├── __init__.py
    ├── test_auth.py           # Auth, register, login, session tests
    ├── test_ocr.py            # OCR endpoint tests
    └── test_routes.py         # End-to-end API integration tests
```

---

## 🚀 Installation & Local Setup

### 1. Prerequisites
- **Python 3.11+** installed on your system.
- VS Code or your preferred editor.

### 2. Clone or Open the Project
Open the project directory in VS Code:
```bash
cd "c:\Users\ELCOT\Desktop\Blind assists"
```

### 3. Create and Activate Virtual Environment
On Windows (PowerShell or Command Prompt):
```powershell
python -m venv venv
.\venv\Scripts\activate
```

On macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Variables (Optional)
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```
Default configuration works out of the box with zero external configuration!

---

## 🏃 How to Run

Start the Flask development server:
```bash
python app.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 👤 Demo Login Instructions

1. Click **GET STARTED** or **Register** to create an account.
2. Enter your name, email, password, phone, and emergency contact.
3. Registration immediately signs you in and initializes default accessibility settings.
4. If you restart the server, you can log back in using your registered credentials.

---

## 📖 Feature Guide

### 1. How to Use the Voice Assistant
- Click the large microphone button on the **Voice Assistant** page or press <kbd>Spacebar</kbd>.
- Speak commands clearly into your microphone:
  - *"Open dashboard"*
  - *"Read text"*
  - *"Detect object"*
  - *"My location"*
  - *"Emergency"*
  - *"Open settings"*
  - *"Show history"*
- The system speaks back and navigates directly to the requested feature.

### 2. How to Use Object Detection
- Navigate to **Object Detection**.
- Click **Start Camera** to allow browser camera permissions.
- Point the camera toward surrounding objects and click **Capture & Detect**.
- The system highlights the detected objects and speaks the description aloud (e.g., *"I can see a person, chair, laptop, and bottle"*).
- Alternatively, click **Upload Image File** to analyze a photo saved on your disk.

### 3. How to Use the Text Reader (OCR)
- Navigate to **Read Text**.
- Position a document, mail, or book in front of your camera and click **Capture & Extract Text** (or upload an image).
- The system extracts the text and automatically begins reading it aloud.
- Use the **Pause**, **Resume**, and **Stop** buttons to control speech playback.

### 4. How to Use Location Assistance
- Navigate to **My Location**.
- Click **Get My Current Location**.
- Allow browser GPS location permission.
- The assistant speaks your coordinates and accuracy, and provides an OpenStreetMap link.

### 5. How to Use Emergency Assistance
- Click the large red **ACTIVATE EMERGENCY** button (or press <kbd>Alt + E</kbd>).
- A confirmation dialog appears to prevent accidental triggers.
- Click **CONFIRM EMERGENCY**.
- Incident coordinates are recorded in the database, your registered emergency contact is displayed, and calm voice instructions guide you on next steps.

---

## 🧪 Running Automated Tests

Run the complete test suite using `pytest`:
```bash
pytest
```
To run tests with detailed verbosity:
```bash
pytest -v
```

---

## 🔧 Connecting Real AI Models (Advanced)

### Connecting Ultralytics YOLOv8 for Object Detection:
1. Install Ultralytics:
   ```bash
   pip install ultralytics
   ```
2. Download YOLOv8 weights (e.g., `yolov8n.pt`).
3. `services/vision_service.py` is pre-configured with model hooks. Once `ultralytics` is installed, it will automatically load `yolov8n.pt` and perform real neural network inference!

### Installing System Tesseract OCR Engine:
1. Windows: Download the installer from [UB-Mannheim Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki).
2. Set `TESSERACT_CMD` in `.env` if installed in a custom directory:
   ```env
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   ```
3. If not installed, Blind Assist's built-in fallback automatically provides clean demonstration extractions without crashing.

---

## ❓ Troubleshooting

| Issue | Solution |
| :--- | :--- |
| **Microphone not working** | Ensure your browser has permission to access your microphone (`chrome://settings/content/microphone`). Use the fallback text input on the Voice page if needed. |
| **Camera not displaying** | Click "Start Camera" and allow browser camera permissions. Ensure no other application (like Zoom or Teams) is using the webcam. |
| **Location permission denied** | Allow location permissions in browser settings (`chrome://settings/content/location`). |
| **Speech synthesis silent** | Ensure your computer audio/speakers are unmuted and volume is up. Check in Settings that Voice Assistance is set to "ON". |
| **Database locked error** | SQLite database file is in `instance/blind_assist.db`. Ensure only one instance of `python app.py` is running. |

---

## 📜 License
Blind Assist is open-source under the **MIT License**. Free for educational, assistive, and non-commercial accessibility use.
