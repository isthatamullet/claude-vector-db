#!/usr/bin/env node

/**
 * MCP Tool CLI UI Generator - Modular System for All 20 Tools
 * Provides reusable components for professional Terminal Kit interfaces
 */

const term = require('terminal-kit').terminal;

class MCPToolUIGenerator {
  constructor(config) {
    this.config = config;
    this.currentPhase = 0;
    this.startTime = Date.now();
  }

  // Clear screen and initialize
  initialize() {
    term.clear();
    this.renderHeader();
  }

  // Render tool header with icon, name, and parameters
  renderHeader() {
    const { toolName, icon, description, parameters = {} } = this.config;
    
    term.blue.bold(`${icon} ${toolName}`);
    term.bold(` (${description || 'Enhanced UI'})\n\n`);
    
    // Display parameters if provided
    Object.entries(parameters).forEach(([key, value]) => {
      term.gray(`${key}: `);
      this.colorizeValue(value);
      term('\n');
    });
    term('\n');
  }

  // Smart value colorization
  colorizeValue(value) {
    if (typeof value === 'boolean') {
      term[value ? 'green' : 'red'](value.toString());
    } else if (typeof value === 'number') {
      term.cyan(value.toString());
    } else if (value.includes('.') && value.split('.').length === 2) {
      term.green(value); // Project names
    } else {
      term.white(value);
    }
  }

  // Progress indicator with phases
  async runProgressPhases() {
    const { phases = [] } = this.config;
    
    if (phases.length === 0) return;

    const progressBarWidth = 50;
    
    for (let i = 0; i < phases.length; i++) {
      const phase = phases[i];
      
      // Update phase label
      term.moveTo(1, 8);
      term.yellow(phase.label);
      term.eraseLineAfter();
      term('\n');
      
      // Update progress bar
      const percentage = ((i + 1) / phases.length);
      const filled = Math.floor(percentage * progressBarWidth);
      const empty = progressBarWidth - filled;
      
      term.cyan('█'.repeat(filled));
      term.dim('░'.repeat(empty));
      term(` ${Math.round(percentage * 100)}%\n`);
      
      await new Promise(resolve => setTimeout(resolve, phase.duration || 1000));
    }

    // Show completion
    term.moveTo(1, 8);
    term.green('✅ Operation complete! ');
    term.gray(`(${Date.now() - this.startTime}ms)`);
    term.eraseLineAfter();
    term('\n\n');
  }

  // Render statistics table
  renderStatsTable(data, title = 'Statistics') {
    const { statsTable = {} } = this.config;
    const {
      borderColor = 'cyan',
      headerColor = 'cyan',
      valueColor = 'white',
      keyColor = 'yellow'
    } = statsTable;

    if (!data || data.length === 0) return;

    term[headerColor].bold(`📊 ${title}\n`);
    
    term.table(data, {
      hasBorder: true,
      borderChars: 'lightRounded',
      borderAttr: { color: borderColor },
      textAttr: { color: valueColor },
      firstRowTextAttr: { color: headerColor, bold: true },
      firstColumnTextAttr: { color: keyColor },
      width: 65,
      fit: true
    });
    
    term('\n');
  }

  // Render results with flexible formatting
  renderResults(results, title = 'Results') {
    const { resultsTable = {} } = this.config;
    const {
      borderColor = 'gray',
      headerColor = 'white',
      formatter = 'default'
    } = resultsTable;

    if (!results || results.length === 0) return;

    term.cyan.bold(`🎯 ${title}\n\n`);

    // Different formatters for different result types
    switch (formatter) {
      case 'searchResults':
        this.renderSearchResults(results, borderColor, headerColor);
        break;
      case 'healthMetrics':
        this.renderHealthMetrics(results, borderColor, headerColor);
        break;
      case 'processingStatus':
        this.renderProcessingStatus(results, borderColor, headerColor);
        break;
      default:
        this.renderDefaultResults(results, borderColor, headerColor);
    }
  }

  // Search results formatter
  renderSearchResults(results, borderColor, headerColor) {
    results.forEach((result, index) => {
      const tableData = [
        ['Rank', 'Score', 'Project', 'Timestamp'],
        [result.rank || `#${index + 1}`, result.score, result.project, result.timestamp],
        ['Snippet', result.snippet || result.content],
        [`Tools: ${result.tools}`, `Category: ${result.category}`]
      ];

      term.table(tableData, {
        hasBorder: true,
        borderChars: 'lightRounded',
        borderAttr: { color: borderColor },
        textAttr: { color: 'white' },
        firstRowTextAttr: { color: headerColor, bold: true },
        firstColumnTextAttr: { color: 'yellow' },
        width: 75,
        fit: true
      });
      term('\n');
    });
  }

  // Health metrics formatter
  renderHealthMetrics(components, borderColor, headerColor) {
    term.table([
      ['Component', 'Status', 'Key Metric', 'Trend'],
      ...components.map(comp => [
        `${comp.icon} ${comp.name}`,
        comp.status,
        comp.metric,
        comp.trend || '████████▉▉'
      ])
    ], {
      hasBorder: true,
      borderChars: 'lightRounded',
      borderAttr: { color: borderColor },
      textAttr: { color: 'white' },
      firstRowTextAttr: { color: headerColor, bold: true },
      firstColumnTextAttr: { color: 'yellow' },
      width: 75,
      fit: true
    });
    term('\n');
  }

  // Processing status formatter (for sync, enhancement tools)
  renderProcessingStatus(files, borderColor, headerColor) {
    const tableData = [['Status', 'File', 'Added', 'Updated']];
    
    files.forEach(file => {
      const statusIcon = file.status === 'error' ? '❌' : 
                        file.status === 'skipped' ? '⏭️' : '✅';
      tableData.push([
        statusIcon,
        file.name.slice(0, 35),
        file.status === 'success' ? `+${file.added}` : file.status,
        file.status === 'success' ? `~${file.updated}` : ''
      ]);
    });

    term.table(tableData, {
      hasBorder: true,
      borderChars: 'lightRounded',
      borderAttr: { color: borderColor },
      textAttr: { color: 'white' },
      firstRowTextAttr: { color: headerColor, bold: true },
      width: 65,
      fit: true
    });
    term('\n');
  }

  // Default results formatter
  renderDefaultResults(results, borderColor, headerColor) {
    if (Array.isArray(results[0])) {
      // Already in table format
      term.table(results, {
        hasBorder: true,
        borderChars: 'lightRounded',
        borderAttr: { color: borderColor },
        textAttr: { color: 'white' },
        firstRowTextAttr: { color: headerColor, bold: true },
        firstColumnTextAttr: { color: 'yellow' },
        width: 70,
        fit: true
      });
    } else {
      // Convert object array to table
      if (results.length > 0) {
        const headers = Object.keys(results[0]);
        const tableData = [headers, ...results.map(r => headers.map(h => r[h]))];
        
        term.table(tableData, {
          hasBorder: true,
          borderChars: 'lightRounded',
          borderAttr: { color: borderColor },
          textAttr: { color: 'white' },
          firstRowTextAttr: { color: headerColor, bold: true },
          width: 70,
          fit: true
        });
      }
    }
    term('\n');
  }

  // Render footer with action suggestions
  renderFooter() {
    const { actions = [], tips = [] } = this.config;

    if (actions.length > 0) {
      term.cyan.bold('🚀 Available Actions:\n');
      actions.forEach(action => {
        term('  • ');
        term.white(action.command);
        term.dim(` - ${action.description}\n`);
      });
      term('\n');
    }

    if (tips.length > 0) {
      term.yellow.bold('💡 Pro Tips:\n');
      tips.forEach(tip => {
        term(`  • ${tip}\n`);
      });
      term('\n');
    }

    term.dim('Press Ctrl+C to exit\n');
  }

  // Complete UI workflow
  async render(data = {}) {
    this.initialize();
    
    if (this.config.phases) {
      await this.runProgressPhases();
    }
    
    if (data.stats) {
      this.renderStatsTable(data.stats, data.statsTitle);
    }
    
    if (data.results) {
      this.renderResults(data.results, data.resultsTitle);
    }
    
    this.renderFooter();
    
    // Keep display visible
    return new Promise(() => {
      process.on('SIGINT', () => {
        term.clear();
        term.green(`\n👋 Thanks for using ${this.config.toolName}!\n`);
        process.exit(0);
      });
    });
  }
}

module.exports = MCPToolUIGenerator;