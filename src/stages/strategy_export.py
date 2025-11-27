"""Stage 6: Strategy Export Bundle.

Aggregates approved artifacts into an export bundle with multiple export formats:
- PRISMA-compliant Markdown protocol
- CSV export of retrieved papers
- BibTeX citations
- RIS format for EndNote/Mendeley
- Query files in database-specific formats
"""
from datetime import UTC, datetime
from pathlib import Path
from typing import List, Dict, Any
import csv
import logging

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
    SearchResults,
    StrategyExportBundle,
)

logger = logging.getLogger(__name__)


class StrategyExportStage(BaseStage):
    """Generate a StrategyExportBundle from prior approved artifacts with multi-format export."""

    def execute(self, *, project_id: str, include_markdown: bool = True, export_formats: List[str] = None, **kwargs) -> StageResult:
        """Execute strategy export with multiple format support.

        Args:
            project_id: Project identifier
            include_markdown: Generate PRISMA-compliant Markdown summary
            export_formats: List of formats to export (csv, bibtex, ris). Defaults to all.
        """
        if export_formats is None:
            export_formats = ["csv", "bibtex", "ris"]

        errors = self.validate_inputs(project_id=project_id)
        if errors:
            return StageResult(
                stage_name="strategy-export",
                draft_artifact=None,
                metadata=ModelMetadata(model_name="n/a", mode="n/a", generated_at=datetime.now(UTC)),
                validation_errors=errors,
            )

        # Load all artifacts
        ctx = self.persistence_service.load_artifact("ProjectContext", project_id, ProjectContext)
        framing = self.persistence_service.load_artifact("ProblemFraming", project_id, ProblemFraming)
        concept_model = self.persistence_service.load_artifact("ConceptModel", project_id, ConceptModel)
        rq_set = self.persistence_service.load_artifact("ResearchQuestionSet", project_id, ResearchQuestionSet)
        blocks = self.persistence_service.load_artifact("SearchConceptBlocks", project_id, SearchConceptBlocks)
        query_plan = self.persistence_service.load_artifact("DatabaseQueryPlan", project_id, DatabaseQueryPlan)
        screening = self.persistence_service.load_artifact("ScreeningCriteria", project_id, ScreeningCriteria)
        search_results = self.persistence_service.load_artifact("SearchResults", project_id, SearchResults)  # NEW

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
        export_stats: Dict[str, Any] = {}

        # Export papers from SearchResults if available
        papers_exported = 0
        if search_results and search_results.result_file_paths:
            logger.info(f"Exporting {search_results.total_results} papers from SearchResults...")

            try:
                # Load all papers from result files
                from ..services.search_service import SearchService
                service = SearchService()

                all_papers = []
                for file_path in search_results.result_file_paths:
                    if "deduplicated" in file_path:  # Prefer deduplicated results
                        papers = service.load_results(file_path)
                        all_papers = papers
                        break

                # Fallback to loading all files if no deduplicated file
                if not all_papers:
                    for file_path in search_results.result_file_paths:
                        papers = service.load_results(file_path)
                        all_papers.extend(papers)

                logger.info(f"Loaded {len(all_papers)} papers for export")

                # Export to requested formats
                if "csv" in export_formats and all_papers:
                    csv_path = self._export_papers_csv(all_papers, export_dir)
                    exported_files.append(str(csv_path.relative_to(export_dir.parent)))
                    papers_exported += len(all_papers)

                if "bibtex" in export_formats and all_papers:
                    bib_path = self._export_papers_bibtex(all_papers, export_dir)
                    exported_files.append(str(bib_path.relative_to(export_dir.parent)))

                if "ris" in export_formats and all_papers:
                    ris_path = self._export_papers_ris(all_papers, export_dir)
                    exported_files.append(str(ris_path.relative_to(export_dir.parent)))

                export_stats["papers_exported"] = len(all_papers)
                export_stats["databases"] = search_results.databases_searched
                export_stats["deduplication_rate"] = search_results.deduplication_stats.get("deduplication_rate", 0)

            except Exception as e:
                logger.error(f"Failed to export papers: {e}", exc_info=True)
                export_stats["export_error"] = str(e)

        # Export database queries in their native formats
        if query_plan:
            queries_dir = export_dir / "queries"
            queries_dir.mkdir(exist_ok=True)

            for query in query_plan.queries:
                # Save as text file for copy/paste
                query_file = queries_dir / f"{query.database_name}_query.txt"
                query_file.write_text(query.boolean_query_string, encoding="utf-8")
                exported_files.append(str(query_file.relative_to(export_dir.parent)))

        # Generate PRISMA-compliant Markdown summary
        markdown_summary = ""
        if include_markdown:
            markdown_summary = self._build_markdown_summary(
                ctx, framing, concept_model, rq_set, blocks, query_plan, screening, search_results
            )
            summary_path = export_dir / "STRATEGY_PROTOCOL.md"
            summary_path.write_text(markdown_summary, encoding="utf-8")
            exported_files.append(str(summary_path.relative_to(export_dir.parent)))

        # Create export bundle
        bundle = StrategyExportBundle(
            project_id=project_id,
            exported_files=exported_files,
            notes=f"Export includes {papers_exported} papers in {len(export_formats)} formats. " +
                  f"Deduplication rate: {export_stats.get('deduplication_rate', 0)}%",
            model_metadata=ModelMetadata(
                model_name=self.model_service.model_name,
                mode=self.model_service.mode,
                generated_at=datetime.now(UTC)
            ),
        )

        self.persistence_service.save_artifact(bundle, project_id, "StrategyExportBundle")

        # Build user prompts
        prompts = [
            f"✅ Exported {len(exported_files)} files to {export_dir}",
        ]

        if papers_exported > 0:
            prompts.append(f"✅ Exported {papers_exported} papers in formats: {', '.join(export_formats)}")
            prompts.append(f"   Databases: {', '.join(export_stats.get('databases', []))}")

        if include_markdown:
            prompts.append(f"✅ PRISMA protocol saved to STRATEGY_PROTOCOL.md")

        prompts.extend([
            "📁 All files available in export/ directory",
            "💡 Import .bib file into Zotero/Mendeley for citation management",
            "💡 Use .csv file for screening in Excel/Google Sheets",
        ])

        return StageResult(
            stage_name="strategy-export",
            draft_artifact=bundle,
            metadata=bundle.model_metadata,
            prompts=prompts,
            validation_errors=[],
        )

    def _build_markdown_summary(self, ctx, framing, concept_model, rq_set, blocks, query_plan, screening, search_results=None) -> str:
        """Build PRISMA-compliant Markdown summary."""
        lines = [
            f"# Systematic Literature Review Protocol",
            f"## Project: {ctx.title}",
            "",
            f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
            f"**Project ID:** {ctx.id}",
            "",
            "---",
            "",
            "## 1. Problem Framing",
            "",
            framing.problem_statement,
            "",
            "### Research Goals",
            *[f"- {g}" for g in framing.goals],
            "",
            "### Scope",
            "**Included:**",
            *[f"- {s}" for s in framing.scope_in],
            "",
            "**Excluded:**",
            *[f"- {s}" for s in framing.scope_out],
            "",
            "---",
            "",
            "## 2. Key Concepts (PICO Elements)",
            "",
            *[f"- **{c.label}** ({c.type}): {c.description}" for c in concept_model.concepts[:20]],
            "",
            "---",
            "",
            "## 3. Research Questions",
            "",
            *[f"{i+1}. {q.text}" for i, q in enumerate(rq_set.questions)],
            "",
            "---",
            "",
            "## 4. Search Strategy",
            "",
            "### Search Concept Blocks",
            "",
            *[f"**{b.label}:** {', '.join(b.terms_included[:10])}" for b in blocks.blocks],
            "",
            "### Database Queries",
            "",
        ]

        for q in query_plan.queries:
            lines.append(f"#### {q.database_name.upper()}")
            lines.append("")
            lines.append("```")
            lines.append(q.boolean_query_string)
            lines.append("```")
            lines.append("")
            if q.complexity_analysis:
                lines.append(f"- **Complexity:** {q.complexity_analysis.get('complexity_level')}")
                lines.append(f"- **Expected Results:** {q.complexity_analysis.get('expected_results')}")
                lines.append("")

        # Add search results section if available
        if search_results:
            lines.extend([
                "---",
                "",
                "## 5. Search Results",
                "",
                f"**Total Papers Retrieved:** {search_results.total_results}",
                f"**After Deduplication:** {search_results.deduplicated_count}",
                f"**Databases Searched:** {', '.join(search_results.databases_searched)}",
                f"**Execution Time:** {search_results.execution_time_seconds:.2f} seconds",
                "",
            ])

            if search_results.deduplication_stats:
                lines.extend([
                    "### Deduplication Statistics",
                    "",
                    f"- Original count: {search_results.deduplication_stats.get('original_count', 0)}",
                    f"- Duplicates removed: {search_results.deduplication_stats.get('duplicates_removed', 0)}",
                    f"- Deduplication rate: {search_results.deduplication_stats.get('deduplication_rate', 0)}%",
                    "",
                ])

            lines.extend([
                "### Exported Files",
                "",
                "- `papers.csv` - All papers in CSV format",
                "- `papers.bib` - BibTeX citations for reference managers",
                "- `papers.ris` - RIS format for EndNote/Mendeley",
                "",
            ])

        if screening:
            lines.extend([
                "---",
                "",
                "## 6. Screening Criteria",
                "",
                "### Inclusion Criteria",
                "",
                *[f"- {c}" for c in screening.inclusion_criteria],
                "",
                "### Exclusion Criteria",
                "",
                *[f"- {c}" for c in screening.exclusion_criteria],
                "",
            ])

        lines.extend([
            "---",
            "",
            "## PRISMA Compliance",
            "",
            "This protocol follows PRISMA guidelines for systematic reviews:",
            "",
            "- ✅ Research questions clearly defined",
            "- ✅ Search strategy documented and reproducible",
            "- ✅ Multiple databases searched",
            "- ✅ Inclusion/exclusion criteria specified",
            "- ✅ Deduplication performed",
            "",
            "---",
            "",
            f"*Generated by Strategy Pipeline v1.0 | {datetime.now(UTC).strftime('%Y-%m-%d')}*",
        ])

        return "\n".join(lines)

    def _export_papers_csv(self, papers: List[Dict], export_dir: Path) -> Path:
        """Export papers to CSV format."""
        csv_path = export_dir / "papers.csv"

        with open(csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'Title', 'Authors', 'Year', 'Venue', 'DOI', 'URL',
                'Abstract', 'Citations', 'Provider', 'ArXiv ID', 'PubMed ID'
            ])

            # Rows
            for paper in papers:
                authors_str = "; ".join([
                    f"{a.get('given_name', '')} {a.get('family_name', '')}".strip()
                    for a in paper.get('authors', [])
                ][:10])  # Limit to first 10 authors

                writer.writerow([
                    paper.get('title', ''),
                    authors_str,
                    paper.get('year', ''),
                    paper.get('venue', ''),
                    paper.get('doi', ''),
                    paper.get('url', ''),
                    paper.get('abstract', '')[:500] if paper.get('abstract') else '',  # Truncate long abstracts
                    paper.get('cited_by_count', ''),
                    paper.get('provider', ''),
                    paper.get('arxiv_id', ''),
                    paper.get('pmid', ''),
                ])

        logger.info(f"Exported {len(papers)} papers to CSV: {csv_path}")
        return csv_path

    def _export_papers_bibtex(self, papers: List[Dict], export_dir: Path) -> Path:
        """Export papers to BibTeX format."""
        bib_path = export_dir / "papers.bib"

        bib_entries = []
        for i, paper in enumerate(papers, 1):
            # Generate citation key
            first_author = paper.get('authors', [{}])[0].get('family_name', 'Unknown') if paper.get('authors') else 'Unknown'
            year = paper.get('year', 'YYYY')
            key = f"{first_author}{year}_{i}"

            # Determine entry type
            entry_type = "article"  # Default
            if paper.get('arxiv_id'):
                entry_type = "misc"  # arXiv preprints

            # Build author string
            authors_list = []
            for author in paper.get('authors', [])[:20]:  # Limit to 20 authors
                family = author.get('family_name', '')
                given = author.get('given_name', '')
                if family:
                    authors_list.append(f"{family}, {given}" if given else family)
            authors_str = " and ".join(authors_list) if authors_list else "Unknown"

            # Build BibTeX entry
            entry = [
                f"@{entry_type}{{{key},",
                f"  title = {{{paper.get('title', 'Untitled')}}},",
                f"  author = {{{authors_str}}},",
            ]

            if year and year != 'YYYY':
                entry.append(f"  year = {{{year}}},")

            if paper.get('venue'):
                entry.append(f"  journal = {{{paper.get('venue')}}},")

            if paper.get('doi'):
                entry.append(f"  doi = {{{paper.get('doi')}}},")

            if paper.get('url'):
                entry.append(f"  url = {{{paper.get('url')}}},")

            if paper.get('abstract'):
                # Escape special characters in abstract
                abstract = paper.get('abstract', '').replace('{', '\\{').replace('}', '\\}')
                entry.append(f"  abstract = {{{abstract}}},")

            if paper.get('arxiv_id'):
                entry.append(f"  archivePrefix = {{arXiv}},")
                entry.append(f"  eprint = {{{paper.get('arxiv_id')}}},")

            entry.append("}")
            bib_entries.append("\n".join(entry))

        bib_path.write_text("\n\n".join(bib_entries), encoding='utf-8')
        logger.info(f"Exported {len(papers)} papers to BibTeX: {bib_path}")
        return bib_path

    def _export_papers_ris(self, papers: List[Dict], export_dir: Path) -> Path:
        """Export papers to RIS format (for EndNote, Mendeley, Zotero)."""
        ris_path = export_dir / "papers.ris"

        ris_entries = []
        for paper in papers:
            # Determine document type
            typ = "JOUR"  # Journal article (default)
            if paper.get('arxiv_id'):
                typ = "UNPB"  # Unpublished work

            entry = [
                f"TY  - {typ}",
                f"TI  - {paper.get('title', 'Untitled')}",
            ]

            # Authors
            for author in paper.get('authors', [])[:20]:
                family = author.get('family_name', '')
                given = author.get('given_name', '')
                if family:
                    entry.append(f"AU  - {family}, {given}" if given else f"AU  - {family}")

            # Year
            if paper.get('year'):
                entry.append(f"PY  - {paper.get('year')}")

            # Journal/Venue
            if paper.get('venue'):
                entry.append(f"JO  - {paper.get('venue')}")

            # DOI
            if paper.get('doi'):
                entry.append(f"DO  - {paper.get('doi')}")

            # URL
            if paper.get('url'):
                entry.append(f"UR  - {paper.get('url')}")

            # Abstract
            if paper.get('abstract'):
                entry.append(f"AB  - {paper.get('abstract')}")

            # Keywords/Tags
            if paper.get('provider'):
                entry.append(f"KW  - {paper.get('provider')}")

            # arXiv ID
            if paper.get('arxiv_id'):
                entry.append(f"N1  - arXiv:{paper.get('arxiv_id')}")

            # End of record
            entry.append("ER  - ")
            entry.append("")

            ris_entries.append("\n".join(entry))

        ris_path.write_text("\n".join(ris_entries), encoding='utf-8')
        logger.info(f"Exported {len(papers)} papers to RIS: {ris_path}")
        return ris_path

