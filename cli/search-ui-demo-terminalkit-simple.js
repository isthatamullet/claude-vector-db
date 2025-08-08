#!/usr/bin/env node

/**
 * Terminal Kit Search UI Demo - SIMPLE VERSION
 * Uses Terminal Kit's table functionality for professional box drawing
 */

var term = require('terminal-kit').terminal;

function clearScreen() {
  term.clear();
}

function simpleProgressBar(current, total, width = 50) {
  const percentage = Math.round((current / total) * 100);
  const filled = Math.floor((current / total) * width);
  const empty = width - filled;
  
  return `${'█'.repeat(filled)}${'░'.repeat(empty)} ${percentage}%`;
}

async function demoSearchUI() {
  clearScreen();
  
  // Header
  term.blue.bold('🔍 search_conversations_unified');
  term.bold(' (Terminal Kit Enhanced UI)\n\n');
  
  term.gray('Query: ');
  term.white('"React performance optimization"\n');
  term.gray('Project Context: ');
  term.green('tylergohr.com\n');
  term.gray('Search Mode: ');
  term.cyan('semantic\n');
  term.gray('Enhancement: ');
  term.green('enabled\n\n');

  const phases = [
    { label: '⚡ Initializing vector database...', duration: 1000 },
    { label: '🧠 Generating embeddings for query...', duration: 1800 },
    { label: '🔍 Searching conversation vectors...', duration: 1200 },
    { label: '🎯 Applying project context filters...', duration: 800 },
    { label: '✨ Running semantic enhancement...', duration: 600 }
  ];

  // Show progress phases
  for (let i = 0; i < phases.length; i++) {
    term.moveTo(1, 9);
    term.yellow(phases[i].label);
    term.eraseLineAfter();
    term('\n');
    term.cyan(simpleProgressBar(i + 1, phases.length, 50));
    term('\n');
    
    await new Promise(resolve => setTimeout(resolve, phases[i].duration));
  }

  // Show completion
  term.moveTo(1, 9);
  term.green('✅ Search complete! ');
  term.gray('(285ms)');
  term.eraseLineAfter();
  term('\n\n');

  // Statistics using Terminal Kit table
  term.cyan.bold('📊 Enhanced Search Statistics\n');
  term.table([
    ['Metric', 'Value'],
    ['Total conversations in database', '31,245'],
    ['Project context filtered', '847 (tylergohr.com)'],
    ['Semantic similarity matches', '3'],
    ['Hybrid intelligence applied', '✓'],
    ['Cache hit rate', '87%'],
    ['Response time', '285ms (target: <500ms)']
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'cyan' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'cyan', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 60,
    fit: true
  });
  
  term('\n');

  // Search Results
  term.cyan.bold('🎯 Search Results ');
  term.bold('(Ranked by semantic similarity)\n\n');

  const results = [
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
  ];

  // Each result as a separate table for better formatting
  results.forEach((result, index) => {
    term.table([
      ['Rank', 'Score', 'Project', 'Timestamp'],
      [result.rank, result.score, result.project, result.timestamp],
      ['Snippet', result.snippet],
      ['Tools: ' + result.tools, 'Category: ' + result.category]
    ], {
      hasBorder: true,
      borderChars: 'lightRounded',
      borderAttr: { color: 'gray' },
      textAttr: { color: 'white' },
      firstRowTextAttr: { color: 'white', bold: true },
      firstColumnTextAttr: { color: 'yellow' },
      width: 75,
      fit: true
    });
    term('\n');
  });

  // Pro tips
  term.yellow.bold('💡 Pro Tips:\n');
  term('  • Use --project flag to boost relevance for specific projects\n');
  term('  • Add --include-code-only to filter for technical conversations\n');
  term('  • Try --search-mode=validated_only for proven solutions\n\n');
  
  term.dim('Press Ctrl+C to exit\n');
}

// Handle graceful exit
process.on('SIGINT', () => {
  term.clear();
  term.green('\n👋 Thanks for viewing the Terminal Kit Search UI demo!\n');
  process.exit(0);
});

// Run the demo
demoSearchUI().then(() => {
  // Keep the display visible
  setInterval(() => {}, 1000);
}).catch(console.error);