from uagents import Agent, Context
from backend.agents.logistics.db import create_shipment, update_status
from backend.agents.logistics.db import init_db
from backend.shared.event_bus import publish_event
from backend.shared.message_models import PaymentConfirmation, ShipmentCreated, ShipmentOrder

logistics = Agent(
    name="logistics_agent",
    seed="logistics_seed",
    port=8004,
    endpoint=["http://127.0.0.1:8004/submit"]
)
# agent1qwnyz80p5gjhu2m4kn3cc2swwqqpa3w92nj84am73xkcsc4mgcyxjjpqn6j
# WAREHOUSE_AGENT_ADDRESS = "agent1qt9j646aygmng6fac44n7jgg02hc6slw5y98yf2gc9pmtn6eywfjjfy5ywy"
TRACKING_AGENT_ADDRESS = "agent1q0pxgnkpv7yfhwgu9fmhevfmx5h7gq9a6pxacgds877zcz29afm6yqjh266"
FINANCE_AGENT_ADDRESS = "agent1qw5a37ddlm9t6xckde6lvt6xvtf22n05hhxdql75d562nq7jkr6wy7h7qc0"
LOGISTICS_ID = "LOG-001"

CARRIERS = ["DHL", "FedEx", "UPS", "BlueDart"]

init_db()

@logistics.on_message(model=ShipmentOrder)
async def handle_shipment_order(ctx: Context, sender: str, msg: ShipmentOrder):
    """
    Enhanced logistics process: choose carrier, estimate cost, and initiate tracking.
    """
    ctx.logger.info(f"🚚 Processing shipment order for {msg.item} ({msg.quantity})")

    shipment = create_shipment(
        msg.item, msg.quantity, msg.supplier, msg.unit_price, msg.delivery_time_days
    )

    ctx.logger.info(
        f"🚛 Shipment {shipment['shipment_id']} created | Carrier: {shipment['carrier']} | ETA: {shipment['eta_days']} days"
    )
    
    publish_event(
        source="LogisticsAgent",
        event_type="shipment_created",
        message=f"Shipment {shipment['shipment_id']} created for {msg.item} ({msg.quantity} units).",
        data={
            "logistics_id": LOGISTICS_ID,
            "shipment_id": shipment["shipment_id"],
            "item": msg.item,
            "quantity": msg.quantity,
            "supplier_name": msg.supplier,
            "carrier": shipment["carrier"],
            "shipment_cost": shipment["cost"]
        }
    )

    # Notify FinanceAgent to hold funds
    total_cost = msg.unit_price * msg.quantity + shipment["cost"]
    await ctx.send(FINANCE_AGENT_ADDRESS, PaymentConfirmation(
        shipment_id=shipment["shipment_id"],
        amount=total_cost,
        status="hold"
    ))

    ctx.logger.info(f"💳 Shipping cost sent to FinanceAgent.")
    
    publish_event(
        source="LogisticsAgent",
        event_type="payment_request_sent",
        message=f"Requested payment hold for shipment {shipment['shipment_id']} (${shipment['cost']}).",
        data={
            "shipment_id": shipment["shipment_id"],
            "supplier_name": msg.supplier,
            "amount": shipment["cost"],
            "finance_agent": FINANCE_AGENT_ADDRESS
        }
    )

    # Notify TrackingAgent to start shipment
    await ctx.send(TRACKING_AGENT_ADDRESS, ShipmentCreated(
        shipment_id=shipment["shipment_id"],
        carrier=shipment["carrier"],
        cost=shipment["cost"],
        eta_days=shipment["eta_days"],
        item=msg.item,
        quantity=msg.quantity
    ))
    
    publish_event(
        source="LogisticsAgent",
        event_type="tracking_initiated",
        message=f"Tracking started for shipment {shipment['shipment_id']}.",
        data={
            "shipment_id": shipment["shipment_id"],
            "carrier": shipment["carrier"],
            "tracking_agent": TRACKING_AGENT_ADDRESS
        }
    )

    
@logistics.on_message(model=PaymentConfirmation)
async def handle_payment_confirmation(ctx: Context, sender: str, msg: PaymentConfirmation):
    ctx.logger.info(f"💰 Payment {msg.status} for shipment {msg.shipment_id}")

    if msg.status == "approved":
        update_status(msg.shipment_id, "in_transit")
    elif msg.status == "failed":
        update_status(msg.shipment_id, "cancelled")

if __name__ == "__main__":
    print(f"Logistics agent address: {logistics.address}")
    logistics.run()