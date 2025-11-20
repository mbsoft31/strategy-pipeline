## Plan: Enhance HITL Pipeline with LLM Integration and Syntax Engine

The repository implements Stages 0-1 (Project Setup and Problem Framing) with a simple local model service and web UI. The next-steps docs propose three main enhancements: (1) LLM-powered critique loop, (2) database syntax engine, and (3) real OpenAI integration. This plan integrates these features into the existing architecture while adopting proven patterns from the `slr` scratch project, maintaining UI-agnostic design and production-quality standards.

### Key Insights from SLR Scratch Project

The scratch project in `docs/next-steps/scratch_project/slr/` demonstrates production-ready patterns we should adopt:

- **Pydantic models** (`slr/core/models.py`) for validation and type safety vs plain dataclasses
- **Provider abstraction layer** (`slr/providers/base.py`) with BaseProvider pattern for extensibility
- **Rate limiting** (`slr/utils/rate_limit.py`) with TokenBucket algorithm for API protection
- **Retry logic** (`slr/utils/retry.py`) with exponential backoff for resilience
- **Query parsing/translation** (`slr/providers/query_translator.py`) framework for Boolean syntax
- **Exception hierarchy** (`slr/utils/exceptions.py`) for granular error handling
- **Configuration management** (`slr/core/config.py`) with YAML + environment variables
- **Field extraction utilities** (`slr/providers/normalizer.py`) for robust data normalization

### Steps

1. **Enhance Data Models with Validation** - Migrate `src/models.py` from dataclasses to Pydantic BaseModel, adding field validators (like DOI normalization), keeping backward compatibility via `model_validate` for existing JSON files in `data/` folder.

2. **Build Configuration System** - Create `src/config.py` using Pydantic with `Settings` class loading from `.env` file (LLM provider, API keys, rate limits, timeouts), plus optional YAML config for advanced users, following `slr/core/config.py` pattern.

3. **Implement LLM Provider Layer** - Create `src/services/llm_provider.py` with abstract `BaseLLMProvider` class (similar to `BaseProvider` in scratch), concrete `OpenAIProvider` and `MockProvider`, integrate `TokenBucket` rate limiter from scratch project, add retry logic with exponential backoff.

4. **Add Exception Hierarchy** - Create `src/utils/exceptions.py` defining `PipelineException`, `LLMProviderError`, `ValidationError`, `RateLimitError` following scratch project's exception patterns for better error handling throughout pipeline.

5. **Create Prompt Management Module** - Build `src/services/prompts.py` as prompt registry with versioned templates, support for Jinja2 templating for complex prompts, store prompt metadata (version, model compatibility, expected output schema).

6. **Enhance ModelService with Critique Pattern** - Refactor `src/services/simple_model_service.py` to use LLM provider, implement Draft→Critique→Refine loop storing critique in `ProblemFraming.critique_report`, add `research_gap` field to `ProblemFraming` model per OPTION-1 specification.

7. **Build Query Translation Framework** - Create `src/search/query_parser.py` adapting `QueryParser` from scratch project to parse Boolean queries, support field-specific search (title, abstract, MeSH terms), handle operators (AND, OR, NOT) and parentheses.

8. **Implement Database Syntax Engine** - Create `src/search/` package with `models.py` (SearchTerm, ConceptBlock, QueryPlan using Pydantic), `dialects.py` (PubMedDialect, ScopusDialect using strategy pattern from scratch), `builder.py` (SyntaxBuilder orchestrator), include validation logic ensuring syntactically correct output.

9. **Add OpenAlex Validation Service** - Create `src/services/validation_service.py` adapting OpenAlex provider pattern from scratch, implement hit count checking for terms/concepts, add caching layer to avoid redundant API calls, integrate rate limiting (9 req/s for polite pool).

10. **Implement Stage 2: Research Questions** - Create `src/stages/research_questions.py` following existing stage pattern in `src/stages/base.py`, implement PICO framework extraction (Population, Intervention, Comparison, Outcome), generate typed questions (descriptive, comparative, evaluative).

11. **Add Utility Modules** - Create `src/utils/rate_limit.py` with `TokenBucket` class from scratch project, `src/utils/retry.py` with `retry_with_backoff` decorator, `src/utils/field_extractor.py` for safe nested field access in LLM responses.

12. **Update Tests and Documentation** - Add unit tests for syntax engine (like `test_syntax.py` from OPTION-2), test LLM provider with mocks, update `requirements.txt` with `pydantic`, `openai`, `python-dotenv`, `pyyaml`, `requests`, create migration guide for existing projects.

### Further Considerations

1. **Pydantic vs Dataclasses Trade-off** - Pydantic adds validation overhead but provides runtime type checking and automatic serialization - should we migrate all models at once or incrementally? Recommend incremental starting with new models, use `from __future__ import annotations` for forward compatibility.

2. **Configuration Priority** - With both `.env` and YAML config, what takes precedence for conflicting values? Suggest: CLI args > Environment variables > YAML file > Defaults, document in README.

3. **Rate Limiting Strategy** - Should each provider (OpenAI, OpenAlex) have independent rate limiters or shared token bucket? Recommend independent limiters with provider-specific configs to avoid cascading failures.

4. **Error Handling Philosophy** - Should stages fail fast on LLM errors or gracefully degrade to mock data? Recommend configurable behavior via `FAIL_ON_LLM_ERROR` env var, default to fail fast in production, graceful in development.

5. **Backward Compatibility for Data** - Existing projects use old format - should we auto-migrate on load or require manual migration? Suggest detecting format version in JSON, auto-migrate with backup creation, log migration actions.

6. **Testing Without API Costs** - How to test LLM integration without burning API credits? Implement `CachedLLMProvider` wrapper that stores responses in local cache, replay mode for CI/CD, VCR-like cassette recording for deterministic tests.

### Implementation Priority (Revised - Interleaved Approach)

**Sprint 1: Minimal Foundation + Syntax Engine (Days 1-3)**
- Day 1 Morning: Step 2 - Configuration system (`.env` only, skip YAML)
- Day 1 Afternoon: Step 4 - Exception hierarchy
- Day 2: Step 7-8 - Query parser + Syntax engine (the "moat")
- Day 3: Unit tests for syntax validation + demo

**Sprint 2: LLM Integration (Days 4-6)**
- Day 4 Morning: Step 11 - Rate limiter + Retry (needed for APIs)
- Day 4 Afternoon: Step 3 - LLM provider layer (OpenAI + Mock)
- Day 5: Step 5 - Prompt management + Step 6 - Critique loop
- Day 6: Integration tests + demo

**Sprint 3: Validation + Stage 2 (Days 7-9)**
- Day 7: Step 1 - Migrate to Pydantic (incremental, start with new models)
- Day 8: Step 9 - OpenAlex validation service
- Day 9: Step 10 - Research Questions stage

**Sprint 4: Polish + Documentation (Days 10-12)**
- Day 10: Step 11 - Field extractor utility
- Day 11: Step 12 - Comprehensive tests
- Day 12: Documentation, migration guide, examples

**Why This Order:**
- Get visible "moat" feature (Syntax Engine) working by Day 3
- Add resilience (rate limiting) only when needed for APIs
- Pydantic migration happens incrementally, not as blocking work
- Each sprint delivers a working demo

