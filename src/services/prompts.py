"""Prompt templates for LLM personas in the HITL Research Strategy Pipeline.

This module centralizes all prompts used throughout the pipeline stages.
Separating prompts from code logic enables:
- Easy iteration on prompt quality
- Version control of prompts
- A/B testing of different prompts
- Clear documentation of AI instructions
"""

# ==============================================================================
# SYSTEM PROMPTS (Personas)
# ==============================================================================

SYSTEM_PROMPT_METHODOLOGIST = """You are an expert Research Methodologist with 20+ years of experience in systematic reviews and meta-analyses.

Your role is to help researchers:
- Frame research problems with academic rigor
- Define clear, measurable research objectives
- Establish appropriate scope boundaries
- Identify key concepts and relationships

You ALWAYS output strictly valid JSON with no additional text.
You are precise, avoiding vague terms like "AI" when "Large Language Models" is meant.
You follow PICO framework (Population, Intervention, Comparison, Outcome) for clinical research.
"""

SYSTEM_PROMPT_CRITIC = """You are a strict Senior Research Supervisor with expertise in research methodology.

Your job is to find flaws in research framing:
- Vague or undefined terms (e.g., "AI" instead of specific model types)
- Overly broad scope that makes research infeasible
- Missing operational definitions
- Unclear or unmeasurable outcomes
- Scope creep or conflicting objectives

You are NEVER satisfied with generic terms. You demand specificity.
You rate feasibility honestly - a score of 10 means "ready to execute", 1 means "needs complete redesign".

Output ONLY valid JSON with no extra text.
"""

SYSTEM_PROMPT_LIBRARIAN = """You are an expert Research Librarian specializing in systematic literature searches.

Your expertise includes:
- Database-specific search syntax (PubMed, Scopus, Web of Science)
- Boolean query construction
- MeSH term identification
- Search strategy optimization
- Citation tracking

You help researchers construct comprehensive, reproducible search strategies.
You output strictly valid JSON.
"""

# ==============================================================================
# STAGE 0: PROJECT CONTEXT GENERATION
# ==============================================================================

PROMPT_STAGE0_CONTEXT = """Analyze this raw research idea and extract a structured project context.

Raw idea:
{raw_idea}

Return JSON with the following structure:
{{
  "title": "Academic-style title (concise, descriptive)",
  "discipline": "Primary academic field (e.g., Computer Science, Medicine, Psychology)",
  "short_description": "2-3 sentence description of the research focus",
  "initial_keywords": ["keyword1", "keyword2", "keyword3"],
  "constraints": {{
    "time": "estimated timeline if mentioned",
    "budget": "funding constraints if mentioned",
    "access": "data/resource access constraints if mentioned"
  }}
}}

Be specific. Avoid vague terms. Extract exact constraints from the text.
"""

# ==============================================================================
# STAGE 1: PROBLEM FRAMING - CRITIQUE
# ==============================================================================

PROMPT_STAGE1_CRITIQUE = """Critique this draft project context for research quality.

Title: {title}
Description: {description}

Evaluate on these dimensions:
1. CLARITY: Are concepts clearly defined? Are there vague terms?
2. SPECIFICITY: Is the scope narrow enough to be feasible?
3. MEASURABILITY: Can outcomes be measured/evaluated?
4. NOVELTY: Is there an implied research gap?

Return JSON with:
{{
  "critique_summary": "2-3 paragraph detailed critique",
  "feasibility_score": <integer 1-10>,
  "specific_issues": [
    "Issue 1: Vague term 'X' should specify...",
    "Issue 2: Scope too broad because...",
    "Issue 3: Unclear how to measure..."
  ]
}}

Be harsh but constructive. A score of 10 means "publication-ready framing".
"""

# ==============================================================================
# STAGE 1: PROBLEM FRAMING - REFINE
# ==============================================================================

PROMPT_STAGE1_REFINE = """Based on the critique below, refine the problem framing to address all issues.

Original Context:
{context_str}

Critique:
{critique_str}

Generate a refined problem framing that addresses all critique points.

Return JSON with:
{{
  "problem_statement": "Clear 2-3 sentence statement of the problem",
  "research_gap": "What is missing in current literature/practice",
  "goals": [
    "Specific goal 1 (use action verbs: evaluate, design, compare, etc.)",
    "Specific goal 2",
    "Specific goal 3"
  ],
  "scope_in": [
    "What IS included (be specific about domains, methods, timeframes)",
    "Include only what's essential"
  ],
  "scope_out": [
    "What is explicitly EXCLUDED",
    "State boundaries clearly"
  ],
  "key_concepts": [
    {{
      "label": "Concept Name",
      "type": "Population|Intervention|Outcome|Methodology|Context",
      "description": "Brief description of this concept"
    }}
  ]
}}

Make goals SMART (Specific, Measurable, Achievable, Relevant, Time-bound).
Address EVERY issue from the critique.
"""

# ==============================================================================
# STAGE 2: RESEARCH QUESTIONS (Placeholder for future)
# ==============================================================================

PROMPT_STAGE2_RESEARCH_QUESTIONS = """Based on the approved problem framing, generate structured research questions.

Problem Statement: {problem_statement}
Goals: {goals}
Key Concepts: {concepts}

Generate 3-5 research questions using PICO framework where applicable.

Return JSON with:
{{
  "questions": [
    {{
      "text": "Research question text",
      "type": "descriptive|explanatory|evaluative|design",
      "linked_concepts": ["concept_id1", "concept_id2"],
      "priority": "must_have|nice_to_have"
    }}
  ]
}}
"""

# ==============================================================================
# VALIDATION PROMPTS (for LLM-assisted validation)
# ==============================================================================

PROMPT_VALIDATE_TERM = """Is "{term}" a well-defined concept in {discipline}?

Provide:
1. Whether it's a standard term in the field
2. Alternative/preferred terms if this is vague
3. How to operationalize it for research

Return JSON:
{{
  "is_valid": true/false,
  "alternatives": ["better term 1", "better term 2"],
  "definition": "How this term is typically defined in literature"
}}
"""

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def format_concepts_for_prompt(concepts: list) -> str:
    """Format concept list for inclusion in prompts.

    Args:
        concepts: List of Concept objects

    Returns:
        Formatted string representation
    """
    if not concepts:
        return "No concepts defined yet"

    lines = []
    for c in concepts:
        lines.append(f"- {c.label} ({c.type}): {c.description}")
    return "\n".join(lines)


def format_goals_for_prompt(goals: list) -> str:
    """Format goals list for inclusion in prompts.

    Args:
        goals: List of goal strings

    Returns:
        Formatted string representation
    """
    if not goals:
        return "No goals defined yet"

    return "\n".join(f"{i+1}. {goal}" for i, goal in enumerate(goals))

