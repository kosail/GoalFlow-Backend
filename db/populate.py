from pathlib import Path

import sqlite3
import random
from datetime import datetime, timedelta
from collections import defaultdict

DB_PATH = "db/goalflow.db"

random.seed(42)
START_DATE = datetime(2024, 10, 1)
END_DATE = datetime(2025, 10, 1)

EXPENSE_CATEGORIES = [
    ("RENT", 0.08, 1400, 2200),
    ("GROCERIES", 0.22, 35, 120),
    ("RESTAURANT", 0.12, 15, 60),
    ("COFFEE", 0.08, 4, 12),
    ("TRANSPORT", 0.10, 8, 40),
    ("ONLINE_SHOPPING", 0.07, 20, 120),
    ("ENTERTAINMENT", 0.10, 10, 50),
    ("UTILITIES", 0.05, 60, 220),
    ("HEALTH", 0.03, 25, 150),
    ("EDUCATION", 0.03, 20, 110),
    ("CHILDCARE", 0.02, 20, 180),
]

INCOME_CATEGORIES = [
    ("PAYROLL", 0.85),
    ("REFUND", 0.10),
    ("BONUS", 0.05),
]

def daterange(start, end):
    curr = start
    while curr < end:
        yield curr
        curr += timedelta(days=1)

def pick_amount(low, high):
    return round(random.uniform(low, high), 2)

def weighted_choice(options):
    total = sum(w for _, w in options)
    r = random.uniform(0, total)
    upto = 0
    for name, weight in options:
        if upto + weight >= r:
            return name
        upto += weight
    return options[-1][0]

def ensure_fk(conn):
    conn.execute("PRAGMA foreign_keys = ON;")

def reset_tables(conn):
    cur = conn.cursor()
    cur.executescript("""
        DELETE FROM WeeklyMissions;
        DELETE FROM MissionTemplates;
        DELETE FROM GoalTransactions;
        DELETE FROM Goals;
        DELETE FROM Transactions;
        DELETE FROM Accounts;
    """)
    conn.commit()

def insert_accounts(conn):
    accounts = [
        ("Sarah", "Johnson", "5551110001", "sarah.johnson@example.com", 0.0),
        ("Alex", "Smith", "5552220002", "alex.smith@example.com", 0.0),
        ("Maria", "Rodriguez", "5553330003", "maria.rod@example.com", 0.0),
    ]
    cur = conn.cursor()
    cur.executemany(
        "INSERT INTO Accounts (first_name,last_name,phone_number,email,balance) VALUES (?,?,?,?,?)",
        accounts
    )
    conn.commit()
    cur.execute("SELECT id, first_name, last_name FROM Accounts ORDER BY id;")
    return [(r[0], r[1], r[2]) for r in cur.fetchall()]

def salary_schedule_for_user(user_name):
    if user_name == "Sarah":
        return "semi-monthly"
    if user_name == "Alex":
        return "monthly"
    if user_name == "Maria":
        return "biweekly"
    return "monthly"

def salary_amount_for_user(user_name):
    if user_name == "Sarah":
        return 2600.0
    if user_name == "Alex":
        return 1200.0
    if user_name == "Maria":
        return 3400.0
    return 2000.0

def insert_transactions(conn, accounts):
    cur = conn.cursor()
    tx_count_by_acc = defaultdict(int)
    inflow_by_acc = defaultdict(float)
    outflow_by_acc = defaultdict(float)

    next_biweekly = {}

    for acc_id, first_name, _ in accounts:
        schedule = salary_schedule_for_user(first_name)
        salary = salary_amount_for_user(first_name)

        if schedule == "biweekly":
            next_biweekly[acc_id] = START_DATE

        for day in daterange(START_DATE, END_DATE):
            if schedule == "monthly" and day.day == 1:
                cur.execute("INSERT INTO Transactions (origin_account,destination_account,amount,datetime,business_type) VALUES (?,?,?,?,?)",
                    (None, acc_id, salary, day.strftime("%Y-%m-%d 09:00:00"), "PAYROLL"))
                inflow_by_acc[acc_id] += salary
                tx_count_by_acc[acc_id] += 1

            elif schedule == "semi-monthly" and day.day in (1, 15):
                cur.execute("INSERT INTO Transactions (origin_account,destination_account,amount,datetime,business_type) VALUES (?,?,?,?,?)",
                    (None, acc_id, salary, day.strftime("%Y-%m-%d 09:00:00"), "PAYROLL"))
                inflow_by_acc[acc_id] += salary
                tx_count_by_acc[acc_id] += 1

            elif schedule == "biweekly" and day >= next_biweekly.get(acc_id, START_DATE):
                cur.execute("INSERT INTO Transactions (origin_account,destination_account,amount,datetime,business_type) VALUES (?,?,?,?,?)",
                    (None, acc_id, salary, day.strftime("%Y-%m-%d 09:00:00"), "PAYROLL"))
                inflow_by_acc[acc_id] += salary
                tx_count_by_acc[acc_id] += 1
                next_biweekly[acc_id] = day + timedelta(days=14)

            if day.day == 3:
                rent_amount = pick_amount(1500, 2200)
                cur.execute("INSERT INTO Transactions (origin_account,destination_account,amount,datetime,business_type) VALUES (?,?,?,?,?)",
                    (acc_id, None, rent_amount, day.strftime("%Y-%m-%d 10:00:00"), "RENT"))
                outflow_by_acc[acc_id] += rent_amount
                tx_count_by_acc[acc_id] += 1

            n = random.randint(1, 3)
            if day.weekday() >= 5:
                n += 1
            for _ in range(n):
                cat, _, low, high = random.choice(EXPENSE_CATEGORIES)
                amount = pick_amount(low, high)
                if cat in ("ENTERTAINMENT", "RESTAURANT", "ONLINE_SHOPPING") and day.weekday() < 4 and random.random() < 0.5:
                    continue
                time_str = f"{day.strftime('%Y-%m-%d')} {random.randint(8, 22):02d}:{random.randint(0,59):02d}:00"
                cur.execute("INSERT INTO Transactions (origin_account,destination_account,amount,datetime,business_type) VALUES (?,?,?,?,?)",
                    (acc_id, None, amount, time_str, cat))
                outflow_by_acc[acc_id] += amount
                tx_count_by_acc[acc_id] += 1

    conn.commit()
    return tx_count_by_acc, inflow_by_acc, outflow_by_acc

def recompute_and_update_balances(conn):
    cur = conn.cursor()
    cur.execute("SELECT id FROM Accounts ORDER BY id;")
    ids = [r[0] for r in cur.fetchall()]
    for acc_id in ids:
        cur.execute("""
            SELECT 
                IFNULL(SUM(CASE WHEN destination_account = ? THEN amount ELSE 0 END), 0) -
                IFNULL(SUM(CASE WHEN origin_account = ? THEN amount ELSE 0 END), 0)
            FROM Transactions
        """, (acc_id, acc_id))
        bal = round(float(cur.fetchone()[0] or 0.0), 2)
        cur.execute("UPDATE Accounts SET balance = ?, last_updated = datetime('now') WHERE id = ?", (bal, acc_id))
    conn.commit()

def populate_db():
    conn = sqlite3.connect(DB_PATH)
    ensure_fk(conn)
    reset_tables(conn)

    accounts = insert_accounts(conn)
    insert_transactions(conn, accounts)
    recompute_and_update_balances(conn)
    conn.close()

if __name__ == "__main__":
    main()