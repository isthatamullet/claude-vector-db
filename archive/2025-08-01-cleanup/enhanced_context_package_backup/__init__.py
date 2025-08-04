"""
Enhanced Context Awareness Module for Claude Code Vector Database

This module provides advanced context awareness capabilities including:
- Topic detection and classification
- Solution quality assessment  
- Adjacency analysis and conversation flow tracking
- User feedback sentiment analysis and validation learning
- Multi-factor relevance scoring

All components are designed for high performance (<20ms per conversation processing)
while maintaining backward compatibility with existing vector database functionality.

Author: Claude Code Vector Database Enhancement System
Version: 1.0.0
"""

from .topic_detector import (
    detect_conversation_topics,
    TOPIC_PATTERNS,
    apply_topic_boost
)

from .quality_scorer import (
    calculate_solution_quality_score,
    SUCCESS_MARKERS,
    QUALITY_INDICATORS,
    detect_success_markers,
    detect_quality_indicators
)

from .adjacency_analyzer import (
    analyze_conversation_adjacency,
    is_solution_attempt,
    classify_solution_type,
    build_context_chain
)

from .feedback_learner import (
    analyze_feedback_sentiment,
    apply_feedback_to_solution,
    POSITIVE_FEEDBACK_PATTERNS,
    NEGATIVE_FEEDBACK_PATTERNS,
    PARTIAL_SUCCESS_PATTERNS
)

from .boosting_engine import (
    calculate_enhanced_relevance_score,
    calculate_troubleshooting_boost,
    calculate_recency_boost,
    combine_all_boosts,
    get_boost_explanation
)

# Live validation learning functions available separately from enhanced_context.py
# Import directly using: from enhanced_context import get_live_validation_learner

__all__ = [
    # Topic detection
    'detect_conversation_topics',
    'TOPIC_PATTERNS', 
    'apply_topic_boost',
    
    # Quality scoring
    'calculate_solution_quality_score',
    'SUCCESS_MARKERS',
    'QUALITY_INDICATORS',
    'detect_success_markers',
    'detect_quality_indicators',
    
    # Adjacency analysis
    'analyze_conversation_adjacency',
    'is_solution_attempt',
    'classify_solution_type',
    'build_context_chain',
    
    # Feedback learning
    'analyze_feedback_sentiment',
    'apply_feedback_to_solution',
    'POSITIVE_FEEDBACK_PATTERNS',
    'NEGATIVE_FEEDBACK_PATTERNS',
    'PARTIAL_SUCCESS_PATTERNS',
    
    # Boosting engine
    'calculate_enhanced_relevance_score',
    'calculate_troubleshooting_boost',
    'calculate_recency_boost',
    'combine_all_boosts',
    'get_boost_explanation'
]

# Version and metadata
__version__ = "1.0.0"
__author__ = "Claude Code Vector Database Enhancement System"
__description__ = "Advanced context awareness and feedback learning for conversation search"