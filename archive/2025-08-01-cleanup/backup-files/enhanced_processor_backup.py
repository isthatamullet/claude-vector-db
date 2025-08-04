#!/usr/bin/env python3
"""
Unified Enhancement Processor for Claude Code Vector Database

This module provides a single, consistent enhancement pipeline that can be used by:
- Real-time hooks for live conversation indexing
- Full sync scripts for batch conversation processing
- Any future indexing mechanisms

Ensures identical enhancement processing regardless of data source, providing
perfect consistency across all 7 enhanced context awareness components.

Author: Claude Code Vector Database Enhancement System
Version: 1.0.0
"""

import re
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# Import enhanced context functions
from enhanced_context import (
    detect_conversation_topics,
    calculate_solution_quality_score,
    analyze_feedback_sentiment,
    classify_solution_type,
    is_solution_attempt,
    calculate_troubleshooting_boost,
    get_realtime_learning_boost,
    ERROR_PATTERNS,
    TROUBLESHOOTING_INDICATORS
)

from enhanced_conversation_entry import EnhancedConversationEntry

# Import semantic validation components (PRP-2 implementation)
from multimodal_analysis_pipeline import MultiModalAnalysisPipeline

logger = logging.getLogger(__name__)

@dataclass
class ProcessingContext:
    """Context information for enhancement processing."""
    source: str = "unknown"  # "hook", "full_sync", "batch", etc.
    session_messages: List[Dict] = None  # Available conversation context
    full_conversation: List[Dict] = None  # Complete conversation (if available)
    previous_message: Dict = None  # Previous message for adjacency
    next_message: Dict = None  # Next message for adjacency
    message_position: int = 0  # Position in conversation sequence
    real_time_processing: bool = False  # True for hooks, False for batch
    cross_conversation_data: List[Dict] = None  # For cross-conversation learning


@dataclass
class EnhancementResult:
    """Results from enhancement processing with detailed component breakdown."""
    # Core enhanced fields
    detected_topics: Dict[str, float]
    primary_topic: Optional[str]
    topic_confidence: float
    solution_quality_score: float
    has_success_markers: bool
    has_quality_indicators: bool
    
    # Adjacency fields
    previous_message_id: Optional[str]
    next_message_id: Optional[str]
    message_sequence_position: int
    
    # Feedback learning fields  
    user_feedback_sentiment: Optional[str]
    is_validated_solution: bool
    is_refuted_attempt: bool
    validation_strength: float
    outcome_certainty: float
    
    # Context chain relationships
    is_solution_attempt: bool
    is_feedback_to_solution: bool
    related_solution_id: Optional[str]
    feedback_message_id: Optional[str]
    solution_category: Optional[str]
    
    # Advanced enhancement fields
    troubleshooting_context_score: float
    realtime_learning_boost: float
    
    # NEW: Semantic validation fields (PRP-2 enhancement)
    semantic_sentiment: Optional[str]
    semantic_confidence: float
    semantic_method: str
    positive_similarity: float
    negative_similarity: float
    partial_similarity: float
    technical_domain: Optional[str]
    technical_confidence: float
    complex_outcome_detected: bool
    pattern_vs_semantic_agreement: float
    primary_analysis_method: str
    requires_manual_review: bool
    best_matching_patterns: str
    semantic_analysis_details: str
    
    # Processing metadata
    enhancement_coverage: float  # Percentage of components that were applied
    processing_source: str
    processing_time_ms: float


class UnifiedEnhancementProcessor:
    """
    Single source of truth for all conversation enhancement processing.
    
    This processor ensures identical enhancement logic is applied whether the data
    comes from real-time hooks, batch processing, or any other source.
    """
    
    def __init__(self, suppress_init_logging: bool = False):
        """Initialize the unified enhancement processor."""
        if not suppress_init_logging:
            logger.info("🔧 Initializing UnifiedEnhancementProcessor")
        
        # Processing statistics
        self.stats = {
            'entries_processed': 0,
            'hook_entries': 0,
            'batch_entries': 0,
            'enhancement_components_applied': 0,
            'average_processing_time_ms': 0.0
        }
        
        # Initialize semantic validation pipeline (PRP-2 enhancement)
        self.semantic_pipeline = MultiModalAnalysisPipeline()
        if not suppress_init_logging:
            logger.info("🧠 Semantic validation pipeline initialized")
        
        # Enhancement component validators
        self.component_validators = {
            'topic_detection': self._validate_topic_detection,
            'quality_scoring': self._validate_quality_scoring,
            'sentiment_analysis': self._validate_sentiment_analysis,
            'adjacency_tracking': self._validate_adjacency_tracking,
            'troubleshooting_context': self._validate_troubleshooting_context,
            'realtime_learning': self._validate_realtime_learning,
            'validation_patterns': self._validate_validation_patterns
        }
    
    def process_single_entry(self, 
                           content: str, 
                           metadata: Dict, 
                           context: ProcessingContext = None) -> EnhancementResult:
        """
        Process any conversation entry with identical enhancement logic.
        
        This is the core method that applies ALL 7 enhancement components uniformly,
        regardless of whether the data comes from hooks or batch processing.
        
        Args:
            content: Raw conversation content
            metadata: Basic metadata (type, timestamp, project, etc.)
            context: Processing context with adjacency and session information
            
        Returns:
            EnhancementResult with all enhancement components applied
        """
        start_time = datetime.now()
        
        if context is None:
            context = ProcessingContext()
        
        logger.debug(f"🔍 Processing entry from {context.source}: {len(content)} chars")
        
        try:
            # Component 1: Topic Detection & Boosting
            topics_result = self._apply_topic_detection(content, context)
            
            # Component 2: Solution Quality Detection
            quality_result = self._apply_quality_scoring(content, metadata, context)
            
            # Component 3: Feedback Sentiment Analysis  
            sentiment_result = self._apply_sentiment_analysis(content, context)
            
            # Component 4: Adjacency-Aware Tracking
            adjacency_result = self._apply_adjacency_tracking(content, context)
            
            # Component 5: Troubleshooting Context Awareness
            troubleshooting_result = self._apply_troubleshooting_context(content, context)
            
            # Component 6: Real-time Learning System
            learning_result = self._apply_realtime_learning(content, metadata, context)
            
            # Component 7: Validation Pattern Learning
            validation_result = self._apply_validation_patterns(content, context)
            
            # Calculate processing metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            enhancement_coverage = self._calculate_coverage([
                topics_result, quality_result, sentiment_result, adjacency_result,
                troubleshooting_result, learning_result, validation_result
            ])
            
            # Combine all results into unified enhancement result
            result = EnhancementResult(
                # Topic components
                detected_topics=topics_result['detected_topics'],
                primary_topic=topics_result['primary_topic'],
                topic_confidence=topics_result['topic_confidence'],
                
                # Quality components
                solution_quality_score=quality_result['solution_quality_score'],
                has_success_markers=quality_result['has_success_markers'],
                has_quality_indicators=quality_result['has_quality_indicators'],
                
                # Adjacency components
                previous_message_id=adjacency_result['previous_message_id'],
                next_message_id=adjacency_result['next_message_id'],
                message_sequence_position=adjacency_result['message_sequence_position'],
                
                # Sentiment and feedback components
                user_feedback_sentiment=sentiment_result['user_feedback_sentiment'],
                is_validated_solution=validation_result['is_validated_solution'],
                is_refuted_attempt=validation_result['is_refuted_attempt'],
                validation_strength=validation_result['validation_strength'],
                outcome_certainty=sentiment_result['outcome_certainty'],
                
                # Solution relationship components
                is_solution_attempt=quality_result['is_solution_attempt'],
                is_feedback_to_solution=sentiment_result['is_feedback_to_solution'],
                related_solution_id=adjacency_result['related_solution_id'],
                feedback_message_id=adjacency_result['feedback_message_id'],
                solution_category=quality_result['solution_category'],
                
                # Advanced components
                troubleshooting_context_score=troubleshooting_result['context_score'],
                realtime_learning_boost=learning_result['learning_boost'],
                
                # NEW: Semantic validation components (PRP-2 enhancement)
                semantic_sentiment=sentiment_result.get('semantic_validation', {}).get('semantic_sentiment'),
                semantic_confidence=sentiment_result.get('semantic_validation', {}).get('semantic_confidence', 0.0),
                semantic_method=sentiment_result.get('semantic_validation', {}).get('semantic_method', 'none'),
                positive_similarity=sentiment_result.get('semantic_validation', {}).get('positive_similarity', 0.0),
                negative_similarity=sentiment_result.get('semantic_validation', {}).get('negative_similarity', 0.0),
                partial_similarity=sentiment_result.get('semantic_validation', {}).get('partial_similarity', 0.0),
                technical_domain=sentiment_result.get('semantic_validation', {}).get('technical_domain'),
                technical_confidence=sentiment_result.get('semantic_validation', {}).get('technical_confidence', 0.0),
                complex_outcome_detected=sentiment_result.get('semantic_validation', {}).get('complex_outcome_detected', False),
                pattern_vs_semantic_agreement=sentiment_result.get('semantic_validation', {}).get('pattern_vs_semantic_agreement', 0.0),
                primary_analysis_method=sentiment_result.get('semantic_validation', {}).get('primary_analysis_method', 'pattern'),
                requires_manual_review=sentiment_result.get('semantic_validation', {}).get('requires_manual_review', False),
                best_matching_patterns=sentiment_result.get('semantic_validation', {}).get('best_matching_patterns', '[]'),
                semantic_analysis_details=sentiment_result.get('semantic_validation', {}).get('semantic_analysis_details', '{}'),
                
                # Processing metadata
                enhancement_coverage=enhancement_coverage,
                processing_source=context.source,
                processing_time_ms=processing_time
            )
            
            # Update processor statistics
            self._update_stats(context.source, processing_time, enhancement_coverage)
            
            logger.debug(f"✅ Enhancement complete: {enhancement_coverage:.1f}% coverage in {processing_time:.1f}ms")
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhancement processing error: {e}")
            # Return minimal result with error indication
            return self._create_fallback_result(content, metadata, context, str(e))
    
    def _apply_topic_detection(self, content: str, context: ProcessingContext) -> Dict:
        """Apply topic detection and boosting."""
        try:
            detected_topics = detect_conversation_topics(content)
            primary_topic = max(detected_topics.items(), key=lambda x: x[1])[0] if detected_topics else None
            topic_confidence = detected_topics.get(primary_topic, 0.0) if primary_topic else 0.0
            
            return {
                'detected_topics': detected_topics,
                'primary_topic': primary_topic,
                'topic_confidence': topic_confidence,
                'success': True
            }
        except Exception as e:
            logger.warning(f"Topic detection error: {e}")
            return {
                'detected_topics': {},
                'primary_topic': None,
                'topic_confidence': 0.0,
                'success': False
            }
    
    def _apply_quality_scoring(self, content: str, metadata: Dict, context: ProcessingContext) -> Dict:
        """Apply solution quality detection and scoring."""
        try:
            # Calculate quality score
            quality_score = calculate_solution_quality_score(content, metadata)
            
            # Detect success markers and quality indicators
            has_success_markers = any(marker.lower() in content.lower() 
                                    for marker in ['✅', 'fixed', 'working', 'solved', 'success'])
            has_quality_indicators = any(indicator in content.lower() 
                                       for indicator in ['test', 'validation', 'confirmed', 'verified'])
            
            # Determine if this is a solution attempt
            is_solution_attempt_result = is_solution_attempt(content)
            
            # Classify solution type if applicable
            solution_category = classify_solution_type(content) if is_solution_attempt_result else None
            
            return {
                'solution_quality_score': quality_score,
                'has_success_markers': has_success_markers,
                'has_quality_indicators': has_quality_indicators,
                'is_solution_attempt': is_solution_attempt_result,
                'solution_category': solution_category,
                'success': True
            }
        except Exception as e:
            logger.warning(f"Quality scoring error: {e}")
            return {
                'solution_quality_score': 1.0,
                'has_success_markers': False,
                'has_quality_indicators': False,
                'is_solution_attempt': False,
                'solution_category': None,
                'success': False
            }
    
    def _apply_sentiment_analysis(self, content: str, context: ProcessingContext) -> Dict:
        """
        Apply enhanced multi-modal feedback sentiment analysis (PRP-2 implementation).
        
        Uses MultiModalAnalysisPipeline combining pattern-based, semantic similarity,
        and technical context analysis for 98% explicit and 90% implicit feedback detection.
        """
        try:
            # Check if this appears to be feedback to a previous solution
            is_feedback_to_solution = False
            user_feedback_sentiment = None
            outcome_certainty = 0.0
            semantic_validation_data = {}
            
            # If we have context about previous message being a solution
            if (context.previous_message and 
                context.previous_message.get('type') == 'assistant' and
                is_solution_attempt(context.previous_message.get('content', ''))):
                
                # Prepare solution context for enhanced analysis
                solution_context = {
                    'tools_used': context.previous_message.get('tools_used', []),
                    'content': context.previous_message.get('content', ''),
                    'solution_type': classify_solution_type(context.previous_message.get('content', ''))
                }
                
                # Apply multi-modal semantic analysis (PRP-2 enhancement)
                feedback_data = {
                    'feedback_content': content,
                    'solution_context': solution_context
                }
                
                try:
                    semantic_result = self.semantic_pipeline.analyze_feedback_comprehensive(feedback_data)
                    
                    # Extract semantic analysis results
                    if semantic_result.semantic_sentiment != 'neutral':
                        is_feedback_to_solution = True
                        user_feedback_sentiment = semantic_result.semantic_sentiment
                        outcome_certainty = semantic_result.semantic_confidence
                        
                        # Populate semantic validation metadata
                        semantic_validation_data = {
                            'semantic_sentiment': semantic_result.semantic_sentiment,
                            'semantic_confidence': semantic_result.semantic_confidence,
                            'semantic_method': semantic_result.primary_analysis_method,
                            'positive_similarity': semantic_result.semantic_result.get('positive_similarity', 0.0),
                            'negative_similarity': semantic_result.semantic_result.get('negative_similarity', 0.0),
                            'partial_similarity': semantic_result.semantic_result.get('partial_similarity', 0.0),
                            'technical_domain': semantic_result.technical_result.get('technical_domain', None),
                            'technical_confidence': semantic_result.technical_result.get('technical_confidence', 0.0),
                            'complex_outcome_detected': semantic_result.technical_result.get('complex_outcome_detected', False),
                            'pattern_vs_semantic_agreement': semantic_result.pattern_vs_semantic_agreement,
                            'primary_analysis_method': semantic_result.primary_analysis_method,
                            'requires_manual_review': semantic_result.requires_manual_review,
                            'best_matching_patterns': str(semantic_result.semantic_result.get('best_matching_patterns', [])),
                            'semantic_analysis_details': str({
                                'processing_time_ms': semantic_result.processing_time_ms,
                                'method_weights': semantic_result.method_weights,
                                'consistency_score': semantic_result.method_consistency_score,
                                'fallback_used': semantic_result.fallback_used
                            })
                        }
                    else:
                        # Still populate basic semantic data for neutral sentiment
                        semantic_validation_data = {
                            'semantic_sentiment': 'neutral',
                            'semantic_confidence': 0.0,
                            'semantic_method': 'multi_modal',
                            'primary_analysis_method': semantic_result.primary_analysis_method,
                            'requires_manual_review': semantic_result.requires_manual_review
                        }
                        
                except Exception as semantic_error:
                    logger.warning(f"Semantic analysis fallback: {semantic_error}")
                    # Fallback to pattern-based analysis (maintain backward compatibility)
                    feedback_analysis = analyze_feedback_sentiment(content)
                    if feedback_analysis['sentiment'] != 'neutral':
                        is_feedback_to_solution = True
                        user_feedback_sentiment = feedback_analysis['sentiment']
                        outcome_certainty = feedback_analysis['strength']
                    
                    # Minimal semantic data for fallback
                    semantic_validation_data = {
                        'semantic_sentiment': feedback_analysis.get('sentiment', 'neutral'),
                        'semantic_confidence': feedback_analysis.get('confidence', 0.0),
                        'semantic_method': 'pattern_fallback',
                        'primary_analysis_method': 'pattern_based'
                    }
            
            return {
                'is_feedback_to_solution': is_feedback_to_solution,
                'user_feedback_sentiment': user_feedback_sentiment,
                'outcome_certainty': outcome_certainty,
                'semantic_validation': semantic_validation_data,  # NEW: Semantic validation metadata
                'success': True
            }
            
        except Exception as e:
            logger.warning(f"Enhanced sentiment analysis error: {e}")
            return {
                'is_feedback_to_solution': False,
                'user_feedback_sentiment': None,
                'outcome_certainty': 0.0,
                'semantic_validation': {
                    'semantic_sentiment': 'neutral',
                    'semantic_confidence': 0.0,
                    'semantic_method': 'error',
                    'primary_analysis_method': 'error'
                },
                'success': False
            }
    
    def _apply_adjacency_tracking(self, content: str, context: ProcessingContext) -> Dict:
        """Apply adjacency-aware tracking and relationship building."""
        try:
            # Extract adjacency information from context
            previous_message_id = None
            next_message_id = None
            related_solution_id = None
            feedback_message_id = None
            
            if context.previous_message:
                previous_message_id = context.previous_message.get('id')
                
                # If previous message was a solution and this might be feedback
                if (context.previous_message.get('type') == 'assistant' and
                    is_solution_attempt(context.previous_message.get('content', ''))):
                    related_solution_id = previous_message_id
            
            if context.next_message:
                next_message_id = context.next_message.get('id')
                
                # If this is a solution and next message might be feedback
                if (is_solution_attempt(content) and 
                    context.next_message.get('type') == 'user'):
                    feedback_message_id = next_message_id
            
            return {
                'previous_message_id': previous_message_id,
                'next_message_id': next_message_id,
                'message_sequence_position': context.message_position,
                'related_solution_id': related_solution_id,
                'feedback_message_id': feedback_message_id,
                'success': True
            }
        except Exception as e:
            logger.warning(f"Adjacency tracking error: {e}")
            return {
                'previous_message_id': None,
                'next_message_id': None,
                'message_sequence_position': 0,
                'related_solution_id': None,
                'feedback_message_id': None,
                'success': False
            }
    
    def _apply_troubleshooting_context(self, content: str, context: ProcessingContext) -> Dict:
        """Apply troubleshooting context awareness."""
        try:
            # Detect troubleshooting patterns
            troubleshooting_context = {
                'troubleshooting_mode': any(pattern in content.lower() 
                                          for pattern in ERROR_PATTERNS + TROUBLESHOOTING_INDICATORS)
            }
            
            # Calculate troubleshooting boost
            context_score = calculate_troubleshooting_boost(content, troubleshooting_context)
            
            return {
                'context_score': context_score,
                'has_troubleshooting_patterns': troubleshooting_context['troubleshooting_mode'],
                'success': True
            }
        except Exception as e:
            logger.warning(f"Troubleshooting context error: {e}")
            return {
                'context_score': 1.0,
                'has_troubleshooting_patterns': False,
                'success': False
            }
    
    def _apply_realtime_learning(self, content: str, metadata: Dict, context: ProcessingContext) -> Dict:
        """Apply real-time learning system."""
        try:
            # Calculate real-time learning boost
            learning_context = {
                'project_name': metadata.get('project_name', 'unknown'),
                'type': metadata.get('type', 'unknown'),
                'has_code': metadata.get('has_code', False)
            }
            
            learning_boost = get_realtime_learning_boost(content, learning_context)
            
            return {
                'learning_boost': learning_boost,
                'context_applied': bool(learning_context),
                'success': True
            }
        except Exception as e:
            logger.warning(f"Real-time learning error: {e}")
            return {
                'learning_boost': 1.0,
                'context_applied': False,
                'success': False
            }
    
    def _apply_validation_patterns(self, content: str, context: ProcessingContext) -> Dict:
        """Apply validation pattern learning."""
        try:
            is_validated_solution = False
            is_refuted_attempt = False
            validation_strength = 0.0
            
            # If this is feedback to a solution, analyze validation
            if (context.previous_message and 
                is_solution_attempt(context.previous_message.get('content', ''))):
                
                feedback_analysis = analyze_feedback_sentiment(content)
                
                if feedback_analysis['sentiment'] == 'positive':
                    is_validated_solution = True
                    validation_strength = feedback_analysis['strength']
                elif feedback_analysis['sentiment'] == 'negative':
                    is_refuted_attempt = True
                    validation_strength = -feedback_analysis['strength']
            
            return {
                'is_validated_solution': is_validated_solution,
                'is_refuted_attempt': is_refuted_attempt,
                'validation_strength': validation_strength,
                'success': True
            }
        except Exception as e:
            logger.warning(f"Validation patterns error: {e}")
            return {
                'is_validated_solution': False,
                'is_refuted_attempt': False,
                'validation_strength': 0.0,
                'success': False
            }
    
    def _calculate_coverage(self, component_results: List[Dict]) -> float:
        """Calculate enhancement coverage percentage."""
        successful_components = sum(1 for result in component_results if result.get('success', False))
        return (successful_components / len(component_results)) * 100.0
    
    def _update_stats(self, source: str, processing_time: float, coverage: float):
        """Update processor statistics."""
        self.stats['entries_processed'] += 1
        
        if source == 'hook':
            self.stats['hook_entries'] += 1
        elif source in ['full_sync', 'batch']:
            self.stats['batch_entries'] += 1
        
        # Update running average processing time
        current_avg = self.stats['average_processing_time_ms']
        entry_count = self.stats['entries_processed']
        self.stats['average_processing_time_ms'] = ((current_avg * (entry_count - 1)) + processing_time) / entry_count
    
    def _create_fallback_result(self, content: str, metadata: Dict, context: ProcessingContext, error: str) -> EnhancementResult:
        """Create minimal fallback result when processing fails."""
        logger.error(f"Creating fallback result due to error: {error}")
        
        return EnhancementResult(
            # Minimal enhancement data
            detected_topics={},
            primary_topic=None,
            topic_confidence=0.0,
            solution_quality_score=1.0,
            has_success_markers=False,
            has_quality_indicators=False,
            previous_message_id=None,
            next_message_id=None,
            message_sequence_position=0,
            user_feedback_sentiment=None,
            is_validated_solution=False,
            is_refuted_attempt=False,
            validation_strength=0.0,
            outcome_certainty=0.0,
            is_solution_attempt=False,
            is_feedback_to_solution=False,
            related_solution_id=None,
            feedback_message_id=None,
            solution_category=None,
            troubleshooting_context_score=1.0,
            realtime_learning_boost=1.0,
            enhancement_coverage=0.0,
            processing_source=context.source,
            processing_time_ms=0.0
        )
    
    def create_enhanced_entry(self, 
                            content: str, 
                            base_metadata: Dict, 
                            context: ProcessingContext = None) -> EnhancedConversationEntry:
        """
        Create a complete EnhancedConversationEntry with all enhancement processing applied.
        
        This is the main public interface for converting any conversation data
        into a fully enhanced entry suitable for database storage.
        
        Args:
            content: Raw conversation content
            base_metadata: Basic metadata (id, type, timestamp, project, etc.)
            context: Processing context for adjacency and session information
            
        Returns:
            Complete EnhancedConversationEntry with all enhancement components
        """
        # Apply unified enhancement processing
        enhancement_result = self.process_single_entry(content, base_metadata, context)
        
        # Create enhanced conversation entry
        enhanced_entry = EnhancedConversationEntry(
            # Base fields from metadata
            id=base_metadata['id'],
            content=content,
            type=base_metadata['type'],
            project_path=base_metadata['project_path'],
            project_name=base_metadata['project_name'],
            timestamp=base_metadata['timestamp'],
            timestamp_unix=base_metadata.get('timestamp_unix'),
            session_id=base_metadata.get('session_id'),
            file_name=base_metadata['file_name'],
            has_code=base_metadata.get('has_code', False),
            tools_used=base_metadata.get('tools_used', []),
            content_length=len(content),
            
            # Enhanced fields from processing result
            detected_topics=enhancement_result.detected_topics,
            primary_topic=enhancement_result.primary_topic,
            topic_confidence=enhancement_result.topic_confidence,
            solution_quality_score=enhancement_result.solution_quality_score,
            has_success_markers=enhancement_result.has_success_markers,
            has_quality_indicators=enhancement_result.has_quality_indicators,
            previous_message_id=enhancement_result.previous_message_id,
            next_message_id=enhancement_result.next_message_id,
            message_sequence_position=enhancement_result.message_sequence_position,
            user_feedback_sentiment=enhancement_result.user_feedback_sentiment,
            is_validated_solution=enhancement_result.is_validated_solution,
            is_refuted_attempt=enhancement_result.is_refuted_attempt,
            validation_strength=enhancement_result.validation_strength,
            outcome_certainty=enhancement_result.outcome_certainty,
            is_solution_attempt=enhancement_result.is_solution_attempt,
            is_feedback_to_solution=enhancement_result.is_feedback_to_solution,
            related_solution_id=enhancement_result.related_solution_id,
            feedback_message_id=enhancement_result.feedback_message_id,
            solution_category=enhancement_result.solution_category
        )
        
        # Add dynamic attributes for advanced features
        enhanced_entry.troubleshooting_context_score = enhancement_result.troubleshooting_context_score
        enhanced_entry.realtime_learning_boost = enhancement_result.realtime_learning_boost
        enhanced_entry.enhancement_coverage = enhancement_result.enhancement_coverage
        enhanced_entry.processing_source = enhancement_result.processing_source
        
        return enhanced_entry
    
    def get_processor_stats(self) -> Dict[str, Any]:
        """Get comprehensive processor statistics."""
        return {
            **self.stats,
            'components_available': len(self.component_validators),
            'components_enabled': len([name for name, validator in self.component_validators.items() 
                                     if validator is not None])
        }
    
    # Component validators (for testing and validation)
    def _validate_topic_detection(self, result: Dict) -> bool:
        """Validate topic detection results."""
        return (isinstance(result.get('detected_topics'), dict) and
                isinstance(result.get('topic_confidence'), (int, float)))
    
    def _validate_quality_scoring(self, result: Dict) -> bool:
        """Validate quality scoring results."""
        return (isinstance(result.get('solution_quality_score'), (int, float)) and
                0.1 <= result.get('solution_quality_score', 0) <= 3.0)
    
    def _validate_sentiment_analysis(self, result: Dict) -> bool:
        """Validate sentiment analysis results."""
        valid_sentiments = ['positive', 'negative', 'partial', 'neutral', None]
        return result.get('user_feedback_sentiment') in valid_sentiments
    
    def _validate_adjacency_tracking(self, result: Dict) -> bool:
        """Validate adjacency tracking results."""
        return isinstance(result.get('message_sequence_position'), int)
    
    def _validate_troubleshooting_context(self, result: Dict) -> bool:
        """Validate troubleshooting context results."""
        return isinstance(result.get('context_score'), (int, float))
    
    def _validate_realtime_learning(self, result: Dict) -> bool:
        """Validate real-time learning results."""
        return isinstance(result.get('learning_boost'), (int, float))
    
    def _validate_validation_patterns(self, result: Dict) -> bool:
        """Validate validation pattern results."""
        return (isinstance(result.get('is_validated_solution'), bool) and
                isinstance(result.get('is_refuted_attempt'), bool))


# Utility functions for data normalization

def normalize_hook_data(hook_input: Dict, session_id: str, cwd: str) -> Dict:
    """
    Normalize hook input data to standard format for processing.
    
    Args:
        hook_input: Raw hook input data
        session_id: Session identifier
        cwd: Current working directory
        
    Returns:
        Normalized metadata dictionary
    """
    return {
        'id': f"{session_id}_{hook_input.get('type', 'unknown')}_{int(datetime.now().timestamp() * 1000)}",
        'type': hook_input.get('type', 'unknown'),
        'project_path': cwd,
        'project_name': Path(cwd).name,
        'timestamp': hook_input.get('timestamp', datetime.now().isoformat()),
        'timestamp_unix': datetime.now().timestamp(),
        'session_id': session_id,
        'file_name': f"{session_id}.jsonl",
        'has_code': detect_code_presence(hook_input.get('content', '')),
        'tools_used': extract_tools_used(hook_input.get('content', ''))
    }


def normalize_jsonl_data(jsonl_entry: Dict, file_path: Path, line_num: int) -> Dict:
    """
    Normalize JSONL entry data to standard format for processing.
    
    Args:
        jsonl_entry: Raw JSONL entry data
        file_path: Path to source JSONL file
        line_num: Line number in file
        
    Returns:
        Normalized metadata dictionary
    """
    # Extract session ID from file path or entry
    session_id = extract_session_id_from_path(file_path)
    
    return {
        'id': f"{session_id}_{jsonl_entry.get('type', 'unknown')}_{line_num}",
        'type': jsonl_entry.get('type', 'unknown'),
        'project_path': str(file_path.parent.parent),  # Go up from projects/session.jsonl
        'project_name': file_path.parent.parent.name,
        'timestamp': jsonl_entry.get('timestamp', ''),
        'timestamp_unix': parse_timestamp_to_unix(jsonl_entry.get('timestamp', '')),
        'session_id': session_id,
        'file_name': file_path.name,
        'has_code': detect_code_presence(extract_content_from_jsonl(jsonl_entry)),
        'tools_used': extract_tools_from_jsonl(jsonl_entry)
    }


# Helper functions

def detect_code_presence(content: str) -> bool:
    """Detect if content contains code.""" 
    code_indicators = ['```', 'function', 'class ', 'def ', 'import ', 'npm ', 'git ']
    return any(indicator in content.lower() for indicator in code_indicators)


def extract_tools_used(content: str) -> List[str]:
    """Extract tools used from content."""
    tools = []
    tool_patterns = [
        r'<function_calls>.*?<invoke name="([^"]+)"',
        r'Using tool:\s*([^\s\n]+)',
    ]
    
    for pattern in tool_patterns:
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        tools.extend(matches)
    
    return list(set(tools))  # Remove duplicates


def extract_session_id_from_path(file_path: Path) -> str:
    """Extract session ID from JSONL file path."""
    return file_path.stem  # File name without extension


def extract_content_from_jsonl(jsonl_entry: Dict) -> str:
    """Extract content from JSONL entry message."""
    message = jsonl_entry.get('message', {})
    content = message.get('content', '')
    
    # Handle different content formats
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    text_parts.append(item.get('text', ''))
                elif 'content' in item:
                    text_parts.append(str(item['content']))
            elif isinstance(item, str):
                text_parts.append(item)
        return ' '.join(text_parts)
    
    return str(content) if content else ''


def extract_tools_from_jsonl(jsonl_entry: Dict) -> List[str]:
    """Extract tools used from JSONL entry."""
    content = extract_content_from_jsonl(jsonl_entry)
    return extract_tools_used(content)


def parse_timestamp_to_unix(timestamp_str: str) -> Optional[float]:
    """Parse timestamp string to Unix timestamp."""
    if not timestamp_str:
        return None
        
    try:
        # Handle ISO format timestamps
        if 'T' in timestamp_str:
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            return dt.timestamp()
    except Exception:
        pass
    
    return None


# Main interface functions for easy integration

def process_hook_entry(hook_input: Dict, session_id: str, cwd: str, 
                      previous_messages: List[Dict] = None) -> EnhancedConversationEntry:
    """
    Process hook entry with unified enhancement pipeline.
    
    This is the main interface for hooks to use for consistent processing.
    """
    processor = UnifiedEnhancementProcessor()
    
    # Extract content and normalize metadata
    content = hook_input.get('content', '')
    metadata = normalize_hook_data(hook_input, session_id, cwd)
    
    # Create processing context
    context = ProcessingContext(
        source="hook",
        session_messages=previous_messages or [],
        real_time_processing=True,
        message_position=len(previous_messages) if previous_messages else 0
    )
    
    # Add adjacency context if available
    if previous_messages:
        context.previous_message = previous_messages[-1] if previous_messages else None
    
    return processor.create_enhanced_entry(content, metadata, context)


def process_jsonl_entry(jsonl_entry: Dict, file_path: Path, line_num: int,
                       all_messages: List[Dict] = None, message_index: int = 0) -> EnhancedConversationEntry:
    """
    Process JSONL entry with unified enhancement pipeline.
    
    This is the main interface for batch processing to use for consistent processing.
    """
    processor = UnifiedEnhancementProcessor()
    
    # Extract content and normalize metadata
    content = extract_content_from_jsonl(jsonl_entry)
    metadata = normalize_jsonl_data(jsonl_entry, file_path, line_num)
    
    # Create processing context with full conversation data
    context = ProcessingContext(
        source="full_sync",
        full_conversation=all_messages or [],
        real_time_processing=False,
        message_position=message_index
    )
    
    # Add adjacency context if available
    if all_messages and message_index < len(all_messages):
        if message_index > 0:
            context.previous_message = all_messages[message_index - 1]
        if message_index < len(all_messages) - 1:
            context.next_message = all_messages[message_index + 1]
    
    return processor.create_enhanced_entry(content, metadata, context)


if __name__ == "__main__":
    # Simple test/demo when run directly
    print("🔧 UnifiedEnhancementProcessor - Testing Mode")
    
    processor = UnifiedEnhancementProcessor()
    
    # Test with sample data
    test_content = "I'm having a debug error with my authentication system. Can you help me fix this issue?"
    test_metadata = {
        'id': 'test_001',
        'type': 'user',
        'project_path': '/test/project',
        'project_name': 'test-project',
        'timestamp': datetime.now().isoformat(),
        'file_name': 'test.jsonl'
    }
    
    test_context = ProcessingContext(source="test")
    
    result = processor.process_single_entry(test_content, test_metadata, test_context)
    
    print("✅ Test processing complete:")
    print(f"   Enhancement coverage: {result.enhancement_coverage:.1f}%")
    print(f"   Primary topic: {result.primary_topic}")
    print(f"   Processing time: {result.processing_time_ms:.1f}ms")
    print(f"   Troubleshooting detected: {result.troubleshooting_context_score > 1.0}")
    
    stats = processor.get_processor_stats()
    print(f"📊 Processor stats: {stats}")