#!/usr/bin/env python3
"""
Claude Code Vector Database API Server
FastAPI backend service for semantic conversation search with project-aware filtering
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
import uvicorn
from datetime import datetime

from vector_database import ClaudeVectorDatabase

# Import file watcher components
from file_watcher import file_watcher
from incremental_processor import incremental_processor
from watcher_recovery import recovery_system

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Claude Code Vector Database API",
    description="Semantic search API for Claude conversation history with project-aware intelligent filtering",
    version="1.0.0"
)

# Add CORS middleware for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure as needed for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global database instance
db = None

# Pydantic models for API
class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query", min_length=1)
    current_project: Optional[str] = Field(None, description="Current project name for relevance boosting")
    n_results: int = Field(5, ge=1, le=50, description="Number of results to return")
    include_metadata: bool = Field(True, description="Include metadata in results")
    filter_conditions: Optional[Dict[str, Any]] = Field(None, description="ChromaDB filter conditions")

class SearchResult(BaseModel):
    id: str
    content: str
    relevance_score: float
    base_similarity: float
    project_boost: float
    rank: int
    type: Optional[str] = None
    project_name: Optional[str] = None
    project_path: Optional[str] = None
    timestamp: Optional[str] = None
    session_id: Optional[str] = None
    file_name: Optional[str] = None
    has_code: Optional[bool] = None
    tools_used: Optional[List[str]] = None
    content_length: Optional[int] = None

class SearchResponse(BaseModel):
    query: str
    current_project: Optional[str]
    results: List[SearchResult]
    total_found: int
    search_time_ms: float

class DatabaseStats(BaseModel):
    total_entries: int
    sample_size: Optional[int] = None
    projects: Dict[str, Dict[str, Any]]
    message_types: Dict[str, int]
    code_entries: int
    code_percentage: float

class RebuildResponse(BaseModel):
    success: bool
    message: str
    total_processed: int
    rebuild_results: Dict[str, int]
    final_stats: DatabaseStats

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize the vector database on startup"""
    global db
    
    logger.info("🚀 Starting Claude Code Vector Database API Server...")
    
    try:
        db = ClaudeVectorDatabase()
        logger.info("✅ Vector database initialized successfully")
        
        # Check if database needs initialization
        stats = db.get_collection_stats()
        if stats.get('total_entries', 0) == 0:
            logger.info("📊 Database is empty - use /rebuild endpoint to initialize")
        else:
            logger.info(f"📊 Database ready with {stats.get('total_entries', 0)} entries")
            
    except Exception as e:
        logger.error(f"❌ Failed to initialize vector database: {e}")
        raise

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database_initialized": db is not None
    }

# Search endpoint
@app.post("/search", response_model=SearchResponse)
async def search_conversations(request: SearchRequest):
    """
    Search conversations with project-aware intelligent filtering
    
    This endpoint performs semantic search across Claude conversation history,
    with intelligent boosting for results from the current project.
    """
    
    if not db:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    start_time = datetime.now()
    
    try:
        # Perform search
        results = db.search_conversations(
            query=request.query,
            current_project=request.current_project,
            n_results=request.n_results,
            include_metadata=request.include_metadata,
            filter_conditions=request.filter_conditions
        )
        
        # Convert to response format
        search_results = [SearchResult(**result) for result in results]
        
        search_time_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        return SearchResponse(
            query=request.query,
            current_project=request.current_project,
            results=search_results,
            total_found=len(search_results),
            search_time_ms=round(search_time_ms, 2)
        )
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

# Simple search endpoint with query parameters
@app.get("/search", response_model=SearchResponse)
async def search_conversations_get(
    q: str = Query(..., description="Search query"),
    project: Optional[str] = Query(None, description="Current project name"),
    limit: int = Query(5, ge=1, le=50, description="Number of results"),
    metadata: bool = Query(True, description="Include metadata")
):
    """
    Simple GET endpoint for searching conversations
    Useful for quick testing and browser-based access
    """
    
    request = SearchRequest(
        query=q,
        current_project=project,
        n_results=limit,
        include_metadata=metadata
    )
    
    return await search_conversations(request)

# Database statistics endpoint
@app.get("/stats", response_model=DatabaseStats)
async def get_database_stats():
    """Get statistics about the vector database"""
    
    if not db:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        stats = db.get_collection_stats()
        return DatabaseStats(**stats)
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Rebuild database endpoint
@app.post("/rebuild", response_model=RebuildResponse)
async def rebuild_database(
    background_tasks: BackgroundTasks,
    max_files: Optional[int] = Query(None, description="Maximum number of files to process")
):
    """
    Rebuild the vector database index from conversation files
    This is a long-running operation that processes all conversation history
    """
    
    if not db:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        logger.info(f"🔄 Starting database rebuild (max_files: {max_files})...")
        
        # Perform rebuild
        rebuild_results = db.rebuild_index(max_files=max_files)
        
        if "error" in rebuild_results:
            raise HTTPException(status_code=500, detail=rebuild_results["error"])
        
        # Format response
        final_stats = rebuild_results.get("final_stats", {})
        
        return RebuildResponse(
            success=True,
            message=f"Database rebuilt successfully with {rebuild_results.get('total_processed', 0)} entries",
            total_processed=rebuild_results.get("total_processed", 0),
            rebuild_results=rebuild_results.get("rebuild_results", {}),
            final_stats=DatabaseStats(**final_stats) if final_stats else DatabaseStats(
                total_entries=0, projects={}, message_types={}, code_entries=0, code_percentage=0
            )
        )
        
    except Exception as e:
        logger.error(f"Rebuild error: {e}")
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {str(e)}")

# Project-aware search suggestions endpoint
@app.get("/projects")
async def get_available_projects():
    """Get list of available projects in the database"""
    
    if not db:
        raise HTTPException(status_code=500, detail="Vector database not initialized")
    
    try:
        stats = db.get_collection_stats()
        projects = stats.get("projects", {})
        
        project_list = []
        for project_name, project_data in projects.items():
            project_list.append({
                "name": project_name,
                "entries": project_data.get("count", 0),
                "user_messages": project_data.get("user", 0),
                "assistant_messages": project_data.get("assistant", 0),
                "code_entries": project_data.get("code", 0)
            })
        
        # Sort by entry count
        project_list.sort(key=lambda x: x["entries"], reverse=True)
        
        return {
            "projects": project_list,
            "total_projects": len(project_list)
        }
        
    except Exception as e:
        logger.error(f"Projects error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get projects: {str(e)}")

# File watcher status endpoint
@app.get("/watcher/status")
async def get_watcher_status():
    """Get real-time file watcher status and health metrics"""
    try:
        # Check if watcher components are available
        if not file_watcher:
            return {
                "enabled": False,
                "watching": False,
                "message": "File watcher not initialized",
                "status": "inactive"
            }
        
        # Get comprehensive status from watcher
        status = file_watcher.get_status()
        
        # Add processor and recovery status if available
        if incremental_processor:
            status["processor"] = incremental_processor.get_processing_status()
        
        if recovery_system:
            status["recovery"] = recovery_system.get_recovery_status()
        
        return {
            "enabled": True,
            "watching": status.get("status") == "active",
            "health": status.get("health", "unknown"),
            "details": status,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting watcher status: {e}")
        return {
            "enabled": False,
            "watching": False,
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }

# File watcher force sync endpoint
@app.post("/watcher/sync")
async def force_watcher_sync():
    """Force synchronization of all conversation files"""
    try:
        if not file_watcher:
            raise HTTPException(status_code=503, detail="File watcher not available")
        
        # Use file watcher's force scan method
        result = await file_watcher.force_scan()
        
        if result.get("success"):
            return {
                "success": True,
                "message": "File synchronization completed",
                "details": result,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Sync failed: {result.get('error', 'Unknown error')}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in force sync: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

# Root endpoint with usage information
@app.get("/")
async def root():
    """API root with usage information"""
    return {
        "name": "Claude Code Vector Database API",
        "version": "1.0.0",
        "description": "Semantic search API for Claude conversation history",
        "endpoints": {
            "search": {
                "POST /search": "Full search with request body",
                "GET /search": "Simple search with query parameters"
            },
            "management": {
                "GET /stats": "Database statistics",
                "POST /rebuild": "Rebuild database index",
                "GET /projects": "Available projects"
            },
            "monitoring": {
                "GET /health": "Health check",
                "GET /watcher/status": "File watcher status",
                "POST /watcher/sync": "Force file synchronization"
            }
        },
        "example_usage": {
            "simple_search": "/search?q=React hooks error&project=tylergohr.com&limit=5",
            "project_search": "/search?q=performance optimization&project=tylergohr.com",
            "general_search": "/search?q=git commit&limit=10"
        }
    }

def main():
    """Run the API server"""
    
    print("🚀 Starting Claude Code Vector Database API Server")
    print("=" * 60)
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("📊 Stats: http://localhost:8000/stats")
    print("🔧 Rebuild: POST http://localhost:8000/rebuild")
    print("=" * 60)
    
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload for production
        log_level="info"
    )

if __name__ == "__main__":
    main()