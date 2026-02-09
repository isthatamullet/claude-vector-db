# Workflow Examples

Common usage patterns and complete workflows for the Claude Code Vector Database System.

## Overview

This guide provides tested, real-world examples of how to use the 14 consolidated MCP tools for common development scenarios. Each workflow includes step-by-step instructions, expected outputs, and troubleshooting guidance.

**Target Users**: Developers using Claude Code with the vector database system for context-aware development assistance.

---

## Workflow Categories

### 1. 🔍 Search & Discovery Workflows
### 2. 🐛 Debugging & Troubleshooting Workflows  
### 3. 📊 System Monitoring & Health Workflows
### 4. ⚡ Performance Optimization Workflows
### 5. 🔧 System Maintenance Workflows
### 6. 📈 Learning & Analytics Workflows

---

## 🔍 Search & Discovery Workflows

### Workflow 1: Project-Aware Solution Discovery

**Scenario**: Finding previous solutions for React component optimization in a specific project.

**Steps**:
```python
# Step 1: Detect current project context
project_info = detect_current_project()
# Returns: {"project_name": "tylergohr.com", "confidence": 0.95, "path": "/home/user/tylergohr.com"}

# Step 2: Search for React optimization solutions in current project
solutions = search_conversations_unified(
    query="React component optimization performance",
    project_context=project_info["project_name"],
    search_mode="validated_only",
    use_validation_boost=True,
    limit=10
)

# Step 3: Get detailed context for most relevant solution
if solutions["results"]:
    context_chain = get_conversation_context_chain(
        message_id=solutions["results"][0]["id"],
        chain_length=5,
        show_relationships=True
    )
```

**Expected Output**: 
- Project context with high confidence score
- 5-10 validated solutions with relevance scores
- Complete conversation chain showing solution development

**Use Cases**: Code review preparation, architecture decisions, performance optimization

---

### Workflow 2: Cross-Project Learning Discovery

**Scenario**: Learning from similar problems solved in different projects.

**Steps**:
```python
# Step 1: Search across all projects for similar patterns
cross_project_results = search_conversations_unified(
    query="authentication implementation JWT tokens",
    search_mode="semantic",
    include_context_chains=True,
    troubleshooting_mode=True,
    limit=15
)

# Step 2: Analyze patterns across projects
patterns = analyze_patterns_unified(
    feedback_content="Found similar auth implementations",
    analysis_type="pattern_similarity",
    pattern_type="positive",
    top_k=5
)

# Step 3: Get project-specific context summary
for project in ["tylergohr.com", "invoice-chaser"]:
    context = get_project_context_summary(
        project_name=project,
        days_back=60
    )
```

**Expected Output**:
- Solutions from multiple projects with technology stack correlation
- Pattern analysis showing successful authentication approaches  
- Project-specific context highlighting different implementation strategies

**Use Cases**: Technology stack decisions, cross-project knowledge transfer, architecture consistency

---

## 🐛 Debugging & Troubleshooting Workflows

### Workflow 3: Error Resolution with Historical Context

**Scenario**: Resolving a build error by learning from previous similar failures.

**Steps**:
```python
# Step 1: Search for similar build failures
error_history = search_conversations_unified(
    query="vite build failed dependency version conflict",
    search_mode="failed_only",
    project_context="tylergohr.com",
    troubleshooting_mode=True,
    include_context_chains=True,
    limit=8
)

# Step 2: Analyze technical context of failures
technical_analysis = analyze_patterns_unified(
    feedback_content="Build failed after dependency update, similar to previous issues",
    analysis_type="technical",
    solution_context={
        "build_system": "vite",
        "error_type": "dependency_conflict",
        "project": "tylergohr.com"
    }
)

# Step 3: Get recent project activity for context
recent_changes = search_conversations_unified(
    query="dependency package.json changes",
    search_mode="recent_only",
    project_context="tylergohr.com",
    recency="last_3_days",
    limit=5
)

# Step 4: Provide solution feedback for learning
solution_feedback = process_feedback_unified(
    feedback_text="The rollback to previous dependency versions worked",
    solution_context={
        "tool_used": "Edit",
        "file_modified": "package.json",
        "solution_type": "dependency_rollback"
    },
    processing_mode="adaptive"
)
```

**Expected Output**:
- Historical failures with resolution patterns
- Technical analysis highlighting common failure modes
- Recent project changes that might be related
- Adaptive learning integration for future similar issues

**Use Cases**: Build error resolution, dependency conflict troubleshooting, deployment issues

---

### Workflow 4: Performance Issue Investigation

**Scenario**: Investigating performance degradation with comprehensive context analysis.

**Steps**:
```python
# Step 1: Search for performance-related conversations
perf_issues = search_conversations_unified(
    query="performance slow loading optimization",
    search_mode="by_topic",
    topic_focus="performance",
    project_context="tylergohr.com",
    prefer_solutions=True,
    limit=12
)

# Step 2: Analyze performance patterns
perf_patterns = analyze_patterns_unified(
    feedback_content="Page load times increased after recent changes",
    analysis_type="multimodal",
    solution_context={
        "performance_metric": "page_load_time",
        "baseline": "1.2s",
        "current": "3.8s",
        "change_timeframe": "last_week"
    }
)

# Step 3: Get system health to rule out infrastructure issues  
system_health = get_system_status(
    status_type="performance",
    include_analytics=True,
    format="metrics_only"
)

# Step 4: Run adaptive learning to improve future performance analysis
learning_enhancement = run_adaptive_learning_enhancement(
    learning_type="comprehensive",
    hours=168  # 1 week
)
```

**Expected Output**:
- Performance-related conversations with solution success rates
- Multi-modal analysis of performance degradation patterns
- System performance metrics to rule out infrastructure issues
- Enhanced learning for future performance investigations

**Use Cases**: Performance regression analysis, optimization strategy development, system capacity planning

---

## 📊 System Monitoring & Health Workflows

### Workflow 5: Comprehensive System Health Assessment

**Scenario**: Regular system health check with detailed analytics and trend analysis.

**Steps**:
```python
# Step 1: Comprehensive system status
full_status = get_system_status(
    status_type="comprehensive",
    include_analytics=True,
    include_enhancement_metrics=True,
    include_semantic_health=True
)

# Step 2: Learning insights for trend analysis
learning_trends = get_learning_insights(
    insight_type="comprehensive",
    time_range="7d",
    metric_type="performance"
)

# Step 3: Enhanced metadata coverage analysis
metadata_status = smart_metadata_sync_status()

# Step 4: Adaptive learning system health
adaptive_health = run_adaptive_learning_enhancement(
    learning_type="comprehensive",
    cultural_adaptation=True,
    hours=24
)
```

**Expected Output**:
- Complete system health report with all subsystems
- 7-day trend analysis of learning and validation systems
- Metadata coverage statistics with enhancement recommendations
- Adaptive learning system performance metrics

**Use Cases**: Daily system health monitoring, performance trend analysis, capacity planning

---

### Workflow 6: Performance Bottleneck Identification

**Scenario**: Identifying and resolving system performance bottlenecks.

**Steps**:
```python
# Step 1: Performance-focused system status
perf_metrics = get_system_status(
    status_type="performance",
    include_analytics=True,
    format="metrics_only"
)

# Step 2: Configuration optimization analysis
config_analysis = configure_enhancement_systems(
    performance_mode="balanced",
    enhancement_aggressiveness=1.2,
    max_search_latency_ms=150,  # Stricter than default 200ms
    degradation_threshold=0.85
)

# Step 3: Force sync with performance monitoring
sync_performance = force_conversation_sync(
    parallel_processing=True
)

# Step 4: Validate performance improvements
post_optimization_status = get_system_status(
    status_type="performance",
    format="summary"
)
```

**Expected Output**:
- Detailed performance metrics with bottleneck identification
- Configuration changes with expected impact analysis
- Sync performance results with timing metrics
- Post-optimization validation showing improvements

**Use Cases**: Performance tuning, system optimization, capacity planning

---

## ⚡ Performance Optimization Workflows

### Workflow 7: Search Performance Optimization

**Scenario**: Optimizing search response times and cache effectiveness.

**Steps**:
```python
# Step 1: Baseline search performance measurement
import time

start_time = time.time()
baseline_search = search_conversations_unified(
    query="React hooks useState performance",
    project_context="tylergohr.com",
    use_validation_boost=True,
    limit=5
)
baseline_duration = time.time() - start_time

# Step 2: Enable all performance optimizations
optimized_config = configure_enhancement_systems(
    performance_mode="aggressive",
    enhancement_aggressiveness=1.5,
    max_search_latency_ms=100,  # Aggressive target
    chromadb_optimization=True
)

# Step 3: Repeated search to test cache effectiveness
start_time = time.time()
cached_search = search_conversations_unified(
    query="React hooks useState performance",  # Same query
    project_context="tylergohr.com",
    use_validation_boost=True,
    limit=5
)
cached_duration = time.time() - start_time

# Step 4: Performance analytics comparison
performance_comparison = get_learning_insights(
    insight_type="realtime",
    time_range="1h",
    metric_type="performance"
)
```

**Expected Output**:
- Baseline search performance metrics
- Optimized configuration impact analysis
- Cache effectiveness measurement (target: 100x improvement)
- Performance analytics showing optimization results

**Use Cases**: System performance tuning, cache optimization, search latency reduction

---

### Workflow 8: Enhancement System Optimization

**Scenario**: Optimizing the PRP enhancement systems for maximum effectiveness.

**Steps**:
```python
# Step 1: Current enhancement system status
enhancement_status = get_system_status(
    status_type="analytics_only",
    include_enhancement_metrics=True
)

# Step 2: Run unified enhancement with optimization focus
enhancement_results = run_unified_enhancement(
    enable_backfill=True,
    enable_optimization=True,
    enable_validation=True,
    max_sessions=15
)

# Step 3: Adaptive learning optimization
adaptive_optimization = run_adaptive_learning_enhancement(
    learning_type="comprehensive",
    cultural_adaptation=True,
    hours=72  # 3 days for comprehensive analysis
)

# Step 4: Validate enhancement effectiveness
post_enhancement_status = get_system_status(
    status_type="comprehensive",
    include_enhancement_metrics=True
)
```

**Expected Output**:
- Enhancement system baseline metrics
- Unified enhancement processing results with field population improvements
- Adaptive learning effectiveness metrics
- Post-optimization validation showing enhancement system health

**Use Cases**: Enhancement system tuning, metadata optimization, learning system improvement

---

## 🔧 System Maintenance Workflows

### Workflow 9: Comprehensive System Maintenance

**Scenario**: Regular maintenance including sync, optimization, and health validation.

**Steps**:
```python
# Step 1: Pre-maintenance system status
pre_maintenance = get_system_status(
    status_type="comprehensive",
    format="summary"
)

# Step 2: Force conversation sync for data consistency
sync_results = force_conversation_sync(
    parallel_processing=True
)

# Step 3: Enhanced metadata sync for optimization
metadata_sync = smart_metadata_sync_run()

# Step 4: Unified enhancement for system optimization
enhancement_run = run_unified_enhancement(
    enable_backfill=True,
    enable_optimization=True,
    max_sessions=20
)

# Step 5: Post-maintenance validation
post_maintenance = get_system_status(
    status_type="comprehensive",
    include_analytics=True
)

# Step 6: Generate maintenance report
maintenance_report = {
    "pre_maintenance": pre_maintenance,
    "sync_results": sync_results,
    "metadata_sync": metadata_sync,
    "enhancement_results": enhancement_run,
    "post_maintenance": post_maintenance,
    "improvement_metrics": {
        "search_latency": "post vs pre comparison",
        "metadata_coverage": "coverage improvement",
        "system_health": "health score improvement"
    }
}
```

**Expected Output**:
- Complete maintenance workflow results
- Before/after system health comparison
- Performance improvement metrics
- Comprehensive maintenance report

**Use Cases**: Weekly system maintenance, performance optimization, data consistency validation

---

### Workflow 10: Troubleshooting System Issues

**Scenario**: Diagnosing and resolving system issues with comprehensive analysis.

**Steps**:
```python
# Step 1: System diagnostic analysis
diagnostic_status = get_system_status(
    status_type="health_only",
    include_semantic_health=True,
    format="detailed"
)

# Step 2: Enhanced metadata system analysis
metadata_diagnostic = smart_metadata_sync_status()

# Step 3: Learning system health check
learning_health = get_learning_insights(
    insight_type="validation",
    time_range="24h",
    metric_type="comprehensive"
)

# Step 4: Recovery operations if needed
if diagnostic_status.get("issues_detected"):
    # Force sync for data recovery
    recovery_sync = force_conversation_sync(parallel_processing=True)
    
    # Enhanced metadata recovery
    metadata_recovery = smart_metadata_sync_run()
    
    # System reconfiguration
    recovery_config = configure_enhancement_systems(
        performance_mode="conservative",
        fallback_strategy="graceful",
        degradation_threshold=0.9
    )

# Step 5: Post-recovery validation
post_recovery = get_system_status(
    status_type="comprehensive",
    include_analytics=True
)
```

**Expected Output**:
- Comprehensive system diagnostics with issue identification
- Metadata system health analysis
- Learning system performance metrics
- Recovery operation results (if needed)
- Post-recovery system validation

**Use Cases**: System troubleshooting, issue resolution, disaster recovery

---

## 📈 Learning & Analytics Workflows

### Workflow 11: User Behavior Analysis and Adaptation

**Scenario**: Analyzing user interaction patterns and improving system adaptation.

**Steps**:
```python
# Step 1: Comprehensive learning insights analysis
user_insights = get_learning_insights(
    insight_type="adaptive",
    user_id="current_user",
    metric_type="user_specific",
    time_range="30d"
)

# Step 2: Feedback pattern analysis
feedback_patterns = analyze_patterns_unified(
    feedback_content="Analyzing user feedback patterns over time",
    analysis_type="pattern_similarity",
    pattern_type="positive",
    top_k=15
)

# Step 3: Adaptive learning enhancement
adaptation_results = run_adaptive_learning_enhancement(
    learning_type="user_only",
    cultural_adaptation=True,
    hours=720  # 30 days
)

# Step 4: Cultural intelligence analysis
cultural_analysis = run_adaptive_learning_enhancement(
    learning_type="cultural_only",
    cultural_adaptation=True,
    hours=168  # 1 week
)

# Step 5: Cross-conversation behavioral analysis
behavioral_insights = get_learning_insights(
    insight_type="comprehensive",
    time_range="7d",
    metric_type="performance"
)
```

**Expected Output**:
- User-specific adaptation patterns and preferences
- Positive feedback pattern analysis
- Adaptive learning system effectiveness metrics
- Cultural intelligence insights
- Cross-conversation behavioral trends

**Use Cases**: User experience optimization, personalization improvement, system adaptation tuning

---

### Workflow 12: A/B Testing and Validation Analysis

**Scenario**: Analyzing system enhancement effectiveness through comprehensive validation.

**Steps**:
```python
# Step 1: Baseline system configuration
baseline_config = configure_enhancement_systems(
    enable_prp1=True,
    enable_prp2=False,  # Disable for baseline
    enable_prp3=False,
    performance_mode="conservative"
)

# Step 2: Baseline performance measurement
baseline_search = search_conversations_unified(
    query="test query for baseline measurement",
    limit=5
)

# Step 3: Enhanced system configuration
enhanced_config = configure_enhancement_systems(
    enable_prp1=True,
    enable_prp2=True,   # Enable semantic validation
    enable_prp3=True,   # Enable adaptive learning
    performance_mode="aggressive"
)

# Step 4: Enhanced performance measurement
enhanced_search = search_conversations_unified(
    query="test query for baseline measurement",  # Same query
    limit=5
)

# Step 5: A/B testing insights analysis
ab_insights = get_learning_insights(
    insight_type="ab_testing",
    time_range="1h",
    metric_type="performance"
)

# Step 6: Validation analysis
validation_analysis = get_learning_insights(
    insight_type="validation",
    time_range="24h",
    metric_type="comprehensive"
)
```

**Expected Output**:
- Baseline vs enhanced system performance comparison
- A/B testing effectiveness metrics
- Validation system accuracy improvements
- Enhancement system impact analysis

**Use Cases**: System optimization validation, enhancement effectiveness measurement, performance improvement verification

---

## 🎯 Common Workflow Patterns

### Pattern 1: Search → Analyze → Learn

Many workflows follow this pattern:
1. **Search** for relevant information using `search_conversations_unified`
2. **Analyze** patterns using `analyze_patterns_unified`  
3. **Learn** from results using adaptive learning tools

### Pattern 2: Monitor → Optimize → Validate

System management workflows typically follow:
1. **Monitor** system health using `get_system_status`
2. **Optimize** configuration using `configure_enhancement_systems`
3. **Validate** improvements using performance metrics

### Pattern 3: Detect → Context → Enhance

Project-aware workflows often use:
1. **Detect** current project using `detect_current_project`
2. **Context** gathering using `get_project_context_summary`
3. **Enhance** with project-specific optimization

---

## 🚨 Troubleshooting Common Issues

### Issue 1: Slow Search Performance
```python
# Quick diagnosis
status = get_system_status(status_type="performance", format="summary")
# Look for search_latency > 200ms

# Solution
configure_enhancement_systems(
    performance_mode="aggressive",
    max_search_latency_ms=150,
    chromadb_optimization=True
)
```

### Issue 2: Low Cache Hit Rate
```python
# Check cache effectiveness
insights = get_learning_insights(insight_type="realtime", time_range="1h")
# Look for cache_hit_rate < 0.85

# Solution: Clear search pattern diversity or increase cache size
```

### Issue 3: Enhancement System Issues
```python
# Comprehensive enhancement diagnosis
enhancement_status = run_unified_enhancement(
    enable_validation=True,
    max_sessions=5
)
# Check for field population issues or chain back-fill problems
```

---

## 📋 Workflow Checklists

### Daily Health Check Workflow
- [ ] Run `get_system_status(status_type="health_only")`
- [ ] Check `smart_metadata_sync_status()`
- [ ] Review `get_learning_insights(insight_type="realtime")`
- [ ] Validate search performance < 200ms

### Weekly Maintenance Workflow
- [ ] Run `force_conversation_sync()`
- [ ] Execute `smart_metadata_sync_run()`
- [ ] Perform `run_unified_enhancement()`
- [ ] Analyze `get_learning_insights(time_range="7d")`
- [ ] Review performance trends

### Monthly Optimization Workflow
- [ ] Comprehensive `get_system_status(status_type="comprehensive")`
- [ ] Run `run_adaptive_learning_enhancement(hours=720)`
- [ ] Analyze cross-project patterns
- [ ] Update enhancement system configuration
- [ ] Validate performance improvements

---

**Workflow Examples Complete**: This guide provides 12 comprehensive workflows covering all major use cases for the Claude Code Vector Database System with 14 consolidated MCP tools, including real code examples, expected outputs, and troubleshooting guidance.