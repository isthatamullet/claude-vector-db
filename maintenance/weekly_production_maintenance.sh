#!/bin/bash
# Weekly Production Maintenance for Claude Vector Database System

echo "🔧 Weekly Production Maintenance"
echo "==============================="
date

cd /home/user/.claude-vector-db-enhanced

# 1. Health Check
echo "Step 1: System Health Check"
if [ -f "system/health_dashboard.sh" ]; then
    bash system/health_dashboard.sh
else
    bash system/basic_health_check.sh
fi

# 2. Performance Check
echo ""
echo "Step 2: Performance Monitoring"
if [ -f "system/performance_monitor.sh" ]; then
    bash system/performance_monitor.sh
fi

# 3. Database Optimization Check
echo ""
echo "Step 3: Database Health"
DB_SIZE=$(du -sh chroma_db 2>/dev/null | cut -f1)
DB_ENTRIES=$(./venv/bin/python -c "
import sys
sys.path.insert(0, '$(pwd)')
from database.vector_database import ClaudeVectorDatabase
db = ClaudeVectorDatabase()
print(db.collection.count())
" 2>/dev/null)
echo "📊 Database size: $DB_SIZE"
echo "📊 Database entries: $DB_ENTRIES"

# 4. Backup Status Check
echo ""
echo "Step 4: Backup Status"
RECENT_BACKUPS=$(find .. -name "vector-db-*-backup-*.tar.gz" -mtime -7 | wc -l)
echo "📁 Recent backups (7 days): $RECENT_BACKUPS"

# 5. Archive Review (monthly check)
if [ $(date +%d) -le 7 ]; then
    echo ""
    echo "Step 5: Monthly Archive Review"
    if [ -d "migration_backup" ]; then
        MIGRATION_SIZE=$(du -sh migration_backup | cut -f1)
        MIGRATION_AGE=$(find migration_backup -name "*.json" -mtime +90 | wc -l)
        echo "📁 Migration backup: $MIGRATION_SIZE (files >90 days: $MIGRATION_AGE)"
        
        if [ $MIGRATION_AGE -gt 0 ]; then
            echo "💡 Consider reviewing migration_backup for cleanup"
        fi
    fi
fi

echo ""
echo "✅ Weekly maintenance complete"
echo "Next maintenance: $(date -d '+7 days' +%Y-%m-%d)"