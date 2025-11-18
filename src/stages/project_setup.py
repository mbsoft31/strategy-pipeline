"""Stage 0: Project setup & context capture.

Generates a draft ProjectContext from a raw idea using the ModelService.
"""
from typing import Optional
from datetime import UTC, datetime

from .base import BaseStage, StageResult
from ..models import ModelMetadata


class ProjectSetupStage(BaseStage):
    """Generate a draft ProjectContext from a raw idea.

    Inputs:
        raw_idea: str
        suggested_title: Optional[str]

    Output:
        StageResult with draft ProjectContext and metadata.
    """

    def execute(self, *, raw_idea: str, project_id: Optional[str] = None, suggested_title: Optional[str] = None) -> StageResult:
        errors = self.validate_inputs(raw_idea=raw_idea)
        if errors:
            # Return a minimal StageResult with validation errors
            return StageResult(
                stage_name="project-setup",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                prompts=[],
                validation_errors=errors,
            )

        # Ask the model service to propose a draft context
        draft, metadata = self.model_service.suggest_project_context(raw_idea)

        if project_id:
            draft.id = project_id
        if suggested_title:
            draft.title = suggested_title

        # Persist as draft immediately; controller will save too for consistency
        self.persistence_service.save_artifact(draft, draft.id, "ProjectContext")

        return StageResult(
            stage_name="project-setup",
            draft_artifact=draft,
            metadata=metadata,
            prompts=[
                "Review the generated project title and short_description.",
                "Edit discipline, subfield, application_area if needed.",
                "Add or refine initial_keywords and constraints.",
            ],
        )

    def validate_inputs(self, *, raw_idea: str, **_) -> list[str]:
        errors: list[str] = []
        if not raw_idea or not raw_idea.strip():
            errors.append("raw_idea must be a non-empty string")
        return errors
