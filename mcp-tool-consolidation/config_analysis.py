#!/usr/bin/env python3
"""
MCP Tool Configuration Analysis
Analyze tool registration patterns, parameter structures, and configuration dependencies
PRP-1 Discovery Phase - Configuration Analysis
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ToolDefinition:
    """Structure representing an MCP tool definition"""
    name: str
    line_number: int
    parameters: List[Dict[str, Any]]
    return_type: str
    has_security_validation: bool
    uses_global_instances: List[str]
    complexity_score: int
    parameter_count: int
    optional_parameter_count: int

@dataclass
class ConfigurationPattern:
    """Configuration patterns identified across tools"""
    pattern_name: str
    frequency: int
    examples: List[str]
    consolidation_impact: str

def analyze_mcp_server_configuration():
    """Analyze mcp_server.py configuration patterns"""
    
    server_file = Path("/home/user/.claude-vector-db-enhanced/mcp/mcp_server.py")
    
    with open(server_file, 'r') as f:
        content = f.read()
    
    # Find all tool definitions
    tool_definitions = extract_tool_definitions(content)
    
    # Analyze configuration patterns
    config_patterns = analyze_configuration_patterns(content, tool_definitions)
    
    # Analyze parameter structures
    parameter_analysis = analyze_parameter_structures(tool_definitions)
    
    # Analyze dependencies
    dependency_analysis = analyze_configuration_dependencies(content)
    
    return {
        "tool_definitions": tool_definitions,
        "configuration_patterns": config_patterns,
        "parameter_analysis": parameter_analysis,
        "dependency_analysis": dependency_analysis
    }

def extract_tool_definitions(content: str) -> List[ToolDefinition]:
    """Extract all MCP tool definitions from server code"""
    
    tools = []
    lines = content.split('\n')
    
    # Find all @mcp.tool() decorators
    tool_pattern = re.compile(r'@mcp\.tool\(\)')
    function_pattern = re.compile(r'async def (\w+)\((.*?)\) -> (.+?):')
    
    for i, line in enumerate(lines):
        if tool_pattern.match(line.strip()):
            # Find the function definition on the next line(s)
            for j in range(i+1, min(i+5, len(lines))):
                func_match = function_pattern.match(lines[j].strip())
                if func_match:
                    tool_name = func_match.group(1)
                    params_str = func_match.group(2)
                    return_type = func_match.group(3)
                    
                    # Parse parameters
                    parameters = parse_function_parameters(params_str)
                    
                    # Analyze tool body for patterns
                    tool_body = extract_tool_body(lines, j)
                    
                    tool_def = ToolDefinition(
                        name=tool_name,
                        line_number=i+1,
                        parameters=parameters,
                        return_type=return_type,
                        has_security_validation=check_security_validation(tool_body),
                        uses_global_instances=find_global_instances(tool_body),
                        complexity_score=calculate_complexity_score(tool_body),
                        parameter_count=len(parameters),
                        optional_parameter_count=count_optional_parameters(parameters)
                    )
                    
                    tools.append(tool_def)
                    break
    
    return tools

def parse_function_parameters(params_str: str) -> List[Dict[str, Any]]:
    """Parse function parameters from parameter string"""
    
    if not params_str.strip():
        return []
    
    parameters = []
    
    # Simple parameter parsing (handles most cases)
    param_parts = []
    paren_depth = 0
    current_part = ""
    
    for char in params_str:
        if char == ',' and paren_depth == 0:
            param_parts.append(current_part.strip())
            current_part = ""
        else:
            if char in '([{':
                paren_depth += 1
            elif char in ')]}':
                paren_depth -= 1
            current_part += char
    
    if current_part.strip():
        param_parts.append(current_part.strip())
    
    for param in param_parts:
        param = param.strip()
        if not param:
            continue
            
        # Parse parameter components
        param_info = {"raw": param}
        
        # Extract parameter name
        if ':' in param:
            name_part = param.split(':')[0].strip()
            type_part = param.split(':', 1)[1].strip()
            
            # Handle default values
            if '=' in type_part:
                type_part, default_part = type_part.split('=', 1)
                param_info["default_value"] = default_part.strip()
                param_info["optional"] = True
            else:
                param_info["optional"] = False
            
            param_info["name"] = name_part
            param_info["type"] = type_part.strip()
        else:
            param_info["name"] = param
            param_info["type"] = "unknown"
            param_info["optional"] = False
        
        parameters.append(param_info)
    
    return parameters

def extract_tool_body(lines: List[str], start_line: int) -> str:
    """Extract tool function body"""
    
    body_lines = []
    indent_level = None
    
    for i in range(start_line + 1, len(lines)):
        line = lines[i]
        
        # Skip empty lines and comments at the start
        if not line.strip() or line.strip().startswith('"""') or line.strip().startswith('#'):
            continue
        
        # Determine initial indent level
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
        
        # Stop when we reach a line with less indentation (next function/class)
        if line.strip() and len(line) - len(line.lstrip()) <= indent_level and not line.startswith(' ' * indent_level):
            break
        
        body_lines.append(line)
        
        # Stop after reasonable function length to avoid reading too much
        if len(body_lines) > 100:
            break
    
    return '\n'.join(body_lines)

def check_security_validation(tool_body: str) -> bool:
    """Check if tool implements security validation"""
    return "validate_mcp_request" in tool_body or "security_validation" in tool_body

def find_global_instances(tool_body: str) -> List[str]:
    """Find global instances used by the tool"""
    global_instances = []
    
    patterns = [
        r'global (\w+)',
        r'if not (\w+):',
        r'(\w+) = .*Database\(\)',
        r'(\w+) = .*Extractor\(\)',
        r'(\w+) = .*Analyzer\(\)',
        r'(\w+) = .*Manager\(\)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, tool_body)
        global_instances.extend(matches)
    
    return list(set(global_instances))

def calculate_complexity_score(tool_body: str) -> int:
    """Calculate complexity score based on tool body"""
    score = 0
    
    # Basic complexity indicators
    score += tool_body.count('if ') * 1
    score += tool_body.count('for ') * 2
    score += tool_body.count('while ') * 2
    score += tool_body.count('try:') * 2
    score += tool_body.count('async ') * 1
    score += tool_body.count('await ') * 1
    
    # Function calls
    score += len(re.findall(r'\w+\([^)]*\)', tool_body)) * 0.5
    
    return int(score)

def count_optional_parameters(parameters: List[Dict[str, Any]]) -> int:
    """Count optional parameters"""
    return sum(1 for param in parameters if param.get("optional", False))

def analyze_configuration_patterns(content: str, tools: List[ToolDefinition]) -> List[ConfigurationPattern]:
    """Analyze configuration patterns across tools"""
    
    patterns = []
    
    # Pattern 1: Security validation pattern
    security_tools = [t for t in tools if t.has_security_validation]
    patterns.append(ConfigurationPattern(
        pattern_name="Security Validation",
        frequency=len(security_tools),
        examples=[t.name for t in security_tools[:3]],
        consolidation_impact="Must be preserved in consolidated tools"
    ))
    
    # Pattern 2: Global database instance pattern
    db_tools = [t for t in tools if 'db' in t.uses_global_instances]
    patterns.append(ConfigurationPattern(
        pattern_name="Global Database Instance",
        frequency=len(db_tools),
        examples=[t.name for t in db_tools[:3]],
        consolidation_impact="Shared resource - consolidation opportunity"
    ))
    
    # Pattern 3: Parameter expansion pattern (many optional parameters)
    param_heavy_tools = [t for t in tools if t.optional_parameter_count > 5]
    patterns.append(ConfigurationPattern(
        pattern_name="Parameter Expansion",
        frequency=len(param_heavy_tools),
        examples=[t.name for t in param_heavy_tools[:3]],
        consolidation_impact="Already following consolidation-friendly pattern"
    ))
    
    # Pattern 4: Error handling pattern
    error_handling_count = content.count('try:')
    patterns.append(ConfigurationPattern(
        pattern_name="Error Handling",
        frequency=error_handling_count,
        examples=["try/except blocks throughout codebase"],
        consolidation_impact="Consistent error handling simplifies consolidation"
    ))
    
    # Pattern 5: Async function pattern
    async_tools = [t for t in tools if 'async' in t.return_type or 'async' in str(t.parameters)]
    patterns.append(ConfigurationPattern(
        pattern_name="Async Function Pattern",
        frequency=len(tools),  # All tools are async
        examples=["All MCP tools use async def pattern"],
        consolidation_impact="Consistent async pattern enables clean consolidation"
    ))
    
    return patterns

def analyze_parameter_structures(tools: List[ToolDefinition]) -> Dict[str, Any]:
    """Analyze parameter structures across tools"""
    
    # Common parameter patterns
    common_params = {}
    for tool in tools:
        for param in tool.parameters:
            param_name = param.get("name", "")
            if param_name in common_params:
                common_params[param_name] += 1
            else:
                common_params[param_name] = 1
    
    # Sort by frequency
    common_params = dict(sorted(common_params.items(), key=lambda x: x[1], reverse=True))
    
    # Parameter type analysis
    type_distribution = {}
    for tool in tools:
        for param in tool.parameters:
            param_type = param.get("type", "unknown")
            # Normalize type names
            if "Optional" in param_type:
                param_type = "Optional"
            elif "str" in param_type:
                param_type = "str"
            elif "int" in param_type:
                param_type = "int"
            elif "bool" in param_type:
                param_type = "bool"
            elif "Dict" in param_type:
                param_type = "Dict"
            elif "List" in param_type:
                param_type = "List"
            
            type_distribution[param_type] = type_distribution.get(param_type, 0) + 1
    
    # Tools by parameter complexity
    complexity_categories = {
        "simple": [t for t in tools if t.parameter_count <= 2],
        "moderate": [t for t in tools if 3 <= t.parameter_count <= 6],
        "complex": [t for t in tools if t.parameter_count > 6]
    }
    
    return {
        "common_parameters": common_params,
        "type_distribution": type_distribution,
        "complexity_categories": {
            category: [t.name for t in tools_list]
            for category, tools_list in complexity_categories.items()
        },
        "consolidation_insights": {
            "parameter_expansion_candidates": [t.name for t in tools if t.optional_parameter_count > 3],
            "simple_consolidation_targets": [t.name for t in tools if t.parameter_count <= 2],
            "complex_tools_needing_cleanup": [t.name for t in tools if t.parameter_count > 10]
        }
    }

def analyze_configuration_dependencies(content: str) -> Dict[str, Any]:
    """Analyze configuration dependencies"""
    
    # Import dependencies
    import_lines = [line.strip() for line in content.split('\n') if line.strip().startswith('from ') or line.strip().startswith('import ')]
    
    # Global variable dependencies
    global_vars = re.findall(r'^(\w+):\s*Optional\[.*\]\s*=\s*None', content, re.MULTILINE)
    
    # Configuration patterns
    config_patterns = {
        "fastmcp_initialization": content.count("FastMCP("),
        "security_manager_usage": content.count("security_manager"),
        "database_initialization": content.count("ClaudeVectorDatabase()"),
        "error_handling_blocks": content.count("try:"),
        "logging_statements": content.count("logger."),
        "mcp_tool_decorators": content.count("@mcp.tool()")
    }
    
    # Tool registration order dependencies
    tool_registration_order = extract_tool_registration_order(content)
    
    return {
        "import_dependencies": import_lines,
        "global_variables": global_vars,
        "configuration_patterns": config_patterns,
        "tool_registration_order": tool_registration_order,
        "consolidation_risks": {
            "shared_global_state": len(global_vars),
            "complex_imports": len([imp for imp in import_lines if "try:" in imp or "except" in imp]),
            "security_dependencies": content.count("validate_mcp_request"),
            "initialization_dependencies": content.count("initialize")
        }
    }

def extract_tool_registration_order(content: str) -> List[str]:
    """Extract tool registration order"""
    
    tool_pattern = re.compile(r'@mcp\.tool\(\)\s*\nasync def (\w+)')
    matches = tool_pattern.findall(content)
    return matches

def main():
    """Run configuration analysis"""
    
    print("⚙️  MCP Server Configuration Analysis")
    print("=" * 40)
    
    try:
        analysis = analyze_mcp_server_configuration()
        
        # Save detailed analysis
        analysis_file = Path(__file__).parent / "configuration_analysis.json"
        
        # Convert ToolDefinition objects to dicts for JSON serialization
        analysis_for_json = {
            "tool_definitions": [asdict(tool) for tool in analysis["tool_definitions"]],
            "configuration_patterns": [asdict(pattern) for pattern in analysis["configuration_patterns"]],
            "parameter_analysis": analysis["parameter_analysis"],
            "dependency_analysis": analysis["dependency_analysis"]
        }
        
        with open(analysis_file, 'w') as f:
            json.dump(analysis_for_json, f, indent=2)
        
        # Print summary
        tools = analysis["tool_definitions"]
        patterns = analysis["configuration_patterns"]
        
        print(f"\n📊 CONFIGURATION SUMMARY:")
        print(f"   Total MCP Tools: {len(tools)}")
        print(f"   Tools with Security Validation: {len([t for t in tools if t.has_security_validation])}")
        print(f"   Average Parameters per Tool: {sum(t.parameter_count for t in tools) / len(tools):.1f}")
        print(f"   Tools with >5 Optional Parameters: {len([t for t in tools if t.optional_parameter_count > 5])}")
        
        print(f"\n🔧 CONFIGURATION PATTERNS:")
        for pattern in patterns:
            print(f"   {pattern.pattern_name}: {pattern.frequency} occurrences")
        
        print(f"\n📋 CONSOLIDATION INSIGHTS:")
        param_analysis = analysis["parameter_analysis"]
        print(f"   Parameter Expansion Candidates: {len(param_analysis['consolidation_insights']['parameter_expansion_candidates'])}")
        print(f"   Simple Consolidation Targets: {len(param_analysis['consolidation_insights']['simple_consolidation_targets'])}")
        
        complexity_dist = param_analysis["complexity_categories"]
        print(f"   Tool Complexity Distribution:")
        print(f"     - Simple (≤2 params): {len(complexity_dist['simple'])} tools")
        print(f"     - Moderate (3-6 params): {len(complexity_dist['moderate'])} tools") 
        print(f"     - Complex (>6 params): {len(complexity_dist['complex'])} tools")
        
        print(f"\n📁 Analysis saved to: {analysis_file}")
        
    except Exception as e:
        print(f"❌ Configuration analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()