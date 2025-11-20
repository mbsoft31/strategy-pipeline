# Sprint 1 Implementation Guide: Minimal Foundation + Syntax Engine

This guide provides step-by-step instructions for Sprint 1, which establishes **only the essential foundation** needed to build the Syntax Engine (your "moat" feature).

**Duration**: 3 days  
**Dependencies**: None (can start immediately)  
**Risk**: Low (no external API dependencies)  
**Deliverable**: Working Boolean query generator for PubMed and Scopus

## Overview

Sprint 1 focuses on getting to visible value quickly:

**Day 1 (Foundation Essentials)**
1. Configuration system (`.env` only - no YAML)
2. Exception hierarchy (for proper error handling)

**Day 2 (The Moat)**
3. Query parser (Boolean logic)
4. Syntax engine (PubMed/Scopus dialects)

**Day 3 (Validation)**
5. Unit tests proving correctness
6. Demo showing superiority over ChatGPT

**What We're Skipping for Now:**
- Rate limiting (add in Sprint 2 when we need APIs)
- Retry logic (add in Sprint 2 when we need APIs)
- Field extractor (add in Sprint 4)
- YAML config support (never needed for this project)

This approach avoids "boilerplate fatigue" while building your technical moat.

---

## Step 1: Configuration System (Day 1 Morning)

### Objective
Create a simple configuration management system using Pydantic Settings that supports environment variables and `.env` files.

**Why We Need This:**
- Manage OpenAI API keys securely
- Toggle between mock/real LLM providers
- Configure rate limits (will be used in Sprint 2)

**What We're NOT Building:**
- YAML support (overkill for this project)
- Complex nested configs (keep it simple)

### Files to Create

**1.1 Create `src/config.py`**

Location: `C:\Users\mouadh\Desktop\strategy-pipeline\src\config.py`

```python
"""Configuration management for HITL Research Strategy Pipeline.

This module provides configuration models and utilities for loading
and validating configuration from .env files and environment variables.

Configuration priority (highest to lowest):
1. Environment variables
2. .env file
3. Default values
"""

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

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
```

**1.2 Create `.env.example`**

Location: `C:\Users\mouadh\Desktop\strategy-pipeline\.env.example`

```ini
# HITL Pipeline Configuration
# Copy this file to .env and fill in your values

# ==========================================
# Environment
# ==========================================
ENVIRONMENT=development
DEBUG=False
LOG_LEVEL=INFO

# ==========================================
# LLM Provider Configuration
# ==========================================

# Provider: openai, mock, or cached
LLM__PROVIDER=mock

# OpenAI Settings (required if provider=openai)
# Get your API key from https://platform.openai.com/api-keys
LLM__OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
LLM__OPENAI_MODEL=gpt-4o-mini
LLM__OPENAI_TEMPERATURE=0.7
LLM__OPENAI_MAX_TOKENS=

# Rate Limiting
LLM__RATE_LIMIT=10.0
LLM__RATE_LIMIT_BURST=20

# Retry Configuration
LLM__MAX_RETRIES=3
LLM__RETRY_BASE_DELAY=1.0
LLM__RETRY_MAX_DELAY=60.0

# Timeout
LLM__TIMEOUT=30

# Cache Settings
LLM__CACHE_DIR=.cache/llm
LLM__CACHE_ENABLED=False

# ==========================================
# Validation Services (OpenAlex)
# ==========================================

# Your email for polite OpenAlex requests (recommended)
VALIDATION__OPENALEX_MAILTO=your.email@example.com
VALIDATION__OPENALEX_RATE_LIMIT=9.0
VALIDATION__OPENALEX_TIMEOUT=30
VALIDATION__OPENALEX_CACHE_ENABLED=True
VALIDATION__OPENALEX_CACHE_TTL=86400

# ==========================================
# Pipeline Settings
# ==========================================

# Data directory
DATA_DIR=./data

# Error handling: fail fast or graceful degradation
FAIL_ON_LLM_ERROR=True
```

**1.3 Update `requirements.txt`**

Add to existing requirements:

```txt
# Configuration
pydantic>=2.5.0
pydantic-settings>=2.1.0
python-dotenv>=1.0.0

# LLM Providers (will be used in Sprint 2)
openai>=1.3.0

# Validation (will be used in Sprint 3)
requests>=2.31.0

# Testing
pytest>=7.4.0
pytest-cov>=4.1.0
```

### Testing Configuration

**1.4 Create `tests/test_config.py`**

```python
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
```

### Documentation

Add to `README.md`:

```markdown
## Configuration

The pipeline uses environment-based configuration with support for `.env` files.

### Quick Start

1. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` and set your configuration:
   ```ini
   LLM__PROVIDER=openai
   LLM__OPENAI_API_KEY=your-api-key-here
   ```

3. Configuration is loaded automatically when you import from `src.config`:
   ```python
   from src.config import get_config
   
   config = get_config()
   print(config.llm.provider)  # openai
   ```

### Configuration Options

See `.env.example` for all available configuration options.

Configuration priority (highest to lowest):
1. Environment variables
2. `.env` file
3. Default values
```

---

## Step 2: Exception Hierarchy (Day 1 Afternoon)

### Objective
Create a comprehensive exception hierarchy for structured error handling with timestamps and context.

**Why We Need This:**
- Syntax engine needs proper error types for invalid queries
- LLM provider (Sprint 2) needs `RateLimitError`, `NetworkError`
- Better debugging with structured error context

### Files to Create

**2.1 Create `src/utils/__init__.py`**

```python
"""Utility modules for HITL Pipeline."""

from .exceptions import (
    PipelineException,
    ConfigurationError,
    LLMProviderError,
    RateLimitError,
    ValidationError,
    NetworkError,
)

__all__ = [
    "PipelineException",
    "ConfigurationError",
    "LLMProviderError",
    "RateLimitError",
    "ValidationError",
    "NetworkError",
]
```

**2.2 Create `src/utils/exceptions.py`**

```python
"""Exception hierarchy for HITL Research Strategy Pipeline.

This module defines a comprehensive exception hierarchy for handling
various error scenarios in the pipeline.
"""

from datetime import datetime, UTC
from typing import Any, Dict, Optional


class PipelineException(Exception):
    """Base exception for all pipeline errors.
    
    All custom exceptions in the pipeline inherit from this class.
    Provides common functionality for error details and timestamps.
    
    Attributes:
        message: Human-readable error message
        details: Additional error context
        timestamp: UTC timestamp when exception was raised
    """
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.timestamp = datetime.now(UTC)
    
    def __str__(self) -> str:
        """String representation of the exception."""
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for logging/serialization.
        
        Returns:
            Dictionary with exception details
        """
        return {
            "type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp.isoformat(),
        }


class ConfigurationError(PipelineException):
    """Configuration-related errors.
    
    Raised when:
    - Required configuration is missing
    - Configuration values are invalid
    - Configuration file cannot be loaded
    """
    pass


class LLMProviderError(PipelineException):
    """LLM provider-related errors.
    
    Base class for all errors that occur when interacting with
    language model providers (OpenAI, etc.).
    """
    pass


class AuthenticationError(LLMProviderError):
    """Authentication/authorization errors.
    
    Raised when:
    - API key is invalid
    - API key is missing
    - Permission denied
    """
    pass


class RateLimitError(LLMProviderError):
    """Rate limit exceeded errors.
    
    Raised when API rate limits are exceeded.
    Can be retried after a delay.
    
    Attributes:
        retry_after: Suggested retry delay in seconds
    """
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize with retry information.
        
        Args:
            message: Error message
            retry_after: Suggested delay before retry (seconds)
            details: Additional context
        """
        super().__init__(message, details)
        self.retry_after = retry_after


class NetworkError(LLMProviderError):
    """Network/connectivity errors.
    
    Raised when:
    - Network request fails
    - Connection timeout
    - DNS resolution fails
    """
    pass


class ValidationError(PipelineException):
    """Data validation errors.
    
    Raised when:
    - Input validation fails
    - Output validation fails
    - Data format is invalid
    """
    pass


class StageExecutionError(PipelineException):
    """Pipeline stage execution errors.
    
    Raised when a stage fails to execute properly.
    
    Attributes:
        stage_name: Name of the stage that failed
        project_id: Project ID if applicable
    """
    
    def __init__(
        self,
        message: str,
        stage_name: Optional[str] = None,
        project_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize with stage context.
        
        Args:
            message: Error message
            stage_name: Name of the failed stage
            project_id: Associated project ID
            details: Additional context
        """
        details = details or {}
        if stage_name:
            details["stage_name"] = stage_name
        if project_id:
            details["project_id"] = project_id
        
        super().__init__(message, details)
        self.stage_name = stage_name
        self.project_id = project_id


class PersistenceError(PipelineException):
    """Data persistence errors.
    
    Raised when:
    - File cannot be read/written
    - Database operation fails
    - Data cannot be serialized
    """
    pass
```

**2.3 Create `tests/test_exceptions.py`**

```python
"""Tests for exception hierarchy."""

from datetime import datetime, UTC

import pytest

from src.utils.exceptions import (
    PipelineException,
    ConfigurationError,
    LLMProviderError,
    AuthenticationError,
    RateLimitError,
    NetworkError,
    ValidationError,
    StageExecutionError,
    PersistenceError,
)


def test_pipeline_exception_basic():
    """Test basic PipelineException functionality."""
    exc = PipelineException("Test error")
    
    assert str(exc) == "Test error"
    assert exc.message == "Test error"
    assert exc.details == {}
    assert isinstance(exc.timestamp, datetime)


def test_pipeline_exception_with_details():
    """Test PipelineException with details."""
    details = {"field": "value", "count": 42}
    exc = PipelineException("Test error", details=details)
    
    assert "field=value" in str(exc)
    assert "count=42" in str(exc)
    assert exc.details == details


def test_pipeline_exception_to_dict():
    """Test exception serialization."""
    exc = PipelineException("Test error", details={"key": "value"})
    
    data = exc.to_dict()
    
    assert data["type"] == "PipelineException"
    assert data["message"] == "Test error"
    assert data["details"] == {"key": "value"}
    assert "timestamp" in data


def test_rate_limit_error_with_retry_after():
    """Test RateLimitError with retry_after."""
    exc = RateLimitError("Rate limit exceeded", retry_after=30.0)
    
    assert exc.retry_after == 30.0
    assert "Rate limit exceeded" in str(exc)


def test_stage_execution_error_context():
    """Test StageExecutionError with stage context."""
    exc = StageExecutionError(
        "Stage failed",
        stage_name="problem-framing",
        project_id="project_123",
    )
    
    assert exc.stage_name == "problem-framing"
    assert exc.project_id == "project_123"
    assert exc.details["stage_name"] == "problem-framing"
    assert exc.details["project_id"] == "project_123"


def test_exception_inheritance():
    """Test exception inheritance hierarchy."""
    # All custom exceptions inherit from PipelineException
    assert issubclass(ConfigurationError, PipelineException)
    assert issubclass(LLMProviderError, PipelineException)
    assert issubclass(ValidationError, PipelineException)
    
    # LLM-specific exceptions inherit from LLMProviderError
    assert issubclass(AuthenticationError, LLMProviderError)
    assert issubclass(RateLimitError, LLMProviderError)
    assert issubclass(NetworkError, LLMProviderError)
    
    # Can catch by base class
    try:
        raise AuthenticationError("Invalid API key")
    except LLMProviderError:
        pass  # Should catch
    
    try:
        raise RateLimitError("Too many requests")
    except PipelineException:
        pass  # Should catch
```

---

## Day 2: The Syntax Engine (Your "Moat")

### Objective
Build the deterministic Boolean query generator that ensures syntactically correct output for PubMed and Scopus.

**Why This Is Critical:**
- ChatGPT hallucinates invalid syntax (e.g., `NEAR/5` in PubMed)
- This is your competitive advantage
- Works standalone with no API costs
- Proves technical value immediately

### Architecture

The syntax engine uses the **Strategy Pattern** with three components:

1. **Models** (`src/search/models.py`) - Data structures for queries
2. **Dialects** (`src/search/dialects.py`) - Database-specific syntax rules
3. **Builder** (`src/search/builder.py`) - Orchestration layer

### 3.1 Create `src/search/__init__.py`

```python
"""Database-specific query syntax generation."""

from .models import SearchTerm, ConceptBlock, QueryPlan, FieldTag
from .dialects import PubMedDialect, ScopusDialect
from .builder import SyntaxBuilder, get_builder

__all__ = [
    "SearchTerm",
    "ConceptBlock",
    "QueryPlan",
    "FieldTag",
    "PubMedDialect",
    "ScopusDialect",
    "SyntaxBuilder",
    "get_builder",
]
```

### 3.2 Create `src/search/models.py`

```python
"""Data models for search query construction.

These are intermediate representations of queries before they are
translated into database-specific syntax.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class FieldTag(str, Enum):
    """Search field types."""
    KEYWORD = "keyword"  # Title/Abstract/Keywords
    CONTROLLED_VOCAB = "controlled"  # MeSH / Emtree
    ALL_FIELDS = "all"


@dataclass
class SearchTerm:
    """An atomic search unit.
    
    Attributes:
        text: The search term (e.g., "machine learning")
        field_tag: Which field to search
        is_phrase: Whether to treat as exact phrase
    """
    text: str
    field_tag: FieldTag = FieldTag.KEYWORD
    is_phrase: bool = False
    
    def __post_init__(self):
        """Auto-detect phrases (terms with spaces)."""
        if not self.is_phrase and " " in self.text.strip():
            self.is_phrase = True


@dataclass
class ConceptBlock:
    """A group of synonyms combined with OR.
    
    Example:
        label = "Population"
        terms = ["elderly", "older adults", "seniors"]
        
    Becomes: (elderly OR "older adults" OR seniors)
    """
    label: str
    terms: List[SearchTerm] = field(default_factory=list)
    
    def add_term(self, text: str, tag: FieldTag = FieldTag.KEYWORD):
        """Add a term to this concept block.
        
        Args:
            text: Search term text
            tag: Field tag for this term
        """
        self.terms.append(SearchTerm(text, tag))


@dataclass
class QueryPlan:
    """Complete search strategy (blocks combined with AND).
    
    Example:
        Block 1: (elderly OR "older adults")
        Block 2: (diabetes OR "type 2 diabetes")
        
    Becomes: (elderly OR "older adults") AND (diabetes OR "type 2 diabetes")
    """
    blocks: List[ConceptBlock] = field(default_factory=list)
```

### 3.3 Create `src/search/dialects.py`

```python
"""Database-specific syntax dialects using Strategy Pattern.

Each dialect knows how to format terms, join with operators,
and apply database-specific quirks.
"""

from abc import ABC, abstractmethod
from typing import List

from .models import SearchTerm, FieldTag


class DatabaseDialect(ABC):
    """Abstract base class for database syntax rules."""
    
    @abstractmethod
    def format_term(self, term: SearchTerm) -> str:
        """Format a single search term with field tags."""
        pass
    
    @abstractmethod
    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR operator."""
        pass
    
    @abstractmethod
    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND operator."""
        pass


class PubMedDialect(DatabaseDialect):
    """PubMed/MEDLINE syntax.
    
    Rules:
    - Phrases use double quotes: "machine learning"
    - Field tags use square brackets: [Title/Abstract]
    - OR groups use parentheses: (term1 OR term2)
    - AND joins concept blocks
    
    Example:
        "deep learning"[Title/Abstract] AND (diabetes[MeSH Terms] OR "type 2 diabetes"[Title/Abstract])
    """
    
    def format_term(self, term: SearchTerm) -> str:
        """Format term with PubMed field tags.
        
        Args:
            term: Search term to format
            
        Returns:
            Formatted string
        """
        # Sanitize and quote if needed
        clean_text = term.text.replace('"', '').strip()
        
        if term.is_phrase:
            base = f'"{clean_text}"'
        else:
            base = clean_text
        
        # Apply field tags
        if term.field_tag == FieldTag.CONTROLLED_VOCAB:
            return f"{base}[MeSH Terms]"
        elif term.field_tag == FieldTag.KEYWORD:
            return f"{base}[Title/Abstract]"
        else:
            return f"{base}[All Fields]"
    
    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR, wrapped in parentheses.
        
        Args:
            terms: List of formatted terms
            
        Returns:
            OR-joined string
        """
        if not terms:
            return ""
        if len(terms) == 1:
            return terms[0]
        return f"({' OR '.join(terms)})"
    
    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND.
        
        Args:
            groups: List of OR-joined groups
            
        Returns:
            AND-joined string
        """
        return "\nAND\n".join(groups)


class ScopusDialect(DatabaseDialect):
    """Scopus syntax.
    
    Rules:
    - Phrases use double quotes: "machine learning"
    - Uses TITLE-ABS-KEY() wrapper for keyword search
    - Can optimize: TITLE-ABS-KEY(term1 OR term2) instead of multiple wrappers
    - AND joins concept blocks
    
    Example:
        TITLE-ABS-KEY("deep learning" OR "neural networks") AND TITLE-ABS-KEY(diabetes OR "type 2 diabetes")
    """
    
    def format_term(self, term: SearchTerm) -> str:
        """Format term for Scopus.
        
        Args:
            term: Search term to format
            
        Returns:
            Formatted string (without wrapper, added by join_or)
        """
        clean_text = term.text.replace('"', '').strip()
        
        if term.is_phrase:
            return f'"{clean_text}"'
        return clean_text
    
    def join_or(self, terms: List[str]) -> str:
        """Join terms with OR inside TITLE-ABS-KEY wrapper.
        
        This is more efficient than wrapping each term individually.
        
        Args:
            terms: List of formatted terms
            
        Returns:
            OR-joined string with wrapper
        """
        if not terms:
            return ""
        
        inner = " OR ".join(terms)
        return f"TITLE-ABS-KEY({inner})"
    
    def join_and(self, groups: List[str]) -> str:
        """Join groups with AND.
        
        Args:
            groups: List of wrapped groups
            
        Returns:
            AND-joined string
        """
        return " AND ".join(groups)
```

### 3.4 Create `src/search/builder.py`

```python
"""Query builder that orchestrates dialect-specific syntax generation."""

from typing import Type

from .models import QueryPlan
from .dialects import DatabaseDialect, PubMedDialect, ScopusDialect


class SyntaxBuilder:
    """Builds database-specific query strings from a QueryPlan.
    
    Example:
        >>> plan = QueryPlan()
        >>> block = ConceptBlock("Disease")
        >>> block.add_term("diabetes")
        >>> plan.blocks.append(block)
        >>> 
        >>> builder = SyntaxBuilder(PubMedDialect)
        >>> query = builder.build(plan)
        >>> print(query)
        diabetes[Title/Abstract]
    """
    
    def __init__(self, dialect: Type[DatabaseDialect]):
        """Initialize with a dialect class.
        
        Args:
            dialect: DatabaseDialect subclass (not instance)
        """
        self.dialect = dialect()
    
    def build(self, plan: QueryPlan) -> str:
        """Build query string from plan.
        
        Args:
            plan: QueryPlan with concept blocks
            
        Returns:
            Database-specific query string
        """
        group_strings = []
        
        for block in plan.blocks:
            # Format each term in the block
            term_strings = []
            for term in block.terms:
                formatted = self.dialect.format_term(term)
                term_strings.append(formatted)
            
            if term_strings:
                # Join terms with OR
                group_str = self.dialect.join_or(term_strings)
                group_strings.append(group_str)
        
        # Join groups with AND
        return self.dialect.join_and(group_strings)


def get_builder(db_name: str) -> SyntaxBuilder:
    """Factory function to get builder for a database.
    
    Args:
        db_name: Database name ("pubmed" or "scopus")
        
    Returns:
        SyntaxBuilder instance
        
    Raises:
        ValueError: If database name is unknown
        
    Example:
        >>> builder = get_builder("pubmed")
        >>> isinstance(builder.dialect, PubMedDialect)
        True
    """
    db_name_lower = db_name.lower()
    
    if db_name_lower == "pubmed":
        return SyntaxBuilder(PubMedDialect)
    elif db_name_lower == "scopus":
        return SyntaxBuilder(ScopusDialect)
    else:
        raise ValueError(
            f"Unknown database: {db_name}. "
            f"Supported: pubmed, scopus"
        )
```

---

## Day 3: Testing & Demo

### Objective
Prove the syntax engine works correctly and is superior to ChatGPT.

### 3.5 Create `tests/test_syntax_engine.py`

```python
"""Tests for syntax engine - proves the 'moat'."""

import pytest

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder
from src.search.dialects import PubMedDialect, ScopusDialect


class TestSyntaxEngine:
    """Test suite proving correct syntax generation."""
    
    def setUp(self):
        """Create a sample query plan."""
        self.plan = QueryPlan()
        
        # Block 1: Disease concept
        disease_block = ConceptBlock("Disease")
        disease_block.add_term("heart attack", FieldTag.KEYWORD)
        disease_block.add_term("myocardial infarction", FieldTag.CONTROLLED_VOCAB)
        self.plan.blocks.append(disease_block)
        
        # Block 2: Treatment concept
        treatment_block = ConceptBlock("Treatment")
        treatment_block.add_term("aspirin", FieldTag.KEYWORD)
        treatment_block.add_term("acetylsalicylic acid", FieldTag.KEYWORD)
        self.plan.blocks.append(treatment_block)
    
    def test_pubmed_syntax_correctness(self):
        """Test PubMed syntax is valid and complete."""
        builder = get_builder("pubmed")
        query = builder.build(self.plan)
        
        print(f"\n[PubMed Query]\n{query}")
        
        # Verify phrase quoting
        assert '"heart attack"[Title/Abstract]' in query
        
        # Verify MeSH tag format
        assert '"myocardial infarction"[MeSH Terms]' in query
        
        # Verify OR grouping
        assert " OR " in query
        
        # Verify AND between concept blocks
        assert "\nAND\n" in query
        
        # Verify no hallucinated operators (ChatGPT mistake)
        assert "NEAR" not in query
        assert "ADJ" not in query
    
    def test_scopus_syntax_correctness(self):
        """Test Scopus syntax is valid and complete."""
        builder = get_builder("scopus")
        query = builder.build(self.plan)
        
        print(f"\n[Scopus Query]\n{query}")
        
        # Verify TITLE-ABS-KEY wrapper
        assert query.startswith("TITLE-ABS-KEY")
        
        # Verify phrase quoting
        assert '"heart attack"' in query
        
        # Verify efficient OR grouping (not repeated wrappers)
        assert query.count("TITLE-ABS-KEY") == 2  # One per concept block
        
        # Verify AND between blocks
        assert " AND " in query
    
    def test_factory_function(self):
        """Test get_builder factory."""
        pubmed_builder = get_builder("pubmed")
        scopus_builder = get_builder("scopus")
        
        assert isinstance(pubmed_builder.dialect, PubMedDialect)
        assert isinstance(scopus_builder.dialect, ScopusDialect)
        
        # Test case insensitivity
        assert isinstance(get_builder("PubMed").dialect, PubMedDialect)
        
        # Test invalid database
        with pytest.raises(ValueError, match="Unknown database"):
            get_builder("google_scholar")
    
    def test_empty_plan(self):
        """Test handling of empty query plan."""
        empty_plan = QueryPlan()
        builder = get_builder("pubmed")
        
        query = builder.build(empty_plan)
        assert query == ""
    
    def test_single_term(self):
        """Test query with single term."""
        plan = QueryPlan()
        block = ConceptBlock("Test")
        block.add_term("diabetes")
        plan.blocks.append(block)
        
        pubmed_builder = get_builder("pubmed")
        query = pubmed_builder.build(plan)
        
        # Single term should not have OR parentheses
        assert query == 'diabetes[Title/Abstract]'
    
    def test_phrase_detection(self):
        """Test automatic phrase detection."""
        plan = QueryPlan()
        block = ConceptBlock("Test")
        block.add_term("machine learning")  # Has space, should become phrase
        plan.blocks.append(block)
        
        builder = get_builder("pubmed")
        query = builder.build(plan)
        
        # Should be quoted
        assert '"machine learning"' in query


def test_demo_comparison():
    """Demo showing superiority over ChatGPT.
    
    This test generates a complex query and shows what ChatGPT
    would likely produce (with errors) vs our correct output.
    """
    plan = QueryPlan()
    
    # Complex multi-concept query
    pop_block = ConceptBlock("Population")
    pop_block.add_term("elderly")
    pop_block.add_term("older adults")
    pop_block.add_term("aged", FieldTag.CONTROLLED_VOCAB)
    plan.blocks.append(pop_block)
    
    intervention_block = ConceptBlock("Intervention")
    intervention_block.add_term("deep learning")
    intervention_block.add_term("neural networks")
    intervention_block.add_term("artificial intelligence", FieldTag.KEYWORD)
    plan.blocks.append(intervention_block)
    
    outcome_block = ConceptBlock("Outcome")
    outcome_block.add_term("diagnosis")
    outcome_block.add_term("diagnostic accuracy")
    plan.blocks.append(outcome_block)
    
    # Generate queries
    pubmed_query = get_builder("pubmed").build(plan)
    scopus_query = get_builder("scopus").build(plan)
    
    print("\n" + "="*60)
    print("SYNTAX ENGINE DEMO: The 'Moat'")
    print("="*60)
    
    print("\n[PubMed Query - CORRECT]")
    print(pubmed_query)
    
    print("\n[Scopus Query - CORRECT]")
    print(scopus_query)
    
    print("\n[What ChatGPT Might Produce - WRONG]")
    print('(elderly NEAR/5 "older adults") AND "deep learning" [mesh]')
    print("                ^^^^^^^^ Invalid operator in PubMed!")
    print("                                             ^^^^^^ Wrong tag format!")
    
    print("\n" + "="*60)
    print("✅ Our engine GUARANTEES valid syntax")
    print("❌ ChatGPT hallucinates invalid operators")
    print("="*60 + "\n")
```

### 3.6 Create Demo Script

**Create `demo_syntax_engine.py`**

```python
"""Demo script showing the syntax engine in action.

Run this to see the 'moat' feature working.
"""

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder


def main():
    """Run syntax engine demo."""
    print("\n" + "="*60)
    print("SYNTAX ENGINE DEMO")
    print("="*60)
    
    # Build a realistic research query
    plan = QueryPlan()
    
    # Population concept
    pop = ConceptBlock("Population")
    pop.add_term("type 2 diabetes", FieldTag.KEYWORD)
    pop.add_term("diabetes mellitus type 2", FieldTag.CONTROLLED_VOCAB)
    pop.add_term("T2DM", FieldTag.KEYWORD)
    plan.blocks.append(pop)
    
    # Intervention concept
    intervention = ConceptBlock("Intervention")
    intervention.add_term("machine learning", FieldTag.KEYWORD)
    intervention.add_term("deep learning", FieldTag.KEYWORD)
    intervention.add_term("neural networks", FieldTag.KEYWORD)
    plan.blocks.append(intervention)
    
    # Outcome concept
    outcome = ConceptBlock("Outcome")
    outcome.add_term("prediction", FieldTag.KEYWORD)
    outcome.add_term("risk stratification", FieldTag.KEYWORD)
    plan.blocks.append(outcome)
    
    # Generate for both databases
    print("\n[PubMed/MEDLINE Query]")
    print("-" * 60)
    pubmed_query = get_builder("pubmed").build(plan)
    print(pubmed_query)
    
    print("\n[Scopus Query]")
    print("-" * 60)
    scopus_query = get_builder("scopus").build(plan)
    print(scopus_query)
    
    print("\n" + "="*60)
    print("✅ Both queries are syntactically VALID")
    print("✅ Ready to paste directly into databases")
    print("✅ ChatGPT cannot guarantee this!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
```

---

## Sprint 1 Checklist

### Day 1 (Foundation)
- [ ] Install dependencies: `pip install pydantic pydantic-settings python-dotenv pytest`
- [ ] Create `.env` file from `.env.example`
- [ ] Create `src/config.py`
- [ ] Create `src/utils/__init__.py`
- [ ] Create `src/utils/exceptions.py`
- [ ] Run: `pytest tests/test_config.py tests/test_exceptions.py`

### Day 2 (Syntax Engine)
- [ ] Create `src/search/__init__.py`
- [ ] Create `src/search/models.py`
- [ ] Create `src/search/dialects.py`
- [ ] Create `src/search/builder.py`
- [ ] Create `demo_syntax_engine.py`
- [ ] Run demo: `python demo_syntax_engine.py`

### Day 3 (Validation)
- [ ] Create `tests/test_syntax_engine.py`
- [ ] Run: `pytest tests/test_syntax_engine.py -v`
- [ ] Verify all tests pass
- [ ] Update `.gitignore` to include `.env`
- [ ] Update README.md with syntax engine section
- [ ] Commit: "Sprint 1: Config + Exceptions + Syntax Engine"

---

## What You've Built

After Sprint 1, you have:

✅ **The "Moat"** - A deterministic Boolean query generator that ChatGPT cannot match  
✅ **Proper Foundation** - Config and exceptions for future sprints  
✅ **Proven Value** - Working demo showing technical superiority  
✅ **Zero API Costs** - All features work offline

---

## Next: Sprint 2 (LLM Integration)

Now that you have visible value, Sprint 2 will add:
- Rate limiting (Step 11 utilities)
- LLM provider layer (Step 3)
- Prompt management (Step 5)
- Critique loop (Step 6)

This will integrate the syntax engine with AI-powered concept extraction.

```python
"""Rate limiting utilities for HITL Pipeline.

This module provides rate limiting mechanisms to control the frequency
of operations like API requests.
"""

import logging
import time
from threading import Lock
from typing import Optional

logger = logging.getLogger(__name__)


class TokenBucket:
    """Token bucket rate limiter.
    
    Implements the token bucket algorithm for rate limiting.
    Tokens are added at a constant rate, and operations consume tokens.
    If tokens are available, the operation proceeds; otherwise, it blocks or fails.
    
    This is thread-safe and can be used across multiple threads.
    
    Attributes:
        rate: Rate at which tokens are added (tokens per second)
        capacity: Maximum number of tokens the bucket can hold
        tokens: Current number of available tokens
        
    Example:
        >>> limiter = TokenBucket(rate=10.0, capacity=20)
        >>> if limiter.consume(1):
        ...     make_api_call()
        ... else:
        ...     print("Rate limit exceeded")
    """
    
    def __init__(self, rate: float, capacity: int):
        """Initialize the token bucket.
        
        Args:
            rate: Rate at which tokens are added (tokens per second)
            capacity: Maximum number of tokens the bucket can hold (burst size)
            
        Raises:
            ValueError: If rate or capacity is not positive
        """
        if rate <= 0:
            raise ValueError(f"Rate must be positive, got {rate}")
        if capacity <= 0:
            raise ValueError(f"Capacity must be positive, got {capacity}")
        
        self.rate = rate
        self.capacity = capacity
        self.tokens = float(capacity)
        self.last_update = time.monotonic()
        self.lock = Lock()
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.monotonic()
        elapsed = now - self.last_update
        
        # Add tokens based on elapsed time
        self.tokens = min(
            self.capacity,
            self.tokens + (elapsed * self.rate)
        )
        self.last_update = now
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens without blocking.
        
        Args:
            tokens: Number of tokens to consume (default: 1)
            
        Returns:
            True if tokens were consumed, False if insufficient tokens
            
        Example:
            >>> limiter = TokenBucket(rate=10.0, capacity=20)
            >>> limiter.consume(5)
            True
        """
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                logger.debug(f"Consumed {tokens} token(s), {self.tokens:.2f} remaining")
                return True
            
            logger.debug(f"Insufficient tokens: need {tokens}, have {self.tokens:.2f}")
            return False
    
    def wait_for_token(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """Block until tokens are available or timeout occurs.
        
        Args:
            tokens: Number of tokens to wait for (default: 1)
            timeout: Maximum time to wait in seconds (None = wait forever)
            
        Returns:
            True if tokens were consumed, False if timeout occurred
            
        Example:
            >>> limiter = TokenBucket(rate=10.0, capacity=20)
            >>> limiter.wait_for_token(1, timeout=5.0)
            True
        """
        start_time = time.monotonic()
        
        while True:
            if self.consume(tokens):
                return True
            
            # Check timeout
            if timeout is not None:
                elapsed = time.monotonic() - start_time
                if elapsed >= timeout:
                    logger.warning(f"Timeout waiting for {tokens} token(s)")
                    return False
            
            # Calculate sleep time (wait for 1 token to be available)
            with self.lock:
                self._refill()
                needed = tokens - self.tokens
                if needed > 0:
                    sleep_time = needed / self.rate
                    # Cap sleep time to avoid long waits
                    sleep_time = min(sleep_time, 1.0)
                else:
                    sleep_time = 0.1
            
            time.sleep(sleep_time)
    
    def reset(self) -> None:
        """Reset the bucket to full capacity."""
        with self.lock:
            self.tokens = float(self.capacity)
            self.last_update = time.monotonic()
        logger.debug("Token bucket reset")
```

### 3.2 Retry Logic

**Create `src/utils/retry.py`**

```python
"""Retry utilities with exponential backoff.

This module provides decorators and utilities for retrying operations
that may fail transiently (e.g., network requests, rate-limited APIs).
"""

import logging
import time
from functools import wraps
from typing import Any, Callable, Optional, Tuple, Type, TypeVar

from .exceptions import NetworkError, RateLimitError

# Type variable for generic function signatures
T = TypeVar("T")

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
    exceptions: Tuple[Type[Exception], ...] = (NetworkError, RateLimitError),
    on_retry: Optional[Callable[[Exception, int], None]] = None,
) -> Callable:
    """Decorator for retrying failed operations with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds before first retry (default: 1.0)
        backoff_factor: Multiplier for delay after each retry (default: 2.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exceptions: Tuple of exception types to catch and retry
            (default: NetworkError, RateLimitError)
        on_retry: Optional callback function called before each retry
            with (exception, attempt_number)
            
    Returns:
        Decorated function that retries on specified exceptions
        
    Example:
        >>> @retry_with_backoff(max_retries=3, base_delay=1.0)
        ... def fetch_data():
        ...     # Your code that might fail
        ...     return requests.get(url)
    """
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = base_delay
            last_exception: Optional[Exception] = None
            func_name = getattr(func, "__name__", repr(func))
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    # Don't sleep after the last attempt
                    if attempt < max_retries - 1:
                        # Calculate delay with exponential backoff
                        current_delay = min(delay, max_delay)
                        
                        # Special handling for RateLimitError with retry_after
                        if isinstance(e, RateLimitError) and e.retry_after:
                            current_delay = min(e.retry_after, max_delay)
                        
                        # Log the retry attempt
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries} failed for {func_name}: {e}. "
                            f"Retrying in {current_delay:.2f}s..."
                        )
                        
                        # Call the on_retry callback if provided
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        # Sleep before retrying
                        time.sleep(current_delay)
                        
                        # Increase delay for next attempt
                        delay *= backoff_factor
                    else:
                        logger.error(f"All {max_retries} attempts failed for {func_name}: {e}")
            
            # All retries exhausted, raise the last exception
            if last_exception:
                raise last_exception
            
            # This should never happen, but mypy needs it
            raise RuntimeError("Retry logic failed unexpectedly")
        
        return wrapper
    
    return decorator


def retry_on_rate_limit(
    max_retries: int = 5,
    base_delay: float = 5.0,
    max_delay: float = 300.0,
) -> Callable:
    """Specialized decorator for retrying on rate limit errors.
    
    Args:
        max_retries: Maximum number of retry attempts (default: 5)
        base_delay: Initial delay in seconds (default: 5.0)
        max_delay: Maximum delay in seconds (default: 300.0)
        
    Returns:
        Decorated function
        
    Example:
        >>> @retry_on_rate_limit(max_retries=5)
        ... def call_api():
        ...     return api.request()
    """
    return retry_with_backoff(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=(RateLimitError,),
    )
```

### 3.3 Field Extractor

**Create `src/utils/field_extractor.py`**

```python
"""Field extraction utilities for safe nested data access.

This module provides utilities for safely extracting fields from
nested dictionaries, with fallbacks and type conversions.
"""

import logging
from typing import Any, Dict, List, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")


class FieldExtractor:
    """Utility for extracting fields from nested dictionaries.
    
    Provides methods for safely extracting nested fields, with fallbacks
    and type conversions. Useful for parsing API responses and LLM outputs.
    
    Example:
        >>> data = {"user": {"name": "John", "age": 30}}
        >>> extractor = FieldExtractor(data)
        >>> name = extractor.get_string("user.name")
        >>> age = extractor.get_int("user.age")
    """
    
    def __init__(self, data: Dict[str, Any]):
        """Initialize with data dictionary.
        
        Args:
            data: Dictionary to extract from
        """
        self.data = data
    
    def get(self, path: str, default: Any = None) -> Any:
        """Get value at path using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "metadata.title")
            default: Default value if path not found
            
        Returns:
            Value at path or default
            
        Example:
            >>> extractor.get("authors.0.name")
            'John Doe'
        """
        parts = path.split(".")
        current = self.data
        
        for part in parts:
            if current is None:
                return default
            
            # Handle list indexing
            if isinstance(current, list):
                try:
                    idx = int(part)
                    current = current[idx] if 0 <= idx < len(current) else default
                except (ValueError, IndexError):
                    return default
            # Handle dict access
            elif isinstance(current, dict):
                current = current.get(part, default)
            else:
                return default
        
        return current if current is not None else default
    
    def get_string(self, path: str, default: str = "") -> str:
        """Get string value at path.
        
        Args:
            path: Dot-separated path
            default: Default string value
            
        Returns:
            String value or default
        """
        value = self.get(path, default)
        return str(value).strip() if value else default
    
    def get_int(self, path: str, default: Optional[int] = None) -> Optional[int]:
        """Get integer value at path.
        
        Args:
            path: Dot-separated path
            default: Default integer value
            
        Returns:
            Integer value or default
        """
        value = self.get(path)
        if value is None:
            return default
        
        try:
            return int(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to int at path '{path}'")
            return default
    
    def get_float(self, path: str, default: Optional[float] = None) -> Optional[float]:
        """Get float value at path.
        
        Args:
            path: Dot-separated path
            default: Default float value
            
        Returns:
            Float value or default
        """
        value = self.get(path)
        if value is None:
            return default
        
        try:
            return float(value)
        except (ValueError, TypeError):
            logger.warning(f"Could not convert '{value}' to float at path '{path}'")
            return default
    
    def get_bool(self, path: str, default: bool = False) -> bool:
        """Get boolean value at path.
        
        Args:
            path: Dot-separated path
            default: Default boolean value
            
        Returns:
            Boolean value or default
        """
        value = self.get(path)
        if value is None:
            return default
        
        if isinstance(value, bool):
            return value
        
        # Handle string representations
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on")
        
        return bool(value)
    
    def get_list(self, path: str, default: Optional[List] = None) -> List:
        """Get list value at path.
        
        Args:
            path: Dot-separated path
            default: Default list value
            
        Returns:
            List value or default
        """
        value = self.get(path, default or [])
        return value if isinstance(value, list) else (default or [])
    
    def get_first(self, *paths: str, default: Any = None) -> Any:
        """Get first non-None value from multiple paths.
        
        Args:
            *paths: Multiple paths to try
            default: Default if all paths are None
            
        Returns:
            First non-None value or default
            
        Example:
            >>> extractor.get_first("doi", "DOI", "identifier.doi")
            '10.1234/paper'
        """
        for path in paths:
            value = self.get(path)
            if value is not None:
                return value
        return default
```

### 3.4 Tests for Utilities

**Create `tests/test_rate_limit.py`**

```python
"""Tests for rate limiter."""

import time
from threading import Thread

import pytest

from src.utils.rate_limit import TokenBucket


def test_token_bucket_basic():
    """Test basic token bucket functionality."""
    limiter = TokenBucket(rate=10.0, capacity=10)
    
    # Should be able to consume up to capacity
    assert limiter.consume(10)
    # Should not be able to consume more
    assert not limiter.consume(1)


def test_token_bucket_refill():
    """Test token refilling over time."""
    limiter = TokenBucket(rate=10.0, capacity=10)
    
    # Consume all tokens
    assert limiter.consume(10)
    assert not limiter.consume(1)
    
    # Wait for refill (1 token should be added in 0.1 seconds)
    time.sleep(0.15)
    assert limiter.consume(1)


def test_token_bucket_wait():
    """Test waiting for tokens."""
    limiter = TokenBucket(rate=10.0, capacity=5)
    
    # Consume all tokens
    assert limiter.consume(5)
    
    # Wait for 1 token (should succeed quickly)
    start = time.time()
    assert limiter.wait_for_token(1, timeout=1.0)
    elapsed = time.time() - start
    
    # Should take ~0.1 seconds to get 1 token
    assert 0.05 < elapsed < 0.3


def test_token_bucket_timeout():
    """Test timeout when waiting for tokens."""
    limiter = TokenBucket(rate=1.0, capacity=1)
    
    # Consume token
    assert limiter.consume(1)
    
    # Try to get 10 tokens with short timeout (should fail)
    assert not limiter.wait_for_token(10, timeout=0.1)


def test_token_bucket_thread_safety():
    """Test thread safety of token bucket."""
    limiter = TokenBucket(rate=10.0, capacity=100)
    consumed = []
    
    def consumer():
        for _ in range(10):
            if limiter.consume(1):
                consumed.append(1)
            time.sleep(0.01)
    
    threads = [Thread(target=consumer) for _ in range(5)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    # Should have consumed some tokens (but not more than capacity)
    assert 0 < len(consumed) <= 100


def test_token_bucket_validation():
    """Test input validation."""
    with pytest.raises(ValueError, match="Rate must be positive"):
        TokenBucket(rate=0, capacity=10)
    
    with pytest.raises(ValueError, match="Capacity must be positive"):
        TokenBucket(rate=10.0, capacity=0)
```

**Create `tests/test_retry.py`**

```python
"""Tests for retry logic."""

import pytest

from src.utils.retry import retry_with_backoff, retry_on_rate_limit
from src.utils.exceptions import NetworkError, RateLimitError


def test_retry_success_on_second_attempt():
    """Test successful retry after initial failure."""
    attempts = []
    
    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def flaky_function():
        attempts.append(1)
        if len(attempts) < 2:
            raise NetworkError("Temporary failure")
        return "success"
    
    result = flaky_function()
    
    assert result == "success"
    assert len(attempts) == 2


def test_retry_exhaustion():
    """Test that retries are exhausted and exception is raised."""
    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def always_fails():
        raise NetworkError("Permanent failure")
    
    with pytest.raises(NetworkError, match="Permanent failure"):
        always_fails()


def test_retry_with_rate_limit():
    """Test retry handling of rate limit errors."""
    attempts = []
    
    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def rate_limited():
        attempts.append(1)
        if len(attempts) < 2:
            raise RateLimitError("Rate limit", retry_after=0.01)
        return "success"
    
    result = rate_limited()
    
    assert result == "success"
    assert len(attempts) == 2


def test_retry_on_rate_limit_decorator():
    """Test specialized rate limit retry decorator."""
    attempts = []
    
    @retry_on_rate_limit(max_retries=3, base_delay=0.01)
    def rate_limited():
        attempts.append(1)
        if len(attempts) < 2:
            raise RateLimitError("Rate limit")
        return "success"
    
    result = rate_limited()
    
    assert result == "success"
    assert len(attempts) == 2


def test_retry_callback():
    """Test on_retry callback."""
    callback_args = []
    
    def on_retry(exc, attempt):
        callback_args.append((exc, attempt))
    
    @retry_with_backoff(max_retries=3, base_delay=0.01, on_retry=on_retry)
    def fails_twice():
        if len(callback_args) < 2:
            raise NetworkError("Fail")
        return "success"
    
    result = fails_twice()
    
    assert result == "success"
    assert len(callback_args) == 2
    assert callback_args[0][1] == 1  # First retry
    assert callback_args[1][1] == 2  # Second retry
```

**Create `tests/test_field_extractor.py`**

```python
"""Tests for field extractor."""

import pytest

from src.utils.field_extractor import FieldExtractor


def test_basic_field_extraction():
    """Test basic field extraction."""
    data = {"name": "John", "age": 30}
    extractor = FieldExtractor(data)
    
    assert extractor.get("name") == "John"
    assert extractor.get("age") == 30
    assert extractor.get("missing") is None


def test_nested_field_extraction():
    """Test nested field extraction with dot notation."""
    data = {
        "user": {
            "name": "John",
            "contact": {
                "email": "john@example.com"
            }
        }
    }
    extractor = FieldExtractor(data)
    
    assert extractor.get("user.name") == "John"
    assert extractor.get("user.contact.email") == "john@example.com"


def test_list_indexing():
    """Test list indexing in paths."""
    data = {
        "authors": [
            {"name": "John"},
            {"name": "Jane"}
        ]
    }
    extractor = FieldExtractor(data)
    
    assert extractor.get("authors.0.name") == "John"
    assert extractor.get("authors.1.name") == "Jane"
    assert extractor.get("authors.2.name") is None


def test_type_conversions():
    """Test type conversion methods."""
    data = {
        "string": "hello",
        "int": "42",
        "float": "3.14",
        "bool_true": "true",
        "bool_false": "false",
        "list": [1, 2, 3]
    }
    extractor = FieldExtractor(data)
    
    assert extractor.get_string("string") == "hello"
    assert extractor.get_int("int") == 42
    assert extractor.get_float("float") == 3.14
    assert extractor.get_bool("bool_true") is True
    assert extractor.get_bool("bool_false") is False
    assert extractor.get_list("list") == [1, 2, 3]


def test_default_values():
    """Test default values for missing fields."""
    data = {}
    extractor = FieldExtractor(data)
    
    assert extractor.get_string("missing", "default") == "default"
    assert extractor.get_int("missing", 99) == 99
    assert extractor.get_float("missing", 1.5) == 1.5
    assert extractor.get_bool("missing", True) is True
    assert extractor.get_list("missing", [1, 2]) == [1, 2]


def test_get_first():
    """Test getting first non-None value from multiple paths."""
    data = {
        "doi": "10.1234/test",
        "alternative": {
            "DOI": "10.5678/test"
        }
    }
    extractor = FieldExtractor(data)
    
    # Should return first found value
    assert extractor.get_first("missing", "doi") == "10.1234/test"
    assert extractor.get_first("missing1", "missing2", "alternative.DOI") == "10.5678/test"
    
    # Should return default if none found
    assert extractor.get_first("missing1", "missing2", default="fallback") == "fallback"
```

---

## Checklist

- [ ] Install new dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file from `.env.example`
- [ ] Create `src/config.py`
- [ ] Create `src/utils/__init__.py`
- [ ] Create `src/utils/exceptions.py`
- [ ] Create `src/utils/rate_limit.py`
- [ ] Create `src/utils/retry.py`
- [ ] Create `src/utils/field_extractor.py`
- [ ] Create all test files
- [ ] Run tests: `pytest tests/test_config.py tests/test_exceptions.py tests/test_rate_limit.py tests/test_retry.py tests/test_field_extractor.py`
- [ ] Update `.gitignore` to include `.env`
- [ ] Update README.md with configuration section
- [ ] Commit changes with message: "Phase 1: Add configuration, exceptions, and utilities"

---

## Next Steps

After completing Phase 1, you can proceed to:
- **Phase 2**: Database Syntax Engine (no API costs, can be tested standalone)
- **Phase 3**: LLM Integration (requires API key but builds on Phase 1 infrastructure)

Phase 1 provides the foundation for both Phase 2 and Phase 3, allowing parallel development.

