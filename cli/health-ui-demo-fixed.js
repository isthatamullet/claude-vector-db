#!/usr/bin/env node

/**
 * Individual Health Dashboard UI Demo - FIXED VERSION  
 * Shows enhanced get_system_status interface with properly aligned boxes
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

// Helper function to get string length without ANSI codes
function getVisualLength(str) {
  return str.replace(/\x1b\[[0-9;]*m/g, '').length;
}

// Helper function to pad string to exact visual width
function padToWidth(str, width) {
  const visualLength = getVisualLength(str);
  const padding = width - visualLength;
  return str + ' '.repeat(Math.max(0, padding));
}

// Helper function to create properly aligned box line
function createBoxLine(content, width, borderColor = 'green') {
  const paddedContent = padToWidth(content, width - 2); // -2 for borders
  return colorize('│', borderColor) + paddedContent + colorize('│', borderColor);
}

function clearScreen() {
  process.stdout.write('\x1b[2J\x1b[0f');
}

function getStatusIcon(status) {
  return status === 'healthy' ? '🟢' : status === 'warning' ? '🟡' : '🔴';
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
  
  console.log(colorize('🏥 get_system_status', 'blue') + colorize(' (Enhanced Health Dashboard - FIXED)', 'bright'));
  console.log('');
  console.log(colorize('System Health Overview', 'gray') + ' '.repeat(40) + colorize('🟢 All Systems Operational', 'green'));
  console.log(colorize('Last Updated: ', 'dim') + colorize(new Date().toLocaleString(), 'white') + ' '.repeat(20) + colorize('Auto-refresh: 5s', 'dim'));
  console.log('');

  // Generate some sample metrics for sparklines
  const latencyHistory = Array.from({length: 20}, () => Math.floor(Math.random() * 100) + 120);
  const cpuHistory = Array.from({length: 20}, () => Math.floor(Math.random() * 30) + 15);
  const memoryHistory = Array.from({length: 20}, () => Math.floor(Math.random() * 200) + 400);

  // Fixed component status grid with proper alignment
  const componentWidth = 39;
  
  // First row
  console.log(colorize('┌─ 🟢 Vector Database ─────────────────┐', 'green') + '  ' + colorize('┌─ 🟢 MCP Server ─────────────────────┐', 'green'));
  console.log(createBoxLine(' Status: ' + colorize('Healthy', 'green'), componentWidth, 'green') + '  ' + createBoxLine(' Status: ' + colorize('Healthy', 'green'), componentWidth, 'green'));
  console.log(createBoxLine(' ⚡ Avg Latency: ' + colorize('145ms', 'cyan'), componentWidth, 'green') + '  ' + createBoxLine(' 🔧 Active Tools: ' + colorize('20/20', 'cyan'), componentWidth, 'green'));
  console.log(createBoxLine(' 📊 Total Entries: ' + colorize('31,245', 'white'), componentWidth, 'green') + '  ' + createBoxLine(' ⏱️  Uptime: ' + colorize('2d 14h 23m', 'white'), componentWidth, 'green'));
  console.log(createBoxLine(' 💾 Storage Used: ' + colorize('2.1GB', 'white'), componentWidth, 'green') + '  ' + createBoxLine(' 🔄 Requests Today: ' + colorize('1,247', 'white'), componentWidth, 'green'));
  console.log(createBoxLine(' 🔍 Last Search: ' + colorize('12s ago', 'dim'), componentWidth, 'green') + '  ' + createBoxLine(' 📈 Success Rate: ' + colorize('99.8%', 'green'), componentWidth, 'green'));
  console.log(createBoxLine(' 📈 Trend: ' + colorize(createSparkline(latencyHistory), 'cyan'), componentWidth, 'green') + '  ' + createBoxLine(' 🌐 Connections: ' + colorize('Active', 'green'), componentWidth, 'green'));
  console.log(colorize('└───────────────────────────────────────┘', 'green') + '  ' + colorize('└─────────────────────────────────────────┘', 'green'));
  console.log('');
  
  // Second row  
  console.log(colorize('┌─ 🟢 Enhancement Pipeline ────────────┐', 'green') + '  ' + colorize('┌─ 🟢 Performance Cache ──────────────┐', 'green'));
  console.log(createBoxLine(' Status: ' + colorize('Healthy', 'green'), componentWidth, 'green') + '  ' + createBoxLine(' Status: ' + colorize('Healthy', 'green'), componentWidth, 'green'));
  console.log(createBoxLine(' 📈 Metadata Coverage: ' + colorize('99.6%', 'cyan'), componentWidth, 'green') + '  ' + createBoxLine(' 🎯 Hit Rate: ' + colorize('87%', 'yellow'), componentWidth, 'green'));
  console.log(createBoxLine(' ⚙️  Processing Queue: ' + colorize('0 jobs', 'green'), componentWidth, 'green') + '  ' + createBoxLine(' 💾 Cache Size: ' + colorize('245MB', 'white'), componentWidth, 'green'));
  console.log(createBoxLine(' 🎯 Quality Score: ' + colorize('Excellent', 'green'), componentWidth, 'green') + '  ' + createBoxLine(' 🧹 Last Cleanup: ' + colorize('2h ago', 'dim'), componentWidth, 'green'));
  console.log(createBoxLine(' 🔄 Last Enhancement: ' + colorize('3m ago', 'dim'), componentWidth, 'green') + '  ' + createBoxLine(' ⚡ Avg Retrieval: ' + colorize('12ms', 'cyan'), componentWidth, 'green'));
  console.log(createBoxLine(' 📊 Processed Today: ' + colorize('156', 'white'), componentWidth, 'green') + '  ' + createBoxLine(' 📈 Trend: ' + colorize(createSparkline([85, 87, 89, 87, 88, 87, 86, 87, 87, 88]), 'yellow'), componentWidth, 'green'));
  console.log(colorize('└───────────────────────────────────────┘', 'green') + '  ' + colorize('└─────────────────────────────────────────┘', 'green'));
  console.log('');

  // Fixed system resources section
  const resourcesWidth = 75;
  console.log(colorize('┌─ 💻 System Resources ────────────────────────────────────────────────────┐', 'blue'));
  console.log(createBoxLine(' CPU Usage: ' + colorize('23%', 'green') + ' ' + colorize('████▎', 'green') + '                  Memory: ' + colorize('512MB/2GB', 'cyan') + ' ' + colorize('███████▋', 'cyan'), resourcesWidth, 'blue'));
  console.log(createBoxLine(' CPU Trend: ' + colorize(createSparkline(cpuHistory), 'green') + '            Memory Trend: ' + colorize(createSparkline(memoryHistory), 'cyan'), resourcesWidth, 'blue'));
  console.log(createBoxLine(' Disk I/O: ' + colorize('Low', 'green') + '     Network: ' + colorize('Normal', 'green') + '     Load Avg: ' + colorize('0.45, 0.52, 0.48', 'white'), resourcesWidth, 'blue'));
  console.log(colorize('└───────────────────────────────────────────────────────────────────────────┘', 'blue'));
  console.log('');

  // Fixed performance metrics dashboard
  const metricsWidth = 74;
  console.log(colorize('╔══ 📊 Performance Metrics (Last 24 Hours) ═══════════════════════════════╗', 'cyan'));
  console.log(createBoxLine(' Search Operations                           │  Database Performance', metricsWidth, 'cyan'));
  console.log(createBoxLine(' ─────────────────                           │  ──────────────────', metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Average Latency: ' + colorize('168ms', 'green') + '                   │  • Query Time: ' + colorize('145ms avg', 'green'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • P95 Latency: ' + colorize('285ms', 'yellow') + '                      │  • Index Size: ' + colorize('2.1GB', 'white'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • P99 Latency: ' + colorize('450ms', 'yellow') + '                      │  • Compression: ' + colorize('68%', 'cyan'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Total Searches: ' + colorize('2,847', 'blue') + '                    │  • Fragmentation: ' + colorize('Low', 'green'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Success Rate: ' + colorize('99.96%', 'green') + '                    │  • Backup Status: ' + colorize('✓ Current', 'green'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Error Rate: ' + colorize('0.04%', 'green') + ' (' + colorize('1 error', 'red') + ')            │  • Last Optimization: ' + colorize('1d ago', 'dim'), metricsWidth, 'cyan'));
  console.log(createBoxLine('                                              │', metricsWidth, 'cyan'));
  console.log(createBoxLine(' Enhancement Pipeline                         │  MCP Tools Status', metricsWidth, 'cyan'));
  console.log(createBoxLine(' ──────────────────                           │  ───────────────', metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Jobs Processed: ' + colorize('156 completed', 'blue') + '             │  • Tools Active: ' + colorize('20/20', 'green'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Success Rate: ' + colorize('99.4%', 'green') + '                     │  • Response Time: ' + colorize('<50ms', 'green'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Queue Length: ' + colorize('0', 'green') + '                         │  • Memory Usage: ' + colorize('125MB', 'cyan'), metricsWidth, 'cyan'));
  console.log(createBoxLine(' • Avg Processing: ' + colorize('2.3s', 'cyan') + '                    │  • Connection Pool: ' + colorize('Healthy', 'green'), metricsWidth, 'cyan'));
  console.log(colorize('╚══════════════════════════════════════════════════════════════════════════╝', 'cyan'));
  console.log('');

  // Fixed active monitoring alerts
  const alertsWidth = 75;
  console.log(colorize('┌─ 🔔 System Alerts & Notifications ───────────────────────────────────────┐', 'yellow'));
  console.log(createBoxLine(' ' + colorize('ℹ️  INFO:', 'blue') + ' Scheduled maintenance window: Sunday 2AM-4AM PST', alertsWidth, 'yellow'));
  console.log(createBoxLine(' ' + colorize('✅ OK:', 'green') + ' All health checks passing - no issues detected', alertsWidth, 'yellow'));
  console.log(createBoxLine(' ' + colorize('📈 PERF:', 'cyan') + ' Search performance 15% above baseline today', alertsWidth, 'yellow'));
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