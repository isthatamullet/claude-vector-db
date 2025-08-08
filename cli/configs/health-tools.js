/**
 * Configuration for System Health & Analytics MCP Tools
 * - get_system_status
 * - get_performance_analytics_dashboard
 * - get_hybrid_system_health
 */

const healthToolsConfigs = {
  get_system_status: {
    toolName: 'get_system_status',
    icon: '🏥',
    description: 'Comprehensive System Health Dashboard',
    
    phases: [
      { label: '🔍 Checking system components...', duration: 800 },
      { label: '📊 Gathering performance metrics...', duration: 1000 },
      { label: '🔧 Validating MCP tool status...', duration: 600 },
      { label: '💾 Analyzing database health...', duration: 700 },
      { label: '📈 Generating health report...', duration: 400 }
    ],
    
    statsTable: {
      borderColor: 'green',
      headerColor: 'green',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'green',
      headerColor: 'green',
      formatter: 'healthMetrics'
    },
    
    tips: [
      'Check this dashboard regularly to monitor system performance',
      'Watch for warning indicators (🟡) that may need attention',
      'Performance metrics help optimize search and processing times',
      'Use --status-type=comprehensive for detailed analysis'
    ],
    
    actions: [
      { command: 'health --refresh 10', description: 'Enable auto-refresh every 10 seconds' },
      { command: 'health --export json', description: 'Export metrics to JSON format' },
      { command: 'health --alerts', description: 'View detailed alert configuration' },
      { command: 'health --history 7d', description: 'View 7-day performance history' }
    ]
  },

  get_performance_analytics_dashboard: {
    toolName: 'get_performance_analytics_dashboard',
    icon: '📊',
    description: 'Real-Time Performance Monitoring',
    
    phases: [
      { label: '⚡ Initializing analytics engine...', duration: 600 },
      { label: '📈 Collecting performance data...', duration: 1200 },
      { label: '🔍 Analyzing search latencies...', duration: 800 },
      { label: '💾 Processing cache metrics...', duration: 500 },
      { label: '📊 Building analytics dashboard...', duration: 700 }
    ],
    
    statsTable: {
      borderColor: 'cyan',
      headerColor: 'cyan',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'blue',
      headerColor: 'cyan',
      formatter: 'default'
    },
    
    tips: [
      'Monitor search latency to ensure sub-500ms performance targets',
      'Cache hit rates above 80% indicate good performance optimization',
      'Processing queue length should typically be 0 or very low',
      'Use performance trends to identify optimization opportunities'
    ],
    
    actions: [
      { command: 'analytics --time-range 24h', description: 'View 24-hour performance window' },
      { command: 'analytics --component search', description: 'Focus on search performance metrics' },
      { command: 'analytics --threshold-alert', description: 'Set performance threshold alerts' }
    ]
  },

  get_hybrid_system_health: {
    toolName: 'get_hybrid_system_health',
    icon: '🤖',
    description: 'Hybrid Intelligence System Status',
    
    phases: [
      { label: '🧠 Checking spaCy NLP models...', duration: 800 },
      { label: '🔍 Validating Sentence Transformers...', duration: 1000 },
      { label: '⚙️ Testing tool detection accuracy...', duration: 700 },
      { label: '🎯 Verifying framework recognition...', duration: 600 },
      { label: '📊 Generating intelligence report...', duration: 500 }
    ],
    
    statsTable: {
      borderColor: 'magenta',
      headerColor: 'magenta',
      valueColor: 'white',
      keyColor: 'yellow'
    },
    
    resultsTable: {
      borderColor: 'purple',
      headerColor: 'magenta',
      formatter: 'healthMetrics'
    },
    
    tips: [
      'Hybrid intelligence combines semantic search with structured extraction',
      'Tool detection accuracy should be above 90% for optimal filtering',
      'Framework recognition helps with technology-specific searches',
      'ML confidence scoring ensures high-quality results'
    ],
    
    actions: [
      { command: 'hybrid-health --test-extraction', description: 'Run intelligence extraction tests' },
      { command: 'hybrid-health --model-status', description: 'Check NLP model availability' },
      { command: 'hybrid-health --accuracy-report', description: 'Generate accuracy metrics report' }
    ]
  }
};

module.exports = healthToolsConfigs;