/**
 * Processing Commands - CLI wrappers for processing and sync MCP tools
 */

const MCPToolUIGenerator = require('../ui-generator');
const { defaultClient } = require('../mcp-client');
const { transformMCPResponse } = require('../data-transformer');
const { getToolConfig } = require('../configs');

/**
 * Execute force_conversation_sync with CLI UI and progress updates
 */
async function forceSync(options = {}) {
  const toolName = 'force_conversation_sync';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Mode': options.fullRebuild ? 'Full rebuild from scratch' : 'Incremental sync',
    'Parallel Processing': options.parallel !== false ? 'enabled' : 'disabled',
    'File Path': options.filePath || 'All files',
    'Enhancement': options.enhancement !== false ? 'enabled' : 'disabled'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    // For long-running sync operations, we might want to implement streaming
    const mcpResponse = await defaultClient.callTool(toolName, {
      parallel_processing: options.parallel !== false,
      file_path: options.filePath,
      full_rebuild: options.fullRebuild || false
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
    console.error(`\n❌ Sync operation failed: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Execute run_unified_enhancement with CLI UI
 */
async function unifiedEnhancement(options = {}) {
  const toolName = 'run_unified_enhancement';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Session ID': options.sessionId || 'All sessions',
    'Enable Backfill': options.backfill !== false ? 'enabled' : 'disabled',
    'Enable Optimization': options.optimization !== false ? 'enabled' : 'disabled',
    'Max Sessions': options.maxSessions || 'No limit'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      session_id: options.sessionId,
      enable_backfill: options.backfill !== false,
      enable_optimization: options.optimization !== false,
      enable_validation: options.validation !== false,
      max_sessions: options.maxSessions || 0,
      force_reprocess_fields: options.reprocessFields,
      create_backup: options.backup !== false
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
    console.error(`\n❌ Enhancement operation failed: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Execute backfill_conversation_chains with CLI UI
 */
async function backfillChains(options = {}) {
  const toolName = 'backfill_conversation_chains';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Session ID': options.sessionId || 'All sessions',
    'Limit': options.limit || '10 sessions',
    'Field Types': options.fieldTypes || 'chains'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      session_id: options.sessionId,
      limit: options.limit || 10,
      field_types: options.fieldTypes || 'chains'
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
    console.error(`\n❌ Chain backfill failed: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Execute smart_metadata_sync_status with CLI UI
 */
async function metadataStatus(options = {}) {
  const toolName = 'smart_metadata_sync_status';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Analysis Type': options.type || 'comprehensive',
    'Include Recommendations': options.recommendations !== false ? 'enabled' : 'disabled',
    'Export Format': options.export || 'none'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      detailed: options.detailed !== false,
      recommendations: options.recommendations !== false,
      export_format: options.export
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
    console.error(`\n❌ Metadata status check failed: ${error.message}\n`);
    process.exit(1);
  }
}

module.exports = {
  forceSync,
  unifiedEnhancement,
  backfillChains,
  metadataStatus
};