#!/usr/bin/env python3
"""
Add claude-vector-db MCP server to Claude Code configuration
"""
import json
from pathlib import Path

def add_mcp_server():
    """Add the claude-vector-db MCP server to Claude Code configuration"""
    
    config_path = Path.home() / '.claude.json'
    
    # Load existing configuration
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    # Add claude-vector-db MCP server
    mcp_config = {
        "claude-vector-db": {
            "type": "stdio",
            "command": "/home/user/.claude-vector-db/venv/bin/python",
            "args": [
                "/home/user/.claude-vector-db/mcp_server.py"
            ],
            "cwd": "/home/user/.claude-vector-db",
            "env": {
                "CLAUDE_PROJECTS_DIR": "/home/user/.claude/projects",
                "VECTOR_DB_PATH": "/home/user/.claude-vector-db/chroma_db",
                "LOG_LEVEL": "INFO"
            }
        }
    }
    
    # Merge with existing MCP servers
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    
    config['mcpServers'].update(mcp_config)
    
    # Write back to configuration file
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("Successfully added claude-vector-db MCP server to Claude Code configuration")
    print("Configuration added:")
    print(json.dumps(mcp_config, indent=2))

if __name__ == "__main__":
    add_mcp_server()