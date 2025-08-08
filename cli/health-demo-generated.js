#!/usr/bin/env node

/**
 * Generated Health Demo - Using the MCP Tool UI Generator
 * Demonstrates the health dashboard using the modular system
 */

const MCPToolUIGenerator = require('./ui-generator');
const { getToolConfig } = require('./configs');

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

async function runHealthDemo() {
  // Get configuration for health tool
  const config = getToolConfig('get_system_status');
  
  // Add demo parameters
  config.parameters = {
    'Status Type': 'comprehensive',
    'Include Analytics': true,
    'Format': 'detailed'
  };

  // Initialize UI generator
  const ui = new MCPToolUIGenerator(config);
  
  // Generate sample metrics
  const latencyHistory = Array.from({length: 10}, () => Math.floor(Math.random() * 100) + 120);
  const cpuHistory = Array.from({length: 10}, () => Math.floor(Math.random() * 30) + 15);

  // Sample data (would come from actual MCP tool execution)
  const demoData = {
    stats: [
      ['System Component', 'Status'],
      ['Overall System Health', '🟢 All Systems Operational'],
      ['Last Updated', new Date().toLocaleString()],
      ['Auto-refresh', '5s'],
      ['Total Components Monitored', '4'],
      ['Healthy Components', '4/4'],
      ['Warning Indicators', '0'],
      ['Critical Issues', '0']
    ],
    statsTitle: 'System Overview',
    
    results: [
      {
        icon: '🟢',
        name: 'Vector Database',
        status: 'Healthy',
        metric: '145ms avg latency',
        trend: createSparkline(latencyHistory)
      },
      {
        icon: '🟢',
        name: 'MCP Server',
        status: 'Healthy', 
        metric: '20/20 tools active',
        trend: '████████▉▉'
      },
      {
        icon: '🟢',
        name: 'Enhancement Pipeline',
        status: 'Healthy',
        metric: '99.6% coverage',
        trend: '█████▉▉▉▉▉'
      },
      {
        icon: '🟢',
        name: 'Performance Cache',
        status: 'Healthy',
        metric: '87% hit rate',
        trend: '██████▉▉▉▉'
      }
    ],
    resultsTitle: 'Component Status Overview'
  };

  // Render the complete UI
  await ui.render(demoData);
}

// Run the demo
runHealthDemo().catch(console.error);