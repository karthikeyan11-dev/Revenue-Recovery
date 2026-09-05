# AI Revenue Recovery Orchestrator

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![React + Vite](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![Docker Compose](https://img.shields.io/badge/docker-compose-2496ed.svg)](https://www.docker.com/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-black.svg?logo=github)](https://github.com/karthikeyan11-dev/Revenue-Recovery.git)

> **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**  
> An autonomous, policy-governed AI orchestration engine that identifies failed payments and checkout drop-offs, synthesizes payment-native customer signals, executes bounded multi-rail recovery, and benchmarks recovered revenue against a naive baseline in real time.  
> **Repository:** [https://github.com/karthikeyan11-dev/Revenue-Recovery.git](https://github.com/karthikeyan11-dev/Revenue-Recovery.git)

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

### The 6-Stage Orchestration Pipeline (Compiled LangGraph)

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
   - **Floating Diagnostic Intelligence Panel**: Draggable, interactive widget that alerts upon cohort run completion. When configured with an external LLM API key, it generates a live natural-language forensic diagnosis citing exact database numbers with transparent model attribution; in default mock mode or without an external key, it honestly displays verified PostgreSQL telemetry without fabricating ungrounded model output.
2. **Recovery Cases (`/cases`)**:
   - Searchable, filterable ledger of every failure case.
   - Visual indicators for Precedent Sufficiency, Promise-to-Pay status, and Policy decisions.
   - Slide-over drawer detailing the complete 6-stage agent audit trace for any transaction.
3. **Agent Activity Feed (`/activity`)**:
   - Live-refreshing telemetry stream showing agent execution steps.
   - Dual confidence gauges displaying both empirical statistical confidence (Laplace smoothing over past trials) and LLM self-stated confidence.

---

## 5. Step-by-Step Judge Run Guide

> [!IMPORTANT]
> ### ⚠️ Evaluation Disclaimer: Zero-Credential Default (`LLM_PROVIDER=mock`)
> For evaluating and reviewing this repository, **`LLM_PROVIDER=mock`** is the zero-credential default path configured in `backend/.env`.
>
> **Why `mock` is the recommended default setup for hackathon evaluation:**
> 1. **Zero External API Dependency & Zero Rate Limits**: External LLM providers (OpenRouter, Gemini, OpenAI, Anthropic) are subject to upstream API quota limits, HTTP 429 rate-limiting, and network latency during concurrent evaluations. Mock mode guarantees 100% reliable, zero-latency execution out-of-the-box without requiring judges to register, acquire, or fund private API keys.
> 2. **Focus on Deterministic Architecture & Math**: The core innovation of RevRecovery lies in its **compiled LangGraph state machine, deterministic Policy Engine boundaries (max 3 retries, 10% incentive cap, ₹25k escalation gate), Bayesian Laplace reliability smoothing (`(successful + 2) / (total + 4)`), and dense ChromaDB vector RAG retrieval**. The mock provider executes deterministically in seconds.
> 3. **Diagnostic Panel Fallback vs. Real LLM Inspection**: In default mock mode (without external API credentials), the Forensic Diagnostic Panel honestly displays its built-in fallback state (*"Live LLM reasoning temporarily unavailable. Telemetry below is computed directly from live PostgreSQL state"*) rather than pretending that mock data was produced by a real frontier model.
> 4. **Testing Real LLM Reasoning**: Judges who wish to inspect live frontier LLM reasoning and observe real model attribution tags (e.g., `minimax/minimax-m3:free (OpenRouter)`) can set `LLM_PROVIDER=openrouter` and supply their `OPENROUTER_API_KEY` in `backend/.env`.

Follow these numbered steps to run and verify the system locally:

### Step 1: Clone Repository
```bash
git clone https://github.com/karthikeyan11-dev/Revenue-Recovery.git
cd Revenue-Recovery
```

### Step 2: Configure Environment Variables
Copy the example environment file:
```bash
cp backend/.env.example backend/.env
```

Review `backend/.env`. Key configurations:
- **`LLM_PROVIDER=mock`** *(Default & Strongly Recommended)*: Zero-credential path for fast, deterministic evaluation of the multi-agent pipeline and 100-case simulation without external API rate-limit bottlenecks.
- **`OPENROUTER_API_KEY`** *(Optional)*: Required only if you want to inspect live frontier model reasoning and transparent model attribution in the Forensic Panel. If omitted or kept as mock, the application operates in zero-credential mode and displays verified database telemetry.
- **`RAZORPAY_KEY_ID` & `RAZORPAY_KEY_SECRET`** *(Optional)*: If provided, live test orders will be created via Razorpay API. If omitted, the system falls back to realistic synthetic identifiers.
- **`DATABASE_URL`**: Defaults to PostgreSQL `postgresql://postgres:postgres@localhost:5433/revenue_recovery`.


### Step 3: Launch Application

#### Method 1: Docker Compose (Standard Evaluation)
```bash
docker compose up -d --build
```
*Wait ~20 seconds for PostgreSQL and migrations to complete.*

Then access:
- **Frontend Dashboard (Docker):** [http://localhost:3000](http://localhost:3000)
- **Interactive Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

#### Method 2: Local Development (Without Docker)
1. Ensure PostgreSQL is running (default port `5433`).
2. Run backend:
   ```bash
   cd backend && ./venv/bin/uvicorn app.main:app --reload --port 8000
   ```
3. Run frontend development server:
   ```bash
   cd frontend && npm run dev
   ```
Then access:
- **Frontend Dashboard (Local Dev):** [http://localhost:5173](http://localhost:5173)
- **Interactive Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

### Step 4: Execute the Benchmark Flow
1. Navigate to the **Dashboard** in your browser.
2. Click **`1. Generate Data`**: Seeds 100 transactions with calibrated Indian e-commerce failure distributions.
3. Click **`2. Run Baseline`**: Executes the naive rule-based single-retry benchmark.
4. Click **`3. Run AI Orchestrator`**: Dispatches the multi-agent pipeline with RAG retrieval, policy validation, and adaptive channels.

### Step 5: Where to Look & How to Verify
- **Inspect KPIs**: Check the 8 KPI cards. Observe the exact differences in Gross Revenue and Customer Accounts Saved.
- **Open Forensic Diagnostic Panel**: Click the floating circular intelligence icon at the bottom right to review cohort recovery diagnostics and financial metrics computed directly from PostgreSQL.
- **Verify Diagnostic State & Model Attribution**:
  - *Default Mock Mode (Zero Credentials):* The panel honestly displays the verified telemetry fallback banner (*"Live LLM reasoning temporarily unavailable. Telemetry below is computed directly from live PostgreSQL state"*), confirming that the system does not fabricate artificial model attribution without real credentials.
  - *Real LLM Mode (with `OPENROUTER_API_KEY`):* The panel generates live natural-language synthesis and displays the verified model attribution tag (e.g., `minimax/minimax-m3:free (OpenRouter)`). Click **Regenerate** to observe live streaming generation.
- **Inspect Audit Timeline**: Navigate to **Recovery Cases** and click on any case row to inspect the full LangGraph state transition.
- **Verify Numbers are Real**: Re-run the simulation (click Generate $\to$ Run Baseline $\to$ Run AI). All metrics, percentages, and case counts will recompute dynamically based on live database state.

---

## 6. Known Limitations

In the spirit of technical honesty, here are known boundaries of the current implementation:

1. **Payment Gateway Scope**: Razorpay Test API integration is active for order creation (`/v1/orders`) and webhook verification (`/webhooks/razorpay`). Live bank settlement and card capture simulation rely on Razorpay test mode VPAs and calibrated simulators.
2. **WhatsApp Channel Execution**: Customer WhatsApp interactions are simulated via a calibrated response engine modeled after Indian UPI intent conversion rates (72% with incentive, 55% standard) rather than a live Meta Business API account.
3. **Escalated Case Settlement**: Transactions held in the Human Escalation Queue are accounted as ₹0.00 automated recovery until manually resolved by support operators in the dashboard.
4. **LLM Provider & Diagnostic Panel Mode**: Mock mode is the default zero-credential path. Without an active `OPENROUTER_API_KEY`, or when external APIs experience upstream rate limits, the diagnostic panel cleanly displays the verified PostgreSQL telemetry fallback state rather than fabricating ungrounded reasoning or claiming that a real model was called.

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
cd ../frontend && npm run build
```
