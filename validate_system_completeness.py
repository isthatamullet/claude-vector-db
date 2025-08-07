#!/usr/bin/env python3
"""
System Completeness Validation Script

This script validates that the repository contains ALL necessary files
for the Claude Vector Database System to function properly.

Run this on a fresh clone to verify system completeness.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    print("🔍 CLAUDE VECTOR DATABASE SYSTEM - COMPLETENESS VALIDATION")
    print("=" * 60)
    
    validation_passed = True
    
    # Test 1: Essential directories exist
    print("\n1. Testing essential directory structure...")
    essential_dirs = [
        "database", "processing", "mcp", "system", "maintenance"
    ]
    
    for dir_name in essential_dirs:
        if Path(dir_name).exists():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory MISSING")
            validation_passed = False
    
    # Test 2: Critical Python files exist
    print("\n2. Testing critical Python files...")
    critical_files = [
        "database/vector_database.py",
        "database/conversation_extractor.py", 
        "processing/enhanced_processor.py",
        "processing/run_full_sync_orchestrated.py",
        "mcp/mcp_server.py",
        "system/health_dashboard.sh",
    ]
    
    for file_path in critical_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} MISSING")
            validation_passed = False
    
    # Test 3: Test Python imports (basic syntax check)
    print("\n3. Testing Python file syntax...")
    python_files = [
        "database/vector_database.py",
        "database/conversation_extractor.py",
        "processing/enhanced_processor.py", 
        "mcp/mcp_server.py"
    ]
    
    for file_path in python_files:
        if Path(file_path).exists():
            try:
                # Test syntax by compiling
                with open(file_path, 'r') as f:
                    compile(f.read(), file_path, 'exec')
                print(f"✅ {file_path} syntax valid")
            except SyntaxError as e:
                print(f"❌ {file_path} syntax error: {e}")
                validation_passed = False
        else:
            validation_passed = False
    
    # Test 4: Check for required dependency info
    print("\n4. Testing dependency requirements...")
    
    # Check if we have dependency information
    readme_exists = Path("README.md").exists()
    if readme_exists:
        print("✅ README.md exists (should contain setup instructions)")
    else:
        print("❌ README.md missing")
        validation_passed = False
    
    # Test 5: Test key configuration files
    print("\n5. Testing configuration completeness...")
    config_files = [
        ".gitignore"
    ]
    
    for file_path in config_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} MISSING")
            validation_passed = False
    
    # Test 6: Maintenance and monitoring scripts
    print("\n6. Testing operational scripts...")
    operational_scripts = [
        "system/health_dashboard.sh",
        "maintenance/weekly_production_maintenance.sh"
    ]
    
    for script_path in operational_scripts:
        if Path(script_path).exists():
            print(f"✅ {script_path} exists")
        else:
            print(f"❌ {script_path} MISSING")
            validation_passed = False
    
    # Final Assessment
    print("\n" + "=" * 60)
    if validation_passed:
        print("🎉 VALIDATION PASSED: Repository contains all essential system files!")
        print("\nNext Steps for Fresh Installation:")
        print("1. Set up Python virtual environment: python -m venv venv")
        print("2. Install dependencies: pip install chromadb fastmcp sentence-transformers")
        print("3. Run system health check: bash system/health_dashboard.sh")
        print("4. Start MCP server: python mcp/mcp_server.py")
        return 0
    else:
        print("❌ VALIDATION FAILED: Repository is missing essential system files!")
        print("System will NOT function properly with current repository state.")
        return 1

if __name__ == "__main__":
    sys.exit(main())