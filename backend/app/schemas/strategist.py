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
    reasoning: str = Field(
        description="Strategic reasoning explaining why this bounded action was selected",
    )
