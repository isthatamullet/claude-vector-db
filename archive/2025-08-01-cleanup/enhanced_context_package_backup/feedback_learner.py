"""
User Feedback Learning Engine

Analyzes user feedback sentiment to learn from conversation outcomes.
Tracks solution validation and refutation to improve future recommendations.

Key Features:
- Multi-tier feedback sentiment analysis
- Solution validation strength scoring
- Outcome certainty assessment
- Learning from user feedback patterns
- Boost/penalty application for solutions
"""

import re
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Positive feedback patterns (hierarchical by strength)
POSITIVE_FEEDBACK_PATTERNS = {
    "strong_positive": [
        "perfect", "exactly", "brilliant", "awesome", "fantastic", "excellent",
        "works perfectly", "fixed it", "that worked", "problem solved", 
        "exactly what i needed", "spot on", "flawless", "incredible",
        "you nailed it", "perfect solution", "amazing work"
    ],
    "moderate_positive": [
        "great", "good", "works", "working", "fixed", "thanks", "helpful",
        "solved", "success", "✅", "correct", "right", "yes", "good job",
        "that helps", "much better", "resolved", "successful"
    ],
    "subtle_positive": [
        "better", "improved", "progress", "closer", "helped", "useful",
        "getting there", "on the right track", "step forward", "partial fix",
        "some improvement", "heading in right direction"
    ]
}

# Negative feedback patterns (hierarchical by strength)
NEGATIVE_FEEDBACK_PATTERNS = {
    "strong_negative": [
        "completely broken", "made it worse", "totally wrong", "disaster",
        "doesn't work at all", "same exact error", "even more broken",
        "completely failed", "waste of time", "no improvement", "worse than before"
    ],
    "moderate_negative": [
        "still not working", "didn't work", "still broken", "not fixed",
        "same error", "still happening", "no change", "still failing",
        "not right", "incorrect", "wrong approach", "doesn't help"
    ],
    "subtle_negative": [
        "not quite", "almost", "close but", "still some issues",
        "partially broken", "sort of works", "mostly wrong", 
        "needs more work", "not there yet", "some problems remain"
    ]
}

# Partial success patterns (mixed feedback)
PARTIAL_SUCCESS_PATTERNS = [
    "partially working", "some progress", "better but", "almost there",
    "fixed one issue but", "working sometimes", "intermittent", 
    "works for some cases", "half working", "mixed results",
    "progress made but", "step in right direction but", "improvement but"
]

# Neutral/ambiguous patterns
NEUTRAL_PATTERNS = [
    "i see", "okay", "understood", "got it", "makes sense",
    "i'll try", "let me check", "interesting", "noted", "hmm"
]

# Confidence indicators (strengthen sentiment analysis)
CONFIDENCE_INDICATORS = {
    "high_confidence": [
        "definitely", "absolutely", "certainly", "clearly", "obviously",
        "without a doubt", "for sure", "completely", "totally", "entirely"
    ],
    "medium_confidence": [
        "probably", "likely", "seems", "appears", "looks like",
        "i think", "believe", "pretty sure", "fairly certain"
    ],
    "low_confidence": [
        "maybe", "perhaps", "might", "could be", "not sure",
        "unsure", "hard to tell", "difficult to say", "unclear"
    ]
}

# Pre-compiled patterns for performance
_COMPILED_FEEDBACK_PATTERNS: Optional[Dict[str, Dict[str, List[re.Pattern]]]] = None

def _get_compiled_feedback_patterns() -> Dict[str, Dict[str, List[re.Pattern]]]:
    """Get pre-compiled feedback analysis patterns"""
    global _COMPILED_FEEDBACK_PATTERNS
    
    if _COMPILED_FEEDBACK_PATTERNS is None:
        _COMPILED_FEEDBACK_PATTERNS = {}
        
        pattern_groups = {
            'positive': POSITIVE_FEEDBACK_PATTERNS,
            'negative': NEGATIVE_FEEDBACK_PATTERNS,
            'partial': {'partial_success': PARTIAL_SUCCESS_PATTERNS},
            'neutral': {'neutral': NEUTRAL_PATTERNS},
            'confidence': CONFIDENCE_INDICATORS
        }
        
        for group_name, pattern_dict in pattern_groups.items():
            _COMPILED_FEEDBACK_PATTERNS[group_name] = {}
            for subgroup, patterns in pattern_dict.items():
                _COMPILED_FEEDBACK_PATTERNS[group_name][subgroup] = [
                    re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
                    for pattern in patterns
                ]
    
    return _COMPILED_FEEDBACK_PATTERNS


def analyze_feedback_sentiment(feedback_content: str) -> Dict[str, Any]:
    """
    Analyze user feedback to determine sentiment and strength.
    
    Uses hierarchical pattern matching with confidence weighting to provide
    accurate sentiment analysis for solution validation learning.
    
    Args:
        feedback_content: User feedback text to analyze
        
    Returns:
        Comprehensive sentiment analysis dictionary
    """
    if not feedback_content or len(feedback_content.strip()) < 3:
        return {
            'sentiment': 'neutral',
            'strength': 0.0,
            'confidence': 0.0,
            'certainty': 0.0,
            'detailed_scores': {}
        }
    
    content_lower = feedback_content.lower()
    compiled_patterns = _get_compiled_feedback_patterns()
    
    # Calculate positive sentiment scores
    positive_scores = {}
    total_positive = 0
    for strength, patterns in compiled_patterns['positive'].items():
        score = sum(len(pattern.findall(content_lower)) for pattern in patterns)
        positive_scores[strength] = score
        
        # Weight by strength level
        if strength == "strong_positive":
            total_positive += score * 3
        elif strength == "moderate_positive":
            total_positive += score * 2
        else:  # subtle_positive
            total_positive += score * 1
    
    # Calculate negative sentiment scores
    negative_scores = {}
    total_negative = 0
    for strength, patterns in compiled_patterns['negative'].items():
        score = sum(len(pattern.findall(content_lower)) for pattern in patterns)
        negative_scores[strength] = score
        
        # Weight by strength level
        if strength == "strong_negative":
            total_negative += score * 3
        elif strength == "moderate_negative":
            total_negative += score * 2
        else:  # subtle_negative
            total_negative += score * 1
    
    # Calculate partial success score
    partial_patterns = compiled_patterns['partial']['partial_success']
    partial_score = sum(len(pattern.findall(content_lower)) for pattern in partial_patterns)
    
    # Calculate neutral score
    neutral_patterns = compiled_patterns['neutral']['neutral']
    neutral_score = sum(len(pattern.findall(content_lower)) for pattern in neutral_patterns)
    
    # Determine overall sentiment
    sentiment = 'neutral'
    strength = 0.0
    
    if total_positive > total_negative and total_positive > partial_score:
        sentiment = 'positive'
        strength = min(total_positive / 5.0, 1.0)  # Normalize to 0-1
    elif total_negative > total_positive and total_negative > partial_score:
        sentiment = 'negative'  
        strength = min(total_negative / 5.0, 1.0)  # Normalize to 0-1
    elif partial_score > 0 and partial_score >= max(total_positive, total_negative):
        sentiment = 'partial'
        strength = min(partial_score / 3.0, 1.0)  # Normalize to 0-1
    elif neutral_score > 0:
        sentiment = 'neutral'
        strength = 0.0
    
    # Calculate confidence based on confidence indicators
    confidence_score = 0.0
    for conf_level, patterns in compiled_patterns['confidence'].items():
        matches = sum(len(pattern.findall(content_lower)) for pattern in patterns)
        if conf_level == "high_confidence":
            confidence_score += matches * 0.4
        elif conf_level == "medium_confidence":
            confidence_score += matches * 0.2
        else:  # low_confidence
            confidence_score -= matches * 0.2
    
    confidence = max(0.0, min(confidence_score + 0.5, 1.0))  # Base 0.5 + adjustments
    
    # Calculate certainty based on pattern strength and clarity
    certainty = 0.0
    if sentiment != 'neutral':
        # Higher certainty for clearer, stronger patterns
        dominant_score = max(total_positive, total_negative, partial_score)
        total_patterns = total_positive + total_negative + partial_score + neutral_score
        if total_patterns > 0:
            certainty = (dominant_score / total_patterns) * confidence
    
    return {
        'sentiment': sentiment,
        'strength': strength,
        'confidence': confidence,
        'certainty': certainty,
        'detailed_scores': {
            'positive_breakdown': positive_scores,
            'negative_breakdown': negative_scores,
            'partial_score': partial_score,
            'neutral_score': neutral_score,
            'total_positive': total_positive,
            'total_negative': total_negative
        }
    }


def apply_feedback_to_solution(solution_entry: Dict, feedback_analysis: Dict) -> Dict:
    """
    Apply user feedback analysis to solution entry for learning.
    
    Updates solution confidence, validation status, and outcome tracking
    based on user feedback sentiment analysis.
    
    Args:
        solution_entry: Solution message entry to update
        feedback_analysis: Result from analyze_feedback_sentiment()
        
    Returns:
        Updated solution entry with feedback learning applied
    """
    sentiment = feedback_analysis['sentiment']
    strength = feedback_analysis['strength']
    confidence = feedback_analysis['confidence']
    certainty = feedback_analysis['certainty']
    
    # Create updated entry
    updated_entry = solution_entry.copy()
    
    if sentiment == "positive":
        updated_entry['is_validated_solution'] = True
        updated_entry['is_refuted_attempt'] = False
        # Boost confidence: base 1.0 + strength boost (up to 2.0 total)
        updated_entry['solution_confidence'] = 1.0 + (strength * confidence)
        updated_entry['validation_strength'] = strength * confidence
        
    elif sentiment == "negative":
        updated_entry['is_validated_solution'] = False
        updated_entry['is_refuted_attempt'] = True
        # Reduce confidence: base 1.0 - penalty (down to 0.3 minimum)
        penalty = strength * confidence * 0.7
        updated_entry['solution_confidence'] = max(0.3, 1.0 - penalty)
        updated_entry['validation_strength'] = -(strength * confidence)
        
    elif sentiment == "partial":
        updated_entry['is_validated_solution'] = False
        updated_entry['is_refuted_attempt'] = False
        # Slight boost for partial success
        updated_entry['solution_confidence'] = 1.0 + (strength * confidence * 0.3)
        updated_entry['validation_strength'] = strength * confidence * 0.5
        
    else:  # neutral
        updated_entry['is_validated_solution'] = False
        updated_entry['is_refuted_attempt'] = False
        updated_entry['solution_confidence'] = 1.0  # No change
        updated_entry['validation_strength'] = 0.0
    
    # Set feedback metadata
    updated_entry['user_feedback_sentiment'] = sentiment
    updated_entry['outcome_certainty'] = certainty
    
    return updated_entry


def calculate_validation_boost(entry: Dict, preference: str = "neutral") -> float:
    """
    Calculate relevance boost based on solution validation status.
    
    Args:
        entry: Conversation entry with validation metadata
        preference: Validation preference ("validated_only", "include_failures", "neutral")
        
    Returns:
        Boost multiplier for relevance scoring
    """
    if preference == "validated_only":
        if entry.get('is_validated_solution', False):
            validation_strength = entry.get('validation_strength', 0.0)
            return 1.5 + validation_strength  # 1.5x to 2.5x boost
        elif entry.get('is_refuted_attempt', False):
            return 0.2  # Heavy penalty for refuted attempts
        else:
            return 0.8  # Slight penalty for unvalidated
    
    elif preference == "include_failures":
        if entry.get('is_refuted_attempt', False):
            return 1.3  # Boost failed attempts for learning "what not to do"
        else:
            return 1.0  # Neutral for others
    
    else:  # "neutral" - use confidence directly
        confidence = entry.get('solution_confidence', 1.0)
        return confidence


def get_learning_summary(entries: List[Dict]) -> Dict[str, Any]:
    """
    Generate learning summary from conversation entries with feedback analysis.
    
    Args:
        entries: List of conversation entries with feedback analysis
        
    Returns:
        Comprehensive learning summary
    """
    total_solutions = 0
    validated_solutions = 0
    refuted_solutions = 0
    partial_solutions = 0
    
    sentiment_distribution = {'positive': 0, 'negative': 0, 'partial': 0, 'neutral': 0}
    avg_validation_strength = 0.0
    avg_outcome_certainty = 0.0
    
    strength_sum = 0.0
    certainty_sum = 0.0
    feedback_count = 0
    
    for entry in entries:
        if entry.get('is_solution_attempt', False):
            total_solutions += 1
            
            if entry.get('is_validated_solution', False):
                validated_solutions += 1
            elif entry.get('is_refuted_attempt', False):
                refuted_solutions += 1
            elif entry.get('validation_strength', 0.0) > 0:
                partial_solutions += 1
        
        if entry.get('user_feedback_sentiment'):
            sentiment = entry['user_feedback_sentiment']
            sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1
            
            strength_sum += entry.get('validation_strength', 0.0)
            certainty_sum += entry.get('outcome_certainty', 0.0)
            feedback_count += 1
    
    # Calculate averages
    if feedback_count > 0:
        avg_validation_strength = strength_sum / feedback_count
        avg_outcome_certainty = certainty_sum / feedback_count
    
    # Calculate success metrics
    success_rate = validated_solutions / max(total_solutions, 1)
    failure_rate = refuted_solutions / max(total_solutions, 1)
    partial_rate = partial_solutions / max(total_solutions, 1)
    
    return {
        'total_solutions': total_solutions,
        'validated_solutions': validated_solutions,
        'refuted_solutions': refuted_solutions,
        'partial_solutions': partial_solutions,
        'success_rate': success_rate,
        'failure_rate': failure_rate,
        'partial_rate': partial_rate,
        'sentiment_distribution': sentiment_distribution,
        'avg_validation_strength': avg_validation_strength,
        'avg_outcome_certainty': avg_outcome_certainty,
        'learning_quality': avg_outcome_certainty * feedback_count / max(len(entries), 1)
    }


def identify_solution_patterns(entries: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Identify patterns in successful vs failed solutions.
    
    Args:
        entries: List of conversation entries with feedback analysis
        
    Returns:
        Dictionary of solution patterns by category
    """
    validated_solutions = []
    refuted_solutions = []
    partial_solutions = []
    
    for entry in entries:
        if not entry.get('is_solution_attempt', False):
            continue
            
        solution_data = {
            'id': entry.get('id'),
            'content_length': len(entry.get('content', '')),
            'solution_category': entry.get('solution_category'),
            'tools_used': entry.get('tools_used', []),
            'has_code': entry.get('has_code', False),
            'validation_strength': entry.get('validation_strength', 0.0),
            'outcome_certainty': entry.get('outcome_certainty', 0.0)
        }
        
        if entry.get('is_validated_solution', False):
            validated_solutions.append(solution_data)
        elif entry.get('is_refuted_attempt', False):
            refuted_solutions.append(solution_data)
        elif entry.get('validation_strength', 0.0) > 0:
            partial_solutions.append(solution_data)
    
    return {
        'validated_patterns': validated_solutions,
        'refuted_patterns': refuted_solutions,
        'partial_patterns': partial_solutions,
        'pattern_insights': analyze_pattern_differences(validated_solutions, refuted_solutions)
    }


def analyze_pattern_differences(validated: List[Dict], refuted: List[Dict]) -> Dict[str, Any]:
    """
    Analyze differences between validated and refuted solution patterns.
    
    Args:
        validated: List of validated solution data
        refuted: List of refuted solution data
        
    Returns:
        Pattern analysis insights
    """
    if not validated or not refuted:
        return {}
    
    # Calculate average metrics for each group
    validated_avg_length = sum(s['content_length'] for s in validated) / len(validated)
    refuted_avg_length = sum(s['content_length'] for s in refuted) / len(refuted)
    
    validated_code_rate = sum(1 for s in validated if s['has_code']) / len(validated)
    refuted_code_rate = sum(1 for s in refuted if s['has_code']) / len(refuted)
    
    # Tool usage analysis
    validated_tools = set()
    refuted_tools = set()
    for s in validated:
        validated_tools.update(s['tools_used'])
    for s in refuted:
        refuted_tools.update(s['tools_used'])
    
    return {
        'length_difference': validated_avg_length - refuted_avg_length,
        'code_rate_difference': validated_code_rate - refuted_code_rate,
        'validated_exclusive_tools': validated_tools - refuted_tools,
        'refuted_exclusive_tools': refuted_tools - validated_tools,
        'common_tools': validated_tools & refuted_tools,
        'insights': generate_pattern_insights(validated_avg_length, refuted_avg_length, 
                                            validated_code_rate, refuted_code_rate)
    }


def generate_pattern_insights(val_length: float, ref_length: float, 
                            val_code_rate: float, ref_code_rate: float) -> List[str]:
    """Generate human-readable insights from pattern analysis"""
    insights = []
    
    if val_length > ref_length * 1.2:
        insights.append("Validated solutions tend to be more detailed/comprehensive")
    elif ref_length > val_length * 1.2:
        insights.append("Refuted solutions tend to be longer (possibly over-complex)")
    
    if val_code_rate > ref_code_rate * 1.2:
        insights.append("Validated solutions more likely to include concrete code")
    elif ref_code_rate > val_code_rate * 1.2:
        insights.append("Refuted solutions include code but may be incorrect implementations")
    
    return insights