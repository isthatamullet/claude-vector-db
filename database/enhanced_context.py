#!/usr/bin/env python3
"""
Enhanced Context Analysis for Claude Code Vector Database

This module implements the live validation learning system and other enhancement features
from the ENHANCED_CONTEXT_AWARENESS.md specification:

1. Topic Detection & Boosting
2. Solution Quality Detection  
3. Feedback Sentiment Analysis
4. Adjacency-Aware Feedback Learning
5. Live Validation Learning System

Enables real-time learning from user feedback to improve solution recommendations.
"""

import re
import logging
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

# Topic Pattern Detection (from ENHANCED_CONTEXT_AWARENESS.md)
TOPIC_PATTERNS = {
    "debugging": ["error", "bug", "issue", "problem", "fix", "debug", "troubleshoot", "stack trace", "exception", "crash"],
    "performance": ["slow", "optimize", "performance", "speed", "latency", "memory", "bottleneck", "cache", "efficient"],
    "authentication": ["auth", "login", "token", "session", "user", "security", "oauth", "jwt", "password", "signin"],
    "deployment": ["deploy", "production", "live", "release", "build", "ci/cd", "pipeline", "docker", "kubernetes"],
    "testing": ["test", "jest", "playwright", "coverage", "validation", "unit test", "e2e", "mock", "spec"],
    "styling": ["css", "design", "responsive", "layout", "ui", "styling", "theme", "component", "responsive"],
    "database": ["sql", "query", "database", "db", "migration", "schema", "table", "orm", "postgres", "mongodb"],
    "api": ["endpoint", "api", "rest", "graphql", "request", "response", "http", "fetch", "axios", "curl"],
    "state_management": ["state", "redux", "context", "store", "mutation", "reactive", "useState", "zustand"],
    "configuration": ["config", "env", "environment", "settings", "variables", "setup", "dotenv", ".env"],
    "framework": ["react", "next", "vue", "angular", "express", "fastapi", "django", "flask", "nodejs"],
    "devtools": ["vscode", "git", "npm", "yarn", "webpack", "vite", "typescript", "eslint", "prettier"]
}

# Solution Quality Indicators (from specification)
SUCCESS_MARKERS = [
    "✅", "fixed", "working", "solved", "success", "complete", "done",
    "perfect", "exactly", "brilliant", "awesome", "fantastic", "great job"
]

QUALITY_INDICATORS = [
    "tested", "validated", "confirmed", "production-ready", "deployed",
    "typecheck passed", "build succeeded", "tests passing", "verified", "approved"
]

IMPLEMENTATION_SUCCESS = [
    "final solution", "this worked", "problem resolved", "issue fixed",
    "successfully implemented", "now working", "deployment successful",
    "performance improved", "optimization complete", "implementation complete"
]

CODE_SUCCESS_PATTERNS = [
    "code works", "implementation successful", "function working",
    "no errors", "running smoothly", "behaving correctly", "compiled successfully"
]

# Feedback Pattern Recognition (from specification)
POSITIVE_FEEDBACK_PATTERNS = {
    "strong_positive": [
        "perfect", "exactly", "brilliant", "awesome", "fantastic", 
        "works perfectly", "fixed it", "that worked", "problem solved",
        "this is great", "love it", "amazing", "spot on"
    ],
    "moderate_positive": [
        "great", "good", "works", "working", "fixed", "thanks", 
        "solved", "success", "✅", "correct", "nice", "helpful"
    ],
    "subtle_positive": [
        "better", "improved", "progress", "closer", "helped", "useful"
    ]
}

NEGATIVE_FEEDBACK_PATTERNS = {
    "strong_negative": [
        "still completely broken", "made it worse", "totally wrong", 
        "doesn't work at all", "same exact error", "completely failed",
        "broken", "useless", "wrong approach"
    ],
    "moderate_negative": [
        "still not working", "didn't work", "still broken", "not fixed",
        "same error", "still happening", "no change", "still failing"
    ],
    "subtle_negative": [
        "not quite", "almost", "close but", "still some issues",
        "partially broken", "needs work"
    ]
}

PARTIAL_SUCCESS_PATTERNS = [
    "partially working", "some progress", "better but", "almost there",
    "fixed one issue but", "working sometimes", "intermittent",
    "mostly working", "some improvements"
]

# Error and Problem Detection
ERROR_PATTERNS = [
    "error", "exception", "failed", "failing", "broken", "not working",
    "issue", "problem", "bug", "crash", "hang", "timeout", "traceback"
]

TROUBLESHOOTING_INDICATORS = [
    "debug", "investigate", "diagnose", "trace", "inspect", "analyze",
    "troubleshoot", "examine", "check", "verify", "test", "reproduce"
]

RESOLUTION_PROGRESSION = [
    "tried", "attempted", "testing", "checking", "investigating",
    "found the issue", "identified the problem", "root cause",
    "solution found", "fixed by", "resolved with", "turns out"
]


def detect_conversation_topics(content: str) -> Dict[str, float]:
    """
    Analyze conversation content and return topic relevance scores.
    
    Args:
        content: The conversation content to analyze
        
    Returns:
        Dictionary mapping topic names to relevance scores (0.0 to 2.0)
    """
    topic_scores = {}
    content_lower = content.lower()
    content_words = content_lower.split()
    
    for topic, keywords in TOPIC_PATTERNS.items():
        score = 0.0
        
        # Count keyword matches
        for keyword in keywords:
            if keyword in content_lower:
                # Weight multi-word keywords higher
                if ' ' in keyword:
                    score += content_lower.count(keyword) * 2.0
                else:
                    score += content_lower.count(keyword) * 1.0
        
        # Normalize by content length and keyword count
        if len(content_words) > 0:
            normalized_score = score / (len(content_words) * 0.01)
            topic_scores[topic] = min(normalized_score, 2.0)
        else:
            topic_scores[topic] = 0.0
    
    # Only return topics with meaningful scores
    return {topic: score for topic, score in topic_scores.items() if score > 0.1}


def calculate_solution_quality_score(content: str, metadata: Dict) -> float:
    """
    Calculate a quality score for solutions based on success indicators.
    
    Args:
        content: The conversation content
        metadata: Entry metadata including tools_used, has_code, etc.
        
    Returns:
        Quality score (1.0 to 3.0), where 1.0 is baseline
    """
    content_lower = content.lower()
    quality_score = 1.0  # Base score
    
    # Success marker detection
    success_count = sum(content_lower.count(marker) for marker in SUCCESS_MARKERS)
    quality_score += success_count * 0.3
    
    # Quality indicator boost
    quality_count = sum(content_lower.count(indicator) for indicator in QUALITY_INDICATORS)
    quality_score += quality_count * 0.4
    
    # Implementation success boost
    impl_count = sum(content_lower.count(pattern) for pattern in IMPLEMENTATION_SUCCESS)
    quality_score += impl_count * 0.5
    
    # Code success patterns
    code_success_count = sum(content_lower.count(pattern) for pattern in CODE_SUCCESS_PATTERNS)
    quality_score += code_success_count * 0.4
    
    # Code presence and tools used boost
    if metadata.get('has_code', False):
        quality_score += 0.2
    
    tools_used = metadata.get('tools_used', [])
    if isinstance(tools_used, str):
        try:
            tools_used = json.loads(tools_used)
        except:
            tools_used = []
    
    # Boost for implementation tools
    implementation_tools = ['Edit', 'Write', 'MultiEdit', 'Bash']
    if any(tool in implementation_tools for tool in tools_used):
        quality_score += 0.3
    
    # Length and comprehensiveness bonus
    if len(content) > 500:
        quality_score += 0.1
    if len(content) > 1500:
        quality_score += 0.1
    
    return min(quality_score, 3.0)  # Cap at 3x boost


def analyze_feedback_sentiment(feedback_content: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze user feedback to determine sentiment and strength.
    
    Args:
        feedback_content: User's feedback message content
        context: Optional context information for enhanced analysis
        
    Returns:
        Dictionary with sentiment analysis results
    """
    content_lower = feedback_content.lower()
    
    # Check for positive patterns
    positive_score = 0
    for strength, patterns in POSITIVE_FEEDBACK_PATTERNS.items():
        matches = sum(content_lower.count(pattern) for pattern in patterns)
        if strength == "strong_positive":
            positive_score += matches * 3
        elif strength == "moderate_positive":
            positive_score += matches * 2
        else:
            positive_score += matches * 1
    
    # Check for negative patterns
    negative_score = 0
    for strength, patterns in NEGATIVE_FEEDBACK_PATTERNS.items():
        matches = sum(content_lower.count(pattern) for pattern in patterns)
        if strength == "strong_negative":
            negative_score += matches * 3
        elif strength == "moderate_negative":
            negative_score += matches * 2
        else:
            negative_score += matches * 1
    
    # Check for partial success
    partial_score = sum(content_lower.count(pattern) for pattern in PARTIAL_SUCCESS_PATTERNS)
    
    # Determine overall sentiment
    if positive_score > negative_score and positive_score > partial_score:
        sentiment = "positive"
        strength = min(positive_score / 3.0, 1.0)
    elif negative_score > positive_score and negative_score > partial_score:
        sentiment = "negative"
        strength = min(negative_score / 3.0, 1.0)
    elif partial_score > 0:
        sentiment = "partial"
        strength = min(partial_score / 2.0, 1.0)
    else:
        sentiment = "neutral"
        strength = 0.0
    
    # Calculate confidence based on clarity of signal
    total_signal = positive_score + negative_score + partial_score
    confidence = min(total_signal / 5.0, 1.0) if total_signal > 0 else 0.0
    
    # Calculate certainty (how clear the outcome is)
    if sentiment in ["positive", "negative"]:
        certainty = strength * confidence
    else:
        certainty = 0.5 * confidence  # Partial/neutral outcomes are less certain
    
    # Context-aware enhancements
    context_boost = 0.0
    is_contextual_feedback = False
    
    if context:
        # Check if this is feedback responding to an assistant solution
        if hasattr(context, 'previous_message') and context.previous_message:
            prev_msg = context.previous_message
            if isinstance(prev_msg, dict) and prev_msg.get('type') == 'assistant':
                is_contextual_feedback = True
                # Boost confidence for contextual feedback patterns
                if sentiment != 'neutral':
                    context_boost = 0.1  # 10% confidence boost for contextual feedback
        
        # Project-specific adjustments could be added here in the future
        # if hasattr(context, 'file_path'):
        #     # Project-specific sentiment pattern adjustments
    
    # Apply context boost
    if context_boost > 0:
        confidence = min(confidence + context_boost, 1.0)
        if sentiment in ["positive", "negative"]:
            certainty = strength * confidence
        else:
            certainty = 0.5 * confidence
    
    return {
        'sentiment': sentiment,
        'strength': strength,
        'confidence': confidence,
        'certainty': certainty,
        'positive_score': positive_score,
        'negative_score': negative_score,
        'partial_score': partial_score,
        'is_contextual_feedback': is_contextual_feedback,
        'context_boost_applied': context_boost
    }


def is_solution_attempt(content: str) -> bool:
    """
    Determine if a message is a solution attempt from Claude using semantic analysis.
    
    Args:
        content: Message content to analyze
        
    Returns:
        True if content appears to be a solution attempt
    """
    content_lower = content.lower()
    
    # Fast path: Strong solution indicators (high precision patterns)
    strong_indicators = [
        'multiedit', 'edit tool', 'bash tool', 'write tool', 'read tool',
        '```', 'function ', 'npm ', 'git ', 'pip install', 'apt install',
        'here\'s the solution', 'try this', 'run this command'
    ]
    
    if any(indicator in content_lower for indicator in strong_indicators):
        return True
    
    # Semantic approach: Check for solution-oriented language patterns
    solution_patterns = [
        # Helpful/assistive language
        ('help', ['i\'ll help', 'let me help', 'i can help']),
        ('assistance', ['let me', 'i\'ll', 'allow me']),
        
        # Action-oriented language  
        ('implementation', ['implement', 'create', 'build', 'setup', 'configure']),
        ('modification', ['update', 'change', 'modify', 'edit', 'fix', 'adjust']),
        ('instruction', ['use this', 'run this', 'add this', 'replace', 'install']),
        
        # Problem-solving language
        ('resolution', ['solution', 'resolve', 'solve', 'address']),
        ('guidance', ['here\'s how', 'you can', 'try', 'should']),
    ]
    
    pattern_matches = 0
    for category, patterns in solution_patterns:
        if any(pattern in content_lower for pattern in patterns):
            pattern_matches += 1
    
    # Contextual factors
    has_code_context = any(marker in content for marker in [
        '```', 'function', 'const ', 'let ', 'var ', 'import ', 'from ',
        '.js', '.py', '.json', '.md', '.sh', '.tsx', '.ts'
    ])
    
    has_steps = bool(re.search(r'\d+\.\s', content)) or ('step' in content_lower)
    
    is_substantial = len(content) > 150
    is_moderate = len(content) > 75
    
    # Decision logic (more nuanced than before)
    if pattern_matches >= 2:  # Multiple solution patterns
        return True
    elif pattern_matches >= 1 and (has_code_context or has_steps):
        return True  # Solution language + technical content
    elif pattern_matches >= 1 and is_substantial:
        return True  # Solution language + substantial content
    elif has_code_context and is_moderate:
        return True  # Technical content with reasonable length
    
    return False


def classify_solution_type(content: str, entry_data: Dict = None) -> str:
    """
    Classify the type of solution being attempted.
    
    Args:
        content: Solution content to classify
        entry_data: Additional entry metadata for classification
        
    Returns:
        Solution category string
    """
    content_lower = content.lower()
    
    if any(indicator in content for indicator in ['```', 'function', 'class', 'def ']):
        return "code_fix"
    elif any(indicator in content_lower for indicator in ['config', 'setting', 'env', 'install', 'package']):
        return "config_change"
    elif any(indicator in content_lower for indicator in ['approach', 'strategy', 'consider', 'recommend']):
        return "approach_suggestion"
    elif any(indicator in content_lower for indicator in ['debug', 'check', 'investigate', 'verify']):
        return "debugging_step"
    else:
        return "general_solution"


def apply_feedback_to_solution(solution_dict: Dict, feedback_analysis: Dict) -> Dict:
    """
    Apply user feedback analysis to solution entry dictionary.
    
    Args:
        solution_dict: Dictionary representing solution entry
        feedback_analysis: Results from analyze_feedback_sentiment()
        
    Returns:
        Updated solution dictionary with validation fields
    """
    sentiment = feedback_analysis['sentiment']
    strength = feedback_analysis['strength']
    certainty = feedback_analysis['certainty']
    
    # Create updated dictionary
    updated_dict = solution_dict.copy()
    
    if sentiment == "positive":
        updated_dict['is_validated_solution'] = True
        updated_dict['is_refuted_attempt'] = False
        updated_dict['validation_strength'] = strength
        updated_dict['solution_confidence'] = 1.0 + (strength * 1.0)  # Up to 2.0
    elif sentiment == "negative":
        updated_dict['is_validated_solution'] = False
        updated_dict['is_refuted_attempt'] = True
        updated_dict['validation_strength'] = -strength
        updated_dict['solution_confidence'] = max(0.3, 1.0 - (strength * 0.7))  # Down to 0.3
    elif sentiment == "partial":
        updated_dict['is_validated_solution'] = False
        updated_dict['is_refuted_attempt'] = False
        updated_dict['validation_strength'] = strength * 0.5
        updated_dict['solution_confidence'] = 1.0 + (strength * 0.3)  # Up to 1.3
    else:
        # Neutral - no change to validation status
        pass
    
    updated_dict['user_feedback_sentiment'] = sentiment
    updated_dict['outcome_certainty'] = certainty
    
    return updated_dict


def analyze_conversation_adjacency(messages: List[Dict]) -> Tuple[List[Dict], Dict]:
    """
    Analyze conversation flow and detect solution-feedback relationships.
    
    Args:
        messages: List of message dictionaries with id, content, type, etc.
        
    Returns:
        Tuple of (enhanced_messages, conversation_context)
    """
    enhanced_messages = []
    conversation_context = {
        'total_messages': len(messages),
        'solution_attempts': 0,
        'feedback_instances': 0,
        'solution_feedback_pairs': []
    }
    
    for i, message in enumerate(messages):
        enhanced_msg = message.copy()
        
        # Set adjacency relationships
        if i > 0:
            enhanced_msg['previous_message_id'] = messages[i-1]['id']
        if i < len(messages) - 1:
            enhanced_msg['next_message_id'] = messages[i+1]['id']
        enhanced_msg['message_sequence_position'] = i
        
        # Analyze solution-feedback patterns
        if message['type'] == 'assistant' and is_solution_attempt(message['content']):
            # This is a potential solution from Claude
            enhanced_msg['is_solution_attempt'] = True
            enhanced_msg['solution_category'] = classify_solution_type(message['content'])
            conversation_context['solution_attempts'] += 1
            
            # Check next message for user feedback
            if i < len(messages) - 1:
                next_message = messages[i+1]
                if next_message['type'] == 'user':
                    enhanced_msg['feedback_message_id'] = next_message['id']
                    
                    # Analyze the feedback
                    feedback_analysis = analyze_feedback_sentiment(next_message['content'])
                    if feedback_analysis['sentiment'] != 'neutral':
                        conversation_context['feedback_instances'] += 1
                        conversation_context['solution_feedback_pairs'].append({
                            'solution_id': message['id'],
                            'feedback_id': next_message['id'],
                            'sentiment': feedback_analysis['sentiment'],
                            'strength': feedback_analysis['strength']
                        })
        
        elif message['type'] == 'user' and i > 0:
            prev_message = messages[i-1]
            if prev_message['type'] == 'assistant' and is_solution_attempt(prev_message['content']):
                # This is user feedback on a Claude solution
                enhanced_msg['is_feedback_to_solution'] = True
                enhanced_msg['related_solution_id'] = prev_message['id']
                
                # Analyze feedback sentiment
                feedback_analysis = analyze_feedback_sentiment(message['content'])
                enhanced_msg['feedback_sentiment'] = feedback_analysis['sentiment']
                enhanced_msg['feedback_strength'] = feedback_analysis['strength']
                enhanced_msg['feedback_certainty'] = feedback_analysis['certainty']
        
        enhanced_messages.append(enhanced_msg)
    
    logger.info(f"Adjacency analysis: {conversation_context['solution_attempts']} solutions, "
                f"{conversation_context['feedback_instances']} feedback instances")
    
    return enhanced_messages, conversation_context


def calculate_troubleshooting_boost(content: str, query_context: Dict) -> float:
    """
    Apply boosting for troubleshooting and problem-solving contexts.
    
    Args:
        content: Content to analyze
        query_context: Context about the query (troubleshooting_mode, etc.)
        
    Returns:
        Boost factor for troubleshooting relevance
    """
    if not query_context.get('troubleshooting_mode', False):
        return 1.0
    
    content_lower = content.lower()
    troubleshooting_score = 1.0
    
    # Problem detection boost
    error_count = sum(content_lower.count(pattern) for pattern in ERROR_PATTERNS)
    troubleshooting_score += error_count * 0.2
    
    # Troubleshooting process boost
    debug_count = sum(content_lower.count(indicator) for indicator in TROUBLESHOOTING_INDICATORS)
    troubleshooting_score += debug_count * 0.3
    
    # Resolution progression boost
    resolution_count = sum(content_lower.count(marker) for marker in RESOLUTION_PROGRESSION)
    troubleshooting_score += resolution_count * 0.4
    
    return min(troubleshooting_score, 2.5)


def calculate_recency_boost(timestamp: str, query_context: Dict) -> float:
    """
    Calculate recency boost based on message timestamp.
    
    Args:
        timestamp: ISO timestamp string
        query_context: Query context with recency preferences
        
    Returns:
        Recency boost factor
    """
    if not timestamp or not query_context.get('prefer_recent', False):
        return 1.0
    
    try:
        # Parse timestamp
        if timestamp.endswith('Z'):
            timestamp = timestamp[:-1] + '+00:00'
        
        msg_time = datetime.fromisoformat(timestamp)
        now = datetime.now(msg_time.tzinfo)
        
        # Calculate age in hours
        age_hours = (now - msg_time).total_seconds() / 3600
        
        # Apply recency boost (strongest for last 24 hours)
        if age_hours < 24:
            return 1.8  # Recent conversations get strong boost
        elif age_hours < 24 * 7:  # Last week
            return 1.4
        elif age_hours < 24 * 30:  # Last month
            return 1.2
        else:
            return 1.0
            
    except Exception as e:
        logger.warning(f"Error calculating recency boost: {e}")
        return 1.0


# Live Validation Learning System Implementation

class LiveValidationLearner:
    """
    Implements the live validation learning system from ENHANCED_CONTEXT_AWARENESS.md.
    
    This class continuously learns from user feedback to improve solution recommendations
    by tracking validation patterns and updating solution confidence scores in real-time.
    """
    
    def __init__(self):
        self.validation_patterns = {}
        self.solution_success_rates = {}
        self.feedback_history = []
        self.learning_stats = {
            'total_validations': 0,
            'positive_validations': 0,
            'negative_validations': 0,
            'partial_validations': 0,
            'confidence_updates': 0
        }
    
    def process_validation_feedback(self, solution_id: str, solution_content: str, 
                                  feedback_content: str, metadata: Dict = None) -> Dict[str, Any]:
        """
        Process user feedback for a solution and update validation learning.
        
        Args:
            solution_id: Unique identifier for the solution
            solution_content: The solution content that was provided
            feedback_content: User's feedback on the solution
            metadata: Additional metadata about the solution
            
        Returns:
            Dictionary with validation results and learning updates
        """
        # Analyze feedback sentiment
        feedback_analysis = analyze_feedback_sentiment(feedback_content)
        
        # Extract solution characteristics for pattern learning
        solution_topics = detect_conversation_topics(solution_content)
        solution_quality = calculate_solution_quality_score(solution_content, metadata or {})
        solution_type = classify_solution_type(solution_content)
        
        # Create validation record
        validation_record = {
            'solution_id': solution_id,
            'timestamp': datetime.now().isoformat(),
            'feedback_sentiment': feedback_analysis['sentiment'],
            'feedback_strength': feedback_analysis['strength'],
            'feedback_certainty': feedback_analysis['certainty'],
            'solution_topics': solution_topics,
            'solution_quality': solution_quality,
            'solution_type': solution_type,
            'is_validated': feedback_analysis['sentiment'] == 'positive',
            'is_refuted': feedback_analysis['sentiment'] == 'negative',
            'is_partial': feedback_analysis['sentiment'] == 'partial'
        }
        
        # Update learning statistics
        self.learning_stats['total_validations'] += 1
        if validation_record['is_validated']:
            self.learning_stats['positive_validations'] += 1
        elif validation_record['is_refuted']:
            self.learning_stats['negative_validations'] += 1
        elif validation_record['is_partial']:
            self.learning_stats['partial_validations'] += 1
        
        # Learn from validation patterns
        self._update_validation_patterns(validation_record)
        self._update_solution_success_rates(validation_record)
        
        # Store feedback history
        self.feedback_history.append(validation_record)
        
        # Trim history to last 1000 entries
        if len(self.feedback_history) > 1000:
            self.feedback_history = self.feedback_history[-1000:]
        
        logger.info(f"Processed validation feedback for {solution_id}: "
                   f"{feedback_analysis['sentiment']} (strength: {feedback_analysis['strength']:.2f})")
        
        return {
            'validation_record': validation_record,
            'feedback_analysis': feedback_analysis,
            'learning_update': True,
            'confidence_boost': self._calculate_confidence_boost(validation_record)
        }
    
    def _update_validation_patterns(self, validation_record: Dict):
        """Update validation patterns based on new feedback."""
        solution_type = validation_record['solution_type']
        primary_topic = max(validation_record['solution_topics'].items(), key=lambda x: x[1])[0] if validation_record['solution_topics'] else 'general'
        
        # Create pattern key
        pattern_key = f"{solution_type}_{primary_topic}"
        
        if pattern_key not in self.validation_patterns:
            self.validation_patterns[pattern_key] = {
                'total_attempts': 0,
                'successful': 0,
                'failed': 0,
                'partial': 0,
                'success_rate': 0.0,
                'avg_strength': 0.0,
                'strength_history': []
            }
        
        pattern = self.validation_patterns[pattern_key]
        pattern['total_attempts'] += 1
        
        if validation_record['is_validated']:
            pattern['successful'] += 1
        elif validation_record['is_refuted']:
            pattern['failed'] += 1
        elif validation_record['is_partial']:
            pattern['partial'] += 1
        
        # Update success rate
        pattern['success_rate'] = pattern['successful'] / pattern['total_attempts']
        
        # Update average strength
        pattern['strength_history'].append(validation_record['feedback_strength'])
        if len(pattern['strength_history']) > 100:  # Keep last 100 samples
            pattern['strength_history'] = pattern['strength_history'][-100:]
        pattern['avg_strength'] = sum(pattern['strength_history']) / len(pattern['strength_history'])
    
    def _update_solution_success_rates(self, validation_record: Dict):
        """Update solution success rates by topic and type."""
        for topic, score in validation_record['solution_topics'].items():
            if score > 0.5:  # Only consider strong topic associations
                if topic not in self.solution_success_rates:
                    self.solution_success_rates[topic] = {
                        'attempts': 0,
                        'successes': 0,
                        'rate': 0.0
                    }
                
                topic_stats = self.solution_success_rates[topic]
                topic_stats['attempts'] += 1
                
                if validation_record['is_validated']:
                    topic_stats['successes'] += 1
                
                topic_stats['rate'] = topic_stats['successes'] / topic_stats['attempts']
    
    def _calculate_confidence_boost(self, validation_record: Dict) -> float:
        """Calculate confidence boost for similar future solutions."""
        base_boost = 1.0
        
        if validation_record['is_validated']:
            base_boost = 1.0 + (validation_record['feedback_strength'] * 0.5)
        elif validation_record['is_refuted']:
            base_boost = max(0.3, 1.0 - (validation_record['feedback_strength'] * 0.4))
        elif validation_record['is_partial']:
            base_boost = 1.0 + (validation_record['feedback_strength'] * 0.2)
        
        return base_boost
    
    def get_solution_confidence_multiplier(self, solution_content: str, solution_topics: Dict[str, float], 
                                         solution_type: str) -> float:
        """
        Get confidence multiplier for a solution based on learned patterns.
        
        Args:
            solution_content: The solution content
            solution_topics: Detected topics for the solution
            solution_type: Type of solution (code_fix, config_change, etc.)
            
        Returns:
            Confidence multiplier to apply to the solution
        """
        if not self.validation_patterns:
            return 1.0  # No learning data yet
        
        confidence_factors = []
        
        # Check pattern-based confidence
        for topic, score in solution_topics.items():
            if score > 0.5:
                pattern_key = f"{solution_type}_{topic}"
                if pattern_key in self.validation_patterns:
                    pattern = self.validation_patterns[pattern_key]
                    if pattern['total_attempts'] >= 3:  # Need minimum sample size
                        confidence_factors.append(pattern['success_rate'] * 2.0)  # Convert to multiplier
        
        # Check topic-based success rates
        for topic, score in solution_topics.items():
            if score > 0.5 and topic in self.solution_success_rates:
                topic_stats = self.solution_success_rates[topic]
                if topic_stats['attempts'] >= 5:
                    confidence_factors.append(0.5 + topic_stats['rate'])  # 0.5 to 1.5 range
        
        if confidence_factors:
            # Use geometric mean of confidence factors
            import math
            geometric_mean = math.pow(math.prod(confidence_factors), 1.0 / len(confidence_factors))
            return max(0.3, min(2.0, geometric_mean))  # Clamp to reasonable range
        
        return 1.0  # Default neutral confidence
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get insights about the learning system's performance and patterns.
        
        Returns:
            Dictionary with learning insights and statistics
        """
        total_validations = self.learning_stats['total_validations']
        if total_validations == 0:
            return {'status': 'no_data', 'message': 'No validation data available yet'}
        
        # Calculate overall success rate
        success_rate = self.learning_stats['positive_validations'] / total_validations
        
        # Find most successful patterns
        best_patterns = sorted(
            [(k, v) for k, v in self.validation_patterns.items() if v['total_attempts'] >= 3],
            key=lambda x: x[1]['success_rate'],
            reverse=True
        )[:5]
        
        # Find most successful topics
        best_topics = sorted(
            [(k, v) for k, v in self.solution_success_rates.items() if v['attempts'] >= 3],
            key=lambda x: x[1]['rate'],
            reverse=True
        )[:5]
        
        return {
            'status': 'active',
            'overall_stats': self.learning_stats.copy(),
            'overall_success_rate': success_rate,
            'validation_coverage': len(self.validation_patterns),
            'topic_coverage': len(self.solution_success_rates),
            'best_performing_patterns': [
                {'pattern': pattern, 'success_rate': data['success_rate'], 'attempts': data['total_attempts']}
                for pattern, data in best_patterns
            ],
            'best_performing_topics': [
                {'topic': topic, 'success_rate': data['rate'], 'attempts': data['attempts']}
                for topic, data in best_topics
            ],
            'recent_feedback_trend': self._analyze_recent_trend(),
            'confidence_distribution': self._get_confidence_distribution()
        }
    
    def _analyze_recent_trend(self) -> Dict[str, Any]:
        """Analyze recent feedback trends."""
        if len(self.feedback_history) < 10:
            return {'status': 'insufficient_data'}
        
        recent_feedback = self.feedback_history[-20:]  # Last 20 items
        older_feedback = self.feedback_history[-40:-20] if len(self.feedback_history) >= 40 else []
        
        recent_success = sum(1 for f in recent_feedback if f['is_validated']) / len(recent_feedback)
        
        if older_feedback:
            older_success = sum(1 for f in older_feedback if f['is_validated']) / len(older_feedback)
            trend = 'improving' if recent_success > older_success else 'declining' if recent_success < older_success else 'stable'
        else:
            trend = 'unknown'
        
        return {
            'status': 'available',
            'recent_success_rate': recent_success,
            'trend': trend,
            'sample_size': len(recent_feedback)
        }
    
    def _get_confidence_distribution(self) -> Dict[str, int]:
        """Get distribution of confidence levels."""
        distribution = {'low': 0, 'medium': 0, 'high': 0}
        
        for pattern_data in self.validation_patterns.values():
            if pattern_data['total_attempts'] >= 3:
                rate = pattern_data['success_rate']
                if rate < 0.4:
                    distribution['low'] += 1
                elif rate < 0.7:
                    distribution['medium'] += 1
                else:
                    distribution['high'] += 1
        
        return distribution


# Global instance for live validation learning
_live_validation_learner = LiveValidationLearner()

# Real-time Feedback Loop Learning System
class RealTimeFeedbackLoopLearner:
    """
    Implements the real-time feedback loop learning system - the final component
    from ENHANCED_CONTEXT_AWARENESS.md.
    
    This class automatically detects solution→feedback patterns during conversation
    processing and continuously learns from outcomes in real-time.
    """
    
    def __init__(self):
        self.active_learning = True
        self.feedback_detection_threshold = 0.3
        self.learning_stats = {
            'conversations_processed': 0,
            'feedback_loops_detected': 0,
            'solutions_learned_from': 0,
            'validation_updates': 0
        }
        self.real_time_patterns = {}  # Patterns detected in current session
        
    def process_conversation_for_feedback_loops(self, conversation_messages: List[Dict]) -> Dict[str, Any]:
        """
        Process a complete conversation to detect and learn from feedback loops in real-time.
        
        This is the core of the real-time feedback loop learning system.
        
        Args:
            conversation_messages: List of conversation messages in chronological order
            
        Returns:
            Dictionary with feedback loop learning results
        """
        logger.info("🔄 Processing conversation for real-time feedback loops...")
        
        feedback_loops = []
        learning_updates = []
        
        for i, message in enumerate(conversation_messages):
            # Look for assistant solutions followed by user feedback
            if (message.get('type') == 'assistant' and 
                is_solution_attempt(message.get('content', '')) and
                i < len(conversation_messages) - 1):
                
                next_message = conversation_messages[i + 1]
                if next_message.get('type') == 'user':
                    
                    # Analyze potential feedback
                    feedback_analysis = analyze_feedback_sentiment(next_message.get('content', ''))
                    
                    if feedback_analysis['strength'] > self.feedback_detection_threshold:
                        
                        # Detected a feedback loop!
                        feedback_loop = {
                            'solution_id': message.get('id'),
                            'solution_content': message.get('content', ''),
                            'feedback_id': next_message.get('id'),
                            'feedback_content': next_message.get('content', ''),
                            'feedback_sentiment': feedback_analysis['sentiment'],
                            'feedback_strength': feedback_analysis['strength'],
                            'timestamp': message.get('timestamp'),
                            'detected_in_realtime': True
                        }
                        
                        feedback_loops.append(feedback_loop)
                        
                        # Apply real-time learning
                        learning_update = self._apply_realtime_learning(feedback_loop)
                        learning_updates.append(learning_update)
                        
                        self.learning_stats['feedback_loops_detected'] += 1
                        self.learning_stats['solutions_learned_from'] += 1
        
        self.learning_stats['conversations_processed'] += 1
        
        return {
            'feedback_loops_detected': len(feedback_loops),
            'feedback_loops': feedback_loops,
            'learning_updates': learning_updates,
            'real_time_learning_applied': len(learning_updates) > 0,
            'learning_stats': self.learning_stats.copy()
        }
    
    def _apply_realtime_learning(self, feedback_loop: Dict) -> Dict[str, Any]:
        """
        Apply real-time learning from a detected feedback loop.
        
        This updates patterns and validation scores immediately as feedback is processed.
        """
        solution_content = feedback_loop['solution_content']
        feedback_sentiment = feedback_loop['feedback_sentiment']
        feedback_strength = feedback_loop['feedback_strength']
        
        # Detect solution characteristics
        solution_topics = detect_conversation_topics(solution_content)
        solution_quality = calculate_solution_quality_score(solution_content, {'has_code': 'def ' in solution_content or 'function' in solution_content})
        
        # Create real-time pattern key
        primary_topic = max(solution_topics.items(), key=lambda x: x[1])[0] if solution_topics else 'general'
        solution_type = classify_solution_type(solution_content)
        pattern_key = f"realtime_{solution_type}_{primary_topic}"
        
        # Initialize pattern if new
        if pattern_key not in self.real_time_patterns:
            self.real_time_patterns[pattern_key] = {
                'success_count': 0,
                'failure_count': 0,
                'total_feedback': 0,
                'avg_strength': 0.0,
                'confidence_score': 1.0,
                'last_updated': datetime.now().isoformat()
            }
        
        pattern = self.real_time_patterns[pattern_key]
        
        # Update pattern based on feedback
        pattern['total_feedback'] += 1
        
        if feedback_sentiment == 'positive':
            pattern['success_count'] += 1
            pattern['confidence_score'] = min(pattern['confidence_score'] + (feedback_strength * 0.2), 2.0)
        elif feedback_sentiment == 'negative':
            pattern['failure_count'] += 1
            pattern['confidence_score'] = max(pattern['confidence_score'] - (feedback_strength * 0.3), 0.2)
        
        pattern['avg_strength'] = ((pattern['avg_strength'] * (pattern['total_feedback'] - 1)) + feedback_strength) / pattern['total_feedback']
        pattern['last_updated'] = datetime.now().isoformat()
        
        # Process through live validation learner for long-term learning
        _live_validation_learner.process_validation_feedback(
            feedback_loop['solution_id'],
            feedback_loop['solution_content'],
            feedback_loop['feedback_content'],
            {
                'solution_topics': solution_topics,
                'solution_quality': solution_quality,
                'real_time_detection': True
            }
        )
        
        self.learning_stats['validation_updates'] += 1
        
        logger.info(f"✅ Real-time learning applied: {feedback_sentiment} feedback (strength: {feedback_strength:.2f}) for {solution_type} solution")
        
        return {
            'pattern_key': pattern_key,
            'feedback_sentiment': feedback_sentiment,
            'feedback_strength': feedback_strength,
            'confidence_update': pattern['confidence_score'],
            'pattern_stats': pattern.copy(),
            'learning_applied': True
        }
    
    def get_realtime_learning_boost(self, solution_content: str, solution_topics: Dict[str, float]) -> float:
        """
        Calculate boost based on real-time learning patterns.
        
        This allows the system to immediately apply learned patterns to boost/demote
        similar solutions based on recent feedback.
        """
        if not self.real_time_patterns:
            return 1.0
        
        solution_type = classify_solution_type(solution_content)
        primary_topic = max(solution_topics.items(), key=lambda x: x[1])[0] if solution_topics else 'general'
        pattern_key = f"realtime_{solution_type}_{primary_topic}"
        
        if pattern_key in self.real_time_patterns:
            pattern = self.real_time_patterns[pattern_key]
            
            # Use confidence score as boost factor
            boost = pattern['confidence_score']
            
            # Apply recency weighting - more recent patterns have stronger influence
            try:
                last_updated = datetime.fromisoformat(pattern['last_updated'])
                hours_since_update = (datetime.now() - last_updated).total_seconds() / 3600
                recency_factor = max(0.5, 1.0 - (hours_since_update / 24))  # Decay over 24 hours
                boost = 1.0 + ((boost - 1.0) * recency_factor)
            except:
                pass  # Use raw boost if timestamp parsing fails
            
            return boost
        
        return 1.0
    
    def get_learning_insights(self) -> Dict[str, Any]:
        """
        Get comprehensive insights about real-time learning progress.
        """
        total_patterns = len(self.real_time_patterns)
        high_confidence_patterns = sum(1 for p in self.real_time_patterns.values() if p['confidence_score'] > 1.2)
        low_confidence_patterns = sum(1 for p in self.real_time_patterns.values() if p['confidence_score'] < 0.8)
        
        return {
            'learning_stats': self.learning_stats.copy(),
            'pattern_analysis': {
                'total_patterns': total_patterns,
                'high_confidence_patterns': high_confidence_patterns,
                'low_confidence_patterns': low_confidence_patterns,
                'patterns_by_topic': self._analyze_patterns_by_topic()
            },
            'recent_patterns': dict(list(self.real_time_patterns.items())[-10:]) if self.real_time_patterns else {},
            'system_status': {
                'active_learning': self.active_learning,
                'feedback_threshold': self.feedback_detection_threshold
            }
        }
    
    def _analyze_patterns_by_topic(self) -> Dict[str, Dict]:
        """Analyze real-time patterns grouped by topic."""
        topic_analysis = {}
        
        for pattern_key, pattern in self.real_time_patterns.items():
            parts = pattern_key.split('_')
            if len(parts) >= 3:
                topic = parts[2]
                if topic not in topic_analysis:
                    topic_analysis[topic] = {
                        'pattern_count': 0,
                        'avg_confidence': 0.0,
                        'total_feedback': 0,
                        'success_rate': 0.0
                    }
                
                topic_stats = topic_analysis[topic]
                topic_stats['pattern_count'] += 1
                topic_stats['avg_confidence'] += pattern['confidence_score']
                topic_stats['total_feedback'] += pattern['total_feedback']
                
                # Calculate success rate
                if pattern['total_feedback'] > 0:
                    success_rate = pattern['success_count'] / pattern['total_feedback']
                    topic_stats['success_rate'] = ((topic_stats['success_rate'] * (topic_stats['pattern_count'] - 1)) + success_rate) / topic_stats['pattern_count']
        
        # Finalize averages
        for topic_stats in topic_analysis.values():
            if topic_stats['pattern_count'] > 0:
                topic_stats['avg_confidence'] /= topic_stats['pattern_count']
        
        return topic_analysis

# Global instance for real-time feedback loop learning
_realtime_feedback_learner = RealTimeFeedbackLoopLearner()


def get_live_validation_learner() -> LiveValidationLearner:
    """Get the global live validation learner instance."""
    return _live_validation_learner


def process_live_validation_feedback(solution_id: str, solution_content: str, 
                                   feedback_content: str, metadata: Dict = None) -> Dict[str, Any]:
    """
    Process live validation feedback using the global learner.
    
    This is the main entry point for the live validation learning system.
    
    Args:
        solution_id: Unique identifier for the solution
        solution_content: The solution content that was provided
        feedback_content: User's feedback on the solution
        metadata: Additional metadata about the solution
        
    Returns:
        Dictionary with validation results and learning updates
    """
    return _live_validation_learner.process_validation_feedback(
        solution_id, solution_content, feedback_content, metadata
    )

def process_conversation_for_realtime_learning(conversation_messages: List[Dict]) -> Dict[str, Any]:
    """
    Process a complete conversation through the real-time feedback loop learner.
    
    This is the main integration point for real-time feedback loop learning.
    
    Args:
        conversation_messages: List of conversation messages in chronological order
        
    Returns:
        Dictionary with real-time learning results
    """
    return _realtime_feedback_learner.process_conversation_for_feedback_loops(conversation_messages)

def get_realtime_learning_boost(solution_content: str, solution_topics: Dict[str, float]) -> float:
    """
    Get boost factor based on real-time learning patterns.
    
    This allows immediate application of learned patterns to similar solutions.
    
    Args:
        solution_content: Content of the solution to boost
        solution_topics: Detected topics for the solution
        
    Returns:
        Boost factor based on real-time learning
    """
    return _realtime_feedback_learner.get_realtime_learning_boost(solution_content, solution_topics)

def get_realtime_learning_insights() -> Dict[str, Any]:
    """
    Get comprehensive insights about real-time learning system.
    
    Returns:
        Dictionary with learning insights and statistics
    """
    return _realtime_feedback_learner.get_learning_insights()


def get_solution_confidence_boost(solution_content: str, solution_topics: Dict[str, float], 
                                solution_type: str) -> float:
    """
    Get confidence boost for a solution based on learned validation patterns.
    
    Args:
        solution_content: The solution content
        solution_topics: Detected topics for the solution
        solution_type: Type of solution
        
    Returns:
        Confidence multiplier based on learned patterns
    """
    return _live_validation_learner.get_solution_confidence_multiplier(
        solution_content, solution_topics, solution_type
    )


def get_validation_learning_insights() -> Dict[str, Any]:
    """Get insights about the validation learning system's performance."""
    return _live_validation_learner.get_learning_insights()