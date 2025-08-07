#!/bin/bash
# Production Performance Monitor
echo "📊 Vector Database Performance Monitor"
echo "====================================="

cd /home/user/.claude-vector-db-enhanced

# Database performance test
echo "Testing database performance..."
PERF_RESULT=$(./venv/bin/python -c "
import sys, time
sys.path.insert(0, '$(pwd)')
from database.vector_database import ClaudeVectorDatabase

# Test initialization time
start = time.time()
db = ClaudeVectorDatabase()
init_time = (time.time() - start) * 1000

# Test query time
if db.collection.count() > 0:
    start = time.time()
    results = db.collection.query(
        query_texts=['performance monitoring test'],
        n_results=min(5, db.collection.count())
    )
    query_time = (time.time() - start) * 1000
    print(f'{init_time:.1f},{query_time:.1f},{db.collection.count()}')
else:
    print(f'{init_time:.1f},0.0,0')
" 2>/dev/null || echo "Error,Error,Error")

if [ "$PERF_RESULT" != "Error,Error,Error" ]; then
    INIT_TIME=$(echo $PERF_RESULT | cut -d',' -f1)
    QUERY_TIME=$(echo $PERF_RESULT | cut -d',' -f2) 
    ENTRY_COUNT=$(echo $PERF_RESULT | cut -d',' -f3)
    
    echo "📈 Performance Results:"
    echo "   Database initialization: ${INIT_TIME}ms"
    echo "   Query response time: ${QUERY_TIME}ms"
    echo "   Database entries: $ENTRY_COUNT"
    
    # Performance assessment
    if [ $(echo "$QUERY_TIME < 500" | bc -l 2>/dev/null || echo "1") -eq 1 ]; then
        echo "✅ Performance: Within target (<500ms)"
    else
        echo "⚠️ Performance: Slower than target (>500ms)"
    fi
else
    echo "❌ Performance test failed"
fi

# Memory usage check
echo "Checking memory usage..."
MEMORY_INFO=$(ps aux | grep -E "(mcp_server|python.*vector)" | grep -v grep | awk '{sum+=$6} END {print sum/1024}' 2>/dev/null || echo "0")
echo "📊 Memory usage: ${MEMORY_INFO}MB"

echo "✅ Performance monitoring complete"