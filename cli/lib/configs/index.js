/**
 * Master Configuration Index for All 20 MCP Tools
 * Provides unified access to tool configurations
 */

const searchToolsConfigs = require('./search-tools');
const healthToolsConfigs = require('./health-tools');
const processingToolsConfigs = require('./processing-tools');

// Additional tool configs (to be expanded for all 20 tools)
const additionalToolsConfigs = {
  // Context & Project Management (3 tools)
  get_project_context_summary: {
    toolName: 'get_project_context_summary',
    icon: '📁',
    description: 'Project-Specific Conversation Analysis',
    phases: [
      { label: '🔍 Detecting project context...', duration: 600 },
      { label: '📊 Analyzing conversation patterns...', duration: 1000 },
      { label: '🎯 Generating project insights...', duration: 800 }
    ],
    statsTable: { borderColor: 'green', headerColor: 'green' },
    resultsTable: { formatter: 'default' },
    tips: ['Provides project-aware conversation analysis', 'Helps understand project-specific patterns']
  },

  detect_current_project: {
    toolName: 'detect_current_project',
    icon: '🎯',
    description: 'Auto-Detect Working Directory Context',
    phases: [
      { label: '📂 Scanning working directory...', duration: 400 },
      { label: '🔍 Analyzing project structure...', duration: 600 },
      { label: '🎯 Identifying project type...', duration: 500 }
    ],
    statsTable: { borderColor: 'blue', headerColor: 'blue' },
    resultsTable: { formatter: 'default' },
    tips: ['Automatically detects current project context', 'Boosts search relevance for current work']
  },

  get_conversation_context_chain: {
    toolName: 'get_conversation_context_chain',
    icon: '🔗',
    description: 'Detailed Conversation Flow Analysis',
    phases: [
      { label: '🔍 Locating target message...', duration: 500 },
      { label: '🔗 Building context chain...', duration: 800 },
      { label: '📊 Analyzing relationships...', duration: 600 }
    ],
    statsTable: { borderColor: 'cyan', headerColor: 'cyan' },
    resultsTable: { formatter: 'default' },
    tips: ['Shows conversation flow and message relationships', 'Ideal for understanding solution context']
  },

  // Analytics & Learning Tools (2 tools)
  get_learning_insights: {
    toolName: 'get_learning_insights',
    icon: '🧠',
    description: 'Unified Learning Analytics',
    phases: [
      { label: '📊 Gathering learning data...', duration: 800 },
      { label: '🎯 Analyzing user patterns...', duration: 1000 },
      { label: '📈 Generating insights...', duration: 600 }
    ],
    statsTable: { borderColor: 'purple', headerColor: 'purple' },
    resultsTable: { formatter: 'default' },
    tips: ['Provides comprehensive learning analytics', 'Tracks system adaptation and improvement']
  },

  process_feedback_unified: {
    toolName: 'process_feedback_unified',
    icon: '💬',
    description: 'Unified Feedback Processing',
    phases: [
      { label: '🔍 Analyzing feedback content...', duration: 600 },
      { label: '🧠 Running semantic analysis...', duration: 800 },
      { label: '🎯 Applying adaptive learning...', duration: 700 }
    ],
    statsTable: { borderColor: 'green', headerColor: 'green' },
    resultsTable: { formatter: 'default' },
    tips: ['Processes user feedback for system improvement', 'Enables personalized user adaptation']
  },

  // Pattern Analysis & Adaptive Learning (4 tools)
  analyze_patterns_unified: {
    toolName: 'analyze_patterns_unified',
    icon: '🔍',
    description: 'Unified Pattern Analysis',
    phases: [
      { label: '🔍 Scanning conversation patterns...', duration: 900 },
      { label: '🧠 Running multimodal analysis...', duration: 1200 },
      { label: '🎯 Identifying solution patterns...', duration: 800 }
    ],
    statsTable: { borderColor: 'magenta', headerColor: 'magenta' },
    resultsTable: { formatter: 'default' },
    tips: ['Analyzes conversation patterns across all modes', 'Identifies successful solution strategies']
  },

  analyze_solution_feedback_patterns: {
    toolName: 'analyze_solution_feedback_patterns',
    icon: '🔄',
    description: 'Solution-Feedback Relationship Analysis',
    phases: [
      { label: '🔍 Identifying solution patterns...', duration: 700 },
      { label: '💬 Analyzing feedback relationships...', duration: 900 },
      { label: '📊 Building pattern insights...', duration: 600 }
    ],
    statsTable: { borderColor: 'blue', headerColor: 'blue' },
    resultsTable: { formatter: 'default' },
    tips: ['Specialized analysis of solution-feedback relationships', 'Improves solution quality assessment']
  },

  run_adaptive_learning_enhancement: {
    toolName: 'run_adaptive_learning_enhancement',
    icon: '🎓',
    description: 'Personalized User Adaptation System',
    phases: [
      { label: '👤 Analyzing user patterns...', duration: 800 },
      { label: '🌍 Applying cultural intelligence...', duration: 700 },
      { label: '🎯 Personalizing responses...', duration: 600 }
    ],
    statsTable: { borderColor: 'green', headerColor: 'green' },
    resultsTable: { formatter: 'default' },
    tips: ['Personalizes system behavior to user preferences', 'Includes cultural communication adaptation']
  },

  analyze_conversation_intelligence: {
    toolName: 'analyze_conversation_intelligence',
    icon: '🤖',
    description: 'Structured Intelligence Extraction',
    phases: [
      { label: '🧠 Running spaCy NER analysis...', duration: 600 },
      { label: '⚙️ Detecting tools and frameworks...', duration: 800 },
      { label: '🎯 Classifying solution patterns...', duration: 500 }
    ],
    statsTable: { borderColor: 'cyan', headerColor: 'cyan' },
    resultsTable: { formatter: 'default' },
    tips: ['Extracts structured intelligence from conversations', 'Provides detailed technical context analysis']
  },

  // System Utilities (1 tool) 
  force_database_connection_refresh: {
    toolName: 'force_database_connection_refresh',
    icon: '🔧',
    description: 'Database Connection Refresh',
    phases: [
      { label: '🔌 Closing stale connections...', duration: 300 },
      { label: '🔄 Refreshing database pool...', duration: 400 },
      { label: '✅ Validating new connections...', duration: 200 }
    ],
    statsTable: { borderColor: 'yellow', headerColor: 'yellow' },
    resultsTable: { formatter: 'default' },
    tips: ['Resolves database connection issues', 'Use when experiencing connection problems']
  }
};

// Combine all tool configurations
const allToolConfigs = {
  ...searchToolsConfigs,
  ...healthToolsConfigs,
  ...processingToolsConfigs,
  ...additionalToolsConfigs
};

// Tool categories for organization
const toolCategories = {
  'Search & Retrieval': ['search_conversations_unified', 'search_with_hybrid_intelligence'],
  'Context & Project Management': ['get_project_context_summary', 'detect_current_project', 'get_conversation_context_chain'],
  'Data Processing & Sync': ['force_conversation_sync', 'backfill_conversation_chains', 'smart_metadata_sync_status'],
  'Analytics & Learning': ['get_learning_insights', 'process_feedback_unified'],
  'Enhancement System Management': ['run_unified_enhancement', 'get_system_status', 'configure_enhancement_systems'],
  'Pattern Analysis & Adaptive Learning': ['analyze_patterns_unified', 'analyze_solution_feedback_patterns', 'get_performance_analytics_dashboard', 'run_adaptive_learning_enhancement'],
  'Hybrid Intelligence System': ['search_with_hybrid_intelligence', 'analyze_conversation_intelligence', 'get_hybrid_system_health'],
  'System Utilities': ['force_database_connection_refresh']
};

function getToolConfig(toolName) {
  return allToolConfigs[toolName] || null;
}

function getToolsByCategory(category) {
  return toolCategories[category] || [];
}

function getAllTools() {
  return Object.keys(allToolConfigs);
}

function getToolCategories() {
  return Object.keys(toolCategories);
}

module.exports = {
  allToolConfigs,
  toolCategories,
  getToolConfig,
  getToolsByCategory,
  getAllTools,
  getToolCategories
};