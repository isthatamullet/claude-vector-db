# Enhanced Batch Sync Guide

This guide explains how to use the batch processing system for enhanced conversation sync that stays within Claude Code's 2-minute timeout limits.

## Quick Start

### Single Batch Processing
```bash
# Process 4 files (recommended batch size)
./venv/bin/python run_enhanced_batch_sync.py

# Process 6 files (medium batch)
./venv/bin/python run_enhanced_batch_sync.py --batch-size 6

# Check current progress
./venv/bin/python run_enhanced_batch_sync.py --stats

# Reset and start fresh
./venv/bin/python run_enhanced_batch_sync.py --reset
```

### Multiple Batch Processing
```bash
# Run 5 batches automatically (recommended)
./venv/bin/python run_multiple_batches.py

# Run 3 batches with smaller batch size
./venv/bin/python run_multiple_batches.py --batches 3 --batch-size 3

# Run many small batches for safety
./venv/bin/python run_multiple_batches.py --batches 10 --batch-size 2
```

## Batch Size Recommendations

Based on testing with Claude Code's 2-minute timeout:

| Batch Size | Processing Time | Status | Recommendation |
|------------|-----------------|--------|----------------|
| 2-4 files  | 30-90 seconds   | ✅ Safe | **Recommended** |
| 5-6 files  | 60-110 seconds  | ⚠️ Medium | Use with caution |
| 7+ files   | 120+ seconds    | ❌ Risky | May timeout |

**Recommended**: Start with batch size 4, adjust based on your file complexity.

## Progress Tracking Features

### State File (`batch_sync_progress.json`)
The system automatically tracks:
- Total files and progress percentage
- Completed file list (prevents reprocessing)
- Running totals for database entries
- Enhancement statistics
- Last run timestamp
- Current batch number

### Resume Capability
- **Automatic Resume**: Simply run the script again to continue where you left off
- **No Duplicate Processing**: Completed files are tracked and skipped
- **Cross-Session Persistence**: Progress survives Claude Code session restarts

### Progress Statistics
```bash
# Show detailed progress
./venv/bin/python run_enhanced_batch_sync.py --stats
```

Shows:
- Files processed vs total (with percentage)
- Database entry counts
- Enhancement statistics (topics, solutions, feedback, adjacency)
- Estimated batches remaining

## Enhanced Processing Features

Each batch processes files with full enhancements:

### Topic Detection
- Automatically detects conversation topics
- Tracks topic coverage across files

### Solution Quality Scoring
- Identifies high-quality solution content
- Measures solution effectiveness

### Feedback Sentiment Analysis
- Analyzes user feedback sentiment
- Tracks feedback patterns

### Adjacency Relationships
- Links related conversation messages
- Builds conversation flow context

## Typical Workflow

### Complete Database Rebuild
1. **Reset** (optional): `./venv/bin/python run_enhanced_batch_sync.py --reset`
2. **Process in batches**: Run `./venv/bin/python run_enhanced_batch_sync.py` repeatedly
3. **Check progress**: Use `--stats` flag between batches
4. **Multiple batches**: Use `run_multiple_batches.py` for automation

### Example Session (114 files)
```bash
# Check starting state
./venv/bin/python run_enhanced_batch_sync.py --stats

# Process first batch (4 files)
./venv/bin/python run_enhanced_batch_sync.py --batch-size 4
# Result: 4/114 files (3.5%) completed

# Process multiple batches automatically
./venv/bin/python run_multiple_batches.py --batches 5 --batch-size 4
# Result: 24/114 files (21.1%) completed

# Continue until complete...
```

## Error Handling

### Timeout Recovery
- If a batch times out, no progress is lost
- Reduce batch size and continue: `--batch-size 3`
- State file remains unchanged on timeout

### File Processing Errors
- Individual file errors don't stop the batch
- Errors are counted but files are marked complete
- View detailed error logs in output

### State File Corruption
- Delete `batch_sync_progress.json` to reset
- Use `--reset` flag for clean restart
- No data loss - JSONL files are source of truth

## Performance Optimization

### Batch Size Tuning
- **Large files**: Use smaller batches (2-3 files)
- **Small files**: Use larger batches (5-6 files)
- **Mixed sizes**: Use default batch size (4 files)

### Memory Management
- Each batch releases memory between files
- Large conversations (500+ entries) take more time
- Monitor with `--stats` for processing patterns

### Database Performance
- ChromaDB handles incremental additions efficiently
- No need to rebuild entire database
- Search performance improves as index grows

## Monitoring and Validation

### Progress Validation
```bash
# Check database size
./venv/bin/python -c "
from vector_database import ClaudeVectorDatabase
db = ClaudeVectorDatabase()
print(f'Database entries: {db.collection.count():,}')
"

# Check conversation files
find /home/user/.claude/projects -name "*.jsonl" | wc -l
```

### Enhancement Coverage
- Track topics detected per batch
- Monitor solution identification rates
- Validate feedback analysis coverage
- Verify adjacency relationship building

## Troubleshooting

### Common Issues

**"Batch times out at 2 minutes"**
- Reduce batch size: `--batch-size 3` or `--batch-size 2`
- Some files are very large and need smaller batches

**"No progress after timeout"**
- This is correct behavior - progress only saves on successful completion
- Reduce batch size and retry

**"State file shows wrong totals"**
- Use `--reset` to start fresh
- State file tracks cumulative totals across all batches

**"Database entries don't match expectations"**
- Enhanced entries may differ from raw JSONL entries
- Some entries may be filtered during enhancement processing
- Check enhancement statistics for coverage details

### Recovery Commands
```bash
# Complete reset
./venv/bin/python run_enhanced_batch_sync.py --reset

# Force state file regeneration
rm batch_sync_progress.json
./venv/bin/python run_enhanced_batch_sync.py --stats

# Database health check (via MCP)
# Use Claude Code MCP tool: get_vector_db_health
```

## Integration with Existing Tools

### Relationship to Other Scripts
- **`run_full_sync.py`**: Long-running script for complete processing
- **`run_enhanced_batch_sync.py`**: Timeout-friendly batch processing
- **`run_multiple_batches.py`**: Automated multiple batch execution

### MCP Tool Compatibility
The batch system works alongside existing MCP tools:
- `force_conversation_sync`: Alternative for small datasets
- `get_vector_db_health`: Monitor database status
- `search_conversations`: Use enhanced database immediately

### When to Use Each Approach
- **Batch Sync**: Best for Claude Code with timeout constraints
- **Full Sync**: Best for server environments or long-running processes
- **MCP Tools**: Best for small updates or status checks

---

This batch processing system enables efficient, timeout-safe enhanced conversation processing with comprehensive progress tracking and resume capabilities.