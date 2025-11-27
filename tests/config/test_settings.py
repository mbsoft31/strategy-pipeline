"""Tests for enhanced configuration system."""

import pytest
import os
from pathlib import Path
from src.config.settings import (
    get_config,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    Environment,
    LLMProvider,
    LogLevel,
    LLMConfig,
)


class TestConfigurationSystem:
    """Test suite for configuration management."""

    def test_development_config_defaults(self):
        """Test development config has correct defaults."""
        config = DevelopmentConfig()

        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.log_level == LogLevel.DEBUG
        assert config.llm.provider == LLMProvider.MOCK
        assert config.data_dir == Path("./data")
        assert config.flask_port == 5000

    def test_testing_config_overrides(self):
        """Test testing config overrides appropriately."""
        config = TestingConfig()

        assert config.environment == Environment.TESTING
        assert config.debug is True
        assert config.llm.provider == LLMProvider.MOCK  # Always mock in tests
        assert config.data_dir == Path("./test_data")
        assert config.flask_secret_key == "test-secret-key"

    def test_production_config_requires_secure_secret(self):
        """Test production config validates secrets."""
        # Should fail with default dev secret
        with pytest.raises(ValueError, match="secure random string"):
            ProductionConfig(flask_secret_key="dev-secret-key")

        # Should fail with "change" in the name
        with pytest.raises(ValueError, match="secure random string"):
            ProductionConfig(flask_secret_key="please-change-this")

        # Should fail if too short
        with pytest.raises(ValueError, match="at least 32 characters"):
            ProductionConfig(flask_secret_key="short")

    def test_production_config_accepts_secure_secret(self):
        """Test production config accepts properly generated secret."""
        import secrets
        secure_key = secrets.token_hex(32)  # 64 character hex string

        config = ProductionConfig(flask_secret_key=secure_key)

        assert config.environment == Environment.PRODUCTION
        assert config.debug is False
        assert config.flask_secret_key == secure_key

    def test_llm_openai_key_validation(self):
        """Test OpenAI key required when using OpenAI provider."""
        with pytest.raises(ValueError, match="openai_api_key"):
            LLMConfig(
                provider=LLMProvider.OPENAI,
                openai_api_key=None
            )

    def test_llm_openai_key_not_required_for_mock(self):
        """Test OpenAI key not required when using mock provider."""
        config = LLMConfig(
            provider=LLMProvider.MOCK,
            openai_api_key=None
        )

        assert config.provider == LLMProvider.MOCK
        assert config.openai_api_key is None

    def test_llm_openrouter_key_validation(self):
        """Test OpenRouter key required when using OpenRouter provider."""
        with pytest.raises(ValueError, match="openrouter_api_key"):
            LLMConfig(
                provider=LLMProvider.OPENROUTER,
                openrouter_api_key=None
            )

    def test_config_factory_returns_dev_by_default(self, monkeypatch):
        """Test get_config returns DevelopmentConfig by default."""
        monkeypatch.delenv("ENVIRONMENT", raising=False)

        config = get_config(force_reload=True)

        assert isinstance(config, DevelopmentConfig)
        assert config.environment == Environment.DEVELOPMENT

    def test_config_factory_respects_environment_var(self, monkeypatch):
        """Test get_config respects ENVIRONMENT variable."""
        monkeypatch.setenv("ENVIRONMENT", "testing")

        config = get_config(force_reload=True)

        assert isinstance(config, TestingConfig)
        assert config.environment == Environment.TESTING

    def test_config_factory_caches_instance(self):
        """Test get_config caches instance."""
        config1 = get_config()
        config2 = get_config()

        assert config1 is config2  # Same instance

    def test_config_factory_force_reload(self):
        """Test force_reload creates new instance."""
        config1 = get_config()
        config2 = get_config(force_reload=True)

        # Both should be valid configs
        assert isinstance(config1, (DevelopmentConfig, TestingConfig, ProductionConfig))
        assert isinstance(config2, (DevelopmentConfig, TestingConfig, ProductionConfig))

    def test_environment_variable_overrides(self, monkeypatch):
        """Test environment variables override defaults."""
        monkeypatch.setenv("LLM__TEMPERATURE", "0.5")
        monkeypatch.setenv("LLM__MAX_TOKENS", "1000")
        monkeypatch.setenv("DATA_DIR", "./custom_data")

        config = DevelopmentConfig()

        assert config.llm.temperature == 0.5
        assert config.llm.max_tokens == 1000
        assert config.data_dir == Path("./custom_data")

    def test_nested_config_delimiter(self, monkeypatch):
        """Test nested configuration with double underscore delimiter."""
        monkeypatch.setenv("LLM__RATE_LIMIT", "5.0")
        monkeypatch.setenv("LLM__MAX_RETRIES", "5")

        config = DevelopmentConfig()

        assert config.llm.rate_limit == 5.0
        assert config.llm.max_retries == 5

    def test_validation_config_defaults(self):
        """Test validation config has sensible defaults."""
        config = DevelopmentConfig()

        assert config.validation.openalex_rate_limit == 9.0
        assert config.validation.openalex_cache_enabled is True
        assert config.validation.openalex_cache_ttl == 86400

    def test_path_fields_convert_to_path_objects(self):
        """Test that path fields are converted to Path objects."""
        config = DevelopmentConfig()

        assert isinstance(config.data_dir, Path)
        assert isinstance(config.llm.cache_dir, Path)

    def test_llm_temperature_validation(self):
        """Test LLM temperature must be in valid range."""
        # Too low
        with pytest.raises(ValueError):
            LLMConfig(temperature=-0.1)

        # Too high
        with pytest.raises(ValueError):
            LLMConfig(temperature=2.1)

        # Valid values
        config1 = LLMConfig(temperature=0.0)
        config2 = LLMConfig(temperature=2.0)
        assert config1.temperature == 0.0
        assert config2.temperature == 2.0

    def test_flask_port_validation(self):
        """Test Flask port must be in valid range."""
        # Too low
        with pytest.raises(ValueError):
            DevelopmentConfig(flask_port=0)

        # Too high
        with pytest.raises(ValueError):
            DevelopmentConfig(flask_port=70000)

        # Valid
        config = DevelopmentConfig(flask_port=8080)
        assert config.flask_port == 8080


class TestBackwardCompatibility:
    """Test backward compatibility with old config system."""

    def test_old_import_still_works(self):
        """Test importing from src.config still works."""
        from src.config import config, LLMProvider, Environment

        assert config is not None
        assert hasattr(config, 'llm')
        assert hasattr(config, 'data_dir')

    def test_old_pipeline_config_alias_works(self):
        """Test PipelineConfig alias for backward compatibility."""
        from src.config import PipelineConfig

        # Should be an alias to BaseConfig
        from src.config.settings import BaseConfig
        assert PipelineConfig is BaseConfig

    def test_config_singleton_accessible(self):
        """Test config singleton is accessible from both old and new paths."""
        from src.config import config as old_config
        from src.config.settings import config as new_config

        # Should be the same instance
        assert old_config is new_config


class TestConfigUsagePatterns:
    """Test common usage patterns for configuration."""

    def test_override_config_for_testing(self):
        """Test overriding config values for testing."""
        config = TestingConfig(
            data_dir="./temp_test_data",
            llm__provider=LLMProvider.MOCK,
            llm__temperature=0.5,
        )

        assert config.data_dir == Path("./temp_test_data")
        assert config.llm.provider == LLMProvider.MOCK
        assert config.llm.temperature == 0.5

    def test_access_nested_config(self):
        """Test accessing nested configuration."""
        config = DevelopmentConfig()

        # Direct access
        assert config.llm.provider == LLMProvider.MOCK
        assert config.llm.temperature == 0.7
        assert config.validation.openalex_rate_limit == 9.0

    def test_config_to_dict_works(self):
        """Test configuration can be converted to dict if needed."""
        config = DevelopmentConfig()

        # model_dump() is the Pydantic v2 method
        config_dict = config.model_dump()

        assert isinstance(config_dict, dict)
        assert 'environment' in config_dict
        assert 'llm' in config_dict
        assert config_dict['environment'] == 'development'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

