class AppBaseException(Exception):
    """Base domain exception for Revenue Recovery Orchestrator."""

    def __init__(self, message: str, code: str | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__


class DatabaseException(AppBaseException):
    """Database connectivity or query exception."""


class IntegrationException(AppBaseException):
    """Third-party service/API integration error."""


class RazorpayIntegrationException(IntegrationException):
    """Razorpay API integration failure."""


class LLMIntegrationException(IntegrationException):
    """LLM provider call failure."""


class PolicyViolationException(AppBaseException):
    """Deterministic policy guardrail violation."""


class EntityNotFoundException(AppBaseException):
    """Requested domain entity was not found."""
