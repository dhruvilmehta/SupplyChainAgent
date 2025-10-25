import React from "react";
import AgentEventsPage from "./components/AgentEventsPage";

const App: React.FC = () => {
  return (
    <div style={{ fontFamily: "Inter, sans-serif", background: "#f9fafb", minHeight: "100vh" }}>
      <header
        style={{
          padding: "1.5rem 2rem",
          background: "linear-gradient(90deg, #3b82f6, #2563eb)",
          color: "white",
          fontSize: "1.5rem",
          fontWeight: 600,
        }}
      >
        ⚡ Live Agent Event Dashboard
      </header>
      <main style={{ padding: "2rem" }}>
        <AgentEventsPage />
      </main>
    </div>
  );
};

export default App;
