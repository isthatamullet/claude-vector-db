#!/usr/bin/env python3
"""
PRP-2 Semantic Validation Enhancement System Standalone Runner

Comprehensive standalone script for running semantic validation enhancement
on conversation data with full integration testing and performance validation.

Features:
- Semantic feedback analysis using all-MiniLM-L6-v2 embeddings
- Technical context classification across 4 domains  
- Multi-modal analysis pipeline integration
- Pattern similarity matching with <50ms performance
- A/B testing validation framework
- ChromaDB integration with semantic metadata
- Enhanced conversation entry processing
- Performance benchmarking and health monitoring

Usage:
    python run_semantic_enhancement.py --help
    python run_semantic_enhancement.py --analyze "That worked perfectly!"
    python run_semantic_enhancement.py --batch-process --input-file conversations.jsonl
    python run_semantic_enhancement.py --ab-test --sample-size 100
    python run_semantic_enhancement.py --health-check
    python run_semantic_enhancement.py --benchmark

Based on PRP-2 specifications targeting 85%→98% explicit and 40%→90% implicit detection.
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all semantic validation components
from semantic_feedback_analyzer import SemanticFeedbackAnalyzer
from technical_context_analyzer import TechnicalContextAnalyzer
from multimodal_analysis_pipeline import MultiModalAnalysisPipeline
from semantic_pattern_manager import SemanticPatternManager
from validation_enhancement_metrics import ValidationEnhancementMetrics
from vector_database import ClaudeVectorDatabase
from enhanced_conversation_entry import EnhancedConversationEntry, SemanticValidationFields
from conversation_extractor import ConversationExtractor, ConversationEntry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SemanticEnhancementRunner:
    """
    Comprehensive semantic enhancement system runner.
    
    Provides unified interface for all semantic validation operations
    including analysis, batch processing, A/B testing, and health monitoring.
    """
    
    def __init__(self, cache_dir: str = "./semantic_cache"):
        """
        Initialize semantic enhancement runner.
        
        Args:
            cache_dir: Directory for caching embeddings and patterns
        """
        logger.info("🚀 Initializing PRP-2 Semantic Enhancement System")
        
        # Initialize core components
        self.db = ClaudeVectorDatabase()
        self.cache_dir = cache_dir
        
        # Initialize analyzers
        self.semantic_analyzer = SemanticFeedbackAnalyzer()
        self.technical_analyzer = TechnicalContextAnalyzer()
        self.multimodal_pipeline = MultiModalAnalysisPipeline(self.db)
        self.pattern_manager = SemanticPatternManager(self.db, cache_dir=cache_dir)
        self.validation_metrics = ValidationEnhancementMetrics()
        
        # Performance tracking
        self.performance_stats = {
            'total_analyses': 0,
            'total_time_ms': 0.0,
            'average_time_ms': 0.0,
            'fastest_time_ms': float('inf'),
            'slowest_time_ms': 0.0
        }
        
        logger.info("✅ Semantic Enhancement System initialized successfully")
    
    def analyze_single_feedback(self, feedback_content: str, 
                               context: Optional[Dict[str, Any]] = None,
                               analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze single feedback using specified analysis type.
        
        Args:
            feedback_content: Feedback text to analyze
            context: Optional solution context
            analysis_type: Type of analysis ("semantic", "technical", "pattern", "comprehensive")
            
        Returns:
            Analysis results with performance metrics
        """
        start_time = time.time()
        context = context or {}
        
        logger.info(f"🔍 Analyzing feedback: '{feedback_content[:50]}...' (type: {analysis_type})")
        
        results = {
            "input": {
                "feedback_content": feedback_content,
                "context": context,
                "analysis_type": analysis_type
            },
            "analysis_results": {},
            "performance_metrics": {},
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        try:
            if analysis_type in ["semantic", "comprehensive"]:
                # Semantic analysis
                semantic_result = self.semantic_analyzer.analyze_semantic_feedback(feedback_content, context)
                results["analysis_results"]["semantic"] = {
                    "sentiment": semantic_result.semantic_sentiment,
                    "confidence": semantic_result.semantic_confidence,
                    "method": semantic_result.method,
                    "positive_similarity": semantic_result.positive_similarity,
                    "negative_similarity": semantic_result.negative_similarity,
                    "partial_similarity": semantic_result.partial_similarity,
                    "processing_time_ms": semantic_result.processing_time_ms
                }
            
            if analysis_type in ["technical", "comprehensive"]:
                # Technical context analysis
                technical_result = self.technical_analyzer.analyze_technical_feedback(feedback_content, context)
                results["analysis_results"]["technical"] = {
                    "primary_domain": technical_result.technical_domain,
                    "domain_confidence": technical_result.technical_confidence,
                    "complex_outcome_detected": technical_result.complex_outcome_detected,
                    "domain_scores": technical_result.domain_scores,
                    "processing_time_ms": technical_result.processing_time_ms
                }
            
            if analysis_type in ["pattern", "comprehensive"]:
                # Pattern similarity analysis
                pattern_result = self.pattern_manager.get_pattern_similarity(feedback_content)
                results["analysis_results"]["pattern"] = {
                    "best_matches": pattern_result.best_matches[:3],
                    "similarities": pattern_result.similarities[:3],
                    "pattern_types": pattern_result.pattern_types[:3],
                    "max_similarity": pattern_result.max_similarity,
                    "dominant_pattern_type": pattern_result.dominant_pattern_type,
                    "processing_time_ms": pattern_result.processing_time_ms,
                    "cache_hit": pattern_result.cache_hit
                }
            
            if analysis_type == "comprehensive":
                # Multi-modal comprehensive analysis
                feedback_data = {
                    "content": feedback_content,
                    "context": context,
                    "options": {}
                }
                multimodal_result = self.multimodal_pipeline.analyze_feedback_comprehensive(feedback_data)
                results["analysis_results"]["multimodal"] = {
                    "final_sentiment": multimodal_result.semantic_sentiment,
                    "confidence": multimodal_result.semantic_confidence,
                    "primary_method": multimodal_result.primary_analysis_method,
                    "method_agreement": multimodal_result.pattern_vs_semantic_agreement,
                    "processing_time_ms": multimodal_result.processing_time_ms
                }
            
            # Calculate performance metrics
            total_time = (time.time() - start_time) * 1000
            self._update_performance_stats(total_time)
            
            results["performance_metrics"] = {
                "total_processing_time_ms": total_time,
                "performance_target_met": total_time < 2000,  # 2 second target for comprehensive
                "analysis_type": analysis_type
            }
            
            logger.info(f"✅ Analysis complete ({total_time:.1f}ms)")
            return results
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {e}")
            results["error"] = str(e)
            results["analysis_results"] = None
            return results
    
    def batch_process_conversations(self, input_file: str, 
                                  output_file: Optional[str] = None,
                                  max_entries: Optional[int] = None) -> Dict[str, Any]:
        """
        Batch process conversations from JSONL file with semantic enhancement.
        
        Args:
            input_file: Path to input JSONL conversation file
            output_file: Optional output file for enhanced results
            max_entries: Maximum number of entries to process
            
        Returns:
            Batch processing results and statistics
        """
        logger.info(f"📦 Starting batch processing: {input_file}")
        
        input_path = Path(input_file)
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")
        
        output_path = Path(output_file) if output_file else input_path.with_suffix('.enhanced.jsonl')
        
        start_time = time.time()
        processed_count = 0
        enhanced_entries = []
        error_count = 0
        
        try:
            with open(input_path, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    if max_entries and processed_count >= max_entries:
                        break
                    
                    try:
                        # Parse conversation entry
                        data = json.loads(line.strip())
                        
                        # Create base conversation entry
                        base_entry = ConversationEntry(
                            id=data.get('id', f'entry_{line_num}'),
                            content=data.get('content', ''),
                            type=data.get('type', 'unknown'),
                            project_path=data.get('project_path', ''),
                            project_name=data.get('project_name', ''),
                            timestamp=data.get('timestamp', ''),
                            session_id=data.get('session_id'),
                            file_name=data.get('file_name', input_file),
                            has_code=data.get('has_code', False),
                            tools_used=data.get('tools_used', []),
                            content_length=len(data.get('content', ''))
                        )
                        
                        # Skip empty content
                        if not base_entry.content.strip():
                            continue
                        
                        # Run semantic analysis
                        analysis_result = self.analyze_single_feedback(
                            base_entry.content,
                            context={"project": base_entry.project_name, "type": base_entry.type},
                            analysis_type="comprehensive"
                        )
                        
                        # Create semantic validation fields
                        if not analysis_result.get("error"):
                            semantic_results = analysis_result["analysis_results"]
                            
                            semantic_fields = SemanticValidationFields(
                                semantic_sentiment=semantic_results.get("semantic", {}).get("sentiment", "neutral"),
                                semantic_confidence=semantic_results.get("semantic", {}).get("confidence", 0.0),
                                semantic_method="multimodal" if "multimodal" in semantic_results else "semantic",
                                positive_similarity=semantic_results.get("semantic", {}).get("positive_similarity", 0.0),
                                negative_similarity=semantic_results.get("semantic", {}).get("negative_similarity", 0.0),
                                partial_similarity=semantic_results.get("semantic", {}).get("partial_similarity", 0.0),
                                technical_domain=semantic_results.get("technical", {}).get("primary_domain", "unknown"),
                                technical_confidence=semantic_results.get("technical", {}).get("domain_confidence", 0.0),
                                complex_outcome_detected=semantic_results.get("technical", {}).get("complex_outcome_detected", False),
                                pattern_vs_semantic_agreement=semantic_results.get("multimodal", {}).get("method_agreement", 0.0),
                                primary_analysis_method=semantic_results.get("multimodal", {}).get("primary_method", "semantic"),
                                requires_manual_review=False,
                                best_matching_patterns=json.dumps(semantic_results.get("pattern", {}).get("best_matches", [])),
                                semantic_analysis_details=json.dumps(semantic_results)
                            )
                            
                            # Create enhanced conversation entry
                            enhanced_entry = EnhancedConversationEntry.from_base_entry(
                                base_entry,
                                semantic_validation=semantic_fields
                            )
                            
                            enhanced_entries.append(enhanced_entry)
                        
                        processed_count += 1
                        
                        if processed_count % 100 == 0:
                            logger.info(f"📊 Processed {processed_count} entries...")
                    
                    except Exception as e:
                        logger.warning(f"Error processing line {line_num}: {e}")
                        error_count += 1
            
            # Write enhanced results
            if enhanced_entries:
                with open(output_path, 'w') as f:
                    for entry in enhanced_entries:
                        enhanced_data = {
                            **entry.to_semantic_enhanced_metadata(),
                            "content": entry.content,
                            "id": entry.id
                        }
                        f.write(json.dumps(enhanced_data) + '\n')
                
                logger.info(f"💾 Enhanced results written to: {output_path}")
            
            # Calculate statistics
            total_time = time.time() - start_time
            
            results = {
                "batch_processing_summary": {
                    "input_file": str(input_path),
                    "output_file": str(output_path),
                    "total_entries_processed": processed_count,
                    "enhanced_entries_created": len(enhanced_entries),
                    "error_count": error_count,
                    "processing_time_seconds": total_time,
                    "average_time_per_entry_ms": (total_time * 1000) / max(1, processed_count)
                },
                "performance_metrics": self.performance_stats.copy(),
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            
            logger.info(f"✅ Batch processing complete: {processed_count} entries in {total_time:.1f}s")
            return results
            
        except Exception as e:
            logger.error(f"❌ Batch processing failed: {e}")
            raise
    
    async def run_ab_test_validation(self, sample_size: int = 100, 
                                   test_queries: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Run A/B test validation of semantic enhancement effectiveness.
        
        Args:
            sample_size: Number of test iterations per system
            test_queries: Optional custom test queries
            
        Returns:
            A/B test results with statistical analysis
        """
        logger.info(f"🧪 Running A/B test validation (sample size: {sample_size})")
        
        if not test_queries:
            # Use default test queries covering various feedback types
            test_queries = [
                # Explicit positive
                "That worked perfectly!",
                "Excellent solution!",
                "Problem solved completely!",
                
                # Explicit negative
                "That doesn't work at all",
                "Still getting the same error",
                "This approach failed",
                
                # Partial success
                "Almost there, minor issues remain",
                "Better but still some problems",
                "Mostly working, edge cases fail",
                
                # Implicit feedback (key PRP-2 target)
                "Let me try something else",
                "Moving on to the next issue",
                "Hmm, interesting error now",
                "Build passes but tests are failing",
                "Could you help with something else?"
            ]
        
        try:
            # Run A/B test
            test_result = await self.validation_metrics.run_ab_test_validation(
                test_queries=test_queries,
                baseline_system="pattern_only",
                enhanced_system="multimodal",
                sample_size=sample_size
            )
            
            # Calculate statistical significance
            statistical_analysis = self.validation_metrics.calculate_statistical_significance(test_result)
            
            results = {
                "ab_test_configuration": {
                    "sample_size": sample_size,
                    "test_queries_count": len(test_queries),
                    "baseline_system": "pattern_only",
                    "enhanced_system": "multimodal"
                },
                "test_results": {
                    "baseline_performance": test_result.baseline_metrics,
                    "enhanced_performance": test_result.enhanced_metrics,
                    "improvement_summary": test_result.improvement_summary,
                    "test_duration_seconds": test_result.test_duration_seconds
                },
                "statistical_analysis": {
                    "p_value": statistical_analysis.p_value,
                    "confidence_interval": statistical_analysis.confidence_interval,
                    "significance_level": statistical_analysis.significance_level,
                    "statistically_significant": statistical_analysis.is_significant,
                    "effect_size": statistical_analysis.effect_size
                },
                "recommendations": test_result.recommendations,
                "metadata": {
                    "timestamp": datetime.now().isoformat(),
                    "version": "1.0"
                }
            }
            
            # Print summary
            logger.info("📊 A/B Test Results Summary:")
            logger.info(f"   Baseline accuracy: {test_result.baseline_metrics.get('accuracy', 0):.1%}")
            logger.info(f"   Enhanced accuracy: {test_result.enhanced_metrics.get('accuracy', 0):.1%}")
            logger.info(f"   Improvement: {test_result.improvement_summary.get('accuracy_improvement', 0):.1%}")
            logger.info(f"   Statistically significant: {statistical_analysis.is_significant}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ A/B test validation failed: {e}")
            raise
    
    def run_health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive health check of semantic validation system.
        
        Returns:
            Health status of all components
        """
        logger.info("🏥 Running semantic validation system health check")
        
        health_results = {
            "overall_health": "healthy",
            "component_status": {},
            "performance_metrics": {},
            "system_capabilities": {},
            "recommendations": [],
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        try:
            # Test semantic analyzer
            test_feedback = "Test feedback for health check"
            semantic_result = self.semantic_analyzer.analyze_semantic_feedback(test_feedback)
            health_results["component_status"]["semantic_analyzer"] = {
                "available": True,
                "model_loaded": True,
                "test_response_time_ms": semantic_result.processing_time_ms,
                "healthy": semantic_result.processing_time_ms < 500
            }
            
            # Test technical analyzer
            technical_result = self.technical_analyzer.analyze_technical_feedback(test_feedback)
            health_results["component_status"]["technical_analyzer"] = {
                "available": True,
                "test_response_time_ms": technical_result.processing_time_ms,
                "healthy": technical_result.processing_time_ms < 1000
            }
            
            # Test pattern manager
            pattern_health = self.pattern_manager.validate_pattern_collection_health()
            health_results["component_status"]["pattern_manager"] = pattern_health
            
            # Test multi-modal pipeline
            feedback_data = {"content": test_feedback, "context": {}, "options": {}}
            multimodal_result = self.multimodal_pipeline.analyze_feedback_comprehensive(feedback_data)
            health_results["component_status"]["multimodal_pipeline"] = {
                "available": True,
                "test_response_time_ms": multimodal_result.processing_time_ms,
                "healthy": multimodal_result.processing_time_ms < 2000
            }
            
            # Test database connectivity
            db_count = self.db.collection.count()
            health_results["component_status"]["vector_database"] = {
                "available": True,
                "entries_count": db_count,
                "healthy": True
            }
            
            # Performance metrics
            if self.pattern_manager:
                perf_stats = self.pattern_manager.get_performance_stats()
                health_results["performance_metrics"] = perf_stats
            
            # System capabilities
            health_results["system_capabilities"] = {
                "semantic_analysis": True,
                "technical_context_analysis": True,
                "pattern_matching": True,
                "multimodal_pipeline": True,
                "a_b_testing": True,
                "chromadb_integration": True,
                "batch_processing": True
            }
            
            # Determine overall health
            component_healths = [
                comp.get("healthy", comp.get("overall_health") == "healthy")
                for comp in health_results["component_status"].values()
            ]
            
            if not all(component_healths):
                health_results["overall_health"] = "degraded" 
                health_results["recommendations"].append("Some components are not performing optimally")
            
            logger.info(f"✅ Health check complete - Status: {health_results['overall_health']}")
            return health_results
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            health_results["overall_health"] = "unhealthy"
            health_results["error"] = str(e)
            return health_results
    
    def run_performance_benchmark(self, num_samples: int = 100) -> Dict[str, Any]:
        """
        Run performance benchmark against PRP-2 requirements.
        
        Args:
            num_samples: Number of samples to benchmark
            
        Returns:
            Performance benchmark results
        """
        logger.info(f"🏃 Running performance benchmark ({num_samples} samples)")
        
        # Test data covering different feedback types
        test_samples = [
            "That worked perfectly!",
            "Still getting errors",
            "Almost there, minor issues",
            "Let me try something else",
            "Build passes but tests fail"
        ] * (num_samples // 5 + 1)
        
        test_samples = test_samples[:num_samples]
        
        benchmark_results = {
            "configuration": {
                "num_samples": num_samples,
                "analysis_type": "comprehensive"
            },
            "performance_metrics": {},
            "analysis_breakdown": {},
            "compliance_status": {},
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        try:
            # Run benchmark
            start_time = time.time()
            processing_times = []
            analysis_counts = {"semantic": 0, "technical": 0, "pattern": 0, "multimodal": 0}
            
            for i, sample in enumerate(test_samples):
                sample_start = time.time()
                
                result = self.analyze_single_feedback(sample, analysis_type="comprehensive")
                
                sample_time = (time.time() - sample_start) * 1000
                processing_times.append(sample_time)
                
                # Count successful analyses
                if not result.get("error"):
                    analysis_results = result.get("analysis_results", {})
                    for analysis_type in analysis_counts:
                        if analysis_type in analysis_results:
                            analysis_counts[analysis_type] += 1
                
                if (i + 1) % 20 == 0:
                    logger.info(f"📊 Processed {i + 1}/{num_samples} samples...")
            
            total_time = time.time() - start_time
            
            # Calculate metrics
            benchmark_results["performance_metrics"] = {
                "total_samples": num_samples,
                "total_time_seconds": total_time,
                "average_time_per_sample_ms": sum(processing_times) / len(processing_times),
                "min_time_ms": min(processing_times),
                "max_time_ms": max(processing_times),
                "samples_per_second": num_samples / total_time
            }
            
            benchmark_results["analysis_breakdown"] = analysis_counts
            
            # Check compliance with PRP-2 requirements
            avg_time = benchmark_results["performance_metrics"]["average_time_per_sample_ms"]
            max_time = benchmark_results["performance_metrics"]["max_time_ms"]
            
            benchmark_results["compliance_status"] = {
                "average_time_compliant": avg_time < 2000,  # 2 second average target
                "max_time_compliant": max_time < 5000,      # 5 second max target
                "throughput_compliant": benchmark_results["performance_metrics"]["samples_per_second"] > 0.5,
                "overall_compliant": avg_time < 2000 and max_time < 5000
            }
            
            logger.info("📊 Benchmark Results:")
            logger.info(f"   Average time: {avg_time:.1f}ms")
            logger.info(f"   Max time: {max_time:.1f}ms") 
            logger.info(f"   Throughput: {benchmark_results['performance_metrics']['samples_per_second']:.2f} samples/sec")
            logger.info(f"   PRP-2 compliant: {benchmark_results['compliance_status']['overall_compliant']}")
            
            return benchmark_results
            
        except Exception as e:
            logger.error(f"❌ Benchmark failed: {e}")
            benchmark_results["error"] = str(e)
            return benchmark_results
    
    def _update_performance_stats(self, processing_time_ms: float):
        """Update internal performance statistics"""
        self.performance_stats['total_analyses'] += 1
        self.performance_stats['total_time_ms'] += processing_time_ms
        self.performance_stats['average_time_ms'] = (
            self.performance_stats['total_time_ms'] / self.performance_stats['total_analyses']
        )
        self.performance_stats['fastest_time_ms'] = min(
            self.performance_stats['fastest_time_ms'], processing_time_ms
        )
        self.performance_stats['slowest_time_ms'] = max(
            self.performance_stats['slowest_time_ms'], processing_time_ms
        )


def main():
    """Main entry point for semantic enhancement runner"""
    
    parser = argparse.ArgumentParser(
        description="PRP-2 Semantic Validation Enhancement System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --analyze "That worked perfectly!"
  %(prog)s --batch-process --input-file conversations.jsonl --max-entries 1000
  %(prog)s --ab-test --sample-size 200
  %(prog)s --health-check
  %(prog)s --benchmark --num-samples 50
        """
    )
    
    # Analysis options
    parser.add_argument('--analyze', type=str, help='Analyze single feedback text')
    parser.add_argument('--context', type=str, help='JSON context for analysis (optional)')
    parser.add_argument('--analysis-type', 
                       choices=['semantic', 'technical', 'pattern', 'comprehensive'],
                       default='comprehensive',
                       help='Type of analysis to perform')
    
    # Batch processing
    parser.add_argument('--batch-process', action='store_true', help='Run batch processing')
    parser.add_argument('--input-file', type=str, help='Input JSONL file for batch processing')
    parser.add_argument('--output-file', type=str, help='Output file for enhanced results')
    parser.add_argument('--max-entries', type=int, help='Maximum entries to process')
    
    # A/B testing
    parser.add_argument('--ab-test', action='store_true', help='Run A/B test validation')
    parser.add_argument('--sample-size', type=int, default=100, help='A/B test sample size')
    parser.add_argument('--test-queries', type=str, help='JSON file with custom test queries')
    
    # Health and performance
    parser.add_argument('--health-check', action='store_true', help='Run system health check')
    parser.add_argument('--benchmark', action='store_true', help='Run performance benchmark')
    parser.add_argument('--num-samples', type=int, default=100, help='Benchmark sample count')
    
    # System options
    parser.add_argument('--cache-dir', type=str, default='./semantic_cache', 
                       help='Cache directory for embeddings')
    parser.add_argument('--output-format', choices=['json', 'pretty'], default='pretty',
                       help='Output format')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Configure logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize runner
    try:
        runner = SemanticEnhancementRunner(cache_dir=args.cache_dir)
    except Exception as e:
        logger.error(f"❌ Failed to initialize semantic enhancement runner: {e}")
        sys.exit(1)
    
    # Execute requested operation
    try:
        result = None
        
        if args.analyze:
            # Single feedback analysis
            context = json.loads(args.context) if args.context else None
            result = runner.analyze_single_feedback(args.analyze, context, args.analysis_type)
            
        elif args.batch_process:
            # Batch processing
            if not args.input_file:
                logger.error("❌ --input-file required for batch processing")
                sys.exit(1)
            result = runner.batch_process_conversations(args.input_file, args.output_file, args.max_entries)
            
        elif args.ab_test:
            # A/B test validation
            test_queries = None
            if args.test_queries:
                with open(args.test_queries, 'r') as f:
                    test_queries = json.load(f)
            result = asyncio.run(runner.run_ab_test_validation(args.sample_size, test_queries))
            
        elif args.health_check:
            # Health check
            result = runner.run_health_check()
            
        elif args.benchmark:
            # Performance benchmark
            result = runner.run_performance_benchmark(args.num_samples)
            
        else:
            # No operation specified
            parser.print_help()
            sys.exit(1)
        
        # Output results
        if result:
            if args.output_format == 'json':
                print(json.dumps(result, indent=2))
            else:
                # Pretty format
                print("\n" + "=" * 80)
                print("🎯 SEMANTIC ENHANCEMENT RESULTS")
                print("=" * 80)
                
                if "input" in result:
                    print(f"📝 Input: {result['input']['feedback_content']}")
                    print(f"🔍 Analysis Type: {result['input']['analysis_type']}")
                
                if "analysis_results" in result and result["analysis_results"]:
                    print(f"\n📊 Analysis Results:")
                    for analysis_type, results in result["analysis_results"].items():
                        print(f"   {analysis_type.title()}:")
                        if analysis_type == "semantic":
                            print(f"     Sentiment: {results.get('sentiment', 'N/A')}")
                            print(f"     Confidence: {results.get('confidence', 0):.2f}")
                        elif analysis_type == "technical":
                            print(f"     Domain: {results.get('primary_domain', 'N/A')}")
                            print(f"     Confidence: {results.get('domain_confidence', 0):.2f}")
                        elif analysis_type == "pattern":
                            print(f"     Pattern Type: {results.get('dominant_pattern_type', 'N/A')}")
                            print(f"     Max Similarity: {results.get('max_similarity', 0):.2f}")
                        elif analysis_type == "multimodal":
                            print(f"     Final Sentiment: {results.get('final_sentiment', 'N/A')}")
                            print(f"     Confidence: {results.get('confidence', 0):.2f}")
                
                if "performance_metrics" in result:
                    print(f"\n⚡ Performance:")
                    if "total_processing_time_ms" in result["performance_metrics"]:
                        print(f"   Processing Time: {result['performance_metrics']['total_processing_time_ms']:.1f}ms")
                        target_met = result["performance_metrics"].get("performance_target_met", False)
                        print(f"   Target Met: {'✅' if target_met else '❌'}")
                
                if "error" in result:
                    print(f"\n❌ Error: {result['error']}")
                
                print("\n" + "=" * 80)
        
        logger.info("✅ Operation completed successfully")
        
    except KeyboardInterrupt:
        logger.info("⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()