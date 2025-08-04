#!/usr/bin/env python3
"""
Enhanced Batch Conversation Sync Script with Progress Tracking

Processes conversation files in small batches (10-15 files) to stay within 
Claude Code's 2-minute timeout limits. Tracks progress across multiple runs
and can resume where it left off.

Features:
- Batch processing with configurable batch size
- Progress state file tracking
- Resume capability from last completed batch
- Enhanced conversation processing with all features
- Clear status updates and completion tracking
- Timeout-friendly execution
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from conversation_extractor import ConversationExtractor
from vector_database import ClaudeVectorDatabase

# Progress state file
STATE_FILE = Path("batch_sync_progress.json")

class BatchSyncState:
    """Manages batch processing state and progress tracking"""
    
    def __init__(self, state_file: Path = STATE_FILE):
        self.state_file = state_file
        self.state = self._load_state()
    
    def _load_state(self) -> Dict:
        """Load existing state or create new one"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠ Warning: Could not load state file: {e}")
                return self._create_new_state()
        else:
            return self._create_new_state()
    
    def _create_new_state(self) -> Dict:
        """Create new state structure"""
        return {
            "version": "1.0",
            "created_at": datetime.now().isoformat(),
            "total_files": 0,
            "files_processed": 0,
            "current_batch": 0,
            "completed_files": [],
            "batch_size": 12,
            "last_run_at": None,
            "totals": {
                "entries_added": 0,
                "entries_skipped": 0,
                "entries_errors": 0
            },
            "enhancement_stats": {
                "topics_detected": 0,
                "solutions_identified": 0,
                "feedback_analyzed": 0,
                "adjacency_relationships": 0
            },
            "status": "ready"  # ready, running, completed, error
        }
    
    def save_state(self):
        """Save current state to file"""
        self.state["last_run_at"] = datetime.now().isoformat()
        try:
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            print(f"⚠ Warning: Could not save state file: {e}")
    
    def reset_state(self):
        """Reset state for fresh start"""
        self.state = self._create_new_state()
        self.save_state()
        print("🔄 State reset - starting fresh batch sync")
    
    def mark_file_completed(self, file_path: str):
        """Mark a file as completed"""
        if file_path not in self.state["completed_files"]:
            self.state["completed_files"].append(file_path)
            self.state["files_processed"] += 1
    
    def is_file_completed(self, file_path: str) -> bool:
        """Check if file was already processed"""
        return file_path in self.state["completed_files"]
    
    def update_totals(self, added: int, skipped: int, errors: int):
        """Update running totals"""
        self.state["totals"]["entries_added"] += added
        self.state["totals"]["entries_skipped"] += skipped
        self.state["totals"]["entries_errors"] += errors
    
    def update_enhancement_stats(self, topics: int, solutions: int, feedback: int, adjacency: int):
        """Update enhancement statistics"""
        stats = self.state["enhancement_stats"]
        stats["topics_detected"] += topics
        stats["solutions_identified"] += solutions
        stats["feedback_analyzed"] += feedback
        stats["adjacency_relationships"] += adjacency
    
    def get_progress_percentage(self) -> float:
        """Calculate completion percentage"""
        if self.state["total_files"] == 0:
            return 0.0
        return (self.state["files_processed"] / self.state["total_files"]) * 100
    
    def is_completed(self) -> bool:
        """Check if all files have been processed"""
        return self.state["files_processed"] >= self.state["total_files"] and self.state["total_files"] > 0


def get_all_conversation_files() -> List[Path]:
    """Get sorted list of all conversation files"""
    claude_projects_dir = Path("/home/user/.claude/projects")
    return sorted(list(claude_projects_dir.rglob("*.jsonl")))


def run_batch_sync(batch_size: int = 12, reset: bool = False, show_stats: bool = False):
    """Run batch sync with progress tracking"""
    
    # Initialize state
    state_manager = BatchSyncState()
    
    if reset:
        state_manager.reset_state()
    
    if show_stats:
        show_progress_stats(state_manager)
        return
    
    # Get all files
    all_files = get_all_conversation_files()
    total_files = len(all_files)
    
    if total_files == 0:
        print("❌ No conversation files found")
        return
    
    # Update total files count if changed
    if state_manager.state["total_files"] != total_files:
        state_manager.state["total_files"] = total_files
    
    # Update batch size if different
    state_manager.state["batch_size"] = batch_size
    state_manager.state["status"] = "running"
    
    # Filter out already completed files
    remaining_files = [f for f in all_files if not state_manager.is_file_completed(str(f))]
    
    if not remaining_files:
        print("🎉 All files already processed! Sync is complete.")
        state_manager.state["status"] = "completed"
        state_manager.save_state()
        show_final_summary(state_manager)
        return
    
    # Calculate batch info
    current_batch = state_manager.state["current_batch"]
    files_to_process = remaining_files[:batch_size]
    
    print("🚀 Starting enhanced batch sync")
    print(f"📊 Progress: {state_manager.state['files_processed']}/{total_files} files completed ({state_manager.get_progress_percentage():.1f}%)")
    print(f"📦 Processing batch {current_batch + 1}: {len(files_to_process)} files")
    
    # Initialize components
    print("🔧 Initializing enhanced vector database and extractor...")
    db = ClaudeVectorDatabase()
    extractor = ConversationExtractor()
    
    # Process batch
    batch_stats = {
        "files_processed": 0,
        "entries_added": 0,
        "entries_skipped": 0,
        "entries_errors": 0,
        "topics": 0,
        "solutions": 0,
        "feedback": 0,
        "adjacency": 0
    }
    
    for i, file_path in enumerate(files_to_process, 1):
        print(f"\n📄 Processing file {i}/{len(files_to_process)}: {file_path.name}")
        
        try:
            # Extract entries with full enhancements
            print("  🔍 Extracting with enhancements...")
            enhanced_entries = list(extractor.extract_with_enhancements(file_path))
            
            if enhanced_entries:
                # Analyze enhancement coverage for this file
                file_topics = sum(1 for entry in enhanced_entries if entry.detected_topics)
                file_solutions = sum(1 for entry in enhanced_entries if entry.solution_quality_score > 1.0)
                file_feedback = sum(1 for entry in enhanced_entries if entry.user_feedback_sentiment)
                file_adjacency = sum(1 for entry in enhanced_entries if entry.previous_message_id or entry.next_message_id)
                
                batch_stats["topics"] += file_topics
                batch_stats["solutions"] += file_solutions
                batch_stats["feedback"] += file_feedback
                batch_stats["adjacency"] += file_adjacency
                
                print(f"  📊 Enhancements - Topics: {file_topics}, Solutions: {file_solutions}, Feedback: {file_feedback}, Adjacency: {file_adjacency}")
                
                # Add enhanced entries to vector database
                print(f"  💾 Adding {len(enhanced_entries)} enhanced entries to database...")
                result = db.batch_add_enhanced_entries(enhanced_entries, batch_size=50)
                
                added = result.get("added", 0)
                skipped = result.get("skipped", 0)
                errors = result.get("errors", 0)
                
                batch_stats["entries_added"] += added
                batch_stats["entries_skipped"] += skipped
                batch_stats["entries_errors"] += errors
                
                print(f"  ✅ Database - Added: {added}, Skipped: {skipped}, Errors: {errors}")
            else:
                print("  ⚠ No valid entries found in this file")
            
            # Mark file as completed
            state_manager.mark_file_completed(str(file_path))
            batch_stats["files_processed"] += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path.name}: {e}")
            batch_stats["entries_errors"] += 1
            # Still mark as completed to avoid reprocessing
            state_manager.mark_file_completed(str(file_path))
            batch_stats["files_processed"] += 1
    
    # Update state with batch results
    state_manager.update_totals(
        batch_stats["entries_added"],
        batch_stats["entries_skipped"], 
        batch_stats["entries_errors"]
    )
    state_manager.update_enhancement_stats(
        batch_stats["topics"],
        batch_stats["solutions"],
        batch_stats["feedback"],
        batch_stats["adjacency"]
    )
    state_manager.state["current_batch"] += 1
    
    # Check if completed
    if state_manager.is_completed():
        state_manager.state["status"] = "completed"
        print("\n🎉 BATCH SYNC COMPLETE!")
        show_final_summary(state_manager)
    else:
        remaining_count = total_files - state_manager.state["files_processed"]
        estimated_batches = (remaining_count + batch_size - 1) // batch_size
        print(f"\n📈 Batch {current_batch + 1} complete!")
        print(f"📊 Progress: {state_manager.state['files_processed']}/{total_files} files ({state_manager.get_progress_percentage():.1f}%)")
        print(f"⏳ Estimated batches remaining: {estimated_batches}")
        print("🔄 Run the script again to continue processing")
    
    # Save state
    state_manager.save_state()
    
    # Show batch summary
    print("\n📦 Batch Summary:")
    print(f"  Files processed: {batch_stats['files_processed']}")
    print(f"  Entries added: {batch_stats['entries_added']}")
    print(f"  Enhancements: {batch_stats['topics']} topics, {batch_stats['solutions']} solutions")


def show_progress_stats(state_manager: BatchSyncState):
    """Show current progress statistics"""
    state = state_manager.state
    
    print("📊 Enhanced Batch Sync Progress")
    print("="*50)
    print(f"Status: {state['status'].upper()}")
    print(f"Progress: {state['files_processed']}/{state['total_files']} files ({state_manager.get_progress_percentage():.1f}%)")
    print(f"Current batch: {state['current_batch']}")
    print(f"Batch size: {state['batch_size']} files")
    
    if state.get("last_run_at"):
        print(f"Last run: {state['last_run_at']}")
    
    print("\n📈 Database Totals:")
    totals = state["totals"]
    print(f"  Entries added: {totals['entries_added']:,}")
    print(f"  Entries skipped: {totals['entries_skipped']:,}")
    print(f"  Errors: {totals['entries_errors']:,}")
    
    print("\n🧠 Enhancement Statistics:")
    stats = state["enhancement_stats"]
    print(f"  Topics detected: {stats['topics_detected']:,}")
    print(f"  Solutions identified: {stats['solutions_identified']:,}")
    print(f"  Feedback analyzed: {stats['feedback_analyzed']:,}")
    print(f"  Adjacency relationships: {stats['adjacency_relationships']:,}")
    
    if state["status"] == "completed":
        print("\n🎉 Sync completed successfully!")
    elif state["files_processed"] > 0:
        remaining = state["total_files"] - state["files_processed"]
        estimated_batches = (remaining + state["batch_size"] - 1) // state["batch_size"]
        print(f"\n⏳ Remaining: {remaining} files (~{estimated_batches} batches)")


def show_final_summary(state_manager: BatchSyncState):
    """Show final completion summary"""
    state = state_manager.state
    
    print("\n🎯 Enhanced Batch Sync Complete!")
    print("="*50)
    print(f"Total files processed: {state['files_processed']}")
    print(f"Total batches: {state['current_batch']}")
    
    totals = state["totals"]
    print("\n📊 Database Results:")
    print(f"  Entries added: {totals['entries_added']:,}")
    print(f"  Entries skipped: {totals['entries_skipped']:,}")
    print(f"  Total errors: {totals['entries_errors']:,}")
    
    stats = state["enhancement_stats"]
    print("\n🧠 Enhancement Results:")
    print(f"  Topics detected: {stats['topics_detected']:,}")
    print(f"  Solutions identified: {stats['solutions_identified']:,}")
    print(f"  Feedback analyzed: {stats['feedback_analyzed']:,}")
    print(f"  Adjacency relationships: {stats['adjacency_relationships']:,}")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced Batch Conversation Sync with Progress Tracking",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_enhanced_batch_sync.py                    # Continue from last position
  python run_enhanced_batch_sync.py --batch-size 15    # Process 15 files per batch
  python run_enhanced_batch_sync.py --reset            # Reset and start fresh
  python run_enhanced_batch_sync.py --stats            # Show current progress
  python run_enhanced_batch_sync.py --batch-size 10    # Smaller batches for slower systems
        """
    )
    
    parser.add_argument(
        '--batch-size', 
        type=int, 
        default=12, 
        help='Number of files to process per batch (default: 12, stays within 2-minute timeout)'
    )
    
    parser.add_argument(
        '--reset', 
        action='store_true',
        help='Reset progress and start fresh (deletes existing state)'
    )
    
    parser.add_argument(
        '--stats', 
        action='store_true',
        help='Show current progress statistics without processing'
    )
    
    args = parser.parse_args()
    
    # Validate batch size
    if args.batch_size < 1 or args.batch_size > 50:
        print("❌ Batch size must be between 1 and 50")
        return
    
    if args.batch_size > 20:
        print(f"⚠ Warning: Batch size {args.batch_size} may exceed 2-minute timeout")
    
    print("🚀 Enhanced Batch Sync Starting...")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    run_batch_sync(
        batch_size=args.batch_size,
        reset=args.reset,
        show_stats=args.stats
    )


if __name__ == "__main__":
    main()