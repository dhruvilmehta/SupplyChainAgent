import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

app = FastAPI()

# Redis client (adjust host/port as needed)
redis = Redis(host="localhost", port=6379, decode_responses=True)

# Keep track of active websocket connections
active_connections: set[WebSocket] = set()


async def redis_listener():
    """Background task: listens for Redis 'agent_events' and broadcasts to WebSocket clients."""
    pubsub = redis.pubsub()
    await pubsub.subscribe("agent_events")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"]
            print(data)
            await broadcast(data)


async def broadcast(message: str):
    """Send message to all connected WebSocket clients."""
    disconnected = []
    for connection in active_connections:
        try:
            await connection.send_text(message)
        except WebSocketDisconnect:
            disconnected.append(connection)
    for conn in disconnected:
        active_connections.remove(conn)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(redis_listener())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Handle WebSocket connections."""
    await websocket.accept()
    active_connections.add(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive; ignore client messages
    except WebSocketDisconnect:
        active_connections.remove(websocket)
