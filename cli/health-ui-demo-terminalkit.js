#!/usr/bin/env node

/**
 * Terminal Kit Health UI Demo - PERFECT ALIGNMENT VERSION
 * Uses Terminal Kit's table functionality for professional box drawing
 */

var term = require('terminal-kit').terminal;

function clearScreen() {
  term.clear();
}

function getStatusIcon(status) {
  return status === 'healthy' ? '🟢' : status === 'warning' ? '🟡' : '🔴';
}

function createSparkline(values, width = 10) {
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  
  const bars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
  
  return values.slice(-width).map(val => {
    const normalized = (val - min) / range;
    const barIndex = Math.floor(normalized * (bars.length - 1));
    return bars[barIndex];
  }).join('');
}

async function demoHealthDashboard() {
  clearScreen();
  
  // Header
  term.blue.bold('🏥 get_system_status');
  term.bright(' (Terminal Kit Health Dashboard)\n\n');
  
  term.gray('System Health Overview');
  term.moveTo(60, 3);
  term.green('🟢 All Systems Operational\n');
  
  term.dim('Last Updated: ');
  term.white(new Date().toLocaleString());
  term.moveTo(60, 4);
  term.dim('Auto-refresh: 5s\n\n');

  // Generate sample metrics for sparklines
  const latencyHistory = Array.from({length: 10}, () => Math.floor(Math.random() * 100) + 120);
  const cpuHistory = Array.from({length: 10}, () => Math.floor(Math.random() * 30) + 15);
  const memoryHistory = Array.from({length: 10}, () => Math.floor(Math.random() * 200) + 400);

  // Component Status Grid using side-by-side tables
  term.green.bold('Component Status Overview\n');
  
  // First row - Vector Database and MCP Server
  term.table([
    ['🟢 Vector Database', 'Status'],
    ['Status', 'Healthy'],
    ['⚡ Avg Latency', '145ms'],
    ['📊 Total Entries', '31,245'],
    ['💾 Storage Used', '2.1GB'],
    ['🔍 Last Search', '12s ago'],
    ['📈 Trend', createSparkline(latencyHistory)]
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'green' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'green', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 35,
    fit: true,
    x: 1
  });

  term.moveTo(40, 7);
  term.table([
    ['🟢 MCP Server', 'Status'],
    ['Status', 'Healthy'],
    ['🔧 Active Tools', '20/20'],
    ['⏱️ Uptime', '2d 14h 23m'],
    ['🔄 Requests Today', '1,247'],
    ['📈 Success Rate', '99.8%'],
    ['🌐 Connections', 'Active']
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'green' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'green', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 35,
    fit: true
  });

  term('\n\n');

  // Second row - Enhancement Pipeline and Performance Cache
  term.table([
    ['🟢 Enhancement Pipeline', 'Status'],
    ['Status', 'Healthy'],
    ['📈 Metadata Coverage', '99.6%'],
    ['⚙️ Processing Queue', '0 jobs'],
    ['🎯 Quality Score', 'Excellent'],
    ['🔄 Last Enhancement', '3m ago'],
    ['📊 Processed Today', '156']
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'green' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'green', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 35,
    fit: true,
    x: 1
  });

  term.moveTo(40, 18);
  term.table([
    ['🟢 Performance Cache', 'Status'],
    ['Status', 'Healthy'],
    ['🎯 Hit Rate', '87%'],
    ['💾 Cache Size', '245MB'],
    ['🧹 Last Cleanup', '2h ago'],
    ['⚡ Avg Retrieval', '12ms'],
    ['📈 Trend', createSparkline([85, 87, 89, 87, 88, 87, 86, 87, 87, 88])]
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'green' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'green', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 35,
    fit: true
  });

  term('\n\n');

  // System Resources
  term.blue.bold('💻 System Resources\n');
  term.table([
    ['Resource', 'Usage', 'Status', 'Trend'],
    ['CPU Usage', '23%', '████▎         ', createSparkline(cpuHistory)],
    ['Memory', '512MB/2GB', '███████▋      ', createSparkline(memoryHistory)],
    ['Disk I/O', 'Low', 'Normal', ''],
    ['Network', 'Normal', 'Active', ''],
    ['Load Average', '0.45, 0.52, 0.48', 'Good', '']
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'blue' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'blue', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 75,
    fit: true
  });

  term('\n');

  // Performance Metrics Dashboard
  term.cyan.bold('📊 Performance Metrics (Last 24 Hours)\n');
  term.table([
    ['Category', 'Metric', 'Value', 'Status'],
    ['Search Operations', 'Average Latency', '168ms', '✅'],
    ['', 'P95 Latency', '285ms', '⚠️'],
    ['', 'P99 Latency', '450ms', '⚠️'],
    ['', 'Total Searches', '2,847', 'ℹ️'],
    ['', 'Success Rate', '99.96%', '✅'],
    ['', 'Error Rate', '0.04% (1 error)', '✅'],
    ['Database', 'Query Time', '145ms avg', '✅'],
    ['', 'Index Size', '2.1GB', 'ℹ️'],
    ['', 'Compression', '68%', '✅'],
    ['', 'Fragmentation', 'Low', '✅'],
    ['', 'Backup Status', '✓ Current', '✅'],
    ['', 'Last Optimization', '1d ago', 'ℹ️'],
    ['Enhancement', 'Jobs Processed', '156 completed', '✅'],
    ['', 'Success Rate', '99.4%', '✅'],
    ['', 'Queue Length', '0', '✅'],
    ['', 'Avg Processing', '2.3s', 'ℹ️'],
    ['MCP Tools', 'Tools Active', '20/20', '✅'],
    ['', 'Response Time', '<50ms', '✅'],
    ['', 'Memory Usage', '125MB', 'ℹ️'],
    ['', 'Connection Pool', 'Healthy', '✅']
  ], {
    hasBorder: true,
    borderChars: 'double',
    borderAttr: { color: 'cyan' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'cyan', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 75,
    fit: true
  });

  term('\n');

  // System Alerts
  term.yellow.bold('🔔 System Alerts & Notifications\n');
  term.table([
    ['Type', 'Message'],
    ['ℹ️ INFO', 'Scheduled maintenance window: Sunday 2AM-4AM PST'],
    ['✅ OK', 'All health checks passing - no issues detected'],
    ['📈 PERF', 'Search performance 15% above baseline today']
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'yellow' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'yellow', bold: true },
    width: 75,
    fit: true
  });

  term('\n');

  // Quick Actions
  term.cyan.bold('🚀 Quick Actions Available:\n');
  term('  • ');
  term.white('mcp-health --refresh 10');
  term.dim(' - Enable auto-refresh every 10 seconds\n');
  term('  • ');
  term.white('mcp-health --alerts');
  term.dim(' - View detailed alert configuration\n');
  term('  • ');
  term.white('mcp-health --export');
  term.dim(' - Export metrics to JSON/CSV\n');
  term('  • ');
  term.white('mcp-health --history 7d');
  term.dim(' - View 7-day performance history\n\n');
  
  term.dim('Press Ctrl+C to exit\n');
}

// Handle graceful exit
process.on('SIGINT', () => {
  term.clear();
  term.green('\n👋 Thanks for viewing the Terminal Kit Health Dashboard demo!\n');
  process.exit(0);
});

// Run the demo
demoHealthDashboard().then(() => {
  // Keep the display visible
  setInterval(() => {}, 1000);
}).catch(console.error);