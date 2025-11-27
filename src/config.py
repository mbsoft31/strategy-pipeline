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


