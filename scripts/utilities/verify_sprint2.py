"""Quick verification test for Sprint 2 implementation."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all new modules can be imported."""
    print("Testing imports...")

    try:
        from src.services.llm_provider import LLMProvider, OpenAIProvider, MockProvider, get_llm_provider
        print("✓ llm_provider imports OK")
    except Exception as e:
        print(f"✗ llm_provider import failed: {e}")
        return False

    try:
        from src.services.prompts import SYSTEM_PROMPT_METHODOLOGIST, PROMPT_STAGE0_CONTEXT
        print("✓ prompts imports OK")
    except Exception as e:
        print(f"✗ prompts import failed: {e}")
        return False

    try:
        from src.services.validation_service import ValidationService, ValidationResult, ValidationReport
        print("✓ validation_service imports OK")
    except Exception as e:
        print(f"✗ validation_service import failed: {e}")
        return False

    try:
        from src.services.intelligent_model_service import IntelligentModelService
        print("✓ intelligent_model_service imports OK")
    except Exception as e:
        print(f"✗ intelligent_model_service import failed: {e}")
        return False

    return True


def test_mock_provider():
    """Test MockProvider functionality."""
    print("\nTesting MockProvider...")

    try:
        from src.services.llm_provider import MockProvider

        provider = MockProvider()

        # Test context generation
        response = provider.generate(
            "You are a researcher",
            "Generate project context for: LLM hallucinations"
        )

        assert len(response) > 0, "Empty response"
        assert "title" in response.lower() or "{" in response, "Not JSON-like"

        print("✓ MockProvider generates responses")
        return True

    except Exception as e:
        print(f"✗ MockProvider test failed: {e}")
        return False


def test_validation_service():
    """Test ValidationService with OpenAlex."""
    print("\nTesting ValidationService...")

    try:
        from src.services.validation_service import ValidationService

        service = ValidationService()

        # Test with a well-known term
        result = service.validate_term("machine learning")

        assert result.term == "machine learning"
        assert result.hit_count > 0, f"Expected hits > 0, got {result.hit_count}"
        assert result.is_valid, "Well-known term should be valid"
        assert result.severity in ["ok", "warning"], f"Unexpected severity: {result.severity}"

        print(f"✓ ValidationService works (found {result.hit_count} works)")
        return True

    except Exception as e:
        print(f"✗ ValidationService test failed: {e}")
        print("  Note: This requires internet connection to OpenAlex API")
        return False


def test_intelligent_service():
    """Test IntelligentModelService with Mock."""
    print("\nTesting IntelligentModelService...")

    try:
        from src.services.intelligent_model_service import IntelligentModelService
        from src.config import get_config

        service = IntelligentModelService()

        # Test Stage 0
        context, meta = service.suggest_project_context(
            "Research LLM hallucinations in healthcare"
        )

        assert context.title, "No title generated"
        assert len(context.initial_keywords) > 0, "No keywords extracted"
        assert meta.model_name, "No metadata"

        print(f"✓ Stage 0 works: {context.title}")

        # Test Stage 1
        framing, concepts, meta2 = service.generate_problem_framing(context)

        assert framing.problem_statement, "No problem statement"
        assert len(framing.goals) > 0, "No goals"
        assert len(concepts.concepts) > 0, "No concepts extracted"
        assert framing.critique_report, "No critique report"

        print(f"✓ Stage 1 works: {len(concepts.concepts)} concepts, {len(framing.goals)} goals")
        print(f"✓ Critique report generated ({len(framing.critique_report)} chars)")

        return True

    except Exception as e:
        print(f"✗ IntelligentModelService test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*70)
    print(" Sprint 2 Verification Tests")
    print("="*70)

    results = []

    results.append(("Imports", test_imports()))
    results.append(("MockProvider", test_mock_provider()))
    results.append(("ValidationService", test_validation_service()))
    results.append(("IntelligentModelService", test_intelligent_service()))

    print("\n" + "="*70)
    print(" Test Results")
    print("="*70)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status:8s} - {name}")

    total = len(results)
    passed_count = sum(1 for _, p in results if p)

    print(f"\n{passed_count}/{total} tests passed")

    if passed_count == total:
        print("\n🎉 All tests passed! Sprint 2 implementation is working.")
        return 0
    else:
        print(f"\n⚠️  {total - passed_count} test(s) failed. Review errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

