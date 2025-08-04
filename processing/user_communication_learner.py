#!/usr/bin/env python3
"""
User Communication Style Learner for Adaptive Learning Validation System
Implements individual user communication pattern learning using River online learning framework.

Based on PRP-3: Adaptive Learning Validation System (July 2025)
Uses River 0.21.0 for real-time online machine learning with <200ms processing requirements.
"""

import time
import hashlib
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np

# River framework for online learning (July 2025)
try:
    from river import compose, linear_model, preprocessing, feature_extraction, metrics
except ImportError as e:
    logging.error(f"River not available - install with: pip install river")
    raise ImportError("River framework required for adaptive learning") from e

# Existing system integration
from database.enhanced_conversation_entry import ConversationEntry, EnhancedConversationEntry
from database.enhanced_context import LiveValidationLearner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class UserCommunicationProfile:
    """
    Individual user communication profile for adaptive learning.
    
    Tracks user-specific communication patterns, satisfaction expressions,
    and learning confidence to enable personalized validation adaptation.
    """
    user_id: str
    communication_style_strength: float = 0.0
    satisfaction_expression_patterns: Dict[str, float] = field(default_factory=dict)
    cultural_context: Optional[Dict[str, Any]] = None
    feedback_reliability_history: List[float] = field(default_factory=list)
    interaction_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    
    # Communication pattern indicators
    directness_preference: float = 0.5  # 0.0 = indirect, 1.0 = direct
    politeness_level: float = 0.5  # 0.0 = casual, 1.0 = formal
    satisfaction_threshold: float = 0.6  # User-specific satisfaction threshold
    
    # Learning effectiveness metrics
    prediction_accuracy_history: List[float] = field(default_factory=list)
    adaptation_effectiveness: float = 0.0
    
    def get_profile_strength(self) -> float:
        """Calculate user profile strength based on interaction history and accuracy"""
        if self.interaction_count < 5:
            return 0.2  # Low confidence with few interactions
        elif self.interaction_count < 20:
            base_strength = 0.6  # Medium confidence
        else:
            base_strength = min(0.95, 0.4 + (self.interaction_count * 0.01))  # High confidence, capped
        
        # Adjust based on prediction accuracy if available
        if self.prediction_accuracy_history:
            avg_accuracy = np.mean(self.prediction_accuracy_history[-10:])  # Last 10 predictions
            accuracy_boost = (avg_accuracy - 0.5) * 0.5  # -0.25 to +0.25 adjustment
            base_strength = max(0.1, min(0.95, base_strength + accuracy_boost))
        
        return base_strength
    
    def update_with_feedback(self, feedback_text: str, verified_outcome: bool, features: Dict[str, Any]):
        """Update profile with new feedback data"""
        self.interaction_count += 1
        self.last_updated = datetime.now()
        
        # Update communication patterns
        self._update_satisfaction_patterns(feedback_text, verified_outcome)
        self._update_communication_style(feedback_text, features)
        
        # Track feedback reliability
        reliability_score = 1.0 if verified_outcome else 0.0
        self.feedback_reliability_history.append(reliability_score)
        
        # Keep history manageable (last 100 interactions)
        if len(self.feedback_reliability_history) > 100:
            self.feedback_reliability_history = self.feedback_reliability_history[-100:]
    
    def _update_satisfaction_patterns(self, feedback_text: str, verified_outcome: bool):
        """Update satisfaction expression patterns based on feedback"""
        # Extract satisfaction indicators
        satisfaction_words = ['great', 'excellent', 'perfect', 'works', 'helpful', 'thanks']
        dissatisfaction_words = ['wrong', 'broken', 'failed', 'error', 'issue', 'problem']
        
        feedback_lower = feedback_text.lower()
        
        for word in satisfaction_words:
            if word in feedback_lower:
                current_strength = self.satisfaction_expression_patterns.get(word, 0.0)
                if verified_outcome:
                    # Strengthen positive association
                    self.satisfaction_expression_patterns[word] = min(1.0, current_strength + 0.1)
                else:
                    # Weaken if outcome was negative
                    self.satisfaction_expression_patterns[word] = max(0.0, current_strength - 0.05)
        
        for word in dissatisfaction_words:
            if word in feedback_lower:
                current_strength = self.satisfaction_expression_patterns.get(f"neg_{word}", 0.0)
                if not verified_outcome:
                    # Strengthen negative association
                    self.satisfaction_expression_patterns[f"neg_{word}"] = min(1.0, current_strength + 0.1)
                else:
                    # Weaken if outcome was actually positive
                    self.satisfaction_expression_patterns[f"neg_{word}"] = max(0.0, current_strength - 0.05)
    
    def _update_communication_style(self, feedback_text: str, features: Dict[str, Any]):
        """Update communication style indicators"""
        # Analyze directness (simple heuristic)
        direct_indicators = ['exactly', 'clearly', 'definitely', 'wrong', 'right']
        indirect_indicators = ['maybe', 'perhaps', 'might', 'could', 'somewhat']
        
        feedback_lower = feedback_text.lower()
        direct_count = sum(1 for word in direct_indicators if word in feedback_lower)
        indirect_count = sum(1 for word in indirect_indicators if word in feedback_lower)
        
        if direct_count + indirect_count > 0:
            directness_signal = direct_count / (direct_count + indirect_count)
            # Smooth update of directness preference
            self.directness_preference = (self.directness_preference * 0.8 + directness_signal * 0.2)
        
        # Analyze politeness level
        polite_indicators = ['please', 'thank', 'appreciate', 'kindly', 'sorry']
        casual_indicators = ['hey', 'yeah', 'ok', 'sure', 'cool']
        
        polite_count = sum(1 for word in polite_indicators if word in feedback_lower)
        casual_count = sum(1 for word in casual_indicators if word in feedback_lower)
        
        if polite_count + casual_count > 0:
            politeness_signal = polite_count / (polite_count + casual_count)
            # Smooth update of politeness level
            self.politeness_level = (self.politeness_level * 0.8 + politeness_signal * 0.2)


class UserCommunicationStyleLearner:
    """
    Individual user communication pattern learning and adaptation.
    
    Uses River online learning framework to learn user-specific communication patterns
    and adapt validation predictions based on individual user feedback styles.
    
    Integrates with existing LiveValidationLearner while adding personalization layers.
    """
    
    def __init__(self):
        # Integration with existing validation learning system
        self.existing_validation_learner = LiveValidationLearner()
        
        # User-specific models and profiles
        self.user_models: Dict[str, Any] = {}  # user_id -> River model
        self.user_profiles: Dict[str, UserCommunicationProfile] = {}  # user_id -> profile
        
        # Base model template for new users (River 0.21.0)
        self.base_model_template = compose.Pipeline(
            preprocessing.StandardScaler(),
            feature_extraction.TFIDF(ngram_range=(1, 2)),
            linear_model.LogisticRegression()
        )
        
        # Performance tracking
        self.processing_stats = {
            'total_users': 0,
            'total_learning_updates': 0,
            'average_processing_time': 0.0,
            'performance_violations': 0
        }
        
        # Feature extractors
        self.feature_extractors = {
            'length': lambda text: len(text),
            'word_count': lambda text: len(text.split()),
            'exclamation_count': lambda text: text.count('!'),
            'question_count': lambda text: text.count('?'),
            'capitalization_ratio': lambda text: sum(1 for c in text if c.isupper()) / max(1, len(text)),
            'punctuation_density': lambda text: sum(1 for c in text if c in '.,!?;:') / max(1, len(text))
        }
    
    def learn_user_communication_style(self, user_id: str, feedback_text: str, 
                                     verified_outcome: bool, solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learn individual user communication patterns from verified feedback.
        
        Args:
            user_id: Unique identifier for the user
            feedback_text: User's feedback text
            verified_outcome: Whether the solution actually worked (ground truth)
            solution_context: Context about the solution that was provided
            
        Returns:
            Dictionary with learning results and performance metrics
        """
        # PERFORMANCE: Start timing to meet <200ms requirement
        start_time = time.time()
        
        try:
            # Initialize user model if new user
            if user_id not in self.user_models:
                self.user_models[user_id] = self.base_model_template.clone()
                self.user_profiles[user_id] = UserCommunicationProfile(user_id)
                self.processing_stats['total_users'] += 1
                logger.info(f"✨ Initialized adaptive learning for new user: {user_id}")
            
            user_model = self.user_models[user_id]
            user_profile = self.user_profiles[user_id]
            
            # Extract communication features for learning
            communication_features = self._extract_communication_features(feedback_text, solution_context)
            
            # Online learning update (River framework)
            user_model.learn_one(communication_features, verified_outcome)
            
            # Update user communication profile
            user_profile.update_with_feedback(feedback_text, verified_outcome, communication_features)
            
            # INTEGRATION: Also update existing LiveValidationLearner
            # This ensures backward compatibility and leverages existing sophisticated learning
            existing_result = self.existing_validation_learner.process_validation_feedback(
                solution_context.get('solution_id', ''),
                solution_context.get('solution_content', ''),
                feedback_text,
                solution_context
            )
            
            # Performance tracking
            processing_time = time.time() - start_time
            self.processing_stats['total_learning_updates'] += 1
            self.processing_stats['average_processing_time'] = (
                (self.processing_stats['average_processing_time'] * 
                 (self.processing_stats['total_learning_updates'] - 1) + processing_time) / 
                self.processing_stats['total_learning_updates']
            )
            
            # Validate performance requirement
            if processing_time > 0.2:  # 200ms threshold
                self.processing_stats['performance_violations'] += 1
                logger.warning(f"⚠️ Processing time {processing_time:.3f}s exceeds 200ms requirement for user {user_id}")
            
            return {
                'user_model_updated': True,
                'user_profile_strength': user_profile.get_profile_strength(),
                'learning_features': communication_features,
                'processing_time': processing_time,
                'performance_compliant': processing_time <= 0.2,
                'existing_system_updated': True,
                'existing_system_result': existing_result,
                'interaction_count': user_profile.interaction_count,
                'adaptation_confidence': user_profile.get_profile_strength()
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in user communication learning for {user_id}: {e}")
            return {
                'error': str(e),
                'user_model_updated': False,
                'processing_time': processing_time,
                'performance_compliant': processing_time <= 0.2
            }
    
    def predict_user_satisfaction_with_adaptation(self, user_id: str, feedback_text: str, 
                                                solution_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict user satisfaction with personalized adaptation.
        
        Args:
            user_id: User identifier
            feedback_text: Feedback text to analyze
            solution_context: Context about the solution
            
        Returns:
            Dictionary with personalized satisfaction prediction
        """
        start_time = time.time()
        
        try:
            # Get base prediction from existing system
            base_prediction = self.existing_validation_learner.search_conversations_enhanced(
                query=solution_context.get('query', feedback_text),
                n_results=1,
                validation_preference='neutral'
            )
            
            base_satisfaction = 0.5  # Default neutral
            if base_prediction:
                base_satisfaction = base_prediction[0].get('enhancement_analysis', {}).get('validation_boost', 0.5)
            
            if user_id not in self.user_models:
                # No user history - return base prediction with learning opportunity flag
                processing_time = time.time() - start_time
                return {
                    'satisfaction_score': base_satisfaction,
                    'user_adapted': False,
                    'learning_opportunity': True,
                    'base_prediction': base_satisfaction,
                    'adaptation_applied': 0.0,
                    'recommendation': 'collect_user_feedback_for_learning',
                    'processing_time': processing_time,
                    'performance_compliant': processing_time <= 0.2
                }
            
            # Apply user-specific adaptation
            user_model = self.user_models[user_id]
            user_profile = self.user_profiles[user_id]
            
            # Extract features and get user-specific prediction
            features = self._extract_communication_features(feedback_text, solution_context)
            
            try:
                user_prediction = user_model.predict_proba_one(features)
                user_satisfaction = user_prediction.get(True, 0.5) if isinstance(user_prediction, dict) else 0.5
            except Exception as e:
                logger.warning(f"User model prediction failed for {user_id}: {e}")
                user_satisfaction = 0.5
            
            # Blend with base prediction based on user profile strength
            profile_strength = user_profile.get_profile_strength()
            blended_satisfaction = (
                base_satisfaction * (1 - profile_strength) + 
                user_satisfaction * profile_strength
            )
            
            # Apply user-specific communication adjustments
            adjusted_satisfaction = self._apply_user_communication_adjustments(
                blended_satisfaction, feedback_text, user_profile
            )
            
            processing_time = time.time() - start_time
            
            return {
                'satisfaction_score': adjusted_satisfaction,
                'user_adapted': True,
                'base_prediction': base_satisfaction,
                'user_specific_prediction': user_satisfaction,
                'blended_prediction': blended_satisfaction,
                'adaptation_applied': adjusted_satisfaction - base_satisfaction,
                'user_profile_strength': profile_strength,
                'adaptation_confidence': profile_strength,
                'communication_adjustments': {
                    'directness_preference': user_profile.directness_preference,
                    'politeness_level': user_profile.politeness_level,
                    'satisfaction_threshold': user_profile.satisfaction_threshold
                },
                'processing_time': processing_time,
                'performance_compliant': processing_time <= 0.2
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in user satisfaction prediction for {user_id}: {e}")
            return {
                'error': str(e),
                'satisfaction_score': 0.5,
                'user_adapted': False,
                'processing_time': processing_time,
                'performance_compliant': processing_time <= 0.2
            }
    
    def _extract_communication_features(self, feedback_text: str, solution_context: Dict[str, Any]) -> Dict[str, float]:
        """Extract communication features for learning"""
        features = {}
        
        # Basic text features
        for feature_name, extractor in self.feature_extractors.items():
            try:
                features[feature_name] = float(extractor(feedback_text))
            except Exception:
                features[feature_name] = 0.0
        
        # Sentiment indicators
        positive_words = ['great', 'excellent', 'perfect', 'works', 'helpful', 'thanks', 'good']
        negative_words = ['wrong', 'broken', 'failed', 'error', 'issue', 'problem', 'bad']
        
        feedback_lower = feedback_text.lower()
        features['positive_word_count'] = sum(1 for word in positive_words if word in feedback_lower)
        features['negative_word_count'] = sum(1 for word in negative_words if word in feedback_lower)
        
        # Communication style indicators
        direct_indicators = ['exactly', 'clearly', 'definitely', 'obviously']
        indirect_indicators = ['maybe', 'perhaps', 'might', 'could', 'somewhat']
        
        features['directness_score'] = sum(1 for word in direct_indicators if word in feedback_lower)
        features['indirectness_score'] = sum(1 for word in indirect_indicators if word in feedback_lower)
        
        # Politeness indicators
        polite_words = ['please', 'thank', 'appreciate', 'kindly', 'sorry']
        features['politeness_score'] = sum(1 for word in polite_words if word in feedback_lower)
        
        # Solution context features
        features['solution_has_code'] = 1.0 if solution_context.get('has_code', False) else 0.0
        features['solution_length'] = float(len(solution_context.get('solution_content', '')))
        
        return features
    
    def _apply_user_communication_adjustments(self, base_satisfaction: float, feedback_text: str, 
                                            user_profile: UserCommunicationProfile) -> float:
        """Apply user-specific communication style adjustments"""
        adjusted_satisfaction = base_satisfaction
        
        # Apply directness preference adjustment
        feedback_lower = feedback_text.lower()
        
        # If user is typically indirect but gives direct negative feedback, amplify it
        if user_profile.directness_preference < 0.3:  # Indirect user
            direct_negative = any(word in feedback_lower for word in ['wrong', 'broken', 'failed'])
            if direct_negative and base_satisfaction < 0.5:
                adjusted_satisfaction *= 0.8  # Amplify negative signal for indirect users
        
        # If user is typically formal but gives casual positive feedback, it's more meaningful
        if user_profile.politeness_level > 0.7:  # Formal user
            casual_positive = any(word in feedback_lower for word in ['cool', 'awesome', 'great'])
            if casual_positive and base_satisfaction > 0.5:
                adjusted_satisfaction = min(1.0, adjusted_satisfaction * 1.2)
        
        # Apply user-specific satisfaction patterns
        for pattern, strength in user_profile.satisfaction_expression_patterns.items():
            if pattern.startswith('neg_'):
                word = pattern[4:]  # Remove 'neg_' prefix
                if word in feedback_lower and strength > 0.5:
                    adjusted_satisfaction *= (1 - strength * 0.3)  # Reduce satisfaction
            else:
                if pattern in feedback_lower and strength > 0.5:
                    adjusted_satisfaction = min(1.0, adjusted_satisfaction * (1 + strength * 0.2))
        
        # Ensure result stays within valid range
        return max(0.0, min(1.0, adjusted_satisfaction))
    
    def get_user_learning_insights(self, user_id: str) -> Dict[str, Any]:
        """Get learning insights for a specific user"""
        if user_id not in self.user_profiles:
            return {
                'error': 'User not found',
                'user_id': user_id,
                'learning_available': False
            }
        
        user_profile = self.user_profiles[user_id]
        
        return {
            'user_id': user_id,
            'learning_available': True,
            'profile_strength': user_profile.get_profile_strength(),
            'interaction_count': user_profile.interaction_count,
            'communication_style': {
                'directness_preference': user_profile.directness_preference,
                'politeness_level': user_profile.politeness_level,
                'satisfaction_threshold': user_profile.satisfaction_threshold
            },
            'satisfaction_patterns': user_profile.satisfaction_expression_patterns,
            'feedback_reliability': np.mean(user_profile.feedback_reliability_history) if user_profile.feedback_reliability_history else 0.0,
            'prediction_accuracy': np.mean(user_profile.prediction_accuracy_history) if user_profile.prediction_accuracy_history else None,
            'adaptation_effectiveness': user_profile.adaptation_effectiveness,
            'last_updated': user_profile.last_updated.isoformat(),
            'cultural_context': user_profile.cultural_context
        }
    
    def get_system_learning_insights(self) -> Dict[str, Any]:
        """Get system-wide learning insights"""
        return {
            'total_users': self.processing_stats['total_users'],
            'total_learning_updates': self.processing_stats['total_learning_updates'],
            'average_processing_time': self.processing_stats['average_processing_time'],
            'performance_compliance_rate': (
                (self.processing_stats['total_learning_updates'] - self.processing_stats['performance_violations']) /
                max(1, self.processing_stats['total_learning_updates'])
            ),
            'active_user_profiles': len(self.user_profiles),
            'user_profile_strengths': {
                user_id: profile.get_profile_strength() 
                for user_id, profile in self.user_profiles.items()
            },
            'system_health': {
                'models_loaded': len(self.user_models),
                'profiles_active': len(self.user_profiles),
                'performance_violations': self.processing_stats['performance_violations'],
                'integration_active': hasattr(self, 'existing_validation_learner')
            }
        }


# Helper functions for testing and validation
def test_user_communication_learning():
    """Test user communication style learning functionality"""
    learner = UserCommunicationStyleLearner()
    
    # Test data
    test_user = "test_user_adaptive"
    test_cases = [
        {"text": "Great solution!", "outcome": True, "context": {"domain": "testing"}},
        {"text": "This works perfectly", "outcome": True, "context": {"domain": "testing"}},
        {"text": "Not quite right", "outcome": False, "context": {"domain": "testing"}},
        {"text": "Excellent fix", "outcome": True, "context": {"domain": "debugging"}}
    ]
    
    print("🧪 Testing User Communication Learning...")
    
    # Train user model
    for i, case in enumerate(test_cases):
        result = learner.learn_user_communication_style(
            test_user, case["text"], case["outcome"], case["context"]
        )
        print(f"  Learning update {i+1}: Profile strength {result['user_profile_strength']:.2f}, "
              f"Processing time: {result['processing_time']:.3f}s")
    
    # Test prediction
    prediction = learner.predict_user_satisfaction_with_adaptation(
        test_user, "Perfect solution!", {"domain": "testing"}
    )
    
    print(f"  Prediction test: Satisfaction {prediction['satisfaction_score']:.2f}, "
          f"User adapted: {prediction['user_adapted']}")
    
    # Get insights
    insights = learner.get_user_learning_insights(test_user)
    print(f"  User insights: {insights['interaction_count']} interactions, "
          f"Profile strength: {insights['profile_strength']:.2f}")
    
    print("✅ User Communication Learning test completed!")
    return learner


if __name__ == "__main__":
    # Run basic functionality test
    test_learner = test_user_communication_learning()
    
    # Display system insights
    system_insights = test_learner.get_system_learning_insights()
    print(f"\n📊 System Learning Insights:")
    print(f"  Total users: {system_insights['total_users']}")
    print(f"  Performance compliance: {system_insights['performance_compliance_rate']:.1%}")
    print(f"  Average processing time: {system_insights['average_processing_time']:.3f}s")