/**
 * Data Transformer - Convert MCP JSON responses to UI format
 * Transforms raw MCP tool responses into Terminal Kit UI compatible data
 */

/**
 * Transform search results from MCP to UI format
 * @param {object} mcpResponse - Raw MCP search response
 * @returns {object} UI-compatible data structure
 */
function transformSearchResults(mcpResponse) {
  // Handle null/undefined response
  if (!mcpResponse) {
    return {
      stats: [['Metric', 'Value'], ['Error', 'No response data']],
      statsTitle: 'Search Error',
      results: [],
      resultsTitle: 'No Results'
    };
  }
  
  // Handle both old format and new enhanced format
  const results = mcpResponse.results || [];
  const metadata = mcpResponse.search_metadata || mcpResponse.metadata || {};
  const stats = mcpResponse.search_statistics || mcpResponse.stats || {};

  // Transform statistics table with enhanced format
  const statsData = [
    ['Metric', 'Value'],
    ['Total conversations in database', formatNumber(stats.total_database_entries || metadata.total_conversations || 0)],
    ['Project context filtered', `${formatNumber(stats.project_context_matches || metadata.filtered_count || 0)}${metadata.project_context ? ` (${metadata.project_context})` : ''}`],
    ['Semantic similarity matches', formatNumber(stats.results_returned || results.length)],
    ['Hybrid intelligence applied', metadata.hybrid_intelligence || stats.hybrid_intelligence_applied ? '✓' : '✗'],
    ['Cache hit rate', stats.cache_hit_rate ? `${Math.round(stats.cache_hit_rate)}%` : `${Math.round((stats.cache_hit_rate || 0) * 100)}%`],
    ['Response time', `${Math.round(stats.search_time_ms || stats.response_time_ms || 0)}ms${stats.target_ms ? ` (target: <${stats.target_ms}ms)` : ''}`]
  ];

  // Transform results for display (handle enhanced format)
  const transformedResults = results.map((result, index) => ({
    rank: `#${index + 1}`,
    score: result.relevance_score ? result.relevance_score.toFixed(3) : 
           (typeof result.score === 'number' ? result.score.toFixed(2) : result.score || '0.000'),
    project: result.metadata?.project_name || result.project_name || result.project || 'Unknown',
    snippet: truncateText(result.content || result.snippet || '', 80),
    timestamp: formatTimestamp(result.metadata?.timestamp || result.timestamp),
    tools: Array.isArray(result.metadata?.tools_used) ? result.metadata.tools_used.join(', ') : 
           (Array.isArray(result.tools_used) ? result.tools_used.join(', ') : (result.tools_used || 'None')),
    category: result.metadata?.solution_category || result.solution_category || result.category || 'General',
    hasCode: result.metadata?.has_code ? '✓' : '✗'
  }));

  return {
    stats: statsData,
    statsTitle: 'Enhanced Search Statistics',
    results: transformedResults,
    resultsTitle: `Search Results (${results.length} found)${metadata.project_context ? ` - ${metadata.project_context}` : ''}`
  };
}

/**
 * Transform health/system status from MCP to UI format
 * @param {object} mcpResponse - Raw MCP health response
 * @returns {object} UI-compatible data structure
 */
function transformHealthStatus(mcpResponse) {
  const { components = [], metrics = {}, alerts = [] } = mcpResponse;

  // Transform system overview
  const statsData = [
    ['System Component', 'Status'],
    ['Overall System Health', getOverallHealthIcon(components) + ' ' + getOverallHealthText(components)],
    ['Last Updated', new Date().toLocaleString()],
    ['Auto-refresh', '5s'],
    ['Total Components Monitored', components.length.toString()],
    ['Healthy Components', `${components.filter(c => c.status === 'healthy').length}/${components.length}`],
    ['Warning Indicators', components.filter(c => c.status === 'warning').length.toString()],
    ['Critical Issues', components.filter(c => c.status === 'error').length.toString()]
  ];

  // Transform components for display
  const transformedResults = components.map(component => ({
    icon: getStatusIcon(component.status),
    name: component.name || 'Unknown Component',
    status: capitalizeFirst(component.status || 'unknown'),
    metric: component.key_metric || component.metric || 'No data',
    trend: component.trend || generateMockTrend()
  }));

  return {
    stats: statsData,
    statsTitle: 'System Overview',
    results: transformedResults,
    resultsTitle: 'Component Status Overview'
  };
}

/**
 * Transform processing/sync status from MCP to UI format
 * @param {object} mcpResponse - Raw MCP processing response
 * @returns {object} UI-compatible data structure
 */
function transformProcessingStatus(mcpResponse) {
  const { 
    processed_files = [], 
    statistics = {}, 
    progress = {},
    errors = []
  } = mcpResponse;

  // Transform statistics
  const statsData = [
    ['Processing Metric', 'Value'],
    ['✅ Conversations Added', formatNumber(statistics.added || 0)],
    ['🔄 Conversations Updated', formatNumber(statistics.updated || 0)],
    ['📝 Total Entries Processed', formatNumber(statistics.total_entries || 0)],
    ['❌ Processing Errors', formatNumber(statistics.errors || errors.length)],
    ['⏭️ Files Skipped', formatNumber(statistics.skipped || 0)],
    ['⚡ Processing Rate', `${(statistics.files_per_second || 0).toFixed(1)} files/sec`],
    ['📈 Success Rate', `${((statistics.success_rate || 0) * 100).toFixed(1)}%`]
  ];

  // Transform file processing results
  const transformedResults = processed_files.slice(-10).map(file => ({
    name: truncateText(file.name || file.filename || 'Unknown', 35),
    status: file.status || 'unknown',
    added: file.added || 0,
    updated: file.updated || 0
  }));

  return {
    stats: statsData,
    statsTitle: 'Live Processing Statistics',
    results: transformedResults,
    resultsTitle: 'Recently Processed Files'
  };
}

/**
 * Generic transformer for unknown/simple responses
 * @param {object} mcpResponse - Raw MCP response
 * @returns {object} UI-compatible data structure
 */
function transformGenericResponse(mcpResponse) {
  // Try to extract meaningful data from any response
  if (typeof mcpResponse === 'string') {
    return {
      stats: [['Response', mcpResponse]],
      statsTitle: 'Tool Response'
    };
  }

  // Convert object to key-value pairs
  const entries = Object.entries(mcpResponse)
    .filter(([key, value]) => value !== null && value !== undefined)
    .map(([key, value]) => [
      humanizeKey(key),
      formatValue(value)
    ]);

  return {
    stats: [['Property', 'Value'], ...entries],
    statsTitle: 'Tool Response'
  };
}

/**
 * Main transformer function - routes to appropriate transformer
 * @param {object} mcpResponse - Raw MCP response
 * @param {string} toolName - Name of the MCP tool
 * @returns {object} UI-compatible data structure
 */
function transformMCPResponse(mcpResponse, toolName) {
  // Handle HTTP wrapper response format - extract the actual result
  let actualResponse = mcpResponse;
  
  // The HTTP wrapper returns: {result: actualData, status: "success", error: null}
  // We need to extract the 'result' field to get the real MCP tool response
  if (mcpResponse && typeof mcpResponse === 'object' && 'result' in mcpResponse && 'status' in mcpResponse) {
    // Check for error status
    if (mcpResponse.status !== 'success' || mcpResponse.error) {
      return {
        stats: [['Metric', 'Value'], ['Error', mcpResponse.error || 'Unknown error']],
        statsTitle: 'Tool Error',
        results: [],
        resultsTitle: 'Error Response'
      };
    }
    actualResponse = mcpResponse.result;
  }
  
  // Route to appropriate transformer based on tool name
  if (toolName.includes('search')) {
    return transformSearchResults(actualResponse);
  } else if (toolName.includes('health') || toolName.includes('status')) {
    return transformHealthStatus(actualResponse);
  } else if (toolName.includes('sync') || toolName.includes('enhancement') || toolName.includes('backfill')) {
    return transformProcessingStatus(actualResponse);
  } else {
    return transformGenericResponse(actualResponse);
  }
}

// Helper functions
function formatNumber(num) {
  return typeof num === 'number' ? num.toLocaleString() : num.toString();
}

function formatTimestamp(timestamp) {
  if (!timestamp) return 'Unknown';
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) return 'Today';
  if (diffDays === 1) return '1 day ago';
  if (diffDays < 7) return `${diffDays} days ago`;
  if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks ago`;
  return date.toLocaleDateString();
}

function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

function getStatusIcon(status) {
  const icons = {
    'healthy': '🟢',
    'warning': '🟡', 
    'error': '🔴',
    'unknown': '⚪'
  };
  return icons[status] || icons.unknown;
}

function getOverallHealthIcon(components) {
  const hasError = components.some(c => c.status === 'error');
  const hasWarning = components.some(c => c.status === 'warning');
  
  if (hasError) return '🔴';
  if (hasWarning) return '🟡';
  return '🟢';
}

function getOverallHealthText(components) {
  const hasError = components.some(c => c.status === 'error');
  const hasWarning = components.some(c => c.status === 'warning');
  
  if (hasError) return 'System Issues Detected';
  if (hasWarning) return 'System Warnings Present';
  return 'All Systems Operational';
}

function capitalizeFirst(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

function humanizeKey(key) {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function formatValue(value) {
  if (typeof value === 'boolean') return value ? '✓' : '✗';
  if (typeof value === 'number') return value.toLocaleString();
  if (Array.isArray(value)) return value.join(', ');
  if (typeof value === 'object') return JSON.stringify(value);
  return value.toString();
}

function generateMockTrend() {
  // Generate a simple trend indicator
  const chars = ['▁', '▂', '▃', '▄', '▅', '▆', '▇', '█'];
  return Array.from({length: 10}, () => chars[Math.floor(Math.random() * chars.length)]).join('');
}

module.exports = {
  transformMCPResponse,
  transformSearchResults,
  transformHealthStatus,
  transformProcessingStatus,
  transformGenericResponse
};