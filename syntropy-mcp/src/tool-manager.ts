import { promises as fs } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

interface ToolState {
  enabled: string[];
  disabled: string[];
}

export class ToolStateManager {
  private stateFile: string;
  private state: ToolState;

  constructor() {
    this.stateFile = join(homedir(), '.syntropy', 'tool-state.json');
    this.state = { enabled: [], disabled: [] };
  }

  async initialize(): Promise<void> {
    try {
      await fs.mkdir(join(homedir(), '.syntropy'), { recursive: true });
      const data = await fs.readFile(this.stateFile, 'utf-8');
      this.state = JSON.parse(data);
    } catch (error) {
      // File doesn't exist or is corrupted → use default (all enabled)
      console.warn(`Tool state file missing or corrupted, using defaults: ${error}`);
      this.state = { enabled: [], disabled: [] };
      await this.persist();
    }
  }

  async enableTools(toolsToEnable: string[], toolsToDisable: string[]): Promise<void> {
    // Add to enabled set, remove from disabled set
    const enabledSet = new Set(this.state.enabled);
    const disabledSet = new Set(this.state.disabled);

    for (const tool of toolsToEnable) {
      enabledSet.add(tool);
      disabledSet.delete(tool);
    }

    for (const tool of toolsToDisable) {
      disabledSet.add(tool);
      enabledSet.delete(tool);
    }

    this.state.enabled = Array.from(enabledSet);
    this.state.disabled = Array.from(disabledSet);

    await this.persist();
  }

  isEnabled(toolName: string): boolean {
    // If in disabled list → disabled
    if (this.state.disabled.includes(toolName)) {
      return false;
    }
    // If enabled list is empty → all enabled (default)
    // If in enabled list → enabled
    return this.state.enabled.length === 0 || this.state.enabled.includes(toolName);
  }

  getState(): ToolState {
    return { ...this.state };
  }

  private async persist(): Promise<void> {
    try {
      await fs.writeFile(
        this.stateFile,
        JSON.stringify(this.state, null, 2),
        'utf-8'
      );
    } catch (error) {
      console.error(`Failed to persist tool state: ${error}`);
      throw new Error(`Tool state persistence failed: ${error}`);
    }
  }
}
