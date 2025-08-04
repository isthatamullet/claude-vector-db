#!/usr/bin/env python3
"""
Cultural Intelligence Engine for Adaptive Learning Validation System
Implements cross-cultural communication adaptation and intelligence using Transformers 4.53.3.

Based on PRP-3: Adaptive Learning Validation System (July 2025)
Uses latest sentiment analysis models with cultural communication pattern awareness.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np
from datetime import datetime

# Transformers 4.53.3 for multi-language sentiment analysis
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
except ImportError as e:
    logging.error(f"Transformers not available - install with: pip install transformers torch")
    raise ImportError("Transformers framework required for cultural intelligence") from e

# Language detection
try:
    import langdetect
except ImportError:
    # Fallback to basic language detection
    langdetect = None
    logging.warning("langdetect not available - using basic language detection")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CulturalIntelligenceContext:
    """
    Cultural intelligence context for communication analysis.
    
    Captures cultural communication patterns, adjustment factors,
    and confidence scores for culturally-aware validation.
    """
    language: str
    communication_directness: str  # 'direct', 'indirect'
    context_dependency: str  # 'high_context', 'low_context'
    politeness_level: str  # 'high', 'medium', 'low'
    cultural_adjustment_factors: Dict[str, float] = field(default_factory=dict)
    confidence_score: float = 0.0
    explanation: str = ""
    bias_prevention_applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'language': self.language,
            'communication_directness': self.communication_directness,
            'context_dependency': self.context_dependency,
            'politeness_level': self.politeness_level,
            'cultural_adjustment_factors': self.cultural_adjustment_factors,
            'confidence_score': self.confidence_score,
            'explanation': self.explanation,
            'bias_prevention_applied': self.bias_prevention_applied
        }


class CulturalIntelligenceEngine:
    """
    Cross-cultural communication adaptation and intelligence.
    
    Analyzes user feedback with cultural communication norm awareness,
    applies appropriate cultural adjustments, and prevents cultural bias
    while improving validation accuracy across diverse user populations.
    """
    
    def __init__(self):
        # Sentiment analysis models for different languages (Transformers 4.53.3)
        self.sentiment_models = {}
        self._initialize_sentiment_models()
        
        # Cultural communication patterns (from cultural intelligence guide)
        self.cultural_patterns = self._load_cultural_patterns()
        
        # Bias prevention thresholds (critical for ethical AI)
        self.bias_prevention = {
            'max_cultural_boost': 1.5,  # Maximum cultural adjustment
            'min_cultural_penalty': 0.7,  # Minimum cultural adjustment  
            'bias_threshold': 0.2  # Maximum disparity between cultures
        }
        
        # Performance tracking
        self.processing_stats = {
            'total_analyses': 0,
            'cultural_adjustments_applied': 0,
            'bias_prevention_triggers': 0,
            'average_processing_time': 0.0,
            'performance_violations': 0
        }
        
        # Cultural adjustment cache for performance
        self.cultural_cache = {}
        self.cache_max_size = 1000
        
        logger.info("🌍 Cultural Intelligence Engine initialized with multi-language support")
    
    def _initialize_sentiment_models(self):
        """Initialize sentiment analysis models for different languages"""
        try:
            # English model (latest sentiment analysis)
            self.sentiment_models['english'] = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                return_all_scores=True
            )
            
            # Multilingual model
            self.sentiment_models['multilingual'] = pipeline(
                "sentiment-analysis",
                model="nlptown/bert-base-multilingual-uncased-sentiment",
                return_all_scores=True
            )
            
            logger.info("✅ Sentiment analysis models loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load sentiment models: {e}")
            # Create fallback models
            self.sentiment_models = {
                'english': None,
                'multilingual': None
            }
    
    def _load_cultural_patterns(self) -> Dict[str, Any]:
        """Load cultural communication patterns"""
        return {
            'direct_cultures': {
                'languages': ['en', 'de', 'nl', 'da', 'sv'],
                'feedback_interpretation': {
                    'positive_threshold': 0.6,
                    'negative_threshold': 0.4,
                    'adjustment_factor': 1.0
                },
                'linguistic_markers': [
                    'exactly', 'clearly', 'definitely', 'obviously',
                    'wrong', 'incorrect', 'doesn\'t work', 'failed'
                ]
            },
            'indirect_cultures': {
                'languages': ['ja', 'ko', 'th', 'id', 'my'],
                'feedback_interpretation': {
                    'positive_threshold': 0.8,  # Higher threshold needed
                    'negative_threshold': 0.3,  # Lower threshold for negative
                    'adjustment_factor': 1.3    # Amplify subtle signals
                },
                'linguistic_markers': [
                    'maybe', 'perhaps', 'might', 'could be',
                    'not quite', 'somewhat', 'a bit', 'slightly'
                ]
            },
            'high_context': {
                'languages': ['ja', 'ar', 'zh', 'ko'],
                'requires_conversation_history': True,
                'implicit_meaning_weight': 0.7,
                'explicit_meaning_weight': 0.3,
                'context_window': 5  # Previous messages to consider
            },
            'low_context': {
                'languages': ['en', 'de', 'sv', 'fi'],
                'requires_conversation_history': False,
                'implicit_meaning_weight': 0.2,
                'explicit_meaning_weight': 0.8,
                'context_window': 1  # Current message sufficient
            }
        }
    
    def analyze_with_cultural_intelligence(self, feedback_text: str, 
                                         user_cultural_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze feedback with cultural communication norm awareness.
        
        Args:
            feedback_text: User's feedback text
            user_cultural_profile: User's cultural profile information
            
        Returns:
            Dictionary with culturally-adjusted analysis results
        """
        # PERFORMANCE: Timing for <200ms compliance
        start_time = time.time()
        
        try:
            # Detect language if not provided
            language = user_cultural_profile.get('language', 'auto')
            if language == 'auto':
                language = self._detect_language(feedback_text)
            
            # Get base sentiment analysis
            base_sentiment = self._get_base_sentiment(feedback_text, language)
            
            # Create cultural context
            cultural_context = self._create_cultural_context(user_cultural_profile, language)
            
            # Apply cultural adaptation
            cultural_adjustments = self._calculate_cultural_adjustments(
                base_sentiment, cultural_context, feedback_text
            )
            
            # Apply adjustments with bias prevention
            adjusted_sentiment = self._apply_cultural_adjustments_with_bias_prevention(
                base_sentiment, cultural_adjustments, cultural_context
            )
            
            # Calculate cultural confidence
            cultural_confidence = self._calculate_cultural_confidence(cultural_context, feedback_text)
            
            # Performance tracking
            processing_time = time.time() - start_time
            self._update_processing_stats(processing_time, cultural_adjustments)
            
            # Validate performance requirement
            performance_compliant = processing_time <= 0.2
            if not performance_compliant:
                self.processing_stats['performance_violations'] += 1
                logger.warning(f"⚠️ Cultural analysis exceeded 200ms: {processing_time:.3f}s")
            
            return {
                'base_sentiment': base_sentiment,
                'cultural_context': cultural_context.to_dict(),
                'culturally_adjusted_sentiment': adjusted_sentiment,
                'cultural_confidence': cultural_confidence,
                'cultural_adjustments_applied': cultural_adjustments,
                'processing_time': processing_time,
                'performance_compliant': performance_compliant,
                'bias_prevention_applied': cultural_context.bias_prevention_applied,
                'language_detected': language,
                'explanation': self._generate_cultural_explanation(
                    cultural_context, cultural_adjustments, adjusted_sentiment
                )
            }
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Error in cultural intelligence analysis: {e}")
            return {
                'error': str(e),
                'base_sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                'culturally_adjusted_sentiment': {'label': 'NEUTRAL', 'score': 0.5},
                'cultural_confidence': 0.0,
                'processing_time': processing_time,
                'performance_compliant': processing_time <= 0.2
            }
    
    def _detect_language(self, text: str) -> str:
        """Detect language of the text"""
        try:
            if langdetect:
                detected = langdetect.detect(text)
                return detected
            else:
                # Basic fallback - check for common non-English characters
                if any(ord(char) > 127 for char in text):
                    # Has non-ASCII characters - likely non-English
                    if any(char in text for char in '你我他她它们'):
                        return 'zh'
                    elif any(char in text for char in 'あいうえおかきくけこ'):
                        return 'ja'
                    elif any(char in text for char in '안녕하세요감사합니다'):
                        return 'ko'
                    else:
                        return 'unknown'
                else:
                    return 'en'  # ASCII only - likely English
        except Exception:
            return 'en'  # Default to English
    
    def _get_base_sentiment(self, text: str, language: str) -> Dict[str, Any]:
        """Get base sentiment analysis for the text"""
        try:
            # Choose appropriate model
            model_key = 'english' if language == 'en' else 'multilingual'
            model = self.sentiment_models.get(model_key)
            
            if model is None:
                # Fallback to simple sentiment analysis
                return self._fallback_sentiment_analysis(text)
            
            # Get sentiment prediction
            results = model(text)
            
            # Process results (models return different formats)
            if isinstance(results, list) and len(results) > 0:
                if isinstance(results[0], list):
                    # Model returns list of scores
                    best_result = max(results[0], key=lambda x: x['score'])
                else:
                    # Model returns single result
                    best_result = results[0]
                
                return {
                    'label': best_result['label'],
                    'score': best_result['score'],
                    'all_scores': results[0] if isinstance(results[0], list) else results,
                    'model_used': model_key
                }
            else:
                return self._fallback_sentiment_analysis(text)
                
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return self._fallback_sentiment_analysis(text)
    
    def _fallback_sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """Simple fallback sentiment analysis"""
        positive_words = ['great', 'excellent', 'perfect', 'works', 'good', 'helpful', 'thanks']
        negative_words = ['wrong', 'broken', 'failed', 'error', 'bad', 'issue', 'problem']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return {'label': 'POSITIVE', 'score': 0.7, 'model_used': 'fallback'}
        elif negative_count > positive_count:
            return {'label': 'NEGATIVE', 'score': 0.7, 'model_used': 'fallback'}
        else:
            return {'label': 'NEUTRAL', 'score': 0.5, 'model_used': 'fallback'}
    
    def _create_cultural_context(self, user_cultural_profile: Dict[str, Any], language: str) -> CulturalIntelligenceContext:
        """Create cultural intelligence context"""
        # Determine communication directness
        directness = self._determine_communication_directness(language, user_cultural_profile)
        
        # Determine context dependency
        context_dependency = self._determine_context_dependency(language)
        
        # Assess politeness level (basic heuristic)
        politeness = user_cultural_profile.get('politeness_level', 'medium')
        
        return CulturalIntelligenceContext(
            language=language,
            communication_directness=directness,
            context_dependency=context_dependency,
            politeness_level=politeness,
            confidence_score=0.0  # Will be calculated later
        )
    
    def _determine_communication_directness(self, language: str, profile: Dict[str, Any]) -> str:
        """Determine if culture uses direct or indirect communication"""
        # Check explicit profile setting first
        if 'communication_style' in profile:
            return profile['communication_style']
        
        # Use language-based heuristics
        direct_languages = self.cultural_patterns['direct_cultures']['languages']
        indirect_languages = self.cultural_patterns['indirect_cultures']['languages']
        
        if language in direct_languages:
            return 'direct'
        elif language in indirect_languages:
            return 'indirect'
        else:
            return 'unknown'  # Default to neutral approach
    
    def _determine_context_dependency(self, language: str) -> str:
        """Determine if culture uses high-context or low-context communication"""
        high_context_languages = self.cultural_patterns['high_context']['languages']
        low_context_languages = self.cultural_patterns['low_context']['languages']
        
        if language in high_context_languages:
            return 'high_context'
        elif language in low_context_languages:
            return 'low_context'
        else:
            return 'unknown'
    
    def _calculate_cultural_adjustments(self, base_sentiment: Dict[str, Any], 
                                      cultural_context: CulturalIntelligenceContext, 
                                      feedback_text: str) -> Dict[str, float]:
        """Calculate cultural adjustment factors"""
        adjustments = {}
        
        # Directness adjustment
        if cultural_context.communication_directness == 'indirect':
            # Indirect cultures may understate negative feedback
            if base_sentiment['label'] in ['NEGATIVE', 'negative']:
                adjustments['directness_amplification'] = 1.4
            # May overstate politeness in positive feedback
            elif base_sentiment['label'] in ['POSITIVE', 'positive'] and base_sentiment['score'] < 0.7:
                adjustments['politeness_reduction'] = 0.8
            else:
                adjustments['directness_amplification'] = 1.0
        elif cultural_context.communication_directness == 'direct':
            # Direct cultures: take feedback more literally
            adjustments['directness_amplification'] = 1.0
        else:
            adjustments['directness_amplification'] = 1.0
        
        # Context dependency adjustment
        if cultural_context.context_dependency == 'high_context':
            # High-context cultures embed meaning in conversation history
            # For now, apply moderate adjustment - full implementation would need conversation history
            adjustments['context_amplification'] = 1.2
        else:
            adjustments['context_amplification'] = 1.0
        
        # Politeness level adjustment
        if cultural_context.politeness_level == 'high':
            # High politeness cultures may mask true sentiment
            if 'thank' in feedback_text.lower() or 'please' in feedback_text.lower():
                adjustments['politeness_masking'] = 0.9
            else:
                adjustments['politeness_masking'] = 1.0
        else:
            adjustments['politeness_masking'] = 1.0
        
        return adjustments
    
    def _apply_cultural_adjustments_with_bias_prevention(self, base_sentiment: Dict[str, Any], 
                                                       cultural_adjustments: Dict[str, float],
                                                       cultural_context: CulturalIntelligenceContext) -> Dict[str, Any]:
        """Apply cultural adjustments while preventing bias"""
        adjusted_sentiment = base_sentiment.copy()
        
        # Calculate combined adjustment factor
        combined_factor = 1.0
        for adjustment_name, factor in cultural_adjustments.items():
            combined_factor *= factor
        
        # Apply bias prevention limits
        if combined_factor > self.bias_prevention['max_cultural_boost']:
            combined_factor = self.bias_prevention['max_cultural_boost']
            cultural_context.bias_prevention_applied = True
            self.processing_stats['bias_prevention_triggers'] += 1
            logger.info(f"🛡️ Bias prevention: Cultural boost capped at {self.bias_prevention['max_cultural_boost']}x")
        
        if combined_factor < self.bias_prevention['min_cultural_penalty']:
            combined_factor = self.bias_prevention['min_cultural_penalty']
            cultural_context.bias_prevention_applied = True
            self.processing_stats['bias_prevention_triggers'] += 1
            logger.info(f"🛡️ Bias prevention: Cultural penalty capped at {self.bias_prevention['min_cultural_penalty']}x")
        
        # Apply adjustment to sentiment score
        adjusted_score = base_sentiment['score'] * combined_factor
        adjusted_score = max(0.0, min(1.0, adjusted_score))  # Clamp to valid range
        
        # Update label if score crosses thresholds
        if adjusted_score > 0.6 and base_sentiment['label'] not in ['POSITIVE', 'positive']:
            adjusted_label = 'POSITIVE'
        elif adjusted_score < 0.4 and base_sentiment['label'] not in ['NEGATIVE', 'negative']:
            adjusted_label = 'NEGATIVE'
        else:
            adjusted_label = base_sentiment['label']
        
        adjusted_sentiment.update({
            'label': adjusted_label,
            'score': adjusted_score,
            'cultural_adjustment_factor': combined_factor,
            'original_score': base_sentiment['score']
        })
        
        return adjusted_sentiment
    
    def _calculate_cultural_confidence(self, cultural_context: CulturalIntelligenceContext, 
                                     feedback_text: str) -> float:
        """Calculate confidence in cultural analysis"""
        confidence_factors = []
        
        # Language detection confidence
        if cultural_context.language in ['en', 'de', 'ja', 'ko', 'zh']:
            confidence_factors.append(0.8)  # High confidence for common languages
        elif cultural_context.language != 'unknown':
            confidence_factors.append(0.6)  # Medium confidence for detected languages
        else:
            confidence_factors.append(0.2)  # Low confidence for unknown languages
        
        # Communication style confidence
        if cultural_context.communication_directness != 'unknown':
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Context dependency confidence
        if cultural_context.context_dependency != 'unknown':
            confidence_factors.append(0.6)
        else:
            confidence_factors.append(0.3)
        
        # Text length factor (longer text = more confident)
        text_length_factor = min(1.0, len(feedback_text) / 100.0)
        confidence_factors.append(text_length_factor)
        
        # Calculate overall confidence
        overall_confidence = np.mean(confidence_factors) if confidence_factors else 0.0
        cultural_context.confidence_score = overall_confidence
        
        return overall_confidence
    
    def _generate_cultural_explanation(self, cultural_context: CulturalIntelligenceContext,
                                     cultural_adjustments: Dict[str, float],
                                     adjusted_sentiment: Dict[str, Any]) -> str:
        """Generate explanation for cultural adjustments"""
        explanations = []
        
        # Language and directness explanation
        if cultural_context.communication_directness == 'indirect':
            explanations.append(f"Indirect communication culture ({cultural_context.language}): feedback signals may be understated")
        elif cultural_context.communication_directness == 'direct':
            explanations.append(f"Direct communication culture ({cultural_context.language}): feedback taken literally")
        
        # Adjustment explanations
        for adjustment_name, factor in cultural_adjustments.items():
            if abs(factor - 1.0) > 0.1:  # Significant adjustment
                if adjustment_name == 'directness_amplification' and factor > 1.0:
                    explanations.append(f"Amplified subtle negative signals by {factor:.1f}x")
                elif adjustment_name == 'politeness_reduction' and factor < 1.0:
                    explanations.append(f"Reduced politeness-driven positive signals by {1/factor:.1f}x")
                elif adjustment_name == 'context_amplification' and factor > 1.0:
                    explanations.append(f"High-context culture: applied {factor:.1f}x contextual amplification")
        
        # Bias prevention explanation
        if cultural_context.bias_prevention_applied:
            explanations.append("Bias prevention limits applied to ensure fair treatment")
        
        # Confidence explanation
        confidence_level = "high" if cultural_context.confidence_score > 0.7 else "medium" if cultural_context.confidence_score > 0.4 else "low"
        explanations.append(f"Cultural analysis confidence: {confidence_level} ({cultural_context.confidence_score:.2f})")
        
        return "; ".join(explanations) if explanations else "No significant cultural adjustments applied"
    
    def _update_processing_stats(self, processing_time: float, cultural_adjustments: Dict[str, float]):
        """Update processing statistics"""
        self.processing_stats['total_analyses'] += 1
        
        # Check if cultural adjustments were applied
        if any(abs(factor - 1.0) > 0.05 for factor in cultural_adjustments.values()):
            self.processing_stats['cultural_adjustments_applied'] += 1
        
        # Update average processing time
        current_count = self.processing_stats['total_analyses']
        current_avg = self.processing_stats['average_processing_time']
        self.processing_stats['average_processing_time'] = (
            (current_avg * (current_count - 1) + processing_time) / current_count
        )
    
    def get_cultural_intelligence_insights(self) -> Dict[str, Any]:
        """Get insights about cultural intelligence performance"""
        total_analyses = self.processing_stats['total_analyses']
        
        return {
            'total_analyses': total_analyses,
            'cultural_adjustments_rate': (
                self.processing_stats['cultural_adjustments_applied'] / max(1, total_analyses)
            ),
            'bias_prevention_rate': (
                self.processing_stats['bias_prevention_triggers'] / max(1, total_analyses)
            ),
            'average_processing_time': self.processing_stats['average_processing_time'],
            'performance_compliance_rate': (
                (total_analyses - self.processing_stats['performance_violations']) / max(1, total_analyses)
            ),
            'supported_languages': list(set(
                self.cultural_patterns['direct_cultures']['languages'] + 
                self.cultural_patterns['indirect_cultures']['languages']
            )),
            'cultural_patterns_loaded': len(self.cultural_patterns),
            'sentiment_models_available': {
                model_name: model is not None 
                for model_name, model in self.sentiment_models.items()
            },
            'bias_prevention_settings': self.bias_prevention,
            'system_health': {
                'cache_size': len(self.cultural_cache),
                'performance_violations': self.processing_stats['performance_violations'],
                'models_loaded': sum(1 for model in self.sentiment_models.values() if model is not None)
            }
        }


# Helper functions for testing and validation
def test_cultural_intelligence():
    """Test cultural intelligence functionality"""
    engine = CulturalIntelligenceEngine()
    
    # Test cases for different cultures
    test_cases = [
        {
            'text': "This doesn't work at all",
            'culture': {'language': 'en', 'communication_style': 'direct'},
            'expected_adjustment': 1.0  # Direct culture - no adjustment
        },
        {
            'text': "It's not quite what I expected",
            'culture': {'language': 'ja', 'communication_style': 'indirect'},
            'expected_adjustment': 1.3  # Indirect culture - amplify negative
        },
        {
            'text': "Thank you, this helps",
            'culture': {'language': 'ko', 'politeness_level': 'high'},
            'expected_politeness_reduction': True
        }
    ]
    
    print("🌍 Testing Cultural Intelligence...")
    
    for i, case in enumerate(test_cases):
        result = engine.analyze_with_cultural_intelligence(
            case['text'], case['culture']
        )
        
        print(f"  Test {i+1}: {case['culture']['language']} culture")
        print(f"    Base sentiment: {result['base_sentiment']['label']} ({result['base_sentiment']['score']:.2f})")
        print(f"    Adjusted sentiment: {result['culturally_adjusted_sentiment']['label']} ({result['culturally_adjusted_sentiment']['score']:.2f})")
        print(f"    Cultural confidence: {result['cultural_confidence']:.2f}")
        print(f"    Processing time: {result['processing_time']:.3f}s")
        print(f"    Bias prevention: {result['bias_prevention_applied']}")
    
    # Get system insights
    insights = engine.get_cultural_intelligence_insights()
    print(f"\n📊 Cultural Intelligence Insights:")
    print(f"  Total analyses: {insights['total_analyses']}")
    print(f"  Cultural adjustments rate: {insights['cultural_adjustments_rate']:.1%}")
    print(f"  Performance compliance: {insights['performance_compliance_rate']:.1%}")
    print(f"  Supported languages: {len(insights['supported_languages'])}")
    
    print("✅ Cultural Intelligence test completed!")
    return engine


if __name__ == "__main__":
    # Run basic functionality test
    test_engine = test_cultural_intelligence()