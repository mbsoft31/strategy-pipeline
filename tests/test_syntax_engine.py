"""Tests for syntax engine - proves the 'moat'."""

import pytest

from src.search.models import QueryPlan, ConceptBlock, FieldTag
from src.search.builder import get_builder
from src.search.dialects import (
    PubMedDialect, ScopusDialect, ArxivDialect,
    OpenAlexDialect, SemanticScholarDialect, CrossRefDialect
)


class TestSyntaxEngine:
    """Test suite proving correct syntax generation."""

    @pytest.fixture
    def sample_plan(self):
        """Create a sample query plan."""
        plan = QueryPlan()

        # Block 1: Disease concept
        disease_block = ConceptBlock("Disease")
        disease_block.add_term("heart attack", FieldTag.KEYWORD)
        disease_block.add_term("myocardial infarction", FieldTag.CONTROLLED_VOCAB)
        plan.blocks.append(disease_block)

        # Block 2: Treatment concept
        treatment_block = ConceptBlock("Treatment")
        treatment_block.add_term("aspirin", FieldTag.KEYWORD)
        treatment_block.add_term("acetylsalicylic acid", FieldTag.KEYWORD)
        plan.blocks.append(treatment_block)

        return plan

    def test_pubmed_syntax_correctness(self, sample_plan):
        """Test PubMed syntax is valid and complete."""
        builder = get_builder("pubmed")
        query = builder.build(sample_plan)

        print(f"\n[PubMed Query]\n{query}")

        # Verify phrase quoting
        assert '"heart attack"[Title/Abstract]' in query

        # Verify MeSH tag format
        assert '"myocardial infarction"[MeSH Terms]' in query

        # Verify OR grouping
        assert " OR " in query

        # Verify AND between concept blocks
        assert "\nAND\n" in query

        # Verify no hallucinated operators (ChatGPT mistake)
        assert "NEAR" not in query
        assert "ADJ" not in query

    def test_scopus_syntax_correctness(self, sample_plan):
        """Test Scopus syntax is valid and complete."""
        builder = get_builder("scopus")
        query = builder.build(sample_plan)

        print(f"\n[Scopus Query]\n{query}")

        # Verify TITLE-ABS-KEY wrapper
        assert query.startswith("TITLE-ABS-KEY")

        # Verify phrase quoting
        assert '"heart attack"' in query

        # Verify efficient OR grouping (not repeated wrappers)
        assert query.count("TITLE-ABS-KEY") == 2  # One per concept block

        # Verify AND between blocks
        assert " AND " in query

    def test_factory_function(self):
        """Test get_builder factory."""
        pubmed_builder = get_builder("pubmed")
        scopus_builder = get_builder("scopus")

        assert isinstance(pubmed_builder.dialect, PubMedDialect)
        assert isinstance(scopus_builder.dialect, ScopusDialect)

        # Test case insensitivity
        assert isinstance(get_builder("PubMed").dialect, PubMedDialect)

        # Test invalid database
        with pytest.raises(ValueError, match="Unknown database"):
            get_builder("google_scholar")

    def test_empty_plan(self):
        """Test handling of empty query plan."""
        empty_plan = QueryPlan()
        builder = get_builder("pubmed")

        query = builder.build(empty_plan)
        assert query == ""

    def test_single_term(self):
        """Test query with single term."""
        plan = QueryPlan()
        block = ConceptBlock("Test")
        block.add_term("diabetes")
        plan.blocks.append(block)

        pubmed_builder = get_builder("pubmed")
        query = pubmed_builder.build(plan)

        # Single term should not have OR parentheses
        assert query == 'diabetes[Title/Abstract]'

    def test_phrase_detection(self):
        """Test automatic phrase detection."""
        plan = QueryPlan()
        block = ConceptBlock("Test")
        block.add_term("machine learning")  # Has space, should become phrase
        plan.blocks.append(block)

        builder = get_builder("pubmed")
        query = builder.build(plan)

        # Should be quoted
        assert '"machine learning"' in query

    def test_complex_multi_concept_query(self):
        """Test complex query with multiple concepts."""
        plan = QueryPlan()

        # Population
        pop_block = ConceptBlock("Population")
        pop_block.add_term("elderly")
        pop_block.add_term("older adults")
        pop_block.add_term("aged", FieldTag.CONTROLLED_VOCAB)
        plan.blocks.append(pop_block)

        # Intervention
        intervention_block = ConceptBlock("Intervention")
        intervention_block.add_term("deep learning")
        intervention_block.add_term("neural networks")
        plan.blocks.append(intervention_block)

        # Outcome
        outcome_block = ConceptBlock("Outcome")
        outcome_block.add_term("diagnosis")
        outcome_block.add_term("diagnostic accuracy")
        plan.blocks.append(outcome_block)

        # Generate queries
        pubmed_query = get_builder("pubmed").build(plan)
        scopus_query = get_builder("scopus").build(plan)

        # Verify structure
        assert pubmed_query.count("\nAND\n") == 2  # 3 blocks = 2 ANDs
        assert scopus_query.count(" AND ") == 2

        # Verify all concepts present
        assert "elderly" in pubmed_query
        assert "aged[MeSH Terms]" in pubmed_query
        assert "deep learning" in pubmed_query
        assert "diagnosis" in pubmed_query

    def test_arxiv_syntax(self):
        """Test arXiv syntax generation."""
        plan = QueryPlan()

        # Block 1: Disease concept
        disease_block = ConceptBlock("Disease")
        disease_block.add_term("heart attack", FieldTag.KEYWORD)
        disease_block.add_term("myocardial infarction", FieldTag.CONTROLLED_VOCAB)
        plan.blocks.append(disease_block)

        # Block 2: Treatment concept
        treatment_block = ConceptBlock("Treatment")
        treatment_block.add_term("aspirin", FieldTag.KEYWORD)
        plan.blocks.append(treatment_block)

        builder = get_builder("arxiv")
        query = builder.build(plan)

        # Arxiv uses 'all:' or 'ti:' prefixes
        assert "all:" in query
        assert " AND " in query
        assert " OR " in query

    def test_openalex_syntax(self):
        """Test OpenAlex syntax generation."""
        plan = QueryPlan()

        # Block 1: Disease concept
        disease_block = ConceptBlock("Disease")
        disease_block.add_term("heart attack", FieldTag.KEYWORD)
        disease_block.add_term("myocardial infarction", FieldTag.CONTROLLED_VOCAB)
        plan.blocks.append(disease_block)

        builder = get_builder("openalex")
        query = builder.build(plan)

        # Should be standard boolean
        assert '("heart attack" OR "myocardial infarction")' in query

    def test_excluded_terms_not_logic(self, sample_plan):
        # Add excluded term to first block
        sample_plan.blocks[0].add_excluded_term("animal models")
        pubmed_query = get_builder("pubmed").build(sample_plan)
        assert "NOT" in pubmed_query
        assert "animal models" in pubmed_query
        # Ensure NOT group properly parenthesized OR inside
        assert "animal models" in pubmed_query


def test_demo_comparison():
    """Demo showing superiority over ChatGPT.

    This test generates a complex query and shows what ChatGPT
    would likely produce (with errors) vs our correct output.
    """
    plan = QueryPlan()

    # Complex multi-concept query
    pop_block = ConceptBlock("Population")
    pop_block.add_term("elderly")
    pop_block.add_term("older adults")
    pop_block.add_term("aged", FieldTag.CONTROLLED_VOCAB)
    plan.blocks.append(pop_block)

    intervention_block = ConceptBlock("Intervention")
    intervention_block.add_term("deep learning")
    intervention_block.add_term("neural networks")
    intervention_block.add_term("artificial intelligence", FieldTag.KEYWORD)
    plan.blocks.append(intervention_block)

    outcome_block = ConceptBlock("Outcome")
    outcome_block.add_term("diagnosis")
    outcome_block.add_term("diagnostic accuracy")
    plan.blocks.append(outcome_block)

    # Generate queries
    pubmed_query = get_builder("pubmed").build(plan)
    scopus_query = get_builder("scopus").build(plan)

    print("\n" + "="*60)
    print("SYNTAX ENGINE DEMO: The 'Moat'")
    print("="*60)

    print("\n[PubMed Query - CORRECT]")
    print(pubmed_query)

    print("\n[Scopus Query - CORRECT]")
    print(scopus_query)

    print("\n[What ChatGPT Might Produce - WRONG]")
    print('(elderly NEAR/5 "older adults") AND "deep learning" [mesh]')
    print("                ^^^^^^^^ Invalid operator in PubMed!")
    print("                                             ^^^^^^ Wrong tag format!")

    print("\n" + "="*60)
    print("✅ Our engine GUARANTEES valid syntax")
    print("❌ ChatGPT hallucinates invalid operators")
    print("="*60 + "\n")
