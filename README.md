# Fetch.ai Supply Chain Simulation — Project Plan

## Overview
Build a simulated **manufacturing digital twin** that combines a frontend production simulator with backend **Fetch.ai agents** (Warehouse → Buyer → Negotiation → Supplier → Logistics → Tracking → Finance).

---

## Deliverables
- WarehouseAgent (detects low stock → sends PurchaseRequest)
- Buyer, Negotiation, Supplier agents (negotiate and confirm orders)
- Logistics, Tracking, Finance agents (basic workflows)
- Backend Coordinator (REST + WebSocket bridge)
- React frontend (production simulator + dashboard)
- Dev tooling: Docker, CI, seeded DB, k8s manifests
- Deployment: agents on Agentverse or k8s
- Documentation & demo

---

## MVP
- Frontend simulates production that consumes inventory
- WarehouseAgent detects low stock and triggers BuyerAgent
- BuyerAgent requests quotes; SupplierAgents respond
- NegotiationAgent picks one; Warehouse updated and UI reflects it

---

## Phases

### Phase 0 — Prerequisites & Planning
- Create Git repo
- Create Agentverse, Docker Hub, k8s accounts
- Install: Python 3.11+, Node 18+, Docker, kubectl, PostgreSQL/SQLite
- Deliverable: repo scaffold & toolchain ready

### Phase 1 — Repo Scaffolding & Shared Components
- Folder structure under `/backend`, `/frontend`, `/docker`, `/k8s`
- Shared message models using `uagents.Model`
- Dependencies in `requirements.txt`
- Acceptance: successful install and importable shared models

### Phase 2 — DB Schema & Synthetic Data
- Tables: `inventory`, `purchase_orders`, `shipments`, `suppliers`
- Scripts: `seed_inventory.py`
- Acceptance: database seeded with sample data

### Phase 3 — WarehouseAgent
- Monitors DB every 30–60s
- Sends `PurchaseRequest` to BuyerAgent when stock low
- Acceptance: agent detects low stock and triggers request

### Phase 4 — BuyerAgent + Negotiation + SupplierAgents
- BuyerAgent receives `PurchaseRequest` and forwards RFQ
- NegotiationAgent collects and evaluates quotes
- SupplierAgents respond with `QuoteResponse`
- Acceptance: order created and supplier selected

### Phase 5 — Coordinator Service
- FastAPI REST + WebSocket bridge
- APIs: `/inventory`, `/trigger_purchase`, `/ws/events`
- Logs agent messages & exposes data to UI
- Acceptance: UI can connect & see live events

### Phase 6 — Frontend Simulator & Dashboard
- React + TypeScript + Tailwind
- Panels: ProductionControl, InventoryDashboard, AgentMap, Timeline
- WebSocket feed for real-time updates
- Acceptance: simulate production and view full chain visually

### Phase 7 — Logistics, Tracking, Finance Agents
- LogisticsAgent: creates shipments
- TrackingAgent: simulates delivery updates
- FinanceAgent: marks POs paid after delivery
- Acceptance: delivery → payment workflow complete

### Phase 8 — LLM Integration (optional)
- Add reasoning for negotiation or explanation
- Always validate LLM output before execution

### Phase 9 — Containerization & Deployment
- Dockerize each agent and Coordinator
- Compose file for local run, k8s manifests for production
- Deploy to Agentverse or cluster
- Acceptance: `docker-compose up` runs entire system

### Phase 10 — Monitoring, Logging, CI/CD
- Add Prometheus + Grafana for metrics
- GitHub Actions for lint/test/build/deploy
- Health endpoints per agent

### Phase 11 — Security & Governance
- Store secrets securely (k8s secrets / Vault)
- Input validation and audit logging

### Phase 12 — Demo & Documentation
- README, architecture diagrams, API docs, runbook
- Demo script for production → negotiation → restock
- Recorded walkthrough

---

## Sprint Plan (approx. 2 weeks each)
| Sprint | Focus |
|---------|--------|
| 0 | Setup & DB seed |
| 1 | Warehouse + Buyer + Supplier skeletons |
| 2 | Negotiation + Coordinator |
| 3 | Frontend MVP |
| 4 | Logistics + Tracking + Finance + LLM |
| 5 | Containerization + CI/CD + docs |

---

## Acceptance Criteria
- WarehouseAgent triggers PurchaseRequest correctly
- Negotiation selects optimal supplier
- Frontend shows live event chain
- End-to-end restock workflow works via `docker-compose up`

---

## Tech Stack
- Agents: Python 3.11 + uAgents
- API: FastAPI
- DB: SQLite/PostgreSQL
- Frontend: React + TypeScript + Tailwind
- Container: Docker + Kubernetes
- Monitoring: Prometheus + Grafana
- CI: GitHub Actions

---

## Next Steps
1. Create repo structure
2. Add shared models and DB helpers
3. Seed inventory DB
4. Implement WarehouseAgent (monitor & trigger)
5. Test manually, then proceed to BuyerAgent







[WarehouseAgent] detects low inventory (auto trigger)
        │
        ▼
[BuyerAgent] creates purchase request → sends to NegotiationAgent
        │
        ▼
[NegotiationAgent] requests quotes from multiple SupplierAgents
        │
        ▼
[SupplierAgents] respond with QuoteResponse messages
        │
        ▼
[NegotiationAgent] compares bids (with LLM or logic)
        │
        ▼
[BuyerAgent] confirms best offer and instructs LogisticsAgent
        │
        ▼
[LogisticsAgent] creates shipment and updates TrackingAgent
        │
        ▼
[TrackingAgent] sends shipment status updates → WarehouseAgent
        │
        ▼
[WarehouseAgent] confirms receipt
        │
        ▼
[FinanceAgent] validates and releases payment
        │
        ▼
[UI/Dashboard] updates live event feed and status visualization
