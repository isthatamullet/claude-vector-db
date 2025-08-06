#!/usr/bin/env python3
"""
Database Integrity Repair Tool
Fixes the duplicate entry and unknown file issues in the vector database.
"""

import os
import shutil
from pathlib import Path
from database.vector_database import ClaudeVectorDatabase
from database.conversation_extractor import ConversationExtractor
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def backup_database():
    """Create backup of current database"""
    db_path = Path("/home/user/.claude-vector-db-enhanced/chroma_db")
    backup_path = Path("/home/user/.claude-vector-db-enhanced/chroma_db_backup_corrupt")
    
    if db_path.exists():
        if backup_path.exists():
            shutil.rmtree(backup_path)
        shutil.copytree(db_path, backup_path)
        logger.info(f"✅ Database backed up to {backup_path}")
        return True
    return False

def analyze_corruption():
    """Analyze the current corruption state"""
    logger.info("🔍 Analyzing current database corruption...")
    
    db = ClaudeVectorDatabase()
    
    # Get all entries
    results = db.collection.get(include=['metadatas'])
    total_entries = len(results['ids'])
    
    # Analyze corruption patterns
    unknown_files = 0
    duplicate_hashes = {}
    problematic_sessions = set()
    
    for i, (entry_id, metadata) in enumerate(zip(results['ids'], results['metadatas'])):
        if metadata:
            file_name = metadata.get('file_name', 'unknown')
            session_id = metadata.get('session_id', 'unknown')
            content_hash = metadata.get('content_hash', 'none')
            
            if file_name == 'unknown':
                unknown_files += 1
                problematic_sessions.add(session_id)
            
            if content_hash in duplicate_hashes:
                duplicate_hashes[content_hash] += 1
            else:
                duplicate_hashes[content_hash] = 1
    
    # Count actual duplicates
    actual_duplicates = sum(count - 1 for count in duplicate_hashes.values() if count > 1)
    
    logger.info(f"📊 Corruption Analysis:")
    logger.info(f"   Total entries: {total_entries:,}")
    logger.info(f"   Unknown file entries: {unknown_files:,}")
    logger.info(f"   Duplicate content entries: {actual_duplicates:,}")
    logger.info(f"   Problematic sessions: {len(problematic_sessions)}")
    
    return {
        'total_entries': total_entries,
        'unknown_files': unknown_files,
        'duplicates': actual_duplicates,
        'problematic_sessions': len(problematic_sessions)
    }

def clean_rebuild_database():
    """Perform clean rebuild of the database"""
    logger.info("🔄 Starting clean database rebuild...")
    
    # Backup first
    backup_success = backup_database()
    if not backup_success:
        logger.error("❌ Backup failed - aborting rebuild")
        return False
    
    # Remove corrupted database
    db_path = Path("/home/user/.claude-vector-db-enhanced/chroma_db")
    if db_path.exists():
        shutil.rmtree(db_path)
        logger.info("✅ Removed corrupted database")
    
    # Initialize fresh database
    logger.info("🆕 Creating fresh database...")
    db = ClaudeVectorDatabase()
    
    # Extract all conversations from source JSONL files
    logger.info("📁 Extracting conversations from JSONL files...")
    extractor = ConversationExtractor()
    
    # Get all JSONL files for verification
    jsonl_files = list(extractor.claude_projects_dir.rglob("*.jsonl"))
    logger.info(f"Found {len(jsonl_files)} JSONL files to process")
    
    # Extract conversations
    all_entries = []
    for file_path in jsonl_files:
        try:
            file_entries = list(extractor.extract_from_jsonl_file(file_path))
            all_entries.extend(file_entries)
            logger.info(f"  ✅ {file_path.name}: {len(file_entries)} entries")
        except Exception as e:
            logger.error(f"  ❌ {file_path.name}: {e}")
    
    logger.info(f"📊 Total entries extracted: {len(all_entries)}")
    
    # Add to database with deduplication
    if all_entries:
        logger.info("💾 Adding entries to fresh database...")
        results = db.add_conversation_entries(all_entries)
        logger.info(f"✅ Database rebuild complete: {results}")
        
        # Get final stats
        final_stats = db.get_collection_stats()
        logger.info(f"📈 Final database stats: {final_stats.get('total_entries', 0)} entries")
        
        return True
    else:
        logger.error("❌ No entries to add to database")
        return False

def verify_rebuild():
    """Verify the rebuilt database integrity"""
    logger.info("🔍 Verifying rebuilt database...")
    
    db = ClaudeVectorDatabase()
    
    # Count database entries
    db_count = db.collection.count()
    
    # Count JSONL entries
    extractor = ConversationExtractor()
    jsonl_files = list(extractor.claude_projects_dir.rglob("*.jsonl"))
    
    jsonl_count = 0
    for file_path in jsonl_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        jsonl_count += 1
        except Exception as e:
            logger.warning(f"Could not read {file_path.name}: {e}")
    
    # Check for unknown files
    results = db.collection.get(
        where={'file_name': {'$eq': 'unknown'}},
        include=[]
    )
    unknown_count = len(results['ids'])
    
    logger.info(f"✅ Verification Results:")
    logger.info(f"   Database entries: {db_count:,}")
    logger.info(f"   JSONL entries: {jsonl_count:,}")
    logger.info(f"   Discrepancy: {db_count - jsonl_count:+,}")
    logger.info(f"   Unknown file entries: {unknown_count}")
    
    # Check if rebuild was successful
    success = (abs(db_count - jsonl_count) <= 10) and (unknown_count == 0)
    
    if success:
        logger.info("🎯 Database integrity restored successfully!")
    else:
        logger.warning("⚠️ Database integrity issues remain")
    
    return success

def main():
    """Main repair function"""
    print("🚀 Database Integrity Repair Tool")
    print("=" * 50)
    
    # Analyze current state
    corruption_stats = analyze_corruption()
    
    if corruption_stats['duplicates'] > 1000 or corruption_stats['unknown_files'] > 1000:
        print(f"\n⚠️ Severe corruption detected:")
        print(f"   Duplicate entries: {corruption_stats['duplicates']:,}")
        print(f"   Unknown file entries: {corruption_stats['unknown_files']:,}")
        print(f"\n🔧 Proceeding with clean rebuild...")
        
        # Perform clean rebuild
        rebuild_success = clean_rebuild_database()
        
        if rebuild_success:
            # Verify the rebuild
            verify_success = verify_rebuild()
            
            if verify_success:
                print("\n✅ Database integrity repair completed successfully!")
                print("💡 The corrupted database has been backed up and can be removed.")
            else:
                print("\n⚠️ Rebuild completed but integrity issues remain.")
                print("💡 Manual investigation may be required.")
        else:
            print("\n❌ Database rebuild failed.")
            print("💡 The original corrupted database backup is preserved.")
    else:
        print("\n✅ Database integrity is acceptable - no major repair needed.")
    
    return True

if __name__ == "__main__":
    main()