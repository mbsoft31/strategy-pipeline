## Plan: LLM Integration with OpenAlex Validation

The strategy-pipeline has a fully functional syntax engine supporting 6 academic databases (PubMed, Scopus, arXiv, OpenAlex, Semantic Scholar, CrossRef) with comprehensive tests. The pipeline implements Stages 0-1 (Project Setup and Problem Framing) but currently uses a mock model service. The next critical enhancement is integrating real LLM capabilities with validation to transform the tool from a prototype into a production-ready AI research assistant that generates reliable, validated research queries.

### Steps

1. **Implement LLM Provider Layer** - Create `src/services/llm_provider.py` with abstract `LLMProvider` base class defining `generate()` and `generate_with_critique()` methods, then implement concrete providers: `OpenAIProvider` (using OpenAI API with GPT-4), `MockProvider` (preserving existing test functionality), and `CachedProvider` (wrapping any provider with filesystem caching to reduce API costs during development), plus update `src/config.py` with `LLMConfig` class containing provider selection, API keys, model parameters (temperature, max_tokens), and retry settings.

2. **Design Prompt Architecture** - Create `src/services/prompts.py` as centralized prompt management module with system prompts for each persona (Academic Supervisor for critique, Research Methodologist for framing, Librarian for search strategy), user prompt templates using f-strings with structured placeholders, and critique-specific prompts implementing Draft→Critique→Refine reflection pattern with explicit rubrics (clarity, specificity, feasibility, novelty), separating AI intelligence from code logic to enable rapid iteration on prompt quality.

3. **Implement Critique Loop in Model Service** - Update `src/services/simple_model_service.py` to use LLM provider for `generate_problem_framing()` by first generating draft ProblemFraming using Research Methodologist prompt, then invoking Academic Supervisor critique with explicit evaluation rubric, finally refining draft based on critique feedback, storing full critique report in `ProblemFraming.critique_report` field (add to model if missing), and including metadata tracking iterations, model used, and critique quality score.

4. **Build OpenAlex Validation Service** - Create `src/services/validation_service.py` implementing "reality check" by querying OpenAlex API for each suggested term/keyword to verify literature existence, flagging hallucinations (zero hits) with severity levels (critical for core concepts, warning for peripheral terms), suggesting validated alternatives with actual hit counts from OpenAlex, and caching validation results by term to avoid redundant API calls, providing structured `ValidationReport` with flagged terms, hit counts, and alternative suggestions.

5. **Integrate Validation into Pipeline** - Update `generate_problem_framing()` workflow to run OpenAlex validation immediately after LLM generation but before presenting to user, automatically re-prompt LLM with validation feedback if critical hallucinations detected (automatic refinement loop), include validation report in `ProblemFraming` metadata for user transparency, and add validation warnings to web UI with color-coded severity (red for hallucinations, yellow for low-hit terms, green for validated terms with hit counts).

6. **Enhance Web UI for Critique and Validation** - Update Flask templates to display critique reports in expandable sections on problem framing review page, show validation warnings with inline hit counts and alternative suggestions, add toggle to view draft vs. refined versions side-by-side, implement approval workflow that requires acknowledgment of validation warnings before proceeding, and create dedicated `/api/validate` endpoint for on-demand term validation during editing.

### Further Considerations

1. **Cost Management** - CachedProvider should implement intelligent cache invalidation (expire after 7 days or on model version change), development mode should default to MockProvider to avoid API costs, and validation service should batch OpenAlex queries where possible since API is free but rate-limited. Consider adding cost tracking middleware to log API usage and estimated costs per project.

2. **Critique Quality Metrics** - Should critique loop run fixed iterations (e.g., always 1 critique cycle) or continue until quality threshold met (e.g., critique score > 8/10)? Recommend configurable max iterations (default 2) with early stopping if critique indicates "acceptable quality" to balance quality vs. API cost, storing all iterations in metadata for transparency.

3. **Validation Strictness** - OpenAlex validation could be strict (block terms with <10 hits) or permissive (warn only). Recommend tiered approach: block hallucinations (0 hits), warn on rare terms (<100 hits), suggest refinements for moderate terms (100-1000 hits), and validate high-frequency terms (>1000 hits) with green checkmark, allowing users to override warnings with explicit acknowledgment for novel/emerging research areas.

4. **Fallback Strategies** - When OpenAI API fails (rate limits, downtime), should system fall back to MockProvider or queue requests? Recommend exponential backoff with 3 retries, then graceful degradation to cached responses if available, finally presenting user with option to continue with mock data or wait for API recovery, storing failed requests for later retry.

5. **Multi-Model Support** - Current plan uses GPT-4 for all tasks, but cheaper models (GPT-3.5-turbo) might suffice for validation or routine framing. Consider model routing: GPT-4 for critique/complex reasoning, GPT-3.5-turbo for straightforward generation, and Claude/local models as fallback options, configured via `LLMConfig` model selection per task type.

