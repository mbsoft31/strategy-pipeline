"""Pipeline stages implementation."""

from .base import BaseStage, StageResult
from .project_setup import ProjectSetupStage

__all__ = [
    "BaseStage",
    "StageResult",
    "ProjectSetupStage",
]
