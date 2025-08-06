#!/usr/bin/env python3
"""
Database Integrity Check Script
Complete Implementation Reference - Line 604

Performs comprehensive integrity verification of the vector database:
- Validates database consistency and structure
- Detects corruption or data anomalies
- Checks ChromaDB collection health
- Verifies metadata field consistency
- Identifies missing or malformed entries
"""

import sys
import os
import json
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add base path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.vector_database import ClaudeVectorDatabase
from system.central_logging import VectorDatabaseLogger

def check_collection_health(db: ClaudeVectorDatabase) -> Dict[str, Any]:
    """Check basic ChromaDB collection health"""
    print("🔍 Checking ChromaDB collection health...")
    
    try:
        # Basic collection checks
        collection_name = db.collection.name
        entry_count = db.collection.count()
        
        # Test basic operations
        test_query_success = True
        test_search_success = True
        
        try:
            # Test get operation
            sample = db.collection.get(limit=1, include=["metadatas", "documents"])
        except Exception as e:
            test_query_success = False
            print(f"  ❌ Get operation failed: {e}")
        
        try:
            # Test search operation
            if entry_count > 0:
                search_results = db.search_conversations("test query", n_results=1)
        except Exception as e:
            test_search_success = False
            print(f"  ❌ Search operation failed: {e}")
        
        result = {
            "collection_name": collection_name,
            "entry_count": entry_count,
            "test_query_success": test_query_success,
            "test_search_success": test_search_success,
            "health_score": sum([test_query_success, test_search_success]) / 2 * 100
        }
        
        print(f"  ✅ Collection: {collection_name}")
        print(f"  ✅ Entry count: {entry_count:,}")
        print(f"  ✅ Health score: {result['health_score']:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Collection health check failed: {e}")
        return {"error": str(e), "health_score": 0}

def check_metadata_consistency(db: ClaudeVectorDatabase) -> Dict[str, Any]:
    """Check metadata field consistency across entries"""
    print("📋 Checking metadata field consistency...")
    
    try:
        # Sample a representative set of entries
        sample_size = min(1000, db.collection.count())
        sample_data = db.collection.get(limit=sample_size, include=["metadatas"])
        
        if not sample_data or not sample_data.get('metadatas'):
            return {"error": "No metadata found", "consistency_score": 0}
        
        # Analyze field consistency
        field_counts = {}
        required_fields = {
            'id', 'type', 'project_path', 'project_name', 'timestamp',
            'session_id', 'file_name', 'has_code', 'content_length'
        }
        
        entries_analyzed = len(sample_data['metadatas'])
        missing_required_fields = {}
        malformed_entries = []
        
        for i, metadata in enumerate(sample_data['metadatas']):
            if not metadata:
                malformed_entries.append(f"entry_{i}")
                continue
            
            # Count field occurrence
            for field in metadata.keys():
                field_counts[field] = field_counts.get(field, 0) + 1
            
            # Check required fields
            for req_field in required_fields:
                if req_field not in metadata or metadata[req_field] is None:
                    if req_field not in missing_required_fields:
                        missing_required_fields[req_field] = 0
                    missing_required_fields[req_field] += 1
        
        # Calculate consistency metrics
        total_fields = len(field_counts)
        required_field_coverage = {}
        for field in required_fields:
            coverage = ((entries_analyzed - missing_required_fields.get(field, 0)) / entries_analyzed * 100) if entries_analyzed > 0 else 0
            required_field_coverage[field] = coverage
        
        avg_required_coverage = sum(required_field_coverage.values()) / len(required_field_coverage) if required_field_coverage else 0
        malformed_percentage = (len(malformed_entries) / entries_analyzed * 100) if entries_analyzed > 0 else 0
        
        consistency_score = max(0, avg_required_coverage - malformed_percentage)
        
        result = {
            "entries_analyzed": entries_analyzed,
            "total_fields_found": total_fields,
            "required_field_coverage": required_field_coverage,
            "missing_required_fields": missing_required_fields,
            "malformed_entries": len(malformed_entries),
            "malformed_percentage": malformed_percentage,
            "consistency_score": consistency_score,
            "field_counts": field_counts
        }
        
        print(f"  ✅ Entries analyzed: {entries_analyzed:,}")
        print(f"  ✅ Total fields found: {total_fields}")
        print(f"  ✅ Required field coverage: {avg_required_coverage:.1f}%")
        print(f"  ✅ Malformed entries: {len(malformed_entries)} ({malformed_percentage:.1f}%)")
        print(f"  ✅ Consistency score: {consistency_score:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Metadata consistency check failed: {e}")
        return {"error": str(e), "consistency_score": 0}

def check_data_integrity(db: ClaudeVectorDatabase) -> Dict[str, Any]:
    """Check for data corruption or anomalies"""
    print("🔍 Checking data integrity...")
    
    try:
        # Sample entries for integrity analysis
        sample_size = min(500, db.collection.count())
        sample_data = db.collection.get(limit=sample_size, include=["metadatas", "documents"])
        
        if not sample_data:
            return {"error": "No data found", "integrity_score": 0}
        
        integrity_issues = []
        entries_checked = len(sample_data.get('ids', []))
        
        metadatas = sample_data.get('metadatas', [])
        documents = sample_data.get('documents', [])
        ids = sample_data.get('ids', [])
        
        # Check for empty or null data
        empty_documents = sum(1 for doc in documents if not doc or doc.strip() == '')
        empty_metadatas = sum(1 for meta in metadatas if not meta)
        empty_ids = sum(1 for id_val in ids if not id_val)
        
        # Check for data type consistency
        timestamp_format_errors = 0
        numeric_field_errors = 0
        boolean_field_errors = 0
        
        for metadata in metadatas:
            if not metadata:
                continue
            
            # Check timestamp format
            timestamp = metadata.get('timestamp', '')
            if timestamp and not isinstance(timestamp, str):
                timestamp_format_errors += 1
            
            # Check numeric fields
            content_length = metadata.get('content_length')
            if content_length is not None and not isinstance(content_length, (int, float)):
                numeric_field_errors += 1
            
            # Check boolean fields
            has_code = metadata.get('has_code')
            if has_code is not None and not isinstance(has_code, bool):
                boolean_field_errors += 1
        
        # Check for duplicate IDs
        unique_ids = len(set(ids))
        duplicate_ids = entries_checked - unique_ids
        
        # Calculate integrity score
        total_possible_issues = entries_checked * 6  # 6 checks per entry
        total_issues = (empty_documents + empty_metadatas + empty_ids + 
                       timestamp_format_errors + numeric_field_errors + 
                       boolean_field_errors + duplicate_ids)
        
        integrity_score = max(0, (1 - total_issues / total_possible_issues) * 100) if total_possible_issues > 0 else 0
        
        result = {
            "entries_checked": entries_checked,
            "empty_documents": empty_documents,
            "empty_metadatas": empty_metadatas,
            "empty_ids": empty_ids,
            "timestamp_format_errors": timestamp_format_errors,
            "numeric_field_errors": numeric_field_errors,
            "boolean_field_errors": boolean_field_errors,
            "duplicate_ids": duplicate_ids,
            "unique_ids": unique_ids,
            "total_issues": total_issues,
            "integrity_score": integrity_score
        }
        
        print(f"  ✅ Entries checked: {entries_checked:,}")
        print(f"  ✅ Empty documents: {empty_documents}")
        print(f"  ✅ Empty metadata: {empty_metadatas}")
        print(f"  ✅ Duplicate IDs: {duplicate_ids}")
        print(f"  ✅ Data type errors: {timestamp_format_errors + numeric_field_errors + boolean_field_errors}")
        print(f"  ✅ Integrity score: {integrity_score:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Data integrity check failed: {e}")
        return {"error": str(e), "integrity_score": 0}

def check_content_hash_integrity(db: ClaudeVectorDatabase) -> Dict[str, Any]:
    """Check content hash integrity for duplicate detection"""
    print("🔐 Checking content hash integrity...")
    
    try:
        # Get all entries with content hashes
        all_data = db.collection.get(include=["metadatas"], limit=None)
        
        if not all_data or not all_data.get('metadatas'):
            return {"error": "No metadata found", "hash_integrity_score": 0}
        
        content_hashes = []
        entries_with_hash = 0
        entries_without_hash = 0
        invalid_hashes = 0
        
        for metadata in all_data['metadatas']:
            if not metadata:
                continue
                
            content_hash = metadata.get('content_hash')
            if content_hash and content_hash != '':
                entries_with_hash += 1
                content_hashes.append(content_hash)
                
                # Basic hash format validation (assuming MD5-like format)
                if len(content_hash) < 10 or not content_hash.replace('-', '').replace('_', '').isalnum():
                    invalid_hashes += 1
            else:
                entries_without_hash += 1
        
        total_entries = len(all_data['metadatas'])
        unique_hashes = len(set(content_hashes))
        duplicate_hashes = entries_with_hash - unique_hashes
        
        hash_coverage = (entries_with_hash / total_entries * 100) if total_entries > 0 else 0
        hash_validity = ((entries_with_hash - invalid_hashes) / entries_with_hash * 100) if entries_with_hash > 0 else 0
        
        hash_integrity_score = (hash_coverage * 0.7 + hash_validity * 0.3)  # Weighted score
        
        result = {
            "total_entries": total_entries,
            "entries_with_hash": entries_with_hash,
            "entries_without_hash": entries_without_hash,
            "unique_hashes": unique_hashes,
            "duplicate_hashes": duplicate_hashes,
            "invalid_hashes": invalid_hashes,
            "hash_coverage_percent": hash_coverage,
            "hash_validity_percent": hash_validity,
            "hash_integrity_score": hash_integrity_score
        }
        
        print(f"  ✅ Total entries: {total_entries:,}")
        print(f"  ✅ Entries with hash: {entries_with_hash:,} ({hash_coverage:.1f}%)")
        print(f"  ✅ Unique hashes: {unique_hashes:,}")
        print(f"  ✅ Duplicate hashes: {duplicate_hashes}")
        print(f"  ✅ Invalid hashes: {invalid_hashes}")
        print(f"  ✅ Hash integrity: {hash_integrity_score:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Content hash integrity check failed: {e}")
        return {"error": str(e), "hash_integrity_score": 0}

def check_conversation_chain_integrity(db: ClaudeVectorDatabase) -> Dict[str, Any]:
    """Check conversation chain relationship integrity"""
    print("🔗 Checking conversation chain integrity...")
    
    try:
        # Sample entries to check chain relationships
        sample_size = min(1000, db.collection.count())
        sample_data = db.collection.get(limit=sample_size, include=["metadatas"])
        
        if not sample_data or not sample_data.get('metadatas'):
            return {"error": "No metadata found", "chain_integrity_score": 0}
        
        chain_fields = ['previous_message_id', 'next_message_id', 'related_solution_id', 'feedback_message_id']
        
        entries_analyzed = len(sample_data['metadatas'])
        chain_statistics = {}
        broken_chains = 0
        orphaned_references = 0
        
        # Build ID index for reference validation
        all_ids = set()
        for metadata in sample_data['metadatas']:
            if metadata and metadata.get('id'):
                all_ids.add(metadata['id'])
        
        # Analyze chain relationships
        for field in chain_fields:
            populated_count = 0
            valid_references = 0
            
            for metadata in sample_data['metadatas']:
                if not metadata:
                    continue
                
                field_value = metadata.get(field, '')
                if field_value and field_value != '':
                    populated_count += 1
                    
                    # Check if referenced ID exists in our sample
                    if field_value in all_ids:
                        valid_references += 1
                    else:
                        orphaned_references += 1
            
            coverage = (populated_count / entries_analyzed * 100) if entries_analyzed > 0 else 0
            validity = (valid_references / populated_count * 100) if populated_count > 0 else 100
            
            chain_statistics[field] = {
                "populated_count": populated_count,
                "valid_references": valid_references,
                "coverage_percent": coverage,
                "validity_percent": validity
            }
        
        # Calculate overall chain integrity
        avg_coverage = sum(stats["coverage_percent"] for stats in chain_statistics.values()) / len(chain_statistics)
        avg_validity = sum(stats["validity_percent"] for stats in chain_statistics.values()) / len(chain_statistics)
        
        chain_integrity_score = (avg_coverage * 0.6 + avg_validity * 0.4)  # Coverage more important
        
        result = {
            "entries_analyzed": entries_analyzed,
            "chain_field_statistics": chain_statistics,
            "orphaned_references": orphaned_references,
            "average_coverage_percent": avg_coverage,
            "average_validity_percent": avg_validity,
            "chain_integrity_score": chain_integrity_score
        }
        
        print(f"  ✅ Entries analyzed: {entries_analyzed:,}")
        print(f"  ✅ Average chain coverage: {avg_coverage:.1f}%")
        print(f"  ✅ Average reference validity: {avg_validity:.1f}%")
        print(f"  ✅ Orphaned references: {orphaned_references}")
        print(f"  ✅ Chain integrity: {chain_integrity_score:.1f}%")
        
        return result
        
    except Exception as e:
        print(f"  ❌ Conversation chain integrity check failed: {e}")
        return {"error": str(e), "chain_integrity_score": 0}

def main():
    """Main integrity check function"""
    print("🔍 DATABASE INTEGRITY CHECK")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("Comprehensive database health and integrity analysis")
    print()
    
    # Initialize logging
    logger = VectorDatabaseLogger("database_integrity")
    logger.logger.info("Starting database integrity check")
    
    try:
        # Initialize database
        print("💾 Initializing vector database...")
        db = ClaudeVectorDatabase()
        print("✅ Database connected")
        print()
        
        # Run all integrity checks
        results = {}
        
        results["collection_health"] = check_collection_health(db)
        print()
        
        results["metadata_consistency"] = check_metadata_consistency(db)
        print()
        
        results["data_integrity"] = check_data_integrity(db)
        print()
        
        results["content_hash_integrity"] = check_content_hash_integrity(db)
        print()
        
        results["chain_integrity"] = check_conversation_chain_integrity(db)
        print()
        
        # Calculate overall integrity score
        scores = []
        for check_name, check_result in results.items():
            if isinstance(check_result, dict):
                # Find the score field (varies by check)
                score_fields = ['health_score', 'consistency_score', 'integrity_score', 
                               'hash_integrity_score', 'chain_integrity_score']
                for field in score_fields:
                    if field in check_result:
                        scores.append(check_result[field])
                        break
        
        overall_score = sum(scores) / len(scores) if scores else 0
        
        # Summary report
        print("=" * 60)
        print("📋 INTEGRITY CHECK SUMMARY")
        print("=" * 60)
        
        status = "✅ HEALTHY" if overall_score >= 80 else "⚠️ NEEDS ATTENTION" if overall_score >= 60 else "❌ CRITICAL"
        print(f"Overall Status: {status}")
        print(f"Integrity Score: {overall_score:.1f}%")
        print()
        
        # Individual check results
        check_names = [
            ("Collection Health", results.get("collection_health", {}).get("health_score", 0)),
            ("Metadata Consistency", results.get("metadata_consistency", {}).get("consistency_score", 0)),
            ("Data Integrity", results.get("data_integrity", {}).get("integrity_score", 0)),
            ("Content Hash Integrity", results.get("content_hash_integrity", {}).get("hash_integrity_score", 0)),
            ("Chain Integrity", results.get("chain_integrity", {}).get("chain_integrity_score", 0))
        ]
        
        for check_name, score in check_names:
            status_icon = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            print(f"{check_name:<25} {status_icon} {score:.1f}%")
        
        print()
        
        # Recommendations
        recommendations = []
        if results.get("collection_health", {}).get("health_score", 0) < 80:
            recommendations.append("Run database maintenance and check ChromaDB configuration")
        
        if results.get("metadata_consistency", {}).get("consistency_score", 0) < 80:
            recommendations.append("Check metadata field population and run field backfill")
        
        if results.get("data_integrity", {}).get("integrity_score", 0) < 80:
            recommendations.append("Investigate data corruption and consider database rebuild")
        
        if results.get("content_hash_integrity", {}).get("hash_integrity_score", 0) < 80:
            recommendations.append("Check content hash generation and duplicate detection")
        
        if results.get("chain_integrity", {}).get("chain_integrity_score", 0) < 80:
            recommendations.append("Run conversation chain backfill to fix relationship links")
        
        if recommendations:
            print("🔧 RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
            print()
        
        # Save detailed results
        results["overall_score"] = overall_score
        results["check_timestamp"] = datetime.now().isoformat()
        
        output_file = "database_integrity_report.json"
        with open(output_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Detailed report saved to: {output_file}")
        
        logger.logger.info(f"Integrity check complete: {overall_score:.1f}% overall score")
        
        return 0 if overall_score >= 80 else 1
        
    except Exception as e:
        print(f"❌ Integrity check failed with error: {e}")
        logger.log_error("integrity_check_error", e)
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)