from flask import Blueprint, jsonify
import time
import threading

bp = Blueprint('emergency', __name__)

@bp.route('/<int:event_id>/acknowledge', methods=['POST'])
def acknowledge_emergency(event_id):
    # In a real app, update the database to mark event_id as acknowledged
    return jsonify({"status": "success", "message": "Emergency acknowledged"})

def escalate_to_backup(event_id: int, backup_contact_phone: str):
    """
    Escalates the emergency to the backup contact.
    In Phase 3, this would send an SMS via Twilio.
    For now, we simulate an FCM push or log it.
    """
    print(f"ESCALATION: Emergency {event_id} not acknowledged. Alerting backup contact at {backup_contact_phone} via FCM.")

def start_escalation_timer(event_id: int, backup_contact_phone: str, timeout_seconds: int = 180):
    """
    Starts a background timer to escalate if not acknowledged.
    """
    def timer_task():
        time.sleep(timeout_seconds)
        # Check DB if acknowledged; if not, escalate
        # For mock, we just escalate
        escalate_to_backup(event_id, backup_contact_phone)
        
    threading.Thread(target=timer_task, daemon=True).start()

