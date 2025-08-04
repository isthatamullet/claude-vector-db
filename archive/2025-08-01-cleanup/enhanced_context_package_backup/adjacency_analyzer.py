"""
Adjacency Analysis Engine for Conversation Flow Tracking

Analyzes conversation sequences to detect:
- Message adjacency relationships  
- Solution-feedback pair detection
- Context chain construction
- Solution attempt classification
- Conversational flow patterns

Essential for building the feedback learning system that tracks which solutions
users validated or refuted based on their subsequent responses.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Solution attempt detection patterns
SOLUTION_PATTERNS = [
    # Direct solution indicators
    r"try\s+this", r"here'?s\s+(?:the\s+)?(?:fix|solution)", r"you\s+can\s+(?:fix|solve)",
    r"to\s+(?:fix|solve|resolve)", r"the\s+(?:issue|problem|bug)\s+is",
    
    # Implementation suggestions
    r"(?:add|change|modify|update|replace)\s+this", r"update\s+(?:the\s+)?code",
    r"modify\s+(?:your\s+)?(?:function|method|class)", r"replace\s+(?:this\s+)?(?:line|code)",
    
    # Tool-based solutions  
    r"let\s+me\s+(?:fix|update|modify|change)", r"i'll\s+(?:fix|update|modify|add)",
    r"going\s+to\s+(?:fix|update|modify|add)", r"will\s+(?:fix|update|modify|add)",
    
    # Debugging guidance
    r"check\s+(?:if|whether|that)", r"verify\s+(?:that\s+)?(?:the\s+)?",
    r"make\s+sure", r"ensure\s+(?:that\s+)?(?:the\s+)?",
    
    # Configuration solutions
    r"set\s+(?:the\s+)?(?:config|environment|variable)", r"configure\s+(?:the\s+)?",
    r"install\s+(?:the\s+)?", r"run\s+(?:the\s+)?(?:following\s+)?command"
]

# Assistant response indicators (for solution detection)
ASSISTANT_INDICATORS = [
    "i'll", "let me", "here's", "you can", "try", "to fix", "to solve",
    "the solution", "the issue", "the problem", "update", "modify", "change"
]

# Pre-compiled solution patterns for performance
_COMPILED_SOLUTION_PATTERNS: Optional[List[re.Pattern]] = None

def _get_compiled_solution_patterns() -> List[re.Pattern]:
    """Get pre-compiled solution detection patterns"""
    global _COMPILED_SOLUTION_PATTERNS
    
    if _COMPILED_SOLUTION_PATTERNS is None:
        _COMPILED_SOLUTION_PATTERNS = [
            re.compile(pattern, re.IGNORECASE) for pattern in SOLUTION_PATTERNS
        ]
    
    return _COMPILED_SOLUTION_PATTERNS


@dataclass
class ConversationContext:
    """Context information for a conversation sequence"""
    total_messages: int
    assistant_messages: int
    user_messages: int
    solution_attempts: int
    feedback_messages: int
    context_chain_length: int


def is_solution_attempt(content: str, message_type: str = "assistant") -> bool:
    """
    Detect if a message contains a solution attempt.
    
    Args:
        content: Message content to analyze
        message_type: Type of message ("assistant" or "user")
        
    Returns:
        True if message appears to contain a solution attempt
    """
    if message_type != "assistant":
        return False
    
    if not content or len(content.strip()) < 20:
        return False
    
    content_lower = content.lower()
    compiled_patterns = _get_compiled_solution_patterns()
    
    # Check for solution patterns
    pattern_matches = sum(1 for pattern in compiled_patterns if pattern.search(content_lower))
    
    # Check for assistant solution indicators
    indicator_matches = sum(1 for indicator in ASSISTANT_INDICATORS if indicator in content_lower)
    
    # Check for code blocks (strong solution indicator)
    has_code_blocks = bool(re.search(r'```[\w]*\n.*?\n```', content, re.DOTALL))
    
    # Check for tool usage mentions (Edit, Write, etc.)
    has_tool_mentions = bool(re.search(r'\b(?:edit|write|modify|update|add|change)\b.*?(?:file|code|function)', content_lower))
    
    # Scoring system for solution detection
    solution_score = 0
    solution_score += pattern_matches * 2  # Pattern matches worth 2 points each
    solution_score += indicator_matches * 1  # Indicator matches worth 1 point each
    solution_score += 4 if has_code_blocks else 0  # Code blocks worth 4 points
    solution_score += 2 if has_tool_mentions else 0  # Tool mentions worth 2 points
    
    # Message length bonus (longer messages more likely to contain solutions)
    if len(content) > 200:
        solution_score += 1
    if len(content) > 500:
        solution_score += 1
    
    # Threshold for solution detection (tunable)
    return solution_score >= 3


def classify_solution_type(content: str) -> str:
    """
    Classify the type of solution being provided.
    
    Args:
        content: Solution content to classify
        
    Returns:
        Solution category string
    """
    content_lower = content.lower()
    
    # Code implementation solutions
    if (re.search(r'```[\w]*\n.*?\n```', content, re.DOTALL) or
        any(pattern in content_lower for pattern in ['function', 'class', 'def ', 'const ', 'let ', 'var '])):
        return "code_fix"
    
    # Configuration changes
    if any(pattern in content_lower for pattern in [
        'config', 'environment', '.env', 'package.json', 'settings', 'variable'
    ]):
        return "config_change"
    
    # Command/bash solutions
    if any(pattern in content_lower for pattern in [
        'run ', 'execute', 'command', 'bash', 'terminal', 'npm ', 'pip ', 'yarn '
    ]):
        return "command_solution"
    
    # Debugging guidance
    if any(pattern in content_lower for pattern in [
        'debug', 'check', 'verify', 'inspect', 'console.log', 'print', 'log'
    ]):
        return "debugging_help"
    
    # Architectural/approach suggestions
    if any(pattern in content_lower for pattern in [
        'approach', 'strategy', 'pattern', 'architecture', 'design', 'structure'
    ]):
        return "approach_suggestion"
    
    # File/directory operations
    if any(pattern in content_lower for pattern in [
        'file', 'directory', 'folder', 'path', 'create', 'delete', 'move'
    ]):
        return "file_operation"
    
    return "general_guidance"


def analyze_conversation_adjacency(messages: List[Dict]) -> Tuple[List[Dict], ConversationContext]:
    """
    Analyze conversation flow and detect adjacency relationships.
    
    Processes entire conversation to establish:
    - Previous/next message relationships
    - Solution-feedback pair detection
    - Message sequence positioning
    - Context chain construction
    
    Args:
        messages: List of message dictionaries with id, type, content, etc.
        
    Returns:
        Tuple of (enhanced_messages, conversation_context)
    """
    if not messages:
        return [], ConversationContext(0, 0, 0, 0, 0, 0)
    
    enhanced_messages = []
    solution_attempts = 0
    feedback_messages = 0
    assistant_count = 0
    user_count = 0
    
    for i, message in enumerate(messages):
        # Create enhanced message with adjacency fields
        enhanced_message = message.copy()
        
        # Set adjacency relationships
        enhanced_message['previous_message_id'] = messages[i-1]['id'] if i > 0 else None
        enhanced_message['next_message_id'] = messages[i+1]['id'] if i < len(messages) - 1 else None
        enhanced_message['message_sequence_position'] = i
        
        # Count message types
        if message['type'] == 'assistant':
            assistant_count += 1
        elif message['type'] == 'user':
            user_count += 1
        
        # Analyze solution attempts from assistant
        if message['type'] == 'assistant':
            is_solution = is_solution_attempt(message['content'], 'assistant')
            enhanced_message['is_solution_attempt'] = is_solution
            
            if is_solution:
                solution_attempts += 1
                enhanced_message['solution_category'] = classify_solution_type(message['content'])
                
                # Check next message for user feedback
                if i < len(messages) - 1:
                    next_message = messages[i+1]
                    if next_message['type'] == 'user':
                        enhanced_message['feedback_message_id'] = next_message['id']
                        # Will be analyzed by feedback_learner module
            else:
                enhanced_message['solution_category'] = None
        
        # Analyze user feedback responses
        elif message['type'] == 'user' and i > 0:
            prev_message = messages[i-1]
            if (prev_message['type'] == 'assistant' and 
                is_solution_attempt(prev_message['content'], 'assistant')):
                
                enhanced_message['is_feedback_to_solution'] = True
                enhanced_message['related_solution_id'] = prev_message['id']
                feedback_messages += 1
            else:
                enhanced_message['is_feedback_to_solution'] = False
        
        enhanced_messages.append(enhanced_message)
    
    # Create conversation context
    context = ConversationContext(
        total_messages=len(messages),
        assistant_messages=assistant_count,
        user_messages=user_count,
        solution_attempts=solution_attempts,
        feedback_messages=feedback_messages,
        context_chain_length=len(messages)
    )
    
    return enhanced_messages, context


def build_context_chain(messages: List[Dict], anchor_message_id: str, chain_length: int = 5) -> List[Dict]:
    """
    Build context chain around a specific message.
    
    Args:
        messages: All messages in conversation
        anchor_message_id: ID of message to build chain around
        chain_length: Number of messages to include in each direction
        
    Returns:
        List of messages forming the context chain
    """
    # Find anchor message index
    anchor_index = None
    for i, msg in enumerate(messages):
        if msg['id'] == anchor_message_id:
            anchor_index = i
            break
    
    if anchor_index is None:
        return []
    
    # Calculate chain boundaries
    start_index = max(0, anchor_index - chain_length)
    end_index = min(len(messages), anchor_index + chain_length + 1)
    
    # Extract context chain
    context_chain = messages[start_index:end_index]
    
    # Mark the anchor message
    for msg in context_chain:
        msg['is_anchor'] = (msg['id'] == anchor_message_id)
    
    return context_chain


def detect_conversation_patterns(messages: List[Dict]) -> Dict[str, Any]:
    """
    Analyze conversation for common patterns.
    
    Args:
        messages: List of conversation messages
        
    Returns:
        Dictionary with pattern analysis results
    """
    enhanced_messages, context = analyze_conversation_adjacency(messages)
    
    # Calculate pattern metrics
    solution_success_rate = 0.0
    if context.solution_attempts > 0:
        # This would be calculated by feedback_learner after sentiment analysis
        successful_solutions = sum(1 for msg in enhanced_messages 
                                 if msg.get('is_validated_solution', False))
        solution_success_rate = successful_solutions / context.solution_attempts
    
    # Conversation flow analysis
    avg_response_length = sum(len(msg['content']) for msg in messages) / len(messages)
    
    # Solution complexity analysis
    complex_solutions = sum(1 for msg in enhanced_messages 
                          if (msg.get('is_solution_attempt', False) and 
                              len(msg['content']) > 500))
    
    return {
        'context': context,
        'solution_success_rate': solution_success_rate,
        'avg_response_length': avg_response_length,
        'complex_solutions': complex_solutions,
        'solution_density': context.solution_attempts / context.total_messages,
        'feedback_ratio': context.feedback_messages / max(context.solution_attempts, 1),
        'conversation_type': classify_conversation_type(enhanced_messages, context)
    }


def classify_conversation_type(messages: List[Dict], context: ConversationContext) -> str:
    """
    Classify the overall type/purpose of the conversation.
    
    Args:
        messages: Enhanced messages with adjacency analysis
        context: Conversation context information
        
    Returns:
        Conversation type classification
    """
    if context.solution_attempts >= context.total_messages * 0.6:
        return "solution_focused"
    elif context.feedback_messages >= context.solution_attempts * 0.8:
        return "iterative_debugging"
    elif context.total_messages > 20:
        return "extended_discussion"
    elif any("error" in msg['content'].lower() or "bug" in msg['content'].lower() 
             for msg in messages):
        return "troubleshooting"
    else:
        return "general_assistance"


def get_adjacency_summary(messages: List[Dict]) -> Dict[str, Any]:
    """
    Get comprehensive adjacency analysis summary.
    
    Args:
        messages: Conversation messages to analyze
        
    Returns:
        Complete adjacency analysis results
    """
    enhanced_messages, context = analyze_conversation_adjacency(messages)
    patterns = detect_conversation_patterns(messages)
    
    # Find solution-feedback pairs
    solution_feedback_pairs = []
    for msg in enhanced_messages:
        if msg.get('is_solution_attempt') and msg.get('feedback_message_id'):
            solution_feedback_pairs.append({
                'solution_id': msg['id'],
                'feedback_id': msg['feedback_message_id'],
                'solution_category': msg.get('solution_category'),
                'sequence_position': msg['message_sequence_position']
            })
    
    return {
        'context': context,
        'patterns': patterns,
        'solution_feedback_pairs': solution_feedback_pairs,
        'enhanced_messages': enhanced_messages,
        'adjacency_relationships': len([m for m in enhanced_messages 
                                      if m.get('previous_message_id') or m.get('next_message_id')])
    }