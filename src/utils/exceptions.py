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

