from flask import Blueprint, jsonify, request
import sqlite3

missions_bp = Blueprint('missions', __name__)

DB_PATH = "db/goalflow.db"

@missions_bp.route('/', methods=['GET'])
def get_all_missions():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM WeeklyMissions").fetchall()
    return jsonify([dict(row) for row in rows])

@missions_bp.route('/<int:mission_id>', methods=['GET'])
def get_mission(mission_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM WeeklyMissions WHERE MissionId = ?", (mission_id,)).fetchone()
    if not row:
        return jsonify({"error": "Mission not found"}), 404
    return jsonify(dict(row))

@missions_bp.route('/', methods=['POST'])
def add_mission():
    data = request.get_json()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO WeeklyMissions (UserId, GoalId, TemplateId, Title, Description, Type, TargetAmount, Deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["UserId"],
            data["GoalId"],
            data.get("TemplateId"),
            data["Title"],
            data.get("Description", ""),
            data.get("Type", "SAVE"),
            data.get("TargetAmount", 0),
            data["Deadline"]
        ))
        conn.commit()
    return jsonify({"message": "Mission created"}), 201

@missions_bp.route('/<int:mission_id>', methods=['PATCH'])
def update_mission(mission_id):
    data = request.get_json()
    fields = []
    values = []
    for f in ["Title", "Description", "TargetAmount", "IsCompleted"]:
        if f in data:
            fields.append(f"{f} = ?")
            values.append(data[f])
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    values.append(mission_id)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE WeeklyMissions SET {', '.join(fields)} WHERE MissionId = ?", values)
        conn.commit()
    return jsonify({"message": "Mission updated"})

@missions_bp.route('/<int:mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM WeeklyMissions WHERE MissionId = ?", (mission_id,))
        conn.commit()
    return jsonify({"message": "Mission deleted"})
