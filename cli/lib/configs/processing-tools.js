/**
 * Configuration for Data Processing & Sync MCP Tools
 * - force_conversation_sync
 * - run_unified_enhancement
 * - backfill_conversation_chains
 */

const processingToolsConfigs = {
  force_conversation_sync: {
    toolName: 'force_conversation_sync',
    icon: '🔄',
    description: 'Full Database Synchronization',
    
    phases: [
      { label: '📂 Scanning conversation files...', duration: 1200 },
      { label: '🔍 Processing JSONL data...', duration: 2000 },
      { label: '🧠 Generating embeddings...', duration: 1800 },
      { label: '💾 Updating database entries...', duration: 1500 },
      { label: '✨ Applying enhancements...', duration: 1000 }
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
      formatter: 'processingStatus'
    },
    
    tips: [
      'Full sync processes all JSONL files for complete database rebuild',
      'Large datasets may take 10-15 minutes for complete processing',
      'Enhanced metadata is applied automatically during sync',
      'Use this for recovery scenarios or initial database setup'
    ],
    
    actions: [
      { command: 'sync --project specific', description: 'Sync only specific project files' },
      { command: 'sync --incremental', description: 'Process only new/changed files' },
      { command: 'sync --validate', description: 'Validate database integrity after sync' }
    ]
  },

  run_unified_enhancement: {
    toolName: 'run_unified_enhancement',
    icon: '✨',
    description: 'Advanced Enhancement Pipeline',
    
    phases: [
      { label: '🔍 Analyzing conversation chains...', duration: 1000 },
      { label: '🧠 Running semantic validation...', duration: 1500 },
      { label: '🎯 Applying adaptive learning...', duration: 1200 },
      { label: '🔗 Building relationship links...', duration: 800 },
      { label: '📊 Updating metadata fields...', duration: 600 }
    ],
    
    statsTable: {
      borderColor: 'green',
      headerColor: 'green',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'blue',
      headerColor: 'green',
      formatter: 'default'
    },
    
    tips: [
      'Unified enhancement addresses conversation chain back-fill',
      'Achieves 99.6%+ coverage for relationship metadata fields',
      'Combines PRP-1 through PRP-4 enhancement systems',
      'Use regularly to maintain optimal metadata population'
    ],
    
    actions: [
      { command: 'enhance --session specific', description: 'Enhance specific conversation session' },
      { command: 'enhance --backfill-only', description: 'Run only conversation chain back-fill' },
      { command: 'enhance --validation-only', description: 'Run only semantic validation' }
    ]
  },

  backfill_conversation_chains: {
    toolName: 'backfill_conversation_chains',
    icon: '🔗',
    description: 'Conversation Chain Relationship Builder',
    
    phases: [
      { label: '🔍 Identifying conversation sessions...', duration: 800 },
      { label: '📋 Analyzing message sequences...', duration: 1200 },
      { label: '🔗 Building chain relationships...', duration: 1000 },
      { label: '🎯 Linking solutions & feedback...', duration: 700 },
      { label: '💾 Updating chain metadata...', duration: 500 }
    ],
    
    statsTable: {
      borderColor: 'blue',
      headerColor: 'blue',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'green',
      headerColor: 'blue',
      formatter: 'default'
    },
    
    tips: [
      'Conversation chains link adjacent messages for context flow',
      'Back-fill addresses timing limitations of real-time hooks',
      'Solution-feedback relationships improve search relevance',
      'Essential for conversation context understanding'
    ],
    
    actions: [
      { command: 'backfill --session specific', description: 'Process specific session chains' },
      { command: 'backfill --field-types chains', description: 'Focus on chain relationship fields' },
      { command: 'backfill --limit 50', description: 'Limit processing to 50 sessions' }
    ]
  },

  smart_metadata_sync_status: {
    toolName: 'smart_metadata_sync_status',
    icon: '📊',
    description: 'Enhanced Metadata Status Analysis',
    
    phases: [
      { label: '🔍 Scanning metadata coverage...', duration: 600 },
      { label: '📊 Analyzing field population...', duration: 800 },
      { label: '🎯 Identifying optimization opportunities...', duration: 500 },
      { label: '📈 Generating coverage statistics...', duration: 400 }
    ],
    
    statsTable: {
      borderColor: 'yellow',
      headerColor: 'yellow',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'green',
      headerColor: 'yellow',
      formatter: 'default'
    },
    
    tips: [
      'Provides detailed analysis of 30+ metadata field coverage',
      'Identifies which files need selective enhancement processing',
      'Shows conversation chain population statistics',
      'Helps monitor enhancement system effectiveness'
    ],
    
    actions: [
      { command: 'metadata-status --detailed', description: 'Show detailed field-by-field analysis' },
      { command: 'metadata-status --recommendations', description: 'Get optimization recommendations' },
      { command: 'metadata-status --export csv', description: 'Export status data to CSV' }
    ]
  }
};

module.exports = processingToolsConfigs;