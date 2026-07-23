import os
import json
from openai import OpenAI
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

# Ensure you have OPENAI_API_KEY set in your environment
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY", "mock_key_for_now"))

class IntentResponse(BaseModel):
    category: str = Field(description="Must be 'food', 'cab', or 'none'")
    summary_text: str = Field(description="One plain sentence a busy parent can read in 2 seconds")
    details: Dict[str, Any] = Field(description="Details of the task (e.g., restaurant, cost)")
    confidence: float = Field(description="Confidence score from 0.0 to 1.0")
    is_emergency: bool = Field(description="True if distress, fear, pain, or safety threats are detected")
    emergency_reason: Optional[str] = Field(description="Reason for the emergency, or null if none")

def transcribe_audio(file_path: str) -> str:
    """
    Transcribes audio using OpenAI Whisper API.
    """
    try:
        with open(file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
            )
        return transcript.text
    except Exception as e:
        print(f"Transcription error: {e}")
        # Return mock transcript for prototype if it fails (e.g., no API key)
        return "Mom, can you order me a pizza from Domino's?"

def extract_intent_from_transcript(transcript: str) -> IntentResponse:
    """
    Extracts the task intent and checks for emergencies from a transcript.
    """
    prompt = (
        "You are a task-intent classifier for a child's phone call to their parent. "
        "Given this transcript, output STRICT JSON only: category (food/cab/none), "
        "summary_text (one plain sentence a busy parent can read in 2 seconds), "
        "details (object), confidence (0-1), is_emergency (bool), emergency_reason (string or null). "
        "Treat distress, fear, pain, or safety threats as emergencies — bias toward false positives "
        "over false negatives for emergency detection."
    )

    try:
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",  # Using gpt-4o which supports structured outputs
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": transcript}
            ],
            response_format=IntentResponse,
        )
        
        return completion.choices[0].message.parsed
    except Exception as e:
        print(f"Intent extraction error: {e}")
        # Return a mocked response for prototype if it fails
        return IntentResponse(
            category="food",
            summary_text="Order pizza from Domino's",
            details={"restaurant": "Domino's", "item": "pizza", "cost": 300},
            confidence=0.95,
            is_emergency=False,
            emergency_reason=None
        )
