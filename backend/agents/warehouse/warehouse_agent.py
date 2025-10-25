import sqlite3
from uagents import Agent, Context
from backend.agents.logistics.db import get_shipment_details
from backend.shared.event_bus import publish_event
from backend.shared.message_models import DeliveryNotification, PurchaseRequest
from backend.agents.warehouse.db import get_inventory_item_id, init_db, get_low_stock_items, mark_reorder_pending, mark_restocked

warehouse = Agent(
    name="warehouse_agent",
    seed="warehouse_seed",
    port=8002,
    endpoint=["http://127.0.0.1:8002/submit"]
)
# agent1qt9j646aygmng6fac44n7jgg02hc6slw5y98yf2gc9pmtn6eywfjjfy5ywy
# Initialize database
init_db()

BUYER_ADDRESS = "agent1q09h7c0xu2va8lrtezw59njcv37vxxl9n85amc04nvr0w9ez6emz2fnzrx2"

WAREHOUSE_ID = "WH-001"  # You can store this in config/env

# Periodic task: check stock every 60 seconds
@warehouse.on_interval(period=60.0)
async def check_inventory(ctx: Context):
    low_items = get_low_stock_items()
    
    if not low_items:
        ctx.logger.info("Stock levels are healthy.")
        return

    for item_id, name, qty, target in low_items:
        order_quantity = target - qty
        ctx.logger.info(f"Low stock detected: {name} ({qty} left). Ordering {order_quantity} units.")
        await ctx.send(
            BUYER_ADDRESS,
            PurchaseRequest(item=name, quantity=order_quantity, max_unit_price=50.0)
        )
        mark_reorder_pending(name)
        
        publish_event(
            source="WarehouseAgent",
            event_type="low_stock_detected",
            message=f"Low stock detected for {name}. Order of {order_quantity} units sent to BuyerAgent.",
            data={
                "warehouse_id": WAREHOUSE_ID,
                "inventory_id": item_id,
                "item": name,
                "current_quantity": qty,
                "order_quantity": order_quantity,
                "target_quantity": target
            }
        )

        ctx.logger.info(f"Marked {name} as reorder_pending to prevent duplicates.")

@warehouse.on_message(model=DeliveryNotification)
async def handle_delivery(ctx: Context, sender: str, msg: DeliveryNotification):
    ctx.logger.info(f"📦 Delivery confirmation received for shipment {msg.shipment_id}")

    shipment = get_shipment_details(msg.shipment_id)
    if not shipment:
        ctx.logger.warning(f"⚠️ Shipment details not found for ID {msg.shipment_id}. Cannot restock.")
        
        publish_event(
            source="WarehouseAgent",
            event_type="shipment_error",
            message=f"Shipment details not found for ID {msg.shipment_id}",
            data={"shipment_id": msg.shipment_id}
        )
        return

    item = shipment["item"]
    quantity = shipment["quantity"]
    item_id = get_inventory_item_id(item)

    ctx.logger.info(f"✅ Shipment details fetched: {item} ({quantity} units). Updating inventory...")
    mark_restocked(item, quantity)
    ctx.logger.info(f"📦 Restock complete for {item}: added {quantity} units to inventory.")
    
    publish_event(
        source="WarehouseAgent",
        event_type="restock_complete",
        message=f"Restock complete for Shipment ID {msg.shipment_id} ({item}, +{quantity})",
        data={
            "warehouse_id": WAREHOUSE_ID,
            "shipment_id": msg.shipment_id,
            "inventory_id": item_id,
            "item": item,
            "quantity_added": quantity
        }
    )


if __name__ == "__main__":
    print(f"Warehouse agent address: {warehouse.address}")
    warehouse.run()