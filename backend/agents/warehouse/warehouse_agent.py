from uagents import Agent, Context
from backend.shared.message_models import PurchaseRequest
from backend.agents.warehouse.db import init_db, get_low_stock_items

warehouse = Agent(
    name="warehouse_agent",
    seed="warehouse_seed",
    port=8002
)

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

if __name__ == "__main__":
    print(f"Warehouse agent address: {warehouse.address}")
    warehouse.run()