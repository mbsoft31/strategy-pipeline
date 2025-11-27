"""Enhanced configuration management using Pydantic Settings v2.

This module provides environment-aware configuration with proper validation,
type safety, and support for dev/test/prod environments.

Architecture:
- BaseConfig: Shared configuration across all environments
- DevelopmentConfig: Development-specific settings
- TestingConfig: Testing-specific settings
- ProductionConfig: Production-specific settings with strict validation
- get_config(): Factory function that returns appropriate config based on ENVIRONMENT

Usage:
    >>> from src.config.settings import config
    >>> print(config.llm.provider)
    >>> print(config.data_dir)
"""

from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Supported deployment environments."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    MOCK = "mock"
    OPENAI = "openai"
    OPENROUTER = "openrouter"
    CACHED = "cached"


class LogLevel(str, Enum):
    """Logging level options."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LLMConfig(BaseSettings):
    """LLM provider configuration with validation."""

    model_config = SettingsConfigDict(
        extra="ignore",  # Ignore extra fields from environment
    )

    # Provider selection
    provider: LLMProvider = Field(
        default=LLMProvider.MOCK,
        description="LLM provider to use"
    )

    # Model settings
    model: str = Field(
        default="gpt-4o-mini",
        description="Model name (provider-specific)"
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature"
    )
    max_tokens: Optional[int] = Field(
        default=2000,
        description="Maximum tokens per generation"
    )

    # API Keys
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openrouter_api_key: Optional[str] = Field(
        default=None,
        description="OpenRouter API key"
    )
    openai_base_url: Optional[str] = Field(
        default=None,
        description="Custom base URL (for OpenRouter)"
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
        description="Burst capacity"
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
        description="Initial retry delay (seconds)"
    )
    retry_max_delay: float = Field(
        default=60.0,
        gt=0,
        description="Maximum retry delay (seconds)"
    )

    # Timeout
    timeout: int = Field(
        default=30,
        gt=0,
        le=300,
        description="Request timeout (seconds)"
    )

    # Cache settings
    cache_dir: Path = Field(
        default=Path(".cache/llm"),
        description="Cache directory for responses"
    )
    cache_enabled: bool = Field(
        default=False,
        description="Enable response caching"
    )

    @field_validator("openai_api_key")
    @classmethod
    def validate_openai_key(cls, v: Optional[str], info) -> Optional[str]:
        """Validate OpenAI key when using OpenAI provider."""
        provider = info.data.get("provider")
        if provider == LLMProvider.OPENAI and not v:
            raise ValueError(
                "openai_api_key is required when provider='openai'"
            )
        return v

    @field_validator("openrouter_api_key")
    @classmethod
    def validate_openrouter_key(cls, v: Optional[str], info) -> Optional[str]:
        """Validate OpenRouter key when using OpenRouter provider."""
        provider = info.data.get("provider")
        if provider == LLMProvider.OPENROUTER and not v:
            raise ValueError(
                "openrouter_api_key is required when provider='openrouter'"
            )
        return v


class ValidationConfig(BaseSettings):
    """Configuration for validation services."""

    model_config = SettingsConfigDict(
        extra="ignore",
    )

    # OpenAlex settings
    openalex_mailto: Optional[str] = Field(
        default=None,
        description="Email for polite OpenAlex requests"
    )
    openalex_rate_limit: float = Field(
        default=9.0,
        gt=0,
        le=10,
        description="OpenAlex requests per second"
    )
    openalex_timeout: int = Field(
        default=30,
        gt=0,
        description="OpenAlex request timeout"
    )
    openalex_cache_enabled: bool = Field(
        default=True,
        description="Enable OpenAlex response caching"
    )
    openalex_cache_ttl: int = Field(
        default=86400,  # 24 hours
        description="Cache TTL in seconds"
    )


class BaseConfig(BaseSettings):
    """Base configuration shared across all environments."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Current deployment environment"
    )

    # Project settings
    project_name: str = Field(
        default="Strategy Pipeline",
        description="Project display name"
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Logging level"
    )

    # Data storage
    data_dir: Path = Field(
        default=Path("./data"),
        description="Base directory for data storage"
    )

    # Flask settings
    flask_host: str = Field(
        default="127.0.0.1",
        description="Flask server host"
    )
    flask_port: int = Field(
        default=5000,
        ge=1,
        le=65535,
        description="Flask server port"
    )
    flask_secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Flask session secret key"
    )

    # Error handling
    fail_on_llm_error: bool = Field(
        default=True,
        description="Fail fast on LLM errors"
    )

    # Sub-configurations
    llm: LLMConfig = Field(default_factory=LLMConfig)
    validation: ValidationConfig = Field(default_factory=ValidationConfig)


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""

    # Force environment-specific values
    environment: Environment = Field(default=Environment.DEVELOPMENT)
    debug: bool = Field(default=True)
    log_level: LogLevel = Field(default=LogLevel.DEBUG)

    def __init__(self, **kwargs):
        # Set dev defaults before parent init
        if 'environment' not in kwargs:
            kwargs['environment'] = Environment.DEVELOPMENT
        if 'debug' not in kwargs:
            kwargs['debug'] = True
        if 'log_level' not in kwargs:
            kwargs['log_level'] = LogLevel.DEBUG

        # Create mock LLM config if not provided
        if 'llm' not in kwargs:
            # Get llm params from kwargs
            llm_params = {k.replace('llm__', ''): v
                         for k, v in kwargs.items()
                         if k.startswith('llm__')}
            if 'provider' not in llm_params:
                llm_params['provider'] = LLMProvider.MOCK
            kwargs['llm'] = LLMConfig(**llm_params)

        super().__init__(**kwargs)


class TestingConfig(BaseConfig):
    """Testing environment configuration."""

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        env_prefix="TEST_",
        case_sensitive=False,
        extra="ignore",
    )

    # Force environment-specific values
    environment: Environment = Field(default=Environment.TESTING)
    debug: bool = Field(default=True)
    log_level: LogLevel = Field(default=LogLevel.DEBUG)
    data_dir: Path = Field(default=Path("./test_data"))
    flask_secret_key: str = Field(default="test-secret-key")

    def __init__(self, **kwargs):
        # Set test defaults
        if 'environment' not in kwargs:
            kwargs['environment'] = Environment.TESTING
        if 'debug' not in kwargs:
            kwargs['debug'] = True
        if 'log_level' not in kwargs:
            kwargs['log_level'] = LogLevel.DEBUG
        if 'data_dir' not in kwargs:
            kwargs['data_dir'] = Path("./test_data")
        if 'flask_secret_key' not in kwargs:
            kwargs['flask_secret_key'] = "test-secret-key"

        # Always use mock in tests
        if 'llm' not in kwargs:
            llm_params = {k.replace('llm__', '').replace('test_llm__', ''): v
                         for k, v in kwargs.items()
                         if k.startswith(('llm__', 'test_llm__'))}
            llm_params['provider'] = LLMProvider.MOCK  # Force mock
            kwargs['llm'] = LLMConfig(**llm_params)

        super().__init__(**kwargs)


class ProductionConfig(BaseConfig):
    """Production environment configuration with strict validation."""

    # Force environment-specific values
    environment: Environment = Field(default=Environment.PRODUCTION)
    debug: bool = Field(default=False)
    log_level: LogLevel = Field(default=LogLevel.WARNING)

    # Production requires proper secret
    flask_secret_key: str = Field(
        ...,  # Required
        description="Flask session secret key (MUST be set in production!)"
    )

    def __init__(self, **kwargs):
        # Set production defaults
        if 'environment' not in kwargs:
            kwargs['environment'] = Environment.PRODUCTION
        if 'debug' not in kwargs:
            kwargs['debug'] = False
        if 'log_level' not in kwargs:
            kwargs['log_level'] = LogLevel.WARNING

        super().__init__(**kwargs)

    @field_validator("flask_secret_key")
    @classmethod
    def validate_production_secret(cls, v: str) -> str:
        """Ensure production secret is not a default/dev value."""
        forbidden = ["dev", "test", "change", "secret-key", "example"]
        if any(word in v.lower() for word in forbidden):
            raise ValueError(
                "Production flask_secret_key must be a secure random string! "
                f"Current value looks like a default: {v[:20]}..."
            )
        if len(v) < 32:
            raise ValueError(
                "Production flask_secret_key must be at least 32 characters"
            )
        return v


# Config factory and singleton
_config_cache: Optional[BaseConfig] = None


def get_config(force_reload: bool = False) -> BaseConfig:
    """Get configuration instance based on ENVIRONMENT variable.

    This function caches the config instance for performance. Use force_reload=True
    in tests to get a fresh instance.

    Args:
        force_reload: Force reloading config (useful for testing)

    Returns:
        Configuration instance for current environment

    Example:
        >>> config = get_config()
        >>> print(config.environment)
        >>> print(config.llm.provider)
    """
    global _config_cache

    if _config_cache is not None and not force_reload:
        return _config_cache

    import os
    env = os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "production": ProductionConfig,
    }

    config_class = config_map.get(env, DevelopmentConfig)
    _config_cache = config_class()

    return _config_cache


# Singleton instance for backward compatibility
config = get_config()


# Export all for convenience
__all__ = [
    "config",
    "get_config",
    "BaseConfig",
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
    "Environment",
    "LLMProvider",
    "LogLevel",
    "LLMConfig",
    "ValidationConfig",
]

