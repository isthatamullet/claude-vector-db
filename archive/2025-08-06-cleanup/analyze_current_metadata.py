#!/usr/bin/env python3
"""
Analyze metadata field population in the current chroma_db database.

This script queries the current database to compare metadata field population
with the backup database, showing the impact of the force sync failure.
"""

import chromadb
from chromadb.config import Settings
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List

def analyze_current_database():
    """Analyze metadata field population in the current database."""
    
    current_db_path = Path("/home/user/.claude-vector-db-enhanced/chroma_db")
    
    if not current_db_path.exists():
        print(f"❌ Current database not found at {current_db_path}")
        return
    
    print(f"🔍 Analyzing current database at: {current_db_path}")
    print("=" * 60)
    
    try:
        # Initialize ChromaDB client for current database
        client = chromadb.PersistentClient(
            path=str(current_db_path),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get the collection
        try:
            collection = client.get_collection("claude_conversations")
            print(f"✅ Connected to collection: {collection.name}")
        except Exception as e:
            print(f"❌ Failed to get collection: {e}")
            return
        
        # Get total count
        total_count = collection.count()
        print(f"📊 Total entries in current database: {total_count:,}")
        
        if total_count == 0:
            print("⚠️ Database is empty")
            return
        
        # Sample a reasonable number of entries to analyze
        sample_size = min(1000, total_count)
        print(f"🔬 Analyzing sample of {sample_size:,} entries...")
        
        # Get sample data with metadata
        sample_data = collection.get(
            limit=sample_size,
            include=["metadatas"]
        )
        
        metadatas = sample_data.get('metadatas', [])
        if not metadatas:
            print("❌ No metadata found in sample")
            return
        
        print(f"✅ Retrieved {len(metadatas):,} metadata records")
        print("\n" + "=" * 60)
        
        # Analyze field population
        analyze_field_population(metadatas, sample_size, total_count)
        
    except Exception as e:
        print(f"❌ Error analyzing current database: {e}")
        import traceback
        traceback.print_exc()

def analyze_field_population(metadatas: List[Dict], sample_size: int, total_count: int):
    """Analyze field population statistics from metadata records."""
    
    print("📈 FIELD POPULATION ANALYSIS (CURRENT DATABASE)")
    print("=" * 60)
    
    # Count field occurrences and analyze values
    field_stats = defaultdict(lambda: {
        'count': 0,
        'non_empty_count': 0,
        'sample_values': [],
        'data_types': Counter()
    })
    
    # Process each metadata record
    for metadata in metadatas:
        if not isinstance(metadata, dict):
            continue
            
        for field_name, field_value in metadata.items():
            stats = field_stats[field_name]
            stats['count'] += 1
            
            # Check if value is non-empty/meaningful
            is_non_empty = is_meaningful_value(field_value)
            if is_non_empty:
                stats['non_empty_count'] += 1
                
                # Collect sample values (first 3)
                if len(stats['sample_values']) < 3:
                    stats['sample_values'].append(str(field_value)[:50])
            
            # Track data types
            stats['data_types'][type(field_value).__name__] += 1
    
    # Sort fields by presence
    sorted_fields = sorted(field_stats.items(), key=lambda x: x[1]['count'], reverse=True)
    
    # Display all fields found
    print("🔍 ALL FIELDS IN CURRENT DATABASE")
    print("-" * 40)
    
    for field_name, stats in sorted_fields:
        presence_pct = stats['count'] / sample_size * 100
        meaningful_pct = stats['non_empty_count'] / sample_size * 100 if stats['non_empty_count'] > 0 else 0
        
        # Status indicator
        if meaningful_pct > 80:
            status = "✅"
        elif meaningful_pct > 20:
            status = "🔶"  
        elif meaningful_pct > 0:
            status = "🔸"
        else:
            status = "❌"
        
        print(f"   {status} {field_name:<30} | Present: {presence_pct:5.1f}% | Meaningful: {meaningful_pct:5.1f}%")
        
        # Show sample values for interesting fields
        if stats['sample_values'] and meaningful_pct > 0:
            sample_str = ", ".join(stats['sample_values'][:2])
            print(f"      Sample values: {sample_str}")
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS (CURRENT DATABASE)")
    print("=" * 60)
    
    total_fields = len(field_stats)
    print(f"Total unique fields found: {total_fields}")
    
    # Check for specific field categories
    basic_fields = [
        'type', 'project_path', 'project_name', 'timestamp', 'session_id', 
        'file_name', 'has_code', 'tools_used', 'content_length', 'content_hash', 'timestamp_unix'
    ]
    
    enhanced_fields = [
        'detected_topics', 'primary_topic', 'topic_confidence',
        'solution_quality_score', 'has_success_markers', 'has_quality_indicators',
        'previous_message_id', 'next_message_id', 'message_sequence_position',
        'user_feedback_sentiment', 'is_validated_solution', 'is_refuted_attempt',
        'validation_strength', 'outcome_certainty', 'is_solution_attempt',
        'is_feedback_to_solution', 'related_solution_id', 'feedback_message_id',
        'solution_category'
    ]
    
    basic_present = sum(1 for f in basic_fields if f in field_stats)
    enhanced_present = sum(1 for f in enhanced_fields if f in field_stats)
    
    print(f"Basic fields present: {basic_present}/{len(basic_fields)} ({basic_present/len(basic_fields)*100:.1f}%)")
    print(f"Enhanced fields present: {enhanced_present}/{len(enhanced_fields)} ({enhanced_present/len(enhanced_fields)*100:.1f}%)")
    
    # Calculate meaningful data percentage
    meaningful_basic = sum(1 for f in basic_fields if f in field_stats and field_stats[f]['non_empty_count'] > 0)
    meaningful_enhanced = sum(1 for f in enhanced_fields if f in field_stats and field_stats[f]['non_empty_count'] > 0)
    
    print(f"Meaningful basic fields: {meaningful_basic}/{len(basic_fields)} ({meaningful_basic/len(basic_fields)*100:.1f}%)")
    print(f"Meaningful enhanced fields: {meaningful_enhanced}/{len(enhanced_fields)} ({meaningful_enhanced/len(enhanced_fields)*100:.1f}%)")

def is_meaningful_value(value) -> bool:
    """Determine if a field value is meaningful (not empty/default)."""
    
    if value is None:
        return False
    
    if isinstance(value, str):
        if value in ("", "unknown", "None", "null", "[]", "{}", "0", "0.0"):
            return False
        return len(value.strip()) > 0
    
    if isinstance(value, (int, float)):
        return value != 0
    
    if isinstance(value, bool):
        return True  # Both True and False are meaningful for booleans
    
    if isinstance(value, (list, dict)):
        return len(value) > 0
    
    return True

if __name__ == "__main__":
    print("🔍 CURRENT DATABASE METADATA ANALYSIS")
    print("=" * 60)
    print("Analyzing metadata field population in current chroma_db")
    print()
    
    analyze_current_database()
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")