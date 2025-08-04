#!/usr/bin/env python3
"""
Memory Usage Analysis for ChromaDB Sort Operations
Analyze memory consumption during retrieval and sorting
"""

import psutil
import os
import time
import gc
from typing import Dict, Any
from database.vector_database import ClaudeVectorDatabase

def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage in MB"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    return {
        'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size (physical memory)
        'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        'percent': process.memory_percent(),
        'available_mb': psutil.virtual_memory().available / 1024 / 1024,
        'total_mb': psutil.virtual_memory().total / 1024 / 1024,
        'used_mb': psutil.virtual_memory().used / 1024 / 1024
    }

def format_mb(mb: float) -> str:
    """Format MB to human readable"""
    if mb > 1024:
        return f"{mb/1024:.2f} GB"
    return f"{mb:.2f} MB"

def estimate_data_size(db_results: Dict[str, Any]) -> Dict[str, float]:
    """Estimate memory size of the retrieved data"""
    
    # Calculate approximate size of each component
    documents = db_results.get('documents', [])
    metadatas = db_results.get('metadatas', [])
    ids = db_results.get('ids', [])
    
    # Estimate document size (text content)
    doc_size_mb = 0
    if documents:
        total_chars = sum(len(doc) for doc in documents)
        doc_size_mb = (total_chars * 1) / 1024 / 1024  # ~1 byte per char
    
    # Estimate metadata size (JSON objects)
    metadata_size_mb = 0
    if metadatas:
        # Rough estimate: ~200 bytes per metadata object
        metadata_size_mb = (len(metadatas) * 200) / 1024 / 1024
    
    # Estimate ID size (strings)
    id_size_mb = 0
    if ids:
        total_id_chars = sum(len(str(id_)) for id_ in ids)
        id_size_mb = (total_id_chars * 1) / 1024 / 1024
    
    # Python object overhead (rough estimate)
    python_overhead_mb = len(documents) * 0.001  # ~1KB per Python object
    
    total_estimated_mb = doc_size_mb + metadata_size_mb + id_size_mb + python_overhead_mb
    
    return {
        'documents_mb': doc_size_mb,
        'metadata_mb': metadata_size_mb,
        'ids_mb': id_size_mb,
        'python_overhead_mb': python_overhead_mb,
        'total_estimated_mb': total_estimated_mb,
        'entry_count': len(documents) if documents else 0
    }

def memory_test_retrieval():
    """Test memory usage during retrieval operation"""
    print("=" * 60)
    print("MEMORY USAGE ANALYSIS - CHROMADB RETRIEVAL")
    print("=" * 60)
    
    # Get baseline memory
    print("📊 System Memory Overview:")
    baseline = get_memory_usage()
    print(f"   Total RAM: {format_mb(baseline['total_mb'])}")
    print(f"   Available: {format_mb(baseline['available_mb'])}")
    print(f"   Used: {format_mb(baseline['used_mb'])}")
    print(f"   Process baseline: {format_mb(baseline['rss_mb'])}")
    
    # Initialize database
    print("\n🔄 Initializing database...")
    init_memory = get_memory_usage()
    
    db = ClaudeVectorDatabase()
    post_init_memory = get_memory_usage()
    init_increase = post_init_memory['rss_mb'] - init_memory['rss_mb']
    print(f"   Database initialization: +{format_mb(init_increase)}")
    
    # Force garbage collection for clean baseline
    gc.collect()
    pre_retrieval_memory = get_memory_usage()
    print(f"   Pre-retrieval memory: {format_mb(pre_retrieval_memory['rss_mb'])}")
    
    # Retrieve all data
    print("\n📥 Retrieving all entries...")
    start_time = time.time()
    
    all_results = db.collection.get(include=["documents", "metadatas"])
    
    post_retrieval_memory = get_memory_usage()
    retrieval_time = time.time() - start_time
    
    # Calculate memory increase
    memory_increase = post_retrieval_memory['rss_mb'] - pre_retrieval_memory['rss_mb']
    
    print(f"   ✅ Retrieved {len(all_results['documents']):,} entries in {retrieval_time:.2f}s")
    print(f"   📈 Memory increase: +{format_mb(memory_increase)}")
    print(f"   💾 Total process memory: {format_mb(post_retrieval_memory['rss_mb'])}")
    
    # Estimate data size
    data_estimate = estimate_data_size(all_results)
    print("\n📏 Estimated Data Breakdown:")
    print(f"   Documents: {format_mb(data_estimate['documents_mb'])}")
    print(f"   Metadata: {format_mb(data_estimate['metadata_mb'])}")
    print(f"   IDs: {format_mb(data_estimate['ids_mb'])}")
    print(f"   Python overhead: {format_mb(data_estimate['python_overhead_mb'])}")
    print(f"   Total estimated: {format_mb(data_estimate['total_estimated_mb'])}")
    print(f"   Actual increase: {format_mb(memory_increase)}")
    print(f"   Efficiency ratio: {(data_estimate['total_estimated_mb'] / memory_increase * 100):.1f}%")
    
    return all_results, post_retrieval_memory

def memory_test_sorting(all_results, pre_sort_memory):
    """Test memory usage during sorting operation"""
    print("\n" + "=" * 60)
    print("MEMORY USAGE ANALYSIS - SORTING OPERATION")
    print("=" * 60)
    
    print(f"📊 Pre-sort memory: {format_mb(pre_sort_memory['rss_mb'])}")
    
    # Prepare data for sorting
    print("🔄 Preparing data for sorting...")
    prep_start = time.time()
    
    combined = list(zip(
        all_results['documents'],
        all_results['metadatas'], 
        all_results['ids']
    ))
    
    post_prep_memory = get_memory_usage()
    prep_time = time.time() - prep_start
    prep_increase = post_prep_memory['rss_mb'] - pre_sort_memory['rss_mb']
    
    print(f"   ⏱️  Preparation time: {prep_time*1000:.2f}ms")
    print(f"   📈 Memory increase: +{format_mb(prep_increase)}")
    
    # Sort the data
    print("🔄 Sorting by timestamp_unix...")
    sort_start = time.time()
    
    sorted_results = sorted(
        combined,
        key=lambda x: x[1].get('timestamp_unix', 0),
        reverse=True
    )
    
    post_sort_memory = get_memory_usage()
    sort_time = time.time() - sort_start
    sort_increase = post_sort_memory['rss_mb'] - post_prep_memory['rss_mb']
    
    print(f"   ⏱️  Sorting time: {sort_time*1000:.2f}ms")
    print(f"   📈 Memory increase: +{format_mb(sort_increase)}")
    print(f"   💾 Total process memory: {format_mb(post_sort_memory['rss_mb'])}")
    
    # Memory efficiency analysis
    entry_count = len(sorted_results)
    bytes_per_entry = (post_sort_memory['rss_mb'] * 1024 * 1024) / entry_count
    
    print("\n📊 Memory Efficiency:")
    print(f"   Entries processed: {entry_count:,}")
    print(f"   Memory per entry: {bytes_per_entry:.1f} bytes")
    print(f"   Peak memory usage: {format_mb(post_sort_memory['rss_mb'])}")
    
    return sorted_results, post_sort_memory

def memory_test_cleanup(peak_memory):
    """Test memory cleanup after operations"""
    print("\n" + "=" * 60)
    print("MEMORY CLEANUP ANALYSIS")
    print("=" * 60)
    
    print("🧹 Forcing garbage collection...")
    
    # Multiple garbage collection passes
    for i in range(3):
        collected = gc.collect()
        print(f"   GC pass {i+1}: collected {collected} objects")
    
    post_gc_memory = get_memory_usage()
    memory_freed = peak_memory['rss_mb'] - post_gc_memory['rss_mb']
    
    print("📊 Memory after cleanup:")
    print(f"   Peak memory: {format_mb(peak_memory['rss_mb'])}")
    print(f"   After cleanup: {format_mb(post_gc_memory['rss_mb'])}")
    print(f"   Memory freed: {format_mb(memory_freed)}")
    print(f"   Retention: {((post_gc_memory['rss_mb'] / peak_memory['rss_mb']) * 100):.1f}%")

def analyze_vm_impact():
    """Analyze impact on VM resources"""
    print("\n" + "=" * 60)
    print("VM RESOURCE IMPACT ANALYSIS")
    print("=" * 60)
    
    memory = get_memory_usage()
    
    print("🖥️  VM Memory Status:")
    print(f"   Total RAM: {format_mb(memory['total_mb'])}")
    print(f"   Used RAM: {format_mb(memory['used_mb'])} ({memory['used_mb']/memory['total_mb']*100:.1f}%)")
    print(f"   Available: {format_mb(memory['available_mb'])}")
    print(f"   Process usage: {format_mb(memory['rss_mb'])} ({memory['percent']:.1f}%)")
    
    # Safety margins
    safety_threshold = memory['total_mb'] * 0.8  # 80% threshold
    current_usage = memory['used_mb']
    
    print("\n⚠️  Safety Analysis:")
    print(f"   80% threshold: {format_mb(safety_threshold)}")
    print(f"   Current usage: {format_mb(current_usage)}")
    
    if current_usage < safety_threshold:
        headroom = safety_threshold - current_usage
        print(f"   ✅ Safe headroom: {format_mb(headroom)}")
    else:
        print("   ⚠️  Above safe threshold!")
    
    # Projections for larger datasets
    current_entries = 17642
    current_process_mb = memory['rss_mb']
    
    print(f"\n📊 Scaling Projections (current: {current_entries:,} entries, {format_mb(current_process_mb)}):")
    
    for scale in [25000, 50000, 100000]:
        projected_mb = current_process_mb * (scale / current_entries)
        projected_total_used = (memory['used_mb'] - current_process_mb) + projected_mb
        
        if projected_total_used < safety_threshold:
            status = "✅ Safe"
        elif projected_total_used < memory['total_mb']:
            status = "⚠️  Caution"
        else:
            status = "❌ Risk"
        
        print(f"   {scale:,} entries: {format_mb(projected_mb)} process, {format_mb(projected_total_used)} total {status}")

def run_memory_analysis():
    """Run complete memory analysis"""
    print("🔬 Starting ChromaDB Memory Usage Analysis")
    
    # Test retrieval memory usage
    all_results, post_retrieval_memory = memory_test_retrieval()
    
    # Test sorting memory usage
    sorted_results, peak_memory = memory_test_sorting(all_results, post_retrieval_memory)
    
    # Test cleanup
    memory_test_cleanup(peak_memory)
    
    # Analyze VM impact
    analyze_vm_impact()
    
    print("\n" + "=" * 60)
    print("MEMORY ANALYSIS COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    try:
        run_memory_analysis()
    except Exception as e:
        print(f"❌ Memory analysis failed: {e}")
        import traceback
        traceback.print_exc()