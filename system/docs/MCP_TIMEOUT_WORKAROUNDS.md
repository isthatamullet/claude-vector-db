# MCP Timeout Workarounds

Creative approaches to work around the 2-minute MCP timeout constraint for long-running operations like force conversation sync.

## Problem Statement

Claude Code's MCP client has a hardcoded 2-minute timeout for tool execution. This prevents long-running operations (like processing 92 conversation files that takes 10-15 minutes) from completing successfully via MCP tools.

## Solution Options

### Option 1: Background Process with Status Polling

Create separate tools for starting a process and checking its status.

```python
@mcp.tool()
async def start_conversation_sync() -> Dict[str, Any]:
    # Spawn background process and return immediately
    task_id = str(uuid.uuid4())
    subprocess.Popen(["/home/user/.claude-vector-db/venv/bin/python", "processin/home/user/.claude-vector-db-enhanced/processing/run_full_sync.py"])
    return {"task_id": task_id, "status": "started"}

@mcp.tool() 
async def check_sync_status(task_id: str) -> Dict[str, Any]:
    # Check if process is still running, read progress from log file
    return {"status": "running", "progress": "45%", "files_processed": 42}
```

**Pros**: Clean separation, can track progress
**Cons**: Requires multiple tool calls, complex state management

### Option 2: Chunked Processing with State

Process data in small chunks that each complete within 2 minutes.

```python
@mcp.tool()
async def sync_conversation_chunk(batch_number: int = 1) -> Dict[str, Any]:
    # Process 10 files at a time, store state between calls
    # Each chunk completes in <2 minutes
    # Return next batch number to continue
    
    files_per_batch = 10
    start_idx = (batch_number - 1) * files_per_batch
    end_idx = start_idx + files_per_batch
    
    # Process batch...
    
    return {
        "batch_completed": batch_number,
        "next_batch": batch_number + 1 if more_files else None,
        "progress": f"{end_idx}/{total_files} files"
    }
```

**Pros**: Works within timeout constraints, provides progress
**Cons**: Requires multiple sequential calls, user must remember to continue

### Option 3: File-based Progress Tracking

Write progress to disk and resume from where it left off.

```python
@mcp.tool()
async def smart_force_sync() -> Dict[str, Any]:
    # Read progress file to see where we left off
    progress_file = "/tmp/sync_progress.json"
    
    # Process as much as possible in 2 minutes
    # Write progress to file before timeout
    
    return {
        "processed": files_completed,
        "remaining": files_remaining,
        "continue_command": "Run smart_force_sync again to continue"
    }
```

**Pros**: Automatic resume capability, fault tolerant
**Cons**: Still requires multiple calls, complexity in state management

### Option 4: Multiple Specialized Tools

Break down the work into smaller, focused tools.

```python
@mcp.tool()
async def sync_project_files(project_name: str) -> Dict[str, Any]:
    # Sync only files for a specific project
    # Example: sync only tylergohr.com conversations

@mcp.tool()
async def sync_date_range(start_date: str, end_date: str) -> Dict[str, Any]:
    # Sync only files within date range
    # Example: sync only last week's conversations

@mcp.tool()
async def sync_large_files_only() -> Dict[str, Any]:
    # Sync only files over a certain size threshold
```

**Pros**: More granular control, each tool completes quickly
**Cons**: Requires knowledge of what to sync, may miss files

### Option 5: Process Spawning (Most Promising)

Start a detached background process that continues after MCP call ends.

```python
@mcp.tool()
async def start_background_sync() -> Dict[str, Any]:
    # Spawn detached process that continues after MCP call ends
    import subprocess
    import os
    
    # Start detached background process
    process = subprocess.Popen(
        ["/home/user/.claude-vector-db/venv/bin/python", "processin/home/user/.claude-vector-db-enhanced/processing/run_full_sync.py"],
        stdout=open("/tmp/sync_progress.log", "w"),
        stderr=subprocess.STDOUT,
        start_new_session=True,  # Detach from parent
        preexec_fn=os.setsid     # Create new process group
    )
    
    return {
        "success": True,
        "message": "Background sync started",
        "pid": process.pid,
        "progress_log": "/tmp/sync_progress.log",
        "check_command": "tail -f /tmp/sync_progress.log"
    }

@mcp.tool()
async def check_background_sync() -> Dict[str, Any]:
    # Check if background process is still running
    import psutil
    
    # Read progress from log file
    # Check if PID still exists
    
    return {
        "status": "running" | "completed" | "failed",
        "progress": "current progress from log",
        "estimated_remaining": "5 minutes"
    }
```

**Pros**: Truly bypasses timeout, process continues independently
**Cons**: Complexity in process management, requires careful cleanup

### Option 6: Direct Script Recommendation (Current Solution)

Simply recommend running the script directly outside MCP.

```python
@mcp.tool()
async def force_conversation_sync() -> Dict[str, Any]:
    return {
        "success": True,
        "message": "Large dataset detected. Use timeout-free script.",
        "command": "cd /home/user/.claude-vector-db && ./venv/bin/python run_full_sync.py",
        "estimated_time": "10-15 minutes",
        "benefits": [
            "No timeout constraints",
            "Complete progress tracking",
            "Comprehensive error handling"
        ]
    }
```

**Pros**: Simple, reliable, no complexity
**Cons**: Requires terminal access, not integrated with MCP workflow

## Implementation Priority

1. **Option 5 (Process Spawning)** - Most promising for true integration
2. **Option 2 (Chunked Processing)** - Good balance of integration and reliability  
3. **Option 1 (Background + Polling)** - Clean architecture
4. **Option 6 (Direct Script)** - Current working solution
5. **Option 3 (File-based Progress)** - Good for fault tolerance
6. **Option 4 (Specialized Tools)** - Useful for specific use cases

## Current Status

- ✅ **Option 6 implemented** - `processin/home/user/.claude-vector-db-enhanced/processing/run_full_sync.py` script works perfectly
- ✅ **Database rebuilt successfully** - All 92 conversation files processed
- ✅ **Hooks working** - No more ChromaDB corruption
- 🔄 **Next step**: Implement Option 5 for better MCP integration

## Notes

- The 2-minute timeout is a Claude Code MCP client limitation, not server-side
- Cannot be configured or changed from FastMCP server
- Background process spawning appears to be the most viable long-term solution
- Current script-based approach is reliable fallback