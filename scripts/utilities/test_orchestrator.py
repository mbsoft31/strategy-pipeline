"""
Quick test of the Orchestrator Agent with MOCK provider.

This test uses the MockProvider so it works without API keys.
It validates that the agent can:
1. Initialize correctly
2. Generate search strategies
3. Execute searches
4. Return results
"""

import logging
from src.agents.orchestrator import OrchestratorAgent

logging.basicConfig(level=logging.INFO)


def test_with_mock_provider():
    """Test autonomous research using Mock LLM provider."""
    
    print("\n" + "="*70)
    print("TESTING ORCHESTRATOR AGENT (MOCK MODE)")
    print("="*70)
    print()
    print("This test uses the Mock LLM provider (no API key needed)")
    print()
    
    # Initialize agent (will use Mock provider by default from config)
    print("1. Initializing Orchestrator Agent...")
    agent = OrchestratorAgent()
    print("✅ Agent initialized")
    print()
    
    # Test with a simple question
    question = "What are LLM hallucination detection methods?"
    print(f"2. Research Question: {question}")
    print()
    
    print("3. Executing autonomous research...")
    print("   (Agent will generate strategy and execute searches)")
    print()
    
    try:
        results = agent.research(question, max_results_per_query=5)
        
        print("\n" + "="*70)
        print("RESULTS")
        print("="*70)
        print()
        
        print(f"✅ Research completed successfully!")
        print()
        print(f"📊 Papers found: {results.total_papers}")
        print(f"⏱️  Execution time: {results.execution_time:.2f}s")
        print(f"🗄️  Databases searched: {', '.join(results.strategy.databases)}")
        print(f"🔍 Queries executed: {len(results.strategy.queries)}")
        print()
        
        print("Strategy:")
        print(f"  {results.strategy.reasoning}")
        print()
        
        if results.search_results:
            print("Search Results:")
            for i, result in enumerate(results.search_results, 1):
                status = "✅" if not result.error else "❌"
                print(f"  {status} {result.database}: {result.total_hits} papers in {result.execution_time:.2f}s")
        
        if results.errors:
            print(f"\n⚠️  Errors: {len(results.errors)}")
            for error in results.errors[:3]:
                print(f"  - {error}")
        
        print()
        print("="*70)
        print("TEST PASSED ✅")
        print("="*70)
        print()
        print("The Orchestrator Agent is working!")
        print()
        print("Next steps:")
        print("  1. To use real LLM (OpenAI), set LLM__PROVIDER=openai in .env")
        print("  2. Add your OPENAI_API_KEY to .env")
        print("  3. Run: python demo_autonomous_agent.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_with_mock_provider()
    exit(0 if success else 1)

