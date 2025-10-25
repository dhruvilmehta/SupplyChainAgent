import sqlite3
import random

DB_PATH = "suppliers.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            base_price REAL,
            delivery_days INTEGER,
            reliability REAL
        )
    """)
    conn.commit()

    # Seed some sample suppliers if DB empty
    cur.execute("SELECT COUNT(*) FROM suppliers")
    if cur.fetchone()[0] == 0:
        suppliers = [
            ("Supplier A", 38.0, 3, 0.95),
            ("Supplier B", 42.0, 2, 0.88),
            ("Supplier C", 36.0, 5, 0.92),
        ]
        cur.executemany("INSERT INTO suppliers (name, base_price, delivery_days, reliability) VALUES (?, ?, ?, ?)", suppliers)
    conn.commit()
    conn.close()

def get_supplier_quotes(item: str, quantity: int):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, base_price, delivery_days, reliability FROM suppliers")
    suppliers = cur.fetchall()
    conn.close()

    quotes = []
    for name, price, days, reliability in suppliers:
        adj_price = round(price * random.uniform(0.9, 1.1), 2)
        adj_days = max(1, days + random.randint(-1, 1))
        quotes.append({
            "supplier": name,
            "price": adj_price,
            "eta": adj_days,
            "reliability": reliability
        })
    return quotes
