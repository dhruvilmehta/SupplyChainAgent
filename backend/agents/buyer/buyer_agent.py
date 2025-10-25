import uuid
from uagents import Agent, Context
from backend.agents.logistics.db import create_shipment
from backend.shared.event_bus import publish_event
from backend.shared.message_models import NegotiationResult, PurchaseRequest, ShipmentOrder, SupplierQuote

buyer = Agent(
    name="buyer_agent",
    seed="buyer_seed",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]  # Add explicit endpoint
)
# agent1q09h7c0xu2va8lrtezw59njcv37vxxl9n85amc04nvr0w9ez6emz2fnzrx2
NEGOTIATION_AGENT="agent1qwx9j9a8d8ejkmu4t95xkuw4tjxtrdcw6tcfjgy92ck5xg0f7fgxuyvc5ht"

BUYER_ID = "BUY-001"  

@buyer.on_message(model=PurchaseRequest)
async def handle_request(ctx: Context, sender: str, msg: PurchaseRequest):
    ctx.logger.info(f"✅ Received purchase request from {sender}: {msg.item} x{msg.quantity}")
    ctx.logger.info(f"Forwarding request for {msg.item} to NegotiationAgent.")
    
    publish_event(
        source="BuyerAgent",
        event_type="purchase_request_received",
        message=f"Received purchase request for {msg.item} ({msg.quantity}) from WarehouseAgent.",
        data={
            "buyer_id": BUYER_ID,
            "sender": sender,
            "item": msg.item,
            "quantity": msg.quantity,
            "max_unit_price": msg.max_unit_price
        }
    )

    await ctx.send(
        NEGOTIATION_AGENT,
        PurchaseRequest(item=msg.item, quantity=msg.quantity, max_unit_price=msg.max_unit_price)
    )
    
    publish_event(
        source="BuyerAgent",
        event_type="negotiation_initiated",
        message=f"Sent purchase request for {msg.item} to NegotiationAgent.",
        data={
            "buyer_id": BUYER_ID,
            "negotiation_agent": NEGOTIATION_AGENT,
            "item": msg.item,
            "quantity": msg.quantity
        }
    )

LOGISTICS_AGENT_ADDRESS = "agent1qwnyz80p5gjhu2m4kn3cc2swwqqpa3w92nj84am73xkcsc4mgcyxjjpqn6j"  

@buyer.on_message(model=NegotiationResult)
async def handle_negotiation_result(ctx: Context, sender: str, msg: NegotiationResult):
    ctx.logger.info(
        f"🎯 Best quote received: {msg.chosen_supplier} @ ${msg.unit_price}/unit, ETA {msg.delivery_time_days} days"
    )

    publish_event(
        source="BuyerAgent",
        event_type="best_quote_received",
        message=(
            f"Best quote selected from {msg.chosen_supplier} "
            f"for {msg.item} ({msg.quantity} units @ ${msg.unit_price}/unit)"
        ),
        data={
            "buyer_id": BUYER_ID,
            "item": msg.item,
            "quantity": msg.quantity,
            "supplier": msg.chosen_supplier,
            "unit_price": msg.unit_price,
            "delivery_time_days": msg.delivery_time_days
        }
    )

    # Create shipment order
    shipment = ShipmentOrder(
        item=msg.item,
        quantity=msg.quantity,
        supplier=msg.chosen_supplier,
        delivery_time_days=msg.delivery_time_days,
        unit_price=msg.unit_price
    )

    # Send to LogisticsAgent
    await ctx.send(LOGISTICS_AGENT_ADDRESS, shipment)
    ctx.logger.info(f"📤 Shipment order sent to LogisticsAgent for {msg.item}.")
    
    publish_event(
        source="BuyerAgent",
        event_type="shipment_order_created",
        message=f"Shipment order details sent to LogisticsAgent for {msg.item}.",
        data={
            "buyer_id": BUYER_ID,
            "item": msg.item,
            "quantity": msg.quantity,
            "supplier_name": msg.chosen_supplier,
            "unit_price": msg.unit_price,
            "delivery_time_days": msg.delivery_time_days,
            "logistics_agent": LOGISTICS_AGENT_ADDRESS
        }
    )

if __name__ == "__main__":
    print(f"Buyer agent address: {buyer.address}")
    print(f"Buyer agent running on: http://127.0.0.1:8001")
    buyer.run()