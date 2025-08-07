#!/bin/bash
# Production Alert System

check_critical_issues() {
    echo "🚨 Production Critical Issues Check"
    echo "================================="
    
    cd /home/user/.claude-vector-db-enhanced
    ISSUES=0
    
    # Check 1: MCP Server can start
    echo "Checking MCP server..."
    timeout 15 ./venv/bin/python mcp/mcp_server.py &
    MCP_PID=$!
    sleep 10
    if kill $MCP_PID 2>/dev/null; then
        echo "✅ MCP Server: OK"
    else
        echo "🚨 CRITICAL: MCP Server cannot start"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check 2: Database accessible
    echo "Checking database..."
    DB_CHECK=$(./venv/bin/python -c "
import sys
sys.path.insert(0, '$(pwd)')
from database.vector_database import ClaudeVectorDatabase
db = ClaudeVectorDatabase()
print('OK')
" 2>/dev/null || echo "ERROR")
    
    if [ "$DB_CHECK" = "OK" ]; then
        echo "✅ Database: OK"
    else
        echo "🚨 CRITICAL: Database cannot be accessed"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check 3: Hooks present
    echo "Checking hooks..."
    if [ -f "/home/user/.claude/hooks/index-claude-response.py" ]; then
        echo "✅ Hooks: OK"
    else
        echo "🚨 CRITICAL: Hook files missing"
        ISSUES=$((ISSUES + 1))
    fi
    
    # Check 4: Disk space
    echo "Checking disk space..."
    DISK_USAGE=$(df . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -lt 90 ]; then
        echo "✅ Disk Space: OK (${DISK_USAGE}% used)"
    else
        echo "🚨 WARNING: Disk space low (${DISK_USAGE}% used)"
        ISSUES=$((ISSUES + 1))
    fi
    
    echo ""
    if [ $ISSUES -eq 0 ]; then
        echo "✅ No critical issues detected"
        return 0
    else
        echo "🚨 CRITICAL: $ISSUES issues found"
        return $ISSUES
    fi
}

# Run critical check
check_critical_issues