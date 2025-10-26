from flask import Blueprint, jsonify, request
import sqlite3

goals_bp = Blueprint('goals', __name__)

DB_PATH = "db/goalflow.db"

@goals_bp.route('/', methods=['GET'])
def get_goals():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM Goals").fetchall()
    return jsonify([dict(row) for row in rows])

@goals_bp.route('/account/<int:account_id>', methods=['GET'])
def get_account_goals(account_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory  = sqlite3.Row
        rows = conn.execute("SELECT * FROM Goals WHERE UserId = ?", (account_id,)).fetchall()
    return jsonify([dict(row) for row in rows])

@goals_bp.route('/<int:goal_id>', methods=['GET'])
def get_goal(goal_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM Goals WHERE GoalId = ?", (goal_id,)).fetchone()
    if not row:
        return jsonify({"error": "Goal not found"}), 404
    return jsonify(dict(row))

@goals_bp.route('/', methods=['POST'])
def add_goal():
    data = request.get_json()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Goals (UserId, GoalName, Description, TargetAmount, CurrentAmount, Deadline)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["UserId"],
            data["GoalName"],
            data.get("Description", ""),
            data["TargetAmount"],
            data.get("CurrentAmount", 0.0),
            data.get("Deadline")
        ))
        conn.commit()
    return jsonify({"message": "Goal added"}), 201

@goals_bp.route('/<int:goal_id>', methods=['PATCH'])
def update_goal(goal_id):
    data = request.get_json()
    fields = []
    values = []
    for f in ["GoalName", "Description", "TargetAmount", "CurrentAmount", "Deadline", "IsCompleted"]:
        if f in data:
            fields.append(f"{f} = ?")
            values.append(data[f])
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    values.append(goal_id)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE Goals SET {', '.join(fields)} WHERE GoalId = ?", values)
        conn.commit()
    return jsonify({"message": "Goal updated"})

@goals_bp.route('/<int:goal_id>', methods=['DELETE'])
def delete_goal(goal_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM Goals WHERE GoalId = ?", (goal_id,))
        conn.commit()
    return jsonify({"message": "Goal deleted"})
