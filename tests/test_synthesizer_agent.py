"""Tests for SynthesizerAgent (using MockProvider)."""
import os
from pathlib import Path

from src.agents.orchestrator import OrchestratorAgent
from src.agents.synthesizer import SynthesizerAgent


def test_synthesizer_basic_flow():
    question = "What are effective techniques for reducing LLM hallucinations?"
    orchestrator = OrchestratorAgent()
    research = orchestrator.research(question, max_results_per_query=5)
    result_files = [r.result_file for r in research.search_results if r.result_file]
    assert result_files, "Expected at least one result file"

    synthesizer = SynthesizerAgent(max_papers=20)
    synthesis = synthesizer.synthesize(question, result_files)

    assert synthesis.used_papers > 0
    assert synthesis.cluster_summaries or synthesis.used_papers <= synthesizer.min_cluster_size
    # Synthesis paragraph should exist (fallback or generated)
    assert synthesis.synthesis_paragraph
    # Bullets should be list
    assert isinstance(synthesis.bullet_points, list)


def test_synthesizer_handles_empty():
    synthesizer = SynthesizerAgent()
    synthesis = synthesizer.synthesize("Test question", [])
    assert synthesis.used_papers == 0
    assert "No sufficient" in synthesis.synthesis_paragraph


