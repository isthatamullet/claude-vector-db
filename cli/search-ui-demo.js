#!/usr/bin/env node

/**
 * Individual Search UI Demo
 * Shows enhanced search_conversations_unified interface
 */

const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  gray: '\x1b[90m',
  bgGreen: '\x1b[42m',
  bgRed: '\x1b[41m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

function progressBar(current, total, width = 50) {
  const percentage = Math.round((current / total) * 100);
  const filled = Math.floor((current / total) * width);
  const empty = width - filled;
  
  return `${colorize('█'.repeat(filled), 'cyan')}${colorize('░'.repeat(empty), 'dim')} ${percentage}%`;
}

function clearScreen() {
  process.stdout.write('\x1b[2J\x1b[0f');
}

function moveCursor(row, col) {
  process.stdout.write(`\x1b[${row};${col}H`);
}

async function demoSearchUI() {
  clearScreen();
  
  console.log(colorize('🔍 search_conversations_unified', 'blue') + colorize(' (Enhanced UI Demo)', 'bright'));
  console.log('');
  console.log(colorize('Query: ', 'gray') + colorize('"React performance optimization"', 'white'));
  console.log(colorize('Project Context: ', 'gray') + colorize('tylergohr.com', 'green'));
  console.log(colorize('Search Mode: ', 'gray') + colorize('semantic', 'cyan'));
  console.log(colorize('Enhancement: ', 'gray') + colorize('enabled', 'green'));
  console.log('');

  const phases = [
    { label: '⚡ Initializing vector database...', duration: 1000 },
    { label: '🧠 Generating embeddings for query...', duration: 1800 },
    { label: '🔍 Searching conversation vectors...', duration: 1200 },
    { label: '🎯 Applying project context filters...', duration: 800 },
    { label: '✨ Running semantic enhancement...', duration: 600 }
  ];

  // Show progress phases
  for (let i = 0; i < phases.length; i++) {
    moveCursor(8, 1);
    console.log(colorize(phases[i].label, 'yellow') + ' '.repeat(50));
    console.log('');
    console.log(progressBar(i + 1, phases.length, 50));
    console.log('');
    
    await new Promise(resolve => setTimeout(resolve, phases[i].duration));
  }

  // Show completion and results
  moveCursor(8, 1);
  console.log(colorize('✅ Search complete!', 'green') + colorize(' (285ms)', 'gray') + ' '.repeat(50));
  console.log('');
  console.log(''); // Clear progress bar line
  console.log('');
  
  // Statistics box - enhanced version
  console.log(colorize('┌─ 📊 Enhanced Search Statistics ───────────────────────────┐', 'cyan'));
  console.log(colorize('│', 'cyan') + ' Total conversations in database: ' + colorize('31,245', 'white') + '         ' + colorize('│', 'cyan'));
  console.log(colorize('│', 'cyan') + ' Project context filtered: ' + colorize('847', 'white') + ' (' + colorize('tylergohr.com', 'green') + ')    ' + colorize('│', 'cyan'));
  console.log(colorize('│', 'cyan') + ' Semantic similarity matches: ' + colorize('3', 'white') + '                 ' + colorize('│', 'cyan'));
  console.log(colorize('│', 'cyan') + ' Hybrid intelligence applied: ' + colorize('✓', 'green') + '                  ' + colorize('│', 'cyan'));
  console.log(colorize('│', 'cyan') + ' Cache hit rate: ' + colorize('87%', 'yellow') + '                        ' + colorize('│', 'cyan'));
  console.log(colorize('│', 'cyan') + ' Response time: ' + colorize('285ms', 'green') + ' (target: <500ms)          ' + colorize('│', 'cyan'));
  console.log(colorize('└─────────────────────────────────────────────────────────────┘', 'cyan'));
  console.log('');

  // Enhanced results with more detail
  console.log(colorize('🎯 Search Results', 'cyan') + colorize(' (Ranked by semantic similarity)', 'bright'));
  console.log('');

  const results = [
    { 
      score: 0.95, 
      project: 'tylergohr.com', 
      snippet: 'Fixed React component performance issue with useMemo hook optimization...',
      timestamp: '2 days ago',
      tools: ['Edit', 'Read'],
      category: 'Performance'
    },
    { 
      score: 0.87, 
      project: 'invoice-chaser', 
      snippet: 'Added real-time validation for form inputs using Supabase real-time subscriptions...',
      timestamp: '1 week ago',
      tools: ['Edit', 'Bash'],
      category: 'Validation'
    },
    { 
      score: 0.82, 
      project: 'tylergohr.com', 
      snippet: 'Implemented mobile-first responsive design patterns with CSS Grid and Flexbox...',
      timestamp: '3 days ago',
      tools: ['Edit', 'Write'],
      category: 'Responsive'
    }
  ];

  results.forEach((result, index) => {
    console.log(colorize('┌─────────────────────────────────────────────────────────────────────────┐', 'gray'));
    
    // Header line with rank, score, project
    const headerLine = colorize(`#${index + 1}`, 'bright') + 
                      '  Score: ' + colorize(result.score.toString(), 'yellow') + 
                      '  Project: ' + colorize(result.project, 'green') + 
                      '  ' + colorize(result.timestamp, 'dim');
    const padding = Math.max(0, 73 - headerLine.replace(/\x1b\[[0-9;]*m/g, '').length);
    console.log(colorize('│', 'gray') + headerLine + ' '.repeat(padding) + colorize('│', 'gray'));
    
    // Snippet line
    const snippetPadding = Math.max(0, 73 - result.snippet.length);
    console.log(colorize('│', 'gray') + colorize(result.snippet, 'white') + ' '.repeat(snippetPadding) + colorize('│', 'gray'));
    
    // Metadata line with tools and category
    const metaLine = 'Tools: ' + colorize(result.tools.join(', '), 'blue') + 
                     '  Category: ' + colorize(result.category, 'magenta');
    const metaPadding = Math.max(0, 73 - metaLine.replace(/\x1b\[[0-9;]*m/g, '').length);
    console.log(colorize('│', 'gray') + metaLine + ' '.repeat(metaPadding) + colorize('│', 'gray'));
    
    console.log(colorize('└─────────────────────────────────────────────────────────────────────────┘', 'gray'));
    console.log('');
  });

  // Additional information
  console.log(colorize('💡 Pro Tips:', 'yellow'));
  console.log('  • Use --project flag to boost relevance for specific projects');
  console.log('  • Add --include-code-only to filter for technical conversations');
  console.log('  • Try --search-mode=validated_only for proven solutions');
  console.log('');
  console.log(colorize('Press Ctrl+C to exit', 'dim'));
}

// Handle graceful exit
process.on('SIGINT', () => {
  clearScreen();
  console.log(colorize('\n👋 Thanks for viewing the Search UI demo!\n', 'green'));
  process.exit(0);
});

// Run the demo
demoSearchUI().then(() => {
  // Keep the display visible
  setInterval(() => {}, 1000);
}).catch(console.error);