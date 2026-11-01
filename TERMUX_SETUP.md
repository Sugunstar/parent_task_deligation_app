# 📱 Running LevelUp PWA on Android via Termux

This guide walks you through running the entire **LevelUp Parental Task Delegation App** locally on your Android device using **Termux**.

---

## 1. Prerequisites (on your Android Phone)

> [!IMPORTANT]
> Install **Termux from F-Droid** (do **NOT** use the Google Play Store version, which is obsolete and unmaintained).
> - [Download Termux on F-Droid](https://f-droid.org/en/packages/com.termux/)

---

## 2. Termux Environment Setup

Open Termux and execute the following commands:

```bash
# Update package repositories
pkg update && pkg upgrade -y

# Install Python and Git
pkg install python git -y

# (Optional) Install Termux API for native hardware integration
pkg install termux-api -y
```

---

## 3. Clone / Copy the Project to Termux

If copying via storage or cloning from git:
```bash
# Allow storage access if copying files from your phone's storage
termux-setup-storage

# Navigate to your preferred directory
cd ~

# If cloning:
# git clone <your-repo-url> levelup
# cd levelup/backend

# If copied to internal storage (e.g. Downloads/backend):
# cp -r ~/storage/downloads/backend ~/levelup-backend
# cd ~/levelup-backend
```

---

## 4. Install Dependencies

Inside the `backend/` directory:

```bash
cd backend

# Create and activate a Python virtual environment
python -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

> [!TIP]
> The requirements are lightweight (Flask, SQLAlchemy, Pydantic, python-dotenv, google-genai). Heavy local AI like PyTorch/Whisper is made completely optional and lazy-loaded, ensuring quick installation on mobile NPUs/CPUs.

---

## 5. Configure API Keys

Edit or create the `.env` file:

```bash
nano .env
```

Ensure your keys are populated:
```env
# Gemini API Key (for intelligent intent classification & emergency triage)
GEMINI_API_KEY=your_gemini_api_key_here

# Sarvam API Key (for Speech-to-Text — optional, or use audio files)
SARVAM_API_KEY=your_sarvam_api_key_here

# Port and Secret Key
PORT=8000
SECRET_KEY=your_custom_secret_key
```

Save and exit in nano (`Ctrl+O`, `Enter`, `Ctrl+X`).

---

## 6. Run the Application

Start the Flask server:

```bash
python main.py
```

You will see:
```text
Starting server on http://0.0.0.0:8000
```

---

## 7. Install & Use as a Progressive Web App (PWA)

1. Open **Google Chrome** (or any Chromium browser) on your phone.
2. Navigate to:
   ```text
   http://localhost:8000
   ```
   *(Or if accessing from a computer/tablet on the same Wi-Fi network, navigate to `http://<your-phone-ip>:8000`)*
3. **Install the PWA**:
   - In Chrome, tap the three dots **(⋮)** in the top right.
   - Tap **"Add to Home screen"** or **"Install app"**.
   - An icon called **LevelUp** will be added to your Android home screen and app drawer.
4. When opened from the home screen, it launches in **full-screen standalone mode** without browser address bars, giving you a native app feel.

---

## 8. App Features in MVP

- **Home (`/`)**: Manage child profiles (Name, Phone number, Age, Backup Emergency Contact).
- **Record & Process (`/record`)**:
  - Live in-browser microphone recording with HTML5 `MediaRecorder`.
  - Audio file upload fallback (WAV, MP3, WebM, OGG, M4A).
  - One-tap intent extraction using Gemini API with safe local rule-based fallback.
  - Interactive **Accept / Decline** task card.
- **Task Review (`/task/<id>`)**: View transcript, estimated cost, extracted items, and approve/decline.
- **Task History (`/history`)**: Real-time log of all requests with status tags (`Pending`, `Executed`, `Declined`, `Failed`).
- **Emergency Triage (`/emergency/<id>`)**: Instant high-priority alert when distress keywords are detected, with one-tap parental acknowledgement and automated backup contact escalation timer.
