import sqlite3
from datetime import datetime
import uuid

DB_PATH = "transactions.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY,
            shipment_id TEXT,
            amount REAL,
            status TEXT,
            reason TEXT,
            created_at TEXT
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            name TEXT PRIMARY KEY,
            balance REAL
        )
    """)
    conn.commit()

    # Seed with a main account if not exists
    cur.execute("SELECT COUNT(*) FROM accounts WHERE name = ?", ("main_wallet",))
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", ("main_wallet", 50000.0))
    conn.commit()
    conn.close()


def get_balance(account_name="main_wallet"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT balance FROM accounts WHERE name = ?", (account_name,))
    row = cur.fetchone()
    conn.close()
    return row[0] if row else 0.0


def update_balance(amount, account_name="main_wallet"):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE accounts SET balance = balance - ? WHERE name = ?", (amount, account_name))
    conn.commit()
    conn.close()


def log_transaction(shipment_id, amount, status, reason):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    txn_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO transactions (id, shipment_id, amount, status, reason, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (txn_id, shipment_id, amount, status, reason, created_at))
    conn.commit()
    conn.close()
    return txn_id
