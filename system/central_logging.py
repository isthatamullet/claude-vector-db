import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import time

class VectorDatabaseLogger:
    """Centralized logging for vector database operations."""
    
    def __init__(self, component_name: str, log_level: str = "INFO"):
        """Initialize logger for specific component."""
        self.component_name = component_name
        self.logger = logging.getLogger(f"vector_db.{component_name}")
        
        # Configure file handler
        log_dir = Path("/home/user/.claude-vector-db-enhanced/logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{component_name}.log"
        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(getattr(logging, log_level.upper()))
    
    def log_entry_processing(self, entry_id: str, status: str, details: Dict[str, Any] = None):
        """Log individual entry processing."""
        message = f"Entry {entry_id}: {status.upper()}"
        if details:
            message += f" | {json.dumps(details)}"
        
        if status == "success":
            self.logger.info(message)
        elif status == "failed":
            self.logger.error(message)
        else:
            self.logger.warning(message)
    
    def log_batch_processing(self, batch_size: int, processed: int, failed: int, duration_ms: float):
        """Log batch processing metrics."""
        self.logger.info(f"Batch completed: {processed}/{batch_size} processed, {failed} failed, {duration_ms:.1f}ms")
    
    def log_field_population(self, field_stats: Dict[str, int]):
        """Log metadata field population statistics."""
        self.logger.info(f"Field population: {json.dumps(field_stats)}")
    
    def log_duplicate_handling(self, content_hash: str, action: str):
        """Log duplicate detection and handling."""
        self.logger.info(f"Duplicate {content_hash}: {action}")
    
    def log_error(self, operation: str, error: Exception, context: Dict[str, Any] = None):
        """Log errors with full context."""
        message = f"Error in {operation}: {str(error)}"
        if context:
            message += f" | Context: {json.dumps(context)}"
        self.logger.error(message, exc_info=True)
    
    def log_duplicate_handling(self, content_hash: str, action: str):
        """Log duplicate detection and handling."""
        self.logger.info(f"Duplicate {content_hash}: {action}")
    
    def log_error(self, operation: str, error: Exception, context: Dict[str, Any] = None):
        """Log errors with full context."""
        message = f"Error in {operation}: {str(error)}"
        if context:
            message += f" | Context: {json.dumps(context, default=str)}"
        self.logger.error(message, exc_info=True)
    
    def log_processing_start(self, operation: str, details: Dict[str, Any] = None):
        """Log start of major processing operation."""
        message = f"Starting {operation}"
        if details:
            message += f" | {json.dumps(details, default=str)}"
        self.logger.info(message)
    
    def log_processing_complete(self, operation: str, duration_seconds: float, details: Dict[str, Any] = None):
        """Log completion of major processing operation."""
        message = f"Completed {operation} in {duration_seconds:.2f}s"
        if details:
            message += f" | {json.dumps(details, default=str)}"
        self.logger.info(message)
    
    def log_database_operation(self, operation: str, count: int, duration_ms: float = None):
        """Log database operations."""
        message = f"Database {operation}: {count} entries"
        if duration_ms:
            message += f" in {duration_ms:.1f}ms"
        self.logger.info(message)
    
    def log_session_processing(self, session_id: str, status: str, entry_count: int = None, details: Dict[str, Any] = None):
        """Log session-level processing."""
        message = f"Session {session_id}: {status.upper()}"
        if entry_count is not None:
            message += f" | {entry_count} entries"
        if details:
            message += f" | {json.dumps(details, default=str)}"
        
        if status == "success":
            self.logger.info(message)
        elif status == "failed":
            self.logger.error(message)
        else:
            self.logger.warning(message)
    
    def log_enhancement_processing(self, field_name: str, success_count: int, total_count: int, duration_ms: float = None):
        """Log enhancement field processing."""
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        message = f"Enhancement {field_name}: {success_count}/{total_count} ({success_rate:.1f}%)"
        if duration_ms:
            message += f" in {duration_ms:.1f}ms"
        self.logger.info(message)
    
    def log_backfill_operation(self, operation: str, session_count: int, field_updates: int, duration_seconds: float):
        """Log backfill operations."""
        message = f"Backfill {operation}: {session_count} sessions, {field_updates} field updates in {duration_seconds:.2f}s"
        self.logger.info(message)


class ProcessingTimer:
    """Context manager for timing operations with automatic logging."""
    
    def __init__(self, logger: VectorDatabaseLogger, operation_name: str, details: Dict[str, Any] = None):
        self.logger = logger
        self.operation_name = operation_name
        self.details = details or {}
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        self.logger.log_processing_start(self.operation_name, self.details)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        if exc_type is None:
            self.logger.log_processing_complete(self.operation_name, duration, self.details)
        else:
            self.logger.log_error(f"{self.operation_name}_completion", exc_val, {
                "duration_seconds": duration,
                **self.details
            })


def create_logger(component_name: str, log_level: str = "INFO") -> VectorDatabaseLogger:
    """Factory function to create a logger for a component."""
    return VectorDatabaseLogger(component_name, log_level)