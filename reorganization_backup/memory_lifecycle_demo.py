#!/usr/bin/env python3
"""
Python Memory Lifecycle and Garbage Collection Demo
Show how Python manages memory during heavy operations
"""

import gc
import psutil
import os
import time
import weakref
from typing import Dict, Any

def get_memory_mb() -> float:
    """Get current process memory in MB"""
    return psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

def get_gc_stats() -> Dict[str, Any]:
    """Get garbage collection statistics"""
    return {
        'collections': gc.get_stats(),
        'counts': gc.get_count(),
        'threshold': gc.get_threshold()
    }

class MemoryDemo:
    """Demo class to show memory lifecycle"""
    
    def __init__(self, data_size: int):
        self.data = [f"Large data chunk {i} " * 100 for i in range(data_size)]
        self.metadata = {"size": data_size, "created": time.time()}
    
    def __del__(self):
        print(f"  🗑️  MemoryDemo object with {len(self.data)} items deleted")

def demo_memory_allocation_and_release():
    """Demonstrate how Python allocates and releases memory"""
    print("=" * 70)
    print("PYTHON MEMORY ALLOCATION & RELEASE DEMO")
    print("=" * 70)
    
    baseline_memory = get_memory_mb()
    print(f"📊 Baseline memory: {baseline_memory:.2f} MB")
    
    # Create large objects in different scopes
    print("\n🔄 Creating large objects...")
    objects = []
    
    for i in range(5):
        print(f"   Creating object {i+1}...")
        obj = MemoryDemo(1000)  # ~100KB per object
        objects.append(obj)
        current_memory = get_memory_mb()
        increase = current_memory - baseline_memory
        print(f"   Memory: {current_memory:.2f} MB (+{increase:.2f} MB)")
    
    peak_memory = get_memory_mb()
    print(f"\n📈 Peak memory with objects: {peak_memory:.2f} MB")
    
    # Clear references
    print("\n🧹 Clearing object references...")
    objects.clear()  # Remove references
    
    after_clear_memory = get_memory_mb()
    print(f"💾 Memory after clearing references: {after_clear_memory:.2f} MB")
    
    # Force garbage collection
    print("\n🗑️  Forcing garbage collection...")
    collected = gc.collect()
    after_gc_memory = get_memory_mb()
    
    print(f"   Collected {collected} objects")
    print(f"💾 Memory after GC: {after_gc_memory:.2f} MB")
    
    # Show memory recovery
    memory_recovered = peak_memory - after_gc_memory
    recovery_rate = (memory_recovered / (peak_memory - baseline_memory)) * 100
    
    print("\n📊 Memory Recovery Analysis:")
    print(f"   Peak usage: +{peak_memory - baseline_memory:.2f} MB")
    print(f"   Recovered: {memory_recovered:.2f} MB")
    print(f"   Recovery rate: {recovery_rate:.1f}%")
    
    return baseline_memory, peak_memory, after_gc_memory

def demo_reference_cycles():
    """Show how Python handles reference cycles"""
    print("\n" + "=" * 70)
    print("REFERENCE CYCLES & CIRCULAR REFERENCES DEMO")
    print("=" * 70)
    
    class CircularRef:
        def __init__(self, name: str):
            self.name = name
            self.refs = []
        
        def add_ref(self, other):
            self.refs.append(other)
            other.refs.append(self)  # Circular reference!
        
        def __del__(self):
            print(f"  🗑️  CircularRef '{self.name}' deleted")
    
    baseline = get_memory_mb()
    print(f"📊 Baseline: {baseline:.2f} MB")
    
    # Create circular references
    print("\n🔄 Creating circular references...")
    obj1 = CircularRef("Object1")
    obj2 = CircularRef("Object2")
    obj1.add_ref(obj2)  # They now reference each other
    
    # Create weak reference to track deletion
    weak_ref1 = weakref.ref(obj1)
    weak_ref2 = weakref.ref(obj2)
    
    after_creation = get_memory_mb()
    print(f"💾 After creation: {after_creation:.2f} MB")
    
    # Clear our references
    print("\n🧹 Clearing our references (but circular refs remain)...")
    del obj1, obj2
    
    after_del = get_memory_mb()
    print(f"💾 After del: {after_del:.2f} MB")
    print(f"   Object1 still exists: {weak_ref1() is not None}")
    print(f"   Object2 still exists: {weak_ref2() is not None}")
    
    # Force garbage collection to break cycles
    print("\n🗑️  Running cyclic garbage collection...")
    collected = gc.collect()
    
    after_gc = get_memory_mb()
    print(f"   Collected {collected} objects")
    print(f"💾 After GC: {after_gc:.2f} MB")
    print(f"   Object1 still exists: {weak_ref1() is not None}")
    print(f"   Object2 still exists: {weak_ref2() is not None}")

def demo_mcp_simulation():
    """Simulate heavy MCP usage patterns"""
    print("\n" + "=" * 70)
    print("HEAVY MCP USAGE SIMULATION")
    print("=" * 70)
    
    baseline = get_memory_mb()
    print(f"📊 Starting memory: {baseline:.2f} MB")
    
    # Simulate multiple MCP calls
    memory_history = []
    
    for call_num in range(10):
        print(f"\n🔄 MCP Call #{call_num + 1}: Simulating database query...")
        
        # Simulate retrieving and processing data (like ChromaDB query)
        fake_results = {
            'documents': [f"Document {i} with lots of content " * 50 for i in range(1000)],
            'metadatas': [{'timestamp': time.time() + i, 'type': 'assistant'} for i in range(1000)],
            'ids': [f"id_{call_num}_{i}" for i in range(1000)]
        }
        
        # Simulate processing (like sorting)
        combined = list(zip(fake_results['documents'], fake_results['metadatas'], fake_results['ids']))
        sorted_results = sorted(combined, key=lambda x: x[1]['timestamp'], reverse=True)
        
        # Get top 5 (simulate typical MCP response)
        top_results = sorted_results[:5]
        
        current_memory = get_memory_mb()
        increase = current_memory - baseline
        memory_history.append(current_memory)
        
        print(f"   💾 Memory: {current_memory:.2f} MB (+{increase:.2f} MB)")
        
        # Simulate end of MCP call - variables go out of scope
        del fake_results, combined, sorted_results, top_results
        
        # Periodic garbage collection (Python does this automatically)
        if call_num % 3 == 2:  # Every 3rd call
            print("   🗑️  Automatic garbage collection...")
            collected = gc.collect()
            gc_memory = get_memory_mb()
            print(f"      Collected {collected} objects, memory: {gc_memory:.2f} MB")
            memory_history[-1] = gc_memory
    
    final_memory = get_memory_mb()
    print("\n📊 Memory Usage Pattern:")
    print(f"   Starting: {baseline:.2f} MB")
    print(f"   Peak during calls: {max(memory_history):.2f} MB")
    print(f"   Final: {final_memory:.2f} MB")
    
    # Show memory growth over time
    print("\n📈 Memory Growth Analysis:")
    for i, mem in enumerate(memory_history):
        growth = mem - baseline
        print(f"   Call {i+1}: +{growth:.2f} MB")

def explain_gc_settings():
    """Explain Python's garbage collection settings"""
    print("\n" + "=" * 70)
    print("PYTHON GARBAGE COLLECTION EXPLAINED")
    print("=" * 70)
    
    stats = get_gc_stats()
    
    print("🗑️  Garbage Collection Configuration:")
    print(f"   Thresholds: {stats['threshold']}")
    print("   - Generation 0: Young objects (created recently)")
    print("   - Generation 1: Objects that survived one GC cycle")  
    print("   - Generation 2: Long-lived objects")
    
    print(f"\n📊 Current GC Counts: {stats['counts']}")
    print("   - Shows how many objects in each generation")
    
    print("\n📈 GC Statistics:")
    for i, gen_stats in enumerate(stats['collections']):
        print(f"   Generation {i}:")
        print(f"     Collections: {gen_stats['collections']}")
        print(f"     Collected: {gen_stats['collected']}")
        print(f"     Uncollectable: {gen_stats['uncollectable']}")
    
    print("\n⚙️  How Python GC Works:")
    print("   1. Reference counting: Objects deleted when no references")
    print("   2. Cyclic GC: Breaks circular references periodically")
    print("   3. Generational: Focus on young objects (most likely garbage)")
    print("   4. Automatic: Runs based on allocation thresholds")

def memory_management_best_practices():
    """Show best practices for memory management"""
    print("\n" + "=" * 70)
    print("MEMORY MANAGEMENT BEST PRACTICES")
    print("=" * 70)
    
    print("✅ Good Practices:")
    print("   1. Let variables go out of scope naturally")
    print("   2. Use 'del' for large objects when done")
    print("   3. Avoid circular references when possible")
    print("   4. Use context managers (with statements)")
    print("   5. Don't manually call gc.collect() unless debugging")
    
    print("\n❌ Things to Avoid:")
    print("   1. Keeping references to large objects unnecessarily")
    print("   2. Creating circular references without cleanup")
    print("   3. Disabling garbage collection")
    print("   4. Assuming manual GC is faster than automatic")
    
    print("\n🎯 For MCP Usage:")
    print("   1. MCP calls are naturally scoped - memory cleans up")
    print("   2. Python handles most memory management automatically")
    print("   3. Your VM has plenty of headroom for normal usage")
    print("   4. Memory leaks are rare in typical Python code")

def run_memory_lifecycle_demo():
    """Run complete memory lifecycle demonstration"""
    print("🧠 Python Memory Management & Garbage Collection Demo")
    print("Understanding how Python handles memory during heavy MCP usage\n")
    
    # Demo 1: Basic allocation and release
    demo_memory_allocation_and_release()
    
    # Demo 2: Reference cycles
    demo_reference_cycles()
    
    # Demo 3: Heavy MCP simulation
    demo_mcp_simulation()
    
    # Demo 4: Explain GC settings
    explain_gc_settings()
    
    # Demo 5: Best practices
    memory_management_best_practices()
    
    print("\n" + "=" * 70)
    print("MEMORY DEMO COMPLETE")
    print("=" * 70)
    print("🎯 Key Takeaway: Python's automatic memory management")
    print("   handles typical MCP usage very well. Your VM is safe!")

if __name__ == "__main__":
    try:
        run_memory_lifecycle_demo()
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()