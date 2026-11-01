from flask import Blueprint, request, jsonify
from database import SessionLocal
import models
from services.mock_execution import execute_task
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

bp = Blueprint('tasks', __name__)


@bp.route('/', methods=['GET'])
def list_all_tasks():
    """Returns all tasks, optionally filtered by status."""
    status_filter = request.args.get('status')  # e.g., ?status=pending

    db = SessionLocal()
    try:
        query = db.query(models.TaskRecord).order_by(models.TaskRecord.created_at.desc())

        if status_filter:
            try:
                status_enum = models.TaskStatus(status_filter)
                query = query.filter(models.TaskRecord.status == status_enum)
            except ValueError:
                return jsonify({"error": f"Invalid status: {status_filter}"}), 400

        tasks = query.all()

        task_list = []
        for task in tasks:
            # Get child name for display
            child = db.query(models.ChildProfile).filter(
                models.ChildProfile.id == task.child_id
            ).first()

            task_list.append({
                "id": task.id,
                "child_id": task.child_id,
                "child_name": child.name if child else "Unknown",
                "call_id": task.call_id,
                "transcript": task.transcript,
                "summary_text": task.summary_text,
                "category": task.category,
                "details": json.loads(task.details_json) if task.details_json else {},
                "status": task.status.value,
                "decision_source": task.decision_source.value if task.decision_source else None,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "decided_at": task.decided_at.isoformat() if task.decided_at else None,
            })

        return jsonify(task_list)

    except Exception as e:
        logger.error(f"Error listing tasks: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Returns a single task by ID."""
    db = SessionLocal()
    try:
        task = db.query(models.TaskRecord).filter(models.TaskRecord.id == task_id).first()
        if not task:
            return jsonify({"error": "Task not found"}), 404

        child = db.query(models.ChildProfile).filter(
            models.ChildProfile.id == task.child_id
        ).first()

        return jsonify({
            "id": task.id,
            "child_id": task.child_id,
            "child_name": child.name if child else "Unknown",
            "call_id": task.call_id,
            "transcript": task.transcript,
            "summary_text": task.summary_text,
            "category": task.category,
            "details": json.loads(task.details_json) if task.details_json else {},
            "status": task.status.value,
            "decision_source": task.decision_source.value if task.decision_source else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "decided_at": task.decided_at.isoformat() if task.decided_at else None,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:task_id>/decision', methods=['POST'])
def make_decision(task_id):
    """Accept or decline a pending task."""
    data = request.get_json()
    if not data or 'decision' not in data:
        return jsonify({"error": "Missing 'decision' field"}), 400

    decision = data['decision']
    if decision not in ('approved', 'declined'):
        return jsonify({"error": "decision must be 'approved' or 'declined'"}), 400

    db = SessionLocal()
    try:
        task_record = db.query(models.TaskRecord).filter(models.TaskRecord.id == task_id).first()
        if not task_record:
            return jsonify({"error": "Task not found"}), 404

        # Prevent re-deciding already decided tasks
        if task_record.status != models.TaskStatus.pending:
            return jsonify({
                "error": f"Task already {task_record.status.value}",
                "status": task_record.status.value,
            }), 409

        if decision == "approved":
            category = task_record.category
            details = json.loads(task_record.details_json) if task_record.details_json else {}
            exec_status = execute_task(category, details)

            task_record.status = (
                models.TaskStatus.executed if exec_status == "executed"
                else models.TaskStatus.failed
            )
            task_record.decision_source = models.DecisionSource.manual
            task_record.decided_at = datetime.utcnow()
            db.commit()

            return jsonify({"status": task_record.status.value, "task_id": task_id})

        else:  # declined
            task_record.status = models.TaskStatus.declined
            task_record.decision_source = models.DecisionSource.manual
            task_record.decided_at = datetime.utcnow()
            db.commit()

            return jsonify({"status": "declined", "task_id": task_id})

    except Exception as e:
        db.rollback()
        logger.error(f"Decision error: {e}", exc_info=True)
        return jsonify({"error": f"Error: {str(e)}"}), 500
    finally:
        db.close()
