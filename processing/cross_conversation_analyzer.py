#!/usr/bin/env python3
"""
Cross-Conversation Behavioral Analyzer for Adaptive Learning Validation System
Analyzes patterns across multiple conversation sessions to identify behavioral trends.

Based on PRP-3: Adaptive Learning Validation System (July 2025)
Leverages existing vector database for conversation history and behavioral pattern recognition.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict

# Existing system integration
from database.vector_database import ClaudeVectorDatabase
from database.enhanced_conversation_entry import ConversationEntry, EnhancedConversationEntry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class BehavioralPattern:
    """
    Behavioral pattern detected across conversations.
    
    Captures user behavioral trends, satisfaction patterns,
    and communication style evolution over time.
    """
    pattern_type: str  # 'satisfaction_trend', 'communication_evolution', 'solution_preference'
    pattern_strength: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    supporting_evidence: List[str] = field(default_factory=list)
    contradicting_evidence: List[str] = field(default_factory=list)
    temporal_trend: str = "stable"  # 'improving', 'declining', 'stable', 'volatile'
    first_observed: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    def get_pattern_reliability(self) -> float:
        """Calculate reliability of this behavioral pattern"""
        evidence_ratio = len(self.supporting_evidence) / max(1, len(self.supporting_evidence) + len(self.contradicting_evidence))
        return self.confidence * evidence_ratio * self.pattern_strength


@dataclass
class UserBehavioralProfile:
    """
    Comprehensive behavioral profile for a user across conversations.
    
    Tracks satisfaction patterns, communication evolution, solution preferences,
    and genuine vs polite feedback indicators.
    """
    user_id: str
    total_conversations: int = 0
    conversation_sessions: List[str] = field(default_factory=list)
    
    # Satisfaction pattern analysis
    satisfaction_reliability_score: float = 0.5  # How reliable user feedback is
    genuine_satisfaction_markers: List[str] = field(default_factory=list)
    polite_response_markers: List[str] = field(default_factory=list)
    
    # Communication evolution tracking
    communication_style_evolution: Dict[str, List[float]] = field(default_factory=dict)
    directness_trend: str = "stable"  # 'increasing', 'decreasing', 'stable'
    politeness_trend: str = "stable"  # 'increasing', 'decreasing', 'stable'
    
    # Behavioral patterns
    detected_patterns: List[BehavioralPattern] = field(default_factory=list)
    
    # Solution preferences
    preferred_solution_types: Dict[str, float] = field(default_factory=dict)
    solution_success_correlation: Dict[str, float] = field(default_factory=dict)
    
    # Cross-session insights
    session_satisfaction_trend: List[float] = field(default_factory=list)
    follow_up_behavior_patterns: Dict[str, int] = field(default_factory=dict)
    
    # Profile metadata
    profile_created: datetime = field(default_factory=datetime.now)
    last_analysis: Optional[datetime] = None
    analysis_confidence: float = 0.0
    
    def get_behavioral_confidence(self) -> float:
        """Calculate overall confidence in behavioral analysis"""
        if self.total_conversations < 3:
            return 0.2  # Low confidence with few conversations
        elif self.total_conversations < 10:
            base_confidence = 0.6  # Medium confidence
        else:
            base_confidence = min(0.95, 0.4 + (self.total_conversations * 0.02))
        
        # Adjust based on pattern reliability
        if self.detected_patterns:
            avg_pattern_reliability = np.mean([p.get_pattern_reliability() for p in self.detected_patterns])
            base_confidence = (base_confidence + avg_pattern_reliability) / 2
        
        return base_confidence


class CrossConversationAnalyzer:
    """
    Analyzes patterns across multiple conversation sessions.
    
    Provides behavioral pattern recognition, satisfaction trend analysis,
    and cross-session intelligence for improved validation accuracy.
    """
    
    def __init__(self):
        # Integration with existing vector database
        self.vector_db = ClaudeVectorDatabase()
        
        # User behavioral profiles
        self.user_profiles: Dict[str, UserBehavioralProfile] = {}
        
        # Pattern detection algorithms
        self.pattern_detectors = {
            'satisfaction_trend': self._detect_satisfaction_trend,
            'communication_evolution': self._detect_communication_evolution,
            'solution_preference': self._detect_solution_preferences,
            'feedback_reliability': self._detect_feedback_reliability,
            'follow_up_behavior': self._detect_follow_up_patterns
        }
        
        # Performance tracking
        self.processing_stats = {
            'total_analyses': 0,
            'behavioral_patterns_detected': 0,
            'cross_session_insights_generated': 0,
            'average_processing_time': 0.0,
            'performance_violations': 0
        }
        
        # Configuration
        self.config = {
            'min_conversations_for_analysis': 3,
            'lookback_days': 30,
            'satisfaction_trend_threshold': 0.15,
            'communication_evolution_threshold': 0.1,
            'pattern_confidence_threshold': 0.3
        }
        
        logger.info("🔄 Cross-Conversation Analyzer initialized")
    
    def analyze_user_behavior_patterns(self, user_id: str, current_feedback: str, 
                                     solution_context: Dict[str, Any], 
                                     lookback_days: int = 30) -> Dict[str, Any]:
        """
        Analyze user behavioral patterns across conversations.
        
        Args:
            user_id: User identifier
            current_feedback: Current feedback text
            solution_context: Context about current solution
            lookback_days: How far back to analyze conversations
            
        Returns:
            Dictionary with behavioral analysis results
        """
        # PERFORMANCE: Start timing for <200ms requirement
        start_time = time.time()
        
        try:
            # Get user's conversation history
            user_conversations = self._get_user_conversation_history(user_id, lookback_days)
            
            if len(user_conversations) < self.config['min_conversations_for_analysis']:
                processing_time = time.time() - start_time
                return {
                    'behavioral_analysis_available': False,
                    'reason': 'insufficient_conversation_history',
                    'user_id': user_id,
                    'conversation_count': len(user_conversations),
                    'min_required': self.config['min_conversations_for_analysis'],
                    'processing_time': processing_time,
                    'performance_compliant': processing_time <= 0.2
                }
            
            # Get or create user behavioral profile
            if user_id not in self.user_profiles:
                self.user_profiles[user_id] = UserBehavioralProfile(user_id)
            
            user_profile = self.user_profiles[user_id]
            
            # Update profile with conversation history
            self._update_behavioral_profile(user_profile, user_conversations, current_feedback, solution_context)
            
            # Detect behavioral patterns
            behavioral_patterns = self._detect_all_behavioral_patterns(user_profile, user_conversations)
            
            # Analyze satisfaction reliability
            satisfaction_analysis = self._analyze_satisfaction_reliability(user_profile, user_conversations)
            
            # Generate behavioral insights
            behavioral_insights = self._generate_behavioral_insights(user_profile, behavioral_patterns)
            
            # Calculate behavioral trend adjustments
            trend_adjustments = self._calculate_behavioral_trend_adjustments(
                user_profile, current_feedback, solution_context
            )
            
            # Performance tracking
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, behavioral_patterns)
            
            # Validate performance requirement
            performance_compliant = processing_time <= 0.2
            if not performance_compliant:
                self.processing_stats['performance_violations'] += 1
                logger.warning(f"⚠️ Cross-conversation analysis exceeded 200ms: {processing_time:.3f}s")
            
            return {
                'behavioral_analysis_available': True,
                'user_id': user_id,
                'conversation_count': len(user_conversations),
                'behavioral_confidence': user_profile.get_behavioral_confidence(),
                
                # Behavioral patterns
                'detected_patterns': [
                    {
                        'type': pattern.pattern_type,
                        'strength': pattern.pattern_strength,
                        'confidence': pattern.confidence,
                        'trend': pattern.temporal_trend,
                        'reliability': pattern.get_pattern_reliability(),
                        'evidence_count': len(pattern.supporting_evidence)
                    }
                    for pattern in behavioral_patterns
                ],
                
                # Satisfaction analysis
                'satisfaction_reliability': satisfaction_analysis,
                'genuine_vs_polite_analysis': self._analyze_genuine_vs_polite_feedback(
                    user_profile, current_feedback
                ),
                
                # Behavioral insights
                'behavioral_insights': behavioral_insights,
                
                # Trend adjustments
                'satisfaction_trend_adjustment': trend_adjustments.get('satisfaction_trend', 1.0),
                'communication_style_adjustment': trend_adjustments.get('communication_style', 1.0),
                'solution_preference_boost': trend_adjustments.get('solution_preference', 1.0),
                
                # Profile evolution
                'communication_evolution': {
                    'directness_trend': user_profile.directness_trend,
                    'politeness_trend': user_profile.politeness_trend,
                    'evolution_data': user_profile.communication_style_evolution
                },
                
                # Solution preferences
                'preferred_solution_types': user_profile.preferred_solution_types,
                'solution_success_correlation': user_profile.solution_success_correlation,
                
                # Performance metrics
                'processing_time': processing_time,
                'performance_compliant': performance_compliant,
                'analysis_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in cross-conversation analysis for {user_id}: {e}")
            return {
                'error': str(e),
                'behavioral_analysis_available': False,
                'user_id': user_id,
                'processing_time': processing_time,
                'performance_compliant': processing_time <= 0.2
            }
    
    def _get_user_conversation_history(self, user_id: str, lookback_days: int) -> List[Dict[str, Any]]:
        """Get user's conversation history from vector database"""
        try:
            # Use existing vector database search capabilities
            # Search for conversations involving this user
            user_conversations = []
            
            # Search for user messages
            user_results = self.vector_db.search_conversations(
                query=f"user_id:{user_id}",
                limit=50,
                include_metadata=True
            )
            
            # Filter and process results
            cutoff_date = datetime.now() - timedelta(days=lookback_days)
            
            for result in user_results:
                # Extract conversation data
                conversation_data = {
                    'id': result.get('id', ''),
                    'content': result.get('content', ''),
                    'type': result.get('type', ''),
                    'timestamp': result.get('timestamp', ''),
                    'session_id': result.get('session_id', ''),
                    'project_name': result.get('project_name', ''),
                    'has_code': result.get('has_code', False),
                    'enhancement_analysis': result.get('enhancement_analysis', {}),
                    'metadata': result.get('metadata', {})
                }
                
                # Check if within lookback period
                try:
                    if conversation_data['timestamp']:
                        msg_time = datetime.fromisoformat(conversation_data['timestamp'])
                        if msg_time >= cutoff_date:
                            user_conversations.append(conversation_data)
                except ValueError:
                    # Skip if timestamp parsing fails
                    continue
            
            # Sort by timestamp (newest first)
            user_conversations.sort(
                key=lambda x: x.get('timestamp', ''), 
                reverse=True
            )
            
            return user_conversations[:30]  # Limit to 30 most recent conversations
            
        except Exception as e:
            logger.warning(f"Failed to get conversation history for {user_id}: {e}")
            return []
    
    def _update_behavioral_profile(self, profile: UserBehavioralProfile, 
                                 conversations: List[Dict[str, Any]], 
                                 current_feedback: str, 
                                 solution_context: Dict[str, Any]):
        """Update behavioral profile with conversation data"""
        profile.total_conversations = len(conversations)
        profile.last_analysis = datetime.now()
        
        # Extract session IDs
        session_ids = list(set(conv.get('session_id', '') for conv in conversations if conv.get('session_id')))
        profile.conversation_sessions = session_ids[:20]  # Keep most recent 20 sessions
        
        # Analyze satisfaction trends
        satisfaction_scores = []
        for conv in conversations:
            enhancement = conv.get('enhancement_analysis', {})
            if 'validation_boost' in enhancement:
                satisfaction_scores.append(enhancement['validation_boost'])
            elif 'user_feedback_sentiment' in enhancement:
                # Convert sentiment to numeric score
                sentiment = enhancement['user_feedback_sentiment']
                if sentiment == 'positive':
                    satisfaction_scores.append(0.8)
                elif sentiment == 'negative':
                    satisfaction_scores.append(0.2)
                elif sentiment == 'partial':
                    satisfaction_scores.append(0.6)
                else:
                    satisfaction_scores.append(0.5)
        
        profile.session_satisfaction_trend = satisfaction_scores[-10:]  # Keep last 10
        
        # Track communication style evolution
        self._track_communication_evolution(profile, conversations, current_feedback)
        
        # Update solution preferences
        self._update_solution_preferences(profile, conversations, solution_context)
        
        # Analyze follow-up behaviors
        self._analyze_follow_up_behaviors(profile, conversations)
    
    def _track_communication_evolution(self, profile: UserBehavioralProfile, 
                                     conversations: List[Dict[str, Any]], 
                                     current_feedback: str):
        """Track evolution of communication style over time"""
        # Initialize evolution tracking if needed
        if 'directness' not in profile.communication_style_evolution:
            profile.communication_style_evolution = {
                'directness': [],
                'politeness': [],
                'sentiment_expression': [],
                'timestamps': []
            }
        
        # Analyze current feedback
        current_directness = self._calculate_directness_score(current_feedback)
        current_politeness = self._calculate_politeness_score(current_feedback)
        current_sentiment_expression = self._calculate_sentiment_expression_score(current_feedback)
        
        # Add to evolution tracking
        profile.communication_style_evolution['directness'].append(current_directness)
        profile.communication_style_evolution['politeness'].append(current_politeness)
        profile.communication_style_evolution['sentiment_expression'].append(current_sentiment_expression)
        profile.communication_style_evolution['timestamps'].append(datetime.now().isoformat())
        
        # Keep only recent data (last 20 interactions)
        for key in profile.communication_style_evolution:
            profile.communication_style_evolution[key] = profile.communication_style_evolution[key][-20:]
        
        # Calculate trends
        profile.directness_trend = self._calculate_trend(profile.communication_style_evolution['directness'])
        profile.politeness_trend = self._calculate_trend(profile.communication_style_evolution['politeness'])
    
    def _calculate_directness_score(self, text: str) -> float:
        """Calculate directness score for text"""
        direct_indicators = ['exactly', 'clearly', 'definitely', 'obviously', 'wrong', 'right', 'no', 'yes']
        indirect_indicators = ['maybe', 'perhaps', 'might', 'could', 'somewhat', 'kind of', 'sort of']
        
        text_lower = text.lower()
        direct_count = sum(1 for word in direct_indicators if word in text_lower)
        indirect_count = sum(1 for word in indirect_indicators if word in text_lower)
        
        if direct_count + indirect_count == 0:
            return 0.5  # Neutral
        
        return direct_count / (direct_count + indirect_count)
    
    def _calculate_politeness_score(self, text: str) -> float:
        """Calculate politeness score for text"""
        polite_indicators = ['please', 'thank', 'appreciate', 'kindly', 'sorry', 'excuse', 'pardon']
        casual_indicators = ['hey', 'yeah', 'ok', 'sure', 'cool', 'awesome', 'great']
        
        text_lower = text.lower()
        polite_count = sum(1 for word in polite_indicators if word in text_lower)
        casual_count = sum(1 for word in casual_indicators if word in text_lower)
        
        if polite_count + casual_count == 0:
            return 0.5  # Neutral
        
        return polite_count / (polite_count + casual_count)
    
    def _calculate_sentiment_expression_score(self, text: str) -> float:
        """Calculate how expressively sentiment is communicated"""
        strong_positive = ['excellent', 'perfect', 'amazing', 'brilliant', 'fantastic']
        strong_negative = ['terrible', 'awful', 'horrible', 'useless', 'broken']
        mild_positive = ['good', 'nice', 'helpful', 'works']
        mild_negative = ['issue', 'problem', 'concern', 'not quite']
        
        text_lower = text.lower()
        
        strong_pos_count = sum(1 for word in strong_positive if word in text_lower)
        strong_neg_count = sum(1 for word in strong_negative if word in text_lower)
        mild_pos_count = sum(1 for word in mild_positive if word in text_lower)
        mild_neg_count = sum(1 for word in mild_negative if word in text_lower)
        
        total_sentiment = strong_pos_count + strong_neg_count + mild_pos_count + mild_neg_count
        if total_sentiment == 0:
            return 0.5  # Neutral expression
        
        strong_sentiment = strong_pos_count + strong_neg_count
        return strong_sentiment / total_sentiment
    
    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction from sequence of values"""
        if len(values) < 3:
            return 'stable'
        
        # Calculate linear trend
        x = np.arange(len(values))
        y = np.array(values)
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > self.config['communication_evolution_threshold']:
            return 'increasing'
        elif slope < -self.config['communication_evolution_threshold']:
            return 'decreasing'
        else:
            return 'stable'
    
    def _update_solution_preferences(self, profile: UserBehavioralProfile, 
                                   conversations: List[Dict[str, Any]], 
                                   current_solution_context: Dict[str, Any]):
        """Update user's solution type preferences"""
        solution_feedback = []
        
        for conv in conversations:
            if conv.get('type') == 'assistant' and conv.get('has_code'):
                enhancement = conv.get('enhancement_analysis', {})
                solution_type = self._classify_solution_type(conv.get('content', ''))
                
                # Get feedback from subsequent user message
                feedback_quality = enhancement.get('validation_boost', 0.5)
                solution_feedback.append((solution_type, feedback_quality))
        
        # Update preferences based on feedback
        solution_scores = defaultdict(list)
        for solution_type, quality in solution_feedback:
            solution_scores[solution_type].append(quality)
        
        # Calculate average success for each solution type
        for solution_type, scores in solution_scores.items():
            avg_score = np.mean(scores)
            profile.preferred_solution_types[solution_type] = avg_score
            profile.solution_success_correlation[solution_type] = len(scores)
    
    def _classify_solution_type(self, solution_content: str) -> str:
        """Classify solution type based on content"""
        content_lower = solution_content.lower()
        
        if any(word in content_lower for word in ['test', 'spec', 'describe', 'it(']):
            return 'testing'
        elif any(word in content_lower for word in ['function', 'def ', 'const ', 'let ']):
            return 'code_implementation'
        elif any(word in content_lower for word in ['config', 'setting', 'setup']):
            return 'configuration'
        elif any(word in content_lower for word in ['debug', 'fix', 'error', 'bug']):
            return 'debugging'
        elif any(word in content_lower for word in ['install', 'npm', 'pip', 'dependency']):
            return 'environment_setup'
        else:
            return 'general_advice'
    
    def _analyze_follow_up_behaviors(self, profile: UserBehavioralProfile, 
                                   conversations: List[Dict[str, Any]]):
        """Analyze follow-up behavior patterns"""
        follow_up_patterns = defaultdict(int)
        
        # Group conversations by session
        sessions = defaultdict(list)
        for conv in conversations:
            session_id = conv.get('session_id', 'unknown')
            sessions[session_id].append(conv)
        
        # Analyze follow-up patterns within sessions
        for session_id, session_convs in sessions.items():
            session_convs.sort(key=lambda x: x.get('timestamp', ''))
            
            for i, conv in enumerate(session_convs[:-1]):
                if conv.get('type') == 'assistant':
                    next_conv = session_convs[i + 1]
                    if next_conv.get('type') == 'user':
                        # Analyze follow-up type
                        follow_up_type = self._classify_follow_up_type(next_conv.get('content', ''))
                        follow_up_patterns[follow_up_type] += 1
        
        profile.follow_up_behavior_patterns = dict(follow_up_patterns)
    
    def _classify_follow_up_type(self, follow_up_content: str) -> str:
        """Classify type of follow-up message"""
        content_lower = follow_up_content.lower()
        
        if any(word in content_lower for word in ['thank', 'great', 'perfect', 'works']):
            return 'positive_confirmation'
        elif any(word in content_lower for word in ['error', 'failed', 'not work', 'issue']):
            return 'problem_report'
        elif any(word in content_lower for word in ['what about', 'also', 'additionally', 'how to']):
            return 'additional_question'
        elif any(word in content_lower for word in ['clarify', 'explain', 'mean', 'understand']):
            return 'clarification_request'
        else:
            return 'other'
    
    def _detect_all_behavioral_patterns(self, profile: UserBehavioralProfile, 
                                      conversations: List[Dict[str, Any]]) -> List[BehavioralPattern]:
        """Detect all behavioral patterns for the user"""
        detected_patterns = []
        
        for pattern_type, detector in self.pattern_detectors.items():
            try:
                pattern = detector(profile, conversations)
                if pattern and pattern.confidence >= self.config['pattern_confidence_threshold']:
                    detected_patterns.append(pattern)
            except Exception as e:
                logger.warning(f"Pattern detection failed for {pattern_type}: {e}")
        
        profile.detected_patterns = detected_patterns
        return detected_patterns
    
    def _detect_satisfaction_trend(self, profile: UserBehavioralProfile, 
                                 conversations: List[Dict[str, Any]]) -> Optional[BehavioralPattern]:
        """Detect satisfaction trend pattern"""
        if len(profile.session_satisfaction_trend) < 3:
            return None
        
        # Calculate trend
        x = np.arange(len(profile.session_satisfaction_trend))
        y = np.array(profile.session_satisfaction_trend)
        slope = np.polyfit(x, y, 1)[0]
        
        if abs(slope) < self.config['satisfaction_trend_threshold']:
            return None  # No significant trend
        
        trend_direction = 'improving' if slope > 0 else 'declining'
        pattern_strength = min(1.0, abs(slope) * 2)  # Scale to 0-1
        confidence = min(1.0, len(profile.session_satisfaction_trend) / 10.0)  # More data = higher confidence
        
        return BehavioralPattern(
            pattern_type='satisfaction_trend',
            pattern_strength=pattern_strength,
            confidence=confidence,
            temporal_trend=trend_direction,
            supporting_evidence=[f"Satisfaction trend slope: {slope:.3f}"],
            first_observed=datetime.now() - timedelta(days=len(profile.session_satisfaction_trend)),
            last_updated=datetime.now()
        )
    
    def _detect_communication_evolution(self, profile: UserBehavioralProfile, 
                                      conversations: List[Dict[str, Any]]) -> Optional[BehavioralPattern]:
        """Detect communication style evolution pattern"""
        evolution = profile.communication_style_evolution
        if not evolution or len(evolution.get('directness', [])) < 5:
            return None
        
        # Check for significant evolution in any dimension
        directness_trend = profile.directness_trend
        politeness_trend = profile.politeness_trend
        
        if directness_trend == 'stable' and politeness_trend == 'stable':
            return None
        
        pattern_strength = 0.5  # Base strength for detected evolution
        confidence = min(1.0, len(evolution['directness']) / 15.0)
        
        evidence = []
        if directness_trend != 'stable':
            evidence.append(f"Directness trend: {directness_trend}")
        if politeness_trend != 'stable':
            evidence.append(f"Politeness trend: {politeness_trend}")
        
        return BehavioralPattern(
            pattern_type='communication_evolution',
            pattern_strength=pattern_strength,
            confidence=confidence,
            temporal_trend='evolving',
            supporting_evidence=evidence,
            first_observed=datetime.now() - timedelta(days=len(evolution['directness']) * 2),
            last_updated=datetime.now()
        )
    
    def _detect_solution_preferences(self, profile: UserBehavioralProfile, 
                                   conversations: List[Dict[str, Any]]) -> Optional[BehavioralPattern]:
        """Detect solution type preferences pattern"""
        if not profile.preferred_solution_types:
            return None
        
        # Find strongest preference
        best_solution_type = max(profile.preferred_solution_types.items(), key=lambda x: x[1])
        worst_solution_type = min(profile.preferred_solution_types.items(), key=lambda x: x[1])
        
        preference_gap = best_solution_type[1] - worst_solution_type[1]
        if preference_gap < 0.2:  # Not significant enough
            return None
        
        pattern_strength = min(1.0, preference_gap)
        confidence = min(1.0, sum(profile.solution_success_correlation.values()) / 20.0)
        
        return BehavioralPattern(
            pattern_type='solution_preference',
            pattern_strength=pattern_strength,
            confidence=confidence,
            temporal_trend='stable',
            supporting_evidence=[
                f"Prefers {best_solution_type[0]} (score: {best_solution_type[1]:.2f})",
                f"Less effective with {worst_solution_type[0]} (score: {worst_solution_type[1]:.2f})"
            ],
            first_observed=profile.profile_created,
            last_updated=datetime.now()
        )
    
    def _detect_feedback_reliability(self, profile: UserBehavioralProfile, 
                                   conversations: List[Dict[str, Any]]) -> Optional[BehavioralPattern]:
        """Detect feedback reliability pattern"""
        follow_up_patterns = profile.follow_up_behavior_patterns
        total_follow_ups = sum(follow_up_patterns.values())
        
        if total_follow_ups < 5:
            return None
        
        # Calculate reliability indicators
        positive_confirmations = follow_up_patterns.get('positive_confirmation', 0)
        problem_reports = follow_up_patterns.get('problem_report', 0)
        
        reliability_score = positive_confirmations / (positive_confirmations + problem_reports + 1)
        profile.satisfaction_reliability_score = reliability_score
        
        if reliability_score > 0.8:
            reliability_level = 'high'
        elif reliability_score > 0.5:
            reliability_level = 'medium'
        else:
            reliability_level = 'low'
        
        return BehavioralPattern(
            pattern_type='feedback_reliability',
            pattern_strength=abs(reliability_score - 0.5) * 2,  # Distance from neutral
            confidence=min(1.0, total_follow_ups / 20.0),
            temporal_trend='stable',
            supporting_evidence=[
                f"Reliability level: {reliability_level} ({reliability_score:.2f})",
                f"Follow-up patterns: {follow_up_patterns}"
            ],
            first_observed=profile.profile_created,
            last_updated=datetime.now()
        )
    
    def _detect_follow_up_patterns(self, profile: UserBehavioralProfile, 
                                 conversations: List[Dict[str, Any]]) -> Optional[BehavioralPattern]:
        """Detect follow-up behavior patterns"""
        follow_up_patterns = profile.follow_up_behavior_patterns
        total_follow_ups = sum(follow_up_patterns.values())
        
        if total_follow_ups < 3:
            return None
        
        # Find dominant follow-up pattern
        dominant_pattern = max(follow_up_patterns.items(), key=lambda x: x[1])
        dominance_ratio = dominant_pattern[1] / total_follow_ups
        
        if dominance_ratio < 0.4:  # No clear dominant pattern
            return None
        
        return BehavioralPattern(
            pattern_type='follow_up_behavior',
            pattern_strength=dominance_ratio,
            confidence=min(1.0, total_follow_ups / 15.0),
            temporal_trend='stable',
            supporting_evidence=[
                f"Dominant pattern: {dominant_pattern[0]} ({dominance_ratio:.1%} of follow-ups)",
                f"Total follow-up interactions: {total_follow_ups}"
            ],
            first_observed=profile.profile_created,
            last_updated=datetime.now()
        )
    
    def _analyze_satisfaction_reliability(self, profile: UserBehavioralProfile, 
                                        conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze reliability of user satisfaction feedback"""
        return {
            'reliability_score': profile.satisfaction_reliability_score,
            'reliability_level': (
                'high' if profile.satisfaction_reliability_score > 0.8 else
                'medium' if profile.satisfaction_reliability_score > 0.5 else
                'low'
            ),
            'follow_up_behavior_patterns': profile.follow_up_behavior_patterns,
            'genuine_satisfaction_markers': profile.genuine_satisfaction_markers,
            'polite_response_markers': profile.polite_response_markers
        }
    
    def _analyze_genuine_vs_polite_feedback(self, profile: UserBehavioralProfile, 
                                          current_feedback: str) -> Dict[str, Any]:
        """Analyze if current feedback is genuine or polite"""
        # Simple heuristics for genuine vs polite feedback
        feedback_lower = current_feedback.lower()
        
        # Genuine positive indicators
        genuine_positive = ['works perfect', 'exactly what', 'solved', 'fixed', 'brilliant', 'awesome']
        # Polite positive indicators  
        polite_positive = ['thank you', 'appreciate', 'helpful', 'nice']
        
        # Genuine negative indicators
        genuine_negative = ['doesn\'t work', 'broken', 'failed', 'error', 'wrong']
        # Polite negative indicators
        polite_negative = ['not quite', 'perhaps', 'might be', 'could be better']
        
        genuine_pos_count = sum(1 for phrase in genuine_positive if phrase in feedback_lower)
        polite_pos_count = sum(1 for phrase in polite_positive if phrase in feedback_lower)
        genuine_neg_count = sum(1 for phrase in genuine_negative if phrase in feedback_lower)
        polite_neg_count = sum(1 for phrase in polite_negative if phrase in feedback_lower)
        
        total_genuine = genuine_pos_count + genuine_neg_count
        total_polite = polite_pos_count + polite_neg_count
        
        if total_genuine + total_polite == 0:
            genuineness_score = 0.5  # Neutral
        else:
            genuineness_score = total_genuine / (total_genuine + total_polite)
        
        return {
            'genuineness_score': genuineness_score,
            'feedback_type': (
                'genuine' if genuineness_score > 0.6 else
                'polite' if genuineness_score < 0.4 else
                'mixed'
            ),
            'genuine_indicators': genuine_pos_count + genuine_neg_count,
            'polite_indicators': polite_pos_count + polite_neg_count
        }
    
    def _generate_behavioral_insights(self, profile: UserBehavioralProfile, 
                                    patterns: List[BehavioralPattern]) -> Dict[str, Any]:
        """Generate behavioral insights from detected patterns"""
        insights = {
            'user_reliability': profile.satisfaction_reliability_score,
            'communication_maturity': self._calculate_communication_maturity(profile),
            'solution_expertise': self._calculate_solution_expertise(profile),
            'engagement_level': self._calculate_engagement_level(profile),
            'behavioral_consistency': self._calculate_behavioral_consistency(patterns)
        }
        
        # Generate recommendations
        recommendations = []
        if profile.satisfaction_reliability_score < 0.5:
            recommendations.append("Monitor follow-up behavior to validate feedback accuracy")
        if profile.directness_trend == 'decreasing':
            recommendations.append("User becoming less direct - may need to amplify subtle signals")
        if any(p.pattern_type == 'solution_preference' for p in patterns):
            pref_pattern = next(p for p in patterns if p.pattern_type == 'solution_preference')
            recommendations.append(f"User shows strong solution preferences - leverage pattern insights")
        
        insights['recommendations'] = recommendations
        return insights
    
    def _calculate_communication_maturity(self, profile: UserBehavioralProfile) -> float:
        """Calculate communication maturity score"""
        maturity_factors = []
        
        # Consistency in communication style
        if profile.communication_style_evolution.get('directness'):
            directness_std = np.std(profile.communication_style_evolution['directness'])
            maturity_factors.append(1.0 - min(1.0, directness_std * 2))  # Lower variance = higher maturity
        
        # Feedback reliability
        maturity_factors.append(profile.satisfaction_reliability_score)
        
        # Length of interaction history
        history_maturity = min(1.0, profile.total_conversations / 20.0)
        maturity_factors.append(history_maturity)
        
        return np.mean(maturity_factors) if maturity_factors else 0.5
    
    def _calculate_solution_expertise(self, profile: UserBehavioralProfile) -> float:
        """Calculate user's solution domain expertise"""
        if not profile.preferred_solution_types:
            return 0.5
        
        # Higher variance in solution preferences indicates broader expertise
        preference_values = list(profile.preferred_solution_types.values())
        if len(preference_values) > 1:
            expertise_score = 1.0 - (np.std(preference_values) / np.mean(preference_values))
        else:
            expertise_score = 0.5
        
        return max(0.0, min(1.0, expertise_score))
    
    def _calculate_engagement_level(self, profile: UserBehavioralProfile) -> float:
        """Calculate user engagement level"""
        # Based on follow-up behavior patterns
        follow_up_total = sum(profile.follow_up_behavior_patterns.values())
        if follow_up_total == 0:
            return 0.3  # Low engagement if no follow-ups
        
        # Higher engagement if user asks follow-up questions and provides feedback
        engaged_behaviors = (
            profile.follow_up_behavior_patterns.get('additional_question', 0) +
            profile.follow_up_behavior_patterns.get('clarification_request', 0) +
            profile.follow_up_behavior_patterns.get('positive_confirmation', 0)
        )
        
        engagement_score = engaged_behaviors / follow_up_total
        return max(0.1, min(1.0, engagement_score))
    
    def _calculate_behavioral_consistency(self, patterns: List[BehavioralPattern]) -> float:
        """Calculate behavioral consistency score"""
        if not patterns:
            return 0.5
        
        # Higher consistency if patterns have high confidence and agree with each other
        avg_confidence = np.mean([p.confidence for p in patterns])
        avg_reliability = np.mean([p.get_pattern_reliability() for p in patterns])
        
        return (avg_confidence + avg_reliability) / 2.0
    
    def _calculate_behavioral_trend_adjustments(self, profile: UserBehavioralProfile, 
                                              current_feedback: str, 
                                              solution_context: Dict[str, Any]) -> Dict[str, float]:
        """Calculate behavioral trend adjustments for validation"""
        adjustments = {}
        
        # Satisfaction trend adjustment
        if profile.session_satisfaction_trend:
            recent_satisfaction = np.mean(profile.session_satisfaction_trend[-3:])  # Last 3 sessions
            if recent_satisfaction > 0.7:
                adjustments['satisfaction_trend'] = 1.1  # Boost positive trends
            elif recent_satisfaction < 0.3:
                adjustments['satisfaction_trend'] = 0.9  # Dampen if recent dissatisfaction
            else:
                adjustments['satisfaction_trend'] = 1.0
        else:
            adjustments['satisfaction_trend'] = 1.0
        
        # Communication style adjustment
        directness_score = self._calculate_directness_score(current_feedback)
        user_typical_directness = np.mean(profile.communication_style_evolution.get('directness', [0.5]))
        
        if abs(directness_score - user_typical_directness) > 0.3:
            # Unusual directness level - may indicate stronger sentiment
            adjustments['communication_style'] = 1.2
        else:
            adjustments['communication_style'] = 1.0
        
        # Solution preference adjustment
        solution_type = self._classify_solution_type(solution_context.get('solution_content', ''))
        if solution_type in profile.preferred_solution_types:
            preference_score = profile.preferred_solution_types[solution_type]
            if preference_score > 0.7:
                adjustments['solution_preference'] = 1.15  # Boost for preferred solution types
            elif preference_score < 0.3:
                adjustments['solution_preference'] = 0.85  # Reduce for disliked solution types
            else:
                adjustments['solution_preference'] = 1.0
        else:
            adjustments['solution_preference'] = 1.0
        
        return adjustments
    
    def _update_processing_stats(self, processing_time: float, patterns: List[BehavioralPattern]):
        """Update processing statistics"""
        self.processing_stats['total_analyses'] += 1
        self.processing_stats['behavioral_patterns_detected'] += len(patterns)
        
        if patterns:
            self.processing_stats['cross_session_insights_generated'] += 1
        
        # Update average processing time
        current_count = self.processing_stats['total_analyses']
        current_avg = self.processing_stats['average_processing_time']
        self.processing_stats['average_processing_time'] = (
            (current_avg * (current_count - 1) + processing_time) / current_count
        )
    
    def get_cross_conversation_insights(self) -> Dict[str, Any]:
        """Get system-wide cross-conversation analysis insights"""
        return {
            'total_analyses': self.processing_stats['total_analyses'],
            'behavioral_patterns_detected': self.processing_stats['behavioral_patterns_detected'],
            'cross_session_insights_generated': self.processing_stats['cross_session_insights_generated'],
            'average_processing_time': self.processing_stats['average_processing_time'],
            'performance_compliance_rate': (
                (self.processing_stats['total_analyses'] - self.processing_stats['performance_violations']) /
                max(1, self.processing_stats['total_analyses'])
            ),
            'active_user_profiles': len(self.user_profiles),
            'user_behavioral_summaries': {
                user_id: {
                    'total_conversations': profile.total_conversations,
                    'behavioral_confidence': profile.get_behavioral_confidence(),
                    'satisfaction_reliability': profile.satisfaction_reliability_score,
                    'detected_patterns_count': len(profile.detected_patterns)
                }
                for user_id, profile in self.user_profiles.items()
            },
            'system_configuration': self.config,
            'pattern_detection_coverage': {
                detector_name: True for detector_name in self.pattern_detectors.keys()
            }
        }


# Helper functions for testing and validation
def test_cross_conversation_analysis():
    """Test cross-conversation analysis functionality"""
    analyzer = CrossConversationAnalyzer()
    
    print("🔄 Testing Cross-Conversation Analysis...")
    
    # Test with mock data (since we don't have real conversation history)
    test_user = "test_user_behavioral"
    
    # Simulate behavioral analysis
    result = analyzer.analyze_user_behavior_patterns(
        user_id=test_user,
        current_feedback="This solution works perfectly for our use case!",
        solution_context={
            'solution_content': 'def solve_problem(): return solution',
            'has_code': True,
            'domain': 'problem_solving'
        },
        lookback_days=30
    )
    
    print(f"  Analysis available: {result['behavioral_analysis_available']}")
    if result['behavioral_analysis_available']:
        print(f"  Behavioral confidence: {result['behavioral_confidence']:.2f}")
        print(f"  Detected patterns: {len(result['detected_patterns'])}")
        print(f"  Processing time: {result['processing_time']:.3f}s")
    else:
        print(f"  Reason: {result.get('reason', 'unknown')}")
        print(f"  Conversation count: {result.get('conversation_count', 0)}")
    
    # Get system insights
    insights = analyzer.get_cross_conversation_insights()
    print(f"\n📊 Cross-Conversation Insights:")
    print(f"  Total analyses: {insights['total_analyses']}")
    print(f"  Active user profiles: {insights['active_user_profiles']}")
    print(f"  Performance compliance: {insights['performance_compliance_rate']:.1%}")
    
    print("✅ Cross-Conversation Analysis test completed!")
    return analyzer


if __name__ == "__main__":
    # Run basic functionality test
    test_analyzer = test_cross_conversation_analysis()