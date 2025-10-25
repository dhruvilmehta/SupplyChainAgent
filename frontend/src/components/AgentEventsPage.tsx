import React, { useEffect, useState } from "react";

interface AgentEvent {
  agent_id: string;
  event: string;
  message?: string;
  timestamp?: string;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  [key: string]: any;
}

interface AgentGroup {
  [agentId: string]: AgentEvent[];
}

const AgentEventsPage: React.FC = () => {
  const [agents, setAgents] = useState<AgentGroup>({});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws");

    ws.onopen = () => {
      setConnected(true);
      console.log("✅ Connected to WebSocket");
    };

    ws.onmessage = (message) => {
      try {
        const data = JSON.parse(message.data) as AgentEvent;
        console.log(data)
        const { agent_id } = data;
        // if (!agent_id) return;

        setAgents((prev) => {
            const updated = {
                ...prev,
                [agent_id]: [data, ...(prev[agent_id] || [])],
            };
            console.log("Updated agents:", updated);
            return updated;
        });

        // console.log("Agents", agents);
      } catch {
        console.warn("Received non-JSON message:", message.data);
      }
    };

    ws.onclose = () => {
      setConnected(false);
      console.log("❌ WebSocket disconnected");
    };

    return () => ws.close();
  }, []);

  return (
    <div>
      <div style={{ marginBottom: "1.5rem" }}>
        <span
          style={{
            display: "inline-block",
            width: "12px",
            height: "12px",
            borderRadius: "50%",
            background: connected ? "#22c55e" : "#ef4444",
            marginRight: "8px",
          }}
        />
        <span style={{ fontWeight: 500 }}>
          {connected ? "Connected to backend" : "Disconnected"}
        </span>
      </div>

      {Object.keys(agents).length === 0 ? (
        <p style={{ color: "#6b7280" }}>No agent activity yet...</p>
      ) : (
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))",
            gap: "1.5rem",
          }}
        >
          {Object.entries(agents).map(([agentId, events]) => (
            <div
              key={agentId}
              style={{
                background: "white",
                borderRadius: "12px",
                boxShadow: "0 2px 8px rgba(0,0,0,0.08)",
                padding: "1rem",
                borderTop: "4px solid #3b82f6",
              }}
            >
              <h3
                style={{
                  fontSize: "1.1rem",
                  fontWeight: 600,
                  marginBottom: "0.5rem",
                  color: "#1f2937",
                }}
              >
                🧠 Agent: {agentId}
              </h3>
              <div style={{ fontSize: "0.9rem", color: "#4b5563" }}>
                {events.map((e, i) => (
                  <div
                    key={i}
                    style={{
                      background: "#f3f4f6",
                      borderRadius: "8px",
                      padding: "0.6rem",
                      marginBottom: "0.5rem",
                      lineHeight: "1.4",
                      color: "black"
                    }}
                  >
                    <div style={{ fontWeight: 500, color: "#111827" }}>
                      {e.event}
                    </div>
                    {e.message && <div>{e.message}</div>}
                    <div
                      style={{
                        fontSize: "0.75rem",
                        color: "#6b7280",
                        marginTop: "0.25rem",
                      }}
                    >
                      {e.timestamp
                        ? new Date(e.timestamp).toLocaleTimeString()
                        : new Date().toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AgentEventsPage;
