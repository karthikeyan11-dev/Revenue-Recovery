# AI Revenue Recovery Orchestrator — Live Demo Script (5 Minutes)

> **Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery
> **Core Principle:** *"The LLM proposes decisions. A deterministic Policy Engine decides. Empirical data proves the recovery."*

---

## 🎬 0:00 - 0:45 | Introduction & Architecture Overview

- **What is this?**
  An autonomous, policy-governed multi-agent revenue recovery system that detects revenue at risk, evaluates customer & failure telemetry, bounds recovery strategies via hard business guardrails, and **empirically proves how much additional ₹ is recovered over a naive baseline**.

- **The Problem:**
  Traditional dunning blindly retries every failed payment on a static schedule or sends generic spam. This causes:
  1. High payment gateway retry fees on unrecoverable hard declines.
  2. Severe customer churn for Tier-1 customers harassed with generic emails.
  3. Margin leakage when excessive discounts are offered blindly.

- **Our Solution:**
  A 5-stage compiled **LangGraph** architecture with a strict **Deterministic Policy Engine** that guarantees zero unconstrained LLM actions, backed by **ChromaDB RAG Precedent Playbook** and **Dual Empirical Confidence Tracking**.

```
  Razorpay Test API / Synthetic Telemetry
                     ↓
             Revenue Detective
                     ↓
           Customer Intelligence
                     ↓
            Recovery Strategist  ←→  ChromaDB RAG Playbook
                     ↓
         Deterministic Policy Engine
          ┌──────────┴──────────┐
          ↓                     ↓
       APPROVE            BLOCK / ESCALATE
          ↓                     ↓
    Action Executor       Human Review Queue
          ↓
   Promise-to-Pay Tracker (1-retry stopping rule)
          ↓
   Recovery Analyst  ──(Dynamic Write-Back)──→  ChromaDB Playbook
```

---

## 🚀 0:45 - 1:45 | Generating Data & Running the Baseline Benchmark

1. Open the **Dashboard** (`http://localhost:3000` or `http://localhost:5173`).
2. Click **"1. Generate Data"**:
   - Seeds 500+ synthetic transactions with realistic payment failures across 6 customer cohorts (`HIGH_VALUE`, `LOYAL`, `REGULAR`, `AT_RISK`, `CHURNING`, `LOW_VALUE`).
3. Click **"2. Run Baseline"**:
   - Executes the naive retry-once benchmark.
   - Point to the KPI card: *“Notice our baseline recovers ~45–55% of revenue blindly with high failure rates on card expirations and customer dropoffs.”*

---

## ⚡ 1:45 - 3:00 | Executing the AI Multi-Agent Orchestrator

1. Click **"3. Run AI Orchestrator"**:
   - Watch the state execute node-by-node across the compiled LangGraph graph:
     $$\text{Revenue Detective} \to \text{Customer Intelligence} \to \text{Recovery Strategist} \to \text{Policy Engine} \to \text{Action Executor} \to \text{Recovery Analyst}$$
2. Examine the live Dashboard updates:
   - **AI Recovery Rate:** Reaches **68–78%** ($+15\text{--}25\%$ empirical uplift over baseline).
   - **Net ₹ Gain:** Shows the exact ₹ uplift and net ROI computed live from database rows.
   - **Segment Breakdown Chart:** Point out how the AI strategically targets high-value customers with empathetic WhatsApp links and gives calibrated incentives only to at-risk cohorts while blocking low-value retries.

---

## 🛡️ 3:00 - 4:00 | Deep-Dive: Cases, Precedents & Promise-to-Pay

1. Navigate to the **Recovery Cases** tab.
2. Highlight the **Precedent Sufficiency Badge**:
   - Show cases with `Sufficient (n=5)` vs. novel failure modes with `Insufficient (n=0)` triggering the mandatory human escalation gate.
3. Highlight the **Promise-to-Pay Tracking**:
   - Click a case with active payment commitments (`Kept`, `Pending`, `Broken`).
   - Open the slide-over drawer: show the **Promise-to-Pay Commitment Tracking** section.
   - Explain the **Stopping Rule**: *“If a customer breaks a promise once, we send 1 follow-up retry. If they break it a second time, the system strictly halts automation and escalates to a human to prevent spam loops.”*
4. Click on a **Blocked Case**:
   - Show the Policy Engine intervention card:
     *“Strategist proposed a 15% discount, but our deterministic rule capped it strictly at 10% maximum discount. The policy engine overrode the proposal before execution.”*

---

## 📡 4:00 - 5:00 | Live Agent Activity Stream & Dual Confidence

1. Navigate to **Agent Activity**:
   - Show the auto-polling stream (3-second live updates).
   - Point to the side-by-side **Empirical Confidence** (computed via Laplace smoothing over historical cohort trials) and **LLM Stated Confidence**.
   - Show the `Retrieved Precedents (n=X)` badge on the Recovery Strategist entries.
2. **Real Razorpay Test Mode Verification**:
   - Show how live orders are created via `POST https://api.razorpay.com/v1/orders` (`order_...`).
   - Show how authentic webhooks (`POST /webhooks/razorpay`) acknowledge in under 50ms with FastAPI `BackgroundTasks`, executing full recovery in the background and closing active cases on `payment.captured`.
3. **Closing Takeaway:**
   *“We didn't just build a demo prompt that suggests what it could do — we built a stateful, policy-governed orchestrator backed by PostgreSQL, ChromaDB RAG, and deterministic safeguards that proves exact ROI for merchants.”*
