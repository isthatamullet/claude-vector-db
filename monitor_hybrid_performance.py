#!/usr/bin/env python3
"""Monitor hybrid processing performance in production"""

import sys
import time
import json
import psutil
from datetime import datetime
sys.path.insert(0, '.')

from database.vector_database import ClaudeVectorDatabase

def monitor_hybrid_performance(duration_minutes: int = 5):
    """Monitor hybrid processing performance for specified duration"""
    
    print(f"📊 Monitoring hybrid processing performance for {duration_minutes} minutes...")
    
    db = ClaudeVectorDatabase()
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    # Initial metrics
    initial_count = db.collection.count()
    initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
    
    metrics = {
        "start_time": datetime.now().isoformat(),
        "initial_count": initial_count,
        "initial_memory_mb": initial_memory,
        "measurements": []
    }
    
    print(f"Initial database count: {initial_count}")
    print(f"Initial memory usage: {initial_memory:.1f} MB")
    print("\nMonitoring...")
    
    while time.time() < end_time:
        current_time = datetime.now()
        current_count = db.collection.count()
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Test search performance
        search_start = time.time()
        results = db.search_conversations("test query", n_results=5)
        search_duration = (time.time() - search_start) * 1000  # ms
        
        measurement = {
            "timestamp": current_time.isoformat(),
            "database_count": current_count,
            "memory_usage_mb": current_memory,
            "search_latency_ms": search_duration,
            "new_entries": current_count - initial_count
        }
        
        metrics["measurements"].append(measurement)
        
        print(f"\r{current_time.strftime('%H:%M:%S')} | "
              f"Count: {current_count} (+{current_count - initial_count}) | "
              f"Memory: {current_memory:.1f} MB | "
              f"Search: {search_duration:.1f}ms", end="")
        
        time.sleep(30)  # Check every 30 seconds
    
    # Final analysis
    print("\n\n📈 Performance Analysis:")
    
    if metrics["measurements"]:
        final_measurement = metrics["measurements"][-1]
        
        memory_increase = final_measurement["memory_usage_mb"] - initial_memory
        entries_added = final_measurement["new_entries"]
        avg_search_latency = sum(m["search_latency_ms"] for m in metrics["measurements"]) / len(metrics["measurements"])
        
        print(f"   New entries processed: {entries_added}")
        print(f"   Memory increase: {memory_increase:.1f} MB")
        print(f"   Average search latency: {avg_search_latency:.1f}ms")
        
        # Performance assessment
        if avg_search_latency < 200:
            print("✅ Search performance target met (<200ms)")
        else:
            print(f"⚠️ Search performance above target: {avg_search_latency:.1f}ms")
        
        if memory_increase < 100:
            print("✅ Memory usage increase acceptable (<100MB)")
        else:
            print(f"⚠️ Memory usage increase high: {memory_increase:.1f}MB")
    
    # Save metrics
    with open(f"hybrid_performance_metrics_{int(time.time())}.json", "w") as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✅ Performance monitoring complete. Metrics saved.")

if __name__ == "__main__":
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    monitor_hybrid_performance(duration)