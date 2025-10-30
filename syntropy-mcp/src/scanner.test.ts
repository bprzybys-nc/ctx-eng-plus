import { strict as assert } from 'node:assert';
import { test, describe } from 'node:test';
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";
import {
  detectProjectLayout,
  findCLAUDEmd,
  validateProjectRoot,
  directoryExists,
  fileExists,
  isAlreadyInitialized
} from "./scanner.js";

describe("Scanner Module", () => {
  describe("detectProjectLayout", () => {
    test("returns standard layout", () => {
      const layout = detectProjectLayout("/path/to/project");
      assert.equal(layout.ceDir, ".ce");
      assert.equal(layout.prpsDir, "PRPs");
      assert.equal(layout.examplesDir, "examples");
      assert.equal(layout.memoriesDir, ".serena/memories");
      assert.equal(layout.claudeMd, "CLAUDE.md");
      assert.equal(layout.commandsDir, ".claude/commands");
    });

    test("returns consistent layout for different paths", () => {
      const layout1 = detectProjectLayout("/path/1");
      const layout2 = detectProjectLayout("/path/2");
      assert.deepEqual(layout1, layout2);
    });
  });

  describe("findCLAUDEmd", () => {
    test("finds existing CLAUDE.md", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const claudeMdPath = path.join(tmpDir, "CLAUDE.md");
        await fs.writeFile(claudeMdPath, "# Test");
        const result = await findCLAUDEmd(tmpDir);
        assert.equal(result, claudeMdPath);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns default path when CLAUDE.md missing", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const result = await findCLAUDEmd(tmpDir);
        assert.equal(result, path.join(tmpDir, "CLAUDE.md"));
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });
  });

  describe("validateProjectRoot", () => {
    test("validates existing directory", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        await validateProjectRoot(tmpDir);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("rejects non-existent directory", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      const nonExistent = path.join(tmpDir, "does-not-exist");
      try {
        await assert.rejects(() => validateProjectRoot(nonExistent));
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("rejects file path", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const filePath = path.join(tmpDir, "test.txt");
        await fs.writeFile(filePath, "test");
        await assert.rejects(() => validateProjectRoot(filePath));
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });
  });

  describe("directoryExists", () => {
    test("returns true for existing directory", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const result = await directoryExists(tmpDir);
        assert.equal(result, true);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false for non-existent directory", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const result = await directoryExists(path.join(tmpDir, "does-not-exist"));
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false for file path", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const filePath = path.join(tmpDir, "test.txt");
        await fs.writeFile(filePath, "test");
        const result = await directoryExists(filePath);
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });
  });

  describe("fileExists", () => {
    test("returns true for existing file", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const filePath = path.join(tmpDir, "test.txt");
        await fs.writeFile(filePath, "test");
        const result = await fileExists(filePath);
        assert.equal(result, true);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false for non-existent file", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const result = await fileExists(path.join(tmpDir, "does-not-exist.txt"));
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false for directory path", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        const result = await fileExists(tmpDir);
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });
  });

  describe("isAlreadyInitialized", () => {
    test("returns true when all markers exist", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        // Create all 3 marker files/directories
        await fs.mkdir(path.join(tmpDir, ".ce", "PRPs", "system"), { recursive: true });
        await fs.mkdir(path.join(tmpDir, ".ce", "tools"), { recursive: true });
        await fs.writeFile(path.join(tmpDir, ".ce", "RULES.md"), "# Rules");

        const result = await isAlreadyInitialized(tmpDir);
        assert.equal(result, true);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false when markers missing", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        // Empty directory - no markers
        const result = await isAlreadyInitialized(tmpDir);
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false when only some markers exist", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        // Create only 1 marker
        await fs.mkdir(path.join(tmpDir, ".ce", "tools"), { recursive: true });

        const result = await isAlreadyInitialized(tmpDir);
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns false when .ce exists but markers missing", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "scanner-test-"));
      try {
        // Create .ce but no markers inside
        await fs.mkdir(path.join(tmpDir, ".ce"), { recursive: true });

        const result = await isAlreadyInitialized(tmpDir);
        assert.equal(result, false);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });
  });
});
