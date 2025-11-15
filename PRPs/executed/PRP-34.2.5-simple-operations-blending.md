---
prp_id: PRP-34.2.5
title: Simple Operations (PRPs, Commands)
status: pending
created: 2025-11-05
batch: 34
stage: 2
order: 5
complexity: low
estimated_hours: 1.5
dependencies: PRP-34.1.1
---

# Simple Operations (PRPs, Commands)

## 1. TL;DR

**Objective**: Implement move-all strategy for PRPs (no ID deduplication) and overwrite strategy for commands with backup

**What**: Create Python-only blending strategies for PRPs (move-all with hash dedupe) and commands (overwrite with backup)

**Why**: Enable simple file operations without LLM overhead for straightforward blending scenarios

**Effort**: 1.5 hours

**Dependencies**: PRP-34.1.1 (blending architecture)

## 2. Context

### Background

Phase 2 of CE 1.1 initialization requires blending user files with framework files. Two categories are simple enough to handle without LLM:

**PRPs**: Move all user PRPs to target location, no ID-based deduplication (different projects can have same PRP IDs like PRP-1, PRP-2)

**Commands**: Framework commands overwrite user commands (framework is authoritative), backup user versions

### Philosophy

**No ID Deduplication for PRPs**: Different projects can independently use PRP-1, PRP-2, etc. When migrating to CE, we preserve ALL PRPs by adding `type: user` header and placing in appropriate directory.

**Example**:
- User has `PRPs/PRP-1-authentication.md`
- Framework has `.ce/PRPs/executed/system/PRP-0-CONTEXT-ENGINEERING.md`
- Both coexist: User PRP becomes `.ce/PRPs/executed/PRP-1-authentication.md` with `type: user` header

**Framework Authority for Commands**: Commands like `/generate-prp`, `/execute-prp` are framework-defined. User customizations should go in separate custom commands (e.g. `/custom-workflow`).

### Requirements

**PRPMoveStrategy**:
1. Move all user PRPs from `PRPs/` to `.ce/PRPs/`
2. Parse status from content (executed/feature-requests)
3. Skip if exact file exists (hash-based dedupe)
4. Add `type: user` YAML header if missing
5. Preserve original PRP ID (no ID deduplication)

**CommandOverwriteStrategy**:
1. Backup existing commands to `.claude/commands.backup/`
2. Overwrite with framework commands from `.ce/commands/`
3. Skip if exact file exists (hash match)
4. Preserve user custom commands (not in framework)

**Hash-Based Deduplication**:
- Calculate SHA256 hash of file content
- Skip copy if identical file already exists at destination
- Prevents duplicate copies of same content

**YAML Header Format** (for PRPs without headers):
```yaml
---
type: user
source: target-project
created: "2025-11-04T00:00:00Z"
updated: "2025-11-04T00:00:00Z"
---
```

### Constraints and Considerations

**No LLM Required**: Pure Python file operations (move, copy, hash, parse)

**Idempotent**: Can run multiple times safely (hash dedupe prevents duplicates)

**Status Detection**: Parse PRP markdown content to determine if executed/feature-request:
- Look for keywords: "completed", "merged", "deployed" → executed
- Default to feature-requests if ambiguous

**File Safety**:
- Never overwrite without backup (commands)
- Never delete user files
- Atomic operations (use temp files + rename)

### Acceptance Criteria

1. `PRPMoveStrategy` class implemented with hash-based dedupe
2. All user PRPs moved to `.ce/PRPs/[executed|feature-requests]/`
3. PRPs without YAML header get `type: user` header added
4. No ID-based deduplication (all PRPs preserved)
5. `CommandOverwriteStrategy` class implemented
6. User commands backed up to `.claude/commands.backup/`
7. Framework commands overwrite existing
8. Unit tests pass (≥4 tests, ≥80% coverage)

## 3. Implementation Steps

### Phase 1: PRPMoveStrategy (45 min)

**File**: `tools/ce/blending/strategies/simple.py`

1. Create `PRPMoveStrategy` class (inherits `BaseRealStrategy`)
2. Implement `execute(input_data)` method:
   - Input: `{"source_dir": Path, "target_dir": Path}`
   - Output: `{"prps_moved": int, "prps_skipped": int, "errors": []}`
3. Helper method `_calculate_hash(file_path: Path) -> str`
4. Helper method `_parse_prp_status(content: str) -> str` (executed|feature-requests)
5. Helper method `_add_user_header(content: str) -> str`
6. Helper method `_has_yaml_header(content: str) -> bool`

**Algorithm**:
```python
for prp_file in source_dir.glob("*.md"):
    # 1. Read content
    content = read_file(prp_file)

    # 2. Check if has YAML header
    if not has_yaml_header(content):
        content = add_user_header(content)

    # 3. Parse status (executed vs feature-requests)
    status = parse_prp_status(content)

    # 4. Determine destination
    dest = target_dir / status / prp_file.name

    # 5. Hash-based dedupe
    if dest.exists():
        if calculate_hash(prp_file) == calculate_hash(dest):
            skip()
            continue

    # 6. Write to destination
    write_file(dest, content)
```

### Phase 2: CommandOverwriteStrategy (30 min)

**File**: `tools/ce/blending/strategies/simple.py`

1. Create `CommandOverwriteStrategy` class (inherits `BaseRealStrategy`)
2. Implement `execute(input_data)` method:
   - Input: `{"source_dir": Path, "target_dir": Path, "backup_dir": Path}`
   - Output: `{"commands_overwritten": int, "commands_backed_up": int, "errors": []}`
3. Helper method `_backup_file(src: Path, backup_dir: Path)`

**Algorithm**:
```python
for cmd_file in source_dir.glob("*.md"):
    target_file = target_dir / cmd_file.name

    # 1. Backup existing command if present
    if target_file.exists():
        backup_file(target_file, backup_dir)

    # 2. Hash-based dedupe
    if target_file.exists():
        if calculate_hash(cmd_file) == calculate_hash(target_file):
            skip()
            continue

    # 3. Overwrite with framework command
    copy_file(cmd_file, target_file)
```

### Phase 3: Testing (15 min)

**File**: `tools/tests/test_simple_strategies.py`

**Tests** (≥4 required):
1. `test_prp_move_adds_user_header`: PRPs without YAML get header
2. `test_prp_move_preserves_all_ids`: No ID deduplication (PRP-1, PRP-1 both kept)
3. `test_prp_move_hash_dedupe`: Skips if exact file exists
4. `test_prp_status_detection`: Parses executed vs feature-requests
5. `test_command_backup`: User commands backed up before overwrite
6. `test_command_overwrite`: Framework commands overwrite existing
7. `test_command_hash_dedupe`: Skips if identical command exists

## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**: `cd tools && uv run pytest tests/test_simple_strategies.py -v`

**Success Criteria**:
- ≥7 tests pass
- Code coverage ≥80%
- No regressions in existing tests

### Gate 2: Integration Test

**Manual Test Scenario**:

```bash
# Setup test directories
mkdir -p /tmp/test-blending/{source,target}/.ce/PRPs/{executed,feature-requests}
mkdir -p /tmp/test-blending/{source,target}/.claude/commands

# Create test PRP (no YAML header)
echo "# PRP-1: Test Feature

Status: completed
" > /tmp/test-blending/source/PRPs/PRP-1-test.md

# Create test command
echo "Test command" > /tmp/test-blending/source/.claude/commands/test-cmd.md

# Run strategies
cd tools
uv run python -c "
from pathlib import Path
from ce.blending.strategies.simple import PRPMoveStrategy, CommandOverwriteStrategy

# Test PRP move
prp_strategy = PRPMoveStrategy()
result = prp_strategy.execute({
    'source_dir': Path('/tmp/test-blending/source/PRPs'),
    'target_dir': Path('/tmp/test-blending/target/.ce/PRPs')
})
print('PRPs moved:', result['prps_moved'])

# Test command overwrite
cmd_strategy = CommandOverwriteStrategy()
result = cmd_strategy.execute({
    'source_dir': Path('/tmp/test-blending/source/.claude/commands'),
    'target_dir': Path('/tmp/test-blending/target/.claude/commands'),
    'backup_dir': Path('/tmp/test-blending/target/.claude/commands.backup')
})
print('Commands overwritten:', result['commands_overwritten'])
"

# Verify results
cat /tmp/test-blending/target/.ce/PRPs/executed/PRP-1-test.md  # Should have type: user header
ls /tmp/test-blending/target/.claude/commands.backup/         # Should have backup
```

**Success Criteria**:
- PRP has `type: user` header
- PRP in correct directory (executed)
- Command backed up
- Command overwritten

### Gate 3: Hash Deduplication Works

**Test Scenario**:

```bash
# Create identical files
echo "Same content" > /tmp/test-blending/source/PRPs/PRP-2-dup.md
echo "Same content" > /tmp/test-blending/target/.ce/PRPs/executed/PRP-2-dup.md

# Run strategy (should skip)
cd tools
uv run python -c "
from pathlib import Path
from ce.blending.strategies.simple import PRPMoveStrategy

strategy = PRPMoveStrategy()
result = strategy.execute({
    'source_dir': Path('/tmp/test-blending/source/PRPs'),
    'target_dir': Path('/tmp/test-blending/target/.ce/PRPs')
})
print('Skipped:', result['prps_skipped'])  # Should be 1
"
```

**Success Criteria**:
- Skipped count = 1
- File not duplicated

## 5. Testing Strategy

### Test Framework

pytest

### Test Files

- `tools/tests/test_simple_strategies.py` (unit tests)

### Coverage Requirements

- Unit test coverage: ≥80%
- All critical paths tested (move, backup, hash dedupe, header add)
- Edge cases: missing directories, corrupted files, permission errors

### Test Patterns

**Strategy Pattern Testing**:
- Real strategies (no mocks) for file operations
- Temp directories for isolation
- Cleanup after each test

**Example Test**:
```python
def test_prp_move_adds_user_header(tmp_path):
    # Setup
    source = tmp_path / "source" / "PRPs"
    target = tmp_path / "target" / ".ce" / "PRPs"
    source.mkdir(parents=True)
    target.mkdir(parents=True)

    prp_file = source / "PRP-1-test.md"
    prp_file.write_text("# PRP-1: Test\n\nContent here")

    # Execute
    strategy = PRPMoveStrategy()
    result = strategy.execute({
        "source_dir": source,
        "target_dir": target
    })

    # Verify
    assert result["prps_moved"] == 1
    moved_content = (target / "feature-requests" / "PRP-1-test.md").read_text()
    assert "type: user" in moved_content
    assert "source: target-project" in moved_content
```

## 6. Rollout Plan

### Phase 1: Development (1 hour)

1. Create `tools/ce/blending/strategies/` directory
2. Create `simple.py` with both strategies
3. Write unit tests
4. Pass validation gates

### Phase 2: Integration (30 min)

1. Update `tools/ce/blending/__init__.py` to export strategies
2. Update initialization workflow to use strategies
3. Document usage in `examples/INITIALIZATION.md`

### Phase 3: Documentation (15 min)

1. Add docstrings to all methods
2. Add usage examples to module docstring
3. Update this PRP with final results

---

## Implementation Notes

**File Location**: `tools/ce/blending/strategies/simple.py`

**Dependencies**:
- `pathlib.Path` (file operations)
- `hashlib.sha256` (hash calculation)
- `shutil.copy2` (preserve metadata)
- `re` (YAML header detection)

**Error Handling**:
- Wrap file operations in try/except
- Collect errors in result dict
- Continue processing on single file failure
- Log errors for troubleshooting

**Performance**:
- Hash calculation: O(n) where n = file size
- Expected: <1s for typical PRP/command sets (<100 files)
- Bottleneck: Disk I/O, not CPU

**Future Enhancements** (out of scope):
- Parallel processing for large file sets
- Progress reporting for long-running operations
- Conflict resolution UI for non-identical duplicates

---

## Linear Integration

**Issue ID**: TBD (will be created during batch generation)

**Project**: Context Engineering

**Assignee**: blazej.przybyszewski@gmail.com

**Team**: Blaise78

---

## Research Findings

**Strategy Pattern References**:
- `tools/ce/vacuum_strategies/base.py`: Base class pattern for cleanup strategies
- `tools/ce/testing/strategy.py`: Protocol-based strategy interface

**Hash-Based Deduplication**:
- SHA256 for collision resistance
- Read file in chunks (4KB) to handle large files
- Compare hex digest strings

**YAML Frontmatter Detection**:
- Check first line == "---"
- Used in `vacuum_strategies/base.py::_has_yaml_frontmatter()`
