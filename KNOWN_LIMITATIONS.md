# Known Limitations & Technical Constraints

This document outlines the known technical limitations in the Phase 1 & 2 prototype of the Parental Task Delegation App.

## 1. Automatic Call Recording Reliability
The application attempts to automatically capture the phone call audio natively on the device when a call from a registered child is detected.

**Limitation:** Automatic, silent call recording is heavily restricted in modern Android (Android 10+). 
- To function, the app typically needs to hold the `Default Dialer` role.
- Even with the default dialer role, behavior varies widely across OEMs (Samsung, Xiaomi, Pixel).
- In some regions and carriers, call recording is fundamentally blocked by the OS framework.

**Workaround/Fallback:** 
If the `NativeCallRecordingSource` fails to produce an audio file after a call ends, the app falls back to the `ManualUploadAudioSource` flow. This triggers a lightweight prompt asking the parent to manually share the call recording from their device's native voice recorder app into this application.

## 2. Emergency Location Tracking
In the event of an emergency (distress detected via Voice/STT), the system attempts to share the child's last known location with the parent and backup contacts.

**Limitation:** 
The child's phone must have some digital capability to provide GPS data. A completely offline basic keypad phone (feature phone without data or SMS location sharing capabilities) cannot provide GPS coordinates to the parent's app. 

**Workaround:** 
For children using feature phones without location sharing capabilities, the location tracking feature will fail gracefully. The parent will still receive the emergency alert and the transcript, but the `location_lat` and `location_lng` fields will be null. A lightweight SMS-based location responder on the child's phone could be explored as a future enhancement for feature phone users.

## 3. Mocked Integrations
- **Task Execution:** Real integrations with Zomato, Uber, etc., are mocked via `MockExecutionService` simulating delays and success outcomes.
- **Biometrics:** `voice_biometrics.py` simulates the Resemblyzer vectorization and cosine similarity logic to avoid heavy native ML dependencies in this prototype stage.
- **SMS Escalation:** Backup contact escalation currently simulates an FCM push notification instead of a real Twilio SMS.
