from datetime import datetime

from pydantic import BaseModel, Field


class AgentStatusInfo(BaseModel):
    name: str
    status: str = "Online"  # Online | Busy | Idle
    last_active: datetime | None = None


class AgentActivityItem(BaseModel):
    id: str
    case_id: str
    agent: str = Field(
        description="Agent name: Detective, Intelligence, Strategist, Policy, Executor, Analyst"
    )
    step_name: str
    action_name: str = "Processing"
    status: str = "Completed"  # Completed | Approved | Escalated | Dispatched
    input_summary: str
    output_summary: str
    decision: str | None = None
    confidence: float
    empirical_confidence: float | None = None
    llm_stated_confidence: float | None = None
    precedent_sample_size: int | None = 0
    duration_seconds: float = 1.25
    timestamp: datetime


class AgentActivityStats(BaseModel):
    active_agents_count: int = 6
    total_agents_count: int = 6
    active_cases_count: int = 0
    actions_today_count: int = 0
    success_rate_percent: float = 0.0
    avg_processing_time_seconds: float = 2.41
    playbook_precedent_count: int = 0
    playbook_learned_cases_count: int = 0
    agent_statuses: list[AgentStatusInfo] = []


class AgentActivityFeedResponse(BaseModel):
    activities: list[AgentActivityItem]
    stats: AgentActivityStats
    total_events: int


class PlaybookReasonBreakdownItem(BaseModel):
    failure_reason: str
    display_name: str
    count: int


class PlaybookActionBreakdownItem(BaseModel):
    action: str
    display_name: str
    count: int


class PlaybookOutcomesSummary(BaseModel):
    recovered_count: int
    failed_or_escalated_count: int


class PlaybookStatsDetail(BaseModel):
    total_cases: int = 0
    baseline_precedents: int = 0
    learned_cases: int = 0
    failure_reasons: list[PlaybookReasonBreakdownItem] = []
    outcomes: PlaybookOutcomesSummary | None = None
    actions: list[PlaybookActionBreakdownItem] = []
