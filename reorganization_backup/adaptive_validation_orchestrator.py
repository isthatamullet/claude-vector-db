#!/usr/bin/env python3
"""
Adaptive Validation Orchestrator for Adaptive Learning Validation System
Main coordination system that integrates all adaptive learning components.

Based on PRP-3: Adaptive Learning Validation System (July 2025)
Orchestrates user communication learning, cultural intelligence, and cross-conversation analysis
while maintaining backward compatibility with existing LiveValidationLearner.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np
from datetime import datetime

# Import adaptive learning components
from user_communication_learner import UserCommunicationStyleLearner, UserCommunicationProfile
from cultural_intelligence_engine import CulturalIntelligenceEngine, CulturalIntelligenceContext
from cross_conversation_analyzer import CrossConversationAnalyzer, UserBehavioralProfile

# Integration with existing system
from vector_database import ClaudeVectorDatabase
from enhanced_context import LiveValidationLearner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AdaptiveValidationRequest:
    """
    Request structure for adaptive validation processing.
    
    Contains all necessary information for comprehensive adaptive learning
    including user identification, feedback content, solution context,
    and cultural profile information.
    """
    # Core validation data
    feedback_text: str
    solution_context: Dict[str, Any]
    
    # User identification and cultural context
    user_id: Optional[str] = None
    user_cultural_profile: Dict[str, Any] = field(default_factory=dict)
    
    # Processing options
    enable_user_adaptation: bool = True
    enable_cultural_intelligence: bool = True
    enable_cross_conversation_analysis: bool = True
    enable_existing_system: bool = True
    
    # Performance requirements
    max_processing_time: float = 0.2  # 200ms requirement
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'feedback_text': self.feedback_text,
            'solution_context': self.solution_context,
            'user_id': self.user_id,
            'user_cultural_profile': self.user_cultural_profile,
            'enable_user_adaptation': self.enable_user_adaptation,
            'enable_cultural_intelligence': self.enable_cultural_intelligence,
            'enable_cross_conversation_analysis': self.enable_cross_conversation_analysis,
            'enable_existing_system': self.enable_existing_system,
            'max_processing_time': self.max_processing_time
        }


@dataclass
class AdaptiveValidationResult:
    """
    Complete result from adaptive validation processing.
    
    Contains blended results from all adaptive learning components
    along with confidence scores, explanations, and performance metrics.
    """
    # Final blended validation
    final_validation_strength: float
    adaptation_confidence: float
    
    # Component results
    base_validation: Optional[Dict[str, Any]] = None
    user_adaptation: Optional[Dict[str, Any]] = None
    cultural_analysis: Optional[Dict[str, Any]] = None
    behavioral_analysis: Optional[Dict[str, Any]] = None
    
    # Blending and confidence information
    blending_weights: Dict[str, float] = field(default_factory=dict)
    component_contributions: Dict[str, float] = field(default_factory=dict)
    
    # Explanations and insights
    adaptation_explanation: str = ""
    recommendations: List[str] = field(default_factory=list)
    
    # Performance metrics
    processing_time: float = 0.0
    performance_compliant: bool = True
    components_processed: List[str] = field(default_factory=list)
    
    # Quality metrics
    improvement_over_baseline: float = 0.0
    confidence_increase: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'final_validation_strength': self.final_validation_strength,
            'adaptation_confidence': self.adaptation_confidence,
            'base_validation': self.base_validation,
            'user_adaptation': self.user_adaptation,
            'cultural_analysis': self.cultural_analysis,
            'behavioral_analysis': self.behavioral_analysis,
            'blending_weights': self.blending_weights,
            'component_contributions': self.component_contributions,
            'adaptation_explanation': self.adaptation_explanation,
            'recommendations': self.recommendations,
            'processing_time': self.processing_time,
            'performance_compliant': self.performance_compliant,
            'components_processed': self.components_processed,
            'improvement_over_baseline': self.improvement_over_baseline,
            'confidence_increase': self.confidence_increase
        }


class ProcessingStats:
    """Performance and processing statistics tracking"""
    
    def __init__(self):
        self.total_requests = 0
        self.successful_adaptations = 0
        self.performance_violations = 0
        self.component_usage = {
            'user_adaptation': 0,
            'cultural_intelligence': 0,
            'cross_conversation': 0,
            'existing_system': 0
        }
        self.average_processing_time = 0.0
        self.average_improvement = 0.0
        self.confidence_improvements = []
        
    def record_processing(self, processing_time: float, components_used: List[str], 
                         improvement: float, confidence_increase: float):
        """Record processing statistics"""
        self.total_requests += 1
        
        if improvement > 0:
            self.successful_adaptations += 1
        
        if processing_time > 0.2:
            self.performance_violations += 1
        
        for component in components_used:
            if component in self.component_usage:
                self.component_usage[component] += 1
        
        # Update averages
        self.average_processing_time = (
            (self.average_processing_time * (self.total_requests - 1) + processing_time) / 
            self.total_requests
        )
        
        self.average_improvement = (
            (self.average_improvement * (self.total_requests - 1) + improvement) / 
            self.total_requests
        )
        
        self.confidence_improvements.append(confidence_increase)
        if len(self.confidence_improvements) > 100:  # Keep last 100
            self.confidence_improvements = self.confidence_improvements[-100:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        return {
            'total_requests': self.total_requests,
            'successful_adaptations': self.successful_adaptations,
            'success_rate': self.successful_adaptations / max(1, self.total_requests),
            'performance_violations': self.performance_violations,
            'performance_compliance_rate': (
                (self.total_requests - self.performance_violations) / max(1, self.total_requests)
            ),
            'component_usage': self.component_usage,
            'average_processing_time': self.average_processing_time,
            'average_improvement': self.average_improvement,
            'average_confidence_increase': (
                np.mean(self.confidence_improvements) if self.confidence_improvements else 0.0
            )
        }


class AdaptiveValidationOrchestrator:
    """
    Main coordination system for all adaptive learning components.
    
    Orchestrates user communication learning, cultural intelligence, 
    cross-conversation analysis, and existing validation systems to
    achieve 92% → 96% validation accuracy improvement.
    """
    
    def __init__(self):
        # Initialize all adaptive learning components
        logger.info("🚀 Initializing Adaptive Validation Orchestrator...")
        
        try:
            self.user_communication_learner = UserCommunicationStyleLearner()
            logger.info("✅ User Communication Learner initialized")
        except Exception as e:
            logger.error(f"Failed to initialize User Communication Learner: {e}")
            self.user_communication_learner = None
        
        try:
            self.cultural_intelligence_engine = CulturalIntelligenceEngine()
            logger.info("✅ Cultural Intelligence Engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cultural Intelligence Engine: {e}")
            self.cultural_intelligence_engine = None
        
        try:
            self.cross_conversation_analyzer = CrossConversationAnalyzer()
            logger.info("✅ Cross-Conversation Analyzer initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Cross-Conversation Analyzer: {e}")
            self.cross_conversation_analyzer = None
        
        # Integration with existing system (CRITICAL: Build upon, don't replace)
        try:
            self.existing_validation_learner = LiveValidationLearner()
            self.vector_database = ClaudeVectorDatabase()
            logger.info("✅ Existing system integration established")
        except Exception as e:
            logger.error(f"Failed to initialize existing system integration: {e}")
            self.existing_validation_learner = None
            self.vector_database = None
        
        # Performance and statistics tracking
        self.processing_stats = ProcessingStats()
        
        # Blending configuration
        self.blending_config = {
            'base_weight': 0.4,  # Weight for existing system baseline
            'user_adaptation_weight': 0.25,  # Weight for user-specific adaptation
            'cultural_intelligence_weight': 0.2,  # Weight for cultural adjustments
            'behavioral_analysis_weight': 0.15,  # Weight for cross-conversation insights
            
            # Confidence thresholds for component activation
            'min_user_confidence': 0.3,
            'min_cultural_confidence': 0.4,
            'min_behavioral_confidence': 0.3,
            
            # Performance requirements
            'max_processing_time': 0.2,  # 200ms hard limit
            'graceful_degradation': True  # Fall back to existing system if components fail
        }
        
        logger.info("🎯 Adaptive Validation Orchestrator ready for 92% → 96% accuracy improvement")
    
    def process_adaptive_validation(self, request: AdaptiveValidationRequest) -> AdaptiveValidationResult:
        """
        Main entry point for adaptive validation processing.
        
        Coordinates all adaptive learning components to provide enhanced
        validation with personalization, cultural intelligence, and behavioral insights.
        
        Args:
            request: AdaptiveValidationRequest with feedback and context
            
        Returns:
            AdaptiveValidationResult with blended adaptive predictions
        """
        # PERFORMANCE: Overall <200ms requirement
        start_time = time.time()
        
        try:
            logger.info(f"🧠 Processing adaptive validation for user: {request.user_id or 'anonymous'}")
            
            # Initialize result structure
            result = AdaptiveValidationResult(
                final_validation_strength=0.5,  # Default neutral
                adaptation_confidence=0.0
            )
            
            components_processed = []
            component_results = {}
            
            # 1. Process with existing LiveValidationLearner (baseline - ALWAYS include)
            if request.enable_existing_system and self.existing_validation_learner:
                try:
                    base_result = self.existing_validation_learner.process_live_validation_feedback(
                        request.solution_context.get('solution_id', ''),
                        request.solution_context.get('solution_content', ''),
                        request.feedback_text,
                        request.solution_context
                    )
                    
                    result.base_validation = base_result
                    component_results['base'] = base_result
                    components_processed.append('existing_system')
                    
                    logger.debug("✅ Base validation processed")
                    
                except Exception as e:
                    logger.warning(f"Base validation failed: {e}")
                    result.base_validation = {'validation_strength': 0.5, 'error': str(e)}
                    component_results['base'] = result.base_validation
            
            # 2. Apply user communication style adaptation
            if (request.enable_user_adaptation and 
                request.user_id and 
                self.user_communication_learner):
                try:
                    user_result = self.user_communication_learner.predict_user_satisfaction_with_adaptation(
                        request.user_id, request.feedback_text, request.solution_context
                    )
                    
                    result.user_adaptation = user_result
                    component_results['user'] = user_result
                    components_processed.append('user_adaptation')
                    
                    logger.debug(f"✅ User adaptation processed: {user_result.get('user_adapted', False)}")
                    
                except Exception as e:
                    logger.warning(f"User adaptation failed: {e}")
                    result.user_adaptation = {'error': str(e), 'user_adapted': False}
                    component_results['user'] = result.user_adaptation
            
            # 3. Apply cultural intelligence
            if (request.enable_cultural_intelligence and 
                request.user_cultural_profile and 
                self.cultural_intelligence_engine):
                try:
                    cultural_result = self.cultural_intelligence_engine.analyze_with_cultural_intelligence(
                        request.feedback_text, request.user_cultural_profile
                    )
                    
                    result.cultural_analysis = cultural_result
                    component_results['cultural'] = cultural_result
                    components_processed.append('cultural_intelligence')
                    
                    logger.debug(f"✅ Cultural intelligence processed: {cultural_result.get('cultural_confidence', 0):.2f}")
                    
                except Exception as e:
                    logger.warning(f"Cultural intelligence failed: {e}")
                    result.cultural_analysis = {'error': str(e), 'cultural_confidence': 0.0}
                    component_results['cultural'] = result.cultural_analysis
            
            # 4. Apply cross-conversation behavioral analysis
            if (request.enable_cross_conversation_analysis and 
                request.user_id and 
                self.cross_conversation_analyzer):
                try:
                    behavioral_result = self.cross_conversation_analyzer.analyze_user_behavior_patterns(
                        request.user_id, request.feedback_text, request.solution_context
                    )
                    
                    result.behavioral_analysis = behavioral_result
                    component_results['behavioral'] = behavioral_result
                    components_processed.append('cross_conversation')
                    
                    logger.debug(f"✅ Behavioral analysis processed: {behavioral_result.get('behavioral_analysis_available', False)}")
                    
                except Exception as e:
                    logger.warning(f"Behavioral analysis failed: {e}")
                    result.behavioral_analysis = {'error': str(e), 'behavioral_analysis_available': False}
                    component_results['behavioral'] = result.behavioral_analysis
            
            # 5. Blend all adaptive predictions intelligently
            blended_validation = self._blend_adaptive_predictions(component_results, request)
            
            # Update result with blended predictions
            result.final_validation_strength = blended_validation['validation_strength']
            result.adaptation_confidence = blended_validation['adaptation_confidence']
            result.blending_weights = blended_validation['blending_weights']
            result.component_contributions = blended_validation['component_contributions']
            result.adaptation_explanation = blended_validation['explanation']
            result.recommendations = blended_validation['recommendations']
            
            # Calculate improvements
            baseline_strength = component_results.get('base', {}).get('validation_strength', 0.5)
            result.improvement_over_baseline = result.final_validation_strength - baseline_strength
            result.confidence_increase = result.adaptation_confidence - 0.5  # Base confidence
            
            # Performance tracking
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            result.performance_compliant = processing_time <= request.max_processing_time
            result.components_processed = components_processed
            
            # Update statistics
            self.processing_stats.record_processing(
                processing_time, components_processed, 
                result.improvement_over_baseline, result.confidence_increase
            )
            
            # Performance compliance check
            if not result.performance_compliant:
                logger.warning(f"⚠️ Adaptive validation exceeded {request.max_processing_time:.0f}ms: {processing_time:.3f}s")
            
            logger.info(f"🎯 Adaptive validation complete: "
                       f"Strength {result.final_validation_strength:.2f} "
                       f"(+{result.improvement_over_baseline:+.2f}), "
                       f"Confidence {result.adaptation_confidence:.2f}, "
                       f"Time {processing_time:.3f}s")
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Critical error in adaptive validation: {e}")
            
            # Graceful degradation - return minimal result
            return AdaptiveValidationResult(
                final_validation_strength=0.5,
                adaptation_confidence=0.0,
                adaptation_explanation=f"Adaptive validation failed: {str(e)}",
                processing_time=processing_time,
                performance_compliant=processing_time <= request.max_processing_time,
                components_processed=['fallback']
            )
    
    def _blend_adaptive_predictions(self, component_results: Dict[str, Dict[str, Any]], 
                                  request: AdaptiveValidationRequest) -> Dict[str, Any]:
        """
        Intelligent blending of all adaptive learning predictions.
        
        Uses confidence-weighted blending with dynamic weight adjustment
        based on component reliability and user context.
        """
        # Extract predictions and confidences from each component
        predictions = {}
        confidences = {}
        
        # Base validation (existing system)
        if 'base' in component_results:
            base_result = component_results['base']
            predictions['base'] = base_result.get('validation_strength', 0.5)
            confidences['base'] = 0.8  # High confidence in existing system
        
        # User adaptation
        if 'user' in component_results:
            user_result = component_results['user']
            if user_result.get('user_adapted', False):
                predictions['user'] = user_result.get('satisfaction_score', 0.5)
                confidences['user'] = user_result.get('adaptation_confidence', 0.0)
        
        # Cultural intelligence
        if 'cultural' in component_results:
            cultural_result = component_results['cultural']
            if 'culturally_adjusted_sentiment' in cultural_result:
                cultural_sentiment = cultural_result['culturally_adjusted_sentiment']
                # Convert sentiment to validation strength
                if cultural_sentiment.get('label') in ['POSITIVE', 'positive']:
                    predictions['cultural'] = cultural_sentiment.get('score', 0.5)
                elif cultural_sentiment.get('label') in ['NEGATIVE', 'negative']:
                    predictions['cultural'] = 1.0 - cultural_sentiment.get('score', 0.5)
                else:
                    predictions['cultural'] = 0.5
                
                confidences['cultural'] = cultural_result.get('cultural_confidence', 0.0)
        
        # Behavioral analysis
        if 'behavioral' in component_results:
            behavioral_result = component_results['behavioral']
            if behavioral_result.get('behavioral_analysis_available', False):
                # Use satisfaction trend adjustment as prediction modifier
                base_prediction = predictions.get('base', 0.5)
                trend_adjustment = behavioral_result.get('satisfaction_trend_adjustment', 1.0)
                predictions['behavioral'] = base_prediction * trend_adjustment
                confidences['behavioral'] = behavioral_result.get('behavioral_confidence', 0.0)
        
        # Apply confidence thresholds
        filtered_predictions = {}
        filtered_confidences = {}
        
        for component, prediction in predictions.items():
            confidence = confidences.get(component, 0.0)
            
            # Apply minimum confidence thresholds
            if component == 'base':
                # Always include base prediction
                filtered_predictions[component] = prediction
                filtered_confidences[component] = confidence
            elif component == 'user' and confidence >= self.blending_config['min_user_confidence']:
                filtered_predictions[component] = prediction
                filtered_confidences[component] = confidence
            elif component == 'cultural' and confidence >= self.blending_config['min_cultural_confidence']:
                filtered_predictions[component] = prediction
                filtered_confidences[component] = confidence
            elif component == 'behavioral' and confidence >= self.blending_config['min_behavioral_confidence']:
                filtered_predictions[component] = prediction
                filtered_confidences[component] = confidence
        
        # Calculate dynamic weights based on confidences
        blending_weights = self._calculate_dynamic_weights(filtered_confidences)
        
        # Blend predictions using confidence-weighted average
        if filtered_predictions:
            blended_strength = sum(
                blending_weights.get(component, 0) * prediction 
                for component, prediction in filtered_predictions.items()
            )
            
            # Calculate overall adaptation confidence
            adaptation_confidence = sum(
                blending_weights.get(component, 0) * confidence 
                for component, confidence in filtered_confidences.items()
            )
        else:
            # Fallback to neutral
            blended_strength = 0.5
            adaptation_confidence = 0.0
            blending_weights = {'fallback': 1.0}
        
        # Ensure valid range
        blended_strength = max(0.0, min(1.0, blended_strength))
        adaptation_confidence = max(0.0, min(1.0, adaptation_confidence))
        
        # Calculate component contributions
        component_contributions = {}
        for component in filtered_predictions:
            component_contributions[component] = abs(
                filtered_predictions[component] - 0.5
            ) * blending_weights.get(component, 0)
        
        # Generate explanation
        explanation = self._generate_blending_explanation(
            filtered_predictions, blending_weights, component_results
        )
        
        # Generate recommendations
        recommendations = self._generate_adaptive_recommendations(
            component_results, blended_strength, adaptation_confidence
        )
        
        return {
            'validation_strength': blended_strength,
            'adaptation_confidence': adaptation_confidence,
            'blending_weights': blending_weights,
            'component_contributions': component_contributions,
            'explanation': explanation,
            'recommendations': recommendations,
            'components_used': list(filtered_predictions.keys())
        }
    
    def _calculate_dynamic_weights(self, confidences: Dict[str, float]) -> Dict[str, float]:
        """Calculate dynamic blending weights based on component confidences"""
        if not confidences:
            return {}
        
        # Start with base configuration weights
        base_weights = {
            'base': self.blending_config['base_weight'],
            'user': self.blending_config['user_adaptation_weight'],
            'cultural': self.blending_config['cultural_intelligence_weight'],
            'behavioral': self.blending_config['behavioral_analysis_weight']
        }
        
        # Adjust weights based on confidence
        adjusted_weights = {}
        for component, confidence in confidences.items():
            base_weight = base_weights.get(component, 0.1)
            
            # Higher confidence gets higher weight
            confidence_multiplier = 0.5 + (confidence * 1.5)  # 0.5 to 2.0 multiplier
            adjusted_weights[component] = base_weight * confidence_multiplier
        
        # Normalize weights to sum to 1.0
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            normalized_weights = {
                component: weight / total_weight 
                for component, weight in adjusted_weights.items()
            }
        else:
            # Fallback to equal weights
            num_components = len(confidences)
            normalized_weights = {
                component: 1.0 / num_components 
                for component in confidences.keys()
            }
        
        return normalized_weights
    
    def _generate_blending_explanation(self, predictions: Dict[str, float], 
                                     weights: Dict[str, float], 
                                     component_results: Dict[str, Dict[str, Any]]) -> str:
        """Generate human-readable explanation of adaptive blending"""
        explanations = []
        
        # Base system explanation
        if 'base' in predictions:
            base_strength = predictions['base']
            base_weight = weights.get('base', 0)
            explanations.append(f"Existing system: {base_strength:.2f} (weight: {base_weight:.1%})")
        
        # User adaptation explanation
        if 'user' in predictions:
            user_result = component_results.get('user', {})
            user_strength = predictions['user']
            user_weight = weights.get('user', 0)
            profile_strength = user_result.get('user_profile_strength', 0)
            explanations.append(f"User adaptation: {user_strength:.2f} (weight: {user_weight:.1%}, profile: {profile_strength:.2f})")
        
        # Cultural intelligence explanation
        if 'cultural' in predictions:
            cultural_result = component_results.get('cultural', {})
            cultural_strength = predictions['cultural']
            cultural_weight = weights.get('cultural', 0)
            cultural_confidence = cultural_result.get('cultural_confidence', 0)
            language = cultural_result.get('language_detected', 'unknown')
            explanations.append(f"Cultural intelligence: {cultural_strength:.2f} (weight: {cultural_weight:.1%}, {language}, conf: {cultural_confidence:.2f})")
        
        # Behavioral analysis explanation
        if 'behavioral' in predictions:
            behavioral_result = component_results.get('behavioral', {})
            behavioral_strength = predictions['behavioral']
            behavioral_weight = weights.get('behavioral', 0)
            behavioral_confidence = behavioral_result.get('behavioral_confidence', 0)
            explanations.append(f"Behavioral analysis: {behavioral_strength:.2f} (weight: {behavioral_weight:.1%}, conf: {behavioral_confidence:.2f})")
        
        if explanations:
            return "Adaptive blending: " + "; ".join(explanations)
        else:
            return "Adaptive validation unavailable - using fallback"
    
    def _generate_adaptive_recommendations(self, component_results: Dict[str, Dict[str, Any]], 
                                         final_strength: float, 
                                         confidence: float) -> List[str]:
        """Generate actionable recommendations based on adaptive analysis"""
        recommendations = []
        
        # Confidence-based recommendations
        if confidence < 0.3:
            recommendations.append("Low adaptation confidence - consider collecting more user feedback for learning")
        elif confidence > 0.8:
            recommendations.append("High adaptation confidence - user patterns well established")
        
        # User adaptation recommendations
        if 'user' in component_results:
            user_result = component_results['user']
            if user_result.get('learning_opportunity', False):
                recommendations.append("New user detected - initial feedback will improve future predictions")
            
            profile_strength = user_result.get('user_profile_strength', 0)
            if profile_strength > 0.7:
                recommendations.append("Strong user profile available - personalized predictions highly reliable")
        
        # Cultural intelligence recommendations
        if 'cultural' in component_results:
            cultural_result = component_results['cultural']
            if cultural_result.get('bias_prevention_applied', False):
                recommendations.append("Cultural bias prevention applied - adjustments kept within ethical limits")
            
            cultural_confidence = cultural_result.get('cultural_confidence', 0)
            if cultural_confidence > 0.6:
                recommendations.append("Strong cultural adaptation applied - feedback interpreted with cultural context")
        
        # Behavioral analysis recommendations
        if 'behavioral' in component_results:
            behavioral_result = component_results['behavioral']
            if behavioral_result.get('behavioral_analysis_available', False):
                behavioral_confidence = behavioral_result.get('behavioral_confidence', 0)
                if behavioral_confidence > 0.5:
                    recommendations.append("Cross-conversation patterns detected - behavioral insights applied")
                
                # Specific behavioral recommendations
                behavioral_insights = behavioral_result.get('behavioral_insights', {})
                if behavioral_insights.get('user_reliability', 0) < 0.5:
                    recommendations.append("Monitor follow-up behavior to validate feedback accuracy")
        
        # Final strength recommendations
        if final_strength > 0.8:
            recommendations.append("High validation strength - solution likely very effective")
        elif final_strength < 0.3:
            recommendations.append("Low validation strength - consider alternative approaches")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def get_adaptive_learning_insights(self, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Get comprehensive insights about adaptive learning performance"""
        insights = {
            'system_performance': self.processing_stats.get_performance_metrics(),
            'orchestrator_health': self._get_orchestrator_health(),
            'component_status': self._get_component_status()
        }
        
        # User-specific insights if requested
        if user_id:
            insights['user_insights'] = self._get_user_specific_insights(user_id)
        
        # System-wide insights
        insights['system_insights'] = self._get_system_wide_insights()
        
        return insights
    
    def _get_orchestrator_health(self) -> Dict[str, Any]:
        """Get orchestrator health status"""
        return {
            'components_initialized': {
                'user_communication_learner': self.user_communication_learner is not None,
                'cultural_intelligence_engine': self.cultural_intelligence_engine is not None,
                'cross_conversation_analyzer': self.cross_conversation_analyzer is not None,
                'existing_validation_learner': self.existing_validation_learner is not None,
                'vector_database': self.vector_database is not None
            },
            'blending_configuration': self.blending_config,
            'processing_stats_available': True
        }
    
    def _get_component_status(self) -> Dict[str, Any]:
        """Get status of all adaptive learning components"""
        status = {}
        
        # User communication learner status
        if self.user_communication_learner:
            status['user_communication'] = self.user_communication_learner.get_system_learning_insights()
        
        # Cultural intelligence engine status
        if self.cultural_intelligence_engine:
            status['cultural_intelligence'] = self.cultural_intelligence_engine.get_cultural_intelligence_insights()
        
        # Cross-conversation analyzer status
        if self.cross_conversation_analyzer:
            status['cross_conversation'] = self.cross_conversation_analyzer.get_cross_conversation_insights()
        
        return status
    
    def _get_user_specific_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights specific to a user"""
        user_insights = {}
        
        # User communication insights
        if self.user_communication_learner:
            user_insights['communication_learning'] = self.user_communication_learner.get_user_learning_insights(user_id)
        
        # Cross-conversation insights
        if self.cross_conversation_analyzer and user_id in self.cross_conversation_analyzer.user_profiles:
            profile = self.cross_conversation_analyzer.user_profiles[user_id]
            user_insights['behavioral_profile'] = {
                'total_conversations': profile.total_conversations,
                'behavioral_confidence': profile.get_behavioral_confidence(),
                'satisfaction_reliability': profile.satisfaction_reliability_score,
                'detected_patterns': len(profile.detected_patterns),
                'communication_trends': {
                    'directness_trend': profile.directness_trend,
                    'politeness_trend': profile.politeness_trend
                }
            }
        
        return user_insights
    
    def _get_system_wide_insights(self) -> Dict[str, Any]:
        """Get system-wide adaptive learning insights"""
        return {
            'accuracy_improvement_target': "92% → 96% (4 percentage point gain)",
            'cultural_adaptation_target': ">85% accuracy across 10+ cultural styles",
            'user_personalization_target': ">90% improvement within 10-20 interactions",
            'cross_conversation_target': ">80% behavioral pattern accuracy",
            'performance_requirement': "<200ms processing latency",
            
            'current_performance': self.processing_stats.get_performance_metrics(),
            'integration_status': {
                'builds_on_existing_system': True,
                'backward_compatible': True,
                'graceful_degradation': self.blending_config['graceful_degradation']
            }
        }


# Helper functions for testing and validation
def test_adaptive_validation_orchestrator():
    """Test adaptive validation orchestrator functionality"""
    orchestrator = AdaptiveValidationOrchestrator()
    
    print("🎯 Testing Adaptive Validation Orchestrator...")
    
    # Test comprehensive adaptive validation
    request = AdaptiveValidationRequest(
        feedback_text="This solution works perfectly for our project setup!",
        solution_context={
            'solution_id': 'test_adaptive_solution',
            'solution_content': 'def adaptive_solution(): return "optimized code"',
            'has_code': True,
            'domain': 'optimization',
            'query': 'optimize performance'
        },
        user_id='test_user_orchestrator',
        user_cultural_profile={
            'language': 'en',
            'communication_style': 'direct',
            'politeness_level': 'medium'
        }
    )
    
    result = orchestrator.process_adaptive_validation(request)
    
    print(f"  Final validation strength: {result.final_validation_strength:.2f}")
    print(f"  Adaptation confidence: {result.adaptation_confidence:.2f}")
    print(f"  Components processed: {result.components_processed}")
    print(f"  Processing time: {result.processing_time:.3f}s")
    print(f"  Performance compliant: {result.performance_compliant}")
    print(f"  Improvement over baseline: {result.improvement_over_baseline:+.2f}")
    print(f"  Explanation: {result.adaptation_explanation}")
    
    if result.recommendations:
        print(f"  Recommendations:")
        for rec in result.recommendations[:3]:
            print(f"    - {rec}")
    
    # Get system insights
    insights = orchestrator.get_adaptive_learning_insights()
    perf_metrics = insights['system_performance']
    
    print(f"\n📊 Orchestrator Insights:")
    print(f"  Success rate: {perf_metrics['success_rate']:.1%}")
    print(f"  Performance compliance: {perf_metrics['performance_compliance_rate']:.1%}")
    print(f"  Average improvement: {perf_metrics['average_improvement']:+.2f}")
    print(f"  Component usage: {perf_metrics['component_usage']}")
    
    print("✅ Adaptive Validation Orchestrator test completed!")
    return orchestrator


if __name__ == "__main__":
    # Run comprehensive functionality test
    test_orchestrator = test_adaptive_validation_orchestrator()