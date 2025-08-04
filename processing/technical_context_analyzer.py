"""
Technical Context Analyzer - Domain-specific technical feedback analysis system.

Implements sophisticated technical domain detection and context analysis for feedback
validation enhancement. Targets 85% technical context accuracy with <30ms processing time.

Key Features:  
- 4 technical domain detection (build_system, testing, runtime, deployment)
- Solution context analysis using tools_used and content patterns
- Complex outcome detection for mixed success/failure scenarios
- Performance-optimized pattern matching with caching
- Integration with existing enhanced_context.py patterns

Based on July 2025 technical feedback analysis best practices and production
system troubleshooting patterns.
"""

import logging
import re
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from functools import lru_cache

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class TechnicalAnalysisResult:
    """Structured result from technical context analysis"""
    technical_domain: Optional[str]  # Primary detected domain
    technical_confidence: float  # 0.0-1.0 confidence score
    domain_scores: Dict[str, float]  # All domain scores
    complex_outcome_detected: bool  # Mixed success/failure scenarios
    solution_context_analysis: Dict[str, Any]  # Analysis of solution context
    detected_tools: List[str]  # Technical tools detected in feedback
    outcome_patterns: List[str]  # Specific outcome patterns found
    processing_time_ms: float  # Processing time in milliseconds
    method: str  # Analysis method used


class TechnicalContextAnalyzer:
    """
    Domain-specific technical feedback analysis with 85% accuracy target.
    
    Analyzes technical feedback across 4 key domains:
    - build_system: Compilation, building, packaging
    - testing: Unit tests, integration tests, test frameworks  
    - runtime: Execution, performance, runtime errors
    - deployment: Deployment, production, server management
    
    Features advanced pattern matching for complex technical outcomes and
    integration with solution context from tools_used metadata.
    """
    
    def __init__(self, performance_target_ms: float = 30.0):
        """
        Initialize technical context analyzer.
        
        Args:
            performance_target_ms: Target processing time in milliseconds
        """
        logger.info("⚙️ Initializing TechnicalContextAnalyzer")
        
        self.performance_target_ms = performance_target_ms
        
        # Initialize domain-specific pattern libraries
        self._initialize_domain_patterns()
        
        # Initialize tools and technology mappings
        self._initialize_tool_mappings()
        
        # Initialize complex outcome patterns
        self._initialize_complex_outcome_patterns()
        
        # Performance tracking
        self.stats = {
            'total_analyses': 0,
            'domain_detections': 0,
            'complex_outcomes_detected': 0,
            'average_processing_time_ms': 0.0,
            'accuracy_samples': []
        }
        
        logger.info(f"✅ TechnicalContextAnalyzer initialized with {len(self.domain_patterns)} domains")
    
    def _initialize_domain_patterns(self):
        """Initialize sophisticated domain-specific pattern libraries"""
        
        self.domain_patterns = {
            'build_system': {
                'success_patterns': [
                    'build successful', 'compilation successful', 'build passes', 'compiled successfully',
                    'build complete', 'make successful', 'gradle build successful', 'webpack build',
                    'build finished', 'no build errors', 'build succeeded', 'npm run build',
                    'compiled without errors', 'build process completed', 'successful compilation',
                    'build artifacts created', 'clean build', 'build passed'
                ],
                'failure_patterns': [
                    'build failed', 'compilation error', 'build error', 'compile failed',
                    'build broken', 'make failed', 'gradle build failed', 'webpack failed',
                    'build failure', 'compilation failed', 'build issues', 'build problems',
                    'cannot compile', 'build script failed', 'build process failed',
                    'build artifacts missing', 'build timeout', 'build crashed'
                ],
                'tools': ['gcc', 'clang', 'make', 'cmake', 'gradle', 'maven', 'npm', 'webpack', 'vite', 'rollup']
            },
            
            'testing': {
                'success_patterns': [
                    'tests pass', 'all tests pass', 'tests successful', 'test suite passed',
                    'no test failures', 'tests green', 'test execution successful', '100% tests passed',
                    'all tests passed', 'test run successful', 'no failing tests', 'tests completed',
                    'test coverage', 'all assertions passed', 'test validation passed', 'tests ok',
                    'unit tests pass', 'integration tests pass', 'e2e tests pass'
                ],
                'failure_patterns': [
                    'test failed', 'tests failing', 'test failure', 'failing tests',
                    'test errors', 'assertion failed', 'test suite failed', 'tests broken',
                    'test execution failed', 'some tests failed', 'test timeout', 'test crashed',
                    'unit test failed', 'integration test failed', 'e2e tests failed', 'test flaky',
                    'tests unstable', 'intermittent test failures', 'test environment issues'
                ],
                'tools': ['pytest', 'jest', 'mocha', 'junit', 'phpunit', 'rspec', 'jasmine', 'cypress', 'selenium', 'playwright']
            },
            
            'runtime': {
                'success_patterns': [
                    'runs successfully', 'executes correctly', 'running fine', 'works as expected',
                    'no runtime errors', 'application running', 'execution successful', 'runs without issues',
                    'performance good', 'responsive', 'stable execution', 'running smoothly',
                    'no crashes', 'application stable', 'runtime healthy', 'executing properly',
                    'process running', 'service up', 'application responsive'
                ],
                'failure_patterns': [
                    'runtime error', 'execution failed', 'application crashed', 'runtime exception',
                    'segmentation fault', 'memory error', 'null pointer', 'stack overflow',
                    'runtime failure', 'execution error', 'process crashed', 'application hang',
                    'performance issues', 'slow execution', 'timeout error', 'deadlock',
                    'resource exhausted', 'out of memory', 'cpu spike', 'infinite loop'
                ],
                'tools': ['node', 'python', 'java', 'dotnet', 'go', 'ruby', 'php', 'docker', 'pm2', 'systemd']
            },
            
            'deployment': {
                'success_patterns': [
                    'deployed successfully', 'deployment complete', 'deploy successful', 'deployment passed',
                    'server running', 'service deployed', 'production ready', 'deployment finished',
                    'rollout successful', 'deployment healthy', 'service up', 'deployment validated',
                    'infrastructure ready', 'deployment stable', 'release successful', 'deploy complete',
                    'environment ready', 'deployment verified', 'production deployment successful'
                ],
                'failure_patterns': [
                    'deployment failed', 'deploy error', 'deployment failure', 'rollout failed',
                    'deployment timeout', 'deploy crashed', 'deployment issues', 'rollback required',
                    'deployment unhealthy', 'service down', 'deployment validation failed', 'deploy problems',
                    'infrastructure issues', 'deployment blocked', 'release failed', 'environment issues',
                    'deployment rollback', 'deployment stuck', 'service unavailable'
                ],
                'tools': ['docker', 'kubernetes', 'helm', 'terraform', 'ansible', 'jenkins', 'github-actions', 'aws', 'gcp', 'azure']
            }
        }
    
    def _initialize_tool_mappings(self):
        """Initialize mappings between tools and technical domains"""
        
        self.tool_domain_mapping = {
            # Build tools
            'gcc': 'build_system', 'clang': 'build_system', 'make': 'build_system',
            'cmake': 'build_system', 'gradle': 'build_system', 'maven': 'build_system',
            'npm': 'build_system', 'webpack': 'build_system', 'vite': 'build_system',
            
            # Testing tools  
            'pytest': 'testing', 'jest': 'testing', 'mocha': 'testing',
            'junit': 'testing', 'rspec': 'testing', 'cypress': 'testing',
            'playwright': 'testing', 'selenium': 'testing',
            
            # Runtime tools
            'node': 'runtime', 'python': 'runtime', 'java': 'runtime',
            'dotnet': 'runtime', 'go': 'runtime', 'ruby': 'runtime',
            'pm2': 'runtime', 'systemd': 'runtime',
            
            # Deployment tools
            'docker': 'deployment', 'kubernetes': 'deployment', 'helm': 'deployment',
            'terraform': 'deployment', 'ansible': 'deployment', 'jenkins': 'deployment',
            'github-actions': 'deployment', 'aws': 'deployment'
        }
        
        # Technology stack indicators
        self.tech_stack_indicators = {
            'javascript': ['npm', 'node', 'webpack', 'jest', 'cypress'],
            'python': ['pip', 'pytest', 'django', 'flask', 'fastapi'],
            'java': ['maven', 'gradle', 'junit', 'spring'],
            'go': ['go', 'mod', 'test'],
            'rust': ['cargo', 'rustc'],
            'docker': ['dockerfile', 'docker-compose', 'container']
        }
    
    def _initialize_complex_outcome_patterns(self):
        """Initialize patterns for detecting complex technical outcomes"""
        
        self.complex_outcome_patterns = [
            # Build vs Test contradictions
            (r'build\s+(pass|success|ok)', r'test\s+(fail|error|broken)'),
            (r'compil\w+\s+(success|ok)', r'test\s+(fail|error)'),
            
            # Local vs Production contradictions
            (r'works?\s+(local|dev)', r'fail\w*\s+(prod|production|deploy)'),
            (r'local\w*\s+(success|ok)', r'production\s+(error|fail)'),
            
            # Partial success patterns
            (r'some\s+tests?\s+(pass|ok)', r'other\s+tests?\s+(fail|error)'),
            (r'mostly\s+(work|success)', r'but\s+\w*\s+(error|fail|issue)'),
            (r'partial\w*\s+(success|work)', r'still\s+\w*\s+(error|issue)'),
            
            # Performance vs Functionality
            (r'functional\w*\s+(correct|ok)', r'performance\s+(slow|issue|problem)'),
            (r'works?\s+(correct)', r'too\s+(slow|fast)'),
            
            # Intermittent issues
            (r'sometimes\s+(work|pass)', r'sometimes\s+(fail|error)'),
            (r'intermittent\w*', r'(fail|error|issue)'),
            (r'flaky', r'test'),
            
            # Environment-specific issues
            (r'dev\s+(environment|env)', r'prod\w*\s+(fail|error)'),
            (r'staging\s+(ok|pass)', r'production\s+(fail|error)')
        ]
    
    @lru_cache(maxsize=500)
    def _analyze_content_patterns(self, content: str) -> Dict[str, float]:
        """Analyze content for domain-specific patterns with caching"""
        content_lower = content.lower()
        domain_scores = {}
        
        for domain, patterns in self.domain_patterns.items():
            score = 0.0
            
            # Success pattern scoring (positive weight)
            for pattern in patterns['success_patterns']:
                if pattern in content_lower:
                    score += 2.0  # Higher weight for explicit success
            
            # Failure pattern scoring (also positive for domain detection)
            for pattern in patterns['failure_patterns']:
                if pattern in content_lower:
                    score += 1.5  # Detect domain even with failure
            
            # Tool-based scoring
            for tool in patterns['tools']:
                if tool in content_lower:
                    score += 1.0
            
            domain_scores[domain] = score
        
        return domain_scores
    
    def analyze_technical_feedback(self, 
                                 feedback_content: str,
                                 solution_context: Optional[Dict] = None) -> TechnicalAnalysisResult:
        """
        Analyze technical domain context for enhanced feedback understanding.
        
        Targets 85% technical context accuracy with <30ms processing time.
        
        Args:
            feedback_content: User feedback text to analyze
            solution_context: Context about solution including tools_used, domain info
            
        Returns:
            TechnicalAnalysisResult with comprehensive technical analysis
        """
        start_time = time.time()
        self.stats['total_analyses'] += 1
        
        if not feedback_content or not feedback_content.strip():
            return TechnicalAnalysisResult(
                technical_domain=None,
                technical_confidence=0.0,
                domain_scores={},
                complex_outcome_detected=False,
                solution_context_analysis={},
                detected_tools=[],
                outcome_patterns=[],
                processing_time_ms=0.0,
                method="empty_input"
            )
        
        # Analyze content patterns for domain detection
        domain_scores = self._analyze_content_patterns(feedback_content.strip())
        
        # Enhance with solution context analysis
        if solution_context:
            context_analysis = self._analyze_solution_context(solution_context)
            # Boost domain scores based on context
            for domain, boost in context_analysis.get('domain_boosts', {}).items():
                if domain in domain_scores:
                    domain_scores[domain] *= (1.0 + boost)
        else:
            context_analysis = {}
        
        # Determine primary technical domain
        if domain_scores:
            primary_domain_item = max(domain_scores.items(), key=lambda x: x[1])
            primary_domain, domain_confidence = primary_domain_item
            
            # Normalize confidence (scores can be >1.0)
            max_possible_score = 5.0  # Estimated max from patterns + tools
            domain_confidence = min(domain_confidence / max_possible_score, 1.0)
        else:
            primary_domain, domain_confidence = None, 0.0
        
        # Detect complex technical outcomes
        complex_outcome = self._detect_complex_technical_outcome(feedback_content)
        if complex_outcome:
            self.stats['complex_outcomes_detected'] += 1
        
        # Extract detected tools
        detected_tools = self._extract_technical_tools(feedback_content)
        
        # Find specific outcome patterns
        outcome_patterns = self._find_outcome_patterns(feedback_content)
        
        # Calculate processing time and validate performance
        processing_time = (time.time() - start_time) * 1000
        
        # Update performance statistics
        self.stats['average_processing_time_ms'] = (
            (self.stats['average_processing_time_ms'] * (self.stats['total_analyses'] - 1) + processing_time)
            / self.stats['total_analyses']
        )
        
        # Performance validation: Must complete within target time
        if processing_time > self.performance_target_ms:
            logger.warning(f"⚠️ Technical analysis took {processing_time:.1f}ms, exceeds {self.performance_target_ms}ms target")
        
        # Track domain detection success
        if primary_domain and domain_confidence > 0.4:
            self.stats['domain_detections'] += 1
        
        return TechnicalAnalysisResult(
            technical_domain=primary_domain if domain_confidence > 0.4 else None,
            technical_confidence=domain_confidence,
            domain_scores=domain_scores,
            complex_outcome_detected=complex_outcome,
            solution_context_analysis=context_analysis,
            detected_tools=detected_tools,
            outcome_patterns=outcome_patterns,
            processing_time_ms=processing_time,
            method="technical_context_analysis"
        )
    
    def _analyze_solution_context(self, solution_context: Dict) -> Dict[str, Any]:
        """Analyze solution context to enhance domain detection"""
        context_analysis = {
            'tools_analysis': {},
            'domain_boosts': {},
            'tech_stack_detected': []
        }
        
        # Analyze tools_used if available
        tools_used = solution_context.get('tools_used', [])
        if isinstance(tools_used, list):
            for tool in tools_used:
                if tool in self.tool_domain_mapping:
                    domain = self.tool_domain_mapping[tool]
                    context_analysis['tools_analysis'][tool] = domain
                    
                    # Boost corresponding domain score
                    if domain not in context_analysis['domain_boosts']:
                        context_analysis['domain_boosts'][domain] = 0.0
                    context_analysis['domain_boosts'][domain] += 0.5
        
        # Detect technology stack
        content = solution_context.get('content', '')
        if content:
            for tech_stack, indicators in self.tech_stack_indicators.items():
                for indicator in indicators:
                    if indicator in content.lower():
                        context_analysis['tech_stack_detected'].append(tech_stack)
                        break
        
        return context_analysis
    
    def _detect_complex_technical_outcome(self, feedback_content: str) -> bool:
        """Detect complex technical outcomes like 'build passes but tests fail'"""
        content_lower = feedback_content.lower()
        
        # Check for contradictory pattern combinations
        for success_pattern, failure_pattern in self.complex_outcome_patterns:
            if re.search(success_pattern, content_lower) and re.search(failure_pattern, content_lower):
                logger.debug(f"🔍 Complex outcome detected: {success_pattern} + {failure_pattern}")
                return True
        
        # Additional heuristic patterns
        complex_indicators = [
            'but', 'however', 'although', 'except', 'partially',
            'some work', 'mostly work', 'intermittent', 'sometimes'
        ]
        
        for indicator in complex_indicators:
            if indicator in content_lower:
                # Look for success/failure keywords near the indicator
                words = content_lower.split()
                try:
                    indicator_idx = words.index(indicator)
                    nearby_words = words[max(0, indicator_idx-3):indicator_idx+4]
                    
                    success_words = ['work', 'pass', 'success', 'ok', 'good']
                    failure_words = ['fail', 'error', 'broke', 'issue', 'problem']
                    
                    has_success = any(word in nearby_words for word in success_words)
                    has_failure = any(word in nearby_words for word in failure_words)
                    
                    if has_success and has_failure:
                        return True
                except ValueError:
                    continue
        
        return False
    
    def _extract_technical_tools(self, feedback_content: str) -> List[str]:
        """Extract technical tools mentioned in feedback"""
        content_lower = feedback_content.lower()
        detected_tools = []
        
        # Check for all known tools
        all_tools = set()
        for domain_patterns in self.domain_patterns.values():
            all_tools.update(domain_patterns['tools'])
        
        for tool in all_tools:
            if tool in content_lower:
                detected_tools.append(tool)
        
        return detected_tools
    
    def _find_outcome_patterns(self, feedback_content: str) -> List[str]:
        """Find specific outcome patterns in feedback"""
        content_lower = feedback_content.lower()
        found_patterns = []
        
        # Check for specific outcome indicators
        outcome_indicators = [
            'successful', 'failed', 'error', 'pass', 'crash',
            'timeout', 'hang', 'slow', 'fast', 'broken', 'fixed'
        ]
        
        for indicator in outcome_indicators:
            if indicator in content_lower:
                found_patterns.append(indicator)
        
        return found_patterns
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get comprehensive performance and accuracy statistics"""
        detection_rate = (self.stats['domain_detections'] / max(1, self.stats['total_analyses'])) * 100
        complex_outcome_rate = (self.stats['complex_outcomes_detected'] / max(1, self.stats['total_analyses'])) * 100
        
        return {
            'total_analyses': self.stats['total_analyses'],
            'domain_detections': self.stats['domain_detections'],
            'domain_detection_rate_percent': detection_rate,
            'complex_outcomes_detected': self.stats['complex_outcomes_detected'],
            'complex_outcome_rate_percent': complex_outcome_rate,
            'average_processing_time_ms': self.stats['average_processing_time_ms'],
            'performance_target_met': self.stats['average_processing_time_ms'] < self.performance_target_ms,
            'performance_target_ms': self.performance_target_ms,
            'domain_info': {
                'total_domains': len(self.domain_patterns),
                'total_tools_mapped': len(self.tool_domain_mapping),
                'complex_patterns': len(self.complex_outcome_patterns)
            }
        }
    
    def validate_accuracy(self, test_cases: List[Tuple[str, str, Optional[Dict]]]) -> float:
        """
        Validate technical context detection accuracy using test cases.
        
        Args:
            test_cases: List of (feedback_content, expected_domain, solution_context) tuples
            
        Returns:
            Accuracy score (0.0-1.0) for technical domain detection
        """
        if not test_cases:
            return 0.0
        
        correct_predictions = 0
        
        for feedback_content, expected_domain, solution_context in test_cases:
            result = self.analyze_technical_feedback(feedback_content, solution_context)
            
            if result.technical_domain == expected_domain:
                correct_predictions += 1
            
            # Store for accuracy tracking
            self.stats['accuracy_samples'].append({
                'expected': expected_domain,
                'predicted': result.technical_domain,
                'confidence': result.technical_confidence,
                'correct': result.technical_domain == expected_domain
            })
        
        accuracy = correct_predictions / len(test_cases)
        logger.info(f"📊 Technical context accuracy: {accuracy:.1%} ({correct_predictions}/{len(test_cases)})")
        return accuracy


# Convenience functions for integration
def create_technical_analyzer(**kwargs) -> TechnicalContextAnalyzer:
    """Create a technical context analyzer with default settings"""
    return TechnicalContextAnalyzer(**kwargs)


def analyze_technical_context(feedback_content: str, 
                            solution_context: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function for quick technical context analysis.
    
    Args:
        feedback_content: User feedback text to analyze
        solution_context: Optional solution context dictionary
        
    Returns:
        Dictionary with technical analysis results
    """
    analyzer = create_technical_analyzer()
    result = analyzer.analyze_technical_feedback(feedback_content, solution_context)
    
    return {
        'technical_domain': result.technical_domain,
        'technical_confidence': result.technical_confidence,
        'domain_scores': result.domain_scores,
        'complex_outcome_detected': result.complex_outcome_detected,
        'detected_tools': result.detected_tools,
        'outcome_patterns': result.outcome_patterns,
        'processing_time_ms': result.processing_time_ms,
        'method': result.method
    }


if __name__ == "__main__":
    # Demo and basic validation
    analyzer = TechnicalContextAnalyzer()
    
    # Test various technical feedback scenarios
    test_cases = [
        ("Build passes but tests are failing", None),
        ("npm run build successful", {'tools_used': ['npm']}),
        ("Runtime error: null pointer exception", None),
        ("Deployment to production failed with timeout", {'tools_used': ['docker', 'kubernetes']}),
        ("All tests pass in local environment", None),
        ("Performance is slow but functionally correct", None)
    ]
    
    print("⚙️ Technical Context Analyzer Demo")
    print("=" * 50)
    
    for i, (feedback, context) in enumerate(test_cases, 1):
        result = analyzer.analyze_technical_feedback(feedback, context)
        print(f"\n{i}. Feedback: '{feedback}'")
        print(f"   Domain: {result.technical_domain} (confidence: {result.technical_confidence:.2f})")
        print(f"   Complex outcome: {result.complex_outcome_detected}")
        print(f"   Tools detected: {result.detected_tools}")
        print(f"   Processing: {result.processing_time_ms:.1f}ms")
    
    print(f"\n📊 Performance Summary:")
    stats = analyzer.get_performance_stats()
    for key, value in stats.items():
        if isinstance(value, dict):
            print(f"   {key}: {value}")
        else:
            print(f"   {key}: {value}")