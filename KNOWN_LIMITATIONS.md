# Known Limitations & Technical Constraints

This document outlines the known technical constraints and design trade-offs in the MVP prototype of the Parental Task Delegation App (LevelUp PWA).

---

## 1. Call Audio Ingestion (Browser vs. System Call Interception)

In this MVP phase, the application runs as a **Progressive Web App (PWA)** hosted locally on Termux or accessed via the phone's browser.

* **Limitation**: Web applications running in standard mobile browsers cannot passively intercept cellular phone calls or record cellular audio in the background without explicit user interaction due to Android sandboxing and OS-level privacy protections.
* **MVP Implementation**: Audio is captured actively via the HTML5 `MediaRecorder` API (one-tap voice recording in the browser) or uploaded as an audio file (`.wav`, `.mp3`, `.webm`, `.ogg`, `.m4a`).
* **Future Enhancement (Phase 3)**: A native companion service holding the Android `Default Dialer` or Accessibility role can be integrated to passively dump call recordings into a local folder monitored by the Flask server.

---

## 2. Emergency Location Tracking for Basic Phones

During detected emergencies, the system prepares location telemetry alongside the distress alert.

* **Limitation**: When a child calls from an offline basic feature phone (keypad phone without GPS or cellular data enabled), the child's device cannot deliver GPS coordinates to the parent's server.
* **Graceful Degradation**: The system logs `location_lat: null` and `location_lng: null`. The parent immediately receives the high-priority alarm notification with the verbatim transcript and distress reason, bypassing normal task approval flows.
* **Workaround**: An optional SMS-based cell-tower triangulation or SMS location-responder can be explored for feature phones in future milestones.

---

## 3. Real-World Third-Party Platform Execution

When a parent approves a task (e.g. food delivery or ride booking):

* **Limitation**: Consumer platforms like Zomato, Swiggy, Uber, and Ola do not offer public, open developer APIs for third-party automated order placement and payment execution without institutional partnerships.
* **MVP Implementation**: Real-world execution is safely simulated via `services/mock_execution.py`, replicating network delays, realistic restaurant/destination responses, and state persistence (`pending` → `executed` / `failed`).

---

## 4. Voice Biometrics

Caller verification across children:

* **Limitation**: Local voice biometric verification (e.g., using Resemblyzer or WavLM embeddings) requires compiling native C++ audio libraries and PyTorch on mobile ARM architectures, which adds unnecessary footprint to a quick-running Termux environment.
* **MVP Implementation**: The prototype scaffolds the enrollment and similarity check endpoints (`voice_biometrics.py`) while relying on phone-number binding and parent approval cards for identity safety.

---

## 5. Escalation Delivery

When an emergency alert is not acknowledged within the configurable window (default 3 minutes):

* **Limitation**: Cellular SMS delivery directly from Termux requires the `termux-api` package and Android `SEND_SMS` runtime permission, or an external cloud SMS gateway (e.g., Twilio).
* **MVP Implementation**: Background thread escalation updates the database record (`backup_contact_notified = True`) and logs the high-priority alert. Integration with `termux-sms-send` or Twilio is ready to be hooked into `api/emergency.py:escalate_to_backup()`.
