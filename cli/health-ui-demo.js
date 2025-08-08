#!/usr/bin/env node

/**
 * Individual Health Dashboard UI Demo
 * Shows enhanced get_system_status interface
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

function clearScreen() {
  process.stdout.write('\x1b[2J\x1b[0f');
}

function getStatusIcon(status) {
  return status === 'healthy' ? '🟢' : status === 'warning' ? '🟡' : '🔴';
}

function getStatusColor(status) {
  return status === 'healthy' ? 'green' : status === 'warning' ? 'yellow' : 'red';
}

function createSparkline(values, width = 20) {
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
  
  console.log(colorize('🏥 get_system_status', 'blue') + colorize(' (Enhanced Health Dashboard)', 'bright'));
  console.log('');
  console.log(colorize('System Health Overview', 'gray') + ' '.repeat(40) + colorize('🟢 All Systems Operational', 'green'));
  console.log(colorize('Last Updated: ', 'dim') + colorize(new Date().toLocaleString(), 'white') + ' '.repeat(20) + colorize('Auto-refresh: 5s', 'dim'));
  console.log('');

  // Generate some sample metrics for sparklines
  const latencyHistory = Array.from({length: 20}, () => Math.floor(Math.random() * 100) + 120);
  const cpuHistory = Array.from({length: 20}, () => Math.floor(Math.random() * 30) + 15);
  const memoryHistory = Array.from({length: 20}, () => Math.floor(Math.random() * 200) + 400);

  // Component status grid - enhanced version
  console.log(colorize('┌─ 🟢 Vector Database ─────────────────┐  ┌─ 🟢 MCP Server ─────────────────────┐', 'green'));
  console.log(colorize('│', 'green') + ' Status: ' + colorize('Healthy', 'green') + '                   ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' Status: ' + colorize('Healthy', 'green') + '                  ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ⚡ Avg Latency: ' + colorize('145ms', 'cyan') + '           ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 🔧 Active Tools: ' + colorize('20/20', 'cyan') + '         ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 📊 Total Entries: ' + colorize('31,245', 'white') + '        ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' ⏱️  Uptime: ' + colorize('2d 14h 23m', 'white') + '         ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 💾 Storage Used: ' + colorize('2.1GB', 'white') + '          ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 🔄 Requests Today: ' + colorize('1,247', 'white') + '      ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 🔍 Last Search: ' + colorize('12s ago', 'dim') + '         ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 📈 Success Rate: ' + colorize('99.8%', 'green') + '        ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 📈 Trend: ' + colorize(createSparkline(latencyHistory), 'cyan') + '    ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 🌐 Connections: ' + colorize('Active', 'green') + '         ' + colorize('│', 'green'));
  console.log(colorize('└───────────────────────────────────────┘', 'green') + '  ' + colorize('└─────────────────────────────────────────┘', 'green'));
  console.log('');
  console.log(colorize('┌─ 🟢 Enhancement Pipeline ────────────┐  ┌─ 🟢 Performance Cache ──────────────┐', 'green'));
  console.log(colorize('│', 'green') + ' Status: ' + colorize('Healthy', 'green') + '                   ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' Status: ' + colorize('Healthy', 'green') + '                  ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 📈 Metadata Coverage: ' + colorize('99.6%', 'cyan') + '      ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 🎯 Hit Rate: ' + colorize('87%', 'yellow') + '            ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' ⚙️  Processing Queue: ' + colorize('0 jobs', 'green') + '      ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 💾 Cache Size: ' + colorize('245MB', 'white') + '          ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 🎯 Quality Score: ' + colorize('Excellent', 'green') + '     ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 🧹 Last Cleanup: ' + colorize('2h ago', 'dim') + '       ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 🔄 Last Enhancement: ' + colorize('3m ago', 'dim') + '      ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' ⚡ Avg Retrieval: ' + colorize('12ms', 'cyan') + '       ' + colorize('│', 'green'));
  console.log(colorize('│', 'green') + ' 📊 Processed Today: ' + colorize('156', 'white') + '        ' + colorize('│', 'green') + '  ' + colorize('│', 'green') + ' 📈 Trend: ' + colorize(createSparkline([85, 87, 89, 87, 88, 87, 86, 87, 87, 88]), 'yellow') + '      ' + colorize('│', 'green'));
  console.log(colorize('└───────────────────────────────────────┘', 'green') + '  ' + colorize('└─────────────────────────────────────────┘', 'green'));
  console.log('');

  // System Resources section
  console.log(colorize('┌─ 💻 System Resources ────────────────────────────────────────────────────┐', 'blue'));
  console.log(colorize('│', 'blue') + ' CPU Usage: ' + colorize('23%', 'green') + ' ' + colorize('████▎', 'green') + colorize('                  ', 'dim') + '  Memory: ' + colorize('512MB/2GB', 'cyan') + ' ' + colorize('███████▋', 'cyan') + colorize('         ', 'dim') + ' ' + colorize('│', 'blue'));
  console.log(colorize('│', 'blue') + ' CPU Trend: ' + colorize(createSparkline(cpuHistory), 'green') + '            Memory Trend: ' + colorize(createSparkline(memoryHistory), 'cyan') + '         ' + colorize('│', 'blue'));
  console.log(colorize('│', 'blue') + ' Disk I/O: ' + colorize('Low', 'green') + '     Network: ' + colorize('Normal', 'green') + '     Load Avg: ' + colorize('0.45, 0.52, 0.48', 'white') + '   ' + colorize('│', 'blue'));
  console.log(colorize('└───────────────────────────────────────────────────────────────────────────┘', 'blue'));
  console.log('');

  // Performance metrics dashboard - enhanced
  console.log(colorize('╔══ 📊 Performance Metrics (Last 24 Hours) ═══════════════════════════════╗', 'cyan'));
  console.log(colorize('║', 'cyan') + ' Search Operations                           │  Database Performance           ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' ─────────────────                           │  ──────────────────           ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Average Latency: ' + colorize('168ms', 'green') + '                   │  • Query Time: ' + colorize('145ms avg', 'green') + '       ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • P95 Latency: ' + colorize('285ms', 'yellow') + '                      │  • Index Size: ' + colorize('2.1GB', 'white') + '         ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • P99 Latency: ' + colorize('450ms', 'yellow') + '                      │  • Compression: ' + colorize('68%', 'cyan') + '         ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Total Searches: ' + colorize('2,847', 'blue') + '                    │  • Fragmentation: ' + colorize('Low', 'green') + '       ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Success Rate: ' + colorize('99.96%', 'green') + '                    │  • Backup Status: ' + colorize('✓ Current', 'green') + '  ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Error Rate: ' + colorize('0.04%', 'green') + ' (' + colorize('1 error', 'red') + ')            │  • Last Optimization: ' + colorize('1d ago', 'dim') + ' ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + '                                              │                                 ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' Enhancement Pipeline                         │  MCP Tools Status               ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' ──────────────────                           │  ───────────────               ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Jobs Processed: ' + colorize('156 completed', 'blue') + '             │  • Tools Active: ' + colorize('20/20', 'green') + '         ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Success Rate: ' + colorize('99.4%', 'green') + '                     │  • Response Time: ' + colorize('<50ms', 'green') + '      ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Queue Length: ' + colorize('0', 'green') + '                         │  • Memory Usage: ' + colorize('125MB', 'cyan') + '       ' + colorize('║', 'cyan'));
  console.log(colorize('║', 'cyan') + ' • Avg Processing: ' + colorize('2.3s', 'cyan') + '                    │  • Connection Pool: ' + colorize('Healthy', 'green') + '   ' + colorize('║', 'cyan'));
  console.log(colorize('╚══════════════════════════════════════════════════════════════════════════╝', 'cyan'));
  console.log('');

  // Active Monitoring Alerts
  console.log(colorize('┌─ 🔔 System Alerts & Notifications ───────────────────────────────────────┐', 'yellow'));
  console.log(colorize('│', 'yellow') + ' ' + colorize('ℹ️  INFO:', 'blue') + ' Scheduled maintenance window: Sunday 2AM-4AM PST           ' + colorize('│', 'yellow'));
  console.log(colorize('│', 'yellow') + ' ' + colorize('✅ OK:', 'green') + ' All health checks passing - no issues detected              ' + colorize('│', 'yellow'));
  console.log(colorize('│', 'yellow') + ' ' + colorize('📈 PERF:', 'cyan') + ' Search performance 15% above baseline today               ' + colorize('│', 'yellow'));
  console.log(colorize('└───────────────────────────────────────────────────────────────────────────┘', 'yellow'));
  console.log('');

  // Quick Actions
  console.log(colorize('🚀 Quick Actions Available:', 'cyan'));
  console.log('  ' + colorize('• mcp-health --refresh 10', 'white') + colorize(' - Enable auto-refresh every 10 seconds', 'dim'));
  console.log('  ' + colorize('• mcp-health --alerts', 'white') + colorize(' - View detailed alert configuration', 'dim'));
  console.log('  ' + colorize('• mcp-health --export', 'white') + colorize(' - Export metrics to JSON/CSV', 'dim'));
  console.log('  ' + colorize('• mcp-health --history 7d', 'white') + colorize(' - View 7-day performance history', 'dim'));
  console.log('');
  console.log(colorize('Press Ctrl+C to exit', 'dim'));
}

// Handle graceful exit
process.on('SIGINT', () => {
  clearScreen();
  console.log(colorize('\n👋 Thanks for viewing the Health Dashboard demo!\n', 'green'));
  process.exit(0);
});

// Run the demo
demoHealthDashboard().then(() => {
  // Keep the display visible
  setInterval(() => {}, 1000);
}).catch(console.error);