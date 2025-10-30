import { strict as assert } from 'node:assert';
import { test, describe } from 'node:test';
import * as fs from "fs/promises";
import * as path from "path";
import * as os from "os";
import { fileURLToPath } from "url";
import { initProject } from "./init.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe("Init Tool", () => {
  describe("initProject", () => {
    test("initializes fresh project with all directories", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
      try {
        const boilerplatePath = path.join(__dirname, "../../ce");
        process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

        const result = await initProject({ project_root: tmpDir });

        assert.equal(result.success, true);
        assert(result.message.includes("successfully"));
        assert.equal(result.structure, ".ce/ (system) + PRPs/examples/ (user)");

        // Verify directory structure created
        const ceDir = path.join(tmpDir, ".ce");
        const prpsDir = path.join(tmpDir, "PRPs");
        const examplesDir = path.join(tmpDir, "examples");
        const memoriesDir = path.join(tmpDir, ".serena/memories");

        const ceExists = await fs.stat(ceDir).then(() => true).catch(() => false);
        const prpsExists = await fs.stat(prpsDir).then(() => true).catch(() => false);
        const examplesExists = await fs.stat(examplesDir).then(() => true).catch(() => false);
        const memoriesExists = await fs.stat(memoriesDir).then(() => true).catch(() => false);

        assert.equal(ceExists, true);
        assert.equal(prpsExists, true);
        assert.equal(examplesExists, true);
        assert.equal(memoriesExists, true);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("creates CLAUDE.md with template", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
      try {
        const boilerplatePath = path.join(__dirname, "../../ce");
        process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

        await initProject({ project_root: tmpDir });

        const claudeMdPath = path.join(tmpDir, "CLAUDE.md");
        const content = await fs.readFile(claudeMdPath, "utf-8");

        assert(content.includes("## Project Guide"));
        assert(content.includes("/generate-prp"));
        assert(content.includes("/execute-prp"));
        assert(content.includes("/update-context"));
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("creates PRPs subdirectories", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
      try {
        const boilerplatePath = path.join(__dirname, "../../ce");
        process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

        await initProject({ project_root: tmpDir });

        const featureRequestsDir = path.join(tmpDir, "PRPs/feature-requests");
        const executedDir = path.join(tmpDir, "PRPs/executed");

        const featureExists = await fs.stat(featureRequestsDir).then(() => true).catch(() => false);
        const executedExists = await fs.stat(executedDir).then(() => true).catch(() => false);

        assert.equal(featureExists, true);
        assert.equal(executedExists, true);
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("rejects invalid project root", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
      try {
        const invalidPath = path.join(tmpDir, "does-not-exist");
        const boilerplatePath = path.join(__dirname, "../../ce");
        process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

        await assert.rejects(() => initProject({ project_root: invalidPath }));
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });

    test("returns layout information", async () => {
      const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), "init-test-"));
      try {
        const boilerplatePath = path.join(__dirname, "../../ce");
        process.env.SYNTROPY_BOILERPLATE_PATH = boilerplatePath;

        const result = await initProject({ project_root: tmpDir });

        assert(result.layout);
        assert.equal(result.layout.ceDir, ".ce");
        assert.equal(result.layout.prpsDir, "PRPs");
        assert.equal(result.layout.examplesDir, "examples");
        assert.equal(result.layout.memoriesDir, ".serena/memories");
        assert.equal(result.layout.claudeMd, "CLAUDE.md");
        assert.equal(result.layout.commandsDir, ".claude/commands");
      } finally {
        await fs.rm(tmpDir, { recursive: true, force: true });
      }
    });
  });
});
