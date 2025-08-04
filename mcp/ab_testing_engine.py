#!/usr/bin/env python3
"""
A/B Testing Engine for MCP Integration Enhancement System

Comprehensive A/B testing framework for enhancement validation with statistical analysis
and AI-enhanced testing patterns following July 2025 standards.

Provides systematic validation of enhancement configurations with automated
performance comparison and predictive analytics.

Author: Claude Code MCP Integration Enhancement System
Version: 1.0.0 - July 2025 A/B Testing Standards
"""

import asyncio
import logging
import time
import json
import random
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from statistics import mean, stdev
from scipy import stats
import numpy as np

# Import existing vector database components
from database.vector_database import ClaudeVectorDatabase
from processing.unified_enhancement_manager import UnifiedEnhancementManager, SearchStrategy

logger = logging.getLogger(__name__)

@dataclass
class ABTestConfiguration:
    """Configuration for A/B testing scenarios."""
    test_id: str
    test_name: str
    description: str
    baseline_config: Dict[str, Any]
    enhanced_config: Dict[str, Any]
    test_queries: List[str]
    metrics_to_track: List[str]
    sample_size: int
    test_duration_hours: int
    confidence_level: float = 0.95
    minimum_effect_size: float = 0.1
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()

@dataclass
class ABTestResult:
    """Results from A/B testing execution."""
    test_id: str
    baseline_results: List[Dict[str, Any]]
    enhanced_results: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    statistical_analysis: Dict[str, Any]
    performance_comparison: Dict[str, Any]
    ai_recommendations: List[str]
    execution_time_ms: float
    completed_at: str = None
    
    def __post_init__(self):
        if self.completed_at is None:
            self.completed_at = datetime.now().isoformat()

class ABTestingEngine:
    """
    Comprehensive A/B testing framework for enhancement validation.
    Following July 2025 AI-enhanced testing patterns with statistical rigor.
    """
    
    def __init__(self):
        """Initialize A/B testing engine with required components."""
        self.vector_db = None  # Lazy initialization
        self.enhancement_manager = None  # Lazy initialization
        
        # Test execution tracking
        self.active_tests = {}
        self.completed_tests = {}
        
        # Statistical configuration
        self.default_confidence_level = 0.95
        self.default_minimum_effect_size = 0.1
        
        # Performance benchmarking
        self.performance_baselines = {
            "search_latency_ms": 200,  # Target latency
            "result_relevance": 0.8,   # Minimum relevance score
            "user_satisfaction": 0.9,  # Target satisfaction
            "enhancement_boost": 1.2   # Minimum enhancement multiplier
        }
        
        logger.info("🧪 A/B Testing Engine initialized")
    
    async def _ensure_components_initialized(self):
        """Lazy initialization of required components."""
        if not self.vector_db:
            self.vector_db = ClaudeVectorDatabase()
        if not self.enhancement_manager:
            self.enhancement_manager = UnifiedEnhancementManager()
    
    async def create_test_configuration(
        self,
        test_name: str,
        description: str,
        baseline_system: str = "current",
        enhanced_system: str = "unified",
        test_queries: List[str] = None,
        sample_size: int = 100,
        test_duration_hours: int = 24
    ) -> ABTestConfiguration:
        """
        Create a comprehensive A/B test configuration.
        
        Args:
            test_name: Human-readable test name
            description: Test description and objectives
            baseline_system: Baseline system configuration
            enhanced_system: Enhanced system configuration
            test_queries: Queries to test (auto-generated if None)
            sample_size: Number of test iterations per configuration
            test_duration_hours: Maximum test duration
            
        Returns:
            Complete A/B test configuration
        """
        await self._ensure_components_initialized()
        
        # Generate unique test ID
        test_id = f"ab_test_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"
        
        # Get system configurations
        baseline_config = await self._get_system_config(baseline_system)
        enhanced_config = await self._get_system_config(enhanced_system)
        
        # Generate test queries if not provided
        if test_queries is None:
            test_queries = await self._generate_test_queries()
        
        # Define metrics to track
        metrics_to_track = [
            "search_relevance",
            "user_satisfaction", 
            "processing_latency",
            "result_diversity",
            "enhancement_contribution",
            "system_reliability"
        ]
        
        config = ABTestConfiguration(
            test_id=test_id,
            test_name=test_name,
            description=description,
            baseline_config=baseline_config,
            enhanced_config=enhanced_config,
            test_queries=test_queries,
            metrics_to_track=metrics_to_track,
            sample_size=sample_size,
            test_duration_hours=test_duration_hours
        )
        
        logger.info(f"🧪 Created A/B test configuration: {test_name} ({test_id})")
        return config
    
    async def run_enhancement_ab_test(
        self,
        test_name: str,
        test_queries: List[str] = None,
        baseline_system: str = "current",
        enhanced_system: str = "unified",
        test_duration_hours: int = 24,
        sample_size: int = 100
    ) -> Dict[str, Any]:
        """
        Run comprehensive A/B test comparing enhancement configurations.
        
        This is the main entry point for A/B testing as specified in the PRP.
        
        Args:
            test_name: Human-readable test name
            test_queries: List of queries to test
            baseline_system: Baseline system identifier
            enhanced_system: Enhanced system identifier
            test_duration_hours: Maximum test duration
            sample_size: Number of test iterations
            
        Returns:
            Complete A/B test results with statistical analysis
        """
        start_time = time.time()
        
        try:
            # Create test configuration
            config = await self.create_test_configuration(
                test_name=test_name,
                description=f"A/B test comparing {baseline_system} vs {enhanced_system}",
                baseline_system=baseline_system,
                enhanced_system=enhanced_system,
                test_queries=test_queries,
                sample_size=sample_size,
                test_duration_hours=test_duration_hours
            )
            
            # Execute parallel testing
            logger.info(f"🧪 Starting A/B test execution: {test_name}")
            test_results = await self._execute_parallel_tests(config)
            
            # Statistical analysis using July 2025 AI-enhanced methods
            statistical_analysis = await self._calculate_statistical_significance(test_results)
            
            # Performance comparison analysis
            performance_comparison = await self._compare_performance_metrics(test_results)
            
            # AI-enhanced recommendations
            ai_recommendations = await self._generate_ai_recommendations(test_results, statistical_analysis)
            
            # Calculate execution time
            execution_time = (time.time() - start_time) * 1000
            
            # Create comprehensive result object
            result = ABTestResult(
                test_id=config.test_id,
                baseline_results=test_results['baseline'],
                enhanced_results=test_results['enhanced'],
                metrics=test_results['metrics'],
                statistical_analysis=statistical_analysis,
                performance_comparison=performance_comparison,
                ai_recommendations=ai_recommendations,
                execution_time_ms=execution_time
            )
            
            # Store completed test
            self.completed_tests[config.test_id] = result
            
            logger.info(f"✅ A/B test completed: {test_name} in {execution_time:.1f}ms")
            
            return {
                "test_configuration": asdict(config),
                "test_results": asdict(result),
                "summary": {
                    "test_id": config.test_id,
                    "baseline_performance": performance_comparison.get('baseline_summary', {}),
                    "enhanced_performance": performance_comparison.get('enhanced_summary', {}),
                    "statistical_significance": statistical_analysis.get('is_significant', False),
                    "confidence_level": statistical_analysis.get('confidence_level', 0.95),
                    "recommendation": ai_recommendations[0] if ai_recommendations else "No recommendations generated"
                }
            }
            
        except Exception as e:
            logger.error(f"❌ A/B test execution failed: {e}")
            return {
                "error": str(e),
                "test_name": test_name,
                "execution_time_ms": (time.time() - start_time) * 1000,
                "status": "failed"
            }
    
    async def _get_system_config(self, system_identifier: str) -> Dict[str, Any]:
        """Get system configuration for A/B testing."""
        await self._ensure_components_initialized()
        
        if system_identifier == "current" or system_identifier == "baseline":
            return {
                "type": "baseline",
                "use_conversation_chains": False,
                "use_semantic_enhancement": False,
                "use_adaptive_learning": False,
                "enhancement_preference": "conservative",
                "description": "Current system without unified enhancements"
            }
        elif system_identifier == "unified" or system_identifier == "enhanced":
            return {
                "type": "enhanced",
                "use_conversation_chains": True,
                "use_semantic_enhancement": True,
                "use_adaptive_learning": True,
                "enhancement_preference": "auto",
                "description": "Unified enhancement system with all features"
            }
        elif system_identifier == "partial":
            return {
                "type": "partial",
                "use_conversation_chains": True,
                "use_semantic_enhancement": False,
                "use_adaptive_learning": False,
                "enhancement_preference": "conservative",
                "description": "Partial enhancement with conversation chains only"
            }
        else:
            # Default to baseline
            return await self._get_system_config("baseline")
    
    async def _generate_test_queries(self) -> List[str]:
        """Generate representative test queries for A/B testing."""
        # Mix of different query types for comprehensive testing
        test_queries = [
            # Technical queries
            "How do I fix authentication errors in React?",
            "Database connection issues with PostgreSQL",
            "TypeScript compilation errors",
            "Performance optimization for large datasets",
            
            # Project-specific queries
            "Next.js routing configuration",
            "Supabase integration patterns",
            "Playwright test automation",
            "Docker deployment setup",
            
            # Troubleshooting queries
            "Debug build failures",
            "Memory leak investigation",
            "API response timeout issues",
            "CSS styling conflicts",
            
            # General development queries
            "Best practices for error handling",
            "Code review recommendations",
            "Testing strategy implementation",
            "CI/CD pipeline optimization"
        ]
        
        # Randomly sample queries for variety
        selected_queries = random.sample(test_queries, min(10, len(test_queries)))
        logger.info(f"🧪 Generated {len(selected_queries)} test queries")
        return selected_queries
    
    async def _execute_parallel_tests(self, config: ABTestConfiguration) -> Dict[str, Any]:
        """Execute parallel A/B testing with both configurations."""
        baseline_results = []
        enhanced_results = []
        
        logger.info(f"🧪 Executing {config.sample_size} tests per configuration")
        
        # Execute tests for each query
        for query in config.test_queries:
            # Test baseline configuration
            baseline_result = await self._execute_single_test(
                query, config.baseline_config, "baseline"
            )
            baseline_results.append(baseline_result)
            
            # Test enhanced configuration
            enhanced_result = await self._execute_single_test(
                query, config.enhanced_config, "enhanced"
            )
            enhanced_results.append(enhanced_result)
            
            # Small delay to prevent overwhelming the system
            await asyncio.sleep(0.1)
        
        # Calculate aggregate metrics
        metrics = {
            "total_tests": len(config.test_queries) * 2,
            "baseline_tests": len(baseline_results),
            "enhanced_tests": len(enhanced_results),
            "queries_tested": len(config.test_queries)
        }
        
        return {
            "baseline": baseline_results,
            "enhanced": enhanced_results,
            "metrics": metrics
        }
    
    async def _execute_single_test(
        self, 
        query: str, 
        config: Dict[str, Any], 
        config_type: str
    ) -> Dict[str, Any]:
        """Execute a single test iteration."""
        start_time = time.time()
        
        try:
            if config["type"] == "baseline":
                # Use standard search for baseline
                results = self.vector_db.search_conversations_enhanced(
                    query=query,
                    n_results=5,
                    include_metadata=True
                )
            else:
                # Use unified search for enhanced testing
                from mcp.mcp_server import search_conversations_unified
                results = await search_conversations_unified(
                    query=query,
                    limit=5,
                    use_conversation_chains=config.get("use_conversation_chains", True),
                    use_semantic_enhancement=config.get("use_semantic_enhancement", True),
                    use_adaptive_learning=config.get("use_adaptive_learning", True),
                    enhancement_preference=config.get("enhancement_preference", "auto")
                )
            
            execution_time = (time.time() - start_time) * 1000
            
            # Calculate metrics
            metrics = await self._calculate_test_metrics(query, results, execution_time)
            
            return {
                "query": query,
                "config_type": config_type,
                "results_count": len(results),
                "execution_time_ms": execution_time,
                "metrics": metrics,
                "success": True
            }
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            logger.warning(f"Test iteration failed: {e}")
            
            return {
                "query": query,
                "config_type": config_type,
                "results_count": 0,
                "execution_time_ms": execution_time,
                "metrics": {"error": str(e)},
                "success": False
            }
    
    async def _calculate_test_metrics(
        self, 
        query: str, 
        results: List[Dict], 
        execution_time: float
    ) -> Dict[str, Any]:
        """Calculate comprehensive metrics for test results."""
        if not results:
            return {
                "search_relevance": 0.0,
                "user_satisfaction": 0.0,
                "processing_latency": execution_time,
                "result_diversity": 0.0,
                "enhancement_contribution": 0.0,
                "system_reliability": 0.0
            }
        
        # Search relevance (based on result scores and content quality)
        search_relevance = await self._calculate_search_relevance(query, results)
        
        # User satisfaction (simulated based on result quality indicators)
        user_satisfaction = await self._estimate_user_satisfaction(results)
        
        # Processing latency (measured execution time)
        processing_latency = execution_time
        
        # Result diversity (variety in result sources and types)
        result_diversity = await self._calculate_result_diversity(results)
        
        # Enhancement contribution (boost from enhancement systems)
        enhancement_contribution = await self._calculate_enhancement_contribution(results)
        
        # System reliability (successful execution and result quality)
        system_reliability = 1.0 if all(r.get('content') for r in results) else 0.8
        
        return {
            "search_relevance": search_relevance,
            "user_satisfaction": user_satisfaction,
            "processing_latency": processing_latency,
            "result_diversity": result_diversity,
            "enhancement_contribution": enhancement_contribution,
            "system_reliability": system_reliability
        }
    
    async def _calculate_search_relevance(self, query: str, results: List[Dict]) -> float:
        """Calculate search relevance score."""
        if not results:
            return 0.0
        
        # Simple relevance calculation based on content matching
        relevance_scores = []
        query_terms = query.lower().split()
        
        for result in results:
            content = result.get('content', '').lower()
            matches = sum(1 for term in query_terms if term in content)
            relevance = matches / len(query_terms) if query_terms else 0.0
            relevance_scores.append(relevance)
        
        return mean(relevance_scores) if relevance_scores else 0.0
    
    async def _estimate_user_satisfaction(self, results: List[Dict]) -> float:
        """Estimate user satisfaction based on result quality indicators."""
        if not results:
            return 0.0
        
        satisfaction_factors = []
        
        for result in results:
            factors = 0.5  # Base satisfaction
            
            # Higher satisfaction for results with code
            if result.get('has_code', False):
                factors += 0.2
            
            # Higher satisfaction for enhanced results
            if result.get('enhancement_metadata', {}).get('progressive_enhancement_applied'):
                factors += 0.2
            
            # Higher satisfaction for validated solutions
            if result.get('is_validated_solution', False):
                factors += 0.1
            
            satisfaction_factors.append(min(1.0, factors))
        
        return mean(satisfaction_factors) if satisfaction_factors else 0.5
    
    async def _calculate_result_diversity(self, results: List[Dict]) -> float:
        """Calculate diversity in search results."""
        if not results:
            return 0.0
        
        # Check diversity in project sources
        projects = set()
        types = set()
        
        for result in results:
            projects.add(result.get('project_name', 'unknown'))
            types.add(result.get('type', 'unknown'))
        
        # Normalize diversity scores
        project_diversity = min(1.0, len(projects) / len(results))
        type_diversity = min(1.0, len(types) / 2)  # Assuming max 2 types (user/assistant)
        
        return (project_diversity + type_diversity) / 2
    
    async def _calculate_enhancement_contribution(self, results: List[Dict]) -> float:
        """Calculate contribution from enhancement systems."""
        if not results:
            return 0.0
        
        enhancement_scores = []
        
        for result in results:
            enhancement_metadata = result.get('enhancement_metadata', {})
            
            if enhancement_metadata.get('progressive_enhancement_applied'):
                systems_used = len(enhancement_metadata.get('systems_used', []))
                # Score based on number of enhancement systems used
                score = min(1.0, systems_used / 4)  # Max 4 systems
                enhancement_scores.append(score)
            else:
                enhancement_scores.append(0.0)
        
        return mean(enhancement_scores) if enhancement_scores else 0.0
    
    async def _calculate_statistical_significance(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate statistical significance using AI-enhanced methods."""
        try:
            baseline_results = test_results['baseline']
            enhanced_results = test_results['enhanced']
            
            if not baseline_results or not enhanced_results:
                return {
                    "error": "Insufficient data for statistical analysis",
                    "is_significant": False
                }
            
            # Extract metric values for comparison
            baseline_metrics = self._extract_metric_values(baseline_results)
            enhanced_metrics = self._extract_metric_values(enhanced_results)
            
            statistical_tests = {}
            
            # Perform statistical tests for each metric
            for metric_name in baseline_metrics.keys():
                baseline_values = baseline_metrics[metric_name]
                enhanced_values = enhanced_metrics.get(metric_name, [])
                
                if len(baseline_values) > 1 and len(enhanced_values) > 1:
                    # Perform t-test
                    try:
                        t_statistic, p_value = stats.ttest_ind(enhanced_values, baseline_values)
                        
                        statistical_tests[metric_name] = {
                            "t_statistic": float(t_statistic),
                            "p_value": float(p_value),
                            "is_significant": p_value < 0.05,
                            "baseline_mean": float(mean(baseline_values)),
                            "enhanced_mean": float(mean(enhanced_values)),
                            "improvement": float(mean(enhanced_values) - mean(baseline_values)),
                            "improvement_percentage": float((mean(enhanced_values) - mean(baseline_values)) / mean(baseline_values) * 100) if mean(baseline_values) > 0 else 0.0
                        }
                    except Exception as e:
                        statistical_tests[metric_name] = {
                            "error": str(e),
                            "is_significant": False
                        }
            
            # Overall significance assessment
            significant_metrics = [m for m in statistical_tests.values() if m.get('is_significant', False)]
            overall_significance = len(significant_metrics) > 0
            
            return {
                "statistical_tests": statistical_tests,
                "is_significant": overall_significance,
                "significant_metrics_count": len(significant_metrics),
                "total_metrics_tested": len(statistical_tests),
                "confidence_level": 0.95,
                "methodology": "Two-sample t-test with 95% confidence interval"
            }
            
        except Exception as e:
            logger.error(f"Statistical analysis failed: {e}")
            return {
                "error": str(e),
                "is_significant": False,
                "methodology": "Statistical analysis failed"
            }
    
    def _extract_metric_values(self, results: List[Dict[str, Any]]) -> Dict[str, List[float]]:
        """Extract metric values for statistical analysis."""
        metrics = {}
        
        for result in results:
            if not result.get('success', True):
                continue
                
            result_metrics = result.get('metrics', {})
            
            for metric_name, value in result_metrics.items():
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if metric_name not in metrics:
                        metrics[metric_name] = []
                    metrics[metric_name].append(float(value))
        
        return metrics
    
    async def _compare_performance_metrics(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance metrics between baseline and enhanced systems."""
        try:
            baseline_results = test_results['baseline']
            enhanced_results = test_results['enhanced']
            
            # Calculate summary statistics
            baseline_summary = self._calculate_summary_statistics(baseline_results)
            enhanced_summary = self._calculate_summary_statistics(enhanced_results)
            
            # Performance comparison
            comparison = {}
            
            for metric_name in baseline_summary.keys():
                if metric_name in enhanced_summary:
                    baseline_avg = baseline_summary[metric_name]['mean']
                    enhanced_avg = enhanced_summary[metric_name]['mean']
                    
                    comparison[metric_name] = {
                        "baseline_average": baseline_avg,
                        "enhanced_average": enhanced_avg,
                        "absolute_improvement": enhanced_avg - baseline_avg,
                        "percentage_improvement": ((enhanced_avg - baseline_avg) / baseline_avg * 100) if baseline_avg > 0 else 0.0,
                        "performance_ratio": enhanced_avg / baseline_avg if baseline_avg > 0 else 1.0
                    }
            
            return {
                "baseline_summary": baseline_summary,
                "enhanced_summary": enhanced_summary,
                "performance_comparison": comparison,
                "overall_improvement": self._calculate_overall_improvement(comparison)
            }
            
        except Exception as e:
            logger.error(f"Performance comparison failed: {e}")
            return {
                "error": str(e),
                "baseline_summary": {},
                "enhanced_summary": {},
                "performance_comparison": {}
            }
    
    def _calculate_summary_statistics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate summary statistics for a set of results."""
        metrics_data = self._extract_metric_values(results)
        summary = {}
        
        for metric_name, values in metrics_data.items():
            if len(values) > 0:
                summary[metric_name] = {
                    "mean": float(mean(values)),
                    "median": float(np.median(values)),
                    "std_dev": float(stdev(values)) if len(values) > 1 else 0.0,
                    "min": float(min(values)),
                    "max": float(max(values)),
                    "count": len(values)
                }
        
        return summary
    
    def _calculate_overall_improvement(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall improvement score."""
        if not comparison:
            return {"score": 0.0, "assessment": "No data available"}
        
        improvements = []
        
        for metric_name, metrics in comparison.items():
            # Weight different metrics differently
            weight = 1.0
            if metric_name == "processing_latency":
                # Lower is better for latency
                improvement = -metrics["percentage_improvement"] * weight
            else:
                # Higher is better for most other metrics
                improvement = metrics["percentage_improvement"] * weight
            
            improvements.append(improvement)
        
        if improvements:
            overall_score = mean(improvements)
            
            if overall_score > 10:
                assessment = "Significant improvement"
            elif overall_score > 5:
                assessment = "Moderate improvement"
            elif overall_score > 0:
                assessment = "Minor improvement"
            else:
                assessment = "No improvement or degradation"
            
            return {
                "score": overall_score,
                "assessment": assessment,
                "individual_improvements": improvements
            }
        
        return {"score": 0.0, "assessment": "Unable to calculate"}
    
    async def _generate_ai_recommendations(
        self, 
        test_results: Dict[str, Any], 
        statistical_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate AI-enhanced recommendations based on test results."""
        recommendations = []
        
        try:
            # Analyze statistical significance
            if statistical_analysis.get('is_significant', False):
                significant_count = statistical_analysis.get('significant_metrics_count', 0)
                total_count = statistical_analysis.get('total_metrics_tested', 0)
                
                if significant_count >= total_count * 0.5:
                    recommendations.append(
                        f"Strong recommendation: Deploy enhanced system. "
                        f"{significant_count}/{total_count} metrics show significant improvement."
                    )
                else:
                    recommendations.append(
                        f"Moderate recommendation: Consider enhanced system with monitoring. "
                        f"{significant_count}/{total_count} metrics show improvement."
                    )
            else:
                recommendations.append(
                    "Caution: No statistically significant improvements detected. "
                    "Consider optimizing enhancement parameters before deployment."
                )
            
            # Analyze specific metrics
            stats_tests = statistical_analysis.get('statistical_tests', {})
            
            # Latency recommendations
            if 'processing_latency' in stats_tests:
                latency_test = stats_tests['processing_latency']
                if latency_test.get('enhanced_mean', 0) > self.performance_baselines['search_latency_ms']:
                    recommendations.append(
                        f"Performance concern: Average latency {latency_test.get('enhanced_mean', 0):.1f}ms "
                        f"exceeds target {self.performance_baselines['search_latency_ms']}ms. "
                        "Consider caching optimizations."
                    )
            
            # Relevance recommendations
            if 'search_relevance' in stats_tests:
                relevance_test = stats_tests['search_relevance']
                if relevance_test.get('improvement_percentage', 0) > 10:
                    recommendations.append(
                        f"Excellent: Search relevance improved by "
                        f"{relevance_test.get('improvement_percentage', 0):.1f}%. "
                        "Enhancement system is providing significant value."
                    )
            
            # Enhancement contribution recommendations
            if 'enhancement_contribution' in stats_tests:
                enhancement_test = stats_tests['enhancement_contribution']
                if enhancement_test.get('enhanced_mean', 0) < 0.5:
                    recommendations.append(
                        "Optimization opportunity: Enhancement contribution is lower than expected. "
                        "Review enhancement system configuration and thresholds."
                    )
            
            # Default recommendation if no specific ones generated
            if not recommendations:
                recommendations.append(
                    "Recommendation: Continue monitoring system performance. "
                    "Consider extended testing with larger sample sizes."
                )
            
        except Exception as e:
            logger.error(f"AI recommendation generation failed: {e}")
            recommendations.append(
                f"Unable to generate detailed recommendations due to analysis error: {str(e)}"
            )
        
        return recommendations
    
    async def get_test_history(self) -> Dict[str, Any]:
        """Get history of completed A/B tests."""
        return {
            "completed_tests_count": len(self.completed_tests),
            "active_tests_count": len(self.active_tests),
            "completed_tests": {
                test_id: {
                    "test_id": result.test_id,
                    "completed_at": result.completed_at,
                    "execution_time_ms": result.execution_time_ms,
                    "baseline_results_count": len(result.baseline_results),
                    "enhanced_results_count": len(result.enhanced_results),
                    "statistical_significance": result.statistical_analysis.get('is_significant', False)
                }
                for test_id, result in self.completed_tests.items()
            }
        }
    
    async def get_testing_insights(self) -> Dict[str, Any]:
        """Get insights about A/B testing performance and patterns."""
        if not self.completed_tests:
            return {
                "message": "No completed tests available for analysis",
                "insights": []
            }
        
        insights = []
        
        # Calculate success rate
        successful_tests = sum(1 for test in self.completed_tests.values() 
                             if test.statistical_analysis.get('is_significant', False))
        total_tests = len(self.completed_tests)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0
        
        insights.append(f"A/B testing success rate: {success_rate:.1f}% ({successful_tests}/{total_tests} tests showed significant improvements)")
        
        # Calculate average execution time
        execution_times = [test.execution_time_ms for test in self.completed_tests.values()]
        if execution_times:
            avg_execution_time = mean(execution_times)
            insights.append(f"Average test execution time: {avg_execution_time:.1f}ms")
        
        # Most common improvements
        all_recommendations = []
        for test in self.completed_tests.values():
            all_recommendations.extend(test.ai_recommendations)
        
        if all_recommendations:
            insights.append(f"Total recommendations generated: {len(all_recommendations)}")
        
        return {
            "total_tests_completed": total_tests,
            "successful_improvements": successful_tests,
            "success_rate_percentage": success_rate,
            "insights": insights,
            "testing_engine_status": "operational"
        }