import time
import src.utils.console_display  # Windows UTF-8 console output support
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from .schemas import (
    SearchDomain, SearchResult, SemanticSearchQuery, 
    SemanticSearchResponse, RelaxationSearchRequest,
    RelaxationOption, RelaxationSearchResponse
)
from .embedder import HotelEmbedder, HospitalityEmbedder
from .faiss_store import FAISSVectorStore, HybridFAISSStore

logger = logging.getLogger(__name__)


class SemanticSearchEngine:
    """Main semantic search engine for hotel knowledge."""
    
    DEFAULT_INDEX_DIR = "data/faiss_index"
    
    def __init__(
        self, 
        embedder: Optional[HotelEmbedder] = None,
        index_dir: str = DEFAULT_INDEX_DIR,
        use_hybrid: bool = True
    ):
        self.embedder = embedder or HotelEmbedder()
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        index_path = str(self.index_dir / "hotel_index.faiss")
        metadata_path = str(self.index_dir / "hotel_metadata.pkl")
        
        store_class = HybridFAISSStore if use_hybrid else FAISSVectorStore
        self.store = store_class(
            embedder=self.embedder,
            index_path=index_path,
            metadata_path=metadata_path
        )
        self._loaded = False
    
    def load_or_build(self, documents: Optional[List[Dict[str, Any]]] = None):
        """Load existing index or build new one."""
        if self.store._initialized:
            return
        
        try:
            self.store.load()
            if self.store._initialized:
                logger.info("Loaded existing FAISS index")
                self._loaded = True
                return
        except Exception as e:
            logger.warning(f"Could not load index: {e}")
        
        if documents:
            self.build_index(documents)
        else:
            self.build_from_knowledge_base()
    
    def build_from_knowledge_base(self):
        """Build index from hotel knowledge base."""
        from src.module2_kb.kb_manager import KnowledgeBaseManager
        from src.module5_rag.chunker import MarkdownChunker
        
        kb = KnowledgeBaseManager()
        chunker = MarkdownChunker()
        
        documents = []
        
        for room in kb.rooms:
            content = f"{room.name} ({room.tier} Tier): {room.bed_configuration}, {room.square_meters} sqm, {room.view_type} view. Base rate: ${room.base_rate_usd}/night. Features: {', '.join(room.features)}."
            documents.append({
                "content": content,
                "source": "rooms.json",
                "domain": SearchDomain.ROOMS,
                "chunk_id": f"room_{room.id}",
                "metadata": {"room_type": room.name, "tier": room.tier}
            })
        
        for restaurant in kb.restaurants:
            hours_str = ", ".join(f"{k}: {v}" for k, v in restaurant.hours.items())
            content = f"{restaurant.name} ({restaurant.cuisine_type}, {restaurant.dining_style}): Located at {restaurant.location}. Hours: {hours_str}. Signature dishes: {', '.join(restaurant.signature_dishes)}. Dress code: {restaurant.dress_code}."
            documents.append({
                "content": content,
                "source": "dining.json",
                "domain": SearchDomain.DINING,
                "chunk_id": f"restaurant_{restaurant.id}",
                "metadata": {"cuisine": restaurant.cuisine_type, "price_level": restaurant.price_level}
            })
        
        for spa in kb.spa_treatments:
            content = f"{spa.name}: {spa.description}. Duration: {spa.duration_minutes} mins. Category: {spa.category}. Price: ${spa.price_usd}."
            documents.append({
                "content": content,
                "source": "spa.json",
                "domain": SearchDomain.SPA,
                "chunk_id": f"spa_{spa.id}",
                "metadata": {"category": spa.category, "price": spa.price_usd}
            })
        
        for amenity in kb.amenities:
            content = f"{amenity.name} ({amenity.category}): Located at {amenity.location}. Hours: {amenity.operating_hours}. Access fee: ${amenity.access_fee_usd}. Rules: {', '.join(amenity.rules)}."
            documents.append({
                "content": content,
                "source": "amenities.json",
                "domain": SearchDomain.AMENITIES,
                "chunk_id": f"amenity_{amenity.id}",
                "metadata": {"category": amenity.category, "fee": amenity.access_fee_usd}
            })
        
        for policy in kb.policies:
            content = f"{policy.title}: {policy.summary}. Details: {policy.details}."
            documents.append({
                "content": content,
                "source": "policies.json",
                "domain": SearchDomain.POLICIES,
                "chunk_id": f"policy_{policy.id}",
                "metadata": {"strictness": policy.strictness_level}
            })
        
        markdown_dir = Path("data/knowledge_docs")
        if markdown_dir.exists():
            for md_file in markdown_dir.glob("*.md"):
                chunks = chunker.chunk_file(str(md_file))
                for i, chunk in enumerate(chunks):
                    domain = self._infer_domain_from_filename(md_file.name)
                    documents.append({
                        "content": chunk.content,
                        "source": md_file.name,
                        "domain": domain,
                        "chunk_id": f"{md_file.stem}_{i}",
                        "metadata": {"section": chunk.header}
                    })
        
        self.build_index(documents)
    
    def _infer_domain_from_filename(self, filename: str) -> SearchDomain:
        fname = filename.lower()
        if "spa" in fname or "wellness" in fname:
            return SearchDomain.SPA
        elif "dining" in fname or "restaurant" in fname or "bar" in fname:
            return SearchDomain.DINING
        elif "room" in fname or "suite" in fname:
            return SearchDomain.ROOMS
        elif "amenit" in fname or "facil" in fname or "pool" in fname or "gym" in fname:
            return SearchDomain.AMENITIES
        elif "policy" in fname or "regulat" in fname:
            return SearchDomain.POLICIES
        elif "attraction" in fname or "local" in fname:
            return SearchDomain.ATTRACTIONS
        elif "transport" in fname:
            return SearchDomain.TRANSPORTATION
        return SearchDomain.ALL
    
    def build_index(self, documents: List[Dict[str, Any]]):
        """Build FAISS index from documents."""
        texts = [d["content"] for d in documents]
        metadatas = documents
        self.store.initialize(texts, metadatas)
        self._loaded = True
    
    def search(self, query: SemanticSearchQuery) -> SemanticSearchResponse:
        """Execute semantic search."""
        start_time = time.time()
        
        self.load_or_build()
        
        if isinstance(self.store, HybridFAISSStore):
            results = self.store.hybrid_search(
                query.query,
                top_k=query.top_k,
                domain_filter=query.domains[0] if len(query.domains) == 1 else None,
                min_score=query.min_score
            )
        else:
            results = self.store.search(
                query.query,
                top_k=query.top_k,
                domain_filter=query.domains[0] if len(query.domains) == 1 else None,
                min_score=query.min_score
            )
        
        search_time = (time.time() - start_time) * 1000
        
        return SemanticSearchResponse(
            query=query.query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time,
            embedding_model=self.embedder.model_name
        )
    
    def search_relaxation(self, request: RelaxationSearchRequest) -> RelaxationSearchResponse:
        """Specialized search for relaxation/evening queries."""
        self.load_or_build()
        
        enhanced_query = request.query
        if isinstance(self.embedder, HospitalityEmbedder):
            enhanced_query = self.embedder.enhance_query_for_relaxation(request.query)
        
        relaxation_domains = [SearchDomain.SPA, SearchDomain.LOUNGE, SearchDomain.POOL, SearchDomain.GARDEN, SearchDomain.DINING]
        
        all_results = []
        for domain in relaxation_domains:
            results = self.store.search(enhanced_query, top_k=request.top_k, domain_filter=domain)
            all_results.extend(results)
        
        all_results.sort(key=lambda x: x.score, reverse=True)
        top_results = all_results[:request.top_k]
        
        options = []
        for r in top_results:
            suitability = r.score
            if isinstance(self.embedder, HospitalityEmbedder):
                suitability *= (1 + self.embedder.relaxation_relevance(r.content)) / 2
            
            options.append(RelaxationOption(
                name=self._extract_name(r.content, r.source),
                type=r.domain.value,
                description=r.content[:300],
                location=r.metadata.get("location", "Hotel premises"),
                hours=r.metadata.get("hours", "Varies"),
                amenities=r.metadata.get("amenities", []),
                suitability_score=min(suitability, 1.0),
                source=r.source
            ))
        
        reasoning = self._generate_relaxation_reasoning(request.query, options)
        
        return RelaxationSearchResponse(
            query=request.query,
            options=options,
            reasoning=reasoning
        )
    
    def _extract_name(self, content: str, source: str) -> str:
        """Extract a friendly name from content."""
        parts = content.split(":")
        if len(parts) > 1:
            return parts[0].strip()
        return source.replace(".json", "").replace(".md", "").replace("_", " ").title()
    
    def _generate_relaxation_reasoning(self, query: str, options: List[RelaxationOption]) -> str:
        """Generate reasoning for relaxation recommendations."""
        if not options:
            return "No suitable relaxation options found matching your criteria."
        
        types = list(set(o.type for o in options))
        top_option = options[0]
        
        return (
            f"Based on your request '{query}', I found {len(options)} relaxation options "
            f"across {', '.join(types)}. The top recommendation is {top_option.name} "
            f"({top_option.type}) with a suitability score of {top_option.suitability_score:.0%}. "
            f"This location offers {top_option.description[:100]}..."
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get search engine statistics."""
        return self.store.get_stats()


def run_lab6():
    """Run Module 6 lab demonstration."""
    print("=" * 80)
    print("🏨 MODULE 6: SEMANTIC HOTEL SEARCH")
    print("=" * 80)
    
    print("\n📦 Initializing Semantic Search Engine with FAISS + MiniLM...")
    engine = SemanticSearchEngine(use_hybrid=True)
    engine.load_or_build()
    
    stats = engine.get_stats()
    print(f"\n📊 Index Statistics:")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Dimension: {stats['dimension']}")
    print(f"   Domains: {stats['domains']}")
    
    test_queries = [
        "Where can I relax after dinner?",
        "I want a quiet place for evening drinks",
        "Best spot for a romantic evening",
        "Where is the spa and what treatments do they offer?",
        "Pool hours and amenities",
        "Family friendly activities near hotel"
    ]
    
    print("\n🔍 Testing Semantic Search Queries:")
    print("-" * 80)
    
    for query in test_queries:
        print(f"\n❓ Query: \"{query}\"")
        
        search_query = SemanticSearchQuery(query=query, top_k=3)
        response = engine.search(search_query)
        
        print(f"   ⏱️  Search time: {response.search_time_ms:.1f}ms")
        print(f"   📄 Results: {response.total_results}")
        
        for i, result in enumerate(response.results, 1):
            print(f"   {i}. [{result.domain.value}] {result.source} (score: {result.score:.3f})")
            print(f"      \"{result.content[:150]}...\"")
    
    print("\n" + "=" * 80)
    print("🧘 Testing Relaxation Search:")
    print("=" * 80)
    
    relax_request = RelaxationSearchRequest(
        query="Where can I relax after dinner?",
        preferences={"quiet": True, "romantic": True},
        time_of_day="evening",
        party_size=2
    )
    
    relax_response = engine.search_relaxation(relax_request)
    
    print(f"\n❓ Query: \"{relax_request.query}\"")
    print(f"💭 Reasoning: {relax_response.reasoning}")
    print(f"\n🏆 Top Relaxation Options:")
    
    for i, opt in enumerate(relax_response.options, 1):
        print(f"\n   {i}. {opt.name} ({opt.type}) - {opt.suitability_score:.0%} match")
        print(f"      📍 {opt.location} | 🕐 {opt.hours}")
        print(f"      📝 {opt.description[:200]}...")
    
    print("\n" + "=" * 80)
    print("✅ MODULE 6 LAB COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    run_lab6()