from uagents import Agent, Context, Model
from backend.shared.message_models import PurchaseRequest

buyer = Agent(
    name="buyer_agent", 
    seed="buyer_seed",
    port=8001,
    endpoint=["http://127.0.0.1:8001/submit"]  # Add explicit endpoint
)

@buyer.on_message(model=PurchaseRequest)
async def handle_request(ctx: Context, sender: str, msg: PurchaseRequest):
    ctx.logger.info(f"✅ Received purchase request from {sender}: {msg.item} x{msg.quantity}")
    ctx.logger.info(f"Forwarding request for {msg.item} to NegotiationAgent (coming next).")

if __name__ == "__main__":
    print(f"Buyer agent address: {buyer.address}")
    print(f"Buyer agent running on: http://127.0.0.1:8001")
    buyer.run()