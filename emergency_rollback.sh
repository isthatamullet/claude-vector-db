#!/bin/bash
# emergency_rollback.sh - PRP-3 Emergency Rollback Script
# Based on successful PRP-2 rollback procedures

echo "🚨 Emergency MCP Tool Rollback - PRP-3 Implementation"
echo "Restoring backup using PRP-2 validated procedures..."

# Stop any running processes
echo "Stopping MCP server processes..."
pkill -f mcp_server.py

# Check if backup exists
BACKUP_FILE="/home/user/.claude-vector-db-enhanced/mcp/mcp_server.py.backup-before-prp3"
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ ERROR: Backup file not found at $BACKUP_FILE"
    echo "Cannot perform rollback without backup!"
    exit 1
fi

# Restore backup
echo "Restoring backup from before PRP-3 implementation..."
cp "$BACKUP_FILE" "/home/user/.claude-vector-db-enhanced/mcp/mcp_server.py"

# Verify rollback success using backup validation
echo "Verifying rollback..."
tool_count=$(grep -c "@mcp.tool" /home/user/.claude-vector-db-enhanced/mcp/mcp_server.py)
echo "Tool count after rollback: $tool_count"

# Check for PRP-3 markers (should be absent after rollback)
prp3_markers=$(grep -c "prp3_consolidation" /home/user/.claude-vector-db-enhanced/mcp/mcp_server.py)
echo "PRP-3 markers found: $prp3_markers (should be 0)"

if [ "$prp3_markers" -eq 0 ]; then
    echo "✅ Rollback successful: PRP-3 implementation removed"
    echo "✅ MCP server restored to pre-PRP-3 state"
else
    echo "⚠️ Rollback verification warning: PRP-3 markers still present"
fi

echo ""
echo "📊 Rollback Summary:"
echo "  - Backup restored: ✅"
echo "  - Tool count: $tool_count"
echo "  - PRP-3 markers: $prp3_markers"
echo ""
echo "🔄 Next steps:"
echo "  1. Restart Claude to reload MCP server"
echo "  2. Test basic MCP functionality"
echo "  3. Investigate rollback cause if needed"
echo ""
echo "✅ Emergency rollback complete!"