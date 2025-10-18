import sqlite3

conn = sqlite3.connect("warehouse.db")
cur = conn.cursor()
cur.executemany("""
INSERT OR REPLACE INTO inventory (item_id, name, quantity, reorder_threshold, target_quantity)
VALUES (?, ?, ?, ?, ?)
""", [
    ("BAT4000", "Battery 4000mAh", 120, 100, 500),
    ("LCD15", "15-inch LCD Screen", 300, 200, 500),
    ("CPU7000", "CPU i7-7000", 120, 150, 400),
])
conn.commit()
conn.close()
