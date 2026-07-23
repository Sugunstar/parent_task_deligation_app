# How to Run the Application

This guide provides step-by-step instructions on how to run both the Python Flask Backend and the Android Frontend locally for development and testing.

---

## 1. Running the Flask Backend

The backend is a Python application that uses Flask, SQLAlchemy (SQLite), and OpenAI.

### Prerequisites
- Python 3.10 or higher installed.
- An OpenAI API Key (for Whisper STT and GPT-4 logic).

### Setup Steps
1. **Navigate to the Backend Directory:**
   Open a terminal and navigate to the backend folder:
   ```bash
   cd child_parent_system/backend
   ```

2. **Create a Virtual Environment:**
   It is highly recommended to use a virtual environment to isolate dependencies.
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   Install the required Python packages from `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables:**
   The AI service requires an OpenAI API key to function correctly. Set it in your terminal:
   ```bash
   export OPENAI_API_KEY="your-real-api-key-here"
   ```
   *(Alternatively, you can create a `.env` file in the backend directory and python-dotenv will load it automatically).*

5. **Run the Server:**
   Start the Flask development server:
   ```bash
   python main.py
   ```
   You should see output indicating that the server is running on `http://127.0.0.1:8000`. The SQLite database (`parental_task_app.db`) will be automatically created in the backend folder upon first run.

---

## 2. Running the Android Frontend

The frontend is a Native Android app written in Java.

### Prerequisites
- **Android Studio** installed on your machine.
- An **Android Emulator** running API 26 or higher, OR a physical Android device connected via USB debugging.

### Setup Steps
1. **Open the Project in Android Studio:**
   - Launch Android Studio.
   - Select **File > Open**.
   - Navigate to and select the `child_parent_system/android/app` directory.
   - Wait for Android Studio to sync the Gradle files and download required dependencies.

2. **Configure Localhost Networking (Emulator Only):**
   - The app's `RetrofitClient` is hardcoded to `http://10.0.2.2:8000/`. This is the special alias used by the Android Emulator to connect to your computer's `127.0.0.1` localhost.
   - *Note: If you are testing on a physical device, you must change the `BASE_URL` in `RetrofitClient.java` to your computer's actual local IP address (e.g., `http://192.168.1.5:8000/`).*

3. **Build and Run:**
   - Click the green **Run (Play)** button in the top toolbar of Android Studio.
   - Select your emulator or physical device.
   - The app will compile and install on the device.

### Note on Firebase (FCM)
Push notifications via `FcmService` require a valid `google-services.json` file. To fully test push notifications:
1. Create a project in the Firebase Console.
2. Register the Android app with the package name `com.example.parentaltaskapp`.
3. Download the `google-services.json` file and place it in the `android/app/` directory.
4. Add the `com.google.gms.google-services` plugin to your `build.gradle` (omitted in scaffolding for simplicity).
