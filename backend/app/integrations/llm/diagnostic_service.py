import hashlib
import json
import logging
import time
from typing import Any

import openai
from pydantic import BaseModel, Field

from app.config import settings

logger = logging.getLogger("app.integrations.llm.diagnostic_service")


class DiagnosticLLMResult(BaseModel):
    narrative: str
    status: str = Field(description="'live', 'cached', or 'unavailable'")
    model_attributed: str | None = None
    generated_at_unix: float


class RealLLMDiagnosticService:
    """
    Dedicated Real-LLM Reasoning Engine for the Judge-Facing Forensic Diagnostic Panel.
    ALWAYS executes a live LLM call regardless of the system-wide LLM_PROVIDER setting.
    Includes strict timeouts, single retry, real model attribution, run-level caching,
    and a genuine failure fallback (never pretends canned text is LLM-generated).
    """

    # In-memory run-level cache: {cohort_fingerprint: DiagnosticLLMResult}
    _run_cache: dict[str, DiagnosticLLMResult] = {}

    # Verified candidates on OpenRouter
    PRIMARY_MODELS = [
        "minimax/minimax-m3:free",
        "nvidia/nemotron-3.5-lightning:free",
    ]

    @classmethod
    def compute_cohort_fingerprint(cls, cases: list[Any]) -> str:
        """Computes a deterministic hash representing the current failure/recovery cohort state."""
        if not cases:
            return "empty_cohort"
        serialized = "|".join(
            sorted(f"{c.id}:{c.status.value}:{float(c.recovered_amount or 0.0):.2f}" for c in cases)
        )
        return hashlib.md5(serialized.encode("utf-8")).hexdigest()

    @classmethod
    def get_or_generate_narrative(
        cls,
        cases: list[Any],
        metrics_dict: dict[str, Any],
        verdict: str,
        escalated_cases_data: list[dict[str, Any]],
        primary_reasons: list[str],
        force_refresh: bool = False,
    ) -> DiagnosticLLMResult:
        fingerprint = cls.compute_cohort_fingerprint(cases)

        # 1. Return cached narrative if this run was already analyzed and not force-refreshed
        if not force_refresh and fingerprint in cls._run_cache:
            cached = cls._run_cache[fingerprint]
            logger.info(f"Returning cached LLM diagnostic narrative for cohort {fingerprint[:8]}")
            return DiagnosticLLMResult(
                narrative=cached.narrative,
                status="cached",
                model_attributed=cached.model_attributed,
                generated_at_unix=cached.generated_at_unix,
            )

        # 2. Prepare strictly grounded prompt with real telemetry
        ai_rev = metrics_dict.get("ai_recovered", 0.0)
        base_rev = metrics_dict.get("baseline_recovered", 0.0)
        ai_cases = metrics_dict.get("ai_recovered_cases", 0)
        base_cases = metrics_dict.get("baseline_recovered_cases", 0)
        total_cases = metrics_dict.get("total_cases", 0)
        ai_case_rate = metrics_dict.get("ai_case_rate", 0.0)
        base_case_rate = metrics_dict.get("baseline_case_rate", 0.0)
        escalated_count = metrics_dict.get("escalated_cases_count", 0)
        escalated_rev = metrics_dict.get("escalated_revenue_inr", 0.0)

        system_prompt = (
            "You are a fintech payment operations analyst presenting to hackathon judges. "
            "Explain why the AI Revenue Recovery Orchestrator performed against the Naive Baseline in 2 concise, executive sentences. "
            "RULES:\n"
            "1. Only cite the EXACT numbers provided in the user context. Do not invent any numbers.\n"
            "2. If baseline has higher gross revenue because high-value transactions were routed to the human escalation queue by policy guardrails, state that clearly.\n"
            "3. If AI has a higher case recovery count, emphasize customer account retention.\n"
            "4. Respond with NO preamble, NO thinking traces, and NO bullet points—strictly 2 boardroom-ready sentences."
        )

        whale_summary = ", ".join(
            f"₹{c['amount']:,.0f} ({c['failure_reason']}, rule: {c['policy_rule']})"
            for c in escalated_cases_data[:3]
        )

        user_prompt = (
            f"Cohort Telemetry:\n"
            f"- Verdict: {verdict}\n"
            f"- AI Recovered Revenue: ₹{ai_rev:,.2f} ({metrics_dict.get('ai_recovery_rate', 0):.1f}%)\n"
            f"- Baseline Recovered Revenue: ₹{base_rev:,.2f} ({metrics_dict.get('baseline_recovery_rate', 0):.1f}%)\n"
            f"- AI Customer Cases Rescued: {ai_cases} of {total_cases} ({ai_case_rate:.1f}%)\n"
            f"- Baseline Customer Cases Rescued: {base_cases} of {total_cases} ({base_case_rate:.1f}%)\n"
            f"- Cases Held in Human Escalation Queue: {escalated_count} cases totaling ₹{escalated_rev:,.2f}\n"
            f"- Key Escalated Transactions: {whale_summary or 'None'}\n"
            f"- System Key Drivers: {'; '.join(primary_reasons)}"
        )

        # 3. Attempt live LLM generation across real providers with timeout & 1 retry
        openrouter_key = settings.OPENROUTER_API_KEY
        if openrouter_key and not openrouter_key.startswith("your_") and not openrouter_key.startswith("mock-dev-key"):
            client = openai.OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=openrouter_key,
                timeout=8.0,
                max_retries=1,
                default_headers={
                    "HTTP-Referer": "https://github.com/karthikeyan11-dev/Revenue-Recovery",
                    "X-Title": "AI Revenue Recovery Orchestrator",
                },
            )

            for model_candidate in cls.PRIMARY_MODELS:
                try:
                    logger.info(f"Calling live LLM for diagnostic analysis via OpenRouter model '{model_candidate}'...")
                    response = client.chat.completions.create(
                        model=model_candidate,
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        max_tokens=150,
                        temperature=0.2,
                    )
                    raw_text = response.choices[0].message.content or ""
                    clean_text = cls._clean_narrative(raw_text)

                    if clean_text and len(clean_text) > 30:
                        result = DiagnosticLLMResult(
                            narrative=clean_text,
                            status="live",
                            model_attributed=f"{model_candidate} (OpenRouter)",
                            generated_at_unix=time.time(),
                        )
                        cls._run_cache[fingerprint] = result
                        return result
                except Exception as e:
                    logger.warning(f"Live LLM call to '{model_candidate}' failed: {e}")
                    continue

        # 4. Genuine Failure Fallback (Never fake canned text as LLM generated)
        logger.error("All live LLM reasoning calls failed or timed out. Returning genuine unavailable status.")
        return DiagnosticLLMResult(
            narrative="Live LLM reasoning is temporarily unavailable. Telemetry metrics and deterministic policy audit trail below remain verified from PostgreSQL.",
            status="unavailable",
            model_attributed=None,
            generated_at_unix=time.time(),
        )

    @staticmethod
    def _clean_narrative(text: str) -> str:
        """Strips out thinking tokens or meta-commentary from reasoning models."""
        cleaned = text.strip()
        # Strip reasoning model thinking traces like "Here's a thinking process: ... \n\n"
        if "Here's a thinking process:" in cleaned:
            parts = cleaned.split("\n\n")
            non_thinking = [p for p in parts if not p.startswith("Here's a thinking") and not p.strip().startswith("1.") and not p.strip().startswith("2.")]
            if non_thinking:
                cleaned = " ".join(non_thinking).strip()
        return cleaned
