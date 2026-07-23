# Developer Guide

Welcome to the Developer Guide for the AI-Powered Parental Task Delegation App. This document provides an in-depth breakdown of the project architecture, directory structure, and the purpose of individual files and functions.

---

## Architecture Overview

The system is split into two primary layers:
1. **Flask Backend (`/backend`)**: A REST API responsible for handling audio uploads, communicating with OpenAI (Whisper + GPT-4), managing the database, and triggering task executions (mocked) or emergency escalations.
2. **Android Frontend (`/android`)**: A native Java Android app installed *only* on the parent's phone. It captures child call recordings (or accepts manual uploads), interacts with the backend, and displays Approval/Emergency push notifications.

---

## 1. Backend (`/backend`)

The backend is built with Python, Flask, SQLAlchemy (SQLite), and Pydantic.

### Core Configuration
- **`main.py`**: The application entry point. 
  - Initializes the Flask application (`app = Flask(__name__)`).
  - Registers the API routing Blueprints (calls, tasks, children, emergency).
  - Triggers SQLAlchemy to create the database tables if they do not exist.
  - Runs the local development server on port 8000.
- **`database.py`**: Handles the SQLAlchemy engine setup. Defines the `SQLALCHEMY_DATABASE_URL` (currently a local SQLite file) and exposes the `Base` declarative class used by the models.
- **`requirements.txt`**: Python dependencies including `flask`, `sqlalchemy`, `pydantic`, and `openai`.

### Data Layer
- **`models.py`**: Defines the SQLAlchemy database tables.
  - `Parent`: Stores parent account info and Firebase auth IDs.
  - `ChildProfile`: Stores child info, their phone number, and auto-approval strictness rules.
  - `TaskRecord`: Logs transcribed calls, GPT-4 task summaries, and the parent's accept/decline decisions.
  - `EmergencyEvent`: Logs identified emergencies and escalation tracking.
- **`schemas.py`**: Pydantic models used to strictly validate incoming JSON requests and format API responses (e.g., `ChildProfileCreate`, `IntentResponse`).

### API Endpoints (`/api`)
Flask Blueprints mapping URLs to specific logical functions.
- **`calls.py`**:
  - `POST /calls/upload`: Accepts the multipart audio file upload from the Android app.
  - `POST /calls/<id>/process`: The core processing pipeline. It currently mocks receiving the transcript, but in production, it routes the transcript through the `ai_service` to extract the intent and evaluate emergencies.
- **`tasks.py`**:
  - `POST /tasks/<id>/decision`: Accepts the parent's decision ("approved" or "declined"). If approved, it triggers the `MockExecutionService`.
- **`children.py`**:
  - `POST /children/`: Endpoint to register a new `ChildProfile`.
  - `GET /children/<id>/tasks`: Fetches task history for a specific child.
  - `POST /children/<id>/enroll-voice`: Endpoint for Phase 2 voice biometric enrollment.
- **`emergency.py`**:
  - `POST /emergency/<id>/acknowledge`: Allows the parent to acknowledge an emergency.
  - Contains background timer logic (`start_escalation_timer`) to escalate to a backup contact if the parent doesn't respond.

### Services Layer (`/services`)
Business logic abstracted away from the API routes.
- **`ai_service.py`**: 
  - `transcribe_audio()`: Calls OpenAI's Whisper API to convert audio to text.
  - `extract_intent_from_transcript()`: Uses OpenAI's `gpt-4o` with Structured JSON Output mode to reliably parse the transcript into a strict Pydantic model (`IntentResponse`). It categorizes the task (food/cab/none) and detects distress for the emergency bypass.
- **`mock_execution.py`**:
  - `execute_task()`: Simulates network latency (time.sleep) and returns a success status. Designed to mock Zomato/Uber integrations safely during the prototype phase.
- **`voice_biometrics.py`**:
  - Phase 2 mock implementations of `compute_voice_embedding()` and `verify_voice()` simulating Resemblyzer cosine similarity logic.

---

## 2. Android Frontend (`/android`)

The frontend is a Native Android application written in Java.

### Core Configuration
- **`build.gradle`**: Contains all Android dependencies, including Retrofit for networking, Google Material components, and Firebase (FCM + Auth). Configured for `minSdk 26`.
- **`AndroidManifest.xml`**: Defines application permissions (Internet, Record Audio, Read Phone State) and registers all Activities, Receivers, and Services.

### Networking (`/network`)
- **`RetrofitClient.java`**: Configures the Retrofit instance pointing to the local Flask server (`http://10.0.2.2:8000/` for emulators).
- **`ApiService.java`**: The Retrofit Interface mapping Java methods to the Flask API endpoints (e.g., `@Multipart @POST("calls/upload")`).

### User Interface (`/ui`)
- **`home/HomeActivity.java`**: The main launch screen for managing child profiles.
- **`history/HistoryActivity.java`**: Displays the log of past task requests.
- **`profile/ProfileActivity.java`**: Parent account settings.
- **`approval/ApprovalCardActivity.java`**: Triggered via push notification. Displays the AI-generated task summary with Accept/Decline buttons. Calls the `/tasks/<id>/decision` endpoint.
- **`emergency/EmergencyAlertActivity.java`**: A high-priority, full-screen activity triggered during emergencies.

### Features
- **`call/ManualUploadAudioSource.java`**: A fallback class that uploads an existing audio file from the device storage to the backend. Used when native silent call recording is blocked by the Android OS/OEM.
- **`notifications/FcmService.java`**: Extends `FirebaseMessagingService`. Listens for incoming push notifications from the backend.
  - `showApprovalNotification()`: Builds a standard notification that opens `ApprovalCardActivity`.
  - `showEmergencyNotification()`: Builds a max-priority alarm notification that ignores Do Not Disturb and launches `EmergencyAlertActivity` immediately.
