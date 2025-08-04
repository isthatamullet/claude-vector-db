# Claude Code Vector Database System

A comprehensive vector database system that provides Claude Code with semantic search capabilities across conversation history, featuring project-aware intelligent filtering and real-time hooks-based indexing.

## 🎯 Overview

This system automatically indexes Claude Code conversation history using **hooks-based real-time indexing** and provides semantic search through **MCP (Model Context Protocol)** integration with intelligent relevance boosting based on:

- **Same-project priority**: Contextual boosting for results from current project
- **Cross-project intelligence**: Technology stack relationship detection
- **Content relevance**: Semantic similarity using all-MiniLM-L6-v2 embeddings
- **Code-aware filtering**: Special handling for conversations containing code
- **Real-time indexing**: Automatic processing via Claude Code hooks

## 🏗️ Architecture

### Current System (July 28, 2025)

- **Hooks-based indexing**: Real-time conversation processing via Claude Code hooks
- **MCP integration**: Direct Claude Code access via Model Context Protocol
- **ChromaDB vector store**: CPU-optimized embeddings with persistent storage
- **Health monitoring**: Comprehensive system status via `get_vector_db_health`

### Technology Stack

- **ChromaDB**: Vector database with built-in CPU-only embeddings (all-MiniLM-L6-v2)
- **FastMCP**: Model Context Protocol server for seamless Claude Code integration
- **sentence-transformers**: CPU-optimized embedding models
- **Python 3.12**: Modern Python with virtual environment isolation

## 🚀 Quick Start

### MCP Integration (Current System)

The vector database operates automatically through **Claude Code's MCP integration**. No manual setup required!

**Available MCP Tools:**
- `search_conversations` - Semantic search across conversation history
- `get_vector_db_health` - Comprehensive system health report
- `detect_current_project` - Auto-detect working directory context
- `get_project_context_summary` - Project-specific conversation analysis
- `force_conversation_sync` - Manual sync for recovery scenarios

### Usage Examples

**Search conversations:**
```bash
# Example: Claude Code automatically uses these tools
# when you ask questions about your codebase
"What did we discuss about React hooks in the tylergohr.com project?"
```

**Check system health:**
```bash
# Use the vector health MCP command
/vector-health
```

**Manual recovery (if needed):**
Use `force_conversation_sync` MCP tool if indexing appears stalled.

## 🔍 MCP Tool Usage

### Automatic Search Integration

Claude Code automatically uses the vector database when you:

```bash
# Ask about previous work
"Show me how we implemented authentication in the invoice-chaser project"

# Reference past solutions  
"What was the solution to the React performance issue we discussed?"

# Cross-project context
"Find discussions about TypeScript interfaces across all projects"
```

### Health Monitoring

```bash
# Get comprehensive system status
/vector-health

# Example health report:
# ✅ Vector DB connectivity: 429ms response time
# ✅ Storage: 20 conversations across 6 projects  
# ✅ Search performance: 397ms (healthy)
# ✅ Hooks indexing: Last indexed 5 minutes ago
# ✅ Index integrity: 100% (10/10 conversations valid)
```

### Project Context Analysis

The system provides intelligent project-aware search results with:
- **Current project boosting** for relevant context
- **Technology stack awareness** across related projects
- **Automatic project detection** based on working directory

## 📊 Data Processing

### Conversation Data Structure

The system processes rich conversation data including:

- **Content**: Cleaned and normalized conversation text
- **Project Context**: Full project path and name
- **Metadata**: Timestamps, session IDs, message types
- **Code Detection**: Automatic identification of code-containing messages
- **Tool Usage**: Extraction of Claude Code tool usage patterns

### Example Processed Entry

```python
ConversationEntry(
    id="bf8134c6_1245_assistant",
    content="Here's how to optimize React component rendering...",
    type="assistant",
    project_path="/home/user/tylergohr.com",
    project_name="tylergohr.com",
    timestamp="2025-07-23T15:30:45.123Z",
    session_id="bf8134c6-c6e1-4bf6-ac2c-492497fcda97",
    file_name="bf8134c6-c6e1-4bf6-ac2c-492497fcda97.jsonl",
    has_code=True,
    tools_used=["Edit", "Read", "Bash"],
    content_length=1247
)
```

## 🧠 Intelligent Filtering

### Project-Aware Relevance Boosting

1. **Same Project**: 50% relevance boost
   ```
   if result.project_name == current_project:
       score *= 1.5
   ```

2. **Related Technology**: 20% boost for technology stack overlap
   ```python
   tech_stacks = {
       "tylergohr.com": {"nextjs", "react", "typescript", "playwright"},
       "invoice-chaser": {"react", "express", "supabase", "socketio"},
       # ... more projects
   }
   ```

3. **Cross-Project Intelligence**: Automatically detects related projects based on technology overlap

### Search Result Ranking

Final relevance score combines:
- **Base Similarity**: Cosine similarity from vector embeddings
- **Project Boost**: 1.0x to 1.5x multiplier based on project relevance  
- **Content Quality**: Length and code content weighting

## 📁 File Structure

```
/home/user/.claude-vector-db/
├── README.md                 # This documentation (updated 2025-07-27)
├── mcp_server.py            # MCP server with hooks-based indexing
├── conversation_extractor.py # JSONL data processing utilities
├── vector_database.py       # ChromaDB implementation
├── chroma_db/              # ChromaDB database files (persistent storage)
├── config/                 # Hook configuration and settings
├── logs/                   # Hooks execution and indexing logs
├── venv/                   # Python virtual environment
├── analytics_simplified.py  # Performance analytics
└── health_dashboard.sh     # System health monitoring
```

## 🔧 Configuration

### Hooks-Based Indexing

The system uses **Claude Code hooks** for automatic indexing:

- **Response indexing**: Triggered after each Claude response
- **Conversation monitoring**: Real-time processing of `.claude/projects/*.jsonl` files  
- **MCP integration**: Direct access via Model Context Protocol
- **Health monitoring**: 10-minute activity threshold for "healthy" status

### Environment Variables

- `CLAUDE_PROJECTS_DIR`: Path to Claude projects directory (default: `/home/user/.claude/projects`)
- `CHROMA_DB_PATH`: Database storage path (default: `/home/user/.claude-vector-db/chroma_db`)
- **No API server required** - operates via MCP hooks

### ChromaDB Settings

- **CPU-Only Operation**: Uses all-MiniLM-L6-v2 via ONNX Runtime
- **Local Deployment**: No external API calls required
- **Privacy-Focused**: Telemetry disabled, all data stays local
- **Persistent Storage**: Data persisted in DuckDB + Parquet format

## 📈 Performance Characteristics

### Benchmarks (Based on Research)

- **Index Building**: ~1,700 entries in 2-3 minutes (CPU-only)
- **Search Latency**: Sub-200ms for typical queries
- **Memory Usage**: ~500MB for 31MB conversation data
- **Storage**: ~2x original data size for vector index

### Scalability

- **Current Capacity**: Tested with 1,700+ conversation entries
- **Estimated Limits**: 50,000+ entries on typical cloud VM
- **Upgrade Path**: Can migrate to Qdrant for enterprise scale

### Resource Requirements

- **CPU**: Single-core sufficient, multi-core beneficial for indexing
- **Memory**: 2GB+ recommended for large conversation histories
- **Storage**: 2-3x original conversation data size
- **Network**: Local-only, no external dependencies

## 🔍 MCP Tool Reference

### Available MCP Tools

#### `search_conversations`
Semantic search across conversation history with project-aware boosting

**Parameters:**
- `query`: Search query (required)
- `project_context`: Current project for relevance boosting (optional)
- `limit`: Number of results (default: 5)
- `include_code_only`: Filter to code-containing conversations (default: false)

**Response:**
```json
{
  "id": "bf8134c6_1245_assistant",
  "content": "The issue with React hooks...",
  "relevance_score": 0.87,
  "base_similarity": 0.58,
  "project_boost": 1.0,
  "rank": 1,
  "type": "assistant",
  "project_name": "tylergohr.com",
  "has_code": true,
  "tools_used": ["Edit", "Read"]
}
```

#### `get_vector_db_health`
Comprehensive system health report

**Returns:**
- Vector DB connectivity and response times
- Storage metrics (conversations, projects tracked)
- Search performance benchmarks
- Hooks indexing status (last activity, health threshold)
- Index integrity scores

#### `detect_current_project`
Auto-detect working directory context

#### `get_project_context_summary`
Project-specific conversation analysis and patterns

#### `force_conversation_sync`
Manual sync for recovery scenarios (processes all conversation files)

## 🛠️ Development

### Testing Current System

```bash
# Test MCP server
cd /home/user/.claude-vector-db
./venv/bin/python mcp_server.py

# Test conversation extraction
./venv/bin/python conversation_extractor.py

# Check system health
./health_dashboard.sh
```

### Monitoring & Debugging

```bash
# View hooks execution logs
tail -f /home/user/.claude-vector-db/logs/response-indexer.log

# Check ChromaDB status
ls -la /home/user/.claude-vector-db/chroma_db/

# Monitor MCP health via Claude Code
/vector-health
```

### System Architecture (2025)

1. **Hooks-based indexing**: Real-time processing via Claude Code response hooks
2. **MCP integration**: Direct tool access without API servers
3. **Health monitoring**: Comprehensive status reporting
4. **Performance analytics**: Built-in timing and effectiveness metrics

## 🔮 Future Enhancements

### Current Status (✅ Completed in 2025)

1. ✅ **Real-time indexing**: Implemented via hooks-based system
2. ✅ **Claude Code integration**: Full MCP implementation
3. ✅ **Health monitoring**: Comprehensive system status
4. ✅ **Project awareness**: Automatic context detection

### Planned Features

1. **Enhanced analytics**: Usage patterns and search optimization
2. **Advanced filters**: Date ranges, conversation types, tool usage patterns
3. **Export/Import**: Database backup and migration tools
4. **Performance optimization**: GPU acceleration for larger datasets

### Upgrade Paths

1. **Qdrant migration**: For enterprise-scale performance (>100k conversations)
2. **Distributed deployment**: Multi-node setup for team environments
3. **Cloud integration**: S3/GCS backup and sync capabilities

## 📝 Research Foundation

This implementation is based on comprehensive research documented in:

- **PRP Document**: `/home/user/AI Orchestrator Platform/PRPs/vector-db/claude-code-vector-db.md`
- **Prototype Findings**: `/home/user/AI Orchestrator Platform/PRPs/vector-db/docs/prototype_findings.md`
- **2025 Vector DB Research**: `/home/user/AI Orchestrator Platform/PRPs/vector-db/research/vector_db_comparison_2025.md`

The system successfully validates all research hypotheses:
- ✅ Rich conversation data suitable for semantic search
- ✅ Project-aware filtering significantly improves relevance
- ✅ CPU-only ChromaDB optimal for single-user development
- ✅ Cross-project intelligence through technology stack detection

## ⚡ Production Status (2025)

The system is **production-ready and actively running** with:

- ✅ **Global installation**: Located at `/home/user/.claude-vector-db/`
- ✅ **MCP integration**: Seamless Claude Code hooks-based indexing
- ✅ **Real-time processing**: Automatic conversation indexing
- ✅ **Health monitoring**: `/vector-health` command integration
- ✅ **Privacy-first**: No external API calls, all data local
- ✅ **Performance optimized**: Sub-500ms search response times

**Current system health**: 6/6 components healthy, 20 conversations indexed across 6 projects.

**Integration complete** - no additional setup required for Claude Code workflows!