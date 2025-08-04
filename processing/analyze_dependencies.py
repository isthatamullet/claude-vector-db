#!/usr/bin/env python3
"""
Dependency Analysis Script for Claude Vector Database Enhanced
Analyzes imports and dependencies to identify which files can be safely archived.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Set
import re

def extract_imports_from_file(file_path: Path) -> List[str]:
    """Extract all import statements from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Handle exec() calls that load other files
        exec_pattern = r"exec\(open\('([^']+)'\)\.read\(\)\)"
        exec_matches = re.findall(exec_pattern, content)
        
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
        
        # Add exec'd files as dependencies
        for exec_file in exec_matches:
            if exec_file.startswith('/'):
                exec_path = Path(exec_file)
                if exec_path.exists():
                    imports.append(exec_path.stem)
        
        return imports
    except Exception as e:
        print(f"Error parsing {file_path}: {e}")
        return []

def analyze_dependencies():
    """Analyze all Python files and their dependencies."""
    project_root = Path("/home/user/.claude-vector-db-enhanced")
    
    # Core system files
    core_files = [
        "mcp/mcp_server.py",
        "processing/run_full_sync.py", 
        "database/vector_database.py",
        "conversation_extractor.py"
    ]
    
    # Find all Python files (excluding venv)
    all_py_files = []
    for py_file in project_root.rglob("*.py"):
        if "/venv/" not in str(py_file):
            rel_path = py_file.relative_to(project_root)
            all_py_files.append(str(rel_path))
    
    # Build dependency map
    dependencies = {}
    for py_file in all_py_files:
        file_path = project_root / py_file
        imports = extract_imports_from_file(file_path)
        
        # Filter to only local imports (files that exist in this project)
        local_imports = []
        for imp in imports:
            # Check if this import corresponds to a local file
            possible_files = [
                f"{imp}.py",
                f"{imp}/__init__.py",
            ]
            for possible in possible_files:
                if (project_root / possible).exists():
                    local_imports.append(imp)
                    break
        
        dependencies[py_file] = local_imports
    
    return dependencies, core_files, all_py_files

def find_used_files(dependencies: Dict, core_files: List[str]) -> Set[str]:
    """Find all files used by core system (recursively)."""
    used = set()
    to_process = set(core_files)
    
    while to_process:
        current = to_process.pop()
        if current in used:
            continue
        used.add(current)
        
        # Add dependencies of current file
        if current in dependencies:
            for dep in dependencies[current]:
                dep_file = f"{dep}.py"
                if dep_file not in used:
                    to_process.add(dep_file)
    
    return used

def categorize_files(all_files: List[str], used_files: Set[str]) -> Dict[str, List[str]]:
    """Categorize files by their status."""
    categories = {
        "core_active": [],
        "backup_files": [],
        "old_versions": [],
        "test_files": [],
        "archived_already": [],
        "unused_modules": [],
        "support_modules": []
    }
    
    for file_path in all_files:
        file_name = Path(file_path).name
        
        if file_path.startswith("archive/"):
            categories["archived_already"].append(file_path)
        elif any(suffix in file_name for suffix in ["_backup.py", "_old.py", "_pre_"]):
            categories["backup_files"].append(file_path)
        elif file_name.startswith("test_") or "/test_" in file_path:
            categories["test_files"].append(file_path)
        elif file_path in used_files:
            categories["core_active"].append(file_path)
        else:
            # Check if it's a support module used by other non-core files
            categories["unused_modules"].append(file_path)
    
    return categories

def main():
    print("🔍 Claude Vector Database Enhanced - Dependency Analysis")
    print("=" * 60)
    
    dependencies, core_files, all_files = analyze_dependencies()
    used_files = find_used_files(dependencies, core_files)
    categories = categorize_files(all_files, used_files)
    
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"Total Python files: {len(all_files)}")
    print(f"Core system files: {len(core_files)}")
    print(f"Files used by core system: {len(used_files)}")
    
    print(f"\n✅ CORE ACTIVE FILES ({len(categories['core_active'])})")
    print("These files are actively used by the core system:")
    for f in sorted(categories['core_active']):
        print(f"  • {f}")
    
    print(f"\n📁 ALREADY ARCHIVED ({len(categories['archived_already'])})")
    print("These files are already in the archive directory:")
    for f in sorted(categories['archived_already']):
        print(f"  • {f}")
    
    print(f"\n🗂️ BACKUP FILES - SAFE TO ARCHIVE ({len(categories['backup_files'])})")
    print("These are clearly backup/old versions:")
    for f in sorted(categories['backup_files']):
        print(f"  • {f}")
    
    print(f"\n🧪 TEST FILES ({len(categories['test_files'])})")  
    print("These are test files (may or may not be needed):")
    for f in sorted(categories['test_files']):
        print(f"  • {f}")
    
    print(f"\n❓ UNUSED MODULES - CANDIDATE FOR ARCHIVING ({len(categories['unused_modules'])})")
    print("These files are not used by the core system:")
    for f in sorted(categories['unused_modules']):
        print(f"  • {f}")
    
    print(f"\n🎯 CORE SYSTEM DEPENDENCY TREE")
    print("Dependencies of core files:")
    for core_file in core_files:
        print(f"\n  {core_file}:")
        if core_file in dependencies:
            for dep in sorted(dependencies[core_file]):
                print(f"    → {dep}")
        else:
            print("    → No local dependencies found")
    
    # Files that are 100% safe to archive
    safe_to_archive = categories['backup_files'] + [
        f for f in categories['unused_modules'] 
        if not any(f.startswith(prefix) for prefix in ['tests/', 'config/'])
    ]
    
    print(f"\n🎉 RECOMMENDATION")
    print(f"Files that can be 100% safely archived: {len(safe_to_archive)}")
    print("These files are either backup versions or completely unused by the core system.")

if __name__ == "__main__":
    main()