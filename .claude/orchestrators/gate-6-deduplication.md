# Gate 6: Deduplication Verification (Orchestrator Template)

**Purpose**: Validate that memory files are properly deduplicated with no conflicts

**Status**: Implementation (Phase 2 PRP-48)

---

## Gate 6: Deduplication Verification

Validates that all memory files in `.serena/memories/` are properly deduplicated with no unexpected conflicts or duplicates.

### Checks

1. **Filename Uniqueness**: No duplicate filenames
2. **Content Hash Uniqueness**: No unexpected content duplicates
3. **Framework Files**: All 6 framework files present
4. **Project Files**: All project-specific files preserved
5. **Deduplication Count**: Verify deduplication events

### Expected Results

```
✓ Total unique files: 24
✓ Framework files: 6 (code-style, checklist, standards, commands, syntropy, tool-usage)
✓ Project files: 18+ (project-specific memories)
✓ Content duplicates: 0 unexpected
✓ Deduplication events: 3 (framework exact matches)
```

### Implementation

The validation is performed by:

1. **Scanning .serena/memories/**
   - List all .md files
   - Calculate SHA256 hash for each
   - Build filename and hash indices

2. **Checking for Duplicates**
   - Filename uniqueness check (no duplicates)
   - Hash-based content duplicate detection
   - Framework vs project file classification

3. **Generating Statistics**
   - Count framework files (known 6)
   - Count project-specific files
   - Calculate deduplication metrics
   - Identify any conflicts

4. **Pass/Fail Decision**
   - PASS: All unique, no conflicts, correct counts
   - FAIL: Duplicates found, missing files, wrong counts

### Output Format

```json
{
  "gate_id": "gate-6-deduplication",
  "status": "PASS" or "FAIL",
  "checks": {
    "filename_uniqueness": true/false,
    "content_hash_uniqueness": true/false,
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
    "project_files": ["codebase-structure.md", "project-overview.md", "..."]
  },
  "potential_issues": [],
  "summary": "All 24 memories properly deduplicated with no conflicts."
}
```

### Pass Criteria

**PASS** when all of:
- All filenames are unique (no duplicates)
- No unexpected content duplicates
- Framework file count = 6
- Project file count ≥ 18
- Total files = 24+
- No conflicts in deduplication

**FAIL** when any of:
- Duplicate filenames detected
- Unexpected content duplicates found
- Framework files missing
- Total file count incorrect
- Deduplication conflicts detected

---

## Integration with Iteration Orchestrator

Gate 6 is spawned as parallel Task agent (after Gates 1-5):

```
Phase 4: Spawn Validation Gates (Parallel)
  Gate 1 ┐
  Gate 2 ├─> All gates run simultaneously
  Gate 3 │
  Gate 4 │
  Gate 5 │
  Gate 6 ┘ (NEW)

Result: 6 independent validators complete in ~3 seconds
```

No inter-gate dependencies - all can run in parallel.

---

## Expected Performance

| Metric | Value |
|--------|-------|
| Gate execution time | ~0.5 seconds |
| File scanning | ~100ms (24 files) |
| Hash calculation | ~200ms (SHA256) |
| Analysis | ~150ms (dedup logic) |
| Output generation | ~50ms (JSON) |
| **Total** | **~0.5 seconds** |

All 6 gates in parallel: ~3 seconds total

---

## Validation Success (Iteration 4 - Expected)

**Gate Results**:
| Gate | Result | Details |
|------|--------|---------|
| Gate 1 | ✅ PASS | Framework Structure (6/6) |
| Gate 2 | ✅ PASS | Examples Migration (14 files) |
| Gate 3 | ✅ PASS | PRPs Migration (1 PRP, cleanup) |
| Gate 4 | ✅ PASS | Memories Domain (24 total) |
| Gate 5 | ✅ PASS | Critical Memories (3/3) |
| Gate 6 | ✅ PASS | Deduplication (no conflicts) |

**Overall**: ✅ 6/6 PASS (100% with enhanced statistics)

---

## Related Documentation

- `.ce/GATE-6-DEDUPLICATION-DESIGN.md` - Design document
- `.ce/SERENA-DOMAIN-ARCHITECTURE.md` - Architecture reference
- `.claude/orchestrators/iteration-orchestrator.md` - Main orchestrator
- `tmp/iteration-4-report.md` - Execution results (after Iteration 4)

---

**Status**: Ready for Phase 2 implementation
**Next**: Run Iteration 4 with all 6 gates
