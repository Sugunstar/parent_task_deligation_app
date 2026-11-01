import os
import json
import logging
import requests
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

# ─── Lazy Whisper Loading ────────────────────────────────────────
# Whisper is heavy (torch dependency). Only load if actually needed
# and if the package is installed. On Termux, Sarvam API is primary
# so whisper may not even be installed.

_whisper_model = None
_whisper_load_attempted = False


def _get_whisper_model():
    """Lazily loads the whisper model on first use. Returns None if unavailable."""
    global _whisper_model, _whisper_load_attempted
    if _whisper_load_attempted:
        return _whisper_model
    _whisper_load_attempted = True
    try:
        import whisper
        _whisper_model = whisper.load_model("base")
        logger.info("Whisper model loaded successfully")
    except ImportError:
        logger.warning("openai-whisper not installed — Whisper fallback disabled")
    except Exception as e:
        logger.warning(f"Failed to load Whisper model: {e}")
    return _whisper_model


# ─── Sarvam API ──────────────────────────────────────────────────

SARVAM_API_URL = "https://api.sarvam.ai/speech-to-text-translate"


def transcribe_with_sarvam(file_path: str) -> str:
    """
    Transcribes audio using the Sarvam API.
    Reads the API key fresh each call so .env changes take effect without restart.
    Returns empty string on failure.
    """
    api_key = os.environ.get("SARVAM_API_KEY", "").strip()
    if not api_key or api_key == "your_sarvam_api_key_here":
        logger.info("Sarvam API key not configured, skipping")
        return ""

    try:
        with open(file_path, 'rb') as audio_file:
            files = {'file': (os.path.basename(file_path), audio_file, 'audio/wav')}
            headers = {'api-subscription-key': api_key}

            response = requests.post(
                SARVAM_API_URL,
                files=files,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                text = (
                    result.get('transcript', '')
                    or result.get('text', '')
                    or result.get('transcription', '')
                ).strip()

                if text:
                    logger.info(f"Sarvam transcription OK: {text[:60]}...")
                    return text
                else:
                    logger.warning("Sarvam returned empty transcription")
                    return ""
            else:
                logger.warning(f"Sarvam API error: {response.status_code} — {response.text[:200]}")
                return ""

    except requests.exceptions.RequestException as e:
        logger.warning(f"Sarvam API request error: {e}")
        return ""
    except Exception as e:
        logger.warning(f"Sarvam transcription error: {e}")
        return ""


def transcribe_with_whisper(file_path: str) -> str:
    """
    Transcribes audio using local Whisper model.
    Returns empty string if whisper is unavailable or fails.
    """
    model = _get_whisper_model()
    if model is None:
        return ""

    try:
        result = model.transcribe(file_path)
        text = result["text"].strip()
        if text:
            logger.info(f"Whisper transcription OK: {text[:60]}...")
            return text
        else:
            logger.warning("Whisper returned empty transcription")
            return ""
    except Exception as e:
        logger.warning(f"Whisper transcription error: {e}")
        return ""


def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio. Priority: Sarvam API → Whisper → empty string.
    Never returns a hardcoded fake transcript — the caller decides what to do on failure.
    """
    # Try Sarvam first (cloud, fast, supports Indian languages)
    transcript = transcribe_with_sarvam(file_path)
    if transcript:
        return transcript

    # Fall back to Whisper (local, heavier)
    transcript = transcribe_with_whisper(file_path)
    if transcript:
        return transcript

    logger.error(f"All transcription methods failed for {file_path}")
    return ""


# ─── Intent Extraction ──────────────────────────────────────────

class IntentResponse(BaseModel):
    category: str = Field(description="Must be 'food', 'cab', or 'none'")
    summary_text: str = Field(description="One plain sentence a busy parent can read in 2 seconds")
    details: Dict[str, Any] = Field(description="Details of the task (e.g., restaurant, cost)")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    is_emergency: bool = Field(description="True if distress, fear, pain, or safety threats are detected")
    emergency_reason: Optional[str] = Field(default=None, description="Reason for the emergency, or null")


# Emergency keywords — leading spaces stripped, matched as whole-ish substrings
EMERGENCY_KEYWORDS = [
    'help me', 'emergency', 'hurt', 'pain', 'scared', 'fear', 'afraid',
    'danger', 'stranger', 'attack', 'hit me', 'choke',
    "can't breathe", 'bleeding', 'blood', 'fire', 'smoke',
    'call 911', 'call police', 'ambulance', 'urgent', 'sos', 'distress',
    'kidnap', 'accident', 'dying', 'kill',
]

FOOD_KEYWORDS = [
    'pizza', 'burger', 'sandwich', 'food', 'eat', 'hungry', 'meal',
    'order', 'delivery', 'restaurant', 'mcdonalds', 'taco',
    'sushi', 'pasta', 'chicken', 'fries', 'biryani', 'dosa',
    'noodles', 'rice', 'snack', 'swiggy', 'zomato',
]

RESTAURANT_NAMES = [
    'domino', 'pizza hut', 'papa johns', 'mcdonald', 'burger king',
    "wendy's", 'taco bell', 'subway', 'kfc', 'swiggy', 'zomato',
]

CAB_KEYWORDS = [
    'uber', 'lyft', 'ola', 'taxi', 'cab', 'ride', 'transport',
    'pick up', 'pick me up', 'go to', 'need to go', 'drop me',
    'rapido', 'auto',
]


def _extract_intent_rule_based(transcript: str) -> IntentResponse:
    """
    Rule-based intent extraction. Fast, no API calls, works offline.
    """
    text = transcript.lower().strip()

    # ── Emergency check (highest priority) ──
    is_emergency = False
    emergency_reason = None
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in text:
            is_emergency = True
            emergency_reason = keyword
            break

    # ── Category classification ──
    category = "none"
    summary_text = "No actionable request detected"
    details: Dict[str, Any] = {}
    confidence = 0.6

    if any(kw in text for kw in FOOD_KEYWORDS):
        category = "food"
        restaurant = "Unknown Restaurant"
        for name in RESTAURANT_NAMES:
            if name in text:
                restaurant = name.title()
                break
        summary_text = f"Order food from {restaurant}"
        details = {"restaurant": restaurant, "item": "meal", "estimated_cost": 250}
        confidence = 0.85

    elif any(kw in text for kw in CAB_KEYWORDS):
        category = "cab"
        destination = "Unknown Destination"
        for place, label in [('mall', 'Mall'), ('school', 'School'),
                             ('hospital', 'Hospital'), ('station', 'Station'),
                             ('friend', "Friend's house"), ('house', "Friend's house"),
                             ('home', 'Home')]:
            if place in text:
                destination = label
                break
        summary_text = f"Book a cab to {destination}"
        details = {"destination": destination, "estimated_cost": 150}
        confidence = 0.80

    return IntentResponse(
        category=category,
        summary_text=summary_text,
        details=details,
        confidence=confidence,
        is_emergency=is_emergency,
        emergency_reason=emergency_reason,
    )


def _extract_intent_gemini(transcript: str) -> Optional[IntentResponse]:
    """
    Uses Gemini API for smarter intent extraction.
    Returns None if Gemini is unavailable or fails.
    """
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types

        prompt = (
            "You are a task-intent classifier for a child's phone call to their parent.\n"
            "Given this transcript, output STRICT JSON matching this schema:\n"
            "{\n"
            '  "category": "food" | "cab" | "none",\n'
            '  "summary_text": "One plain sentence a busy parent can read in 2 seconds",\n'
            '  "details": {\n'
            '    "restaurant": "Name of restaurant if food, else null",\n'
            '    "destination": "Target location if cab, else null",\n'
            '    "items": ["item1", "item2"],\n'
            '    "estimated_cost": 300\n'
            '  },\n'
            '  "confidence": 0.95,\n'
            '  "is_emergency": false,\n'
            '  "emergency_reason": null\n'
            "}\n\n"
            "Rules:\n"
            "- Bias toward false positives for emergency detection (safety first).\n"
            "- If distress, injury, threat, fear, or urgent danger is mentioned, set is_emergency: true and emergency_reason to the issue.\n"
            "- For food: extract restaurant, items, estimated cost in INR.\n"
            "- For cab: extract destination, estimated cost in INR.\n"
            "- If no clear task or only casual chit-chat, set category to 'none'.\n\n"
            f"Transcript: {transcript}"
        )

        client = genai.Client(api_key=api_key)
        # Try resilient model cascade
        parsed = None
        for model_name in ["gemini-2.5-flash", "gemini-flash-latest"]:
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )
                parsed = json.loads(response.text)
                break
            except Exception as model_err:
                logger.warning(f"Model {model_name} failed: {model_err}")
                continue

        if not parsed:
            return None

        result = IntentResponse(**parsed)
        logger.info(f"Gemini intent extraction OK: {result.category} / {result.summary_text}")
        return result

    except Exception as e:
        logger.warning(f"Gemini intent extraction failed: {e}")
        return None


def extract_intent_from_transcript(transcript: str) -> IntentResponse:
    """
    Extracts task intent from a transcript.
    Priority: Gemini API → rule-based fallback.
    """
    # Try Gemini first (smarter)
    gemini_result = _extract_intent_gemini(transcript)
    if gemini_result is not None:
        return gemini_result

    # Fall back to rule-based
    return _extract_intent_rule_based(transcript)
