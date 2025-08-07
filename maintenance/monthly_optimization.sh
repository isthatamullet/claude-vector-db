#!/bin/bash
# Monthly Production Optimization

echo "⚙️ Monthly System Optimization"
echo "=============================="
date

cd /home/user/.claude-vector-db-enhanced

# 1. Performance Analysis
echo "Step 1: Performance Analysis"
if [ -f "system/performance_monitor.sh" ]; then
    echo "Running extended performance test..."
    bash system/performance_monitor.sh
fi

# 2. Archive Cleanup Review
echo ""
echo "Step 2: Archive Cleanup Review"
if [ -d "migration_backup" ]; then
    MIGRATION_SIZE=$(du -sh migration_backup | cut -f1)
    echo "📁 Migration backup size: $MIGRATION_SIZE"
    echo "💡 Review migration_backup - consider cleanup if stable >3 months"
fi

# 3. Log Cleanup
echo ""
echo "Step 3: Log File Cleanup"
LOG_SIZE=$(find . -name "*.log" -type f -exec du -sh {} + 2>/dev/null | awk '{sum+=$1} END {print sum}' || echo "0")
echo "📊 Log files size: ${LOG_SIZE}MB"

# Find old log files (>30 days)
OLD_LOGS=$(find . -name "*.log" -mtime +30 2>/dev/null | wc -l)
if [ $OLD_LOGS -gt 0 ]; then
    echo "🗑️ Old log files found: $OLD_LOGS (>30 days)"
    echo "💡 Consider archiving old log files"
fi

# 4. System Statistics
echo ""
echo "Step 4: System Statistics"
echo "Total system size: $(du -sh --exclude=venv . | cut -f1)"
echo "ChromaDB size: $(du -sh chroma_db 2>/dev/null | cut -f1)"
echo "Archive size: $(du -sh archive 2>/dev/null | cut -f1 || echo "0")"

echo ""
echo "✅ Monthly optimization review complete"