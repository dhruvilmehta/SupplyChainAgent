from uagents import Agent, Context
from backend.shared.message_models import NegotiationResult, PurchaseRequest, ShipmentOrder, SupplierQuote

buyer = Agent(
    name="buyer_agent",
    seed="buyer_seed",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]  # Add explicit endpoint
)
# agent1q09h7c0xu2va8lrtezw59njcv37vxxl9n85amc04nvr0w9ez6emz2fnzrx2
SUPPLIER_ADDRESS="agent1qwx9j9a8d8ejkmu4t95xkuw4tjxtrdcw6tcfjgy92ck5xg0f7fgxuyvc5ht"

@buyer.on_message(model=PurchaseRequest)
async def handle_request(ctx: Context, sender: str, msg: PurchaseRequest):
    ctx.logger.info(f"✅ Received purchase request from {sender}: {msg.item} x{msg.quantity}")
    ctx.logger.info(f"Forwarding request for {msg.item} to NegotiationAgent (coming next).")
    await ctx.send(
        SUPPLIER_ADDRESS,
        PurchaseRequest(item=msg.item, quantity=msg.quantity, max_unit_price=msg.max_unit_price)
    )

LOGISTICS_AGENT_ADDRESS = "agent1qwnyz80p5gjhu2m4kn3cc2swwqqpa3w92nj84am73xkcsc4mgcyxjjpqn6j"  

@buyer.on_message(model=NegotiationResult)
async def handle_negotiation_result(ctx: Context, sender: str, msg: NegotiationResult):
    ctx.logger.info(
        f"🎯 Best quote received: {msg.chosen_supplier} @ ${msg.unit_price}/unit, ETA {msg.delivery_time_days} days"
    )

    # Create shipment order
    shipment = ShipmentOrder(
        item=msg.item,
        quantity=msg.quantity,
        supplier=msg.chosen_supplier,
        delivery_time_days=msg.delivery_time_days
    )

    # Send to LogisticsAgent
    await ctx.send(LOGISTICS_AGENT_ADDRESS, shipment)
    ctx.logger.info(f"📤 Shipment order sent to LogisticsAgent for {msg.item}.")

if __name__ == "__main__":
    print(f"Buyer agent address: {buyer.address}")
    print(f"Buyer agent running on: http://127.0.0.1:8001")
    buyer.run()