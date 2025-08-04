"""
Incremental processor for real-time conversation indexing.

This module handles event processing from the file watcher, manages adaptive
batching for ChromaDB operations, and ensures performance requirements are met:
- <200ms processing latency
- >1000 entries/sec processing rate
- Respect ChromaDB 166-item batch limit
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import List, Optional, Dict, Set, Any

from config.watcher_config import (
    FileWatcherConfig, 
    FileChangeEvent, 
    ProcessingStats,
    DEFAULT_CONFIG
)
from conversation_extractor import ConversationEntry, ConversationExtractor


class AdaptiveBatchManager:
    """Manages adaptive batching for ChromaDB operations.
    
    Adjusts batch sizes based on performance metrics while respecting
    the ChromaDB SQLite constraint limit of 166 items per batch.
    """
    
    def __init__(self, config: FileWatcherConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Adaptive sizing
        self.current_batch_size = config.batch_size
        self.min_batch_size = 10
        self.max_batch_size = config.max_batch_size  # 166 ChromaDB limit
        
        # Performance tracking
        self._recent_processing_times: List[float] = []
        self._recent_batch_sizes: List[int] = []
        self._adjustment_cooldown = 0
        
    def adjust_batch_size(self, processing_time: float, entries_processed: int):
        """Adjust batch size based on recent performance.
        
        Args:
            processing_time: Time taken to process last batch
            entries_processed: Number of entries in last batch
        """
        self._recent_processing_times.append(processing_time)
        self._recent_batch_sizes.append(entries_processed)
        
        # Keep only recent measurements (last 10 batches)
        if len(self._recent_processing_times) > 10:
            self._recent_processing_times.pop(0)
            self._recent_batch_sizes.pop(0)
        
        # Avoid frequent adjustments
        if self._adjustment_cooldown > 0:
            self._adjustment_cooldown -= 1
            return
        
        if len(self._recent_processing_times) < 3:
            return  # Need more data
        
        avg_processing_time = sum(self._recent_processing_times) / len(self._recent_processing_times)
        
        # Adjust based on performance target (<200ms)
        if avg_processing_time > self.config.processing_timeout * 0.8:  # 160ms threshold
            # Performance degrading, reduce batch size
            new_size = max(self.min_batch_size, int(self.current_batch_size * 0.8))
            if new_size != self.current_batch_size:
                self.logger.info(f"Reducing batch size: {self.current_batch_size} -> {new_size} "
                               f"(avg_time={avg_processing_time:.3f}s)")
                self.current_batch_size = new_size
                self._adjustment_cooldown = 5
                
        elif avg_processing_time < self.config.processing_timeout * 0.3:  # 60ms threshold
            # Performance good, try increasing batch size
            new_size = min(self.max_batch_size, int(self.current_batch_size * 1.2))
            if new_size != self.current_batch_size:
                self.logger.info(f"Increasing batch size: {self.current_batch_size} -> {new_size} "
                               f"(avg_time={avg_processing_time:.3f}s)")
                self.current_batch_size = new_size
                self._adjustment_cooldown = 5
    
    def chunk_entries(self, entries: List[ConversationEntry]) -> List[List[ConversationEntry]]:
        """Chunk entries into appropriately sized batches.
        
        Args:
            entries: List of conversation entries to chunk
            
        Returns:
            List of entry batches respecting size limits
        """
        if not entries:
            return []
        
        chunks = []
        for i in range(0, len(entries), self.max_batch_size):
            chunk = entries[i:i + self.max_batch_size]
            chunks.append(chunk)
        
        return chunks


class IncrementalProcessor:
    """Processes file change events and updates the vector database incrementally.
    
    Handles event queue processing, conversation extraction, and database updates
    with performance monitoring and adaptive batching.
    """
    
    def __init__(self, 
                 vector_db,  # ClaudeVectorDatabase instance
                 extractor: Optional[ConversationExtractor] = None,
                 config: Optional[FileWatcherConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.vector_db = vector_db
        self.extractor = extractor or ConversationExtractor()
        self.batch_manager = AdaptiveBatchManager(self.config)
        
        # Processing state
        self.is_processing = False
        self.processed_files: Dict[str, str] = {}  # file_path -> content_hash
        self.stats = ProcessingStats()
        
        # Event tracking
        self._pending_events: List[FileChangeEvent] = []
        self._processing_lock = asyncio.Lock()
        self._shutdown_event = asyncio.Event()
    
    async def start_processing(self, event_queue: asyncio.Queue):
        """Start processing events from the file watcher queue.
        
        Args:
            event_queue: Queue of FileChangeEvent objects to process
        """
        if self.is_processing:
            self.logger.warning("Incremental processor already running")
            return
        
        self.is_processing = True
        self.logger.info("Starting incremental processor")
        
        # Start processing task
        asyncio.create_task(self._process_events_loop(event_queue))
        
    async def stop_processing(self):
        """Stop processing events gracefully."""
        if not self.is_processing:
            return
            
        self.logger.info("Stopping incremental processor...")
        self.is_processing = False
        self._shutdown_event.set()
        
        # Process any remaining events
        async with self._processing_lock:
            if self._pending_events:
                await self._process_pending_events()
    
    async def _process_events_loop(self, event_queue: asyncio.Queue):
        """Main event processing loop."""
        batch_timeout = self.config.processing_timeout / 2  # 100ms batch timeout
        
        while self.is_processing and not self._shutdown_event.is_set():
            try:
                # Collect events for batching
                events_collected = 0
                batch_start_time = time.time()
                
                # Collect events up to batch size or timeout
                while (events_collected < self.batch_manager.current_batch_size and
                       time.time() - batch_start_time < batch_timeout):
                    
                    try:
                        # Wait for event with timeout
                        remaining_timeout = batch_timeout - (time.time() - batch_start_time)
                        if remaining_timeout <= 0:
                            break
                            
                        event = await asyncio.wait_for(
                            event_queue.get(), 
                            timeout=remaining_timeout
                        )
                        
                        self._pending_events.append(event)
                        events_collected += 1
                        
                    except asyncio.TimeoutError:
                        break  # Batch timeout reached
                    
                # Process collected events
                if self._pending_events:
                    async with self._processing_lock:
                        await self._process_pending_events()
                
            except Exception as e:
                self.logger.error(f"Error in event processing loop: {e}")
                await asyncio.sleep(1.0)  # Prevent tight error loop
    
    async def _process_pending_events(self):
        """Process all pending events in batch."""
        if not self._pending_events:
            return
        
        processing_start_time = time.time()
        
        try:
            # Group events by file for efficient processing
            file_events: Dict[str, FileChangeEvent] = {}
            
            for event in self._pending_events:
                # Keep only the latest event per file
                file_events[event.file_path] = event
            
            # Process files and extract entries
            all_entries: List[ConversationEntry] = []
            
            for file_path, event in file_events.items():
                entries = await self._process_file_event(event)
                if entries:
                    all_entries.extend(entries)
            
            # Batch update database
            if all_entries:
                await self._batch_update_database(all_entries)
            
            # Update statistics
            processing_time = time.time() - processing_start_time
            self.stats.update_performance_metrics(processing_time, len(all_entries))
            
            # Adjust batch size based on performance
            self.batch_manager.adjust_batch_size(processing_time, len(all_entries))
            
            # Clear processed events
            self._pending_events.clear()
            
            self.logger.debug(
                f"Processed {len(file_events)} files with {len(all_entries)} entries "
                f"in {processing_time:.3f}s"
            )
            
        except Exception as e:
            self.logger.error(f"Error processing pending events: {e}")
            self.stats.errors += 1
            # Don't clear events on error - they'll be retried
    
    async def _process_file_event(self, event: FileChangeEvent) -> List[ConversationEntry]:
        """Process a single file change event.
        
        Args:
            event: File change event to process
            
        Returns:
            List of new conversation entries from the file
        """
        file_path = Path(event.file_path)
        
        try:
            # Handle file deletion
            if event.event_type == "deleted" or not file_path.exists():
                if event.file_path in self.processed_files:
                    del self.processed_files[event.file_path]
                    self.logger.info(f"File deleted, removed from tracking: {file_path}")
                return []
            
            # Check if file has actually changed content
            current_hash = await self._get_file_content_hash(file_path)
            if current_hash is None:
                self.logger.warning(f"Cannot read file: {file_path}")
                return []
            
            # Skip if content hasn't changed
            if (event.file_path in self.processed_files and 
                self.processed_files[event.file_path] == current_hash):
                return []
            
            # Extract new entries from file
            entries = await self._extract_new_entries(file_path, event)
            
            # Update processed files tracking
            self.processed_files[event.file_path] = current_hash
            
            return entries
            
        except Exception as e:
            self.logger.error(f"Error processing file event {event.file_path}: {e}")
            self.stats.errors += 1
            return []
    
    async def _extract_new_entries(self, file_path: Path, event: FileChangeEvent) -> List[ConversationEntry]:
        """Extract new conversation entries from a file.
        
        Args:
            file_path: Path to JSONL file
            event: File change event context
            
        Returns:
            List of new conversation entries
        """
        try:
            # For incremental processing, we need to handle different scenarios:
            # 1. New file: extract all entries
            # 2. Modified file: extract only new entries (challenging without file position tracking)
            # 3. For now, we'll extract all entries and rely on database deduplication
            
            entries = []
            
            # Use the existing extractor to get entries
            for entry in self.extractor.extract_from_jsonl_file(file_path):
                entries.append(entry)
            
            # Filter to only new entries based on timestamp if this is a modification
            if event.event_type == "modified" and event.file_path in self.processed_files:
                # For now, we'll process all entries and let the database handle deduplication
                # A more sophisticated approach would track file positions/line numbers
                pass
            
            self.logger.debug(f"Extracted {len(entries)} entries from {file_path}")
            return entries
            
        except Exception as e:
            self.logger.error(f"Error extracting entries from {file_path}: {e}")
            return []
    
    async def _batch_update_database(self, entries: List[ConversationEntry]):
        """Update database with entries in appropriate batches.
        
        Args:
            entries: List of conversation entries to add to database
        """
        if not entries:
            return
        
        try:
            # Chunk entries respecting ChromaDB limits
            chunks = self.batch_manager.chunk_entries(entries)
            
            for chunk in chunks:
                batch_start_time = time.time()
                
                # Use the enhanced vector database batch method
                success = await self.vector_db.batch_add_entries(chunk)
                
                batch_time = time.time() - batch_start_time
                
                if success:
                    self.logger.debug(
                        f"Successfully added batch of {len(chunk)} entries "
                        f"in {batch_time:.3f}s"
                    )
                else:
                    self.logger.error(f"Failed to add batch of {len(chunk)} entries")
                    self.stats.batch_failures += 1
                
        except Exception as e:
            self.logger.error(f"Error in batch database update: {e}")
            self.stats.errors += 1
    
    async def _get_file_content_hash(self, file_path: Path) -> Optional[str]:
        """Get content hash for change detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            Optional[str]: Content hash or None if file cannot be read
        """
        try:
            import hashlib
            
            with open(file_path, 'rb') as f:
                hash_md5 = hashlib.md5()
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
                return hash_md5.hexdigest()
                
        except Exception as e:
            self.logger.error(f"Error computing hash for {file_path}: {e}")
            return None
    
    def get_processing_status(self) -> Dict[str, Any]:
        """Get current processing status and statistics.
        
        Returns:
            Dict containing processing status for monitoring
        """
        return {
            "is_processing": self.is_processing,
            "pending_events": len(self._pending_events),
            "processed_files": len(self.processed_files),
            "current_batch_size": self.batch_manager.current_batch_size,
            "stats": {
                "events_processed": self.stats.events_processed,
                "entries_indexed": self.stats.entries_indexed,
                "processing_latency_avg": self.stats.processing_latency_avg,
                "entries_per_second": self.stats.entries_per_second,
                "errors": self.stats.errors,
                "batch_failures": self.stats.batch_failures,
                "last_update": self.stats.last_update.isoformat() if self.stats.last_update else None
            }
        }
    
    async def force_process_all_files(self, monitored_files: Set[str]) -> Dict[str, Any]:
        """Force processing of all monitored files.
        
        Args:
            monitored_files: Set of file paths to process
            
        Returns:
            Dict with processing results
        """
        try:
            self.logger.info(f"Force processing {len(monitored_files)} files...")
            
            start_time = time.time()
            all_entries = []
            files_processed = 0
            
            for file_path in monitored_files:
                try:
                    path_obj = Path(file_path)
                    if path_obj.exists():
                        # Create a synthetic event for processing
                        event = FileChangeEvent(
                            file_path=file_path,
                            event_type="modified",
                            timestamp=time.time(),
                            file_size=path_obj.stat().st_size,
                            last_modified=path_obj.stat().st_mtime
                        )
                        
                        entries = await self._process_file_event(event)
                        if entries:
                            all_entries.extend(entries)
                        
                        files_processed += 1
                        
                except Exception as e:
                    self.logger.error(f"Error force processing {file_path}: {e}")
            
            # Batch update database
            if all_entries:
                await self._batch_update_database(all_entries)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "files_processed": files_processed,
                "entries_processed": len(all_entries),
                "processing_time": processing_time,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error in force process all files: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }


# Global processor instance (follows MCP server pattern)
incremental_processor: Optional[IncrementalProcessor] = None


async def initialize_incremental_processor(vector_db, 
                                         extractor: Optional[ConversationExtractor] = None,
                                         config: Optional[FileWatcherConfig] = None) -> bool:
    """Initialize the global incremental processor instance.
    
    Args:
        vector_db: ClaudeVectorDatabase instance
        extractor: Optional conversation extractor
        config: Optional configuration
        
    Returns:
        bool: True if initialized successfully
    """
    global incremental_processor
    
    if incremental_processor is not None and incremental_processor.is_processing:
        return True
    
    try:
        incremental_processor = IncrementalProcessor(vector_db, extractor, config)
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to initialize incremental processor: {e}")
        return False


async def shutdown_incremental_processor():
    """Shutdown the global incremental processor instance."""
    global incremental_processor
    
    if incremental_processor is not None:
        await incremental_processor.stop_processing()
        incremental_processor = None