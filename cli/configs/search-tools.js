/**
 * Configuration for Search & Retrieval MCP Tools
 * - search_conversations_unified
 */

const searchToolsConfigs = {
  search_conversations_unified: {
    toolName: 'search_conversations_unified',
    icon: '🔍',
    description: 'Enhanced Semantic Search',
    
    phases: [
      { label: '⚡ Initializing vector database...', duration: 1000 },
      { label: '🧠 Generating embeddings for query...', duration: 1800 },
      { label: '🔍 Searching conversation vectors...', duration: 1200 },
      { label: '🎯 Applying project context filters...', duration: 800 },
      { label: '✨ Running semantic enhancement...', duration: 600 }
    ],
    
    statsTable: {
      borderColor: 'cyan',
      headerColor: 'cyan',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'gray',
      headerColor: 'white',
      formatter: 'searchResults'
    },
    
    tips: [
      'Use --project flag to boost relevance for specific projects',
      'Add --include-code-only to filter for technical conversations',
      'Try --search-mode=validated_only for proven solutions',
      'Use --hybrid-intelligence for advanced filtering by tools/frameworks'
    ],
    
    actions: [
      { command: 'search --project myproject', description: 'Search within specific project context' },
      { command: 'search --search-mode=validated_only', description: 'Find only validated solutions' },
      { command: 'search --include-code-only', description: 'Filter for technical conversations' }
    ]
  },

  search_with_hybrid_intelligence: {
    toolName: 'search_with_hybrid_intelligence',
    icon: '🤖',
    description: 'AI-Enhanced Search with Tool & Framework Filtering',
    
    phases: [
      { label: '⚡ Initializing hybrid intelligence...', duration: 800 },
      { label: '🔍 Running semantic search...', duration: 1000 },
      { label: '🧠 Applying spaCy NER filtering...', duration: 600 },
      { label: '⚙️ Tool and framework detection...', duration: 400 },
      { label: '🎯 Confidence scoring and ranking...', duration: 500 }
    ],
    
    statsTable: {
      borderColor: 'magenta',
      headerColor: 'magenta',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'blue',
      headerColor: 'white',
      formatter: 'searchResults'
    },
    
    tips: [
      'Use --tool-filter to find conversations using specific Claude Code tools',
      'Try --framework-filter to search by technology stack (React, TypeScript, etc.)',
      'Set --min-confidence to filter by ML confidence threshold',
      'Use --pattern-type to find specific solution/feedback/error patterns'
    ],
    
    actions: [
      { command: 'search --tool-filter=Edit', description: 'Find conversations using the Edit tool' },
      { command: 'search --framework-filter=React', description: 'Search React-related conversations' },
      { command: 'search --pattern-type=solution', description: 'Find solution patterns only' }
    ]
  }
};

module.exports = searchToolsConfigs;