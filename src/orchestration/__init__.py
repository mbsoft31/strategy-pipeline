"""Orchestration layer for pipeline execution.

This module contains specialized components that decompose the responsibilities
of the original PipelineController:

- ArtifactManager: Handles artifact persistence and approval workflows
- ProjectNavigator: Manages stage progression and project status
- StageOrchestrator: Executes pipeline stages and manages stage registry

These components work together to provide a clean separation of concerns:
1. ArtifactManager directly interfaces with PersistenceService
2. ProjectNavigator uses ArtifactManager to check artifact states
3. StageOrchestrator uses both ModelService and ArtifactManager
4. PipelineController (in src/controller.py) acts as a facade coordinating all three

Example usage:
    >>> from src.orchestration import ArtifactManager, ProjectNavigator, StageOrchestrator
    >>> from src.services import FilePersistenceService, SimpleModelService
    >>>
    >>> persistence = FilePersistenceService(base_dir="./data")
    >>> model = SimpleModelService()
    >>>
    >>> artifact_mgr = ArtifactManager(persistence)
    >>> navigator = ProjectNavigator(artifact_mgr)
    >>> orchestrator = StageOrchestrator(model, artifact_mgr)
"""

from .artifact_manager import ArtifactManager
from .project_navigator import ProjectNavigator
from .stage_orchestrator import StageOrchestrator

__all__ = [
    "ArtifactManager",
    "ProjectNavigator",
    "StageOrchestrator",
]

