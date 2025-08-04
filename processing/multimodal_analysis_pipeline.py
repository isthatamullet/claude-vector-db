"""
Multi-Modal Analysis Pipeline - Integrated multi-modal analysis system.
OPTIMIZED VERSION with shared embedding model support.

Combines pattern-based, semantic similarity, and technical context analysis methods
with confidence-based weighting and cross-validation for maximum accuracy.

Key Optimizations:
- Shared embedding model support across all sub-components
- Eliminates redundant SentenceTransformer initialization 
- Maintains full backward compatibility
- Same performance and accuracy as original version

Key Features:
- Integrates existing 85% accuracy pattern-based system with new semantic analysis
- Confidence-based weighting algorithm for optimal method combination
- Cross-validation and consistency checking between analysis methods
- >95% method agreement target for high-confidence results
- <250ms end-to-end processing latency
- Fallback strategies for low-confidence scenarios

Targets: 98% explicit and 90% implicit feedback detection accuracy through
sophisticated multi-modal approach.
"""

import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from statistics import mean, stdev

# Import existing pattern-based analysis
from database.enhanced_context import analyze_feedback_sentiment

# Import optimized semantic and technical analyzers
from processing.semantic_feedback_analyzer import SemanticFeedbackAnalyzer
from processing.technical_context_analyzer import TechnicalContextAnalyzer

# Import shared model manager for optimization
from database.shared_embedding_model_manager import get_shared_embedding_model

# Configure logging
logger = logging.getLogger(__name__)


@dataclass 
class MultiModalAnalysisResult:
    """Comprehensive result from multi-modal analysis pipeline"""
    # Final combined results
    semantic_sentiment: str  # Final sentiment determination
    semantic_confidence: float  # Combined confidence score
    primary_analysis_method: str  # Primary method used for final decision
    
    # Multi-modal specific fields
    pattern_vs_semantic_agreement: float  # Agreement between methods
    requires_manual_review: bool  # Flag for low-confidence results
    method_consistency_score: float  # Overall consistency across methods
    
    # Individual method results
    pattern_result: Dict[str, Any]  # Pattern-based analysis results
    semantic_result: Dict[str, Any]  # Semantic similarity results  
    technical_result: Dict[str, Any]  # Technical context results
    
    # Analysis metadata
    processing_time_ms: float  # Total processing time
    method_weights: Dict[str, float]  # Final method weighting
    consistency_details: Dict[str, Any]  # Cross-validation details
    fallback_used: bool  # Whether fallback strategy was used


class PatternBasedAnalyzer:
    """
    Wrapper for existing pattern-based analysis system to provide consistent interface.
    
    Wraps the sophisticated analyze_feedback_sentiment function from enhanced_context.py
    which already achieves 85% accuracy with 3-tier weighted scoring.
    """
    
    def __init__(self):
        """Initialize pattern-based analyzer wrapper"""
        self.method_name = "pattern_based"
        self.stats = {
            'analyses_performed': 0,
            'average_processing_time_ms': 0.0
        }
    
    def analyze_feedback_sentiment_wrapped(self, feedback_content: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Analyze feedback using existing pattern-based system with performance tracking.
        
        Args:
            feedback_content: Feedback text to analyze
            context: Optional context information
            
        Returns:
            Standardized analysis result dictionary
        """
        start_time = time.time()
        
        try:
            # Use existing enhanced_context function
            result = analyze_feedback_sentiment(feedback_content, context or {})
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Update statistics
            self.stats['analyses_performed'] += 1
            total_time = (self.stats['average_processing_time_ms'] * 
                         (self.stats['analyses_performed'] - 1) + processing_time_ms)
            self.stats['average_processing_time_ms'] = total_time / self.stats['analyses_performed']
            
            # Standardize result format
            return {
                'sentiment': result.get('user_feedback_sentiment', 'neutral'),
                'confidence': result.get('validation_strength', 0.0),
                'strength': result.get('validation_strength', 0.0),
                'method': 'pattern_based',
                'processing_time_ms': processing_time_ms,
                'raw_result': result
            }
            
        except Exception as e:
            logger.error(f"Error in pattern-based analysis: {e}")
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'strength': 0.0,
                'method': 'pattern_based_error',
                'processing_time_ms': (time.time() - start_time) * 1000,
                'error': str(e)
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        return self.stats.copy()


class MultiModalAnalysisPipeline:
    """
    Integrated multi-modal analysis pipeline with confidence-based weighting.
    OPTIMIZED VERSION with shared embedding model support.
    
    Combines pattern-based, semantic similarity, and technical context analysis
    with sophisticated cross-validation and consistency checking for maximum accuracy.
    """
    
    def __init__(self, 
                 db,
                 confidence_threshold: float = 0.6,
                 consistency_threshold: float = 0.8,
                 shared_embedding_model: Optional[Union['SentenceTransformer', None]] = None):
        """
        Initialize multi-modal analysis pipeline with shared model optimization.
        
        Args:
            db: Database instance for technical context analysis
            confidence_threshold: Minimum confidence for high-confidence results
            consistency_threshold: Minimum consistency score for method agreement
            shared_embedding_model: Pre-initialized shared model (optimization)
        """
        logger.info("🔀 Initializing MultiModalAnalysisPipeline")
        
        self.db = db
        self.confidence_threshold = confidence_threshold
        self.consistency_threshold = consistency_threshold
        
        # Get or use shared embedding model for all sub-components
        if shared_embedding_model is not None:
            logger.info("⚡ Using provided shared embedding model for all components")
            self.shared_model = shared_embedding_model
            self._using_shared_model = True
        else:
            logger.info("🔄 Obtaining shared embedding model for all components")
            try:
                self.shared_model = get_shared_embedding_model(
                    model_name='all-MiniLM-L6-v2',
                    component_name="MultiModalAnalysisPipeline"
                )
                self._using_shared_model = True
                logger.info("✅ Successfully obtained shared embedding model")
            except Exception as e:
                logger.warning(f"⚠️ Shared model unavailable for pipeline: {e}")
                self.shared_model = None
                self._using_shared_model = False
        
        # Initialize all analysis components with shared model
        self.pattern_analyzer = PatternBasedAnalyzer()  # Existing 85% accuracy system
        self.semantic_analyzer = SemanticFeedbackAnalyzer(
            shared_embedding_model=self.shared_model
        )  # New semantic system
        self.technical_analyzer = TechnicalContextAnalyzer()  # New technical system
        
        # Configuration
        self.method_weights = {
            'pattern_based': 0.4,      # Proven 85% accuracy system
            'semantic_similarity': 0.4, # New semantic analysis
            'technical_context': 0.2    # Technical domain awareness
        }
        
        # Performance tracking
        self.stats = {
            'analyses_performed': 0,
            'high_confidence_results': 0,
            'method_agreements': 0,
            'fallback_used': 0,
            'average_processing_time_ms': 0.0,
            'method_performance': {
                'pattern_based': {'count': 0, 'avg_confidence': 0.0},
                'semantic_similarity': {'count': 0, 'avg_confidence': 0.0},
                'technical_context': {'count': 0, 'avg_confidence': 0.0}
            },
            'using_shared_model': self._using_shared_model
        }
        
        component_info = "shared model" if self._using_shared_model else "individual models"
        logger.info(f"✅ MultiModalAnalysisPipeline initialized with 3 analysis methods ({component_info})")
    
    def analyze_feedback_multimodal(self, 
                                   feedback_content: str,
                                   context: Optional[Dict[str, Any]] = None) -> MultiModalAnalysisResult:
        """
        Perform comprehensive multi-modal feedback analysis.
        
        Args:
            feedback_content: Feedback text to analyze
            context: Optional context information for enhanced analysis
            
        Returns:
            MultiModalAnalysisResult with comprehensive analysis
        """
        start_time = time.time()
        fallback_used = False
        
        try:
            # Run all analysis methods in parallel conceptually
            logger.debug(f"🔍 Starting multi-modal analysis for: '{feedback_content[:50]}...'")
            
            # 1. Pattern-based analysis (existing system)
            pattern_result = self.pattern_analyzer.analyze_feedback_sentiment_wrapped(
                feedback_content, context
            )
            
            # 2. Semantic similarity analysis (new system)
            semantic_analysis = self.semantic_analyzer.analyze_feedback_sentiment(
                feedback_content, context
            )
            semantic_result = {
                'sentiment': semantic_analysis.semantic_sentiment,
                'confidence': semantic_analysis.semantic_confidence,
                'strength': semantic_analysis.semantic_strength,
                'method': 'semantic_similarity',
                'processing_time_ms': semantic_analysis.processing_time_ms,
                'best_patterns': semantic_analysis.best_matching_patterns
            }
            
            # 3. Technical context analysis
            technical_analysis = self.technical_analyzer.analyze_technical_context(
                feedback_content, context
            )
            technical_result = {
                'sentiment': technical_analysis.get('technical_sentiment', 'neutral'),
                'confidence': technical_analysis.get('technical_confidence', 0.0),
                'strength': technical_analysis.get('technical_confidence', 0.0),
                'method': 'technical_context',
                'processing_time_ms': technical_analysis.get('processing_time_ms', 0.0),
                'domain': technical_analysis.get('technical_domain', 'general')
            }
            
            # Calculate method agreement and consistency
            agreement_analysis = self._calculate_method_agreement([
                pattern_result, semantic_result, technical_result
            ])
            
            # Apply confidence-based weighting to determine final result
            final_result = self._apply_confidence_weighting([
                pattern_result, semantic_result, technical_result
            ], agreement_analysis)
            
            # Check if manual review is required
            requires_manual_review = (
                final_result['confidence'] < self.confidence_threshold or
                agreement_analysis['consistency_score'] < self.consistency_threshold
            )
            
            # Update performance statistics
            self._update_performance_stats(pattern_result, semantic_result, technical_result)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Update pipeline statistics
            self.stats['analyses_performed'] += 1
            if final_result['confidence'] >= self.confidence_threshold:
                self.stats['high_confidence_results'] += 1
            if agreement_analysis['consistency_score'] >= self.consistency_threshold:
                self.stats['method_agreements'] += 1
            
            total_time = (self.stats['average_processing_time_ms'] * 
                         (self.stats['analyses_performed'] - 1) + processing_time_ms)
            self.stats['average_processing_time_ms'] = total_time / self.stats['analyses_performed']
            
            return MultiModalAnalysisResult(
                semantic_sentiment=final_result['sentiment'],
                semantic_confidence=final_result['confidence'],
                primary_analysis_method=final_result['primary_method'],
                pattern_vs_semantic_agreement=agreement_analysis['pattern_semantic_agreement'],
                requires_manual_review=requires_manual_review,
                method_consistency_score=agreement_analysis['consistency_score'],
                pattern_result=pattern_result,
                semantic_result=semantic_result,
                technical_result=technical_result,
                processing_time_ms=processing_time_ms,
                method_weights=self.method_weights.copy(),
                consistency_details=agreement_analysis,
                fallback_used=fallback_used
            )
            
        except Exception as e:
            logger.error(f"Error in multi-modal analysis: {e}")
            fallback_used = True
            self.stats['fallback_used'] += 1
            
            # Fallback to pattern-based analysis only
            try:
                fallback_result = self.pattern_analyzer.analyze_feedback_sentiment_wrapped(
                    feedback_content, context
                )
                
                return MultiModalAnalysisResult(
                    semantic_sentiment=fallback_result.get('sentiment', 'neutral'),
                    semantic_confidence=fallback_result.get('confidence', 0.0),
                    primary_analysis_method='pattern_based_fallback',
                    pattern_vs_semantic_agreement=0.0,
                    requires_manual_review=True,
                    method_consistency_score=0.0,
                    pattern_result=fallback_result,
                    semantic_result={'error': str(e)},
                    technical_result={'error': str(e)},
                    processing_time_ms=(time.time() - start_time) * 1000,
                    method_weights={'pattern_based': 1.0},
                    consistency_details={'error': str(e)},
                    fallback_used=True
                )
                
            except Exception as fallback_error:
                logger.error(f"Fallback analysis also failed: {fallback_error}")
                
                # Complete failure fallback
                return MultiModalAnalysisResult(
                    semantic_sentiment='neutral',
                    semantic_confidence=0.0,
                    primary_analysis_method='error_fallback',
                    pattern_vs_semantic_agreement=0.0,
                    requires_manual_review=True,
                    method_consistency_score=0.0,
                    pattern_result={'error': str(e)},
                    semantic_result={'error': str(e)},
                    technical_result={'error': str(e)},
                    processing_time_ms=(time.time() - start_time) * 1000,
                    method_weights={},
                    consistency_details={'error': str(e)},
                    fallback_used=True
                )
    
    def _calculate_method_agreement(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate agreement and consistency between analysis methods"""
        
        try:
            pattern_result, semantic_result, technical_result = results
            
            # Extract sentiments for comparison
            sentiments = [
                pattern_result.get('sentiment', 'neutral'),
                semantic_result.get('sentiment', 'neutral'),
                technical_result.get('sentiment', 'neutral')
            ]
            
            # Calculate pairwise agreements
            pattern_semantic_agreement = 1.0 if sentiments[0] == sentiments[1] else 0.0
            pattern_technical_agreement = 1.0 if sentiments[0] == sentiments[2] else 0.0
            semantic_technical_agreement = 1.0 if sentiments[1] == sentiments[2] else 0.0
            
            # Overall consistency score
            total_agreements = pattern_semantic_agreement + pattern_technical_agreement + semantic_technical_agreement
            consistency_score = total_agreements / 3.0
            
            # Confidence-based agreement (weighted by individual confidences)
            confidences = [
                pattern_result.get('confidence', 0.0),
                semantic_result.get('confidence', 0.0),
                technical_result.get('confidence', 0.0)
            ]
            
            confidence_weighted_agreement = 0.0
            if sum(confidences) > 0:
                for i in range(len(sentiments)):
                    for j in range(i + 1, len(sentiments)):
                        if sentiments[i] == sentiments[j]:
                            weight = (confidences[i] + confidences[j]) / 2
                            confidence_weighted_agreement += weight
                
                confidence_weighted_agreement /= 3.0  # Normalize
            
            return {
                'pattern_semantic_agreement': pattern_semantic_agreement,
                'pattern_technical_agreement': pattern_technical_agreement,
                'semantic_technical_agreement': semantic_technical_agreement,
                'consistency_score': consistency_score,
                'confidence_weighted_agreement': confidence_weighted_agreement,
                'sentiment_distribution': {
                    'positive': sentiments.count('positive'),
                    'negative': sentiments.count('negative'),
                    'partial': sentiments.count('partial'),
                    'neutral': sentiments.count('neutral')
                }
            }
            
        except Exception as e:
            logger.error(f"Error calculating method agreement: {e}")
            return {
                'pattern_semantic_agreement': 0.0,
                'pattern_technical_agreement': 0.0,
                'semantic_technical_agreement': 0.0,
                'consistency_score': 0.0,
                'confidence_weighted_agreement': 0.0,
                'error': str(e)
            }
    
    def _apply_confidence_weighting(self, results: List[Dict[str, Any]], agreement: Dict[str, Any]) -> Dict[str, Any]:
        """Apply confidence-based weighting to combine method results"""
        
        try:
            pattern_result, semantic_result, technical_result = results
            
            # Get confidences and sentiments
            methods_data = [
                ('pattern_based', pattern_result.get('confidence', 0.0), pattern_result.get('sentiment', 'neutral')),
                ('semantic_similarity', semantic_result.get('confidence', 0.0), semantic_result.get('sentiment', 'neutral')),
                ('technical_context', technical_result.get('confidence', 0.0), technical_result.get('sentiment', 'neutral'))
            ]
            
            # Boost confidence based on method agreement
            consistency_boost = 1.0 + (agreement.get('consistency_score', 0.0) * 0.2)  # Up to 20% boost
            
            # Calculate weighted confidences
            weighted_results = []
            for method_name, confidence, sentiment in methods_data:
                base_weight = self.method_weights.get(method_name, 0.33)
                boosted_confidence = confidence * consistency_boost
                weighted_confidence = base_weight * boosted_confidence
                weighted_results.append((method_name, weighted_confidence, sentiment, confidence))
            
            # Find the method with highest weighted confidence
            best_method = max(weighted_results, key=lambda x: x[1])
            primary_method, final_confidence, final_sentiment, raw_confidence = best_method
            
            # If confidence is still low, check for consensus
            if final_confidence < self.confidence_threshold:
                sentiment_counts = {}
                for _, _, sentiment, _ in weighted_results:
                    sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
                
                # Use consensus if available
                if max(sentiment_counts.values()) >= 2:
                    consensus_sentiment = max(sentiment_counts, key=sentiment_counts.get)
                    final_sentiment = consensus_sentiment
                    final_confidence = min(self.confidence_threshold, final_confidence * 1.1)  # Slight boost
                    primary_method = f"{primary_method}_consensus"
            
            return {
                'sentiment': final_sentiment,
                'confidence': final_confidence,
                'primary_method': primary_method,
                'weighted_results': weighted_results,
                'consistency_boost_applied': consistency_boost
            }
            
        except Exception as e:
            logger.error(f"Error in confidence weighting: {e}")
            # Fallback to first result
            return {
                'sentiment': results[0].get('sentiment', 'neutral'),
                'confidence': results[0].get('confidence', 0.0),
                'primary_method': 'fallback_first_method',
                'error': str(e)
            }
    
    def _update_performance_stats(self, pattern_result: Dict, semantic_result: Dict, technical_result: Dict):
        """Update method-specific performance statistics"""
        
        methods = [
            ('pattern_based', pattern_result),
            ('semantic_similarity', semantic_result),
            ('technical_context', technical_result)
        ]
        
        for method_name, result in methods:
            if result and 'confidence' in result:
                method_stats = self.stats['method_performance'][method_name]
                
                # Update count and running average confidence
                current_count = method_stats['count']
                current_avg = method_stats['avg_confidence']
                new_confidence = result['confidence']
                
                new_count = current_count + 1
                new_avg = (current_avg * current_count + new_confidence) / new_count
                
                method_stats['count'] = new_count
                method_stats['avg_confidence'] = new_avg
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics"""
        
        # Calculate rates
        total_analyses = max(1, self.stats['analyses_performed'])
        high_confidence_rate = self.stats['high_confidence_results'] / total_analyses
        agreement_rate = self.stats['method_agreements'] / total_analyses
        fallback_rate = self.stats['fallback_used'] / total_analyses
        
        return {
            'analyses_performed': self.stats['analyses_performed'],
            'high_confidence_rate': high_confidence_rate,
            'method_agreement_rate': agreement_rate,
            'fallback_rate': fallback_rate,
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'method_performance': self.stats['method_performance'],
            'using_shared_model': self.stats['using_shared_model'],
            'configuration': {
                'confidence_threshold': self.confidence_threshold,
                'consistency_threshold': self.consistency_threshold,
                'method_weights': self.method_weights
            }
        }


# Convenience function for backward compatibility
def analyze_multimodal_feedback(feedback_content: str,
                              context: Optional[Dict] = None,
                              db=None,
                              shared_embedding_model: Optional['SentenceTransformer'] = None) -> Dict[str, Any]:
    """
    Convenience function for multi-modal feedback analysis with shared model support.
    
    Args:
        feedback_content: Feedback text to analyze
        context: Optional context information
        db: Database instance
        shared_embedding_model: Optional shared model for optimization
        
    Returns:
        Dictionary with analysis results
    """
    pipeline = MultiModalAnalysisPipeline(db, shared_embedding_model=shared_embedding_model)
    result = pipeline.analyze_feedback_multimodal(feedback_content, context)
    
    return {
        'semantic_sentiment': result.semantic_sentiment,
        'semantic_confidence': result.semantic_confidence,
        'primary_method': result.primary_analysis_method,
        'requires_manual_review': result.requires_manual_review,
        'processing_time_ms': result.processing_time_ms,
        'method_consistency': result.method_consistency_score
    }


if __name__ == "__main__":
    print("🔀 MultiModalAnalysisPipeline Optimized Demo")
    print("=" * 50)
    
    # Mock database for demo
    class MockDB:
        pass
    
    db = MockDB()
    
    # Test with shared model optimization
    print("\n1. Testing with shared model optimization:")
    pipeline = MultiModalAnalysisPipeline(db)
    
    # Test various feedback types
    test_cases = [
        "That worked perfectly! The issue is completely resolved now.",
        "Still not working, getting the same build error as before.",
        "Better but still having some occasional timeout issues.",
        "The documentation could be clearer about the installation process."
    ]
    
    for i, feedback in enumerate(test_cases, 1):
        print(f"\n   Test {i}: '{feedback[:60]}...'")
        result = pipeline.analyze_feedback_multimodal(feedback)
        print(f"   → Final sentiment: {result.semantic_sentiment}")
        print(f"   → Confidence: {result.semantic_confidence:.3f}")
        print(f"   → Primary method: {result.primary_analysis_method}")
        print(f"   → Method consistency: {result.method_consistency_score:.3f}")
        print(f"   → Manual review needed: {result.requires_manual_review}")
        print(f"   → Processing time: {result.processing_time_ms:.1f}ms")
    
    print(f"\n2. Performance statistics:")
    stats = pipeline.get_stats()
    for key, value in stats.items():
        if key != 'method_performance':  # Skip nested dict for brevity
            print(f"   {key}: {value}")
    
    print(f"\n3. Method performance breakdown:")
    for method, perf in stats['method_performance'].items():
        print(f"   {method}: {perf['count']} analyses, avg confidence {perf['avg_confidence']:.3f}")
    
    print(f"\n✅ MultiModalAnalysisPipeline optimized demo completed!")