"""LLM Provider abstraction layer for HITL Research Strategy Pipeline.

This module provides a unified interface for interacting with different LLM providers
(OpenAI, Mock, Cached) with error handling, retries, and JSON parsing.
"""

import json
import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from src.config import get_config, LLMProvider as ProviderEnum
from src.utils.exceptions import LLMProviderError, RateLimitError, AuthenticationError

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text from prompts.

        Args:
            system_prompt: System message defining the AI's role/persona
            user_prompt: User message with the actual task

        Returns:
            Generated text response

        Raises:
            LLMProviderError: On provider-specific errors
            RateLimitError: When rate limits are exceeded
            AuthenticationError: On authentication failures
        """
        pass

    def clean_json_response(self, response: str) -> Dict[str, Any]:
        """Extract and parse JSON from LLM response.

        LLMs often wrap JSON in markdown code blocks. This method
        strips those and parses the JSON.

        Args:
            response: Raw LLM response text

        Returns:
            Parsed JSON as dictionary

        Raises:
            LLMProviderError: If JSON parsing fails
        """
        # Strip markdown fencing
        clean_str = re.sub(r"```json\s*", "", response, flags=re.IGNORECASE)
        clean_str = re.sub(r"```\s*$", "", clean_str)
        clean_str = clean_str.strip()

        try:
            return json.loads(clean_str)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {clean_str}")
            raise LLMProviderError(
                f"Invalid JSON from LLM: {str(e)}",
                details={"response": response[:500]}  # Truncate for logging
            )


class OpenAIProvider(LLMProvider):
    """OpenAI API implementation."""

    def __init__(self):
        """Initialize OpenAI provider with config."""
        config = get_config()
        api_key = config.llm.openai_api_key

        if not api_key:
            raise AuthenticationError(
                "OpenAI API key not found in config. "
                "Set LLM__OPENAI_API_KEY in .env or environment."
            )

        # Import here to make openai optional for non-OpenAI users
        try:
            from openai import OpenAI
            import openai as openai_module
            self.openai_module = openai_module
        except ImportError:
            raise LLMProviderError(
                "OpenAI package not installed. Run: pip install openai"
            )

        self.client = OpenAI(api_key=api_key)
        self.model = config.llm.openai_model
        self.temperature = config.llm.openai_temperature
        self.max_tokens = config.llm.openai_max_tokens
        self.timeout = config.llm.timeout

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate text using OpenAI API.

        Args:
            system_prompt: System message
            user_prompt: User message

        Returns:
            Generated text

        Raises:
            RateLimitError: On rate limit
            AuthenticationError: On auth failure
            LLMProviderError: On other errors
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )
            return response.choices[0].message.content or ""

        except self.openai_module.RateLimitError as e:
            logger.warning(f"OpenAI rate limit exceeded: {e}")
            raise RateLimitError(
                "OpenAI rate limit exceeded",
                retry_after=20,
                details={"error": str(e)}
            )
        except self.openai_module.AuthenticationError as e:
            logger.error(f"OpenAI authentication failed: {e}")
            raise AuthenticationError(
                f"OpenAI authentication failed: {str(e)}",
                details={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise LLMProviderError(
                f"OpenAI API error: {str(e)}",
                details={"error": str(e)}
            )


class MockProvider(LLMProvider):
    """Mock implementation for testing and offline development.

    This provider returns realistic mock responses based on keyword detection
    in the prompts. Useful for:
    - Testing without API costs
    - Offline development
    - CI/CD pipelines
    """

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate mock response based on prompt content.

        Args:
            system_prompt: System message (used for context)
            user_prompt: User message (analyzed for keywords)

        Returns:
            Mock JSON response appropriate to the task
        """
        # Detect task type from prompts
        combined = (system_prompt + " " + user_prompt).lower()

        # Stage 0: Project Context generation
        if "project context" in combined or "raw idea" in user_prompt.lower():
            return json.dumps({
                "title": "Mock Project: AI in Healthcare Decision Support",
                "discipline": "Health Informatics",
                "short_description": "A systematic investigation of large language model hallucinations in clinical decision support systems and their impact on patient safety.",
                "initial_keywords": ["LLM", "Hallucination", "Clinical Decision Support", "Patient Safety", "Medical AI"],
                "constraints": {"time": "6 months", "budget": "limited", "access": "public datasets only"}
            })

        # Stage 1: Refine/Problem Framing (check before critique since refine prompts may mention critique)
        elif "refine" in combined or "problem framing" in combined or "based on critique" in user_prompt.lower():
            return json.dumps({
                "problem_statement": "Healthcare systems lack validated methods to detect and quantify hallucinations in Large Language Model outputs used for clinical decision support, creating potential patient safety risks.",
                "research_gap": "No standardized metrics exist for measuring LLM factuality in clinical contexts, and current evaluation methods from NLP don't account for medical domain knowledge requirements.",
                "goals": [
                    "Define operational metrics for detecting LLM hallucinations in clinical notes",
                    "Benchmark hallucination rates across GPT-4, Claude, and Llama-2 on clinical tasks",
                    "Propose a validation framework for medical AI systems"
                ],
                "scope_in": [
                    "Clinical notes and summaries",
                    "Commercial LLMs (GPT-4, Claude, Llama-2)",
                    "English language medical text",
                    "Factual accuracy as primary outcome"
                ],
                "scope_out": [
                    "Medical imaging or diagnostic AI",
                    "Patient-facing chatbots",
                    "Non-English languages",
                    "Predictive models or risk scores"
                ],
                "key_concepts": [
                    {"label": "Large Language Models", "type": "Intervention", "description": "GPT-4, Claude, Llama-2"},
                    {"label": "Clinical Notes", "type": "Population", "description": "Patient medical records and clinical documentation"},
                    {"label": "Hallucination Detection", "type": "Outcome", "description": "Factual errors in AI-generated text"},
                    {"label": "Patient Safety", "type": "Outcome", "description": "Risk of harm from incorrect information"},
                    {"label": "Validation Framework", "type": "Methodology", "description": "Systematic evaluation approach"}
                ]
            })

        # Stage 1: Critique (after refine check)
        elif "critique" in combined or "supervisor" in system_prompt.lower():
            return json.dumps({
                "critique_summary": "The scope is too broad. 'AI in healthcare' encompasses thousands of applications. Narrow to specific AI type (e.g., LLMs, not all AI) and specific healthcare domain (e.g., clinical notes, not all medical data). Define 'hallucination' operationally - are we measuring factual errors, citation accuracy, or diagnostic mistakes?",
                "feasibility_score": 6,
                "specific_issues": [
                    "Vague term: 'AI' should specify 'Large Language Models'",
                    "Unclear outcome: Define measurable hallucination metrics",
                    "Missing comparator: Against what baseline?",
                    "Scope creep: 'Healthcare' is too broad - pick one subdomain"
                ]
            })

        # Default fallback
        else:
            return json.dumps({
                "message": "Mock response - provider is in test mode",
                "note": "Configure LLM__PROVIDER=openai for real AI"
            })


def get_llm_provider() -> LLMProvider:
    """Factory function to get configured LLM provider.

    Returns:
        Configured LLMProvider instance based on config

    Raises:
        ConfigurationError: If provider configuration is invalid
    """
    config = get_config()

    if config.llm.provider == ProviderEnum.OPENAI:
        return OpenAIProvider()
    elif config.llm.provider == ProviderEnum.MOCK:
        return MockProvider()
    elif config.llm.provider == ProviderEnum.CACHED:
        # TODO: Implement CachedProvider wrapper
        logger.warning("CachedProvider not yet implemented, falling back to Mock")
        return MockProvider()
    else:
        logger.warning(f"Unknown provider {config.llm.provider}, using Mock")
        return MockProvider()

