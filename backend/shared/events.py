from pydantic import BaseModel
from datetime import datetime

class AgentEvent(BaseModel):
    source: str          # e.g. "WarehouseAgent"
    event_type: str      # e.g. "restock_complete", "shipment_created"
    message: str         # human-readable log
    data: dict           # structured payload (item, quantity, etc.)
    timestamp: datetime
