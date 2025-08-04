#!/usr/bin/env python3
"""
Claude Code Vector Database Implementation
ChromaDB-based semantic search with project-aware intelligent filtering
"""

import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import logging
import json
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional

from database.conversation_extractor import ConversationExtractor, ConversationEntry

# Enhanced context awareness imports
from database.enhanced_conversation_entry import EnhancedConversationEntry

# Import enhanced context functions
try:
    # Try importing from the enhanced_context directory structure
    from database.enhanced_context import (
        detect_conversation_topics,
        calculate_solution_quality_score,
        analyze_feedback_sentiment,
        is_solution_attempt,
        classify_solution_type,
        calculate_troubleshooting_boost,
        calculate_recency_boost,
        get_realtime_learning_boost,
        get_realtime_learning_insights,
        process_live_validation_feedback
    )
    enhanced_context_imports_success = True
except ImportError:
    enhanced_context_imports_success = False

# Set up logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import live validation learning functions directly from enhanced_context.py
try:
    exec(open('/home/user/.claude-vector-db-enhanced/database/enhanced_context.py').read())
    validation_imports_success = True
except Exception as e:
    validation_imports_success = False
    logger.warning(f"Could not import live validation learning functions: {e}")

class ClaudeVectorDatabase:
    """ChromaDB-based vector database for Claude conversation context"""
    
    def __init__(self, 
                 db_path: str = "/home/user/.claude-vector-db-enhanced/chroma_db",
                 collection_name: str = "claude_conversations"):
        
        self.db_path = Path(db_path)
        self.collection_name = collection_name
        
        # Ensure directory exists
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client with CPU-only embeddings
        logger.info("🔄 Initializing ChromaDB with CPU-only embeddings...")
        
        self.client = chromadb.PersistentClient(
            path=str(self.db_path),
            settings=Settings(
                anonymized_telemetry=False  # Privacy-focused
            )
        )
        
        # Use default sentence transformer embedding function (all-MiniLM-L6-v2)
        # This is CPU-only and built into ChromaDB
        self.embedding_function = embedding_functions.DefaultEmbeddingFunction()
        
        # Get or create collection
        try:
            self.collection = self.client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            logger.info(f"✅ Connected to existing collection '{self.collection_name}' with {self.collection.count()} entries")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function,
                metadata={"description": "Claude Code conversation context with project-aware search"}
            )
            logger.info(f"✅ Created new collection '{self.collection_name}'")
    
    def generate_content_hash(self, content: str) -> str:
        """Generate consistent hash for content deduplication"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def add_conversation_entry(self, entry: ConversationEntry) -> bool:
        """Add a single conversation entry to the vector database"""
        
        try:
            # Create metadata for the entry
            metadata = {
                "type": entry.type,
                "project_path": entry.project_path,
                "project_name": entry.project_name,
                "timestamp": entry.timestamp,
                "session_id": entry.session_id or "unknown",
                "file_name": entry.file_name,
                "has_code": entry.has_code,
                "tools_used": json.dumps(entry.tools_used),  # Store as JSON string
                "content_length": entry.content_length,
                "content_hash": self.generate_content_hash(entry.content)
            }
            
            # Add to collection
            self.collection.add(
                documents=[entry.content],
                metadatas=[metadata],
                ids=[entry.id]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error adding entry {entry.id}: {e}")
            return False
    
    def add_conversation_entries(self, entries: List[ConversationEntry], batch_size: int = 100) -> Dict[str, int]:
        """Add multiple conversation entries in batches"""
        
        logger.info(f"🔄 Adding {len(entries)} conversation entries to vector database...")
        
        results = {"added": 0, "skipped": 0, "errors": 0}
        
        # Check for existing entries to avoid duplicates
        existing_ids = set()
        try:
            existing_data = self.collection.get(include=[])
            existing_ids = set(existing_data['ids'])
            logger.info(f"Found {len(existing_ids)} existing entries in database")
        except Exception as e:
            logger.warning(f"Could not check existing entries: {e}")
        
        # Process in batches
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            
            # Prepare batch data
            documents = []
            metadatas = []
            ids = []
            
            for entry in batch:
                # Skip if already exists
                if entry.id in existing_ids:
                    results["skipped"] += 1
                    continue
                
                try:
                    metadata = {
                        "type": entry.type,
                        "project_path": entry.project_path,
                        "project_name": entry.project_name,
                        "timestamp": entry.timestamp,
                        "session_id": entry.session_id or "unknown",
                        "file_name": entry.file_name,
                        "has_code": entry.has_code,
                        "tools_used": json.dumps(entry.tools_used),
                        "content_length": entry.content_length,
                    }
                    
                    # Add Unix timestamp if available (for new entries with timezone-aware filtering)
                    if hasattr(entry, 'timestamp_unix') and entry.timestamp_unix:
                        metadata["timestamp_unix"] = entry.timestamp_unix
                    
                    metadata["content_hash"] = self.generate_content_hash(entry.content)
                    
                    documents.append(entry.content)
                    metadatas.append(metadata)
                    ids.append(entry.id)
                    
                except Exception as e:
                    logger.error(f"Error preparing entry {entry.id}: {e}")
                    results["errors"] += 1
            
            # Add batch to collection
            if documents:
                try:
                    self.collection.add(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    results["added"] += len(documents)
                    logger.info(f"✅ Added batch {i//batch_size + 1}: {len(documents)} entries")
                    
                except Exception as e:
                    logger.error(f"Error adding batch {i//batch_size + 1}: {e}")
                    results["errors"] += len(documents)
        
        logger.info(f"✅ Batch addition complete: {results['added']} added, {results['skipped']} skipped, {results['errors']} errors")
        return results
    
    async def batch_add_entries(self, entries: List[ConversationEntry]) -> bool:
        """Add conversation entries for real-time incremental updates.
        
        Optimized for file watcher real-time processing with:
        - Respect ChromaDB 166-item batch limit
        - Content-based deduplication using hashes
        - Performance monitoring
        - Async operation for non-blocking processing
        
        Args:
            entries: List of ConversationEntry objects to add
            
        Returns:
            bool: True if batch was successfully processed
        """
        if not entries:
            return True
        
        try:
            import asyncio
            
            # Respect ChromaDB SQLite constraint limit of 166 items per batch
            MAX_BATCH_SIZE = 166
            
            if len(entries) > MAX_BATCH_SIZE:
                # Process in chunks
                success = True
                for i in range(0, len(entries), MAX_BATCH_SIZE):
                    chunk = entries[i:i + MAX_BATCH_SIZE]
                    chunk_success = await self.batch_add_entries(chunk)
                    success = success and chunk_success
                return success
            
            # Use content hashes for efficient deduplication
            entry_hashes = {self.generate_content_hash(entry.content): entry for entry in entries}
            
            # Check for existing entries by content hash (more efficient than ID lookup)
            existing_hashes = set()
            try:
                # Get sample of recent entries to check for duplicates
                recent_data = self.collection.get(
                    limit=min(1000, len(entries) * 10),  # Sample for hash comparison
                    include=["metadatas"]
                )
                
                for metadata in recent_data.get('metadatas', []):
                    if metadata and 'content_hash' in metadata:
                        existing_hashes.add(metadata['content_hash'])
                        
            except Exception as e:
                logger.debug(f"Could not check existing hashes: {e}")
                # Continue without deduplication check
            
            # Filter out duplicates
            new_entries = []
            for content_hash, entry in entry_hashes.items():
                if content_hash not in existing_hashes:
                    new_entries.append(entry)
            
            if not new_entries:
                logger.debug(f"All {len(entries)} entries already exist (duplicate content)")
                return True
                
            logger.debug(f"Adding {len(new_entries)} new entries (filtered {len(entries) - len(new_entries)} duplicates)")
            
            # Prepare batch data
            documents = []
            metadatas = []
            ids = []
            
            for entry in new_entries:
                try:
                    metadata = {
                        "type": entry.type,
                        "project_path": entry.project_path,
                        "project_name": entry.project_name,
                        "timestamp": entry.timestamp,
                        "session_id": entry.session_id or "unknown",
                        "file_name": entry.file_name,
                        "has_code": entry.has_code,
                        "tools_used": json.dumps(entry.tools_used),
                        "content_length": entry.content_length,
                    }
                    
                    # Add Unix timestamp if available (for new entries with timezone-aware filtering)
                    if hasattr(entry, 'timestamp_unix') and entry.timestamp_unix:
                        metadata["timestamp_unix"] = entry.timestamp_unix
                    
                    metadata["content_hash"] = self.generate_content_hash(entry.content)
                    
                    documents.append(entry.content)
                    metadatas.append(metadata)
                    ids.append(entry.id)
                    
                except Exception as e:
                    logger.error(f"Error preparing entry {entry.id}: {e}")
                    return False
            
            # Add batch to collection (this operation is synchronous in ChromaDB)
            if documents:
                try:
                    # Run the synchronous ChromaDB operation in an executor to avoid blocking
                    loop = asyncio.get_event_loop()
                    await loop.run_in_executor(
                        None,
                        lambda: self.collection.add(
                            documents=documents,
                            metadatas=metadatas,
                            ids=ids
                        )
                    )
                    
                    logger.debug(f"✅ Successfully added {len(documents)} entries to vector database")
                    return True
                    
                except Exception as e:
                    # Check if it's a duplicate ID error (which is recoverable)
                    if "duplicate" in str(e).lower() or "already exists" in str(e).lower():
                        logger.debug(f"Some entries already existed: {e}")
                        return True  # Consider this a success
                    else:
                        logger.error(f"Error adding batch to collection: {e}")
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error in batch_add_entries: {e}")
            return False
    
    def check_entry_exists(self, entry_id: str) -> bool:
        """Check if an entry exists by ID.
        
        Args:
            entry_id: ID of the entry to check
            
        Returns:
            bool: True if entry exists
        """
        try:
            result = self.collection.get(ids=[entry_id], include=[])
            return len(result['ids']) > 0
        except Exception as e:
            logger.debug(f"Error checking entry existence: {e}")
            return False
    
    def check_content_exists(self, content_hash: str) -> bool:
        """Check if content exists by hash.
        
        Args:
            content_hash: MD5 hash of content to check
            
        Returns:
            bool: True if content exists
        """
        try:
            result = self.collection.get(
                where={"content_hash": content_hash},
                include=[],
                limit=1
            )
            return len(result['ids']) > 0
        except Exception as e:
            logger.debug(f"Error checking content hash: {e}")
            return False
    
    def calculate_project_relevance_boost(self, result_project: str, current_project: str) -> float:
        """Calculate relevance boost based on project similarity"""
        
        if not current_project or current_project == "unknown":
            return 1.0
        
        if result_project == current_project:
            return 1.5  # 50% boost for same project
        
        # Check for technology stack overlap
        tech_stacks = {
            "tylergohr.com": {"nextjs", "react", "typescript", "playwright", "vercel"},
            "invoice-chaser": {"react", "express", "supabase", "socketio", "nodejs"},
            "AI Orchestrator Platform": {"python", "prp", "claude", "ai", "automation"},
            "grow": {"react", "vite", "typescript", "tailwind"},
            "idaho-adventures": {"react", "vite", "javascript"},
            "snake-river-adventures": {"html", "css", "javascript", "vanilla"},
            "toast-of-the-town": {"react", "vite", "tailwind"}
        }
        
        current_stack = tech_stacks.get(current_project, set())
        result_stack = tech_stacks.get(result_project, set())
        
        if current_stack and result_stack:
            overlap = len(current_stack & result_stack) / len(current_stack | result_stack)
            if overlap > 0.3:  # 30% technology overlap
                return 1.2  # 20% boost for related technology
        
        return 1.0  # No boost
    
    def calculate_cultural_similarity_boost(self, result_content: str, user_cultural_profile: Optional[Dict[str, Any]] = None) -> float:
        """
        Calculate cultural similarity boost for adaptive learning validation.
        
        Integrates with cultural intelligence engine to provide culturally-aware
        search relevance boosting based on user communication patterns.
        
        Args:
            result_content: Content of the search result
            user_cultural_profile: User's cultural profile information
            
        Returns:
            float: Cultural similarity boost factor (1.0 = no boost, 1.3 = maximum boost)
        """
        # Skip cultural boosting if no user profile provided
        if not user_cultural_profile:
            return 1.0
        
        try:
            # Import cultural intelligence engine (lazy loading for performance)
            from processing.cultural_intelligence_engine import CulturalIntelligenceEngine
            
            # Initialize engine if not already cached
            if not hasattr(self, '_cultural_engine'):
                self._cultural_engine = CulturalIntelligenceEngine()
            
            # Analyze cultural fit between result content and user profile
            cultural_analysis = self._cultural_engine.analyze_with_cultural_intelligence(
                result_content, user_cultural_profile
            )
            
            # Extract cultural confidence from analysis
            cultural_confidence = cultural_analysis.get('cultural_confidence', 0.0)
            
            # Apply cultural similarity boost based on confidence
            # High cultural confidence (>0.7) gets maximum 1.3x boost
            # Medium confidence (0.4-0.7) gets moderate boost
            # Low confidence (<0.4) gets minimal boost
            if cultural_confidence > 0.7:
                boost_factor = 1.3  # Maximum cultural boost
            elif cultural_confidence > 0.4:
                boost_factor = 1.0 + (cultural_confidence - 0.4) * 1.0  # 1.0 to 1.3 scaling
            else:
                boost_factor = 1.0 + cultural_confidence * 0.25  # Minimal boost up to 1.1
            
            # Log cultural boosting for debugging
            if boost_factor > 1.05:  # Only log significant boosts
                logger.debug(f"🌍 Cultural boost applied: {boost_factor:.2f}x (confidence: {cultural_confidence:.2f})")
            
            return boost_factor
            
        except ImportError:
            # Cultural intelligence engine not available - no boost
            logger.debug("Cultural intelligence engine not available for cultural boosting")
            return 1.0
        except Exception as e:
            # Error in cultural analysis - log and return no boost
            logger.warning(f"Cultural similarity boost failed: {e}")
            return 1.0
    
    def search_conversations(self, 
                           query: str,
                           current_project: Optional[str] = None,
                           n_results: int = 10,
                           include_metadata: bool = True,
                           filter_conditions: Optional[Dict[str, Any]] = None,
                           user_cultural_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Search conversations with project-aware and culturally-intelligent filtering
        
        Args:
            query: Search query
            current_project: Current project name for relevance boosting
            n_results: Number of results to return
            include_metadata: Whether to include metadata in results
            filter_conditions: Optional ChromaDB filter conditions
            user_cultural_profile: Optional user cultural profile for cultural similarity boosting
        
        Returns:
            List of search results with relevance scores
        """
        
        logger.info(f"🔍 Searching for: '{query}' | Project context: {current_project}")
        
        try:
            # Get more results than needed for re-ranking
            search_count = min(n_results * 2, 20)  # Get 2x results for intelligent filtering
            
            # Prepare include list
            include = ["documents", "distances", "metadatas"] if include_metadata else ["documents", "distances"]
            
            # Perform vector search
            search_results = self.collection.query(
                query_texts=[query],
                n_results=search_count,
                include=include,
                where=filter_conditions
            )
            
            if not search_results['documents'] or not search_results['documents'][0]:
                logger.info("No results found")
                return []
            
            # Process and re-rank results
            processed_results = []
            
            documents = search_results['documents'][0]
            distances = search_results['distances'][0]
            metadatas = search_results.get('metadatas', [[]])[0] if include_metadata else [{}] * len(documents)
            ids = search_results.get('ids', [[]])[0]
            
            for i, (doc, distance, metadata, doc_id) in enumerate(zip(documents, distances, metadatas, ids)):
                # Convert distance to similarity score (lower distance = higher similarity)
                base_similarity = max(0, 1 - distance)
                
                # Apply project-aware relevance boosting
                project_boost = 1.0
                if current_project and metadata:
                    result_project = metadata.get('project_name', 'unknown')
                    project_boost = self.calculate_project_relevance_boost(result_project, current_project)
                
                # Apply cultural similarity boosting (PRP-3 Adaptive Learning)
                cultural_boost = self.calculate_cultural_similarity_boost(doc, user_cultural_profile)
                
                # Calculate final relevance score with combined boosting
                relevance_score = base_similarity * project_boost * cultural_boost
                
                # Skip results with extremely low relevance (likely noise for time-filtered searches)
                if relevance_score < 0.01:  # 1% minimum relevance threshold
                    continue
                
                # Parse tools from JSON string
                tools_used = []
                if metadata and metadata.get('tools_used'):
                    try:
                        tools_used = json.loads(metadata['tools_used'])
                    except (json.JSONDecodeError, TypeError):
                        tools_used = []
                
                result = {
                    "id": doc_id,
                    "content": doc,
                    "relevance_score": relevance_score,
                    "base_similarity": base_similarity,
                    "project_boost": project_boost,
                    "cultural_boost": cultural_boost,
                    "rank": i + 1
                }
                
                if include_metadata and metadata:
                    result.update({
                        "type": metadata.get('type', 'unknown'),
                        "project_name": metadata.get('project_name', 'unknown'),
                        "project_path": metadata.get('project_path', 'unknown'),
                        "timestamp": metadata.get('timestamp', ''),
                        "session_id": metadata.get('session_id', 'unknown'),
                        "file_name": metadata.get('file_name', 'unknown'),
                        "has_code": metadata.get('has_code', False),
                        "tools_used": tools_used,
                        "content_length": metadata.get('content_length', 0)
                    })
                
                processed_results.append(result)
            
            # Sort by relevance score and return top results
            processed_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            final_results = processed_results[:n_results]
            
            logger.info(f"✅ Found {len(final_results)} relevant results")
            
            # Log top result for debugging
            if final_results:
                top_result = final_results[0]
                logger.info(f"Top result: {top_result['project_name']} (score: {top_result['relevance_score']:.3f})")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def search_conversations_enhanced(self,
                                    query: str,
                                    current_project: Optional[str] = None,
                                    n_results: int = 10,
                                    include_metadata: bool = True,
                                    filter_conditions: Optional[Dict[str, Any]] = None,
                                    # Enhanced parameters
                                    topic_focus: Optional[str] = None,
                                    prefer_solutions: bool = False,
                                    troubleshooting_mode: bool = False,
                                    validation_preference: str = "neutral",
                                    prefer_recent: bool = False,
                                    show_context_chain: bool = False,
                                    # Adaptive learning parameters (PRP-3)
                                    user_cultural_profile: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Enhanced conversation search with multi-factor relevance scoring.
        
        Combines semantic similarity with topic boosting, quality scoring, validation learning,
        and other enhancement factors for sophisticated search relevance.
        
        Args:
            query: Search query
            current_project: Current project for relevance boosting
            n_results: Number of results to return
            include_metadata: Include metadata in results
            filter_conditions: ChromaDB filter conditions
            topic_focus: Specific topic to boost (e.g., "debugging", "performance")
            prefer_solutions: Boost high-quality solution content
            troubleshooting_mode: Enhanced relevance for error-solving contexts
            validation_preference: "validated_only", "include_failures", "neutral"
            prefer_recent: Boost recent conversations
            show_context_chain: Include adjacency context in results
            
        Returns:
            Enhanced search results with detailed relevance analysis
        """
        logger.info(f"🚀 Enhanced search: '{query}' | Project: {current_project} | Topic: {topic_focus}")
        
        try:
            # Get base search results (more than needed for re-ranking)
            search_count = min(n_results * 3, 50)
            
            # Prepare include list
            include = ["documents", "distances", "metadatas"] if include_metadata else ["documents", "distances"]
            
            # Perform vector search
            search_results = self.collection.query(
                query_texts=[query],
                n_results=search_count,
                include=include,
                where=filter_conditions
            )
            
            if not search_results['documents'] or not search_results['documents'][0]:
                logger.info("No results found")
                return []
            
            # Build query context for enhancement scoring
            query_context = {
                'topic_focus': topic_focus,
                'prefer_solutions': prefer_solutions,
                'troubleshooting_mode': troubleshooting_mode,
                'validation_preference': validation_preference,
                'prefer_recent': prefer_recent,
                'prefer_validated': validation_preference == "validated_only",
                'prefer_code': prefer_solutions,
                'prefer_detailed': prefer_solutions,
                'prefer_implementation': prefer_solutions
            }
            
            # Process and enhance results
            enhanced_results = []
            
            documents = search_results['documents'][0]
            distances = search_results['distances'][0]
            metadatas = search_results.get('metadatas', [[]])[0] if include_metadata else [{}] * len(documents)
            ids = search_results.get('ids', [[]])[0]
            
            for i, (doc, distance, metadata, doc_id) in enumerate(zip(documents, distances, metadatas, ids)):
                # Convert cosine distance to similarity score
                # ChromaDB uses cosine distance where 0 = perfect match, 2 = completely opposite
                # Convert to similarity: 1.0 = perfect match, 0.0 = no similarity
                base_similarity = max(0, (2 - distance) / 2)
                
                # Apply basic project boosting
                project_boost = 1.0
                if current_project and metadata:
                    result_project = metadata.get('project_name', 'unknown')
                    project_boost = self.calculate_project_relevance_boost(result_project, current_project)
                
                # Apply cultural similarity boosting (PRP-3 Adaptive Learning)
                cultural_boost = self.calculate_cultural_similarity_boost(doc, user_cultural_profile)
                
                # Apply enhanced relevance scoring with live validation learning
                enhanced_scoring = self._calculate_enhanced_relevance_score_with_validation(
                    base_similarity=base_similarity,
                    project_boost=project_boost,
                    cultural_boost=cultural_boost,
                    content=doc,
                    metadata=metadata,
                    query_context=query_context
                )
                
                # Skip results with extremely low relevance
                if enhanced_scoring['final_score'] < 0.01:
                    continue
                
                # Parse tools from JSON string
                tools_used = []
                if metadata and metadata.get('tools_used'):
                    try:
                        tools_used = json.loads(metadata['tools_used'])
                    except (json.JSONDecodeError, TypeError):
                        tools_used = []
                
                # Build enhanced result
                result = {
                    "id": doc_id,
                    "content": doc,
                    "relevance_score": enhanced_scoring['final_score'],
                    "enhancement_analysis": enhanced_scoring,
                    "boost_explanation": self._get_boost_explanation(enhanced_scoring),
                    "rank": i + 1
                }
                
                if include_metadata and metadata:
                    # Parse enhanced metadata fields
                    detected_topics = {}
                    if metadata.get('detected_topics'):
                        try:
                            detected_topics = json.loads(metadata['detected_topics'])
                        except (json.JSONDecodeError, TypeError):
                            detected_topics = {}
                    
                    result.update({
                        "type": metadata.get('type', 'unknown'),
                        "project_name": metadata.get('project_name', 'unknown'),
                        "project_path": metadata.get('project_path', 'unknown'),
                        "timestamp": metadata.get('timestamp', ''),
                        "session_id": metadata.get('session_id', 'unknown'),
                        "file_name": metadata.get('file_name', 'unknown'),
                        "has_code": metadata.get('has_code', False),
                        "tools_used": tools_used,
                        "content_length": metadata.get('content_length', 0),
                        
                        # Enhanced fields
                        "detected_topics": detected_topics,
                        "primary_topic": metadata.get('primary_topic'),
                        "topic_confidence": metadata.get('topic_confidence', 0.0),
                        "solution_quality_score": metadata.get('solution_quality_score', 1.0),
                        "is_validated_solution": metadata.get('is_validated_solution', False),
                        "is_refuted_attempt": metadata.get('is_refuted_attempt', False),
                        "user_feedback_sentiment": metadata.get('user_feedback_sentiment'),
                        "validation_strength": metadata.get('validation_strength', 0.0),
                        "solution_category": metadata.get('solution_category'),
                    })
                    
                    # Add context chain if requested
                    if show_context_chain:
                        result['context_chain'] = self.get_context_chain(doc_id, metadata)
                
                enhanced_results.append(result)
            
            # Sort by enhanced relevance score
            enhanced_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            final_results = enhanced_results[:n_results]
            
            logger.info(f"✅ Enhanced search complete: {len(final_results)} results")
            
            # Log top result with enhancement details
            if final_results:
                top_result = final_results[0]
                logger.info(f"Top result: {top_result['project_name']} "
                          f"(score: {top_result['relevance_score']:.3f}) "
                          f"Enhanced: {len(top_result['boost_explanation'])} boosts")
            
            return final_results
            
        except Exception as e:
            logger.error(f"Enhanced search error: {e}")
            return []
    
    def search_validated_solutions(self,
                                 query: str,
                                 current_project: Optional[str] = None,
                                 n_results: int = 5,
                                 min_validation_strength: float = 0.3) -> List[Dict[str, Any]]:
        """
        Search for user-validated solutions only.
        
        Args:
            query: Search query
            current_project: Current project context
            n_results: Number of results
            min_validation_strength: Minimum validation strength threshold
            
        Returns:
            List of validated solution results
        """
        logger.info(f"🔍 Searching validated solutions: '{query}'")
        
        # Filter for validated solutions
        filter_conditions = {
            "$and": [
                {"is_validated_solution": {"$eq": True}},
                {"validation_strength": {"$gte": min_validation_strength}}
            ]
        }
        
        return self.search_conversations_enhanced(
            query=query,
            current_project=current_project,
            n_results=n_results,
            filter_conditions=filter_conditions,
            validation_preference="validated_only",
            prefer_solutions=True
        )
    
    def search_failed_attempts(self,
                             query: str,
                             current_project: Optional[str] = None,
                             n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for solutions that users reported as unsuccessful.
        Useful for learning "what not to do" patterns.
        
        Args:
            query: Search query
            current_project: Current project context
            n_results: Number of results
            
        Returns:
            List of refuted solution results
        """
        logger.info(f"⚠️ Searching failed attempts: '{query}'")
        
        # Filter for refuted attempts
        filter_conditions = {"is_refuted_attempt": {"$eq": True}}
        
        return self.search_conversations_enhanced(
            query=query,
            current_project=current_project,
            n_results=n_results,
            filter_conditions=filter_conditions,
            validation_preference="include_failures"
        )
    
    def search_by_topic(self,
                       query: str,
                       topic: str,
                       current_project: Optional[str] = None,
                       n_results: int = 10) -> List[Dict[str, Any]]:
        """
        Search conversations focused on a specific topic.
        
        Args:
            query: Search query
            topic: Topic to focus on (e.g., "debugging", "performance")
            current_project: Current project context
            n_results: Number of results
            
        Returns:
            Topic-focused search results
        """
        logger.info(f"🏷️ Topic-focused search: '{query}' → {topic}")
        
        return self.search_conversations_enhanced(
            query=query,
            current_project=current_project,
            n_results=n_results,
            topic_focus=topic,
            troubleshooting_mode=(topic in ["debugging", "troubleshooting", "error"]),
            prefer_solutions=True
        )
    
    def get_context_chain(self, anchor_message_id: str, metadata: Dict, chain_length: int = 3) -> List[Dict]:
        """
        Get enhanced conversation context chain around a specific message.
        
        Provides intelligent context chain showing:
        - Message sequence flow (previous/next messages)
        - Solution-feedback relationships
        - Validation status and outcomes
        - Topic progression and context
        
        Args:
            anchor_message_id: ID of the anchor message
            metadata: Metadata of the anchor message
            chain_length: Number of messages in each direction
            
        Returns:
            Enhanced context chain with relationship metadata
        """
        try:
            # Get messages from same session
            session_id = metadata.get('session_id')
            file_name = metadata.get('file_name')
            
            if not session_id or not file_name:
                return []
            
            # Query for messages from same session with enhanced metadata
            session_results = self.collection.query(
                query_texts=["context"],  # Dummy query for filtering
                n_results=150,  # Get more results for comprehensive context
                where={
                    "$and": [
                        {"session_id": {"$eq": session_id}},
                        {"file_name": {"$eq": file_name}}
                    ]
                },
                include=["metadatas", "documents"]
            )
            
            if not session_results['metadatas'] or not session_results['metadatas'][0]:
                return []
            
            # We need to get the IDs separately since we can't include them in the query above
            # Use the get method to retrieve the same data with IDs
            all_session_data = self.collection.get(
                where={
                    "$and": [
                        {"session_id": {"$eq": session_id}},
                        {"file_name": {"$eq": file_name}}
                    ]
                },
                include=["metadatas", "documents"]
            )
            
            if not all_session_data['ids']:
                return []
            
            # Build enhanced context messages with relationship data  
            context_messages = []
            messages_by_id = {}
            
            documents = all_session_data['documents']
            metadatas = all_session_data['metadatas'] 
            ids = all_session_data['ids']
            
            for i, (doc, meta, msg_id) in enumerate(zip(documents, metadatas, ids)):
                # Parse enhanced metadata fields
                detected_topics = {}
                if meta.get('detected_topics'):
                    try:
                        detected_topics = json.loads(meta['detected_topics'])
                    except:
                        detected_topics = {}
                
                context_msg = {
                    'id': msg_id,
                    'content': doc[:300] + "..." if len(doc) > 300 else doc,  # More content for context
                    'content_preview': doc[:150] + "..." if len(doc) > 150 else doc,
                    'type': meta.get('type', 'unknown'),
                    'sequence_position': meta.get('message_sequence_position', i),
                    'timestamp': meta.get('timestamp', ''),
                    'is_anchor': msg_id == anchor_message_id,
                    
                    # Enhanced relationship data
                    'previous_message_id': meta.get('previous_message_id'),
                    'next_message_id': meta.get('next_message_id'),
                    'is_solution_attempt': meta.get('is_solution_attempt', False),
                    'is_feedback_to_solution': meta.get('is_feedback_to_solution', False),
                    'related_solution_id': meta.get('related_solution_id'),
                    'feedback_message_id': meta.get('feedback_message_id'),
                    'solution_category': meta.get('solution_category'),
                    
                    # Validation and quality data
                    'is_validated_solution': meta.get('is_validated_solution', False),
                    'is_refuted_attempt': meta.get('is_refuted_attempt', False),
                    'user_feedback_sentiment': meta.get('user_feedback_sentiment'),
                    'validation_strength': meta.get('validation_strength', 0.0),
                    'solution_quality_score': meta.get('solution_quality_score', 1.0),
                    
                    # Topic and context data
                    'detected_topics': detected_topics,
                    'primary_topic': meta.get('primary_topic'),
                    'has_code': meta.get('has_code', False),
                    'tools_used': json.loads(meta.get('tools_used', '[]')) if meta.get('tools_used') else []
                }
                
                context_messages.append(context_msg)
                messages_by_id[msg_id] = context_msg
            
            # Sort by sequence position
            context_messages.sort(key=lambda x: x.get('sequence_position', 0))
            
            # Find anchor message and build intelligent context chain
            anchor_msg = next((msg for msg in context_messages if msg['is_anchor']), None)
            if not anchor_msg:
                return context_messages[:chain_length * 2 + 1]  # Fallback
            
            # Build context chain with relationship awareness
            context_chain = self._build_enhanced_context_chain(
                anchor_msg, context_messages, messages_by_id, chain_length
            )
            
            # Add relationship analysis to the context chain
            self._add_context_chain_relationships(context_chain)
            
            return context_chain
            
        except Exception as e:
            logger.warning(f"Enhanced context chain error: {e}")
            return []
    
    def _build_enhanced_context_chain(self, anchor_msg: Dict, all_messages: List[Dict], 
                                    messages_by_id: Dict, chain_length: int) -> List[Dict]:
        """
        Build intelligent context chain considering relationships and relevance.
        
        Prioritizes:
        1. Direct sequence flow (previous/next messages)
        2. Solution-feedback pairs
        3. Related solutions and validation outcomes
        4. Topic coherence and conversation flow
        """
        context_chain = [anchor_msg]
        anchor_pos = next((i for i, msg in enumerate(all_messages) if msg['is_anchor']), 0)
        
        # Add messages before anchor (prioritizing relevant context)
        before_messages = []
        current_pos = anchor_pos - 1
        added_before = 0
        
        while current_pos >= 0 and added_before < chain_length:
            msg = all_messages[current_pos]
            
            # Always include direct relationships
            if (msg['id'] == anchor_msg.get('previous_message_id') or
                msg['id'] == anchor_msg.get('related_solution_id') or
                anchor_msg['id'] == msg.get('feedback_message_id')):
                before_messages.insert(0, msg)
                added_before += 1
            # Include sequential messages if we have space
            elif added_before < chain_length - 1:
                before_messages.insert(0, msg)
                added_before += 1
            
            current_pos -= 1
        
        # Add messages after anchor
        after_messages = []
        current_pos = anchor_pos + 1
        added_after = 0
        
        while current_pos < len(all_messages) and added_after < chain_length:
            msg = all_messages[current_pos]
            
            # Always include direct relationships
            if (msg['id'] == anchor_msg.get('next_message_id') or
                msg['id'] == anchor_msg.get('feedback_message_id') or
                anchor_msg['id'] == msg.get('related_solution_id')):
                after_messages.append(msg)
                added_after += 1
            # Include sequential messages if we have space
            elif added_after < chain_length - 1:
                after_messages.append(msg)
                added_after += 1
            
            current_pos += 1
        
        # Combine into full context chain
        full_chain = before_messages + context_chain + after_messages
        
        return full_chain
    
    def _add_context_chain_relationships(self, context_chain: List[Dict]):
        """
        Add relationship analysis and metadata to context chain messages.
        
        Identifies and labels relationships between messages in the chain.
        """
        # Create lookup for efficient relationship detection
        chain_by_id = {msg['id']: msg for msg in context_chain}
        
        for i, msg in enumerate(context_chain):
            relationships = []
            context_role = "context"
            
            # Determine message role in context chain
            if msg['is_anchor']:
                context_role = "anchor"
            elif msg['is_solution_attempt']:
                context_role = "solution"
                if msg['is_validated_solution']:
                    context_role = "validated_solution"
                elif msg['is_refuted_attempt']:
                    context_role = "refuted_solution"
            elif msg['is_feedback_to_solution']:
                context_role = "feedback"
            elif msg['type'] == 'user':
                context_role = "user_input"
            elif msg['type'] == 'assistant':
                context_role = "assistant_response"
            
            # Find relationships to other messages in chain
            for other_msg in context_chain:
                if other_msg['id'] == msg['id']:
                    continue
                
                if msg.get('feedback_message_id') == other_msg['id']:
                    relationships.append(f"provides_feedback_to:{other_msg['id']}")
                elif msg.get('related_solution_id') == other_msg['id']:
                    relationships.append(f"feedback_for_solution:{other_msg['id']}")
                elif msg.get('next_message_id') == other_msg['id']:
                    relationships.append(f"followed_by:{other_msg['id']}")
                elif msg.get('previous_message_id') == other_msg['id']:
                    relationships.append(f"follows:{other_msg['id']}")
            
            # Add relationship metadata
            msg['context_role'] = context_role
            msg['chain_relationships'] = relationships
            msg['chain_position'] = i
            msg['validation_status'] = self._get_validation_status_display(msg)
    
    def _get_validation_status_display(self, msg: Dict) -> str:
        """Get human-readable validation status for display."""
        if msg.get('is_validated_solution'):
            strength = msg.get('validation_strength', 0.0)
            return f"✅ Validated (strength: {strength:.2f})"
        elif msg.get('is_refuted_attempt'):
            strength = abs(msg.get('validation_strength', 0.0))
            return f"❌ Refuted (strength: {strength:.2f})"
        elif msg.get('validation_strength', 0.0) > 0:
            strength = msg.get('validation_strength', 0.0)
            return f"🔄 Partial success (strength: {strength:.2f})"
        elif msg.get('user_feedback_sentiment'):
            sentiment = msg.get('user_feedback_sentiment')
            return f"💬 Feedback: {sentiment}"
        else:
            return "⚪ No validation data"
    
    # Live Validation Learning System Integration
    
    def _calculate_enhanced_relevance_score_with_validation(self, 
                                                          base_similarity: float,
                                                          project_boost: float,
                                                          cultural_boost: float,
                                                          content: str,
                                                          metadata: Dict,
                                                          query_context: Dict) -> Dict[str, float]:
        """
        Calculate enhanced relevance score including live validation learning and cultural intelligence.
        
        Integrates the live validation learning system and PRP-3 adaptive learning components 
        to boost/demote solutions based on learned user feedback patterns and cultural intelligence.
        
        Args:
            base_similarity: Base vector similarity score
            project_boost: Project relevance boost factor
            cultural_boost: Cultural similarity boost factor (PRP-3 Adaptive Learning)
            content: Content to analyze
            metadata: Entry metadata
            query_context: Query context with preferences
            
        Returns:
            Dictionary with detailed scoring breakdown including validation learning and cultural boosting
        """
        # Detect topics for this content
        detected_topics = detect_conversation_topics(content)
        
        # Calculate base quality score
        quality_boost = calculate_solution_quality_score(content, metadata)
        
        # Apply topic boost if specified
        topic_boost = 1.0
        if query_context.get('topic_focus') and detected_topics:
            topic_relevance = detected_topics.get(query_context['topic_focus'], 0.0)
            topic_boost = 1.0 + (topic_relevance * 0.5)  # Up to 50% boost
        
        # Apply troubleshooting boost
        troubleshooting_boost = calculate_troubleshooting_boost(content, query_context)
        
        # Apply recency boost
        recency_boost = calculate_recency_boost(metadata.get('timestamp', ''), query_context)
        
        # Apply live validation learning boost
        validation_boost = self._get_validation_learning_boost(content, detected_topics, metadata)
        
        # ✨ NEW: Apply Semantic Validation boost (PRP-2 enhancement) ✨
        semantic_boost = self._get_semantic_validation_boost(metadata, query_context)
        
        # ✨ Apply Real-time Feedback Loop Learning boost ✨
        realtime_learning_boost = get_realtime_learning_boost(content, detected_topics) if enhanced_context_imports_success else 1.0
        
        # Apply preference multipliers
        preference_multiplier = 1.0
        if query_context.get('prefer_solutions') and quality_boost > 1.5:
            preference_multiplier *= 1.8
        if query_context.get('prefer_recent') and recency_boost > 1.2:
            preference_multiplier *= 1.3
        
        # Apply validation preference filtering
        validation_preference = query_context.get('validation_preference', 'neutral')
        if validation_preference == 'validated_only':
            if not metadata.get('is_validated_solution', False):
                validation_boost *= 0.3  # Heavy penalty for unvalidated
        elif validation_preference == 'include_failures' and metadata.get('is_refuted_attempt', False):
            validation_boost *= 1.5  # Boost failed attempts for learning
        
        # Calculate final score including real-time learning, semantic validation, and cultural intelligence
        final_score = (
            base_similarity *
            project_boost *
            cultural_boost *
            topic_boost *
            quality_boost *
            troubleshooting_boost *
            recency_boost *
            validation_boost *
            semantic_boost *
            realtime_learning_boost *
            preference_multiplier
        )
        
        return {
            'final_score': final_score,
            'base_similarity': base_similarity,
            'project_boost': project_boost,
            'cultural_boost': cultural_boost,
            'topic_boost': topic_boost,
            'quality_boost': quality_boost,
            'troubleshooting_boost': troubleshooting_boost,
            'recency_boost': recency_boost,
            'validation_boost': validation_boost,
            'semantic_boost': semantic_boost,
            'realtime_learning_boost': realtime_learning_boost,
            'preference_multiplier': preference_multiplier,
            'detected_topics': detected_topics,
            'boost_capping_applied': final_score > 5.0  # Cap at 5x total boost
        }
    
    def _get_validation_learning_boost(self, content: str, detected_topics: Dict[str, float], metadata: Dict) -> float:
        """
        Get validation learning boost based on learned patterns.
        
        Uses the live validation learner to determine confidence boost
        for solutions based on historical user feedback patterns.
        
        Args:
            content: Solution content
            detected_topics: Detected topics for the content
            metadata: Entry metadata
            
        Returns:
            Validation learning boost factor
        """
        try:
            # Check if this is a solution attempt
            if not is_solution_attempt(content):
                return 1.0  # No validation boost for non-solutions
            
            # Get solution type
            solution_type = classify_solution_type(content)
            
            # Get validation learner
            learner = get_live_validation_learner()
            
            # Get confidence multiplier from learned patterns
            confidence_multiplier = learner.get_solution_confidence_multiplier(
                content, detected_topics, solution_type
            )
            
            # Apply metadata-based validation status
            if metadata.get('is_validated_solution', False):
                validation_strength = metadata.get('validation_strength', 0.0)
                confidence_multiplier *= (1.0 + validation_strength)  # Boost validated solutions
            elif metadata.get('is_refuted_attempt', False):
                validation_strength = abs(metadata.get('validation_strength', 0.0))
                confidence_multiplier *= max(0.3, 1.0 - validation_strength)  # Demote refuted attempts
            
            return max(0.2, min(3.0, confidence_multiplier))  # Clamp to reasonable range
            
        except Exception as e:
            logger.warning(f"Error in validation learning boost: {e}")
            return 1.0  # Default neutral boost on error
    
    def _get_semantic_validation_boost(self, metadata: Dict, query_context: Dict) -> float:
        """
        Get semantic validation boost based on PRP-2 semantic analysis fields.
        
        Applies boost based on semantic sentiment analysis, confidence scores,
        and technical domain matching from the PRP-2 enhancement system.
        
        Args:
            metadata: Entry metadata containing semantic validation fields
            query_context: Query context for semantic matching
            
        Returns:
            Semantic validation boost factor (0.5-2.5x range)
        """
        try:
            # Check if semantic validation fields are available
            if not metadata.get('semantic_sentiment'):
                return 1.0  # No boost if semantic data unavailable
            
            semantic_sentiment = metadata.get('semantic_sentiment', 'neutral')
            semantic_confidence = float(metadata.get('semantic_confidence', 0.0))
            semantic_method = metadata.get('semantic_method', 'none')
            
            # Base boost from semantic sentiment
            sentiment_boost = 1.0
            if semantic_sentiment == 'positive':
                sentiment_boost = 1.4  # Strong positive boost
            elif semantic_sentiment == 'negative':
                sentiment_boost = 0.7  # Moderate negative penalty
            elif semantic_sentiment == 'partial':
                sentiment_boost = 1.1  # Small positive boost for partial success
            
            # Confidence-based scaling
            confidence_multiplier = 1.0 + (semantic_confidence * 0.5)  # 0-50% additional boost
            
            # Method quality bonus
            method_bonus = 1.0
            if semantic_method == 'multimodal':
                method_bonus = 1.2  # Premium for multi-modal analysis
            elif semantic_method == 'semantic':
                method_bonus = 1.1  # Good for semantic-only analysis
            
            # Technical domain matching (if available)
            domain_boost = 1.0
            primary_domain = metadata.get('primary_domain')
            if primary_domain and query_context.get('topic_focus'):
                query_topic = query_context['topic_focus'].lower()
                if (primary_domain == 'build_system' and query_topic in ['build', 'compilation', 'dependencies']) or \
                   (primary_domain == 'testing' and query_topic in ['test', 'testing', 'validation']) or \
                   (primary_domain == 'runtime' and query_topic in ['runtime', 'execution', 'performance']) or \
                   (primary_domain == 'deployment' and query_topic in ['deploy', 'deployment', 'production']):
                    domain_boost = 1.3  # Strong domain match boost
            
            # Calculate final semantic boost
            final_boost = sentiment_boost * confidence_multiplier * method_bonus * domain_boost
            
            # Clamp to reasonable range (0.5x to 2.5x)
            return max(0.5, min(2.5, final_boost))
            
        except Exception as e:
            logger.warning(f"Error in semantic validation boost: {e}")
            return 1.0  # Default neutral boost on error
    
    def _get_boost_explanation(self, enhanced_scoring: Dict) -> List[str]:
        """Generate human-readable explanation of boost factors."""
        explanations = []
        
        if enhanced_scoring.get('project_boost', 1.0) > 1.0:
            explanations.append(f"Project boost: {enhanced_scoring['project_boost']:.2f}x")
        
        if enhanced_scoring.get('topic_boost', 1.0) > 1.0:
            explanations.append(f"Topic boost: {enhanced_scoring['topic_boost']:.2f}x")
        
        if enhanced_scoring.get('quality_boost', 1.0) > 1.0:
            explanations.append(f"Solution quality boost: {enhanced_scoring['quality_boost']:.2f}x")
        
        if enhanced_scoring.get('troubleshooting_boost', 1.0) > 1.0:
            explanations.append(f"Troubleshooting boost: {enhanced_scoring['troubleshooting_boost']:.2f}x")
        
        if enhanced_scoring.get('recency_boost', 1.0) > 1.0:
            explanations.append(f"Recency boost: {enhanced_scoring['recency_boost']:.2f}x")
        
        if enhanced_scoring.get('validation_boost', 1.0) != 1.0:
            boost_val = enhanced_scoring['validation_boost']
            if boost_val > 1.0:
                explanations.append(f"Validation learning boost: {boost_val:.2f}x")
            else:
                explanations.append(f"Validation learning penalty: {boost_val:.2f}x")
        
        if enhanced_scoring.get('semantic_boost', 1.0) != 1.0:
            boost_val = enhanced_scoring['semantic_boost']
            if boost_val > 1.0:
                explanations.append(f"Semantic validation boost: {boost_val:.2f}x")
            else:
                explanations.append(f"Semantic validation penalty: {boost_val:.2f}x")
        
        return explanations
    
    def process_validation_feedback(self, solution_id: str, solution_content: str, 
                                  feedback_content: str, solution_metadata: Dict = None) -> Dict[str, Any]:
        """
        Process user feedback for live validation learning.
        
        This is the main integration point for the live validation learning system.
        Call this method when users provide feedback on Claude's solutions.
        
        Args:
            solution_id: Unique identifier for the solution
            solution_content: The solution content that was provided
            feedback_content: User's feedback on the solution
            solution_metadata: Additional metadata about the solution
            
        Returns:
            Dictionary with validation processing results
        """
        logger.info(f"🧠 Processing validation feedback for solution {solution_id}")
        
        try:
            # Process through live validation learning system
            result = process_live_validation_feedback(
                solution_id, solution_content, feedback_content, solution_metadata
            )
            
            # Update the solution entry in the database if it exists
            self._update_solution_validation_status(solution_id, result['validation_record'])
            
            logger.info(f"✅ Validation feedback processed: {result['feedback_analysis']['sentiment']} "
                       f"(strength: {result['feedback_analysis']['strength']:.2f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing validation feedback: {e}")
            return {
                'error': str(e),
                'validation_record': None,
                'learning_update': False
            }
    
    def _update_solution_validation_status(self, solution_id: str, validation_record: Dict):
        """
        Update solution validation status in the vector database.
        
        Args:
            solution_id: ID of the solution to update
            validation_record: Validation record from live learning system
        """
        try:
            # Get existing entry
            existing = self.collection.get(ids=[solution_id], include=['metadatas'])
            
            if not existing['metadatas'] or not existing['metadatas'][0]:
                logger.warning(f"Solution {solution_id} not found in database")
                return
            
            # Update metadata with validation status
            metadata = existing['metadatas'][0]
            metadata.update({
                'is_validated_solution': validation_record['is_validated'],
                'is_refuted_attempt': validation_record['is_refuted'],
                'user_feedback_sentiment': validation_record['feedback_sentiment'],
                'validation_strength': validation_record['feedback_strength'],
                'outcome_certainty': validation_record['feedback_certainty'],
                'validation_timestamp': validation_record['timestamp']
            })
            
            # Update in database
            self.collection.update(
                ids=[solution_id],
                metadatas=[metadata]
            )
            
            logger.info(f"✅ Updated validation status for solution {solution_id}")
            
        except Exception as e:
            logger.warning(f"Could not update solution validation status: {e}")
    
    def get_validation_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about the live validation learning system.
        
        Returns:
            Dictionary with learning insights and performance metrics
        """
        try:
            learner = get_live_validation_learner()
            insights = learner.get_learning_insights()
            
            # Add database-specific statistics (using direct collection access)
            insights['database_integration'] = {
                'total_entries': self.collection.count(),
                'validated_solutions_in_db': self._count_validated_solutions(),
                'refuted_attempts_in_db': self._count_refuted_attempts(),
                'integration_status': 'active'
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting validation learning insights: {e}")
            return {'error': str(e), 'status': 'error'}
    
    def _count_validated_solutions(self) -> int:
        """Count validated solutions in the database."""
        try:
            results = self.collection.get(
                where={'is_validated_solution': {'$eq': True}},
                include=[]
            )
            return len(results['ids'])
        except:
            return 0
    
    def _count_refuted_attempts(self) -> int:
        """Count refuted attempts in the database."""
        try:
            results = self.collection.get(
                where={'is_refuted_attempt': {'$eq': True}},
                include=[]
            )
            return len(results['ids'])
        except:
            return 0
    
    def add_enhanced_entry(self, entry: EnhancedConversationEntry) -> bool:
        """
        Add an enhanced conversation entry to the database.
        
        Args:
            entry: EnhancedConversationEntry with full enhancement metadata
            
        Returns:
            True if added successfully, False otherwise
        """
        try:
            # Create content hash for deduplication
            content_hash = hashlib.md5(entry.content.encode('utf-8')).hexdigest()
            
            # Check for duplicates
            existing = self.collection.query(
                query_texts=[entry.content[:100]],  # Use content prefix for similarity
                n_results=1,
                where={"content_hash": {"$eq": content_hash}}
            )
            
            if existing['documents'] and existing['documents'][0]:
                logger.debug(f"Skipping duplicate entry: {entry.id}")
                return False
            
            # Convert to ChromaDB-compatible metadata
            metadata = entry.to_enhanced_metadata()
            metadata['content_hash'] = content_hash
            
            # Add to collection
            self.collection.add(
                documents=[entry.content],
                metadatas=[metadata],
                ids=[entry.id]
            )
            
            logger.debug(f"✅ Added enhanced entry: {entry.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding enhanced entry {entry.id}: {e}")
            return False
    
    def batch_add_enhanced_entries(self, entries: List[EnhancedConversationEntry], batch_size: int = 100) -> Dict[str, int]:
        """
        Add multiple enhanced entries in batches.
        
        Args:
            entries: List of EnhancedConversationEntry objects
            batch_size: Batch size for processing
            
        Returns:
            Statistics about the batch add operation
        """
        logger.info(f"📦 Batch adding {len(entries)} enhanced entries (batch size: {batch_size})")
        
        stats = {'added': 0, 'skipped': 0, 'errors': 0}
        
        for i in range(0, len(entries), batch_size):
            batch = entries[i:i + batch_size]
            
            try:
                batch_docs = []
                batch_metadatas = []
                batch_ids = []
                
                for entry in batch:
                    # Create content hash for deduplication
                    content_hash = hashlib.md5(entry.content.encode('utf-8')).hexdigest()
                    
                    # Convert to ChromaDB-compatible metadata with semantic support
                    # Use semantic-enhanced metadata if semantic validation fields are populated
                    if hasattr(entry, 'semantic_validation') and entry.semantic_validation.semantic_sentiment:
                        metadata = entry.to_semantic_enhanced_metadata()
                    else:
                        metadata = entry.to_enhanced_metadata()
                    
                    metadata['content_hash'] = content_hash
                    
                    batch_docs.append(entry.content)
                    batch_metadatas.append(metadata)
                    batch_ids.append(entry.id)
                
                # Add batch to collection
                self.collection.add(
                    documents=batch_docs,
                    metadatas=batch_metadatas,
                    ids=batch_ids
                )
                
                stats['added'] += len(batch)
                logger.info(f"✅ Batch {i//batch_size + 1} added: {len(batch)} entries")
                
            except Exception as e:
                logger.error(f"Batch {i//batch_size + 1} error: {e}")
                stats['errors'] += len(batch)
        
        logger.info(f"🎯 Batch add complete: {stats}")
        return stats
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector database collection"""
        
        try:
            count = self.collection.count()
            
            # Get sample of metadata for analysis
            sample_data = self.collection.get(
                limit=min(1000, count),
                include=["metadatas"]
            )
            
            if not sample_data['metadatas']:
                return {"total_entries": count, "projects": {}}
            
            # Analyze projects
            projects = {}
            type_counts = {"user": 0, "assistant": 0}
            code_entries = 0
            
            for metadata in sample_data['metadatas']:
                project_name = metadata.get('project_name', 'unknown')
                msg_type = metadata.get('type', 'unknown')
                has_code = metadata.get('has_code', False)
                
                if project_name not in projects:
                    projects[project_name] = {"count": 0, "user": 0, "assistant": 0, "code": 0}
                
                projects[project_name]["count"] += 1
                projects[project_name][msg_type] = projects[project_name].get(msg_type, 0) + 1
                
                if msg_type in type_counts:
                    type_counts[msg_type] += 1
                
                if has_code:
                    projects[project_name]["code"] += 1
                    code_entries += 1
            
            return {
                "total_entries": count,
                "sample_size": len(sample_data['metadatas']),
                "projects": projects,
                "message_types": type_counts,
                "code_entries": code_entries,
                "code_percentage": (code_entries / len(sample_data['metadatas'])) * 100 if sample_data['metadatas'] else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {"error": str(e)}
    
    def rebuild_index(self, max_files: int = None) -> Dict[str, Any]:
        """Rebuild the entire vector database index from conversation files"""
        
        logger.info("🔄 Rebuilding vector database index...")
        
        # Clear existing collection
        try:
            self.client.delete_collection(name=self.collection_name)
            logger.info("✅ Cleared existing collection")
        except Exception:
            pass
        
        # Create new collection
        self.collection = self.client.create_collection(
            name=self.collection_name,
            embedding_function=self.embedding_function,
            metadata={"description": "Claude Code conversation context with project-aware search"}
        )
        
        # Extract all conversations
        extractor = ConversationExtractor()
        entries = extractor.extract_all_conversations(max_files=max_files)
        
        if not entries:
            logger.error("No conversation entries found")
            return {"error": "No conversation entries found"}
        
        # Add to vector database
        results = self.add_conversation_entries(entries)
        
        # Get final stats
        stats = self.get_collection_stats()
        
        logger.info("✅ Vector database index rebuild completed")
        
        return {
            "rebuild_results": results,
            "final_stats": stats,
            "total_processed": len(entries)
        }

def main():
    """Test the vector database implementation"""
    
    print("🚀 Testing Claude Code Vector Database")
    print("=" * 50)
    
    # Initialize database
    db = ClaudeVectorDatabase()
    
    # Get current stats
    stats = db.get_collection_stats()
    print("\n📊 Current Database Stats:")
    print(f"   Total entries: {stats.get('total_entries', 0)}")
    print(f"   Projects: {len(stats.get('projects', {}))}")
    
    # If empty, rebuild index
    if stats.get('total_entries', 0) == 0:
        print("\n🔄 Database is empty, rebuilding index...")
        rebuild_results = db.rebuild_index(max_files=5)  # Test with 5 files
        print(f"✅ Rebuild completed: {rebuild_results.get('total_processed', 0)} entries processed")
    
    # Test searches
    print("\n🧪 Testing search functionality...")
    
    test_queries = [
        ("React hooks error", "tylergohr.com"),
        ("TypeScript interface", "tylergohr.com"),
        ("vector database", "AI Orchestrator Platform"),
        ("performance optimization", None),
        ("git commit", None)
    ]
    
    for query, project in test_queries:
        print(f"\n🔍 Query: '{query}' | Project: {project}")
        results = db.search_conversations(query, current_project=project, n_results=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"   {i}. [{result['type']}] {result['project_name']} (score: {result['relevance_score']:.3f})")
                print(f"      {result['content'][:100]}...")
        else:
            print("   No results found")
    
    print("\n✅ Vector database test completed!")

if __name__ == "__main__":
    main()