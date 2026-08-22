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
    timestamp: datetime


class AgentActivityFeedResponse(BaseModel):
    activities: list[AgentActivityItem]
    total_events: int
