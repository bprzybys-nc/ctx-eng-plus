/**
 * Unit tests for knowledge management tools
 * Tests: getSystemDoc, getUserDoc, knowledgeSearch
 */

import { describe, it, before, after } from "node:test";
import assert from "node:assert";
import fs from "fs/promises";
import path from "path";
import os from "os";
import { getSystemDoc, getUserDoc, knowledgeSearch } from "./knowledge.js";
import { KnowledgeIndexer, saveIndex } from "../indexer/knowledge-indexer.js";

describe("Knowledge Tools", () => {
  let testProjectRoot: string;

  before(async () => {
    // Create temp project structure
    testProjectRoot = await fs.mkdtemp(path.join(os.tmpdir(), "knowledge-test-"));

    // Create directory structure
    await fs.mkdir(path.join(testProjectRoot, ".ce"), { recursive: true });
    await fs.mkdir(path.join(testProjectRoot, ".ce", "docs"), { recursive: true });
    await fs.mkdir(path.join(testProjectRoot, "user-docs"), { recursive: true });
    await fs.mkdir(path.join(testProjectRoot, "PRPs"), { recursive: true });
    await fs.mkdir(path.join(testProjectRoot, "examples"), { recursive: true });
    await fs.mkdir(path.join(testProjectRoot, ".serena", "memories"), { recursive: true });

    // Create test files
    await fs.writeFile(
      path.join(testProjectRoot, ".ce", "docs", "framework.md"),
      "# Framework Doc\nTest framework documentation"
    );

    await fs.writeFile(
      path.join(testProjectRoot, "user-docs", "user-guide.md"),
      "# User Guide\nTest user documentation"
    );

    await fs.writeFile(
      path.join(testProjectRoot, "PRPs", "PRP-1-test.md"),
      "---\ntitle: Test PRP\n---\n# Test PRP\nImplementation details"
    );

    await fs.writeFile(
      path.join(testProjectRoot, "examples", "example.ts"),
      "// Example code\nfunction test() {}"
    );

    // Build knowledge index
    const indexer = new KnowledgeIndexer(testProjectRoot);
    const index = await indexer.buildIndex();
    await saveIndex(testProjectRoot, index);
  });

  after(async () => {
    // Cleanup
    await fs.rm(testProjectRoot, { recursive: true, force: true });
  });

  describe("getSystemDoc", () => {
    it("returns system doc from .ce/ directory", async () => {
      const result = await getSystemDoc({
        project_root: testProjectRoot,
        doc_path: "docs/framework.md"  // Path relative to .ce/
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.content);
      assert.ok(result.content.includes("Framework Doc"));
    });

    it("rejects paths outside .ce/ directory", async () => {
      const result = await getSystemDoc({
        project_root: testProjectRoot,
        doc_path: "../user-docs/user-guide.md"  // Path traversal outside .ce/
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("must be within .ce/"));
    });

    it("returns error for non-existent file", async () => {
      const result = await getSystemDoc({
        project_root: testProjectRoot,
        doc_path: "docs/missing.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("not found"));
    });

    it("rejects path traversal attempts", async () => {
      const result = await getSystemDoc({
        project_root: testProjectRoot,
        doc_path: "../user-docs/user-guide.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("must be within .ce/"));
    });
  });

  describe("getUserDoc", () => {
    it("returns user doc from project root", async () => {
      const result = await getUserDoc({
        project_root: testProjectRoot,
        doc_path: "user-docs/user-guide.md"
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.content);
      assert.ok(result.content.includes("User Guide"));
    });

    it("rejects paths inside .ce/ directory", async () => {
      const result = await getUserDoc({
        project_root: testProjectRoot,
        doc_path: ".ce/docs/framework.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("syntropy_get_system_doc"));
    });

    it("returns error for non-existent file", async () => {
      const result = await getUserDoc({
        project_root: testProjectRoot,
        doc_path: "user-docs/missing.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("not found"));
    });

    it("rejects path traversal to .ce/", async () => {
      const result = await getUserDoc({
        project_root: testProjectRoot,
        doc_path: "user-docs/../.ce/docs/framework.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("syntropy_get_system_doc"));
    });
  });

  describe("knowledgeSearch", () => {
    it("searches across all knowledge sources", async () => {
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "test",
        limit: 10
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);
      assert.ok(Array.isArray(result.results));
      assert.ok(result.results.length > 0);
    });

    it("filters results by type", async () => {
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "test",
        types: ["prp"],
        limit: 10
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);

      // All results should be PRPs
      result.results.forEach((entry: any) => {
        assert.strictEqual(entry.type, "prp");
      });
    });

    it("filters results by tags", async () => {
      // This test assumes tags are indexed - may need adjustment based on indexer implementation
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "test",
        tags: ["implementation"],
        limit: 10
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);
      // Tags filtering verification would depend on tag extraction in indexer
    });

    it("respects limit parameter", async () => {
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "test",
        limit: 2
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);
      assert.ok(result.results.length <= 2);
    });

    it("returns empty results for non-matching query", async () => {
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "nonexistentquerystringthatwontmatch",
        limit: 10
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);
      assert.strictEqual(result.results.length, 0);
    });

    it("handles missing knowledge index gracefully", async () => {
      const emptyProjectRoot = await fs.mkdtemp(path.join(os.tmpdir(), "empty-project-"));

      try {
        const result = await knowledgeSearch({
          project_root: emptyProjectRoot,
          query: "test",
          limit: 10
        });

        assert.strictEqual(result.success, false);
        assert.ok(result.error);
        assert.ok(result.error.includes("not found") || result.error.includes("🔧"));
      } finally {
        await fs.rm(emptyProjectRoot, { recursive: true, force: true });
      }
    });

    it("includes match explanations in results", async () => {
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "test",
        limit: 10
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);

      if (result.results.length > 0) {
        const firstResult = result.results[0];
        assert.ok(firstResult.match_reason);
        assert.ok(typeof firstResult.match_reason === "string");
      }
    });

    it("returns results sorted by relevance score", async () => {
      const result = await knowledgeSearch({
        project_root: testProjectRoot,
        query: "test",
        limit: 10
      });

      assert.strictEqual(result.success, true);
      assert.ok(result.results);

      // Scores should be in descending order
      for (let i = 1; i < result.results.length; i++) {
        assert.ok(
          result.results[i - 1].score >= result.results[i].score,
          "Results should be sorted by score descending"
        );
      }
    });
  });

  describe("Error Handling", () => {
    it("getSystemDoc includes troubleshooting guidance on error", async () => {
      const result = await getSystemDoc({
        project_root: testProjectRoot,
        doc_path: ".ce/missing.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("🔧"), "Should include troubleshooting emoji");
    });

    it("getUserDoc includes troubleshooting guidance on error", async () => {
      const result = await getUserDoc({
        project_root: testProjectRoot,
        doc_path: "missing.md"
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("🔧"), "Should include troubleshooting emoji");
    });

    it("knowledgeSearch includes troubleshooting guidance on error", async () => {
      const result = await knowledgeSearch({
        project_root: "/nonexistent/path",
        query: "test",
        limit: 10
      });

      assert.strictEqual(result.success, false);
      assert.ok(result.error);
      assert.ok(result.error.includes("🔧"), "Should include troubleshooting emoji");
    });
  });
});
