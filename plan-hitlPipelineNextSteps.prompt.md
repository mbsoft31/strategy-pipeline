## Plan: Enhance HITL Pipeline with LLM Integration and Syntax Engine

The repository implements Stages 0-1 (Project Setup and Problem Framing) with a simple local model service and web UI. The next-steps docs propose three main enhancements: (1) LLM-powered critique loop, (2) database syntax engine, and (3) real OpenAI integration. The plan will integrate these features into the existing architecture while maintaining UI-agnostic design and avoiding code duplication.

### Steps

1. **Implement LLM Provider Layer** - Create `src/services/llm_provider.py` with abstract `LLMProvider` base class and concrete `OpenAIProvider` and `MockProvider` implementations, plus `src/config.py` to manage API keys and settings from `.env` file per OPTION-3 pattern.
2. **Add Prompt Management Module** - Create `src/services/prompts.py` to centralize all LLM prompts as constants (system prompts and user prompt templates), separating AI intelligence from code logic and enabling easy iteration.
3. **Enhance ModelService with Critique Loop** - Update `SimpleModelService` to use the LLM provider for `suggest_project_context` and `generate_problem_framing`, implementing the Draft→Critique→Refine pattern from OPTION-1, storing critique reports in `ProblemFraming.critique_report` field.
4. **Build Database Syntax Engine** - Create `src/search/` package with `models.py` (SearchTerm, ConceptBlock, QueryPlan), `dialects.py` (PubMedDialect, ScopusDialect strategy pattern), and `builder.py` (SyntaxBuilder) per OPTION-2 specification, implementing deterministic Boolean query generation.
5. **Implement Stage 2 Research Questions** - Create `src/stages/research_questions.py` following existing stage pattern, implementing `generate_research_questions` in model service to produce structured questions using PICO framework from `ProblemFraming` and `ConceptModel`.
6. **Add Validation Layer with OpenAlex** - Implement "Reality Check" from OPTIONAL-FUTURE-PRIORITY by creating `src/services/validation_service.py` that queries OpenAlex API to verify keyword/term viability, flagging hallucinations with zero hit counts before presenting to users.

### Further Considerations

1. **LLM Provider Selection** - Should default to MockProvider for cost-free testing, or OpenAIProvider for better quality? Recommend config-driven toggle via `.env` LLM_PROVIDER setting.
2. **Backwards Compatibility** - Existing projects in `data/` folder use SimpleModelService format - should migration script update metadata, or gracefully handle both? Suggest version field in ModelMetadata.
3. **Stage Priority** - OPTION-1 (critique loop) delivers highest perceived value but requires paid API; OPTION-2 (syntax engine) works standalone with tests - should we implement syntax engine first to demonstrate technical moat, then add LLM? Recommend parallel implementation with syntax engine having unit tests independent of API costs.

