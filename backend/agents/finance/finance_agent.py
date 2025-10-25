import asyncio
import random
from uagents import Agent, Context
from backend.agents.finance.db import get_balance, init_db, log_transaction, update_balance
from backend.shared.event_bus import publish_event
from backend.shared.message_models import PaymentTrigger, PaymentConfirmation

finance = Agent(
    name="finance_agent",
    seed="finance_seed",
    port=8006,
    endpoint=["http://127.0.0.1:8006/submit"]
)
# agent1qw5a37ddlm9t6xckde6lvt6xvtf22n05hhxdql75d562nq7jkr6wy7h7qc0

# LOGISTICS_AGENT_ADDRESS = "agent1qwnyz80p5gjhu2m4kn3cc2swwqqpa3w92nj84am73xkcsc4mgcyxjjpqn6j"

FINANCE_ID = "FIN-001"

init_db()

@finance.on_message(model=PaymentConfirmation)
async def handle_payment(ctx: Context, sender: str, msg: PaymentConfirmation):
    ctx.logger.info(f"💵 Received payment request for shipment {msg.shipment_id} amount ${msg.amount}")
    
    publish_event(
        source="FinanceAgent",
        event_type="payment_request_received",
        message=f"Payment request received for shipment {msg.shipment_id} (${msg.amount}, status: {msg.status}).",
        data={
            "finance_id": FINANCE_ID,
            "shipment_id": msg.shipment_id,
            "amount": msg.amount,
            "status": msg.status,
            "sender": sender
        }
    )

    balance = get_balance()
    ctx.logger.info(f"🏦 Current balance: ${balance}")

    if msg.status == "hold":
        # Evaluate payment feasibility
        publish_event(
            source="FinanceAgent",
            event_type="payment_hold_evaluation",
            message=f"Evaluating hold for shipment {msg.shipment_id}.",
            data={
                "finance_id": FINANCE_ID,
                "shipment_id": msg.shipment_id,
                "balance": balance,
                "amount": msg.amount
            }
        )

        ctx.logger.info(f"Balance: {balance} Amount: {msg.amount}")
        if balance >= msg.amount:
            update_balance(msg.amount)
            log_transaction(msg.shipment_id, msg.amount, "approved", "Shipment Payment")
            ctx.logger.info(f"✅ Approved payment for {msg.shipment_id} (${msg.amount})")
            
            publish_event(
                source="FinanceAgent",
                event_type="payment_approved",
                message=f"Payment approved for shipment {msg.shipment_id} (${msg.amount}).",
                data={
                    "finance_id": FINANCE_ID,
                    "shipment_id": msg.shipment_id,
                    "amount": msg.amount,
                    "previous_balance": balance,
                    "new_balance": balance - msg.amount
                }
            )

            await ctx.send(
                sender,
                PaymentConfirmation(
                    shipment_id=msg.shipment_id,
                    amount=msg.amount,
                    status="approved"
                )
            )
        else:
            log_transaction(msg.shipment_id, msg.amount, "failed", "Insufficient funds")
            ctx.logger.info(f"❌ Payment failed for {msg.shipment_id}: Insufficient funds (${balance})")
            
            publish_event(
                source="FinanceAgent",
                event_type="payment_failed",
                message=f"Payment failed for shipment {msg.shipment_id}: Insufficient funds.",
                data={
                    "finance_id": FINANCE_ID,
                    "shipment_id": msg.shipment_id,
                    "balance": balance,
                    "required_amount": msg.amount
                }
            )

            await ctx.send(
                sender,
                PaymentConfirmation(
                    shipment_id=msg.shipment_id,
                    amount=msg.amount,
                    status="failed"
                )
            )

if __name__ == "__main__":
    print(f"Finance agent address: {finance.address}")
    finance.run()