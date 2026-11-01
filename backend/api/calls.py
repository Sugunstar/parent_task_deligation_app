from flask import Blueprint, request, jsonify
import uuid
import os
import json
import logging
from datetime import datetime
from database import SessionLocal
import models
from services.ai_service import transcribe_audio, extract_intent_from_transcript

logger = logging.getLogger(__name__)

bp = Blueprint('calls', __name__)

# Upload directory — resolved relative to the backend folder
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


@bp.route('/upload-and-process', methods=['POST'])
def upload_and_process():
    """
    Single endpoint: upload audio → transcribe → extract intent → return result.
    Combines the old /upload + /process into one call for the PWA.
    The frontend records audio, sends it here, and gets back the approval card data.
    """
    audio_file = request.files.get('audio_file')
    child_id = request.form.get('child_id')

    if not audio_file or not child_id:
        return jsonify({"error": "Missing required fields: audio_file, child_id"}), 400

    try:
        child_id = int(child_id)
    except ValueError:
        return jsonify({"error": "child_id must be an integer"}), 400

    # Save uploaded audio file
    call_id = str(uuid.uuid4())
    file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".wav"
    # Sanitize extension
    if file_extension not in ('.wav', '.mp3', '.ogg', '.webm', '.m4a', '.flac'):
        file_extension = '.wav'
    audio_filename = f"{call_id}{file_extension}"
    audio_path = os.path.join(UPLOAD_DIR, audio_filename)

    try:
        audio_file.save(audio_path)
    except Exception as e:
        logger.error(f"Failed to save audio file: {e}")
        return jsonify({"error": "Failed to save audio file"}), 500

    # Process in a single DB session
    db = SessionLocal()
    try:
        # Verify child exists
        child = db.query(models.ChildProfile).filter(models.ChildProfile.id == child_id).first()
        if not child:
            # Clean up saved file
            os.remove(audio_path)
            return jsonify({"error": "Child not found"}), 404

        # Transcribe
        transcript = transcribe_audio(audio_path)
        if not transcript:
            transcript = "[Transcription failed — audio may be unclear or too short]"

        # Extract intent
        intent = extract_intent_from_transcript(transcript)

        # Create task record
        task_record = models.TaskRecord(
            child_id=child_id,
            call_id=call_id,
            transcript=transcript,
            summary_text=intent.summary_text,
            category=intent.category,
            details_json=json.dumps(intent.details),
            status=models.TaskStatus.pending,
        )
        db.add(task_record)
        db.flush()  # Get the ID without committing yet

        emergency_event_data = None

        if intent.is_emergency:
            # Create emergency event
            emergency_event = models.EmergencyEvent(
                child_id=child_id,
                trigger_reason=intent.emergency_reason or "Distress detected in call",
                transcript_snippet=transcript[:500],
                location_lat=None,
                location_lng=None,
            )
            db.add(emergency_event)
            db.flush()

            # Mark task as auto-handled
            task_record.status = models.TaskStatus.executed
            task_record.decision_source = models.DecisionSource.auto_timeout
            task_record.decided_at = datetime.utcnow()

            emergency_event_data = {
                "id": emergency_event.id,
                "trigger_reason": emergency_event.trigger_reason,
                "transcript_snippet": emergency_event.transcript_snippet,
                "created_at": emergency_event.created_at.isoformat() if emergency_event.created_at else None,
            }

            # Start escalation timer if child has a backup contact
            if child.backup_contact_phone:
                from api.emergency import start_escalation_timer
                start_escalation_timer(emergency_event.id, child.backup_contact_phone)

        db.commit()

        response = {
            "call_id": call_id,
            "task_id": task_record.id,
            "transcript": transcript,
            "is_emergency": intent.is_emergency,
            "task": {
                "category": intent.category,
                "summary_text": intent.summary_text,
                "details": intent.details,
                "confidence": intent.confidence,
            },
            "emergency_event": emergency_event_data,
        }

        return jsonify(response)

    except Exception as e:
        db.rollback()
        logger.error(f"Processing error: {e}", exc_info=True)
        return jsonify({"error": f"Processing error: {str(e)}"}), 500
    finally:
        db.close()


@bp.route('/upload', methods=['POST'])
def upload_call():
    """
    Legacy endpoint: upload audio only, process separately.
    Kept for backward compatibility / separate upload+process workflows.
    """
    audio_file = request.files.get('audio_file')
    child_id = request.form.get('child_id')
    call_timestamp = request.form.get('call_timestamp', datetime.utcnow().isoformat())

    if not audio_file or not child_id:
        return jsonify({"error": "Missing required fields"}), 400

    try:
        child_id = int(child_id)
    except ValueError:
        return jsonify({"error": "child_id must be an integer"}), 400

    call_id = str(uuid.uuid4())
    file_extension = os.path.splitext(audio_file.filename)[1] if audio_file.filename else ".wav"
    if file_extension not in ('.wav', '.mp3', '.ogg', '.webm', '.m4a', '.flac'):
        file_extension = '.wav'
    audio_filename = f"{call_id}{file_extension}"
    audio_path = os.path.join(UPLOAD_DIR, audio_filename)

    try:
        audio_file.save(audio_path)
    except Exception as e:
        return jsonify({"error": f"Failed to save audio file: {str(e)}"}), 500

    db = SessionLocal()
    try:
        child = db.query(models.ChildProfile).filter(models.ChildProfile.id == child_id).first()
        if not child:
            os.remove(audio_path)
            return jsonify({"error": "Child not found"}), 404

        task_record = models.TaskRecord(
            child_id=child_id,
            call_id=call_id,
            transcript="",
            summary_text="",
            category="none",
            details_json="{}",
            status=models.TaskStatus.pending
        )
        db.add(task_record)
        db.commit()

        return jsonify({"call_id": call_id, "task_id": task_record.id})

    except Exception as e:
        db.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        db.close()


@bp.route('/<call_id>/process', methods=['POST'])
def process_call(call_id):
    """
    Legacy endpoint: process a previously uploaded call.
    """
    db = SessionLocal()
    try:
        task_record = db.query(models.TaskRecord).filter(models.TaskRecord.call_id == call_id).first()
        if not task_record:
            return jsonify({"error": "Call/task not found"}), 404

        # Find the audio file
        audio_file_path = None
        for filename in os.listdir(UPLOAD_DIR):
            if filename.startswith(call_id):
                audio_file_path = os.path.join(UPLOAD_DIR, filename)
                break

        # Transcribe
        transcript = ""
        if audio_file_path and os.path.exists(audio_file_path):
            transcript = transcribe_audio(audio_file_path)
        if not transcript:
            transcript = "[Transcription failed — audio may be unclear or too short]"

        task_record.transcript = transcript

        # Extract intent
        intent = extract_intent_from_transcript(transcript)
        task_record.summary_text = intent.summary_text
        task_record.category = intent.category
        task_record.details_json = json.dumps(intent.details)

        emergency_event_data = None

        if intent.is_emergency:
            child = db.query(models.ChildProfile).filter(
                models.ChildProfile.id == task_record.child_id
            ).first()

            emergency_event = models.EmergencyEvent(
                child_id=task_record.child_id,
                trigger_reason=intent.emergency_reason or "Distress detected",
                transcript_snippet=transcript[:500],
            )
            db.add(emergency_event)
            db.flush()

            task_record.decision_source = models.DecisionSource.auto_timeout
            task_record.status = models.TaskStatus.executed
            task_record.decided_at = datetime.utcnow()

            emergency_event_data = {
                "id": emergency_event.id,
                "trigger_reason": emergency_event.trigger_reason,
                "created_at": emergency_event.created_at.isoformat() if emergency_event.created_at else None,
            }

            if child and child.backup_contact_phone:
                from api.emergency import start_escalation_timer
                start_escalation_timer(emergency_event.id, child.backup_contact_phone)
        else:
            task_record.status = models.TaskStatus.pending

        db.commit()

        return jsonify({
            "call_id": call_id,
            "task_id": task_record.id,
            "transcript": transcript,
            "is_emergency": intent.is_emergency,
            "task": {
                "category": intent.category,
                "summary_text": intent.summary_text,
                "details": intent.details,
                "confidence": intent.confidence,
            },
            "emergency_event": emergency_event_data,
        })

    except Exception as e:
        db.rollback()
        logger.error(f"Processing error: {e}", exc_info=True)
        return jsonify({"error": f"Processing error: {str(e)}"}), 500
    finally:
        db.close()
