#!/usr/bin/env node

/**
 * Individual Sync UI Demo
 * Shows enhanced force_conversation_sync interface
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
  gray: '\x1b[90m'
};

function colorize(text, color) {
  return `${colors[color]}${text}${colors.reset}`;
}

function progressBar(current, total, width = 50) {
  const percentage = Math.round((current / total) * 100);
  const filled = Math.floor((current / total) * width);
  const empty = width - filled;
  
  return `${colorize('█'.repeat(filled), 'cyan')}${colorize('░'.repeat(empty), 'dim')} ${percentage}% (${current}/${total})`;
}

function clearScreen() {
  process.stdout.write('\x1b[2J\x1b[0f');
}

function moveCursor(row, col) {
  process.stdout.write(`\x1b[${row};${col}H`);
}

async function demoSyncUI() {
  clearScreen();
  
  console.log(colorize('🔄 force_conversation_sync', 'blue') + colorize(' (Enhanced UI Demo)', 'bright'));
  console.log('');
  console.log(colorize('Mode: ', 'gray') + colorize('Full rebuild from scratch', 'yellow'));
  console.log(colorize('Enhancement: ', 'gray') + colorize('All enhancements enabled', 'green'));
  console.log(colorize('Source: ', 'gray') + colorize('/home/user/.claude/projects/*.jsonl', 'white'));
  console.log('');

  const totalFiles = 106;
  let processed = 0;
  let stats = { 
    added: 0, 
    updated: 0, 
    errors: 0, 
    skipped: 0,
    totalEntries: 0,
    startTime: Date.now()
  };
  
  const files = [
    'tylergohr_com_session_001.jsonl',
    'tylergohr_com_session_012.jsonl',
    'invoice_chaser_session_042.jsonl',
    'invoice_chaser_session_087.jsonl', 
    'ai_orchestrator_session_015.jsonl',
    'ai_orchestrator_session_033.jsonl',
    'personal_dev_session_028.jsonl',
    'personal_dev_session_054.jsonl',
    'vector_db_session_089.jsonl',
    'vector_db_session_103.jsonl'
  ];

  let recentFiles = [];

  // Simulate processing with more realistic progress
  for (let i = 0; i < 40; i++) { // Show 40 files for demo
    processed++;
    const currentFile = files[i % files.length];
    
    // Simulate more realistic results
    const isError = Math.random() < 0.03; // 3% error rate
    const isSkipped = Math.random() < 0.08; // 8% skip rate
    const addedCount = isError || isSkipped ? 0 : Math.floor(Math.random() * 35) + 10;
    const updatedCount = isError || isSkipped ? 0 : Math.floor(Math.random() * 15) + 2;
    
    stats.added += addedCount;
    stats.updated += updatedCount;
    stats.totalEntries += addedCount + updatedCount;
    if (isError) stats.errors++;
    if (isSkipped) stats.skipped++;

    // Update recent files list
    const fileStatus = isError ? 'error' : isSkipped ? 'skipped' : 'success';
    recentFiles.unshift({
      name: currentFile,
      status: fileStatus,
      added: addedCount,
      updated: updatedCount
    });
    recentFiles = recentFiles.slice(0, 8); // Keep last 8 files

    // Update display
    moveCursor(7, 1);
    console.log(colorize('📂 Currently processing: ', 'yellow') + colorize(currentFile, 'white') + ' '.repeat(50));
    console.log('');
    console.log(progressBar(processed, totalFiles, 60));
    console.log('');
    
    // Enhanced statistics with more metrics
    console.log(colorize('┌─ 📊 Live Processing Statistics ──────────────────────────────┐', 'cyan'));
    console.log(colorize('│', 'cyan') + ' ' + colorize('✅ Conversations Added:', 'green') + ` ${stats.added.toLocaleString()}`.padEnd(44) + colorize('│', 'cyan'));
    console.log(colorize('│', 'cyan') + ' ' + colorize('🔄 Conversations Updated:', 'blue') + ` ${stats.updated.toLocaleString()}`.padEnd(42) + colorize('│', 'cyan'));
    console.log(colorize('│', 'cyan') + ' ' + colorize('📝 Total Entries Processed:', 'white') + ` ${stats.totalEntries.toLocaleString()}`.padEnd(39) + colorize('│', 'cyan'));
    console.log(colorize('│', 'cyan') + ' ' + colorize('❌ Processing Errors:', 'red') + ` ${stats.errors}`.padEnd(44) + colorize('│', 'cyan'));
    console.log(colorize('│', 'cyan') + ' ' + colorize('⏭️  Files Skipped:', 'yellow') + ` ${stats.skipped}`.padEnd(47) + colorize('│', 'cyan'));
    
    // Calculate processing rate
    const elapsedSeconds = (Date.now() - stats.startTime) / 1000;
    const filesPerSecond = (processed / elapsedSeconds).toFixed(1);
    const entriesPerSecond = (stats.totalEntries / elapsedSeconds).toFixed(0);
    
    console.log(colorize('│', 'cyan') + ' ' + colorize('⚡ Processing Rate:', 'magenta') + ` ${filesPerSecond} files/sec, ${entriesPerSecond} entries/sec`.padEnd(29) + colorize('│', 'cyan'));
    
    // Success rate
    const successRate = ((processed - stats.errors) / processed * 100).toFixed(1);
    console.log(colorize('│', 'cyan') + ' ' + colorize('📈 Success Rate:', 'green') + ` ${successRate}%`.padEnd(47) + colorize('│', 'cyan'));
    
    console.log(colorize('└─────────────────────────────────────────────────────────────┘', 'cyan'));
    console.log('');
    
    // Recent files processed
    console.log(colorize('┌─ 📋 Recently Processed Files ────────────────────────────────┐', 'gray'));
    recentFiles.slice(0, 6).forEach((file, index) => {
      const statusIcon = file.status === 'error' ? '❌' : 
                        file.status === 'skipped' ? '⏭️' : '✅';
      const statusColor = file.status === 'error' ? 'red' : 
                         file.status === 'skipped' ? 'yellow' : 'green';
      
      let line = `│ ${statusIcon} ${file.name.slice(0, 35).padEnd(35)}`;
      if (file.status === 'success') {
        line += colorize(` +${file.added}`, 'green') + colorize(` ~${file.updated}`, 'blue');
      } else {
        line += colorize(` ${file.status}`, statusColor);
      }
      line = line.padEnd(70 - line.replace(/\x1b\[[0-9;]*m/g, '').length + line.length) + ' │';
      console.log(colorize(line.slice(0, 1), 'gray') + line.slice(1, -1) + colorize('│', 'gray'));
    });
    console.log(colorize('└─────────────────────────────────────────────────────────────┘', 'gray'));
    
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  // Show completion
  moveCursor(7, 1);
  console.log(' '.repeat(80)); // Clear current file line
  moveCursor(7, 1);
  
  console.log(colorize('🎉 Synchronization Complete!', 'green') + colorize(' All conversation files processed successfully', 'bright'));
  console.log('');
  console.log(progressBar(totalFiles, totalFiles, 60));
  console.log('');
  
  // Final statistics
  console.log(colorize('┌─ 🏆 Final Processing Summary ─────────────────────────────────┐', 'green'));
  console.log(colorize('│', 'green') + ' ' + colorize('Total Conversations Indexed:', 'white') + ` ${stats.totalEntries.toLocaleString()}`.padEnd(38) + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ' + colorize('New Conversations Added:', 'cyan') + ` ${stats.added.toLocaleString()}`.padEnd(41) + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ' + colorize('Existing Conversations Updated:', 'blue') + ` ${stats.updated.toLocaleString()}`.padEnd(35) + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ' + colorize('Files Successfully Processed:', 'green') + ` ${totalFiles - stats.errors}/${totalFiles}`.padEnd(36) + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ' + colorize('Overall Success Rate:', 'yellow') + ` ${((totalFiles - stats.errors) / totalFiles * 100).toFixed(1)}%`.padEnd(43) + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ' + colorize('Processing Time:', 'magenta') + ` ${((Date.now() - stats.startTime) / 1000).toFixed(1)}s`.padEnd(48) + colorize('│', 'green'));
  console.log(colorize('└─────────────────────────────────────────────────────────────┘', 'green'));
  console.log('');
  
  // Next steps
  console.log(colorize('🚀 Next Steps:', 'cyan'));
  console.log('  • Vector embeddings are being generated in background');  
  console.log('  • Enhanced metadata processing is complete');
  console.log('  • Database is now ready for semantic search operations');
  console.log('');
  console.log(colorize('Press Ctrl+C to exit', 'dim'));
}

// Handle graceful exit
process.on('SIGINT', () => {
  clearScreen();
  console.log(colorize('\n👋 Thanks for viewing the Sync UI demo!\n', 'green'));
  process.exit(0);
});

// Run the demo
demoSyncUI().then(() => {
  // Keep the display visible
  setInterval(() => {}, 1000);
}).catch(console.error);