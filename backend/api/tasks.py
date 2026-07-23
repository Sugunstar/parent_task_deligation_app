from flask import Blueprint, request, jsonify

bp = Blueprint('tasks', __name__)

from ..services.mock_execution import execute_task

@bp.route('/<int:task_id>/decision', methods=['POST'])
def make_decision(task_id):
    data = request.get_json()
    if not data or 'decision' not in data:
        return jsonify({"error": "Missing decision"}), 400
        
    decision = data['decision']
    
    # In a real app, you would fetch the task category and details from DB using task_id
    mock_category = "food"
    mock_details = {"restaurant": "Domino's", "item": "pizza", "cost": 300}
    
    if decision == "approved":
        status = execute_task(mock_category, mock_details)
        return jsonify({"status": status})
        
    return jsonify({"status": "declined"})
