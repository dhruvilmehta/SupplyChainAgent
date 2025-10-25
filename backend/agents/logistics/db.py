import sqlite3
import random
import uuid
from datetime import datetime, timedelta

DB_PATH = "shipments.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id TEXT PRIMARY KEY,
            item TEXT,
            quantity INTEGER,
            supplier_name TEXT,
            unit_price REAL,
            cost REAL,
            carrier TEXT,
            eta_days INTEGER,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def create_shipment(item: str, quantity: int) -> dict:
    shipment_id = str(uuid.uuid4())[:8]
    carrier = random.choice(["DHL", "FedEx", "UPS", "BlueDart"])
    cost = round(random.uniform(100, 500), 2)
    eta_days = random.randint(2, 7)

    shipment = {
        "id": shipment_id,
        "item": item,
        "quantity": quantity,
        "carrier": carrier,
        "cost": cost,
        "eta_days": eta_days,
        "status": "CREATED",
        "created_at": datetime.utcnow().isoformat()
    }

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO shipments (id, item, quantity, carrier, cost, eta_days, status, created_at)
        VALUES (:id, :item, :quantity, :carrier, :cost, :eta_days, :status, :created_at)
    """, shipment)
    conn.commit()
    conn.close()

    return shipment

def create_shipment(item, quantity, supplier_name, unit_price, eta_days):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    shipment_id = str(uuid.uuid4())
    carrier = "FastShip Logistics"
    cost = round(unit_price * quantity * 0.05, 2)  # Example: 5% of item cost
    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO shipments (id, item, quantity, supplier_name, unit_price, cost, carrier, eta_days, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (shipment_id, item, quantity, supplier_name, unit_price, cost, carrier, eta_days, "pending", created_at))
    conn.commit()
    conn.close()

    return {
        "shipment_id": shipment_id,
        "carrier": carrier,
        "cost": cost,
        "eta_days": eta_days
    }

def update_status(shipment_id: str, new_status: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        UPDATE shipments
        SET status = ?
        WHERE id = ?
    """, (new_status, shipment_id))
    conn.commit()
    conn.close()


def list_shipments():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT * FROM shipments")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_shipment_details(shipment_id: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        SELECT item, quantity, supplier_name, unit_price, status
        FROM shipments
        WHERE id = ?
    """, (shipment_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {
            "item": row[0],
            "quantity": row[1],
            "supplier_name": row[2],
            "unit_price": row[3],
            "status": row[4],
        }
    return None