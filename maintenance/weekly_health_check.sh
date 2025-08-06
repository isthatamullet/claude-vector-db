#!/bin/bash
# Weekly Database Health Verification Script
# Complete Implementation Reference - Lines 598-608

echo "🔍 WEEKLY DATABASE HEALTH CHECK"
echo "==============================="
echo "Started at: $(date)"
echo ""

# Navigate to vector database directory
cd /home/user/.claude-vector-db-enhanced

echo "📊 Running comprehensive health check..."
./system/health_dashboard.sh

echo ""
echo "🔍 Running database integrity check..."
./venv/bin/python check_database_integrity.py

echo ""
echo "📋 Checking for new duplicates..."
./venv/bin/python verify_database_rebuild.py

echo ""
echo "✅ Weekly health check completed at: $(date)"
echo "Next check scheduled for: $(date -d '+7 days')"