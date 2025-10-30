import { MCPClientManager } from "./build/client-manager.js";
import { runHealthCheck, formatHealthCheckText } from "./build/health-checker.js";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const manager = new MCPClientManager(path.join(__dirname, "servers.json"));

try {
  console.log("🔍 Checking Syntropy MCP Server Health...\n");
  const result = await runHealthCheck(manager, 5000);
  console.log(formatHealthCheckText(result));
} catch (error) {
  console.error("❌ Error:", error.message);
} finally {
  await manager.closeAll();
}
