"""
Syntropy MCP TypeScript Implementation Patterns

Best practices for extending Syntropy MCP with new servers.
Reference: /syntropy-mcp/ implementation
"""

/**
 * ✅ PATTERN 1: Server Configuration
 * 
 * Location: servers.json (root of syntropy-mcp)
 * Use: Define new MCP servers for Syntropy aggregation
 */

// servers.json structure
const SERVER_CONFIG_PATTERN = {
  "servers": {
    "new-server": {
      "description": "Clear description of what server does",
      "spawn": {
        "command": "npx",  // or "uvx" for Python servers
        "args": ["new-server"]  // Package name or command
      },
      "env": {
        // Optional: Environment variables for server
        "API_KEY": "${process.env.NEW_SERVER_API_KEY}"
      }
    }
  }
};


/**
 * ✅ PATTERN 2: Tool Definition Interface
 * 
 * Use: Define tool schemas with strict typing
 * Best practice: Always include descriptions, required fields, examples
 */

interface ToolDefinition {
  name: string;           // Tool name (kebab-case)
  description: string;    // Clear description
  inputSchema: {
    type: "object";
    properties: Record<string, PropertySchema>;
    required: string[];   // Required parameter names
  };
}

interface PropertySchema {
  type: string;           // "string", "number", "boolean", "array", etc.
  description: string;    // What this parameter does
  items?: PropertySchema; // For arrays
  enum?: string[];        // For constrained values
  default?: any;          // Default value if optional
}

// Example: Find symbol tool definition
const FIND_SYMBOL_TOOL: ToolDefinition = {
  name: "find_symbol",
  description: "Find function/class definition by name with implementation",
  inputSchema: {
    type: "object",
    properties: {
      name_path: {
        type: "string",
        description: "Symbol name path (e.g., 'Class/method' or 'function_name')"
      },
      include_body: {
        type: "boolean",
        description: "Include function/class body in results",
        default: true
      }
    },
    required: ["name_path"]
  }
};


/**
 * ✅ PATTERN 3: Lazy Server Initialization
 * 
 * Best practice: Servers spawn on first use, not at startup
 * Benefit: Faster startup, shared connections, automatic cleanup
 */

class ServerPool {
  private servers: Map<string, any> = new Map();
  private spawning: Map<string, Promise<any>> = new Map();
  
  async getServer(name: string): Promise<any> {
    // Return existing connection
    if (this.servers.has(name)) {
      return this.servers.get(name);
    }
    
    // Avoid duplicate spawn if already spawning
    if (this.spawning.has(name)) {
      return this.spawning.get(name);
    }
    
    // Spawn new server (lazy initialization)
    const spawnPromise = this.spawnServer(name);
    this.spawning.set(name, spawnPromise);
    
    try {
      const server = await spawnPromise;
      this.servers.set(name, server);
      this.spawning.delete(name);
      return server;
    } catch (error) {
      this.spawning.delete(name);
      throw error;
    }
  }
  
  private async spawnServer(name: string): Promise<any> {
    // Load config
    const config = require('./servers.json').servers[name];
    if (!config) {
      throw new Error(`❌ Server not configured: ${name}`);
    }
    
    // Spawn process
    const { spawn } = require('child_process');
    const child = spawn(config.spawn.command, config.spawn.args, {
      env: { ...process.env, ...config.env }
    });
    
    // ⏱️ Timeout protection
    const timeout = setTimeout(() => {
      child.kill();
      throw new Error(`⏱️ Server spawn timeout: ${name}`);
    }, 5000);
    
    // Wait for ready signal
    return new Promise((resolve, reject) => {
      child.on('error', reject);
      child.stdout.once('data', () => {
        clearTimeout(timeout);
        resolve(child);
      });
    });
  }
  
  async cleanup(): Promise<void> {
    // Graceful shutdown
    for (const [name, server] of this.servers.entries()) {
      if (server.kill) {
        server.kill('SIGTERM');
      }
    }
    this.servers.clear();
    this.spawning.clear();
  }
}


/**
 * ✅ PATTERN 4: Error Handling with Troubleshooting
 * 
 * Best practice: All errors include 🔧 troubleshooting guidance
 * Never: Silent failures, generic "error occurred" messages
 */

interface SynthropyError {
  code: string;           // Error code (e.g., "TIMEOUT", "NOT_FOUND")
  message: string;        // Clear error message
  troubleshooting: string; // How to fix it
  context?: Record<string, any>; // Additional context
}

function createError(code: string, message: string, troubleshooting: string, context?: any): SynthropyError {
  return {
    code,
    message,
    troubleshooting,
    context
  };
}

// Examples of errors with troubleshooting

const TIMEOUT_ERROR = createError(
  "TIMEOUT",
  "Server did not respond within 5 seconds",
  "🔧 Check if server is running and responsive. " +
  "Verify network connectivity. " +
  "Try restarting: rm -rf ~/.mcp-auth"
);

const NOT_FOUND_ERROR = (symbol: string) => createError(
  "NOT_FOUND",
  `Symbol not found: ${symbol}`,
  "🔧 Verify symbol name is exact (case-sensitive). " +
  "Use get_symbols_overview to list available symbols. " +
  "Check file path is correct."
);

const INVALID_CONFIG_ERROR = (server: string) => createError(
  "INVALID_CONFIG",
  `Server not configured: ${server}`,
  "🔧 Check servers.json has entry for '${server}'. " +
  "Verify spawn command and args are valid. " +
  "See examples/syntropy-ts-patterns.ts for configuration."
);


/**
 * ✅ PATTERN 5: Request/Response Envelope
 * 
 * Best practice: Consistent message format for all tools
 * Benefit: Unified error handling, easy debugging, standardized logs
 */

interface SynthropyRequest {
  id: string;             // Unique request ID
  tool: string;           // Tool name
  params: Record<string, any>; // Tool parameters
  timestamp: number;      // Request timestamp
}

interface SynthropyResponse {
  id: string;             // Correlate with request
  success: boolean;       // Operation succeeded?
  result?: any;           // Tool result (if success)
  error?: SynthropyError; // Error details (if failure)
  duration: number;       // Execution time in ms
  timestamp: number;      // Response timestamp
}

class ToolExecutor {
  async execute(request: SynthropyRequest): Promise<SynthropyResponse> {
    const startTime = Date.now();
    
    try {
      // Get appropriate server
      const server = await this.getServer(request.tool);
      
      // Execute tool
      const result = await this.callTool(server, request.tool, request.params);
      
      return {
        id: request.id,
        success: true,
        result,
        duration: Date.now() - startTime,
        timestamp: Date.now()
      };
    } catch (error) {
      const synthropyError = this.normalizeError(error);
      
      return {
        id: request.id,
        success: false,
        error: synthropyError,
        duration: Date.now() - startTime,
        timestamp: Date.now()
      };
    }
  }
  
  private normalizeError(error: any): SynthropyError {
    if (error.code) {
      return error; // Already SynthropyError
    }
    
    // Convert native errors
    if (error.message.includes('timeout')) {
      return TIMEOUT_ERROR;
    }
    
    return createError(
      "UNKNOWN",
      error.message || "Unknown error",
      "🔧 Check server logs for details. " +
      "Try restarting Syntropy server. " +
      "Enable debug logging for more information."
    );
  }
  
  private async getServer(tool: string): Promise<any> {
    // Implement server lookup
    return null;
  }
  
  private async callTool(server: any, tool: string, params: any): Promise<any> {
    // Implement tool invocation
    return null;
  }
}


/**
 * ✅ PATTERN 6: Structured Logging
 * 
 * Best practice: All operations logged with context
 * Format: [LEVEL] [COMPONENT] [OPERATION] message {context}
 */

interface LogContext {
  servername?: string;
  toolName?: string;
  duration?: number;
  resultSize?: number;
  error?: string;
}

class SynthropyLogger {
  info(message: string, context?: LogContext) {
    console.log(`[INFO] [${context?.servername}] ${message}`, context);
  }
  
  warn(message: string, context?: LogContext) {
    console.warn(`[WARN] [${context?.servername}] ${message}`, context);
  }
  
  error(message: string, context?: LogContext) {
    console.error(`[ERROR] [${context?.servername}] ${message}`, context);
  }
  
  debug(message: string, context?: LogContext) {
    if (process.env.DEBUG) {
      console.debug(`[DEBUG] [${context?.servername}] ${message}`, context);
    }
  }
}

// Usage example
const logger = new SynthropyLogger();
logger.info("Tool executed successfully", {
  servername: "serena",
  toolName: "find_symbol",
  duration: 45,
  resultSize: 2048
});


/**
 * ✅ PATTERN 7: Connection Pooling & Lifecycle
 * 
 * Best practice: Reuse connections, graceful cleanup
 * Benefit: Performance, resource management, clean shutdown
 */

class SynthropyMCP {
  private pool: ServerPool;
  private logger: SynthropyLogger;
  
  constructor() {
    this.pool = new ServerPool();
    this.logger = new SynthropyLogger();
  }
  
  async initialize(): Promise<void> {
    this.logger.info("Initializing Syntropy MCP");
    // Load configurations, validate servers
  }
  
  async shutdown(): Promise<void> {
    this.logger.info("Shutting down Syntropy MCP");
    await this.pool.cleanup();
    this.logger.info("Cleanup complete");
  }
  
  // Graceful shutdown on process signals
  setupSignalHandlers(): void {
    ['SIGTERM', 'SIGINT'].forEach(signal => {
      process.on(signal, async () => {
        this.logger.info(`Received ${signal}, shutting down...`);
        await this.shutdown();
        process.exit(0);
      });
    });
  }
}


/**
 * ✅ PATTERN 8: Tool Versioning & Deprecation
 * 
 * Best practice: Track tool versions, deprecate gracefully
 * Never: Remove tools without migration path
 */

interface ToolVersion {
  version: string;        // semver
  deprecated?: boolean;
  deprecatedIn?: string;  // When deprecated
  replacedBy?: string;    // Replacement tool
  migrationGuide?: string; // How to upgrade
}

const TOOL_VERSIONS: Record<string, ToolVersion> = {
  "find_symbol": {
    version: "1.0.0"
  },
  "find_symbol_old": {
    version: "0.9.0",
    deprecated: true,
    deprecatedIn: "1.0.0",
    replacedBy: "find_symbol",
    migrationGuide: "see examples/migration-guide.md"
  }
};


/**
 * ✅ PATTERN 9: Type-Safe Tool Definitions
 * 
 * Best practice: Strong typing prevents runtime errors
 * Use: TypeScript interfaces for all tool parameters
 */

interface FindSymbolParams {
  name_path: string;
  include_body?: boolean;
}

interface FindSymbolResult {
  symbol: string;
  type: "function" | "class" | "method" | "variable";
  file: string;
  line: number;
  column: number;
  body?: string;
  docstring?: string;
}

async function findSymbol(params: FindSymbolParams): Promise<FindSymbolResult> {
  // Implementation with type safety
  return {
    symbol: params.name_path,
    type: "function",
    file: "ce/core.py",
    line: 42,
    column: 0,
    body: "def function(): pass",
    docstring: "Function documentation"
  };
}


/**
 * ✅ PATTERN 10: Testing & Mocking
 * 
 * Best practice: Mock servers for testing, real servers for integration
 * Benefit: Fast tests, deterministic behavior, no external dependencies
 */

class MockServer {
  private responses: Map<string, any> = new Map();
  
  setResponse(tool: string, result: any): void {
    this.responses.set(tool, result);
  }
  
  async call(tool: string, params: any): Promise<any> {
    if (!this.responses.has(tool)) {
      throw new Error(`No mock response for tool: ${tool}`);
    }
    return this.responses.get(tool);
  }
}

// Usage in tests
function testFindSymbol() {
  const mock = new MockServer();
  mock.setResponse("find_symbol", {
    symbol: "test_function",
    type: "function",
    file: "test.py",
    line: 10
  });
  
  // Test code using mock
  // No real server spawned, fast & deterministic
}


/**
 * 🔧 ANTI-PATTERNS TO AVOID
 */

// ❌ ANTI-PATTERN 1: Synchronous server initialization
// Problem: Blocks startup, slow for multiple servers
const BAD_INIT = () => {
  const server1 = spawnServerSync("server1");  // ❌ Blocks
  const server2 = spawnServerSync("server2");  // ❌ Blocks
  const server3 = spawnServerSync("server3");  // ❌ Blocks
};

// ✅ GOOD: Lazy initialization
// Servers spawn on first use, startup is fast

// ❌ ANTI-PATTERN 2: Generic error messages
// Problem: Unclear how to fix
const BAD_ERROR = { message: "Error occurred" };

// ✅ GOOD: Include troubleshooting
const GOOD_ERROR = createError(
  "NOT_FOUND",
  "Symbol 'authenticate' not found",
  "🔧 Check symbol name is exact. Use get_symbols_overview to list available symbols."
);

// ❌ ANTI-PATTERN 3: Silent failures
// Problem: Bugs hard to track
const BAD_CALL = async () => {
  try {
    const result = await callTool(...);
    return result || { success: true };  // ❌ Hides failures
  } catch {
    return { success: false };  // ❌ Silent error
  }
};

// ✅ GOOD: Always throw on failure
const GOOD_CALL = async () => {
  const result = await callTool(...);
  if (!result) {
    throw createError("EMPTY_RESULT", "Tool returned no result", "🔧 Check tool parameters");
  }
  return result;
};

// ❌ ANTI-PATTERN 4: Unbounded resource allocation
// Problem: Memory leak, server proliferation
const BAD_POOL = new Map();
const BAD_GET = async (name: string) => {
  if (!BAD_POOL.has(name)) {
    BAD_POOL.set(name, await spawnServer(name));  // ❌ Unbounded
  }
  return BAD_POOL.get(name);
};

// ✅ GOOD: Connection pooling with limits
// See ServerPool pattern above

// ❌ ANTI-PATTERN 5: Hardcoded configuration
// Problem: Not extensible, requires code changes to add servers
const BAD_CONFIG = {
  serena: spawn("npx", ["serena"]),  // ❌ Hardcoded
  filesystem: spawn("npx", ["fs"]),  // ❌ Hardcoded
};

// ✅ GOOD: External configuration
// See SERVER_CONFIG_PATTERN (servers.json) above


/**
 * 📚 IMPLEMENTATION CHECKLIST
 * 
 * When extending Syntropy with new server:
 * 
 * [ ] Define server in servers.json with spawn config
 * [ ] Create tool definitions with InputSchema
 * [ ] Implement type-safe tool handlers
 * [ ] Add error handling with troubleshooting
 * [ ] Add structured logging
 * [ ] Write unit tests with mocks
 * [ ] Test integration with ServerPool
 * [ ] Document tool patterns in examples/syntropy/
 * [ ] Add to tool-usage-guide.md memory
 * [ ] Update CLAUDE.md tool reference
 * [ ] Mark deprecated tools (if replacing)
 * [ ] Test graceful shutdown
 * [ ] Verify connection pooling works
 */


/**
 * 📖 REFERENCE IMPLEMENTATION
 * 
 * Location: /Users/bprzybysz/nc-src/ctx-eng-plus/syntropy-mcp/
 * 
 * Key files:
 * - index.ts: Main MCP router
 * - servers.json: Server configuration
 * - src/server-pool.ts: Connection pooling
 * - src/error-handler.ts: Error handling
 * - src/logger.ts: Structured logging
 * 
 * Follow these patterns when extending.
 */
