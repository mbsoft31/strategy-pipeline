"""Demo script for Sprint 2: LLM Integration with Validation.

This script demonstrates the complete workflow:
1. Draft generation with LLM
2. Critique loop (reflection)
3. OpenAlex validation (reality check)
4. Final report assembly

Run with Mock provider (free):
    LLM__PROVIDER=mock python demo_sprint2.py

Run with OpenAI (requires API key):
    LLM__PROVIDER=openai python demo_sprint2.py
"""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import get_config
from src.services.intelligent_model_service import IntelligentModelService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Run the demo workflow."""
    print("\n" + "="*80)
    print(" SPRINT 2 DEMO: LLM Integration with Validation")
    print("="*80)

    # Show configuration
    config = get_config()
    print(f"\n📊 Configuration:")
    print(f"   LLM Provider: {config.llm.provider.value}")
    print(f"   Model: {config.llm.openai_model}")
    print(f"   Temperature: {config.llm.openai_temperature}")

    # Initialize service
    print(f"\n🔧 Initializing IntelligentModelService...")
    service = IntelligentModelService()

    # =========================================================================
    # STAGE 0: Project Context Generation
    # =========================================================================
    print(f"\n" + "="*80)
    print(" STAGE 0: Project Context Generation")
    print("="*80)

    raw_idea = """
    I want to research how large language models like GPT-4 and Claude 
    sometimes generate false information when used in clinical decision 
    support systems. This could be dangerous for patients if doctors rely 
    on incorrect AI outputs. I want to develop a way to detect these 
    'hallucinations' and measure how often they happen.
    """

    print(f"\n💡 Raw Research Idea:")
    print(f"{raw_idea.strip()}\n")

    try:
        context, meta = service.suggest_project_context(raw_idea)

        print(f"\n✅ Project Context Generated:")
        print(f"   Title: {context.title}")
        print(f"   Discipline: {context.discipline}")
        print(f"   Keywords: {', '.join(context.initial_keywords)}")
        print(f"   Model: {meta.model_name}")

    except Exception as e:
        print(f"\n❌ Error generating context: {e}")
        return 1

    # =========================================================================
    # STAGE 1: Problem Framing with Critique Loop & Validation
    # =========================================================================
    print(f"\n" + "="*80)
    print(" STAGE 1: Problem Framing (Draft → Critique → Refine → Validate)")
    print("="*80)

    try:
        print(f"\n⏳ Running critique loop and validation...")
        print(f"   This may take 10-30 seconds with OpenAI...")

        framing, concepts, meta = service.generate_problem_framing(context)

        # Display results
        print(f"\n✅ Problem Framing Complete!")
        print(f"\n📝 Problem Statement:")
        print(f"   {framing.problem_statement}\n")

        print(f"🔍 Research Gap:")
        print(f"   {framing.research_gap}\n")

        print(f"🎯 Goals:")
        for i, goal in enumerate(framing.goals, 1):
            print(f"   {i}. {goal}")

        print(f"\n✅ Scope IN:")
        for item in framing.scope_in:
            print(f"   • {item}")

        print(f"\n❌ Scope OUT:")
        for item in framing.scope_out:
            print(f"   • {item}")

        print(f"\n🧩 Concepts Extracted: {len(concepts.concepts)}")
        for concept in concepts.concepts:
            print(f"   • {concept.label} ({concept.type})")

        # Display critique report
        print(f"\n" + "="*80)
        print(" CRITIQUE & VALIDATION REPORT")
        print("="*80)
        if framing.critique_report:
            print(framing.critique_report)
        else:
            print("No critique report available")

        # Summary
        print(f"\n" + "="*80)
        print(" SUMMARY")
        print("="*80)
        print(f"\n✅ Workflow Complete!")
        print(f"   Model: {meta.model_name}")
        print(f"   Mode: {meta.mode}")
        print(f"   Concepts: {len(concepts.concepts)}")
        print(f"   Goals: {len(framing.goals)}")

        print(f"\n💡 Next Steps:")
        print(f"   1. Review the critique report for validation warnings")
        print(f"   2. Check OpenAlex hit counts for each concept")
        print(f"   3. Refine any terms with 0 hits (hallucinations)")
        print(f"   4. Approve the framing to move to Stage 2")

        print(f"\n🎉 Demo complete! This is production-ready validated AI.\n")
        return 0

    except Exception as e:
        print(f"\n❌ Error in problem framing: {e}")
        logger.exception("Problem framing failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

