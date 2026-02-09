#!/usr/bin/env python3
"""
Test the exact query that analyze_solution_feedback_patterns should be using
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

def test_direct_solution_query():
    """Test the exact query that should work for solution patterns"""
    
    logger.info("🔍 Testing direct solution pattern query...")
    
    # Create completely fresh database connection
    db = ClaudeVectorDatabase()
    
    try:
        # Method 1: Direct ChromaDB query (this worked in our tests)
        logger.info("Method 1: Direct ChromaDB query for is_solution_attempt=True")
        direct_results = db.collection.get(
            where={'is_solution_attempt': {'$eq': True}},
            include=['documents', 'metadatas'],
            limit=20
        )
        
        direct_count = len(direct_results['documents'])
        logger.info(f"✅ Direct query found: {direct_count} solution attempts")
        
        # Method 2: Check if search_conversations_enhanced method exists
        logger.info("Method 2: Testing search_conversations_enhanced method")
        if hasattr(db, 'search_conversations_enhanced'):
            logger.info("✅ search_conversations_enhanced method exists")
            try:
                enhanced_results = db.search_conversations_enhanced(
                    query="solution implementation code fix",
                    current_project=None,
                    n_results=20,
                    prefer_solutions=True,
                    show_context_chain=True,
                    include_metadata=True
                )
                logger.info(f"✅ Enhanced search returned: {len(enhanced_results)} results")
                
                # Check if any have is_solution_attempt
                solution_count = 0
                for result in enhanced_results:
                    if result.get('is_solution_attempt'):
                        solution_count += 1
                
                logger.info(f"✅ Enhanced search solutions: {solution_count}")
                
            except Exception as e:
                logger.error(f"❌ Enhanced search failed: {e}")
        else:
            logger.warning("❌ search_conversations_enhanced method does NOT exist")
        
        # Method 3: Try search_conversations method
        logger.info("Method 3: Testing search_conversations method")
        if hasattr(db, 'search_conversations'):
            try:
                basic_results = db.search_conversations(
                    query="solution implementation",
                    n_results=20
                )
                logger.info(f"✅ Basic search returned: {len(basic_results)} results")
            except Exception as e:
                logger.error(f"❌ Basic search failed: {e}")
        else:
            logger.warning("❌ search_conversations method does NOT exist")
        
        # Method 4: List all available methods
        logger.info("Method 4: Available database methods")
        methods = [method for method in dir(db) if not method.startswith('_') and callable(getattr(db, method))]
        logger.info(f"📝 Available methods: {methods}")
        
        return {
            'direct_query_count': direct_count,
            'has_enhanced_search': hasattr(db, 'search_conversations_enhanced'),
            'has_basic_search': hasattr(db, 'search_conversations'),
            'available_methods': methods
        }
        
    except Exception as e:
        logger.error(f"❌ Error in direct query test: {e}")
        return None

if __name__ == "__main__":
    logger.info("🚀 Starting direct query test...")
    results = test_direct_solution_query()
    
    if results:
        logger.info(f"🏁 Test complete:")
        logger.info(f"   Direct ChromaDB query: {results['direct_query_count']} solutions")
        logger.info(f"   Enhanced search available: {results['has_enhanced_search']}")
        logger.info(f"   Basic search available: {results['has_basic_search']}")
    else:
        logger.info("🏁 Test failed")