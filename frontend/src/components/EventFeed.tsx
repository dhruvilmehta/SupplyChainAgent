import React, { useEffect, useState } from "react";

interface EventMessage {
  event: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

const EventFeed: React.FC = () => {
  const [events, setEvents] = useState<EventMessage[]>([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      console.log("✅ Connected to WebSocket");
      setConnected(true);
    };

    ws.onmessage = (message) => {
      try {
        const data = JSON.parse(message.data);
        setEvents((prev) => [data, ...prev]);
      } catch {
        // Handle raw string messages too
        setEvents((prev) => [{ event: message.data }, ...prev]);
      }
    };

    ws.onclose = () => {
      console.log("❌ WebSocket disconnected");
      setConnected(false);
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      <p>
        Status:{" "}
        <span style={{ color: connected ? "green" : "red" }}>
          {connected ? "Connected" : "Disconnected"}
        </span>
      </p>

      <div
        style={{
          border: "1px solid #ddd",
          borderRadius: "8px",
          padding: "1rem",
          maxHeight: "400px",
          overflowY: "auto",
          background: "#fafafa",
          color: "black"
        }}
      >
        {events.length === 0 ? (
          <p>No events yet...</p>
        ) : (
          events.map((event, index) => (
            <div
              key={index}
              style={{
                borderBottom: "1px solid #eee",
                marginBottom: "0.5rem",
                paddingBottom: "0.5rem",
              }}
            >
              <pre style={{ margin: 0, fontSize: "0.9rem" }}>
                {JSON.stringify(event, null, 2)}
              </pre>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default EventFeed;
