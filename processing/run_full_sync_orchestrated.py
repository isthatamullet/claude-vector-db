#!/usr/bin/env python3
"""
Orchestrated Force Sync - Complete Implementation Reference Implementation

Architecture: JSONL Files → ConversationExtractor → UnifiedEnhancementProcessor → ConversationBackFillEngine → Vector Database

This script implements the complete orchestrated approach combining:
- Fixed JSONL extraction (no more broken IDs)
- Enhanced metadata processing 
- Automatic conversation chain back-fill
- Comprehensive logging
- Single-command database rebuild capability
"""

import argparse
import json
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add base path to sys.path for package imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import core processing components
from database.conversation_extractor import ConversationExtractor
from database.vector_database import ClaudeVectorDatabase
from processing.enhanced_processor import UnifiedEnhancementProcessor
from database.enhanced_conversation_entry import EnhancedConversationEntry
from processing.conversation_backfill_engine import ConversationBackFillEngine
from system.central_logging import VectorDatabaseLogger, ProcessingTimer

def extract_conversation_data_fixed(raw_entry: Dict) -> Dict:
    """
    FIXED conversation data extraction from Claude JSONL format.
    
    Fixes the critical ID generation bug and infinite retry loops.
    """
    extracted = {}
    
    # FIXED: Proper ID extraction hierarchy
    if 'uuid' in raw_entry and raw_entry['uuid']:
        extracted['id'] = raw_entry['uuid']
    elif 'id' in raw_entry and raw_entry['id']:
        extracted['id'] = raw_entry['id']
    else:
        # Generate fallback ID from timestamp and content hash
        timestamp = raw_entry.get('timestamp', str(int(time.time() * 1000)))
        content_preview = str(raw_entry.get('message', {}).get('content', ''))[:50]
        import hashlib
        content_hash = hashlib.md5(content_preview.encode()).hexdigest()[:8]
        extracted['id'] = f"generated_{timestamp}_{content_hash}"
    
    # Extract content from nested message structure
    if 'message' in raw_entry:
        message = raw_entry['message']
        if 'content' in message:
            if isinstance(message['content'], list):
                # Handle structured content format
                text_parts = []
                for part in message['content']:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        text_parts.append(part.get('text', ''))
                    elif isinstance(part, str):
                        text_parts.append(part)
                extracted['content'] = ' '.join(text_parts).strip()
            else:
                extracted['content'] = str(message['content'])
        else:
            extracted['content'] = ''
        
        extracted['type'] = message.get('role', 'unknown')
    else:
        # Fallback for direct content
        extracted['content'] = raw_entry.get('content', '')
        extracted['type'] = raw_entry.get('type', 'unknown')
    
    # FIXED: Prevent empty content that causes infinite loops
    if not extracted['content'] or extracted['content'].strip() == '':
        extracted['content'] = f"[Empty {extracted['type']} message]"
    
    # Map other fields correctly
    extracted['project_path'] = raw_entry.get('cwd', '/home/user')
    extracted['session_id'] = raw_entry.get('sessionId', 'unknown')
    extracted['timestamp'] = raw_entry.get('timestamp', '')
    
    # Extract project name from path
    if extracted['project_path'] and extracted['project_path'] != '/home/user':
        extracted['project_name'] = os.path.basename(extracted['project_path'])
    else:
        extracted['project_name'] = 'unknown'
    
    return extracted


def process_session_with_automatic_backfill(session_file_path: Path, 
                                          extractor: ConversationExtractor,
                                          processor: UnifiedEnhancementProcessor,
                                          database: ClaudeVectorDatabase,
                                          backfill_engine: ConversationBackFillEngine,
                                          logger: VectorDatabaseLogger) -> Dict[str, Any]:
    """
    Process a single session file with automatic backfill integration.
    
    This is the core orchestrated processing function that:
    1. Extracts entries from JSONL
    2. Enhances with UnifiedEnhancementProcessor  
    3. Stores with enhanced metadata
    4. Runs conversation chain backfill automatically
    """
    
    with ProcessingTimer(logger, f"process_session_with_backfill", {"file": session_file_path.name}):
        result = {
            "session_file": session_file_path.name,
            "entries_processed": 0,
            "entries_added": 0,
            "entries_skipped": 0,
            "entries_errors": 0,
            "backfill_result": None,
            "success": False,
            "error": None
        }
        
        try:
            # Step 1: Extract raw entries from JSONL
            logger.log_processing_start("jsonl_extraction", {"file": session_file_path.name})
            
            raw_entries = []
            with open(session_file_path, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            raw_entries.append(json.loads(line))
                        except json.JSONDecodeError as e:
                            logger.log_error("jsonl_parse", e, {"file": session_file_path.name, "line": line_num})
            
            if not raw_entries:
                logger.log_session_processing(session_file_path.stem, "skipped", 0, {"reason": "no_valid_entries"})
                return result
            
            result["entries_processed"] = len(raw_entries)
            logger.log_processing_complete("jsonl_extraction", 0, {"entries_found": len(raw_entries)})
            
            # Step 2: Extract and enhance entries using orchestrated components
            logger.log_processing_start("entry_enhancement", {"count": len(raw_entries)})
            
            enhanced_entries = []
            for i, raw_entry in enumerate(raw_entries):
                try:
                    # Use the FIXED extraction function
                    extracted_data = extract_conversation_data_fixed(raw_entry)
                    
                    # Enhance with UnifiedEnhancementProcessor
                    enhanced_entry = processor.process_conversation_entry(extracted_data)
                    enhanced_entries.append(enhanced_entry)
                    
                    logger.log_entry_processing(extracted_data['id'], "success", {
                        "content_length": len(extracted_data['content']),
                        "type": extracted_data['type'],
                        "index": i
                    })
                    
                except Exception as e:
                    logger.log_error("entry_enhancement", e, {"entry_index": i, "file": session_file_path.name})
                    result["entries_errors"] += 1
            
            logger.log_processing_complete("entry_enhancement", 0, {"enhanced_entries": len(enhanced_entries)})
            
            # Step 3: Store entries with enhanced metadata
            if enhanced_entries:
                logger.log_processing_start("database_storage", {"count": len(enhanced_entries)})
                
                storage_result = database.batch_add_enhanced_entries(enhanced_entries, batch_size=100)
                
                result["entries_added"] = storage_result.get("added", 0)
                result["entries_skipped"] = storage_result.get("skipped", 0) 
                result["entries_errors"] += storage_result.get("errors", 0)
                
                logger.log_processing_complete("database_storage", 0, storage_result)
                
                # Step 4: Run conversation chain backfill automatically
                if backfill_engine and enhanced_entries:
                    session_id = enhanced_entries[0].session_id
                    if session_id and session_id != 'unknown':
                        logger.log_processing_start("conversation_backfill", {"session_id": session_id})
                        
                        try:
                            backfill_result = backfill_engine.process_session_relationships(session_id)
                            result["backfill_result"] = backfill_result
                            
                            logger.log_backfill_operation("session_backfill", 1, 
                                                        backfill_result.get("relationships_built", 0), 0)
                        except Exception as e:
                            logger.log_error("conversation_backfill", e, {"session_id": session_id})
            
            result["success"] = True
            logger.log_session_processing(session_file_path.stem, "success", result["entries_processed"], {
                "added": result["entries_added"],
                "skipped": result["entries_skipped"], 
                "errors": result["entries_errors"]
            })
            
        except Exception as e:
            result["error"] = str(e)
            result["success"] = False
            logger.log_error("session_processing", e, {"file": session_file_path.name})
        
        return result


def run_orchestrated_force_sync(max_files: Optional[int] = None, 
                               test_session: Optional[str] = None,
                               rebuild_from_scratch: bool = False,
                               log_level: str = "INFO") -> Dict[str, Any]:
    """
    Run the complete orchestrated force sync process.
    
    This is the main entry point implementing the complete architecture:
    JSONL Files → ConversationExtractor → UnifiedEnhancementProcessor → ConversationBackFillEngine → Vector Database
    """
    
    # Initialize central logging
    logger = VectorDatabaseLogger("orchestrated_force_sync", log_level)
    
    with ProcessingTimer(logger, "complete_orchestrated_sync", {"rebuild": rebuild_from_scratch}):
        
        results = {
            "started_at": datetime.now().isoformat(),
            "rebuild_from_scratch": rebuild_from_scratch,
            "files_processed": 0,
            "total_entries_processed": 0,
            "total_entries_added": 0,
            "total_entries_skipped": 0,
            "total_entries_errors": 0,
            "sessions_backfilled": 0,
            "processing_errors": [],
            "success": False
        }
        
        try:
            # Initialize core components
            logger.log_processing_start("component_initialization")
            
            # Initialize database
            database = ClaudeVectorDatabase()
            
            # Optional: Rebuild from scratch
            if rebuild_from_scratch:
                logger.log_processing_start("database_rebuild")
                try:
                    database.client.delete_collection(name=database.collection_name)
                    database.collection = database.client.create_collection(
                        name=database.collection_name,
                        embedding_function=database.embedding_function,
                        metadata={"description": "Claude Code conversation context with project-aware search"}
                    )
                    logger.log_processing_complete("database_rebuild", 0, {"status": "fresh_database"})
                except Exception as e:
                    logger.log_error("database_rebuild", e)
            
            # Initialize extractor  
            extractor = ConversationExtractor()
            
            # Initialize unified processor
            processor = UnifiedEnhancementProcessor(suppress_init_logging=True)
            
            # Initialize backfill engine
            backfill_engine = ConversationBackFillEngine(database)
            
            logger.log_processing_complete("component_initialization", 0)
            
            # Get conversation files
            logger.log_processing_start("file_discovery")
            
            claude_projects_dir = Path("/home/user/.claude/projects")
            
            if test_session:
                # Single session testing
                test_file = claude_projects_dir / f"{test_session}.jsonl"
                if test_file.exists():
                    jsonl_files = [test_file]
                else:
                    # Try to find file containing the session name (recursive search)
                    jsonl_files = [f for f in claude_projects_dir.rglob("*.jsonl") if test_session in f.name]
                    if not jsonl_files:
                        raise FileNotFoundError(f"Test session file not found: {test_session}")
            else:
                # All files (recursive search in subdirectories)
                jsonl_files = sorted(list(claude_projects_dir.rglob("*.jsonl")))
                if max_files:
                    jsonl_files = jsonl_files[:max_files]
            
            logger.log_processing_complete("file_discovery", 0, {"files_found": len(jsonl_files)})
            
            if not jsonl_files:
                raise ValueError("No JSONL files found to process")
            
            # Process each session file with orchestrated approach
            logger.log_processing_start("orchestrated_file_processing", {"total_files": len(jsonl_files)})
            
            for i, session_file in enumerate(jsonl_files, 1):
                logger.log_processing_start(f"file_processing_{i}", {"file": session_file.name})
                
                session_result = process_session_with_automatic_backfill(
                    session_file_path=session_file,
                    extractor=extractor,
                    processor=processor,
                    database=database,
                    backfill_engine=backfill_engine,
                    logger=logger
                )
                
                # Aggregate results
                results["files_processed"] += 1
                results["total_entries_processed"] += session_result["entries_processed"]
                results["total_entries_added"] += session_result["entries_added"]
                results["total_entries_skipped"] += session_result["entries_skipped"]
                results["total_entries_errors"] += session_result["entries_errors"]
                
                if session_result["backfill_result"]:
                    results["sessions_backfilled"] += 1
                
                if not session_result["success"]:
                    results["processing_errors"].append({
                        "file": session_file.name,
                        "error": session_result["error"]
                    })
                
                logger.log_processing_complete(f"file_processing_{i}", 0, session_result)
                
                # Progress logging
                if i % 5 == 0:
                    logger.log_processing_start("progress_report", {
                        "completed": i,
                        "total": len(jsonl_files),
                        "entries_added": results["total_entries_added"]
                    })
            
            logger.log_processing_complete("orchestrated_file_processing", 0, {
                "files_processed": results["files_processed"],
                "total_entries": results["total_entries_added"]
            })
            
            results["success"] = True
            results["completed_at"] = datetime.now().isoformat()
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            logger.log_error("orchestrated_force_sync", e)
        
        return results


def main():
    """Main entry point with command line argument parsing."""
    
    parser = argparse.ArgumentParser(
        description="Orchestrated Force Sync - Complete Implementation Reference",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Architecture: JSONL Files → ConversationExtractor → UnifiedEnhancementProcessor → ConversationBackFillEngine → Vector Database

Key Features:
- Fixed JSONL extraction (no more broken IDs or infinite loops)
- Enhanced metadata storage (30+ fields)
- Automatic conversation chain back-fill
- Comprehensive logging with central logging system
- Single-command database rebuild

Usage Examples:
  # Full database rebuild
  python run_full_sync_orchestrated.py --rebuild-from-scratch
  
  # Test with single session
  python run_full_sync_orchestrated.py --test-session session_20250805_123456
  
  # Process limited files
  python run_full_sync_orchestrated.py --max-files 10
        """
    )
    
    parser.add_argument(
        '--max-files',
        type=int,
        help='Maximum number of files to process (for testing)'
    )
    
    parser.add_argument(
        '--test-session',
        type=str,
        help='Process only a specific session file (for testing)'
    )
    
    parser.add_argument(
        '--rebuild-from-scratch',
        action='store_true',
        help='Delete existing database and rebuild completely'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    print("🚀 Starting Orchestrated Force Sync")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Architecture: JSONL → Extractor → Processor → BackFill → Database")
    
    if args.rebuild_from_scratch:
        print("⚠️  REBUILD MODE: Will delete existing database!")
    
    if args.test_session:
        print(f"🧪 TEST MODE: Processing session {args.test_session}")
    elif args.max_files:
        print(f"📊 LIMITED MODE: Processing max {args.max_files} files")
    
    print()
    
    # Run orchestrated sync
    results = run_orchestrated_force_sync(
        max_files=args.max_files,
        test_session=args.test_session,
        rebuild_from_scratch=args.rebuild_from_scratch,
        log_level=args.log_level
    )
    
    # Print results
    print("\n" + "=" * 60)
    print("🎯 ORCHESTRATED FORCE SYNC COMPLETE")
    print("=" * 60)
    
    if results["success"]:
        print("✅ Success!")
        print(f"Files processed: {results['files_processed']}")
        print(f"Total entries processed: {results['total_entries_processed']}")
        print(f"Total entries added: {results['total_entries_added']}")
        print(f"Total entries skipped: {results['total_entries_skipped']}")
        print(f"Total errors: {results['total_entries_errors']}")
        print(f"Sessions backfilled: {results['sessions_backfilled']}")
        
        if results["processing_errors"]:
            print(f"\n⚠️  Processing errors: {len(results['processing_errors'])}")
            for error in results["processing_errors"][:5]:  # Show first 5
                print(f"  - {error['file']}: {error['error']}")
    else:
        print("❌ Failed!")
        print(f"Error: {results.get('error', 'Unknown error')}")
    
    print(f"\nCompleted at: {results.get('completed_at', 'Unknown')}")
    print(f"Logs available in: /home/user/.claude-vector-db-enhanced/logs/")


if __name__ == "__main__":
    main()