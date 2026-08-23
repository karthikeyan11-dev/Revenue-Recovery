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
    confidence: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Empirically computed recovery confidence score (Laplace smoothed)",
    )
    preferred_channel: CommunicationChannel = Field(description="Optimal recovery outreach channel")
    insights: str = Field(description="Contextual customer recovery insights")
    llm_stated_confidence: float | None = Field(
        default=None,
        description="LLM self-stated confidence for audit & calibration tracking",
    )
    precedent_sample_size: int = Field(
        default=0,
        ge=0,
        description="Number of matching past resolved customer cases queried",
    )
