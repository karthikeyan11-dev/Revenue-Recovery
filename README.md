# AI Revenue Recovery Orchestrator

[![CI](https://github.com/your-username/revenue-recovery/actions/workflows/ci.yml/badge.svg)](https://github.com/your-username/revenue-recovery/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![React + Vite](https://img.shields.io/badge/frontend-React%20%2B%20Vite-61dafb.svg)](https://vitejs.dev/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)

> **Razorpay AI Buildathon — Track 03: AI Revenue Recovery**

## 1. One-Line Definition

An autonomous, policy-governed AI system that detects revenue at risk from failed payments and abandoned checkouts, understands customer and payment context, selects and executes a bounded recovery strategy, and measures actual recovered revenue against a naive baseline.

> **Key Architectural Principle:** The LLM proposes decisions. A deterministic policy engine and executor control what the system is actually allowed to do. The LLM is a reasoning layer, not an authority.

---

## 2. System Architecture

```
                    ┌──────────────────┐
                    │   React + Vite   │
                    │  Tailwind/Recharts│
                    └────────┬─────────┘
                             │ REST API
                             ↓
                    ┌──────────────────┐
                    │   FastAPI App    │
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
                       Policy Engine (Deterministic Guard)
                    ┌────────┴────────┐
                    ↓                 ↓
                 APPROVE            BLOCK/ESCALATE
                    ↓                 ↓
                 Executor        Human Review Queue
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

---

## 3. Key Capabilities & Verified Features

- **Empirical Baseline vs AI Benchmark:** Live snapshot database persistence calculates exact ₹ recovered, recovery rates, and net ROI across customer cohorts without hardcoded numbers.
- **Compiled LangGraph Multi-Agent Pipeline:** StateGraph manages state flow across `Revenue Detective` $\to$ `Customer Intelligence` $\to$ `Recovery Strategist` $\to$ `Policy Engine` $\to$ `Action Executor`.
- **Hybrid AI Reasoning with Graceful Fallback:** Real Anthropic Claude LLM API calls generate natural-language rationale with automated contextual fallback when API credits are low.
- **Strict Deterministic Policy Engine:** Hard rules cap retry attempts ($\le 3$), enforce discount limits ($\le 10\%$), and route high-value at-risk payments ($\ge ₹25,000$) to human escalation.
- **Real-Time Interactive Frontend:**
  - **Dashboard:** One-click simulation triggers, 4 KPI cards, and Recharts segment comparisons.
  - **Recovery Cases:** Searchable cases table with interactive slide-over drawer showing full 5-stage audit timelines.
  - **Agent Activity:** Auto-refreshing 3-second live audit feed highlighting policy rejections and LLM reasoning.

---

## 4. Quick Start

### Option A: Run with Docker Compose (Recommended)

1. Start services:
   ```bash
   docker compose up -d --build
   ```

2. Open services:
   - **Frontend UI:** [http://localhost:5173](http://localhost:5173) (or [http://localhost:3000](http://localhost:3000))
   - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Local Development

1. **Backend Setup:**
   ```bash
   cd backend
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 5. Live Demo Guide

For a step-by-step 5-minute presentation script covering data generation, baseline comparison, AI recovery uplift, and policy engine demonstrations, refer to [docs/demo-script.md](docs/demo-script.md).

---

## 6. Verification & Test Suite

Run the full backend test suite and verification traces:
```bash
# Run full unit & integration tests
cd backend && venv/bin/pytest -v

# Run verification traces
venv/bin/python ../scratch/verify_phase1.py   # Baseline & Metrics Verification
venv/bin/python ../scratch/verify_phase2.py   # LangGraph StateGraph Execution Trace
venv/bin/python ../scratch/verify_phase3.py   # Hybrid LLM Reasoning & Fallback Trace
```
