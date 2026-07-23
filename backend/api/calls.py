from flask import Blueprint, request, jsonify
import uuid

bp = Blueprint('calls', __name__)

@bp.route('/upload', methods=['POST'])
def upload_call():
    # In Flask, files are in request.files and form data in request.form
    audio_file = request.files.get('audio_file')
    child_id = request.form.get('child_id')
    call_timestamp = request.form.get('call_timestamp')
    
    if not audio_file or not child_id or not call_timestamp:
        return jsonify({"error": "Missing required fields"}), 400

    # Mocking upload behavior
    call_id = str(uuid.uuid4())
    return jsonify({"call_id": call_id})

from ..services.ai_service import extract_intent_from_transcript, IntentResponse

@bp.route('/<call_id>/process', methods=['POST'])
def process_call(call_id):
    # In a real scenario, you would fetch the transcript from the database 
    # or process the uploaded audio file here using `transcribe_audio`.
    # For now, we simulate receiving a transcript.
    transcript = "Mom, can you order me a pizza from Domino's?"
    
    intent_data: IntentResponse = extract_intent_from_transcript(transcript)
    
    # Normally, you would save this to the database here (TaskRecord/EmergencyEvent).
    
    return jsonify({
        "call_id": call_id,
        "transcript": transcript,
        "is_emergency": intent_data.is_emergency,
        "task": {
            "category": intent_data.category,
            "summary_text": intent_data.summary_text,
            "details": intent_data.details,
            "confidence": intent_data.confidence
        } if not intent_data.is_emergency else None,
        "emergency_event": {
            "trigger_reason": intent_data.emergency_reason,
            "timestamp": "now" # In real app, generate a timestamp
        } if intent_data.is_emergency else None
    })
