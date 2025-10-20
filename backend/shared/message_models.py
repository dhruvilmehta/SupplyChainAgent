from uagents import Model

class PurchaseRequest(Model):
    item: str
    quantity: int
    max_unit_price: float

class SupplierQuote(Model):
    item: str
    quantity: int
    unit_price: float
    delivery_time_days: int
    supplier_name: str

class NegotiationResult(Model):
    item: str
    quantity: int
    chosen_supplier: str
    unit_price: float
    delivery_time_days: int

class ShipmentOrder(Model):
    item: str
    quantity: int
    supplier: str
    delivery_time_days: int

class DeliveryNotification(Model):
    item: str
    quantity: int
    new_quantity: int  # total stock after restock
