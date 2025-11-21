"""Unit tests for ValidationService."""

import pytest
from unittest.mock import Mock, patch
import requests

from src.services.validation_service import (
    ValidationService,
    ValidationResult,
    ValidationReport
)
from src.utils.exceptions import NetworkError, ValidationError


class TestValidationService:
    """Test ValidationService functionality."""

    def test_initialization(self):
        """Test service initializes correctly."""
        service = ValidationService()
        assert service is not None
        assert service._cache == {}

    @patch('src.services.validation_service.requests.get')
    def test_validate_term_success(self, mock_get):
        """Test successful term validation."""
        # Mock OpenAlex response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'meta': {'count': 5000},
            'results': [
                {'title': 'Machine Learning in Healthcare'},
                {'title': 'Deep Learning Applications'},
                {'title': 'Neural Networks for Diagnosis'}
            ]
        }
        mock_get.return_value = mock_response

        service = ValidationService()
        result = service.validate_term("machine learning")

        assert result.term == "machine learning"
        assert result.hit_count == 5000
        assert result.is_valid is True
        assert result.severity == "ok"
        assert len(result.sample_works) == 3

    @patch('src.services.validation_service.requests.get')
    def test_validate_term_hallucination(self, mock_get):
        """Test validation of hallucinated term (0 hits)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'meta': {'count': 0},
            'results': []
        }
        mock_get.return_value = mock_response

        service = ValidationService()
        result = service.validate_term("completely made up term xyz123")

        assert result.hit_count == 0
        assert result.is_valid is False
        assert result.severity == "critical"
        assert "not found" in result.suggestion.lower()

    @patch('src.services.validation_service.requests.get')
    def test_validate_term_rare(self, mock_get):
        """Test validation of rare term (< 100 hits)."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'meta': {'count': 50},
            'results': [{'title': 'Rare research topic'}]
        }
        mock_get.return_value = mock_response

        service = ValidationService()
        result = service.validate_term("rare term")

        assert result.hit_count == 50
        assert result.is_valid is True  # Valid but rare
        assert result.severity == "warning"
        assert "rare" in result.suggestion.lower()

    @patch('src.services.validation_service.requests.get')
    def test_validate_term_caching(self, mock_get):
        """Test result caching."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'meta': {'count': 1000},
            'results': []
        }
        mock_get.return_value = mock_response

        service = ValidationService()

        # First call - should hit API
        result1 = service.validate_term("test term")
        assert mock_get.call_count == 1

        # Second call - should use cache
        result2 = service.validate_term("test term")
        assert mock_get.call_count == 1  # Still 1, not 2

        assert result1.hit_count == result2.hit_count

    @patch('src.services.validation_service.requests.get')
    def test_validate_term_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        service = ValidationService()

        with pytest.raises(NetworkError):
            service.validate_term("test")

    @patch('src.services.validation_service.requests.get')
    def test_validate_term_timeout(self, mock_get):
        """Test handling of timeouts."""
        mock_get.side_effect = requests.Timeout("Connection timeout")

        service = ValidationService()

        with pytest.raises(NetworkError):
            service.validate_term("test")

    @patch('src.services.validation_service.requests.get')
    def test_validate_concept_list(self, mock_get):
        """Test batch validation."""
        # Mock different responses for different terms
        def mock_response_func(*args, **kwargs):
            term = kwargs['params']['search']
            mock_resp = Mock()
            mock_resp.status_code = 200

            if term == "valid term":
                mock_resp.json.return_value = {'meta': {'count': 1000}, 'results': []}
            elif term == "rare term":
                mock_resp.json.return_value = {'meta': {'count': 50}, 'results': []}
            else:  # hallucination
                mock_resp.json.return_value = {'meta': {'count': 0}, 'results': []}

            return mock_resp

        mock_get.side_effect = mock_response_func

        service = ValidationService()
        report = service.validate_concept_list([
            "valid term",
            "rare term",
            "hallucinated term"
        ])

        assert report.total_terms == 3
        assert report.valid_count == 1  # Only "valid term" has 100+ hits
        assert report.warning_count == 1  # "rare term"
        assert report.critical_count == 1  # "hallucinated term"
        assert len(report.results) == 3

    def test_clear_cache(self):
        """Test cache clearing."""
        service = ValidationService()
        service._cache = {"test": Mock()}

        assert len(service._cache) > 0
        service.clear_cache()
        assert len(service._cache) == 0


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_creation(self):
        """Test creating ValidationResult."""
        result = ValidationResult(
            term="test",
            hit_count=100,
            is_valid=True,
            severity="ok",
            suggestion=None,
            sample_works=["Work 1", "Work 2"]
        )

        assert result.term == "test"
        assert result.hit_count == 100
        assert len(result.sample_works) == 2

    def test_default_sample_works(self):
        """Test default sample_works initialization."""
        result = ValidationResult(
            term="test",
            hit_count=0,
            is_valid=False,
            severity="critical"
        )

        assert result.sample_works == []


class TestValidationReport:
    """Test ValidationReport dataclass."""

    def test_creation(self):
        """Test creating ValidationReport."""
        results = {
            "term1": ValidationResult("term1", 1000, True, "ok"),
            "term2": ValidationResult("term2", 0, False, "critical")
        }

        report = ValidationReport(
            results=results,
            total_terms=2,
            valid_count=1,
            warning_count=0,
            critical_count=1,
            summary="Test summary"
        )

        assert report.total_terms == 2
        assert report.valid_count == 1
        assert report.critical_count == 1

