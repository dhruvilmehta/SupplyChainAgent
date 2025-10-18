from uagents import Model

class PurchaseRequest(Model):
    item: str
    quantity: int
    max_unit_price: float
