from uagents import Bureau
from backend.agents.warehouse.warehouse_agent import warehouse
from backend.agents.buyer.buyer_agent import buyer

# Create a bureau and add both agents to it
bureau = Bureau()
bureau.add(warehouse)
bureau.add(buyer)

# Store the buyer's address in the warehouse's storage for communication
warehouse.ctx.storage.set("buyer_address", buyer.address)

# Run the bureau
if __name__ == "__main__":
    print(f"Buyer agent address: {buyer.address}")
    bureau.run()

