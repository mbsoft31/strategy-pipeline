"""Configuration module - DEPRECATED redirect to new settings system.

DEPRECATED: This file exists for backward compatibility only.
New code should import from src.config.settings directly.

The configuration system has been enhanced with environment-aware settings:
- Development, Testing, and Production environments
- Proper validation and type safety
- Secrets management
- Easy testing overrides

Migration:
    OLD: from src.config import config
    NEW: from src.config.settings import config  # (or just use this file, it redirects)

All existing imports will continue to work unchanged.
"""

# Import everything from new settings module
from .config.settings import (
    config,
    get_config,
    BaseConfig,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    Environment,
    LLMProvider,
    LogLevel,
    LLMConfig,
    ValidationConfig,
)

# For backward compatibility, create PipelineConfig as alias to BaseConfig
PipelineConfig = BaseConfig

# Export everything for backward compatibility
__all__ = [
    "config",
    "get_config",
    "PipelineConfig",  # Backward compatibility
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

