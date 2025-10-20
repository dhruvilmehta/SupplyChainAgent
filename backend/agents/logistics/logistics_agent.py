import asyncio
from uagents import Agent, Context
from backend.shared.message_models import ShipmentOrder, DeliveryNotification

logistics = Agent(
    name="logistics_agent",
    seed="logistics_seed",
    port=8004,
    endpoint=["http://127.0.0.1:8004/submit"]
)
# agent1qwnyz80p5gjhu2m4kn3cc2swwqqpa3w92nj84am73xkcsc4mgcyxjjpqn6j
WAREHOUSE_AGENT_ADDRESS = "agent1qt9j646aygmng6fac44n7jgg02hc6slw5y98yf2gc9pmtn6eywfjjfy5ywy"

@logistics.on_message(model=ShipmentOrder)
async def handle_shipment(ctx: Context, sender: str, msg: ShipmentOrder):
    """
    Simulate shipment creation and delivery.
    """
    ctx.logger.info(
        f"🚚 Received shipment order: {msg.item} x{msg.quantity} from {msg.supplier}, ETA {msg.delivery_time_days} days"
    )

    # Simulate shipment transit
    delivery_time_seconds = msg.delivery_time_days * 2  # speed up simulation
    ctx.logger.info(f"📦 Shipment in transit for {delivery_time_seconds}s (simulated)...")
    await asyncio.sleep(delivery_time_seconds)

    # Send delivery confirmation to WarehouseAgent
    delivered_qty = msg.quantity
    notification = DeliveryNotification(
        item=msg.item,
        quantity=delivered_qty,
        new_quantity=delivered_qty  # (you can later update this with DB)
    )

    await ctx.send(WAREHOUSE_AGENT_ADDRESS, notification)
    ctx.logger.info(f"✅ Delivered {msg.item} ({msg.quantity} units). Notification sent to WarehouseAgent.")

if __name__ == "__main__":
    print(f"Logistics agent address: {logistics.address}")
    logistics.run()