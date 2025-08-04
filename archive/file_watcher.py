"""
Real-time file watcher for Claude vector database incremental updates.

This module implements the core file watching functionality using watchdog
to monitor /home/user/.claude/projects/*.jsonl files and trigger incremental
database updates with sub-100ms detection and <200ms processing latency.
"""

import asyncio
import fcntl
import hashlib
import logging
import os
import time
from pathlib import Path
from typing import Dict, Optional, Set, Any
import psutil

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent

from config.watcher_config import (
    FileWatcherConfig, 
    FileChangeEvent, 
    ProcessingStats, 
    DEFAULT_CONFIG
)


class ConversationFileHandler(FileSystemEventHandler):
    """Handles file system events for conversation JSONL files.
    
    Filters events to only process relevant conversation files and
    queues them for incremental processing.
    """
    
    def __init__(self, watcher: 'ConversationFileWatcher'):
        super().__init__()
        self.watcher = watcher
        self.logger = logging.getLogger(__name__)
        self._last_processed: Dict[str, float] = {}  # Debounce rapid changes
    
    def on_any_event(self, event: FileSystemEvent):
        """Handle any file system event with filtering and debouncing."""
        if event.is_directory:
            return
        
        # Filter to only JSONL files
        if not any(Path(str(event.src_path)).match(pattern) 
                  for pattern in self.watcher.config.file_patterns):
            return
        
        # Skip ignored patterns
        if any(Path(str(event.src_path)).match(pattern) 
              for pattern in self.watcher.config.ignore_patterns):
            return
        
        # Debounce rapid changes to same file
        current_time = time.time()
        event_src_path = str(event.src_path)
        if (event_src_path in self._last_processed and 
            current_time - self._last_processed[event_src_path] < 
            self.watcher.config.content_change_debounce):
            return
        
        self._last_processed[event_src_path] = current_time
        
        # Queue event for processing (thread-safe)
        try:
            # Get the event loop from the main thread
            loop = self.watcher._main_loop
            if loop and not loop.is_closed():
                asyncio.run_coroutine_threadsafe(self._queue_file_event(event), loop)
        except Exception as e:
            self.logger.error(f"Error queuing file event: {e}")
            self.watcher.stats.errors += 1
    
    async def _queue_file_event(self, event: FileSystemEvent):
        """Queue a file event for processing with safety checks."""
        try:
            file_path = str(event.src_path)
            event_type = str(event.event_type)
            
            # Get file stats safely
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                file_size = stat.st_size
                last_modified = stat.st_mtime
            else:
                # File deleted
                file_size = 0
                last_modified = time.time()
            
            # Create change event
            change_event = FileChangeEvent(
                file_path=file_path,
                event_type=event_type,
                timestamp=time.time(),
                file_size=file_size,
                last_modified=last_modified
            )
            
            # Queue event (non-blocking)
            try:
                self.watcher.event_queue.put_nowait(change_event)
                self.logger.debug(f"Queued event: {change_event}")
            except asyncio.QueueFull:
                self.logger.warning(f"Event queue full, dropping event: {change_event}")
                self.watcher.stats.errors += 1
                
        except Exception as e:
            self.logger.error(f"Error processing file event {str(event.src_path)}: {e}")
            self.watcher.stats.errors += 1


class ConversationFileWatcher:
    """Real-time file watcher for conversation JSONL files.
    
    Monitors filesystem changes and queues events for incremental processing
    with performance requirements: <100ms detection, <200ms processing.
    """
    
    def __init__(self, config: Optional[FileWatcherConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.observer: Optional[Any] = None
        self.event_handler: Optional[ConversationFileHandler] = None
        self.event_queue: asyncio.Queue = asyncio.Queue(
            maxsize=self.config.queue_max_size
        )
        
        # State management
        self.is_running = False
        self.monitored_files: Set[str] = set()
        self.stats = ProcessingStats()
        self._shutdown_event = asyncio.Event()
        self._main_loop: Optional[Any] = None
        
        # Performance monitoring
        self._last_memory_check = 0
        self._process = psutil.Process()
    
    async def start(self) -> bool:
        """Start the file watcher system.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        try:
            if self.is_running:
                self.logger.warning("File watcher already running")
                return True
            
            # Check if auto-processing is disabled (Phase 2 migration)
            if not self.config.auto_processing_enabled:
                self.logger.info("🚫 File watcher auto-processing disabled - hooks handle real-time indexing")
                return True
            
            self.logger.info(f"Starting file watcher for: {self.config.watch_directory}")
            
            # Store the current event loop for thread-safe operation
            self._main_loop = asyncio.get_event_loop()
            
            # Initialize watchdog observer
            self.observer = Observer()
            self.event_handler = ConversationFileHandler(self)
            
            # Start monitoring the directory
            self.observer.schedule(
                self.event_handler,
                self.config.watch_directory,
                recursive=self.config.recursive
            )
            
            self.observer.start()
            self.is_running = True
            
            # Start background tasks
            asyncio.create_task(self._monitor_performance())
            asyncio.create_task(self._scan_existing_files())
            
            self.logger.info("File watcher started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start file watcher: {e}")
            await self.stop()
            return False
    
    async def stop(self):
        """Stop the file watcher system gracefully."""
        try:
            if not self.is_running:
                return
            
            self.logger.info("Stopping file watcher...")
            self.is_running = False
            self._shutdown_event.set()
            
            # Stop observer
            if self.observer:
                self.observer.stop()
                self.observer.join(timeout=5.0)
                self.observer = None
            
            # Clear event queue
            while not self.event_queue.empty():
                try:
                    self.event_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            self.logger.info("File watcher stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping file watcher: {e}")
    
    async def safe_file_access(self, file_path: str) -> bool:
        """Safely access a file with locking and retry logic.
        
        Implements file locking to handle concurrent access from Claude Code.
        Uses exponential backoff retry pattern as specified in PRP.
        
        Args:
            file_path: Path to file to access
            
        Returns:
            bool: True if file can be safely accessed, False otherwise
        """
        for attempt in range(self.config.file_read_retry_attempts):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    # Try to acquire shared lock (non-blocking)
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    
                    # Verify file is readable and not empty for JSONL
                    first_line = f.readline()
                    if first_line.strip():
                        return True
                    
            except (IOError, OSError, BlockingIOError) as e:
                delay = self.config.file_read_retry_delay * (2 ** attempt)
                self.logger.debug(
                    f"File access attempt {attempt + 1} failed for {file_path}: {e}. "
                    f"Retrying in {delay:.2f}s"
                )
                
                if attempt < self.config.file_read_retry_attempts - 1:
                    await asyncio.sleep(delay)
                else:
                    self.stats.file_lock_failures += 1
                    
            except Exception as e:
                self.logger.error(f"Unexpected error accessing {file_path}: {e}")
                break
        
        return False
    
    async def get_file_content_hash(self, file_path: str) -> Optional[str]:
        """Get content hash for change detection.
        
        Args:
            file_path: Path to file
            
        Returns:
            Optional[str]: Content hash or None if file cannot be read
        """
        try:
            if not await self.safe_file_access(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                hash_md5 = hashlib.md5()
                for chunk in iter(lambda: f.read(8192), b""):
                    hash_md5.update(chunk)
                return hash_md5.hexdigest()
                
        except Exception as e:
            self.logger.error(f"Error computing hash for {file_path}: {e}")
            return None
    
    async def has_file_changed(self, file_path: str, last_checksum: Optional[str] = None) -> bool:
        """Check if file has actually changed content.
        
        Args:
            file_path: Path to file to check
            last_checksum: Previous content checksum
            
        Returns:
            bool: True if file content has changed
        """
        if not os.path.exists(file_path):
            return last_checksum is not None  # File was deleted
        
        current_checksum = await self.get_file_content_hash(file_path)
        if current_checksum is None:
            return False  # Cannot read file
        
        return current_checksum != last_checksum
    
    async def _scan_existing_files(self):
        """Scan existing files on startup to populate monitored files set."""
        try:
            watch_path = Path(self.config.watch_directory)
            if not watch_path.exists():
                self.logger.warning(f"Watch directory does not exist: {watch_path}")
                return
            
            # Find all matching files
            for pattern in self.config.file_patterns:
                if self.config.recursive:
                    files = watch_path.rglob(pattern)
                else:
                    files = watch_path.glob(pattern)
                
                for file_path in files:
                    if file_path.is_file():
                        self.monitored_files.add(str(file_path))
            
            self.stats.files_monitored = len(self.monitored_files)
            self.logger.info(f"Monitoring {self.stats.files_monitored} existing files")
            
        except Exception as e:
            self.logger.error(f"Error scanning existing files: {e}")
    
    async def _monitor_performance(self):
        """Background task to monitor performance and update statistics."""
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Update memory usage
                current_time = time.time()
                if current_time - self._last_memory_check > self.config.memory_check_interval:
                    memory_info = self._process.memory_info()
                    self.stats.memory_usage_mb = memory_info.rss / 1024 / 1024
                    self._last_memory_check = current_time
                
                # Update queue size
                self.stats.queue_size = self.event_queue.qsize()
                
                # Check performance requirements
                if not self.stats.is_performance_acceptable(self.config):
                    self.logger.warning(
                        f"Performance degraded: "
                        f"latency={self.stats.processing_latency_avg:.3f}s, "
                        f"memory={self.stats.memory_usage_mb:.1f}MB"
                    )
                
                await asyncio.sleep(self.config.stats_update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(self.config.stats_update_interval)
    
    def get_status(self) -> Dict[str, Any]:
        """Get current watcher status and statistics.
        
        Returns:
            Dict containing status information for MCP tools
        """
        return {
            "status": "active" if self.is_running else "inactive",
            "health": self.stats.get_health_status(),
            "files_monitored": len(self.monitored_files),
            "events_processed": self.stats.events_processed,
            "entries_indexed": self.stats.entries_indexed,
            "queue_size": self.event_queue.qsize(),
            "memory_usage_mb": self.stats.memory_usage_mb,
            "processing_latency_avg": self.stats.processing_latency_avg,
            "detection_time_avg": self.stats.detection_time_avg,
            "events_per_second": self.stats.events_per_second,
            "entries_per_second": self.stats.entries_per_second,
            "errors": self.stats.errors,
            "last_update": self.stats.last_update.isoformat() if self.stats.last_update else None,
            "performance_acceptable": self.stats.is_performance_acceptable(self.config),
            "config": {
                "watch_directory": self.config.watch_directory,
                "batch_size": self.config.batch_size,
                "detection_timeout": self.config.detection_timeout,
                "processing_timeout": self.config.processing_timeout
            }
        }
    
    async def force_scan(self) -> Dict[str, Any]:
        """Force a manual scan of all monitored files.
        
        Returns:
            Dict with scan results for MCP tools
        """
        try:
            self.logger.info("Starting forced file scan...")
            scan_start = time.time()
            
            files_scanned = 0
            files_changed = 0
            
            for file_path in list(self.monitored_files):
                if await self.has_file_changed(file_path):
                    # Queue file for processing
                    change_event = FileChangeEvent(
                        file_path=file_path,
                        event_type="modified",
                        timestamp=time.time(),
                        file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        last_modified=os.path.getmtime(file_path) if os.path.exists(file_path) else 0
                    )
                    
                    try:
                        self.event_queue.put_nowait(change_event)
                        files_changed += 1
                    except asyncio.QueueFull:
                        self.logger.warning("Queue full during forced scan")
                        break
                
                files_scanned += 1
            
            scan_duration = time.time() - scan_start
            self.stats.recovery_scans += 1
            
            return {
                "success": True,
                "files_scanned": files_scanned,
                "files_changed": files_changed,
                "scan_duration": scan_duration,
                "timestamp": time.time()
            }
            
        except Exception as e:
            self.logger.error(f"Error during forced scan: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }


# Global file watcher instance (follows MCP server pattern)
file_watcher: Optional[ConversationFileWatcher] = None


async def initialize_file_watcher(config: Optional[FileWatcherConfig] = None) -> bool:
    """Initialize the global file watcher instance.
    
    Args:
        config: Optional configuration, uses default if not provided
        
    Returns:
        bool: True if initialized successfully
    """
    global file_watcher
    
    if file_watcher is not None and file_watcher.is_running:
        return True
    
    try:
        file_watcher = ConversationFileWatcher(config)
        return await file_watcher.start()
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to initialize file watcher: {e}")
        return False


async def shutdown_file_watcher():
    """Shutdown the global file watcher instance."""
    global file_watcher
    
    if file_watcher is not None:
        await file_watcher.stop()
        file_watcher = None