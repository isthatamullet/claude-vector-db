name: "Vector Database File Watcher Auto-Recovery Enhancement"
description: |

## Purpose

Template optimized for AI agents to implement automatic recovery from VM suspend/resume cycles in the existing vector database file watcher system without requiring manual force sync commands.

## Core Principles

1. **Context is King**: Include ALL necessary documentation, examples, and caveats
2. **Validation Loops**: Provide executable tests/lints the AI can run and fix
3. **Information Dense**: Use keywords and patterns from the codebase
4. **Progressive Success**: Start simple, validate, then enhance

---

## Goal

Enhance the existing vector database file watcher recovery system to automatically detect and recover from VM suspend/resume cycles that cause watchdog file descriptors to become stale, eliminating the need for manual 10-minute force sync operations.

## Why

- **User Experience**: VM suspend/resume cycles currently break file watching, requiring manual intervention
- **System Reliability**: Automatic recovery ensures continuous file monitoring without user awareness
- **Performance Impact**: Current manual force sync takes 10+ minutes vs target 5-minute auto-recovery
- **Integration Value**: Maintains existing checkpoint and recovery architecture while adding VM resume detection

## What

Auto-recovery system that detects VM suspend/resume events and automatically reinitializes the file watcher when broken state is detected (0 files monitored despite healthy status).

### Success Criteria

- [ ] System automatically recovers within 5 minutes of VM resume
- [ ] Detection of broken file watcher state (0 files monitored but healthy status)
- [ ] Auto-reinitialize file watcher when broken state detected
- [ ] Maintain all existing functionality and pass existing test suite
- [ ] No external dependencies - use existing Python infrastructure
- [ ] Handle edge cases like multiple suspend/resume cycles

## All Needed Context

### Documentation & References (list all context needed to implement the feature)

```yaml
# MUST READ - Include these in your context window
- file: /home/user/.claude-vector-db/file_watcher.py
  why: Core file watching implementation using watchdog library
  critical: ConversationFileWatcher class and Observer pattern usage

- file: /home/user/.claude-vector-db/watcher_recovery.py  
  why: Existing recovery system with 60s checkpoints and 5-minute recovery scans
  critical: WatcherRecoverySystem class and recovery_loop implementation

- file: /home/user/.claude-vector-db/mcp_server.py
  why: MCP server integration and global instances management
  critical: File watcher initialization and status checking patterns

- file: /home/user/.claude-vector-db/config/watcher_config.py
  why: Configuration parameters and performance requirements
  critical: FileWatcherConfig class and DEFAULT_CONFIG usage

# CURRENT PROBLEM CONTEXT
- issue: VM suspend/resume breaks watchdog file descriptors but process doesn't detect this
- symptom: file_watcher.monitored_files becomes empty (0 files) despite healthy status
- current_solution: Manual force_conversation_sync() call every 10+ minutes
- target_solution: Automatic recovery within 5 minutes of VM resume
```

### Current Codebase tree (run `tree` in the root of the project) to get an overview of the codebase

```bash
/home/user/.claude-vector-db/
├── mcp_server.py                    # MCP server with file watcher integration
├── file_watcher.py                  # Core file watching with Observer pattern
├── watcher_recovery.py              # Recovery system with checkpoint persistence
├── incremental_processor.py        # Processing engine for file changes
├── vector_database.py              # ChromaDB vector storage
├── conversation_extractor.py       # JSONL conversation parsing
└── config/
    └── watcher_config.py           # Configuration and performance settings
```

### Desired Codebase tree with files to be added and responsibility of file

```bash
/home/user/.claude-vector-db/
├── mcp_server.py                    # [ENHANCED] Add VM resume detection MCP tool
├── file_watcher.py                  # [ENHANCED] Add reinitialize capability and broken state detection
├── watcher_recovery.py              # [ENHANCED] Add VM resume detection logic to recovery system
├── vm_resume_detector.py            # [NEW] VM suspend/resume detection utility class
├── config/
    └── watcher_config.py           # [ENHANCED] Add VM resume detection configuration
└── tests/
    └── test_vm_recovery.py         # [NEW] Test suite for VM recovery functionality
```

### Known Gotchas of our codebase & Library Quirks

```python
# CRITICAL: watchdog Observer uses inotify file descriptors that become stale after VM suspend
# Example: observer.start() creates file descriptors, VM suspend/resume breaks them silently
# Watchdog doesn't detect this - monitored_files becomes 0 but observer appears healthy

# CRITICAL: Recovery system runs every 5 minutes (recovery_scan_interval = 300)
# We need to detect broken state faster than current 5-minute recovery cycle

# PATTERN: Global instances in each module (file_watcher, recovery_system, etc.)
# Follow existing pattern: global variable + initialize/shutdown functions

# PATTERN: MCP tools use ensure_file_watcher_initialized() pattern
# Always check initialization before accessing global instances

# GOTCHA: ChromaDB SQLite has 166 entry batch limit (max_batch_size)
# Don't exceed this during recovery processing

# PATTERN: All async operations use asyncio.create_task() for background tasks
# Don't block main thread during recovery operations

# CRITICAL: VM resume detection must work without external dependencies
# Use Python standard library only (os, time, threading, asyncio)
```

## Implementation Blueprint

### Data models and structure

Create the core data models to ensure type safety and consistency.

```python
# VM Resume Detection Models
@dataclass
class VMResumeEvent:
    """Represents a detected VM suspend/resume cycle."""
    suspend_detected_at: float
    resume_detected_at: float
    duration_seconds: float
    file_descriptors_affected: bool
    recovery_triggered: bool

@dataclass 
class FileWatcherHealthCheck:
    """Health check results for file watcher state."""
    is_observer_running: bool
    monitored_files_count: int
    expected_files_count: int
    is_broken_state: bool
    last_event_timestamp: Optional[float]
    needs_reinitialize: bool

# Enhanced Configuration
@dataclass
class VMRecoveryConfig:
    """Configuration for VM resume detection and recovery."""
    vm_check_interval: int = 30  # Check every 30 seconds
    broken_state_threshold: int = 5  # Consider broken if 0 files for 5+ checks
    resume_detection_methods: List[str] = field(default_factory=lambda: ["uptime", "boot_time"])
    auto_recovery_enabled: bool = True
    max_recovery_attempts: int = 3
```

### List of tasks to be completed to fulfill the PRP in the order they should be completed

```yaml
Task 1:
CREATE /home/user/.claude-vector-db/vm_resume_detector.py:
  - IMPLEMENT VMResumeDetector class with uptime-based detection
  - MIRROR pattern from: watcher_recovery.py async background tasks
  - DETECT VM resume by monitoring system uptime changes
  - KEEP error handling pattern identical to existing recovery system

Task 2:
MODIFY /home/user/.claude-vector-db/config/watcher_config.py:
  - FIND pattern: "DEFAULT_CONFIG = FileWatcherConfig()"
  - INJECT VMRecoveryConfig class before DEFAULT_CONFIG
  - ADD vm_recovery_config field to FileWatcherConfig
  - PRESERVE existing configuration structure

Task 3:
MODIFY /home/user/.claude-vector-db/file_watcher.py:
  - FIND pattern: "class ConversationFileWatcher"
  - INJECT reinitialize_observer() method after stop() method
  - ADD is_in_broken_state() health check method
  - PRESERVE existing initialization and error handling patterns

Task 4:
MODIFY /home/user/.claude-vector-db/watcher_recovery.py:
  - FIND pattern: "class WatcherRecoverySystem" 
  - INJECT vm_resume_detector integration in __init__
  - ENHANCE _recovery_loop() to include VM resume checks
  - PRESERVE existing recovery scan intervals and checkpoint system

Task 5:
MODIFY /home/user/.claude-vector-db/mcp_server.py:
  - FIND pattern: "async def get_file_watcher_status()"
  - INJECT VM resume status information in status response
  - ADD broken state detection to determine_overall_health()
  - PRESERVE existing MCP tool patterns and error handling

Task 6:
CREATE /home/user/.claude-vector-db/tests/test_vm_recovery.py:
  - IMPLEMENT unit tests for VMResumeDetector
  - TEST broken state detection and auto-recovery
  - MOCK VM suspend/resume scenarios
  - FOLLOW existing test patterns from codebase
```

### Per task pseudocode as needed added to each task

```python
# Task 1: VM Resume Detector
class VMResumeDetector:
    def __init__(self, config: VMRecoveryConfig):
        self.config = config
        self._last_uptime = self._get_system_uptime()
        self._last_boot_time = self._get_boot_time()
        self._detection_task: Optional[asyncio.Task] = None
        
    async def start_detection(self):
        """Start background VM resume detection."""
        # PATTERN: Follow recovery_loop pattern from watcher_recovery.py
        self._detection_task = asyncio.create_task(self._detection_loop())
    
    async def _detection_loop(self):
        """Main detection loop checking for VM resume events."""
        while self.is_running:
            try:
                # CRITICAL: Check uptime - if decreased, VM was suspended/resumed
                current_uptime = self._get_system_uptime()
                if current_uptime < self._last_uptime:
                    # VM resume detected!
                    await self._handle_vm_resume()
                self._last_uptime = current_uptime
                
                await asyncio.sleep(self.config.vm_check_interval)
            except Exception as e:
                self.logger.error(f"Error in VM detection loop: {e}")

# Task 3: File Watcher Broken State Detection  
async def is_in_broken_state(self) -> bool:
    """Detect if file watcher is in broken state."""
    # CRITICAL: Broken state = Observer running but 0 monitored files
    if not self.observer or not self.observer.is_alive():
        return True
    
    # PATTERN: Count expected files vs monitored files
    expected_count = await self._count_expected_files()
    actual_count = len(self.monitored_files)
    
    # GOTCHA: If we should have files but don't, we're broken
    return expected_count > 0 and actual_count == 0

async def reinitialize_observer(self) -> bool:
    """Reinitialize the watchdog observer after VM resume."""
    try:
        self.logger.info("Reinitializing file watcher after VM resume...")
        
        # PATTERN: Follow existing stop/start pattern
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=5.0)
        
        # CRITICAL: Recreate observer with fresh file descriptors
        self.observer = Observer()
        self.event_handler = ConversationFileHandler(self)
        self.observer.schedule(
            self.event_handler,
            self.config.watch_directory,
            recursive=self.config.recursive
        )
        self.observer.start()
        
        # PATTERN: Rescan existing files after reinitialize
        await self._scan_existing_files()
        return True
        
    except Exception as e:
        self.logger.error(f"Failed to reinitialize observer: {e}")
        return False

# Task 4: Enhanced Recovery System
async def _recovery_loop(self):
    """Enhanced recovery loop with VM resume detection."""
    while self.is_running and not self._shutdown_event.is_set():
        try:
            # EXISTING: Wait for recovery scan interval
            await asyncio.wait_for(
                self._shutdown_event.wait(),
                timeout=self.config.recovery_scan_interval
            )
            break
            
        except asyncio.TimeoutError:
            # ENHANCED: Check for broken state before regular recovery
            if await self._check_and_handle_broken_state():
                self.logger.info("Auto-recovery completed, skipping regular scan")
                continue
                
            # EXISTING: Regular recovery scan
            await self.perform_recovery_scan()

async def _check_and_handle_broken_state(self) -> bool:
    """Check for broken file watcher state and auto-recover."""
    if not self.file_watcher:
        return False
        
    # CRITICAL: Detect broken state
    if await self.file_watcher.is_in_broken_state():
        self.logger.warning("Broken file watcher state detected - auto-recovering...")
        
        # PATTERN: Attempt reinitialize with retry logic
        success = await self.file_watcher.reinitialize_observer()
        if success:
            # CRITICAL: Force scan after reinitialize to catch missed events
            await self.perform_recovery_scan()
            return True
    
    return False
```

### Integration Points

```yaml
CONFIGURATION:
  - add to: config/watcher_config.py
  - pattern: "vm_recovery_config: VMRecoveryConfig = field(default_factory=VMRecoveryConfig)"

MCP_TOOLS:
  - enhance: get_file_watcher_status()
  - add_fields: ["vm_resume_detection", "broken_state_detected", "auto_recovery_status"]
  - pattern: Follow existing status aggregation in determine_overall_health()

RECOVERY_SYSTEM:
  - integrate: vm_resume_detector in WatcherRecoverySystem.__init__
  - enhance: _recovery_loop() with broken state detection
  - preserve: existing checkpoint and recovery scan intervals

LOGGING:
  - add to: existing logger instances
  - pattern: self.logger.info/warning/error for VM resume events
  - levels: INFO for successful recovery, WARNING for broken state detection
```

## Validation Loop

### Level 1: Syntax & Style

```bash
# Run these FIRST - fix any errors before proceeding
ruff check /home/user/.claude-vector-db/vm_resume_detector.py --fix
ruff check /home/user/.claude-vector-db/file_watcher.py --fix  
ruff check /home/user/.claude-vector-db/watcher_recovery.py --fix
mypy /home/user/.claude-vector-db/vm_resume_detector.py
mypy /home/user/.claude-vector-db/file_watcher.py
mypy /home/user/.claude-vector-db/watcher_recovery.py

# Expected: No errors. If errors, READ the error and fix.
```

### Level 2: Unit Tests each new feature/file/function use existing test patterns

```python
# CREATE test_vm_recovery.py with these test cases:
def test_vm_resume_detection():
    """VM resume detection works correctly"""
    detector = VMResumeDetector(VMRecoveryConfig())
    # Mock uptime change to simulate VM resume
    with patch.object(detector, '_get_system_uptime', side_effect=[100, 50, 60]):
        result = await detector._check_for_resume()
        assert result.resume_detected is True

def test_broken_state_detection():
    """Broken file watcher state detected correctly"""
    watcher = ConversationFileWatcher()
    watcher.observer = Mock()
    watcher.observer.is_alive.return_value = True
    watcher.monitored_files = set()  # Empty but should have files
    
    with patch.object(watcher, '_count_expected_files', return_value=5):
        is_broken = await watcher.is_in_broken_state()
        assert is_broken is True

def test_auto_recovery_flow():
    """Auto-recovery flow works end-to-end"""
    recovery_system = WatcherRecoverySystem(file_watcher, processor)
    
    with patch.object(recovery_system.file_watcher, 'is_in_broken_state', return_value=True):
        with patch.object(recovery_system.file_watcher, 'reinitialize_observer', return_value=True):
            result = await recovery_system._check_and_handle_broken_state()
            assert result is True

def test_observer_reinitialize():
    """Observer reinitialize creates fresh file descriptors"""
    watcher = ConversationFileWatcher()
    old_observer = watcher.observer
    
    success = await watcher.reinitialize_observer()
    assert success is True
    assert watcher.observer is not old_observer  # New observer instance
    assert watcher.observer.is_alive() is True
```

```bash
# Run and iterate until passing:
cd /home/user/.claude-vector-db && python -m pytest tests/test_vm_recovery.py -v
# If failing: Read error, understand root cause, fix code, re-run (never mock to pass)
```

### Level 3: Integration Test

```bash
# Start the MCP server
cd /home/user/.claude-vector-db && python mcp_server.py

# Test VM resume detection via MCP
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "get_file_watcher_status"}}'

# Expected: {"file_watcher": {"status": "active", "files_monitored": >0}}
# If broken state: {"file_watcher": {"status": "active", "files_monitored": 0, "broken_state_detected": true}}

# Test force sync still works
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "force_conversation_sync"}}'

# Expected: {"success": true, "method": "recovery_system"}
```

### Level 4: Deployment & Creative Validation

```bash
# Simulate VM suspend/resume scenario
# 1. Start file watcher system
cd /home/user/.claude-vector-db && python mcp_server.py &
MCP_PID=$!

# 2. Verify normal operation  
sleep 10
curl -s http://localhost:8000/mcp -d '{"method": "tools/call", "params": {"name": "get_file_watcher_status"}}' | jq '.file_watcher.files_monitored'

# 3. Simulate broken state by killing observer file descriptors (creative test)
# This mimics what happens during VM suspend/resume
pkill -f "inotify" 2>/dev/null || true

# 4. Wait for auto-recovery (should happen within 5 minutes)
for i in {1..10}; do
    echo "Check $i/10 - waiting for auto-recovery..."
    FILES_COUNT=$(curl -s http://localhost:8000/mcp -d '{"method": "tools/call", "params": {"name": "get_file_watcher_status"}}' | jq '.file_watcher.files_monitored')
    if [ "$FILES_COUNT" -gt 0 ]; then
        echo "✅ Auto-recovery successful! Files monitored: $FILES_COUNT"
        break
    fi
    sleep 30
done

# Cleanup
kill $MCP_PID
```

## 🚨 MANDATORY RECOVERY PLAN 🚨

**CRITICAL**: Follow this recovery plan EXACTLY to ensure safe implementation with zero data loss and full rollback capability.

### Phase 1: Pre-Implementation Safety Backup

**STEP 1**: Create complete system backup before ANY changes:

```bash
# Create timestamped backup directory
BACKUP_DIR="/home/user/.claude-vector-db.backup-$(date +%Y%m%d-%H%M%S)"
echo "Creating backup at: $BACKUP_DIR"

# Full system backup with permissions preserved
cp -rp /home/user/.claude-vector-db "$BACKUP_DIR"

# Backup vector database data separately
cp -rp /home/user/.claude-vector-db/chroma_db "$BACKUP_DIR/chroma_db.safe"

# Backup checkpoint file separately (critical for recovery state)
cp /home/user/.claude-vector-db/file_watcher_checkpoint.json "$BACKUP_DIR/checkpoint.safe"

# Verify backup integrity
echo "Verifying backup integrity..."
diff -r /home/user/.claude-vector-db/mcp_server.py "$BACKUP_DIR/mcp_server.py" && echo "✅ Backup verified"

# Record current system state
cd /home/user/.claude-vector-db
python -c "
import json
from pathlib import Path
backup_info = {
    'backup_timestamp': '$(date -Iseconds)',
    'original_files': [str(p) for p in Path('.').rglob('*.py')],
    'vector_db_size': $(du -sb chroma_db | cut -f1),
    'checkpoint_exists': $(test -f file_watcher_checkpoint.json && echo 'true' || echo 'false')
}
with open('$BACKUP_DIR/backup_manifest.json', 'w') as f:
    json.dump(backup_info, f, indent=2)
print('📋 Backup manifest created')
"
```

**STEP 2**: Verify system is working before changes:

```bash
# Test current system functionality
cd /home/user/.claude-vector-db

# Verify MCP server starts
timeout 10s python mcp_server.py &
MCP_PID=$!
sleep 5
if kill -0 $MCP_PID 2>/dev/null; then
    echo "✅ MCP server starts successfully"
    kill $MCP_PID
else
    echo "❌ MCP server failed to start - DO NOT PROCEED"
    exit 1
fi

# Verify file watcher status
python -c "
import json
from mcp_server import mcp
print('✅ Current system baseline established')
"
```

### Phase 2: Safe Implementation Strategy

**STEP 3**: Implement with staged rollback points:

```bash
# Create implementation log
IMPL_LOG="/tmp/vm-recovery-implementation-$(date +%Y%m%d-%H%M%S).log"
echo "Implementation started: $(date)" > "$IMPL_LOG"

# Stage 1: Config changes only (safest)
echo "STAGE 1: Config modifications" >> "$IMPL_LOG"
# Implement config changes, test, then checkpoint

# Stage 2: Utility classes (VM detector)  
echo "STAGE 2: VM detector utility" >> "$IMPL_LOG"
# Implement VM detector, test independently, then checkpoint

# Stage 3: File watcher enhancements
echo "STAGE 3: File watcher enhancements" >> "$IMPL_LOG"
# Modify file watcher with broken state detection

# Stage 4: Recovery system integration
echo "STAGE 4: Recovery system integration" >> "$IMPL_LOG"  
# Integrate with existing recovery system

# Stage 5: MCP server updates
echo "STAGE 5: MCP server updates" >> "$IMPL_LOG"
# Final MCP tool enhancements
```

### Phase 3: Failure Detection & Auto-Rollback

**STEP 4**: Automated failure detection during implementation:

```bash
# Function to test system health after each change
test_system_health() {
    local stage_name="$1"
    echo "🔍 Testing system health after $stage_name..."
    
    # Test 1: Python syntax check
    if ! python -m py_compile /home/user/.claude-vector-db/mcp_server.py; then
        echo "❌ SYNTAX ERROR - Rolling back $stage_name"
        return 1
    fi
    
    # Test 2: MCP server starts
    timeout 15s python /home/user/.claude-vector-db/mcp_server.py &
    local mcp_pid=$!
    sleep 8
    if ! kill -0 $mcp_pid 2>/dev/null; then
        echo "❌ MCP SERVER FAILED - Rolling back $stage_name"
        return 1
    fi
    kill $mcp_pid
    
    # Test 3: File watcher initializes
    python -c "
import sys
sys.path.append('/home/user/.claude-vector-db')
try:
    from file_watcher import initialize_file_watcher
    from config.watcher_config import DEFAULT_CONFIG
    print('✅ File watcher imports successfully')
except Exception as e:
    print(f'❌ IMPORT ERROR: {e}')
    sys.exit(1)
    " || return 1
    
    echo "✅ System health check passed for $stage_name"
    return 0
}

# Use after each implementation stage:
# test_system_health "Stage 1: Config" || rollback_to_backup
```

### Phase 4: Emergency Rollback Procedures

**STEP 5**: Complete system rollback (if anything goes wrong):

```bash
# EMERGENCY ROLLBACK FUNCTION
emergency_rollback() {
    echo "🚨 EMERGENCY ROLLBACK INITIATED 🚨"
    
    # Stop any running MCP processes
    pkill -f "mcp_server.py" || true
    sleep 3
    
    # Find most recent backup
    LATEST_BACKUP=$(ls -td /home/user/.claude-vector-db.backup-* | head -1)
    if [ -z "$LATEST_BACKUP" ]; then
        echo "❌ NO BACKUP FOUND - MANUAL RECOVERY REQUIRED"
        exit 1
    fi
    
    echo "📦 Restoring from: $LATEST_BACKUP"
    
    # Remove broken implementation
    rm -rf /home/user/.claude-vector-db.broken 2>/dev/null || true
    mv /home/user/.claude-vector-db /home/user/.claude-vector-db.broken
    
    # Restore from backup
    cp -rp "$LATEST_BACKUP" /home/user/.claude-vector-db
    
    # Verify restoration
    if test_system_health "ROLLBACK"; then
        echo "✅ ROLLBACK SUCCESSFUL - System restored"
        echo "🗑️  Broken implementation saved at: /home/user/.claude-vector-db.broken"
        echo "📋 Check logs at: $IMPL_LOG"
    else
        echo "❌ ROLLBACK FAILED - MANUAL INTERVENTION REQUIRED"
        echo "💾 Backup location: $LATEST_BACKUP"
        exit 1
    fi
}

# Call this function if ANY stage fails:
# emergency_rollback
```

### Phase 5: Data Integrity Validation

**STEP 6**: Vector database integrity checks:

```bash
# Validate vector database after implementation
validate_vector_db() {
    echo "🔍 Validating vector database integrity..."
    
    python -c "
import sys
sys.path.append('/home/user/.claude-vector-db')
from vector_database import ClaudeVectorDatabase

try:
    db = ClaudeVectorDatabase()
    
    # Test basic operations
    results = db.search_conversations('test query', n_results=1)
    entry_count = len(db.collection.get()['ids'])
    
    print(f'✅ Vector DB operational: {entry_count} entries')
    
    # Compare with backup count if available
    import json
    with open('$LATEST_BACKUP/backup_manifest.json', 'r') as f:
        backup_info = json.load(f)
    
    print(f'📊 Backup had: {backup_info.get(\"vector_db_size\", \"unknown\")} bytes')
    print('✅ Vector database validation complete')
    
except Exception as e:
    print(f'❌ VECTOR DB ERROR: {e}')
    sys.exit(1)
    "
}
```

### Phase 6: Post-Implementation Verification

**STEP 7**: Comprehensive system validation:

```bash
# Full system validation after successful implementation
validate_implementation() {
    echo "🎯 Comprehensive post-implementation validation..."
    
    # Test all critical paths
    cd /home/user/.claude-vector-db
    
    # 1. All tests pass
    python -m pytest tests/ -v || { echo "❌ Tests failed"; return 1; }
    
    # 2. No linting errors
    ruff check . --fix || { echo "❌ Linting failed"; return 1; }
    
    # 3. Type checking passes
    mypy vm_resume_detector.py || { echo "❌ Type check failed"; return 1; }
    
    # 4. MCP server functionality
    timeout 20s python mcp_server.py &
    MCP_PID=$!
    sleep 10
    
    # Test VM recovery status endpoint
    python -c "
import asyncio
import sys
sys.path.append('.')
from mcp_server import get_file_watcher_status
async def test():
    status = await get_file_watcher_status()
    if 'vm_resume_detection' not in str(status):
        print('❌ VM resume detection not in status')
        return False
    print('✅ VM resume detection integrated')
    return True
result = asyncio.run(test())
sys.exit(0 if result else 1)
    " || { kill $MCP_PID; echo "❌ MCP integration failed"; return 1; }
    
    kill $MCP_PID
    
    # 5. Validate vector database
    validate_vector_db || { echo "❌ Vector DB validation failed"; return 1; }
    
    echo "🎉 IMPLEMENTATION SUCCESSFUL - All validations passed!"
    return 0
}
```

### Recovery Plan Summary

**✅ SAFETY CHECKLIST**:
- [ ] Full system backup created with timestamp
- [ ] Vector database backed up separately  
- [ ] Checkpoint file preserved
- [ ] Backup integrity verified
- [ ] Current system baseline established
- [ ] Staged implementation with rollback points
- [ ] Automated health checks after each stage
- [ ] Emergency rollback procedure tested
- [ ] Data integrity validation performed
- [ ] Post-implementation verification complete

**📞 EMERGENCY CONTACTS**:
- Backup location: `/home/user/.claude-vector-db.backup-TIMESTAMP`
- Implementation log: `/tmp/vm-recovery-implementation-TIMESTAMP.log`
- Emergency rollback: `emergency_rollback()` function above

**⚠️  CRITICAL REMINDERS**:
1. **NEVER skip the backup step** - This is your only safety net
2. **Test after EVERY change** - Don't accumulate failures
3. **Use emergency rollback immediately** if anything breaks
4. **Preserve logs** for post-mortem analysis
5. **Validate data integrity** before declaring success

## Final validation Checklist

- [ ] All tests pass: `python -m pytest tests/test_vm_recovery.py -v`
- [ ] No linting errors: `ruff check /home/user/.claude-vector-db/ --fix`
- [ ] No type errors: `mypy /home/user/.claude-vector-db/vm_resume_detector.py`
- [ ] MCP server starts without errors: `python mcp_server.py`
- [ ] File watcher status includes VM resume detection info
- [ ] Auto-recovery completes within 5 minutes of broken state detection
- [ ] Existing functionality preserved (checkpoint system, recovery scans)
- [ ] Force sync manual command still works as fallback

---

## Anti-Patterns to Avoid

- ❌ Don't create new global state patterns when existing ones work
- ❌ Don't break existing recovery system timing (5-minute scans)
- ❌ Don't add external dependencies - use Python standard library only
- ❌ Don't ignore existing error handling patterns
- ❌ Don't skip VM resume edge cases (multiple suspend/resume cycles)
- ❌ Don't block main thread during recovery operations
- ❌ Don't exceed ChromaDB 166 entry batch limit during recovery
- ❌ Don't modify existing MCP tool signatures - only enhance responses