import { strict as assert } from 'node:assert';
import { test, describe } from 'node:test';
import { parseSyntropyTool, toMcpToolName, toSyntropyToolName } from './index.js';

describe('Syntropy Tool Parsing', () => {
  test('parseSyntropyTool - valid format', () => {
    const parsed = parseSyntropyTool("syntropy:serena:find_symbol");
    assert.deepEqual(parsed, { server: "serena", tool: "find_symbol" });
  });

  test('parseSyntropyTool - invalid format', () => {
    const parsed = parseSyntropyTool("invalid:format");
    assert.equal(parsed, null);
  });

  test('parseSyntropyTool - missing tool part', () => {
    const parsed = parseSyntropyTool("syntropy:serena");
    assert.equal(parsed, null);
  });

  test('parseSyntropyTool - empty string', () => {
    const parsed = parseSyntropyTool("");
    assert.equal(parsed, null);
  });
});

describe('Tool Name Conversion', () => {
  test('toMcpToolName - valid server', () => {
    const mcp = toMcpToolName("serena", "find_symbol");
    assert.equal(mcp, "mcp__serena__find_symbol");
  });

  test('toMcpToolName - unknown server throws error', () => {
    assert.throws(
      () => toMcpToolName("unknown", "tool"),
      /Unknown syntropy server: unknown/
    );
  });

  test('toSyntropyToolName - valid MCP tool', () => {
    const syn = toSyntropyToolName("mcp__serena__find_symbol");
    assert.equal(syn, "syntropy:serena:find_symbol");
  });

  test('toSyntropyToolName - invalid format', () => {
    const syn = toSyntropyToolName("invalid_format");
    assert.equal(syn, null);
  });

  test('toSyntropyToolName - unknown server prefix', () => {
    const syn = toSyntropyToolName("mcp__unknown__tool");
    assert.equal(syn, null);
  });
});
