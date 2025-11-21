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

