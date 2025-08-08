# Vector Database MCP Tools - CLI UI Implementation Plan

## Overview

This plan outlines how to enhance your vector database MCP tools with interactive CLI interfaces using React Ink, providing users with real-time progress bars, status updates, and rich visual feedback during operations.

## Architecture Approach

### Dual-Mode Operation
Your MCP tools will support both modes:
- **Standard Mode**: Current JSON response format (for existing integrations)
- **Interactive Mode**: Enhanced CLI UI with progress bars and real-time updates

### Implementation Strategy
1. **Progressive Enhancement**: Add UI layer without breaking existing functionality
2. **Optional Dependencies**: Ink components only loaded when needed
3. **Environment Detection**: Auto-detect if running in interactive terminal vs programmatic context
4. **Graceful Fallback**: Fall back to standard output if UI components fail

## Technical Implementation

### 1. Package Setup

```bash
# In your vector DB directory
cd /home/user/.claude-vector-db-enhanced
npm init -y
npm install ink react ink-progress-bar ink-spinner ink-table ink-text-input
npm install --save-dev @babel/preset-react
```

### 2. Core UI Components

Create `ui/` directory with reusable components:

```
ui/
├── components/
│   ├── ProgressBar.tsx          # Reusable progress bar
│   ├── StatusIndicator.tsx      # Health status indicators  
│   ├── SearchResults.tsx        # Formatted search results
│   ├── StatsPanel.tsx          # Statistics display
│   └── FileProcessor.tsx       # File processing UI
├── hooks/
│   ├── useProgress.ts          # Progress state management
│   ├── useRealTimeStats.ts     # Live statistics
│   └── useInteractiveMode.ts   # Mode detection
└── utils/
    ├── formatting.ts           # Text formatting utilities
    └── colors.ts              # Color schemes
```

### 3. Enhanced MCP Tools

#### A. search_conversations_unified
```typescript
// Enhanced with progress tracking
async function search_conversations_unified(params) {
  const isInteractive = detectInteractiveMode();
  
  if (isInteractive) {
    return renderSearchUI({
      query: params.query,
      project_context: params.project_context,
      onProgress: (phase, progress) => {
        // Real-time progress updates
      },
      onComplete: (results, stats) => {
        // Final results display
      }
    });
  } else {
    // Standard JSON response
    return await performSearch(params);
  }
}
```

#### B. force_conversation_sync
```typescript
// Enhanced with file processing UI
async function force_conversation_sync(params) {
  const isInteractive = detectInteractiveMode();
  
  if (isInteractive) {
    return renderSyncUI({
      onFileStart: (filename) => {
        // Show current file
      },
      onFileComplete: (filename, stats) => {
        // Update progress and stats
      },
      onComplete: (totalStats) => {
        // Final completion display
      }
    });
  } else {
    return await performSync(params);
  }
}
```

#### C. get_system_status
```typescript
// Enhanced with dashboard UI
async function get_system_status(params) {
  const isInteractive = detectInteractiveMode();
  
  if (isInteractive) {
    return renderHealthDashboard({
      refreshInterval: 5000, // Update every 5 seconds
      metrics: await gatherSystemMetrics(),
      onRefresh: () => {
        // Live updates
      }
    });
  } else {
    return await gatherSystemMetrics();
  }
}
```

### 4. UI Component Examples

#### Progress Bar Component
```tsx
import React from 'react';
import { Box, Text } from 'ink';

interface ProgressBarProps {
  current: number;
  total: number;
  label?: string;
  color?: string;
  width?: number;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  current,
  total,
  label,
  color = 'cyan',
  width = 40
}) => {
  const percentage = Math.round((current / total) * 100);
  const filled = Math.floor(width * current / total);
  const empty = width - filled;
  
  return (
    <Box flexDirection="column">
      {label && (
        <Text color="gray">{label}</Text>
      )}
      <Box>
        <Text color={color}>{'█'.repeat(filled)}</Text>
        <Text color="gray">{'░'.repeat(empty)}</Text>
        <Text> {percentage}% ({current}/{total})</Text>
      </Box>
    </Box>
  );
};
```

#### Search Results Component
```tsx
import React from 'react';
import { Box, Text } from 'ink';

interface SearchResult {
  id: number;
  score: number;
  project: string;
  snippet: string;
  timestamp?: string;
}

interface SearchResultsProps {
  results: SearchResult[];
  stats: {
    total: number;
    filtered: number;
    matched: number;
    time_ms: number;
  };
}

export const SearchResults: React.FC<SearchResultsProps> = ({ results, stats }) => {
  return (
    <Box flexDirection="column">
      {/* Statistics Panel */}
      <Box padding={1} borderStyle="round" borderColor="cyan" marginBottom={1}>
        <Box flexDirection="column">
          <Text color="cyan" bold>📊 Search Statistics</Text>
          <Text>Total conversations: {stats.total.toLocaleString()}</Text>
          <Text>Project filtered: {stats.filtered.toLocaleString()}</Text>
          <Text>Semantic matches: {stats.matched}</Text>
          <Text>Response time: {stats.time_ms}ms</Text>
        </Box>
      </Box>

      {/* Results */}
      <Text color="cyan" bold>🎯 Results</Text>
      {results.map((result, index) => (
        <Box 
          key={result.id}
          padding={1} 
          borderStyle="single" 
          borderColor="gray"
          marginTop={1}
        >
          <Box flexDirection="column">
            <Box>
              <Text color="white" bold>#{index + 1}</Text>
              <Text color="yellow"> Score: {result.score}</Text>
              <Text color="green"> Project: {result.project}</Text>
            </Box>
            <Text color="gray">{result.snippet}</Text>
          </Box>
        </Box>
      ))}
    </Box>
  );
};
```

### 5. Integration with Existing MCP Server

#### Modified MCP Server Structure
```python
# mcp_server.py modifications

class EnhancedMCPServer:
    def __init__(self):
        self.interactive_mode = self.detect_interactive_mode()
        
    def detect_interactive_mode(self):
        # Detect if running in interactive terminal
        return (
            os.isatty(sys.stdin.fileno()) and 
            os.environ.get('TERM') and
            os.environ.get('MCP_UI_MODE') != 'json'
        )
    
    async def search_conversations_unified(self, params):
        if self.interactive_mode and params.get('ui_mode', True):
            # Launch Node.js Ink UI
            return await self.run_interactive_search(params)
        else:
            # Standard processing
            return await self.standard_search(params)
    
    async def run_interactive_search(self, params):
        # Spawn Node.js process with Ink UI
        import subprocess
        
        ui_script = Path(__file__).parent / 'ui' / 'search-ui.js'
        process = subprocess.Popen([
            'node', str(ui_script),
            '--query', params['query'],
            '--project', params.get('project_context', ''),
            '--mode', 'interactive'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Stream results back to MCP client
        return await self.stream_ui_results(process)
```

### 6. CLI Entry Points

Create standalone CLI commands:

```bash
# New CLI commands
./ui/search-cli.js "React performance optimization" --project tylergohr.com
./ui/sync-cli.js --rebuild-from-scratch --ui
./ui/health-cli.js --dashboard --refresh 5
```

### 7. Environment Variables

```bash
# Enable/disable UI features
export MCP_UI_MODE=interactive  # or 'json'
export MCP_UI_COLORS=true
export MCP_UI_ANIMATIONS=true
export MCP_UI_REFRESH_RATE=1000
```

## Integration Phases

### Phase 1: Core Infrastructure (Week 1)
- [x] Research and planning
- [ ] Set up Ink dependencies
- [ ] Create basic UI components
- [ ] Implement mode detection
- [ ] Test basic progress bar

### Phase 2: Search UI (Week 2)
- [ ] Enhanced search_conversations_unified UI
- [ ] Real-time progress tracking
- [ ] Results formatting and display
- [ ] Statistics panel
- [ ] Testing with actual searches

### Phase 3: Sync UI (Week 3)
- [ ] File processing progress UI
- [ ] Live statistics updates
- [ ] Error handling and display
- [ ] Completion summary
- [ ] Testing with full sync operations

### Phase 4: Health Dashboard (Week 4)
- [ ] System status dashboard
- [ ] Real-time metrics
- [ ] Component health indicators
- [ ] Performance graphs (ASCII art)
- [ ] Auto-refresh capabilities

### Phase 5: Polish & Production (Week 5)
- [ ] Error handling and graceful fallbacks
- [ ] Performance optimization
- [ ] Documentation and examples
- [ ] Integration testing
- [ ] Production deployment

## Benefits

### For Users
- **Visual Feedback**: Clear progress indication for long operations
- **Real-time Information**: Live updates on processing status
- **Better UX**: Professional CLI experience
- **Debugging**: Easier to see what's happening during operations

### For Operations  
- **Monitoring**: Live view of system performance
- **Diagnostics**: Visual health indicators
- **Efficiency**: Quick status checks without parsing JSON
- **Professional Appearance**: Modern CLI interface

## Example Usage

```bash
# Interactive search with progress
mcp-search "React performance" --project tylergohr.com --ui

# File sync with progress bar
mcp-sync --rebuild --ui --verbose

# Live health dashboard
mcp-health --dashboard --refresh 10s

# Traditional JSON output (existing behavior)
mcp-search "React performance" --json
```

## Technical Considerations

### Performance
- UI rendering should add <50ms overhead
- Progress updates throttled to avoid performance impact
- Graceful degradation for resource-constrained environments

### Compatibility
- Maintains 100% backward compatibility
- Works with existing MCP integrations
- Optional dependencies (Ink only loaded when needed)

### Error Handling
- Fallback to standard output if UI fails
- Clear error messages for missing dependencies
- Graceful handling of terminal resize events

### Testing
- Unit tests for UI components
- Integration tests with actual MCP operations
- Performance benchmarks
- Cross-platform compatibility testing

## Conclusion

This implementation provides a significant UX improvement while maintaining full compatibility with existing systems. The phased approach allows for incremental development and testing, ensuring a robust final product.

The enhanced CLI interfaces will make your vector database tools more professional and user-friendly, while the progress indicators and real-time feedback will greatly improve the experience for long-running operations.