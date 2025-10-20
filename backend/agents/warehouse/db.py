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
        target_quantity INTEGER,
        reorder_pending INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    return conn

def get_low_stock_items():
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("""
        SELECT name, quantity, target_quantity
        FROM inventory
        WHERE quantity < reorder_threshold
          AND reorder_pending = 0
    """)
    items = cur.fetchall()
    conn.close()
    return items

def mark_reorder_pending(item_name: str):
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute(
        "UPDATE inventory SET reorder_pending = 1 WHERE name = ?",
        (item_name,)
    )
    conn.commit()
    conn.close()
    
def mark_restocked(item_name: str, new_quantity: int):
    conn = sqlite3.connect("warehouse.db")
    cur = conn.cursor()
    cur.execute("""
        UPDATE inventory
        SET quantity = ?, reorder_pending = 0
        WHERE name = ?
    """, (new_quantity, item_name))
    conn.commit()
    conn.close()

init_db()
print(get_low_stock_items())