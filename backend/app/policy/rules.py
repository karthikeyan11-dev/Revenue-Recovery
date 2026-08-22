"""Deterministic Policy Boundaries & Governance Constants."""

# Maximum allowed automated retry attempts before human escalation
MAX_RETRY_ATTEMPTS: int = 3

# Maximum discount/incentive percentage allowed by autonomous agent
MAX_INCENTIVE_PERCENT: float = 10.0

# Transaction amount threshold requiring human approval if churn risk > 0.4
HIGH_VALUE_THRESHOLD: float = 25000.0

# Minimum cooldown hours between automated messages to same customer
MIN_HOURS_BETWEEN_MESSAGES: int = 6

# Allowed communication channels
ALLOWED_CHANNELS: list[str] = ["WHATSAPP", "EMAIL", "SMS"]
