"""Stage 6: Strategy Export Bundle.

Aggregates approved artifacts into an export bundle (Markdown summary and
file list). Placeholder minimal implementation for scaffolding.
"""
from datetime import UTC, datetime
from pathlib import Path
from typing import List

from .base import BaseStage, StageResult
from ..models import (
    ModelMetadata,
    ProjectContext,
    ProblemFraming,
    ConceptModel,
    ResearchQuestionSet,
    SearchConceptBlocks,
    DatabaseQueryPlan,
    ScreeningCriteria,
    StrategyExportBundle,
)


class StrategyExportStage(BaseStage):
    """Generate a StrategyExportBundle from prior approved artifacts."""

    def execute(self, *, project_id: str, include_markdown: bool = True, **kwargs) -> StageResult:
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="strategy-export",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=errors,
            )

        ctx = self.persistence_service.load_artifact("ProjectContext", project_id, ProjectContext)
        framing = self.persistence_service.load_artifact("ProblemFraming", project_id, ProblemFraming)
        concept_model = self.persistence_service.load_artifact("ConceptModel", project_id, ConceptModel)
        rq_set = self.persistence_service.load_artifact("ResearchQuestionSet", project_id, ResearchQuestionSet)
        blocks = self.persistence_service.load_artifact("SearchConceptBlocks", project_id, SearchConceptBlocks)
        query_plan = self.persistence_service.load_artifact("DatabaseQueryPlan", project_id, DatabaseQueryPlan)
        screening = self.persistence_service.load_artifact("ScreeningCriteria", project_id, ScreeningCriteria)

        required_missing: List[str] = []
        for name, art in [
            ("ProjectContext", ctx),
            ("ProblemFraming", framing),
            ("ConceptModel", concept_model),
            ("ResearchQuestionSet", rq_set),
            ("SearchConceptBlocks", blocks),
            ("DatabaseQueryPlan", query_plan),
        ]:
            if art is None:
                required_missing.append(name)

        if required_missing:
            return StageResult(
                stage_name="strategy-export",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=[f"Missing required artifacts: {', '.join(required_missing)}"],
            )

        export_dir = Path(self.persistence_service.base_dir) / project_id / "export"
        export_dir.mkdir(parents=True, exist_ok=True)

        exported_files: List[str] = []
        # Collect existing JSON artifact files
        for base_name in [
            "ProjectContext", "ProblemFraming", "ConceptModel", "ResearchQuestionSet", "SearchConceptBlocks", "DatabaseQueryPlan", "ScreeningCriteria"
        ]:
            json_path = Path(self.persistence_service.base_dir) / project_id / f"{base_name}.json"
            if json_path.exists():
                exported_files.append(str(json_path.relative_to(export_dir.parent)))

        markdown_summary = ""
        if include_markdown:
            markdown_summary = self._build_markdown_summary(ctx, framing, concept_model, rq_set, blocks, query_plan, screening)
            summary_path = export_dir / "STRATEGY_SUMMARY.md"
            summary_path.write_text(markdown_summary, encoding="utf-8")
            exported_files.append(str(summary_path.relative_to(export_dir.parent)))

        bundle = StrategyExportBundle(
            project_id=project_id,
            exported_files=exported_files,
            notes="Placeholder export bundle; enhance for full protocol packaging.",
            model_metadata=ModelMetadata(model_name=self.model_service.model_name, mode=self.model_service.mode, generated_at=datetime.now(UTC)),
        )

        self.persistence_service.save_artifact(bundle, project_id, "StrategyExportBundle")

        return StageResult(
            stage_name="strategy-export",
            draft_artifact=bundle,
            metadata=bundle.model_metadata,
            prompts=[
                "Review STRATEGY_SUMMARY.md for completeness.",
                "Add PRISMA flow elements if performing SLR.",
                "Package citations and screening log (future).",
            ],
            validation_errors=[],
        )

    def _build_markdown_summary(self, ctx, framing, concept_model, rq_set, blocks, query_plan, screening) -> str:
        lines = [
            f"# Strategy Summary for Project: {ctx.title}",
            "", "## Problem Framing", framing.problem_statement, "", "### Goals", *[f"- {g}" for g in framing.goals],
            "", "## Concepts", *[f"- {c.label} ({c.type})" for c in concept_model.concepts[:20]],
            "", "## Research Questions", *[f"- {q.text}" for q in rq_set.questions],
            "", "## Search Concept Blocks", *[f"- {b.label}: {', '.join(b.terms_included[:6])}" for b in blocks.blocks],
            "", "## Database Queries",
        ]
        for q in query_plan.queries:
            lines.append(f"### {q.database_name.upper()}")
            lines.append("```")
            lines.append(q.boolean_query_string)
            lines.append("```")
            if q.complexity_analysis:
                lines.append(f"Complexity: {q.complexity_analysis.get('complexity_level')} | Expected Results: {q.complexity_analysis.get('expected_results')}")
        if screening:
            lines.extend(["", "## Screening Criteria", "### Inclusion", *[f"- {c}" for c in screening.inclusion_criteria], "### Exclusion", *[f"- {c}" for c in screening.exclusion_criteria]])
        lines.append("\n*Generated by Strategy Pipeline (Stage 6 Preview)*")
        return "\n".join(lines)
