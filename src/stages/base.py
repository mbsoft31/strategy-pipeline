"""Base abstractions for pipeline stages.

This module defines the core interface that all pipeline stages implement,
enabling uniform orchestration by the controller.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..models import ModelMetadata


@dataclass
class StageResult:
    """Result returned by a stage execution.

    This is a UI-agnostic representation of what a stage produces,
    allowing the controller to pass it to any presentation layer.
    """
    stage_name: str
    draft_artifact: Any
    metadata: ModelMetadata
    prompts: List[str] = field(default_factory=list)  # Suggested questions/prompts for the user
    validation_errors: List[str] = field(default_factory=list)
    extra_data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary for JSON serialization (e.g., for web API)."""
        return {
            "stage_name": self.stage_name,
            "draft_artifact": self.draft_artifact,
            "metadata": {
                "model_name": self.metadata.model_name,
                "mode": self.metadata.mode,
                "prompt_version": self.metadata.prompt_version,
                "generated_at": self.metadata.generated_at.isoformat(),
                "notes": self.metadata.notes,
            },
            "prompts": self.prompts,
            "validation_errors": self.validation_errors,
            "extra_data": self.extra_data,
        }


class BaseStage(ABC):
    """Abstract base class for all pipeline stages.

    Each stage:
    - Takes inputs (previous artifacts, user data).
    - Calls model services to generate draft artifacts.
    - Returns a StageResult for HITL review.
    - Does NOT interact with users directly (UI-agnostic).
    """

    def __init__(self, model_service: Any, persistence_service: Any, name: Optional[str] = None):
        """Initialize the stage with required services.

        Args:
            model_service: Service for LLM/SLM interactions.
            persistence_service: Service for saving/loading artifacts.
            name: Optional human-readable name of the stage.
        """
        self.model_service = model_service
        self.persistence_service = persistence_service
        self.name = name or self.__class__.__name__

    @abstractmethod
    def execute(self, *args, **kwargs) -> StageResult:
        """Execute the stage logic.

        This method should:
        1. Validate inputs.
        2. Call model services to generate draft artifacts.
        3. Perform any business logic.
        4. Return a StageResult with draft artifacts and metadata.

        Args:
            *args, **kwargs: Stage-specific inputs.

        Returns:
            StageResult containing draft artifacts and metadata.
        """
        raise NotImplementedError

    def validate_inputs(self, *args, **kwargs) -> List[str]:
        """Validate stage inputs before execution.

        Returns:
            List of validation error messages (empty if valid).
        """
        return []
