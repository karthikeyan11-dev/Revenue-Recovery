# AI Revenue Recovery Orchestrator

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![Docker Compose](https://img.shields.io/badge/docker-compose-2496ed.svg)](https://www.docker.com/)

> **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**  
> An autonomous, policy-governed AI orchestration engine that identifies failed payments and checkout drop-offs, synthesizes payment-native customer signals, executes bounded multi-rail recovery, and benchmarks recovered revenue against a naive baseline in real time.

---

## 1. Architectural Philosophy

> **Core Principle:** The LLM proposes decisions; deterministic policy engines and execution guardrails decide what the system is permitted to do. The LLM functions as a reasoning and natural-language synthesis layer, never an unchecked authority.

```
AI Reasoning (LLM)  ──▶  Deterministic Policy Guardrail  ──▶  Bounded Execution
(Adaptive Strategy)          (Max Retries, Cap, Whales)       (Smart Retry / WhatsApp)
```

---

## 2. System Architecture

![System Architecture](docs/architecture.png)

### The 5-Stage Orchestration Pipeline (Compiled LangGraph)

1. **Revenue Detective**: Analyzes failed payment telemetry (error codes, failure step, payment method) and computes a baseline recoverability score.
2. **Customer Intelligence**: Synthesizes payment-native behavioral context:
   - **Payer Reliability Score** (historical payment success ratio)
   - **Timing Context** (business hours vs night-time drop-offs)
   - **Alternate Rail Availability** (saved UPI VPA, cards, or Netbanking)
   - **Verified Communication Channels** (WhatsApp, SMS, Email)
3. **Recovery Strategist**: Retrieves similar recovery precedent records from vector memory (**ChromaDB permanent store**) via RAG and formulates an optimal intervention (Smart Retry, 1-Click WhatsApp payment link, or split-pay incentive).
4. **Deterministic Policy Engine**: Enforces hard, un-bypassable rules:
   - Cap retries at $\le 3$ attempts.
   - Restrict discounts/incentives to $\le 10\%$.
   - Route high-value "whale" transactions ($\ge ₹25,000$ for low-reliability payers) to the **Human Escalation Queue** to protect merchants from chargeback fines.
   - Block ungrounded strategies via `INSUFFICIENT_PRECEDENT_GATE`.
5. **Action Executor & Promise-to-Pay Tracker**: Dispatches smart retries or interactive WhatsApp payment links. Bounded state tracker monitors customer commitments with strict stopping rules preventing infinite contact loops.
6. **Recovery Analyst**: Calculates net financial yield and writes verified recovery outcomes back to ChromaDB vector memory for continuous precedent learning.

---

## 3. Real Razorpay Test API Integration vs. Batch Simulation

To deliver an authentic demonstration while supporting bulk statistical benchmarks, the system operates in two complementary modes:

| Dimension | Live Razorpay Test Mode (Tier 1 & Tier 2) | Calibrated Batch Simulation Engine |
| :--- | :--- | :--- |
| **Order Creation** | Genuine `POST /v1/orders` API calls creating live `order_...` records in Razorpay Dashboard. | Realistic synthetic batches calibrated to Indian payment failure rates. |
| **Checkout & Webhooks** | Real test checkout (`success@razorpay`, `failure@razorpay`) with cryptographically verified (`HMAC-SHA256`) webhook receiver at `POST /webhooks/razorpay`. | In-memory simulated payment triggers for instant baseline vs AI comparison. |
| **Error Forensics** | Authentic Razorpay fields (`error_code`, `error_source`, `error_step`, `error_reason`). | Normalized error taxonomy across 7 standard failure categories. |
| **Target Use Case** | Demonstrating live gateway interoperability and webhook ingestion. | Benchmarking 100+ transaction cohorts with statistical rigor. |

---

## 4. Frontend Application Structure

The user interface consists of three focused views:

1. **Executive Dashboard (`/`)**:
   - **8 Separated KPI Cards**: Financial metrics (AI Gross Recovered, Baseline Recovered, Recovery Rate, Net ROI) and Case Resolution metrics (AI Cases Rescued, Baseline Cases Rescued, Case Win Rate, Net Case Uplift) with explicit difference badges.
   - **Category Breakdown Chart**: Visualizes At-Risk, Baseline, and AI recovery across 7 failure reasons. Clearly distinguishes automated recoveries from revenue safely held in the Human Escalation Queue.
   - **Floating Diagnostic Intelligence Panel**: Draggable, interactive widget that alerts upon run completion and opens a live LLM-generated forensic diagnosis citing exact database numbers with honest model attribution.
2. **Recovery Cases (`/cases`)**:
   - Searchable, filterable ledger of every failure case.
   - Visual indicators for Precedent Sufficiency, Promise-to-Pay status, and Policy decisions.
   - Slide-over drawer detailing the complete 5-stage agent audit trace for any transaction.
3. **Agent Activity Feed (`/activity`)**:
   - Live-refreshing telemetry stream showing agent execution steps.
   - Dual confidence gauges displaying both empirical statistical confidence (Laplace smoothing over past trials) and LLM self-stated confidence.

---

## 5. Step-by-Step Judge Run Guide

Follow these numbered steps to run and verify the system locally:

### Step 1: Clone Repository
```bash
git clone https://github.com/your-username/Revenue-Recovery.git
cd Revenue-Recovery
```

### Step 2: Configure Environment Variables
Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```

Review `backend/.env`. Key configurations:
- **`OPENROUTER_API_KEY`** *(Recommended)*: Powers live LLM reasoning for the Forensic Diagnostic Panel.
- **`RAZORPAY_KEY_ID` & `RAZORPAY_KEY_SECRET`** *(Optional)*: If provided, live test orders will be created via Razorpay API. If omitted, the system falls back to realistic synthetic identifiers.
- **`DATABASE_URL`**: Defaults to PostgreSQL `postgresql://recovery_user:recovery_pass@localhost:5432/revenue_recovery`.

### Step 3: Launch with Docker Compose
```bash
docker compose up -d --build
```
*Wait ~20 seconds for PostgreSQL and migrations to complete.*

Open your browser:
- **Frontend Dashboard:** [http://localhost:3000](http://localhost:3000) (or [http://localhost:5173](http://localhost:5173))
- **Interactive Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

*(Alternatively, run locally: `uvicorn app.main:app --reload --port 8000` in `backend` and `pnpm dev` in `frontend`.)*

### Step 4: Execute the Benchmark Flow
1. Navigate to the **Dashboard** in your browser.
2. Click **`1. Generate Data`**: Seeds 100 transactions with calibrated Indian e-commerce failure distributions.
3. Click **`2. Run Baseline`**: Executes the naive rule-based single-retry benchmark.
4. Click **`3. Run AI Orchestrator`**: Dispatches the multi-agent pipeline with RAG retrieval, policy validation, and adaptive channels.

### Step 5: Where to Look & How to Verify
- **Inspect KPIs**: Check the 8 KPI cards. Observe the exact differences in Gross Revenue and Customer Accounts Saved.
- **Open Forensic Diagnostic Panel**: Click the floating circular intelligence icon at the bottom right. Review the live LLM synthesis explaining why the AI won or why high-value cases were routed to human review.
- **Verify Live LLM Attribution**: Notice the transparent model attribution tag (e.g. `minimax/minimax-m3:free via OpenRouter`). Click **Regenerate** to observe fresh live reasoning generated with streaming latency.
- **Inspect Audit Timeline**: Navigate to **Recovery Cases** and click on any case row to inspect the full LangGraph state transition.
- **Verify Numbers are Real**: Re-run the simulation (click Generate $\to$ Run Baseline $\to$ Run AI). All metrics, percentages, and case counts will recompute dynamically based on live database state.

---

## 6. Known Limitations

In the spirit of technical honesty, here are known boundaries of the current implementation:

1. **Payment Gateway Scope**: Razorpay Test API integration is active for order creation (`/v1/orders`) and webhook verification (`/webhooks/razorpay`). Live bank settlement and card capture simulation rely on Razorpay test mode VPAs and calibrated simulators.
2. **WhatsApp Channel Execution**: Customer WhatsApp interactions are simulated via a calibrated response engine modeled after Indian UPI intent conversion rates (72% with incentive, 55% standard) rather than a live Meta Business API account.
3. **Escalated Case Settlement**: Transactions held in the Human Escalation Queue are accounted as ₹0.00 automated recovery until manually resolved by support operators in the dashboard.
4. **LLM Provider Availability**: When external LLM APIs experience upstream rate limits, the diagnostic panel cleanly falls back to verified PostgreSQL telemetry rather than fabricating mock reasoning.

---

## 7. Verification & Test Suite

Run the full automated verification test suite:

```bash
# Run pytest backend suite
cd backend && ./venv/bin/pytest -v

# Verify Razorpay Tier 2 Webhook HMAC Verification
./venv/bin/python scripts/razorpay_checkout_flow.py

# Verify Promise-to-Pay Tracker Stopping Rules
./venv/bin/python scripts/trace_promise_tracker.py

# Build frontend production bundle
cd ../frontend && pnpm build
```
