#!/usr/bin/env python3
"""
Analyze the database entry discrepancy to identify the source of extra entries.
"""

import json
from collections import defaultdict, Counter
from database.vector_database import ClaudeVectorDatabase
from database.conversation_extractor import ConversationExtractor
import hashlib

def analyze_database_discrepancy():
    print('🔍 Analyzing database entry discrepancy...')
    
    # Initialize database
    db = ClaudeVectorDatabase()
    total_db_entries = db.collection.count()
    print(f'Database entries: {total_db_entries:,}')
    
    # Initialize extractor
    extractor = ConversationExtractor()
    
    # Count JSONL entries
    print('\n📁 Counting JSONL entries...')
    jsonl_count = 0
    file_counts = {}
    
    # Find all JSONL files
    jsonl_files = list(extractor.claude_projects_dir.rglob("*.jsonl"))
    
    for file_path in jsonl_files:
        file_entry_count = 0
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        jsonl_count += 1
                        file_entry_count += 1
            file_counts[file_path.name] = file_entry_count
            print(f'  {file_path.name}: {file_entry_count} entries')
        except Exception as e:
            print(f'  ERROR reading {file_path.name}: {e}')
    
    print(f'\nTotal JSONL entries: {jsonl_count:,}')
    print(f'Database entries: {total_db_entries:,}')
    print(f'Discrepancy: {total_db_entries - jsonl_count:,} extra entries in database')
    
    # Get all database entries for analysis
    print('\n🔍 Analyzing database entries...')
    db_results = db.collection.get(include=['metadatas'])
    
    # Analyze by file name
    db_by_file = defaultdict(int)
    db_by_project = defaultdict(int)
    db_by_session = defaultdict(int)
    duplicate_content_hashes = defaultdict(int)
    id_patterns = defaultdict(int)
    
    for i, (entry_id, metadata) in enumerate(zip(db_results['ids'], db_results['metadatas'])):
        if metadata:
            file_name = metadata.get('file_name', 'unknown')
            project_name = metadata.get('project_name', 'unknown')
            session_id = metadata.get('session_id', 'unknown')
            content_hash = metadata.get('content_hash', 'none')
            
            db_by_file[file_name] += 1
            db_by_project[project_name] += 1
            db_by_session[session_id] += 1
            duplicate_content_hashes[content_hash] += 1
            
            # Analyze ID patterns
            if entry_id.startswith('f8a4b940'):
                id_patterns['f8a4b940_pattern'] += 1
            elif '-' in entry_id and len(entry_id) == 36:
                id_patterns['uuid_pattern'] += 1
            else:
                id_patterns['other_pattern'] += 1
        
        if i % 10000 == 0:
            print(f'  Processed {i:,} entries...')
    
    print('\n📊 Analysis Results:')
    print('=' * 60)
    
    # File analysis
    print('\n📁 Database vs JSONL by file:')
    total_file_discrepancy = 0
    for file_name in sorted(set(list(file_counts.keys()) + list(db_by_file.keys()))):
        jsonl_count_file = file_counts.get(file_name, 0)
        db_count_file = db_by_file.get(file_name, 0)
        discrepancy = db_count_file - jsonl_count_file
        total_file_discrepancy += discrepancy
        
        if discrepancy != 0:
            print(f'  {file_name}: JSONL={jsonl_count_file}, DB={db_count_file}, Diff={discrepancy:+d}')
    
    print(f'\nTotal file-level discrepancy: {total_file_discrepancy:,}')
    
    # Check for duplicate content hashes
    print('\n🔍 Duplicate content analysis:')
    duplicates = {h: count for h, count in duplicate_content_hashes.items() if count > 1 and h != 'none'}
    if duplicates:
        print(f'Found {len(duplicates)} content hashes with duplicates:')
        for hash_val, count in sorted(duplicates.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f'  Hash {hash_val[:16]}...: {count} copies')
        
        # Count total duplicate entries
        total_duplicates = sum(count - 1 for count in duplicates.values())
        print(f'Total duplicate entries: {total_duplicates:,}')
    else:
        print('No content-based duplicates found')
    
    # ID pattern analysis
    print('\n🆔 ID pattern analysis:')
    for pattern, count in id_patterns.items():
        print(f'  {pattern}: {count:,} entries')
    
    # Top projects by entry count
    print('\n📋 Top projects by entry count:')
    for project, count in sorted(db_by_project.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f'  {project}: {count:,} entries')
    
    # Check for sessions with unusual entry counts
    print('\n📊 Sessions with high entry counts:')
    high_count_sessions = {s: count for s, count in db_by_session.items() 
                          if count > 100 and s != 'unknown'}
    for session, count in sorted(high_count_sessions.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f'  {session}: {count:,} entries')
    
    # Look for entries with missing or invalid file names
    print('\n❓ Entries with problematic file names:')
    problematic_files = ['unknown', 'null', '', None]
    problematic_count = sum(db_by_file.get(fname, 0) for fname in problematic_files)
    if problematic_count > 0:
        print(f'  Entries with missing/invalid file names: {problematic_count:,}')
        for fname in problematic_files:
            count = db_by_file.get(fname, 0)
            if count > 0:
                print(f'    "{fname}": {count:,} entries')
    else:
        print('  All entries have valid file names')
    
    return {
        'total_db_entries': total_db_entries,
        'total_jsonl_entries': jsonl_count,
        'discrepancy': total_db_entries - jsonl_count,
        'duplicate_content_entries': sum(count - 1 for count in duplicates.values()) if duplicates else 0,
        'id_patterns': id_patterns,
        'file_discrepancies': total_file_discrepancy,
        'problematic_files': problematic_count
    }

if __name__ == "__main__":
    results = analyze_database_discrepancy()
    
    print('\n🎯 Summary:')
    print('=' * 40)
    print(f'Database entries: {results["total_db_entries"]:,}')
    print(f'JSONL entries: {results["total_jsonl_entries"]:,}')
    print(f'Net discrepancy: {results["discrepancy"]:,}')
    
    if results["duplicate_content_entries"] > 0:
        print(f'Duplicate content entries: {results["duplicate_content_entries"]:,}')
    if results["problematic_files"] > 0:
        print(f'Entries with bad file names: {results["problematic_files"]:,}')
    
    print('\n✅ Analysis complete!')