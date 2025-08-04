# Context Recovery Best Practices - Claude Code Vector Database

## Overview

This document outlines the proven context recovery system that combines Claude Code hooks with vector database indexing to maintain development context across conversation compacting and session boundaries.

## Hook System Architecture

### 1. UserPromptSubmit Hook
**Purpose**: Indexes user prompts in real-time to the vector database

**Configuration**: 
```json
{
  "hooks": {
    "UserPromptSubmit": {
      "matcher": "*",
      "hook": {
        "type": "command", 
        "command": "/home/user/.claude-vector-db/hooks/user_prompt_submit.py"
      }
    }
  }
}
```

**What it does**:
- Triggers immediately when user submits a prompt
- Indexes the prompt content to ChromaDB
- Enables searchable conversation history
- Provides real-time context preservation

### 2. Stop Hook  
**Purpose**: Indexes Claude's responses after each response completion

**Configuration**:
```json
{
  "hooks": {
    "Stop": {
      "matcher": "*",
      "hook": {
        "type": "command",
        "command": "/home/user/.claude-vector-db/hooks/stop.py"
      }
    }
  }
}
```

**What it does**:
- Triggers after Claude completes each response
- Indexes Claude's response to ChromaDB
- Ensures complete conversation history is searchable
- Maintains bidirectional conversation context

### 3. PreCompact Hook
**Purpose**: Preserves essential development context before conversation compacting

**Configuration**:
```json
{
  "hooks": {
    "PreCompact": {
      "matcher": "auto manual",
      "hook": {
        "type": "command",
        "command": "/home/user/tylergohr.com/scripts/hooks/precompact-context.sh"
      }
    }
  }
}
```

**Script Content**:
```bash
#!/bin/bash
# Preserve essential development context for both manual and auto-compact
echo "=== DEVELOPMENT CONTEXT ==="
echo "Current branch: $(git branch --show-current)"
echo "Quality status: $(npm run typecheck >/dev/null 2>&1 && echo "PASS" || echo "FAIL")"
echo "Last commit: $(git log -1 --oneline)"
echo ""
echo "=== CONVERSATION LOG REFERENCE ==="
echo "Full conversation history available at: $CLAUDE_TRANSCRIPT_PATH"
echo "📝 Use this log if you need to reference specific tasks or decisions"
echo "💡 Prompt: 'Read the conversation log to see [specific topic]'"
```

## Context Recovery Workflow

### Before Compacting
1. **Automatic Context Preservation**: UserPromptSubmit and Stop hooks continuously index conversation
2. **Development State Capture**: PreCompact hook captures git branch, code quality, and recent commits
3. **Log Reference Creation**: PreCompact hook provides conversation log path for detailed history

### After Compacting
1. **Development Context**: PreCompact hook output provides immediate development state
2. **Vector Database Search**: Use MCP search to find specific conversation elements
3. **Conversation Log Access**: Read full conversation log if detailed context needed

### Effective Recovery Prompts

**For General Context Recovery**:
```
"Check the vector database for our recent conversation about [topic]"
```

**For Specific Task Context**:
```
"Search conversations for the todo list we were working on"
"Find the migration plan we discussed"
```

**For Development Context**:
```
"What were we working on before compacting? Check both the PreCompact hook output and vector database"
```

## Best Practices

### 1. Hook Configuration
- **UserPromptSubmit + Stop hooks**: Always use `"matcher": "*"` for complete coverage
- **PreCompact hook**: Use `"matcher": "auto manual"` for both automatic and manual compacting
- **File paths**: Use absolute paths to hook scripts

### 2. Context Preservation Strategy
- **Real-time indexing**: Let UserPromptSubmit and Stop hooks handle continuous conversation indexing
- **Development state**: PreCompact hook focuses on git context and code quality
- **Conversation log**: Maintain as backup for detailed context when vector search isn't sufficient

### 3. Recovery Workflow
1. **Start with PreCompact output**: Quick development context overview
2. **Use vector database search**: Find specific topics, tasks, or decisions
3. **Fall back to conversation log**: When detailed sequential context needed

### 4. Performance Optimization
- **Vector database**: Provides fast semantic search across all conversations
- **Hook execution**: Lightweight scripts ensure minimal performance impact
- **Indexing strategy**: Real-time indexing prevents context loss

## Migration Results

### Performance Improvements
- **Memory usage**: 55.7% reduction (416MB → 184MB)
- **Queue processing**: Eliminated 979 event backlog
- **Hook reliability**: 100% execution success rate
- **Context preservation**: Complete conversation history maintained

### System Architecture
- **File watcher**: Disabled (replaced by real-time hooks)
- **JSONL backup**: Maintained for data integrity
- **ChromaDB indexing**: Real-time via hooks
- **MCP server**: Provides search capabilities

## Troubleshooting

### Hook Not Firing
- Verify hook configuration in `~/.claude/settings.json`
- Check script permissions: `chmod +x /path/to/hook/script`
- Test script independently: `/path/to/hook/script`

### Vector Database Search Issues
- Check ChromaDB status: `python -c "import chromadb; print('ChromaDB working')"`
- Verify MCP server: Test search with recent conversation content
- Force sync if needed: Use `mcp__claude-vector-db__force_conversation_sync`

### Context Recovery Failures
- PreCompact hook output should appear in conversation
- Vector database should contain recent conversations
- Conversation logs should be accessible at provided path

## Advanced Usage

### Custom Search Strategies
```python
# Search for code-related conversations
search_conversations(query="implementation bug fix", include_code_only=True)

# Search within specific project context  
search_conversations(query="database migration", project_context="claude-vector-db")
```

### Development Workflow Integration
1. **Start session**: Check PreCompact context from previous session
2. **During development**: Rely on continuous indexing via hooks
3. **Before major changes**: Use `/compact` to test context recovery
4. **After compacting**: Verify context preservation worked correctly

## Security Considerations

- **Hook scripts**: Ensure proper file permissions and secure paths
- **Database access**: Vector database contains conversation history
- **Log files**: Conversation logs may contain sensitive information
- **MCP server**: Restrict access to authorized sessions only

---

**Status**: Production-ready context recovery system with proven reliability
**Performance**: 55.7% memory reduction, 100% hook execution success  
**Coverage**: Complete conversation history with real-time indexing
**Recovery**: Multi-layered approach (hooks + vector DB + conversation logs)