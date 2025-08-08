/**
 * MCP Client - Node.js to Python MCP Server Communication
 * Handles all communication with the Claude Vector Database MCP Server
 */

const axios = require('axios');

class MCPClient {
  constructor(baseUrl = 'http://localhost:3001', timeout = 60000) {
    this.baseUrl = baseUrl;
    this.timeout = timeout;
    this.axios = axios.create({
      baseURL: baseUrl,
      timeout: timeout,
      headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'Claude-Vector-DB-CLI/1.0.0'
      }
    });

    // Add response interceptor for error handling
    this.axios.interceptors.response.use(
      response => response,
      error => {
        if (error.code === 'ECONNREFUSED') {
          throw new Error(`Cannot connect to MCP server at ${baseUrl}. Is your Python MCP server running?`);
        }
        if (error.response?.status === 404) {
          throw new Error(`MCP tool not found. Available tools: ${error.response.data?.available_tools?.join(', ') || 'unknown'}`);
        }
        throw error;
      }
    );
  }

  /**
   * Call an MCP tool with parameters
   * @param {string} toolName - Name of the MCP tool
   * @param {object} parameters - Tool parameters
   * @returns {Promise<object>} Tool response
   */
  async callTool(toolName, parameters = {}) {
    try {
      const response = await this.axios.post(`/tools/${toolName}`, {
        arguments: parameters
      });
      
      return response.data;
    } catch (error) {
      // Enhanced error reporting
      if (error.response?.data?.error) {
        throw new Error(`MCP Error: ${error.response.data.error}`);
      }
      throw error;
    }
  }

  /**
   * Get server health status
   * @returns {Promise<object>} Health status
   */
  async getHealth() {
    try {
      const response = await this.axios.get('/health');
      return response.data;
    } catch (error) {
      return { 
        status: 'error', 
        message: error.message,
        server_reachable: false 
      };
    }
  }

  /**
   * List available MCP tools
   * @returns {Promise<Array>} List of available tools
   */
  async listTools() {
    try {
      const response = await this.axios.get('/tools');
      return response.data.tools || [];
    } catch (error) {
      throw new Error(`Failed to list tools: ${error.message}`);
    }
  }

  /**
   * Check if MCP server is responding
   * @returns {Promise<boolean>} Server status
   */
  async isServerAlive() {
    try {
      await this.axios.get('/health', { timeout: 5000 });
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Get tool information
   * @param {string} toolName - Name of the tool
   * @returns {Promise<object>} Tool information
   */
  async getToolInfo(toolName) {
    try {
      const response = await this.axios.get(`/tools/${toolName}/info`);
      return response.data;
    } catch (error) {
      return null;
    }
  }

  /**
   * Stream tool execution for long-running operations
   * @param {string} toolName - Name of the MCP tool
   * @param {object} parameters - Tool parameters
   * @param {function} progressCallback - Progress callback function
   * @returns {Promise<object>} Final result
   */
  async streamTool(toolName, parameters = {}, progressCallback = null) {
    // For now, we'll simulate streaming with regular calls
    // This can be enhanced later with WebSocket or Server-Sent Events
    
    if (progressCallback) {
      progressCallback({ phase: 'starting', progress: 0 });
    }
    
    const result = await this.callTool(toolName, parameters);
    
    if (progressCallback) {
      progressCallback({ phase: 'completed', progress: 100 });
    }
    
    return result;
  }
}

/**
 * Default MCP client instance
 */
const defaultClient = new MCPClient();

module.exports = {
  MCPClient,
  defaultClient
};