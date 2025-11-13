# Gate 6: Deduplication Verification (Design)

**Purpose**: Validate that memory files are properly deduplicated with no conflicts or orphans

**Status**: DESIGN (for implementation in Phase 2)

---

## Gate 6 Overview

Validates the deduplication process during init-project blend:

```
Input: .serena/memories/ (24+ files)
  ↓
Check 1: No duplicate filenames
Check 2: No content duplicates (hash-based)
Check 3: Framework vs project breakdown
Check 4: Deduplication statistics
  ↓
Output: Detailed deduplication report
```

---

## Validation Checks

### Check 1: Filename Uniqueness

**Purpose**: Ensure no two files have the same name

```bash
Verify:
  ✓ All .md files in .serena/memories/ have unique names
  ✓ No files with same base name (even with different case)
  ✓ No hidden/backup files (.bak, .old, etc.)
```

**Expected**: All filenames unique (24+ files, all distinct)

**Failure**: If duplicates found, report names and locations

### Check 2: Content Hash Uniqueness

**Purpose**: Detect files with identical content

```bash
Algorithm:
  For each .md file:
    Calculate SHA256 hash of content

  Check for hash collisions:
    If multiple files have same hash:
      Report as "content duplicate"
      Identify which files
      Note if expected (framework std files might match)
```

**Expected**: No unexpected content duplicates

**Pass Criteria**:
- If duplicates exist, they should be framework standard files
- Framework files might legitimately have identical content
- Framework overrides project correctly

### Check 3: File Classification

**Purpose**: Categorize files as framework or project

```bash
Classification Logic:
  Framework Files (6 known):
    - code-style-conventions.md
    - task-completion-checklist.md
    - testing-standards.md
    - suggested-commands.md
    - tool-usage-syntropy.md
    - use-syntropy-tools-not-bash.md

  Project Files (18+):
    - All others in .serena/memories/
```

**Statistics**:
- Framework files: X (expected 6)
- Project files: Y (expected 18+)
- Total: X + Y (expected 24+)

### Check 4: Deduplication Audit Trail

**Purpose**: Track what was deduplicated and why

```bash
Deduplication Events:
  For each file in .serena/memories/:

    1. Check if exists in framework
       - If YES: Compare content
         * If identical: "framework-exact-match"
         * If different: "framework-override"
       - If NO: "project-specific"

    2. Check if exists in project original
       - If YES: Compare versions
         * If same: "preserved"
         * If different: "framework-supersedes"
       - If NO: "framework-added"
```

**Statistics Collected**:
- Total framework-exact-match: X (deduplicated)
- Total framework-override: Y (framework wins)
- Total project-specific: Z (preserved)
- Total framework-added: W (new)

---

## Output Format

### Gate 6 Result JSON

```json
{
  "gate_id": "gate-6-deduplication",
  "status": "PASS" or "FAIL",
  "checks": {
    "filename_uniqueness": true,
    "content_hash_uniqueness": true,
    "framework_file_count": 6,
    "project_file_count": 18,
    "total_files": 24
  },
  "deduplication_audit": {
    "framework_exact_matches": 3,
    "framework_overrides": 0,
    "project_specific_files": 18,
    "framework_added_files": 3,
    "total_deduplicated": 3,
    "total_preserved": 21
  },
  "file_breakdown": {
    "framework_files": [
      "code-style-conventions.md",
      "task-completion-checklist.md",
      "testing-standards.md",
      "suggested-commands.md",
      "tool-usage-syntropy.md",
      "use-syntropy-tools-not-bash.md"
    ],
    "project_files": [
      "codebase-structure.md",
      "project-overview.md",
      "... (18 total)"
    ]
  },
  "potential_issues": [
    {
      "type": "content-duplicate",
      "files": ["file1.md", "file2.md"],
      "severity": "warning",
      "reason": "Identical content but different sources"
    }
  ],
  "summary": "All 24 memories properly deduplicated with 6 framework files and 18 project files. No conflicts detected."
}
```

### Pass/Fail Criteria

**PASS** when:
- ✅ All filenames unique (no duplicates)
- ✅ No unexpected content duplicates
- ✅ Framework files (6) present
- ✅ Project files (18+) present
- ✅ Total files = framework + project

**FAIL** when:
- ❌ Duplicate filenames found
- ❌ Unexpected content duplicates
- ❌ Framework files missing
- ❌ Total file count wrong
- ❌ Deduplication failed

---

## Enhanced Gate Statistics

### For All Gates (1-6)

Each gate should provide statistics:

**Gate 1: Framework Structure**
```
✓ Framework files: 6/6 present
✓ Critical files: 3/3 (code-style, checklist, standards)
✓ Optional files: 3/3 (commands, syntropy, tool-usage)
✓ Location: .serena/memories/ (root canonical)
```

**Gate 2: Examples Migration**
```
✓ Examples migrated: 14 files
✓ Subdirectories: 2 (model/, patterns/)
✓ Cleanup: Root examples/ removed
```

**Gate 3: PRPs Migration**
```
✓ PRPs migrated: 1 (PRP-0-CONTEXT-ENGINEERING.md)
✓ Directory structure: .ce/PRPs/executed/system/
✓ Cleanup: Root PRPs/ removed
```

**Gate 4: Memories Domain**
```
✓ Canonical location: .serena/memories/
✓ Total files: 24 (6 framework + 18 project)
✓ Cleanup: .serena.old/ removed
```

**Gate 5: Critical Memories**
```
✓ code-style-conventions.md: Present (3744 bytes)
✓ task-completion-checklist.md: Present (2447 bytes)
✓ testing-standards.md: Present (2451 bytes)
✓ All at: .serena/memories/ (root level)
```

**Gate 6: Deduplication (NEW)**
```
✓ Framework files deduplicated: 6/6
✓ Project files preserved: 18/18
✓ Total unique files: 24
✓ Content duplicates: 0 unexpected
✓ Deduplication events: 3 (framework exact matches)
```

---

## Implementation Strategy

### Phase 2a: Implement Gate 6

1. Create gate-6-deduplication.md template
2. Define deduplication verification algorithm
3. Create JSON output schema
4. Test with Iteration 4

### Phase 2b: Enhance Gates 1-5 Statistics

1. Add `statistics` section to each gate output
2. Include file counts, breakdown, metrics
3. Provide detailed lists where applicable
4. Prepare for summary reporting

### Phase 2c: Run Iteration 4 with All 6 Gates

1. Execute `/iteration 4 certinia-test-target`
2. Spawn 6 parallel validation gates
3. Collect results from all gates
4. Generate comprehensive Iteration 4 report

---

## Expected Iteration 4 Results

```
Gate 1: Framework Structure        ✅ PASS (6/6 files)
Gate 2: Examples Migration         ✅ PASS (14 files)
Gate 3: PRPs Migration             ✅ PASS (1 PRP, cleanup OK)
Gate 4: Memories Domain            ✅ PASS (24 total)
Gate 5: Critical Memories          ✅ PASS (3/3 critical)
Gate 6: Deduplication (NEW)        ✅ PASS (24 unique, 0 conflicts)
═══════════════════════════════════════════════════════════
OVERALL: 6/6 PASS | Enhanced Statistics | Confidence: 10/10
```

---

## Files to Create/Modify

**Create**:
- `.ce/gate-6-deduplication.md` - Gate 6 template

**Modify**:
- `.claude/orchestrators/iteration-orchestrator.md` - Add Gate 6 to Phase 4
- `.claude/commands/iteration.md` - Document Gate 6
- `tmp/iteration-4-report.md` - Generate after execution

---

## Success Criteria for Phase 2

✅ Gate 6 design complete and documented
✅ Gate 6 implementation template created
✅ All gates 1-5 enhanced with statistics
✅ Iteration 4 executed with all 6 gates
✅ All 6 gates passing
✅ Comprehensive statistics in report
✅ Phase 2 committed

**Estimated Time**: ~2 hours

---

**Status**: Ready for implementation phase 2
