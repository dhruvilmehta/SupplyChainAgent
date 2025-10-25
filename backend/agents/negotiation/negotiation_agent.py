from uagents import Agent, Context
from backend.agents.negotiation.db import get_supplier_quotes
from backend.agents.negotiation.db import init_db
from backend.shared.event_bus import publish_event
from backend.shared.message_models import NegotiationResult, PurchaseRequest, SupplierQuote

negotiation_agent = Agent(
    name="supplier_agent",
    seed="supplier_seed",
    port=8010,
    endpoint=["http://127.0.0.1:8010/submit"]
)
# agent1qwx9j9a8d8ejkmu4t95xkuw4tjxtrdcw6tcfjgy92ck5xg0f7fgxuyvc5ht

# Initialize supplier database
init_db()

NEGOTIATION_AGENT_ID = "NEG-001"

@negotiation_agent.on_message(model=PurchaseRequest)
async def handle_purchase_request(ctx: Context, sender: str, msg: PurchaseRequest):
    """
    Handle purchase requests dynamically using supplier DB.
    """
    ctx.logger.info(f"🤝 Received purchase request: {msg.item} x{msg.quantity}")
    
    publish_event(
        source="NegotiationAgent",
        event_type="negotiation_started",
        message=f"Negotiation started for {msg.item} ({msg.quantity} units) from BuyerAgent.",
        data={
            "negotiation_id": NEGOTIATION_AGENT_ID,
            "buyer_agent": sender,
            "item": msg.item,
            "quantity": msg.quantity
        }
    )

    # Fetch quotes dynamically
    quotes = get_supplier_quotes(msg.item, msg.quantity)
    quote_records = []
    for q in quotes:
        ctx.logger.info(
            f"💰 {q['supplier']}: ${q['price']}/unit, ETA {q['eta']} days, "
            f"Reliability {q['reliability']*100:.1f}%"
        )
        quote_records.append({
            "supplier": q["supplier"],
            "price": q["price"],
            "eta": q["eta"],
            "reliability": q["reliability"]
        })

    publish_event(
        source="NegotiationAgent",
        event_type="quotes_fetched",
        message=f"Fetched {len(quotes)} supplier quotes for {msg.item}.",
        data={
            "negotiation_id": NEGOTIATION_AGENT_ID,
            "item": msg.item,
            "quantity": msg.quantity,
            "quotes": quote_records
        }
    )

    # Evaluate quotes (multi-criteria: price + reliability + speed)
    def score(q):
        return (q["price"] * 0.7) - (q["reliability"] * 10) + (q["eta"] * 0.3)

    best = sorted(quotes, key=score)[0]

    ctx.logger.info(
        f"✅ Selected {best['supplier']} as best supplier: ${best['price']}/unit, "
        f"ETA {best['eta']} days, Reliability {best['reliability']*100:.1f}%"
    )

    publish_event(
        source="NegotiationAgent",
        event_type="best_supplier_selected",
        message=f"Best supplier chosen: {best['supplier']} for {msg.item} (${best['price']}/unit).",
        data={
            "negotiation_id": NEGOTIATION_AGENT_ID,
            "item": msg.item,
            "quantity": msg.quantity,
            "chosen_supplier": best["supplier"],
            "unit_price": best["price"],
            "delivery_time_days": best["eta"],
            "reliability": best["reliability"]
        }
    )

    result = NegotiationResult(
        item=msg.item,
        quantity=msg.quantity,
        chosen_supplier=best["supplier"],
        unit_price=best["price"],
        delivery_time_days=best["eta"]
    )

    await ctx.send(sender, result)
    ctx.logger.info(f"📨 Sent NegotiationResult to BuyerAgent for {msg.item}.")

    publish_event(
        source="NegotiationAgent",
        event_type="negotiation_completed",
        message=f"Negotiation completed for {msg.item}, selected {best['supplier']}.",
        data={
            "negotiation_id": NEGOTIATION_AGENT_ID,
            "buyer_agent": sender,
            "item": msg.item,
            "quantity": msg.quantity,
            "chosen_supplier": best["supplier"],
            "final_price": best["price"],
            "delivery_time_days": best["eta"]
        }
    )


if __name__ == "__main__":
    print(f"Supplier agent address: {negotiation_agent.address}")
    negotiation_agent.run()
