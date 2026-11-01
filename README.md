# 📋 LevelUp — AI-Powered Parental Task Delegation PWA

An AI-driven task delegation companion designed to help parents effortlessly handle requests (food ordering, cab booking) from children who lack independent internet access, while providing instant triage for emergencies.

The application operates as a standalone, mobile-first **Progressive Web App (PWA)** that runs directly on an Android device via **Termux** or any standard Python server.

---

## ⚡ Core Value Loop

```
Child's Voice Request → In-Browser / Upload Audio → STT Transcription → Gemini Intent Understanding → 1-Tap Approval Card → Execution
                                                                      ↳ Distress Detected → EMERGENCY BYPASS
```

* **Zero Internet Required for Child**: Child interacts naturally via normal voice call.
* **Low Mental Load for Parent**: Instead of opening food/ride apps manually, parent gets a concise summary card with single-tap **Accept / Decline**.
* **Safety First**: Emergencies bypass approval completely, triggering persistent alerts, auto-escalation, and location logging.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask, SQLAlchemy, SQLite, Pydantic
- **AI & STT**: Google Gemini API (`gemini-2.5-flash`), Sarvam STT API, local safety keyword fallback
- **Frontend**: Jinja2, Vanilla JavaScript, HTML5 MediaRecorder API, [Pico CSS](https://picocss.com/) (classless, ~10KB)
- **PWA Features**: Web App Manifest (`display: standalone`), Service Worker offline caching, Web Notifications
- **Deployment**: Local Android phone hosting via **Termux** or standard Linux/macOS/Windows machine

---

## 📚 Documentation Index

| Guide | Description |
|---|---|
| **[Termux Setup Guide](./TERMUX_SETUP.md)** | Step-by-step instructions to run and install the PWA on Android via Termux |
| **[Run Instructions](./RUN_INSTRUCTIONS.md)** | Development guide for running on PC or testing end-to-end flows |
| **[Developer Guide](./DEVELOPER_GUIDE.md)** | Full architectural breakdown of database models, services, APIs, and PWA structure |
| **[Known Limitations](./KNOWN_LIMITATIONS.md)** | Technical constraints, trade-offs, and future milestones |
| **[Planning Docs](./planning/)** | Original masterplans and conceptual design specifications |

---

## 🚀 Quick Start (Local PC)

```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
Visit `http://localhost:8000` in your browser.
