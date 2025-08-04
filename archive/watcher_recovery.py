"""
Recovery and checkpoint system for the file watcher.

Provides checkpoint persistence, recovery scans, and error handling
to ensure 99.9% uptime reliability and zero data loss during
file watching operations.
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Optional, Any
import threading

from config.watcher_config import (
    FileWatcherConfig,
    FileChangeEvent,
    ProcessingStats,
    DEFAULT_CONFIG
)


class FileWatcherCheckpoint:
    """Manages checkpoint persistence for file watcher state.
    
    Tracks processed files, last modification times, and processing
    state to enable recovery after system crashes or restarts.
    """
    
    def __init__(self, config: FileWatcherConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Checkpoint file path
        self.checkpoint_path = Path("/home/user/.claude-vector-db") / config.checkpoint_file
        
        # Checkpoint data
        self._checkpoint_data: Dict[str, Any] = {
            "version": "1.0",
            "last_checkpoint": None,
            "processed_files": {},  # file_path -> {"last_modified": float, "content_hash": str, "last_processed": float}
            "processing_stats": {},
            "recovery_info": {
                "last_recovery_scan": None,
                "missed_events": 0,
                "total_recoveries": 0
            }
        }
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Load existing checkpoint
        self._load_checkpoint()
    
    def _load_checkpoint(self):
        """Load checkpoint data from disk."""
        try:
            if self.checkpoint_path.exists():
                with open(self.checkpoint_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                # Validate checkpoint version
                if data.get("version") == "1.0":
                    self._checkpoint_data = data
                    self.logger.info(f"Loaded checkpoint with {len(data.get('processed_files', {}))} files")
                else:
                    self.logger.warning(f"Unsupported checkpoint version: {data.get('version')}")
                    self._create_new_checkpoint()
            else:
                self._create_new_checkpoint()
                
        except Exception as e:
            self.logger.error(f"Error loading checkpoint: {e}")
            self._create_new_checkpoint()
    
    def _create_new_checkpoint(self):
        """Create a new checkpoint file."""
        self._checkpoint_data = {
            "version": "1.0",
            "last_checkpoint": time.time(),
            "processed_files": {},
            "processing_stats": {},
            "recovery_info": {
                "last_recovery_scan": None,
                "missed_events": 0,
                "total_recoveries": 0
            }
        }
        self._save_checkpoint()
        self.logger.info("Created new checkpoint file")
    
    def _save_checkpoint(self):
        """Save checkpoint data to disk."""
        with self._lock:
            try:
                # Update timestamp
                self._checkpoint_data["last_checkpoint"] = time.time()
                
                # Ensure directory exists
                self.checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write atomically using temporary file
                temp_path = self.checkpoint_path.with_suffix('.tmp')
                with open(temp_path, 'w', encoding='utf-8') as f:
                    json.dump(self._checkpoint_data, f, indent=2, default=str)
                
                # Atomic rename
                temp_path.replace(self.checkpoint_path)
                
            except Exception as e:
                self.logger.error(f"Error saving checkpoint: {e}")
    
    def update_file_processed(self, file_path: str, last_modified: float, content_hash: str):
        """Update checkpoint with processed file information.
        
        Args:
            file_path: Path to processed file
            last_modified: File modification timestamp
            content_hash: Content hash for change detection
        """
        with self._lock:
            self._checkpoint_data["processed_files"][file_path] = {
                "last_modified": last_modified,
                "content_hash": content_hash,
                "last_processed": time.time()
            }
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get checkpoint information for a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Dict with file checkpoint info or None if not found
        """
        with self._lock:
            return self._checkpoint_data["processed_files"].get(file_path)
    
    def update_processing_stats(self, stats: ProcessingStats):
        """Update checkpoint with processing statistics.
        
        Args:
            stats: Current processing statistics
        """
        with self._lock:
            self._checkpoint_data["processing_stats"] = {
                "events_processed": stats.events_processed,
                "entries_indexed": stats.entries_indexed,
                "files_monitored": stats.files_monitored,
                "processing_time_total": stats.processing_time_total,
                "errors": stats.errors,
                "last_update": stats.last_update.isoformat() if stats.last_update else None
            }
    
    def record_recovery_scan(self, files_scanned: int, changes_found: int):
        """Record recovery scan results.
        
        Args:
            files_scanned: Number of files scanned
            changes_found: Number of changes detected
        """
        with self._lock:
            recovery_info = self._checkpoint_data["recovery_info"]
            recovery_info["last_recovery_scan"] = time.time()
            recovery_info["total_recoveries"] += 1
            
            if changes_found > 0:
                recovery_info["missed_events"] += changes_found
                self.logger.info(f"Recovery scan found {changes_found} missed changes in {files_scanned} files")
    
    def save_checkpoint(self):
        """Public method to save checkpoint."""
        self._save_checkpoint()
    
    def get_checkpoint_data(self) -> Dict[str, Any]:
        """Get current checkpoint data.
        
        Returns:
            Dict containing checkpoint information
        """
        with self._lock:
            return self._checkpoint_data.copy()


class WatcherRecoverySystem:
    """Recovery system for file watcher operations.
    
    Handles periodic recovery scans, missed event detection,
    and automatic recovery from system failures.
    """
    
    def __init__(self, 
                 file_watcher,  # ConversationFileWatcher instance
                 incremental_processor,  # IncrementalProcessor instance
                 config: Optional[FileWatcherConfig] = None):
        self.config = config or DEFAULT_CONFIG
        self.logger = logging.getLogger(__name__)
        
        # Core components
        self.file_watcher = file_watcher
        self.incremental_processor = incremental_processor
        self.checkpoint = FileWatcherCheckpoint(self.config)
        
        # Recovery state
        self.is_running = False
        self._recovery_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()
        
        # Statistics
        self.recovery_stats = {
            "scans_performed": 0,
            "files_recovered": 0,
            "total_recovery_time": 0.0,
            "last_scan_time": None,
            "errors": 0
        }
    
    async def start_recovery_system(self):
        """Start the recovery system with periodic scans."""
        if self.is_running:
            self.logger.warning("Recovery system already running")
            return
        
        self.is_running = True
        self.logger.info(f"Starting recovery system with {self.config.recovery_scan_interval}s intervals")
        
        # Start recovery task
        self._recovery_task = asyncio.create_task(self._recovery_loop())
        
        # Start checkpoint saving task
        asyncio.create_task(self._checkpoint_loop())
    
    async def stop_recovery_system(self):
        """Stop the recovery system gracefully."""
        if not self.is_running:
            return
        
        self.logger.info("Stopping recovery system...")
        self.is_running = False
        self._shutdown_event.set()
        
        # Cancel recovery task
        if self._recovery_task:
            self._recovery_task.cancel()
            try:
                await self._recovery_task
            except asyncio.CancelledError:
                pass
        
        # Save final checkpoint
        self.checkpoint.save_checkpoint()
        self.logger.info("Recovery system stopped")
    
    async def _recovery_loop(self):
        """Main recovery loop with periodic scans."""
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Wait for next scan interval
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.recovery_scan_interval
                )
                break  # Shutdown requested
                
            except asyncio.TimeoutError:
                # Time for recovery scan
                await self.perform_recovery_scan()
    
    async def _checkpoint_loop(self):
        """Periodic checkpoint saving loop."""
        while self.is_running and not self._shutdown_event.is_set():
            try:
                # Wait for next checkpoint interval
                await asyncio.wait_for(
                    self._shutdown_event.wait(),
                    timeout=self.config.checkpoint_interval
                )
                break  # Shutdown requested
                
            except asyncio.TimeoutError:
                # Time to save checkpoint
                if self.file_watcher and hasattr(self.file_watcher, 'stats'):
                    self.checkpoint.update_processing_stats(self.file_watcher.stats)
                    self.checkpoint.save_checkpoint()
    
    async def perform_recovery_scan(self) -> Dict[str, Any]:
        """Perform a comprehensive recovery scan.
        
        Scans all monitored files for changes that may have been missed
        by the file watcher and queues them for processing.
        
        Returns:
            Dict with recovery scan results
        """
        try:
            self.logger.info("Starting recovery scan...")
            scan_start_time = time.time()
            
            # Get monitored files
            if not self.file_watcher or not hasattr(self.file_watcher, 'monitored_files'):
                self.logger.warning("File watcher not available for recovery scan")
                return {"success": False, "error": "File watcher not available"}
            
            monitored_files = self.file_watcher.monitored_files.copy()
            
            files_scanned = 0
            changes_detected = 0
            files_recovered = 0
            
            for file_path in monitored_files:
                try:
                    # Check if file still exists
                    path_obj = Path(file_path)
                    if not path_obj.exists():
                        # File was deleted, update checkpoint
                        checkpoint_info = self.checkpoint.get_file_info(file_path)
                        if checkpoint_info:
                            self.logger.debug(f"File deleted: {file_path}")
                            # Remove from checkpoint
                            with self.checkpoint._lock:
                                if file_path in self.checkpoint._checkpoint_data["processed_files"]:
                                    del self.checkpoint._checkpoint_data["processed_files"][file_path]
                        files_scanned += 1
                        continue
                    
                    # Get current file state
                    stat = path_obj.stat()
                    current_modified = stat.st_mtime
                    
                    # Check against checkpoint
                    checkpoint_info = self.checkpoint.get_file_info(file_path)
                    needs_processing = False
                    
                    if not checkpoint_info:
                        # New file not in checkpoint
                        needs_processing = True
                        self.logger.debug(f"New file detected: {file_path}")
                    else:
                        # Check if modified since last processing
                        last_modified = checkpoint_info.get("last_modified", 0)
                        if current_modified > last_modified:
                            needs_processing = True
                            self.logger.debug(f"Modified file detected: {file_path}")
                    
                    if needs_processing:
                        # Queue file for processing
                        if await self._queue_file_for_recovery(file_path, current_modified):
                            changes_detected += 1
                            files_recovered += 1
                    
                    files_scanned += 1
                    
                except Exception as e:
                    self.logger.error(f"Error scanning file {file_path}: {e}")
                    self.recovery_stats["errors"] += 1
            
            # Update statistics
            scan_duration = time.time() - scan_start_time
            self.recovery_stats["scans_performed"] += 1
            self.recovery_stats["files_recovered"] += files_recovered
            self.recovery_stats["total_recovery_time"] += scan_duration
            self.recovery_stats["last_scan_time"] = time.time()
            
            # Record in checkpoint
            self.checkpoint.record_recovery_scan(files_scanned, changes_detected)
            
            result = {
                "success": True,
                "files_scanned": files_scanned,
                "changes_detected": changes_detected,
                "files_recovered": files_recovered,
                "scan_duration": scan_duration,
                "timestamp": time.time()
            }
            
            if changes_detected > 0:
                self.logger.info(
                    f"Recovery scan completed: {changes_detected} changes detected "
                    f"in {files_scanned} files ({scan_duration:.2f}s)"
                )
            else:
                self.logger.debug(f"Recovery scan completed: no changes in {files_scanned} files")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in recovery scan: {e}")
            self.recovery_stats["errors"] += 1
            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }
    
    async def _queue_file_for_recovery(self, file_path: str, last_modified: float) -> bool:
        """Queue a file for recovery processing.
        
        Args:
            file_path: Path to file needing recovery
            last_modified: File modification timestamp
            
        Returns:
            bool: True if successfully queued
        """
        try:
            # Create recovery event
            recovery_event = FileChangeEvent(
                file_path=file_path,
                event_type="recovery",
                timestamp=time.time(),
                file_size=os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                last_modified=last_modified
            )
            
            # Queue for processing
            if self.file_watcher and hasattr(self.file_watcher, 'event_queue'):
                try:
                    self.file_watcher.event_queue.put_nowait(recovery_event)
                    return True
                except asyncio.QueueFull:
                    self.logger.warning(f"Queue full, cannot recover file: {file_path}")
                    return False
            else:
                self.logger.warning("File watcher queue not available for recovery")
                return False
                
        except Exception as e:
            self.logger.error(f"Error queuing file for recovery {file_path}: {e}")
            return False
    
    async def force_recovery_all_files(self) -> Dict[str, Any]:
        """Force recovery processing of all monitored files.
        
        Returns:
            Dict with recovery results
        """
        try:
            self.logger.info("Starting forced recovery of all files...")
            
            if not self.incremental_processor:
                return {"success": False, "error": "Incremental processor not available"}
            
            # Get monitored files
            monitored_files = set()
            if self.file_watcher and hasattr(self.file_watcher, 'monitored_files'):
                monitored_files = self.file_watcher.monitored_files.copy()
            
            # Use incremental processor to force process all files
            result = await self.incremental_processor.force_process_all_files(monitored_files)
            
            if result.get("success"):
                # Update checkpoints for all processed files
                for file_path in monitored_files:
                    try:
                        if os.path.exists(file_path):
                            stat = os.stat(file_path)
                            # Generate content hash
                            import hashlib
                            with open(file_path, 'rb') as f:
                                content_hash = hashlib.md5(f.read()).hexdigest()
                            
                            self.checkpoint.update_file_processed(
                                file_path, stat.st_mtime, content_hash
                            )
                    except Exception as e:
                        self.logger.error(f"Error updating checkpoint for {file_path}: {e}")
                
                # Save checkpoint
                self.checkpoint.save_checkpoint()
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error in force recovery: {e}")
            return {"success": False, "error": str(e)}
    
    def get_recovery_status(self) -> Dict[str, Any]:
        """Get current recovery system status.
        
        Returns:
            Dict containing recovery status information
        """
        checkpoint_data = self.checkpoint.get_checkpoint_data()
        
        return {
            "is_running": self.is_running,
            "recovery_stats": self.recovery_stats.copy(),
            "checkpoint_info": {
                "last_checkpoint": checkpoint_data.get("last_checkpoint"),
                "processed_files_count": len(checkpoint_data.get("processed_files", {})),
                "recovery_info": checkpoint_data.get("recovery_info", {})
            },
            "next_scan_in": self._get_time_to_next_scan(),
            "config": {
                "recovery_scan_interval": self.config.recovery_scan_interval,
                "checkpoint_interval": self.config.checkpoint_interval
            }
        }
    
    def _get_time_to_next_scan(self) -> Optional[float]:
        """Get time remaining until next recovery scan.
        
        Returns:
            Time in seconds until next scan, or None if not running
        """
        if not self.is_running or not self.recovery_stats.get("last_scan_time"):
            return None
        
        last_scan = self.recovery_stats["last_scan_time"]
        next_scan = last_scan + self.config.recovery_scan_interval
        time_remaining = next_scan - time.time()
        
        return max(0, time_remaining)


# Global recovery system instance (follows MCP server pattern)
recovery_system: Optional[WatcherRecoverySystem] = None


async def initialize_recovery_system(file_watcher, 
                                   incremental_processor,
                                   config: Optional[FileWatcherConfig] = None) -> bool:
    """Initialize the global recovery system instance.
    
    Args:
        file_watcher: ConversationFileWatcher instance
        incremental_processor: IncrementalProcessor instance
        config: Optional configuration
        
    Returns:
        bool: True if initialized successfully
    """
    global recovery_system
    
    if recovery_system is not None and recovery_system.is_running:
        return True
    
    try:
        recovery_system = WatcherRecoverySystem(file_watcher, incremental_processor, config)
        await recovery_system.start_recovery_system()
        return True
    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to initialize recovery system: {e}")
        return False


async def shutdown_recovery_system():
    """Shutdown the global recovery system instance."""
    global recovery_system
    
    if recovery_system is not None:
        await recovery_system.stop_recovery_system()
        recovery_system = None