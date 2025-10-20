import sqlite3
from uagents import Agent, Context
from backend.shared.message_models import DeliveryNotification, PurchaseRequest
from backend.agents.warehouse.db import init_db, get_low_stock_items, mark_reorder_pending

warehouse = Agent(
    name="warehouse_agent",
    seed="warehouse_seed",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"]
)
# agent1qt9j646aygmng6fac44n7jgg02hc6slw5y98yf2gc9pmtn6eywfjjfy5ywy
# Initialize database
init_db()

# CORRECT buyer address
BUYER_ADDRESS = "agent1q09h7c0xu2va8lrtezw59njcv37vxxl9n85amc04nvr0w9ez6emz2fnzrx2"

# Periodic task: check stock every 60 seconds
@warehouse.on_interval(period=60.0)
async def check_inventory(ctx: Context):
    low_items = get_low_stock_items()
    
    if not low_items:
        ctx.logger.info("Stock levels are healthy.")
        return

    for name, qty, target in low_items:
        order_quantity = target - qty
        ctx.logger.info(f"Low stock detected: {name} ({qty} left). Ordering {order_quantity} units.")
        await ctx.send(
            BUYER_ADDRESS,
            PurchaseRequest(item=name, quantity=order_quantity, max_unit_price=50.0)
        )
        mark_reorder_pending(name)
        ctx.logger.info(f"Marked {name} as reorder_pending to prevent duplicates.")


@warehouse.on_message(model=DeliveryNotification)
async def handle_delivery(ctx: Context, sender: str, msg: DeliveryNotification):
    mark_restocked(msg.item, msg.new_quantity)
    ctx.logger.info(f"Restock complete for {msg.item} ({msg.new_quantity} units).")

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

if __name__ == "__main__":
    print(f"Warehouse agent address: {warehouse.address}")
    warehouse.run()