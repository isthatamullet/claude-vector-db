#!/usr/bin/env node

/**
 * Generated Search Demo - Using the MCP Tool UI Generator
 * Demonstrates how any of the 20 tools can use the modular system
 */

const MCPToolUIGenerator = require('./ui-generator');
const { getToolConfig } = require('./configs');

async function runSearchDemo() {
  // Get configuration for search tool
  const config = getToolConfig('search_conversations_unified');
  
  // Add demo parameters
  config.parameters = {
    'Query': '"React performance optimization"',
    'Project Context': 'tylergohr.com',
    'Search Mode': 'semantic',
    'Enhancement': 'enabled'
  };

  // Initialize UI generator
  const ui = new MCPToolUIGenerator(config);
  
  // Sample data (would come from actual MCP tool execution)
  const demoData = {
    stats: [
      ['Metric', 'Value'],
      ['Total conversations in database', '31,245'],
      ['Project context filtered', '847 (tylergohr.com)'],
      ['Semantic similarity matches', '3'],
      ['Hybrid intelligence applied', '✓'],
      ['Cache hit rate', '87%'],
      ['Response time', '285ms (target: <500ms)']
    ],
    statsTitle: 'Enhanced Search Statistics',
    
    results: [
      {
        rank: '#1',
        score: '0.95',
        project: 'tylergohr.com',
        snippet: 'Fixed React component performance issue with useMemo hook optimization...',
        timestamp: '2 days ago',
        tools: 'Edit, Read',
        category: 'Performance'
      },
      {
        rank: '#2', 
        score: '0.87',
        project: 'invoice-chaser',
        snippet: 'Added real-time validation for form inputs using Supabase real-time subscriptions...',
        timestamp: '1 week ago',
        tools: 'Edit, Bash',
        category: 'Validation'
      },
      {
        rank: '#3',
        score: '0.82',
        project: 'tylergohr.com',
        snippet: 'Implemented mobile-first responsive design patterns with CSS Grid and Flexbox...',
        timestamp: '3 days ago',
        tools: 'Edit, Write',
        category: 'Responsive'
      }
    ],
    resultsTitle: 'Search Results (Ranked by semantic similarity)'
  };

  // Render the complete UI
  await ui.render(demoData);
}

// Run the demo
runSearchDemo().catch(console.error);