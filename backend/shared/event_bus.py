import redis
from datetime import datetime
from backend.shared.events import AgentEvent

redis_client = redis.Redis(host="localhost", port=6379, db=0)

def publish_event(source: str, event_type: str, message: str, data: dict = {}):
    event = AgentEvent(
        source=source,
        event_type=event_type,
        message=message,
        data=data,
        timestamp=datetime.utcnow()
    )
    redis_client.publish("agent_events", event.json())
