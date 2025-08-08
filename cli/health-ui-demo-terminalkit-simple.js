#!/usr/bin/env node

/**
 * Terminal Kit Health UI Demo - SIMPLE VERSION
 * Uses Terminal Kit's table functionality for professional box drawing
 */

var term = require('terminal-kit').terminal;

function clearScreen() {
  term.clear();
}

function createSparkline(values, width = 10) {
  const bars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  
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
  term.bold(' (Terminal Kit Health Dashboard)\n\n');
  
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

  // Component Status Overview
  term.green.bold('Component Status Overview\n');
  
  term.table([
    ['Component', 'Status', 'Key Metric', 'Trend'],
    ['🟢 Vector Database', 'Healthy', '145ms avg latency', createSparkline(latencyHistory)],
    ['🟢 MCP Server', 'Healthy', '20/20 tools active', '████████▉▉'],
    ['🟢 Enhancement Pipeline', 'Healthy', '99.6% coverage', '█████▉▉▉▉▉'],
    ['🟢 Performance Cache', 'Healthy', '87% hit rate', '██████▉▉▉▉']
  ], {
    hasBorder: true,
    borderChars: 'lightRounded',
    borderAttr: { color: 'green' },
    textAttr: { color: 'white' },
    firstRowTextAttr: { color: 'green', bold: true },
    firstColumnTextAttr: { color: 'yellow' },
    width: 75,
    fit: true
  });

  term('\n');

  // System Resources
  term.blue.bold('💻 System Resources\n');
  term.table([
    ['Resource', 'Usage', 'Status', 'Trend'],
    ['CPU Usage', '23%', '████▎         ', createSparkline(cpuHistory)],
    ['Memory', '512MB/2GB', '███████▋      ', '▅▆▇▆▅▄▅▆▇▆'],
    ['Disk I/O', 'Low', 'Normal', '▃▄▃▃▄▅▄▃▃▄'],
    ['Network', 'Normal', 'Active', '▆▇▆▅▆▇▆▅▆▇'],
    ['Load Average', '0.45, 0.52, 0.48', 'Good', '▄▅▄▄▅▆▅▄▄▅']
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
    ['', 'Total Searches', '2,847', 'ℹ️'],
    ['', 'Success Rate', '99.96%', '✅'],
    ['Database', 'Query Time', '145ms avg', '✅'],
    ['', 'Index Size', '2.1GB', 'ℹ️'],
    ['', 'Compression', '68%', '✅'],
    ['Enhancement', 'Jobs Processed', '156 completed', '✅'],
    ['', 'Success Rate', '99.4%', '✅'],
    ['', 'Queue Length', '0', '✅'],
    ['MCP Tools', 'Tools Active', '20/20', '✅'],
    ['', 'Response Time', '<50ms', '✅'],
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