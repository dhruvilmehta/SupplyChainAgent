import sqlite3
from datetime import datetime

DB_PATH = "tracking_log.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tracking_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id TEXT,
            carrier TEXT,
            item TEXT,
            quantity INTEGER,
            progress INTEGER,
            status TEXT,
            last_updated TEXT
        )
    """)
    conn.commit()
    conn.close()

def start_tracking(shipment_id: str, carrier: str, item: str, quantity: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO tracking_log (shipment_id, carrier, item, quantity, progress, status, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (shipment_id, carrier, item, quantity, 0, "in_transit", datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_active_shipments():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT shipment_id, carrier, item, quantity, progress, status FROM tracking_log WHERE status != 'delivered'")
    rows = cur.fetchall()
    conn.close()
    return rows


def update_tracking(shipment_id: str, progress: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE tracking_log
        SET progress = ?, status = ?, last_updated = ?
        WHERE shipment_id = ?
    """, (progress, status, datetime.utcnow().isoformat(), shipment_id))
    conn.commit()
    conn.close()
