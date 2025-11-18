"""Persistence service for saving and loading artifacts.

This module provides an abstraction for storing pipeline artifacts, allowing
different backends (files, databases, cloud storage) to be used interchangeably.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, TypeVar

from ..models import (
    ConceptModel,
    DatabaseQueryPlan,
    ProblemFraming,
    ProjectContext,
    ResearchQuestionSet,
    ScreeningChecklist,
    ScreeningCriteria,
    SearchConceptBlocks,
    StrategyPackage,
)

T = TypeVar("T")


class PersistenceService(ABC):
    """Abstract interface for artifact persistence."""

    @abstractmethod
    def save_artifact(self, artifact: Any, project_id: str, artifact_type: str) -> None:
        """Save an artifact to storage.

        Args:
            artifact: The artifact object to save.
            project_id: The project ID this artifact belongs to.
            artifact_type: Type identifier (e.g., "ProjectContext", "ResearchQuestionSet").
        """
        pass

    @abstractmethod
    def load_artifact(self, artifact_type: str, project_id: str, artifact_class: Type[T]) -> Optional[T]:
        """Load an artifact from storage.

        Args:
            artifact_type: Type identifier of the artifact.
            project_id: The project ID.
            artifact_class: The class to deserialize into.

        Returns:
            The loaded artifact, or None if not found.
        """
        pass

    @abstractmethod
    def list_projects(self) -> List[str]:
        """List all project IDs in storage.

        Returns:
            List of project ID strings.
        """
        pass

    @abstractmethod
    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists in storage.

        Args:
            project_id: The project ID to check.

        Returns:
            True if the project exists, False otherwise.
        """
        pass


class FilePersistenceService(PersistenceService):
    """File-based persistence implementation using JSON.

    Stores artifacts in a directory structure:
    {base_dir}/{project_id}/{artifact_type}.json
    """

    def __init__(self, base_dir: str = "./data"):
        """Initialize the file-based persistence service.

        Args:
            base_dir: Base directory for storing project data.
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, project_id: str) -> Path:
        """Get the directory path for a project."""
        project_dir = self.base_dir / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir

    def _get_artifact_path(self, project_id: str, artifact_type: str) -> Path:
        """Get the file path for an artifact."""
        return self._get_project_dir(project_id) / f"{artifact_type}.json"

    def save_artifact(self, artifact: Any, project_id: str, artifact_type: str) -> None:
        """Save an artifact to a JSON file."""
        artifact_path = self._get_artifact_path(project_id, artifact_type)
        artifact_dict = asdict(artifact)

        # Convert datetime objects to ISO strings for JSON serialization
        artifact_dict = self._serialize_datetimes(artifact_dict)

        with open(artifact_path, "w", encoding="utf-8") as f:
            json.dump(artifact_dict, f, indent=2, ensure_ascii=False)

    def load_artifact(self, artifact_type: str, project_id: str, artifact_class: Type[T]) -> Optional[T]:
        """Load an artifact from a JSON file."""
        artifact_path = self._get_artifact_path(project_id, artifact_type)

        if not artifact_path.exists():
            return None

        with open(artifact_path, "r", encoding="utf-8") as f:
            artifact_dict = json.load(f)

        # Note: This is a simplified deserialization; for production, you'd want
        # proper handling of nested objects, enums, and datetime parsing
        return artifact_class(**artifact_dict)

    def list_projects(self) -> List[str]:
        """List all project directories."""
        if not self.base_dir.exists():
            return []

        return [d.name for d in self.base_dir.iterdir() if d.is_dir()]

    def project_exists(self, project_id: str) -> bool:
        """Check if a project directory exists."""
        return self._get_project_dir(project_id).exists()

    def _serialize_datetimes(self, obj: Any) -> Any:
        """Recursively convert datetime objects to ISO strings."""
        if isinstance(obj, dict):
            return {k: self._serialize_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self._serialize_datetimes(item) for item in obj]
        elif hasattr(obj, "isoformat"):  # datetime objects
            return obj.isoformat()
        else:
            return obj

