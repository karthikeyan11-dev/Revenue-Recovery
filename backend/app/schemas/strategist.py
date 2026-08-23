from typing import Any

from pydantic import BaseModel, Field

from app.models.recovery_action import ActionType


class ProposedRecoveryAction(BaseModel):
    """Structured Pydantic output for Recovery Strategist agent."""

    action_type: ActionType = Field(description="Action proposed by strategist")
    incentive_percent: float = Field(
        default=0.0,
        ge=0.0,
        le=50.0,
        description="Proposed discount percentage if offering an incentive",
    )
    retry_delay_hours: int = Field(
        default=0,
        ge=0,
        le=72,
        description="Delay before smart retry attempt in hours",
    )
    channel: str | None = Field(
        default=None,
        description="Target communication channel (WHATSAPP/EMAIL/SMS)",
    )
    message_tone: str = Field(
        default="EMPATHETIC",
        description="Tone of the outreach message (EMPATHETIC / URGENT / INFORMATIVE)",
    )
    confidence: float = Field(
        default=0.50,
        ge=0.0,
        le=1.0,
        description="Empirical confidence computed from Laplace smoothing over retrieved playbook cases",
    )
    insufficient_precedent: bool = Field(
        default=False,
        description="Flag indicating fewer than 5 precedent cases retrieved from recovery_playbook",
    )
    retrieved_precedent_count: int = Field(
        default=0,
        description="Count of similar historical cases retrieved from recovery_playbook",
    )
    retrieved_cases_summary: list[dict[str, Any]] | None = Field(
        default=None,
        description="Summary list of retrieved precedent cases for grounding evidence",
    )
    llm_stated_confidence: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Strategist LLM self-stated confidence for audit calibration (never used for policy gating)",
    )
    reasoning: str = Field(
        description="Strategic reasoning explaining why this bounded action was selected, grounded in retrieved precedents",
    )
