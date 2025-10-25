from flask import Blueprint, jsonify, request
import sqlite3

accounts_bp = Blueprint('accounts', __name__)

DB_PATH = "db/goalflow.db"

# --- GET ---
@accounts_bp.route('/', methods=['GET'])
def get_all_accounts():
    with sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Accounts")
        rows = cur.fetchall()
    return jsonify([dict(row) for row in rows])

@accounts_bp.route('/<int:account_id>', methods=['GET'])
def get_account(account_id):
    with sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Accounts WHERE id = ?", (account_id,))
        row = cur.fetchone()
    if not row:
        return jsonify({"error": "Account not found"}), 404
    return jsonify(dict(row))

# --- POST ---
@accounts_bp.route('/', methods=['POST'])
def add_account():
    data = request.get_json()
    try:
        with sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False) as conn:
            conn.execute("PRAGMA journal_mode=WAL;")
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO Accounts (first_name, last_name, phone_number, email, balance)
                VALUES (?, ?, ?, ?, ?)
            """, (
                data['first_name'],
                data['last_name'],
                data['phone_number'],
                data['email'],
                data.get('balance', 0.0)
            ))
            conn.commit()
        return jsonify({"message": "Account created successfully"}), 201
    except sqlite3.IntegrityError as e:
        return jsonify({"error": str(e)}), 400

# --- PATCH ---
@accounts_bp.route('/<int:account_id>', methods=['PATCH'])
def update_account(account_id):
    data = request.get_json()
    fields = []
    values = []
    for k in ["first_name", "last_name", "phone_number", "email", "balance"]:
        if k in data:
            fields.append(f"{k} = ?")
            values.append(data[k])
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    values.append(account_id)
    with sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute(f"UPDATE Accounts SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    return jsonify({"message": "Account updated"})

# --- DELETE ---
@accounts_bp.route('/<int:account_id>', methods=['DELETE'])
def delete_account(account_id):
    with sqlite3.connect(DB_PATH, timeout=10, check_same_thread=False) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Accounts WHERE id = ?", (account_id,))
        conn.commit()
    return jsonify({"message": "Account deleted"})
