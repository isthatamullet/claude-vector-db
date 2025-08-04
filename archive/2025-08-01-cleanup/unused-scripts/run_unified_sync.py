#!/usr/bin/env python3
"""
Unified Processor Full Sync Script
Clean implementation using the unified processor for consistent enhancement
"""

import json
from pathlib import Path
from datetime import datetime
from vector_database import ClaudeVectorDatabase
from enhanced_processor import UnifiedEnhancementProcessor, ProcessingContext

def run_unified_sync():
    """Run full sync with unified processor."""
    print("🧠 UNIFIED PROCESSOR Full Sync")
    print("=" * 50)
    print("✨ Consistent enhancement processing identical to real-time hooks")
    
    # Initialize components
    print("Initializing unified processor and database...")
    db = ClaudeVectorDatabase()
    processor = UnifiedEnhancementProcessor()
    
    # Get all conversation files
    claude_projects_dir = Path("/home/user/.claude/projects")
    jsonl_files = sorted(list(claude_projects_dir.rglob("*.jsonl")))
    
    total_files = len(jsonl_files)
    print(f"Found {total_files} conversation files for unified processing")
    
    # Statistics
    total_entries_added = 0
    total_entries_skipped = 0
    total_entries_errors = 0
    
    for i, file_path in enumerate(jsonl_files, 1):
        print(f"\n🔍 Processing file {i}/{total_files}: {file_path.name}")
        
        try:
            # Read and parse JSONL file
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # Parse all entries for context
            all_entries = []
            for line in lines:
                if line.strip():
                    try:
                        all_entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            if not all_entries:
                print("  ⚠️ No valid entries found")
                continue
            
            # Process entries with unified processor
            enhanced_entries = []
            for entry_idx, entry_data in enumerate(all_entries):
                try:
                    # Extract content from JSONL entry
                    message = entry_data.get('message', {})
                    content = message.get('content', '')
                    
                    # Handle different content formats
                    if isinstance(content, list):
                        text_parts = []
                        for item in content:
                            if isinstance(item, dict):
                                if item.get('type') == 'text':
                                    text_parts.append(item.get('text', ''))
                                elif 'content' in item:
                                    text_parts.append(str(item['content']))
                            elif isinstance(item, str):
                                text_parts.append(item)
                        content = ' '.join(text_parts)
                    elif not isinstance(content, str):
                        content = str(content)
                    
                    if not content.strip():
                        continue
                    
                    # Create base metadata for unified processor
                    base_metadata = {
                        'id': f"{file_path.stem}_{entry_data.get('type', 'unknown')}_{entry_idx + 1}",
                        'type': entry_data.get('type', 'unknown'),
                        'project_path': str(file_path.parent.parent),
                        'project_name': file_path.parent.parent.name,
                        'timestamp': entry_data.get('timestamp', ''),
                        'session_id': file_path.stem,
                        'file_name': file_path.name,
                        'has_code': any(indicator in content.lower() for indicator in ['```', 'function', 'class ', 'def ', 'import ']),
                        'tools_used': []
                    }
                    
                    # Create processing context
                    context = ProcessingContext(
                        source="full_sync",
                        full_conversation=all_entries,
                        message_position=entry_idx
                    )
                    
                    # Add adjacency context
                    if entry_idx > 0:
                        context.previous_message = all_entries[entry_idx - 1]
                    if entry_idx < len(all_entries) - 1:
                        context.next_message = all_entries[entry_idx + 1]
                    
                    # Use unified processor to create enhanced entry
                    enhanced_entry = processor.create_enhanced_entry(content, base_metadata, context)
                    enhanced_entries.append(enhanced_entry)
                    
                except Exception as e:
                    print(f"    ⚠️ Error processing entry {entry_idx + 1}: {e}")
                    continue
            
            print(f"  📝 Processed {len(enhanced_entries)} entries with unified processor")
            
            # Add enhanced entries to database
            if enhanced_entries:
                result = db.add_conversation_entries(enhanced_entries, batch_size=min(50, len(enhanced_entries)))
                
                entries_added = result.get('added', 0)
                entries_skipped = result.get('skipped', 0)
                entries_errors = result.get('errors', 0)
                
                total_entries_added += entries_added
                total_entries_skipped += entries_skipped  
                total_entries_errors += entries_errors
                
                print(f"  ✅ Database - Added: {entries_added}, Skipped: {entries_skipped}, Errors: {entries_errors}")
            else:
                print("  ⚠️ No valid entries to add")
                
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            total_entries_errors += 1
        
        # Progress update every 10 files
        if i % 10 == 0:
            print(f"\n📈 Progress Update ({i}/{total_files} files completed)")
            print(f"   Entries processed: {total_entries_added}")
    
    # Get processor statistics
    processor_stats = processor.get_processor_stats()
    
    # Final summary
    print(f"\n{'='*50}")
    print("🎯 UNIFIED PROCESSOR Sync Complete!")
    print(f"{'='*50}")
    print(f"Files processed: {total_files}")
    print(f"Total entries added: {total_entries_added}")
    print(f"Total entries skipped: {total_entries_skipped}")
    print(f"Total errors: {total_entries_errors}")
    
    print("\n🔧 Unified Processor Statistics:")
    print(f"  - Total entries processed: {processor_stats['entries_processed']}")
    print(f"  - Average processing time: {processor_stats['average_processing_time_ms']:.2f}ms")
    print(f"  - Components available: {processor_stats['components_available']}")
    print(f"  - Components enabled: {processor_stats['components_enabled']}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("✨ All entries processed with UNIFIED PROCESSOR - identical logic as real-time hooks!")

if __name__ == "__main__":
    run_unified_sync()