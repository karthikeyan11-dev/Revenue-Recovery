import pytest
from pydantic import ValidationError

from app.agents.customer_intelligence import CustomerIntelligenceAgent
from app.agents.recovery_strategist import RecoveryStrategistAgent
from app.agents.revenue_detective import RevenueDetectiveAgent
from app.config import Settings
from app.integrations.llm.anthropic import AnthropicProvider
from app.integrations.llm.client import LLMClient
from app.integrations.llm.factory import get_llm_provider
from app.integrations.llm.google import GoogleProvider
from app.integrations.llm.mock import MockProvider
from app.integrations.llm.openai import OpenAIProvider
from app.integrations.llm.openrouter import OpenRouterProvider
from app.models.customer import Customer
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

    # OpenRouter
    p_openrouter = get_llm_provider(
        "openrouter", "google/gemini-2.0-flash-001", "sk-or-v1-test-key"
    )
    assert isinstance(p_openrouter, OpenRouterProvider)
    assert p_openrouter.model == "google/gemini-2.0-flash-001"

    # Mock
    p_mock = get_llm_provider("mock", "mock-custom-model", "test-key")
    assert isinstance(p_mock, MockProvider)
    assert p_mock.model == "mock-custom-model"


def test_openrouter_missing_api_key_raises_error():
    """Verify that empty or placeholder OpenRouter API key raises clear ValueError."""
    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
        OpenRouterProvider(model="anthropic/claude-3.5-sonnet", api_key="")

    with pytest.raises(ValueError, match="OPENROUTER_API_KEY is required"):
        OpenRouterProvider(
            model="anthropic/claude-3.5-sonnet", api_key="your_openrouter_api_key_here"
        )


def test_openrouter_model_passthrough_and_headers():
    """Verify OpenRouter preserves arbitrary vendor/model identifier and sets appropriate headers."""
    provider = OpenRouterProvider(
        model="meta-llama/llama-3.3-70b-instruct", api_key="sk-or-v1-valid-token"
    )
    assert provider.model == "meta-llama/llama-3.3-70b-instruct"
    assert str(provider.client.base_url).rstrip("/") == "https://openrouter.ai/api/v1"
    assert (
        provider.client.default_headers.get("HTTP-Referer")
        == "https://github.com/karthikeyan11-dev/Revenue-Recovery"
    )


def test_openrouter_generate_reasoning_mocked(monkeypatch):
    """Verify OpenRouter completions flow correctly into generated reasoning string."""
    provider = OpenRouterProvider(
        model="google/gemini-2.0-flash-001", api_key="sk-or-v1-valid-token"
    )

    class MockMessage:
        content = "Strategic analysis via OpenRouter: Recover transaction via WhatsApp."

    class MockChoice:
        message = MockMessage()

    class MockCompletion:
        choices = [MockChoice()]

    monkeypatch.setattr(
        provider.client.chat.completions,
        "create",
        lambda *args, **kwargs: MockCompletion(),
    )

    reasoning = provider.generate_reasoning("system prompt", "user prompt")
    assert "Strategic analysis via OpenRouter" in reasoning


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
        phone="+919876543210",
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
    intel_out = CustomerIntelligenceAgent.profile(customer, failure=failure)
    assert intel_out.customer_id == customer.id
    assert "MockLLM Reasoning" in intel_out.insights

    # 3. Recovery Strategist
    strat_out = RecoveryStrategistAgent.propose_action(
        det_out, intel_out, failure_reason=failure.failure_reason
    )
    assert strat_out.action_type is not None
    assert "MockLLM Reasoning" in strat_out.reasoning
