import asyncio
import random
from uagents import Agent, Context
from backend.agents.tracking.db import get_active_shipments, start_tracking, update_tracking
from backend.agents.tracking.db import init_db
from backend.shared.event_bus import publish_event
from backend.shared.message_models import ShipmentCreated, DeliveryNotification

tracking = Agent(
    name="tracking_agent",
    seed="tracking_seed",
    port=8005,
    endpoint=["http://127.0.0.1:8005/submit"]
)
# agent1q0pxgnkpv7yfhwgu9fmhevfmx5h7gq9a6pxacgds877zcz29afm6yqjh266
WAREHOUSE_AGENT_ADDRESS = "agent1qt9j646aygmng6fac44n7jgg02hc6slw5y98yf2gc9pmtn6eywfjjfy5ywy"

# Initialize DB
init_db()

TRACKING_ID = "TRK-001"

@tracking.on_message(model=ShipmentCreated)
async def handle_new_shipment(ctx: Context, sender: str, msg: ShipmentCreated):
    ctx.logger.info(f"📦 Tracking shipment {msg.shipment_id} for {msg.item} ({msg.quantity} units)")
    start_tracking(msg.shipment_id, msg.carrier, msg.item, msg.quantity)
    
    publish_event(
        source="TrackingAgent",
        event_type="tracking_started",
        message=f"Started tracking shipment {msg.shipment_id} for {msg.item}.",
        data={
            "tracking_id": TRACKING_ID,
            "shipment_id": msg.shipment_id,
            "carrier": msg.carrier,
            "item": msg.item,
            "quantity": msg.quantity,
            "sender": sender
        }
    )


@tracking.on_interval(period=10.0)
async def update_progress(ctx: Context):
    active = get_active_shipments()
    if not active:
        ctx.logger.info("No active shipments.")
        return

    for shipment_id, carrier, item, quantity, progress, status in active:
        increment = random.choice([10, 20, 25])
        new_progress = min(100, progress + increment)

        if new_progress >= 100:
            status = "delivered"
            ctx.logger.info(f"✅ Shipment {shipment_id} ({item}) delivered! Notifying WarehouseAgent.")
            update_tracking(shipment_id, new_progress, status)

            publish_event(
                source="TrackingAgent",
                event_type="shipment_delivered",
                message=f"Shipment {shipment_id} delivered successfully.",
                data={
                    "tracking_id": TRACKING_ID,
                    "shipment_id": shipment_id,
                    "item": item,
                    "quantity": quantity,
                    "carrier": carrier,
                    "progress": 100,
                    "status": status
                }
            )

            await ctx.send(
                WAREHOUSE_AGENT_ADDRESS,
                DeliveryNotification(shipment_id=shipment_id)
            )
        else:
            status = "in_transit"
            ctx.logger.info(f"🚚 Shipment {shipment_id} ({item}): {new_progress}% complete.")
            publish_event(
                source="TrackingAgent",
                event_type="shipment_progress",
                message=f"Shipment {shipment_id} progress updated to {new_progress}%.",
                data={
                    "tracking_id": TRACKING_ID,
                    "shipment_id": shipment_id,
                    "item": item,
                    "carrier": carrier,
                    "progress": new_progress,
                    "status": status
                }
            )

        update_tracking(shipment_id, min(100, new_progress), status)

if __name__ == "__main__":
    print(f"Tracking agent address: {tracking.address}")
    tracking.run()