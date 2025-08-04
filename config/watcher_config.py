"""
Configuration settings for the real-time file watcher system.

This module defines the configuration parameters for file watching,
processing, and performance tuning based on the PRP requirements.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
from datetime import datetime


@dataclass
class FileWatcherConfig:
    """Configuration for the real-time file watcher system.
    
    Performance targets from PRP:
    - Sub-100ms file change detection
    - <200ms processing latency for incremental updates  
    - >1000 entries/sec processing rate
    - <512MB total memory footprint
    """
    
    # File watching configuration
    watch_directory: str = "/home/user/.claude/projects"
    file_patterns: List[str] = field(default_factory=lambda: ["*.jsonl"])
    recursive: bool = True
    ignore_patterns: List[str] = field(default_factory=lambda: [
        ".*",  # Hidden files
        "*~",  # Backup files
        "*.tmp",  # Temporary files
        "*.temp"  # Temporary files
    ])
    
    # Processing configuration
    batch_size: int = 50  # Conservative start, adaptive sizing
    max_batch_size: int = 166  # ChromaDB SQLite constraint limit
    processing_timeout: float = 0.2  # 200ms target latency
    detection_timeout: float = 0.1  # 100ms target detection
    queue_max_size: int = 1000  # Bounded queue to prevent memory issues
    
    # Performance tuning
    file_read_retry_attempts: int = 3
    file_read_retry_delay: float = 0.1  # Initial delay, exponential backoff
    processing_workers: int = 2  # Concurrent processing workers
    memory_check_interval: int = 60  # Memory usage check interval (seconds)
    
    # Recovery and persistence
    recovery_scan_interval: int = 300  # 5 minutes
    checkpoint_file: str = "file_watcher_checkpoint.json"
    checkpoint_interval: int = 60  # Checkpoint every 60 seconds
    missed_event_threshold: int = 10  # Max missed events before full scan
    
    # Migration control
    auto_processing_enabled: bool = False  # Phase 2: Disable to use hooks only
    
    # Logging and monitoring
    log_level: str = "INFO"
    performance_logging: bool = True
    stats_update_interval: int = 30  # Statistics update interval (seconds)
    
    # File access safety
    file_lock_timeout: float = 5.0  # Max time to wait for file lock
    file_lock_retry_delay: float = 0.05  # Delay between lock attempts
    content_change_debounce: float = 0.1  # Debounce rapid file changes
    
    def __post_init__(self):
        """Validate configuration parameters after initialization."""
        # Ensure watch directory exists
        watch_path = Path(self.watch_directory)
        if not watch_path.exists():
            raise ValueError(f"Watch directory does not exist: {self.watch_directory}")
        
        # Validate batch size constraints
        if self.batch_size > self.max_batch_size:
            raise ValueError(
                f"batch_size ({self.batch_size}) cannot exceed max_batch_size ({self.max_batch_size})"
            )
        
        # Validate timeout constraints
        if self.detection_timeout >= self.processing_timeout:
            raise ValueError(
                "detection_timeout must be less than processing_timeout"
            )
        
        # Ensure reasonable queue size
        if self.queue_max_size < self.batch_size * 2:
            raise ValueError(
                "queue_max_size should be at least 2x batch_size to prevent blocking"
            )


@dataclass
class FileChangeEvent:
    """Represents a file system change event for processing.
    
    Used to queue file changes for incremental processing.
    """
    file_path: str
    event_type: str  # 'created', 'modified', 'deleted', 'moved'
    timestamp: float
    file_size: int
    last_modified: float
    checksum: Optional[str] = None  # Content checksum for duplicate detection
    
    def __str__(self) -> str:
        return f"FileChangeEvent({self.event_type}: {self.file_path} at {self.timestamp})"


@dataclass
class ProcessingStats:
    """Statistics for file watcher performance monitoring.
    
    Tracks performance metrics to ensure PRP requirements are met.
    """
    events_processed: int = 0
    entries_indexed: int = 0
    files_monitored: int = 0
    processing_time_total: float = 0.0
    detection_time_avg: float = 0.0
    processing_latency_avg: float = 0.0
    errors: int = 0
    memory_usage_mb: float = 0.0
    last_update: Optional[datetime] = None
    queue_size: int = 0
    
    # Performance tracking
    events_per_second: float = 0.0
    entries_per_second: float = 0.0
    batch_processing_rate: float = 0.0
    
    # Error tracking
    file_lock_failures: int = 0
    processing_timeouts: int = 0
    batch_failures: int = 0
    recovery_scans: int = 0
    
    def update_performance_metrics(self, processing_duration: float, entries_processed: int):
        """Update performance metrics with latest processing data."""
        self.processing_time_total += processing_duration
        self.entries_indexed += entries_processed
        self.events_processed += 1
        
        if self.events_processed > 0:
            self.processing_latency_avg = self.processing_time_total / self.events_processed
        
        # Calculate rates (entries per second)
        if processing_duration > 0:
            self.entries_per_second = entries_processed / processing_duration
            self.events_per_second = 1.0 / processing_duration
        
        self.last_update = datetime.now()
    
    def is_performance_acceptable(self, config: FileWatcherConfig) -> bool:
        """Check if current performance meets PRP requirements."""
        return (
            self.processing_latency_avg <= config.processing_timeout and
            self.detection_time_avg <= config.detection_timeout and
            self.entries_per_second >= 1000.0 and  # >1000 entries/sec requirement
            self.memory_usage_mb <= 512.0  # <512MB memory requirement
        )
    
    def get_health_status(self) -> str:
        """Get overall health status of the file watcher."""
        if self.errors > self.events_processed * 0.1:  # >10% error rate
            return "unhealthy"
        elif self.processing_latency_avg > 0.2:  # >200ms latency
            return "degraded"
        else:
            return "healthy"


# Default configuration instance
DEFAULT_CONFIG = FileWatcherConfig()