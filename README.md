# AI-Powered Parental Task Delegation App

Welcome to the AI-Powered Parental Task Delegation App! This project is designed to help parents manage tasks (like ordering food or booking a cab) requested by children who do not have independent internet access. 

By simply making a standard phone call to the parent, the application will automatically transcribe the call, extract the task intent using AI (OpenAI Whisper + GPT-4), and present a simple "Accept/Decline" summary card to the parent. It also includes an emergency detection system that bypasses normal approvals to alert the parent immediately if distress is detected.

## 📚 Documentation

The project documentation is split into three main files to help you run, understand, and build upon the application:

### 1. [How to Run the Application](./RUN_INSTRUCTIONS.md)
Start here if you want to get the project up and running. This guide provides detailed, step-by-step instructions on:
- Setting up the Python virtual environment and installing dependencies.
- Configuring your OpenAI API keys.
- Starting the Flask backend server.
- Opening and running the Android application via Android Studio.

### 2. [Developer Guide](./DEVELOPER_GUIDE.md)
Read this if you want to understand how the system is built. This guide offers an in-depth look at the architecture:
- **Backend**: Explains the Flask routing, SQLAlchemy models, Pydantic schemas, and the AI service pipeline.
- **Frontend**: Details the Android Native (Java) structure, including Retrofit networking, call capture fallbacks, and FCM push notification handling.

### 3. [Known Limitations](./KNOWN_LIMITATIONS.md)
Review this document to understand the technical constraints of the current Phase 1 and Phase 2 prototypes. It covers important details regarding:
- The reliability of automatic, silent call recording across different Android OEMs.
- The limitations of GPS tracking for offline feature phones during emergencies.
- What aspects of the system (like external API executions and voice biometrics) are currently mocked for prototyping.

---

### Tech Stack Summary
- **Backend**: Python, Flask, SQLAlchemy (SQLite), Pydantic
- **AI**: OpenAI Whisper (STT), GPT-4o (Structured Intent Extraction)
- **Frontend**: Android (Java), Retrofit, Firebase Cloud Messaging (FCM)
