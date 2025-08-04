#!/usr/bin/env python3
"""
MCP Tool Functionality Audit Script
Systematic testing of all 36 MCP tools following PRP-1 requirements
Created: August 02, 2025
"""

import asyncio
import time
import json
import sys
import os
from typing import Dict, List, Any, Literal
from dataclasses import dataclass, asdict
from pathlib import Path

# Add base path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.mcp_server import (
    search_conversations, search_conversations_unified, get_project_context_summary,
    detect_current_project, get_vector_db_health, get_most_recent_conversation,
    force_conversation_sync, smart_metadata_sync_status, smart_metadata_sync_run,
    search_validated_solutions, search_failed_attempts, search_by_topic,
    get_enhanced_statistics, get_enhancement_analytics_dashboard, run_enhancement_ab_test,
    get_ab_testing_insights, process_validation_feedback, get_validation_learning_insights,
    search_with_validation_boost, get_conversation_context_chain, search_with_context_chains,
    analyze_solution_feedback_patterns, get_realtime_learning_insights, run_unified_enhancement,
    get_system_health_report, configure_enhancement_systems, analyze_semantic_feedback,
    analyze_technical_context, run_multimodal_feedback_analysis, get_semantic_pattern_similarity,
    run_semantic_validation_ab_test, run_adaptive_learning_enhancement,
    process_adaptive_validation_feedback, get_adaptive_learning_insights,
    get_semantic_validation_health
)

@dataclass
class ToolAuditResult:
    """Audit result for individual MCP tool"""
    tool_name: str
    status: Literal["WORKING", "BROKEN", "DEGRADED", "DISABLED"]
    response_time_ms: float
    parameters_tested: List[str]
    error_conditions: List[str]
    output_quality: Literal["HIGH", "MEDIUM", "LOW"]
    redundancy_level: Literal["UNIQUE", "OVERLAPS", "REDUNDANT"]
    consolidation_candidate: bool
    notes: str

class ToolAuditor:
    """Comprehensive MCP tool auditor following PRP-1 specifications"""
    
    def __init__(self):
        self.results: List[ToolAuditResult] = []
        
    async def audit_tool(self, tool_name: str, tool_function, test_params: Dict[str, Any]) -> ToolAuditResult:
        """Audit individual MCP tool using existing patterns"""
        start_time = time.time()
        error_conditions = []
        parameters_tested = list(test_params.keys())
        
        try:
            # Test the tool with appropriate parameters
            result = await tool_function(**test_params)
            response_time = (time.time() - start_time) * 1000
            
            # Validate output quality
            output_quality = self._assess_output_quality(result)
            status = "WORKING" if result is not None else "DEGRADED"
            
            # Assess redundancy level based on tool name patterns
            redundancy_level = self._assess_redundancy(tool_name)
            
            # Determine consolidation candidacy
            consolidation_candidate = self._is_consolidation_candidate(tool_name, redundancy_level)
            
            return ToolAuditResult(
                tool_name=tool_name,
                status=status,
                response_time_ms=response_time,
                parameters_tested=parameters_tested,
                error_conditions=error_conditions,
                output_quality=output_quality,
                redundancy_level=redundancy_level,
                consolidation_candidate=consolidation_candidate,
                notes=f"Response time: {response_time:.2f}ms"
            )
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            error_conditions.append(str(e))
            
            return ToolAuditResult(
                tool_name=tool_name,
                status="BROKEN",
                response_time_ms=response_time,
                parameters_tested=parameters_tested,
                error_conditions=error_conditions,
                output_quality="LOW",
                redundancy_level="UNKNOWN",
                consolidation_candidate=False,
                notes=f"Error: {str(e)}"
            )
    
    def _assess_output_quality(self, result: Any) -> Literal["HIGH", "MEDIUM", "LOW"]:
        """Assess output quality based on content and structure"""
        if result is None:
            return "LOW"
        
        if isinstance(result, dict):
            if len(result) > 3 and "status" in result:
                return "HIGH"
            elif len(result) > 1:
                return "MEDIUM"
            else:
                return "LOW"
        elif isinstance(result, (list, str)) and len(result) > 0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _assess_redundancy(self, tool_name: str) -> Literal["UNIQUE", "OVERLAPS", "REDUNDANT"]:
        """Assess redundancy level based on tool name patterns"""
        # Search tools - high overlap potential
        if tool_name.startswith("search_"):
            return "REDUNDANT" if tool_name in ["search_conversations", "search_conversations_unified"] else "OVERLAPS"
        
        # Analytics tools - moderate overlap
        elif tool_name.startswith("get_") and any(x in tool_name for x in ["analytics", "statistics", "insights"]):
            return "OVERLAPS"
        
        # Enhancement tools - moderate overlap
        elif tool_name.startswith("run_") and "enhancement" in tool_name:
            return "OVERLAPS"
        
        # Validation tools - high overlap potential
        elif "validation" in tool_name:
            return "OVERLAPS"
        
        # Unique functionality tools
        else:
            return "UNIQUE"
    
    def _is_consolidation_candidate(self, tool_name: str, redundancy_level: str) -> bool:
        """Determine if tool is a good candidate for consolidation"""
        # High priority consolidation candidates
        if redundancy_level == "REDUNDANT":
            return True
        
        # Medium priority candidates
        if redundancy_level == "OVERLAPS" and any(x in tool_name for x in ["search_", "get_", "run_"]):
            return True
        
        # Tools that should remain separate
        if tool_name in ["detect_current_project", "get_vector_db_health"]:
            return False
        
        return redundancy_level != "UNIQUE"

    async def audit_all_tools(self) -> List[ToolAuditResult]:
        """Audit all 36 MCP tools systematically"""
        
        # Define all tools with their test parameters
        tools_to_test = [
            # Core Search & Retrieval Tools (8 tools)
            ("search_conversations", search_conversations, {"query": "test", "limit": 1}),
            ("search_conversations_unified", search_conversations_unified, {"query": "test", "limit": 1}),
            ("search_validated_solutions", search_validated_solutions, {"query": "test", "limit": 1}),
            ("search_failed_attempts", search_failed_attempts, {"query": "test", "limit": 1}),
            ("search_by_topic", search_by_topic, {"query": "test", "topic": "debugging", "limit": 1}),
            ("search_with_validation_boost", search_with_validation_boost, {"query": "test", "limit": 1}),
            ("search_with_context_chains", search_with_context_chains, {"query": "test", "limit": 1}),
            ("get_conversation_context_chain", get_conversation_context_chain, {"message_id": "test_id"}),
            
            # System Health & Analytics Tools (8 tools)
            ("get_vector_db_health", get_vector_db_health, {}),
            ("get_enhanced_statistics", get_enhanced_statistics, {}),
            ("get_enhancement_analytics_dashboard", get_enhancement_analytics_dashboard, {}),
            ("get_system_health_report", get_system_health_report, {}),
            ("get_ab_testing_insights", get_ab_testing_insights, {}),
            ("get_validation_learning_insights", get_validation_learning_insights, {}),
            ("get_realtime_learning_insights", get_realtime_learning_insights, {}),
            ("get_semantic_validation_health", get_semantic_validation_health, {}),
            
            # Enhancement & Processing Tools (7 tools)
            ("run_unified_enhancement", run_unified_enhancement, {}),
            ("run_enhancement_ab_test", run_enhancement_ab_test, {"test_name": "test"}),
            ("run_adaptive_learning_enhancement", run_adaptive_learning_enhancement, {}),
            ("run_multimodal_feedback_analysis", run_multimodal_feedback_analysis, {"feedback_content": "test feedback"}),
            ("run_semantic_validation_ab_test", run_semantic_validation_ab_test, {"test_queries": ["test"]}),
            ("configure_enhancement_systems", configure_enhancement_systems, {}),
            ("force_conversation_sync", force_conversation_sync, {}),
            
            # Validation & Learning Tools (6 tools)
            ("process_validation_feedback", process_validation_feedback, {
                "solution_id": "test", "solution_content": "test", "feedback_content": "test"}),
            ("process_adaptive_validation_feedback", process_adaptive_validation_feedback, {
                "feedback_text": "test", "solution_context": {}}),
            ("analyze_semantic_feedback", analyze_semantic_feedback, {"feedback_content": "test"}),
            ("analyze_technical_context", analyze_technical_context, {"feedback_content": "test"}),
            ("get_semantic_pattern_similarity", get_semantic_pattern_similarity, {"feedback_text": "test"}),
            ("get_adaptive_learning_insights", get_adaptive_learning_insights, {}),
            
            # Context & Project Management Tools (4 tools)
            ("get_project_context_summary", get_project_context_summary, {}),
            ("detect_current_project", detect_current_project, {}),
            ("get_most_recent_conversation", get_most_recent_conversation, {}),
            ("analyze_solution_feedback_patterns", analyze_solution_feedback_patterns, {}),
            
            # Data Sync & Management Tools (2 tools)
            ("smart_metadata_sync_status", smart_metadata_sync_status, {}),
            ("smart_metadata_sync_run", smart_metadata_sync_run, {}),
        ]
        
        print(f"🔍 Starting audit of {len(tools_to_test)} MCP tools...")
        
        for tool_name, tool_function, test_params in tools_to_test:
            print(f"   Testing {tool_name}...")
            result = await self.audit_tool(tool_name, tool_function, test_params)
            self.results.append(result)
            
        print(f"✅ Audit completed for {len(self.results)} tools")
        return self.results
    
    def generate_audit_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report"""
        working_tools = [r for r in self.results if r.status == "WORKING"]
        broken_tools = [r for r in self.results if r.status == "BROKEN"]
        degraded_tools = [r for r in self.results if r.status == "DEGRADED"]
        
        consolidation_candidates = [r for r in self.results if r.consolidation_candidate]
        redundant_tools = [r for r in self.results if r.redundancy_level == "REDUNDANT"]
        overlapping_tools = [r for r in self.results if r.redundancy_level == "OVERLAPS"]
        
        avg_response_time = sum(r.response_time_ms for r in working_tools) / len(working_tools) if working_tools else 0
        
        return {
            "audit_summary": {
                "total_tools": len(self.results),
                "working_tools": len(working_tools),
                "broken_tools": len(broken_tools),
                "degraded_tools": len(degraded_tools),
                "average_response_time_ms": round(avg_response_time, 2)
            },
            "consolidation_analysis": {
                "consolidation_candidates": len(consolidation_candidates),
                "redundant_tools": len(redundant_tools),
                "overlapping_tools": len(overlapping_tools),
                "consolidation_potential": f"{len(consolidation_candidates)}/{len(self.results)} tools ({round(len(consolidation_candidates)/len(self.results)*100, 1)}%)"
            },
            "detailed_results": [asdict(result) for result in self.results],
            "recommendations": self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate consolidation recommendations"""
        recommendations = []
        
        # Analyze search tools
        search_tools = [r for r in self.results if r.tool_name.startswith("search_")]
        if len(search_tools) > 3:
            recommendations.append(f"CONSOLIDATE: {len(search_tools)} search tools can be reduced to 2-3 unified tools")
        
        # Analyze analytics tools
        analytics_tools = [r for r in self.results if any(x in r.tool_name for x in ["analytics", "statistics", "insights"])]
        if len(analytics_tools) > 2:
            recommendations.append(f"CONSOLIDATE: {len(analytics_tools)} analytics tools can be unified into 1-2 tools")
        
        # Analyze enhancement tools
        enhancement_tools = [r for r in self.results if r.tool_name.startswith("run_")]
        if len(enhancement_tools) > 3:
            recommendations.append(f"CONSOLIDATE: {len(enhancement_tools)} enhancement tools can be streamlined")
        
        # Performance recommendations
        slow_tools = [r for r in self.results if r.response_time_ms > 1000]
        if slow_tools:
            recommendations.append(f"OPTIMIZE: {len(slow_tools)} tools have response times >1000ms")
        
        return recommendations

async def main():
    """Run comprehensive tool audit"""
    auditor = ToolAuditor()
    
    print("🏥 MCP Tool Functionality Audit - PRP-1 Discovery Phase")
    print("=" * 60)
    
    # Run the audit
    await auditor.audit_all_tools()
    
    # Generate report
    report = auditor.generate_audit_report()
    
    # Save report to file
    report_file = Path(__file__).parent / "tool_audit_results.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print summary
    print("\n📊 AUDIT SUMMARY:")
    print(f"   Total Tools: {report['audit_summary']['total_tools']}")
    print(f"   Working: {report['audit_summary']['working_tools']}")
    print(f"   Broken: {report['audit_summary']['broken_tools']}")
    print(f"   Average Response Time: {report['audit_summary']['average_response_time_ms']}ms")
    print(f"   Consolidation Candidates: {report['consolidation_analysis']['consolidation_candidates']}")
    
    print("\n💡 RECOMMENDATIONS:")
    for rec in report['recommendations']:
        print(f"   • {rec}")
    
    print(f"\n📁 Full report saved to: {report_file}")
    
if __name__ == "__main__":
    asyncio.run(main())