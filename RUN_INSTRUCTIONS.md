# How to Run the Application

This guide covers running the **LevelUp Parental Task Delegation PWA** on a local development machine (Linux/macOS/Windows) or directly on an Android device via Termux.

---

## Option 1: Running on a Development Computer (Linux / macOS / Windows)

### 1. Prerequisites
- **Python 3.10+** installed.
- (Optional) `uv` or standard `python -m venv`.

### 2. Setup Virtual Environment
Navigate to the `backend` folder:
```bash
cd backend

# Using uv (fastest)
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt

# Or using standard python
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure API Keys
Verify or update keys in `backend/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
SARVAM_API_KEY=your_sarvam_api_key_here
PORT=8000
SECRET_KEY=dev-secret-key
```

### 4. Start the Application
```bash
python main.py
```
Open your browser to:
- **Local machine**: `http://localhost:8000`
- **Phone on the same Wi-Fi**: `http://<your-computer-ip>:8000`

---

## Option 2: Running Directly on Android via Termux

For complete instructions on running the entire application natively on your phone without a PC, refer to:
👉 **[TERMUX_SETUP.md](./TERMUX_SETUP.md)**

Quick summary for Termux:
```bash
pkg update && pkg install python git -y
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Then open Chrome on Android, visit `http://localhost:8000`, and tap **"Add to Home Screen"** or **"Install app"**.

---

## 3. Testing the Application End-to-End

1. **Register a Child**:
   - Go to Home (`/`).
   - Tap `+ Add Child`, enter a name (e.g., "Aarav"), phone number, and age.
2. **Record Audio**:
   - Tap `Record` in the bottom navigation bar.
   - Select your registered child.
   - Tap `Hold to Record`, speak your request (e.g. *"Mom, can you order a paneer pizza from Domino's?"*), then stop.
   - Tap `Process Audio`.
3. **Review & Decide**:
   - The AI displays a plain-language summary card with estimated cost.
   - Tap **Approve** to execute or **Decline** to cancel.
4. **Emergency Test**:
   - Record distress audio (e.g. *"Mom I am hurt and scared please help me!"*).
   - The system detects the emergency, bypasses approval, alerts the parent, and starts the backup contact escalation timer.
