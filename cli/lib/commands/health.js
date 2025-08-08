/**
 * Health Commands - CLI wrappers for health and analytics MCP tools
 */

const MCPToolUIGenerator = require('../ui-generator');
const { defaultClient } = require('../mcp-client');
const { transformMCPResponse } = require('../data-transformer');
const { getToolConfig } = require('../configs');

/**
 * Execute get_system_status with CLI UI
 */
async function systemStatus(options = {}) {
  const toolName = 'get_system_status';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Status Type': options.type || 'comprehensive',
    'Include Analytics': options.analytics !== false ? 'true' : 'false',
    'Include Enhancement Metrics': options.enhancement !== false ? 'true' : 'false',
    'Format': options.format || 'detailed'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      status_type: options.type || 'comprehensive',
      include_analytics: options.analytics !== false,
      include_enhancement_metrics: options.enhancement !== false,
      include_semantic_health: options.semantic !== false,
      format: options.format || 'detailed'
    });

    const uiData = transformMCPResponse(mcpResponse, toolName);
    
    if (uiData.stats) {
      ui.renderStatsTable(uiData.stats, uiData.statsTitle);
    }
    
    if (uiData.results) {
      ui.renderResults(uiData.results, uiData.resultsTitle);
    }
    
    ui.renderFooter();

    return new Promise(() => {
      process.on('SIGINT', () => {
        process.exit(0);
      });
    });

  } catch (error) {
    console.error(`\n❌ System status check failed: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Execute get_performance_analytics_dashboard with CLI UI
 */
async function performanceAnalytics(options = {}) {
  const toolName = 'get_performance_analytics_dashboard';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Time Range': options.timeRange || '24h',
    'Component Focus': options.component || 'all',
    'Metrics Type': options.metrics || 'comprehensive'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      time_range: options.timeRange,
      component: options.component,
      metrics_type: options.metrics
    });

    const uiData = transformMCPResponse(mcpResponse, toolName);
    
    if (uiData.stats) {
      ui.renderStatsTable(uiData.stats, uiData.statsTitle);
    }
    
    if (uiData.results) {
      ui.renderResults(uiData.results, uiData.resultsTitle);
    }
    
    ui.renderFooter();

    return new Promise(() => {
      process.on('SIGINT', () => {
        process.exit(0);
      });
    });

  } catch (error) {
    console.error(`\n❌ Performance analytics failed: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Execute get_hybrid_system_health with CLI UI
 */
async function hybridSystemHealth(options = {}) {
  const toolName = 'get_hybrid_system_health';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Model Validation': options.models !== false ? 'enabled' : 'disabled',
    'Accuracy Testing': options.accuracy !== false ? 'enabled' : 'disabled',
    'Performance Check': options.performance !== false ? 'enabled' : 'disabled'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      validate_models: options.models !== false,
      test_accuracy: options.accuracy !== false,
      check_performance: options.performance !== false
    });

    const uiData = transformMCPResponse(mcpResponse, toolName);
    
    if (uiData.stats) {
      ui.renderStatsTable(uiData.stats, uiData.statsTitle);
    }
    
    if (uiData.results) {
      ui.renderResults(uiData.results, uiData.resultsTitle);
    }
    
    ui.renderFooter();

    return new Promise(() => {
      process.on('SIGINT', () => {
        process.exit(0);
      });
    });

  } catch (error) {
    console.error(`\n❌ Hybrid system health check failed: ${error.message}\n`);
    process.exit(1);
  }
}

module.exports = {
  systemStatus,
  performanceAnalytics,
  hybridSystemHealth
};