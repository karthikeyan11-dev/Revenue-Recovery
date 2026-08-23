# AI Revenue Recovery Orchestrator — Live Demo Script (5 Minutes)

> **Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery
> **Core Principle:** *"The LLM proposes decisions. A deterministic Policy Engine decides."*

---

## 🎬 0:00 - 0:45 | Introduction & Problem Framing

- **What is this?**
  An autonomous, policy-governed multi-agent revenue recovery system that detects revenue at risk, evaluates customer & failure telemetry, bounds recovery strategies via hard business guardrails, and **empirically proves how much additional ₹ is recovered over a naive baseline**.

- **The Problem:**
  Traditional dunning blindly retries every failed payment on a static schedule or sends generic spam. This causes:
  1. High payment gateway retry fees on unrecoverable hard declines.
  2. Severe customer churn for Tier-1 customers harassed with generic emails.
  3. Margin leakage when excessive discounts are offered blindly.

- **Our Solution:**
  A 5-stage compiled **LangGraph** architecture with a strict **Deterministic Policy Engine** that guarantees zero unconstrained LLM actions.

---

## 🚀 0:45 - 1:45 | Generating Data & Running the Baseline Benchmark

1. Open the **Dashboard** (`http://localhost:5173`).
2. Click **"1. Generate Data"**:
   - Seeds 500+ synthetic transactions with realistic payment failures across 6 customer cohorts (`HIGH_VALUE`, `LOYAL`, `REGULAR`, `AT_RISK`, `CHURNING`, `LOW_VALUE`).
3. Click **"2. Run Baseline"**:
   - Executes the naive retry-once benchmark.
   - Point to the KPI card: *“Notice our baseline recovers ~45–55% of revenue blindly with high failure rates on card expirations.”*

---

## ⚡ 1:45 - 3:00 | Executing the AI Multi-Agent Orchestrator

1. Click **"3. Run AI Orchestrator"**:
   - Watch the state execute node-by-node across the compiled LangGraph graph:
     $$\text{Revenue Detective} \to \text{Customer Intelligence} \to \text{Recovery Strategist} \to \text{Policy Engine} \to \text{Action Executor}$$
2. Examine the live Dashboard updates:
   - **AI Recovery Rate:** Jump to **68–78%** ($+15\text{--}25\%$ empirical uplift over baseline).
   - **Net ₹ Gain:** Shows the exact ₹ uplift and net ROI computed live from the database.
   - **Segment Breakdown Chart:** Point out how the AI strategically targets high-value customers with empathetic WhatsApp links and gives calibrated discounts only to at-risk cohorts while blocking low-value retries.

---

## 🛡️ 3:00 - 4:00 | Deep-Dive: Cases & Policy Engine Guardrails

1. Navigate to the **Recovery Cases** tab.
2. Filter by status: **Recovered**, **Blocked by Policy**, **Escalated**.
3. Click on a **Blocked Case**:
   - Show the Policy Engine intervention card:
     *“Strategist proposed a 15% discount, but our deterministic rule capped it strictly at 10% maximum discount. The policy engine overrode the proposal before execution.”*
4. Click on an **Escalated Case**:
   - Show how large transactions ($\ge ₹25,000$) on high-churn accounts are routed to Human Escalation rather than automated bot messaging.
5. Inspect the **Vertical Multi-Agent Audit Trail**:
   - Step 1: Revenue Detective identified the root cause.
   - Step 2: Customer Intelligence evaluated LTV and churn risk.
   - Step 3: Recovery Strategist formulated the action.
   - Step 4: Policy Engine validated compliance.
   - Step 5: Action Executor completed the simulation.

---

## 📡 4:00 - 5:00 | Live Agent Stream & Summary

1. Navigate to **Agent Activity**:
   - Show the auto-polling stream (3-second live updates).
   - Filter by agent chips: `Revenue Detective`, `Policy Engine`, etc.
   - Highlight the red/amber alert styling for policy rejections, demonstrating transparent AI accountability.
2. **Closing Takeaway:**
   *“We didn't just build an AI prompt that suggests what it could do — we built a stateful, policy-governed orchestrator backed by PostgreSQL, LangGraph, and deterministic safeguards that proves exact ROI for merchants.”*
