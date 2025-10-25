import sqlite3

# ------------------------------------------------------
# Database initialization for GoalFlow
# ------------------------------------------------------

def init_db():
    conn = sqlite3.connect("goalflow.db")
    cursor = conn.cursor()

    # Enable foreign key constraints (disabled by default in SQLite)
    cursor.execute("PRAGMA foreign_keys = ON;")

    # ------------------------------------------------------
    # Table: Accounts / Cuentas
    # ------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone_number TEXT UNIQUE,
        email TEXT UNIQUE NOT NULL,
        balance REAL DEFAULT 0.0,
        date_created TEXT DEFAULT (datetime('now')),
        last_updated TEXT DEFAULT (datetime('now'))
    );
    """)

    # ------------------------------------------------------
    # Table: Transactions / Transacciones
    # ------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        origin_account INTEGER,
        destination_account INTEGER,
        amount REAL NOT NULL CHECK(amount >= 0),
        datetime TEXT DEFAULT (datetime('now')),
        business_type TEXT DEFAULT 'PERSONAL TRANSFER',
        FOREIGN KEY (origin_account) REFERENCES Accounts(id) ON DELETE SET NULL,
        FOREIGN KEY (destination_account) REFERENCES Accounts(id) ON DELETE SET NULL
    );
    """)

    # ------------------------------------------------------
    # Table: Goals / Metas
    # ------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Goals (
        GoalId INTEGER PRIMARY KEY AUTOINCREMENT,
        UserId INTEGER NOT NULL REFERENCES Accounts(id) ON DELETE CASCADE,

        GoalName TEXT NOT NULL,
        Description TEXT,

        TargetAmount REAL NOT NULL,
        CurrentAmount REAL DEFAULT 0.0,

        CreatedAt TEXT DEFAULT (datetime('now')),
        Deadline TEXT,
        IsCompleted INTEGER DEFAULT 0
    );
    """)

    # ------------------------------------------------------
    # Table: Transacciones relativas a una meta
    # ------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS GoalTransactions (
        TransactionId INTEGER PRIMARY KEY AUTOINCREMENT,
        GoalId INTEGER NOT NULL REFERENCES Goals(GoalId) ON DELETE CASCADE,
        UserId INTEGER NOT NULL REFERENCES Accounts(id) ON DELETE CASCADE,

        Type TEXT CHECK (Type IN ('IN', 'OUT')),
        Amount REAL NOT NULL,
        Description TEXT,

        CreatedAt TEXT DEFAULT (datetime('now'))
    );
    """)

    # ------------------------------------------------------
    # Table: templates para las misiones semanales
    # ------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS MissionTemplates (
        TemplateId INTEGER PRIMARY KEY AUTOINCREMENT,

        Title TEXT NOT NULL,
        Description TEXT,

        Type TEXT CHECK (Type IN ('SAVE', 'LIMIT_SPENDING', 'TRANSFER', 'STREAK', 'INSIGHT')),
        DifficultyLevel INTEGER DEFAULT 1,  -- 1 easy, 2 medium, 3 hard

        DefaultTargetAmount REAL,
        EstimatedDurationDays INTEGER DEFAULT 7,

        CreatedAt TEXT DEFAULT (datetime('now'))
    );
    """)

    # ------------------------------------------------------
    # Table: Misiones semanales
    # ------------------------------------------------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS WeeklyMissions (
        MissionId INTEGER PRIMARY KEY AUTOINCREMENT,
        UserId INTEGER NOT NULL REFERENCES Accounts(id) ON DELETE CASCADE,
        GoalId INTEGER NOT NULL REFERENCES Goals(GoalId) ON DELETE CASCADE,

        TemplateId INTEGER REFERENCES MissionTemplates(TemplateId) ON DELETE SET NULL,

        Title TEXT NOT NULL,
        Description TEXT,
        Type TEXT,
        TargetAmount REAL,
        Deadline TEXT NOT NULL,

        IsCompleted INTEGER DEFAULT 0,
        CreatedAt TEXT DEFAULT (datetime('now')),
        CompletedAt TEXT
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully (goalflow.db)")

if __name__ == "__main__":
    init_db()
