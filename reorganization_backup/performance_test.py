#!/usr/bin/env python3
"""
ChromaDB Sort Performance Test
Test retrieval and sorting performance with real database
"""

import time
import logging
from typing import Dict, Any
from vector_database import ClaudeVectorDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_time(seconds: float) -> str:
    """Format seconds to human readable time"""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"

def test_database_info():
    """Get basic database information"""
    print("=" * 60)
    print("DATABASE INFORMATION")
    print("=" * 60)
    
    db = ClaudeVectorDatabase()
    
    # Get collection count
    total_count = db.collection.count()
    print(f"Total entries in database: {total_count:,}")
    
    # Get a sample entry to understand structure
    sample = db.collection.get(limit=1, include=["documents", "metadatas"])
    if sample['documents']:
        print(f"Sample metadata keys: {list(sample['metadatas'][0].keys())}")
        print(f"Has timestamp_unix: {'timestamp_unix' in sample['metadatas'][0]}")
    
    return db, total_count

def test_full_retrieval_performance(db: ClaudeVectorDatabase) -> Dict[str, Any]:
    """Test retrieving ALL entries from the database"""
    print("\n" + "=" * 60)
    print("FULL RETRIEVAL PERFORMANCE TEST")
    print("=" * 60)
    
    start_time = time.time()
    
    # Retrieve ALL entries with metadata
    print("Retrieving all entries...")
    all_results = db.collection.get(include=["documents", "metadatas"])
    
    retrieval_time = time.time() - start_time
    entry_count = len(all_results['documents'])
    
    print(f"✅ Retrieved {entry_count:,} entries")
    print(f"⏱️  Retrieval time: {format_time(retrieval_time)}")
    print(f"📊 Average per entry: {(retrieval_time/entry_count)*1000:.2f}ms")
    
    return {
        'entries_retrieved': entry_count,
        'retrieval_time': retrieval_time,
        'data': all_results
    }

def test_sorting_performance(retrieval_data: Dict[str, Any]) -> Dict[str, Any]:
    """Test sorting the retrieved data by timestamp_unix"""
    print("\n" + "=" * 60)
    print("SORTING PERFORMANCE TEST")
    print("=" * 60)
    
    all_results = retrieval_data['data']
    
    start_time = time.time()
    
    # Combine data for sorting
    print("Preparing data for sorting...")
    combined = list(zip(
        all_results['documents'],
        all_results['metadatas'], 
        all_results['ids']
    ))
    
    prep_time = time.time() - start_time
    print(f"⏱️  Data preparation time: {format_time(prep_time)}")
    
    # Sort by timestamp_unix (newest first)
    print("Sorting by timestamp_unix...")
    sort_start = time.time()
    
    sorted_results = sorted(
        combined,
        key=lambda x: x[1].get('timestamp_unix', 0),
        reverse=True
    )
    
    sort_time = time.time() - sort_start
    total_sort_time = time.time() - start_time
    
    print(f"✅ Sorted {len(sorted_results):,} entries")
    print(f"⏱️  Pure sorting time: {format_time(sort_time)}")
    print(f"⏱️  Total sorting operation: {format_time(total_sort_time)}")
    
    # Verify sorting worked
    if len(sorted_results) >= 2:
        first_timestamp = sorted_results[0][1].get('timestamp_unix', 0)
        second_timestamp = sorted_results[1][1].get('timestamp_unix', 0)
        print(f"🔍 First entry timestamp: {first_timestamp}")
        print(f"🔍 Second entry timestamp: {second_timestamp}")
        print(f"✅ Sorting correct: {first_timestamp >= second_timestamp}")
    
    return {
        'sort_time': sort_time,
        'total_time': total_sort_time,
        'prep_time': prep_time,
        'sorted_data': sorted_results
    }

def test_get_most_recent(db: ClaudeVectorDatabase, n_results: int = 5) -> Dict[str, Any]:
    """Test the complete 'get most recent' operation"""
    print("\n" + "=" * 60)
    print(f"GET MOST RECENT ({n_results}) - COMPLETE OPERATION")
    print("=" * 60)
    
    start_time = time.time()
    
    # Full operation: retrieve all + sort + slice
    all_results = db.collection.get(include=["documents", "metadatas"])
    
    combined = list(zip(
        all_results['documents'],
        all_results['metadatas'], 
        all_results['ids']
    ))
    
    sorted_results = sorted(
        combined,
        key=lambda x: x[1].get('timestamp_unix', 0),
        reverse=True
    )
    
    # Get most recent N
    most_recent = sorted_results[:n_results]
    
    total_time = time.time() - start_time
    
    print(f"✅ Retrieved {n_results} most recent entries")
    print(f"⏱️  Total operation time: {format_time(total_time)}")
    
    # Show the most recent entries
    print(f"\n📋 Most Recent {n_results} Entries:")
    for i, (doc, meta, doc_id) in enumerate(most_recent, 1):
        timestamp = meta.get('timestamp', 'Unknown')
        content_preview = doc[:80] + "..." if len(doc) > 80 else doc
        print(f"  {i}. {timestamp} - {content_preview}")
    
    return {
        'total_time': total_time,
        'entries_found': len(most_recent),
        'recent_entries': most_recent
    }

def test_filtered_performance(db: ClaudeVectorDatabase):
    """Test performance with metadata filters"""
    print("\n" + "=" * 60)
    print("FILTERED RETRIEVAL PERFORMANCE TEST")
    print("=" * 60)
    
    # Test with type filter (only assistant responses)
    print("Testing with type='assistant' filter...")
    start_time = time.time()
    
    filtered_results = db.collection.get(
        where={"type": {"$eq": "assistant"}},
        include=["documents", "metadatas"]
    )
    
    filter_time = time.time() - start_time
    filtered_count = len(filtered_results['documents'])
    
    print(f"✅ Retrieved {filtered_count:,} assistant entries")
    print(f"⏱️  Filtered retrieval time: {format_time(filter_time)}")
    
    if filtered_count > 0:
        # Sort the filtered results
        sort_start = time.time()
        
        combined = list(zip(
            filtered_results['documents'],
            filtered_results['metadatas'], 
            filtered_results['ids']
        ))
        
        sorted_filtered = sorted(
            combined,
            key=lambda x: x[1].get('timestamp_unix', 0),
            reverse=True
        )
        
        sort_time = time.time() - sort_start
        total_filtered_time = time.time() - start_time
        
        print(f"⏱️  Sorting filtered results: {format_time(sort_time)}")
        print(f"⏱️  Total filtered operation: {format_time(total_filtered_time)}")
        
        return {
            'filtered_count': filtered_count,
            'filter_time': filter_time,
            'sort_time': sort_time,
            'total_time': total_filtered_time
        }

def run_performance_tests():
    """Run all performance tests"""
    print("🚀 Starting ChromaDB Sort Performance Tests")
    print("=" * 60)
    
    # Test 1: Database Info
    db, total_count = test_database_info()
    
    # Test 2: Full Retrieval
    retrieval_results = test_full_retrieval_performance(db)
    
    # Test 3: Sorting Performance  
    sorting_results = test_sorting_performance(retrieval_results)
    
    # Test 4: Complete "Get Most Recent" Operation
    most_recent_results = test_get_most_recent(db, 10)
    
    # Test 5: Filtered Performance
    filtered_results = test_filtered_performance(db)
    
    # Summary
    print("\n" + "=" * 60)
    print("PERFORMANCE SUMMARY")
    print("=" * 60)
    
    print(f"Database entries: {total_count:,}")
    print(f"Full retrieval: {format_time(retrieval_results['retrieval_time'])}")
    print(f"Sorting operation: {format_time(sorting_results['total_time'])}")
    print(f"Get 10 most recent: {format_time(most_recent_results['total_time'])}")
    
    if filtered_results:
        print(f"Filtered retrieval + sort: {format_time(filtered_results['total_time'])}")
    
    # Performance analysis
    total_entries = retrieval_results['entries_retrieved']
    retrieval_per_entry = (retrieval_results['retrieval_time'] / total_entries) * 1000
    sorting_per_entry = (sorting_results['sort_time'] / total_entries) * 1000
    
    print("\nPer-entry performance:")
    print(f"  Retrieval: {retrieval_per_entry:.3f}ms per entry")
    print(f"  Sorting: {sorting_per_entry:.3f}ms per entry")
    
    # Scalability projection
    for scale in [50000, 100000]:
        projected_retrieval = (retrieval_per_entry * scale) / 1000
        projected_sorting = (sorting_per_entry * scale) / 1000
        projected_total = projected_retrieval + projected_sorting
        print(f"  Projected for {scale:,} entries: {format_time(projected_total)}")

if __name__ == "__main__":
    try:
        run_performance_tests()
    except Exception as e:
        logger.error(f"Performance test failed: {e}")
        import traceback
        traceback.print_exc()