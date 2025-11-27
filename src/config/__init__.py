"""Configuration module for Strategy Pipeline.

This module provides environment-aware configuration management.
"""

from .settings import (
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

# Backward compatibility alias
PipelineConfig = BaseConfig

__all__ = [
    "config",
    "get_config",
    "BaseConfig",
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
    "PipelineConfig",  # Backward compatibility
    "Environment",
    "LLMProvider",
    "LogLevel",
    "LLMConfig",
    "ValidationConfig",
]

