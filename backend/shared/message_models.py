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
    unit_price: int

# class DeliveryNotification(Model):
#     item: str
#     quantity: int
#     new_quantity: int  # total stock after restock

class DeliveryNotification(Model):
    shipment_id: str

# class ShipmentStatus(Model):
#     shipment_id: str
#     item: str
#     quantity: int
#     supplier: str
#     status: str  # e.g., "in_transit", "delivered"
#     progress: int  # 0-100%

class ShipmentCreated(Model):
    shipment_id: str
    carrier: str
    cost: float
    eta_days: int
    item: str
    quantity: int

class PaymentTrigger(Model):
    supplier: str
    amount: float
    item: str
    quantity: int
    # reason: str               # "inventory_restock", "shipping_fee"
    # reference_id: str
    currency: str = "USD"

class PaymentConfirmation(Model):
    shipment_id: str
    amount: float
    status: str  # "approved" | "failed" | "hold"
