# INITIAL-PRP-29.3: Syntropy Context Sync

**Feature:** Implement context sync tool in Syntropy MCP that replaces `ce update-context` with unified sync across PRPs, examples, and Serena memories.

---

## FEATURE

Syntropy provides a unified context sync tool that updates PRP metadata, verifies implementations, detects drift, and maintains knowledge index consistency.

**Goals:**
1. Implement `syntropy_sync_context(project_root, options?)` MCP tool
2. Update PRP YAML headers (context_sync flags, last_sync timestamps)
3. Verify implementations exist (function extraction from code)
4. Auto-transition PRPs from feature-requests/ to executed/ when verified
5. Detect pattern drift (code violations + missing examples)
6. Generate drift report at `.ce/drift-report.md`
7. Invalidate and rebuild knowledge index
8. Delegate from `ce update-context` CLI to Syntropy MCP tool
9. Support both universal mode (all PRPs) and targeted mode (specific PRP)

**Current Problems:**
- Context sync complex (multiple tools: ce + Serena + drift detection)
- Manual PRP transitions error-prone
- Drift detection scattered across tools
- No single source of truth for sync operations
- ce CLI reimplements logic already in Serena MCP

**Expected Outcome:**
- MCP tool: `syntropy_sync_context(project_root)` - Full sync
- MCP tool: `syntropy_sync_context(project_root, {prp: 'PRP-15'})` - Targeted sync
- `ce update-context` delegates to Syntropy (thin wrapper)
- PRP YAML updated: `ce_updated: true`, `serena_updated: true`, `last_sync: 2025-10-21T10:00:00Z`
- PRPs auto-moved: feature-requests/ → executed/ when verified
- Drift report: `.ce/drift-report.md` with violations + solutions
- Index rebuilt: `.ce/syntropy-index.json` refreshed

**Prerequisite:** PRP-29.1 and PRP-29.2 must be completed (init creates index, query tools access it)

---

## EXAMPLES

### Example 1: Sync Tool Definition

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
interface SyncOptions {
  prp?: string;           // Target specific PRP (ID or filename)
  force?: boolean;        // Force sync even if recently synced
  skip_drift?: boolean;   // Skip drift detection
  dry_run?: boolean;      // Preview changes without applying them
}

interface SyncResult {
  success: boolean;
  project_root: string;
  synced_at: string;

  prps_updated: {
    id: string;
    file: string;
    ce_updated: boolean;
    serena_updated: boolean;
    transitioned: boolean;  // Moved from feature-requests to executed
  }[];

  drift: {
    score: number;
    violations: DriftViolation[];
    report_path: string;
  };

  index: {
    path: string;
    rebuilt: boolean;
    entries: number;
  };

  errors: string[];
  warnings: string[];
}

export async function syncContext(
  projectRoot: string,
  options?: SyncOptions
): Promise<SyncResult> {
  const result: SyncResult = {
    success: true,
    project_root: projectRoot,
    synced_at: new Date().toISOString(),
    prps_updated: [],
    drift: { score: 0, violations: [], report_path: '' },
    index: { path: '', rebuilt: false, entries: 0 },
    errors: [],
    warnings: []
  };

  try {
    // Step 1: Find PRPs to sync
    const prpsToSync = options?.prp
      ? [await findPRP(projectRoot, options.prp)]
      : await findAllPRPs(projectRoot);

    // Step 2: Update PRP metadata + verify implementations (parallel processing)
    const updatePromises = prpsToSync.map(prpPath =>
      updatePRPMetadata(prpPath, projectRoot, options?.dry_run)
    );
    const updateResults = await Promise.all(updatePromises);
    result.prps_updated = updateResults;

    // Step 3: Auto-transition verified PRPs (unless dry-run)
    if (!options?.dry_run) {
      for (let i = 0; i < prpsToSync.length; i++) {
        const updateResult = updateResults[i];
        if (updateResult.ce_updated && updateResult.serena_updated) {
          const transitioned = await transitionPRP(prpsToSync[i]);
          updateResult.transitioned = transitioned;
        }
      }
    } else {
      result.warnings.push('Dry-run mode: No PRPs transitioned');
    }

    // Step 4: Detect drift (unless skipped)
    if (!options?.skip_drift) {
      const driftResult = await detectDrift(projectRoot);
      result.drift = driftResult;
    }

    // Step 5: Rebuild index (unless dry-run)
    if (!options?.dry_run) {
      const indexResult = await rebuildIndex(projectRoot);
      result.index = indexResult;
    } else {
      result.warnings.push('Dry-run mode: Index not rebuilt');
    }

  } catch (error) {
    result.success = false;
    result.errors.push(error.message);
  }

  return result;
}
```

**Pattern:** Comprehensive sync, auto-transitions, drift detection, index rebuild.

### Example 2: PRP Metadata Update

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
interface PRPMetadata {
  id: string;
  file: string;
  ce_updated: boolean;
  serena_updated: boolean;
  last_sync: string;
  implementations_verified: boolean;
}

async function updatePRPMetadata(
  prpPath: string,
  projectRoot: string,
  dryRun: boolean = false
): Promise<PRPMetadata> {
  // Read PRP file
  const content = await fs.readFile(prpPath, 'utf-8');
  const { yaml, body, preamble } = parseYAMLFrontmatter(content);

  const metadata: PRPMetadata = {
    id: yaml.id || extractPRPId(prpPath),
    file: prpPath,
    ce_updated: false,
    serena_updated: false,
    last_sync: new Date().toISOString(),
    implementations_verified: false
  };

  // Extract implementation files from PRP
  const implFiles = extractImplementationFiles(body);

  // Verify implementations exist
  let allImplemented = true;
  for (const file of implFiles) {
    const fullPath = path.join(projectRoot, file);
    if (!await exists(fullPath)) {
      allImplemented = false;
      break;
    }
  }

  metadata.implementations_verified = allImplemented;
  metadata.ce_updated = allImplemented; // CE sync = files exist

  // Verify via Serena (function extraction)
  try {
    const functionsExtracted = await verifyViaSerena(projectRoot, implFiles);
    metadata.serena_updated = functionsExtracted.length > 0;
  } catch (error) {
    // Graceful degradation if Serena unavailable
    metadata.serena_updated = false;
  }

  // Update PRP YAML header (unless dry-run)
  if (!dryRun) {
    const updatedYAML = {
      ...yaml,
      context_sync: {
        ce_updated: metadata.ce_updated,
        serena_updated: metadata.serena_updated,
        last_sync: metadata.last_sync
      }
    };

    // Preserve preamble when reconstructing
    const updatedContent = stringifyYAMLFrontmatter(updatedYAML, body, preamble);
    await fs.writeFile(prpPath, updatedContent, 'utf-8');
  }

  return metadata;
}
```

**Pattern:** YAML frontmatter parsing, implementation verification, graceful degradation.

### Example 3: Auto-Transition PRPs

**Location:** `syntropy-mcp/src/tools/sync.ts`

```typescript
async function transitionPRP(prpPath: string): Promise<boolean> {
  // Check if PRP in feature-requests/
  if (!prpPath.includes('feature-requests')) {
    return false; // Already in executed/ or elsewhere
  }

  // Compute new path (feature-requests → executed)
  const newPath = prpPath.replace('feature-requests', 'executed');

  // Ensure executed/ directory exists
  const executedDir = path.dirname(newPath);
  await fs.mkdir(executedDir, { recursive: true });

  // Move file
  await fs.rename(prpPath, newPath);

  console.log(`✅ Transitioned: ${path.basename(prpPath)} → executed/`);

  return true;
}
```

**Pattern:** Safe directory creation, rename operation, clear logging.

### Example 4: Drift Detection

**Location:** `syntropy-mcp/src/tools/drift.ts`

```typescript
interface DriftViolation {
  file: string;
  line: number;
  issue: string;
  pattern: string;
  solution: string;
}

interface DriftResult {
  score: number;
  violations: DriftViolation[];
  report_path: string;
}

async function detectDrift(projectRoot: string): Promise<DriftResult> {
  const violations: DriftViolation[] = [];

  // Part 1: Code violating documented patterns
  const codeViolations = await scanCodeViolations(projectRoot);
  violations.push(...codeViolations);

  // Part 2: Critical PRPs missing examples/
  const missingExamples = await scanMissingExamples(projectRoot);
  violations.push(...missingExamples);

  // Compute drift score (% of analyzed files with violations)
  // Only count source files (Python, TypeScript, etc), not all project files
  const analyzedFiles = await countAnalyzedFiles(projectRoot);
  const filesWithViolations = new Set(violations.map(v => v.file)).size;
  const driftScore = filesWithViolations / analyzedFiles;

  // Generate drift report
  const reportPath = path.join(projectRoot, '.ce', 'drift-report.md');
  await generateDriftReport(reportPath, violations, driftScore);

  return {
    score: driftScore,
    violations,
    report_path: reportPath
  };
}

async function scanCodeViolations(projectRoot: string): Promise<DriftViolation[]> {
  const violations: DriftViolation[] = [];

  // Scan Python files for anti-patterns
  const pyFiles = await glob('**/*.py', { cwd: projectRoot, ignore: ['**/node_modules/**', '**/.venv/**'] });

  for (const file of pyFiles) {
    const content = await fs.readFile(path.join(projectRoot, file), 'utf-8');
    const lines = content.split('\n');

    lines.forEach((line, idx) => {
      if (/^\s*except:\s*$/.test(line)) {
        violations.push({
          file,
          line: idx + 1,
          issue: 'Bare except clause (catches all exceptions)',
          pattern: 'error-handling',
          solution: 'Replace with: except SpecificException as e:'
        });
      }
    });
  }

  return violations;
}

async function countAnalyzedFiles(projectRoot: string): Promise<number> {
  // Count source files only (Python, TypeScript, JavaScript)
  const pyFiles = await glob('**/*.py', { cwd: projectRoot, ignore: ['**/node_modules/**', '**/.venv/**'] });
  const tsFiles = await glob('**/*.ts', { cwd: projectRoot, ignore: ['**/node_modules/**', '**/dist/**'] });
  const jsFiles = await glob('**/*.js', { cwd: projectRoot, ignore: ['**/node_modules/**', '**/dist/**'] });

  return pyFiles.length + tsFiles.length + jsFiles.length;
}
```

**Pattern:** Multi-phase drift detection, violation extraction, actionable solutions.

### Example 5: CLI Delegation Pattern

**Location:** `tools/ce/update_context.py`

```python
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

def update_context(
    project_root: Optional[Path] = None,
    prp: Optional[str] = None,
    json_output: bool = False
) -> Dict[str, Any]:
    """Delegate to Syntropy MCP sync tool.

    Args:
        project_root: Project root path (default: current directory)
        prp: Specific PRP to sync (ID or filename)
        json_output: Return JSON output

    Returns:
        Sync result from Syntropy MCP tool

    Raises:
        RuntimeError: If Syntropy sync fails
    """
    project_root = project_root or Path.cwd()

    # Build MCP tool call (via Claude Code)
    # Note: This is a placeholder - actual implementation uses MCP client
    result = call_syntropy_tool(
        tool="syntropy_sync_context",
        args={
            "project_root": str(project_root),
            "options": {
                "prp": prp
            } if prp else {}
        }
    )

    if not result["success"]:
        errors = "\n".join(result.get("errors", []))
        raise RuntimeError(
            f"Context sync failed:\n{errors}\n"
            f"🔧 Check Syntropy MCP server status: mcp__syntropy_healthcheck"
        )

    # Format output
    if json_output:
        return result

    # Human-readable summary
    print(f"✅ Context sync complete ({len(result['prps_updated'])} PRPs)")
    print(f"📊 Drift score: {result['drift']['score']:.1%}")

    if result['drift']['violations']:
        print(f"⚠️  {len(result['drift']['violations'])} violations found")
        print(f"    See: {result['drift']['report_path']}")

    return result

def call_syntropy_tool(tool: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """Call Syntropy MCP tool via subprocess.

    Note: In production, this would use MCP client library.
    For now, placeholder implementation.
    """
    # TODO: Implement actual MCP client call
    # This is simplified for illustration
    cmd = ["syntropy", tool, json.dumps(args)]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if proc.returncode != 0:
        raise RuntimeError(f"MCP tool failed: {proc.stderr}")

    return json.loads(proc.stdout)
```

**Pattern:** Thin CLI wrapper, delegates to MCP tool, formats output for users.

### Example 6: Drift Report Format

**Location:** `.ce/drift-report.md`

```markdown
# Context Drift Report

**Generated:** 2025-10-21T10:15:00Z
**Drift Score:** 8.5%
**Status:** ⚠️ WARNING (5-15% range)

## Summary

- **Total Files:** 120
- **Files with Violations:** 10
- **Total Violations:** 15

## Violations

### Part 1: Code Violating Documented Patterns (12 violations)

#### 1. Bare except clause
**File:** `tools/ce/core.py:45`
**Issue:** Catches all exceptions without specific handling
**Pattern:** error-handling
**Solution:** Replace with `except SpecificException as e:`

#### 2. Hardcoded success message
**File:** `tools/ce/validate.py:102`
**Issue:** Returns fake success without real validation
**Pattern:** real-functionality-testing
**Solution:** Return actual validation result, throw on failure

### Part 2: Critical PRPs Missing Examples (3 violations)

#### 1. PRP-15: Data Validation System
**Issue:** Implemented but no example in `examples/`
**Solution:** Add `examples/patterns/data-validation.md` with usage patterns

## Recommended Actions

1. **High Priority** (5 violations): Fix bare except clauses
2. **Medium Priority** (7 violations): Remove hardcoded success messages
3. **Low Priority** (3 violations): Add missing examples for completed PRPs

## Thresholds

- ✅ **OK:** <5% drift
- ⚠️ **WARNING:** 5-15% drift (current)
- ❌ **CRITICAL:** >15% drift
```

**Pattern:** Clear status, categorized violations, actionable recommendations.

---

## DOCUMENTATION

### YAML Frontmatter Parsing

**Libraries:**
- Use `js-yaml` for parsing/stringifying
- Handle missing frontmatter gracefully
- Preserve non-sync fields in YAML
- Preserve preamble content (title/header before YAML)

**Example:**
```typescript
import yaml from 'js-yaml';

interface ParsedDocument {
  yaml: any;
  body: string;
  preamble: string;  // Content before YAML frontmatter
}

function parseYAMLFrontmatter(content: string): ParsedDocument {
  // Match optional preamble + YAML frontmatter + body
  // Pattern: (preamble)---\n(yaml)\n---\n(body)
  const match = content.match(/^([\s\S]*?)^---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*)$/m);

  if (!match) {
    // No YAML frontmatter found
    return { yaml: {}, body: content, preamble: '' };
  }

  const [, preamble, yamlContent, bodyContent] = match;

  return {
    yaml: yaml.load(yamlContent) || {},
    body: bodyContent,
    preamble: preamble  // Preserve separately
  };
}

function stringifyYAMLFrontmatter(yamlData: any, body: string, preamble: string = ''): string {
  const yamlStr = yaml.dump(yamlData, { lineWidth: -1 });

  // Reconstruct: preamble + YAML + body
  return preamble + `---\n${yamlStr}---\n${body}`;
}
```

**Usage Pattern:**
```typescript
// Parse PRP
const { yaml, body, preamble } = parseYAMLFrontmatter(prpContent);

// Update YAML metadata
yaml.context_sync = { ce_updated: true, serena_updated: true };

// Reconstruct with preserved preamble
const updatedContent = stringifyYAMLFrontmatter(yaml, body, preamble);
```

### Implementation Verification

**CE Verification:**
- Extract file paths from PRP body using `extractImplementationFiles()`
- Check each file exists in project
- Mark `ce_updated: true` if all files present

**Implementation File Extraction:**
```typescript
function extractImplementationFiles(prpBody: string): string[] {
  const files: string[] = [];

  // Match markdown sections: ## Files to Create, ## Files to Modify
  const sections = [
    /## Files to Create\n([\s\S]*?)(?=\n## |$)/,
    /## Files to Modify\n([\s\S]*?)(?=\n## |$)/
  ];

  for (const sectionRegex of sections) {
    const match = prpBody.match(sectionRegex);
    if (!match) continue;

    const sectionContent = match[1];

    // Extract file paths from markdown list items
    // Format: - `path/to/file.ext` - Description
    //     or: - path/to/file.ext - Description
    const fileMatches = sectionContent.matchAll(/^- `?([^`\n-]+\.(?:ts|py|js|md|json|yml|yaml))`?/gm);

    for (const fileMatch of fileMatches) {
      files.push(fileMatch[1].trim());
    }
  }

  return files;
}
```

**Serena Verification:**
- Call `mcp__syntropy_serena_find_symbol` for key functions
- If functions found → `serena_updated: true`
- If Serena unavailable → `serena_updated: false` (graceful degradation)

### Drift Detection Patterns

**Code Violations:**
- Bare except clauses: `except:\s*$`
- Hardcoded success: `return {"success": True}` without real logic
- Missing error messages: `raise Exception()` without message
- pip install usage: `pip install` instead of `uv add`

**Missing Examples:**
- Scan executed PRPs
- Check if `examples/` has corresponding pattern file
- Violation if critical PRP missing example

### Index Rebuild

**When:**
- After every sync operation
- After PRP transitions
- After drift detection

**How:**
- Reuse scanner/indexer from PRP-29.1
- Write to `.ce/syntropy-index.json`
- Update `synced_at` timestamp

---

## OTHER CONSIDERATIONS

### Backward Compatibility

- `ce update-context` CLI preserved (delegates to Syntropy)
- Existing YAML format supported (only add context_sync field)
- PRPs without YAML frontmatter handled gracefully
- Works with both project layouts (root + context-engineering/)

### Performance

- Targeted sync faster than universal (skip irrelevant PRPs)
- Cache drift patterns (don't rescan unchanged files)
- Parallel PRP metadata updates (Promise.all)
- Incremental index rebuild (only changed entries)

### Security

- Validate project_root path (prevent traversal)
- Sanitize PRP file paths before moving
- No shell injection in subprocess calls
- No secret exposure in drift reports

### Error Handling

- Graceful degradation if Serena unavailable
- Continue sync even if some PRPs fail (collect errors)
- Clear troubleshooting for missing implementations
- Warn if drift score critical (>15%)

### Cache Invalidation

**Automatic:**
- After sync completes (invalidate index cache)
- After PRP transitions (reindex affected directories)

**Manual:**
- CLI flag: `ce update-context --force` (bypass checks)

### Drift Thresholds

**Levels:**
- **OK (<5%)**: Green, healthy context
- **WARNING (5-15%)**: Yellow, review recommended
- **CRITICAL (>15%)**: Red, immediate action required

**Actions:**
- OK: No action needed
- WARNING: Generate report, continue
- CRITICAL: Generate report, warn user loudly

### Testing Strategy

**Unit Tests:**
```typescript
describe('parseYAMLFrontmatter', () => {
  it('parses PRP with preamble', () => {
    const content = '# INITIAL: Feature Name\n\n---\nid: PRP-1\n---\n\nBody content';
    const { yaml, body, preamble } = parseYAMLFrontmatter(content);

    expect(preamble).toBe('# INITIAL: Feature Name\n\n');
    expect(yaml.id).toBe('PRP-1');
    expect(body).toBe('\nBody content');
  });

  it('handles PRPs without preamble', () => {
    const content = '---\nid: PRP-2\n---\n\nBody content';
    const { yaml, body, preamble } = parseYAMLFrontmatter(content);

    expect(preamble).toBe('');
    expect(yaml.id).toBe('PRP-2');
  });

  it('handles PRPs without YAML', () => {
    const content = '# Feature\n\nBody content without YAML';
    const { yaml, body, preamble } = parseYAMLFrontmatter(content);

    expect(preamble).toBe('');
    expect(yaml).toEqual({});
    expect(body).toBe(content);
  });
});

describe('updatePRPMetadata', () => {
  it('updates YAML header with sync flags', async () => {
    const prpPath = '/tmp/test-prp.md';
    const metadata = await updatePRPMetadata(prpPath, '/tmp/project');

    expect(metadata.ce_updated).toBe(true);
    expect(metadata.last_sync).toBeTruthy();

    // Verify YAML updated in file
    const content = await fs.readFile(prpPath, 'utf-8');
    expect(content).toContain('ce_updated: true');
  });

  it('preserves preamble when updating YAML', async () => {
    const prpContent = '# INITIAL: Test\n\n---\nid: PRP-1\n---\n\nBody';
    await fs.writeFile('/tmp/test-prp.md', prpContent);

    await updatePRPMetadata('/tmp/test-prp.md', '/tmp/project');

    const updated = await fs.readFile('/tmp/test-prp.md', 'utf-8');
    expect(updated).toContain('# INITIAL: Test\n\n---');
  });

  it('verifies implementations exist', async () => {
    // Create test implementation file
    await fs.writeFile('/tmp/project/impl.py', 'def test(): pass');

    const metadata = await updatePRPMetadata(prpPath, '/tmp/project');
    expect(metadata.implementations_verified).toBe(true);
  });
});

describe('transitionPRP', () => {
  it('moves PRP from feature-requests to executed', async () => {
    const prpPath = '/tmp/project/PRPs/feature-requests/PRP-1.md';
    const transitioned = await transitionPRP(prpPath);

    expect(transitioned).toBe(true);
    expect(await exists('/tmp/project/PRPs/executed/PRP-1.md')).toBe(true);
    expect(await exists(prpPath)).toBe(false);
  });

  it('skips if already in executed/', async () => {
    const prpPath = '/tmp/project/PRPs/executed/PRP-1.md';
    const transitioned = await transitionPRP(prpPath);
    expect(transitioned).toBe(false);
  });
});
```

**Integration Tests:**
```bash
# Test universal sync
syntropy sync /tmp/test-project --json > result.json
jq -e '.success == true' result.json
jq -e '.prps_updated | length > 0' result.json

# Test targeted sync
syntropy sync /tmp/test-project --prp PRP-15 --json
jq -e '.prps_updated | length == 1' result.json
jq -e '.prps_updated[0].id == "PRP-15"' result.json

# Test drift detection
syntropy sync /tmp/test-project --json
jq -e '.drift.score >= 0' result.json
test -f /tmp/test-project/.ce/drift-report.md
```

**E2E Tests:**
```bash
# Full workflow: init → implement → sync → verify
syntropy init /tmp/test-project
cd /tmp/test-project

# Create test PRP
echo "# PRP-1\n## Files to Create\n- test.py" > PRPs/feature-requests/PRP-1.md

# Create implementation
echo "def test(): pass" > test.py

# Sync should verify implementation
syntropy sync . --json > result.json
jq -e '.prps_updated[0].ce_updated == true' result.json

# PRP should transition to executed/
test -f PRPs/executed/PRP-1.md
test ! -f PRPs/feature-requests/PRP-1.md
```

### Constraints

- No breaking changes to existing PRP format
- Works without Serena (graceful degradation)
- Offline-first (no network required)
- Fast targeted sync (<1s for single PRP)

### Gotchas

1. **YAML parsing:** Handle PRPs without frontmatter gracefully
2. **File transitions:** Ensure executed/ directory exists before moving
3. **Serena unavailable:** Don't fail sync, just set serena_updated=false
4. **Drift score:** Normalize by total project files, not just Python
5. **Index rebuild:** Always invalidate cache after sync
6. **CLI delegation:** `ce update-context` is thin wrapper only

---

## VALIDATION

### Level 1: Syntax & Type Checking
```bash
cd syntropy-mcp && npm run build
cd syntropy-mcp && npm run lint
cd tools && uv run mypy ce/update_context.py
```

### Level 2: Unit Tests
```bash
cd syntropy-mcp && npm test src/tools/sync.test.ts
cd syntropy-mcp && npm test src/tools/drift.test.ts
cd tools && uv run pytest tests/test_update_context.py
```

### Level 3: Integration Tests
```bash
# Universal sync
syntropy sync /tmp/test-project --json

# Targeted sync
syntropy sync /tmp/test-project --prp PRP-15 --json

# CLI delegation
cd tools && uv run ce update-context --json

# E2E test on test-certinia (commit 9137b61)
# IMPORTANT: Always run on branch - sync modifies PRP YAML headers
cd ~/nc-rc/test-certinia && git checkout -b test-prp-29-3-sync

# Prerequisite: Run init first to create index (PRP-29.1)
syntropy init . --json

# Universal sync - all PRPs in context-engineering/PRPs/
syntropy sync . --json > sync-result.json

# Verify sync results:
jq -e '.prps_updated | length > 0' sync-result.json  # Multiple PRPs processed
jq -e '.drift.score >= 0' sync-result.json           # Drift score calculated
jq -e '.index.rebuilt == true' sync-result.json      # Index rebuilt
test -f .ce/syntropy-index.json                      # Index file created
test -f .ce/drift-report.md                          # Drift report generated

# Targeted sync - specific PRP
syntropy sync . --prp PRP-8.7 --json > targeted-result.json
jq -e '.prps_updated | length == 1' targeted-result.json
jq -e '.prps_updated[0].id == "PRP-8.7"' targeted-result.json

# Dry-run mode (safe - doesn't modify files)
syntropy sync . --dry-run --json > dryrun-result.json
jq -e '.warnings | any(contains("Dry-run"))' dryrun-result.json

# Verify YAML metadata updated in PRP files
grep -q "ce_updated:" context-engineering/PRPs/executed/PRP-8.7-job-isolation-architecture.md
grep -q "last_sync:" context-engineering/PRPs/executed/PRP-8.7-job-isolation-architecture.md

# MANDATORY cleanup - sync modifies PRP files:
cd ~/nc-rc/test-certinia && git checkout main && git branch -D test-prp-29-3-sync
git reset --hard HEAD  # Revert all PRP YAML changes
git clean -fd .ce      # Remove generated files
```

### Level 4: Pattern Conformance
- Error handling: Fast failure with 🔧 troubleshooting ✅
- No fishy fallbacks: All errors actionable ✅
- Graceful degradation: Works without Serena ✅
- CLI delegation: Thin wrapper pattern ✅

---

## SUCCESS CRITERIA

1. ⬜ MCP tool `syntropy_sync_context` functional
2. ⬜ PRP YAML headers updated with sync flags
3. ⬜ Implementation verification working (CE + Serena)
4. ⬜ Auto-transition PRPs to executed/ when verified
5. ⬜ Drift detection generates report with violations
6. ⬜ Knowledge index rebuilt after sync
7. ⬜ `ce update-context` delegates to Syntropy correctly
8. ⬜ Universal mode syncs all PRPs
9. ⬜ Targeted mode syncs specific PRP only
10. ⬜ All tests passing (unit + integration + E2E)

---

## IMPLEMENTATION NOTES

**Estimated Complexity:** Medium (3-4 days)
- Sync tool implementation: 1.5 days
- Drift detection: 1 day
- CLI delegation: 0.5 days
- Testing: 1 day

**Risk Level:** Low-Medium
- YAML parsing straightforward (js-yaml library)
- File transitions safe (rename operation)
- Graceful degradation if Serena unavailable
- No breaking changes to existing PRP format

**Dependencies:**
- PRP-29.1 (index schema defined)
- PRP-29.2 (query tools for framework docs)
- Syntropy MCP server (existing)
- Serena MCP (existing, optional)
- js-yaml for YAML parsing

**Files to Create:**
- `syntropy-mcp/src/tools/sync.ts` - MCP sync tool
- `syntropy-mcp/src/tools/drift.ts` - Drift detection
- `syntropy-mcp/src/tools/yaml-parser.ts` - YAML frontmatter helpers
- `syntropy-mcp/tests/tools/sync.test.ts` - Unit tests
- `tools/ce/update_context.py` - CLI delegation (replace existing)

**Files to Modify:**
- `syntropy-mcp/src/tools-definition.ts` - Add sync tool
- `syntropy-mcp/src/index.ts` - Register sync handler
- `tools/ce/__main__.py` - Update CLI entry point

**Files to Keep:**
- All existing PRPs (metadata updated in place)
- `.ce/syntropy-index.json` (rebuilt by sync)
- `.ce/drift-report.md` (generated by drift detection)
