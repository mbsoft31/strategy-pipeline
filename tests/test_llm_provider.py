"""Unit tests for LLM Provider layer."""

import pytest
import json
from unittest.mock import Mock, patch

from src.services.llm_provider import (
    LLMProvider,
    MockProvider,
    OpenAIProvider,
    get_llm_provider
)
from src.utils.exceptions import (
    LLMProviderError,
    AuthenticationError,
    RateLimitError
)
from src.config import LLMProvider as ProviderEnum

# Check if openai is available
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class TestMockProvider:
    """Test MockProvider functionality."""

    def test_initialization(self):
        """Test MockProvider can be initialized."""
        provider = MockProvider()
        assert provider is not None

    def test_generate_project_context(self):
        """Test generating project context."""
        provider = MockProvider()

        response = provider.generate(
            "You are a methodologist",
            "Generate project context for: LLM hallucinations"
        )

        assert len(response) > 0
        # Should be valid JSON
        data = json.loads(response)
        assert "title" in data
        assert "discipline" in data

    def test_generate_critique(self):
        """Test generating critique."""
        provider = MockProvider()

        response = provider.generate(
            "You are a strict Senior Research Supervisor",
            "Critique this project"
        )

        assert len(response) > 0
        data = json.loads(response)
        assert "critique_summary" in data
        assert "feasibility_score" in data

    def test_generate_refine(self):
        """Test generating refinement."""
        provider = MockProvider()

        response = provider.generate(
            "You are a methodologist",
            "Refine based on critique"
        )

        assert len(response) > 0
        data = json.loads(response)
        assert "problem_statement" in data
        assert "goals" in data
        assert "key_concepts" in data

    def test_clean_json_response(self):
        """Test JSON cleaning."""
        provider = MockProvider()

        # Test with markdown fence
        response = '```json\n{"test": "value"}\n```'
        cleaned = provider.clean_json_response(response)
        assert cleaned == {"test": "value"}

        # Test without fence
        response = '{"test": "value"}'
        cleaned = provider.clean_json_response(response)
        assert cleaned == {"test": "value"}

    def test_clean_json_invalid(self):
        """Test JSON cleaning with invalid JSON."""
        provider = MockProvider()

        with pytest.raises(LLMProviderError):
            provider.clean_json_response("not json at all")


class TestOpenAIProvider:
    """Test OpenAIProvider functionality."""

    def test_initialization_without_key(self):
        """Test OpenAIProvider fails without API key."""
        with patch('src.config.get_config') as mock_config:
            mock_config.return_value.llm.openai_api_key = None

            with pytest.raises(AuthenticationError):
                OpenAIProvider()

    @pytest.mark.skipif(not HAS_OPENAI, reason="openai package not installed")
    def test_initialization_with_key(self):
        """Test OpenAIProvider initializes with API key."""
        with patch('src.config.get_config') as mock_config:
            config = Mock()
            config.llm.openai_api_key = "sk-test-key"
            config.llm.openai_model = "gpt-4o-mini"
            config.llm.openai_temperature = 0.7
            config.llm.openai_max_tokens = None
            config.llm.timeout = 30
            mock_config.return_value = config

            # Mock the openai import
            with patch('src.services.llm_provider.OpenAI') as mock_openai_class:
                provider = OpenAIProvider()
                assert provider.model == "gpt-4o-mini"
                assert provider.temperature == 0.7

    @pytest.mark.skipif(not HAS_OPENAI, reason="openai package not installed")
    def test_generate_success(self):
        """Test successful generation."""
        # Setup mock
        with patch('src.config.get_config') as mock_config:
            config = Mock()
            config.llm.openai_api_key = "sk-test-key"
            config.llm.openai_model = "gpt-4o-mini"
            config.llm.openai_temperature = 0.7
            config.llm.openai_max_tokens = None
            config.llm.timeout = 30
            mock_config.return_value = config

            # Mock OpenAI client
            with patch('src.services.llm_provider.OpenAI') as mock_openai_class:
                mock_client = Mock()
                mock_response = Mock()
                mock_response.choices = [Mock(message=Mock(content="Generated text"))]
                mock_client.chat.completions.create.return_value = mock_response
                mock_openai_class.return_value = mock_client

                # Test
                provider = OpenAIProvider()
                result = provider.generate("system", "user")

                assert result == "Generated text"
                mock_client.chat.completions.create.assert_called_once()


class TestGetLLMProvider:
    """Test provider factory function."""

    def test_get_mock_provider(self):
        """Test getting mock provider."""
        with patch('src.config.get_config') as mock_config:
            config = Mock()
            config.llm.provider = ProviderEnum.MOCK
            mock_config.return_value = config

            provider = get_llm_provider()
            assert isinstance(provider, MockProvider)

    @pytest.mark.skipif(not HAS_OPENAI, reason="openai package not installed")
    def test_get_openai_provider(self):
        """Test getting OpenAI provider."""
        with patch('src.config.get_config') as mock_config:
            config = Mock()
            config.llm.provider = ProviderEnum.OPENAI
            config.llm.openai_api_key = "sk-test-key"
            config.llm.openai_model = "gpt-4o-mini"
            config.llm.openai_temperature = 0.7
            config.llm.openai_max_tokens = None
            config.llm.timeout = 30
            mock_config.return_value = config

            with patch('src.services.llm_provider.OpenAI'):
                provider = get_llm_provider()
                assert isinstance(provider, OpenAIProvider)

    def test_get_cached_provider_fallback(self):
        """Test cached provider falls back to mock."""
        with patch('src.config.get_config') as mock_config:
            config = Mock()
            config.llm.provider = ProviderEnum.CACHED
            mock_config.return_value = config

            provider = get_llm_provider()
            # Should fall back to Mock since Cached not implemented
            assert isinstance(provider, MockProvider)

