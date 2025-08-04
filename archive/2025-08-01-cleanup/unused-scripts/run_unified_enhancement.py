#!/usr/bin/env python3
"""
Standalone Unified Enhancement Script

Direct command-line interface for the enhanced vector database unified enhancement system.
Provides conversation chain back-fill, field optimization, and health monitoring capabilities
without requiring MCP server integration.

This script addresses the critical conversation chain population issue (0.97% → 80%+) 
and systematically optimizes all 30+ metadata fields with comprehensive health reporting.

Usage:
  python run_unified_enhancement.py --session SESSION_ID    # Process specific session
  python run_unified_enhancement.py --recent 10             # Process 10 recent sessions  
  python run_unified_enhancement.py --health-check          # System health analysis
  python run_unified_enhancement.py --chain-analysis        # Conversation chain coverage analysis

Author: Enhanced Vector Database System (July 2025)
Version: 1.0.0
"""

import argparse
import sys
import time
from datetime import datetime
from typing import List, Optional

# Import unified enhancement engine
from unified_enhancement_engine import UnifiedEnhancementEngine


class UnifiedEnhancementCLI:
    """Command-line interface for unified enhancement system."""
    
    def __init__(self, db_path: Optional[str] = None, performance_target: float = 30.0):
        """Initialize the CLI with unified enhancement engine."""
        self.db_path = db_path or "/home/user/.claude-vector-db-enhanced/chroma_db"
        self.performance_target = performance_target
        self.engine = None
        
    def initialize_engine(self):
        """Initialize the unified enhancement engine."""
        try:
            print("🔧 Initializing Unified Enhancement Engine...")
            self.engine = UnifiedEnhancementEngine(
                db_path=self.db_path,
                performance_target_seconds=self.performance_target
            )
            print("✅ Engine initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize engine: {e}")
            return False
    
    def process_single_session(self, session_id: str, 
                             enable_backfill: bool = True,
                             enable_optimization: bool = True,
                             enable_validation: bool = True) -> bool:
        """Process a single session with unified enhancement."""
        
        print(f"\n🎯 Processing session: {session_id}")
        print(f"   Backfill: {'✅' if enable_backfill else '❌'}")
        print(f"   Optimization: {'✅' if enable_optimization else '❌'}")
        print(f"   Validation: {'✅' if enable_validation else '❌'}")
        
        try:
            start_time = time.time()
            
            result = self.engine.process_enhancement_session(
                session_id=session_id,
                enable_backfill=enable_backfill,
                enable_optimization=enable_optimization,
                enable_validation=enable_validation
            )
            
            processing_time = time.time() - start_time
            
            # Display results
            self._display_session_result(result, processing_time)
            
            return result.success
            
        except Exception as e:
            print(f"❌ Error processing session {session_id}: {e}")
            return False
    
    def process_recent_sessions(self, max_sessions: int = 10,
                              hours_back: int = 24,
                              enable_backfill: bool = True,
                              max_processing_time: float = 300.0) -> bool:
        """Process recent sessions with unified enhancement."""
        
        print("\n🔄 Processing recent sessions...")
        print(f"   Max sessions: {max_sessions}")
        print(f"   Time range: {hours_back} hours")
        print(f"   Max processing time: {max_processing_time}s")
        
        try:
            # Get recent sessions
            print("🔍 Finding recent sessions...")
            recent_sessions = self.engine.get_recent_sessions(
                hours=hours_back, 
                limit=max_sessions
            )
            
            if not recent_sessions:
                print("⚠️ No recent sessions found")
                return False
            
            print(f"📋 Found {len(recent_sessions)} sessions to process")
            
            # Process sessions
            start_time = time.time()
            results = self.engine.process_multiple_sessions(
                session_ids=recent_sessions,
                max_processing_time_seconds=max_processing_time,
                batch_size=5
            )
            total_time = time.time() - start_time
            
            # Display batch results
            self._display_batch_results(results, total_time)
            
            # Check if any sessions were successful
            return any(r.success for r in results)
            
        except Exception as e:
            print(f"❌ Error processing recent sessions: {e}")
            return False
    
    def perform_health_check(self) -> bool:
        """Perform comprehensive system health check."""
        
        print("\n📊 Performing system health check...")
        
        try:
            health_report = self.engine.get_system_health_report()
            
            # Display health report
            self._display_health_report(health_report)
            
            return health_report.get('system_status') in ['healthy', 'needs_attention']
            
        except Exception as e:
            print(f"❌ Error performing health check: {e}")
            return False
    
    def analyze_conversation_chain_coverage(self) -> bool:
        """Analyze conversation chain field coverage."""
        
        print("\n🔗 Analyzing conversation chain coverage...")
        
        try:
            chain_health = self.engine.analyze_conversation_chain_health()
            
            # Display chain analysis
            self._display_chain_analysis(chain_health)
            
            return 'error' not in chain_health
            
        except Exception as e:
            print(f"❌ Error analyzing conversation chain coverage: {e}")
            return False
    
    def _display_session_result(self, result, processing_time: float):
        """Display single session processing results."""
        
        success_icon = "✅" if result.success else "❌"
        
        print(f"\n{success_icon} Enhancement Results for {result.session_id}:")
        print(f"   Overall improvement: {result.overall_improvement:.1f}%")
        print(f"   Health score: {result.health_score:.2f}")
        print(f"   Processing time: {result.processing_time_ms:.1f}ms (CLI: {processing_time*1000:.1f}ms)")
        
        # Performance compliance check
        target_ms = self.performance_target * 1000
        if result.processing_time_ms > target_ms:
            print(f"   ⚠️ Performance target exceeded: {result.processing_time_ms:.1f}ms > {target_ms}ms")
        else:
            print(f"   ✅ Performance target met: {result.processing_time_ms:.1f}ms ≤ {target_ms}ms")
        
        # Component results
        if result.backfill_stats.success:
            print("\n   🔗 Conversation Chain Back-fill:")
            print(f"      Relationships built: {result.backfill_stats.relationships_built}")
            print(f"      Database updates: {result.backfill_stats.database_updates}")
            print(f"      Population improvement: {result.backfill_stats.population_improvement:.1f}%")
            print(f"      Accuracy score: {result.backfill_stats.accuracy_score:.1f}%")
        
        if result.optimization_stats.success and result.optimization_stats.fields_optimized:
            print("\n   ⚙️ Field Optimization:")
            print(f"      Fields optimized: {len(result.optimization_stats.fields_optimized)}")
            for field, score in result.optimization_stats.improvement_scores.items():
                print(f"        • {field}: {score:.1f}% improvement")
        
        if result.validation_stats.success:
            print("\n   ✅ Validation & Health:")
            print(f"      Health score: {result.validation_stats.health_score:.2f}")
            print(f"      Validation passed: {'✅' if result.validation_stats.validation_passed else '❌'}")
    
    def _display_batch_results(self, results: List, total_time: float):
        """Display batch processing results."""
        
        successful_sessions = sum(1 for r in results if r.success)
        total_relationships = sum(r.backfill_stats.relationships_built for r in results if r.backfill_stats.success)
        total_database_updates = sum(r.backfill_stats.database_updates for r in results if r.backfill_stats.success)
        total_improvements = sum(r.overall_improvement for r in results if r.success)
        avg_improvement = total_improvements / successful_sessions if successful_sessions > 0 else 0
        
        print("\n🎯 Batch Processing Results:")
        print(f"   Sessions processed: {len(results)}")
        print(f"   Successful sessions: {successful_sessions}")
        print(f"   Failed sessions: {len(results) - successful_sessions}")
        print(f"   Total processing time: {total_time:.1f}s")
        print(f"   Average per session: {total_time/len(results):.1f}s")
        
        print("\n   🔗 Conversation Chain Back-fill:")
        print(f"      Total relationships built: {total_relationships}")
        print(f"      Total database updates: {total_database_updates}")
        print(f"      Average improvement: {avg_improvement:.1f}%")
        
        # Show individual session summaries
        print("\n   📋 Session Summary:")
        for i, result in enumerate(results[:10], 1):  # Show first 10
            status = "✅" if result.success else "❌"
            improvement = result.overall_improvement if result.success else 0
            relationships = result.backfill_stats.relationships_built if result.backfill_stats.success else 0
            print(f"      {i}. {result.session_id}: {status} {improvement:.1f}% improvement, {relationships} relationships")
        
        if len(results) > 10:
            print(f"      ... and {len(results) - 10} more sessions")
    
    def _display_health_report(self, health_report: dict):
        """Display system health report."""
        
        status = health_report.get('system_status', 'unknown')
        status_icon = {
            'healthy': '✅',
            'needs_attention': '⚠️',
            'error': '❌',
            'critical_error': '🚨'
        }.get(status, '❓')
        
        print(f"\n{status_icon} System Status: {status.upper()}")
        print(f"   Report timestamp: {health_report.get('report_timestamp', 'unknown')}")
        
        # Conversation chain health
        if 'conversation_chain_health' in health_report:
            chain_health = health_report['conversation_chain_health']
            if 'overall_health_score' in chain_health:
                health_score = chain_health['overall_health_score']
                meets_target = chain_health.get('meets_target', False)
                print("\n   🔗 Conversation Chain Health:")
                print(f"      Overall health score: {health_score:.1f}")
                print(f"      Meets 80% target: {'✅' if meets_target else '❌'}")
                
                if 'chain_coverage' in chain_health:
                    coverage = chain_health['chain_coverage']
                    for field, percent in coverage.items():
                        print(f"        • {field}: {percent:.1%}")
        
        # Engine performance
        if 'engine_performance' in health_report:
            perf = health_report['engine_performance']
            print("\n   📊 Engine Performance:")
            print(f"      Sessions processed: {perf.get('sessions_processed', 0)}")
            print(f"      Average processing time: {perf.get('average_processing_time_ms', 0):.1f}ms")
            print(f"      Compliance rate: {perf.get('compliance_rate', 0):.1f}%")
        
        # Critical issues
        if health_report.get('critical_issues'):
            print(f"\n   🚨 Critical Issues ({len(health_report['critical_issues'])}):")
            for issue in health_report['critical_issues'][:5]:  # Show first 5
                print(f"      • {issue}")
        
        # Recommendations
        if health_report.get('recommendations'):
            print(f"\n   💡 Recommendations ({len(health_report['recommendations'])}):")
            for rec in health_report['recommendations'][:5]:  # Show first 5
                print(f"      • {rec}")
    
    def _display_chain_analysis(self, chain_health: dict):
        """Display conversation chain analysis."""
        
        if 'error' in chain_health:
            print(f"❌ Error: {chain_health['error']}")
            return
        
        overall_health = chain_health.get('overall_health_score', 0)
        meets_target = chain_health.get('meets_target', False)
        
        print(f"   Overall chain health: {overall_health:.1f}")
        print(f"   Meets 80% target: {'✅' if meets_target else '❌'}")
        
        if 'chain_coverage' in chain_health:
            print("\n   📊 Field Coverage Analysis:")
            coverage = chain_health['chain_coverage']
            for field, percent in coverage.items():
                status_icon = '✅' if percent >= 0.8 else '⚠️' if percent >= 0.5 else '❌'
                print(f"      {status_icon} {field}: {percent:.1%}")
        
        if 'engine_stats' in chain_health:
            stats = chain_health['engine_stats']
            print("\n   🔧 Engine Statistics:")
            print(f"      Sessions processed: {stats.get('sessions_processed', 0)}")
            print(f"      Total relationships built: {stats.get('total_relationships_built', 0)}")


def main():
    """Main entry point for unified enhancement CLI."""
    
    parser = argparse.ArgumentParser(
        description="Unified Enhancement System - Direct CLI for enhanced vector database",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_unified_enhancement.py --session session_abc123     # Process specific session
  python run_unified_enhancement.py --recent 5                   # Process 5 recent sessions
  python run_unified_enhancement.py --health-check               # System health analysis
  python run_unified_enhancement.py --chain-analysis             # Conversation chain analysis
  python run_unified_enhancement.py --recent 10 --no-backfill    # Process without back-fill
  python run_unified_enhancement.py --session test --no-optimization --no-validation
        """
    )
    
    # Action group (mutually exclusive)
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        '--session',
        type=str,
        help='Process specific session ID with unified enhancement'
    )
    action_group.add_argument(
        '--recent',
        type=int,
        metavar='N',
        help='Process N most recent sessions (default: 10)',
        nargs='?',
        const=10
    )
    action_group.add_argument(
        '--health-check',
        action='store_true',
        help='Perform comprehensive system health check'
    )
    action_group.add_argument(
        '--chain-analysis',
        action='store_true',
        help='Analyze conversation chain field coverage'
    )
    
    # Component control
    parser.add_argument(
        '--no-backfill',
        action='store_true',
        help='Disable conversation chain back-fill processing'
    )
    parser.add_argument(
        '--no-optimization',
        action='store_true',
        help='Disable field population optimization'
    )
    parser.add_argument(
        '--no-validation',
        action='store_true',
        help='Disable validation and health assessment'
    )
    
    # Processing configuration
    parser.add_argument(
        '--hours-back',
        type=int,
        default=24,
        help='Hours back to search for recent sessions (default: 24)'
    )
    parser.add_argument(
        '--max-time',
        type=float,
        default=300.0,
        help='Maximum processing time in seconds (default: 300)'
    )
    parser.add_argument(
        '--performance-target',
        type=float,
        default=30.0,
        help='Performance target per session in seconds (default: 30)'
    )
    parser.add_argument(
        '--db-path',
        type=str,
        help='Custom database path (default: ./chroma_db)'
    )
    
    # Output control
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Increase output verbosity'
    )
    
    args = parser.parse_args()
    
    # Header
    if not args.quiet:
        print("🚀 Unified Enhancement System - Command Line Interface")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
    
    # Initialize CLI
    cli = UnifiedEnhancementCLI(
        db_path=args.db_path,
        performance_target=args.performance_target
    )
    
    if not cli.initialize_engine():
        sys.exit(1)
    
    # Process based on arguments
    success = False
    
    try:
        if args.session:
            # Process specific session
            success = cli.process_single_session(
                session_id=args.session,
                enable_backfill=not args.no_backfill,
                enable_optimization=not args.no_optimization,
                enable_validation=not args.no_validation
            )
            
        elif args.recent is not None:
            # Process recent sessions
            success = cli.process_recent_sessions(
                max_sessions=args.recent,
                hours_back=args.hours_back,
                enable_backfill=not args.no_backfill,
                max_processing_time=args.max_time
            )
            
        elif args.health_check:
            # Perform health check
            success = cli.perform_health_check()
            
        elif args.chain_analysis:
            # Analyze conversation chain coverage
            success = cli.analyze_conversation_chain_coverage()
    
    except KeyboardInterrupt:
        print("\n⚠️ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Final status
    if not args.quiet:
        print()
        if success:
            print("✅ Operation completed successfully")
        else:
            print("❌ Operation completed with issues")
        
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()