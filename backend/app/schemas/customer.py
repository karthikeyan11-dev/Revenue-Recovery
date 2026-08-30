from pydantic import BaseModel, Field


class CustomerIntelligenceOutput(BaseModel):
    """Structured Pydantic output for Customer Intelligence agent using payment-native signals."""

    customer_id: str = Field(description="Analyzed customer identifier")
    payer_reliability_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Historical payment success reliability score with Laplace smoothing ((successes + 2) / (total + 4))",
    )
    total_past_transactions: int = Field(
        default=0, ge=0, description="Total historical transactions count"
    )
    successful_past_transactions: int = Field(
        default=0, ge=0, description="Total successful transactions count"
    )
    timing_band: str = Field(
        default="RECENT", description="Timing classification band ('RECENT' or 'STALE')"
    )
    hours_since_failure: float = Field(
        default=0.0, ge=0.0, description="Hours elapsed since this failure occurred"
    )
    recent_failure_count: int = Field(
        default=1,
        ge=0,
        description="Number of failure attempts for this customer in recent 30-minute window",
    )
    has_alternate_rail: bool = Field(
        default=False,
        description="Whether customer has successfully completed payment via a different payment method in the past",
    )
    alternate_rails: list[str] = Field(
        default_factory=list,
        description="List of previously successful alternate payment methods (e.g. ['UPI', 'NETBANKING'])",
    )
    available_channels: list[str] = Field(
        default_factory=list,
        description="Factual list of available contact channels (e.g. ['WHATSAPP', 'SMS', 'EMAIL'])",
    )
    confidence: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Empirically computed recovery confidence score (Laplace smoothed by failure reason)",
    )
    insights: str = Field(description="Contextual customer recovery insights")
    llm_stated_confidence: float | None = Field(
        default=None,
        description="LLM self-stated confidence for audit & calibration tracking",
    )
    precedent_sample_size: int = Field(
        default=0,
        ge=0,
        description="Number of matching past resolved failure cases queried",
    )

