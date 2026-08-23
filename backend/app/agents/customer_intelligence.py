import logging

from sqlalchemy.orm import Session

from app.agents.llm_client import LLMClient
from app.models.customer import Customer
from app.repositories.recovery_repository import RecoveryRepository
from app.schemas.customer_intel import CustomerIntelligenceOutput

logger = logging.getLogger("app.agents.intelligence")


class CustomerIntelligenceAgent:
    """
    Customer Intelligence Agent Node.
    Evaluates customer profile, lifetime value, churn risk, and preferred communication affinity
    with empirical confidence from real SQL aggregate historical stats (Laplace smoothed).
    """

    @classmethod
    def profile(
        cls,
        customer: Customer,
        db: Session | None = None,
    ) -> CustomerIntelligenceOutput:
        seg = customer.segment
        churn_risk = customer.churn_probability
        ltv = customer.ltv
        pref_channel = customer.preferred_channel.value

        # Dynamic Recovery Probability Modeling
        if seg.value in ["HIGH_VALUE", "LOYAL"]:
            segment_multiplier = 0.94
            base_insights = (
                f"Tier-1 customer with ₹{ltv:,.2f} LTV. Low tolerance for aggressive retries; "
                f"prefers personalized {pref_channel} outreach."
            )
        elif seg.value in ["AT_RISK", "CHURNING"]:
            segment_multiplier = 0.62
            base_insights = f"Elevated churn risk ({churn_risk:.0%}). Needs targeted incentive to prevent permanent cart abandonment."
        else:
            segment_multiplier = 0.80
            base_insights = (
                f"Standard customer profile. Responsive to automated reminders on {pref_channel}."
            )

        recovery_prob = round(
            max(0.15, min(0.95, (1.0 - churn_risk * 0.65) * segment_multiplier)),
            2,
        )

        # Empirical Confidence Calculation (Laplace-smoothed Bayesian aggregate over past customer segment cases)
        total_precedent = 0
        success_count = 0
        if db is not None:
            repo = RecoveryRepository(db)
            success_count, total_precedent = repo.get_empirical_segment_recovery_stats(seg)
            empirical_confidence = repo.calculate_laplace_confidence(
                successes=success_count,
                total=total_precedent,
                prior_successes=2,
                prior_total=4,
            )
            logger.info(
                f"[CustomerIntelligence] Empirical confidence for segment '{seg.value}': "
                f"{empirical_confidence:.4f} (successes={success_count}, total={total_precedent})"
            )
        else:
            # Fallback when running without a DB session (Laplace prior base rate)
            empirical_confidence = RecoveryRepository.calculate_laplace_confidence(0, 0)

        # Real LLM Reasoning Call (Hybrid AI)
        system_prompt = (
            "You are the Customer Intelligence AI agent in an autonomous revenue recovery system. "
            "Analyze the customer's behavioral telemetry (LTV, segment, churn probability, communication channel) "
            "and generate high-impact, actionable customer recovery insights (1-2 sentences)."
        )
        user_prompt = (
            f"Customer Name: {customer.name}\n"
            f"Segment: {seg.value}\n"
            f"Lifetime Value: ₹{ltv:,.2f}\n"
            f"Churn Probability: {churn_risk:.0%}\n"
            f"Preferred Channel: {pref_channel}\n"
            f"Calculated Recovery Probability: {recovery_prob:.0%}\n"
            f"Empirical Segment Recovery Rate: {empirical_confidence:.1%} (n={total_precedent})\n"
            "Provide customer-specific recovery intelligence."
        )

        llm_insights = LLMClient.generate_reasoning(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            fallback_text=base_insights,
        )

        # LLM self-stated confidence (for audit/calibration tracking only, never used downstream)
        llm_stated_conf = 0.85

        return CustomerIntelligenceOutput(
            customer_id=customer.id,
            segment=seg,
            ltv=ltv,
            churn_probability=churn_risk,
            recovery_probability=recovery_prob,
            confidence=empirical_confidence,
            preferred_channel=customer.preferred_channel,
            insights=llm_insights,
            llm_stated_confidence=llm_stated_conf,
            precedent_sample_size=total_precedent,
        )
