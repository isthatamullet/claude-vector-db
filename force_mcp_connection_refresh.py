#!/usr/bin/env python3
"""
Force MCP server database connection refresh by updating the global db variable
This should fix the stale connection issue where MCP tools can't see database updates
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from database.vector_database import ClaudeVectorDatabase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_connection_refresh():
    """
    Force the MCP server to refresh its database connection by 
    updating the global variables in the mcp_server module
    """
    
    logger.info("🔄 Forcing MCP server database connection refresh...")
    
    try:
        # Import the MCP server module to access global variables
        from mcp import mcp_server
        
        logger.info("📡 Accessing MCP server global variables...")
        
        # Force reset the global db variable to None, which will trigger 
        # a fresh connection on next access
        if hasattr(mcp_server, 'db'):
            old_db = mcp_server.db
            logger.info(f"🔄 Resetting global db variable (was: {type(old_db)})")
            mcp_server.db = None
        else:
            logger.info("📡 No global db variable found, creating fresh connection...")
        
        # Also reset extractor if it exists
        if hasattr(mcp_server, 'extractor'):
            old_extractor = mcp_server.extractor
            logger.info(f"🔄 Resetting global extractor variable (was: {type(old_extractor)})")
            mcp_server.extractor = None
        
        # Reset connection pool if it exists
        if hasattr(mcp_server, 'connection_pool'):
            old_pool = mcp_server.connection_pool
            logger.info(f"🔄 Clearing connection pool (had {len(old_pool.active_connections)} connections)")
            old_pool.active_connections.clear()
        
        logger.info("✅ MCP server connection refresh completed!")
        
        # Test that a fresh connection works
        logger.info("🧪 Testing fresh database connection...")
        test_db = ClaudeVectorDatabase()
        
        # Test the exact query that was failing
        solution_results = test_db.collection.get(
            where={'is_solution_attempt': {'$eq': True}},
            include=['documents', 'metadatas'],
            limit=5
        )
        
        logger.info(f"✅ Fresh connection test: Found {len(solution_results['documents'])} solution attempts")
        
        if len(solution_results['documents']) > 0:
            logger.info("🎉 SUCCESS: Fresh connections can see the updated data!")
            return True
        else:
            logger.warning("⚠️ Fresh connection still shows no solution attempts")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error during connection refresh: {e}")
        return False

def test_direct_mcp_import():
    """Test if we can import and access MCP server globals directly"""
    
    try:
        logger.info("🧪 Testing direct MCP server import access...")
        
        # Try to import the MCP server file directly
        sys.path.insert(0, '/home/user/.claude-vector-db-enhanced/mcp')
        import mcp_server
        
        logger.info(f"✅ Successfully imported mcp_server module")
        logger.info(f"📊 Global db variable: {type(mcp_server.db) if hasattr(mcp_server, 'db') else 'Not found'}")
        
        # Reset the global db variable
        if hasattr(mcp_server, 'db') and mcp_server.db is not None:
            logger.info("🔄 Resetting global db to None...")
            mcp_server.db = None
            logger.info("✅ Global db variable reset")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error importing MCP server: {e}")
        return False

if __name__ == "__main__":
    logger.info("🚀 Starting MCP connection refresh...")
    
    # Try both approaches
    success1 = test_direct_mcp_import()
    success2 = force_connection_refresh()
    
    if success1 or success2:
        logger.info("✅ Connection refresh completed successfully!")
        logger.info("💡 MCP tools should now see the database updates")
    else:
        logger.warning("⚠️ Connection refresh had issues")
    
    logger.info("🏁 Refresh complete")