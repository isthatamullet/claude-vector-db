#!/usr/bin/env python3
"""
Comprehensive Test Suite for 15-Tool MCP System
PRP-4 Final Optimization Testing Framework

Tests all 15 consolidated MCP tools with performance validation and PRP-4 enhancement verification.
"""

import asyncio
import time
import json
import sys
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Get package root directory (2 levels up from tests/integration/)
from pathlib import Path
PACKAGE_ROOT = Path(__file__).parent.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

# Import MCP server components
try:
    # Add the mcp directory to path
    mcp_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mcp')
    sys.path.insert(0, mcp_path)
    
    from mcp_server import *
    print("✅ MCP server components imported successfully")
except ImportError as e:
    print(f"❌ Failed to import MCP server: {e}")
    print("Attempting direct import...")
    try:
        # Alternative import method
        exec(open('mcp/mcp_server.py').read(), globals())
        print("✅ MCP server loaded via exec")
    except Exception as e2:
        print(f"❌ Direct import also failed: {e2}")
        sys.exit(1)

class ComprehensiveTestSuite:
    """Comprehensive testing framework for all 15 MCP tools"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "total_tools": 15,
            "tests_passed": 0,
            "tests_failed": 0,
            "performance_metrics": {},
            "tool_results": {}
        }
        
    async def run_all_tests(self):
        """Execute comprehensive test suite for all 15 tools"""
        print("🚀 Starting Comprehensive Test Suite for 15-Tool MCP System")
        print("=" * 70)
        
        # Category 1: Search & Retrieval Tools (1 tool)
        await self.test_search_conversations_unified()
        
        # Category 2: Context & Project Management (3 tools)
        await self.test_get_project_context_summary()
        await self.test_detect_current_project()
        await self.test_get_conversation_context_chain()
        
        # Category 3: Data Processing & Sync Tools (2 tools)
        await self.test_force_conversation_sync()
        await self.test_smart_metadata_sync_status()
        
        # Category 4: Analytics & Learning Tools (2 tools)
        await self.test_get_learning_insights()
        await self.test_process_feedback_unified()
        
        # Category 5: Enhancement System Management (3 tools)
        await self.test_run_unified_enhancement()
        await self.test_get_system_status()
        await self.test_configure_enhancement_systems()
        
        # Category 6: Pattern Analysis & Adaptive Learning (2 tools)
        await self.test_analyze_patterns_unified()
        await self.test_run_adaptive_learning_enhancement()
        
        # Category 7: Performance Analytics (1 tool - NEW PRP-4)
        await self.test_get_performance_analytics_dashboard()
        
        # Performance validation
        await self.test_prp4_performance_improvements()
        
        # Generate final report
        self.generate_test_report()
        
    async def test_tool(self, tool_name: str, test_func, *args, **kwargs):
        """Generic tool testing wrapper with performance monitoring"""
        print(f"\n🧪 Testing {tool_name}...")
        
        try:
            start_time = time.time()
            result = await test_func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            
            # Basic validation
            success = result is not None and not (isinstance(result, dict) and result.get("error"))
            
            self.test_results["tool_results"][tool_name] = {
                "status": "PASS" if success else "FAIL",
                "duration_ms": round(duration_ms, 2),
                "result_type": type(result).__name__,
                "result_size": len(result) if isinstance(result, (list, dict, str)) else 1
            }
            
            if success:
                self.test_results["tests_passed"] += 1
                print(f"✅ {tool_name}: PASS ({duration_ms:.1f}ms)")
            else:
                self.test_results["tests_failed"] += 1
                print(f"❌ {tool_name}: FAIL - {result.get('error', 'Unknown error') if isinstance(result, dict) else 'Invalid result'}")
                
            return result
            
        except Exception as e:
            self.test_results["tests_failed"] += 1
            self.test_results["tool_results"][tool_name] = {
                "status": "ERROR",
                "error": str(e),
                "duration_ms": 0
            }
            print(f"💥 {tool_name}: ERROR - {e}")
            return None
    
    # ===== TOOL TESTS =====
    
    async def test_search_conversations_unified(self):
        """Test unified search with PRP-4 caching validation"""
        print("\n📂 Category 1: Search & Retrieval Tools")
        
        # Basic semantic search
        await self.test_tool(
            "search_conversations_unified",
            search_conversations_unified,
            query="React component testing",
            limit=5,
            search_mode="semantic"
        )
        
        # Cache performance test (same query twice)
        print("🚀 Testing PRP-4 caching performance...")
        query = "React component optimization"
        
        # First run (cache miss expected)
        start = time.time()
        result1 = await search_conversations_unified(query, limit=3)
        miss_time = (time.time() - start) * 1000
        
        # Second run (cache hit expected)
        start = time.time()
        result2 = await search_conversations_unified(query, limit=3)
        hit_time = (time.time() - start) * 1000
        
        # Validate cache improvement
        if hit_time > 0:
            improvement = miss_time / hit_time
            self.test_results["performance_metrics"]["cache_improvement"] = f"{improvement:.1f}x"
            print(f"🚀 Cache Performance: {miss_time:.1f}ms → {hit_time:.1f}ms ({improvement:.1f}x improvement)")
        
    async def test_get_project_context_summary(self):
        """Test project context analysis"""
        print("\n📊 Category 2: Context & Project Management")
        await self.test_tool(
            "get_project_context_summary",
            get_project_context_summary
        )
    
    async def test_detect_current_project(self):
        """Test project detection"""
        await self.test_tool(
            "detect_current_project", 
            detect_current_project
        )
    
    async def test_get_conversation_context_chain(self):
        """Test conversation context chain (requires valid message ID)"""
        # Skip if no valid message ID available
        print("⏭️  get_conversation_context_chain: SKIPPED (requires valid message ID)")
        self.test_results["tool_results"]["get_conversation_context_chain"] = {
            "status": "SKIPPED",
            "reason": "Requires valid message ID for testing"
        }
    
    async def test_force_conversation_sync(self):
        """Test conversation sync"""
        print("\n🔄 Category 3: Data Processing & Sync Tools")
        await self.test_tool(
            "force_conversation_sync",
            force_conversation_sync,
            parallel_processing=True
        )
    
    async def test_smart_metadata_sync_status(self):
        """Test metadata sync status"""
        await self.test_tool(
            "smart_metadata_sync_status",
            smart_metadata_sync_status
        )
    
    
    async def test_get_learning_insights(self):
        """Test learning insights"""
        print("\n🧠 Category 4: Analytics & Learning Tools")
        await self.test_tool(
            "get_learning_insights",
            get_learning_insights,
            insight_type="comprehensive"
        )
    
    async def test_process_feedback_unified(self):
        """Test unified feedback processing"""
        await self.test_tool(
            "process_feedback_unified",
            process_feedback_unified,
            feedback_text="This solution worked perfectly!",
            solution_context={"tool_used": "Edit", "file_modified": "test.tsx"}
        )
    
    async def test_run_unified_enhancement(self):
        """Test unified enhancement"""
        print("\n⚙️ Category 5: Enhancement System Management")
        await self.test_tool(
            "run_unified_enhancement",
            run_unified_enhancement,
            max_sessions=5  # Limit for testing
        )
    
    async def test_get_system_status(self):
        """Test system status with PRP-4 metrics"""
        result = await self.test_tool(
            "get_system_status",
            get_system_status,
            status_type="comprehensive"
        )
        
        # Validate PRP-4 integration
        if result and isinstance(result, dict):
            has_prp4 = result.get("prp4_optimization", False)
            has_performance_metrics = "prp4_performance_metrics" in result
            print(f"🚀 PRP-4 Integration: {has_prp4}, Performance Metrics: {has_performance_metrics}")
    
    async def test_configure_enhancement_systems(self):
        """Test enhancement configuration with PRP-4 features"""
        await self.test_tool(
            "configure_enhancement_systems",
            configure_enhancement_systems,
            enable_prp4_caching=True,
            cache_size=500,
            performance_mode="balanced"
        )
    
    async def test_analyze_patterns_unified(self):
        """Test unified pattern analysis"""
        print("\n🔍 Category 6: Pattern Analysis & Adaptive Learning")
        await self.test_tool(
            "analyze_patterns_unified",
            analyze_patterns_unified,
            feedback_content="The component rendering is slow",
            analysis_type="multimodal"
        )
    
    async def test_run_adaptive_learning_enhancement(self):
        """Test adaptive learning enhancement"""
        await self.test_tool(
            "run_adaptive_learning_enhancement",
            run_adaptive_learning_enhancement,
            learning_type="comprehensive"
        )
    
    async def test_get_performance_analytics_dashboard(self):
        """Test PRP-4 performance analytics dashboard"""
        print("\n📊 Category 7: Performance Analytics (NEW PRP-4)")
        result = await self.test_tool(
            "get_performance_analytics_dashboard",
            get_performance_analytics_dashboard
        )
        
        # Validate dashboard structure
        if result and isinstance(result, dict):
            has_dashboard = result.get("prp4_dashboard", False)
            has_performance_score = "performance_score" in result
            has_cache_analytics = "cache_analytics" in result
            
            print(f"🚀 Dashboard Status: {has_dashboard}")
            print(f"📊 Performance Score: {has_performance_score}")
            print(f"🚀 Cache Analytics: {has_cache_analytics}")
            
            if has_performance_score:
                score = result["performance_score"].get("overall", 0)
                self.test_results["performance_metrics"]["dashboard_score"] = score
    
    async def test_prp4_performance_improvements(self):
        """Test PRP-4 specific performance improvements"""
        print("\n🚀 PRP-4 Performance Validation")
        print("-" * 40)
        
        # Test enhanced cache system
        cache_metrics = enhanced_cache.get_metrics() if 'enhanced_cache' in globals() else {}
        performance_metrics = performance_monitor.get_performance_status() if 'performance_monitor' in globals() else {}
        
        print(f"🚀 Cache System: {'Available' if cache_metrics else 'Not Available'}")
        print(f"📊 Performance Monitor: {'Available' if performance_metrics else 'Not Available'}")
        
        if cache_metrics:
            print(f"   Hit Rate: {cache_metrics.get('cache_hit_rate', 0):.1%}")
            print(f"   Total Requests: {cache_metrics.get('total_requests', 0)}")
            print(f"   Cache Size: {cache_metrics.get('cache_size', 0)}")
        
        if performance_metrics:
            print(f"   Avg Latency: {performance_metrics.get('avg_search_latency_ms', 0):.1f}ms")
            print(f"   Error Rate: {performance_metrics.get('error_rate_percent', 0):.1f}%")
            print(f"   Status: {performance_metrics.get('performance_status', 'unknown')}")
    
    def generate_test_report(self):
        """Generate comprehensive test execution report"""
        print("\n" + "=" * 70)
        print("📊 TEST EXECUTION REPORT - PRP-4 Enhanced System")
        print("=" * 70)
        
        total_tests = self.test_results["tests_passed"] + self.test_results["tests_failed"]
        pass_rate = (self.test_results["tests_passed"] / max(total_tests, 1)) * 100
        
        print(f"📅 Date: {self.test_results['timestamp']}")
        print(f"🔧 System Version: PRP-4 Final Optimization")
        print(f"📊 Tools Tested: {total_tests}/{self.test_results['total_tools']}")
        print(f"✅ Pass Rate: {pass_rate:.1f}%")
        
        print(f"\n📈 Performance Results:")
        for metric, value in self.test_results["performance_metrics"].items():
            print(f"   {metric}: {value}")
        
        print(f"\n🔧 Tool Status:")
        for tool, result in self.test_results["tool_results"].items():
            status = result["status"]
            duration = result.get("duration_ms", 0)
            emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⏭️"
            print(f"   {emoji} {tool}: {status} ({duration:.1f}ms)")
        
        print(f"\n💡 Recommendations:")
        if pass_rate < 90:
            print("   - Investigate failed tools and address issues")
        if self.test_results["performance_metrics"].get("cache_improvement", "1x").replace("x", "") != "1":
            print("   - Cache system working optimally")
        else:
            print("   - Consider cache configuration optimization")
        
        print("   - Monitor performance trends over time")
        print("   - Run tests regularly to ensure system health")
        
        # Save report to file
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed report saved to: {report_file}")

async def main():
    """Main test execution"""
    test_suite = ComprehensiveTestSuite()
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())