#!/usr/bin/env python3
"""
Unified Enhancement Engine for Claude Code Vector Database

This module implements the main orchestrator for the enhanced vector database system,
combining conversation chain back-fill, field population optimization, and health monitoring
to address critical conversation chain field population failures (0.97% vs 80%+ expected).

Key Features:
- Conversation Chain Back-Fill Engine (addresses main system issue)
- Field Population Optimizer (systematically improves all 30+ metadata fields)
- Enhanced Metadata Monitor (real-time health tracking with alerting)
- Performance-optimized processing (<30 seconds per session)
- Integration with existing MCP tools and sync systems

Author: Enhanced Vector Database System (July 2025)
Version: 1.0.0
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from dataclasses import dataclass, field

# Import existing components
from database.vector_database import ClaudeVectorDatabase
from processing.enhanced_processor import UnifiedEnhancementProcessor
from database.conversation_extractor import ConversationExtractor

# Import enhanced context functions
from database.enhanced_context import (
    get_realtime_learning_insights
)

logger = logging.getLogger(__name__)


@dataclass
class BackFillResult:
    """Results from conversation chain back-fill processing."""
    session_id: str
    relationships_built: int = 0
    database_updates: int = 0
    population_improvement: float = 0.0
    processing_time_ms: float = 0.0
    accuracy_score: float = 0.0
    error_count: int = 0
    success: bool = False


@dataclass
class OptimizationResult:
    """Results from field population optimization."""
    session_id: str
    fields_optimized: List[str] = field(default_factory=list)
    improvement_scores: Dict[str, float] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    success: bool = False


@dataclass
class ValidationResult:
    """Results from validation and health assessment."""
    session_id: str
    health_score: float = 0.0
    validation_passed: bool = False
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    success: bool = False


@dataclass
class EnhancementResult:
    """Complete unified enhancement results."""
    session_id: str
    backfill_stats: BackFillResult
    optimization_stats: OptimizationResult
    validation_stats: ValidationResult
    overall_improvement: float = 0.0
    health_score: float = 0.0
    processing_time_ms: float = 0.0
    success: bool = False


class UnifiedEnhancementEngine:
    """
    Main orchestrator combining conversation chain back-fill, field optimization, and monitoring.
    
    This engine addresses the critical conversation chain population issue (0.97% → 80%+)
    while systematically optimizing all 30+ metadata fields and providing real-time health
    monitoring with performance guarantees (<30 seconds per session).
    """
    
    def __init__(self, 
                 db_path: str = "/home/user/.claude-vector-db-enhanced/chroma_db",
                 performance_target_seconds: float = 30.0):
        """Initialize the unified enhancement engine."""
        self.performance_target = performance_target_seconds
        self.db_path = Path(db_path)
        
        # Initialize core components
        logger.info("🔧 Initializing UnifiedEnhancementEngine")
        
        # Database and processing components
        self.database = ClaudeVectorDatabase(str(self.db_path))
        self.processor = UnifiedEnhancementProcessor(suppress_init_logging=True)
        self.extractor = ConversationExtractor()
        
        # Component engines (will be initialized on demand)
        self._backfill_engine = None
        self._field_optimizer = None
        self._metadata_monitor = None
        
        # Processing statistics
        self.stats = {
            'sessions_processed': 0,
            'total_relationships_built': 0,
            'total_processing_time_ms': 0.0,
            'average_processing_time_ms': 0.0,
            'success_rate': 0.0,
            'chain_improvement_total': 0.0,
            'performance_violations': 0
        }
        
        logger.info("✅ UnifiedEnhancementEngine initialized successfully")
    
    @property
    def backfill_engine(self):
        """Lazy initialization of conversation back-fill engine."""
        if self._backfill_engine is None:
            from processing.conversation_backfill_engine import ConversationBackFillEngine
            self._backfill_engine = ConversationBackFillEngine(self.database)
        return self._backfill_engine
    
    @property
    def field_optimizer(self):
        """Lazy initialization of field population optimizer."""
        if self._field_optimizer is None:
            from processing.field_population_optimizer import FieldPopulationOptimizer
            self._field_optimizer = FieldPopulationOptimizer(self.database)
        return self._field_optimizer
    
    @property
    def metadata_monitor(self):
        """Lazy initialization of enhanced metadata monitor."""
        if self._metadata_monitor is None:
            from processing.enhanced_metadata_monitor import EnhancedMetadataMonitor
            self._metadata_monitor = EnhancedMetadataMonitor(self.database)
        return self._metadata_monitor
    
    def process_enhancement_session(self, session_id: str,
                                  enable_backfill: bool = True,
                                  enable_optimization: bool = True,
                                  enable_validation: bool = True) -> EnhancementResult:
        """
        Complete enhancement processing for a single session.
        
        This is the main method that orchestrates all enhancement components
        to address conversation chain population issues and optimize metadata fields.
        
        Args:
            session_id: Session identifier to process
            enable_backfill: Enable conversation chain back-fill (addresses 0.97% issue)
            enable_optimization: Enable field population optimization
            enable_validation: Enable validation and health assessment
            
        Returns:
            EnhancementResult with complete processing statistics and improvements
        """
        start_time = time.time()
        logger.info(f"🚀 Starting unified enhancement for session: {session_id}")
        
        try:
            # Step 1: Conversation Chain Back-Fill (Critical Priority)
            backfill_result = BackFillResult(session_id=session_id)
            if enable_backfill:
                logger.info(f"🔗 Step 1/3: Conversation chain back-fill for {session_id}")
                backfill_result = self.backfill_engine.process_session(session_id)
                
                if not backfill_result.success:
                    logger.warning(f"⚠️ Back-fill failed for {session_id}, continuing with other steps")
            
            # Step 2: Field Population Optimization
            optimization_result = OptimizationResult(session_id=session_id)
            if enable_optimization:
                logger.info(f"⚙️ Step 2/3: Field optimization for {session_id}")
                optimization_result = self.field_optimizer.optimize_session(session_id)
                
                if not optimization_result.success:
                    logger.warning(f"⚠️ Field optimization failed for {session_id}, continuing with validation")
            
            # Step 3: Validation and Health Assessment
            validation_result = ValidationResult(session_id=session_id)
            if enable_validation:
                logger.info(f"✅ Step 3/3: Validation and health assessment for {session_id}")
                validation_result = self.metadata_monitor.validate_session_enhancement(session_id)
                
                if not validation_result.success:
                    logger.warning(f"⚠️ Validation failed for {session_id}")
            
            # Calculate overall metrics
            processing_time_ms = (time.time() - start_time) * 1000
            overall_improvement = self._calculate_overall_improvement(
                backfill_result, optimization_result, validation_result
            )
            health_score = validation_result.health_score if validation_result.success else 0.0
            
            # Check performance compliance
            performance_violation = processing_time_ms > (self.performance_target * 1000)
            if performance_violation:
                self.stats['performance_violations'] += 1
                logger.warning(f"⏱️ Performance target exceeded: {processing_time_ms:.1f}ms > {self.performance_target * 1000}ms")
            
            # Create final result
            result = EnhancementResult(
                session_id=session_id,
                backfill_stats=backfill_result,
                optimization_stats=optimization_result,
                validation_stats=validation_result,
                overall_improvement=overall_improvement,
                health_score=health_score,
                processing_time_ms=processing_time_ms,
                success=(backfill_result.success or optimization_result.success or validation_result.success)
            )
            
            # Update engine statistics
            self._update_engine_stats(result)
            
            # Log completion summary
            self._log_completion_summary(result)
            
            return result
            
        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"❌ Unified enhancement failed for {session_id}: {e}")
            
            # Return error result
            return EnhancementResult(
                session_id=session_id,
                backfill_stats=BackFillResult(session_id=session_id, success=False),
                optimization_stats=OptimizationResult(session_id=session_id, success=False),
                validation_stats=ValidationResult(session_id=session_id, success=False),
                processing_time_ms=processing_time_ms,
                success=False
            )
    
    def process_multiple_sessions(self, session_ids: List[str],
                                 max_processing_time_seconds: float = 300.0,
                                 batch_size: int = 5) -> List[EnhancementResult]:
        """
        Process multiple sessions with time and batch limits.
        
        Args:
            session_ids: List of session IDs to process
            max_processing_time_seconds: Maximum total processing time
            batch_size: Number of sessions to process in each batch
            
        Returns:
            List of EnhancementResult objects
        """
        start_time = time.time()
        results = []
        
        logger.info(f"🔄 Processing {len(session_ids)} sessions (max time: {max_processing_time_seconds}s)")
        
        # Process in batches to respect time limits
        for i in range(0, len(session_ids), batch_size):
            # Check time limit
            elapsed_time = time.time() - start_time
            if elapsed_time > max_processing_time_seconds:
                logger.warning(f"⏱️ Time limit reached, processed {len(results)}/{len(session_ids)} sessions")
                break
            
            batch = session_ids[i:i + batch_size]
            batch_results = []
            
            for session_id in batch:
                # Check time limit for each session
                elapsed_time = time.time() - start_time
                remaining_time = max_processing_time_seconds - elapsed_time
                
                if remaining_time < self.performance_target:
                    logger.warning(f"⏱️ Insufficient time remaining ({remaining_time:.1f}s), stopping batch processing")
                    break
                
                try:
                    result = self.process_enhancement_session(session_id)
                    batch_results.append(result)
                    results.append(result)
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process session {session_id}: {e}")
                    # Add error result
                    error_result = EnhancementResult(
                        session_id=session_id,
                        backfill_stats=BackFillResult(session_id=session_id, success=False),
                        optimization_stats=OptimizationResult(session_id=session_id, success=False),
                        validation_stats=ValidationResult(session_id=session_id, success=False),
                        success=False
                    )
                    results.append(error_result)
            
            # Log batch completion
            successful_in_batch = sum(1 for r in batch_results if r.success)
            logger.info(f"✅ Batch {i//batch_size + 1} complete: {successful_in_batch}/{len(batch_results)} successful")
        
        total_time = time.time() - start_time
        successful_sessions = sum(1 for r in results if r.success)
        
        logger.info(f"🎯 Batch processing complete: {successful_sessions}/{len(results)} successful in {total_time:.1f}s")
        
        return results
    
    def get_recent_sessions(self, hours: int = 24, limit: int = 50) -> List[str]:
        """
        Get recent session IDs for processing.
        
        Args:
            hours: Hours back to look for sessions
            limit: Maximum number of sessions to return
            
        Returns:
            List of recent session IDs
        """
        try:
            # If hours is very large (e.g., >1000), get all sessions without timestamp filtering
            if hours > 1000:
                # Query database for all sessions - use a very large limit to get everything
                results = self.database.collection.get(
                    include=["metadatas"],
                    limit=50000  # Large enough to get all entries
                )
            else:
                # Calculate time threshold
                cutoff_time = datetime.now().timestamp() - (hours * 3600)
                
                # Query database for recent sessions
                results = self.database.collection.get(
                    where={
                        "timestamp_unix": {"$gte": cutoff_time}
                    },
                    include=["metadatas"],
                    limit=limit * 10  # Get more to deduplicate
                )
            
            # Extract unique session IDs
            session_ids = set()
            for metadata in results.get('metadatas', []):
                if metadata and metadata.get('session_id'):
                    session_ids.add(metadata['session_id'])
            
            session_list = list(session_ids)[:limit]
            logger.info(f"📋 Found {len(session_list)} recent sessions (last {hours} hours)")
            
            return session_list
            
        except Exception as e:
            logger.error(f"❌ Failed to get recent sessions: {e}")
            return []
    
    def analyze_conversation_chain_health(self) -> Dict[str, Any]:
        """
        Analyze the current health of conversation chain fields.
        
        Returns comprehensive analysis of the 0.97% population issue.
        """
        logger.info("🔍 Analyzing conversation chain field health")
        
        try:
            # Get comprehensive field analysis
            health_report = self.metadata_monitor.get_conversation_chain_analysis()
            
            # Add engine-specific metrics
            health_report['engine_stats'] = self.get_engine_statistics()
            health_report['analysis_timestamp'] = datetime.now().isoformat()
            
            return health_report
            
        except Exception as e:
            logger.error(f"❌ Failed to analyze conversation chain health: {e}")
            return {
                'error': str(e),
                'status': 'failed',
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def _calculate_overall_improvement(self, backfill: BackFillResult, 
                                     optimization: OptimizationResult,
                                     validation: ValidationResult) -> float:
        """Calculate overall improvement score from component results."""
        total_improvement = 0.0
        component_count = 0
        
        # Back-fill improvement (weighted heavily due to critical nature)
        if backfill.success and backfill.population_improvement > 0:
            total_improvement += backfill.population_improvement * 2.0  # 2x weight
            component_count += 2
        
        # Field optimization improvement
        if optimization.success and optimization.improvement_scores:
            avg_field_improvement = sum(optimization.improvement_scores.values()) / len(optimization.improvement_scores)
            total_improvement += avg_field_improvement
            component_count += 1
        
        # Health score contribution
        if validation.success and validation.health_score > 0:
            total_improvement += validation.health_score * 100  # Convert to percentage
            component_count += 1
        
        return total_improvement / component_count if component_count > 0 else 0.0
    
    def _update_engine_stats(self, result: EnhancementResult):
        """Update engine-level statistics."""
        self.stats['sessions_processed'] += 1
        
        if result.backfill_stats.success:
            self.stats['total_relationships_built'] += result.backfill_stats.relationships_built
            self.stats['chain_improvement_total'] += result.backfill_stats.population_improvement
        
        # Update processing time statistics
        self.stats['total_processing_time_ms'] += result.processing_time_ms
        self.stats['average_processing_time_ms'] = (
            self.stats['total_processing_time_ms'] / self.stats['sessions_processed']
        )
        
        # Update success rate
        successful_sessions = sum(1 for _ in range(self.stats['sessions_processed']) if result.success)
        self.stats['success_rate'] = (successful_sessions / self.stats['sessions_processed']) * 100
    
    def _log_completion_summary(self, result: EnhancementResult):
        """Log completion summary with key metrics."""
        success_icon = "✅" if result.success else "❌"
        
        logger.info(f"{success_icon} Enhancement complete for {result.session_id}:")
        logger.info(f"   • Overall improvement: {result.overall_improvement:.1f}%")
        logger.info(f"   • Health score: {result.health_score:.2f}")
        logger.info(f"   • Processing time: {result.processing_time_ms:.1f}ms")
        
        if result.backfill_stats.success:
            logger.info(f"   • Chain relationships built: {result.backfill_stats.relationships_built}")
            logger.info(f"   • Chain population improvement: {result.backfill_stats.population_improvement:.1f}%")
        
        if result.optimization_stats.success:
            logger.info(f"   • Fields optimized: {len(result.optimization_stats.fields_optimized)}")
        
        if result.validation_stats.success:
            logger.info(f"   • Validation passed: {result.validation_stats.validation_passed}")
    
    def get_engine_statistics(self) -> Dict[str, Any]:
        """Get comprehensive engine statistics."""
        return {
            **self.stats,
            'performance_compliance': {
                'target_seconds': self.performance_target,
                'violations': self.stats['performance_violations'],
                'compliance_rate': (
                    ((self.stats['sessions_processed'] - self.stats['performance_violations']) / 
                     max(1, self.stats['sessions_processed'])) * 100
                )
            },
            'component_status': {
                'backfill_engine_initialized': self._backfill_engine is not None,
                'field_optimizer_initialized': self._field_optimizer is not None,
                'metadata_monitor_initialized': self._metadata_monitor is not None
            }
        }
    
    def get_system_health_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive system health report.
        
        Returns:
            Complete health report including conversation chain analysis,
            field population statistics, and performance metrics.
        """
        logger.info("📊 Generating comprehensive system health report")
        
        try:
            # Get conversation chain health analysis
            chain_health = self.analyze_conversation_chain_health()
            
            # Get engine statistics
            engine_stats = self.get_engine_statistics()
            
            # Get database health from monitor
            db_health = self.metadata_monitor.get_database_health_summary()
            
            # Get real-time learning insights
            learning_insights = get_realtime_learning_insights()
            
            # Combine into comprehensive report
            health_report = {
                'report_timestamp': datetime.now().isoformat(),
                'system_status': 'healthy' if chain_health.get('overall_health_score', 0) > 0.8 else 'needs_attention',
                'conversation_chain_health': chain_health,
                'engine_performance': engine_stats,
                'database_health': db_health,
                'learning_system': learning_insights,
                'critical_issues': self._identify_critical_issues(chain_health, engine_stats, db_health),
                'recommendations': self._generate_health_recommendations(chain_health, engine_stats)
            }
            
            return health_report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate system health report: {e}")
            return {
                'report_timestamp': datetime.now().isoformat(),
                'system_status': 'error',
                'error': str(e),
                'critical_issues': ['System health report generation failed'],
                'recommendations': ['Check system logs and component health']
            }
    
    def _identify_critical_issues(self, chain_health: Dict, engine_stats: Dict, db_health: Dict) -> List[str]:
        """Identify critical issues requiring immediate attention."""
        issues = []
        
        # Check conversation chain population
        if 'chain_coverage' in chain_health:
            prev_msg_coverage = chain_health['chain_coverage'].get('previous_message_id', 0)
            if prev_msg_coverage < 0.8:  # Less than 80%
                issues.append(f"Critical: Conversation chain population at {prev_msg_coverage:.1%} (target: 80%+)")
        
        # Check performance compliance
        compliance_rate = engine_stats.get('performance_compliance', {}).get('compliance_rate', 100)
        if compliance_rate < 95:  # Less than 95% compliance
            issues.append(f"Performance: {compliance_rate:.1f}% compliance with {self.performance_target}s target")
        
        # Check database health
        if db_health.get('status') != 'healthy':
            issues.append(f"Database health: {db_health.get('status', 'unknown')}")
        
        return issues
    
    def _generate_health_recommendations(self, chain_health: Dict, engine_stats: Dict) -> List[str]:
        """Generate actionable health recommendations."""
        recommendations = []
        
        # Conversation chain recommendations
        if 'chain_coverage' in chain_health:
            prev_msg_coverage = chain_health['chain_coverage'].get('previous_message_id', 0)
            if prev_msg_coverage < 0.8:
                recommendations.append("Run conversation chain back-fill on all sessions")
                recommendations.append("Enable automatic back-fill processing for new sessions")
        
        # Performance recommendations
        avg_time = engine_stats.get('average_processing_time_ms', 0) / 1000
        if avg_time > self.performance_target * 0.8:  # Within 80% of target
            recommendations.append("Consider batch processing optimization for large sessions")
            recommendations.append("Monitor component processing times for bottlenecks")
        
        # General maintenance recommendations
        success_rate = engine_stats.get('success_rate', 100)
        if success_rate < 95:
            recommendations.append("Investigate processing failures and improve error handling")
        
        return recommendations


def main():
    """Test the unified enhancement engine."""
    print("🚀 Testing Unified Enhancement Engine")
    print("=" * 60)
    
    # Initialize engine
    engine = UnifiedEnhancementEngine()
    
    # Get system health report
    print("\n📊 System Health Report:")
    health_report = engine.get_system_health_report()
    print(f"   Status: {health_report['system_status']}")
    
    if health_report.get('critical_issues'):
        print(f"   Critical Issues: {len(health_report['critical_issues'])}")
        for issue in health_report['critical_issues'][:3]:  # Show top 3
            print(f"     • {issue}")
    
    # Get recent sessions for testing
    print("\n🔍 Getting recent sessions...")
    recent_sessions = engine.get_recent_sessions(hours=24, limit=5)
    print(f"   Found {len(recent_sessions)} recent sessions")
    
    # Test processing if sessions available
    if recent_sessions:
        print(f"\n⚙️ Testing enhancement processing on {recent_sessions[0]}...")
        result = engine.process_enhancement_session(recent_sessions[0])
        
        print(f"   Success: {result.success}")
        print(f"   Processing time: {result.processing_time_ms:.1f}ms")
        print(f"   Overall improvement: {result.overall_improvement:.1f}%")
        
        if result.backfill_stats.success:
            print(f"   Relationships built: {result.backfill_stats.relationships_built}")
    
    # Display engine statistics
    print("\n📈 Engine Statistics:")
    stats = engine.get_engine_statistics()
    print(f"   Sessions processed: {stats['sessions_processed']}")
    print(f"   Average processing time: {stats['average_processing_time_ms']:.1f}ms")
    print(f"   Performance compliance: {stats['performance_compliance']['compliance_rate']:.1f}%")
    
    print("\n✅ Unified Enhancement Engine test completed!")


if __name__ == "__main__":
    main()