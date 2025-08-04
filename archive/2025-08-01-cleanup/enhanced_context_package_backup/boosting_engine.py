"""
Multi-Factor Relevance Boosting Engine

Combines all enhancement factors into comprehensive relevance scoring:
- Base semantic similarity
- Project relevance boosting  
- Topic-aware boosting
- Solution quality scoring
- Validation-based learning
- Troubleshooting context awareness
- Recency and time-based factors

Maintains sub-500ms search performance while providing sophisticated relevance ranking.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import logging

from .topic_detector import detect_conversation_topics, apply_topic_boost
from .quality_scorer import calculate_solution_quality_score
from .feedback_learner import calculate_validation_boost

logger = logging.getLogger(__name__)

# Boost factor limits to prevent over-weighting
MAX_TOPIC_BOOST = 2.5
MAX_QUALITY_BOOST = 3.0
MAX_VALIDATION_BOOST = 2.5
MAX_TROUBLESHOOTING_BOOST = 2.5
MAX_RECENCY_BOOST = 1.8
MAX_TOTAL_BOOST = 8.0  # Absolute maximum combined boost

# Troubleshooting context patterns
TROUBLESHOOTING_PATTERNS = [
    # Error indicators
    "error", "exception", "failed", "failing", "broken", "not working",
    "issue", "problem", "bug", "crash", "hang", "timeout", "stack trace",
    
    # Debugging processes
    "debug", "investigate", "diagnose", "trace", "inspect", "analyze",
    "troubleshoot", "examine", "check", "verify", "test", "console",
    
    # Resolution attempts
    "tried", "attempted", "testing", "checking", "investigating",
    "found the issue", "identified the problem", "root cause",
    "solution found", "fixed by", "resolved with", "workaround"
]

# Performance monitoring patterns
PERFORMANCE_PATTERNS = [
    "slow", "fast", "performance", "speed", "latency", "memory", "cpu",
    "bottleneck", "optimize", "optimization", "cache", "efficient",
    "benchmark", "profiling", "load time", "response time"
]


def calculate_enhanced_relevance_score(
    base_similarity: float,
    project_boost: float,
    content: str,
    metadata: Dict,
    query_context: Dict
) -> Dict[str, Any]:
    """
    Calculate comprehensive relevance score with all enhancement factors.
    
    Combines multiple boosting factors while maintaining performance and
    preventing over-weighting through factor capping.
    
    Args:
        base_similarity: Base vector similarity score (0.0-1.0)
        project_boost: Project relevance boost factor
        content: Message content for analysis
        metadata: Message metadata including tools, timestamps, etc.
        query_context: Query parameters and user preferences
        
    Returns:
        Dictionary with detailed scoring breakdown and final score
    """
    if not content or base_similarity <= 0:
        return {
            'final_score': 0.0,
            'base_similarity': base_similarity,
            'project_boost': project_boost,
            'topic_boost': 1.0,
            'quality_boost': 1.0,
            'validation_boost': 1.0,
            'troubleshooting_boost': 1.0,
            'recency_boost': 1.0,
            'preference_multiplier': 1.0,
            'detected_topics': {}
        }
    
    # Topic detection and boosting
    detected_topics = detect_conversation_topics(content)
    topic_boost = 1.0
    if query_context.get('topic_focus') and detected_topics:
        topic_boost = apply_topic_boost(1.0, detected_topics, query_context['topic_focus'])
        topic_boost = min(topic_boost, MAX_TOPIC_BOOST)
    
    # Solution quality boosting
    quality_boost = calculate_solution_quality_score(content, metadata)
    quality_boost = min(quality_boost, MAX_QUALITY_BOOST)
    
    # Validation-based boosting (from feedback learning)
    validation_boost = calculate_validation_boost(metadata, query_context.get('validation_preference', 'neutral'))
    validation_boost = min(validation_boost, MAX_VALIDATION_BOOST)
    
    # Troubleshooting context boosting
    troubleshooting_boost = calculate_troubleshooting_boost(content, query_context)
    troubleshooting_boost = min(troubleshooting_boost, MAX_TROUBLESHOOTING_BOOST)
    
    # Recency boosting
    recency_boost = calculate_recency_boost(metadata.get('timestamp'), query_context)
    recency_boost = min(recency_boost, MAX_RECENCY_BOOST)
    
    # User preference multipliers
    preference_multiplier = calculate_preference_multiplier(
        metadata, query_context, quality_boost, validation_boost
    )
    
    # Calculate final score with boost capping
    individual_boosts = (
        project_boost *
        topic_boost *
        quality_boost *
        validation_boost *
        troubleshooting_boost *
        recency_boost
    )
    
    # Apply absolute maximum boost limit
    capped_boosts = min(individual_boosts, MAX_TOTAL_BOOST)
    
    final_score = (
        base_similarity *
        capped_boosts *
        preference_multiplier
    )
    
    return {
        'final_score': final_score,
        'base_similarity': base_similarity,
        'project_boost': project_boost,
        'topic_boost': topic_boost,
        'quality_boost': quality_boost,
        'validation_boost': validation_boost,
        'troubleshooting_boost': troubleshooting_boost,
        'recency_boost': recency_boost,
        'preference_multiplier': preference_multiplier,
        'detected_topics': detected_topics,
        'boost_capping_applied': individual_boosts > MAX_TOTAL_BOOST
    }


def calculate_troubleshooting_boost(content: str, query_context: Dict) -> float:
    """
    Apply boosting for troubleshooting and problem-solving contexts.
    
    Args:
        content: Message content to analyze
        query_context: Query context including troubleshooting_mode flag
        
    Returns:
        Troubleshooting boost factor (1.0 to MAX_TROUBLESHOOTING_BOOST)
    """
    if not query_context.get('troubleshooting_mode', False):
        return 1.0
    
    content_lower = content.lower()
    troubleshooting_score = 1.0
    
    # Count troubleshooting pattern matches
    pattern_matches = sum(1 for pattern in TROUBLESHOOTING_PATTERNS if pattern in content_lower)
    
    # Base boost for pattern matches
    troubleshooting_score += pattern_matches * 0.15
    
    # Additional boost for error-specific content
    error_indicators = ["error", "exception", "failed", "broken", "bug"]
    error_matches = sum(1 for indicator in error_indicators if indicator in content_lower)
    troubleshooting_score += error_matches * 0.2
    
    # Boost for resolution indicators
    resolution_indicators = ["fixed", "solved", "resolved", "working", "solution"]
    resolution_matches = sum(1 for indicator in resolution_indicators if indicator in content_lower)
    troubleshooting_score += resolution_matches * 0.25
    
    return min(troubleshooting_score, MAX_TROUBLESHOOTING_BOOST)


def calculate_recency_boost(timestamp: Optional[str], query_context: Dict) -> float:
    """
    Calculate recency-based boosting for time-sensitive queries.
    
    Args:
        timestamp: Message timestamp (ISO format)
        query_context: Query context including recency preferences
        
    Returns:
        Recency boost factor (0.5 to MAX_RECENCY_BOOST)
    """
    if not timestamp or not query_context.get('prefer_recent', False):
        return 1.0
    
    try:
        # Parse timestamp
        if 'T' in timestamp:
            msg_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        else:
            msg_time = datetime.fromisoformat(timestamp)
        
        now = datetime.now(msg_time.tzinfo) if msg_time.tzinfo else datetime.now()
        time_diff = now - msg_time
        
        # Recency boost calculation
        if time_diff <= timedelta(hours=1):
            return 1.8  # Very recent
        elif time_diff <= timedelta(hours=6):
            return 1.6  # Recent
        elif time_diff <= timedelta(days=1):
            return 1.4  # Today
        elif time_diff <= timedelta(days=3):
            return 1.2  # This week
        elif time_diff <= timedelta(days=7):
            return 1.1  # Recent week
        elif time_diff <= timedelta(days=30):
            return 1.0  # Recent month
        else:
            return 0.8  # Older content
            
    except (ValueError, TypeError):
        return 1.0  # Default if timestamp parsing fails


def calculate_preference_multiplier(
    metadata: Dict,
    query_context: Dict,
    quality_boost: float,
    validation_boost: float
) -> float:
    """
    Calculate user preference multipliers based on query context.
    
    Args:
        metadata: Message metadata
        query_context: Query preferences and filters
        quality_boost: Calculated quality boost
        validation_boost: Calculated validation boost
        
    Returns:
        Preference multiplier factor
    """
    multiplier = 1.0
    
    # Prefer solutions with high quality
    if query_context.get('prefer_solutions', False) and quality_boost > 1.5:
        multiplier *= 1.3
    
    # Prefer validated solutions
    if query_context.get('prefer_validated', False) and validation_boost > 1.2:
        multiplier *= 1.4
    
    # Prefer code-containing solutions
    if query_context.get('prefer_code', False) and metadata.get('has_code', False):
        multiplier *= 1.2
    
    # Prefer comprehensive solutions (longer content)
    if query_context.get('prefer_detailed', False):
        content_length = metadata.get('content_length', 0)
        if content_length > 500:
            multiplier *= 1.1
        if content_length > 1000:
            multiplier *= 1.1
    
    # Tool usage preference
    if query_context.get('prefer_implementation', False):
        tools_used = metadata.get('tools_used', [])
        implementation_tools = {'Edit', 'Write', 'MultiEdit', 'Bash'}
        if any(tool in implementation_tools for tool in tools_used):
            multiplier *= 1.25
    
    return min(multiplier, 2.0)  # Cap at 2x multiplier


def combine_all_boosts(
    base_similarity: float,
    boost_factors: Dict[str, float]
) -> float:
    """
    Combine all boost factors with intelligent capping.
    
    Args:
        base_similarity: Base similarity score
        boost_factors: Dictionary of individual boost factors
        
    Returns:
        Final combined score with capping applied
    """
    # Extract boost factors
    project_boost = boost_factors.get('project_boost', 1.0)
    topic_boost = boost_factors.get('topic_boost', 1.0)
    quality_boost = boost_factors.get('quality_boost', 1.0)
    validation_boost = boost_factors.get('validation_boost', 1.0)
    troubleshooting_boost = boost_factors.get('troubleshooting_boost', 1.0)
    recency_boost = boost_factors.get('recency_boost', 1.0)
    preference_multiplier = boost_factors.get('preference_multiplier', 1.0)
    
    # Calculate combined boost
    combined_boost = (
        project_boost *
        topic_boost *
        quality_boost *
        validation_boost *
        troubleshooting_boost *
        recency_boost
    )
    
    # Apply intelligent capping
    capped_boost = min(combined_boost, MAX_TOTAL_BOOST)
    
    # Calculate final score
    final_score = base_similarity * capped_boost * preference_multiplier
    
    return final_score


def analyze_boost_distribution(entries: List[Dict]) -> Dict[str, Any]:
    """
    Analyze boost factor distribution across a set of entries.
    
    Args:
        entries: List of entries with boost analysis
        
    Returns:
        Statistical analysis of boost factors
    """
    if not entries:
        return {}
    
    boost_stats: Dict[str, List[float]] = {
        'topic_boost': [],
        'quality_boost': [],
        'validation_boost': [],
        'troubleshooting_boost': [],
        'recency_boost': [],
        'final_score': []
    }
    
    for entry in entries:
        boost_data = entry.get('boost_analysis', {})
        for factor in boost_stats.keys():
            if factor in boost_data:
                boost_stats[factor].append(boost_data[factor])
    
    # Calculate statistics
    analysis = {}
    for factor, values in boost_stats.items():
        if values:
            analysis[factor] = {
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'count': len(values),
                'above_neutral': sum(1 for v in values if v > 1.0),
                'below_neutral': sum(1 for v in values if v < 1.0)
            }
    
    return analysis


def optimize_boost_parameters(
    test_entries: List[Dict],
    target_performance: Dict[str, float]
) -> Dict[str, float]:
    """
    Optimize boost parameters based on test data and performance targets.
    
    Args:
        test_entries: Test entries with known relevance
        target_performance: Performance targets (precision, recall, etc.)
        
    Returns:
        Optimized boost parameters
    """
    # This would implement parameter optimization logic
    # For now, return current parameters
    return {
        'max_topic_boost': MAX_TOPIC_BOOST,
        'max_quality_boost': MAX_QUALITY_BOOST,
        'max_validation_boost': MAX_VALIDATION_BOOST,
        'max_troubleshooting_boost': MAX_TROUBLESHOOTING_BOOST,
        'max_recency_boost': MAX_RECENCY_BOOST,
        'max_total_boost': MAX_TOTAL_BOOST
    }


def get_boost_explanation(boost_analysis: Dict[str, float]) -> List[str]:
    """
    Generate human-readable explanations for boost factors.
    
    Args:
        boost_analysis: Boost analysis results
        
    Returns:
        List of explanation strings
    """
    explanations = []
    
    topic_boost = boost_analysis.get('topic_boost', 1.0)
    if topic_boost > 1.2:
        explanations.append(f"Topic relevance boost: {topic_boost:.2f}x")
    
    quality_boost = boost_analysis.get('quality_boost', 1.0)
    if quality_boost > 1.3:
        explanations.append(f"Solution quality boost: {quality_boost:.2f}x")
    
    validation_boost = boost_analysis.get('validation_boost', 1.0)
    if validation_boost > 1.2:
        explanations.append(f"User validation boost: {validation_boost:.2f}x")
    elif validation_boost < 0.8:
        explanations.append(f"Validation penalty: {validation_boost:.2f}x")
    
    troubleshooting_boost = boost_analysis.get('troubleshooting_boost', 1.0)
    if troubleshooting_boost > 1.2:
        explanations.append(f"Troubleshooting context boost: {troubleshooting_boost:.2f}x")
    
    recency_boost = boost_analysis.get('recency_boost', 1.0)
    if recency_boost > 1.2:
        explanations.append(f"Recency boost: {recency_boost:.2f}x")
    elif recency_boost < 0.9:
        explanations.append(f"Age penalty: {recency_boost:.2f}x")
    
    if boost_analysis.get('boost_capping_applied', False):
        explanations.append("Boost capping applied to prevent over-weighting")
    
    return explanations


def benchmark_boosting_performance(
    test_cases: List[Dict],
    iterations: int = 100
) -> Dict[str, float]:
    """
    Benchmark boosting engine performance.
    
    Args:
        test_cases: Test cases with content, metadata, and query context
        iterations: Number of iterations per test case
        
    Returns:
        Performance metrics
    """
    import time
    
    total_times = []
    
    for test_case in test_cases:
        case_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            
            calculate_enhanced_relevance_score(
                test_case['base_similarity'],
                test_case['project_boost'],
                test_case['content'],
                test_case['metadata'],
                test_case['query_context']
            )
            
            end_time = time.perf_counter()
            case_times.append((end_time - start_time) * 1000)
        
        total_times.extend(case_times)
    
    return {
        'avg_time_ms': sum(total_times) / len(total_times),
        'min_time_ms': min(total_times),
        'max_time_ms': max(total_times),
        'total_cases': len(test_cases),
        'target_met': sum(total_times) / len(total_times) < 50.0,  # <50ms target for boosting
        'performance_rating': 'excellent' if sum(total_times) / len(total_times) < 20.0 else 
                             'good' if sum(total_times) / len(total_times) < 50.0 else 'needs_optimization'
    }