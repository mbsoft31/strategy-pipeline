# Quick Start Guide

Get started with Strategy Pipeline in 5 minutes.

## Step 1: Installation

```bash
git clone https://github.com/mbsoft31/strategy-pipeline.git
cd strategy-pipeline
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

See [Installation Guide](installation.md) for detailed setup.

## Step 2: Configure API Keys

Create `.env` file in project root:

```bash
# Required: Choose one LLM provider
OPENAI_API_KEY=sk-...
# OR
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Email for database APIs
SLR_MAILTO=your.email@example.com
```

## Step 3: Run Your First Pipeline

Create `my_first_review.py`:

```python
from src.controller import PipelineController
from src.services import IntelligentModelService, FilePersistenceService

# Initialize controller
controller = PipelineController(
    IntelligentModelService(),  # Uses OpenAI/Anthropic
    FilePersistenceService(base_dir="./data")
)

# Start a systematic review project
result = controller.start_project(
    "Systematic review of machine learning in healthcare diagnostics"
)
project_id = result.draft_artifact.id
print(f"✅ Project created: {project_id}")

# Approve initial project context
controller.approve_artifact(project_id, "ProjectContext")

# Run Stage 1: Problem Framing (extracts PICO elements)
result = controller.run_stage("problem-framing", project_id=project_id)
print(f"✅ Problem framing complete")
print(f"   PICO concepts: {len(result.draft_artifact.concept_model.concepts)}")

# Approve and continue
controller.approve_artifact(project_id, "ProblemFraming")
controller.approve_artifact(project_id, "ConceptModel")

# Run Stage 2: Research Questions
result = controller.run_stage("research-questions", project_id=project_id)
print(f"✅ Research questions generated: {len(result.draft_artifact.questions)}")
controller.approve_artifact(project_id, "ResearchQuestionSet")

# Run Stage 3: Concept Expansion
result = controller.run_stage("search-concept-expansion", project_id=project_id)
print(f"✅ Search concept blocks: {len(result.draft_artifact.blocks)}")
controller.approve_artifact(project_id, "SearchConceptBlocks")

# Run Stage 4: Database Query Plan
result = controller.run_stage("database-query-plan", project_id=project_id)
queries = result.draft_artifact.queries
print(f"✅ Database queries generated: {len(queries)}")
for query in queries:
    print(f"   - {query.database_name}: {query.boolean_query_string[:50]}...")
controller.approve_artifact(project_id, "DatabaseQueryPlan")

# Run Stage 5: Screening Criteria
result = controller.run_stage("screening-criteria", project_id=project_id)
criteria = result.draft_artifact
print(f"✅ Screening criteria:")
print(f"   Inclusion: {len(criteria.inclusion_criteria)} criteria")
print(f"   Exclusion: {len(criteria.exclusion_criteria)} criteria")
controller.approve_artifact(project_id, "ScreeningCriteria")

# Run Stage 7: Query Execution (retrieves papers)
print("\n🔍 Executing database searches (this may take 10-30 seconds)...")
result = controller.run_stage("query-execution", project_id=project_id)
search_results = result.draft_artifact

print(f"✅ Papers retrieved: {search_results.total_results}")
print(f"✅ After deduplication: {search_results.deduplicated_count}")
print(f"✅ Databases: {', '.join(search_results.databases_searched)}")
controller.approve_artifact(project_id, "SearchResults")

# Run Stage 6: Export to multiple formats
print("\n📦 Exporting papers...")
result = controller.run_stage("strategy-export", project_id=project_id)
export_bundle = result.draft_artifact

print(f"✅ Export complete!")
print(f"   Files: {len(export_bundle.exported_files)}")
print(f"\n📁 Output location: data/{project_id}/export/")
print(f"   - papers.csv (Excel-ready)")
print(f"   - papers.bib (Zotero/Mendeley)")
print(f"   - papers.ris (EndNote)")
print(f"   - STRATEGY_PROTOCOL.md (PRISMA protocol)")
```

## Step 4: Run the Script

```bash
python my_first_review.py
```

**Expected output:**
```
✅ Project created: project_20251127_143022
✅ Problem framing complete
   PICO concepts: 12
✅ Research questions generated: 4
✅ Search concept blocks: 3
✅ Database queries generated: 4
   - openalex: ((healthcare OR medical) AND (machine learning OR deep...
   - arxiv: (healthcare OR medical) AND (machine learning OR deep...
   - crossref: (healthcare OR medical) AND (machine learning OR deep...
   - semanticscholar: healthcare machine learning diagnostics...
✅ Screening criteria:
   Inclusion: 10 criteria
   Exclusion: 7 criteria

🔍 Executing database searches (this may take 10-30 seconds)...
✅ Papers retrieved: 347
✅ After deduplication: 295
✅ Databases: openalex, arxiv, crossref

📦 Exporting papers...
✅ Export complete!
   Files: 8

📁 Output location: data/project_20251127_143022/export/
   - papers.csv (Excel-ready)
   - papers.bib (Zotero/Mendeley)
   - papers.ris (EndNote)
   - STRATEGY_PROTOCOL.md (PRISMA protocol)
```

## Step 5: Import Papers into Citation Manager

### Import into Zotero

1. Open Zotero
2. File → Import
3. Select `data/project_XXX/export/papers.bib`
4. ✅ 295 papers imported with metadata

### Import into EndNote

1. Open EndNote
2. File → Import → File
3. Select `data/project_XXX/export/papers.ris`
4. Import Option: "Reference Manager (RIS)"
5. ✅ Papers imported

### Screen in Excel

1. Open `data/project_XXX/export/papers.csv` in Excel
2. Add columns: "Include", "Exclude", "Notes", "Reviewer"
3. Filter and sort as needed
4. ✅ Ready for title/abstract screening

## Next Steps

### Learn More
- 📚 [User Guide](../user-guide/quick-reference.md) - Comprehensive reference
- 🏗️ [Architecture](../architecture/overview.md) - How it works
- 🔌 [API Reference](../api-reference/index.md) - Detailed API docs

### Advanced Usage
- **Customize stages** - Edit artifacts before approval
- **Use different models** - Switch between GPT-4, Claude, etc.
- **Batch processing** - Run multiple projects in parallel
- **Web interface** - Use the React frontend (coming soon)

### Tips for Success

1. **Start with a focused question** - Narrow scope = better results
2. **Review each stage** - Don't blindly approve all artifacts
3. **Adjust queries if needed** - Edit DatabaseQueryPlan before Stage 7
4. **Save time with SimpleModelService** - Use for testing (no API costs)

## Troubleshooting

### No papers retrieved
- Check your research question is specific enough
- Verify internet connection
- Try running Stage 4 again with broader queries

### Too many papers (>1000)
- Refine inclusion criteria in Stage 5
- Narrow the research question
- Add temporal filters (e.g., last 5 years)

### API costs too high
- Use `SimpleModelService` for testing (no LLM calls)
- Limit stages to only what you need
- Use cheaper models (gpt-3.5-turbo vs gpt-4)

## Example Projects

See [Examples](../examples/) for more use cases:
- Basic systematic review
- Meta-analysis workflow
- Rapid review (skip stages 5-6)
- Custom query refinement

---

**Congratulations!** 🎉 You've completed your first systematic review pipeline.

**Next:** [Configuration Guide](configuration.md) for advanced options.

