from datetime import datetime

from pydantic import BaseModel, Field


class AgentActivityItem(BaseModel):
    id: str
    case_id: str
    agent: str = Field(
        description="Agent name: Detective, Intelligence, Strategist, Policy, Executor, Analyst"
    )
    step_name: str
    input_summary: str
    output_summary: str
    decision: str | None = None
    confidence: float
    empirical_confidence: float | None = None
    llm_stated_confidence: float | None = None
    precedent_sample_size: int | None = 0
    timestamp: datetime


class AgentActivityFeedResponse(BaseModel):
    activities: list[AgentActivityItem]
    total_events: int
