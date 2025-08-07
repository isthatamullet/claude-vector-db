#!/usr/bin/env python3
"""
Standardized Path Configuration for Claude Vector Database System
Phase 3: Configuration path standardization and optimization.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any

class PathConfig:
    """
    Centralized path configuration management with standardized relative paths.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        # Use the system root directory as base path
        self.base_path = base_path or Path(__file__).parent.parent
        self.base_path = self.base_path.resolve()
    
    def get_database_path(self) -> Path:
        """Get standardized ChromaDB database path."""
        return self.base_path / 'chroma_db'
    
    def get_config_path(self) -> Path:
        """Get standardized configuration directory path."""
        return self.base_path / 'config'
    
    def get_logs_path(self) -> Path:
        """Get standardized logs directory path."""
        return self.base_path / 'logs'
    
    def get_hooks_path(self) -> Path:
        """Get Claude Code hooks directory path."""
        return Path.home() / '.claude' / 'hooks'
    
    def get_claude_settings_path(self) -> Path:
        """Get Claude Code settings path."""
        return Path.home() / '.claude' / 'settings.local.json'
    
    def get_backup_path(self) -> Path:
        """Get standardized backup directory path."""
        return self.base_path.parent  # One level up from system
    
    def ensure_directories(self) -> None:
        """Ensure all standard directories exist."""
        directories = [
            self.get_config_path(),
            self.get_logs_path(),
            self.get_config_path() / 'system',
            self.get_config_path() / 'development',
            self.get_config_path() / 'external'
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_relative_path(self, absolute_path: Path) -> Path:
        """Convert absolute path to relative path from base."""
        try:
            return absolute_path.relative_to(self.base_path)
        except ValueError:
            # Path is not relative to base, return as-is
            return absolute_path
    
    def to_dict(self) -> Dict[str, str]:
        """Export path configuration as dictionary."""
        return {
            'base_path': str(self.base_path),
            'database_path': str(self.get_database_path()),
            'config_path': str(self.get_config_path()),
            'logs_path': str(self.get_logs_path()),
            'hooks_path': str(self.get_hooks_path()),
            'claude_settings_path': str(self.get_claude_settings_path()),
            'backup_path': str(self.get_backup_path())
        }

# Global path configuration instance
_path_config_instance = None

def get_path_config() -> PathConfig:
    """Get global path configuration instance."""
    global _path_config_instance
    if _path_config_instance is None:
        _path_config_instance = PathConfig()
        _path_config_instance.ensure_directories()
    return _path_config_instance

if __name__ == "__main__":
    # Test path configuration
    config = get_path_config()
    print("Path Configuration Test:")
    paths = config.to_dict()
    for name, path in paths.items():
        print(f"✅ {name}: {path}")
    print("Path configuration test complete.")