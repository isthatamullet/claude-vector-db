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
        
        # Component 3: Recent Activity & Hook Status
        try:
            # Check for recent indexing activity
            recent_conversations = await get_most_recent_conversation(limit=1)
            
            if recent_conversations.get('success') and recent_conversations.get('conversations'):
                latest_entry = recent_conversations['conversations'][0]
                latest_timestamp = latest_entry.get('timestamp')
                
                if latest_timestamp:
                    # Parse timestamp and calculate time since last activity
                    from dateutil.parser import parse
                    latest_time = parse(latest_timestamp)
                    time_diff = datetime.now(latest_time.tzinfo) - latest_time
                    minutes_ago = int(time_diff.total_seconds() / 60)
                    
                    if minutes_ago < 60:
                        activity_status = "healthy"
                        time_desc = f"{minutes_ago} minutes ago"
                    elif minutes_ago < 1440:  # 24 hours
                        activity_status = "stale"
                        time_desc = f"{int(minutes_ago/60)} hours ago"
                    else:
                        activity_status = "inactive"
                        time_desc = f"{int(minutes_ago/1440)} days ago"
                else:
                    activity_status = "unknown"
                    time_desc = "unknown"
            else:
                activity_status = "inactive"
                time_desc = "no recent activity"
            
            health_report["components"]["recent_activity"] = {
                "status": activity_status,
                "last_indexed": latest_timestamp if 'latest_timestamp' in locals() else "unknown",
                "time_since_last": time_desc,
                "indexing_method": "hooks-based"
            }
            
            if activity_status in ["stale", "inactive"] and health_report["overall_status"] == "healthy":
                health_report["overall_status"] = "degraded"
                
        except Exception as e:
            health_report["components"]["recent_activity"] = {
                "status": "unknown",
                "error": str(e)[:200]
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
        
        activity = components.get("recent_activity", {})
        if activity.get("status") == "stale":
            recommendations.append(f"Indexing activity is stale ({activity.get('time_since_last')}) - check hooks")
        elif activity.get("status") == "inactive":
            recommendations.append("No recent indexing activity - verify hooks configuration")
        
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