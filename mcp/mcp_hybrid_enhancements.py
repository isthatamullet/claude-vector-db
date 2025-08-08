#!/usr/bin/env python3
"""MCP tool enhancements for hybrid spaCy + ST integration"""

import json
from typing import List, Dict, Any, Optional

def enhance_search_with_hybrid_filtering(search_results: List[Dict], 
                                       tool_filter: Optional[str] = None,
                                       framework_filter: Optional[str] = None,
                                       min_confidence: Optional[float] = None,
                                       pattern_type: Optional[str] = None) -> List[Dict]:
    """
    Enhance search results with hybrid filtering capabilities.
    
    Args:
        search_results: Original search results from vector database
        tool_filter: Filter by specific tool (e.g., "Edit", "Bash")
        framework_filter: Filter by framework (e.g., "React", "TypeScript") 
        min_confidence: Minimum hybrid confidence threshold
        pattern_type: Filter by pattern type ("solution", "feedback", "error")
        
    Returns:
        Filtered and enhanced search results
    """
    if not search_results:
        return search_results
    
    enhanced_results = []
    
    for result in search_results:
        # Extract hybrid data - handle both nested metadata and direct hybrid_data
        hybrid_data = None
        if hasattr(result, 'hybrid_data'):
            hybrid_data = result.hybrid_data
        elif 'hybrid_data' in result:
            hybrid_data = result['hybrid_data']
        elif 'metadata' in result and 'hybrid_data' in result['metadata']:
            hybrid_data = result['metadata']['hybrid_data']
        
        # If no hybrid data and filters are applied, skip this result
        if not hybrid_data:
            # Only include results without hybrid data if no filters are applied
            if not any([tool_filter, framework_filter, min_confidence, pattern_type]):
                enhanced_results.append(result)
            continue
        
        # Apply filters
        include_result = True
        
        # Tool filtering
        if tool_filter and include_result:
            # Handle both attribute access and dictionary access
            tools_str = hybrid_data.get('technical_tools', '[]') if isinstance(hybrid_data, dict) else getattr(hybrid_data, 'technical_tools', '[]')
            if isinstance(tools_str, str):
                try:
                    tools = json.loads(tools_str)
                    if not any(tool_filter.lower() in tool.lower() for tool in tools):
                        include_result = False
                except json.JSONDecodeError:
                    pass
        
        # Framework filtering
        if framework_filter and include_result:
            frameworks_str = hybrid_data.get('framework_mentions', '[]') if isinstance(hybrid_data, dict) else getattr(hybrid_data, 'framework_mentions', '[]')
            if isinstance(frameworks_str, str):
                try:
                    frameworks = json.loads(frameworks_str)
                    if not any(framework_filter.lower() in fw.lower() for fw in frameworks):
                        include_result = False
                except json.JSONDecodeError:
                    pass
        
        # Confidence filtering
        if min_confidence and include_result:
            confidence = hybrid_data.get('hybrid_confidence', 0.0) if isinstance(hybrid_data, dict) else getattr(hybrid_data, 'hybrid_confidence', 0.0)
            if confidence < min_confidence:
                include_result = False
        
        # Pattern type filtering
        if pattern_type and include_result:
            if pattern_type == "solution":
                score = hybrid_data.get('solution_similarity_score', 0.0) if isinstance(hybrid_data, dict) else getattr(hybrid_data, 'solution_similarity_score', 0.0)
                if score < 0.3:  # Threshold for solution classification
                    include_result = False
            elif pattern_type == "feedback":
                score = hybrid_data.get('feedback_similarity_score', 0.0) if isinstance(hybrid_data, dict) else getattr(hybrid_data, 'feedback_similarity_score', 0.0)
                if score < 0.3:
                    include_result = False
            elif pattern_type == "error":
                score = hybrid_data.get('error_similarity_score', 0.0) if isinstance(hybrid_data, dict) else getattr(hybrid_data, 'error_similarity_score', 0.0)
                if score < 0.3:
                    include_result = False
        
        if include_result:
            # Add hybrid intelligence to result
            if isinstance(hybrid_data, dict):
                result['hybrid_intelligence'] = hybrid_data
            else:
                result['hybrid_intelligence'] = {
                    'technical_tools': getattr(hybrid_data, 'technical_tools', '[]'),
                    'framework_mentions': getattr(hybrid_data, 'framework_mentions', '[]'),
                    'solution_similarity_score': getattr(hybrid_data, 'solution_similarity_score', 0.0),
                    'hybrid_confidence': getattr(hybrid_data, 'hybrid_confidence', 0.0),
                    'best_pattern_match': getattr(hybrid_data, 'best_pattern_match', '')
                }
            
            enhanced_results.append(result)
    
    return enhanced_results

def get_hybrid_search_stats(search_results: List[Dict]) -> Dict[str, Any]:
    """Get statistics about hybrid-enhanced search results"""
    
    if not search_results:
        return {"hybrid_results": 0, "tools_detected": [], "frameworks_detected": []}
    
    tools_detected = set()
    frameworks_detected = set()
    hybrid_results = 0
    total_confidence = 0.0
    
    for result in search_results:
        hybrid_data = result.get('hybrid_intelligence', {})
        
        if hybrid_data:
            hybrid_results += 1
            
            # Extract tools
            tools_str = hybrid_data.get('technical_tools', '[]')
            try:
                tools = json.loads(tools_str) if isinstance(tools_str, str) else tools_str
                tools_detected.update(tools)
            except:
                pass
            
            # Extract frameworks
            frameworks_str = hybrid_data.get('framework_mentions', '[]')
            try:
                frameworks = json.loads(frameworks_str) if isinstance(frameworks_str, str) else frameworks_str
                frameworks_detected.update(frameworks)
            except:
                pass
            
            # Accumulate confidence
            confidence = hybrid_data.get('hybrid_confidence', 0.0)
            total_confidence += confidence
    
    avg_confidence = total_confidence / max(hybrid_results, 1)
    
    return {
        "hybrid_results": hybrid_results,
        "total_results": len(search_results),
        "hybrid_coverage": hybrid_results / len(search_results),
        "tools_detected": sorted(list(tools_detected)),
        "frameworks_detected": sorted(list(frameworks_detected)),
        "average_confidence": avg_confidence,
        "enhancement_active": hybrid_results > 0
    }

# Export functions
__all__ = ['enhance_search_with_hybrid_filtering', 'get_hybrid_search_stats']