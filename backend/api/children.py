from flask import Blueprint, request, jsonify
from ..schemas import ChildProfileCreate

bp = Blueprint('children', __name__)

@bp.route('/', methods=['POST'])
def create_child():
    data = request.get_json()
    try:
        # Validate with pydantic
        child = ChildProfileCreate(**data)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # Mocking child creation
    return jsonify({
        "id": 1,
        "parent_id": 1,
        "name": child.name,
        "phone_number": child.phone_number,
        "age": child.age,
        "approval_mode": "always_approve",
        "auto_approve_max_amount": None,
        "auto_approve_timeout_minutes": 5,
        "backup_contact_phone": child.backup_contact_phone
    })

@bp.route('/<int:child_id>/tasks', methods=['GET'])
def get_tasks(child_id):
    # Mocking tasks list
    return jsonify([])

@bp.route('/<int:child_id>/enroll-voice', methods=['POST'])
def enroll_voice(child_id):
    audio_sample = request.files.get('audio_sample')
    if not audio_sample:
        return jsonify({"error": "Missing audio sample"}), 400
        
    # Mocking voice enrollment
    return jsonify({"status": "success", "message": "Voice enrolled"})
