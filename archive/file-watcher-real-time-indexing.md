name: "Real-Time File Watcher for Claude Vector Database - Context-Rich PRP v2"
description: |

## Goal

Implement a real-time file watching system that automatically monitors `/home/user/.claude/projects/*.jsonl` files and incrementally updates the Claude vector database, eliminating the need for manual rebuild operations and providing immediate access to new conversation context.

Transform the current **manual rebuild-only** architecture to **real-time automatic indexing** with sub-100ms change detection, <200ms processing latency, and 99.9% uptime reliability.

## Why

- **Immediate Context Availability**: Eliminate 30-60 second manual rebuild delays that disrupt development workflow
- **Seamless Integration**: Background processing ensures conversation context is always current for Claude Code MCP tools
- **Improved Developer Experience**: Zero-maintenance operation reduces cognitive load and prevents stale search results
- **System Reliability**: Event-driven architecture replaces error-prone manual processes with automated fault tolerance
- **Scalability Foundation**: Architecture supports future growth from current 900+ conversations to 10,000+ entries

## What

Real-time file monitoring system with the following user-visible behaviors:

- **Automatic Detection**: New conversation files are indexed within 100ms of creation
- **Incremental Updates**: Only new/modified content is processed, maintaining system performance
- **Transparent Operation**: No user intervention required - works invisibly in background
- **Error Recovery**: Automatic recovery from system crashes or missed file events
- **Status Monitoring**: New MCP tools provide visibility into watcher health and performance

### Success Criteria

- [ ] Sub-100ms file change detection using watchdog events
- [ ] <200ms processing latency for incremental updates
- [ ] 99.9% system uptime with comprehensive error recovery
- [ ] Zero data loss during file watching operations
- [ ] Seamless integration with existing MCP tools (search_conversations, get_project_context_summary, detect_current_project)
- [ ] Memory usage <512MB total system footprint
- [ ] Processing rate >1000 entries/sec for batch operations
- [ ] New MCP tools: get_file_watcher_status() and force_conversation_sync()

## All Needed Context

### Documentation & References

```yaml
# MUST READ - Include these in your context window

- url: https://github.com/gorakhargosh/watchdog
  why: Python watchdog library documentation for cross-platform file system monitoring
  critical: Version 6.0.0 already installed, supports free-threaded CPython but thread safety audit incomplete for macOS FSEvents

- url: https://docs.trychroma.com/production/administration/performance
  why: ChromaDB performance optimization, batch processing limitations (max_batch_size=166)
  critical: No out-of-the-box batching support - requires manual implementation

- url: https://cookbook.chromadb.dev/strategies/batching/
  section: Batch processing strategies and performance tips
  critical: Due to SQLite constraints, ChromaDB has maximum statement and parameter limits

- url: https://solace.com/event-driven-architecture-patterns/
  section: Event-driven architecture patterns for real-time processing
  critical: Event streaming patterns and broker vs mediator topologies for scalability

- file: /home/user/.claude-vector-db/mcp_server.py
  why: Current MCP server implementation with three core tools - integration pattern to follow
  critical: Uses FastMCP framework, global db instance management, async tool functions

- file: /home/user/.claude-vector-db/vector_database.py
  why: ChromaDB implementation patterns, collection management, existing rebuild_index() method
  critical: Uses ChromaDB 1.0.15, DefaultEmbeddingFunction (all-MiniLM-L6-v2), persistent client

- file: /home/user/.claude-vector-db/conversation_extractor.py
  why: JSONL processing patterns, ConversationEntry dataclass structure, project name extraction
  critical: Existing streaming pattern for large file processing, metadata extraction logic

- file: /home/user/.claude-vector-db/api_server.py
  why: Current manual rebuild endpoint pattern to replace, FastAPI async background tasks
  critical: rebuild_database() function shows integration with vector_database.rebuild_index()

- docfile: /home/user/.claude-vector-db/file-watcher-feature-research.md
  why: Comprehensive research document with performance targets, implementation challenges, and architecture patterns
  critical: Contains detailed technical requirements, performance benchmarks, and implementation checklist
```

### Current Codebase Structure

```bash
/home/user/.claude-vector-db/
├── mcp_server.py              # MCP server with 3 core tools (search, context, detect)
├── vector_database.py         # ChromaDB implementation with rebuild_index()
├── conversation_extractor.py  # JSONL processing with ConversationEntry dataclass
├── api_server.py             # FastAPI backend with manual /rebuild endpoint
├── claude_search.py          # CLI interface for testing
├── add_mcp_config.py         # MCP configuration utility
├── final_integration_test.py # Integration testing
├── test_mcp_tools.py         # MCP tool testing
├── test_project_detection.py # Project detection testing
├── chroma_db/               # Vector database storage (ChromaDB persistent)
├── logs/                    # Application logs
├── venv/                    # Python virtual environment
└── config/                  # Configuration files

Target Files to Monitor:
/home/user/.claude/projects/
├── -home-user/                    # Root directory conversations
├── -home-user-tylergohr-com/      # Project-specific conversations  
├── -home-user-invoice-chaser/     # Project-specific conversations
├── -home-user-AI-Orchestrator-Platform/ # Project-specific conversations
└── [other project directories]/   # Additional project conversations
    └── *.jsonl files (conversation logs)
```

### Installation Directory: /home/user/.claude-vector-db/

**CRITICAL**: All file watcher components MUST be installed in `/home/user/.claude-vector-db/` to maintain system cohesion with the existing vector database and MCP server.

### Desired Codebase Structure with Files to be Added

```bash
/home/user/.claude-vector-db/
├── mcp_server.py              # ENHANCED: Add file watcher status tools
├── vector_database.py         # ENHANCED: Add incremental update methods
├── conversation_extractor.py  # ENHANCED: Add streaming incremental processing
├── api_server.py             # ENHANCED: Replace rebuild with watcher status
├── file_watcher.py           # NEW: Core file watching implementation
├── incremental_processor.py  # NEW: Batch processing and queue management
├── watcher_recovery.py       # NEW: Error recovery and checkpoint system
├── config/watcher_config.py  # NEW: File watcher configuration
├── tests/test_file_watcher.py # NEW: Comprehensive file watcher tests
├── tests/test_incremental.py  # NEW: Incremental processing tests
└── [existing files unchanged]

Responsibilities:
- file_watcher.py: watchdog integration, file system event handling, change detection
- incremental_processor.py: batch processing, queue management, adaptive batching
- watcher_recovery.py: checkpoint persistence, recovery scans, error handling
- config/watcher_config.py: performance tuning parameters, file patterns
```

### Known Gotchas of our Codebase & Library Quirks

```python
# CRITICAL: ChromaDB 1.0.15 batch limitations
# ChromaDB max_batch_size is 166 due to SQLite constraints
# No out-of-the-box batching support - manual chunking required
db.collection.add(
    documents=batch[:166],  # Must chunk large batches
    metadatas=metadata_batch[:166],
    ids=id_batch[:166]
)

# CRITICAL: watchdog 6.0.0 platform-specific behavior
# Linux: Uses inotify (high performance, native events)
# macOS: Uses fsevents but thread safety audit incomplete
# Kqueue scaling issues - not suitable for deep directory trees

# CRITICAL: File locking considerations
# Claude Code may still be writing when watchdog detects changes
# Must implement safe file reading with retry logic and file locking
import fcntl
with open(file_path, 'r') as f:
    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)

# CRITICAL: MCP server FastMCP framework patterns
# Global instances: db and extractor must be initialized at module level
# Async functions required for all MCP tools
# Error handling must return proper MCP error responses

# CRITICAL: JSONL streaming processing pattern
# Large conversation files >1MB require streaming to avoid memory issues
# Must track file positions to process only new content
# ConversationEntry dataclass must be preserved for compatibility

# CRITICAL: ChromaDB embedding function compatibility
# Uses DefaultEmbeddingFunction (all-MiniLM-L6-v2) - CPU only
# Embedding consistency critical for search accuracy
# Must use same embedding function for incremental updates
```

## Implementation Blueprint

### Data Models and Structure

Create incremental update data models ensuring type safety and consistency with existing ConversationEntry structure.

```python
# File: config/watcher_config.py
@dataclass
class FileWatcherConfig:
    watch_directory: str = "/home/user/.claude/projects"
    file_patterns: List[str] = field(default_factory=lambda: ["*.jsonl"])
    batch_size: int = 50  # Start conservative due to ChromaDB limits
    max_batch_size: int = 166  # ChromaDB hard limit
    processing_timeout: float = 0.2  # 200ms target
    detection_timeout: float = 0.1  # 100ms target
    recovery_scan_interval: int = 300  # 5 minutes
    checkpoint_file: str = "file_watcher_checkpoint.json"

# File: file_watcher.py
@dataclass
class FileChangeEvent:
    file_path: str
    event_type: str  # 'created', 'modified', 'deleted'
    timestamp: float
    file_size: int
    last_modified: float

@dataclass
class ProcessingStats:
    events_processed: int = 0
    entries_indexed: int = 0
    processing_time: float = 0.0
    errors: int = 0
    last_update: Optional[datetime] = None
```

### List of Tasks to be Completed to Fulfill the PRP

```yaml
Task 1:
CREATE config/watcher_config.py:
  - DEFINE FileWatcherConfig dataclass with performance parameters
  - SET conservative batch sizes due to ChromaDB limitations
  - INCLUDE file patterns and timeout configurations
  - PRESERVE modularity for easy tuning

Task 2:
CREATE file_watcher.py:
  - MIRROR pattern from: existing async/await patterns in mcp_server.py
  - IMPLEMENT watchdog.Observer with FileSystemEventHandler
  - ADD safe file reading with fcntl.flock for concurrent access
  - INCLUDE exponential backoff retry logic for file access

Task 3:
CREATE incremental_processor.py:
  - FOLLOW pattern from: conversation_extractor.py streaming logic
  - IMPLEMENT adaptive batching with ChromaDB 166-item limit
  - ADD asyncio.Queue for event processing pipeline
  - PRESERVE ConversationEntry dataclass compatibility

Task 4:
MODIFY vector_database.py:
  - FIND pattern: "def rebuild_index(self)" method
  - INJECT after line: incremental update methods
  - ADD batch_add_entries() method respecting ChromaDB limits
  - PRESERVE existing embedding function consistency

Task 5:
CREATE watcher_recovery.py:
  - IMPLEMENT checkpoint persistence system
  - ADD periodic recovery scans for missed events
  - INCLUDE comprehensive error handling and logging
  - FOLLOW existing logging patterns from vector_database.py

Task 6:
MODIFY mcp_server.py:
  - FIND pattern: "@mcp.tool()" decorator usage
  - INJECT after: existing tool definitions
  - ADD get_file_watcher_status() and force_conversation_sync() tools
  - PRESERVE async function signatures and error handling

Task 7:
MODIFY api_server.py:
  - FIND pattern: "/rebuild endpoint"
  - REPLACE with: file watcher status and control endpoints
  - MAINTAIN FastAPI async patterns and error responses
  - ADD health check integration for file watcher

Task 8:
CREATE tests/test_file_watcher.py:
  - MIRROR pattern from: test_mcp_tools.py structure
  - IMPLEMENT comprehensive event detection tests
  - ADD concurrent file access testing
  - INCLUDE performance benchmark validation

Task 9:
CREATE tests/test_incremental.py:
  - FOLLOW pattern from: final_integration_test.py
  - TEST batch processing with ChromaDB limits
  - VALIDATE incremental update accuracy
  - INCLUDE memory usage and performance tests

Task 10:
INTEGRATE all components:
  - START file watcher service on MCP server startup
  - CONNECT incremental processor to vector database
  - ENABLE recovery system with checkpoint persistence
  - VALIDATE end-to-end real-time indexing pipeline
```

### Per Task Pseudocode

```python
# Task 1 - Configuration
class FileWatcherConfig:
    def __init__(self):
        # PATTERN: Follow existing config patterns in vector_database.py
        self.watch_directory = Path("/home/user/.claude/projects")
        self.batch_size = 50  # Conservative start
        # GOTCHA: ChromaDB SQLite constraint limits batch size to 166
        self.max_batch_size = 166

# Task 2 - File Watcher Core
class ConversationFileWatcher:
    def __init__(self, config: FileWatcherConfig):
        self.observer = Observer()  # watchdog.Observer
        self.event_queue = asyncio.Queue()
        
    async def on_file_changed(self, event):
        # PATTERN: Always validate file access first (file locking)
        if await self.safe_file_access(event.src_path):
            # CRITICAL: Check for actual content changes, not just timestamp
            if await self.has_new_content(event.src_path):
                await self.event_queue.put(FileChangeEvent(...))

    async def safe_file_access(self, file_path: str) -> bool:
        # GOTCHA: Claude Code may still be writing to file
        for attempt in range(3):
            try:
                with open(file_path, 'r') as f:
                    fcntl.flock(f.fileno(), fcntl.LOCK_SH | fcntl.LOCK_NB)
                    return True
            except (IOError, OSError):
                await asyncio.sleep(0.1 * (2 ** attempt))  # Exponential backoff
        return False

# Task 3 - Incremental Processing
class IncrementalProcessor:
    def __init__(self, db: ClaudeVectorDatabase):
        self.db = db
        self.batch_size = 50  # Adaptive sizing
        
    async def process_events(self):
        # PATTERN: Use existing retry decorator patterns
        while True:
            events = await self.collect_batch_events()
            # CRITICAL: ChromaDB batch size limit of 166
            for batch in self.chunk_batch(events, self.max_batch_size):
                await self.process_batch(batch)

# Task 4 - Vector Database Enhancement
class ClaudeVectorDatabase:
    async def batch_add_entries(self, entries: List[ConversationEntry]):
        # PATTERN: Follow existing embed-then-add pattern
        # GOTCHA: Must use same DefaultEmbeddingFunction for consistency
        embeddings = []
        for entry in entries:
            # CRITICAL: Rate limiting for embedding generation
            embedding = await self.generate_embedding(entry.content)
            embeddings.append(embedding)
        
        # CRITICAL: Respect ChromaDB batch limits
        await self.collection.add(
            documents=[e.content for e in entries[:166]],
            embeddings=embeddings[:166],
            metadatas=[asdict(e) for e in entries[:166]],
            ids=[e.id for e in entries[:166]]
        )

# Task 6 - MCP Tool Integration
@mcp.tool()
async def get_file_watcher_status() -> Dict[str, Any]:
    """Get real-time status of file watching system"""
    # PATTERN: Follow existing MCP error handling
    global file_watcher
    if not file_watcher:
        return {"error": "File watcher not initialized"}
    
    return {
        "status": "active" if file_watcher.is_running else "inactive",
        "files_monitored": len(file_watcher.monitored_files),
        "events_processed": file_watcher.stats.events_processed,
        "last_update": file_watcher.stats.last_update.isoformat(),
        "queue_size": file_watcher.event_queue.qsize()
    }
```

### Integration Points

```yaml
DATABASE:
  - method: "Add batch_add_entries() to ClaudeVectorDatabase class"
  - pattern: "Follow existing collection.add() patterns with metadata"
  - constraint: "Respect ChromaDB batch size limit of 166 items"

ASYNC_PROCESSING:
  - add to: file_watcher.py and incremental_processor.py
  - pattern: "asyncio.create_task() for background processing"
  - integration: "Start on MCP server startup event"

MCP_TOOLS:
  - add to: mcp_server.py
  - pattern: "@mcp.tool() decorator with async functions"
  - tools: "get_file_watcher_status(), force_conversation_sync()"

ERROR_HANDLING:
  - add to: all new modules
  - pattern: "logging.getLogger(__name__) + try/except blocks"
  - recovery: "Checkpoint persistence and periodic recovery scans"

STARTUP_INTEGRATION:
  - modify: mcp_server.py startup logic
  - pattern: "Initialize global instances at module level"
  - services: "Start file watcher, recovery system, and MCP server concurrently"
```

## Validation Loop

### Level 1: Syntax & Style

```bash
# Run these FIRST - fix any errors before proceeding
cd /home/user/.claude-vector-db
source venv/bin/activate

# Check new files for syntax and style
ruff check file_watcher.py incremental_processor.py watcher_recovery.py --fix
mypy file_watcher.py incremental_processor.py watcher_recovery.py

# Validate enhanced existing files
ruff check mcp_server.py vector_database.py api_server.py --fix
mypy mcp_server.py vector_database.py api_server.py

# Expected: No errors. If errors, READ the error and fix before proceeding.
```

### Level 2: Unit Tests

```python
# CREATE tests/test_file_watcher.py with these test cases:
import pytest
import asyncio
import tempfile
from pathlib import Path

@pytest.mark.asyncio
async def test_file_change_detection():
    """File changes detected within 100ms"""
    watcher = ConversationFileWatcher(config)
    
    # Create temporary JSONL file
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        temp_path = f.name
        f.write(b'{"test": "data"}\n')
    
    # Start watcher and measure detection time
    start_time = time.time()
    await watcher.start_watching(Path(temp_path).parent)
    
    # Modify file
    with open(temp_path, 'a') as f:
        f.write('{"new": "entry"}\n')
    
    # Wait for event
    event = await asyncio.wait_for(watcher.event_queue.get(), timeout=0.15)
    detection_time = time.time() - start_time
    
    assert detection_time < 0.1  # Sub-100ms requirement
    assert event.file_path == temp_path

@pytest.mark.asyncio
async def test_incremental_processing_batch_limits():
    """Respects ChromaDB batch size limits"""
    processor = IncrementalProcessor(mock_db)
    
    # Create 200 entries (exceeds ChromaDB limit of 166)
    entries = [create_mock_conversation_entry(i) for i in range(200)]
    
    # Process entries
    with patch.object(mock_db, 'batch_add_entries') as mock_add:
        await processor.process_entries(entries)
    
    # Verify batching respected limits
    assert mock_add.call_count == 2  # 166 + 34
    first_batch = mock_add.call_args_list[0][0][0]
    assert len(first_batch) == 166

@pytest.mark.asyncio
async def test_concurrent_file_access():
    """Handles concurrent file access gracefully"""
    watcher = ConversationFileWatcher(config)
    
    # Simulate Claude Code writing while watcher reads
    with tempfile.NamedTemporaryFile(suffix='.jsonl') as f:
        # Lock file (simulate Claude Code writing)
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
        
        # Attempt to read should retry and eventually succeed
        result = await watcher.safe_file_access(f.name)
        # File locked, should return False after retries
        assert result == False

@pytest.mark.asyncio
async def test_mcp_tool_integration():
    """New MCP tools return correct status"""
    # Initialize watcher
    global file_watcher
    file_watcher = ConversationFileWatcher(config)
    await file_watcher.start()
    
    # Test status tool
    status = await get_file_watcher_status()
    
    assert status["status"] == "active"
    assert "files_monitored" in status
    assert "events_processed" in status
    assert "last_update" in status
```

```bash
# Run and iterate until passing:
cd /home/user/.claude-vector-db
source venv/bin/activate
uv run pytest tests/test_file_watcher.py -v
uv run pytest tests/test_incremental.py -v

# If failing: Read error, understand root cause, fix code, re-run
# NEVER mock ChromaDB calls to make tests pass - fix actual implementation
```

### Level 3: Integration Tests

```bash
# Start the MCP server with file watcher enabled
cd /home/user/.claude-vector-db
source venv/bin/activate
python mcp_server.py

# Test real-time indexing with actual conversation file
echo '{"test": "integration", "timestamp": "'$(date -Iseconds)'"}' >> /home/user/.claude/projects/-home-user/test_integration.jsonl

# Verify immediate availability in search (within 300ms total)
sleep 0.3
python -c "
import asyncio
from mcp_server import search_conversations

async def test():
    result = await search_conversations('integration')
    assert len(result) > 0
    print('✅ Real-time indexing working')

asyncio.run(test())
"

# Test file watcher status MCP tool
python -c "
import asyncio
from mcp_server import get_file_watcher_status

async def test_status():
    status = await get_file_watcher_status()
    assert status['status'] == 'active'
    print('✅ File watcher status tool working')
    print(f'Files monitored: {status[\"files_monitored\"]}')
    print(f'Events processed: {status[\"events_processed\"]}')

asyncio.run(test_status())
"

# Test error recovery
pkill -f mcp_server  # Simulate crash
sleep 2
python mcp_server.py &  # Restart
sleep 5

# Verify recovery scan worked
python -c "
import asyncio
from mcp_server import search_conversations

async def test_recovery():
    result = await search_conversations('integration')
    assert len(result) > 0
    print('✅ Error recovery working')

asyncio.run(test_recovery())
"
```

### Level 4: Performance & Creative Validation

```bash
# Performance benchmarking
cd /home/user/.claude-vector-db
source venv/bin/activate

# Test high-volume processing (1000+ entries/sec requirement)
python -c "
import asyncio
import time
import json
from file_watcher import ConversationFileWatcher
from incremental_processor import IncrementalProcessor

async def benchmark():
    processor = IncrementalProcessor(db)
    
    # Generate 2000 test entries
    entries = []
    for i in range(2000):
        entries.append(ConversationEntry(
            id=f'bench_{i}',
            content=f'Benchmark entry {i} with substantial content for realistic testing',
            type='user',
            project_path='/test',
            project_name='benchmark',
            timestamp=datetime.now().isoformat(),
            session_id='bench_session',
            file_name='benchmark.jsonl',
            has_code=False,
            tools_used=[],
            content_length=len(f'Benchmark entry {i}')
        ))
    
    # Measure processing time
    start_time = time.time()
    await processor.process_entries(entries)
    duration = time.time() - start_time
    
    rate = len(entries) / duration
    print(f'Processing rate: {rate:.1f} entries/sec')
    assert rate > 1000, f'Performance requirement not met: {rate} < 1000'
    print('✅ Performance requirement met')

asyncio.run(benchmark())
"

# Memory usage monitoring
python -c "
import psutil
import os
import asyncio
from file_watcher import ConversationFileWatcher

async def monitor_memory():
    process = psutil.Process(os.getpid())
    
    # Start file watcher
    watcher = ConversationFileWatcher(config)
    await watcher.start()
    
    # Monitor for 60 seconds of operation
    max_memory = 0
    for _ in range(60):
        memory_mb = process.memory_info().rss / 1024 / 1024
        max_memory = max(max_memory, memory_mb)
        await asyncio.sleep(1)
    
    print(f'Peak memory usage: {max_memory:.1f} MB')
    assert max_memory < 512, f'Memory requirement not met: {max_memory} >= 512MB'
    print('✅ Memory requirement met')

asyncio.run(monitor_memory())
"

# End-to-end latency testing
python scripts/latency_test.py  # Custom script for end-to-end timing

# Load testing with realistic conversation patterns
python scripts/load_test.py --conversations=100 --concurrent=10

# Fault injection testing
python scripts/fault_injection.py --test-file-locks --test-disk-full --test-network-errors
```

## Final Validation Checklist

- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `ruff check . --fix`
- [ ] No type errors: `mypy file_watcher.py incremental_processor.py watcher_recovery.py`
- [ ] Performance benchmarks met: >1000 entries/sec, <512MB memory, <100ms detection
- [ ] Real-time indexing functional: New files indexed within 200ms
- [ ] MCP tools working: get_file_watcher_status() and force_conversation_sync() respond correctly
- [ ] Error recovery tested: System recovers from crashes and missed events
- [ ] Integration complete: File watcher starts with MCP server and processes events continuously
- [ ] Documentation updated: README.md includes file watcher operation and troubleshooting

---

## Anti-Patterns to Avoid

- ❌ Don't poll files instead of using watchdog events - defeats performance goals
- ❌ Don't ignore ChromaDB batch size limits - will cause SQLite constraint errors  
- ❌ Don't skip file locking checks - will cause data corruption during concurrent access
- ❌ Don't use sync functions in async context - breaks event loop and performance
- ❌ Don't hardcode file paths - use configuration for flexibility
- ❌ Don't catch all exceptions without specific handling - masks important errors
- ❌ Don't mock ChromaDB calls in tests to make them pass - fix real implementation
- ❌ Don't start multiple file watchers - will cause duplicate event processing
- ❌ Don't ignore memory usage patterns - can cause OOM with large conversation files
- ❌ Don't skip checkpoint persistence - will lose progress on system restart

---

**PRP Confidence Score: 9/10**

This PRP provides comprehensive context for one-pass implementation success through:
- ✅ Complete codebase analysis with integration patterns
- ✅ Technology research with July 2025 updates and version compatibility
- ✅ Detailed implementation blueprint with specific technical requirements  
- ✅ Executable validation gates with performance benchmarks
- ✅ Error handling strategies and recovery mechanisms
- ✅ Integration points clearly mapped to existing architecture
- ✅ Anti-patterns documented to prevent common pitfalls

The implementation transforms the manual rebuild architecture to real-time event-driven processing while maintaining compatibility with existing MCP tools and database structure.