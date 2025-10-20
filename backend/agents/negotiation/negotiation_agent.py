import asyncio
import random
from uagents import Agent, Context
from backend.shared.message_models import NegotiationResult, PurchaseRequest, SupplierQuote

negotiation_agent = Agent(
    name="supplier_agent",
    seed="supplier_seed",
    port=8010,
    endpoint=["http://127.0.0.1:8010/submit"]
)
# agent1qwx9j9a8d8ejkmu4t95xkuw4tjxtrdcw6tcfjgy92ck5xg0f7fgxuyvc5ht
# Internal supplier database
SUPPLIERS = {
    "Supplier A": {"base_price": 38, "delivery_days": 3},
    "Supplier B": {"base_price": 42, "delivery_days": 2},
    "Supplier C": {"base_price": 36, "delivery_days": 5},
}

@negotiation_agent.on_message(model=PurchaseRequest)
async def handle_purchase_request(ctx: Context, sender: str, msg: PurchaseRequest):
    """
    Receive a purchase request from BuyerAgent and simulate
    multiple supplier quotes (hardcoded/randomized).
    """
    ctx.logger.info(f"🤝 Received purchase request for {msg.item} ({msg.quantity})")

    # Simulate supplier quotes (no SupplierAgent yet)
    quotes = []
    for name, data in SUPPLIERS.items():
        unit_price = round(random.uniform(data["base_price"] - 2, data["base_price"] + 2), 2)
        delivery_time = max(1, data["delivery_days"] + random.randint(-1, 1))
        quotes.append({
            "supplier": name,
            "price": unit_price,
            "eta": delivery_time
        })
        ctx.logger.info(f"💰 {name} quote: ${unit_price}/unit, ETA {delivery_time} days")

    # Simulate waiting time as if quotes were received asynchronously
    await asyncio.sleep(3)

    # Pick best quote (lowest price, then fastest delivery)
    best = sorted(quotes, key=lambda q: (q["price"], q["eta"]))[0]
    ctx.logger.info(
        f"✅ Best offer: {best['supplier']} "
        f"@ ${best['price']}/unit (ETA {best['eta']} days)"
    )

    # Send the result to BuyerAgent
    result = NegotiationResult(
        item=msg.item,
        quantity=msg.quantity,
        chosen_supplier=best["supplier"],
        unit_price=best["price"],
        delivery_time_days=best["eta"]
    )

    await ctx.send(sender, result)
    ctx.logger.info("📨 Sent best quote result to BuyerAgent.")

if __name__ == "__main__":
    print(f"Supplier agent address: {negotiation_agent.address}")
    negotiation_agent.run()
