"""
Demo: Autonomous Research Agent

This script demonstrates the full autonomous research pipeline:
1. You ask a research question in natural language
2. The Orchestrator Agent thinks about it
3. It generates search queries automatically
4. It executes searches across databases
5. You get results with minimal manual work

This is the "magic" - the system thinks and acts autonomously.
"""

import logging
from src.agents.orchestrator import OrchestratorAgent

# Setup logging to see the agent's "thought process"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def demo_autonomous_research():
    """Demonstrate autonomous research on a real question."""

    print("=" * 70)
    print("AUTONOMOUS RESEARCH AGENT - DEMO")
    print("=" * 70)
    print()
    print("This demo shows the Orchestrator Agent autonomously researching")
    print("a question by generating search strategies and executing searches.")
    print()

    # The research question
    question = "What are effective techniques for reducing LLM hallucinations?"

    print("📝 Research Question:")
    print(f"   {question}")
    print()

    # Create the orchestrator agent
    print("🤖 Initializing Orchestrator Agent...")
    agent = OrchestratorAgent()
    print("✅ Agent ready")
    print()

    # Let the agent do its thing
    print("🧠 Agent is thinking and planning...")
    print()

    results = agent.research(question, max_results_per_query=20)

    # Show what the agent decided
    print()
    print("=" * 70)
    print("AGENT'S SEARCH STRATEGY")
    print("=" * 70)
    print()
    print(agent.explain_strategy(results.strategy))
    print()

    # Show search execution results
    print("=" * 70)
    print("SEARCH EXECUTION RESULTS")
    print("=" * 70)
    print()

    if results.search_results:
        print(f"✅ Successfully searched {len(results.search_results)} database/query combinations")
        print()

        for i, result in enumerate(results.search_results, 1):
            status = "✅" if not result.error else "❌"
            print(f"{status} Search {i}: {result.database} - '{result.query[:50]}...'")
            print(f"   Results: {result.total_hits} papers")
            print(f"   Time: {result.execution_time:.2f}s")
            if result.result_file:
                print(f"   Saved to: {result.result_file}")
            if result.error:
                print(f"   Error: {result.error}")
            print()

    if results.errors:
        print(f"⚠️  {len(results.errors)} errors occurred:")
        for error in results.errors:
            print(f"   - {error}")
        print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"📊 Total Papers Found: {results.total_papers}")
    print(f"⏱️  Total Execution Time: {results.execution_time:.2f}s")
    print(f"🗄️  Databases Searched: {', '.join(results.strategy.databases)}")
    print(f"🔍 Queries Executed: {len(results.strategy.queries)}")
    print()

    # Next steps
    if results.total_papers > 0:
        print("✅ Success! The agent found relevant papers autonomously.")
        print()
        print("Next steps:")
        print("  1. Load and review the papers")
        print("  2. Add a SynthesizerAgent to summarize findings")
        print("  3. Generate a coherent answer to the original question")
        print()

        # Show how to load results
        print("To load and view papers:")
        print()
        print("```python")
        print("from src.services.search_service import get_search_service")
        print("service = get_search_service()")
        print(f"papers = service.load_results('{results.search_results[0].result_file}')")
        print("print(papers[0]['title'])")
        print("```")
    else:
        print("⚠️  No papers found. Check errors above.")

    print()
    print("=" * 70)

    return results


def demo_multiple_questions():
    """Demo with multiple research questions to show versatility."""

    print("\n" + "=" * 70)
    print("TESTING MULTIPLE RESEARCH QUESTIONS")
    print("=" * 70)
    print()

    questions = [
        "What is retrieval augmented generation?",
        "How does chain-of-thought prompting improve reasoning?",
        "What are the latest advances in multimodal transformers?"
    ]

    agent = OrchestratorAgent()

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*70}")
        print(f"Question {i}: {question}")
        print('='*70)

        results = agent.research(question, max_results_per_query=10)

        print(f"\n📊 Results:")
        print(f"   Papers found: {results.total_papers}")
        print(f"   Databases: {', '.join(results.strategy.databases)}")
        print(f"   Queries: {', '.join(results.strategy.queries[:2])}{'...' if len(results.strategy.queries) > 2 else ''}")
        print(f"   Time: {results.execution_time:.2f}s")

        if results.errors:
            print(f"   ⚠️  Errors: {len(results.errors)}")


def interactive_research():
    """Interactive mode - ask your own questions."""

    print("\n" + "=" * 70)
    print("INTERACTIVE AUTONOMOUS RESEARCH")
    print("=" * 70)
    print()
    print("Ask any research question and the agent will autonomously search for papers.")
    print("Type 'quit' to exit.")
    print()

    agent = OrchestratorAgent()

    while True:
        question = input("\n📝 Your research question: ").strip()

        if not question or question.lower() == 'quit':
            print("\nGoodbye! 👋")
            break

        print("\n🧠 Agent is researching...")

        try:
            results = agent.research(question, max_results_per_query=15)

            print(f"\n✅ Found {results.total_papers} papers")
            print(f"⏱️  Completed in {results.execution_time:.2f}s")
            print(f"🔍 Strategy: {results.strategy.reasoning}")

            if results.errors:
                print(f"\n⚠️  {len(results.errors)} errors occurred")

        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


def main():
    """Run the demo."""
    import sys

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'interactive':
            interactive_research()
        elif mode == 'multi':
            demo_multiple_questions()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python demo_autonomous_agent.py [interactive|multi]")
    else:
        # Default: single question demo
        demo_autonomous_research()


if __name__ == '__main__':
    main()

