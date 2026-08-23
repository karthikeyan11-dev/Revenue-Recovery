import pytest
from pydantic import ValidationError

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.llm_client import LLMClient
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.agents.revenue_detective import RevenueDetectiveAgent
from app.config import Settings
from app.llm.anthropic_provider import AnthropicProvider
from app.llm.factory import get_llm_provider
from app.llm.google_provider import GoogleProvider
from app.llm.mock_provider import MockProvider
from app.llm.openai_provider import OpenAIProvider
from app.models.customer import CommunicationChannel, Customer, CustomerSegment
from app.models.payment_failure import FailureReason, PaymentFailure
from app.models.transaction import Transaction, TransactionStatus


def test_provider_factory_instantiates_correct_classes():
    """Verify that factory creates exactly the requested provider subclass."""
    # Anthropic
    p_anthropic = get_llm_provider("anthropic", "claude-3-5-sonnet-20241022", "sk-ant-test-key")
    assert isinstance(p_anthropic, AnthropicProvider)
    assert p_anthropic.model == "claude-3-5-sonnet-20241022"

    # OpenAI
    p_openai = get_llm_provider("openai", "gpt-4o-mini", "sk-test-openai-key")
    assert isinstance(p_openai, OpenAIProvider)
    assert p_openai.model == "gpt-4o-mini"

    # Google
    p_google = get_llm_provider("google", "gemini-1.5-flash", "test-google-key")
    assert isinstance(p_google, GoogleProvider)
    assert p_google.model == "gemini-1.5-flash"

    # Mock
    p_mock = get_llm_provider("mock", "mock-custom-model", "test-key")
    assert isinstance(p_mock, MockProvider)
    assert p_mock.model == "mock-custom-model"


def test_unsupported_provider_raises_error():
    """Verify that invalid provider names raise clear validation/value errors."""
    with pytest.raises(ValueError, match="Unsupported LLM_PROVIDER"):
        get_llm_provider("unsupported_vendor", "some-model", "some-key")

    with pytest.raises(ValidationError):
        Settings(LLM_PROVIDER="invalid_provider")


def test_mock_provider_generates_reasoning():
    """Verify Mock provider returns formatted reasoning."""
    provider = MockProvider(model="test-mock-model")
    res = provider.generate_reasoning("system prompt", "user prompt")
    assert "MockLLM Reasoning" in res
    assert "test-mock-model" in res


def test_llm_client_with_mock_provider(monkeypatch):
    """Verify LLMClient uses active provider and returns structured reasoning."""
    monkeypatch.setattr("app.config.settings.LLM_PROVIDER", "mock")
    monkeypatch.setattr("app.config.settings.MODEL", "mock-agent-model")

    text = LLMClient.generate_reasoning(
        system_prompt="Test system",
        user_prompt="Test user",
        fallback_text="Fallback text",
    )
    assert "MockLLM Reasoning" in text
    assert "mock-agent-model" in text


def test_agents_use_configured_provider_and_produce_pydantic_outputs(monkeypatch):
    """Verify all 3 agents use the configured provider seamlessly."""
    monkeypatch.setattr("app.config.settings.LLM_PROVIDER", "mock")
    monkeypatch.setattr("app.config.settings.MODEL", "claude-or-gemini-or-gpt")

    customer = Customer(
        id="cust_test_prov",
        name="Ananya Sharma",
        email="ananya@example.com",
        segment=CustomerSegment.LOYAL,
        ltv=45000.0,
        preferred_channel=CommunicationChannel.WHATSAPP,
        churn_probability=0.15,
    )
    txn = Transaction(
        id="txn_test_prov",
        customer_id=customer.id,
        amount=3499.0,
        currency="INR",
        status=TransactionStatus.FAILED,
    )
    failure = PaymentFailure(
        id="fail_test_prov",
        transaction_id=txn.id,
        failure_reason=FailureReason.INSUFFICIENT_FUNDS,
        attempt_number=1,
    )
    txn.customer = customer
    failure.transaction = txn

    # 1. Revenue Detective
    det_out = RevenueDetectiveAgent.analyze(failure)
    assert det_out.failure_id == failure.id
    assert "MockLLM Reasoning" in det_out.reasoning

    # 2. Customer Intelligence
    intel_out = CustomerIntelligenceAgent.profile(customer)
    assert intel_out.customer_id == customer.id
    assert "MockLLM Reasoning" in intel_out.insights

    # 3. Recovery Strategist
    strat_out = RecoveryStrategistAgent.propose_action(det_out, intel_out)
    assert strat_out.action_type is not None
    assert "MockLLM Reasoning" in strat_out.reasoning
