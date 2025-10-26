import sqlite3
import random
from datetime import datetime, timedelta

# ------------------------------------------------------------------
# CONFIG
# ------------------------------------------------------------------
NUM_ACCOUNTS = 3
MONTHS_HISTORY = 12
TRANSACTIONS_PER_MONTH = 4  # roughly 50 per account total

BUSINESS_TYPES = [
    "GROCERY", "RESTAURANT", "ONLINE_PURCHASE", "TRANSFER", "HEALTH", "EDUCATION",
    "PAYROLL", "ENTERTAINMENT", "RENT", "UTILITY", "TRANSPORT", "PERSONAL_TRANSFER"
]

def populate_db():
    conn = sqlite3.connect("db/goalflow.db")
    cur = conn.cursor()

    cur.executescript("""
    DELETE FROM WeeklyMissions;
    DELETE FROM MissionTemplates;
    DELETE FROM GoalTransactions;
    DELETE FROM Goals;
    DELETE FROM Transactions;
    DELETE FROM Accounts;
    """)

    # ------------------------------------------------------------
    # 1. Accounts
    # ------------------------------------------------------------
    accounts = [
        ("Fernando", "Lopez", "5551001001", "fernando@example.com", 0.0),
        ("Sofia", "Martinez", "5552002002", "sofia@example.com", 0.0),
        ("Carlos", "Rios", "5553003003", "carlos@example.com", 0.0),
    ]
    cur.executemany(
        "INSERT INTO Accounts (first_name,last_name,phone_number,email,balance) VALUES (?,?,?,?,?)",
        accounts,
    )
    cur.execute("SELECT id FROM Accounts")
    account_ids = [r[0] for r in cur.fetchall()]

    # ------------------------------------------------------------
    # 2. Transactions
    # ------------------------------------------------------------
    base_date = datetime(2024, 10, 1)
    end_date = datetime(2025, 10, 1)

    for acc_id in account_ids:
        current_date = base_date
        while current_date < end_date:
            for _ in range(TRANSACTIONS_PER_MONTH):
                amount = round(random.uniform(50, 1500), 2)
                business_type = random.choice(BUSINESS_TYPES)
                if random.random() < 0.6:
                    origin = acc_id
                    dest = random.choice([a for a in account_ids if a != acc_id])
                else:
                    origin = None
                    dest = acc_id

                cur.execute(
                    """INSERT INTO Transactions (origin_account,destination_account,amount,datetime,business_type)
                       VALUES (?,?,?,?,?)""",
                    (origin, dest, amount, current_date.strftime("%Y-%m-%d %H:%M"), business_type),
                )
            current_date += timedelta(days=7)

    # ------------------------------------------------------------
    # 3. Goals
    # ------------------------------------------------------------
    goals = [
        (account_ids[0], "Emergency Fund", "Save for unexpected expenses", "Savings", 5000, 1500, "2025-12-31"),
        (account_ids[0], "Vacation", "Trip to Japan", "Leisure", 4500, 1200, "2027-12-14"),
        (account_ids[0], "New Car", "Buy a Chevy Pop", "Mobility", 2500, 2300, "2025-11-22"),
        (account_ids[1], "New Laptop", "Save for a MacBook", "Technology", 3000, 800, "2025-09-30"),
        (account_ids[2], "Vacation", "Trip to Cancun", "Leisure", 4000, 2000, "2025-10-01"),
    ]
    cur.executemany(
        """INSERT INTO Goals (UserId,GoalName,Description,Category,TargetAmount,CurrentAmount,Deadline)
           VALUES (?,?,?,?,?,?,?)""",
        goals,
    )

    # ------------------------------------------------------------
    # 4. GoalTransactions
    # ------------------------------------------------------------
    cur.execute("SELECT GoalId,UserId FROM Goals")
    for goal_id, user_id in cur.fetchall():
        for _ in range(random.randint(5, 10)):
            ttype = random.choice(["IN", "OUT"])
            amount = round(random.uniform(100, 500), 2)
            desc = f"{'Deposit' if ttype=='IN' else 'Withdrawal'} for goal"
            date = (datetime.now() - timedelta(days=random.randint(10, 200))).strftime("%Y-%m-%d")
            cur.execute(
                """INSERT INTO GoalTransactions (GoalId,UserId,Type,Amount,Description,CreatedAt)
                   VALUES (?,?,?,?,?,?)""",
                (goal_id, user_id, ttype, amount, desc, date),
            )

    # ------------------------------------------------------------
    # 5. MissionTemplates
    # ------------------------------------------------------------
    templates = [
        ("Save 5% this week", "Save at least 5% of your income", "SAVE", 1, None, 7),
        ("Limit coffee spending", "Spend less than 100 MXN on coffee", "LIMIT_SPENDING", 2, 100, 7),
        ("Transfer to goal", "Add funds to your goal", "TRANSFER", 1, 200, 7),
        ("Maintain streak", "Save for 4 consecutive weeks", "STREAK", 3, None, 28),
    ]
    cur.executemany(
        """INSERT INTO MissionTemplates (Title,Description,Type,DifficultyLevel,DefaultTargetAmount,EstimatedDurationDays)
           VALUES (?,?,?,?,?,?)""",
        templates,
    )

    # ------------------------------------------------------------
    # 6. WeeklyMissions
    # ------------------------------------------------------------
    cur.execute("SELECT TemplateId FROM MissionTemplates")
    template_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT GoalId,UserId FROM Goals")
    for goal_id, user_id in cur.fetchall():
        for _ in range(3):
            tpl = random.choice(template_ids)
            title = f"Mission {tpl} for user {user_id}"
            desc = "Auto-generated mission"
            mtype = random.choice(["SAVE", "LIMIT_SPENDING", "TRANSFER", "STREAK"])
            target = round(random.uniform(100, 500), 2)
            deadline = (datetime.now() + timedelta(days=random.randint(3, 10))).strftime("%Y-%m-%d")
            cur.execute(
                """INSERT INTO WeeklyMissions
                   (UserId,GoalId,TemplateId,Title,Description,Type,TargetAmount,Deadline,IsCompleted)
                   VALUES (?,?,?,?,?,?,?,?,0)""",
                (user_id, goal_id, tpl, title, desc, mtype, target, deadline),
            )

    conn.commit()
    conn.close()
    print("Demo data (accounts, transactions, goals, missions) inserted successfully.")

if __name__ == "__main__":
    populate_db()
