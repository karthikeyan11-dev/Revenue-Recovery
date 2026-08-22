# AI Revenue Recovery Orchestrator — Project Plan

**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery
**Builder:** Karthi (solo)
**Deadline:** September 5, 2026
**Timeline:** 14 days

## 1. One-line definition

An autonomous, policy-governed AI system that detects revenue at risk from failed payments and abandoned checkouts, understands customer and payment context, selects and executes a bounded recovery strategy, and measures actual recovered revenue against a naive baseline.

**Key architectural principle:** The LLM proposes decisions. A deterministic policy engine and executor control what the system is actually allowed to do. The LLM is a reasoning layer, not an authority.

**Success metric the judges care about:** How much ₹ revenue did the system actually recover — not how many AI decisions were made.

## 2. Scope decisions (read this before building)

This plan is a solo-buildable version of a much larger production architecture. Decisions made to fit 14 days:

| Full production version | This build |
|---|---|
| 5 separate microservices | 1 FastAPI monolith with internal modules/LangGraph nodes |
| Node.js BFF + separate frontend | FastAPI serves API directly, React frontend calls it |
| PostgreSQL + Redis | PostgreSQL only (SQLite acceptable for local dev) |
| 10,000+ customers / 50,000+ transactions | 500–1,000 transactions across 5–6 segments |
| 6 frontend screens | 3 frontend screens (Dashboard, Cases, Agent Activity) |

**Do NOT cut:** the policy engine as a real enforced gate, the audit trail, and the baseline-vs-AI comparison. These are the differentiators.

**Non-negotiable rule:** Never fabricate or hardcode recovery numbers. Every ₹ figure shown must come from an actual simulation run.

## 3. Tech stack

**Backend**
- Python 3.11+
- FastAPI (API + agent orchestration host)
- LangGraph (agent state machines — Detective, Intelligence, Strategist, Analyst)
- Pydantic (structured LLM outputs, validated before anything touches the policy engine)
- SQLAlchemy + PostgreSQL (SQLite locally is fine if Postgres setup is friction)
- Anthropic API (or OpenAI, behind a thin provider abstraction) for LLM reasoning calls

**Frontend**
- React + TypeScript + Vite
- Tailwind CSS
- Recharts (baseline-vs-AI comparison chart, recovery-over-time chart)
- TanStack Query (data fetching/polling for "live" agent activity)

**Dev/infra**
- Docker + docker-compose (optional but nice for the demo — one command to run everything)
- GitHub public repo
- `.env` for API keys, never committed

**Explicitly NOT used:** Redis, a separate Node.js service, microservice-per-agent deployment, Kubernetes, message brokers (Kafka/RabbitMQ). All of these add setup risk without adding to what a judge can see in a 5-minute pitch video.

## 4. Folder structure

```
revenue-recovery/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entrypoint
│   │   ├── config.py                # env vars, LLM provider config
│   │   ├── db.py                    # SQLAlchemy engine/session
│   │   │
│   │   ├── models/                  # SQLAlchemy models
│   │   │   ├── customer.py
│   │   │   ├── transaction.py
│   │   │   ├── payment_failure.py
│   │   │   ├── revenue_leak.py
│   │   │   ├── recovery_case.py
│   │   │   ├── recovery_action.py
│   │   │   ├── communication_event.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/                 # Pydantic request/response + structured LLM outputs
│   │   │   ├── detective.py
│   │   │   ├── customer_intel.py
│   │   │   ├── strategist.py
│   │   │   └── analyst.py
│   │   │
│   │   ├── agents/                  # LangGraph agent logic
│   │   │   ├── revenue_detective.py
│   │   │   ├── customer_intelligence.py
│   │   │   ├── recovery_strategist.py
│   │   │   ├── recovery_analyst.py
│   │   │   └── graph.py             # wires agents into one LangGraph workflow
│   │   │
│   │   ├── policy/
│   │   │   ├── engine.py            # deterministic approve/reject/escalate logic
│   │   │   └── rules.py             # MAX_RETRY_ATTEMPTS, MAX_INCENTIVE_PERCENT, etc.
│   │   │
│   │   ├── executor/
│   │   │   ├── executor.py          # takes APPROVED action, dispatches to a simulator
│   │   │   ├── payment_simulator.py
│   │   │   ├── whatsapp_simulator.py
│   │   │   ├── email_simulator.py
│   │   │   └── incentive_service.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── metrics.py           # recovery rate, ROI, per-action performance
│   │   │   └── baseline.py          # naive retry-once baseline for comparison
│   │   │
│   │   ├── data/
│   │   │   └── synthetic_generator.py  # generates customers/transactions/failures
│   │   │
│   │   └── api/
│   │       ├── routes_cases.py
│   │       ├── routes_dashboard.py
│   │       ├── routes_agents.py     # live agent activity feed
│   │       └── routes_run.py        # trigger a full batch run (baseline + AI)
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx        # headline numbers + baseline-vs-AI chart
│   │   │   ├── RecoveryCases.tsx    # cases table
│   │   │   └── AgentActivity.tsx    # live audit timeline
│   │   ├── components/
│   │   ├── api/                     # fetch wrappers to backend
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
│
├── data/
│   └── synthetic/                   # generated CSV/JSON snapshots, checked in for reproducibility
│
├── docs/
│   ├── architecture.png             # export from the diagram in section 8
│   └── demo-script.md               # your 5-minute pitch walkthrough, written in advance
│
├── docker-compose.yml
├── .env.example
└── README.md
```

## 5. Database schema (core tables)

- `customers` — id, segment (HIGH_VALUE/REGULAR/LOW_VALUE/LOYAL/AT_RISK/CHURNING/NEW), ltv, preferred_channel
- `transactions` — id, customer_id, amount, currency, status, created_at
- `payment_failures` — id, transaction_id, failure_reason (BANK_DECLINED/INSUFFICIENT_FUNDS/EXPIRED_CARD/NETWORK_ERROR/etc), attempt_number
- `revenue_leaks` — id, failure_id, type, amount, confidence, recoverability_score
- `recovery_cases` — id, leak_id, customer_id, status (OPEN/IN_PROGRESS/RECOVERED/FAILED/ESCALATED)
- `recovery_actions` — id, case_id, proposed_action, policy_decision (APPROVED/REJECTED/ESCALATED), executed_action, outcome
- `communication_events` — id, case_id, channel, simulated_response (IGNORED/OPENED/CLICKED/PAID/DECLINED)
- `audit_logs` — id, case_id, agent, input_summary, output_summary, decision, confidence, timestamp
- `recovery_metrics` — snapshot table for computed recovery rate / ROI per run (baseline vs AI)

## 6. Agents (LangGraph nodes)

| Agent | Input | Output | Notes |
|---|---|---|---|
| **Revenue Detective** | payment events, failures | leak type, amount, confidence, recoverability_score | Rules/SQL first, LLM adds reasoning/confidence — not LLM-only detection |
| **Customer Intelligence** | customer history | failure_reason, recovery_probability, churn_probability, preferred_channel | Builds a per-customer recovery profile |
| **Recovery Strategist** | leak + customer profile | proposed_action (RETRY / SEND_WHATSAPP / SEND_EMAIL / OFFER_INCENTIVE / SEND_PAYMENT_LINK / WAIT / ESCALATE_TO_HUMAN) | Structured Pydantic output only, no free-text actions |
| **Policy Engine** | proposed_action | APPROVED / REJECTED / ESCALATED | Deterministic — no LLM call. Enforces MAX_RETRY_ATTEMPTS=3, MAX_INCENTIVE_PERCENT=10, HIGH_VALUE_THRESHOLD=₹25,000, etc. |
| **Executor** | approved action | outcome | Pure dispatch to a simulator, no reasoning |
| **Recovery Analyst** | outcomes across a batch | recovery rate, ₹ recovered, ROI, per-action performance | Runs once against baseline results and once against AI results for comparison |

## 7. Feature checklist (in priority order)

**Must have (the demo doesn't work without these):**
- [ ] Synthetic data generator (500–1,000 transactions, 5–6 segments, 5–6 failure types)
- [ ] Payment simulator with controlled/reproducible probabilities
- [ ] Full LangGraph workflow: Detective → Intelligence → Strategist → Policy → Executor → Analyst
- [ ] Policy engine enforcing at least 3 real rules, visibly blocking/escalating at least one action in the demo
- [ ] Audit log for every agent decision, timestamped
- [ ] Baseline (simple retry-once) run against the same dataset
- [ ] AI-strategy run against the same dataset
- [ ] Recovery metrics: recovery rate, ₹ recovered, ROI — computed, not hardcoded
- [ ] Dashboard: 4 headline numbers + baseline-vs-AI chart
- [ ] Recovery cases table
- [ ] Agent activity / audit timeline view
- [ ] README with architecture diagram and one-line definition
- [ ] Public GitHub repo
- [ ] 5-minute pitch video

**Nice to have (add only if ahead of schedule):**
- [ ] WhatsApp/Email simulators with realistic response distributions
- [ ] Human approval queue UI for ESCALATED actions
- [ ] Customer 360 view
- [ ] Docker Compose one-command run
- [ ] Automated eval script (precision/recall on leak detection)

**Explicitly out of scope for this build:**
- Real Razorpay payment integration (test-mode APIs not required for this track — everything is simulated)
- Redis, message queues, Kubernetes
- Multi-tenant auth/RBAC
- 10,000+ record dataset

## 8. Architecture diagram

```
                    ┌──────────────────┐
                    │   React + Vite   │
                    │  Tailwind/Recharts│
                    └────────┬─────────┘
                             │ REST
                             ↓
                    ┌──────────────────┐
                    │   FastAPI app    │
                    │ (single service) │
                    └────────┬─────────┘
                             │
                             ↓
                       PostgreSQL
                             │
                        LangGraph
       ┌─────────────────────┼─────────────────────┐
       ↓                     ↓                     ↓
 Revenue Detective   Customer Intelligence   Recovery Strategist
       └─────────────────────┼─────────────────────┘
                             ↓
                       Policy Engine
                    ┌────────┴────────┐
                    ↓                 ↓
                 APPROVE            BLOCK/ESCALATE
                    ↓                 ↓
                 Executor        Human Queue (v2)
       ┌────────────┼────────────┐
       ↓            ↓            ↓
    Payment      WhatsApp      Email
   Simulator    Simulator    Simulator
       └────────────┼────────────┘
                    ↓
             Recovery Analyst
                    ↓
        Metrics (Recovery Rate, ROI)
                    ↓
        Baseline vs AI comparison
```

## 9. API endpoints (minimum set)

- `POST /data/generate` — generate synthetic dataset
- `POST /run/baseline` — run naive retry-once strategy against the dataset, store results
- `POST /run/ai` — run the full agent pipeline against the dataset, store results
- `GET /dashboard/summary` — headline numbers + baseline-vs-AI comparison
- `GET /cases` — recovery cases table data
- `GET /cases/{id}/timeline` — audit trail for one case
- `GET /agents/activity` — recent agent decisions (polled by the Agent Activity screen)

## 10. 14-day build roadmap

| Days | Focus |
|---|---|
| 1–2 | FastAPI + Postgres setup, domain models, synthetic data generator (500–1,000 transactions) |
| 3–4 | Payment simulator + ONE manually-wired recovery case (hardcoded logic, no LLM) to prove the data/event flow works |
| 5–6 | Revenue Detective + Customer Intelligence agents (LangGraph, structured outputs) |
| 7–8 | Recovery Strategist + Policy Engine (the core differentiator — do not rush) |
| 9 | Executor + payment/WhatsApp/email simulators, audit logging |
| 10 | Recovery Analyst, metrics, baseline-vs-AI comparison run |
| 11–12 | Frontend: Dashboard, Recovery Cases table, Agent Activity timeline |
| 13 | End-to-end bug fixing, README, architecture diagram, clean public repo |
| 14 | Record 5-minute pitch video, final checks, buffer before Sept 5 deadline |

**If behind schedule:** cut frontend polish (Days 11–12) before cutting the Policy Engine or the baseline comparison. Those two are what the judges are actually scoring.

## 11. Evaluation checklist (self-check before submitting)

- [ ] Every ₹ number in the demo comes from an actual run, not a hardcoded value
- [ ] At least one action was REJECTED or ESCALATED by the policy engine, and it's visible in the demo
- [ ] Baseline and AI results ran against the exact same dataset
- [ ] Audit trail for at least one full case is shown live
- [ ] Recovery rate, ₹ recovered, and ROI are all reported — not just "AI made N decisions"
- [ ] README states the one-line definition and the "LLM proposes, policy decides" principle clearly
- [ ] Repo is public and the pitch video is under 5 minutes

## 12. Environment setup (for the agent building this)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic langgraph anthropic python-dotenv
uvicorn app.main:app --reload

# Frontend
cd frontend
npm create vite@latest . -- --template react-ts
npm install tailwindcss recharts @tanstack/react-query
npm run dev
```

`.env` (backend) should contain:
```
DATABASE_URL=postgresql://user:pass@localhost:5432/revenue_recovery
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your_key_here
MODEL=claude-sonnet-4-6
```
