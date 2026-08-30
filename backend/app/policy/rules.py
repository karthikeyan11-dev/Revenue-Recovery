"""Deterministic Policy Boundaries & Governance Constants."""

# Maximum allowed automated retry attempts before human escalation
MAX_RETRY_ATTEMPTS: int = 3

# Maximum discount/incentive percentage allowed by autonomous agent
MAX_INCENTIVE_PERCENT: float = 10.0

# Transaction amount threshold requiring human approval if reliability score < 0.50
HIGH_VALUE_THRESHOLD: float = 25000.0

# Minimum cooldown hours between automated messages to same customer
MIN_HOURS_BETWEEN_MESSAGES: int = 6

# Minimum required precedent cases in recovery_playbook to allow autonomous action
MIN_PRECEDENT_SAMPLE_SIZE: int = 5

# Maximum automated follow-up attempts for broken promise-to-pay before mandatory escalation
MAX_PROMISE_FOLLOWUPS: int = 1

# Policy Rule Identifier Constants
RULE_INSUFFICIENT_PRECEDENT: str = "INSUFFICIENT_PRECEDENT_GATE"
RULE_MAX_INCENTIVE_PERCENT: str = "MAX_INCENTIVE_PERCENT_EXCEEDED"
RULE_MAX_RETRY_ATTEMPTS: str = "MAX_RETRY_ATTEMPTS_EXCEEDED"
RULE_HIGH_VALUE_LOW_RELIABILITY: str = "HIGH_VALUE_LOW_RELIABILITY_GATE"
RULE_HIGH_VALUE_HIGH_CHURN: str = RULE_HIGH_VALUE_LOW_RELIABILITY  # Alias for compatibility
RULE_STRATEGIST_ESCALATION: str = "STRATEGIST_ESCALATION_REQUEST"
RULE_MAX_PROMISE_FOLLOWUPS: str = "MAX_PROMISE_FOLLOWUPS_EXCEEDED"
