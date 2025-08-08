#!/usr/bin/env node

/**
 * Terminal Kit Sync UI Demo - PERFECT ALIGNMENT VERSION
 * Uses Terminal Kit's table functionality for professional box drawing
 */

var term = require('terminal-kit').terminal;

function clearScreen() {
  term.clear();
}

async function demoSyncUI() {
  clearScreen();
  
  // Header
  term.blue.bold('🔄 force_conversation_sync');
  term.bright(' (Terminal Kit Enhanced UI)\n\n');
  
  term.gray('Mode: ');
  term.yellow('Full rebuild from scratch\n');
  term.gray('Enhancement: ');
  term.green('All enhancements enabled\n');
  term.gray('Source: ');
  term.white('/home/user/.claude/projects/*.jsonl\n\n');

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
  let progressBar;

  // Initialize progress bar
  progressBar = term.progressBar({
    width: 60,
    title: 'Processing Files:',
    eta: true,
    percent: true,
    inline: false
  });

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
    recentFiles = recentFiles.slice(0, 6); // Keep last 6 files

    // Update progress bar
    progressBar.update(processed / totalFiles);

    // Show current file
    term.moveTo(1, 8);
    term.yellow('📂 Currently processing: ');
    term.white(currentFile);
    term.eraseLineAfter();
    term('\n\n\n\n'); // Space for progress bar

    // Live Statistics Table
    term.moveTo(1, 12);
    term.cyan.bold('📊 Live Processing Statistics\n');
    
    const elapsedSeconds = (Date.now() - stats.startTime) / 1000;
    const filesPerSecond = (processed / elapsedSeconds).toFixed(1);
    const entriesPerSecond = (stats.totalEntries / elapsedSeconds).toFixed(0);
    const successRate = ((processed - stats.errors) / processed * 100).toFixed(1);

    term.table([
      ['Metric', 'Count'],
      ['✅ Conversations Added', stats.added.toLocaleString()],
      ['🔄 Conversations Updated', stats.updated.toLocaleString()],
      ['📝 Total Entries Processed', stats.totalEntries.toLocaleString()],
      ['❌ Processing Errors', stats.errors.toString()],
      ['⏭️ Files Skipped', stats.skipped.toString()],
      ['⚡ Processing Rate', `${filesPerSecond} files/sec, ${entriesPerSecond} entries/sec`],
      ['📈 Success Rate', `${successRate}%`]
    ], {
      hasBorder: true,
      borderChars: 'lightRounded',
      borderAttr: { color: 'cyan' },
      textAttr: { color: 'white' },
      firstRowTextAttr: { color: 'cyan', bold: true },
      firstColumnTextAttr: { color: 'yellow' },
      width: 65,
      fit: true
    });

    term('\n');

    // Recent Files Table
    term.gray.bold('📋 Recently Processed Files\n');
    
    const fileTableData = [['Status', 'File', 'Added', 'Updated']];
    recentFiles.forEach(file => {
      const statusIcon = file.status === 'error' ? '❌' : 
                        file.status === 'skipped' ? '⏭️' : '✅';
      const fileName = file.name.slice(0, 30);
      const added = file.status === 'success' ? `+${file.added}` : file.status;
      const updated = file.status === 'success' ? `~${file.updated}` : '';
      
      fileTableData.push([statusIcon, fileName, added, updated]);
    });

    term.table(fileTableData, {
      hasBorder: true,
      borderChars: 'lightRounded',
      borderAttr: { color: 'gray' },
      textAttr: { color: 'white' },
      firstRowTextAttr: { color: 'gray', bold: true },
      width: 65,
      fit: true
    });
    
    await new Promise(resolve => setTimeout(resolve, 250));
  }

  // Show completion
  term.moveTo(1, 8);
  term.green.bold('🎉 Synchronization Complete! ');
  term.bright('All conversation files processed successfully\n');
  term.eraseLineAfter();

  // Update progress bar to 100%
  progressBar.update(1);
  term('\n\n');

  // Final Statistics Table
  term.green.bold('🏆 Final Processing Summary\n');
  term.table([
    ['Summary Item', 'Result'],
    ['Total Conversations Indexed', stats.totalEntries.toLocaleString()],
    ['New Conversations Added', stats.added.toLocaleString()],
    ['Existing Conversations Updated', stats.updated.toLocaleString()],
    ['Files Successfully Processed', `${totalFiles - stats.errors}/${totalFiles}`],
    ['Overall Success Rate', `${((totalFiles - stats.errors) / totalFiles * 100).toFixed(1)}%`],
    ['Processing Time', `${((Date.now() - stats.startTime) / 1000).toFixed(1)}s`]
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'green' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'green', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 65,
    fit: true
  });

  term('\n');
  
  // Next steps
  term.cyan.bold('🚀 Next Steps:\n');
  term('  • Vector embeddings are being generated in background\n');  
  term('  • Enhanced metadata processing is complete\n');
  term('  • Database is now ready for semantic search operations\n\n');
  
  term.dim('Press Ctrl+C to exit\n');
}

// Handle graceful exit
process.on('SIGINT', () => {
  term.clear();
  term.green('\n👋 Thanks for viewing the Terminal Kit Sync UI demo!\n');
  process.exit(0);
});

// Run the demo
demoSyncUI().then(() => {
  // Keep the display visible
  setInterval(() => {}, 1000);
}).catch(console.error);