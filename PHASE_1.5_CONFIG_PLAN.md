# Phase 1.5: Configuration Management Enhancement

**Priority:** High (Foundation for Phases 2-4)  
**Status:** Ready to Implement  
**Estimated Duration:** 2-3 hours  
**Risk Level:** 🟢 Low (non-breaking change)

---

## Executive Summary

Upgrade from single `.env` file to a structured configuration system using **Pydantic Settings** (recommended over Dynaconf for better type safety and integration with existing Pydantic models).

This mini-phase addresses the configuration critique while setting up proper environment separation needed for CI/CD (Phase 3) and multi-environment deployment (Phase 5).

---

## Current State Analysis

### What We Have Now

```python
# Current: src/config.py
# Single flat configuration loaded from .env
# No environment separation
# Limited validation
```

**Issues:**
- ❌ No distinction between dev/test/prod
- ❌ Secrets mixed with non-secrets
- ❌ Hard to override for testing
- ❌ No validation beyond basic type checks
- ❌ CI/CD will struggle with environment-specific configs

### What We Need

```python
# Target: Structured, validated, environment-aware configuration
# - BaseSettings for common config
# - DevConfig, TestConfig, ProdConfig for environment-specific
# - Proper secrets management
# - Easy testing overrides
# - CI/CD ready
```

---

## Solution: Pydantic Settings v2

### Why Pydantic Settings?

| Feature | Pydantic Settings | Dynaconf | .env Only |
|---------|------------------|----------|-----------|
| **Type Safety** | ✅ Full | ⚠️ Partial | ❌ None |
| **Validation** | ✅ Built-in | ⚠️ Basic | ❌ None |
| **IDE Support** | ✅ Excellent | ⚠️ Limited | ❌ None |
| **Integration** | ✅ Native Pydantic | ⚠️ External | N/A |
| **Environment Separation** | ✅ Clean | ✅ Good | ❌ Manual |
| **Testing Overrides** | ✅ Easy | ✅ Good | ⚠️ Awkward |
| **Learning Curve** | 🟢 Low (we already use Pydantic) | 🟡 Medium | N/A |

**Decision:** Use **Pydantic Settings v2** for consistency with existing codebase.

---

## Implementation Plan

### Step 1: Install Dependencies (10 minutes)

```bash
# Add to requirements.txt
pydantic-settings>=2.0.0
python-dotenv>=1.0.0  # Already installed, but ensure version
```

### Step 2: Create New Configuration Structure (45 minutes)

**File: `src/config/settings.py`** (New)

```python
"""Enhanced configuration management using Pydantic Settings.

Supports multiple environments (dev, test, prod) with proper validation
and type safety.
"""

from enum import Enum
from pathlib import Path
from typing import Optional
from pydantic import Field, validator
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


class BaseConfig(BaseSettings):
    """Base configuration shared across all environments."""
    
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
    
    # Data storage
    data_dir: Path = Field(
        default=Path("./data"),
        description="Base directory for data storage"
    )
    
    # LLM Configuration
    llm_provider: LLMProvider = Field(
        default=LLMProvider.MOCK,
        description="LLM provider to use"
    )
    llm_model: Optional[str] = Field(
        default=None,
        description="Model name (provider-specific)"
    )
    llm_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature"
    )
    llm_max_tokens: int = Field(
        default=2000,
        ge=1,
        le=32000,
        description="Maximum tokens per generation"
    )
    
    # API Keys (loaded from env)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openrouter_api_key: Optional[str] = Field(
        default=None,
        description="OpenRouter API key"
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
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",  # No prefix for backward compatibility
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars
    )
    
    @validator("openai_api_key")
    def validate_openai_key(cls, v, values):
        """Validate OpenAI key if OpenAI provider is selected."""
        if values.get("llm_provider") == LLMProvider.OPENAI and not v:
            raise ValueError("openai_api_key is required when using OpenAI provider")
        return v
    
    @validator("openrouter_api_key")
    def validate_openrouter_key(cls, v, values):
        """Validate OpenRouter key if OpenRouter provider is selected."""
        if values.get("llm_provider") == LLMProvider.OPENROUTER and not v:
            raise ValueError("openrouter_api_key is required when using OpenRouter provider")
        return v


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # Dev-specific overrides
    llm_provider: LLMProvider = LLMProvider.MOCK  # Safe default for dev


class TestingConfig(BaseConfig):
    """Testing environment configuration."""
    
    environment: Environment = Environment.TESTING
    debug: bool = True
    
    # Test-specific overrides
    data_dir: Path = Path("./test_data")
    llm_provider: LLMProvider = LLMProvider.MOCK  # Always mock in tests
    
    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
        env_prefix="TEST_",
        case_sensitive=False,
    )


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    
    environment: Environment = Environment.PRODUCTION
    debug: bool = False
    
    # Production-specific overrides
    flask_secret_key: str = Field(
        ...,  # Required in production
        description="Flask session secret key (must be set!)"
    )
    
    @validator("flask_secret_key")
    def validate_production_secret(cls, v):
        """Ensure production secret is not default."""
        if "dev-secret" in v.lower() or "change" in v.lower():
            raise ValueError("Production secret key must be properly set!")
        return v


# Config factory
_config_cache: Optional[BaseConfig] = None


def get_config(force_reload: bool = False) -> BaseConfig:
    """Get configuration instance based on ENVIRONMENT variable.
    
    Args:
        force_reload: Force reloading config (useful for testing)
        
    Returns:
        Configuration instance for current environment
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


# Singleton instance (backward compatible)
config = get_config()
```

### Step 3: Create Environment Files (15 minutes)

**File: `.env.example`** (Update)

```env
# Environment
ENVIRONMENT=development

# LLM Provider Configuration
LLM_PROVIDER=mock
# LLM_PROVIDER=openai
# LLM_PROVIDER=openrouter

# LLM Settings
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# API Keys (set these for production)
# OPENAI_API_KEY=sk-proj-...
# OPENROUTER_API_KEY=sk-or-...

# Flask Settings
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_SECRET_KEY=dev-secret-key-change-in-production

# Data Storage
DATA_DIR=./data
```

**File: `.env.test`** (New)

```env
# Testing Environment
ENVIRONMENT=testing

# Force mock provider in tests
TEST_LLM_PROVIDER=mock
TEST_DATA_DIR=./test_data
TEST_FLASK_SECRET_KEY=test-secret-key

# No API keys needed for tests
```

**File: `.env.production.example`** (New)

```env
# Production Environment
ENVIRONMENT=production

# LLM Provider (set appropriately)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.7

# REQUIRED: Production API Keys
OPENAI_API_KEY=your-production-key-here

# REQUIRED: Production Secret
FLASK_SECRET_KEY=your-secure-random-string-here

# Production Settings
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
DATA_DIR=/var/data/strategy-pipeline

# Optional: Performance tuning
LLM_MAX_TOKENS=4000
```

### Step 4: Update Existing Code (30 minutes)

**Backward Compatible Migration:**

1. **Update imports across codebase:**

```python
# OLD
from src.config import config

# NEW (same import, different implementation)
from src.config.settings import config

# For advanced usage
from src.config.settings import get_config, DevelopmentConfig
```

2. **Update `src/config.py` to redirect (for backward compatibility):**

```python
"""Configuration module - redirects to new settings system.

DEPRECATED: This file exists for backward compatibility.
New code should import from src.config.settings directly.
"""

from .config.settings import (
    config,
    get_config,
    BaseConfig,
    DevelopmentConfig,
    TestingConfig,
    ProductionConfig,
    Environment,
    LLMProvider,
)

__all__ = [
    "config",
    "get_config",
    "BaseConfig",
    "DevelopmentConfig",
    "TestingConfig",
    "ProductionConfig",
    "Environment",
    "LLMProvider",
]
```

### Step 5: Update Tests (30 minutes)

**Create: `tests/config/test_settings.py`**

```python
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
)


class TestConfigurationSystem:
    """Test suite for configuration management."""
    
    def test_development_config_defaults(self):
        """Test development config has correct defaults."""
        config = DevelopmentConfig()
        
        assert config.environment == Environment.DEVELOPMENT
        assert config.debug is True
        assert config.llm_provider == LLMProvider.MOCK
        assert config.data_dir == Path("./data")
    
    def test_testing_config_overrides(self):
        """Test testing config overrides appropriately."""
        config = TestingConfig()
        
        assert config.environment == Environment.TESTING
        assert config.llm_provider == LLMProvider.MOCK  # Always mock
        assert config.data_dir == Path("./test_data")
    
    def test_production_config_validation(self):
        """Test production config validates secrets."""
        with pytest.raises(ValueError, match="secret"):
            # Should fail with default dev secret
            ProductionConfig(flask_secret_key="dev-secret-key")
    
    def test_openai_key_validation(self):
        """Test OpenAI key required when using OpenAI."""
        with pytest.raises(ValueError, match="openai_api_key"):
            DevelopmentConfig(
                llm_provider=LLMProvider.OPENAI,
                openai_api_key=None
            )
    
    def test_config_factory_caching(self):
        """Test get_config caches instance."""
        config1 = get_config()
        config2 = get_config()
        
        assert config1 is config2  # Same instance
    
    def test_config_factory_reload(self):
        """Test force_reload creates new instance."""
        config1 = get_config()
        config2 = get_config(force_reload=True)
        
        # May or may not be same object depending on env,
        # but should both be valid configs
        assert isinstance(config1, BaseConfig)
        assert isinstance(config2, BaseConfig)
    
    def test_environment_variable_override(self, monkeypatch):
        """Test environment variables override defaults."""
        monkeypatch.setenv("LLM_TEMPERATURE", "0.5")
        monkeypatch.setenv("LLM_MAX_TOKENS", "1000")
        
        config = DevelopmentConfig()
        
        assert config.llm_temperature == 0.5
        assert config.llm_max_tokens == 1000
```

### Step 6: Update Documentation (20 minutes)

**Update README.md:**

```markdown
## 🔧 Configuration

The project uses environment-based configuration with Pydantic Settings.

### Quick Start

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings (API keys, preferences, etc.)

3. Run the application:
```bash
python main.py  # Uses development config by default
```

### Environments

The system supports three environments:

- **Development** (`ENVIRONMENT=development`) - Default, uses mock LLM
- **Testing** (`ENVIRONMENT=testing`) - Always uses mock, isolated data
- **Production** (`ENVIRONMENT=production`) - Requires real API keys

### Configuration Files

| File | Purpose | Committed? |
|------|---------|------------|
| `.env` | Local development config | ❌ No (gitignored) |
| `.env.example` | Template with all options | ✅ Yes |
| `.env.test` | Testing environment config | ✅ Yes |
| `.env.production.example` | Production template | ✅ Yes |

### Environment Variables

Key settings you can configure:

```env
# Core Settings
ENVIRONMENT=development          # development, testing, or production
LLM_PROVIDER=mock               # mock, openai, or openrouter
LLM_MODEL=gpt-4o-mini           # Model name
LLM_TEMPERATURE=0.7             # Sampling temperature (0.0-2.0)

# API Keys
OPENAI_API_KEY=sk-proj-...      # Required for openai provider
OPENROUTER_API_KEY=sk-or-...    # Required for openrouter provider

# Flask
FLASK_HOST=127.0.0.1            # Server host
FLASK_PORT=5000                 # Server port
FLASK_SECRET_KEY=your-secret    # Session secret (change in production!)

# Storage
DATA_DIR=./data                 # Data storage directory
```

### Programmatic Access

```python
from src.config.settings import config, get_config

# Use singleton (recommended)
print(config.llm_provider)
print(config.data_dir)

# Get fresh instance
new_config = get_config(force_reload=True)

# Access environment-specific config
from src.config.settings import DevelopmentConfig
dev_config = DevelopmentConfig()
```

### Testing with Different Configs

```python
import pytest
from src.config.settings import TestingConfig

def test_something():
    config = TestingConfig(
        llm_provider="mock",  # Override for this test
        data_dir="./temp_test_data"
    )
    # Test with custom config...
```
```

---

## Migration Checklist

### Phase A: Setup (30 min)
- [ ] Install `pydantic-settings>=2.0.0`
- [ ] Create `src/config/` directory
- [ ] Create `src/config/__init__.py`
- [ ] Create `src/config/settings.py` with new config system
- [ ] Create environment files (`.env.test`, `.env.production.example`)
- [ ] Update `.env.example` with all new options

### Phase B: Backward Compatibility (30 min)
- [ ] Update `src/config.py` to redirect to new system
- [ ] Test that existing imports still work
- [ ] Verify `from src.config import config` still functions

### Phase C: Testing (40 min)
- [ ] Create `tests/config/` directory
- [ ] Create `tests/config/__init__.py`
- [ ] Create `tests/config/test_settings.py`
- [ ] Write 10+ tests for config system
- [ ] Run full test suite to ensure no breaks

### Phase D: Documentation (20 min)
- [ ] Update README.md with configuration section
- [ ] Add migration notes to CHANGELOG
- [ ] Document environment variables
- [ ] Add examples for each environment

### Phase E: Validation (20 min)
- [ ] Test development environment
- [ ] Test with mock provider
- [ ] Test with environment variable overrides
- [ ] Test production config validation
- [ ] Verify existing code still works

---

## Benefits

### Immediate Benefits ✅
1. **Type Safety** - All configs validated at startup
2. **Environment Separation** - Clear dev/test/prod boundaries
3. **Better Testing** - Easy to override configs in tests
4. **IDE Support** - Autocomplete for all settings
5. **Validation** - Catch config errors early

### Future Benefits 🚀
1. **CI/CD Ready** - Easy to set different configs per environment
2. **Secrets Management** - Clear separation of secrets vs config
3. **Multi-Region** - Easy to add region-specific configs
4. **Feature Flags** - Can add feature toggles easily
5. **Monitoring** - Can add observability configs

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Breaking existing code | 🟢 Low | 🟡 Medium | Backward compatibility layer |
| Config validation too strict | 🟡 Medium | 🟢 Low | Allow overrides in dev |
| Migration complexity | 🟢 Low | 🟢 Low | Incremental migration |
| Test failures | 🟡 Medium | 🟡 Medium | Comprehensive testing |

**Overall Risk:** 🟢 **LOW** - Backward compatibility makes this safe

---

## Success Criteria

- [ ] All existing tests pass without modification
- [ ] New config tests achieve 100% coverage
- [ ] Can switch between dev/test/prod environments
- [ ] Production config validates secrets properly
- [ ] Documentation is clear and complete
- [ ] Zero breaking changes to existing code

---

## Timeline

| Task | Duration | Cumulative |
|------|----------|------------|
| Install & Setup | 30 min | 30 min |
| Create Config System | 45 min | 1h 15m |
| Environment Files | 15 min | 1h 30m |
| Update Existing Code | 30 min | 2h |
| Write Tests | 40 min | 2h 40m |
| Documentation | 20 min | 3h |
| **TOTAL** | **3 hours** | **3 hours** |

---

## Next Steps After Completion

Once this phase is complete:

1. ✅ **Configuration management** - COMPLETE
2. ⏳ **Phase 2: Frontend Testing** - Use new config for test setup
3. ⏳ **Phase 3: CI/CD Pipeline** - Leverage environment configs
4. ⏳ **Phase 4: UI Strategy Cleanup** - Cleaner environment separation

---

**This phase sets a solid foundation for professional deployment and testing!**

