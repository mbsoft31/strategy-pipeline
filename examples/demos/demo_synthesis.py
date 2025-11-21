"""Demo: Full autonomous pipeline with synthesis.

Flow:
1. OrchestratorAgent generates search strategy & executes searches
2. SynthesizerAgent loads result files and produces structured synthesis
3. Display synthesis outputs (paragraph, bullets, methods, gaps, trends, citations)

Works with Mock provider or real OpenRouter/OpenAI provider.
"""
import logging
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.agents.synthesizer import SynthesizerAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def run_demo(question: str = "What are effective techniques for reducing LLM hallucinations?"):
    print("="*80)
    print("AUTONOMOUS RESEARCH + SYNTHESIS DEMO")
    print("="*80)
    print(f"Question: {question}\n")

    orchestrator = OrchestratorAgent()
    research = orchestrator.research(question, max_results_per_query=15)

    print("Search Strategy:")
    print(orchestrator.explain_strategy(research.strategy))
    print()

    # Collect result files
    result_files = [r.result_file for r in research.search_results if r.result_file]
    print(f"Collected {len(result_files)} result files for synthesis")

    if not result_files:
        print("No results to synthesize. Exiting.")
        return

    synthesizer = SynthesizerAgent(max_papers=50)
    synthesis = synthesizer.synthesize(question, result_files)

    print("\n" + "="*80)
    print("SYNTHESIS OUTPUT")
    print("="*80 + "\n")
    print("Cohesive Synthesis Paragraph:\n")
    print(synthesis.synthesis_paragraph)
    print("\nKey Takeaways:")
    for b in synthesis.bullet_points:
        print(f" - {b}")
    print("\nMethods:")
    for m in synthesis.methods:
        print(f" - {m}")
    print("\nTrends:")
    for t in synthesis.trends:
        print(f" - {t}")
    print("\nGaps / Open Challenges:")
    for g in synthesis.gaps:
        print(f" - {g}")
    print("\nRepresentative Citations (keys):")
    for c in synthesis.citations:
        print(f" - {c}")

    print("\nCluster Summaries (compact):")
    for cs in synthesis.cluster_summaries[:5]:
        print(f"\n[Cluster {cs.cluster_id} | size={cs.size} | keywords={', '.join(cs.keywords)}]\n{cs.summary}")

    print("\n" + "="*80)
    print("DEMO COMPLETE")
    print("="*80)


if __name__ == "__main__":
    run_demo()

