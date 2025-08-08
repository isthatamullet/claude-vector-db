/**
 * Search Commands - CLI wrappers for search and retrieval MCP tools
 */

const MCPToolUIGenerator = require('../ui-generator');
const { defaultClient } = require('../mcp-client');
const { transformMCPResponse } = require('../data-transformer');
const { getToolConfig } = require('../configs');

/**
 * Execute search_conversations_unified with CLI UI
 */
async function searchConversations(query, options = {}) {
  const toolName = 'search_conversations_unified';
  const config = getToolConfig(toolName);
  
  // Add runtime parameters to config
  config.parameters = {
    'Query': `"${query}"`,
    'Project Context': options.project || 'auto-detect',
    'Search Mode': options.mode || 'semantic',
    'Enhancement': options.enhancement !== false ? 'enabled' : 'disabled'
  };

  // Initialize UI generator
  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    // Show progress phases
    if (config.phases) {
      await ui.runProgressPhases();
    }

    // Call MCP tool
    const mcpResponse = await defaultClient.callTool(toolName, {
      query: query,
      project_context: options.project,
      search_mode: options.mode || 'semantic',
      limit: options.limit || 5,
      include_code_only: options.codeOnly || false,
      use_validation_boost: options.validationBoost !== false,
      use_adaptive_learning: options.adaptiveLearning !== false,
      include_context_chains: options.contextChains || false,
      enable_hybrid_intelligence: options.hybrid || false,
      hybrid_tool_filter: options.toolFilter,
      hybrid_framework_filter: options.frameworkFilter,
      hybrid_min_confidence: options.minConfidence,
      hybrid_pattern_type: options.patternType
    });

    // Transform response to UI format
    const uiData = transformMCPResponse(mcpResponse, toolName);
    
    // Display results
    if (uiData.stats) {
      ui.renderStatsTable(uiData.stats, uiData.statsTitle);
    }
    
    if (uiData.results) {
      ui.renderResults(uiData.results, uiData.resultsTitle);
    }
    
    ui.renderFooter();

    // Keep display visible
    return new Promise(() => {
      process.on('SIGINT', () => {
        process.exit(0);
      });
    });

  } catch (error) {
    console.error(`\n❌ Search failed: ${error.message}\n`);
    process.exit(1);
  }
}

/**
 * Execute search_with_hybrid_intelligence with CLI UI
 */
async function hybridSearch(query, options = {}) {
  const toolName = 'search_with_hybrid_intelligence';
  const config = getToolConfig(toolName);
  
  config.parameters = {
    'Query': `"${query}"`,
    'Tool Filter': options.toolFilter || 'any',
    'Framework Filter': options.frameworkFilter || 'any',
    'Min Confidence': options.minConfidence || '0.7',
    'Pattern Type': options.patternType || 'any'
  };

  const ui = new MCPToolUIGenerator(config);
  ui.initialize();

  try {
    if (config.phases) {
      await ui.runProgressPhases();
    }

    const mcpResponse = await defaultClient.callTool(toolName, {
      query: query,
      project_context: options.project,
      tool_filter: options.toolFilter,
      framework_filter: options.frameworkFilter,
      min_confidence: options.minConfidence,
      pattern_type: options.patternType,
      limit: options.limit || 5
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
    console.error(`\n❌ Hybrid search failed: ${error.message}\n`);
    process.exit(1);
  }
}

module.exports = {
  searchConversations,
  hybridSearch
};