#!/usr/bin/env python3
"""Production monitoring dashboard for hybrid system"""

import sys
import time
import json
import psutil
from datetime import datetime, timedelta
sys.path.insert(0, '.')

from database.vector_database import ClaudeVectorDatabase
from processing.enhanced_processor import UnifiedEnhancementProcessor

class ProductionMonitor:
    """Production monitoring for hybrid spaCy + ST system"""
    
    def __init__(self):
        self.db = ClaudeVectorDatabase()
        self.processor = UnifiedEnhancementProcessor(enable_hybrid=True, suppress_init_logging=True)
        self.monitoring_data = []
    
    def collect_metrics(self):
        """Collect current system metrics"""
        timestamp = datetime.now()
        
        # Database metrics
        db_count = self.db.collection.count()
        
        # Memory metrics
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        # Search performance test
        start_time = time.time()
        search_results = self.db.search_conversations("test", n_results=5)
        search_latency = (time.time() - start_time) * 1000
        
        # Processing performance test
        start_time = time.time()
        test_entry = {
            'id': f'monitor_test_{int(time.time())}',
            'content': 'Monitor test for hybrid processing performance',
            'type': 'assistant',
            'project_path': '/monitor',
            'project_name': 'monitor',
            'timestamp': timestamp.isoformat()
        }
        
        try:
            from processing.enhanced_processor import ProcessingContext
            enhanced_entry = self.processor.process_conversation_entry(
                test_entry,
                ProcessingContext(source="monitor")
            )
            processing_latency = (time.time() - start_time) * 1000
            processing_success = True
            hybrid_active = hasattr(enhanced_entry, 'hybrid_data')
        except Exception as e:
            processing_latency = -1
            processing_success = False
            hybrid_active = False
        
        # System stats
        processor_stats = self.processor.get_processor_stats()
        
        metrics = {
            "timestamp": timestamp.isoformat(),
            "database": {
                "total_entries": db_count,
                "search_latency_ms": search_latency,
                "search_results_count": len(search_results)
            },
            "processing": {
                "latency_ms": processing_latency,
                "success": processing_success,
                "components_active": processor_stats.get('components_available', 0),
                "hybrid_active": hybrid_active
            },
            "system": {
                "memory_usage_mb": memory_mb,
                "cpu_percent": psutil.cpu_percent()
            }
        }
        
        return metrics
    
    def run_monitoring_cycle(self, duration_minutes=10, interval_seconds=30):
        """Run monitoring cycle for specified duration"""
        
        print(f"🔍 Starting Production Monitoring ({duration_minutes} minutes)")
        print(f"   Collection interval: {interval_seconds} seconds")
        print(f"   Starting time: {datetime.now().strftime('%H:%M:%S')}")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        cycle_count = 0
        
        while time.time() < end_time:
            try:
                metrics = self.collect_metrics()
                self.monitoring_data.append(metrics)
                cycle_count += 1
                
                # Display current metrics
                current_time = datetime.now().strftime('%H:%M:%S')
                db_count = metrics['database']['total_entries']
                search_ms = metrics['database']['search_latency_ms']
                memory_mb = metrics['system']['memory_usage_mb']
                components = metrics['processing']['components_active']
                
                print(f"\r{current_time} | "
                      f"DB: {db_count} | "
                      f"Search: {search_ms:.1f}ms | "
                      f"Memory: {memory_mb:.1f}MB | "
                      f"Components: {components}/8", end="")
                
                time.sleep(interval_seconds)
                
            except KeyboardInterrupt:
                print(f"\n\n⏹️ Monitoring stopped by user after {cycle_count} cycles")
                break
            except Exception as e:
                print(f"\n❌ Monitoring error: {e}")
                break
        
        # Generate summary
        if self.monitoring_data:
            self.generate_monitoring_report()
        
        return True
    
    def generate_monitoring_report(self):
        """Generate monitoring summary report"""
        
        if not self.monitoring_data:
            print("\n❌ No monitoring data collected")
            return
        
        print(f"\n\n📊 Monitoring Report ({len(self.monitoring_data)} data points)")
        print("=" * 50)
        
        # Calculate averages
        avg_search_latency = sum(m['database']['search_latency_ms'] for m in self.monitoring_data) / len(self.monitoring_data)
        avg_memory = sum(m['system']['memory_usage_mb'] for m in self.monitoring_data) / len(self.monitoring_data)
        avg_processing_latency = sum(m['processing']['latency_ms'] for m in self.monitoring_data if m['processing']['latency_ms'] > 0) / len([m for m in self.monitoring_data if m['processing']['latency_ms'] > 0])
        
        # Check component stability
        components_stable = all(m['processing']['components_active'] >= 8 for m in self.monitoring_data)
        hybrid_stable = all(m['processing']['hybrid_active'] for m in self.monitoring_data)
        
        print(f"Average Search Latency: {avg_search_latency:.1f}ms")
        print(f"Average Memory Usage: {avg_memory:.1f}MB")
        print(f"Average Processing Latency: {avg_processing_latency:.1f}ms")
        print(f"Components Stable: {'✅ Yes' if components_stable else '❌ No'}")
        print(f"Hybrid Processing Stable: {'✅ Yes' if hybrid_stable else '❌ No'}")
        
        # Performance assessment
        print(f"\n📈 Performance Assessment:")
        if avg_search_latency < 500:
            print(f"   ✅ Search performance good (<500ms target)")
        else:
            print(f"   ⚠️ Search performance above target (>500ms)")
        
        if avg_processing_latency < 200:
            print(f"   ✅ Processing performance excellent (<200ms target)")
        elif avg_processing_latency < 500:
            print(f"   ✅ Processing performance good (<500ms tolerance)")
        else:
            print(f"   ⚠️ Processing performance needs attention (>500ms)")
        
        # Save monitoring data
        filename = f"production_monitoring_{int(time.time())}.json"
        with open(filename, "w") as f:
            json.dump(self.monitoring_data, f, indent=2)
        
        print(f"\n📋 Monitoring data saved to {filename}")
        
        return True

def main():
    """Run production monitoring"""
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    monitor = ProductionMonitor()
    monitor.run_monitoring_cycle(duration_minutes=duration)

if __name__ == "__main__":
    main()