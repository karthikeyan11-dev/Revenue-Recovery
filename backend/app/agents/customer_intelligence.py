import logging

from app.models.customer import Customer
from app.schemas.customer_intel import CustomerIntelligenceOutput

logger = logging.getLogger("app.agents.intelligence")


class CustomerIntelligenceAgent:
    """
    Customer Intelligence Agent Node.
    Evaluates customer profile, lifetime value, churn risk, and preferred communication affinity.
    """

    @classmethod
    def profile(cls, customer: Customer) -> CustomerIntelligenceOutput:
        seg = customer.segment
        churn_risk = customer.churn_probability
        ltv = customer.ltv

        if seg.value in ["HIGH_VALUE", "LOYAL"]:
            recovery_prob = 0.88
            insights = f"Tier-1 customer with ₹{ltv:,.2f} LTV. Low tolerance for aggressive retries; prefers white-glove {customer.preferred_channel.value} outreach."
        elif seg.value in ["AT_RISK", "CHURNING"]:
            recovery_prob = 0.45
            insights = f"High churn risk ({churn_risk:.0%}). Needs targeted incentive to prevent permanent cart abandonment."
        else:
            recovery_prob = 0.70
            insights = f"Standard customer profile. Responsive to automated reminders on {customer.preferred_channel.value}."

        return CustomerIntelligenceOutput(
            customer_id=customer.id,
            segment=seg,
            ltv=ltv,
            churn_probability=churn_risk,
            recovery_probability=recovery_prob,
            preferred_channel=customer.preferred_channel,
            insights=insights,
        )
