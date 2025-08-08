#!/usr/bin/env node

/**
 * Simple connection test for MCP server
 */

const { MCPClient } = require('../lib/mcp-client');
const chalk = require('chalk');

async function testConnection() {
  console.log(chalk.blue('🔍 Testing MCP server connection...'));
  
  // Try different common ports for MCP server
  const ports = [3001, 3000, 8000, 8001];
  
  for (const port of ports) {
    const client = new MCPClient(`http://localhost:${port}`, 5000);
    
    try {
      console.log(chalk.dim(`   Trying port ${port}...`));
      const isAlive = await client.isServerAlive();
      
      if (isAlive) {
        console.log(chalk.green(`✅ MCP server found at port ${port}`));
        
        try {
          const health = await client.getHealth();
          console.log(`📊 Server status: ${health.status || 'responding'}`);
        } catch (error) {
          console.log(chalk.yellow('⚠️  Server responding but no health endpoint'));
        }
        
        try {
          const tools = await client.listTools();
          console.log(`🔧 Available tools: ${tools.length || 'unknown'}`);
        } catch (error) {
          console.log(chalk.yellow('⚠️  Cannot list tools - server may use different API'));
        }
        
        console.log(chalk.green('\n✅ Connection test successful!'));
        console.log(chalk.dim('💡 You can now use: mcpui search "your query"'));
        return;
      }
      
    } catch (error) {
      console.log(chalk.dim(`   Port ${port}: ${error.message}`));
    }
  }
  
  console.log(chalk.red('\n❌ No MCP server found on common ports'));
  console.log(chalk.yellow('💡 Make sure your Python MCP server is running:'));
  console.log(chalk.dim('   cd /home/user/.claude-vector-db-enhanced'));
  console.log(chalk.dim('   ./venv/bin/python mcp/mcp_server.py'));
}

testConnection().catch(error => {
  console.error(chalk.red('❌ Test failed:'), error.message);
  process.exit(1);
});