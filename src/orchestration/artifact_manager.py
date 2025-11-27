"""Artifact management and persistence operations.

This module handles all artifact-related operations including loading, saving,
and approval workflows.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, UTC

from ..models import ApprovalStatus
from ..services.persistence_service import PersistenceService


class ArtifactManager:
    """Manages artifact loading, saving, and approval workflows.

    This class is responsible for:
    - Loading artifacts from persistence
    - Saving artifacts to persistence
    - Handling artifact approval with edits and status updates
    - Listing available projects
    - Checking project existence

    It provides a clean interface to the PersistenceService with added
    business logic for approval workflows.
    """

    def __init__(self, persistence_service: PersistenceService):
        """Initialize the ArtifactManager.

        Args:
            persistence_service: The persistence service for data storage.
        """
        self.persistence_service = persistence_service

    def get_artifact(
        self,
        project_id: str,
        artifact_type: str,
        artifact_class: Any,
    ) -> Optional[Any]:
        """Load an artifact from persistence.

        Args:
            project_id: The ID of the project.
            artifact_type: The type/name of the artifact (e.g., "ProjectContext").
            artifact_class: The class to deserialize the artifact into.

        Returns:
            The loaded artifact instance, or None if not found.

        Example:
            >>> manager = ArtifactManager(persistence_service)
            >>> ctx = manager.get_artifact("proj_123", "ProjectContext", ProjectContext)
        """
        return self.persistence_service.load_artifact(
            artifact_type, project_id, artifact_class
        )

    def save_artifact(
        self,
        artifact: Any,
        project_id: str,
        artifact_type: str,
    ) -> None:
        """Save an artifact to persistence.

        Args:
            artifact: The artifact instance to save.
            project_id: The ID of the project.
            artifact_type: The type/name of the artifact.

        Example:
            >>> manager.save_artifact(context_obj, "proj_123", "ProjectContext")
        """
        self.persistence_service.save_artifact(artifact, project_id, artifact_type)

    def approve_artifact(
        self,
        project_id: str,
        artifact_type: str,
        artifact_class: Any,
        edits: Dict[str, Any],
        approval_status: ApprovalStatus = ApprovalStatus.APPROVED,
        user_notes: Optional[str] = None,
    ) -> None:
        """Apply edits, update status, and persist artifact.

        This method implements the approval workflow:
        1. Load the existing artifact
        2. Apply user edits to artifact fields
        3. Update approval status
        4. Update timestamp
        5. Add user notes if provided
        6. Save the modified artifact

        Args:
            project_id: The ID of the project.
            artifact_type: The type/name of the artifact.
            artifact_class: The class of the artifact.
            edits: Dictionary of field names to new values.
            approval_status: The approval status to set (default: APPROVED).
            user_notes: Optional notes from the user.

        Raises:
            ValueError: If the artifact is not found.

        Example:
            >>> manager.approve_artifact(
            ...     "proj_123",
            ...     "ProjectContext",
            ...     ProjectContext,
            ...     edits={"title": "Updated Title"},
            ...     user_notes="Looks good!"
            ... )
        """
        # Load the artifact
        artifact = self.persistence_service.load_artifact(
            artifact_type, project_id, artifact_class
        )
        if artifact is None:
            raise ValueError(
                f"Artifact '{artifact_type}' not found for project '{project_id}'."
            )

        # Apply edits
        for field_name, value in edits.items():
            if hasattr(artifact, field_name):
                setattr(artifact, field_name, value)

        # Update metadata
        artifact.status = approval_status
        artifact.updated_at = datetime.now(UTC)
        if user_notes:
            artifact.user_notes = user_notes

        # Save the updated artifact
        self.persistence_service.save_artifact(artifact, project_id, artifact_type)

    def list_projects(self) -> List[str]:
        """List all available projects.

        Returns:
            List of project IDs.

        Example:
            >>> manager.list_projects()
            ['project_abc123', 'project_def456']
        """
        return self.persistence_service.list_projects()

    def project_exists(self, project_id: str) -> bool:
        """Check if a project exists.

        Args:
            project_id: The ID of the project to check.

        Returns:
            True if the project exists, False otherwise.

        Example:
            >>> manager.project_exists("proj_123")
            True
        """
        return self.persistence_service.project_exists(project_id)

