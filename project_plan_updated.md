# AI Revenue Recovery Agent — Project Documentation v2

**Track:** Razorpay AI Buildathon — Track 03: AI Revenue Recovery
**Builder:** Karthikeyan M (solo)
**Deadline:** September 5, 2026

## 1. What Razorpay actually asked for

Straight from the official track page — this is the real target, not an elaborated
version of it:

> *"Build an agent that detects revenue at risk, determines the right intervention,
> and executes a bounded recovery workflow: from payment failures and checkout
> abandonment to overdue receivables."*
>
> **The bar:** *"Don't just identify the problem. Show measured money recovered
> across a batch, with compliant escalation, stopping rules, and an audit trail."*

Everything in this document exists to satisfy that bar — nothing more. If a feature
doesn't serve "measured recovery," "compliant escalation," "stopping rules," or "audit
trail," it's cut. Judging (per public reporting on the track) weighs four things:
**Problem Taste, Build Quality, AI Judgment, Failure Recovery** — this doc is
structured so each is a visible, demoable part of the system, not a slide claim.

## 2. One-line definition

An agent that detects revenue at risk from failed payments and abandoned checkouts,
reasons about the right recovery intervention using real LLM judgment grounded in
retrieved past outcomes, executes that intervention within deterministic policy
guardrails, tracks whether recovery promises are actually kept, and reports measured
₹ recovered against a baseline — with a full audit trail at every step.

## 3. What's deliberately NOT in this build (and why)

Avoiding over-engineering is itself part of "AI Judgment" — every piece of
architecture needs to earn its place against the actual bar above.

| Cut | Why |
|---|---|
| Microservices per agent | One FastAPI process is easier to demo reliably and audit; Razorpay's bar doesn't ask for distributed systems |
| Redis / message queues | Postgres alone handles this dataset size; adds ops risk with no visible payoff in the demo |
| Separate Node.js BFF | One backend language reduces failure surface on demo day |
| 10,000+ record dataset | 500–1,000 records proves the same recovery-math story with far less generation/debugging time |
| Kubernetes / distributed deploy | Nobody is grading your DevOps maturity here — `docker-compose up` is enough |

## 4. Tech stack

- **Backend:** Python 3.11+, FastAPI, LangGraph (agent orchestration), Pydantic
  (structured LLM outputs), SQLAlchemy + PostgreSQL
- **AI:** LLM provider configured via `.env` (`LLM_PROVIDER` / `MODEL`) behind a thin
  provider abstraction — don't hardcode a single vendor
- **Razorpay Test Integration:** Razorpay Test Mode API/webhook integration for a small
  authentic "hero" subset of payment cases. Real test-mode order/payment events are used
  to validate the integration and capture authentic Razorpay payment/error vocabulary;
  the bulk evaluation dataset remains simulator-driven.
- **RAG / memory:** ChromaDB — stores embeddings of resolved recovery cases (segment,
  failure reason, action taken, channel, outcome) so the Strategist can retrieve real
  precedent instead of reasoning from nothing
- **Frontend:** React + TypeScript + Vite + Tailwind + Recharts + TanStack Query
- **Dev:** Docker Compose (Postgres + backend + frontend), GitHub Actions (lint + test
  on push)

No Redis, no Node BFF, no Kubernetes, no multi-service deploy.

## 5. Razorpay Test Mode + Hero Case Approach

The recovery engine is designed to be event-driven in its real integration path, while
retaining bulk simulation for buildathon evaluation. This does **not** replace the
existing workflow; it gives the workflow two valid entry points.

### 5.1 Real/Test-mode path

Use Razorpay Test Mode to create genuine test orders and exercise a small hero subset
of payment cases through the real test checkout/webhook path.

The intended flow is:

```
Razorpay Test Checkout
        |
        | payment failure
        v
Razorpay `payment.failed` webhook
        |
        v
FastAPI webhook endpoint
        |
        +--> validate + deduplicate event
        |
        v
PaymentFailure / RecoveryCase
        |
        v
Existing LangGraph recovery workflow
        |
        v
Detective -> Customer Intel -> Strategist -> Policy -> Executor -> Analyst
```

The webhook handler must remain lightweight: validate the event, prevent duplicate
processing, persist the failure/recovery case, acknowledge the webhook, and then trigger
the recovery workflow. The AI workflow must not be embedded as a long-running operation
inside the webhook request itself.

The Razorpay integration is primarily for **authenticity and demonstration**, not for
driving the entire 500–1,000 record evaluation through browser automation.

### 5.2 Hero subset

Drive approximately **50–100 hero cases** through Razorpay Test Mode when practical.
These cases provide:

- real Razorpay test `order_id` / payment identifiers;
- authentic test-mode payment outcomes;
- authentic Razorpay failure/error vocabulary;
- a demonstrable webhook-to-recovery path for the final pitch.

The exact hero count is a target, not a hard dependency. Reliability and the core AI
workflow take priority over browser automation volume.

### 5.3 Bulk evaluation path

Do **not** run browser-driven Razorpay checkout for all 500–1,000 records.

The bulk dataset continues to use the existing reproducible statistical simulator, but
its failure taxonomy and probabilities should be calibrated from the authentic Razorpay
test-mode observations collected from the hero subset.

Therefore the project has:

```
REAL/TEST MODE:
Razorpay -> webhook -> RecoveryCase -> same recovery workflow

BULK EVALUATION:
Calibrated synthetic cases -> same recovery workflow
```

Both paths converge on the **same domain models, LangGraph workflow, Policy Engine,
Executor, audit trail, and Recovery Analyst**. There must not be separate recovery
logic for real/test-mode and simulated cases.

### 5.4 Credentials and security

Razorpay Test Mode credentials are backend-only configuration:

```
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_MODE=test
```

Secrets must remain in `.env`, never in the frontend, generated SDK, Git history, or
README. `.env.example` contains placeholders only.

## 6. Agents

| # | Agent | What it actually does | Confidence source |
|---|---|---|---|
| 1 | **Revenue Detective** | Computes a `recoverability_score` from real statistical signal (failure-type base rates, attempt decay, customer LTV/segment). Sends that score + the raw case to the LLM, which classifies the leak type and explains its reasoning. | **Empirical, not LLM-stated**: a SQL aggregate over past resolved cases with the same failure_reason (+ segment where volume allows), smoothed for small samples (see section 8) |
| 2 | **Customer Intelligence** | Builds a profile from real transaction/payment history (churn signal, LTV, preferred channel), sent to the LLM for a grounded recovery-probability read and reasoning. | **Empirical**: SQL aggregate recovery rate over past customers in the same segment, smoothed the same way |
| 3 | **Recovery Strategist (RAG + tool-use)** | Before proposing an action, calls a retrieval tool that queries ChromaDB for the k most similar past resolved cases and their actual outcomes. The LLM proposes one action from a fixed enum (RETRY / SEND_WHATSAPP / SEND_EMAIL / OFFER_INCENTIVE / SEND_PAYMENT_LINK / WAIT / ESCALATE_TO_HUMAN), grounded in that retrieved evidence, with a reasoning narrative. | **Empirical**: the success rate among the retrieved similar cases, smoothed — NOT the LLM's self-reported number (see section 7 for why, and for the cold-start handling) |
| 4 | **Policy Engine** | Deterministic gate. Enforces `MAX_RETRY_ATTEMPTS`, `MAX_INCENTIVE_PERCENT`, `HIGH_VALUE_THRESHOLD`, communication-frequency limits, and the new insufficient-precedent rule (section 8). Approves, rejects, or escalates — the LLM never executes directly. | N/A — 100% deterministic, on purpose |
| 5 | **Executor** | Dispatches only policy-approved actions to the relevant simulator (payment retry, WhatsApp, email, incentive code). Does not reason. | N/A |
| 6 | **Promise-to-Pay Tracker** | When an action includes a payment commitment, creates a `promise_to_pay` record. Evaluates KEPT/BROKEN and routes broken promises back through the Strategist for one bounded follow-up. | N/A |
| 7 | **Recovery Analyst** | Computes recovery rate, ₹ recovered, ROI, and the baseline-vs-AI comparison from real run data. Writes the resolved case + outcome back into ChromaDB — this is what the Strategist's retrieval tool reads from. | N/A |

**What the LLM is actually for, in every agent:** classification, contextual
reasoning, natural-language explanation, and — for the Strategist — choosing between
several empirically-close options when the numbers alone don't clearly favor one.
**What the LLM is never used for:** producing the numeric confidence itself. That
number always comes from counting real outcomes, not from asking the model to
self-assess.

## 7. Confidence calibration & the RAG cold-start problem

This section exists because it's a real weakness in the naive version of this design,
and addressing it directly is a strong "AI Judgment" and "Failure Recovery" signal —
better to own it than have a judge find it.

**Why not just ask the LLM for a confidence number?** LLM-stated confidence is not
reliably calibrated — a model can say "92% confident" with equal fluency whether it's
right 90% of the time or 60% of the time. A number that gates real money decisions
should be a measured statistic, not a model's self-assessment.

**The empirical confidence formula** (used by Detective, Customer Intelligence, and
Strategist alike, on whatever population each one queries):

```
confidence = (successes + prior_successes) / (total_cases + prior_total)
```

This is simple Bayesian/Laplace smoothing — with a weak prior (e.g. `prior_successes
= 2, prior_total = 4`, i.e. an assumed 50% base rate worth 4 pseudo-cases) so that 1-2
retrieved cases don't produce a falsely extreme 0% or 100% confidence. As real
retrieved evidence accumulates, the prior's influence shrinks and the number reflects
genuine historical performance.

**Where do the "past cases" actually come from, honestly?** They are this system's
own simulated outcomes, written back by the Recovery Analyst after each case resolves
— not independent real-world history. Be upfront about this in the pitch if asked:
it's expected and correct for the bulk buildathon evaluation (the large dataset is
simulated by design), while the small Razorpay Test Mode hero subset provides authentic
test-mode integration evidence. It means two things need explicit handling rather than
being glossed over:

1. **Cold start.** At the very start of a run, there's no precedent. Fix: run a
   **warm-up batch** (100–200 synthetic cases, using the deterministic/rule-based path
   only, no LLM) BEFORE the graded baseline-vs-AI comparison run, purely to populate
   `recovery_playbook` with real precedent. Label this clearly in your demo as a
   warm-up/backfill phase — this is honest, and it mirrors how a real production
   system would be seeded from historical data before going live, which is a point
   worth making out loud.
2. **Insufficient precedent, even after warm-up.** If a case's retrieval returns fewer
   than a minimum threshold (e.g. 5 similar cases), the confidence number is
   inherently unreliable regardless of the smoothing. New Policy Engine rule: **route
   any case with insufficient retrieved precedent to human escalation**, regardless of
   its computed confidence value or the case's ₹ amount. This is the direct answer to
   "what if it's a real-world case and the system doesn't have enough evidence" — it
   doesn't guess, it escalates.

**Log both numbers, always.** Even though the empirical number is what gates the
decision, still capture the LLM's own stated confidence in the audit log alongside
it. If the two diverge a lot (LLM says very confident, empirical evidence says
weak), that divergence is itself a useful signal worth flagging for review — this is
literally how real ML risk teams monitor model calibration over time, and mentioning
this in your pitch demonstrates you understand the difference between a model's
opinion and a trustworthy number.

**If this went to real production (worth one line in your pitch, not a build item):**
you'd additionally want backtesting against real historical outcomes before launch,
ongoing calibration monitoring (are confidence numbers still tracking real accuracy
over time), and a circuit breaker that halts autonomous action and forces full human
review if measured recovery rate drops below a threshold. None of this needs to be
built for the buildathon — saying you know it's the next step is the signal, not
building it under time pressure.

## 8. Stopping rules & compliant escalation (explicitly named because the bar names them)

- **Retry cap:** no case gets more than `MAX_RETRY_ATTEMPTS` (3) automated retries —
  beyond that it must go through the Strategist for a non-retry action or escalate.
- **Communication frequency cap:** no customer receives more than N recovery messages
  in a rolling window (e.g. 1 per 48 hours) — Policy Engine enforces this, not the LLM.
- **Incentive ceiling:** `MAX_INCENTIVE_PERCENT` (10%) and `MAX_INCENTIVE_AMOUNT`
  (₹500) are hard limits — any LLM proposal above this is rejected or escalated, not
  silently capped.
- **Promise-to-pay follow-up limit:** a broken promise gets at most one follow-up
  attempt before mandatory human escalation — no infinite reminder loops.
- **High-value auto-escalation:** any case above `HIGH_VALUE_THRESHOLD` (₹25,000)
  requires human approval regardless of what the Strategist proposes.
- **Insufficient-precedent escalation (new):** any case where empirical confidence is
  based on fewer than the minimum retrieved/queried sample size escalates to human
  review, regardless of amount — the system doesn't act confidently on thin evidence.

## 9. Feature checklist

**Must have:**
- [ ] Synthetic dataset generator (500–1,000 transactions, 5–6 segments, 5–6 failure
      types), using a calibrated failure taxonomy/probability distribution informed by
      authentic Razorpay Test Mode hero-case observations
- [ ] Razorpay Test Mode integration for a small hero subset (~50–100 cases when practical),
      including real test orders/payment outcomes and a working `payment.failed` webhook
      ingestion path
- [ ] Payment/WhatsApp/Email/Incentive simulators with reproducible probabilities
- [ ] Revenue Detective: real deterministic score + real LLM classification/reasoning
      + empirical (not LLM-stated) confidence
- [ ] Customer Intelligence: real profile + real LLM reasoning + empirical confidence
- [ ] Recovery Strategist: RAG retrieval tool call + LLM decision grounded in
      retrieved precedent, constrained action enum, empirical confidence from
      retrieved-case success rate
- [ ] Warm-up seeding batch run before the graded AI run, clearly labeled as such
- [ ] Insufficient-precedent escalation rule wired into the Policy Engine
- [ ] Policy Engine enforcing all stopping rules in section 8, visibly rejecting or
      escalating at least one real case in the demo
- [ ] Executor + simulators, full audit log for every step (including both the LLM's
      stated confidence AND the empirical confidence, logged side by side)
- [ ] Promise-to-Pay tracker: creation, resolution (kept/broken), one follow-up cycle
- [ ] Recovery Analyst: metrics + baseline-vs-AI comparison + ChromaDB write-back
- [ ] Frontend: Dashboard (headline numbers + baseline-vs-AI chart), Recovery Cases
      table, Agent Activity timeline
- [ ] Public GitHub repo, README, architecture diagram, 5-minute pitch video

**Nice to have (only if ahead of schedule):**
- [ ] Surfacing "learned" insights in the UI (e.g. "WhatsApp outperforms Email for
      AT_RISK segment — based on N retrieved cases, X% empirical success")
- [ ] A UI flag/badge on cases where LLM-stated and empirical confidence diverged
- [ ] Human approval queue UI for escalated cases

**Explicitly out of scope:**
- Full-scale browser-driven Razorpay checkout for all 500–1,000 cases
- Production/live Razorpay payments; only Razorpay Test Mode is used for the hero subset
- Backtesting, live calibration monitoring, and circuit breakers (mention as future
  work in the pitch, don't build under time pressure)
- Any of the cut items in section 3

## 10. Data model (core tables)

`customers` · `transactions` · `payment_failures` · `revenue_leaks` · `recovery_cases`
· `recovery_actions` · `communication_events` · `promise_to_pay` (new: case_id,
committed_amount, committed_date, status [PENDING/KEPT/BROKEN], follow_up_count) ·
`audit_logs` (now includes both `llm_stated_confidence` and `empirical_confidence`
fields, plus `precedent_sample_size`) · `recovery_metrics` · `webhook_events` (recommended:
provider_event_id, event_type, received_at, processed_at, status for Razorpay webhook
idempotency)

Plus a **ChromaDB collection** (`recovery_playbook`) storing one embedded document per
resolved case: `{segment, failure_reason, action_taken, channel, outcome, recovered_amount}`
— populated first by the warm-up batch (section 8), then continuously by the Recovery
Analyst as the graded run proceeds. This is simulated precedent, not independent real-world production history. Razorpay
Test Mode hero observations are authentic test-environment events, but they are still
test data and must not be presented as production traffic. Document this distinction
honestly in the README.

## 11. Architecture

The architecture below keeps the existing recovery workflow unchanged. Razorpay Test Mode
is an additional event-driven entry point, while bulk evaluation remains the existing
batch path.

```
                 Razorpay Test Mode
                        |
                 payment.failed
                        |
                 FastAPI webhook
                        |
                 RecoveryCase
                        |
                        +---------------------------+
                                                    |
                    React + Vite + Tailwind         |
                             |                      |
                             +---- FastAPI ----------+
                                                    |
                             [WARM-UP / BULK / EVENT]
                                                    |
                        FastAPI (single service)
                             |
              [WARM-UP PHASE: rule-based batch run,
               populates ChromaDB recovery_playbook
               with initial precedent before grading]
                             |
                    LangGraph orchestration
        Detective -> Customer Intel -> Strategist
        (each: deterministic signal -> empirical     |
         confidence via SQL aggregate + LLM          |
         reasoning/classification on top)             |
                                          |
                              [tool call] Query ChromaDB
                              (recovery_playbook: similar
                               past cases + outcomes)
                              -> empirical confidence =
                                 smoothed success rate
                              -> if sample too small,
                                 flag for escalation
                                          |
                                    Policy Engine
                                (deterministic gate incl.
                                 insufficient-precedent rule)
                              /                    \
                        APPROVE                  BLOCK/ESCALATE
                           |                           |
                        Executor                 Human queue
              /      |        |        \
         Payment  WhatsApp  Email   Incentive
         (sim)     (sim)    (sim)    service
                           |
                  Promise-to-Pay created?
                     /            \
                  YES              NO
                   |
            Tracked, checked later
            kept -> done
            broken -> Strategist (follow-up) -> Policy -> ...
                           |
                    Recovery Analyst
              Metrics + Baseline comparison
                           |
              Write outcome -> ChromaDB (recovery_playbook)
                  (closes the feedback loop for future cases)
```

## 12. API endpoints (minimum set)

- `POST /data/generate` — generate synthetic dataset
- `POST /run/warmup` — rule-based warm-up batch, populates `recovery_playbook` only
- `POST /run/baseline` — naive retry-once baseline over the dataset
- `POST /run/ai` — full agent pipeline (Detective → Intel → Strategist w/ RAG →
  Policy → Executor → Promise-to-Pay → Analyst)
- `GET /dashboard/summary` — headline numbers, read from stored `recovery_metrics`
- `GET /cases` / `GET /cases/{id}/timeline` — case list and audit trail (shows both
  confidence numbers and the retrieved-precedent count)
- `GET /agents/activity` — live agent decision feed
- `GET /promises` — promise-to-pay status list
- `POST /webhooks/razorpay` — receive and idempotently ingest Razorpay Test Mode payment
  events (especially `payment.failed`) and trigger the existing recovery workflow

## 13. Build order (not tied to fixed days — sequence matters more than dates)

1. Confirm existing backend (models, policy engine, executor, simulators) — this is
   already solid, reuse it.
2. Fix the three reasoning agents: real LLM calls for classification/reasoning, with
   confidence computed empirically (SQL aggregate for Detective/Intelligence) rather
   than a formula or a bare constant.
3. Stand up ChromaDB, write the case-embedding schema, wire the Analyst's write-back.
4. Build the warm-up batch endpoint and run it to seed `recovery_playbook`.
5. Add the Strategist's retrieval tool call, empirical confidence from retrieved-case
   success rate, and the insufficient-precedent escalation rule in the Policy Engine.
6. Add the `promise_to_pay` table and the follow-up cycle, wired back through the
   Strategist.
7. Add Razorpay Test Mode hero integration: test credentials, order/payment flow,
   webhook ingestion, event idempotency, and mapping into the existing PaymentFailure /
   RecoveryCase models. Keep the hero subset small and reliable.
8. Calibrate the synthetic generator's failure taxonomy/probabilities from the authentic
   Razorpay hero observations, while keeping the bulk simulator reproducible.
9. Build the three frontend screens against the now-real backend, including the
   confidence-source and precedent-count display.
10. Docs: architecture diagram, demo script, README (including the honest note about
    ChromaDB precedent being simulated, not real-world, and the Razorpay Test Mode hero
    integration / calibrated synthetic-data approach).
11. Full re-run of the verification checklist below. Record the pitch video.
12. Buffer.

## 14. Verification checklist (self-check before submitting)

- [ ] Every ₹ number in the dashboard comes from a real run stored in `recovery_metrics`
- [ ] Every agent's confidence number is empirically computed (SQL aggregate or
      retrieved-case success rate), not a formula tuned by hand and not the LLM's
      self-reported number — confirm by tracing the actual code path
- [ ] The warm-up batch runs and visibly populates `recovery_playbook` before the
      graded run starts
- [ ] At least one case during the graded run has insufficient precedent and is
      correctly escalated rather than acted on with a guessed confidence
- [ ] The Strategist's RAG tool call is real — show a retrieved case, its outcome, and
      how the computed empirical confidence and the final decision followed from it,
      for at least 2 different cases
- [ ] At least one action was REJECTED or ESCALATED by the Policy Engine, visible in
      the demo, with the specific stopping rule it violated
- [ ] At least one promise-to-pay was broken and correctly triggered a bounded
      follow-up, not an infinite loop
- [ ] Razorpay Test Mode hero flow produces at least one authentic test order/payment
      event and a successfully ingested `payment.failed` webhook
- [ ] Duplicate Razorpay webhook delivery does not create duplicate recovery cases or
      trigger duplicate autonomous recovery actions
- [ ] Hero Razorpay cases and bulk synthetic cases converge on the same RecoveryCase /
      LangGraph / Policy / Executor workflow
- [ ] Synthetic failure taxonomy/probabilities are explicitly documented as calibrated
      from the hero observations, not presented as real-world production statistics
- [ ] Baseline and AI results ran against the exact same dataset
- [ ] Full audit trail for one case, shown live, start to finish, showing both
      confidence numbers side by side
- [ ] Repo is public, README explains the real architecture — including the honest
      note that RAG precedent is simulated, not independent real-world data — and the
      pitch video is ≤ 5 minutes
