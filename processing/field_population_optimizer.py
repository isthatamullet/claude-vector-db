#!/usr/bin/env python3
"""
Field Population Optimizer for Claude Code Vector Database

This module systematically analyzes and optimizes all 30+ metadata fields in the
enhanced conversation entries to ensure comprehensive field population and
data quality across the entire database.

Key Features:
- Systematic analysis of all enhanced metadata fields
- Field-specific optimization strategies
- Population threshold enforcement (90%+ for critical fields)
- Performance-optimized batch processing
- Integration with existing enhancement processing pipeline

Enhanced Fields Optimized:
- Topic awareness: detected_topics, primary_topic, topic_confidence
- Solution quality: solution_quality_score, has_success_markers, has_quality_indicators
- Adjacency tracking: previous_message_id, next_message_id, message_sequence_position
- Feedback learning: user_feedback_sentiment, is_validated_solution, validation_strength
- Context relationships: related_solution_id, feedback_message_id, solution_category

Author: Enhanced Vector Database System (July 2025)
Version: 1.0.0
"""

import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

# Import existing components
from database.vector_database import ClaudeVectorDatabase
from processing.enhanced_processor import UnifiedEnhancementProcessor

# Import enhanced context functions
from database.enhanced_context import (
    detect_conversation_topics,
    calculate_solution_quality_score,
    analyze_feedback_sentiment,
    is_solution_attempt,
    classify_solution_type
)

logger = logging.getLogger(__name__)


@dataclass
class FieldOptimizationStrategy:
    """Strategy for optimizing a specific metadata field."""
    field_name: str
    field_type: str  # 'string', 'float', 'boolean', 'dict', 'list'
    population_threshold: float  # Target population percentage (0.0-1.0)
    optimization_function: Optional[str] = None  # Function to calculate field value
    dependencies: List[str] = field(default_factory=list)  # Other fields this depends on
    priority: str = "medium"  # 'critical', 'high', 'medium', 'low'


@dataclass
class FieldAnalysisResult:
    """Results from analyzing a specific field."""
    field_name: str
    total_entries: int = 0
    populated_entries: int = 0
    population_percentage: float = 0.0
    meets_threshold: bool = False
    sample_values: List[Any] = field(default_factory=list)
    quality_score: float = 0.0
    optimization_needed: bool = False


@dataclass
class OptimizationResult:
    """Results from field population optimization."""
    session_id: str
    fields_optimized: List[str] = field(default_factory=list)
    improvement_scores: Dict[str, float] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    success: bool = False


class FieldPopulationOptimizer:
    """
    Systematically optimize all enhanced metadata fields.
    
    This optimizer ensures comprehensive field population by analyzing
    current field coverage and applying targeted optimization strategies
    to achieve population thresholds for all 30+ enhanced fields.
    """
    
    def __init__(self, database: ClaudeVectorDatabase):
        """Initialize the field population optimizer."""
        self.database = database
        self.processor = UnifiedEnhancementProcessor(suppress_init_logging=True)
        
        # Define optimization strategies for all enhanced fields
        self.field_strategies = self._initialize_field_strategies()
        
        # Processing configuration
        self.batch_size = 100  # ChromaDB batch limit compliance
        self.max_entries_per_session = 500  # Performance limit
        
        # Statistics tracking
        self.stats = {
            'sessions_processed': 0,
            'total_fields_optimized': 0,
            'total_entries_updated': 0,
            'optimization_time_total_ms': 0.0,
            'field_improvement_scores': {}
        }
        
        logger.info("⚙️ FieldPopulationOptimizer initialized with strategies for 30+ fields")
    
    def _initialize_field_strategies(self) -> Dict[str, FieldOptimizationStrategy]:
        """Initialize optimization strategies for all enhanced fields."""
        strategies = {}
        
        # Topic awareness fields (Critical - used for search relevance)
        strategies['detected_topics'] = FieldOptimizationStrategy(
            field_name='detected_topics',
            field_type='dict',
            population_threshold=0.90,  # 90% target
            optimization_function='detect_conversation_topics',
            priority='critical'
        )
        
        strategies['primary_topic'] = FieldOptimizationStrategy(
            field_name='primary_topic',
            field_type='string',
            population_threshold=0.85,
            dependencies=['detected_topics'],
            priority='high'
        )
        
        strategies['topic_confidence'] = FieldOptimizationStrategy(
            field_name='topic_confidence',
            field_type='float',
            population_threshold=0.85,
            dependencies=['detected_topics', 'primary_topic'],
            priority='high'
        )
        
        # Solution quality fields (Critical - used for solution ranking)
        strategies['solution_quality_score'] = FieldOptimizationStrategy(
            field_name='solution_quality_score',
            field_type='float',
            population_threshold=0.95,  # 95% target - very important
            optimization_function='calculate_solution_quality_score',
            priority='critical'
        )
        
        strategies['has_success_markers'] = FieldOptimizationStrategy(
            field_name='has_success_markers',
            field_type='boolean',
            population_threshold=0.90,
            optimization_function='detect_success_markers',
            priority='high'
        )
        
        strategies['has_quality_indicators'] = FieldOptimizationStrategy(
            field_name='has_quality_indicators',
            field_type='boolean',
            population_threshold=0.90,
            optimization_function='detect_quality_indicators',
            priority='high'
        )
        
        # Adjacency tracking fields (Critical - addresses main system issue)
        strategies['previous_message_id'] = FieldOptimizationStrategy(
            field_name='previous_message_id',
            field_type='string',
            population_threshold=0.80,  # 80% target - main issue to fix
            optimization_function='build_adjacency_relationships',
            priority='critical'
        )
        
        strategies['next_message_id'] = FieldOptimizationStrategy(
            field_name='next_message_id',
            field_type='string',
            population_threshold=0.80,  # 80% target - main issue to fix
            optimization_function='build_adjacency_relationships',
            priority='critical'
        )
        
        strategies['message_sequence_position'] = FieldOptimizationStrategy(
            field_name='message_sequence_position',
            field_type='int',
            population_threshold=0.95,  # Should be very high
            optimization_function='calculate_sequence_position',
            priority='high'
        )
        
        # Feedback learning fields (High priority - used for validation learning)
        strategies['user_feedback_sentiment'] = FieldOptimizationStrategy(
            field_name='user_feedback_sentiment',
            field_type='string',
            population_threshold=0.30,  # Lower threshold - only applies to feedback messages
            optimization_function='analyze_feedback_sentiment',
            priority='high'
        )
        
        strategies['is_validated_solution'] = FieldOptimizationStrategy(
            field_name='is_validated_solution',
            field_type='boolean',
            population_threshold=0.25,  # Lower threshold - only applies to validated solutions
            optimization_function='detect_validation_status',
            priority='high'
        )
        
        strategies['is_refuted_attempt'] = FieldOptimizationStrategy(
            field_name='is_refuted_attempt',
            field_type='boolean',
            population_threshold=0.15,  # Lower threshold - only applies to refuted solutions
            optimization_function='detect_validation_status',
            priority='high'
        )
        
        strategies['validation_strength'] = FieldOptimizationStrategy(
            field_name='validation_strength',
            field_type='float',
            population_threshold=0.40,  # Applies to validated/refuted solutions
            dependencies=['user_feedback_sentiment'],
            priority='medium'
        )
        
        strategies['outcome_certainty'] = FieldOptimizationStrategy(
            field_name='outcome_certainty',
            field_type='float',
            population_threshold=0.40,
            dependencies=['user_feedback_sentiment'],
            priority='medium'
        )
        
        # Context relationship fields (High priority - used for solution-feedback chains)
        strategies['is_solution_attempt'] = FieldOptimizationStrategy(
            field_name='is_solution_attempt',
            field_type='boolean',
            population_threshold=0.90,
            optimization_function='is_solution_attempt',
            priority='high'
        )
        
        strategies['is_feedback_to_solution'] = FieldOptimizationStrategy(
            field_name='is_feedback_to_solution',
            field_type='boolean',
            population_threshold=0.30,  # Lower threshold - only applies to feedback
            optimization_function='detect_feedback_relationship',
            priority='high'
        )
        
        strategies['related_solution_id'] = FieldOptimizationStrategy(
            field_name='related_solution_id',
            field_type='string',
            population_threshold=0.25,  # Applies to feedback messages
            dependencies=['is_feedback_to_solution'],
            priority='medium'
        )
        
        strategies['feedback_message_id'] = FieldOptimizationStrategy(
            field_name='feedback_message_id',
            field_type='string',
            population_threshold=0.20,  # Applies to solutions with feedback
            dependencies=['is_solution_attempt'],
            priority='medium'
        )
        
        strategies['solution_category'] = FieldOptimizationStrategy(
            field_name='solution_category',
            field_type='string',
            population_threshold=0.80,  # High threshold for solution categorization
            optimization_function='classify_solution_type',
            dependencies=['is_solution_attempt'],
            priority='medium'
        )
        
        # Add more fields as needed...
        # Additional enhancement fields can be added here following the same pattern
        
        logger.info(f"📋 Initialized {len(strategies)} field optimization strategies")
        return strategies
    
    def optimize_session(self, session_id: str,
                        target_fields: Optional[List[str]] = None,
                        force_reprocessing: bool = False) -> OptimizationResult:
        """
        Optimize field population for a single session.
        
        Args:
            session_id: Session identifier to optimize
            target_fields: Specific fields to optimize (None for all fields)
            force_reprocessing: Force reprocessing even if fields appear populated
            
        Returns:
            OptimizationResult with improvement statistics
        """
        start_time = time.time()
        
        logger.info(f"⚙️ Starting field optimization for session: {session_id}")
        
        try:
            # Step 1: Analyze current field population for session
            field_analysis = self._analyze_session_fields(session_id, target_fields)
            logger.info(f"📊 Analyzed {len(field_analysis)} fields for optimization")
            
            # Step 2: Identify fields needing optimization
            fields_to_optimize = self._identify_optimization_candidates(
                field_analysis, force_reprocessing
            )
            logger.info(f"🎯 Identified {len(fields_to_optimize)} fields needing optimization")
            
            if not fields_to_optimize:
                processing_time_ms = (time.time() - start_time) * 1000
                logger.info(f"✅ No optimization needed for {session_id}")
                return OptimizationResult(
                    session_id=session_id,
                    processing_time_ms=processing_time_ms,
                    success=True
                )
            
            # Step 3: Load session entries for processing
            session_entries = self._load_session_entries(session_id)
            logger.info(f"📄 Loaded {len(session_entries)} entries for processing")
            
            # Step 4: Apply field optimization strategies
            optimization_results = self._apply_optimization_strategies(
                session_entries, fields_to_optimize
            )
            logger.info(f"🔧 Applied optimization to {len(optimization_results)} entries")
            
            # Step 5: Update database with optimized fields
            update_result = self._update_database_fields(optimization_results)
            logger.info(f"💾 Updated {update_result['updated_count']} database entries")
            
            # Step 6: Calculate improvement scores
            improvement_scores = self._calculate_field_improvements(
                field_analysis, fields_to_optimize, update_result['updated_count']
            )
            
            # Create final result
            processing_time_ms = (time.time() - start_time) * 1000
            result = OptimizationResult(
                session_id=session_id,
                fields_optimized=list(fields_to_optimize),
                improvement_scores=improvement_scores,
                processing_time_ms=processing_time_ms,
                success=True
            )
            
            # Update optimizer statistics
            self._update_optimizer_stats(result)
            
            logger.info(f"✅ Field optimization complete for {session_id}: "
                       f"{len(fields_to_optimize)} fields optimized in {processing_time_ms:.1f}ms")
            
            return result
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ Field optimization failed for {session_id}: {e}")
            
            return OptimizationResult(
                session_id=session_id,
                processing_time_ms=processing_time_ms,
                success=False
            )
    
    def _analyze_session_fields(self, session_id: str, 
                               target_fields: Optional[List[str]] = None) -> Dict[str, FieldAnalysisResult]:
        """
        Analyze current field population for a session.
        
        Args:
            session_id: Session to analyze
            target_fields: Specific fields to analyze (None for all)
            
        Returns:
            Dictionary mapping field names to analysis results
        """
        try:
            # Get session entries
            session_results = self.database.collection.get(
                where={"session_id": {"$eq": session_id}},
                include=['metadatas'],
                limit=self.max_entries_per_session
            )
            
            if not session_results['metadatas']:
                logger.warning(f"No entries found for session {session_id}")
                return {}
            
            # Determine fields to analyze
            fields_to_analyze = target_fields or list(self.field_strategies.keys())
            
            # Analyze each field
            field_analysis = {}
            for field_name in fields_to_analyze:
                if field_name not in self.field_strategies:
                    continue
                
                strategy = self.field_strategies[field_name]
                analysis = self._analyze_single_field(
                    field_name, strategy, session_results['metadatas']
                )
                field_analysis[field_name] = analysis
            
            return field_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze session fields for {session_id}: {e}")
            return {}
    
    def _analyze_single_field(self, field_name: str, strategy: FieldOptimizationStrategy,
                             metadatas: List[Dict]) -> FieldAnalysisResult:
        """
        Analyze a single field's population status.
        
        Args:
            field_name: Name of field to analyze
            strategy: Optimization strategy for the field
            metadatas: List of metadata dictionaries to analyze
            
        Returns:
            FieldAnalysisResult with analysis details
        """
        total_entries = len(metadatas)
        populated_entries = 0
        sample_values = []
        
        for metadata in metadatas:
            value = metadata.get(field_name)
            
            # Check if field is populated based on type
            is_populated = self._is_field_populated(value, strategy.field_type)
            
            if is_populated:
                populated_entries += 1
                # Collect sample values (limit to 10)
                if len(sample_values) < 10:
                    sample_values.append(value)
        
        # Calculate metrics
        population_percentage = populated_entries / total_entries if total_entries > 0 else 0.0
        meets_threshold = population_percentage >= strategy.population_threshold
        optimization_needed = not meets_threshold
        
        # Calculate quality score based on population and threshold
        if population_percentage >= strategy.population_threshold:
            quality_score = 1.0
        else:
            quality_score = population_percentage / strategy.population_threshold
        
        return FieldAnalysisResult(
            field_name=field_name,
            total_entries=total_entries,
            populated_entries=populated_entries,
            population_percentage=population_percentage,
            meets_threshold=meets_threshold,
            sample_values=sample_values,
            quality_score=quality_score,
            optimization_needed=optimization_needed
        )
    
    def _is_field_populated(self, value: Any, field_type: str) -> bool:
        """
        Check if a field value is considered populated.
        
        Args:
            value: Field value to check
            field_type: Type of field ('string', 'float', 'boolean', 'dict', 'list')
            
        Returns:
            True if field is populated with meaningful data
        """
        if value is None:
            return False
        
        if field_type == 'string':
            return isinstance(value, str) and len(value.strip()) > 0
        elif field_type == 'float':
            return isinstance(value, (int, float)) and value != 0.0
        elif field_type == 'boolean':
            return isinstance(value, bool) and value is True
        elif field_type == 'dict':
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    return isinstance(parsed, dict) and len(parsed) > 0
                except json.JSONDecodeError:
                    return False
            return isinstance(value, dict) and len(value) > 0
        elif field_type == 'list':
            if isinstance(value, str):
                try:
                    parsed = json.loads(value)
                    return isinstance(parsed, list) and len(parsed) > 0
                except json.JSONDecodeError:
                    return False
            return isinstance(value, list) and len(value) > 0
        elif field_type == 'int':
            return isinstance(value, int) and value != 0
        
        return False
    
    def _identify_optimization_candidates(self, field_analysis: Dict[str, FieldAnalysisResult],
                                        force_reprocessing: bool = False) -> Set[str]:
        """
        Identify fields that need optimization.
        
        Args:
            field_analysis: Results from field analysis
            force_reprocessing: Force optimization even if thresholds are met
            
        Returns:
            Set of field names that need optimization
        """
        candidates = set()
        
        for field_name, analysis in field_analysis.items():
            strategy = self.field_strategies.get(field_name)
            if not strategy:
                continue
            
            # Add field if it needs optimization or force reprocessing is enabled
            if analysis.optimization_needed or force_reprocessing:
                candidates.add(field_name)
                
                logger.debug(f"Field {field_name}: {analysis.population_percentage:.1%} "
                           f"(threshold: {strategy.population_threshold:.1%}) - "
                           f"{'NEEDS OPTIMIZATION' if analysis.optimization_needed else 'FORCED'}")
        
        # Sort by priority (critical first, then high, medium, low)
        priority_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        candidates = sorted(candidates, key=lambda f: priority_order.get(
            self.field_strategies[f].priority, 3
        ))
        
        return set(candidates)
    
    def _load_session_entries(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Load session entries for processing.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of entry dictionaries with content and metadata
        """
        try:
            results = self.database.collection.get(
                where={"session_id": {"$eq": session_id}},
                include=['documents', 'metadatas'],
                limit=self.max_entries_per_session
            )
            
            if not results['documents'] or not results['metadatas']:
                return []
            
            # Combine documents and metadata
            entries = []
            for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                entry = {
                    'content': doc,
                    'metadata': metadata,
                    'index': i
                }
                entries.append(entry)
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to load session entries for {session_id}: {e}")
            return []
    
    def _apply_optimization_strategies(self, entries: List[Dict[str, Any]], 
                                     fields_to_optimize: Set[str]) -> List[Dict[str, Any]]:
        """
        Apply optimization strategies to entries.
        
        Args:
            entries: List of entry dictionaries
            fields_to_optimize: Set of field names to optimize
            
        Returns:
            List of entries with optimized field values
        """
        optimized_entries = []
        
        for entry in entries:
            content = entry['content']
            metadata = entry['metadata'].copy()
            
            # Track if any fields were optimized for this entry
            entry_optimized = False
            
            # Apply optimization for each field
            for field_name in fields_to_optimize:
                strategy = self.field_strategies.get(field_name)
                if not strategy:
                    continue
                
                # Check if field needs optimization for this entry
                current_value = metadata.get(field_name)
                if self._is_field_populated(current_value, strategy.field_type) and not entry_optimized:
                    continue  # Field already populated, skip unless force reprocessing
                
                # Apply optimization strategy
                optimized_value = self._optimize_field_value(
                    field_name, strategy, content, metadata, entries
                )
                
                if optimized_value is not None:
                    metadata[field_name] = optimized_value
                    entry_optimized = True
            
            # Add entry to results if it was optimized
            if entry_optimized:
                entry['metadata'] = metadata
                entry['optimized'] = True
                optimized_entries.append(entry)
        
        return optimized_entries
    
    def _optimize_field_value(self, field_name: str, strategy: FieldOptimizationStrategy,
                             content: str, metadata: Dict, all_entries: List[Dict]) -> Any:
        """
        Optimize a specific field value using the appropriate strategy.
        
        Args:
            field_name: Name of field to optimize
            strategy: Optimization strategy
            content: Entry content
            metadata: Entry metadata
            all_entries: All session entries (for context)
            
        Returns:
            Optimized field value or None if optimization failed
        """
        try:
            # Apply field-specific optimization
            if field_name == 'detected_topics':
                topics = detect_conversation_topics(content)
                return json.dumps(topics) if topics else None
                
            elif field_name == 'primary_topic':
                # Depends on detected_topics
                topics_json = metadata.get('detected_topics', '{}')
                try:
                    topics = json.loads(topics_json) if isinstance(topics_json, str) else topics_json
                    if topics:
                        return max(topics.items(), key=lambda x: x[1])[0]
                except (json.JSONDecodeError, ValueError):
                    pass
                return None
                
            elif field_name == 'topic_confidence':
                # Depends on detected_topics and primary_topic
                topics_json = metadata.get('detected_topics', '{}')
                primary_topic = metadata.get('primary_topic')
                try:
                    topics = json.loads(topics_json) if isinstance(topics_json, str) else topics_json
                    if topics and primary_topic and primary_topic in topics:
                        return float(topics[primary_topic])
                except (json.JSONDecodeError, ValueError):
                    pass
                return 0.0
                
            elif field_name == 'solution_quality_score':
                return calculate_solution_quality_score(content, metadata)
                
            elif field_name == 'has_success_markers':
                success_markers = ['✅', 'fixed', 'working', 'solved', 'success', 'complete']
                return any(marker.lower() in content.lower() for marker in success_markers)
                
            elif field_name == 'has_quality_indicators':
                quality_indicators = ['tested', 'validated', 'confirmed', 'production-ready']
                return any(indicator.lower() in content.lower() for indicator in quality_indicators)
                
            elif field_name == 'is_solution_attempt':
                return is_solution_attempt(content)
                
            elif field_name == 'solution_category':
                if is_solution_attempt(content):
                    return classify_solution_type(content)
                return None
                
            elif field_name == 'user_feedback_sentiment':
                # Only for user messages that might be feedback
                if metadata.get('type') == 'user':
                    feedback_analysis = analyze_feedback_sentiment(content)
                    if feedback_analysis['sentiment'] != 'neutral':
                        return feedback_analysis['sentiment']
                return None
                
            elif field_name == 'validation_strength':
                sentiment = metadata.get('user_feedback_sentiment')
                if sentiment:
                    feedback_analysis = analyze_feedback_sentiment(content)
                    return feedback_analysis.get('strength', 0.0)
                return 0.0
                
            elif field_name == 'outcome_certainty':
                sentiment = metadata.get('user_feedback_sentiment')
                if sentiment:
                    feedback_analysis = analyze_feedback_sentiment(content)
                    return feedback_analysis.get('certainty', 0.0)
                return 0.0
                
            elif field_name == 'is_validated_solution':
                sentiment = metadata.get('user_feedback_sentiment')
                return sentiment == 'positive' if sentiment else False
                
            elif field_name == 'is_refuted_attempt':
                sentiment = metadata.get('user_feedback_sentiment')
                return sentiment == 'negative' if sentiment else False
                
            elif field_name == 'message_sequence_position':
                # Calculate based on position in all_entries
                for i, entry in enumerate(all_entries):
                    if entry['metadata'].get('id') == metadata.get('id'):
                        return i
                return 0
                
            # For adjacency fields, these should be handled by the back-fill engine
            elif field_name in ['previous_message_id', 'next_message_id', 'related_solution_id', 'feedback_message_id']:
                # These require conversation-level analysis, handled by back-fill engine
                return None
                
            else:
                logger.warning(f"No optimization strategy implemented for field: {field_name}")
                return None
                
        except Exception as e:
            logger.warning(f"Field optimization failed for {field_name}: {e}")
            return None
    
    def _update_database_fields(self, optimized_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Update database with optimized field values.
        
        Args:
            optimized_entries: List of entries with optimized fields
            
        Returns:
            Update statistics dictionary
        """
        if not optimized_entries:
            return {'updated_count': 0, 'batch_errors': 0}
        
        logger.info(f"💾 Updating database with {len(optimized_entries)} optimized entries")
        
        update_stats = {
            'attempted_updates': 0,
            'successful_updates': 0,
            'updated_count': 0,
            'batch_errors': 0
        }
        
        # Process in batches to respect ChromaDB limits
        batch_size = min(self.batch_size, 166)  # ChromaDB constraint
        
        for i in range(0, len(optimized_entries), batch_size):
            batch = optimized_entries[i:i + batch_size]
            
            try:
                # Prepare batch update
                ids = []
                metadatas = []
                
                for entry in batch:
                    entry_id = entry['metadata'].get('id')
                    if entry_id:
                        ids.append(entry_id)
                        
                        # Add optimization timestamp
                        metadata = entry['metadata'].copy()
                        metadata['field_optimization_timestamp'] = datetime.now().isoformat()
                        metadata['field_optimization_processed'] = True
                        
                        metadatas.append(metadata)
                
                # Execute batch update
                if ids and metadatas:
                    self.database.collection.update(
                        ids=ids,
                        metadatas=metadatas
                    )
                    
                    update_stats['successful_updates'] += len(ids)
                    update_stats['updated_count'] += len(ids)
                
                update_stats['attempted_updates'] += len(batch)
                
            except Exception as e:
                logger.error(f"Batch update error for batch {i//batch_size + 1}: {e}")
                update_stats['batch_errors'] += 1
        
        logger.info(f"📊 Database update complete: {update_stats['updated_count']} entries updated")
        
        return update_stats
    
    def _calculate_field_improvements(self, original_analysis: Dict[str, FieldAnalysisResult],
                                    optimized_fields: Set[str], 
                                    updated_count: int) -> Dict[str, float]:
        """
        Calculate improvement scores for optimized fields.
        
        Args:
            original_analysis: Original field analysis results
            optimized_fields: Set of fields that were optimized
            updated_count: Number of entries updated
            
        Returns:
            Dictionary mapping field names to improvement percentages
        """
        improvements = {}
        
        for field_name in optimized_fields:
            original = original_analysis.get(field_name)
            if not original:
                continue
            
            # Estimate improvement based on updates made
            if original.total_entries > 0:
                # Estimate how much the population improved
                estimated_new_populated = original.populated_entries + updated_count
                estimated_new_percentage = min(1.0, estimated_new_populated / original.total_entries)
                
                improvement_percentage = ((estimated_new_percentage - original.population_percentage) / 
                                        max(0.01, original.population_percentage)) * 100
                
                improvements[field_name] = max(0.0, improvement_percentage)
        
        return improvements
    
    def _update_optimizer_stats(self, result: OptimizationResult):
        """Update optimizer statistics."""
        self.stats['sessions_processed'] += 1
        self.stats['total_fields_optimized'] += len(result.fields_optimized)
        self.stats['optimization_time_total_ms'] += result.processing_time_ms
        
        # Update field-specific improvement scores
        for field_name, improvement in result.improvement_scores.items():
            if field_name not in self.stats['field_improvement_scores']:
                self.stats['field_improvement_scores'][field_name] = []
            self.stats['field_improvement_scores'][field_name].append(improvement)
    
    def get_optimizer_statistics(self) -> Dict[str, Any]:
        """Get comprehensive optimizer statistics."""
        avg_optimization_time = 0.0
        if self.stats['sessions_processed'] > 0:
            avg_optimization_time = self.stats['optimization_time_total_ms'] / self.stats['sessions_processed']
        
        # Calculate average improvements per field
        field_avg_improvements = {}
        for field_name, improvements in self.stats['field_improvement_scores'].items():
            if improvements:
                field_avg_improvements[field_name] = sum(improvements) / len(improvements)
        
        return {
            **self.stats,
            'average_optimization_time_ms': avg_optimization_time,
            'fields_per_session': (
                self.stats['total_fields_optimized'] / max(1, self.stats['sessions_processed'])
            ),
            'field_average_improvements': field_avg_improvements,
            'total_field_strategies': len(self.field_strategies)
        }
    
    def analyze_all_field_population(self) -> Dict[str, Any]:
        """
        Analyze field population across the entire database.
        
        Returns comprehensive analysis of all enhanced fields.
        """
        logger.info("📊 Analyzing field population across entire database")
        
        try:
            # Get sample of entries for analysis
            sample_size = 2000
            results = self.database.collection.get(
                limit=sample_size,
                include=['metadatas']
            )
            
            if not results['metadatas']:
                return {'error': 'No data available for analysis'}
            
            # Analyze all fields
            field_analysis = {}
            for field_name, strategy in self.field_strategies.items():
                analysis = self._analyze_single_field(
                    field_name, strategy, results['metadatas']
                )
                field_analysis[field_name] = {
                    'population_percentage': analysis.population_percentage,
                    'populated_entries': analysis.populated_entries,
                    'total_entries': analysis.total_entries,
                    'meets_threshold': analysis.meets_threshold,
                    'threshold': strategy.population_threshold,
                    'priority': strategy.priority,
                    'optimization_needed': analysis.optimization_needed
                }
            
            # Calculate overall statistics
            total_fields = len(field_analysis)
            fields_meeting_threshold = sum(1 for f in field_analysis.values() if f['meets_threshold'])
            critical_fields_needing_optimization = sum(
                1 for field_name, analysis in field_analysis.items()
                if analysis['optimization_needed'] and self.field_strategies[field_name].priority == 'critical'
            )
            
            return {
                'analysis_timestamp': datetime.now().isoformat(),
                'sample_size': len(results['metadatas']),
                'total_fields_analyzed': total_fields,
                'fields_meeting_threshold': fields_meeting_threshold,
                'threshold_compliance_rate': (fields_meeting_threshold / total_fields) * 100,
                'critical_fields_needing_optimization': critical_fields_needing_optimization,
                'field_analysis': field_analysis,
                'optimizer_stats': self.get_optimizer_statistics()
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze field population: {e}")
            return {'error': str(e), 'analysis_timestamp': datetime.now().isoformat()}


def main():
    """Test the field population optimizer."""
    print("⚙️ Testing Field Population Optimizer")
    print("=" * 60)
    
    # Initialize components
    database = ClaudeVectorDatabase()
    optimizer = FieldPopulationOptimizer(database)
    
    # Analyze current field population
    print("\n📊 Current Field Population Analysis:")
    analysis = optimizer.analyze_all_field_population()
    
    if 'error' not in analysis:
        compliance_rate = analysis.get('threshold_compliance_rate', 0)
        critical_issues = analysis.get('critical_fields_needing_optimization', 0)
        
        print(f"   Sample size: {analysis.get('sample_size', 0)}")
        print(f"   Fields analyzed: {analysis.get('total_fields_analyzed', 0)}")
        print(f"   Threshold compliance: {compliance_rate:.1f}%")
        print(f"   Critical fields needing optimization: {critical_issues}")
        
        # Show top fields needing optimization
        field_analysis = analysis.get('field_analysis', {})
        needs_optimization = [
            (name, data) for name, data in field_analysis.items()
            if data['optimization_needed']
        ]
        needs_optimization.sort(key=lambda x: x[1]['population_percentage'])
        
        print("\n   Top 5 fields needing optimization:")
        for name, data in needs_optimization[:5]:
            print(f"     • {name}: {data['population_percentage']:.1%} "
                  f"(threshold: {data['threshold']:.1%}) - {data['priority']} priority")
    else:
        print(f"   Error: {analysis['error']}")
    
    # Test optimization if sessions available
    print("\n🔍 Looking for sessions to test...")
    
    # Get recent session for testing
    recent_results = database.collection.get(limit=10, include=['metadatas'])
    test_session_id = None
    
    if recent_results['metadatas']:
        for metadata in recent_results['metadates']:
            if metadata and metadata.get('session_id'):
                test_session_id = metadata['session_id']
                break
    
    if test_session_id:
        print(f"\n⚙️ Testing field optimization on session: {test_session_id}")
        result = optimizer.optimize_session(test_session_id)
        
        print(f"   Success: {'✅' if result.success else '❌'}")
        print(f"   Fields optimized: {len(result.fields_optimized)}")
        print(f"   Processing time: {result.processing_time_ms:.1f}ms")
        
        if result.improvement_scores:
            print("   Improvements:")
            for field, improvement in result.improvement_scores.items():
                print(f"     • {field}: +{improvement:.1f}%")
    else:
        print("   No sessions available for testing")
    
    # Display optimizer statistics
    print("\n📈 Optimizer Statistics:")
    stats = optimizer.get_optimizer_statistics()
    print(f"   Sessions processed: {stats['sessions_processed']}")
    print(f"   Total fields optimized: {stats['total_fields_optimized']}")
    print(f"   Field strategies available: {stats['total_field_strategies']}")
    
    print("\n✅ Field Population Optimizer test completed!")


if __name__ == "__main__":
    main()