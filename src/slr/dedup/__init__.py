"""
Deduplication module for Simple SLR.

This module provides functionality for identifying and merging duplicate
documents from multiple academic databases.

Main classes:
    - Deduplicator: Main deduplication coordinator
    - ConservativeStrategy: Conservative exact-matching strategy
    - SemanticStrategy: Semantic embedding-based strategy (future)
    - HybridStrategy: Hybrid approach (future)

Example:
    >>> from src.slr.core.config import DeduplicationConfig
    >>> from src.slr.dedup import Deduplicator
    >>>
    >>> config = DeduplicationConfig(strategy="conservative")
    >>> deduplicator = Deduplicator(config)
    >>> clusters = deduplicator.deduplicate(documents)
    >>> unique_docs = [cluster.representative for cluster in clusters]
"""

from src.slr.dedup.deduplicator import Deduplicator
from src.slr.dedup.strategies import (
    ConservativeStrategy,
    DeduplicationStrategy,
    HybridStrategy,
    SemanticStrategy,
)

__all__ = [
    "Deduplicator",
    "DeduplicationStrategy",
    "ConservativeStrategy",
    "SemanticStrategy",
    "HybridStrategy",
]
