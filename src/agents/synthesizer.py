"""
Synthesizer Agent - Transforms raw search results (papers) into structured knowledge.

Responsibilities:
1. Load paper metadata from saved search result files
2. Select relevant subset (filter, limit, prioritize diversity & recency)
3. Generate structured synthesis (themes, methods, challenges, trends, gaps)
4. Produce citation list referencing provider/source identifiers
5. Provide multiple output granularities: bullet summary, paragraph synthesis, JSON structured

Design Principles:
- Stateless aside from configuration: all inputs explicit
- Works with both real LLM provider and MockProvider (degrades gracefully)
- Avoids loading entire large corpora into prompt (implements chunk summarization + aggregation)

Phases:
A. Paper ingestion & normalization
B. Thematic clustering (simple heuristic for now: TF keyword overlap)
C. Per-cluster mini-summary (LLM or rule-based fallback)
D. Global synthesis (LLM prompt aggregating cluster summaries)
E. Output assembly
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Any
import math
import re

from src.services.llm_provider import get_llm_provider
from src.services.search_service import get_search_service

logger = logging.getLogger(__name__)


@dataclass
class Paper:
    title: str
    abstract: Optional[str]
    year: Optional[int]
    doi: Optional[str]
    provider: Optional[str]
    provider_id: Optional[str]

    def citation_key(self) -> str:
        if self.doi:
            return self.doi
        if self.provider and self.provider_id:
            return f"{self.provider}:{self.provider_id}"
        # Fallback - normalized title slug
        return re.sub(r"[^a-z0-9]+", "-", (self.title.lower()))[:40]


@dataclass
class ClusterSummary:
    cluster_id: int
    size: int
    keywords: List[str]
    representative_title: str
    summary: str
    citation_keys: List[str]


@dataclass
class SynthesisResult:
    question: str
    total_papers: int
    used_papers: int
    cluster_summaries: List[ClusterSummary]
    synthesis_paragraph: str
    bullet_points: List[str]
    gaps: List[str]
    methods: List[str]
    trends: List[str]
    citations: List[str]


class SynthesizerAgent:
    def __init__(self,
                 max_papers: int = 60,
                 min_cluster_size: int = 2,
                 max_clusters: int = 8):
        self.llm = get_llm_provider()
        self.search_service = get_search_service()
        self.max_papers = max_papers
        self.min_cluster_size = min_cluster_size
        self.max_clusters = max_clusters
        logger.info("SynthesizerAgent initialized")

    # ------------------------- Public API -------------------------
    def synthesize(self,
                   question: str,
                   result_files: List[str]) -> SynthesisResult:
        """Generate synthesis from search result JSON files."""
        papers = self._load_papers(result_files)
        total = len(papers)
        logger.info(f"Loaded {total} papers from {len(result_files)} result sets")

        selected = self._select_subset(papers)
        logger.info(f"Selected {len(selected)} papers for synthesis (max={self.max_papers})")

        clusters = self._cluster_papers(selected)
        logger.info(f"Formed {len(clusters)} clusters")

        cluster_summaries = self._summarize_clusters(question, clusters)
        logger.info("Cluster summarization complete")

        synthesis_paragraph, bullets, gaps, methods, trends = self._global_synthesis(question, cluster_summaries)

        citations = self._assemble_citations(cluster_summaries)

        return SynthesisResult(
            question=question,
            total_papers=total,
            used_papers=len(selected),
            cluster_summaries=cluster_summaries,
            synthesis_paragraph=synthesis_paragraph,
            bullet_points=bullets,
            gaps=gaps,
            methods=methods,
            trends=trends,
            citations=citations
        )

    # ------------------------- Paper Loading -------------------------
    def _load_papers(self, result_files: List[str]) -> List[Paper]:
        loaded: List[Paper] = []
        for rf in result_files:
            try:
                docs = self.search_service.load_results(rf)
                for d in docs:
                    loaded.append(Paper(
                        title=d.get('title'),
                        abstract=d.get('abstract'),
                        year=d.get('year'),
                        doi=d.get('doi'),
                        provider=d.get('provider'),
                        provider_id=d.get('provider_id')
                    ))
            except Exception as e:
                logger.warning(f"Failed to load {rf}: {e}")
        return loaded

    # ------------------------- Selection -------------------------
    def _select_subset(self, papers: List[Paper]) -> List[Paper]:
        if len(papers) <= self.max_papers:
            return papers
        # Simple heuristic: prioritize newer papers, then diversity by title hash
        sorted_papers = sorted(papers, key=lambda p: (p.year or 0), reverse=True)
        unique = []
        seen_slugs = set()
        for p in sorted_papers:
            slug = p.citation_key()
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            unique.append(p)
            if len(unique) >= self.max_papers:
                break
        return unique

    # ------------------------- Clustering -------------------------
    def _extract_keywords(self, text: str, top_k: int = 8) -> List[str]:
        if not text:
            return []
        # Very naive extraction: split, filter short/common, frequency rank
        words = re.findall(r"[a-zA-Z]{4,}", text.lower())
        stop = {"this","that","from","with","into","using","have","been","were","their","which","between","while","these","those","there","about","within","without","over","under","where","when","shall","could","would","should","such","also","both","many","some","more","than"}
        freq: Dict[str,int] = {}
        for w in words:
            if w in stop:
                continue
            freq[w] = freq.get(w, 0) + 1
        ranked = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_k]
        return [w for w,_ in ranked]

    def _cluster_papers(self, papers: List[Paper]) -> List[List[Paper]]:
        if not papers:
            return []
        # Build simple keyword sets
        keyword_sets = []
        for p in papers:
            kw = set(self._extract_keywords((p.title or '') + ' ' + (p.abstract or '')))
            keyword_sets.append((p, kw))
        # Agglomerative naive clustering based on Jaccard
        clusters: List[List[Paper]] = []
        for p, ks in keyword_sets:
            placed = False
            for cluster in clusters:
                # Compare with representative (first) paper keywords
                rep = cluster[0]
                rep_kw = set(self._extract_keywords((rep.title or '') + ' ' + (rep.abstract or '')))
                jaccard = len(ks & rep_kw) / (len(ks | rep_kw) or 1)
                if jaccard >= 0.15:  # heuristic threshold
                    cluster.append(p)
                    placed = True
                    break
            if not placed:
                clusters.append([p])
        # Filter tiny clusters, sort by size, cap
        clusters = [c for c in clusters if len(c) >= self.min_cluster_size]
        clusters.sort(key=lambda c: len(c), reverse=True)
        return clusters[:self.max_clusters]

    # ------------------------- Cluster Summaries -------------------------
    def _summarize_clusters(self, question: str, clusters: List[List[Paper]]) -> List[ClusterSummary]:
        summaries: List[ClusterSummary] = []
        for cid, cluster in enumerate(clusters, start=1):
            titles = [p.title for p in cluster]
            abstracts = [p.abstract for p in cluster if p.abstract]
            combined_text = '\n'.join(filter(None, titles + abstracts))[:8000]  # safety trim
            keywords = self._extract_keywords(combined_text, top_k=6)
            representative = cluster[0].title
            summary = self._generate_cluster_summary(question, keywords, titles, abstracts, representative)
            summaries.append(ClusterSummary(
                cluster_id=cid,
                size=len(cluster),
                keywords=keywords,
                representative_title=representative,
                summary=summary,
                citation_keys=[p.citation_key() for p in cluster]
            ))
        return summaries

    def _generate_cluster_summary(self,
                                  question: str,
                                  keywords: List[str],
                                  titles: List[str],
                                  abstracts: List[str],
                                  representative: str) -> str:
        system_prompt = "You are an expert research summarization model."
        user_prompt = (
            "Research Question: " + question + "\n" +
            "Cluster Representative Title: " + representative + "\n" +
            "Cluster Keywords: " + ', '.join(keywords) + "\n" +
            "Paper Titles:\n- " + '\n- '.join(titles[:15]) + "\n" +
            "Instructions: Summarize this cluster's focus, typical methods, and distinctive contributions in 4 concise sentences."
        )
        try:
            raw = self.llm.generate(system_prompt, user_prompt)
            return raw.strip()
        except Exception as e:
            logger.warning(f"LLM cluster summary failed, fallback: {e}")
            return f"Cluster on {', '.join(keywords[:4])}: {representative[:120]} ..."

    # ------------------------- Global Synthesis -------------------------
    def _global_synthesis(self, question: str, cluster_summaries: List[ClusterSummary]):
        if not cluster_summaries:
            return ("No sufficient clusters formed for synthesis.", [], [], [], [])
        system_prompt = "You are a senior researcher synthesizing literature across thematic clusters."
        cluster_text = '\n\n'.join([
            f"Cluster {c.cluster_id} (size={c.size}) keywords={', '.join(c.keywords)}\n{c.summary}" for c in cluster_summaries
        ])
        user_prompt = (
            f"Research Question: {question}\n\n" +
            "Cluster Summaries:\n" + cluster_text + "\n\n" +
            "Tasks:\n" +
            "1. Provide a cohesive synthesis paragraph (~180 words) integrating clusters.\n" +
            "2. List 6 bullet key takeaways (be specific).\n" +
            "3. List 3 observed methodological patterns.\n" +
            "4. List 3 emerging trends.\n" +
            "5. List 3 gaps or open challenges.\n" +
            "Respond ONLY in JSON with keys: synthesis, bullets, methods, trends, gaps."
        )
        try:
            raw = self.llm.generate(system_prompt, user_prompt)
            data = self.llm.clean_json_response(raw)
            synthesis = data.get('synthesis', '')
            bullets = data.get('bullets', [])
            methods = data.get('methods', [])
            trends = data.get('trends', [])
            gaps = data.get('gaps', [])
            return (synthesis, bullets, gaps, methods, trends)
        except Exception as e:
            logger.warning(f"Global synthesis LLM failed: {e}")
            # Fallback assembly
            synthesis = ' '.join(c.summary for c in cluster_summaries)[:900]
            bullets = [f"Cluster {c.cluster_id}: {', '.join(c.keywords[:3])}" for c in cluster_summaries[:6]]
            methods = []
            trends = []
            gaps = []
            return (synthesis, bullets, gaps, methods, trends)

    def _assemble_citations(self, cluster_summaries: List[ClusterSummary]) -> List[str]:
        seen = set()
        ordered = []
        for c in cluster_summaries:
            for ck in c.citation_keys[:5]:  # limit per cluster for brevity
                if ck not in seen:
                    seen.add(ck)
                    ordered.append(ck)
        return ordered


# Convenience function

def synthesize_research(question: str, result_files: List[str]) -> SynthesisResult:
    agent = SynthesizerAgent()
    return agent.synthesize(question, result_files)

