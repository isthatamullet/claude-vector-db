#!/usr/bin/env python3
"""
Optimized Database Configuration for Claude Vector Database System
Based on Phase 3 configuration analysis for 43,660+ entries optimization.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

class DatabaseConfig:
    """
    Centralized database configuration management with optimization for large datasets.
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent / 'config' / 'system' / 'database.json'
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file with fallback defaults."""
        
        # Default optimized configuration for 43,660+ entries
        default_config = {
            "chromadb": {
                "persist_directory": "./chroma_db",
                "client_type": "PersistentClient", 
                "collection_name": "claude_conversations",
                "embedding_function": "default",
                "settings": {
                    "anonymized_telemetry": False,
                    "allow_reset": False
                }
            },
            "performance": {
                "batch_size": 500,  # Optimized for large datasets
                "max_connections": 10,  # Connection pooling
                "connection_timeout": 30,
                "query_timeout": 10,  # Increased for large datasets
                "max_memory_mb": 2048,  # Memory allocation limit
                "cache_size": 1000  # Query result caching
            }
        }
        
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults (loaded config takes precedence)
                merged_config = {**default_config}
                for key, value in loaded_config.items():
                    if isinstance(value, dict) and key in merged_config:
                        merged_config[key] = {**merged_config[key], **value}
                    else:
                        merged_config[key] = value
                return merged_config
            except (json.JSONDecodeError, OSError) as e:
                print(f"Warning: Could not load config from {self.config_path}: {e}")
                print("Using default configuration")
        
        return default_config
    
    def get_chromadb_settings(self) -> Dict[str, Any]:
        """Get ChromaDB client settings."""
        return self.config["chromadb"]["settings"]
    
    def get_persist_directory(self) -> str:
        """Get ChromaDB persistence directory."""
        return self.config["chromadb"]["persist_directory"]
    
    def get_collection_name(self) -> str:
        """Get ChromaDB collection name."""
        return self.config["chromadb"]["collection_name"]
    
    def get_batch_size(self) -> int:
        """Get optimized batch size for bulk operations."""
        return self.config["performance"]["batch_size"]
    
    def get_query_timeout(self) -> int:
        """Get query timeout in seconds."""
        return self.config["performance"]["query_timeout"]
    
    def get_max_memory_mb(self) -> int:
        """Get maximum memory allocation in MB."""
        return self.config["performance"]["max_memory_mb"]

# Global configuration instance
_config_instance = None

def get_database_config() -> DatabaseConfig:
    """Get global database configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = DatabaseConfig()
    return _config_instance

if __name__ == "__main__":
    # Test configuration loading
    config = get_database_config()
    print("Database Configuration Test:")
    print(f"✅ Collection name: {config.get_collection_name()}")
    print(f"✅ Batch size: {config.get_batch_size()}")
    print(f"✅ Query timeout: {config.get_query_timeout()}s")
    print(f"✅ Max memory: {config.get_max_memory_mb()}MB")
    print("Configuration loading test complete.")