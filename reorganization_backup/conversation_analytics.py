#!/usr/bin/env python3
"""
Vector Database Conversation Analytics for Sub-Agent Automation
Analyzes conversation patterns to identify automation opportunities
"""

import json
from collections import Counter, defaultdict
import re
from datetime import datetime
import chromadb

class ConversationAnalytics:
    def __init__(self, db_path="/home/user/.claude-vector-db/db"):
        """Initialize analytics with ChromaDB connection"""
        self.client = chromadb.PersistentClient(path=db_path)
        self.collection = self.client.get_or_create_collection("conversations")
    
    def analyze_command_patterns(self):
        """Analyze common command patterns and frequency"""
        # Get all conversations
        all_conversations = self.collection.get()
        
        command_patterns = Counter()
        npm_commands = Counter()
        git_commands = Counter()
        testing_commands = Counter()
        
        # Regex patterns for common commands
        npm_pattern = re.compile(r'npm run ([a-z:.-]+)', re.IGNORECASE)
        git_pattern = re.compile(r'git ([a-z-]+)', re.IGNORECASE)
        playwright_pattern = re.compile(r'playwright test ([^\s]+)', re.IGNORECASE)
        
        for content in all_conversations['documents']:
            if not content:
                continue
                
            # Find npm commands
            npm_matches = npm_pattern.findall(content)
            for cmd in npm_matches:
                npm_commands[f"npm run {cmd}"] += 1
                command_patterns[f"npm run {cmd}"] += 1
            
            # Find git commands  
            git_matches = git_pattern.findall(content)
            for cmd in git_matches:
                git_commands[f"git {cmd}"] += 1
                command_patterns[f"git {cmd}"] += 1
            
            # Find playwright commands
            playwright_matches = playwright_pattern.findall(content)
            for cmd in playwright_matches:
                testing_commands[f"playwright test {cmd}"] += 1
                command_patterns[f"playwright test {cmd}"] += 1
        
        return {
            'all_commands': command_patterns.most_common(20),
            'npm_commands': npm_commands.most_common(15),
            'git_commands': git_commands.most_common(10),
            'testing_commands': testing_commands.most_common(10)
        }
    
    def analyze_prompt_patterns(self):
        """Analyze common prompt patterns and intentions"""
        all_conversations = self.collection.get()
        
        # Pattern categories
        request_patterns = {
            'testing': re.compile(r'\b(test|spec|screenshot|e2e|playwright)\b', re.IGNORECASE),
            'development': re.compile(r'\b(dev|start|build|run|serve)\b', re.IGNORECASE),
            'git_workflow': re.compile(r'\b(commit|push|pull|branch|merge|git)\b', re.IGNORECASE),
            'debugging': re.compile(r'\b(error|fail|debug|fix|issue|problem)\b', re.IGNORECASE),
            'file_operations': re.compile(r'\b(read|write|edit|create|modify|file)\b', re.IGNORECASE),
            'explanation': re.compile(r'\b(what|how|why|explain|describe|tell me)\b', re.IGNORECASE),
            'automation': re.compile(r'\b(automate|script|hook|agent|workflow)\b', re.IGNORECASE)
        }
        
        pattern_counts = defaultdict(int)
        user_prompts = []
        
        # Collect user prompts (assume they're shorter and more question-like)
        for i, content in enumerate(all_conversations['documents']):
            if not content:
                continue
                
            # Heuristic: user prompts are typically shorter and contain questions/requests
            if len(content) < 500 and ('?' in content or any(word in content.lower() for word in ['can you', 'please', 'help', 'how to'])):
                user_prompts.append(content)
            
            # Count pattern matches
            for pattern_name, pattern in request_patterns.items():
                if pattern.search(content):
                    pattern_counts[pattern_name] += 1
        
        return {
            'pattern_frequency': dict(pattern_counts),
            'sample_user_prompts': user_prompts[:20],
            'total_analyzed': len(all_conversations['documents'])
        }
    
    def analyze_workflow_sequences(self):
        """Analyze common workflow sequences that could be automated"""
        all_conversations = self.collection.get()
        
        # Common workflow sequences
        workflow_sequences = []
        sequence_patterns = [
            ['npm run dev', 'npm run test'],
            ['git add', 'git commit'],
            ['npm run build', 'npm run test'],
            ['playwright test', 'screenshot'],
            ['typecheck', 'lint', 'build'],
            ['npm run validate', 'git commit'],
        ]
        
        sequence_counts = defaultdict(int)
        
        # Look for sequences in conversation content
        for content in all_conversations['documents']:
            if not content:
                continue
                
            content_lower = content.lower()
            for sequence in sequence_patterns:
                # Check if all items in sequence appear in content
                if all(item.lower() in content_lower for item in sequence):
                    sequence_key = ' → '.join(sequence)
                    sequence_counts[sequence_key] += 1
        
        return {
            'common_sequences': dict(sequence_counts),
            'automation_opportunities': self._identify_automation_opportunities(sequence_counts)
        }
    
    def _identify_automation_opportunities(self, sequence_counts):
        """Identify specific automation opportunities based on sequence frequency"""
        opportunities = []
        
        for sequence, count in sequence_counts.items():
            if count >= 3:  # Threshold for automation consideration
                if 'npm run validate → git commit' in sequence:
                    opportunities.append({
                        'sequence': sequence,
                        'frequency': count,
                        'automation_type': 'pre-commit-validation',
                        'sub_agent_potential': 'high',
                        'description': 'Automate validation before commits'
                    })
                elif 'npm run dev → npm run test' in sequence:
                    opportunities.append({
                        'sequence': sequence,
                        'frequency': count,
                        'automation_type': 'dev-test-cycle',
                        'sub_agent_potential': 'medium',
                        'description': 'Automate dev server + testing workflow'
                    })
                elif 'playwright test' in sequence and 'screenshot' in sequence:
                    opportunities.append({
                        'sequence': sequence,
                        'frequency': count,
                        'automation_type': 'visual-testing',
                        'sub_agent_potential': 'high',
                        'description': 'Automate visual testing and screenshot generation'
                    })
        
        return opportunities
    
    def analyze_timeout_patterns(self):
        """Analyze patterns that commonly lead to timeouts"""
        all_conversations = self.collection.get()
        
        timeout_indicators = [
            'timeout', 'timed out', '2 minutes', '120000ms', 
            'command failed', 'agent tool', 'use agent'
        ]
        
        timeout_commands = defaultdict(int)
        timeout_contexts = []
        
        for content in all_conversations['documents']:
            if not content:
                continue
                
            if any(indicator in content.lower() for indicator in timeout_indicators):
                timeout_contexts.append(content[:200] + '...')
                
                # Extract commands mentioned in timeout contexts
                commands = re.findall(r'npm run [a-z:.-]+|playwright test|git [a-z-]+', content, re.IGNORECASE)
                for cmd in commands:
                    timeout_commands[cmd] += 1
        
        return {
            'timeout_prone_commands': dict(timeout_commands),
            'timeout_contexts': timeout_contexts[:10],
            'total_timeout_mentions': len(timeout_contexts)
        }
    
    def generate_sub_agent_recommendations(self):
        """Generate specific sub-agent workflow recommendations"""
        command_analysis = self.analyze_command_patterns()
        workflow_analysis = self.analyze_workflow_sequences()
        timeout_analysis = self.analyze_timeout_patterns()
        
        recommendations = []
        
        # High-frequency command automation
        top_commands = command_analysis['all_commands'][:10]
        for cmd, count in top_commands:
            if count >= 5:  # Threshold for sub-agent consideration
                if 'test:e2e' in cmd:
                    recommendations.append({
                        'type': 'Testing Sub-Agent',
                        'command': cmd,
                        'frequency': count,
                        'rationale': 'High-frequency testing command with timeout potential',
                        'sub_agent_pattern': 'test_execution_agent',
                        'priority': 'high' if count >= 10 else 'medium'
                    })
                elif 'dev' in cmd:
                    recommendations.append({
                        'type': 'Development Sub-Agent', 
                        'command': cmd,
                        'frequency': count,
                        'rationale': 'Development server commands with environment setup needs',
                        'sub_agent_pattern': 'environment_setup_agent',
                        'priority': 'high' if count >= 8 else 'medium'
                    })
        
        # Workflow sequence automation
        for opportunity in workflow_analysis['automation_opportunities']:
            recommendations.append({
                'type': 'Workflow Sub-Agent',
                'command': opportunity['sequence'],
                'frequency': opportunity['frequency'],
                'rationale': opportunity['description'],
                'sub_agent_pattern': 'workflow_automation_agent',
                'priority': opportunity['sub_agent_potential']
            })
        
        # Timeout prevention
        for cmd, count in timeout_analysis['timeout_prone_commands'].items():
            if count >= 3:
                recommendations.append({
                    'type': 'Timeout Prevention Sub-Agent',
                    'command': cmd,
                    'frequency': count,
                    'rationale': 'Command frequently mentioned in timeout contexts',
                    'sub_agent_pattern': 'timeout_prevention_agent',
                    'priority': 'high'
                })
        
        return sorted(recommendations, key=lambda x: x['frequency'], reverse=True)
    
    def generate_prompt_templates(self):
        """Generate automated prompt templates for common tasks"""
        prompt_analysis = self.analyze_prompt_patterns()
        command_analysis = self.analyze_command_patterns()
        
        templates = []
        
        # Testing automation templates
        if any('test' in cmd for cmd, _ in command_analysis['npm_commands']):
            templates.append({
                'name': 'Quick E2E Testing',
                'pattern': 'testing_workflow',
                'template': '''Use the Agent tool to execute comprehensive testing workflow:

1. Verify development server is running and accessible
2. Set correct environment variables for testing  
3. Execute npm run test:e2e:smoke for quick validation
4. Generate screenshots for visual validation
5. Report any failures with detailed analysis
6. Suggest next steps based on results

Goal: Reliable testing execution without timeout issues.''',
                'trigger_words': ['test', 'e2e', 'screenshot', 'validate'],
                'frequency_score': 'high'
            })
        
        # Development setup templates
        if any('dev' in cmd for cmd, _ in command_analysis['npm_commands']):
            templates.append({
                'name': 'Development Environment Setup',
                'pattern': 'environment_setup', 
                'template': '''Use the Agent tool to handle complete environment setup:

1. Detect active development server ports
2. Verify server health and accessibility
3. Set correct environment variables (ACTIVE_DEV_PORT, ACTIVE_DEV_URL)
4. Clean up any conflicting or unresponsive servers
5. Start fresh server if needed
6. Validate environment is ready for development/testing

Goal: Eliminate timeout issues by ensuring proper environment setup.''',
                'trigger_words': ['dev', 'server', 'start', 'environment'],
                'frequency_score': 'high'
            })
        
        # Git workflow templates
        if any('git' in cmd for cmd, _ in command_analysis['git_commands']):
            templates.append({
                'name': 'Git Workflow Automation',
                'pattern': 'git_workflow',
                'template': '''Use the Agent tool to handle complete git workflow:

1. Run npm run validate to ensure code quality
2. Check git status and review changes
3. Add appropriate files to staging
4. Create descriptive commit message
5. Execute commit with proper formatting
6. Optionally push to remote if requested

Goal: Streamlined git workflow with quality gates.''',
                'trigger_words': ['commit', 'push', 'git', 'validate'],
                'frequency_score': 'medium'
            })
        
        return templates

def main():
    """Run analytics and generate report"""
    print("🔍 Analyzing Vector Database Conversations for Sub-Agent Opportunities...")
    
    analytics = ConversationAnalytics()
    
    # Run all analyses
    print("\n📊 Command Pattern Analysis...")
    commands = analytics.analyze_command_patterns()
    
    print("\n🎯 Prompt Pattern Analysis...")
    prompts = analytics.analyze_prompt_patterns()
    
    print("\n🔄 Workflow Sequence Analysis...")
    workflows = analytics.analyze_workflow_sequences()
    
    print("\n⏱️ Timeout Pattern Analysis...")
    timeouts = analytics.analyze_timeout_patterns()
    
    print("\n🤖 Generating Sub-Agent Recommendations...")
    recommendations = analytics.generate_sub_agent_recommendations()
    
    print("\n📝 Generating Prompt Templates...")
    templates = analytics.generate_prompt_templates()
    
    # Generate comprehensive report
    report = {
        'analysis_date': datetime.now().isoformat(),
        'command_patterns': commands,
        'prompt_patterns': prompts,
        'workflow_sequences': workflows,
        'timeout_patterns': timeouts,
        'sub_agent_recommendations': recommendations,
        'automated_prompt_templates': templates,
        'summary': {
            'total_conversations_analyzed': prompts['total_analyzed'],
            'top_automation_opportunities': len([r for r in recommendations if r['priority'] == 'high']),
            'template_count': len(templates)
        }
    }
    
    # Save report
    report_path = "/home/user/.claude-vector-db/analytics_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Analysis complete! Report saved to {report_path}")
    
    # Print summary
    print("\n" + "="*60)
    print("📈 CONVERSATION ANALYTICS SUMMARY")
    print("="*60)
    
    print(f"\n🔢 Conversations Analyzed: {prompts['total_analyzed']}")
    print(f"🔥 Top Commands: {', '.join([cmd for cmd, _ in commands['all_commands'][:5]])}")
    print(f"⚡ High-Priority Automation Opportunities: {len([r for r in recommendations if r['priority'] == 'high'])}")
    print(f"📝 Prompt Templates Generated: {len(templates)}")
    
    print("\n🎯 TOP SUB-AGENT RECOMMENDATIONS:")
    for i, rec in enumerate(recommendations[:3], 1):
        print(f"{i}. {rec['type']}: {rec['command']} (frequency: {rec['frequency']})")
    
    print("\n📋 AUTOMATION TEMPLATES AVAILABLE:")
    for template in templates:
        print(f"• {template['name']} - {template['frequency_score']} priority")
    
    return report

if __name__ == "__main__":
    main()