from pydantic import BaseModel, Field

from app.models.revenue_leak import LeakType


class RevenueDetectiveOutput(BaseModel):
    """Structured Pydantic output for Revenue Detective agent."""

    failure_id: str = Field(description="ID of the analyzed payment failure")
    leak_type: LeakType = Field(description="Classified leak category")
    amount: float = Field(ge=0, description="Amount of revenue at risk in INR")
    confidence: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Empirically computed detection confidence score (Laplace smoothed)",
    )
    recoverability_score: float = Field(
        ge=0.0, le=1.0, description="Estimated recoverability potential"
    )
    reasoning: str = Field(description="Technical and domain reasoning for classification")
    llm_stated_confidence: float | None = Field(
        default=None,
        description="LLM self-stated confidence for audit & calibration tracking",
    )
    precedent_sample_size: int = Field(
        default=0,
        ge=0,
        description="Number of matching past resolved cases queried",
    )
