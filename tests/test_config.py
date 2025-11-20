"""Tests for configuration system."""

import os
import tempfile
from pathlib import Path

import pytest

from src.config import LLMProvider, PipelineConfig, get_config, reload_config


def test_default_config():
    """Test default configuration values."""
    config = PipelineConfig()

    assert config.environment == "development"
    assert config.llm.provider == LLMProvider.MOCK
    assert config.llm.rate_limit == 10.0
    assert config.validation.openalex_rate_limit == 9.0


def test_config_from_env(monkeypatch):
    """Test configuration loading from environment variables."""
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("LLM__PROVIDER", "openai")
    monkeypatch.setenv("LLM__OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("LLM__RATE_LIMIT", "5.0")

    config = PipelineConfig()

    assert config.environment == "production"
    assert config.llm.provider == LLMProvider.OPENAI
    assert config.llm.openai_api_key == "test-key"
    assert config.llm.rate_limit == 5.0


def test_openai_key_required_for_openai_provider(monkeypatch):
    """Test that OpenAI key is required when using OpenAI provider."""
    monkeypatch.setenv("LLM__PROVIDER", "openai")
    monkeypatch.delenv("LLM__OPENAI_API_KEY", raising=False)

    with pytest.raises(ValueError, match="openai_api_key is required"):
        PipelineConfig()


def test_data_dir_creation():
    """Test that data directory is created."""
    with tempfile.TemporaryDirectory() as tmpdir:
        data_path = Path(tmpdir) / "test_data"
        config = PipelineConfig(data_dir=data_path)

        assert config.data_dir.exists()
        assert config.data_dir.is_dir()


def test_global_config_singleton():
    """Test global config singleton behavior."""
    config1 = get_config()
    config2 = get_config()

    assert config1 is config2


def test_config_reload(monkeypatch):
    """Test configuration reload."""
    config1 = get_config()
    original_provider = config1.llm.provider

    # Change environment
    monkeypatch.setenv("LLM__PROVIDER", "cached")

    config2 = reload_config()

    assert config2.llm.provider == LLMProvider.CACHED
    assert config2.llm.provider != original_provider

