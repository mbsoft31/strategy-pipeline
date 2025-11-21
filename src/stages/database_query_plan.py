"""Stage 4: Database query plan generation.

Generates database-specific Boolean queries from SearchConceptBlocks using
the Anti-Hallucination syntax engine for guaranteed valid syntax.
"""
from datetime import UTC, datetime
from typing import Optional, List

from .base import BaseStage, StageResult
from ..models import ModelMetadata, SearchConceptBlocks, DatabaseQueryPlan


class DatabaseQueryPlanStage(BaseStage):
    """Generate DatabaseQueryPlan from SearchConceptBlocks.

    Inputs:
        project_id: str
        target_databases: Optional[List[str]] - Databases to generate queries for
        estimate_hits: bool - Whether to estimate hit counts (default: False)

    Output:
        StageResult with DatabaseQueryPlan in draft_artifact.

    Preconditions:
        - SearchConceptBlocks approved
    """

    def execute(
        self,
        *,
        project_id: str,
        target_databases: Optional[List[str]] = None,
        estimate_hits: bool = False,
        **kwargs
    ) -> StageResult:
        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="database-query-plan",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                prompts=[],
                validation_errors=errors,
            )

        # Load SearchConceptBlocks
        blocks = self.persistence_service.load_artifact("SearchConceptBlocks", project_id, SearchConceptBlocks)

        if blocks is None:
            return StageResult(
                stage_name="database-query-plan",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=["SearchConceptBlocks not found"],
            )

        # Handle dict-to-dataclass conversion for blocks
        from ..models import SearchConceptBlock
        if blocks.blocks and isinstance(blocks.blocks[0], dict):
            reconstructed_blocks = []
            for b_dict in blocks.blocks:
                if isinstance(b_dict, dict):
                    reconstructed_blocks.append(SearchConceptBlock(
                        id=b_dict.get('id', ''),
                        label=b_dict.get('label', 'Unnamed'),
                        description=b_dict.get('description'),
                        terms_included=b_dict.get('terms_included', []),
                        terms_excluded=b_dict.get('terms_excluded', [])
                    ))
                else:
                    reconstructed_blocks.append(b_dict)
            blocks.blocks = reconstructed_blocks

        # Validate blocks are not empty
        if not blocks.blocks or len(blocks.blocks) == 0:
            return StageResult(
                stage_name="database-query-plan",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=[
                    "SearchConceptBlocks is empty - no concept blocks defined.",
                    "Please review Stage 3 output and ensure at least one concept block with search terms exists.",
                    "Tip: Check if Stage 3 fell back to heuristic and generated empty blocks."
                ],
            )

        # Validate blocks have terms
        empty_blocks = [b.label for b in blocks.blocks if not b.terms_included]
        if empty_blocks:
            return StageResult(
                stage_name="database-query-plan",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=[
                    f"The following concept blocks have no search terms: {', '.join(empty_blocks)}",
                    "Please edit SearchConceptBlocks to add terms_included for each block."
                ],
            )

        # Default databases if not specified
        if not target_databases:
            target_databases = ["openalex", "arxiv", "pubmed", "scopus"]

        # Generate queries via ModelService
        plan, meta = self.model_service.build_database_queries(blocks, target_databases)

        # Add complexity analysis to each query
        for query in plan.queries:
            query.complexity_analysis = self._calculate_complexity(blocks, query)

        # Optional: Estimate hit counts for executable databases
        if estimate_hits:
            plan = self._estimate_hit_counts(plan)

        # Persist
        self.persistence_service.save_artifact(plan, project_id, "DatabaseQueryPlan")

        return StageResult(
            stage_name="database-query-plan",
            draft_artifact=plan,
            metadata=meta,
            prompts=[
                "Review each database query for accuracy.",
                "For PubMed: Validate suggested MeSH terms.",
                "For executable databases: Check hit count estimates.",
                "Copy syntax-only queries to respective database UIs for validation.",
            ],
            validation_errors=[]
        )
        return plan

    def _calculate_complexity(self, blocks: SearchConceptBlocks, query: DatabaseQuery) -> dict:
        """Calculate query complexity metrics and provide guidance.

        Complexity factors:
        - Number of concept blocks (more = more restrictive)
        - Terms per block (more = less restrictive within block)
        - Excluded terms (more = more restrictive)
        - Query length (proxy for complexity)

        Returns dict with complexity level, metrics, and guidance.
        """
        from ..models import DatabaseQuery

        total_terms = sum(len(b.terms_included) for b in blocks.blocks)
        num_blocks = len(blocks.blocks)
        excluded_count = sum(len(b.terms_excluded) for b in blocks.blocks)
        query_length = len(query.boolean_query_string)

        # Calculate average terms per block
        avg_terms_per_block = total_terms / max(num_blocks, 1)

        # Determine complexity level and guidance
        if num_blocks == 1:
            if avg_terms_per_block > 15:
                complexity = "very_broad"
                guidance = "Single concept with many synonyms - may return thousands of results. Consider adding more concept blocks to narrow scope."
                expected_results = "10,000+"
            elif avg_terms_per_block > 8:
                complexity = "broad"
                guidance = "Single concept block - results may be too broad. Consider adding outcome or population filters."
                expected_results = "1,000-10,000"
            else:
                complexity = "moderate"
                guidance = "Single focused concept - good for exploratory searches."
                expected_results = "100-1,000"

        elif num_blocks >= 6:
            complexity = "very_narrow"
            guidance = "Many concept blocks with AND logic - may miss relevant studies. Consider combining related concepts."
            expected_results = "< 50"

        elif num_blocks >= 4:
            complexity = "narrow"
            guidance = "Highly specific query - good for precise topics. Verify all blocks are essential."
            expected_results = "50-500"

        else:  # 2-3 blocks
            if avg_terms_per_block > 10:
                complexity = "moderate_broad"
                guidance = "Good balance - multiple concepts with rich synonyms. May need manual screening."
                expected_results = "500-5,000"
            else:
                complexity = "balanced"
                guidance = "Well-balanced query - recommended complexity for systematic reviews."
                expected_results = "100-1,000"

        # Adjust for excluded terms
        if excluded_count > 5:
            guidance += f" Note: {excluded_count} excluded terms will further narrow results."

        # Check for PubMed character limit
        warnings = []
        if query.database_name == "pubmed" and query_length > 4000:
            warnings.append(f"Query exceeds PubMed's 4000 character limit ({query_length} chars). Simplify query or split into multiple searches.")
        elif query.database_name == "scopus" and query_length > 2000:
            warnings.append(f"Query is very long ({query_length} chars) - may cause Scopus UI issues. Consider simplifying.")

        return {
            "complexity_level": complexity,
            "total_terms": total_terms,
            "num_blocks": num_blocks,
            "avg_terms_per_block": round(avg_terms_per_block, 1),
            "excluded_terms": excluded_count,
            "query_length": query_length,
            "expected_results": expected_results,
            "guidance": guidance,
            "warnings": warnings
        }

    def _estimate_hit_counts(self, plan: DatabaseQueryPlan) -> DatabaseQueryPlan:
        """Estimate hit counts for executable databases using SearchService."""
        try:
            from ..services.search_service import get_search_service
            search_service = get_search_service()

            for query in plan.queries:
                if search_service.is_executable(query.database_name):
                    try:
                        # Execute with max_results=1 to get total count only
                        result = search_service.execute_search(
                            database=query.database_name,
                            query=query.boolean_query_string,
                            max_results=1,
                            save=False  # Don't save results, just get count
                        )
                        query.hit_count_estimate = result.total_hits
                    except Exception as e:
                        # Don't fail the whole stage if estimation fails
                        query.notes = f"{query.notes or ''} (Hit estimation failed: {str(e)})"
        except ImportError:
            # SearchService not available, skip estimation
            pass

        return plan

    def validate_inputs(self, *, project_id: str, **_) -> list[str]:
        errors: list[str] = []
        if not project_id or not project_id.strip():
            errors.append("project_id must be a non-empty string")
        if not self.persistence_service.project_exists(project_id):
            errors.append(f"Project '{project_id}' does not exist")
        return errors

