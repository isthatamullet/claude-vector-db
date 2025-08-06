#!/usr/bin/env python3
"""
Analyze metadata field population in the chroma_db_backup_corrupt database.

This script queries the corrupted backup database to determine which enhanced
metadata fields are actually populated, providing insight into the storage
layer behavior before the force sync failure.
"""

import chromadb
from chromadb.config import Settings
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, Any, List

def analyze_backup_database():
    """Analyze metadata field population in the backup corrupt database."""
    
    backup_db_path = Path("/home/user/.claude-vector-db-enhanced/chroma_db_backup_corrupt")
    
    if not backup_db_path.exists():
        print(f"❌ Backup database not found at {backup_db_path}")
        return
    
    print(f"🔍 Analyzing backup database at: {backup_db_path}")
    print("=" * 60)
    
    try:
        # Initialize ChromaDB client for backup database
        client = chromadb.PersistentClient(
            path=str(backup_db_path),
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
        print(f"📊 Total entries in backup database: {total_count:,}")
        
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
        print(f"❌ Error analyzing backup database: {e}")
        import traceback
        traceback.print_exc()

def analyze_field_population(metadatas: List[Dict], sample_size: int, total_count: int):
    """Analyze field population statistics from metadata records."""
    
    print("📈 FIELD POPULATION ANALYSIS")
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
    
    # Categorize fields
    basic_fields = [
        'id', 'type', 'content', 'project_path', 'project_name', 'timestamp',
        'session_id', 'file_name', 'has_code', 'tools_used', 'content_length',
        'content_hash', 'timestamp_unix'
    ]
    
    enhanced_fields = [
        'detected_topics', 'primary_topic', 'topic_confidence',
        'solution_quality_score', 'has_success_markers', 'has_quality_indicators',
        'previous_message_id', 'next_message_id', 'message_sequence_position',
        'user_feedback_sentiment', 'is_validated_solution', 'is_refuted_attempt',
        'validation_strength', 'outcome_certainty', 'is_solution_attempt',
        'is_feedback_to_solution', 'related_solution_id', 'feedback_message_id',
        'solution_category', 'troubleshooting_context_score', 'realtime_learning_boost'
    ]
    
    semantic_fields = [
        'semantic_sentiment', 'semantic_confidence', 'semantic_method',
        'positive_similarity', 'negative_similarity', 'partial_similarity',
        'technical_domain', 'technical_confidence', 'complex_outcome_detected',
        'pattern_vs_semantic_agreement', 'primary_analysis_method',
        'requires_manual_review', 'best_matching_patterns', 'semantic_analysis_details'
    ]
    
    # Display results by category
    print("\n🔷 BASIC FIELDS (Expected in all systems)")
    print("-" * 40)
    display_field_category(sorted_fields, basic_fields, sample_size)
    
    print("\n🔶 ENHANCED FIELDS (Main enhancement system)")
    print("-" * 40)
    display_field_category(sorted_fields, enhanced_fields, sample_size)
    
    print("\n🔸 SEMANTIC VALIDATION FIELDS (Advanced analysis)")
    print("-" * 40)
    display_field_category(sorted_fields, semantic_fields, sample_size)
    
    print("\n🔹 OTHER FIELDS (Unexpected or additional)")
    print("-" * 40)
    all_known_fields = set(basic_fields + enhanced_fields + semantic_fields)
    other_fields = [f for f in sorted_fields if f[0] not in all_known_fields]
    if other_fields:
        display_field_category(other_fields, [f[0] for f in other_fields], sample_size)
    else:
        print("   No additional fields found")
    
    # Summary statistics
    print(f"\n📊 SUMMARY STATISTICS")
    print("=" * 60)
    
    total_fields = len(field_stats)
    basic_present = sum(1 for f in basic_fields if f in field_stats)
    enhanced_present = sum(1 for f in enhanced_fields if f in field_stats)
    semantic_present = sum(1 for f in semantic_fields if f in field_stats)
    
    print(f"Total unique fields found: {total_fields}")
    print(f"Basic fields present: {basic_present}/{len(basic_fields)} ({basic_present/len(basic_fields)*100:.1f}%)")
    print(f"Enhanced fields present: {enhanced_present}/{len(enhanced_fields)} ({enhanced_present/len(enhanced_fields)*100:.1f}%)")
    print(f"Semantic validation fields present: {semantic_present}/{len(semantic_fields)} ({semantic_present/len(semantic_fields)*100:.1f}%)")
    
    # Calculate meaningful data percentage
    meaningful_enhanced = sum(1 for f in enhanced_fields if f in field_stats and field_stats[f]['non_empty_count'] > 0)
    meaningful_semantic = sum(1 for f in semantic_fields if f in field_stats and field_stats[f]['non_empty_count'] > 0)
    
    print(f"\nMeaningful enhanced fields: {meaningful_enhanced}/{len(enhanced_fields)} ({meaningful_enhanced/len(enhanced_fields)*100:.1f}%)")
    print(f"Meaningful semantic fields: {meaningful_semantic}/{len(semantic_fields)} ({meaningful_semantic/len(semantic_fields)*100:.1f}%)")
    
    # Extrapolation to full database
    print(f"\n🔮 EXTRAPOLATION TO FULL DATABASE ({total_count:,} entries)")
    print("-" * 40)
    print(f"Sample represents {sample_size/total_count*100:.1f}% of total database")
    if enhanced_present > 0:
        print(f"✅ Enhanced metadata IS present in backup database!")
        print(f"   - {enhanced_present} enhanced field types found")
        print(f"   - {meaningful_enhanced} contain meaningful data")
    else:
        print(f"❌ No enhanced metadata fields found in backup database")

def display_field_category(sorted_fields: List, category_fields: List[str], sample_size: int):
    """Display field statistics for a specific category."""
    
    category_found = [(name, stats) for name, stats in sorted_fields if name in category_fields]
    
    if not category_found:
        print("   No fields from this category found")
        return
    
    for field_name, stats in category_found:
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
    print("🔍 BACKUP DATABASE METADATA ANALYSIS")
    print("=" * 60)
    print("Analyzing enhanced metadata field population in chroma_db_backup_corrupt")
    print()
    
    analyze_backup_database()
    
    print("\n" + "=" * 60)
    print("✅ Analysis complete!")