#!/usr/bin/env python3
"""
Test script to force database connection refresh and verify updates are visible
"""

import sys
import os
# Get package root directory (2 levels up from tests/integration/)
from pathlib import Path
PACKAGE_ROOT = Path(__file__).parent.parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from database.vector_database import ClaudeVectorDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_connection_refresh():
    """Test that a fresh database connection can see recent updates"""
    
    logger.info("🔄 Testing database connection refresh...")
    
    # Create a completely fresh database connection
    db = ClaudeVectorDatabase()
    
    # Search specifically for the session that was updated
    session_id = "f8a4b940-4909-44f7-9196-4ed1342872dc"
    
    logger.info(f"🔍 Searching for session: {session_id}")
    
    try:
        # Query the database directly for that session
        results = db.collection.get(
            where={"session_id": {"$eq": session_id}},
            include=['documents', 'metadatas'],
            limit=10
        )
        
        logger.info(f"📊 Found {len(results['documents'])} entries in session {session_id}")
        
        if len(results['documents']) > 0:
            # Check the first few entries for is_solution_attempt
            solution_attempts = 0
            
            for i, metadata in enumerate(results['metadatas'][:5]):
                entry_id = results['ids'][i] if 'ids' in results else f"entry_{i}"
                is_solution = metadata.get('is_solution_attempt', False)
                content_preview = results['documents'][i][:100] + "..." if len(results['documents'][i]) > 100 else results['documents'][i]
                
                logger.info(f"Entry {i+1} ({entry_id}): is_solution_attempt = {is_solution}")
                logger.info(f"  Content preview: {content_preview}")
                
                if is_solution:
                    solution_attempts += 1
            
            logger.info(f"✅ Found {solution_attempts} solution attempts out of {len(results['documents'])} entries")
            
            if solution_attempts > 0:
                logger.info("🎉 SUCCESS: Updates are visible in fresh database connection!")
                return True
            else:
                logger.warning("⚠️ No solution attempts found - updates may not be visible")
                return False
        else:
            logger.warning(f"❌ No entries found for session {session_id}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error querying database: {e}")
        return False

def test_solution_patterns_query():
    """Test the exact query that analyze_solution_feedback_patterns uses"""
    
    logger.info("🔍 Testing solution patterns query directly...")
    
    db = ClaudeVectorDatabase()
    
    try:
        # This is the exact query from analyze_solution_feedback_patterns
        solution_results = db.collection.get(
            where={'is_solution_attempt': {'$eq': True}},
            include=['documents', 'metadatas'],
            limit=50
        )
        
        logger.info(f"📊 Found {len(solution_results['documents'])} entries with is_solution_attempt=True")
        
        if len(solution_results['documents']) > 0:
            logger.info("🎉 SUCCESS: Solution attempts found!")
            
            # Show first few
            for i in range(min(3, len(solution_results['documents']))):
                metadata = solution_results['metadatas'][i]
                content_preview = solution_results['documents'][i][:100] + "..." if len(solution_results['documents'][i]) > 100 else solution_results['documents'][i]
                
                logger.info(f"Solution {i+1}:")
                logger.info(f"  is_solution_attempt: {metadata.get('is_solution_attempt')}")
                logger.info(f"  solution_category: {metadata.get('solution_category', 'None')}")
                logger.info(f"  content: {content_preview}")
                
            return True
        else:
            logger.warning("❌ No solution attempts found with is_solution_attempt=True")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error in solution patterns query: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting database connection refresh test...")
    
    # Test 1: Check specific session
    session_test = test_database_connection_refresh()
    
    # Test 2: Check solution patterns query
    solution_test = test_solution_patterns_query()
    
    if session_test and solution_test:
        logger.info("✅ All tests passed - database updates are visible!")
    else:
        logger.warning("⚠️ Some tests failed - database sync issue confirmed")
    
    logger.info("🏁 Test complete")