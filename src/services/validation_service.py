"""OpenAlex validation service for verifying research terms against literature.

This service implements the "Reality Check" by querying the OpenAlex API
to verify that suggested terms/concepts actually exist in academic literature.
Helps prevent LLM hallucinations.
"""

import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests

from src.utils.exceptions import NetworkError, ValidationError

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single term against OpenAlex.

    Attributes:
        term: The term that was validated
        hit_count: Number of works found in OpenAlex
        is_valid: Whether the term is considered valid
        severity: Severity level (ok, warning, critical)
        suggestion: Alternative term suggestion if available
        sample_works: Sample work titles for reference
    """
    term: str
    hit_count: int
    is_valid: bool
    severity: str  # "ok", "warning", "critical"
    suggestion: Optional[str] = None
    sample_works: List[str] = None

    def __post_init__(self):
        """Initialize sample_works if None."""
        if self.sample_works is None:
            self.sample_works = []


@dataclass
class ValidationReport:
    """Complete validation report for a set of terms.

    Attributes:
        results: Dictionary mapping terms to their validation results
        total_terms: Total number of terms validated
        valid_count: Number of valid terms
        warning_count: Number of terms with warnings
        critical_count: Number of critical issues (hallucinations)
        summary: Human-readable summary
    """
    results: Dict[str, ValidationResult]
    total_terms: int
    valid_count: int
    warning_count: int
    critical_count: int
    summary: str


class ValidationService:
    """Validates research terms against OpenAlex API.

    OpenAlex is a free, open catalog of scholarly works.
    No authentication required!

    Thresholds:
    - 0 hits: CRITICAL (hallucination - term doesn't exist)
    - 1-99 hits: WARNING (rare term - verify it's correct)
    - 100-999 hits: OK (moderate frequency)
    - 1000+ hits: OK (well-established term)
    """

    BASE_URL = "https://api.openalex.org/works"
    TIMEOUT = 5  # seconds
    RATE_LIMIT_DELAY = 0.1  # 100ms between requests (10 req/sec)

    # Validation thresholds
    CRITICAL_THRESHOLD = 0  # No hits = hallucination
    WARNING_THRESHOLD = 100  # Less than 100 hits = rare term

    def __init__(self):
        """Initialize validation service."""
        self._last_request_time = 0
        self._cache: Dict[str, ValidationResult] = {}

    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self._last_request_time
        if elapsed < self.RATE_LIMIT_DELAY:
            time.sleep(self.RATE_LIMIT_DELAY - elapsed)
        self._last_request_time = time.time()

    def validate_term(self, term: str, use_cache: bool = True) -> ValidationResult:
        """Validate a single term against OpenAlex.

        Args:
            term: The research term to validate
            use_cache: Whether to use cached results

        Returns:
            ValidationResult with hit counts and validity

        Raises:
            NetworkError: On network/API failures
        """
        # Check cache first
        if use_cache and term in self._cache:
            logger.debug(f"Using cached validation for: {term}")
            return self._cache[term]

        # Rate limit
        self._rate_limit()

        try:
            # Query OpenAlex
            # Search in title and abstract for relevance
            params = {
                "search": term,
                "per_page": 5  # Get a few samples for reference
            }

            logger.info(f"Validating term '{term}' against OpenAlex...")
            response = requests.get(
                self.BASE_URL,
                params=params,
                timeout=self.TIMEOUT,
                headers={"User-Agent": "HITL-Research-Pipeline/1.0 (mailto:research@example.com)"}
            )

            if response.status_code != 200:
                logger.warning(f"OpenAlex API returned status {response.status_code}")
                raise NetworkError(
                    f"OpenAlex API error: HTTP {response.status_code}",
                    details={"term": term, "status": response.status_code}
                )

            data = response.json()
            count = data.get('meta', {}).get('count', 0)

            # Extract sample work titles for context
            sample_works = []
            for work in data.get('results', [])[:3]:
                title = work.get('title', 'Untitled')
                sample_works.append(title)

            # Determine validity and severity
            if count == self.CRITICAL_THRESHOLD:
                severity = "critical"
                is_valid = False
                suggestion = f"Term '{term}' not found in literature. Check spelling or use more established terminology."
            elif count < self.WARNING_THRESHOLD:
                severity = "warning"
                is_valid = True  # Valid but rare
                suggestion = f"Rare term ({count} works). Verify this is the correct terminology for your field."
            else:
                severity = "ok"
                is_valid = True
                suggestion = None

            result = ValidationResult(
                term=term,
                hit_count=count,
                is_valid=is_valid,
                severity=severity,
                suggestion=suggestion,
                sample_works=sample_works
            )

            # Cache the result
            self._cache[term] = result

            logger.info(f"Validation complete: {term} -> {count} hits ({severity})")
            return result

        except requests.Timeout:
            logger.error(f"Timeout validating term: {term}")
            raise NetworkError(
                f"OpenAlex API timeout for term: {term}",
                details={"term": term, "timeout": self.TIMEOUT}
            )
        except requests.RequestException as e:
            logger.error(f"Network error validating term {term}: {e}")
            raise NetworkError(
                f"Network error during validation: {str(e)}",
                details={"term": term, "error": str(e)}
            )
        except (NetworkError, ValidationError):
            # Re-raise our own exceptions
            raise
        except Exception as e:
            logger.error(f"Unexpected error validating term {term}: {e}")
            raise ValidationError(
                f"Validation failed for term '{term}': {str(e)}",
                details={"term": term, "error": str(e)}
            )

    def validate_concept_list(self, concepts: List[str]) -> ValidationReport:
        """Batch validate a list of concepts.

        Args:
            concepts: List of concept/term strings to validate

        Returns:
            ValidationReport with results for all terms
        """
        logger.info(f"Validating {len(concepts)} concepts...")

        results = {}
        valid_count = 0
        warning_count = 0
        critical_count = 0

        for concept in concepts:
            try:
                result = self.validate_term(concept)
                results[concept] = result

                if result.severity == "ok":
                    valid_count += 1
                elif result.severity == "warning":
                    warning_count += 1
                else:  # critical
                    critical_count += 1

            except Exception as e:
                # Log error but continue validation
                logger.error(f"Failed to validate '{concept}': {e}")
                results[concept] = ValidationResult(
                    term=concept,
                    hit_count=0,
                    is_valid=False,
                    severity="critical",
                    suggestion=f"Validation error: {str(e)}"
                )
                critical_count += 1

        # Generate summary
        summary = self._generate_summary(
            len(concepts), valid_count, warning_count, critical_count
        )

        report = ValidationReport(
            results=results,
            total_terms=len(concepts),
            valid_count=valid_count,
            warning_count=warning_count,
            critical_count=critical_count,
            summary=summary
        )

        logger.info(f"Validation complete: {summary}")
        return report

    def _generate_summary(
        self, total: int, valid: int, warning: int, critical: int
    ) -> str:
        """Generate human-readable validation summary.

        Args:
            total: Total terms validated
            valid: Number of valid terms
            warning: Number of warnings
            critical: Number of critical issues

        Returns:
            Summary string
        """
        if critical > 0:
            return (
                f"⚠️ CRITICAL: {critical}/{total} terms not found in literature (possible hallucinations). "
                f"{warning} rare terms, {valid} validated."
            )
        elif warning > 0:
            return (
                f"⚠️ WARNING: {warning}/{total} terms are rare in literature. "
                f"{valid} terms validated. Verify rare terms are correct for your field."
            )
        else:
            return f"✅ All {total} terms validated successfully in academic literature."

    def clear_cache(self):
        """Clear the validation cache."""
        self._cache.clear()
        logger.info("Validation cache cleared")

