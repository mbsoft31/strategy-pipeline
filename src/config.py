"""Configuration management for HITL Research Strategy Pipeline.

This module provides configuration models and utilities for loading
and validating configuration from .env files and environment variables.

Configuration priority (highest to lowest):
1. Environment variables
2. .env file
3. Default values
"""

from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Available LLM provider options."""
    OPENAI = "openai"
    MOCK = "mock"
    CACHED = "cached"  # For testing without API calls


class LogLevel(str, Enum):
    """Logging level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LLMConfig(BaseSettings):
    """LLM provider configuration."""

    # Provider selection
    provider: LLMProvider = Field(
        default=LLMProvider.MOCK,
        description="LLM provider to use"
    )

    # OpenAI settings
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model name"
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for generation"
    )
    openai_max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens for completion"
    )

    # Rate limiting
    rate_limit: float = Field(
        default=10.0,
        gt=0,
        le=100,
        description="Requests per second"
    )
    rate_limit_burst: int = Field(
        default=20,
        gt=0,
        description="Burst capacity (tokens)"
    )

    # Retry settings
    max_retries: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum retry attempts"
    )
    retry_base_delay: float = Field(
        default=1.0,
        gt=0,
        description="Initial retry delay in seconds"
    )
    retry_max_delay: float = Field(
        default=60.0,
        gt=0,
        description="Maximum retry delay in seconds"
    )

    # Timeout
    timeout: int = Field(
        default=30,
        gt=0,
        le=300,
        description="Request timeout in seconds"
    )

    # Cache settings (for CachedProvider)
    cache_dir: Path = Field(
        default=Path(".cache/llm"),
        description="Cache directory for LLM responses"
    )
    cache_enabled: bool = Field(
        default=False,
        description="Enable response caching"
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: Optional[str], info) -> Optional[str]:
        """Validate OpenAI API key when using OpenAI provider."""
        provider = info.data.get("provider")
        if provider == LLMProvider.OPENAI and not v:
            raise ValueError(
                "openai_api_key is required when provider='openai'. "
                "Set OPENAI_API_KEY environment variable or in .env file."
            )
        return v


class ValidationConfig(BaseSettings):
    """Configuration for validation services (e.g., OpenAlex)."""

    # OpenAlex settings
    openalex_mailto: Optional[str] = Field(
        default=None,
        description="Email for polite OpenAlex requests (recommended)"
    )
    openalex_rate_limit: float = Field(
        default=9.0,
        gt=0,
        le=10,
        description="OpenAlex requests per second (9 for polite pool)"
    )
    openalex_timeout: int = Field(
        default=30,
        gt=0,
        description="OpenAlex request timeout"
    )
    openalex_cache_enabled: bool = Field(
        default=True,
        description="Enable caching for OpenAlex responses"
    )
    openalex_cache_ttl: int = Field(
        default=86400,  # 24 hours
        description="Cache TTL in seconds"
    )


class PipelineConfig(BaseSettings):
    """Main pipeline configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: str = Field(
        default="development",
        description="Environment: development, production, testing"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )

    # Paths
    data_dir: Path = Field(
        default=Path("./data"),
        description="Base directory for project data"
    )

    # Error handling
    fail_on_llm_error: bool = Field(
        default=True,
        description="Fail fast on LLM errors vs graceful degradation"
    )

    # Sub-configurations
    llm: LLMConfig = Field(default_factory=LLMConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.llm.cache_enabled:
            self.llm.cache_dir.mkdir(parents=True, exist_ok=True)


# Global configuration instance
_config: Optional[PipelineConfig] = None


def get_config() -> PipelineConfig:
    """Get the global configuration instance.

    Returns:
        PipelineConfig instance

    Example:
        >>> from src.config import get_config
        >>> config = get_config()
        >>> print(config.llm.provider)
    """
    global _config
    if _config is None:
        _config = PipelineConfig()
    return _config


def reload_config() -> PipelineConfig:
    """Reload configuration from environment.

    Useful for testing or when environment changes.

    Returns:
        New PipelineConfig instance
    """
    global _config
    _config = PipelineConfig()
    return _config

