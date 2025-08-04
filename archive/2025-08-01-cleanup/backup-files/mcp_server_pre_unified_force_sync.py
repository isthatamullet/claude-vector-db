#!/usr/bin/env python3
"""
Claude Code Vector Database MCP Server
Seamless conversation context integration via Model Context Protocol
"""

from mcp.server.fastmcp import FastMCP
import asyncio
import logging
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import pytz

# Import existing vector database components
from vector_database import ClaudeVectorDatabase
from conversation_extractor import ConversationExtractor

# Import live validation learning functions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize MCP server
mcp = FastMCP(
    name="Claude Code Vector Database",
    description="Semantic search and context retrieval for Claude Code conversations"
)

# Enhanced context awareness imports

# Legacy file watcher components replaced by hooks-based indexing
# from file_watcher import initialize_file_watcher, shutdown_file_watcher, file_watcher
# from incremental_processor import initialize_incremental_processor, shutdown_incremental_processor, incremental_processor
# from watcher_recovery import initialize_recovery_system, shutdown_recovery_system, recovery_system

# Global instances
db: Optional[ClaudeVectorDatabase] = None
extractor: Optional[ConversationExtractor] = None
watcher_initialized: bool = False

def parse_user_timezone(prompt_context: str = "") -> str:
    """Parse user timezone from prompt context"""
    # Look for timezone info in prompt context
    if "America/Denver" in prompt_context:
        return "America/Denver"
    # Add more timezone detection logic as needed
    return "America/Denver"  # Default to user's known timezone

def convert_relative_time_to_unix(time_phrase: str, user_timezone: str = "America/Denver") -> tuple[Optional[float], Optional[float]]:
    """Convert relative time phrases to Unix timestamp ranges"""
    try:
        utc_now = datetime.now(pytz.UTC)
        user_tz = pytz.timezone(user_timezone)
        user_now = utc_now.astimezone(user_tz)
        
        if time_phrase == "last_hour":
            start_time = user_now - timedelta(hours=1)
            end_time = user_now
        elif time_phrase == "today":
            start_time = user_now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = user_now
        elif time_phrase == "last_3_days":
            start_time = user_now - timedelta(days=3)
            end_time = user_now
        elif time_phrase == "this_week":
            days_since_monday = user_now.weekday()
            start_time = user_now - timedelta(days=days_since_monday)
            start_time = start_time.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = user_now
        else:
            return None, None
        
        # Convert to UTC Unix timestamps
        start_unix = start_time.astimezone(pytz.UTC).timestamp()
        end_unix = end_time.astimezone(pytz.UTC).timestamp()
        
        return start_unix, end_unix
        
    except Exception as e:
        logger.warning(f"Failed to convert relative time '{time_phrase}': {e}")
        return None, None

def convert_date_range_to_unix(date_range: str, user_timezone: str = "America/Denver") -> tuple[Optional[float], Optional[float]]:
    """Convert date range to Unix timestamps in user's timezone"""
    try:
        start_date, end_date = date_range.split(",")
        user_tz = pytz.timezone(user_timezone)
        
        # Parse dates in user's timezone
        start_dt = user_tz.localize(datetime.strptime(start_date.strip(), "%Y-%m-%d"))
        end_dt = user_tz.localize(datetime.strptime(end_date.strip(), "%Y-%m-%d"))
        end_dt = end_dt.replace(hour=23, minute=59, second=59)  # End of day
        
        # Convert to UTC Unix timestamps
        start_unix = start_dt.astimezone(pytz.UTC).timestamp()
        end_unix = end_dt.astimezone(pytz.UTC).timestamp()
        
        return start_unix, end_unix
        
    except Exception as e:
        logger.warning(f"Failed to convert date range '{date_range}': {e}")
        return None, None

@mcp.resource("conversation://projects/{project_name}")
async def get_project_conversations(project_name: str) -> str:
    """Get all conversations for a specific project"""
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        # Get project-specific conversations
        results = db.search_conversations(
            query="*",  # Wildcard search
            current_project=project_name,
            n_results=100,
            filter_conditions={"project_name": {"$eq": project_name}}
        )
        
        # Format as structured conversation stream
        conversation_stream = []
        for result in results:
            conversation_stream.append({
                "id": result["id"],
                "content": result["content"],
                "type": result.get("type", "unknown"),
                "timestamp": result.get("timestamp", ""),
                "has_code": result.get("has_code", False),
                "tools_used": result.get("tools_used", [])
            })
        
        return json.dumps(conversation_stream, indent=2)
        
    except Exception as e:
        logger.error(f"Error retrieving project conversations: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
async def search_conversations(
    query: str,
    project_context: Optional[str] = None,
    limit: int = 5,
    include_code_only: bool = False,
    date_range: Optional[str] = None,  # "2025-07-26,2025-07-27" format
    recency: Optional[str] = None,  # "last_hour", "today", "last_3_days", "this_week"
    # Enhanced parameters for context awareness
    topic_focus: Optional[str] = None,  # "debugging", "performance", "authentication", etc.
    prefer_solutions: bool = False,  # Boost high-quality solution content
    troubleshooting_mode: bool = False,  # Enhanced relevance for error-solving contexts
    validation_preference: str = "neutral",  # "validated_only", "include_failures", "neutral"
    show_context_chain: bool = False,  # Include adjacency context in results
    use_enhanced_search: bool = True  # Use enhanced multi-factor relevance scoring
) -> List[Dict[str, Any]]:
    """
    Search conversation history with advanced context awareness and multi-factor relevance scoring
    
    Args:
        query: Search query for semantic matching
        project_context: Optional project name for relevance boosting
        limit: Maximum number of results to return
        include_code_only: Filter to only conversations containing code
        date_range: Date range filter as "start_date,end_date" (e.g., "2025-07-26,2025-07-27")
        recency: Recent time filter ("last_hour", "today", "last_3_days", "this_week")
        topic_focus: Specific topic to boost (e.g., "debugging", "performance", "authentication")
        prefer_solutions: Boost high-quality solution content with success markers
        troubleshooting_mode: Enhanced relevance for error-solving and debugging contexts
        validation_preference: "validated_only" for user-confirmed solutions, "include_failures" for learning patterns, "neutral" for balanced results
        show_context_chain: Include conversation context chain showing adjacent messages
        use_enhanced_search: Use multi-factor relevance scoring (topic, quality, validation boosting)
        
    Returns:
        List of relevant conversation excerpts with enhanced metadata and relevance analysis
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        # Detect current project if not provided
        if not project_context:
            current_dir = Path.cwd()
            project_context = detect_project_from_directory(current_dir)
        
        # Build filter conditions
        filter_conditions = {}
        if include_code_only:
            filter_conditions["has_code"] = {"$eq": True}
        
        # Parse user timezone from context (future enhancement)
        user_timezone = "America/Denver"  # Default to user's known timezone
        
        # Add timezone-aware date/recency filters using Unix timestamps
        if date_range:
            start_unix, end_unix = convert_date_range_to_unix(date_range, user_timezone)
            if start_unix and end_unix:
                filter_conditions["$and"] = [
                    {"timestamp_unix": {"$gte": start_unix}},
                    {"timestamp_unix": {"$lte": end_unix}}
                ]
                logger.info(f"Applied timezone-aware date range filter: {date_range} (Unix: {start_unix} to {end_unix})")
            else:
                logger.warning(f"Invalid date_range format: {date_range}. Expected 'YYYY-MM-DD,YYYY-MM-DD'")
        
        if recency:
            start_unix, end_unix = convert_relative_time_to_unix(recency, user_timezone)
            if start_unix and end_unix:
                filter_conditions["$and"] = [
                    {"timestamp_unix": {"$gte": start_unix}},
                    {"timestamp_unix": {"$lte": end_unix}}
                ]
                logger.info(f"Applied timezone-aware recency filter '{recency}': Unix range {start_unix} to {end_unix}")
            else:
                logger.warning(f"Unknown recency filter: {recency}")
        
        # Choose search method based on enhanced parameters
        prefer_recent = recency is not None
        
        if use_enhanced_search and (topic_focus or prefer_solutions or troubleshooting_mode or 
                                   validation_preference != "neutral" or show_context_chain):
            # Use enhanced search with multi-factor relevance scoring
            results = db.search_conversations_enhanced(
                query=query,
                current_project=project_context,
                n_results=limit,
                include_metadata=True,
                filter_conditions=filter_conditions if filter_conditions else None,
                topic_focus=topic_focus,
                prefer_solutions=prefer_solutions,
                troubleshooting_mode=troubleshooting_mode,
                validation_preference=validation_preference,
                prefer_recent=prefer_recent,
                show_context_chain=show_context_chain
            )
        else:
            # Use standard search for backward compatibility
            results = db.search_conversations(
                query=query,
                current_project=project_context,
                n_results=limit,
                include_metadata=True,
                filter_conditions=filter_conditions if filter_conditions else None
            )
        
        # Enhance results with contextual information
        enhanced_results = []
        for result in results:
            enhanced_result = {
                **result,
                "relevance_explanation": generate_relevance_explanation(
                    result, query, project_context
                ),
                "suggested_follow_up": suggest_follow_up_questions(result),
                "related_files": extract_mentioned_files(result["content"])
            }
            enhanced_results.append(enhanced_result)
        
        logger.info(f"Search completed: {len(enhanced_results)} results for '{query}'")
        return enhanced_results
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def get_project_context_summary(
    project_name: Optional[str] = None,
    days_back: int = 30
) -> Dict[str, Any]:
    """
    Generate comprehensive project context summary
    
    Args:
        project_name: Target project (auto-detected if not provided)
        days_back: Number of days of history to analyze
        
    Returns:
        Comprehensive project context including recent activities, patterns, and insights
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        # Auto-detect project if not provided
        if not project_name:
            current_dir = Path.cwd()
            project_name = detect_project_from_directory(current_dir)
        
        # Calculate date threshold (for future timestamp filtering)
        # cutoff_date = datetime.now() - timedelta(days=days_back)
        # cutoff_timestamp = cutoff_date.isoformat()
        
        # Get recent project conversations
        recent_conversations = db.search_conversations(
            query="*",
            current_project=project_name,
            n_results=200,
            filter_conditions={
                "project_name": {"$eq": project_name}
            }
        )
        
        # Analyze conversation patterns
        context_summary = {
            "project_name": project_name,
            "analysis_period": f"Last {days_back} days",
            "total_conversations": len(recent_conversations),
            "code_conversations": len([c for c in recent_conversations if c.get("has_code")]),
            "most_used_tools": analyze_tool_usage(recent_conversations),
            "recurring_topics": extract_recurring_topics(recent_conversations),
            "recent_decisions": identify_recent_decisions(recent_conversations),
            "technical_patterns": analyze_technical_patterns(recent_conversations),
            "knowledge_gaps": identify_knowledge_gaps(recent_conversations)
        }
        
        logger.info(f"Generated context summary for {project_name}")
        return context_summary
        
    except Exception as e:
        logger.error(f"Context summary error: {e}")
        return {"error": str(e), "project_name": project_name}

@mcp.tool()
async def detect_current_project() -> Dict[str, Any]:
    """
    Detect the current project based on working directory
    
    Returns:
        Project detection information including name, path, and confidence
    """
    try:
        current_dir = Path.cwd()
        project_name = detect_project_from_directory(current_dir)
        
        return {
            "current_directory": str(current_dir),
            "detected_project": project_name,
            "confidence": "high" if project_name else "none",
            "available_projects": list(get_project_mapping().keys())
        }
        
    except Exception as e:
        logger.error(f"Project detection error: {e}")
        return {"error": str(e), "current_directory": str(Path.cwd())}

def detect_project_from_directory(current_dir: Path) -> Optional[str]:
    """Intelligent project detection from current working directory"""
    
    project_mapping = get_project_mapping()
    current_path = str(current_dir)
    
    # Direct path matching
    for project_name, project_path in project_mapping.items():
        if current_path.startswith(project_path):
            return project_name
    
    # Fallback: extract project name from parent directories
    path_parts = current_path.split('/')
    for part in reversed(path_parts):
        if part in project_mapping:
            return part
    
    return None

def get_project_mapping() -> Dict[str, str]:
    """Get the project name to path mapping"""
    return {
        "tylergohr.com": "/home/user/tylergohr.com",
        "invoice-chaser": "/home/user/invoice-chaser", 
        "AI Orchestrator Platform": "/home/user/AI Orchestrator Platform",
        "grow": "/home/user/my-development-projects/grow",
        "idaho-adventures": "/home/user/my-development-projects/idaho-adventures",
        "snake-river-adventures": "/home/user/my-development-projects/snake-river-adventures",
        "toast-of-the-town": "/home/user/my-development-projects/toast-of-the-town"
    }

def generate_relevance_explanation(result: dict, query: str, project: str) -> str:
    """Generate human-readable relevance explanation"""
    explanations = []
    
    if result.get("project_boost", 1.0) > 1.0:
        explanations.append(f"Same project ({project}) - highly relevant")
    
    if result.get("has_code", False):
        explanations.append("Contains code examples")
    
    if result.get("tools_used"):
        tools = ", ".join(result["tools_used"][:3])
        explanations.append(f"Uses tools: {tools}")
    
    base_similarity = result.get("base_similarity", 0)
    if base_similarity > 0.8:
        explanations.append("Strong semantic match")
    elif base_similarity > 0.6:
        explanations.append("Good semantic match")
    
    return " | ".join(explanations) if explanations else "General relevance"

def suggest_follow_up_questions(result: dict) -> List[str]:
    """Suggest follow-up questions based on conversation content"""
    suggestions = []
    
    if result.get("has_code"):
        suggestions.append("Can you show me the specific code implementation?")
        suggestions.append("Are there any related test cases?")
    
    if "error" in result.get("content", "").lower():
        suggestions.append("How was this error resolved?")
        suggestions.append("What caused this issue originally?")
    
    if result.get("tools_used"):
        suggestions.append("What other approaches were considered?")
        suggestions.append("Are there alternative tools for this task?")
    
    return suggestions[:3]  # Limit to top 3 suggestions

def extract_mentioned_files(content: str) -> List[str]:
    """Extract file paths mentioned in conversation content"""
    
    # Pattern for common file path formats
    file_patterns = [
        r'/[\w\-_./]+\.\w+',  # Absolute paths with extensions
        r'[\w\-_./]+\.\w+',   # Relative paths with extensions
        r'src/[\w\-_./]+',    # src directory files
        r'components/[\w\-_./]+',  # component files
    ]
    
    mentioned_files = []
    for pattern in file_patterns:
        matches = re.findall(pattern, content)
        mentioned_files.extend(matches)
    
    # Remove duplicates and limit results
    return list(set(mentioned_files))[:10]

def analyze_tool_usage(conversations: List[Dict[str, Any]]) -> Dict[str, int]:
    """Analyze tool usage patterns from conversations"""
    tool_counts = {}
    
    for conv in conversations:
        tools = conv.get("tools_used", [])
        for tool in tools:
            tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    # Return top 10 most used tools
    return dict(sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)[:10])

def extract_recurring_topics(conversations: List[Dict[str, Any]]) -> List[str]:
    """Extract recurring topics from conversation content"""
    # Simple keyword extraction - can be enhanced with NLP
    topics = {}
    
    for conv in conversations:
        content = conv.get("content", "").lower()
        words = re.findall(r'\b\w{4,}\b', content)  # Words with 4+ characters
        
        for word in words:
            if word not in {'this', 'that', 'with', 'from', 'they', 'have', 'will', 'were', 'been'}:
                topics[word] = topics.get(word, 0) + 1
    
    # Return top 10 topics
    return [topic for topic, count in sorted(topics.items(), key=lambda x: x[1], reverse=True)[:10]]

def identify_recent_decisions(conversations: List[Dict[str, Any]]) -> List[str]:
    """Identify recent technical decisions from conversations"""
    decision_keywords = ['decided', 'chose', 'selected', 'implemented', 'using', 'switched to']
    decisions = []
    
    for conv in conversations:
        content = conv.get("content", "")
        for keyword in decision_keywords:
            if keyword in content.lower():
                # Extract sentence containing the decision
                sentences = content.split('. ')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        decisions.append(sentence.strip())
                        break
    
    return decisions[:5]  # Return top 5 recent decisions

def analyze_technical_patterns(conversations: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze technical patterns from conversations"""
    patterns = {
        "languages_used": [],
        "frameworks_mentioned": [],
        "common_errors": [],
        "solution_approaches": []
    }
    
    # This is a simplified implementation - can be enhanced with more sophisticated analysis
    for conv in conversations:
        content = conv.get("content", "").lower()
        
        # Language detection
        languages = ['python', 'javascript', 'typescript', 'react', 'node.js']
        for lang in languages:
            if lang in content:
                patterns["languages_used"].append(lang)
        
        # Framework detection
        frameworks = ['next.js', 'express', 'fastapi', 'react', 'vue', 'angular']
        for framework in frameworks:
            if framework in content:
                patterns["frameworks_mentioned"].append(framework)
    
    # Remove duplicates and count
    for key in patterns:
        if patterns[key]:
            counted = {}
            for item in patterns[key]:
                counted[item] = counted.get(item, 0) + 1
            patterns[key] = dict(sorted(counted.items(), key=lambda x: x[1], reverse=True)[:5])
    
    return patterns

def identify_knowledge_gaps(conversations: List[Dict[str, Any]]) -> List[str]:
    """Identify potential knowledge gaps from conversations"""
    gap_indicators = ['how do i', 'what is', 'how to', 'confused about', 'not sure', 'error:', 'failed']
    gaps = []
    
    for conv in conversations:
        content = conv.get("content", "").lower()
        for indicator in gap_indicators:
            if indicator in content:
                # Extract the question or error context
                sentences = content.split('. ')
                for sentence in sentences:
                    if indicator in sentence:
                        gaps.append(sentence.strip())
                        break
    
    return gaps[:5]  # Return top 5 identified gaps

async def ensure_file_watcher_initialized():
    """Ensure file watcher system is initialized."""
    global db, extractor, watcher_initialized
    
    if watcher_initialized:
        return True
    
    try:
        # Initialize database and extractor if needed
        if not db:
            db = ClaudeVectorDatabase()
        if not extractor:
            extractor = ConversationExtractor()
        
        # System now uses hooks-based indexing only (Phase 2 migration)
        logger.info("✅ Core components initialized - using hooks-based indexing")
        watcher_initialized = True
        return True
        
    except Exception as e:
        logger.error(f"Error initializing file watcher system: {e}")
        return False

# @mcp.tool()  # DISABLED - deprecated file watcher system
async def get_file_watcher_status() -> Dict[str, Any]:
    """
    Get real-time status of file watching system
    
    DEPRECATED: This tool is disabled as we've moved to hooks-based indexing.
    Use get_vector_db_health() instead for comprehensive health monitoring.
    
    Returns:
        Dict containing file watcher health, performance metrics, and configuration
    """
    try:
        # Ensure watcher is initialized
        if not await ensure_file_watcher_initialized():
            return {"error": "File watcher system not available", "status": "error"}
        
        # Import the global instances to access current state
        from file_watcher import file_watcher
        from incremental_processor import incremental_processor
        from watcher_recovery import recovery_system
        
        # Get status from all components
        watcher_status = file_watcher.get_status() if file_watcher else {"status": "inactive"}
        processor_status = incremental_processor.get_processing_status() if incremental_processor else {"is_processing": False}
        recovery_status = recovery_system.get_recovery_status() if recovery_system else {"is_running": False}
        
        # Combine status information
        combined_status = {
            "file_watcher": watcher_status,
            "incremental_processor": processor_status,
            "recovery_system": recovery_status,
            "overall_health": determine_overall_health(watcher_status, processor_status, recovery_status),
            "initialization_status": "initialized" if watcher_initialized else "not_initialized",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("File watcher status requested")
        return combined_status
        
    except Exception as e:
        logger.error(f"Error getting file watcher status: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool()
async def get_vector_db_health() -> Dict[str, Any]:
    """
    Simplified vector database health check with direct database access
    
    Returns:
        Dict containing essential health metrics for the enhanced database system
    """
    try:
        start_time = datetime.now()
        
        # Initialize database with direct access
        db = ClaudeVectorDatabase()
        
        health_report = {
            "timestamp": start_time.isoformat(),
            "overall_status": "healthy",
            "health_version": "2025-07-30-simplified",
            "indexing_method": "hooks-based",
            "components": {}
        }
        
        # Component 1: Database Connectivity & Basic Metrics
        try:
            connectivity_start = datetime.now()
            
            # Direct collection access for reliable metrics
            total_count = db.collection.count()
            connectivity_time = (datetime.now() - connectivity_start).total_seconds() * 1000
            
            health_report["components"]["database_connectivity"] = {
                "status": "healthy",
                "response_time_ms": connectivity_time,
                "total_conversations": total_count,
                "database_path": str(db.db_path),
                "collection_name": db.collection_name
            }
            
        except Exception as e:
            health_report["components"]["database_connectivity"] = {
                "status": "unhealthy",
                "error": str(e)[:200]
            }
            health_report["overall_status"] = "unhealthy"
        
        # Component 2: Search Functionality
        try:
            search_start = datetime.now()
            
            # Test search with recent conversation method (more reliable)
            recent_conversations = await get_most_recent_conversation(limit=3)
            search_time = (datetime.now() - search_start).total_seconds() * 1000
            
            search_working = recent_conversations.get('success', False)
            results_count = len(recent_conversations.get('conversations', []))
            
            health_report["components"]["search_functionality"] = {
                "status": "healthy" if search_working else "degraded",
                "response_time_ms": search_time,
                "test_results_returned": results_count,
                "search_working": search_working
            }
            
            if not search_working and health_report["overall_status"] == "healthy":
                health_report["overall_status"] = "degraded"
                
        except Exception as e:
            health_report["components"]["search_functionality"] = {
                "status": "unhealthy",
                "error": str(e)[:200]
            }
            health_report["overall_status"] = "unhealthy"
        
        # Component 3: Dual Hook Activity Status (Prompt + Response Indexing)
        try:
            # Get most recent prompt and response separately for precise hook testing
            recent_prompt = await get_most_recent_conversation(conversation_type="user", limit=1)
            recent_response = await get_most_recent_conversation(conversation_type="assistant", limit=1)
            
            def parse_timestamp(timestamp_str):
                """Parse timestamp and return datetime object and minutes ago"""
                if not timestamp_str:
                    return None, None
                try:
                    clean_timestamp = timestamp_str.replace('.Z', 'Z')
                    if clean_timestamp.endswith('Z'):
                        conv_time = datetime.fromisoformat(clean_timestamp.replace('Z', '+00:00'))
                    else:
                        conv_time = datetime.fromisoformat(clean_timestamp)
                    
                    current_time = datetime.now(conv_time.tzinfo) if conv_time.tzinfo else datetime.now()
                    minutes_ago = int((current_time - conv_time).total_seconds() / 60)
                    return conv_time, minutes_ago
                except Exception:
                    return None, None
            
            # Analyze prompt hook
            prompt_healthy = False
            prompt_time_desc = "never"
            prompt_timestamp = None
            
            if recent_prompt.get('success') and recent_prompt.get('conversation'):
                prompt_conv = recent_prompt['conversation']
                prompt_timestamp_str = prompt_conv.get('timestamp')
                prompt_time, prompt_minutes_ago = parse_timestamp(prompt_timestamp_str)
                
                if prompt_time and prompt_minutes_ago is not None:
                    prompt_timestamp = prompt_time
                    if prompt_minutes_ago < 60:
                        prompt_healthy = True
                        prompt_time_desc = f"{prompt_minutes_ago} minutes ago"
                    elif prompt_minutes_ago < 1440:
                        prompt_time_desc = f"{int(prompt_minutes_ago/60)} hours ago"
                    else:
                        prompt_time_desc = f"{int(prompt_minutes_ago/1440)} days ago"
            
            # Analyze response hook
            response_healthy = False
            response_time_desc = "never"
            response_timestamp = None
            
            if recent_response.get('success') and recent_response.get('conversation'):
                response_conv = recent_response['conversation']
                response_timestamp_str = response_conv.get('timestamp')
                response_time, response_minutes_ago = parse_timestamp(response_timestamp_str)
                
                if response_time and response_minutes_ago is not None:
                    response_timestamp = response_time
                    if response_minutes_ago < 60:
                        response_healthy = True
                        response_time_desc = f"{response_minutes_ago} minutes ago"
                    elif response_minutes_ago < 1440:
                        response_time_desc = f"{int(response_minutes_ago/60)} hours ago"
                    else:
                        response_time_desc = f"{int(response_minutes_ago/1440)} days ago"
            
            # Determine overall status
            if prompt_healthy and response_healthy:
                activity_status = "healthy" 
                hook_desc = "Both prompt and response hooks active within 60 minutes"
            elif prompt_healthy and not response_healthy:
                activity_status = "degraded"
                hook_desc = f"Only prompt hook active recently (response: {response_time_desc})"
            elif not prompt_healthy and response_healthy:
                activity_status = "degraded"
                hook_desc = f"Only response hook active recently (prompt: {prompt_time_desc})"
            elif prompt_timestamp or response_timestamp:
                activity_status = "stale"
                hook_desc = f"Both hooks stale (prompt: {prompt_time_desc}, response: {response_time_desc})"
            else:
                activity_status = "inactive"
                hook_desc = "No hook activity detected"
            
            # Find most recent overall activity
            latest_activity_time = None
            if prompt_timestamp and response_timestamp:
                latest_activity_time = max(prompt_timestamp, response_timestamp)
            elif prompt_timestamp:
                latest_activity_time = prompt_timestamp
            elif response_timestamp:
                latest_activity_time = response_timestamp
            
            health_report["components"]["dual_hook_activity"] = {
                "status": activity_status,
                "description": hook_desc,
                "prompt_hook": {
                    "healthy": prompt_healthy,
                    "last_activity": prompt_timestamp.isoformat() if prompt_timestamp else "never",
                    "time_ago": prompt_time_desc
                },
                "response_hook": {
                    "healthy": response_healthy,
                    "last_activity": response_timestamp.isoformat() if response_timestamp else "never", 
                    "time_ago": response_time_desc
                },
                "most_recent_activity": latest_activity_time.isoformat() if latest_activity_time else "never",
                "indexing_method": "hooks-based"
            }
            
            # Update overall status based on dual hook activity
            dual_hook_status = health_report["components"].get("dual_hook_activity", {}).get("status", "unknown")
            if dual_hook_status in ["stale", "inactive", "degraded"] and health_report["overall_status"] == "healthy":
                health_report["overall_status"] = "degraded"
                
        except Exception as e:
            health_report["components"]["dual_hook_activity"] = {
                "status": "unknown",
                "error": str(e)[:200],
                "indexing_method": "hooks-based"
            }
        
        # Component 4: Project Context
        try:
            current_dir = Path.cwd()
            detected_project = detect_project_from_directory(current_dir)
            
            health_report["components"]["project_context"] = {
                "status": "healthy",
                "working_directory": str(current_dir),
                "detected_project": detected_project,
                "context": "Enhanced vector database system" if "vector-db" in str(current_dir) else f"Project: {detected_project}"
            }
            
        except Exception as e:
            health_report["components"]["project_context"] = {
                "status": "degraded",
                "error": str(e)[:200]
            }
        
        # Generate Summary & Recommendations
        components = health_report["components"]
        healthy_count = sum(1 for comp in components.values() if comp.get("status") == "healthy")
        total_count = len(components)
        
        recommendations = []
        
        # Simple recommendation logic
        if components.get("database_connectivity", {}).get("status") != "healthy":
            recommendations.append("Database connectivity issues - check ChromaDB service")
        
        if components.get("search_functionality", {}).get("status") != "healthy":
            recommendations.append("Search functionality degraded - investigate database issues")
        
        activity = components.get("dual_hook_activity", {})
        if activity.get("status") == "degraded":
            recommendations.append(f"Partial hook activity: {activity.get('description', 'unknown')} - check hook configuration")
        elif activity.get("status") == "stale":
            recommendations.append(f"Hook activity is stale ({activity.get('time_since_last')}) - verify hook logs")
        elif activity.get("status") == "inactive":
            recommendations.append("No recent hook activity - verify hooks configuration")
        
        if not recommendations:
            recommendations.append("All systems operational")
        
        health_report["summary"] = {
            "healthy_components": healthy_count,
            "total_components": total_count,
            "health_check_duration_ms": (datetime.now() - start_time).total_seconds() * 1000,
            "recommendations": recommendations
        }
        
        return health_report
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "critical_error",
            "error": str(e)[:200],
            "components": {},
            "summary": {
                "healthy_components": 0,
                "total_components": 0,
                "recommendations": ["Health check system failure - manual investigation required"]
            }
        }

@mcp.tool()
async def get_most_recent_conversation(
    conversation_type: Optional[str] = None,  # "user" or "assistant" 
    project_context: Optional[str] = None,
    limit: int = 1
) -> Dict[str, Any]:
    """
    Get the most recent conversation entry that was indexed
    
    Args:
        conversation_type: Filter by "user" or "assistant", or None for any type
        project_context: Optional project name filter
        limit: Number of recent entries to return (default: 1)
        
    Returns:
        Most recent conversation entry/entries with metadata
    """
    global db
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info(f"Getting {limit} most recent conversations (type: {conversation_type}, project: {project_context})")
        
        # Build filter conditions
        filter_conditions = {}
        if conversation_type:
            filter_conditions["type"] = {"$eq": conversation_type}
        if project_context:
            filter_conditions["project_name"] = {"$eq": project_context}
        
        # Get ALL matching entries (ChromaDB limitation - can't sort natively)
        logger.info("Retrieving all matching entries for sorting...")
        all_results = db.collection.get(
            where=filter_conditions if filter_conditions else None,
            include=["documents", "metadatas"]
        )
        
        if not all_results['documents']:
            return {
                "success": False,
                "message": "No conversations found matching criteria",
                "filter_applied": filter_conditions
            }
        
        logger.info(f"Retrieved {len(all_results['documents'])} entries, sorting by timestamp_unix...")
        
        # Manual sort by timestamp_unix (newest first) - REQUIRED with ChromaDB
        combined = list(zip(
            all_results['documents'],
            all_results['metadatas'], 
            all_results['ids']
        ))
        
        # Sort by timestamp_unix descending (most recent first)
        sorted_results = sorted(
            combined,
            key=lambda x: x[1].get('timestamp_unix', 0),
            reverse=True
        )
        
        # Get the most recent N entries
        most_recent = sorted_results[:limit]
        
        # Format results
        formatted_results = []
        for doc, metadata, doc_id in most_recent:
            # Parse tools from JSON string
            tools_used = []
            if metadata.get('tools_used'):
                try:
                    tools_used = json.loads(metadata['tools_used'])
                except (json.JSONDecodeError, TypeError):
                    tools_used = []
            
            formatted_results.append({
                "id": doc_id,
                "content": doc,
                "timestamp": metadata.get('timestamp'),
                "timestamp_unix": metadata.get('timestamp_unix'),
                "type": metadata.get('type'),
                "project_name": metadata.get('project_name'),
                "project_path": metadata.get('project_path'),
                "has_code": metadata.get('has_code', False),
                "tools_used": tools_used,
                "content_length": metadata.get('content_length'),
                "session_id": metadata.get('session_id'),
                "file_name": metadata.get('file_name')
            })
        
        logger.info(f"Successfully found {len(formatted_results)} most recent conversations")
        
        if limit == 1:
            return {
                "success": True,
                "conversation": formatted_results[0] if formatted_results else None,
                "total_entries_searched": len(all_results['documents']),
                "filter_applied": filter_conditions
            }
        else:
            return {
                "success": True,
                "conversations": formatted_results,
                "count": len(formatted_results),
                "total_entries_searched": len(all_results['documents']),
                "filter_applied": filter_conditions
            }
            
    except Exception as e:
        logger.error(f"Error getting most recent conversation: {e}")
        return {
            "success": False,
            "error": str(e),
            "conversation_type": conversation_type,
            "project_context": project_context
        }

@mcp.tool()
async def force_conversation_sync(parallel_processing: bool = True) -> Dict[str, Any]:
    """
    Force sync of all conversation files for recovery
    
    Uses conversation extractor to rebuild vector database from all JSONL files.
    This replaces the deprecated file watcher system approach.
    
    Returns:
        Dict with sync results including files processed and errors
    """
    try:
        logger.info("Starting forced conversation sync using conversation extractor...")
        
        # Ensure components are initialized
        if not await ensure_file_watcher_initialized():
            return {"error": "Core components not available", "success": False, "timestamp": datetime.now().isoformat()}
        
        # Extract all conversations from JSONL files in smaller batches
        logger.info("Extracting conversations from all JSONL files...")
        
        # Process files in smaller batches to avoid timeout
        from pathlib import Path
        claude_projects_dir = Path("/home/user/.claude/projects")
        jsonl_files = list(claude_projects_dir.rglob("*.jsonl"))
        
        total_files = len(jsonl_files)
        logger.info(f"Found {total_files} conversation files to process")
        
        if parallel_processing and total_files > 20:
            # Return instructions for manual parallel processing
            mid_point = total_files // 2
            first_half = jsonl_files[:mid_point]
            # second_half = jsonl_files[mid_point:]  # For future parallel processing
            
            logger.info("Large dataset detected - recommending parallel processing approach")
            
            return {
                "success": True,
                "message": "Large dataset detected. Use timeout-free script for complete processing.",
                "total_files": total_files,
                "timeout_free_solution": {
                    "approach": "Direct script execution bypasses 2-minute MCP timeout",
                    "command": "cd /home/user/.claude-vector-db && ./venv/bin/python run_full_sync.py",
                    "estimated_time": "10-15 minutes for complete processing",
                    "benefits": [
                        "No timeout constraints",
                        "Complete progress tracking", 
                        "Handles all 92 conversation files",
                        "Comprehensive error handling"
                    ],
                    "alternative_parallel": {
                        "agent1_command": f"Process files 1-{len(first_half)} with Task agents",
                        "agent2_command": f"Process files {len(first_half)+1}-{total_files} with Task agents",
                        "estimated_time_parallel": "5-8 minutes"
                    }
                },
                "method": "timeout_free_script_recommended", 
                "timestamp": datetime.now().isoformat()
            }
            
        else:
            # Use sequential batched processing for smaller datasets
            logger.info("Using sequential batched processing")
            
            # Process in batches of 10 files to provide progress updates
            batch_size = 10
            total_entries_added = 0
            total_entries_skipped = 0
            total_entries_errors = 0
            
            for batch_start in range(0, total_files, batch_size):
                batch_end = min(batch_start + batch_size, total_files)
                batch_files = jsonl_files[batch_start:batch_end]
                
                logger.info(f"Processing batch {batch_start//batch_size + 1} of {(total_files + batch_size - 1)//batch_size}: files {batch_start+1}-{batch_end}")
                
                # Extract entries from this batch of files
                batch_entries = []
                for file_path in batch_files:
                    file_entries = list(extractor.extract_from_jsonl_file(file_path))
                    batch_entries.extend(file_entries)
                
                if batch_entries:
                    # Add batch to vector database
                    logger.info(f"Adding {len(batch_entries)} entries from batch to database...")
                    batch_result = db.add_conversation_entries(batch_entries)
                    
                    total_entries_added += batch_result.get("added", 0)
                    total_entries_skipped += batch_result.get("skipped", 0)  
                    total_entries_errors += batch_result.get("errors", 0)
                    
                    logger.info(f"Batch complete: {batch_result.get('added', 0)} added, {batch_result.get('skipped', 0)} skipped")
            
            # Combine results
            result = {
                "added": total_entries_added,
                "skipped": total_entries_skipped,
                "errors": total_entries_errors
            }
        
        success = result.get("added", 0) > 0 or result.get("skipped", 0) > 0
        
        combined_result = {
            "success": success,
            "files_processed": total_files,
            "entries_added": result.get("added", 0),
            "entries_skipped": result.get("skipped", 0),
            "entries_errors": result.get("errors", 0),
            "method": "conversation_extractor_batched",
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            logger.info(f"Forced conversation sync completed successfully: {result}")
        else:
            logger.warning(f"Forced conversation sync encountered issues: {result}")
        
        return combined_result
        
    except Exception as e:
        logger.error(f"Error in forced conversation sync: {e}")
        return {"error": str(e), "success": False, "timestamp": datetime.now().isoformat()}

def determine_overall_health(watcher_status: Dict, processor_status: Dict, recovery_status: Dict) -> str:
    """Determine overall system health from component statuses."""
    try:
        # Check critical components
        watcher_healthy = watcher_status.get("status") == "active" and watcher_status.get("health") != "unhealthy"
        processor_healthy = processor_status.get("is_processing", False)
        recovery_healthy = recovery_status.get("is_running", False)
        
        # Check for performance issues
        performance_ok = True
        if watcher_status.get("performance_acceptable") is False:
            performance_ok = False
        
        if watcher_healthy and processor_healthy and recovery_healthy and performance_ok:
            return "healthy"
        elif watcher_healthy and processor_healthy:
            return "degraded"  # Recovery issues or performance problems
        else:
            return "unhealthy"  # Core components not working
            
    except Exception as e:
        logger.error(f"Error determining overall health: {e}")
        return "unknown"

# Enhanced MCP Tools for Context Awareness

@mcp.tool()
async def search_validated_solutions(
    query: str,
    project_context: Optional[str] = None,
    limit: int = 5,
    min_validation_strength: float = 0.3
) -> List[Dict[str, Any]]:
    """
    Search for user-validated solutions only.
    
    Finds solutions that users confirmed worked based on their feedback,
    providing high-confidence recommendations for similar problems.
    
    Args:
        query: Search query for semantic matching
        project_context: Optional project name for relevance boosting
        limit: Maximum number of results to return
        min_validation_strength: Minimum validation strength threshold
        
    Returns:
        List of validated solution results with confidence metrics
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        # Detect current project if not provided
        if not project_context:
            current_dir = Path.cwd()
            project_context = detect_project_from_directory(current_dir)
        
        # Use enhanced search for validated solutions
        results = db.search_validated_solutions(
            query=query,
            current_project=project_context,
            n_results=limit,
            min_validation_strength=min_validation_strength
        )
        
        logger.info(f"✅ Validated solutions search: '{query}' → {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error searching validated solutions: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def search_failed_attempts(
    query: str,
    project_context: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for solutions that users reported as unsuccessful.
    
    Useful for learning "what not to do" patterns and avoiding
    approaches that have been confirmed to fail.
    
    Args:
        query: Search query for semantic matching
        project_context: Optional project name for relevance boosting
        limit: Maximum number of results to return
        
    Returns:
        List of refuted solution attempts with failure context
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        # Detect current project if not provided
        if not project_context:
            current_dir = Path.cwd()
            project_context = detect_project_from_directory(current_dir)
        
        # Use enhanced search for failed attempts
        results = db.search_failed_attempts(
            query=query,
            current_project=project_context,
            n_results=limit
        )
        
        logger.info(f"⚠️ Failed attempts search: '{query}' → {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error searching failed attempts: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def search_by_topic(
    query: str,
    topic: str,
    project_context: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Search conversations focused on a specific topic.
    
    Provides topic-focused search with enhanced relevance for specific
    domains like debugging, performance, authentication, etc.
    
    Args:
        query: Search query for semantic matching
        topic: Topic to focus on (e.g., "debugging", "performance", "authentication", "deployment", "testing", "styling", "database", "api", "state_management", "configuration")
        project_context: Optional project name for relevance boosting
        limit: Maximum number of results to return
        
    Returns:
        Topic-focused search results with enhanced relevance
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        # Detect current project if not provided
        if not project_context:
            current_dir = Path.cwd()
            project_context = detect_project_from_directory(current_dir)
        
        # Use topic-focused search
        results = db.search_by_topic(
            query=query,
            topic=topic,
            current_project=project_context,
            n_results=limit
        )
        
        logger.info(f"🏷️ Topic search: '{query}' → {topic} → {len(results)} results")
        return results
        
    except Exception as e:
        logger.error(f"Error in topic search: {e}")
        return [{"error": str(e)}]

@mcp.tool()
async def get_enhanced_statistics() -> Dict[str, Any]:
    """
    Get comprehensive statistics about the enhanced vector database.
    
    Provides detailed analytics including topic distribution, solution validation
    rates, quality metrics, and enhancement coverage statistics.
    
    Returns:
        Comprehensive enhancement statistics and analytics
    """
    global db, extractor
    
    if not db:
        db = ClaudeVectorDatabase()
    if not extractor:
        extractor = ConversationExtractor()
    
    try:
        # Get basic collection stats
        basic_stats = db.get_collection_stats()
        
        # Sample enhanced entries for analysis (if available)
        try:
            sample_results = db.search_conversations_enhanced(
                query="sample analysis",
                n_results=100,
                include_metadata=True
            )
            
            # Analyze enhancement coverage
            enhancement_stats = {
                'total_entries_sampled': len(sample_results),
                'enhanced_entries': 0,
                'topic_detection_coverage': 0,
                'solution_identification': 0,
                'validation_coverage': 0,
                'quality_distribution': {'low': 0, 'medium': 0, 'high': 0},
                'top_topics': [],
                'validation_rates': {
                    'validated_solutions': 0,
                    'refuted_attempts': 0,
                    'neutral_solutions': 0
                }
            }
            
            for result in sample_results:
                if result.get('detected_topics'):
                    enhancement_stats['enhanced_entries'] += 1
                    enhancement_stats['topic_detection_coverage'] += 1
                
                if result.get('solution_quality_score', 1.0) > 1.0:
                    enhancement_stats['solution_identification'] += 1
                
                if result.get('user_feedback_sentiment'):
                    enhancement_stats['validation_coverage'] += 1
                
                # Quality distribution
                quality_score = result.get('solution_quality_score', 1.0)
                if quality_score < 1.5:
                    enhancement_stats['quality_distribution']['low'] += 1
                elif quality_score < 2.0:
                    enhancement_stats['quality_distribution']['medium'] += 1
                else:
                    enhancement_stats['quality_distribution']['high'] += 1
                
                # Validation rates
                if result.get('is_validated_solution'):
                    enhancement_stats['validation_rates']['validated_solutions'] += 1
                elif result.get('is_refuted_attempt'):
                    enhancement_stats['validation_rates']['refuted_attempts'] += 1
                else:
                    enhancement_stats['validation_rates']['neutral_solutions'] += 1
            
            # Combine with basic stats
            basic_stats['enhancement_analysis'] = enhancement_stats
            
        except Exception as e:
            logger.warning(f"Could not get enhanced statistics: {e}")
            basic_stats['enhancement_analysis'] = {'error': 'Enhanced features not available'}
        
        logger.info("📊 Enhanced statistics retrieved")
        return basic_stats
        
    except Exception as e:
        logger.error(f"Error getting enhanced statistics: {e}")
        return {"error": str(e)}

# Live Validation Learning System MCP Tools

@mcp.tool()
async def process_validation_feedback(
    solution_id: str,
    solution_content: str,
    feedback_content: str,
    solution_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process user feedback for live validation learning.
    
    This is the main entry point for the live validation learning system.
    Call this when users provide feedback on Claude's solutions to improve
    future recommendations based on real validation patterns.
    
    Args:
        solution_id: Unique identifier for the solution
        solution_content: The solution content that was provided
        feedback_content: User's feedback on the solution
        solution_metadata: Additional metadata about the solution
        
    Returns:
        Dictionary with validation processing results and learning insights
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info(f"🧠 Processing validation feedback for solution: {solution_id}")
        
        # Process feedback through the live validation learning system
        result = db.process_validation_feedback(
            solution_id=solution_id,
            solution_content=solution_content,
            feedback_content=feedback_content,
            solution_metadata=solution_metadata or {}
        )
        
        # Add processing metadata
        result['processing_timestamp'] = datetime.now().isoformat()
        result['mcp_tool'] = 'process_validation_feedback'
        
        logger.info(f"✅ Validation feedback processed: {result.get('feedback_analysis', {}).get('sentiment', 'unknown')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing validation feedback: {e}")
        return {
            'error': str(e),
            'status': 'error',
            'solution_id': solution_id,
            'processing_timestamp': datetime.now().isoformat()
        }

@mcp.tool()
async def get_validation_learning_insights() -> Dict[str, Any]:
    """
    Get comprehensive insights about the live validation learning system.
    
    Provides analytics about learning patterns, validation rates, solution success,
    and confidence trends to understand how the system is learning from user feedback.
    
    Returns:
        Dictionary with validation learning insights and performance metrics
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info("📊 Generating validation learning insights...")
        
        # Get insights from the vector database
        insights = db.get_validation_learning_insights()
        
        # Add MCP-specific metadata
        insights['mcp_metadata'] = {
            'tool_name': 'get_validation_learning_insights',
            'generated_at': datetime.now().isoformat(),
            'system_status': 'active' if insights.get('status') != 'error' else 'error'
        }
        
        logger.info(f"✅ Generated validation learning insights: {insights.get('status', 'unknown')} status")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting validation learning insights: {e}")
        return {
            'error': str(e),
            'status': 'error',
            'mcp_metadata': {
                'tool_name': 'get_validation_learning_insights',
                'generated_at': datetime.now().isoformat(),
                'system_status': 'error'
            }
        }

@mcp.tool()
async def search_with_validation_boost(
    query: str,
    project_context: Optional[str] = None,
    limit: int = 5,
    validation_preference: str = "neutral",
    prefer_solutions: bool = True,
    topic_focus: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Search conversations with live validation learning boost applied.
    
    Uses learned validation patterns to boost/demote solutions based on
    historical user feedback, providing higher-quality recommendations.
    
    Args:
        query: Search query for semantic matching
        project_context: Optional project name for relevance boosting
        limit: Maximum number of results to return
        validation_preference: "validated_only", "include_failures", or "neutral"
        prefer_solutions: Whether to prefer solution content
        topic_focus: Specific topic to focus on
        
    Returns:
        Enhanced search results with validation learning applied
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info(f"🔍 Enhanced search with validation boost: '{query}'")
        
        # Use enhanced search with validation learning
        results = db.search_conversations_enhanced(
            query=query,
            current_project=project_context,
            n_results=limit,
            include_metadata=True,
            validation_preference=validation_preference,
            prefer_solutions=prefer_solutions,
            topic_focus=topic_focus,
            show_context_chain=False  # Can be added as parameter if needed
        )
        
        # Add validation learning metadata to results
        for result in results:
            if 'enhancement_analysis' in result:
                validation_boost = result['enhancement_analysis'].get('validation_boost', 1.0)
                result['validation_learning_applied'] = validation_boost != 1.0
                result['validation_boost_factor'] = validation_boost
        
        logger.info(f"✅ Enhanced search complete: {len(results)} results with validation learning")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in enhanced search with validation boost: {e}")
        return [{"error": str(e), "query": query}]

# Context Chain Functionality MCP Tools

@mcp.tool()
async def get_conversation_context_chain(
    message_id: str,
    chain_length: int = 5,
    show_relationships: bool = True
) -> Dict[str, Any]:
    """
    Get detailed conversation context chain around a specific message.
    
    Shows the conversation flow, solution-feedback relationships, validation status,
    and adjacency relationships for enhanced context understanding.
    
    Args:
        message_id: ID of the message to build context chain around
        chain_length: Number of messages in each direction from anchor
        show_relationships: Whether to include detailed relationship analysis
        
    Returns:
        Enhanced context chain with relationship metadata and flow analysis
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info(f"🔗 Building context chain for message: {message_id}")
        
        # Get the anchor message metadata first
        anchor_result = db.collection.get(
            ids=[message_id], 
            include=['metadatas', 'documents']
        )
        
        if not anchor_result['metadatas'] or not anchor_result['metadatas'][0]:
            return {
                'error': f'Message {message_id} not found',
                'message_id': message_id,
                'context_chain': []
            }
        
        anchor_metadata = anchor_result['metadatas'][0]
        
        # Build enhanced context chain
        context_chain = db.get_context_chain(
            anchor_message_id=message_id,
            metadata=anchor_metadata,
            chain_length=chain_length
        )
        
        # Add summary statistics
        chain_stats = {
            'total_messages': len(context_chain),
            'solution_attempts': sum(1 for msg in context_chain if msg.get('is_solution_attempt')),
            'feedback_messages': sum(1 for msg in context_chain if msg.get('is_feedback_to_solution')),
            'validated_solutions': sum(1 for msg in context_chain if msg.get('is_validated_solution')),
            'refuted_attempts': sum(1 for msg in context_chain if msg.get('is_refuted_attempt')),
            'topics_discussed': list(set(
                topic for msg in context_chain 
                for topic in msg.get('detected_topics', {}).keys()
            ))
        }
        
        result = {
            'message_id': message_id,
            'anchor_message': next((msg for msg in context_chain if msg['is_anchor']), None),
            'context_chain': context_chain,
            'chain_statistics': chain_stats,
            'chain_length_requested': chain_length,
            'relationships_included': show_relationships,
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Context chain built: {len(context_chain)} messages, "
                   f"{chain_stats['solution_attempts']} solutions, "
                   f"{chain_stats['feedback_messages']} feedback")
        
        return result
        
    except Exception as e:
        logger.error(f"Error building context chain: {e}")
        return {
            'error': str(e),
            'message_id': message_id,
            'context_chain': [],
            'generated_at': datetime.now().isoformat()
        }

@mcp.tool()
async def search_with_context_chains(
    query: str,
    project_context: Optional[str] = None,
    limit: int = 3,
    chain_length: int = 3,
    prefer_solutions: bool = True,
    validation_preference: str = "neutral"
) -> List[Dict[str, Any]]:
    """
    Search conversations with full context chains included in results.
    
    Each search result includes its conversation context chain showing
    the flow of messages, solution-feedback relationships, and validation outcomes.
    
    Args:
        query: Search query for semantic matching
        project_context: Optional project name for relevance boosting
        limit: Maximum number of results to return
        chain_length: Length of context chain for each result
        prefer_solutions: Whether to prefer solution content
        validation_preference: "validated_only", "include_failures", or "neutral"
        
    Returns:
        Search results with embedded context chains
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info(f"🔍 Context-aware search: '{query}' with {chain_length}-message chains")
        
        # Perform enhanced search with context chains enabled
        results = db.search_conversations_enhanced(
            query=query,
            current_project=project_context,
            n_results=limit,
            include_metadata=True,
            prefer_solutions=prefer_solutions,
            validation_preference=validation_preference,
            show_context_chain=True  # Enable context chains
        )
        
        # Enhance results with chain analysis
        for result in results:
            if 'context_chain' in result and result['context_chain']:
                chain = result['context_chain']
                
                # Add chain summary
                result['context_chain_summary'] = {
                    'chain_length': len(chain),
                    'has_solution_feedback_pairs': any(
                        msg.get('is_solution_attempt') and any(
                            other.get('related_solution_id') == msg['id'] 
                            for other in chain
                        ) for msg in chain
                    ),
                    'validation_outcomes': [
                        msg['validation_status'] for msg in chain 
                        if msg.get('validation_status') and '⚪' not in msg['validation_status']
                    ],
                    'conversation_flow': [
                        {
                            'position': msg['chain_position'],
                            'role': msg['context_role'],
                            'type': msg['type'],
                            'has_code': msg.get('has_code', False)
                        } for msg in chain
                    ]
                }
            else:
                result['context_chain_summary'] = {'chain_length': 0, 'no_context': True}
        
        logger.info(f"✅ Context-aware search complete: {len(results)} results with context chains")
        
        return results
        
    except Exception as e:
        logger.error(f"Error in context-aware search: {e}")
        return [{"error": str(e), "query": query}]

@mcp.tool() 
async def analyze_solution_feedback_patterns(
    project_context: Optional[str] = None,
    limit: int = 10,
    min_chain_length: int = 3
) -> Dict[str, Any]:
    """
    Analyze solution-feedback patterns using context chain relationships.
    
    Identifies successful solution patterns, common failure modes, and
    feedback-to-solution relationship patterns for learning insights.
    
    Args:
        project_context: Optional project to focus analysis on
        limit: Maximum number of solution-feedback pairs to analyze
        min_chain_length: Minimum context chain length required
        
    Returns:
        Analysis of solution-feedback patterns and relationship insights
    """
    global db
    
    if not db:
        db = ClaudeVectorDatabase()
    
    try:
        logger.info(f"📊 Analyzing solution-feedback patterns for project: {project_context}")
        
        # Search for solution attempts with context chains
        solution_results = db.search_conversations_enhanced(
            query="solution implementation code fix",
            current_project=project_context,
            n_results=limit * 2,  # Get more to filter
            prefer_solutions=True,
            show_context_chain=True,
            include_metadata=True
        )
        
        # Filter for results with meaningful context chains
        analyzed_patterns = []
        pattern_stats = {
            'total_solutions_analyzed': 0,
            'solutions_with_feedback': 0,
            'validated_solutions': 0,
            'refuted_solutions': 0,
            'partial_success': 0,
            'common_solution_types': {},
            'feedback_response_times': [],
            'success_by_topic': {}
        }
        
        for result in solution_results:
            context_chain = result.get('context_chain', [])
            if len(context_chain) < min_chain_length:
                continue
            
            # Find solution messages in chain
            solution_msgs = [msg for msg in context_chain if msg.get('is_solution_attempt')]
            feedback_msgs = [msg for msg in context_chain if msg.get('is_feedback_to_solution')]
            
            for solution_msg in solution_msgs:
                pattern_stats['total_solutions_analyzed'] += 1
                
                # Find corresponding feedback
                feedback_for_solution = [
                    fb for fb in feedback_msgs 
                    if fb.get('related_solution_id') == solution_msg['id']
                ]
                
                if feedback_for_solution:
                    pattern_stats['solutions_with_feedback'] += 1
                    feedback_msg = feedback_for_solution[0]
                    
                    # Analyze pattern
                    pattern = {
                        'solution_id': solution_msg['id'],
                        'solution_category': solution_msg.get('solution_category', 'unknown'),
                        'solution_topics': solution_msg.get('detected_topics', {}),
                        'feedback_sentiment': feedback_msg.get('user_feedback_sentiment'),
                        'validation_status': solution_msg.get('validation_status', '⚪ No validation data'),
                        'solution_quality_score': solution_msg.get('solution_quality_score', 1.0),
                        'context_chain_length': len(context_chain),
                        'has_code': solution_msg.get('has_code', False),
                        'tools_used': solution_msg.get('tools_used', [])
                    }
                    
                    analyzed_patterns.append(pattern)
                    
                    # Update statistics
                    if solution_msg.get('is_validated_solution'):
                        pattern_stats['validated_solutions'] += 1
                    elif solution_msg.get('is_refuted_attempt'):
                        pattern_stats['refuted_solutions'] += 1
                    elif solution_msg.get('validation_strength', 0) > 0:
                        pattern_stats['partial_success'] += 1
                    
                    # Track solution types
                    sol_type = solution_msg.get('solution_category', 'unknown')
                    pattern_stats['common_solution_types'][sol_type] = \
                        pattern_stats['common_solution_types'].get(sol_type, 0) + 1
                    
                    # Track success by topic
                    for topic in solution_msg.get('detected_topics', {}):
                        if topic not in pattern_stats['success_by_topic']:
                            pattern_stats['success_by_topic'][topic] = {'total': 0, 'validated': 0}
                        pattern_stats['success_by_topic'][topic]['total'] += 1
                        if solution_msg.get('is_validated_solution'):
                            pattern_stats['success_by_topic'][topic]['validated'] += 1
        
        # Calculate success rates
        if pattern_stats['total_solutions_analyzed'] > 0:
            pattern_stats['feedback_coverage_rate'] = \
                pattern_stats['solutions_with_feedback'] / pattern_stats['total_solutions_analyzed']
            pattern_stats['validation_success_rate'] = \
                pattern_stats['validated_solutions'] / pattern_stats['total_solutions_analyzed']
        
        # Sort patterns by quality score
        analyzed_patterns.sort(key=lambda x: x['solution_quality_score'], reverse=True)
        
        result = {
            'analysis_scope': {
                'project_context': project_context,
                'patterns_analyzed': len(analyzed_patterns),
                'min_chain_length': min_chain_length
            },
            'pattern_statistics': pattern_stats,
            'solution_feedback_patterns': analyzed_patterns[:limit],
            'insights': {
                'most_successful_solution_types': sorted(
                    pattern_stats['common_solution_types'].items(),
                    key=lambda x: x[1], reverse=True
                )[:5],
                'topic_success_rates': {
                    topic: stats['validated'] / stats['total'] if stats['total'] > 0 else 0
                    for topic, stats in pattern_stats['success_by_topic'].items()
                    if stats['total'] >= 2  # Only topics with enough data
                }
            },
            'generated_at': datetime.now().isoformat()
        }
        
        logger.info(f"✅ Pattern analysis complete: {len(analyzed_patterns)} patterns, "
                   f"{pattern_stats['solutions_with_feedback']} with feedback")
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing solution-feedback patterns: {e}")
        return {
            'error': str(e),
            'analysis_scope': {'project_context': project_context},
            'generated_at': datetime.now().isoformat()
        }

@mcp.tool()
async def get_realtime_learning_insights() -> Dict[str, Any]:
    """
    Get comprehensive insights about the real-time feedback loop learning system.
    
    Provides analytics about learning patterns, validation rates, solution success,
    and confidence trends to understand how the system is learning from user feedback.
    
    Returns:
        Dictionary with real-time learning insights and performance metrics
    """
    try:
        logger.info("🧠 Getting real-time learning insights...")
        
        # Get insights from the global real-time learner
        insights = get_realtime_learning_insights()
        
        # Add MCP tool metadata
        insights['mcp_tool'] = 'get_realtime_learning_insights'
        insights['generated_at'] = datetime.now().isoformat()
        
        logger.info(f"✅ Real-time learning insights retrieved: {insights['learning_stats']['conversations_processed']} conversations processed")
        
        return insights
        
    except Exception as e:
        logger.error(f"Error getting real-time learning insights: {e}")
        return {
            'error': str(e),
            'status': 'error',
            'generated_at': datetime.now().isoformat()
        }

async def shutdown_handler():
    """Graceful shutdown handler - hooks-based system has no cleanup needed."""
    try:
        logger.info("MCP server shutdown - hooks-based system requires no cleanup")
        # Hooks-based indexing system requires no explicit shutdown
        logger.info("Shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import signal
    import sys
    
    # Register shutdown handler
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        try:
            asyncio.create_task(shutdown_handler())
        except Exception as e:
            logger.error(f"Error in signal handler: {e}")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run MCP server
    try:
        mcp.run()
    except KeyboardInterrupt:
        logger.info("Server interrupted by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Ensure cleanup
        try:
            asyncio.run(shutdown_handler())
        except Exception as e:
            logger.error(f"Error in final cleanup: {e}")