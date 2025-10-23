# INITIAL: Syntropy Context Sync Tool & Optimization

**Feature:** Replace ce update-context with Syntropy-based sync tool including drift detection, incremental reindexing, and performance optimization.

**Prerequisites:**
- PRP-29.1 must be completed first (provides init tool and structure detection)
- PRP-29.2 must be completed first (provides knowledge index and indexer)

**Dependencies:** None (final PRP in series, consolidates functionality)

---

## FEATURE

Syntropy provides context sync functionality that replaces `ce update-context`, with drift detection, YAML header updates, and optimized incremental reindexing.

**Goals:**
1. Implement `syntropy_sync_context` MCP tool
2. Integrate drift detection from `ce analyze-context`
3. Update PRP YAML headers (context_sync flags: ce_updated, serena_updated, last_sync)
4. Incremental reindexing (only scan changed files)
5. Cache optimization (5-min TTL, avoid full scans)
6. Delegate `ce update-context` to Syntropy tool
7. Generate drift report at `.ce/drift-report.md`

**Current Problems:**
- `ce update-context` complex (multiple tools: ce + Serena + drift detection)
- No incremental updates (always full scan)
- No caching (redundant work)
- Drift detection separate from sync

**Expected Outcome:**
- Single tool: `syntropy_sync_context` (replaces ce update-context)
- Incremental reindexing: Only changed files scanned
- Drift detection integrated: Auto-generated `.ce/drift-report.md`
- PRP YAML headers updated: context_sync flags + timestamps
- Performance: <2s for incremental, <10s for full scan
- Backward compat: `ce update-context` delegates to Syntropy

---

## EXAMPLES

### Example 1: Sync Tool Implementation

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
interface SyncContextArgs {
  project_root?: string;  // Optional (defaults to cwd)
  prp_path?: string;      // Optional: sync specific PRP only
  force?: boolean;        // Force full rescan (ignore cache)
}

interface SyncResult {
  success: boolean;
  mode: "incremental" | "full";
  files_scanned: number;
  files_updated: number;
  drift_score: number;
  duration_ms: number;
  changes: {
    prps_updated: string[];
    index_updated: boolean;
    drift_report_updated: boolean;
  };
}

export async function syncContext(args: SyncContextArgs): Promise<SyncResult> {
  const projectRoot = args.project_root || process.cwd();
  const startTime = Date.now();

  try {
    // 1. Load existing index
    const indexPath = path.join(projectRoot, ".ce/syntropy-index.json");
    let index = await loadIndex(indexPath);

    // 2. Determine sync mode (incremental vs full)
    const mode = determineSyncMode(index, args.force);

    // 3. Scan for changes
    const changes = await scanChanges(projectRoot, index, mode);

    // 4. Update PRP YAML headers (context_sync flags)
    const prpsUpdated = await updatePRPHeaders(projectRoot, changes, args.prp_path);

    // 5. Update index (incremental or full)
    index = await updateIndex(projectRoot, index, changes, mode);

    // 6. Run drift detection
    const drift = await detectDrift(projectRoot, index);

    // 7. Generate drift report
    await generateDriftReport(projectRoot, drift);

    const duration = Date.now() - startTime;

    return {
      success: true,
      mode,
      files_scanned: changes.filesScanned,
      files_updated: prpsUpdated.length,
      drift_score: drift.score,
      duration_ms: duration,
      changes: {
        prps_updated: prpsUpdated,
        index_updated: true,
        drift_report_updated: true
      }
    };
  } catch (error) {
    throw new Error(
      `Context sync failed: ${error.message}\n` +
      `🔧 Troubleshooting: Ensure project is initialized (syntropy_init_project)`
    );
  }
}

function determineSyncMode(index: KnowledgeIndex | null, force: boolean): "incremental" | "full" {
  if (force) return "full";
  if (!index) return "full";

  const now = Date.now();
  const syncedAt = new Date(index.synced_at).getTime();
  const age = (now - syncedAt) / 1000 / 60;  // Minutes

  // Full scan if index older than 30 minutes
  return age > 30 ? "full" : "incremental";
}
```

**Pattern:** Incremental by default, full scan when forced or stale, update headers + index + drift.

### Example 2: Incremental Change Detection

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
interface ChangeSet {
  filesScanned: number;
  prps: { added: string[]; modified: string[]; deleted: string[] };
  examples: { added: string[]; modified: string[]; deleted: string[] };
  memories: { added: string[]; modified: string[]; deleted: string[] };
}

async function scanChanges(
  projectRoot: string,
  index: KnowledgeIndex,
  mode: "incremental" | "full"
): Promise<ChangeSet> {
  const changes: ChangeSet = {
    filesScanned: 0,
    prps: { added: [], modified: [], deleted: [] },
    examples: { added: [], modified: [], deleted: [] },
    memories: { added: [], modified: [], deleted: [] }
  };

  if (mode === "full") {
    // Full scan: re-index everything
    return await fullScan(projectRoot);
  }

  // Incremental: check file mtimes
  const layout = detectProjectLayout(projectRoot);

  // Check PRPs
  const prpDir = path.join(projectRoot, layout.prpsDir, "executed");
  const currentPRPs = await glob("PRP-*.md", { cwd: prpDir });

  for (const prp of currentPRPs) {
    const prpPath = path.join(prpDir, prp);
    const stats = await fs.stat(prpPath);
    const mtime = stats.mtime.getTime();
    const syncedAt = new Date(index.synced_at).getTime();

    if (mtime > syncedAt) {
      const prpId = prp.match(/PRP-(\d+)/)?.[0];
      if (prpId && index.knowledge.prp_learnings[prpId]) {
        changes.prps.modified.push(prpPath);
      } else {
        changes.prps.added.push(prpPath);
      }
      changes.filesScanned++;
    }
  }

  // Check for deleted PRPs
  for (const prpId of Object.keys(index.knowledge.prp_learnings)) {
    const prpFile = `${prpId}.md`;  // Simplified
    if (!currentPRPs.includes(prpFile)) {
      changes.prps.deleted.push(prpId);
    }
  }

  // Similar for examples and memories...

  return changes;
}
```

**Pattern:** Compare file mtimes vs last sync timestamp, track added/modified/deleted.

### Example 3: PRP YAML Header Updates

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
async function updatePRPHeaders(
  projectRoot: string,
  changes: ChangeSet,
  specificPRP?: string
): Promise<string[]> {
  const prpsUpdated: string[] = [];

  // Determine which PRPs to update
  const prpsToUpdate = specificPRP
    ? [specificPRP]
    : [...changes.prps.added, ...changes.prps.modified];

  for (const prpPath of prpsToUpdate) {
    try {
      // Read PRP file
      const content = await fs.readFile(prpPath, "utf-8");

      // Parse YAML header using proper YAML parser
      const parts = content.split("---\n");
      if (parts.length < 3) {
        console.warn(`⚠️  No YAML header in ${prpPath}`);
        continue;
      }

      const yamlHeader = parts[1];
      const bodyContent = parts.slice(2).join("---\n");

      // Parse YAML to object
      const yamlData = yaml.parse(yamlHeader);

      // Update context_sync section
      const now = new Date().toISOString();
      yamlData.context_sync = {
        ce_updated: true,
        serena_updated: true,
        last_sync: now
      };

      // Stringify back to YAML
      const updatedYaml = yaml.stringify(yamlData);

      // Reconstruct file
      const updatedContent = `---\n${updatedYaml}---\n${bodyContent}`;

      // Atomic write: write to temp file, then rename
      const tempPath = `${prpPath}.tmp`;
      await fs.writeFile(tempPath, updatedContent);
      await fs.rename(tempPath, prpPath);

      prpsUpdated.push(prpPath);
    } catch (error) {
      console.error(`❌ Failed to update ${prpPath}: ${error.message}`);
    }
  }

  return prpsUpdated;
}
```

**Pattern:** Parse YAML with proper parser (not regex), update context_sync flags, atomic write (temp + rename), track updated files.

**Important:** Uses `yaml` npm package for robust parsing. Atomic writes prevent data corruption if user edits file during sync (old content preserved if write fails).

### Example 4: Drift Detection Integration

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
interface DriftInfo {
  score: number;
  violations: DriftViolation[];
}

interface DriftViolation {
  type: "code_violation" | "missing_example";
  severity: "high" | "medium" | "low";
  file: string;
  line?: number;
  issue: string;
  solution: string;
}

async function detectDrift(projectRoot: string, index: KnowledgeIndex): Promise<DriftInfo> {
  const violations: DriftViolation[] = [];

  // Part 1: Code violations (anti-patterns in codebase)
  const codeViolations = await scanCodeViolations(projectRoot);
  violations.push(...codeViolations);

  // Part 2: Missing examples (PRPs without documentation)
  const missingExamples = await scanMissingExamples(projectRoot, index);
  violations.push(...missingExamples);

  // Calculate drift score
  const score = calculateDriftScore(violations);

  return { score, violations };
}

async function scanCodeViolations(projectRoot: string): Promise<DriftViolation[]> {
  const violations: DriftViolation[] = [];

  // Anti-pattern checks
  const patterns = [
    {
      regex: /except\s*:/g,
      issue: "Bare except clause (catches all exceptions)",
      solution: "Use specific exception types: except ValueError:",
      severity: "high" as const
    },
    {
      regex: /pip install/g,
      issue: "Using pip instead of uv",
      solution: "Use: uv add package-name",
      severity: "medium" as const
    },
    {
      regex: /return \{"success": True\}/g,
      issue: "Hardcoded success (fishy fallback)",
      solution: "Remove fallback, let exceptions propagate",
      severity: "high" as const
    }
  ];

  // Scan Python files
  const pyFiles = await glob("**/*.py", {
    cwd: projectRoot,
    ignore: ["**/node_modules/**", "**/.venv/**"]
  });

  for (const file of pyFiles) {
    const fullPath = path.join(projectRoot, file);
    const content = await fs.readFile(fullPath, "utf-8");
    const lines = content.split("\n");

    for (const pattern of patterns) {
      for (let i = 0; i < lines.length; i++) {
        if (pattern.regex.test(lines[i])) {
          violations.push({
            type: "code_violation",
            severity: pattern.severity,
            file,
            line: i + 1,
            issue: pattern.issue,
            solution: pattern.solution
          });
        }
      }
    }
  }

  return violations;
}

async function scanMissingExamples(projectRoot: string, index: KnowledgeIndex): Promise<DriftViolation[]> {
  const violations: DriftViolation[] = [];

  // Check for PRPs with implementations but no examples
  for (const [prpId, prp] of Object.entries(index.knowledge.prp_learnings)) {
    if (prp.implementations.length > 0 && !prp.verified) {
      violations.push({
        type: "missing_example",
        severity: "medium",
        file: prp.source,
        issue: `PRP ${prpId} has implementations but no examples/ documentation`,
        solution: `Create examples/patterns/${prpId}-pattern.md`
      });
    }
  }

  return violations;
}

function calculateDriftScore(violations: DriftViolation[]): number {
  // Drift score is percentage (0.0-1.0 = 0%-100%)
  // Each violation adds to score based on severity:
  //   High: 10% per violation (critical issues requiring immediate fix)
  //   Medium: 5% per violation (quality issues, should fix soon)
  //   Low: 2% per violation (minor issues, fix when convenient)
  // Score capped at 100% (1.0)
  const weights = { high: 0.1, medium: 0.05, low: 0.02 };
  const totalScore = violations.reduce((sum, v) => sum + weights[v.severity], 0);
  return Math.min(totalScore, 1.0);
}
```

**Pattern:** Scan code anti-patterns, check missing examples, calculate weighted drift score.

### Example 5: Drift Report Generation

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
async function generateDriftReport(projectRoot: string, drift: DriftInfo): Promise<void> {
  const reportPath = path.join(projectRoot, ".ce/drift-report.md");

  // Group violations by severity and file
  const grouped = groupViolations(drift.violations);

  const report = `# Context Drift Report

**Generated:** ${new Date().toISOString()}
**Drift Score:** ${(drift.score * 100).toFixed(2)}%
**Status:** ${getDriftStatus(drift.score)}

---

## Summary

- **Total Violations:** ${drift.violations.length}
- **High Severity:** ${drift.violations.filter(v => v.severity === "high").length}
- **Medium Severity:** ${drift.violations.filter(v => v.severity === "medium").length}
- **Low Severity:** ${drift.violations.filter(v => v.severity === "low").length}

---

${generateGroupedViolations(grouped)}

---

## Next Steps

${drift.score < 0.05 ? "✅ Context is healthy. No immediate action required." : ""}
${drift.score >= 0.05 && drift.score < 0.15 ? "⚠️  Review violations and create action plan." : ""}
${drift.score >= 0.15 ? "🚨 CRITICAL: High drift detected. Immediate action required." : ""}
`;

  await fs.writeFile(reportPath, report);
}

// Helper: Group violations by severity and file
function groupViolations(violations: DriftViolation[]): Map<string, Map<string, DriftViolation[]>> {
  const grouped = new Map<string, Map<string, DriftViolation[]>>();

  for (const v of violations) {
    if (!grouped.has(v.severity)) {
      grouped.set(v.severity, new Map());
    }
    const severityGroup = grouped.get(v.severity)!;
    if (!severityGroup.has(v.file)) {
      severityGroup.set(v.file, []);
    }
    severityGroup.get(v.file)!.push(v);
  }

  return grouped;
}

// Helper: Generate grouped violation markdown
function generateGroupedViolations(grouped: Map<string, Map<string, DriftViolation[]>>): string {
  const sections: string[] = [];

  for (const severity of ["high", "medium", "low"]) {
    const severityGroup = grouped.get(severity);
    if (!severityGroup || severityGroup.size === 0) continue;

    const icon = severity === "high" ? "🚨" : severity === "medium" ? "⚠️" : "ℹ️";
    sections.push(`## ${icon} ${severity.toUpperCase()} Priority (${Array.from(severityGroup.values()).flat().length} violations)\n`);

    for (const [file, violations] of severityGroup.entries()) {
      sections.push(`### File: \`${file}\`\n`);
      for (const v of violations) {
        sections.push(`- **Line ${v.line || "N/A"}:** ${v.issue}`);
        sections.push(`  - **Solution:** ${v.solution}\n`);
      }
    }
  }

  return sections.join("\n");
}

function getDriftStatus(score: number): string {
  if (score < 0.05) return "✅ Healthy";
  if (score < 0.15) return "⚠️  Warning";
  return "🚨 Critical";
}
```

**Pattern:** Markdown report, grouped by severity, actionable next steps.

### Example 6: Python Delegation

**Location:** `tools/ce/update_context.py`

```python
def update_context(prp_path: Optional[str] = None) -> Dict[str, Any]:
    """Delegate to Syntropy sync tool via MCP protocol.

    Note: This is a simplified example. Actual implementation would use
    MCP client library to communicate with Syntropy server.
    """
    try:
        # In practice, this would use MCP client to call tool:
        # from syntropy_client import SyntropyClient
        # client = SyntropyClient()
        # result = client.call_tool("syntropy_sync_context", {
        #     "project_root": os.getcwd(),
        #     "prp_path": prp_path
        # })

        # For now, use subprocess to call via Claude Code MCP interface
        # This assumes Syntropy MCP is registered in Claude Code settings
        import subprocess
        import json

        # Use mcp_cli or similar tool to invoke MCP tool
        cmd = [
            "mcp_cli",  # Hypothetical MCP CLI tool
            "call",
            "syntropy_sync_context",
            "--project_root", os.getcwd(),
        ]
        if prp_path:
            cmd.extend(["--prp_path", prp_path])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Syntropy sync failed: {result.stderr}\n"
                f"🔧 Troubleshooting: Check Syntropy MCP server status with /mcp health"
            )

        # Parse JSON output from MCP tool
        output = json.loads(result.stdout)
        return output

    except Exception as e:
        raise RuntimeError(
            f"Failed to sync context: {str(e)}\n"
            f"🔧 Troubleshooting:\n"
            f"   1. Check Syntropy MCP running: /mcp health\n"
            f"   2. Verify MCP server config in .claude/settings.local.json\n"
            f"   3. Try reinitializing: syntropy_init_project"
        )
```

**Pattern:** Delegate to Syntropy via MCP protocol, parse JSON response, fast failure with detailed troubleshooting steps.

**Note:** Actual MCP client implementation depends on available MCP client libraries. This example shows the conceptual approach.

---

## DOCUMENTATION

### Context Sync Flow
1. Load existing index (`.ce/syntropy-index.json`)
2. Determine mode: incremental (mtime check) vs full (forced/stale)
3. Scan changes: added/modified/deleted files
4. Update PRP YAML headers: context_sync flags + timestamps
5. Update index: incremental (changed files) or full (rescan all)
6. Detect drift: code violations + missing examples
7. Generate drift report: `.ce/drift-report.md`

### Performance Optimization
- **Incremental mode:** Only scan files modified since last sync (mtime check)
- **Cache:** 5-minute TTL for index (avoid redundant scans)
- **Target Performance (for projects with <100 PRPs, <50 examples):**
  - Incremental sync: <2s (only changed files)
  - Full sync: <10s (complete rescan)
  - Drift detection: <3s (code + examples scan)

### Drift Detection
- **Code violations:** Anti-patterns (bare except, pip install, fishy fallbacks)
- **Missing examples:** PRPs with implementations but no examples/ docs
- **Scoring:** High (0.1), Medium (0.05), Low (0.02) weighted sum

---

## OTHER CONSIDERATIONS

### Backward Compatibility
- `ce update-context` delegates to Syntropy (no breaking changes)
- Existing PRPs work (add context_sync section if missing)
- Supports both layouts (root + context-engineering/)

### Error Handling
- Fast failure with 🔧 troubleshooting
- Clear messages: "Index not found → run syntropy_init_project"
- No fishy fallbacks

### Testing Strategy
- **Unit:** Change detection, YAML updates, drift calculation
- **Integration:** Full sync workflow on test projects
- **E2E:** Verify ce update-context delegation works

### Cache Management
- Index cached in `.ce/syntropy-index.json`
- TTL: 5 minutes (configurable in `.ce/config.yml`)
- Force refresh: `--force` flag

### Concurrent Edit Protection
- **Atomic writes:** Use temp file + rename to prevent corruption
- **Limitation:** User edits during sync may be overwritten
- **Recommendation:** Document in user-facing messages:
  ```
  ⚠️  Do not edit PRP files while sync is running.
     Changes may be overwritten. Wait for sync to complete.
  ```
- **Future:** Consider file locking (e.g., `lockfile` npm package) for robust protection

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
cd syntropy-mcp && npm run build
cd tools && uv run mypy ce/
```

### Level 2: Unit Tests
```bash
cd syntropy-mcp && npm test src/tools/sync.test.ts
cd tools && uv run pytest tests/test_update_context.py
```

**Specific Test Scenarios (TypeScript):**
- `test_determineSyncMode_force`: Always full scan when --force
- `test_determineSyncMode_stale`: Full scan when index >30 min old
- `test_determineSyncMode_fresh`: Incremental when index <30 min
- `test_scanChanges_added`: Detect new PRPs added since last sync
- `test_scanChanges_modified`: Detect PRPs modified (mtime check)
- `test_scanChanges_deleted`: Detect PRPs removed from directory
- `test_updatePRPHeaders_yaml`: Parse and update YAML with yaml package
- `test_updatePRPHeaders_atomic`: Verify temp file + rename pattern
- `test_updatePRPHeaders_noYAML`: Handle PRPs without YAML (warn, skip)
- `test_scanCodeViolations_bareExcept`: Detect bare except clauses
- `test_scanCodeViolations_pipInstall`: Detect pip install usage
- `test_scanCodeViolations_fishyFallback`: Detect hardcoded success returns
- `test_scanMissingExamples_implemented`: Find PRPs with code but no examples
- `test_calculateDriftScore_weights`: Verify high=10%, medium=5%, low=2%
- `test_groupViolations_severityFile`: Group by severity then file
- `test_generateDriftReport_format`: Verify grouped markdown output

**Specific Test Scenarios (Python):**
- `test_update_context_delegation`: Verify MCP tool invocation
- `test_update_context_error`: Handle Syntropy unavailable gracefully
- `test_update_context_json`: Parse JSON response correctly

### Level 3: Integration Tests
```bash
# Test sync tool
syntropy_sync_context /tmp/test-project

# Test incremental mode
touch /tmp/test-project/PRPs/executed/PRP-1.md
syntropy_sync_context /tmp/test-project  # Should scan only PRP-1

# Test drift detection
syntropy_sync_context /tmp/test-project  # Should generate drift report

# Test Python delegation
cd tools && uv run ce update-context --json
```

### Level 4: Pattern Conformance
- Incremental updates (no redundant scans)
- Drift detection (code + examples)
- Error handling (fast failure, actionable)
- Performance (<2s incremental, <10s full)

---

## SUCCESS CRITERIA

1. ⬜ `syntropy_sync_context` tool implemented
2. ⬜ Incremental mode works (mtime-based change detection)
3. ⬜ PRP YAML headers updated via proper YAML parser (not regex)
4. ⬜ Atomic writes prevent data corruption (temp file + rename)
5. ⬜ Drift detection integrated (code violations + missing examples)
6. ⬜ Drift report generated (`.ce/drift-report.md`) with severity grouping
7. ⬜ Drift score calculation documented (percentage-based with weights)
8. ⬜ Index updated (incremental or full)
9. ⬜ `ce update-context` delegates to Syntropy via MCP
10. ⬜ Performance: <2s incremental, <10s full scan (projects with <100 PRPs)
11. ⬜ Concurrent edit protection: Document limitation or implement file locking
12. ⬜ All tests passing (unit + integration)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Medium (3-4 days)
- Sync tool core: 1 day
- Incremental change detection: 0.5 day
- PRP YAML updates: 0.5 day
- Drift detection: 1 day (code violations + missing examples)
- Drift report generation: 0.5 day
- Python delegation: 0.5 day
- Testing: 1 day

**Risk Level:** Medium
- Complex change detection logic
- YAML parsing/updating must be robust
- Drift detection anti-pattern matching

**Dependencies:**
- PRP-29.1 (init tool, structure detection)
- PRP-29.2 (knowledge index, indexer)
- Syntropy MCP server (existing)
- ce CLI tools (existing)

**Files to Create:**
- `syntropy-mcp/src/tools/sync.ts`
- `syntropy-mcp/src/drift-detector.ts`

**Files to Modify:**
- `tools/ce/update_context.py` (delegate to Syntropy)
- `tools/ce/core.py` (Syntropy helpers)
- `syntropy-mcp/src/tools-definition.ts` (add sync tool)
