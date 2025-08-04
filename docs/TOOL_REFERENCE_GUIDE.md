# MCP Tool Reference Guide

Complete parameter reference for all 14 consolidated MCP tools in the Claude Code Vector Database System.

## Overview

This guide provides comprehensive documentation for all MCP tools following the PRP-3 consolidation that achieved a 64.1% reduction (39→14 tools). Each tool includes detailed parameter specifications, usage examples, and integration patterns.

**System Status**: **14 active MCP tools** (August 2025) after PRP-3 consolidation phase

## Tool Categories

### 🔍 Search & Retrieval Tools (1 tool)
- `search_conversations_unified` - Unified semantic search with mode-based routing

### 📊 Context & Project Management (3 tools)
- `get_project_context_summary` - Project-specific conversation analysis
- `detect_current_project` - Auto-detect working directory context
- `get_conversation_context_chain` - Detailed conversation flow analysis

### 🔄 Data Processing & Sync Tools (3 tools)
- `force_conversation_sync` - Manual recovery sync for all conversation files
- `smart_metadata_sync_status` - Enhanced metadata statistics
- `smart_metadata_sync_run` - Intelligent selective enhancement sync

### 📈 Analytics & Learning Tools (2 tools)
- `get_learning_insights` - Unified learning analytics across all systems
- `process_feedback_unified` - Unified feedback processing with adaptive learning

### ⚙️ Enhancement System Management (3 tools)
- `run_unified_enhancement` - Main orchestrator for all enhancement systems
- `get_system_status` - Comprehensive system status with unified analytics
- `configure_enhancement_systems` - Real-time enhancement configuration

### 🧠 Pattern Analysis & Adaptive Learning (2 tools)
- `analyze_patterns_unified` - Unified pattern analysis across all methods
- `run_adaptive_learning_enhancement` - Personalized user adaptation system

---

## Detailed Tool Documentation

### 1. search_conversations_unified

**UNIFIED SEARCH TOOL** - PRP-3 Consolidation (8 Search Tools → 1)

Main entry point for the July 2025 MCP Integration Enhancement System, providing unified access to all search capabilities with progressive enhancement.

#### Parameters:

**Core Parameters:**
- `query` *(str, required)*: Search query for semantic matching
- `project_context` *(Optional[str], default: None)*: Optional project name for relevance boosting
- `limit` *(int, default: 5)*: Maximum number of results to return

**Core Search Controls:**
- `search_mode` *(str, default: "semantic")*: Search behavior mode
  - Options: "semantic", "validated_only", "failed_only", "recent_only", "by_topic"
- `topic_focus` *(Optional[str], default: None)*: Required when search_mode="by_topic"
  - Examples: "debugging", "performance", "authentication"

**Enhancement Controls:**
- `use_validation_boost` *(bool, default: True)*: Apply validation learning boost
- `use_adaptive_learning` *(bool, default: True)*: Enable adaptive user learning
- `include_context_chains` *(bool, default: False)*: Include conversation context chains

**Filter Controls:**
- `include_code_only` *(bool, default: False)*: Filter to only conversations containing code
- `validation_preference` *(str, default: "neutral")*: "validated_only", "include_failures", or "neutral"
- `prefer_solutions` *(bool, default: False)*: Boost high-quality solution content
- `troubleshooting_mode` *(bool, default: False)*: Enhanced relevance for error-solving contexts

**Time Controls:**
- `date_range` *(Optional[str], default: None)*: Date range filter as "start_date,end_date"
  - Example: "2025-07-26,2025-07-27"
- `recency` *(Optional[str], default: None)*: Recent time filter
  - Options: "last_hour", "today", "last_3_days", "this_week"

**Advanced Controls:**
- `show_context_chain` *(bool, default: False)*: Include conversation context chain
- `use_enhanced_search` *(bool, default: True)*: Use enhanced multi-factor relevance scoring
- `min_validation_strength` *(float, default: 0.3)*: Minimum validation strength threshold
- `chain_length` *(int, default: 3)*: Length of context chain for each result

**Legacy Enhancement Controls:**
- `use_conversation_chains` *(bool, default: True)*: Enable PRP-1 conversation chain integration
- `use_semantic_enhancement` *(bool, default: True)*: Enable PRP-2 semantic validation
- `user_id` *(Optional[str], default: None)*: User identifier for personalization
- `oauth_token` *(Optional[str], default: None)*: OAuth 2.1 token for enterprise security
- `enhancement_preference` *(str, default: "auto")*: Enhancement aggressiveness level
- `include_analytics` *(bool, default: False)*: Include analytics metadata in results

#### Usage Examples:

```python
# Basic semantic search
search_conversations_unified(
    query="React component optimization",
    project_context="tylergohr.com"
)

# Search for validated solutions only
search_conversations_unified(
    query="database connection pooling",
    search_mode="validated_only",
    use_validation_boost=True
)

# Topic-specific search with context chains
search_conversations_unified(
    query="performance issues",
    search_mode="by_topic",
    topic_focus="performance",
    include_context_chains=True,
    chain_length=5
)

# Recent conversations only
search_conversations_unified(
    query="latest updates",
    search_mode="recent_only",
    recency="last_3_days"
)
```

---

### 2. get_project_context_summary

Generate comprehensive project context summary with recent activities, patterns, and insights.

#### Parameters:
- `project_name` *(Optional[str], default: None)*: Target project (auto-detected if not provided)
- `days_back` *(int, default: 30)*: Number of days of history to analyze

#### Usage Examples:

```python
# Auto-detect current project
get_project_context_summary()

# Specific project with custom timeframe
get_project_context_summary(
    project_name="tylergohr.com",
    days_back=14
)
```

---

### 3. detect_current_project

Detect the current project based on working directory with confidence scoring.

#### Parameters:
None

#### Returns:
Project detection information including name, path, and confidence

#### Usage Examples:

```python
# Simple project detection
detect_current_project()
```

---

### 4. force_conversation_sync

Smart Force Sync with Unified Processor and Pre-Indexing Checks. Uses UnifiedEnhancementProcessor with smart file detection to skip already-indexed files for ~90% performance improvement.

#### Parameters:
- `parallel_processing` *(bool, default: True)*: Enable parallel processing for faster sync

#### Usage Examples:

```python
# Standard parallel sync
force_conversation_sync()

# Sequential processing (for debugging)
force_conversation_sync(parallel_processing=False)
```

---

### 5. smart_metadata_sync_status

Check current enhanced metadata status of the database. Provides detailed analysis of which entries have complete enhanced metadata and which files need selective enhancement processing.

#### Parameters:
None

#### Usage Examples:

```python
# Check metadata coverage status
smart_metadata_sync_status()
```

---

### 6. smart_metadata_sync_run

Run intelligent selective enhanced metadata sync. Efficiently processes only entries that are missing enhanced metadata, avoiding full database rebuilds.

#### Parameters:
- `target_files` *(Optional[List[str]], default: None)*: Optional list of specific JSONL files to process

#### Usage Examples:

```python
# Process all files needing enhancement
smart_metadata_sync_run()

# Process specific files only
smart_metadata_sync_run(
    target_files=["session1.jsonl", "session2.jsonl"]
)
```

---

### 7. get_learning_insights

**UNIFIED LEARNING INSIGHTS TOOL** - PRP-3 Consolidation (4 Learning Tools → 1)

Replaces and consolidates all learning analytics functionality: validation, adaptive, ab_testing, and realtime insights.

#### Parameters:
- `insight_type` *(str, default: "comprehensive")*: Type of learning insights
  - Options: "validation", "adaptive", "ab_testing", "realtime", "comprehensive"
- `user_id` *(Optional[str], default: None)*: Optional user identifier for personalized insights
- `metric_type` *(str, default: "comprehensive")*: Type of metrics
  - Options: "performance", "user_specific", "comprehensive"
- `time_range` *(str, default: "24h")*: Time range for analysis
  - Options: "1h", "24h", "7d", "30d"

#### Usage Examples:

```python
# Comprehensive learning insights
get_learning_insights(
    insight_type="comprehensive",
    time_range="7d"
)

# User-specific adaptive learning metrics
get_learning_insights(
    insight_type="adaptive",
    user_id="user_123",
    metric_type="user_specific"
)

# Recent validation insights
get_learning_insights(
    insight_type="validation",
    time_range="1h"
)
```

---

### 8. process_feedback_unified

**UNIFIED FEEDBACK PROCESSING TOOL** - PRP-3 Consolidation (2 Feedback Tools → 1)

Replaces and consolidates all feedback processing functionality with comprehensive adaptive learning enhancements.

#### Parameters:

**Core Parameters:**
- `feedback_text` *(str, required)*: User's feedback text
- `solution_context` *(Dict[str, Any], required)*: Context about the solution that was provided

**Processing Mode Controls:**
- `processing_mode` *(str, default: "adaptive")*: Processing type
  - Options: "basic", "adaptive", "semantic_only", "multimodal"

**User Context:**
- `user_id` *(Optional[str], default: None)*: Optional user identifier for personalization
- `cultural_profile` *(Optional[Dict[str, Any]], default: None)*: Optional cultural profile

**Enhancement Controls:**
- `enable_user_adaptation` *(bool, default: True)*: Enable individual user communication learning
- `enable_cultural_intelligence` *(bool, default: True)*: Enable cultural communication adaptation
- `enable_cross_conversation_analysis` *(bool, default: True)*: Enable behavioral pattern analysis

**Legacy Compatibility:**
- `solution_id` *(Optional[str], default: None)*: For compatibility - unique identifier for the solution
- `solution_content` *(Optional[str], default: None)*: For compatibility - solution content that was provided

#### Usage Examples:

```python
# Full adaptive feedback processing
process_feedback_unified(
    feedback_text="This solution worked perfectly!",
    solution_context={"tool_used": "Edit", "file_modified": "src/components/Hero.tsx"},
    processing_mode="adaptive",
    user_id="user_123"
)

# Basic feedback processing
process_feedback_unified(
    feedback_text="The fix didn't work",
    solution_context={"issue": "build error", "attempted_fix": "dependency update"},
    processing_mode="basic"
)

# Cultural intelligence enabled
process_feedback_unified(
    feedback_text="Thank you, this helps",
    solution_context={"solution_type": "code_optimization"},
    cultural_profile={"language": "en", "communication_style": "formal"},
    enable_cultural_intelligence=True
)
```

---

### 9. get_conversation_context_chain

Get detailed conversation context chain around a specific message. Shows conversation flow, solution-feedback relationships, validation status, and adjacency relationships for enhanced context understanding.

#### Parameters:
- `message_id` *(str, required)*: ID of the message to build context chain around
- `chain_length` *(int, default: 5)*: Number of messages in each direction from anchor
- `show_relationships` *(bool, default: True)*: Whether to include detailed relationship analysis

#### Usage Examples:

```python
# Standard context chain
get_conversation_context_chain(
    message_id="bf8134c6_1245_assistant"
)

# Extended context with relationships
get_conversation_context_chain(
    message_id="bf8134c6_1245_assistant",
    chain_length=10,
    show_relationships=True
)
```

---

### 10. run_unified_enhancement

✅ **WORKING** - Run the unified enhancement system for conversation chain back-fill and metadata optimization. This tool successfully resolved the critical conversation chain population issue (0.97% → 99.675%) and systematically optimizes all 30+ metadata fields with performance guarantees.

#### Parameters:
- `session_id` *(Optional[str], default: None)*: Specific session to process (auto-detects recent sessions if None)
- `enable_backfill` *(bool, default: True)*: Enable conversation chain back-fill (addresses 0.97% issue)
- `enable_optimization` *(bool, default: True)*: Enable field population optimization
- `enable_validation` *(bool, default: True)*: Enable validation and health assessment
- `max_sessions` *(int, default: 0)*: Maximum number of sessions to process if session_id is None (0 = no limit, processes all remaining sessions)

#### Usage Examples:

```python
# Full enhancement of all remaining sessions (recommended)
run_unified_enhancement()

# Process specific session with all enhancements
run_unified_enhancement(
    session_id="bf8134c6-c6e1-4bf6-ac2c-492497fcda97",
    enable_backfill=True,
    enable_optimization=True
)

# Back-fill only for specific number of sessions
run_unified_enhancement(
    enable_backfill=True,
    enable_optimization=False,
    max_sessions=5
)
```

---

### 11. get_system_status

**UNIFIED SYSTEM STATUS TOOL** - PRP-3 Consolidation (3 Analytics Tools → 1)

Replaces and consolidates all system status functionality: health_only, analytics_only, and comprehensive status reports.

#### Parameters:
- `status_type` *(str, default: "comprehensive")*: Type of status report
  - Options: "basic", "comprehensive", "performance", "health_only", "analytics_only", "semantic_only"
- `include_analytics` *(bool, default: True)*: Include analytics dashboard data
- `include_enhancement_metrics` *(bool, default: True)*: Include enhancement system metrics
- `include_semantic_health` *(bool, default: True)*: Include semantic validation health
- `format` *(str, default: "detailed")*: Output format
  - Options: "detailed", "summary", "metrics_only"

#### Usage Examples:

```python
# Full comprehensive status
get_system_status(status_type="comprehensive")

# Quick health check only
get_system_status(
    status_type="health_only",
    format="summary"
)

# Performance metrics focus
get_system_status(
    status_type="performance",
    include_analytics=True,
    format="metrics_only"
)

# Analytics dashboard data
get_system_status(
    status_type="analytics_only",
    include_enhancement_metrics=True
)
```

---

### 12. configure_enhancement_systems

Real-time configuration management for enhancement systems. Provides unified interface for configuring all enhancement components following July 2025 MCP standards with OAuth 2.1 compliance and ChromaDB 1.0.15 optimizations.

#### Parameters:

**PRP System Controls:**
- `enable_prp1` *(bool, default: True)*: Enable PRP-1 conversation chains enhancement
- `enable_prp2` *(bool, default: True)*: Enable PRP-2 semantic validation enhancement
- `enable_prp3` *(bool, default: False)*: Enable PRP-3 adaptive learning enhancement (opt-in)

**Performance Controls:**
- `performance_mode` *(str, default: "balanced")*: Performance mode
  - Options: "conservative", "balanced", "aggressive"
- `fallback_strategy` *(str, default: "graceful")*: Fallback strategy
  - Options: "graceful", "strict", "disabled"

**Security & Optimization:**
- `oauth_enforcement` *(bool, default: True)*: Enable OAuth 2.1 security enforcement
- `chromadb_optimization` *(bool, default: True)*: Enable ChromaDB 1.0.15 Rust optimizations

**Fine-Tuning:**
- `enhancement_aggressiveness` *(float, default: 1.0)*: Enhancement multiplier (0.5-2.0)
- `degradation_threshold` *(float, default: 0.8)*: Quality threshold for degradation (0.1-1.0)
- `max_search_latency_ms` *(int, default: 2000)*: Maximum acceptable search latency in milliseconds

#### Constraints:
- `enhancement_aggressiveness` must be between 0.5 and 2.0
- `degradation_threshold` must be between 0.1 and 1.0
- `max_search_latency_ms` must be positive integer

#### Usage Examples:

```python
# Enable all PRP systems with aggressive performance
configure_enhancement_systems(
    enable_prp1=True,
    enable_prp2=True,
    enable_prp3=True,
    performance_mode="aggressive",
    enhancement_aggressiveness=1.5
)

# Conservative configuration for production
configure_enhancement_systems(
    performance_mode="conservative",
    fallback_strategy="graceful",
    enhancement_aggressiveness=0.8,
    max_search_latency_ms=1000
)

# Security-focused configuration
configure_enhancement_systems(
    oauth_enforcement=True,
    fallback_strategy="strict",
    degradation_threshold=0.9
)
```

---

### 13. analyze_patterns_unified

**UNIFIED PATTERN ANALYSIS TOOL** - PRP-3 Consolidation (4 Analysis Tools → 1)

Replaces and consolidates all pattern analysis functionality: semantic, technical, multimodal, and pattern similarity analysis.

#### Parameters:

**Core Parameters:**
- `feedback_content` *(str, required)*: Feedback text to analyze
- `analysis_type` *(str, default: "multimodal")*: Type of analysis
  - Options: "semantic", "technical", "multimodal", "pattern_similarity"

**Context Parameters:**
- `context` *(Optional[Dict[str, Any]], default: None)*: Optional solution context for enhanced analysis
- `solution_context` *(Optional[Dict[str, Any]], default: None)*: Optional solution metadata (for technical analysis)

**Pattern Similarity Controls:**
- `pattern_type` *(Optional[str], default: None)*: For pattern_similarity mode
  - Options: "positive", "negative", "partial"
- `top_k` *(int, default: 5)*: Number of top matches to return (for pattern similarity)

**Analysis Options:**
- `analysis_options` *(Optional[Dict[str, Any]], default: None)*: Optional analysis configuration

#### Constraints:
- `pattern_type` is required when `analysis_type` is "pattern_similarity"
- `top_k` must be positive integer

#### Usage Examples:

```python
# Multimodal analysis (default)
analyze_patterns_unified(
    feedback_content="This solution is great but needs optimization",
    analysis_type="multimodal",
    solution_context={"type": "performance_fix", "language": "typescript"}
)

# Semantic analysis only
analyze_patterns_unified(
    feedback_content="The fix worked perfectly!",
    analysis_type="semantic",
    context={"user_sentiment": "positive"}
)

# Technical context analysis
analyze_patterns_unified(
    feedback_content="Build failed after the change",
    analysis_type="technical",
    solution_context={"build_system": "vite", "error_type": "dependency"}
)

# Pattern similarity search
analyze_patterns_unified(
    feedback_content="Thanks, this helped solve the issue",
    analysis_type="pattern_similarity",
    pattern_type="positive",
    top_k=10
)
```

---

### 14. run_adaptive_learning_enhancement

Run adaptive learning enhancement on user feedback and validation data. This is the main entry point for the adaptive learning system, providing personalized user adaptation, cultural intelligence, and cross-conversation behavioral analysis to achieve 92% → 96% validation accuracy improvement.

#### Parameters:
- `user_id` *(Optional[str], default: None)*: Optional user identifier for personalized adaptation
- `session_id` *(Optional[str], default: None)*: Optional session identifier for session-specific analysis
- `cultural_adaptation` *(bool, default: True)*: Enable cultural intelligence adaptation
- `learning_type` *(str, default: "comprehensive")*: Type of learning
  - Options: "comprehensive", "user_only", "cultural_only"
- `hours` *(int, default: 24)*: Hours of recent activity to analyze

#### Constraints:
- `hours` must be positive integer
- `learning_type` must be one of: "comprehensive", "user_only", "cultural_only"

#### Usage Examples:

```python
# Comprehensive adaptive learning
run_adaptive_learning_enhancement()

# User-specific learning with extended timeframe
run_adaptive_learning_enhancement(
    user_id="user_123",
    learning_type="user_only",
    hours=168  # 1 week
)

# Cultural adaptation focus
run_adaptive_learning_enhancement(
    learning_type="cultural_only",
    cultural_adaptation=True,
    hours=72  # 3 days
)

# Session-specific analysis
run_adaptive_learning_enhancement(
    session_id="bf8134c6-c6e1-4bf6-ac2c-492497fcda97",
    learning_type="comprehensive"
)
```

---

## Tool Migration Reference

### Consolidated Tools (PRP-3 Phase)
The following legacy tools have been consolidated into the unified tools above:

**Search Consolidation (8 → 1):**
- `search_conversations` → `search_conversations_unified(search_mode="semantic")`
- `search_validated_solutions` → `search_conversations_unified(search_mode="validated_only")`
- `search_failed_attempts` → `search_conversations_unified(search_mode="failed_only")`
- `search_by_topic` → `search_conversations_unified(search_mode="by_topic", topic_focus="topic")`
- `get_most_recent_conversation` → `search_conversations_unified(search_mode="recent_only")`
- `search_with_validation_boost` → `search_conversations_unified(use_validation_boost=True)`
- `search_with_context_chains` → `search_conversations_unified(include_context_chains=True)`

**Analytics Consolidation (4 → 2):**
- `get_validation_learning_insights` → `get_learning_insights(insight_type="validation")`
- `get_adaptive_learning_insights` → `get_learning_insights(insight_type="adaptive")`
- `get_ab_testing_insights` → `get_learning_insights(insight_type="ab_testing")`
- `get_realtime_learning_insights` → `get_learning_insights(insight_type="realtime")`

**System Status Consolidation (3 → 1):**
- `get_system_health_report` → `get_system_status(status_type="health_only")`
- `get_enhancement_analytics_dashboard` → `get_system_status(status_type="analytics_only")`
- `get_semantic_validation_health` → `get_system_status(status_type="semantic_only")`

**Feedback Processing Consolidation (2 → 1):**
- `process_validation_feedback` → `process_feedback_unified(processing_mode="basic")`
- `process_adaptive_validation_feedback` → `process_feedback_unified(processing_mode="adaptive")`

**Pattern Analysis Consolidation (4 → 1):**
- `analyze_semantic_feedback` → `analyze_patterns_unified(analysis_type="semantic")`
- `analyze_technical_context` → `analyze_patterns_unified(analysis_type="technical")`
- `run_multimodal_feedback_analysis` → `analyze_patterns_unified(analysis_type="multimodal")`
- `get_semantic_pattern_similarity` → `analyze_patterns_unified(analysis_type="pattern_similarity")`

### Disabled Tools
- `get_vector_db_health` → Use `get_system_status(status_type="health_only")` (comprehensive replacement)
- `get_enhanced_statistics` → Use `smart_metadata_sync_status` (working replacement)
- `get_file_watcher_status` → No replacement needed (hooks-based indexing active)

---

## Performance Characteristics

### Tool Response Time Targets
- **Search Tools**: <200ms (`search_conversations_unified`)
- **Health Checks**: <2000ms (`get_system_status`)
- **Enhancement Operations**: <500ms (`run_unified_enhancement`)
- **Analytics**: <1000ms (`get_learning_insights`)
- **Feedback Processing**: <300ms (`process_feedback_unified`)

### Cache Performance
- **Cache Hit Target**: 85%
- **Repeated Query Improvement**: 100x performance boost
- **Memory Usage**: <500MB for 31MB conversation data

### Error Handling
- **Error Rate Target**: <1%
- **Graceful Degradation**: All tools support fallback modes
- **Recovery Guidance**: Enhanced error messages with actionable recovery steps

---

This comprehensive reference covers all 14 active MCP tools with complete parameter specifications, usage examples, migration mappings, and performance characteristics for the Claude Code Vector Database System as of August 2025.