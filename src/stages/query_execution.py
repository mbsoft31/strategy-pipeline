"""Stage 7: Query Execution.

Executes database queries from DatabaseQueryPlan using SearchService,
retrieves papers from supported databases (arXiv, Crossref, OpenAlex, S2),
deduplicates results, and saves metadata artifact pointing to result files.
"""
from datetime import UTC, datetime
from pathlib import Path
from typing import List
import logging

from .base import BaseStage, StageResult
from ..models import (
    ModelMetadata,
    DatabaseQueryPlan,
    SearchResults,
)
from ..services.search_service import SearchService

logger = logging.getLogger(__name__)


class QueryExecutionStage(BaseStage):
    """Execute DatabaseQueryPlan queries and retrieve papers.

    Inputs:
        project_id: str
        auto_deduplicate: bool (default True) - merge results from multiple databases
        max_results_per_db: int (default 100) - limit per database query

    Output:
        SearchResults artifact (metadata only, points to JSON result files)
    """

    # Map database names from Stage 4 to SearchService provider keys
    SUPPORTED_DATABASES = {
        "arxiv": "arxiv",
        "crossref": "crossref",
        "openalex": "openalex",
        "semantic_scholar": "s2",
        "s2": "s2",
    }

    def execute(
        self,
        *,
        project_id: str,
        auto_deduplicate: bool = True,
        max_results_per_db: int = 100,
        **kwargs
    ) -> StageResult:
        """Execute database searches and aggregate results."""

        # Validate inputs
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="query-execution",
                draft_artifact=None,
                metadata=ModelMetadata(
                    model_name="n/a",
                    mode="n/a",
                    generated_at=datetime.now(UTC)
                ),
                validation_errors=errors,
            )

        # Load DatabaseQueryPlan
        query_plan = self.persistence_service.load_artifact(
            "DatabaseQueryPlan",
            project_id,
            DatabaseQueryPlan
        )

        if query_plan is None:
            return StageResult(
                stage_name="query-execution",
                draft_artifact=None,
                metadata=ModelMetadata(
                    model_name="n/a",
                    mode="n/a",
                    generated_at=datetime.now(UTC)
                ),
                validation_errors=["DatabaseQueryPlan artifact not found. Run stage 4 first."],
            )

        if not query_plan.queries:
            return StageResult(
                stage_name="query-execution",
                draft_artifact=None,
                metadata=ModelMetadata(
                    model_name="n/a",
                    mode="n/a",
                    generated_at=datetime.now(UTC)
                ),
                validation_errors=["DatabaseQueryPlan contains no queries to execute."],
            )

        # Initialize project-scoped SearchService
        search_service = SearchService(
            base_dir=self.persistence_service.base_dir,
            project_id=project_id
        )

        # Execute queries for each database
        start_time = datetime.now(UTC)
        executed_results = []
        warnings = []
        databases_executed = []

        for query in query_plan.queries:
            db_name = query.database_name.lower()

            # Check if database is supported
            if db_name not in self.SUPPORTED_DATABASES:
                warning_msg = (
                    f"Database '{query.database_name}' not yet supported. "
                    f"Supported: {', '.join(self.SUPPORTED_DATABASES.keys())}. "
                    f"Skipping this query."
                )
                logger.warning(warning_msg)
                warnings.append(warning_msg)
                continue

            # Execute search
            provider_key = self.SUPPORTED_DATABASES[db_name]
            try:
                logger.info(f"Executing search on {query.database_name}...")
                result_summary = search_service.execute_search(
                    database=provider_key,
                    query=query.boolean_query_string,
                    max_results=max_results_per_db
                )

                executed_results.append(result_summary)
                databases_executed.append(query.database_name)

                logger.info(
                    f"Retrieved {result_summary.total_hits} results from "
                    f"{query.database_name} (saved to {result_summary.file_path})"
                )

            except Exception as e:
                error_msg = f"Failed to execute search on {query.database_name}: {str(e)}"
                logger.error(error_msg, exc_info=True)
                warnings.append(error_msg)
                continue

        # Handle case where no databases executed successfully
        if not executed_results:
            return StageResult(
                stage_name="query-execution",
                draft_artifact=None,
                metadata=ModelMetadata(
                    model_name="n/a",
                    mode="n/a",
                    generated_at=datetime.now(UTC)
                ),
                validation_errors=[
                    "No database queries executed successfully.",
                    *warnings
                ],
            )

        # Deduplicate results if multiple databases were queried
        dedup_stats = {}
        merged_file_path = None
        total_before_dedup = sum(r.total_hits for r in executed_results)

        if auto_deduplicate and len(executed_results) > 1:
            try:
                logger.info("Deduplicating results across databases...")

                # Collect file paths for deduplication
                result_file_paths = [r.file_path for r in executed_results if r.file_path]

                # Deduplicate using SearchService's built-in deduplicator
                deduplicated_papers = search_service.deduplicate_results(result_file_paths)

                # Save merged deduplicated results
                merged_file_path = search_service.save_deduplicated_results(
                    deduplicated_papers,
                    databases=databases_executed
                )

                dedup_stats = {
                    "original_count": total_before_dedup,
                    "deduplicated_count": len(deduplicated_papers),
                    "duplicates_removed": total_before_dedup - len(deduplicated_papers),
                    "deduplication_rate": round(
                        (total_before_dedup - len(deduplicated_papers)) / total_before_dedup * 100,
                        2
                    ) if total_before_dedup > 0 else 0.0
                }

                logger.info(
                    f"Deduplication complete: {dedup_stats['duplicates_removed']} "
                    f"duplicates removed ({dedup_stats['deduplication_rate']}%)"
                )

            except Exception as e:
                warning_msg = f"Deduplication failed: {str(e)}. Keeping separate results."
                logger.warning(warning_msg, exc_info=True)
                warnings.append(warning_msg)
                dedup_stats = {"error": str(e)}

        # Calculate execution time
        execution_time = (datetime.now(UTC) - start_time).total_seconds()

        # Collect all result file paths (individual + merged)
        result_file_paths = [r.file_path for r in executed_results if r.file_path]
        if merged_file_path:
            result_file_paths.append(merged_file_path)

        # Create SearchResults artifact (metadata only, not the papers themselves)
        search_results = SearchResults(
            project_id=project_id,
            total_results=total_before_dedup,
            deduplicated_count=dedup_stats.get("deduplicated_count", total_before_dedup),
            databases_searched=databases_executed,
            result_file_paths=result_file_paths,
            deduplication_stats=dedup_stats,
            execution_time_seconds=execution_time,
            model_metadata=ModelMetadata(
                model_name="SearchService",
                mode="execution",
                generated_at=datetime.now(UTC)
            ),
        )

        # Prepare prompts for user
        prompts = [
            f"Successfully retrieved {search_results.total_results} papers from "
            f"{len(databases_executed)} database(s): {', '.join(databases_executed)}.",
        ]

        if dedup_stats and dedup_stats.get("duplicates_removed", 0) > 0:
            prompts.append(
                f"Deduplication removed {dedup_stats['duplicates_removed']} duplicate papers "
                f"({dedup_stats['deduplication_rate']}% reduction). "
                f"Final unique papers: {dedup_stats['deduplicated_count']}."
            )

        prompts.append(
            f"Result files saved to: {Path(result_file_paths[0]).parent}"
        )

        if warnings:
            prompts.extend([f"⚠️  {w}" for w in warnings])

        return StageResult(
            stage_name="query-execution",
            draft_artifact=search_results,
            metadata=search_results.model_metadata,
            prompts=prompts,
            validation_errors=[],
        )

