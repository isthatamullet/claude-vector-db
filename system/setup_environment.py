#!/usr/bin/env python3
"""
Environment Variable Setup for Claude Vector Database System
Ensures consistent environment configuration across all entry points.
"""

import os
import sys
from pathlib import Path

def setup_vector_db_environment():
    """
    Set up standardized environment variables for the vector database system.
    Based on Phase 3 configuration analysis findings.
    """
    
    # Required variables for privacy and offline operation
    required_env_vars = {
        'TRANSFORMERS_OFFLINE': '1',
        'HF_HUB_OFFLINE': '1', 
        'HF_HUB_DISABLE_TELEMETRY': '1'
    }
    
    # Set required variables if not already set
    for var, value in required_env_vars.items():
        if var not in os.environ:
            os.environ[var] = value
            print(f"✅ Set {var}={value}")
        else:
            print(f"ℹ️ {var} already set to {os.environ[var]}")
    
    # Validate critical environment setup
    validate_environment()
    
def validate_environment():
    """Validate that critical environment variables are set correctly."""
    
    critical_vars = ['TRANSFORMERS_OFFLINE', 'HF_HUB_OFFLINE', 'HF_HUB_DISABLE_TELEMETRY']
    
    for var in critical_vars:
        if os.environ.get(var) != '1':
            print(f"⚠️ WARNING: {var} is not set to '1' - privacy features may not work correctly")
            return False
    
    print("✅ Environment validation passed - all critical variables set correctly")
    return True

def get_database_path():
    """Get standardized database path relative to system root."""
    return Path(__file__).parent.parent / 'chroma_db'

def get_config_path():
    """Get standardized configuration path."""
    return Path(__file__).parent.parent / 'config'

if __name__ == "__main__":
    print("Setting up Claude Vector Database environment...")
    setup_vector_db_environment()
    print("Environment setup complete.")