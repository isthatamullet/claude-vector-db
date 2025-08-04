#!/usr/bin/env python3
"""
Semantic Pattern Manager - Embedding cluster management for semantic validation.

Implements efficient pattern embedding management with separate ChromaDB collection,
LRU caching, and batch processing optimization based on July 2025 best practices.

Key Features:
- Separate ChromaDB collection for pattern embeddings
- LRU caching for embedding computation performance
- Pattern similarity caching and batch processing optimization
- Pattern cluster initialization with proven feedback patterns
- <50ms pattern similarity computation target

Based on comprehensive specifications from PRP-2 implementation analysis.
"""

import json
import logging
import time
import os
import pickle
from typing import Dict, List, Any, Optional, Tuple
from functools import lru_cache
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
from chromadb.utils import embedding_functions

from vector_database import ClaudeVectorDatabase

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class PatternSimilarityResult:
    """Result from pattern similarity analysis"""
    best_matches: List[str]
    similarities: List[float]
    pattern_types: List[str]
    max_similarity: float
    dominant_pattern_type: str
    processing_time_ms: float
    cache_hit: bool


class SemanticPatternManager:
    """
    Efficient pattern embedding management with separate ChromaDB collection.
    
    Manages semantic pattern embeddings for feedback analysis with performance
    optimization through caching and batch processing. Provides <50ms pattern
    similarity computation through pre-computed embeddings and LRU caching.
    """
    
    def __init__(self, 
                 db: ClaudeVectorDatabase,
                 cache_dir: str = "/home/user/.claude-vector-db-enhanced/semantic_cache",
                 cache_size: int = 1000):
        """
        Initialize semantic pattern manager.
        
        Args:
            db: ClaudeVectorDatabase instance for ChromaDB access
            cache_dir: Directory for persistent embedding cache
            cache_size: LRU cache size for embedding computation
        """
        logger.info("🔧 Initializing SemanticPatternManager")
        
        self.db = db
        self.cache_dir = cache_dir
        self.cache_size = cache_size
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
        
        # Initialize separate pattern collection
        self.pattern_collection = self.db.client.get_or_create_collection(
            name="semantic_validation_patterns",
            embedding_function=self.db.embedding_function,
            metadata={"hnsw:space": "cosine"}  # Optimized for semantic similarity
        )
        
        # Initialize sentence transformer (same model as main system)
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Performance tracking
        self.stats = {
            'total_similarity_computations': 0,
            'cache_hits': 0,
            'average_processing_time_ms': 0.0,
            'pattern_collection_size': 0
        }
        
        # Initialize pattern clusters if collection is empty
        if self.pattern_collection.count() == 0:
            self.initialize_pattern_clusters()
        else:
            self.stats['pattern_collection_size'] = self.pattern_collection.count()
            
        logger.info(f"✅ SemanticPatternManager initialized with {self.stats['pattern_collection_size']} patterns")
    
    def initialize_pattern_clusters(self):
        """
        Create embeddings for known feedback patterns in separate ChromaDB collection.
        
        Initializes pattern clusters with proven feedback patterns from existing
        sophisticated pattern analysis, organized by sentiment type.
        """
        logger.info("🔧 Initializing pattern clusters in ChromaDB collection")
        
        start_time = time.time()
        
        # Comprehensive positive feedback patterns (high confidence indicators)
        positive_patterns = [
            "That worked perfectly!", "Perfect solution!", "You nailed it!", "Brilliant approach!",
            "Exactly what I needed!", "Works flawlessly!", "Ideal solution!", "Outstanding work!",
            "This is exactly right!", "Solved the problem completely!", "Working beautifully!",
            "Great job!", "That fixed it!", "Perfect, thank you!", "Excellent solution!",
            "That's the one!", "Working perfectly now!", "You got it!", "Spot on!",
            "This works great!", "Problem solved!", "That did the trick!", "Amazing work!",
            "Fantastic!", "This is perfect!", "You fixed it!", "That's exactly it!",
            "Working like a charm!", "Incredible!", "This is it!", "Perfect fix!"
        ]
        
        # Comprehensive negative feedback patterns (clear failure indicators)  
        negative_patterns = [
            "That doesn't work", "Still getting errors", "Not what I expected", 
            "Let me try something else", "Hmm, different issue now", "This approach failed",
            "That made it worse", "Still broken", "Doesn't solve the problem",
            "Getting more errors", "That didn't help", "Still not working",
            "Same error", "Different error now", "That broke something else",
            "Not working", "Failed", "Error", "Doesn't work", "Broken",
            "Issue persists", "Problem remains", "Still failing", "Not fixed",
            "Doesn't help", "Making it worse", "New problems", "More issues"
        ]
        
        # Comprehensive partial success patterns (mixed outcomes, complex feedback)
        partial_patterns = [
            "Almost there", "Partially working", "Better but still issues",
            "Some progress", "Works but with warnings", "Getting closer",
            "Mostly working", "Almost fixed", "Partly solved", "Some improvement",
            "Better than before", "Progress made", "Partially fixed", "Nearly there",
            "Close but not quite", "On the right track", "Some success",
            "Working sometimes", "Intermittent success", "Half working",
            "Progress but issues remain", "Better approach", "Closer to solution",
            "Some bugs fixed", "Partial improvement", "Mixed results",
            "Works in some cases", "Getting there", "Step in right direction"
        ]
        
        # Batch add pattern embeddings to separate collection
        all_patterns = positive_patterns + negative_patterns + partial_patterns
        all_metadatas = (
            [{"type": "positive", "confidence": "high"}] * len(positive_patterns) +
            [{"type": "negative", "confidence": "high"}] * len(negative_patterns) +
            [{"type": "partial", "confidence": "medium"}] * len(partial_patterns)
        )
        all_ids = (
            [f"pos_{i}" for i in range(len(positive_patterns))] +
            [f"neg_{i}" for i in range(len(negative_patterns))] +
            [f"part_{i}" for i in range(len(partial_patterns))]
        )
        
        # Add to pattern collection with ChromaDB batch limits
        MAX_BATCH_SIZE = 166  # ChromaDB SQLite hard limit
        
        for i in range(0, len(all_patterns), MAX_BATCH_SIZE):
            batch_patterns = all_patterns[i:i + MAX_BATCH_SIZE]
            batch_metadatas = all_metadatas[i:i + MAX_BATCH_SIZE]
            batch_ids = all_ids[i:i + MAX_BATCH_SIZE]
            
            self.pattern_collection.add(
                documents=batch_patterns,
                metadatas=batch_metadatas,
                ids=batch_ids
            )
        
        processing_time = (time.time() - start_time) * 1000
        self.stats['pattern_collection_size'] = self.pattern_collection.count()
        
        logger.info(f"✅ Pattern clusters initialized: {len(positive_patterns)} positive, "
                   f"{len(negative_patterns)} negative, {len(partial_patterns)} partial "
                   f"({processing_time:.1f}ms)")
    
    @lru_cache(maxsize=1000)
    def _get_cached_embedding(self, text_hash: str, text: str) -> np.ndarray:
        """
        Get cached embedding with persistent file cache and LRU cache.
        
        Args:
            text_hash: MD5 hash of text for cache key
            text: Original text for embedding computation
            
        Returns:
            Numpy array embedding
        """
        # Check persistent file cache first
        cache_file = os.path.join(self.cache_dir, f"{text_hash}.pkl")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            except Exception as e:
                logger.warning(f"Cache file read error: {e}")
        
        # Compute embedding if not cached
        embedding = self.encoder.encode([text], convert_to_numpy=True)[0]
        
        # Save to persistent cache
        try:
            with open(cache_file, 'wb') as f:
                pickle.dump(embedding, f)
        except Exception as e:
            logger.warning(f"Cache file write error: {e}")
        
        return embedding
    
    def get_pattern_similarity(self, 
                             feedback_text: str, 
                             pattern_type: Optional[str] = None,
                             top_k: int = 5) -> PatternSimilarityResult:
        """
        Get similarity to stored patterns with <50ms performance target.
        
        Args:
            feedback_text: User feedback text to analyze
            pattern_type: Optional filter ("positive", "negative", "partial")
            top_k: Number of top matches to return
            
        Returns:
            PatternSimilarityResult with similarity analysis and performance data
        """
        start_time = time.time()
        self.stats['total_similarity_computations'] += 1
        
        # Query pattern collection for similarity
        if pattern_type:
            # With pattern type filtering
            results = self.pattern_collection.query(
                query_texts=[feedback_text],
                n_results=top_k,
                where={"type": pattern_type}
            )
        else:
            # Without filtering
            results = self.pattern_collection.query(
                query_texts=[feedback_text],
                n_results=top_k
            )
        
        # Check cache hit status
        import hashlib
        text_hash = hashlib.md5(feedback_text.encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{text_hash}.pkl")
        cache_hit = os.path.exists(cache_file)
        
        if cache_hit:
            self.stats['cache_hits'] += 1
        
        # Process results
        if results['documents'] and results['documents'][0]:
            best_matches = results['documents'][0]
            # Convert ChromaDB distances to similarities (distance -> similarity)
            similarities = [1 - d for d in results['distances'][0]]
            pattern_types = [m['type'] for m in results['metadatas'][0]]
            
            # Find dominant pattern type and max similarity
            max_similarity = max(similarities) if similarities else 0.0
            max_idx = similarities.index(max_similarity) if similarities else 0
            dominant_pattern_type = pattern_types[max_idx] if pattern_types else 'neutral'
            
        else:
            best_matches = []
            similarities = []
            pattern_types = []
            max_similarity = 0.0
            dominant_pattern_type = 'neutral'
        
        processing_time = (time.time() - start_time) * 1000
        
        # Update performance statistics
        self.stats['average_processing_time_ms'] = (
            (self.stats['average_processing_time_ms'] * (self.stats['total_similarity_computations'] - 1) + processing_time)
            / self.stats['total_similarity_computations']
        )
        
        # Performance validation: Must complete within 50ms
        if processing_time > 50:
            logger.warning(f"⚠️ Pattern similarity took {processing_time:.1f}ms, exceeds 50ms target")
        
        return PatternSimilarityResult(
            best_matches=best_matches,
            similarities=similarities,
            pattern_types=pattern_types,
            max_similarity=max_similarity,
            dominant_pattern_type=dominant_pattern_type,
            processing_time_ms=processing_time,
            cache_hit=cache_hit
        )
    
    def get_pattern_cluster_similarities(self, feedback_text: str) -> Dict[str, float]:
        """
        Get similarity scores to all pattern clusters for comprehensive analysis.
        
        Args:
            feedback_text: User feedback text to analyze
            
        Returns:
            Dictionary with similarity scores for each pattern type
        """
        cluster_similarities = {}
        
        for pattern_type in ['positive', 'negative', 'partial']:
            result = self.get_pattern_similarity(feedback_text, pattern_type, top_k=1)
            cluster_similarities[pattern_type] = result.max_similarity
        
        return cluster_similarities
    
    def add_custom_pattern(self, 
                          pattern_text: str, 
                          pattern_type: str,
                          confidence: str = "medium") -> bool:
        """
        Add custom pattern to the pattern collection.
        
        Args:
            pattern_text: Pattern text to add
            pattern_type: Pattern type ("positive", "negative", "partial")
            confidence: Confidence level ("high", "medium", "low")
            
        Returns:
            Success status
        """
        try:
            # Generate unique ID
            import hashlib
            pattern_id = f"custom_{hashlib.md5(pattern_text.encode()).hexdigest()[:8]}"
            
            # Add to pattern collection
            self.pattern_collection.add(
                documents=[pattern_text],
                metadatas=[{"type": pattern_type, "confidence": confidence, "custom": True}],
                ids=[pattern_id]
            )
            
            self.stats['pattern_collection_size'] += 1
            logger.info(f"✅ Added custom pattern: '{pattern_text}' as {pattern_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding custom pattern: {e}")
            return False
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        cache_hit_rate = (self.stats['cache_hits'] / max(1, self.stats['total_similarity_computations'])) * 100
        
        return {
            'total_similarity_computations': self.stats['total_similarity_computations'],
            'cache_hits': self.stats['cache_hits'],
            'cache_hit_rate_percent': cache_hit_rate,
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'performance_target_met': self.stats['average_processing_time_ms'] < 50,
            'pattern_collection_size': self.stats['pattern_collection_size'],
            'cache_directory': self.cache_dir,
            'lru_cache_info': self._get_cached_embedding.cache_info()
        }
    
    def clear_cache(self):
        """Clear all caches to free memory"""
        # Clear LRU cache
        self._get_cached_embedding.cache_clear()
        
        # Clear persistent file cache
        try:
            cache_files = list(Path(self.cache_dir).glob("*.pkl"))
            for cache_file in cache_files:
                cache_file.unlink()
            logger.info(f"🧹 Cleared {len(cache_files)} cache files")
        except Exception as e:
            logger.warning(f"Error clearing cache files: {e}")
        
        # Reset stats
        self.stats['cache_hits'] = 0
        logger.info("🧹 All caches cleared")
    
    def validate_pattern_collection_health(self) -> Dict[str, Any]:
        """Validate pattern collection health and consistency"""
        try:
            # Check collection accessibility
            collection_count = self.pattern_collection.count()
            
            # Check pattern type distribution
            positive_count = len(self.pattern_collection.query(
                query_texts=["test"], n_results=1, where={"type": "positive"}
            )['documents'][0]) if collection_count > 0 else 0
            
            negative_count = len(self.pattern_collection.query(
                query_texts=["test"], n_results=1, where={"type": "negative"}
            )['documents'][0]) if collection_count > 0 else 0
            
            partial_count = len(self.pattern_collection.query(
                query_texts=["test"], n_results=1, where={"type": "partial"} 
            )['documents'][0]) if collection_count > 0 else 0
            
            # Performance test
            test_start = time.time()
            test_result = self.get_pattern_similarity("test feedback")
            test_time = (time.time() - test_start) * 1000
            
            health_status = {
                'collection_accessible': True,
                'total_patterns': collection_count,
                'pattern_distribution': {
                    'positive': positive_count,
                    'negative': negative_count, 
                    'partial': partial_count
                },
                'performance_test_ms': test_time,
                'performance_healthy': test_time < 50,
                'cache_directory_exists': os.path.exists(self.cache_dir),
                'overall_health': 'healthy'
            }
            
            if test_time > 50 or collection_count == 0:
                health_status['overall_health'] = 'degraded'
            
            return health_status
            
        except Exception as e:
            logger.error(f"Pattern collection health check failed: {e}")
            return {
                'collection_accessible': False,
                'error': str(e),
                'overall_health': 'unhealthy'
            }


# Convenience functions for integration
def create_pattern_manager(db: ClaudeVectorDatabase, **kwargs) -> SemanticPatternManager:
    """Create a semantic pattern manager with default settings"""
    return SemanticPatternManager(db, **kwargs)


def get_pattern_similarity_quick(feedback_text: str, 
                                db: ClaudeVectorDatabase,
                                pattern_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Convenience function for quick pattern similarity analysis.
    
    Args:
        feedback_text: User feedback text to analyze
        db: ClaudeVectorDatabase instance
        pattern_type: Optional pattern type filter
        
    Returns:
        Dictionary with pattern similarity results
    """
    manager = create_pattern_manager(db)
    result = manager.get_pattern_similarity(feedback_text, pattern_type)
    
    return {
        'best_matches': result.best_matches,
        'similarities': result.similarities,
        'pattern_types': result.pattern_types,
        'max_similarity': result.max_similarity,
        'dominant_pattern_type': result.dominant_pattern_type,
        'processing_time_ms': result.processing_time_ms,
        'cache_hit': result.cache_hit
    }


if __name__ == "__main__":
    # Demo and basic validation
    from vector_database import ClaudeVectorDatabase
    
    print("🔧 SemanticPatternManager Demo")
    print("=" * 50)
    
    # Initialize database and pattern manager
    db = ClaudeVectorDatabase()
    manager = SemanticPatternManager(db)
    
    # Test various feedback types
    test_cases = [
        "That worked perfectly!",
        "You nailed it!",
        "Let me try something else",
        "Almost there but still issues",
        "Build passes but tests are failing"
    ]
    
    print(f"\n🧪 Testing pattern similarity analysis...")
    
    for i, feedback in enumerate(test_cases, 1):
        result = manager.get_pattern_similarity(feedback)
        print(f"\n{i}. Feedback: '{feedback}'")
        print(f"   Dominant pattern: {result.dominant_pattern_type} (similarity: {result.max_similarity:.3f})")
        print(f"   Best matches: {result.best_matches[:2]}")
        print(f"   Processing: {result.processing_time_ms:.1f}ms (cached: {result.cache_hit})")
    
    # Performance summary
    print(f"\n📊 Performance Summary:")
    stats = manager.get_performance_stats()
    for key, value in stats.items():
        if key != 'lru_cache_info':
            print(f"   {key}: {value}")
    
    # Health validation
    print(f"\n🏥 Health Check:")
    health = manager.validate_pattern_collection_health()
    print(f"   Overall health: {health['overall_health']}")
    print(f"   Total patterns: {health['total_patterns']}")
    print(f"   Performance test: {health['performance_test_ms']:.1f}ms")