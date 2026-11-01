from flask import Blueprint, request, jsonify
from database import SessionLocal
import models
import time
import threading
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('emergency', __name__)


@bp.route('/', methods=['GET'])
def list_emergencies():
    """Returns all emergency events, most recent first."""
    db = SessionLocal()
    try:
        events = db.query(models.EmergencyEvent).order_by(
            models.EmergencyEvent.created_at.desc()
        ).all()

        result = []
        for event in events:
            child = db.query(models.ChildProfile).filter(
                models.ChildProfile.id == event.child_id
            ).first()

            result.append({
                "id": event.id,
                "child_id": event.child_id,
                "child_name": child.name if child else "Unknown",
                "trigger_reason": event.trigger_reason,
                "transcript_snippet": event.transcript_snippet,
                "location_lat": event.location_lat,
                "location_lng": event.location_lng,
                "backup_contact_notified": event.backup_contact_notified,
                "acknowledged": event.acknowledged,
                "created_at": event.created_at.isoformat() if event.created_at else None,
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:event_id>/acknowledge', methods=['POST'])
def acknowledge_emergency(event_id):
    """Mark an emergency event as acknowledged by the parent."""
    db = SessionLocal()
    try:
        event = db.query(models.EmergencyEvent).filter(
            models.EmergencyEvent.id == event_id
        ).first()
        if not event:
            return jsonify({"error": "Emergency event not found"}), 404

        event.acknowledged = True
        db.commit()

        logger.info(f"Emergency {event_id} acknowledged by parent")

        return jsonify({
            "status": "acknowledged",
            "event_id": event_id,
        })

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


def escalate_to_backup(event_id: int, backup_contact_phone: str):
    """
    Escalates the emergency to the backup contact.
    In a real app, this would send an SMS (e.g., via Twilio or termux-sms-send).
    For MVP, we log it and update the DB.
    """
    logger.warning(
        f"ESCALATION: Emergency {event_id} not acknowledged within timeout. "
        f"Alerting backup contact at {backup_contact_phone}."
    )

    # Update the DB to record that backup was notified
    db = SessionLocal()
    try:
        event = db.query(models.EmergencyEvent).filter(
            models.EmergencyEvent.id == event_id
        ).first()
        if event and not event.acknowledged:
            event.backup_contact_notified = True
            db.commit()
            logger.info(f"Backup contact notified for emergency {event_id}")
        elif event and event.acknowledged:
            logger.info(f"Emergency {event_id} was already acknowledged, skipping escalation")
    except Exception as e:
        db.rollback()
        logger.error(f"Escalation DB update error: {e}")
    finally:
        db.close()


def start_escalation_timer(event_id: int, backup_contact_phone: str, timeout_seconds: int = 180):
    """
    Starts a background timer. If the emergency isn't acknowledged
    within timeout_seconds, escalates to the backup contact.
    """
    def timer_task():
        time.sleep(timeout_seconds)

        # Check if acknowledged before escalating
        db = SessionLocal()
        try:
            event = db.query(models.EmergencyEvent).filter(
                models.EmergencyEvent.id == event_id
            ).first()
            if event and not event.acknowledged:
                escalate_to_backup(event_id, backup_contact_phone)
            else:
                logger.info(f"Emergency {event_id} acknowledged before timeout, no escalation needed")
        except Exception as e:
            logger.error(f"Escalation timer check error: {e}")
        finally:
            db.close()

    thread = threading.Thread(target=timer_task, daemon=True)
    thread.start()
    logger.info(f"Escalation timer started for emergency {event_id} ({timeout_seconds}s)")
