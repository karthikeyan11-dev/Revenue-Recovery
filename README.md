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

For complete specification, detailed data schema, and development roadmap, see [projectplan.md](projectplan.md).

---

## 2. System Architecture

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

---

## 3. Tech Stack

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy, Alembic, PostgreSQL, LangGraph, Pydantic v2, Anthropic API
- **Frontend:** React 18, TypeScript, Vite, Tailwind CSS, Recharts, TanStack Query
- **Testing & Quality:** Pytest, HTTPX, Ruff, Black, ESLint, Prettier, GitHub Actions CI
- **DevOps:** Docker, Docker Compose

---

## 4. Quick Start

### Prerequisites
- Docker & Docker Compose **OR** Python 3.11+ and Node.js 20+
- Anthropic API key (for agent reasoning features)

### Option A: Run with Docker Compose (Recommended)

1. Clone repository and copy environment configuration:
   ```bash
   cp .env.example .env
   # Edit .env and supply your ANTHROPIC_API_KEY
   ```

2. Start the full stack (PostgreSQL + Backend + Frontend):
   ```bash
   make up
   # or: docker compose up --build
   ```

3. Open services:
   - **Frontend UI:** [http://localhost:5173](http://localhost:5173) (or [http://localhost:3000](http://localhost:3000))
   - **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
   - **Health Endpoint:** [http://localhost:8000/health](http://localhost:8000/health)

### Option B: Local Development (Without Docker)

1. **Backend setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload --port 8000
   ```

2. **Frontend setup:**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 5. Developer Commands

The project includes a root `Makefile` for streamlined development:

| Command | Description |
|---|---|
| `make up` | Start all services via Docker Compose |
| `make down` | Stop and tear down Docker Compose services |
| `make dev` | Run backend & frontend locally |
| `make test` | Run backend unit & integration tests (`pytest`) |
| `make lint` | Lint backend (`ruff`) and frontend (`eslint`) |
| `make format` | Auto-format backend (`black`, `ruff`) and frontend (`prettier`) |
| `make seed` | Generate synthetic dataset for recovery simulations |
| `make build` | Build production artifacts for backend & frontend |
