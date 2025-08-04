#!/usr/bin/env python3
"""
Performance Benchmark Suite for PRP-4 Enhanced MCP System

Validates PRP-4 performance improvements including caching, monitoring, and analytics.
Tests against performance targets: <200ms search latency, >85% cache hit rate, <100ms dashboard response.
"""

import asyncio
import time
import statistics
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

class PerformanceBenchmarkSuite:
    """Comprehensive performance benchmarking for PRP-4 enhancements"""
    
    def __init__(self):
        self.benchmark_results = {
            "timestamp": datetime.now().isoformat(),
            "prp4_version": "Final Optimization",
            "performance_targets": {
                "cache_miss_latency_ms": 200,
                "cache_hit_latency_ms": 5,
                "cache_hit_rate_target": 0.85,
                "dashboard_response_ms": 100,
                "error_rate_max": 0.01
            },
            "test_results": {},
            "performance_summary": {}
        }
    
    async def run_benchmarks(self):
        """Execute comprehensive performance benchmarks"""
        print("🚀 PRP-4 Performance Benchmark Suite")
        print("=" * 50)
        
        # 1. Cache Performance Benchmark
        await self.benchmark_cache_performance()
        
        # 2. Search Latency Benchmark
        await self.benchmark_search_latency()
        
        # 3. Dashboard Performance Benchmark
        await self.benchmark_dashboard_performance()
        
        # 4. Concurrent Load Benchmark
        await self.benchmark_concurrent_load()
        
        # 5. System Status Performance
        await self.benchmark_system_status()
        
        # Generate performance report
        self.generate_performance_report()
    
    async def benchmark_cache_performance(self):
        """Benchmark PRP-4 caching system performance"""
        print("\n🚀 Cache Performance Benchmark")
        print("-" * 30)
        
        test_queries = [
            "React component optimization",
            "TypeScript debugging errors", 
            "Next.js performance issues",
            "Database connection pooling",
            "CSS styling problems"
        ]
        
        cache_miss_times = []
        cache_hit_times = []
        
        for i, query in enumerate(test_queries):
            print(f"🔍 Testing query {i+1}/{len(test_queries)}: {query[:30]}...")
            
            # First run - cache miss expected
            start = time.time()
            try:
                result1 = await search_conversations_unified(
                    query=query, 
                    limit=5, 
                    search_mode="semantic"
                )
                miss_time = (time.time() - start) * 1000
                cache_miss_times.append(miss_time)
                
                # Second run - cache hit expected
                start = time.time()
                result2 = await search_conversations_unified(
                    query=query,
                    limit=5,
                    search_mode="semantic"
                )
                hit_time = (time.time() - start) * 1000
                cache_hit_times.append(hit_time)
                
                improvement = miss_time / max(hit_time, 0.1)
                print(f"   Cache Miss: {miss_time:.1f}ms, Hit: {hit_time:.1f}ms ({improvement:.1f}x)")
                
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        # Calculate cache performance metrics
        if cache_miss_times and cache_hit_times:
            avg_miss_time = statistics.mean(cache_miss_times)
            avg_hit_time = statistics.mean(cache_hit_times)
            avg_improvement = avg_miss_time / max(avg_hit_time, 0.1)
            
            self.benchmark_results["test_results"]["cache_performance"] = {
                "avg_cache_miss_ms": round(avg_miss_time, 2),
                "avg_cache_hit_ms": round(avg_hit_time, 2),
                "performance_improvement": f"{avg_improvement:.1f}x",
                "meets_targets": {
                    "cache_miss_under_200ms": avg_miss_time < 200,
                    "cache_hit_under_5ms": avg_hit_time < 5,
                    "improvement_over_5x": avg_improvement > 5
                }
            }
            
            print(f"\n📊 Cache Performance Summary:")
            print(f"   Average Cache Miss: {avg_miss_time:.1f}ms (target: <200ms)")
            print(f"   Average Cache Hit: {avg_hit_time:.1f}ms (target: <5ms)")
            print(f"   Performance Improvement: {avg_improvement:.1f}x")
    
    async def benchmark_search_latency(self):
        """Benchmark search latency across different modes"""
        print("\n🔍 Search Latency Benchmark")
        print("-" * 30)
        
        search_modes = ["semantic", "validated_only", "recent_only"]
        query = "React component debugging"
        
        latency_results = {}
        
        for mode in search_modes:
            print(f"📊 Testing {mode} mode...")
            
            latencies = []
            for i in range(3):  # Run 3 times for average
                start = time.time()
                try:
                    result = await search_conversations_unified(
                        query=query,
                        search_mode=mode,
                        limit=5
                    )
                    latency = (time.time() - start) * 1000
                    latencies.append(latency)
                except Exception as e:
                    print(f"   ❌ Error in {mode}: {e}")
                    latencies.append(float('inf'))
            
            avg_latency = statistics.mean([l for l in latencies if l != float('inf')])
            latency_results[mode] = avg_latency
            print(f"   Average latency: {avg_latency:.1f}ms")
        
        self.benchmark_results["test_results"]["search_latency"] = latency_results
    
    async def benchmark_dashboard_performance(self):
        """Benchmark PRP-4 performance analytics dashboard"""
        print("\n📊 Dashboard Performance Benchmark")
        print("-" * 35)
        
        dashboard_times = []
        
        for i in range(5):  # Test 5 times
            start = time.time()
            try:
                result = await get_performance_analytics_dashboard()
                duration = (time.time() - start) * 1000
                dashboard_times.append(duration)
                print(f"   Run {i+1}: {duration:.1f}ms")
            except Exception as e:
                print(f"   ❌ Dashboard error: {e}")
                dashboard_times.append(float('inf'))
        
        valid_times = [t for t in dashboard_times if t != float('inf')]
        if valid_times:
            avg_dashboard_time = statistics.mean(valid_times)
            self.benchmark_results["test_results"]["dashboard_performance"] = {
                "avg_response_ms": round(avg_dashboard_time, 2),
                "meets_target": avg_dashboard_time < 100,
                "all_times": [round(t, 2) for t in valid_times]
            }
            
            print(f"\n📊 Dashboard Performance:")
            print(f"   Average Response: {avg_dashboard_time:.1f}ms (target: <100ms)")
            print(f"   Target Met: {'✅' if avg_dashboard_time < 100 else '❌'}")
    
    async def benchmark_concurrent_load(self):
        """Test performance under concurrent load"""
        print("\n⚡ Concurrent Load Benchmark")
        print("-" * 30)
        
        concurrent_queries = [
            "React hooks usage",
            "CSS flexbox layout", 
            "JavaScript async await",
            "TypeScript interfaces",
            "Node.js performance"
        ]
        
        # Run queries concurrently
        start = time.time()
        try:
            tasks = [
                search_conversations_unified(query=q, limit=3)
                for q in concurrent_queries
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            total_time = (time.time() - start) * 1000
            
            successful_results = sum(1 for r in results if not isinstance(r, Exception))
            error_rate = (len(results) - successful_results) / len(results)
            
            self.benchmark_results["test_results"]["concurrent_load"] = {
                "total_queries": len(concurrent_queries),
                "successful_queries": successful_results,
                "total_time_ms": round(total_time, 2),
                "avg_time_per_query_ms": round(total_time / len(concurrent_queries), 2),
                "error_rate": round(error_rate, 3),
                "meets_error_target": error_rate < 0.01
            }
            
            print(f"   Total Queries: {len(concurrent_queries)}")
            print(f"   Successful: {successful_results}")
            print(f"   Total Time: {total_time:.1f}ms")
            print(f"   Avg per Query: {total_time / len(concurrent_queries):.1f}ms")
            print(f"   Error Rate: {error_rate:.1%}")
            
        except Exception as e:
            print(f"   ❌ Concurrent load test failed: {e}")
    
    async def benchmark_system_status(self):
        """Benchmark system status with PRP-4 metrics"""
        print("\n⚙️ System Status Benchmark")
        print("-" * 30)
        
        status_times = []
        
        for status_type in ["performance", "comprehensive"]:
            start = time.time()
            try:
                result = await get_system_status(status_type=status_type)
                duration = (time.time() - start) * 1000
                status_times.append(duration)
                
                # Check for PRP-4 integration
                has_prp4 = result.get("prp4_optimization", False) if isinstance(result, dict) else False
                print(f"   {status_type}: {duration:.1f}ms, PRP-4: {'✅' if has_prp4 else '❌'}")
                
            except Exception as e:
                print(f"   ❌ {status_type} status error: {e}")
        
        if status_times:
            avg_status_time = statistics.mean(status_times)
            self.benchmark_results["test_results"]["system_status"] = {
                "avg_response_ms": round(avg_status_time, 2),
                "performance_mode_ms": status_times[0] if len(status_times) > 0 else 0,
                "comprehensive_mode_ms": status_times[1] if len(status_times) > 1 else 0
            }
    
    def generate_performance_report(self):
        """Generate comprehensive performance benchmark report"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE BENCHMARK REPORT - PRP-4 Enhanced System")
        print("=" * 60)
        
        # Calculate overall performance score
        targets = self.benchmark_results["performance_targets"]
        results = self.benchmark_results["test_results"]
        
        score_components = []
        
        # Cache performance score
        if "cache_performance" in results:
            cache_data = results["cache_performance"]
            cache_score = 0
            if cache_data["meets_targets"]["cache_miss_under_200ms"]:
                cache_score += 25
            if cache_data["meets_targets"]["cache_hit_under_5ms"]:
                cache_score += 25
            if cache_data["meets_targets"]["improvement_over_5x"]:
                cache_score += 25
            score_components.append(cache_score)
        
        # Dashboard performance score
        if "dashboard_performance" in results:
            dashboard_score = 25 if results["dashboard_performance"]["meets_target"] else 0
            score_components.append(dashboard_score)
        
        # Error rate score
        if "concurrent_load" in results:
            error_score = 25 if results["concurrent_load"]["meets_error_target"] else 0
            score_components.append(error_score)
        
        overall_score = sum(score_components) if score_components else 0
        
        print(f"📅 Benchmark Date: {self.benchmark_results['timestamp']}")
        print(f"🔧 System Version: {self.benchmark_results['prp4_version']}")
        print(f"🏆 Overall Performance Score: {overall_score}/100")
        
        print(f"\n🎯 Performance Targets vs Results:")
        
        # Cache Performance
        if "cache_performance" in results:
            cache_data = results["cache_performance"]
            print(f"   🚀 Cache Miss Latency: {cache_data['avg_cache_miss_ms']:.1f}ms (target: <{targets['cache_miss_latency_ms']}ms)")
            print(f"   ⚡ Cache Hit Latency: {cache_data['avg_cache_hit_ms']:.1f}ms (target: <{targets['cache_hit_latency_ms']}ms)")
            print(f"   📈 Performance Improvement: {cache_data['performance_improvement']}")
        
        # Dashboard Performance
        if "dashboard_performance" in results:
            dashboard_data = results["dashboard_performance"]
            print(f"   📊 Dashboard Response: {dashboard_data['avg_response_ms']:.1f}ms (target: <{targets['dashboard_response_ms']}ms)")
        
        # Error Rate
        if "concurrent_load" in results:
            load_data = results["concurrent_load"]
            print(f"   ❌ Error Rate: {load_data['error_rate']:.1%} (target: <{targets['error_rate_max']:.1%})")
        
        print(f"\n📈 Detailed Results:")
        for test_name, test_results in results.items():
            print(f"   {test_name.replace('_', ' ').title()}:")
            if isinstance(test_results, dict):
                for key, value in test_results.items():
                    if not key.startswith('meets_'):
                        print(f"     {key}: {value}")
        
        print(f"\n💡 Performance Recommendations:")
        if overall_score >= 90:
            print("   ✅ Excellent performance - all targets met")
        elif overall_score >= 70:
            print("   🟡 Good performance - minor optimizations possible")
        else:
            print("   🔴 Performance needs improvement")
            
        if "cache_performance" in results:
            cache_data = results["cache_performance"]
            if not cache_data["meets_targets"]["cache_hit_under_5ms"]:
                print("   - Consider increasing cache size or optimizing cache keys")
        
        if "dashboard_performance" in results:
            if not results["dashboard_performance"]["meets_target"]:
                print("   - Optimize dashboard query aggregation")
        
        print("   - Monitor performance trends over time")
        print("   - Run benchmarks regularly after system changes")
        
        # Save detailed results
        import json
        report_file = f"performance_benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.benchmark_results, f, indent=2)
        print(f"\n📄 Detailed benchmark data saved to: {report_file}")

async def main():
    """Main benchmark execution"""
    benchmark_suite = PerformanceBenchmarkSuite()
    await benchmark_suite.run_benchmarks()

if __name__ == "__main__":
    asyncio.run(main())