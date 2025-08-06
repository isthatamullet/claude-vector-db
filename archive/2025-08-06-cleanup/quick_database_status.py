#!/usr/bin/env python3
"""
Quick database status check after repair attempt.
"""

from database.vector_database import ClaudeVectorDatabase
from database.conversation_extractor import ConversationExtractor
from pathlib import Path

def quick_status_check():
    print("🔍 Quick Database Status Check")
    print("=" * 40)
    
    # Database status
    db = ClaudeVectorDatabase()
    db_entries = db.collection.count()
    print(f"Database entries: {db_entries:,}")
    
    # Check for backups
    backup_path = Path("/home/user/.claude-vector-db-enhanced/chroma_db_backup_corrupt")
    if backup_path.exists():
        print(f"✅ Backup exists: {backup_path}")
    else:
        print("❌ No backup found")
    
    # Quick duplicate check
    results = db.collection.get(include=['metadatas'], limit=1000)
    unknown_files = sum(1 for metadata in results['metadatas'] 
                       if metadata and metadata.get('file_name') == 'unknown')
    
    print(f"Unknown file entries in sample: {unknown_files}/1000")
    
    # JSONL count
    extractor = ConversationExtractor()
    jsonl_files = list(extractor.claude_projects_dir.rglob("*.jsonl"))
    
    total_jsonl = 0
    for file_path in jsonl_files[:10]:  # Quick sample
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                file_count = sum(1 for line in f if line.strip())
                total_jsonl += file_count
        except:
            pass
    
    print(f"Sample JSONL entries (10 files): {total_jsonl}")
    print(f"Total JSONL files: {len(jsonl_files)}")
    
    # Estimate total JSONL entries
    if len(jsonl_files) > 0:
        avg_per_file = total_jsonl / min(10, len(jsonl_files))
        estimated_total = int(avg_per_file * len(jsonl_files))
        print(f"Estimated total JSONL entries: {estimated_total:,}")
        
        if abs(db_entries - estimated_total) > 10000:
            print("⚠️ Large discrepancy detected - integrity issues remain")
        elif unknown_files > 50:
            print("⚠️ Unknown file entries detected - corruption issues remain")
        else:
            print("✅ Database appears healthy")
    
    return {
        'db_entries': db_entries,
        'jsonl_files': len(jsonl_files),
        'unknown_sample': unknown_files,
        'backup_exists': backup_path.exists()
    }

if __name__ == "__main__":
    status = quick_status_check()
    print(f"\nStatus: {status}")