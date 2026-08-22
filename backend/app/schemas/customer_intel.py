from pydantic import BaseModel, Field

from app.models.customer import CommunicationChannel, CustomerSegment


class CustomerIntelligenceOutput(BaseModel):
    """Structured Pydantic output for Customer Intelligence agent."""

    customer_id: str = Field(description="Analyzed customer identifier")
    segment: CustomerSegment = Field(description="Segment classification")
    ltv: float = Field(ge=0, description="Customer lifetime value")
    churn_probability: float = Field(ge=0.0, le=1.0, description="Estimated churn probability")
    recovery_probability: float = Field(
        ge=0.0, le=1.0, description="Estimated recovery probability based on history"
    )
    preferred_channel: CommunicationChannel = Field(description="Optimal recovery outreach channel")
    insights: str = Field(description="Contextual customer recovery insights")
