---
prp_id: PRP-34.2.4
feature_name: Settings Blending Strategy
status: completed
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T21:30:00Z
complexity: medium
estimated_hours: 2.0
dependencies: PRP-34.1.1
batch_id: 34
stage: 2
execution_order: 5
merge_order: 5
conflict_potential: NONE
worktree_path: ../ctx-eng-plus-prp-34-2-4
branch_name: prp-34-2-4-settings-strategy
issue: TBD  # To be created via Linear MCP
---

# Settings Blending Strategy

## 1. TL;DR

**Objective**: Port PRP-33 TypeScript settings blending logic to Python for CE framework initialization

**What**: Implement `SettingsBlendStrategy` class with 3 rule-based blending rules for `.claude/settings.local.json` files

**Why**: Enable automated CE framework initialization with intelligent permission merging (no LLM needed)

**Effort**: 2 hours (implementation + testing)

**Dependencies**: PRP-34.1.1 (BlendStrategy base interface)

## 2. Context

### Background

PRP-33 implemented settings blending logic in TypeScript for syntropy-mcp integration. This PRP ports that logic to Python for use in CE framework's blending subsystem.

**Settings Blending Philosophy**: "Copy ours (CE settings) + import target permissions where not contradictory"

**Three Blending Rules** (from PRP-33):

1. **CE Deny Precedence**: Target allow entries that appear in CE deny list → Remove from target allow
2. **List Merging**: CE entries → Add to target's respective lists (deduplicate)
3. **Single Membership**: CE entries → Ensure not in other lists (CE list takes precedence)

**Example Scenario**:

```json
// CE settings (from infrastructure package)
{
  "allow": ["Bash(git:*)", "Read(//)"],
  "deny": ["mcp__syntropy__filesystem_read_file"],
  "ask": ["Bash(rm:*)", "Bash(mv:*)"]
}

// Target project settings (before blending)
{
  "allow": ["mcp__syntropy__filesystem_read_file", "Write(//)"],
  "deny": ["Bash(cp:*)"],
  "ask": []
}

// After blending (applying Rules 1-3)
{
  "allow": [
    "Write(//)",           // Target entry preserved
    "Bash(git:*)",        // CE entry added
    "Read(//)"            // CE entry added
  ],
  "deny": [
    "Bash(cp:*)",         // Target entry preserved
    "mcp__syntropy__filesystem_read_file"  // CE entry added
  ],
  "ask": [
    "Bash(rm:*)",         // CE entry added
    "Bash(mv:*)"          // CE entry added
  ]
}
```

### Constraints and Considerations

**No LLM Logic**: Rule-based blending only (deterministic, fast, testable)

**JSON Validation**: Must validate JSON syntax before and after blending

**Single Responsibility**: SettingsBlendStrategy only handles settings domain (not CLAUDE.md, not commands)

**Error Handling**: Fast failure with actionable troubleshooting (no silent corruption)

**Testing Requirements**:
- ≥5 unit tests covering all 3 rules
- ≥80% code coverage
- Test edge cases (empty settings, missing lists, malformed JSON)

### Documentation References

**TypeScript Reference** (PRP-33, lines 270-317):
```typescript
function blendSettings(targetProjectDir: string, settingsBackupPath: string) {
  const ceSettings = loadJson(`${targetProjectDir}/.claude/settings.local.json`)
  const targetSettings = fileExists(settingsBackupPath)
    ? loadJson(settingsBackupPath)
    : { allow: [], deny: [], ask: [] }

  // Rule 1: Remove from target's allow list entries in CE's deny list
  targetSettings.allow = targetSettings.allow.filter(
    entry => !ceSettings.deny.includes(entry)
  )

  // Rule 2: Add CE entries to target's respective lists (deduplicate)
  for (const list of ['allow', 'deny', 'ask']) {
    targetSettings[list] = [
      ...new Set([...targetSettings[list], ...ceSettings[list]])
    ]
  }

  // Rule 3: Ensure CE entries only appear in one list
  for (const list of ['allow', 'deny', 'ask']) {
    for (const entry of ceSettings[list]) {
      const otherLists = ['allow', 'deny', 'ask'].filter(l => l !== list)
      for (const otherList of otherLists) {
        targetSettings[otherList] = targetSettings[otherList].filter(
          e => e !== entry
        )
      }
    }
  }

  writeJson(targetSettingsPath, targetSettings)
}
```

**Python Reference Pattern** (Strategy Protocol):
```python
from typing import Protocol, Dict, Any

class BlendStrategy(Protocol):
    def can_handle(self, domain: str) -> bool:
        """Return True if strategy handles this domain."""
        ...

    def blend(self, ce_content: str, target_content: str) -> str:
        """Blend CE and target content, return blended result."""
        ...

    def validate(self, blended_content: str) -> bool:
        """Validate blended content. Raise on failure."""
        ...
```

## 3. Implementation Steps

### Phase 1: SettingsBlendStrategy Class (45 min)

**Goal**: Create strategy class with BlendStrategy interface

1. Create `tools/ce/blending/strategies/settings.py`:

```python
"""Settings blending strategy for .claude/settings.local.json files.

Implements 3-rule blending logic from PRP-33:
1. CE deny removes from target allow
2. Merge CE entries to target lists (dedupe)
3. Ensure tool appears in ONE list only
"""

import json
from typing import Dict, List, Set


class SettingsBlendStrategy:
    """Blend CE and target settings.local.json files.

    Philosophy: Copy ours (CE settings) + import target permissions where not contradictory.

    Blending Rules:
    1. CE Deny Precedence: Target allow entries in CE deny → Remove from target allow
    2. List Merging: CE entries → Add to target's respective lists (deduplicate)
    3. Single Membership: CE entries → Ensure not in other lists (CE list takes precedence)
    """

    def can_handle(self, domain: str) -> bool:
        """Return True for 'settings' domain.

        Args:
            domain: Domain identifier (e.g., 'settings', 'claude-md', 'commands')

        Returns:
            True if domain == 'settings', False otherwise
        """
        return domain == "settings"

    def blend(self, ce_content: str, target_content: str) -> str:
        """Blend CE and target settings with 3-rule logic.

        Args:
            ce_content: CE settings JSON string
            target_content: Target project settings JSON string (may be empty)

        Returns:
            Blended settings JSON string

        Raises:
            ValueError: If JSON parsing fails or settings invalid
            RuntimeError: If blending logic fails
        """
        # Parse JSON
        try:
            ce_settings = json.loads(ce_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"CE settings JSON invalid: {e}")

        try:
            target_settings = json.loads(target_content) if target_content.strip() else {}
        except json.JSONDecodeError as e:
            raise ValueError(f"Target settings JSON invalid: {e}")

        # Initialize default structure if missing
        if not target_settings:
            target_settings = {"allow": [], "deny": [], "ask": []}

        for list_name in ["allow", "deny", "ask"]:
            if list_name not in target_settings:
                target_settings[list_name] = []
            if list_name not in ce_settings:
                ce_settings[list_name] = []

        # Rule 1: Remove from target's allow list entries in CE's deny list
        target_settings["allow"] = [
            entry for entry in target_settings["allow"]
            if entry not in ce_settings["deny"]
        ]

        # Rule 2: Add CE entries to target's respective lists (deduplicate)
        for list_name in ["allow", "deny", "ask"]:
            merged = set(target_settings[list_name]) | set(ce_settings[list_name])
            target_settings[list_name] = sorted(merged)

        # Rule 3: Ensure CE entries only appear in one list
        for list_name in ["allow", "deny", "ask"]:
            other_lists = [l for l in ["allow", "deny", "ask"] if l != list_name]
            for entry in ce_settings[list_name]:
                for other_list in other_lists:
                    if entry in target_settings[other_list]:
                        target_settings[other_list].remove(entry)

        # Serialize back to JSON
        return json.dumps(target_settings, indent=2)

    def validate(self, blended_content: str) -> bool:
        """Validate blended settings JSON.

        Checks:
        1. Valid JSON syntax
        2. Contains allow, deny, ask lists
        3. No duplicates across lists

        Args:
            blended_content: Blended settings JSON string

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        # Check JSON syntax
        try:
            settings = json.loads(blended_content)
        except json.JSONDecodeError as e:
            raise ValueError(f"Blended settings JSON invalid: {e}")

        # Check structure
        for list_name in ["allow", "deny", "ask"]:
            if list_name not in settings:
                raise ValueError(f"Missing '{list_name}' list in blended settings")
            if not isinstance(settings[list_name], list):
                raise ValueError(f"'{list_name}' must be a list, got {type(settings[list_name])}")

        # Check no duplicates across lists
        all_entries = (
            settings["allow"] + settings["deny"] + settings["ask"]
        )
        duplicates = [entry for entry in all_entries if all_entries.count(entry) > 1]
        if duplicates:
            raise ValueError(f"Duplicate entries across lists: {set(duplicates)}")

        return True
```

**Validation**:
```bash
# Check file created
ls -lh tools/ce/blending/strategies/settings.py
# Expected: File exists, ~150 lines
```

### Phase 2: Unit Tests (1 hour)

**Goal**: Test all 3 blending rules + edge cases

2. Create `tools/tests/test_blend_settings.py`:

```python
"""Tests for SettingsBlendStrategy.

Tests 3 blending rules:
1. CE deny removes from target allow
2. Merge CE entries to target lists (dedupe)
3. Ensure tool appears in ONE list only
"""

import json
import pytest
from ce.blending.strategies.settings import SettingsBlendStrategy


def test_can_handle_settings_domain():
    """Test can_handle() returns True for 'settings' domain."""
    strategy = SettingsBlendStrategy()
    assert strategy.can_handle("settings") is True
    assert strategy.can_handle("claude-md") is False
    assert strategy.can_handle("commands") is False


def test_rule1_ce_deny_removes_from_target_allow():
    """Test Rule 1: CE deny entries remove from target allow."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({
        "allow": [],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": []
    })

    target_settings = json.dumps({
        "allow": ["mcp__syntropy__filesystem_read_file", "Write(//)"],
        "deny": [],
        "ask": []
    })

    result = strategy.blend(ce_settings, target_settings)
    result_dict = json.loads(result)

    # mcp__syntropy__filesystem_read_file should be removed from allow
    assert "mcp__syntropy__filesystem_read_file" not in result_dict["allow"]
    assert "Write(//)" in result_dict["allow"]
    assert "mcp__syntropy__filesystem_read_file" in result_dict["deny"]


def test_rule2_merge_ce_entries_dedupe():
    """Test Rule 2: CE entries added to target lists (deduplicated)."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({
        "allow": ["Bash(git:*)", "Read(//)"],
        "deny": [],
        "ask": ["Bash(rm:*)"]
    })

    target_settings = json.dumps({
        "allow": ["Read(//)", "Write(//)"],  # Read(//) duplicate
        "deny": [],
        "ask": []
    })

    result = strategy.blend(ce_settings, target_settings)
    result_dict = json.loads(result)

    # All CE entries added, deduplicated
    assert "Bash(git:*)" in result_dict["allow"]
    assert "Read(//)" in result_dict["allow"]
    assert "Write(//)" in result_dict["allow"]
    assert result_dict["allow"].count("Read(//)")  == 1  # No duplicate
    assert "Bash(rm:*)" in result_dict["ask"]


def test_rule3_ce_entries_single_membership():
    """Test Rule 3: CE entries only in one list (CE list takes precedence)."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({
        "allow": ["Bash(git:*)"],
        "deny": ["mcp__syntropy__git_status"],
        "ask": []
    })

    target_settings = json.dumps({
        "allow": ["mcp__syntropy__git_status"],  # Conflicts with CE deny
        "deny": ["Bash(git:*)"],  # Conflicts with CE allow
        "ask": []
    })

    result = strategy.blend(ce_settings, target_settings)
    result_dict = json.loads(result)

    # CE allow entry should only be in allow
    assert "Bash(git:*)" in result_dict["allow"]
    assert "Bash(git:*)" not in result_dict["deny"]

    # CE deny entry should only be in deny
    assert "mcp__syntropy__git_status" in result_dict["deny"]
    assert "mcp__syntropy__git_status" not in result_dict["allow"]


def test_blend_empty_target_settings():
    """Test blending with empty target settings."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({
        "allow": ["Read(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)"]
    })

    target_settings = ""

    result = strategy.blend(ce_settings, target_settings)
    result_dict = json.loads(result)

    # CE settings copied as-is
    assert result_dict["allow"] == ["Read(//)"]
    assert result_dict["deny"] == ["mcp__syntropy__filesystem_read_file"]
    assert result_dict["ask"] == ["Bash(rm:*)"]


def test_blend_malformed_ce_settings():
    """Test blend() raises on malformed CE settings."""
    strategy = SettingsBlendStrategy()

    ce_settings = "{ invalid json"
    target_settings = json.dumps({"allow": [], "deny": [], "ask": []})

    with pytest.raises(ValueError, match="CE settings JSON invalid"):
        strategy.blend(ce_settings, target_settings)


def test_blend_malformed_target_settings():
    """Test blend() raises on malformed target settings."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({"allow": [], "deny": [], "ask": []})
    target_settings = "{ invalid json"

    with pytest.raises(ValueError, match="Target settings JSON invalid"):
        strategy.blend(ce_settings, target_settings)


def test_validate_valid_settings():
    """Test validate() passes for valid settings."""
    strategy = SettingsBlendStrategy()

    valid_settings = json.dumps({
        "allow": ["Read(//)", "Write(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)"]
    })

    assert strategy.validate(valid_settings) is True


def test_validate_missing_list():
    """Test validate() raises if list missing."""
    strategy = SettingsBlendStrategy()

    invalid_settings = json.dumps({
        "allow": [],
        "deny": []
        # Missing "ask" list
    })

    with pytest.raises(ValueError, match="Missing 'ask' list"):
        strategy.validate(invalid_settings)


def test_validate_duplicate_entries():
    """Test validate() raises if duplicate entries across lists."""
    strategy = SettingsBlendStrategy()

    invalid_settings = json.dumps({
        "allow": ["Read(//)", "Write(//)"],
        "deny": ["Read(//)", "mcp__syntropy__filesystem_read_file"],  # Duplicate "Read(//)"
        "ask": []
    })

    with pytest.raises(ValueError, match="Duplicate entries across lists"):
        strategy.validate(invalid_settings)


def test_comprehensive_blend_scenario():
    """Test comprehensive scenario from PRP-33 documentation."""
    strategy = SettingsBlendStrategy()

    ce_settings = json.dumps({
        "allow": ["Bash(git:*)", "Read(//)"],
        "deny": ["mcp__syntropy__filesystem_read_file"],
        "ask": ["Bash(rm:*)", "Bash(mv:*)"]
    })

    target_settings = json.dumps({
        "allow": ["mcp__syntropy__filesystem_read_file", "Write(//)"],
        "deny": ["Bash(cp:*)"],
        "ask": []
    })

    result = strategy.blend(ce_settings, target_settings)
    result_dict = json.loads(result)

    # Verify expected output
    expected_allow = sorted(["Write(//)", "Bash(git:*)", "Read(//)")])
    expected_deny = sorted(["Bash(cp:*)", "mcp__syntropy__filesystem_read_file"])
    expected_ask = sorted(["Bash(rm:*)", "Bash(mv:*)"])

    assert result_dict["allow"] == expected_allow
    assert result_dict["deny"] == expected_deny
    assert result_dict["ask"] == expected_ask

    # Validate result
    assert strategy.validate(result) is True
```

**Validation**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py -v
# Expected: 11/11 tests pass
```

### Phase 3: Integration and Coverage (15 min)

**Goal**: Verify coverage and integration

3. Run tests with coverage:

```bash
cd tools
uv run pytest tests/test_blend_settings.py --cov=ce.blending.strategies.settings --cov-report=term-missing -v
```

**Expected Coverage**: ≥80%

4. Test integration with BlendStrategy Protocol (if exists):

```bash
cd tools
python3 -c "
from ce.blending.strategies.settings import SettingsBlendStrategy

strategy = SettingsBlendStrategy()
print(f'can_handle(settings): {strategy.can_handle(\"settings\")}')
print(f'can_handle(other): {strategy.can_handle(\"other\")}')
print('✅ Strategy implements BlendStrategy interface')
"
```

## 4. Validation Gates

### Gate 1: Rule 1 - CE Deny Precedence

**Command**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py::test_rule1_ce_deny_removes_from_target_allow -v
```

**Expected**: Test passes - CE deny entries remove from target allow

**On Failure**:
- Verify Rule 1 logic in blend() method
- Check CE deny list filtering target allow list
- Ensure target allow list updated before Rule 2

### Gate 2: Rule 2 - List Merging

**Command**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py::test_rule2_merge_ce_entries_dedupe -v
```

**Expected**: Test passes - CE + target lists merged, deduplicated

**On Failure**:
- Verify set() deduplication in Rule 2
- Check all CE entries added to target lists
- Ensure sorted() for deterministic output

### Gate 3: Rule 3 - Single Membership

**Command**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py::test_rule3_ce_entries_single_membership -v
```

**Expected**: Test passes - CE entries only in one list (CE list precedence)

**On Failure**:
- Verify Rule 3 logic removes CE entries from other lists
- Check iteration order (process all lists)
- Ensure CE list takes precedence (not target)

### Gate 4: JSON Validation

**Command**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py::test_validate_valid_settings -v
uv run pytest tests/test_blend_settings.py::test_validate_missing_list -v
uv run pytest tests/test_blend_settings.py::test_validate_duplicate_entries -v
```

**Expected**: All validation tests pass

**On Failure**:
- Check validate() JSON parsing
- Verify structure checks (allow, deny, ask lists)
- Ensure duplicate detection logic correct

### Gate 5: Unit Tests Pass

**Command**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py -v
```

**Expected**: 11/11 tests pass, ≥80% coverage

**On Failure**:
- Check test failures for specific rule violations
- Verify edge cases (empty settings, malformed JSON)
- Re-run with `-vv` for detailed output

### Gate 6: Comprehensive Scenario

**Command**:
```bash
cd tools
uv run pytest tests/test_blend_settings.py::test_comprehensive_blend_scenario -v
```

**Expected**: PRP-33 example scenario produces correct output

**On Failure**:
- Compare expected vs actual output
- Verify all 3 rules applied correctly
- Check sorting and deduplication

## 5. Testing Strategy

### Test Framework

pytest (project standard)

### Test Command

```bash
cd tools
uv run pytest tests/test_blend_settings.py -v
uv run pytest tests/test_blend_settings.py --cov=ce.blending.strategies.settings --cov-report=term-missing -v
```

### Test Coverage

**Rule-Based Tests** (≥5 tests):
- [ ] Rule 1: CE deny removes from target allow
- [ ] Rule 2: CE + target lists merged (dedupe)
- [ ] Rule 3: CE entries single membership
- [ ] Empty target settings (edge case)
- [ ] Comprehensive scenario (PRP-33 example)

**Validation Tests** (≥3 tests):
- [ ] Valid settings pass validation
- [ ] Missing list fails validation
- [ ] Duplicate entries fail validation

**Error Handling Tests** (≥2 tests):
- [ ] Malformed CE settings raise ValueError
- [ ] Malformed target settings raise ValueError

**Coverage Target**: ≥80%

**Coverage Breakdown**:
- blend() method: 100% (all 3 rules + edge cases)
- validate() method: 100% (structure + duplicate checks)
- can_handle() method: 100% (domain check)

## 6. Rollout Plan

### Phase 1: Implementation

1. Create `tools/ce/blending/strategies/` directory (if not exists)
2. Implement `settings.py` (SettingsBlendStrategy class)
3. Verify Python syntax: `python3 -m py_compile tools/ce/blending/strategies/settings.py`

### Phase 2: Testing

1. Create `tests/test_blend_settings.py`
2. Run tests: `cd tools && uv run pytest tests/test_blend_settings.py -v`
3. Verify coverage: `cd tools && uv run pytest tests/test_blend_settings.py --cov=ce.blending.strategies.settings --cov-report=term-missing`

### Phase 3: Integration

1. Test can_handle() method
2. Test blend() method with example data
3. Test validate() method with blended output
4. Verify BlendStrategy Protocol compliance (if exists)

### Phase 4: Documentation

1. Add docstrings to all methods
2. Include usage examples in module docstring
3. Cross-reference PRP-33 TypeScript implementation

### Phase 5: Rollback Plan

**If tests fail or coverage insufficient**:

1. Revert changes:
   ```bash
   git checkout HEAD -- tools/ce/blending/strategies/settings.py
   git checkout HEAD -- tools/tests/test_blend_settings.py
   ```

2. Debug specific failures:
   ```bash
   cd tools
   uv run pytest tests/test_blend_settings.py -vv --tb=short
   ```

3. Fix and re-test iteratively

---

## Research Findings

### Codebase Analysis

**Strategy Pattern Usage**:
- `tools/ce/testing/strategy.py`: Protocol-based strategy interface
- `tools/ce/vacuum_strategies/`: Multiple strategy implementations
- Pattern: Protocol with execute(), is_mocked() methods

**Blending Strategy Interface** (inferred from PRP-34.1.1 dependency):
```python
class BlendStrategy(Protocol):
    def can_handle(self, domain: str) -> bool: ...
    def blend(self, ce_content: str, target_content: str) -> str: ...
    def validate(self, blended_content: str) -> bool: ...
```

**Testing Standards**:
- pytest framework (project standard)
- ≥80% coverage target
- Real functionality (no mocks in production code)
- TDD approach (test first, implement, refactor)

**Settings Files**:
- `.claude/settings.local.json`: Permission lists (allow, deny, ask)
- Structure: `{"allow": [...], "deny": [...], "ask": [...]}`
- Used by Claude Code for command permissions

### TypeScript Reference (PRP-33)

**Settings Blending Algorithm** (lines 270-317):

1. Load CE and target settings
2. Filter target allow list (remove CE deny entries)
3. Merge CE entries to target lists (deduplicate)
4. Ensure CE entries single membership (remove from other lists)
5. Write blended settings

**Example Scenario** (lines 327-359):
- CE: allow git/read, deny filesystem, ask rm/mv
- Target: allow filesystem/write, deny cp
- Result: allow git/read/write, deny filesystem/cp, ask rm/mv

**Key Insights**:
- No LLM logic (deterministic, rule-based)
- CE permissions take precedence (override conflicts)
- Philosophy: "Copy ours + import target where not contradictory"

### Documentation Sources

- **Internal**: PRP-33 (TypeScript reference implementation)
- **Internal**: tools/ce/testing/strategy.py (Strategy pattern)
- **Internal**: .claude/settings.local.json (settings file structure)
- **Standard**: Python json module (JSON parsing/validation)
- **Standard**: pytest framework (testing)
