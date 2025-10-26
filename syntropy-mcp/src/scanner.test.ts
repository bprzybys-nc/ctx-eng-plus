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
  fileExists
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
});
