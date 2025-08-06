# Semantic Time Search Design Document

**Created**: August 6, 2025  
**Purpose**: Design document for implementing semantic time-based search in Claude Code Vector Database System  
**Status**: Design Phase - Implementation Pending

## Overview

This document outlines the design for transforming the current `search_mode="recent_only"` into a powerful semantic time search system that understands natural language temporal queries and combines them with intelligent content filtering.

## Current State Analysis

### Existing Issues with `recent_only` Mode
- **Broken Implementation**: Calls disabled `get_most_recent_conversation` function
- **Limited Time Windows**: Hardcoded to `recency="today"` instead of pure timestamp sorting
- **Requires Query**: Cannot handle empty queries for pure timestamp searches
- **No Natural Language**: Requires specific parameter combinations

### What Users Actually Need
- **Pure Timestamp Sorting**: "Find the most recent prompt/response" regardless of date
- **Flexible Time Windows**: "Show me what I worked on 2 days ago"
- **Natural Language**: "What did we accomplish earlier today?"
- **Content + Time**: "When did we fix that authentication bug?"

## Proposed Solution: Semantic Time Search

### Core Concept
Replace `search_mode="recent_only"` with `search_mode="time"` that uses semantic understanding to parse temporal intent from natural language queries and combine it with intelligent content filtering.

## Implementation Approaches

### Approach 1: Embedding-Based Time Intent (Recommended)

**Concept**: Use the existing embedding system to understand temporal concepts semantically.

```python
async def semantic_time_search(query: str, db) -> List[Dict[str, Any]]:
    """Semantic understanding of temporal queries"""
    
    # 1. Extract time semantics using embeddings
    time_embedding = embed_time_query(query)
    temporal_concepts = find_similar_time_concepts(time_embedding)
    
    # 2. Dynamic time window calculation
    time_window = calculate_semantic_time_window(query, user_timezone="America/Denver")
    
    # 3. Content semantic search within time window
    results = await db.search_with_time_constraints(
        query=extract_content_intent(query),
        time_window=time_window,
        limit=limit
    )
    
    return results
```

**Benefits**:
- ✅ Leverages existing embedding infrastructure
- ✅ Handles ambiguous time references naturally
- ✅ Scales with the embedding model's understanding
- ✅ No complex rule maintenance required

**Complexity**: Medium (2-3 hours implementation)

### Approach 2: Dynamic Time Context Learning

**Concept**: Learn user's temporal patterns and work habits from conversation history.

```python
# System learns user patterns
user_patterns = {
    "work_hours": "9am-6pm MDT",
    "peak_coding": "10am-12pm, 2pm-5pm", 
    "debugging_sessions": "usually afternoon",
    "weekend_projects": "saturday mornings",
    "time_vocabulary": {
        "earlier": "within last 6 hours",
        "recently": "within last 2 days", 
        "a while back": "1-2 weeks ago"
    }
}
```

**Benefits**:
- ✅ Highly personalized time understanding
- ✅ Adapts to individual work patterns
- ✅ Improves accuracy over time
- ✅ Contextually aware time windows

**Complexity**: High (1-2 days implementation)

### Approach 3: Hybrid Rule-Based + Semantic

**Concept**: Combine regex patterns for common cases with semantic fallback for complex queries.

```python
def parse_temporal_query(query: str) -> Dict[str, Any]:
    """Hybrid time parsing with rules + semantics"""
    
    # Fast path: Common patterns
    if match := re.search(r"most recent (prompt|response)", query.lower()):
        return {"type": "most_recent", "conversation_type": match.group(1)}
    
    if match := re.search(r"(\d+)\s*(hour|day|week)s?\s*ago", query.lower()):
        return {"type": "relative_time", "amount": int(match.group(1)), "unit": match.group(2)}
    
    # Semantic fallback: Complex queries
    return semantic_time_parser(query)
```

**Benefits**:
- ✅ Fast for common queries
- ✅ Flexible for complex queries
- ✅ Easy to debug and extend
- ✅ Predictable performance

**Complexity**: Medium (1-2 hours implementation)

## Recommended Implementation: Approach 1 (Embedding-Based)

**Why This Approach**:
1. **Leverages Existing Infrastructure**: Uses the same embedding model (all-MiniLM-L6-v2) already in the system
2. **Natural Scalability**: As the model improves, time understanding improves
3. **Minimal Maintenance**: No complex rule sets to maintain
4. **Proven Architecture**: Similar to how semantic content search already works

### Implementation Plan

#### Phase 1: Basic Migration (30 minutes)
```python
# 1. Rename search mode
"recent_only" → "time"

# 2. Fix broken _recent_search_implementation 
# 3. Enable pure timestamp sorting for queries like "*" or "recent"
```

#### Phase 2: Semantic Time Parsing (2-3 hours)
```python
# 1. Time concept embedding database
time_concepts = {
    "most_recent": ["latest", "newest", "most recent", "last"],
    "today": ["today", "this morning", "this afternoon", "earlier today"],
    "yesterday": ["yesterday", "last night", "yesterday morning"],
    "relative_past": ["ago", "back", "earlier", "before"],  
    "time_periods": ["hour", "day", "week", "month"]
}

# 2. Semantic time window calculator
def calculate_semantic_time_window(query: str, user_timezone: str) -> Dict[str, Any]:
    """Calculate time window from semantic understanding"""
    
    # Extract temporal concepts using embeddings
    query_embedding = encode_time_query(query)
    
    # Find closest time concepts
    time_matches = find_similar_concepts(query_embedding, time_concepts)
    
    # Calculate actual time window
    if "most_recent" in time_matches:
        return {"type": "pure_timestamp", "sort": "desc", "limit": 1}
    
    if "today" in time_matches:
        return calculate_today_window(user_timezone)
    
    if "relative_past" in time_matches:
        return calculate_relative_window(query, user_timezone)
    
    # Default: last 24 hours
    return calculate_default_recent_window(user_timezone)
```

#### Phase 3: Advanced Features (Optional - 1-2 hours)
```python
# 1. Context-aware time resolution
# 2. User pattern learning
# 3. Project timeline awareness
# 4. Time-based analytics
```

## Example Query Transformations

### Pure Timestamp Queries
| Query | Current Behavior | New Behavior |
|-------|------------------|--------------|
| `"*"` | Broken (no results) | Most recent entry by timestamp |
| `"recent"` | Broken (no results) | Most recent 5 entries |
| `"most recent prompt"` | Not supported | Most recent user message |
| `"latest response"` | Not supported | Most recent assistant message |

### Time Window Queries
| Query | Semantic Understanding | Time Window |
|-------|----------------------|-------------|
| `"earlier today"` | Today + before current time | 2025-08-06 00:00 to now (MDT) |
| `"yesterday's work"` | Previous day + work context | 2025-08-05 00:00-23:59 (MDT) |
| `"2 days ago"` | Relative past calculation | 2025-08-04 00:00-23:59 (MDT) |
| `"last week"` | Previous week period | 2025-07-30 to 2025-08-05 |

### Content + Time Queries
| Query | Temporal Component | Content Component | Result |
|-------|-------------------|-------------------|---------|
| `"debugging this morning"` | This morning (6am-12pm) | Debugging activities | Debug entries from morning |
| `"React work yesterday"` | Yesterday full day | React-related content | React entries from Aug 5 |
| `"when did we fix auth?"` | Flexible recent window | Authentication + solution | Auth solutions with timestamps |

## Technical Architecture

### Core Components

#### 1. Semantic Time Parser
```python
class SemanticTimeParser:
    def __init__(self, embedding_model):
        self.model = embedding_model
        self.time_concept_db = self._build_time_concepts()
    
    async def parse_temporal_intent(self, query: str) -> TimeIntent:
        """Extract temporal intent from natural language"""
        pass
    
    def calculate_time_window(self, intent: TimeIntent, user_tz: str) -> TimeWindow:
        """Convert semantic intent to actual time constraints"""
        pass
```

#### 2. Time-Constrained Search Engine
```python
class TimeConstrainedSearch:
    async def search_with_time_window(self, 
                                    content_query: str,
                                    time_window: TimeWindow,
                                    db: ClaudeVectorDatabase) -> List[Dict]:
        """Combine semantic content search with time filtering"""
        
        # 1. Apply time constraints to database query
        time_filter = self._build_timestamp_filter(time_window)
        
        # 2. Semantic search within time-constrained results
        if content_query:
            results = await db.search_with_constraints(content_query, time_filter)
        else:
            # Pure timestamp sorting
            results = await db.get_by_timestamp(time_filter)
        
        return results
```

#### 3. Time Window Calculator
```python
@dataclass
class TimeWindow:
    start_unix: Optional[float]
    end_unix: Optional[float]
    sort_order: str = "desc"  # "desc" for most recent first
    type: str = "range"  # "range", "pure_timestamp", "relative"

class TimeWindowCalculator:
    def __init__(self, user_timezone: str = "America/Denver"):
        self.user_tz = pytz.timezone(user_timezone)
    
    def calculate_today(self) -> TimeWindow:
        """Calculate today's time window in user timezone"""
        pass
    
    def calculate_relative(self, amount: int, unit: str) -> TimeWindow:
        """Calculate relative time window (e.g., 2 days ago)"""
        pass
    
    def calculate_pure_timestamp(self, limit: int = 1) -> TimeWindow:
        """Pure timestamp sorting without time constraints"""
        pass
```

## Performance Considerations

### Optimization Strategies
1. **Time Concept Caching**: Cache computed time windows for common queries
2. **Index Utilization**: Ensure `timestamp_unix` field is properly indexed
3. **Query Simplification**: Use pure timestamp sorts when no content filtering needed
4. **Batch Processing**: Group similar time window calculations

### Expected Performance
- **Pure Timestamp Queries**: <50ms (direct database sort)
- **Recent Time Windows**: <200ms (time filter + semantic search)
- **Complex Semantic Parsing**: <500ms (embedding computation + search)

## Migration Path

### Step 1: Immediate Fix (5 minutes)
```python
# In mcp_server.py, line 965:
elif search_mode == "time":  # Renamed from "recent_only"
    # Fix broken implementation
    results = await _pure_timestamp_search(
        query=query,
        project_context=project_context,
        limit=limit,
        db=db
    )
```

### Step 2: Semantic Enhancement (2-3 hours)
- Implement `SemanticTimeParser`
- Add time concept embedding database
- Integrate with existing search pipeline

### Step 3: Advanced Features (Optional)
- User pattern learning
- Context-aware time resolution
- Time-based analytics

## Testing Strategy

### Unit Tests
```python
def test_semantic_time_parsing():
    parser = SemanticTimeParser()
    
    # Test pure timestamp queries
    assert parser.parse("most recent") == TimeIntent(type="pure_timestamp")
    assert parser.parse("latest prompt") == TimeIntent(type="pure_timestamp", filter="user")
    
    # Test relative time queries
    assert parser.parse("2 days ago") == TimeIntent(type="relative", amount=2, unit="days")
    
    # Test natural language queries
    assert parser.parse("earlier today") == TimeIntent(type="today", modifier="before_now")
```

### Integration Tests
```python
async def test_time_search_integration():
    # Test pure timestamp search
    results = await search_conversations_unified("*", search_mode="time", limit=1)
    assert len(results) == 1
    assert results[0]["timestamp_unix"] == max_timestamp_in_db
    
    # Test content + time search
    results = await search_conversations_unified("debugging yesterday", search_mode="time")
    assert all("debug" in r["content"].lower() for r in results)
    assert all(is_yesterday(r["timestamp"]) for r in results)
```

## Documentation Updates Required

### Files to Update
1. **README.md**: Update search mode documentation
2. **docs/TOOL_REFERENCE_GUIDE.md**: Update `search_conversations_unified` examples
3. **docs/WORKFLOW_EXAMPLES.md**: Add time-based search examples
4. **docs/MIGRATION_GUIDE.md**: Document `recent_only` → `time` migration

### Example Documentation
```markdown
## Time-Based Search (`search_mode="time"`)

Natural language temporal queries with semantic understanding:

### Pure Timestamp Queries
```python
# Find most recent conversation
search_conversations_unified("*", search_mode="time", limit=1)

# Find most recent user prompt
search_conversations_unified("most recent prompt", search_mode="time")

# Find latest Claude response
search_conversations_unified("latest response", search_mode="time")
```

### Time Window Queries
```python
# Natural language time references
search_conversations_unified("earlier today", search_mode="time")
search_conversations_unified("yesterday's work", search_mode="time")
search_conversations_unified("2 days ago", search_mode="time")
```

### Content + Time Queries
```python
# Combine content search with time filtering
search_conversations_unified("debugging this morning", search_mode="time")
search_conversations_unified("React work last week", search_mode="time")
search_conversations_unified("when did we fix authentication?", search_mode="time")
```
```

## Future Enhancements

### Phase 4: Advanced Semantic Features
1. **Project Timeline Awareness**: "when did we start the tylergohr.com project?"
2. **Session Context**: "earlier in this conversation"
3. **Work Pattern Learning**: "during my usual debugging time"
4. **Collaborative Context**: "when we were working on that together"

### Phase 5: Time-Based Analytics
1. **Topic Trends**: "what topics did I work on most last week?"
2. **Productivity Patterns**: "when am I most productive?"
3. **Problem Resolution Time**: "how long did it take to solve X?"
4. **Learning Progression**: "show my learning progress on React"

## Implementation Priority

**Immediate (This Session)**:
- [x] Document design (this file)
- [ ] Rename `recent_only` → `time` 
- [ ] Fix broken `_recent_search_implementation`

**Next Session**:
- [ ] Implement `SemanticTimeParser`
- [ ] Add time concept embedding database
- [ ] Test pure timestamp and basic time window queries

**Future Sessions**:
- [ ] Advanced semantic features
- [ ] User pattern learning
- [ ] Time-based analytics integration

---

**Status**: Ready for implementation  
**Estimated Total Implementation Time**: 3-4 hours for full semantic capabilities  
**Immediate Quick Fix**: 30 minutes to restore basic functionality