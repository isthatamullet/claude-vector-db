"""
Solution Quality Assessment Engine

Identifies and scores working solutions, successful implementations, and validated fixes.
Prioritizes conversations containing high-quality, validated solutions through success marker detection.

Key Features:
- Multi-tier success marker detection
- Quality indicator analysis
- Code implementation scoring
- Tool usage patterns analysis
- Capped scoring to prevent over-weighting (max 3.0x boost)
"""

import re
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

# High-confidence success markers indicating working solutions
SUCCESS_MARKERS = [
    # Explicit success indicators
    "✅", "fixed", "working", "solved", "success", "complete", "done",
    "perfect", "exactly", "brilliant", "awesome", "fantastic",
    
    # Resolution confirmations
    "that worked", "problem resolved", "issue fixed", "bug fixed",
    "now working", "all good", "working perfectly", "works great",
    
    # Implementation success
    "deployed successfully", "tests passing", "build succeeded",
    "running smoothly", "production ready", "live and working"
]

# Quality assurance and validation indicators
QUALITY_INDICATORS = [
    # Testing and validation
    "tested", "validated", "confirmed", "verified", "checked",
    "production-ready", "deployed", "live", "stable",
    
    # Build and CI success
    "typecheck passed", "build succeeded", "tests passing", 
    "lint clean", "no errors", "validation passed",
    
    # Performance and reliability
    "optimized", "performance improved", "faster", "efficient",
    "scalable", "robust", "reliable", "secure"
]

# Implementation success patterns (more specific)
IMPLEMENTATION_SUCCESS = [
    # Solution patterns
    "final solution", "this worked", "problem solved", 
    "issue resolved", "successfully implemented",
    
    # Outcome descriptions
    "deployment successful", "migration complete", 
    "optimization complete", "refactoring done",
    
    # Functional confirmations
    "functionality working", "feature complete", 
    "integration successful", "configuration correct"
]

# Code success indicators
CODE_SUCCESS_PATTERNS = [
    # Code quality
    "code works", "implementation successful", "function working",
    "method working", "class implemented", "component working",
    
    # Runtime success
    "no errors", "running smoothly", "behaving correctly",
    "executing properly", "output correct", "result as expected"
]

# Failure indicators (for inverse scoring)
FAILURE_INDICATORS = [
    "broken", "not working", "still failing", "error persists",
    "same issue", "didn't work", "still broken", "made worse",
    "regression", "critical bug", "system down"
]

# Pre-compiled patterns for performance
_COMPILED_SUCCESS_PATTERNS: Dict[str, List[re.Pattern]] = {}

def _get_compiled_success_patterns():
    """Get pre-compiled regex patterns for success detection"""
    global _COMPILED_SUCCESS_PATTERNS
    
    if not _COMPILED_SUCCESS_PATTERNS:
        pattern_groups = {
            'success_markers': SUCCESS_MARKERS,
            'quality_indicators': QUALITY_INDICATORS, 
            'implementation_success': IMPLEMENTATION_SUCCESS,
            'code_success': CODE_SUCCESS_PATTERNS,
            'failure_indicators': FAILURE_INDICATORS
        }
        
        for group_name, patterns in pattern_groups.items():
            _COMPILED_SUCCESS_PATTERNS[group_name] = [
                re.compile(r'\b' + re.escape(pattern) + r'\b', re.IGNORECASE)
                for pattern in patterns
            ]
    
    return _COMPILED_SUCCESS_PATTERNS


def detect_success_markers(content: str) -> Dict[str, int]:
    """
    Detect success markers in conversation content.
    
    Args:
        content: Text content to analyze
        
    Returns:
        Dictionary with counts of different success marker types
    """
    patterns = _get_compiled_success_patterns()
    content_lower = content.lower()
    
    marker_counts = {}
    for group_name, compiled_patterns in patterns.items():
        count = 0
        for pattern in compiled_patterns:
            count += len(pattern.findall(content_lower))
        marker_counts[group_name] = count
    
    return marker_counts


def detect_quality_indicators(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Detect quality indicators including code presence and tool usage.
    
    Args:
        content: Text content to analyze
        metadata: Message metadata with tool usage info
        
    Returns:
        Dictionary with quality assessment details
    """
    marker_counts = detect_success_markers(content)
    
    # Analyze tool usage patterns
    tools_used = metadata.get('tools_used', [])
    implementation_tools = {'Edit', 'Write', 'MultiEdit', 'Bash'}
    analysis_tools = {'Read', 'Grep', 'Glob', 'LS'}
    
    has_implementation = bool(set(tools_used) & implementation_tools)
    has_analysis = bool(set(tools_used) & analysis_tools)
    
    # Code pattern detection
    code_patterns = [
        r'```[\w]*\n.*?\n```',  # Code blocks
        r'`[^`]+`',  # Inline code
        r'function\s+\w+',  # Function definitions
        r'class\s+\w+',  # Class definitions
        r'import\s+\w+',  # Import statements
        r'export\s+',  # Export statements
    ]
    
    has_code_patterns = any(
        re.search(pattern, content, re.DOTALL | re.IGNORECASE) 
        for pattern in code_patterns
    )
    
    return {
        'marker_counts': marker_counts,
        'has_implementation_tools': has_implementation,
        'has_analysis_tools': has_analysis,
        'has_code_patterns': has_code_patterns,
        'tool_diversity': len(set(tools_used)),
        'total_tools': len(tools_used)
    }


def calculate_solution_quality_score(content: str, metadata: Dict) -> float:
    """
    Calculate comprehensive solution quality score.
    
    Combines multiple quality indicators with weighted scoring:
    - Success markers: 0.3 per occurrence
    - Quality indicators: 0.4 per occurrence  
    - Implementation success: 0.5 per occurrence
    - Code presence: 0.2 base boost
    - Tool usage: 0.3 implementation boost
    - Failure penalties: -0.4 per occurrence
    
    Args:
        content: Message content to analyze
        metadata: Message metadata including tools_used, has_code
        
    Returns:
        Quality score (0.1 to 3.0 range, capped to prevent over-weighting)
    """
    if not content or len(content.strip()) < 10:
        return 1.0  # Neutral score for minimal content
    
    quality_analysis = detect_quality_indicators(content, metadata)
    marker_counts = quality_analysis['marker_counts']
    
    # Start with neutral base score
    quality_score = 1.0
    
    # Success marker boost (0.3 per occurrence)
    quality_score += marker_counts.get('success_markers', 0) * 0.3
    
    # Quality indicator boost (0.4 per occurrence)
    quality_score += marker_counts.get('quality_indicators', 0) * 0.4
    
    # Implementation success boost (0.5 per occurrence)
    quality_score += marker_counts.get('implementation_success', 0) * 0.5
    
    # Code success boost (0.3 per occurrence)
    quality_score += marker_counts.get('code_success', 0) * 0.3
    
    # Code presence boost
    if metadata.get('has_code', False) or quality_analysis['has_code_patterns']:
        quality_score += 0.2
    
    # Tool usage boost for implementation tools
    if quality_analysis['has_implementation_tools']:
        quality_score += 0.3
    
    # Tool diversity bonus (more tools = more comprehensive solution)
    tool_diversity = quality_analysis['tool_diversity']
    if tool_diversity >= 3:
        quality_score += 0.2
    
    # Content length quality indicator (longer solutions often more complete)
    content_length = len(content)
    if content_length > 500:  # Substantial content
        quality_score += 0.1
    if content_length > 1500:  # Very detailed solution
        quality_score += 0.1
    
    # Failure indicator penalty
    failure_count = marker_counts.get('failure_indicators', 0)
    quality_score -= failure_count * 0.4
    
    # Ensure score stays within valid range
    quality_score = max(0.1, min(quality_score, 3.0))
    
    return quality_score


def classify_solution_type(content: str, metadata: Dict) -> str:
    """
    Classify the type of solution provided.
    
    Args:
        content: Solution content
        metadata: Message metadata
        
    Returns:
        Solution category: "code_fix", "config_change", "approach_suggestion", "debugging_help", "other"
    """
    content_lower = content.lower()
    tools_used = set(metadata.get('tools_used', []))
    
    # Code implementation solutions
    if (tools_used & {'Edit', 'Write', 'MultiEdit'} or 
        any(pattern in content_lower for pattern in ['function', 'class', 'import', 'export', '```'])):
        return "code_fix"
    
    # Configuration changes
    if (any(pattern in content_lower for pattern in ['config', 'env', 'settings', 'package.json', '.env']) or
        'config' in content_lower):
        return "config_change"
    
    # Debugging assistance
    if (any(pattern in content_lower for pattern in ['debug', 'console.log', 'print', 'error', 'trace']) or
        tools_used & {'Bash', 'Grep'}):
        return "debugging_help"
    
    # Strategic or architectural suggestions
    if any(pattern in content_lower for pattern in ['approach', 'strategy', 'pattern', 'architecture', 'design']):
        return "approach_suggestion"
    
    return "other"


def calculate_success_confidence(content: str, metadata: Dict) -> float:
    """
    Calculate confidence level in solution success based on indicators.
    
    Args:
        content: Solution content
        metadata: Message metadata
        
    Returns:
        Confidence score (0.0 to 1.0)
    """
    quality_analysis = detect_quality_indicators(content, metadata)
    marker_counts = quality_analysis['marker_counts']
    
    # Calculate confidence based on strength of success indicators
    confidence = 0.0
    
    # Strong success markers contribute most
    strong_markers = marker_counts.get('success_markers', 0)
    confidence += min(strong_markers * 0.3, 0.6)  # Cap at 60%
    
    # Quality indicators add confidence
    quality_markers = marker_counts.get('quality_indicators', 0)
    confidence += min(quality_markers * 0.2, 0.3)  # Cap at 30%
    
    # Implementation tools suggest concrete solutions
    if quality_analysis['has_implementation_tools']:
        confidence += 0.2
    
    # Code presence suggests specific fixes
    if quality_analysis['has_code_patterns']:
        confidence += 0.15
    
    # Reduce confidence for failure indicators
    failure_count = marker_counts.get('failure_indicators', 0)
    confidence -= failure_count * 0.2
    
    return max(0.0, min(confidence, 1.0))


def get_quality_summary(content: str, metadata: Dict) -> Dict[str, Any]:
    """
    Get comprehensive quality assessment summary.
    
    Args:
        content: Content to analyze
        metadata: Message metadata
        
    Returns:
        Detailed quality assessment dictionary
    """
    quality_score = calculate_solution_quality_score(content, metadata)
    solution_type = classify_solution_type(content, metadata)
    success_confidence = calculate_success_confidence(content, metadata)
    quality_details = detect_quality_indicators(content, metadata)
    
    return {
        'quality_score': quality_score,
        'solution_type': solution_type,
        'success_confidence': success_confidence,
        'has_success_markers': quality_details['marker_counts']['success_markers'] > 0,
        'has_quality_indicators': quality_details['marker_counts']['quality_indicators'] > 0,
        'marker_breakdown': quality_details['marker_counts'],
        'tool_analysis': {
            'has_implementation_tools': quality_details['has_implementation_tools'],
            'has_analysis_tools': quality_details['has_analysis_tools'],
            'tool_diversity': quality_details['tool_diversity']
        },
        'code_analysis': {
            'has_code_patterns': quality_details['has_code_patterns'],
            'has_code_metadata': metadata.get('has_code', False)
        }
    }


def benchmark_quality_scoring(test_cases: List[Tuple[str, Dict]], iterations: int = 50) -> Dict[str, float]:
    """
    Benchmark quality scoring performance.
    
    Args:
        test_cases: List of (content, metadata) tuples for testing
        iterations: Number of iterations per test case
        
    Returns:
        Performance metrics
    """
    import time
    
    total_times = []
    
    for content, metadata in test_cases:
        case_times = []
        for _ in range(iterations):
            start_time = time.perf_counter()
            calculate_solution_quality_score(content, metadata)
            end_time = time.perf_counter()
            case_times.append((end_time - start_time) * 1000)
        
        total_times.extend(case_times)
    
    return {
        'avg_time_ms': sum(total_times) / len(total_times),
        'min_time_ms': min(total_times),
        'max_time_ms': max(total_times),
        'total_cases': len(test_cases),
        'target_met': sum(total_times) / len(total_times) < 10.0  # <10ms target
    }