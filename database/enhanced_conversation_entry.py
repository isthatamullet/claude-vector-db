"""
Enhanced ConversationEntry with context awareness, topic detection, quality scoring,
adjacency tracking, and feedback learning capabilities.

This module extends the base ConversationEntry with sophisticated enhancement metadata
while maintaining backward compatibility with existing code.
"""

from dataclasses import dataclass, field
from typing import Dict, Optional, List
import json


@dataclass
class ConversationEntry:
    """Structured conversation entry with metadata"""
    id: str
    content: str
    type: str  # 'user' or 'assistant'
    project_path: str
    project_name: str
    timestamp: str
    timestamp_unix: Optional[float]  # Unix timestamp for fast filtering
    session_id: Optional[str]
    file_name: str
    has_code: bool
    tools_used: List[str]
    content_length: int


@dataclass
class SemanticValidationFields:
    """
    Semantic validation enhancement fields for advanced feedback analysis.
    
    Extends the existing validation system with semantic similarity, technical context,
    and multi-modal analysis capabilities targeting 98% explicit and 90% implicit
    feedback detection accuracy.
    """
    # Core semantic analysis results
    semantic_sentiment: Optional[str] = None          # "positive", "negative", "partial", "neutral"
    semantic_confidence: float = 0.0                  # 0.0-1.0 confidence score
    semantic_method: str = "none"                     # "semantic_similarity", "multi_modal", etc.
    
    # Similarity scores to pattern clusters
    positive_similarity: float = 0.0                 # Similarity to positive feedback patterns
    negative_similarity: float = 0.0                 # Similarity to negative feedback patterns  
    partial_similarity: float = 0.0                  # Similarity to partial success patterns
    
    # Technical context analysis
    technical_domain: Optional[str] = None            # "build_system", "testing", "runtime", "deployment"
    technical_confidence: float = 0.0                # Domain detection confidence
    complex_outcome_detected: bool = False           # Mixed success/failure scenarios
    
    # Multi-modal analysis results
    pattern_vs_semantic_agreement: float = 0.0       # Agreement score between methods
    primary_analysis_method: str = "pattern"         # "pattern", "semantic", "technical", "multi_modal"
    requires_manual_review: bool = False             # Flag for low-confidence results
    
    # Serialized complex data (JSON strings for ChromaDB compatibility)
    best_matching_patterns: str = "[]"               # JSON array of matching patterns
    semantic_analysis_details: str = "{}"            # JSON object with detailed analysis


@dataclass
class EnhancedConversationEntry(ConversationEntry):
    """
    Enhanced conversation entry with context awareness and feedback learning.
    
    Extends the base ConversationEntry with:
    - Topic detection and classification
    - Solution quality scoring
    - Adjacency relationship tracking
    - User feedback sentiment analysis
    - Solution validation learning
    """
    
    # Topic awareness fields
    detected_topics: Dict[str, float] = field(default_factory=dict)
    primary_topic: Optional[str] = None
    topic_confidence: float = 0.0
    
    # Solution quality fields
    solution_quality_score: float = 1.0
    has_success_markers: bool = False
    has_quality_indicators: bool = False
    
    # Adjacency tracking fields
    previous_message_id: Optional[str] = None
    next_message_id: Optional[str] = None
    message_sequence_position: int = 0
    
    # Feedback learning fields
    user_feedback_sentiment: Optional[str] = None  # "positive", "negative", "partial", "neutral"
    is_validated_solution: bool = False
    is_refuted_attempt: bool = False
    validation_strength: float = 0.0
    outcome_certainty: float = 0.0
    
    # NEW: Semantic validation enhancement
    semantic_validation: SemanticValidationFields = field(default_factory=SemanticValidationFields)
    
    # Context chain relationships  
    is_solution_attempt: bool = False
    is_feedback_to_solution: bool = False
    related_solution_id: Optional[str] = None
    feedback_message_id: Optional[str] = None
    solution_category: Optional[str] = None  # "code_fix", "config_change", "approach_suggestion"
    
    # Advanced context analysis fields
    troubleshooting_context_score: float = 1.0  # Troubleshooting relevance boost factor
    realtime_learning_boost: float = 1.0        # Real-time learning boost factor
    
    def __post_init__(self):
        """Validate and auto-calculate enhancement fields"""
        
        # Validate topic scores are normalized 0.0-2.0
        if self.detected_topics:
            for topic, score in self.detected_topics.items():
                if score < 0.0 or score > 2.0:
                    raise ValueError(f"Topic score {score} out of range [0.0, 2.0] for topic {topic}")
        
        # Auto-calculate primary topic from detected topics
        if self.detected_topics and not self.primary_topic:
            self.primary_topic = max(self.detected_topics.items(), key=lambda x: x[1])[0]
            self.topic_confidence = self.detected_topics[self.primary_topic]
        
        # Validate solution quality score range
        if self.solution_quality_score < 0.1 or self.solution_quality_score > 3.0:
            raise ValueError(f"Solution quality score {self.solution_quality_score} out of range [0.1, 3.0]")
        
        # Validate validation strength range
        if abs(self.validation_strength) > 1.0:
            raise ValueError(f"Validation strength {self.validation_strength} out of range [-1.0, 1.0]")
        
        # Validate outcome certainty range
        if self.outcome_certainty < 0.0 or self.outcome_certainty > 1.0:
            raise ValueError(f"Outcome certainty {self.outcome_certainty} out of range [0.0, 1.0]")
        
        # Validate semantic validation fields
        if self.semantic_validation.semantic_confidence < 0.0 or self.semantic_validation.semantic_confidence > 1.0:
            raise ValueError(f"Semantic confidence {self.semantic_validation.semantic_confidence} out of range [0.0, 1.0]")
        
        if (self.semantic_validation.positive_similarity < 0.0 or self.semantic_validation.positive_similarity > 1.0 or
            self.semantic_validation.negative_similarity < 0.0 or self.semantic_validation.negative_similarity > 1.0 or
            self.semantic_validation.partial_similarity < 0.0 or self.semantic_validation.partial_similarity > 1.0):
            raise ValueError("Similarity scores must be in range [0.0, 1.0]")
        
        if self.semantic_validation.technical_confidence < 0.0 or self.semantic_validation.technical_confidence > 1.0:
            raise ValueError(f"Technical confidence {self.semantic_validation.technical_confidence} out of range [0.0, 1.0]")
        
        if self.semantic_validation.pattern_vs_semantic_agreement < 0.0 or self.semantic_validation.pattern_vs_semantic_agreement > 1.0:
            raise ValueError(f"Pattern vs semantic agreement {self.semantic_validation.pattern_vs_semantic_agreement} out of range [0.0, 1.0]")
    
    def get_topic_summary(self) -> str:
        """Get a human-readable summary of detected topics"""
        if not self.detected_topics:
            return "No topics detected"
        
        sorted_topics = sorted(self.detected_topics.items(), key=lambda x: x[1], reverse=True)
        top_topics = sorted_topics[:3]  # Show top 3 topics
        
        topic_strs = [f"{topic}({score:.2f})" for topic, score in top_topics]
        return ", ".join(topic_strs)
    
    def get_validation_status(self) -> str:
        """Get a human-readable validation status"""
        if self.is_validated_solution:
            return f"✅ Validated (strength: {self.validation_strength:.2f})"
        elif self.is_refuted_attempt:
            return f"❌ Refuted (strength: {abs(self.validation_strength):.2f})"
        elif self.validation_strength > 0:
            return f"🔄 Partial success (strength: {self.validation_strength:.2f})"
        else:
            return "⚪ Unvalidated"
    
    def calculate_enhancement_boost(self) -> float:
        """
        Calculate overall enhancement boost factor combining all enhancement features.
        
        Returns:
            Float boost factor (typically 0.3 to 3.0) to multiply with base relevance
        """
        boost = 1.0
        
        # Topic relevance boost (0% to 100% boost)
        if self.primary_topic and self.topic_confidence > 0.5:
            boost *= (1.0 + self.topic_confidence * 0.5)
        
        # Solution quality boost (up to 3x)
        boost *= self.solution_quality_score
        
        # Validation boost/penalty
        if self.is_validated_solution:
            boost *= (1.0 + self.validation_strength)  # Up to 2x boost
        elif self.is_refuted_attempt:
            boost *= max(0.3, 1.0 - abs(self.validation_strength))  # Down to 0.3x
        
        return min(boost, 5.0)  # Cap at 5x total boost
    
    def to_enhanced_metadata(self) -> Dict:
        """
        Convert enhancement fields to ChromaDB-compatible metadata dictionary.
        
        ChromaDB requires all metadata values to be non-null (Bool, Int, Float, or Str).
        Complex objects are JSON serialized, None values are converted to empty strings.
        """
        import json
        
        # Helper function to handle None values
        def safe_value(value, default=""):
            """Convert None values to ChromaDB-compatible defaults"""
            if value is None:
                return default
            return value
        
        base_metadata = {
            "type": self.type,
            "project_name": self.project_name,
            "project_path": self.project_path,
            "timestamp": self.timestamp,
            "timestamp_unix": self.timestamp_unix if self.timestamp_unix is not None else 0.0,
            "session_id": safe_value(self.session_id),
            "file_name": self.file_name,
            "has_code": self.has_code,
            "tools_used": json.dumps(self.tools_used),
            "content_length": self.content_length
        }
        
        # Add enhancement metadata (with None handling)
        enhancement_metadata = {
            # Topic fields
            "detected_topics": json.dumps(self.detected_topics),
            "primary_topic": safe_value(self.primary_topic),
            "topic_confidence": self.topic_confidence,
            
            # Quality fields
            "solution_quality_score": self.solution_quality_score,
            "has_success_markers": self.has_success_markers,
            "has_quality_indicators": self.has_quality_indicators,
            
            # Adjacency fields
            "previous_message_id": safe_value(self.previous_message_id),
            "next_message_id": safe_value(self.next_message_id),
            "message_sequence_position": self.message_sequence_position,
            "is_solution_attempt": self.is_solution_attempt,
            "is_feedback_to_solution": self.is_feedback_to_solution,
            
            # Feedback fields
            "user_feedback_sentiment": safe_value(self.user_feedback_sentiment),
            "is_validated_solution": self.is_validated_solution,
            "is_refuted_attempt": self.is_refuted_attempt,
            "validation_strength": self.validation_strength,
            "outcome_certainty": self.outcome_certainty,
            
            # Context chain fields
            "related_solution_id": safe_value(self.related_solution_id),
            "feedback_message_id": safe_value(self.feedback_message_id),
            "solution_category": safe_value(self.solution_category),
        }
        
        # Combine and return
        base_metadata.update(enhancement_metadata)
        return base_metadata
    
    def to_semantic_enhanced_metadata(self) -> Dict:
        """
        Convert enhancement fields to ChromaDB-compatible metadata dictionary with semantic validation.
        
        Extends the existing to_enhanced_metadata() with semantic validation fields for
        ChromaDB storage. All semantic validation fields are included for comprehensive
        semantic feedback analysis.
        
        Returns:
            Dictionary with all enhancement fields including semantic validation metadata
        """
        # Get base enhanced metadata
        base_metadata = self.to_enhanced_metadata()
        
        # Helper function to handle None values
        def safe_value(value, default=""):
            """Convert None values to ChromaDB-compatible defaults"""
            if value is None:
                return default
            return value
        
        # Add semantic validation fields
        semantic_fields = {
            # Core semantic analysis results
            "semantic_sentiment": safe_value(self.semantic_validation.semantic_sentiment),
            "semantic_confidence": self.semantic_validation.semantic_confidence,
            "semantic_method": self.semantic_validation.semantic_method,
            
            # Similarity scores to pattern clusters
            "positive_similarity": self.semantic_validation.positive_similarity,
            "negative_similarity": self.semantic_validation.negative_similarity,
            "partial_similarity": self.semantic_validation.partial_similarity,
            
            # Technical context analysis
            "technical_domain": safe_value(self.semantic_validation.technical_domain),
            "technical_confidence": self.semantic_validation.technical_confidence,
            "complex_outcome_detected": self.semantic_validation.complex_outcome_detected,
            
            # Multi-modal analysis results
            "pattern_vs_semantic_agreement": self.semantic_validation.pattern_vs_semantic_agreement,
            "primary_analysis_method": self.semantic_validation.primary_analysis_method,
            "requires_manual_review": self.semantic_validation.requires_manual_review,
            
            # Serialized complex data (JSON strings for ChromaDB compatibility)
            "best_matching_patterns": self.semantic_validation.best_matching_patterns,
            "semantic_analysis_details": self.semantic_validation.semantic_analysis_details
        }
        
        # Combine base metadata with semantic validation fields
        return {**base_metadata, **semantic_fields}
    
    @classmethod
    def from_base_entry(cls, base_entry: ConversationEntry, **enhancement_kwargs) -> 'EnhancedConversationEntry':
        """
        Create EnhancedConversationEntry from base ConversationEntry.
        
        Args:
            base_entry: Base ConversationEntry to enhance
            **enhancement_kwargs: Additional enhancement fields
            
        Returns:
            New EnhancedConversationEntry with base fields and enhancements
        """
        # Extract base fields
        base_fields = {
            'id': base_entry.id,
            'content': base_entry.content,
            'type': base_entry.type,
            'project_path': base_entry.project_path,
            'project_name': base_entry.project_name,
            'timestamp': base_entry.timestamp,
            'timestamp_unix': base_entry.timestamp_unix,
            'session_id': base_entry.session_id,
            'file_name': base_entry.file_name,
            'has_code': base_entry.has_code,
            'tools_used': base_entry.tools_used,
            'content_length': base_entry.content_length
        }
        
        # Combine with enhancement fields
        base_fields.update(enhancement_kwargs)
        
        return cls(**base_fields)


def create_enhanced_entry_from_dict(entry_dict: Dict, **enhancement_kwargs) -> EnhancedConversationEntry:
    """
    Create EnhancedConversationEntry directly from dictionary data.
    
    Args:
        entry_dict: Dictionary with conversation entry data
        **enhancement_kwargs: Additional enhancement fields
        
    Returns:
        New EnhancedConversationEntry
    """
    # Parse complex fields that might be JSON strings
    import json
    
    # Handle tools_used JSON parsing
    tools_used = entry_dict.get('tools_used', [])
    if isinstance(tools_used, str):
        try:
            tools_used = json.loads(tools_used)
        except (json.JSONDecodeError, TypeError):
            tools_used = []
    
    # Handle detected_topics JSON parsing
    detected_topics = enhancement_kwargs.get('detected_topics', {})
    if isinstance(detected_topics, str):
        try:
            detected_topics = json.loads(detected_topics)
        except (json.JSONDecodeError, TypeError):
            detected_topics = {}
        enhancement_kwargs['detected_topics'] = detected_topics
    
    # Create entry with parsed data
    entry_data = {
        'id': entry_dict.get('id', ''),
        'content': entry_dict.get('content', ''),
        'type': entry_dict.get('type', 'unknown'),
        'project_path': entry_dict.get('project_path', 'unknown'),
        'project_name': entry_dict.get('project_name', 'unknown'),
        'timestamp': entry_dict.get('timestamp', ''),
        'timestamp_unix': entry_dict.get('timestamp_unix'),
        'session_id': entry_dict.get('session_id'),
        'file_name': entry_dict.get('file_name', 'unknown'),
        'has_code': entry_dict.get('has_code', False),
        'tools_used': tools_used,
        'content_length': entry_dict.get('content_length', 0)
    }
    
    # Add enhancement fields
    entry_data.update(enhancement_kwargs)
    
    return EnhancedConversationEntry(**entry_data)