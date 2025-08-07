#!/usr/bin/env python3
"""
Database Rebuild Verification Script

Verifies the success of the complete database rebuild implementation,
checking all requirements from the Complete Implementation Reference.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Get package root directory (2 levels up from tests/integration/)
PACKAGE_ROOT = Path(__file__).parent.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from database.vector_database import ClaudeVectorDatabase
from system.central_logging import VectorDatabaseLogger


def count_jsonl_entries() -> int:
    """Count total entries in all JSONL source files."""
    claude_projects_dir = Path("/home/user/.claude/projects")
    jsonl_files = list(claude_projects_dir.glob("*.jsonl"))
    
    total_entries = 0
    for file_path in jsonl_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            json.loads(line)
                            total_entries += 1
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue
    
    return total_entries


def verify_database_rebuild() -> Dict[str, Any]:
    """
    Comprehensive verification of database rebuild following the Complete Implementation Reference.
    
    Success Criteria Checklist:
    - Entry Count: Database contains ~56,789 entries (±100)
    - Field Count: Each entry has 30+ metadata fields
    - Conversation Chains: >90% of entries have valid previous_message_id
    - Topic Detection: >70% of entries have detected_topics populated
    - Solution Quality: >95% of entries have solution_quality_score
    - No Duplicates: Zero duplicate content_hash values
    - Processing Logs: All sessions processed without errors
    - Performance: Search responses <500ms
    - Back-fill: All 5 chain fields populated via automatic backfill
    """
    
    logger = VectorDatabaseLogger("database_verification")
    logger.log_processing_start("comprehensive_database_verification")
    
    results = {
        "verification_timestamp": datetime.now().isoformat(),
        "success_criteria": {},
        "detailed_analysis": {},
        "overall_success": False,
        "recommendations": []
    }
    
    try:
        # Initialize database
        print("🔍 Initializing database connection...")
        db = ClaudeVectorDatabase()
        
        # Verification 1: Entry Count
        print("\n📊 Verification 1: Entry Count Analysis")
        print("=" * 50)
        
        database_count = db.collection.count()
        jsonl_count = count_jsonl_entries()
        
        entry_count_success = abs(database_count - jsonl_count) <= 100
        entry_count_ratio = (database_count / jsonl_count * 100) if jsonl_count > 0 else 0
        
        results["success_criteria"]["entry_count"] = {
            "database_entries": database_count,
            "jsonl_source_entries": jsonl_count,
            "difference": abs(database_count - jsonl_count),
            "ratio_percent": entry_count_ratio,
            "success": entry_count_success,
            "target": "±100 entries from JSONL source"
        }
        
        print(f"Database entries: {database_count:,}")
        print(f"JSONL source entries: {jsonl_count:,}")
        print(f"Difference: {abs(database_count - jsonl_count):,}")
        print(f"Success: {'✅' if entry_count_success else '❌'}")
        
        # Verification 2: Metadata Field Coverage
        print("\n🏷️ Verification 2: Metadata Field Coverage")
        print("=" * 50)
        
        sample_data = db.collection.get(limit=1000, include=["metadatas"])
        field_analysis = {"total_fields": 0, "enhanced_fields": 0, "entries_analyzed": 0}
        
        basic_fields = {'type', 'project_path', 'project_name', 'timestamp', 'session_id', 
                       'file_name', 'has_code', 'tools_used', 'content_length', 'content_hash', 'timestamp_unix'}
        
        if sample_data['metadatas']:
            field_counts = {}
            entries_with_30_plus_fields = 0
            
            for metadata in sample_data['metadatas']:
                if metadata:
                    field_analysis["entries_analyzed"] += 1
                    field_count = len(metadata)
                    
                    if field_count >= 30:
                        entries_with_30_plus_fields += 1
                    
                    for field_name in metadata.keys():
                        field_counts[field_name] = field_counts.get(field_name, 0) + 1
            
            field_analysis["total_fields"] = len(field_counts)
            field_analysis["enhanced_fields"] = len(field_counts) - len(basic_fields)
            field_analysis["entries_with_30_plus_fields"] = entries_with_30_plus_fields
            field_analysis["percentage_30_plus"] = (entries_with_30_plus_fields / field_analysis["entries_analyzed"] * 100) if field_analysis["entries_analyzed"] > 0 else 0
            
            field_coverage_success = field_analysis["total_fields"] >= 30 and field_analysis["percentage_30_plus"] >= 95
            
            results["success_criteria"]["field_coverage"] = {
                "total_unique_fields": field_analysis["total_fields"],
                "enhanced_fields": field_analysis["enhanced_fields"],
                "entries_with_30_plus_fields": entries_with_30_plus_fields,
                "percentage_30_plus": field_analysis["percentage_30_plus"],
                "success": field_coverage_success,
                "target": "30+ fields per entry, 95%+ coverage"
            }
            
            results["detailed_analysis"]["field_list"] = list(field_counts.keys())
            results["detailed_analysis"]["field_population"] = field_counts
        
        print(f"Total unique fields found: {field_analysis['total_fields']}")
        print(f"Enhanced fields (beyond basic): {field_analysis['enhanced_fields']}")
        print(f"Entries with 30+ fields: {entries_with_30_plus_fields:,} ({field_analysis['percentage_30_plus']:.1f}%)")
        print(f"Success: {'✅' if field_coverage_success else '❌'}")
        
        # Verification 3: Conversation Chain Coverage
        print("\n🔗 Verification 3: Conversation Chain Coverage")
        print("=" * 50)
        
        chain_fields = ['previous_message_id', 'next_message_id', 'message_sequence_position', 
                       'related_solution_id', 'feedback_message_id']
        
        chain_analysis = {}
        for field in chain_fields:
            populated_count = 0
            for metadata in sample_data['metadatas']:
                if metadata and metadata.get(field) and metadata[field] != '':
                    populated_count += 1
            
            percentage = (populated_count / field_analysis["entries_analyzed"] * 100) if field_analysis["entries_analyzed"] > 0 else 0
            chain_analysis[field] = {
                "populated_count": populated_count,
                "percentage": percentage
            }
            print(f"{field}: {populated_count:,} ({percentage:.1f}%)")
        
        # Focus on previous_message_id as the key indicator
        primary_chain_coverage = chain_analysis.get('previous_message_id', {}).get('percentage', 0)
        chain_success = primary_chain_coverage >= 90
        
        results["success_criteria"]["conversation_chains"] = {
            "primary_field_coverage": primary_chain_coverage,
            "all_field_analysis": chain_analysis,
            "success": chain_success,
            "target": ">90% previous_message_id coverage"
        }
        
        print(f"Primary chain coverage: {primary_chain_coverage:.1f}%")
        print(f"Success: {'✅' if chain_success else '❌'}")
        
        # Verification 4: Enhanced Metadata Population
        print("\n🧠 Verification 4: Enhanced Metadata Population")
        print("=" * 50)
        
        enhanced_fields_analysis = {
            'detected_topics': 0,
            'solution_quality_score': 0,
            'is_solution_attempt': 0,
            'user_feedback_sentiment': 0,
            'primary_topic': 0
        }
        
        for metadata in sample_data['metadatas']:
            if metadata:
                for field in enhanced_fields_analysis.keys():
                    if metadata.get(field) and metadata[field] not in ['', '{}', 0]:
                        enhanced_fields_analysis[field] += 1
        
        enhanced_percentages = {
            field: (count / field_analysis["entries_analyzed"] * 100) if field_analysis["entries_analyzed"] > 0 else 0
            for field, count in enhanced_fields_analysis.items()
        }
        
        # Key thresholds
        topic_success = enhanced_percentages['detected_topics'] >= 70
        solution_quality_success = enhanced_percentages['solution_quality_score'] >= 95
        
        results["success_criteria"]["enhanced_metadata"] = {
            "topic_detection_percentage": enhanced_percentages['detected_topics'],
            "solution_quality_percentage": enhanced_percentages['solution_quality_score'],
            "field_percentages": enhanced_percentages,
            "topic_success": topic_success,
            "solution_quality_success": solution_quality_success,
            "target_topic": ">70% topic detection",
            "target_solution": ">95% solution quality"
        }
        
        for field, percentage in enhanced_percentages.items():
            print(f"{field}: {enhanced_fields_analysis[field]:,} ({percentage:.1f}%)")
        
        print(f"Topic detection success: {'✅' if topic_success else '❌'}")
        print(f"Solution quality success: {'✅' if solution_quality_success else '❌'}")
        
        # Verification 5: Duplicate Check
        print("\n🔍 Verification 5: Duplicate Detection")
        print("=" * 50)
        
        content_hashes = []
        for metadata in sample_data['metadatas']:
            if metadata and metadata.get('content_hash'):
                content_hashes.append(metadata['content_hash'])
        
        unique_hashes = len(set(content_hashes))
        total_hashes = len(content_hashes)
        duplicate_count = total_hashes - unique_hashes
        
        no_duplicates_success = duplicate_count == 0
        
        results["success_criteria"]["no_duplicates"] = {
            "total_entries_checked": total_hashes,
            "unique_hashes": unique_hashes,
            "duplicate_count": duplicate_count,
            "success": no_duplicates_success,
            "target": "Zero duplicates"
        }
        
        print(f"Total entries checked: {total_hashes:,}")
        print(f"Unique content hashes: {unique_hashes:,}")
        print(f"Duplicates found: {duplicate_count}")
        print(f"Success: {'✅' if no_duplicates_success else '❌'}")
        
        # Verification 6: Search Performance Test
        print("\n⚡ Verification 6: Search Performance")
        print("=" * 50)
        
        test_queries = [
            "React component optimization",
            "TypeScript interface error",
            "vector database search",
            "performance improvement",
            "git commit message"
        ]
        
        search_times = []
        search_errors = 0
        
        for query in test_queries:
            try:
                import time
                start_time = time.time()
                search_results = db.search_conversations(query, n_results=5)
                end_time = time.time()
                
                search_time_ms = (end_time - start_time) * 1000
                search_times.append(search_time_ms)
                
                print(f"'{query}': {search_time_ms:.1f}ms ({len(search_results)} results)")
                
            except Exception as e:
                search_errors += 1
                print(f"'{query}': ERROR - {e}")
        
        avg_search_time = sum(search_times) / len(search_times) if search_times else float('inf')
        performance_success = avg_search_time < 500 and search_errors == 0
        
        results["success_criteria"]["search_performance"] = {
            "average_search_time_ms": avg_search_time,
            "max_search_time_ms": max(search_times) if search_times else 0,
            "search_errors": search_errors,
            "success": performance_success,
            "target": "<500ms average response time"
        }
        
        print(f"Average search time: {avg_search_time:.1f}ms")
        print(f"Search errors: {search_errors}")
        print(f"Success: {'✅' if performance_success else '❌'}")
        
        # Overall Success Determination
        all_criteria = [
            entry_count_success,
            field_coverage_success,
            chain_success,
            topic_success,
            solution_quality_success,
            no_duplicates_success,
            performance_success
        ]
        
        overall_success = all(all_criteria)
        success_count = sum(all_criteria)
        
        results["overall_success"] = overall_success
        results["success_summary"] = {
            "criteria_passed": success_count,
            "total_criteria": len(all_criteria),
            "success_percentage": (success_count / len(all_criteria) * 100)
        }
        
        # Generate Recommendations
        if not entry_count_success:
            results["recommendations"].append("Entry count mismatch: Check JSONL extraction and processing for errors")
        
        if not field_coverage_success:
            results["recommendations"].append("Insufficient metadata fields: Verify enhanced metadata storage is working")
        
        if not chain_success:
            results["recommendations"].append("Low conversation chain coverage: Run backfill_conversation_chains MCP tool")
        
        if not topic_success:
            results["recommendations"].append("Low topic detection: Check UnifiedEnhancementProcessor topic detection")
        
        if not solution_quality_success:
            results["recommendations"].append("Low solution quality scoring: Verify solution quality analysis")
        
        if not no_duplicates_success:
            results["recommendations"].append("Duplicates detected: Check content hash generation and deduplication")
        
        if not performance_success:
            results["recommendations"].append("Poor search performance: Check database optimization and indexing")
        
        logger.log_processing_complete("comprehensive_database_verification", 0, {
            "overall_success": overall_success,
            "criteria_passed": success_count,
            "total_criteria": len(all_criteria)
        })
        
    except Exception as e:
        logger.log_error("database_verification", e)
        results["error"] = str(e)
        results["overall_success"] = False
    
    return results


def main():
    """Main verification entry point."""
    
    print("🎯 DATABASE REBUILD VERIFICATION")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Following Complete Implementation Reference success criteria")
    print()
    
    # Run verification
    results = verify_database_rebuild()
    
    # Print final results
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION COMPLETE")
    print("=" * 60)
    
    if results["overall_success"]:
        print("✅ DATABASE REBUILD SUCCESSFUL!")
        print(f"All {results['success_summary']['criteria_passed']}/{results['success_summary']['total_criteria']} criteria passed")
    else:
        print("❌ DATABASE REBUILD NEEDS ATTENTION")
        print(f"Passed {results['success_summary']['criteria_passed']}/{results['success_summary']['total_criteria']} criteria ({results['success_summary']['success_percentage']:.1f}%)")
        
        if results.get("recommendations"):
            print("\n🔧 RECOMMENDATIONS:")
            for i, rec in enumerate(results["recommendations"], 1):
                print(f"  {i}. {rec}")
    
    if results.get("error"):
        print(f"\n❌ Verification Error: {results['error']}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Detailed results saved to: {Path.cwd()}/verification_results.json")
    
    # Save detailed results
    with open("verification_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    return 0 if results["overall_success"] else 1


if __name__ == "__main__":
    sys.exit(main())