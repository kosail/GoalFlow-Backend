from flask import Blueprint, jsonify, request
import sqlite3
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__)

DB_PATH = "db/goalflow.db"

def update_balance(account_id, delta):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE Accounts SET balance = balance + ? WHERE id = ?", (delta, account_id))
        conn.commit()

@transactions_bp.route('/', methods=['GET'])
def get_all_transactions():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM Transactions ORDER BY datetime DESC").fetchall()
    return jsonify([dict(row) for row in rows])

@transactions_bp.route('/account/<int:account_id>', methods=['GET'])
def get_account_transactions(account_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory  = sqlite3.Row
        rows = conn.execute("""SELECT * FROM Transactions 
                            WHERE destination_account = ?""", (account_id,)).fetchall()
        rows2 = conn.execute("""SELECT * FROM Transactions 
                            WHERE origin_account = ?""", (account_id,)).fetchall()
        rows = rows + rows2
    return jsonify([dict(row) for row in rows])

@transactions_bp.route('/<int:transaction_id>', methods=['GET'])
def get_transaction(transaction_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM Transactions WHERE id = ?", (transaction_id,)).fetchone()
    if not row:
        return jsonify({"error": "Transaction not found"}), 404
    return jsonify(dict(row))

@transactions_bp.route('/', methods=['POST'])
def add_transaction():
    data = request.get_json()
    origin = data.get("origin_account")
    dest = data.get("destination_account")
    amount = data.get("amount")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA journal_mode=WAL;")
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO Transactions (origin_account, destination_account, amount, datetime)
            VALUES (?, ?, ?, ?)
        """, (origin, dest, amount, datetime.now().isoformat()))
        conn.commit()
    if origin:
        update_balance(origin, -amount)
    if dest:
        update_balance(dest, amount)
    return jsonify({"message": "Transaction added"}), 201

@transactions_bp.route('/<int:transaction_id>', methods=['PATCH'])
def update_transaction(transaction_id):
    data = request.get_json()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        if 'amount' in data:
            cur.execute("SELECT origin_account, destination_account, amount FROM Transactions WHERE id = ?", (transaction_id,))
            old = cur.fetchone()
            if old:
                diff = data['amount'] - old[2]
                if old[0]: update_balance(old[0], -diff)
                if old[1]: update_balance(old[1], diff)
            cur.execute("UPDATE Transactions SET amount = ? WHERE id = ?", (data['amount'], transaction_id))
            conn.commit()
    return jsonify({"message": "Transaction updated"})

@transactions_bp.route('/<int:transaction_id>', methods=['DELETE'])
def delete_transaction(transaction_id):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT origin_account, destination_account, amount FROM Transactions WHERE id = ?", (transaction_id,))
        t = cur.fetchone()
        if t:
            if t[0]: update_balance(t[0], t[2])
            if t[1]: update_balance(t[1], -t[2])
        cur.execute("DELETE FROM Transactions WHERE id = ?", (transaction_id,))
        conn.commit()
    return jsonify({"message": "Transaction deleted"})
