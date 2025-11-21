"""
Unified search service - THE GLUE LAYER.
Wraps SLR providers without modifying them.

This service connects our syntax generation (from dialects.py) with
actual query execution using the SLR provider infrastructure.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path
import time
import logging
import json
from datetime import datetime

# Import from vendor library (SLR)
from src.slr.providers.openalex import OpenAlexProvider
from src.slr.providers.arxiv import ArxivProvider
from src.slr.providers.crossref import CrossRefProvider
from src.slr.providers.s2 import SemanticScholarProvider
from src.slr.core.models import Document, Query
from src.slr.dedup.deduplicator import Deduplicator
from src.slr.export.csv_exporter import CSVExporter
from src.slr.export.bibtex_exporter import BibTeXExporter
from src.slr.export.jsonl_exporter import JSONLExporter

logger = logging.getLogger(__name__)


@dataclass
class SearchResultsSummary:
    """Lightweight summary for session state (NOT full papers)."""
    database: str
    query: str
    total_hits: int
    execution_time: float
    error: Optional[str] = None
    result_file: Optional[str] = None  # Path to saved results
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class SearchService:
    """
    Execute searches across multiple databases using SLR providers.
    
    CRITICAL: This is the ADAPTER layer. Do NOT modify SLR code.
    We treat SLR as a "vendor library" - it's already tested and works.
    """
    
    # Map our database names to SLR providers
    # NOTE: PubMed and Scopus are NOT here (no SLR connectors yet)
    PROVIDERS = {
        'openalex': OpenAlexProvider,
        'arxiv': ArxivProvider,
        'crossref': CrossRefProvider,
        'semanticscholar': SemanticScholarProvider,
        's2': SemanticScholarProvider,  # Alias
    }
    
    # Databases we generate syntax for but CAN'T execute yet
    SYNTAX_ONLY = {
        'pubmed': 'PubMed connector requires E-utilities authentication. Use copy/paste for now.',
        'scopus': 'Scopus connector requires API key. Use copy/paste for now.',
        'wos': 'Web of Science connector requires API key. Use copy/paste for now.',
    }
    
    def __init__(self, results_dir: str = "data/search_results"):
        """Initialize search service with result storage directory."""
        self.deduplicator = Deduplicator()
        self._provider_instances = {}
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"SearchService initialized (adapter layer) - results dir: {self.results_dir}")
    
    def get_available_databases(self) -> List[str]:
        """Return databases we can actually execute (not just generate syntax for)."""
        return list(self.PROVIDERS.keys())
    
    def get_syntax_only_databases(self) -> Dict[str, str]:
        """Return databases we can't execute yet with reasons."""
        return self.SYNTAX_ONLY
    
    def is_executable(self, database: str) -> bool:
        """Check if a database can be executed (not just syntax generation)."""
        return database.lower() in self.PROVIDERS
        
    def _get_provider(self, database: str):
        """Get or create provider instance (cached)."""
        db_lower = database.lower()
        
        if db_lower not in self.PROVIDERS:
            raise ValueError(f"Database '{database}' not supported. Available: {list(self.PROVIDERS.keys())}")
        
        # Create instance if not cached
        if db_lower not in self._provider_instances:
            provider_class = self.PROVIDERS[db_lower]
            self._provider_instances[db_lower] = provider_class()
            logger.info(f"Created {provider_class.__name__} instance")
        
        return self._provider_instances[db_lower]
    
    def execute_search(
        self, 
        database: str, 
        query: str, 
        max_results: int = 100,
        save_to_disk: bool = True
    ) -> SearchResultsSummary:
        """
        Execute search and return SUMMARY only (not full papers).
        Full results saved to disk to avoid bloating session state.
        
        Args:
            database: Database name (openalex, arxiv, crossref, semanticscholar)
            query: Search query string
            max_results: Maximum number of results to fetch
            save_to_disk: Whether to save full results to disk
            
        Returns:
            SearchResultsSummary with metadata and path to saved results
        """
        logger.info(f"Executing search: database={database}, query={query[:50]}..., max={max_results}")
        
        try:
            start_time = time.time()
            
            # Get provider
            provider = self._get_provider(database)
            
            # Create Query object (SLR model)
            query_obj = Query(
                text=query,
                max_results=max_results
            )
            
            # Execute search using SLR provider
            documents: List[Document] = []
            for doc in provider.search(query_obj):
                documents.append(doc)
                if len(documents) >= max_results:
                    break
            
            execution_time = time.time() - start_time
            
            logger.info(f"Search completed: {len(documents)} results in {execution_time:.2f}s")
            
            # Save results to disk immediately
            result_file = None
            if save_to_disk and documents:
                result_file = self._save_results(database, query, documents)
            
            # Return lightweight summary
            return SearchResultsSummary(
                database=database,
                query=query,
                total_hits=len(documents),
                execution_time=execution_time,
                result_file=result_file
            )
            
        except Exception as e:
            logger.error(f"Search failed for {database}: {str(e)}", exc_info=True)
            return SearchResultsSummary(
                database=database,
                query=query,
                total_hits=0,
                execution_time=0.0,
                error=str(e)
            )
    
    def _save_results(self, database: str, query: str, documents: List[Document]) -> str:
        """
        Save results to disk, return filepath.
        
        Saves in JSON format with metadata for later loading.
        """
        # Create sanitized filename
        query_short = query[:30].replace(' ', '_').replace('/', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{database}_{query_short}_{timestamp}.json"
        filepath = self.results_dir / filename
        
        # Serialize documents
        # Convert SLR Document objects to dicts
        data = {
            'metadata': {
                'database': database,
                'query': query,
                'timestamp': datetime.now().isoformat(),
                'total_results': len(documents)
            },
            'documents': [self._document_to_dict(doc) for doc in documents]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(documents)} results to {filepath}")
        return str(filepath)
    
    def _document_to_dict(self, doc: Document) -> dict:
        """Convert SLR Document to JSON-serializable dict."""
        return {
            'title': doc.title,
            'abstract': doc.abstract,
            'authors': [{'name': a.name, 'affiliation': getattr(a, 'affiliation', None)} 
                       for a in (doc.authors or [])],
            'year': doc.year,
            'doi': doc.external_ids.doi if doc.external_ids else None,
            'pmid': doc.external_ids.pmid if doc.external_ids else None,
            'arxiv_id': doc.external_ids.arxiv if doc.external_ids else None,
            'url': doc.url,
            'venue': doc.venue,
            'citation_count': doc.citation_count,
            'source': doc.source
        }
    
    def load_results(self, result_file: str) -> List[Dict]:
        """
        Load results from disk.
        
        Returns list of document dicts (not full Document objects to keep it simple).
        """
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return data.get('documents', [])
    
    def deduplicate_results(self, result_files: List[str]) -> List[Dict]:
        """
        Deduplicate results from multiple searches.
        
        Uses SLR's deduplication logic (DOI, title similarity, fingerprint).
        """
        logger.info(f"Deduplicating {len(result_files)} result sets")
        
        # Load all documents
        all_docs = []
        for result_file in result_files:
            docs = self.load_results(result_file)
            all_docs.extend(docs)
        
        logger.info(f"Total documents before dedup: {len(all_docs)}")
        
        # Convert back to Document objects for deduplication
        doc_objects = []
        for doc_dict in all_docs:
            try:
                # Reconstruct Document object (simplified)
                from src.slr.core.models import Document, Author, ExternalIds
                
                authors = [Author(name=a['name']) for a in doc_dict.get('authors', [])]
                external_ids = ExternalIds(
                    doi=doc_dict.get('doi'),
                    pmid=doc_dict.get('pmid'),
                    arxiv=doc_dict.get('arxiv_id')
                )
                
                doc = Document(
                    title=doc_dict['title'],
                    abstract=doc_dict.get('abstract'),
                    authors=authors,
                    year=doc_dict.get('year'),
                    external_ids=external_ids,
                    url=doc_dict.get('url'),
                    venue=doc_dict.get('venue'),
                    citation_count=doc_dict.get('citation_count'),
                    source=doc_dict.get('source', 'unknown')
                )
                doc_objects.append(doc)
            except Exception as e:
                logger.warning(f"Skipping invalid document: {e}")
        
        # Deduplicate using SLR deduplicator
        unique_docs = self.deduplicator.deduplicate(doc_objects)
        
        logger.info(f"Documents after dedup: {len(unique_docs)}")
        
        # Convert back to dicts
        return [self._document_to_dict(doc) for doc in unique_docs]
    
    def export_results(
        self, 
        documents: List[Dict], 
        format: str, 
        output_path: str
    ) -> str:
        """
        Export results to various formats.
        
        Args:
            documents: List of document dicts
            format: Export format ('csv', 'bibtex', 'jsonl')
            output_path: Path to save the export
            
        Returns:
            Path to exported file
        """
        logger.info(f"Exporting {len(documents)} documents to {format}")
        
        # Convert dicts back to Document objects
        from src.slr.core.models import Document, Author, ExternalIds
        
        doc_objects = []
        for doc_dict in documents:
            authors = [Author(name=a['name']) for a in doc_dict.get('authors', [])]
            external_ids = ExternalIds(
                doi=doc_dict.get('doi'),
                pmid=doc_dict.get('pmid'),
                arxiv=doc_dict.get('arxiv_id')
            )
            
            doc = Document(
                title=doc_dict['title'],
                abstract=doc_dict.get('abstract'),
                authors=authors,
                year=doc_dict.get('year'),
                external_ids=external_ids,
                url=doc_dict.get('url'),
                venue=doc_dict.get('venue'),
                citation_count=doc_dict.get('citation_count'),
                source=doc_dict.get('source', 'unknown')
            )
            doc_objects.append(doc)
        
        # Select exporter
        if format == 'csv':
            exporter = CSVExporter()
        elif format == 'bibtex':
            exporter = BibTeXExporter()
        elif format == 'jsonl':
            exporter = JSONLExporter()
        else:
            raise ValueError(f"Unsupported format: {format}. Use csv, bibtex, or jsonl")
        
        # Export
        exporter.export(doc_objects, output_path)
        
        logger.info(f"Exported to {output_path}")
        return output_path


# Singleton instance for easy access
_search_service = None

def get_search_service() -> SearchService:
    """Get or create the search service singleton."""
    global _search_service
    if _search_service is None:
        _search_service = SearchService()
    return _search_service

