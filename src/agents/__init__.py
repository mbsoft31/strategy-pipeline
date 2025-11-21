"""
Autonomous agents for the Research Strategy Pipeline.

Agents:
- OrchestratorAgent: Coordinates research, generates search strategies
- ResearcherAgent: Executes searches and collects papers (future)
- SynthesizerAgent: Synthesizes findings into coherent answers (future)
"""

from src.agents.orchestrator import OrchestratorAgent

__all__ = ['OrchestratorAgent']

