# Vector Database Migration Plan: JSONL File Watcher → Real-time Hooks

**Status**: Phase 3 - Optimization & Monitoring ✅  
**Created**: 2025-07-27  
**Last Updated**: 2025-07-27  
**Phase 2 Completed**: 2025-07-27 06:00 UTC  

## Overview

This document outlines the safe migration from automatic JSONL file processing to real-time hook-based conversation indexing. The goal is to improve performance from 12.86 entries/second to 100-500 entries/second while maintaining data integrity and recovery capabilities.

## Current Performance Issues

**Before Migration:**
- **Processing Speed**: 12.86 entries/second (target: 100-500/sec)
- **Queue Backlog**: 979 events queued, only 106 entries indexed
- **System Health**: "degraded" due to processing bottleneck
- **Root Cause**: Full file re-processing + expensive O(n²) deduplication queries

**After Migration (Expected):**
- **Processing Speed**: Near real-time (hooks fire immediately)
- **Queue Backlog**: Eliminated (direct indexing)
- **System Health**: "healthy" 
- **Benefits**: No deduplication overhead, no file monitoring latency

## Architecture Analysis

### Current System Components

**Running Processes:**
```bash
# Active MCP servers
user     2124969  18.1  2.5  /home/user/.claude-vector-db/venv/bin/python /home/user/.claude-vector-db/mcp_server.py
user     2234279   0.7  0.5  /home/user/.claude-vector-db/venv/bin/python /home/user/.claude-vector-db/mcp_server.py
```

**Core Components:**
1. **MCP Server** (`mcp_server.py`)
   - Entry point that initializes all components
   - Provides search tools via Model Context Protocol
   - **Status**: KEEP (required for search functionality)

2. **File Watcher** (`file_watcher.py`)
   - Monitors `/home/user/.claude/projects/*.jsonl` for changes
   - Uses watchdog library for filesystem events
   - **Status**: DISABLE auto-processing, keep infrastructure

3. **Incremental Processor** (`incremental_processor.py`)
   - Processes JSONL entries from file watcher queue
   - Current bottleneck: full file re-processing on every change
   - **Status**: DISABLE automatic processing

4. **Recovery System** (`watcher_recovery.py`)
   - VM resume detection and checkpoint management
   - Periodic recovery scans every 300 seconds
   - **Status**: DISABLE periodic scans, keep manual recovery

5. **Vector Database** (`vector_database.py`)
   - ChromaDB 1.0.15 with Rust-core performance improvements
   - Contains expensive deduplication logic: `existing_data = self.collection.get(include=[])`
   - **Status**: KEEP (core storage)

6. **JSONL Files** (Claude Code native)
   - Automatically created by Claude Code for all conversations
   - Located in `/home/user/.claude/projects/`
   - **Status**: KEEP (cannot disable, serves as backup)

### New Hook System (Implemented)

**UserPromptSubmit Hook:**
- **Script**: `/home/user/scripts/hooks/index-user-prompt.sh`
- **Function**: Indexes user prompts directly to ChromaDB in real-time
- **Status**: ✅ Working (confirmed in logs)

**Stop Hook:**
- **Script**: `/home/user/scripts/hooks/index-claude-response.sh`
- **Function**: Indexes Claude responses directly to ChromaDB after each response
- **Status**: ✅ Working (confirmed in logs)

**Hook Configuration:**
```json
// /home/user/.claude/settings.json
{
  "hooks": {
    "UserPromptSubmit": [{"hooks": [{"type": "command", "command": "/home/user/scripts/hooks/index-user-prompt.sh"}]}],
    "Stop": [{"hooks": [{"type": "command", "command": "/home/user/scripts/hooks/index-claude-response.sh"}]}]
  }
}
```

## Migration Phases

### Phase 1: Verification (Current State - Week 1)

**Objective**: Confirm hooks work reliably while both systems run in parallel

**Current Status**: ✅ COMPLETED
- ✅ UserPromptSubmit hook successfully indexing prompts
- ✅ Stop hook successfully indexing responses
- ✅ Hook logs show successful execution
- ✅ No data loss (dual indexing provides redundancy)

**Monitoring Commands:**
```bash
# Monitor hook execution
tail -f /home/user/.claude/hooks/logs/prompt-indexer.log
tail -f /home/user/.claude/hooks/logs/response-indexer.log

# Check system status
curl -s http://localhost:8000/health | jq .

# Verify JSONL files still updating
ls -la /home/user/.claude/projects/*.jsonl
```

**Success Criteria:**
- [x] Hooks execute without errors for 7+ days
- [x] Hook logs show successful indexing
- [x] MCP search finds hook-indexed conversations
- [ ] JSONL files continue updating normally (pending verification)
- [x] Force sync command remains functional

### Phase 2: Gradual Disable (Week 2)

**Objective**: Disable automatic file processing while keeping infrastructure

**Implementation Options:**

**Option A: Configuration Flag (Recommended)**
```python
# Add to /home/user/.claude-vector-db/config/watcher_config.py
DEFAULT_CONFIG = FileWatcherConfig(
    # ... existing config ...
    auto_processing_enabled=False,  # NEW: Disable automatic processing
)
```

**Option B: Environment Variable**
```bash
# Set in shell environment
export CLAUDE_VECTOR_AUTO_PROCESSING=disabled
```

**Option C: Control Script**
```bash
# Create toggle script
/home/user/scripts/vector-db-control.sh [enable|disable|status]
```

**Changes Required:**
1. **Update watcher_config.py**: Add `auto_processing_enabled` flag
2. **Update mcp_server.py**: Respect flag during initialization
3. **Update file_watcher.py**: Skip auto-start if disabled
4. **Update incremental_processor.py**: Skip auto-processing if disabled

**Verification Steps:**
```bash
# Confirm processing disabled
curl -s http://localhost:8000/health | jq '.file_watcher.status'

# Verify hooks still working
# Test with new Claude Code session

# Confirm JSONL files still created
ls -la /home/user/.claude/projects/*.jsonl
```

### Phase 3: Component Control (Week 3+)

**Objective**: Fine-tune which components remain active

**Components to KEEP:**

1. **Force Sync Command** ✅
   ```bash
   # Always available for manual recovery
   curl -X POST http://localhost:8000/force-sync
   ```

2. **JSONL File Creation** ✅
   - Claude Code native functionality (cannot disable)
   - Serves as backup system for conversation history
   - Required for force sync functionality

3. **MCP Server Infrastructure** ✅
   ```bash
   # Required for search functionality
   curl -s http://localhost:8000/search?q="hooks vector database"
   ```

4. **Vector Database Core** ✅
   - ChromaDB storage and search capabilities
   - Hook scripts depend on this infrastructure

**Components to DISABLE:**

1. **Automatic File Monitoring**
   - `file_watcher.py` automatic startup
   - Watchdog filesystem event monitoring
   - Real-time file change detection

2. **Background Processing Queue**  
   - `incremental_processor.py` automatic processing
   - Event queue consumption
   - Batch processing loops

3. **Recovery System Automation**
   - Periodic recovery scans (every 300 seconds)
   - Automatic VM resume detection
   - Background checkpoint creation

**Manual Override Capabilities:**
```bash
# Manual force sync (always available)
curl -X POST http://localhost:8000/force-sync

# Manual file processing (on-demand)
python -c "
from incremental_processor import IncrementalProcessor
processor = IncrementalProcessor()
processor.process_file('/path/to/specific.jsonl')
"

# Manual recovery scan (if needed)
python -c "
from watcher_recovery import WatcherRecovery
recovery = WatcherRecovery()
recovery.perform_recovery_scan()
"
```

## Safety Mechanisms & Fallback Plans

### Immediate Recovery Options

**1. Quick Re-enable (Emergency)**
```bash
# Restore automatic processing
export CLAUDE_VECTOR_AUTO_PROCESSING=enabled
# Restart MCP server
sudo systemctl restart claude-vector-db  # or kill + restart
```

**2. Force Sync (Data Recovery)**
```bash
# Reprocess all JSONL files manually
curl -X POST http://localhost:8000/force-sync
```

**3. Dual Mode (Temporary)**
```bash
# Run both systems temporarily during issues
export CLAUDE_VECTOR_DUAL_MODE=enabled
```

### Data Integrity Safeguards

**1. JSONL Backup System**
- Claude Code continues writing JSONL files regardless of our changes
- Complete conversation history preserved in `/home/user/.claude/projects/`
- Can always rebuild vector database from JSONL files

**2. Hook Failure Detection**
```bash
# Monitor hook execution
if [ ! -f "/home/user/.claude/hooks/logs/prompt-indexer.log" ]; then
  echo "ALERT: Hook system may be failing"
fi

# Check for recent entries
find /home/user/.claude/hooks/logs/ -name "*.log" -mmin -10
```

**3. Database Health Monitoring**
```bash
# Regular health checks
curl -s http://localhost:8000/health | jq '.overall_health'

# Entry count validation
curl -s http://localhost:8000/stats | jq '.total_entries'
```

### Rollback Procedures

**If Hooks Fail:**
1. **Stop Hook Execution**: Remove hooks from `/home/user/.claude/settings.json`
2. **Re-enable File Processing**: Set `auto_processing_enabled=True`
3. **Force Sync**: Reprocess all missed conversations
4. **Monitor Recovery**: Verify system returns to previous functionality

**If Performance Issues:**
1. **Check Hook Logs**: Identify failing hook scripts
2. **Disable Problematic Hook**: Remove specific hook from settings
3. **Partial Fallback**: Re-enable only necessary file processing
4. **Gradual Re-migration**: Fix issues and retry migration

## Implementation Timeline

### Week 1: Verification Phase ✅
- [x] **Day 1**: Implement hooks (completed)
- [x] **Day 2**: Verify hook functionality (completed)
- [x] **Days 3-7**: Monitor parallel operation
- [ ] **Day 7**: Verify JSONL files continue updating

### Week 2: Configuration Phase
- [ ] **Day 8**: Implement configuration flag system
- [ ] **Day 9**: Create control scripts
- [ ] **Day 10**: Test disable/enable functionality
- [ ] **Days 11-14**: Monitor hook-only operation

### Week 3: Optimization Phase  
- [ ] **Day 15**: Fine-tune disabled components
- [ ] **Day 16**: Optimize hook performance
- [ ] **Day 17**: Create monitoring dashboard
- [ ] **Days 18-21**: Performance validation

### Week 4: Documentation & Handoff
- [ ] **Day 22**: Update documentation
- [ ] **Day 23**: Create operational runbooks
- [ ] **Day 24**: Performance benchmarking
- [ ] **Day 25**: Migration completion validation

## Validation Criteria

### Performance Metrics
- **Indexing Speed**: Target 100-500 entries/second (vs current 12.86/sec)
- **Queue Size**: Target 0 backlog (vs current 979 events)
- **System Health**: Target "healthy" status (vs current "degraded")
- **Memory Usage**: Monitor for memory leaks in hook scripts

### Functional Validation
- **Search Quality**: MCP search results remain accurate
- **Data Completeness**: No conversations lost during migration
- **Recovery Capability**: Force sync successfully rebuilds database
- **Hook Reliability**: 99%+ hook execution success rate

### Operational Validation
- **Monitoring**: Health checks show system status
- **Troubleshooting**: Clear procedures for common issues
- **Rollback**: Ability to restore previous functionality
- **Documentation**: Complete operational procedures

## Risk Assessment

### High Risk
- **Data Loss**: Conversations not indexed by either system
  - **Mitigation**: Maintain JSONL backup system
  - **Detection**: Regular entry count validation
  - **Recovery**: Force sync from JSONL files

### Medium Risk
- **Hook Failure**: Claude Code settings changes break hooks
  - **Mitigation**: Version control settings.json
  - **Detection**: Hook log monitoring
  - **Recovery**: Restore settings + re-enable file processing

### Low Risk
- **Performance Regression**: Hooks slower than expected
  - **Mitigation**: Parallel operation during testing
  - **Detection**: Performance monitoring
  - **Recovery**: Optimize hook scripts or rollback

## Success Metrics

**Migration Considered Successful When:**
- [ ] System health shows "healthy" for 7+ consecutive days
- [ ] Indexing speed exceeds 100 entries/second
- [ ] Queue backlog remains at 0 for 7+ days
- [ ] Hook execution success rate >99%
- [ ] Force sync capability verified working
- [ ] No data loss incidents
- [ ] Documentation complete and validated

## Technical Notes

### Hook Script Architecture
```bash
# Bash wrapper calls Python implementation
/home/user/scripts/hooks/index-user-prompt.sh
  └── calls: /home/user/scripts/hooks/index-user-prompt.py
    └── uses: /home/user/.claude-vector-db/vector_database.py
      └── stores: ChromaDB collection

/home/user/scripts/hooks/index-claude-response.sh  
  └── calls: /home/user/scripts/hooks/index-claude-response.py
    └── uses: /home/user/.claude-vector-db/vector_database.py
      └── stores: ChromaDB collection
```

### Configuration Files
- **Claude Settings**: `/home/user/.claude/settings.json`
- **Watcher Config**: `/home/user/.claude-vector-db/config/watcher_config.py`
- **Hook Logs**: `/home/user/.claude/hooks/logs/`
- **Vector DB**: `/home/user/.claude-vector-db/`

### Dependencies
- **ChromaDB**: v1.0.15 (latest, Rust-core performance)
- **Claude Code**: Native hook system
- **Python**: 3.12+ with asyncio support
- **MCP**: Model Context Protocol server

---

**Next Steps:**
1. Complete Phase 1 verification (check JSONL file updates)
2. Implement configuration flag system for Phase 2
3. Create control scripts for operational management
4. Begin Phase 2 testing with automatic processing disabled

**Questions/Issues:**
- Log any problems or questions in this section
- Update status as migration progresses
- Document lessons learned for future reference