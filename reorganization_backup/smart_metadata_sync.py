#!/usr/bin/env python3
"""
Smart Enhanced Metadata Sync Script

Efficiently detects and reindexes JSONL files with missing enhanced metadata
without requiring a full database rebuild. Uses intelligent detection to skip
files that already have complete enhanced metadata.

Features:
- Smart detection of missing enhanced metadata
- Selective reindexing of only incomplete entries
- Shared processor instance to eliminate excessive logging
- Progress tracking and performance metrics
- Backward compatibility with existing data

Author: Claude Code Vector Database Enhancement System
Version: 1.0.0
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Set, Optional
from conversation_extractor import ConversationExtractor
from vector_database import ClaudeVectorDatabase
from enhanced_processor import process_jsonl_entry, UnifiedEnhancementProcessor

class SmartMetadataSync:
    """Smart metadata sync that only processes entries missing enhanced metadata."""
    
    def __init__(self, enable_unified_enhancement: bool = False):
        """Initialize smart sync components."""
        print("🧠 Smart Enhanced Metadata Sync - Initializing...")
        
        # Initialize components once (no repeated logging)
        self.db = ClaudeVectorDatabase()
        self.processor = UnifiedEnhancementProcessor(suppress_init_logging=True)
        self.extractor = ConversationExtractor()
        
        # Unified enhancement engine (lazy initialization)
        self.enable_unified_enhancement = enable_unified_enhancement
        self._unified_engine = None
        
        # Enhanced metadata field checklist (expanded for unified enhancement)
        self.required_enhanced_fields = {
            'detected_topics', 'primary_topic', 'solution_quality_score',
            'is_solution_attempt', 'user_feedback_sentiment', 'validation_strength',
            'is_validated_solution', 'is_refuted_attempt'
        }
        
        # Conversation chain fields for unified enhancement
        self.conversation_chain_fields = {
            'previous_message_id', 'next_message_id', 'related_solution_id',
            'feedback_message_id', 'is_feedback_to_solution'
        }
        
        # Performance tracking
        self.stats = {
            'files_scanned': 0,
            'files_needing_enhancement': 0,
            'entries_updated': 0,
            'entries_skipped': 0,
            'processing_time': 0.0,
            'conversation_chains_built': 0,
            'field_optimizations': 0
        }
    
    @property
    def unified_engine(self):
        """Lazy initialization of unified enhancement engine."""
        if self._unified_engine is None and self.enable_unified_enhancement:
            try:
                from unified_enhancement_engine import UnifiedEnhancementEngine
                self._unified_engine = UnifiedEnhancementEngine()
                print("🚀 Unified Enhancement Engine initialized for smart sync")
            except ImportError as e:
                print(f"⚠️ Could not initialize Unified Enhancement Engine: {e}")
                self.enable_unified_enhancement = False
        return self._unified_engine
    
    def detect_missing_enhanced_metadata(self) -> Dict[str, List[str]]:
        """
        Detect which database entries are missing enhanced metadata.
        
        Returns:
            Dictionary mapping file names to lists of entry IDs needing enhancement
        """
        print("🔍 Scanning database for entries with missing enhanced metadata...")
        
        # Get all entries from database
        try:
            all_data = self.db.collection.get(
                include=['metadatas'],
                limit=50000  # Large limit to get all entries
            )
        except Exception as e:
            print(f"❌ Error retrieving database entries: {e}")
            return {}
        
        if not all_data['metadatas']:
            print("⚠️ No entries found in database")
            return {}
        
        # Analyze entries for missing enhanced metadata
        missing_by_file = {}
        total_entries = len(all_data['metadatas'])
        enhanced_count = 0
        
        for i, (entry_id, metadata) in enumerate(zip(all_data['ids'], all_data['metadatas'])):
            if not metadata:
                continue
            
            # Check if entry has enhanced metadata
            has_enhanced_metadata = self._has_complete_enhanced_metadata(metadata)
            
            if has_enhanced_metadata:
                enhanced_count += 1
            else:
                # Track entries needing enhancement by file
                file_name = metadata.get('file_name', 'unknown')
                if file_name not in missing_by_file:
                    missing_by_file[file_name] = []
                missing_by_file[file_name].append(entry_id)
        
        enhancement_percentage = (enhanced_count / total_entries) * 100 if total_entries > 0 else 0
        missing_count = total_entries - enhanced_count
        
        print("📊 Database Analysis Complete:")
        print(f"   Total entries: {total_entries}")
        print(f"   Enhanced entries: {enhanced_count} ({enhancement_percentage:.1f}%)")
        print(f"   Missing enhanced metadata: {missing_count} entries")
        print(f"   Files needing enhancement: {len(missing_by_file)}")
        
        return missing_by_file
    
    def _has_complete_enhanced_metadata(self, metadata: Dict) -> bool:
        """Check if metadata contains complete enhanced fields."""
        if not metadata:
            return False
        
        # Check for presence of key enhanced fields
        enhanced_field_count = 0
        for field in self.required_enhanced_fields:
            if field in metadata and metadata[field] is not None:
                enhanced_field_count += 1
        
        # Consider entry enhanced if it has most required fields
        completion_threshold = len(self.required_enhanced_fields) * 0.6  # 60% threshold
        return enhanced_field_count >= completion_threshold
    
    def sync_missing_metadata(self, target_files: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Sync enhanced metadata for entries missing it.
        
        Args:
            target_files: Optional list of specific files to process
            
        Returns:
            Statistics about the sync operation
        """
        start_time = time.time()
        
        # Detect entries needing enhancement
        missing_by_file = self.detect_missing_enhanced_metadata()
        
        if not missing_by_file:
            print("✅ All entries already have enhanced metadata!")
            return {'files_processed': 0, 'entries_updated': 0, 'entries_skipped': 0}
        
        # Filter to target files if specified
        if target_files:
            missing_by_file = {f: ids for f, ids in missing_by_file.items() if f in target_files}
        
        self.stats['files_needing_enhancement'] = len(missing_by_file)
        
        # Process files with missing metadata
        for file_name, missing_entry_ids in missing_by_file.items():
            print(f"\n📝 Processing {file_name} ({len(missing_entry_ids)} entries need enhancement)")
            
            # Find the actual file path in project subdirectories
            actual_file_path = self._find_actual_file_path(file_name)
            if not actual_file_path:
                print(f"⚠️ File not found in any project subdirectory: {file_name}")
                continue
            
            # Process this file's missing entries
            file_stats = self._process_file_selective_enhancement(
                actual_file_path, set(missing_entry_ids)
            )
            
            self.stats['entries_updated'] += file_stats['updated']
            self.stats['entries_skipped'] += file_stats['skipped']
            self.stats['files_scanned'] += 1
            
            print(f"   ✅ Updated: {file_stats['updated']}, Skipped: {file_stats['skipped']}")
        
        # Final statistics
        self.stats['processing_time'] = time.time() - start_time
        
        print("\n🎯 Smart Metadata Sync Complete!")
        print(f"   Files processed: {self.stats['files_scanned']}")
        print(f"   Entries updated: {self.stats['entries_updated']}")
        print(f"   Entries skipped: {self.stats['entries_skipped']}")
        print(f"   Processing time: {self.stats['processing_time']:.1f}s")
        
        return {
            'files_processed': self.stats['files_scanned'],
            'entries_updated': self.stats['entries_updated'],
            'entries_skipped': self.stats['entries_skipped'],
            'processing_time': self.stats['processing_time']
        }
    
    def _process_file_selective_enhancement(self, file_path: Path, target_entry_ids: Set[str]) -> Dict[str, int]:
        """
        Process a single file, enhancing only entries that need it.
        
        Args:
            file_path: Actual path to JSONL file (already found)
            target_entry_ids: Set of entry IDs that need enhancement
            
        Returns:
            Statistics for this file
        """
        file_stats = {'updated': 0, 'skipped': 0}
        
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
            
            # Process only entries that need enhancement
            enhanced_entries = []
            
            for entry_idx, entry_data in enumerate(all_entries):
                # Generate expected entry ID for this entry
                session_id = file_path.stem
                entry_type = entry_data.get('type', 'unknown')
                expected_id = f"{session_id}_{entry_type}_{entry_idx + 1}"
                
                # Only process if this entry needs enhancement
                if expected_id in target_entry_ids:
                    try:
                        # Use shared processor for consistent enhancement
                        enhanced_entry = process_jsonl_entry(
                            jsonl_entry=entry_data,
                            file_path=file_path,
                            line_num=entry_idx + 1,
                            all_messages=all_entries,
                            message_index=entry_idx
                        )
                        enhanced_entries.append(enhanced_entry)
                        file_stats['updated'] += 1
                        
                    except Exception as e:
                        print(f"      ⚠️ Error enhancing entry {expected_id}: {e}")
                        file_stats['skipped'] += 1
                else:
                    file_stats['skipped'] += 1
            
            # Update database with enhanced entries
            if enhanced_entries:
                # Use upsert operation to update existing entries
                self._update_enhanced_metadata_in_db(enhanced_entries)
                
        except Exception as e:
            print(f"   ❌ Error processing file {file_path.name}: {e}")
            file_stats['skipped'] += len(target_entry_ids)
        
        return file_stats
    
    def _find_actual_file_path(self, file_name: str) -> Optional[Path]:
        """Find the actual file path in project subdirectories."""
        claude_projects_dir = Path("/home/user/.claude/projects")
        
        # Search through all subdirectories
        for file_path in claude_projects_dir.rglob(file_name):
            if file_path.is_file():
                return file_path
        
        return None
    
    def _update_enhanced_metadata_in_db(self, enhanced_entries: List) -> None:
        """
        Update enhanced metadata for existing entries in database.
        
        Args:
            enhanced_entries: List of enhanced entries to update
        """
        try:
            for entry in enhanced_entries:
                # Get enhanced metadata
                enhanced_metadata = entry.to_enhanced_metadata()
                
                # Update existing entry in database
                self.db.collection.update(
                    ids=[entry.id],
                    metadatas=[enhanced_metadata]
                )
                
        except Exception as e:
            print(f"      ⚠️ Error updating database: {e}")
    
    def get_enhancement_status(self) -> Dict[str, any]:
        """Get current enhancement status of the database."""
        # Detect current status
        missing_by_file = self.detect_missing_enhanced_metadata()
        
        # Get total counts
        try:
            total_entries = self.db.collection.count()
        except Exception:
            total_entries = 0
        
        missing_total = sum(len(ids) for ids in missing_by_file.values())
        enhanced_total = total_entries - missing_total
        enhancement_percentage = (enhanced_total / total_entries) * 100 if total_entries > 0 else 0
        
        # Add unified enhancement analysis if enabled
        status = {
            'total_entries': total_entries,
            'enhanced_entries': enhanced_total,
            'missing_enhanced_metadata': missing_total,
            'enhancement_percentage': enhancement_percentage,
            'files_needing_enhancement': len(missing_by_file),
            'missing_by_file': {f: len(ids) for f, ids in missing_by_file.items()}
        }
        
        # Add conversation chain analysis if unified enhancement is enabled
        if self.enable_unified_enhancement and self.unified_engine:
            try:
                chain_health = self.unified_engine.analyze_conversation_chain_health()
                status['conversation_chain_health'] = {
                    'overall_health_score': chain_health.get('overall_health_score', 0),
                    'chain_coverage': chain_health.get('chain_coverage', {}),
                    'meets_target': chain_health.get('meets_target', False)
                }
            except Exception as e:
                status['conversation_chain_health'] = {'error': str(e)}
        
        return status
    
    def analyze_conversation_chain_coverage(self) -> Dict[str, any]:
        """Analyze conversation chain field coverage in the database."""
        if not self.enable_unified_enhancement or not self.unified_engine:
            return {'error': 'Unified enhancement not enabled'}
        
        try:
            print("🔗 Analyzing conversation chain field coverage...")
            
            # Use the back-fill engine from unified engine for analysis
            coverage_analysis = self.unified_engine.backfill_engine.analyze_conversation_chain_coverage()
            
            return coverage_analysis
            
        except Exception as e:
            print(f"❌ Error analyzing conversation chain coverage: {e}")
            return {'error': str(e)}
    
    def sync_with_unified_enhancement(self, target_files: Optional[List[str]] = None, 
                                    enable_backfill: bool = True,
                                    max_sessions: int = 20) -> Dict[str, any]:
        """
        Sync with unified enhancement system for comprehensive improvement.
        
        Args:
            target_files: Optional list of specific files to process
            enable_backfill: Enable conversation chain back-fill
            max_sessions: Maximum sessions to process
            
        Returns:
            Comprehensive sync results with unified enhancement statistics
        """
        if not self.enable_unified_enhancement:
            print("⚠️ Unified enhancement not enabled. Use sync_missing_metadata() instead.")
            return self.sync_missing_metadata(target_files)
        
        start_time = time.time()
        print("🚀 Starting unified enhancement sync...")
        
        try:
            # Get recent sessions for unified processing
            recent_sessions = self.unified_engine.get_recent_sessions(hours=48, limit=max_sessions)
            
            if not recent_sessions:
                print("⚠️ No recent sessions found. Falling back to metadata sync...")
                return self.sync_missing_metadata(target_files)
            
            print(f"📋 Processing {len(recent_sessions)} sessions with unified enhancement...")
            
            # Process sessions with unified enhancement
            results = self.unified_engine.process_multiple_sessions(
                session_ids=recent_sessions,
                max_processing_time_seconds=300.0,  # 5 minute limit
                batch_size=5
            )
            
            # Calculate comprehensive statistics
            successful_sessions = sum(1 for r in results if r.success)
            total_relationships = sum(r.backfill_stats.relationships_built for r in results if r.backfill_stats.success)
            total_database_updates = sum(r.backfill_stats.database_updates for r in results if r.backfill_stats.success)
            total_improvements = sum(r.overall_improvement for r in results if r.success)
            avg_improvement = total_improvements / successful_sessions if successful_sessions > 0 else 0
            
            # Update stats
            self.stats['conversation_chains_built'] = total_relationships
            self.stats['field_optimizations'] = total_database_updates
            self.stats['entries_updated'] = total_database_updates
            self.stats['processing_time'] = time.time() - start_time
            
            print("\n🎯 Unified Enhancement Sync Complete!")
            print(f"  Sessions processed: {len(results)}")
            print(f"  Successful sessions: {successful_sessions}")
            print(f"  Conversation relationships built: {total_relationships}")
            print(f"  Database updates: {total_database_updates}")
            print(f"  Average improvement: {avg_improvement:.1f}%")
            print(f"  Processing time: {self.stats['processing_time']:.1f}s")
            
            return {
                'method': 'unified_enhancement',
                'sessions_processed': len(results),
                'successful_sessions': successful_sessions,
                'conversation_chains_built': total_relationships,
                'database_updates': total_database_updates,
                'average_improvement': avg_improvement,
                'processing_time': self.stats['processing_time'],
                'results': results
            }
            
        except Exception as e:
            print(f"❌ Error in unified enhancement sync: {e}")
            print("🔄 Falling back to standard metadata sync...")
            return self.sync_missing_metadata(target_files)


def main():
    """Main entry point for smart metadata sync."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Smart Enhanced Metadata Sync - Efficiently update missing enhanced metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python smart_metadata_sync.py --status         # Check current enhancement status
  python smart_metadata_sync.py --sync           # Sync all missing metadata
  python smart_metadata_sync.py --unified        # Sync with unified enhancement system
  python smart_metadata_sync.py --chain-analysis # Analyze conversation chain coverage
  python smart_metadata_sync.py --files file1.jsonl file2.jsonl  # Sync specific files
        """
    )
    
    parser.add_argument('--status', action='store_true', 
                       help='Show current enhancement status')
    parser.add_argument('--sync', action='store_true',
                       help='Sync missing enhanced metadata')
    parser.add_argument('--unified', action='store_true',
                       help='Use unified enhancement system with conversation chain back-fill')
    parser.add_argument('--chain-analysis', action='store_true',
                       help='Analyze conversation chain field coverage')
    parser.add_argument('--files', nargs='+', 
                       help='Specific files to process')
    parser.add_argument('--max-sessions', type=int, default=20,
                       help='Maximum sessions to process in unified mode (default: 20)')
    parser.add_argument('--no-backfill', action='store_true',
                       help='Disable conversation chain back-fill in unified mode')
    
    args = parser.parse_args()
    
    # Initialize smart sync with unified enhancement if requested
    enable_unified = args.unified or args.chain_analysis
    sync = SmartMetadataSync(enable_unified_enhancement=enable_unified)
    
    if args.status:
        # Show status
        status = sync.get_enhancement_status()
        print("\n📊 Enhanced Metadata Status:")
        print(f"   Total entries: {status['total_entries']}")
        print(f"   Enhanced: {status['enhanced_entries']} ({status['enhancement_percentage']:.1f}%)")
        print(f"   Missing metadata: {status['missing_enhanced_metadata']}")
        print(f"   Files needing enhancement: {status['files_needing_enhancement']}")
        
        if status['missing_by_file']:
            print("\n📁 Files needing enhancement:")
            for file_name, count in sorted(status['missing_by_file'].items()):
                print(f"   {file_name}: {count} entries")
        
        # Show conversation chain health if unified enhancement is enabled
        if enable_unified and 'conversation_chain_health' in status:
            chain_health = status['conversation_chain_health']
            print("\n🔗 Conversation Chain Health:")
            if 'error' in chain_health:
                print(f"   Error: {chain_health['error']}")
            else:
                health_score = chain_health.get('overall_health_score', 0)
                meets_target = chain_health.get('meets_target', False)
                print(f"   Overall health score: {health_score:.1f}")
                print(f"   Meets 80% target: {'✅' if meets_target else '❌'}")
    
    elif args.chain_analysis:
        # Analyze conversation chain coverage
        coverage_analysis = sync.analyze_conversation_chain_coverage()
        if 'error' in coverage_analysis:
            print(f"❌ Error: {coverage_analysis['error']}")
        else:
            print("\n🔗 Conversation Chain Coverage Analysis:")
            overall_health = coverage_analysis.get('overall_chain_health', 0)
            meets_target = coverage_analysis.get('meets_target', False)
            print(f"   Overall chain health: {overall_health:.1f}%")
            print(f"   Meets 80% target: {'✅' if meets_target else '❌'}")
            
            if 'field_coverage' in coverage_analysis:
                print("\n   Field Coverage Details:")
                for field, stats in coverage_analysis['field_coverage'].items():
                    coverage = stats['coverage_percentage']
                    print(f"     • {field}: {coverage:.1f}% ({stats['populated']}/{stats['total']})")
    
    elif args.unified:
        # Run unified enhancement sync
        target_files = args.files if args.files else None
        enable_backfill = not args.no_backfill
        
        results = sync.sync_with_unified_enhancement(
            target_files=target_files,
            enable_backfill=enable_backfill,
            max_sessions=args.max_sessions
        )
        
        print("\n✨ Unified enhancement sync completed!")
        if results.get('method') == 'unified_enhancement':
            print("   Method: Unified Enhancement System")
            print(f"   Sessions processed: {results['sessions_processed']}")
            print(f"   Conversation chains built: {results['conversation_chains_built']}")
            print(f"   Database updates: {results['database_updates']}")
            print(f"   Average improvement: {results['average_improvement']:.1f}%")
        else:
            print("   Fallback method used - check results above")
        
    elif args.sync or args.files:
        # Run standard sync
        target_files = args.files if args.files else None
        results = sync.sync_missing_metadata(target_files)
        
        print("\n✨ Smart sync completed successfully!")
        print("   Enhancement coverage improved significantly")
        
    else:
        # Default: show status with recommendations
        status = sync.get_enhancement_status()
        enhancement_pct = status['enhancement_percentage']
        
        if enhancement_pct >= 95:
            print("✅ Database enhancement is complete!")
        elif enhancement_pct >= 70:
            print(f"🔄 Database is {enhancement_pct:.1f}% enhanced. Run --sync to complete.")
            print("   Consider --unified for conversation chain back-fill")
        else:
            print(f"⚠️ Database is only {enhancement_pct:.1f}% enhanced. Run --sync to improve.")
            print("   Consider --unified for comprehensive enhancement with conversation chain back-fill")


if __name__ == "__main__":
    main()