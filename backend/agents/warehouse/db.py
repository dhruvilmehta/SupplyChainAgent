import sqlite3

def init_db():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            item_id TEXT PRIMARY KEY,
            name TEXT,
            quantity INTEGER,
            reorder_threshold INTEGER,
            target_quantity INTEGER
        )
    """)
    conn.commit()
    return conn

def get_low_stock_items():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("SELECT name, quantity, reorder_threshold, target_quantity FROM inventory")
    low = []
    for name, qty, thresh, target in cur.fetchall():
        if qty < thresh:
            low.append((name, qty, target))
    conn.close()
    return low

init_db()
print(get_low_stock_items())