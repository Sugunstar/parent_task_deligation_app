from flask import Blueprint, request, jsonify
from database import SessionLocal
import models
from schemas import ChildProfileCreate, ChildProfileUpdate
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('children', __name__)

# ─── Helper: ensure a demo parent exists for MVP ─────────────────
# In the full app, this would be tied to auth. For MVP, we use parent_id=1.

def _ensure_parent(db):
    """Creates the demo parent if it doesn't exist yet."""
    parent = db.query(models.Parent).filter(models.Parent.id == 1).first()
    if not parent:
        parent = models.Parent(
            id=1,
            name="Parent",
            email="parent@app.local",
        )
        db.add(parent)
        db.commit()
    return parent


@bp.route('/', methods=['GET'])
def list_children():
    """Returns all registered children."""
    db = SessionLocal()
    try:
        _ensure_parent(db)
        children = db.query(models.ChildProfile).filter(
            models.ChildProfile.parent_id == 1
        ).all()

        result = []
        for child in children:
            result.append({
                "id": child.id,
                "parent_id": child.parent_id,
                "name": child.name,
                "phone_number": child.phone_number,
                "age": child.age,
                "approval_mode": child.approval_mode.value if child.approval_mode else "always_approve",
                "auto_approve_max_amount": child.auto_approve_max_amount,
                "auto_approve_timeout_minutes": child.auto_approve_timeout_minutes,
                "backup_contact_phone": child.backup_contact_phone,
            })

        return jsonify(result)

    except Exception as e:
        logger.error(f"Error listing children: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/', methods=['POST'])
def create_child():
    """Register a new child profile."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    try:
        child_data = ChildProfileCreate(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    db = SessionLocal()
    try:
        _ensure_parent(db)

        child_profile = models.ChildProfile(
            parent_id=1,
            name=child_data.name,
            phone_number=child_data.phone_number,
            age=child_data.age,
            approval_mode=models.ApprovalMode.always_approve,
            auto_approve_timeout_minutes=5,
            backup_contact_phone=child_data.backup_contact_phone,
        )
        db.add(child_profile)
        db.commit()
        db.refresh(child_profile)

        return jsonify({
            "id": child_profile.id,
            "parent_id": child_profile.parent_id,
            "name": child_profile.name,
            "phone_number": child_profile.phone_number,
            "age": child_profile.age,
            "approval_mode": child_profile.approval_mode.value,
            "auto_approve_max_amount": child_profile.auto_approve_max_amount,
            "auto_approve_timeout_minutes": child_profile.auto_approve_timeout_minutes,
            "backup_contact_phone": child_profile.backup_contact_phone,
        }), 201

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating child: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:child_id>', methods=['GET'])
def get_child(child_id):
    """Get a single child profile."""
    db = SessionLocal()
    try:
        child = db.query(models.ChildProfile).filter(models.ChildProfile.id == child_id).first()
        if not child:
            return jsonify({"error": "Child not found"}), 404

        return jsonify({
            "id": child.id,
            "parent_id": child.parent_id,
            "name": child.name,
            "phone_number": child.phone_number,
            "age": child.age,
            "approval_mode": child.approval_mode.value if child.approval_mode else "always_approve",
            "auto_approve_max_amount": child.auto_approve_max_amount,
            "auto_approve_timeout_minutes": child.auto_approve_timeout_minutes,
            "backup_contact_phone": child.backup_contact_phone,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:child_id>', methods=['PUT'])
def update_child(child_id):
    """Update a child profile."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body required"}), 400

    try:
        update_data = ChildProfileUpdate(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    db = SessionLocal()
    try:
        child = db.query(models.ChildProfile).filter(models.ChildProfile.id == child_id).first()
        if not child:
            return jsonify({"error": "Child not found"}), 404

        # Only update fields that were provided
        update_dict = update_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(child, key, value)

        db.commit()
        db.refresh(child)

        return jsonify({
            "id": child.id,
            "parent_id": child.parent_id,
            "name": child.name,
            "phone_number": child.phone_number,
            "age": child.age,
            "approval_mode": child.approval_mode.value if child.approval_mode else "always_approve",
            "auto_approve_max_amount": child.auto_approve_max_amount,
            "auto_approve_timeout_minutes": child.auto_approve_timeout_minutes,
            "backup_contact_phone": child.backup_contact_phone,
        })

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:child_id>', methods=['DELETE'])
def delete_child(child_id):
    """Delete a child profile and all associated tasks/events."""
    db = SessionLocal()
    try:
        child = db.query(models.ChildProfile).filter(models.ChildProfile.id == child_id).first()
        if not child:
            return jsonify({"error": "Child not found"}), 404

        db.delete(child)
        db.commit()

        return jsonify({"status": "deleted", "child_id": child_id})

    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@bp.route('/<int:child_id>/tasks', methods=['GET'])
def get_child_tasks(child_id):
    """Get all tasks for a specific child."""
    db = SessionLocal()
    try:
        child = db.query(models.ChildProfile).filter(models.ChildProfile.id == child_id).first()
        if not child:
            return jsonify({"error": "Child not found"}), 404

        tasks = db.query(models.TaskRecord).filter(
            models.TaskRecord.child_id == child_id
        ).order_by(models.TaskRecord.created_at.desc()).all()

        import json
        task_list = []
        for task in tasks:
            task_list.append({
                "id": task.id,
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
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()
