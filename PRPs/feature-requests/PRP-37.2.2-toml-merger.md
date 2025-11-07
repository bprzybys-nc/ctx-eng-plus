---
prp_id: "37.2.2"
feature_name: "Merge pyproject.toml with Version Unification"
status: pending
created: "2025-11-06T00:00:00Z"
updated: "2025-11-06T00:00:00Z"
complexity: high
estimated_hours: 6.0
dependencies: ["37.1.1"]
batch: 37
stage: "stage-2-parallel"
execution_order: 3
merge_order: 4
conflict_potential: high
issue: "TBD"
linear_issue_payload: ".tmp/batch-gen/create_linear_issue_37_2_2.py"
files_created:
  - "tools/ce/toml_merger.py"
  - "tools/ce/toml_formats/__init__.py"
  - "tools/ce/toml_formats/pep621_handler.py"
  - "tools/ce/toml_formats/poetry_handler.py"
  - "tools/ce/toml_formats/setuptools_handler.py"
  - "tools/ce/toml_formats/version_resolver.py"
files_modified:
  - "tools/ce/init_project.py"
  - "tools/pyproject.toml"
plan_context: "Part of PRP-36.3: Fix Init-Project Issues from E2E Testing. Implements intelligent TOML merging with version unification to handle dependency conflicts in target projects. Uses version intersection (not 'higher wins') per user requirement."
---

# Merge pyproject.toml with Version Unification

## 1. TL;DR

**Objective**: Intelligently merge framework pyproject.toml into target project's existing pyproject.toml (any format)

**What**: Create TomlMerger class that supports PEP 621, Poetry, and Setuptools formats with version intersection strategy using packaging.specifiers.SpecifierSet

**Why**: Target projects may have existing pyproject.toml files with conflicting dependency versions. Current init process fails or silently breaks dependencies. Version intersection ensures compatibility.

**Effort**: 6 hours (3h implementation with strategy pattern refactoring, 1.5h testing, 1.5h integration)

**Dependencies**: PRP-37.1.1 (Extract Phase implementation)

**Conflict Notes**: High risk - dependency conflicts can break target project installation. Includes comprehensive error handling and UV validation. No file conflicts with other PRPs (creates new toml_merger.py).

## 2. Context

### Background

The CE framework installation currently fails when target projects have existing `pyproject.toml` files:

**Current Issues**:
1. **No merge logic**: Framework overwrites target TOML completely
2. **Version conflicts**: Framework deps (e.g., `pyyaml>=6.0`) conflict with target deps (e.g., `pyyaml~=5.4`)
3. **Format incompatibility**: Target may use Poetry/Setuptools format, framework uses PEP 621
4. **Silent failures**: UV sync fails post-merge with cryptic errors

**User Requirement** (from PRP-36.3 discussion):
- Use **version intersection**, NOT "higher version wins"
- Example: Framework `>=6.0` + Target `~=5.4` → **incompatible** (no intersection), raise error
- Example: Framework `>=6.0,<7.0` + Target `>=6.2` → **intersection**: `>=6.2,<7.0`

### Constraints and Considerations

**Multi-Format Support**:
- **PEP 621**: `[project]` table (used by framework)
- **Poetry**: `[tool.poetry]` table
- **Setuptools**: `[build-system]` with dynamic deps

**Version Intersection Logic**:
```python
from packaging.specifiers import SpecifierSet

# Example 1: Compatible versions
framework_spec = SpecifierSet(">=6.0,<7.0")
target_spec = SpecifierSet(">=6.2")
intersection = framework_spec & target_spec  # >=6.2,<7.0

# Example 2: Incompatible versions
framework_spec = SpecifierSet(">=6.0")
target_spec = SpecifierSet("~=5.4")  # 5.4 <= version < 6.0
intersection = framework_spec & target_spec  # Empty set → error
```

**Claude API Key Validation** (non-fatal):
- Check for `ANTHROPIC_API_KEY` in environment
- Warn if missing, but don't block installation
- User may configure later

**Python 3.10 Compatibility**:
- Use `tomli` for reading TOML (stdlib `tomllib` only in 3.11+)
- Use `tomli_w` for writing TOML (no stdlib writer)

### Edge Cases to Handle

1. **No target TOML**: Use framework TOML directly
2. **Target TOML empty**: Use framework TOML directly
3. **No dependency conflicts**: Merge all deps
4. **Version conflict**: Compute intersection, fail if empty
5. **Poetry format target**: Convert Poetry deps to PEP 621
6. **Setuptools format target**: Convert to PEP 621
7. **Dev dependencies**: Merge separately from production deps
8. **Missing sections**: Handle missing `[project]`, `[dependency-groups]`
9. **Extra keys**: Preserve target's extra keys (authors, urls, etc.)
10. **UV validation fails**: Report validation error with troubleshooting
11. **Claude API key missing**: Warn but continue

### Documentation References

- [PEP 621 - Python Project Metadata](https://peps.python.org/pep-0621/)
- [Poetry pyproject.toml format](https://python-poetry.org/docs/pyproject/)
- [packaging.specifiers documentation](https://packaging.pypa.io/en/stable/specifiers.html)
- [tomli - TOML reader for Python 3.10+](https://github.com/hukkin/tomli)
- [tomli_w - TOML writer](https://github.com/hukkin/tomli_w)

## 3. Implementation Steps

### Phase 1: Setup and Dependencies (30 min)

**Step 1.1**: Add dependencies to framework pyproject.toml

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv add packaging tomli tomli-w
```

Expected dependencies:
```toml
dependencies = [
    "anthropic>=0.40.0",
    "deepdiff>=6.0",
    "diagrams>=0.24.4",
    "jsonschema>=4.25.1",
    "packaging>=24.0",  # NEW
    "python-frontmatter>=1.1.0",
    "pyyaml>=6.0",
    "tomli>=2.0.1",     # NEW
    "tomli-w>=1.0.0",   # NEW
]
```

**Step 1.2**: Create toml_merger.py module

```bash
touch /Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/toml_merger.py
```

### Phase 2: Core Implementation (3 hours)

**Step 2.1**: Implement TomlMerger with Strategy Pattern

**Architecture Decision**: Use strategy pattern to keep classes under 100-line limit (CLAUDE.md compliance)

**Files to Create**:
- `tools/ce/toml_merger.py` - Core orchestration (~60 lines)
- `tools/ce/toml_formats/pep621_handler.py` - PEP 621 format (~35 lines)
- `tools/ce/toml_formats/poetry_handler.py` - Poetry format (~45 lines)
- `tools/ce/toml_formats/setuptools_handler.py` - Setuptools format (~35 lines)
- `tools/ce/toml_formats/version_resolver.py` - Version intersection (~45 lines)

Create `/Users/bprzybyszi/nc-src/ctx-eng-plus/tools/ce/toml_merger.py`:

```python
#!/usr/bin/env python3
"""
TOML Merger - Intelligent pyproject.toml merging with version unification

Uses strategy pattern to handle multi-format TOML files.
"""

import os
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import tomllib  # Python 3.11+
except ImportError:
    import tomli as tomllib  # Fallback for Python 3.10

import tomli_w
from .toml_formats.pep621_handler import PEP621Handler
from .toml_formats.poetry_handler import PoetryHandler
from .toml_formats.setuptools_handler import SetuptoolsHandler
from .toml_formats.version_resolver import VersionResolver


class TomlMerger:
    """
    Orchestrates TOML merging using format-specific handlers.

    Delegates to strategy classes:
    - PEP621Handler: PEP 621 format
    - PoetryHandler: Poetry format
    - SetuptoolsHandler: Setuptools format
    - VersionResolver: Version intersection logic
    """

    def __init__(self, framework_toml: Path, target_toml: Optional[Path] = None):
        self.framework_toml = Path(framework_toml)
        self.target_toml = Path(target_toml) if target_toml else None

        # Load TOMLs
        with open(self.framework_toml, "rb") as f:
            self.framework_data = tomllib.load(f)

        self.target_data = None
        if self.target_toml and self.target_toml.exists():
            with open(self.target_toml, "rb") as f:
                self.target_data = tomllib.load(f)

    def merge(self) -> Dict:
        """
        Merge framework and target TOMLs.

        Returns:
            Merged TOML data (dict)

        Raises:
            ValueError: If version conflict detected
        """
        # No target TOML → use framework directly
        if not self.target_data:
            return self.framework_data.copy()

        # Detect target format
        target_format = self._detect_format(self.target_data)

        # Convert target to PEP 621 if needed
        if target_format == "poetry":
            target_pep621 = self._convert_poetry_to_pep621(self.target_data)
        elif target_format == "setuptools":
            target_pep621 = self._convert_setuptools_to_pep621(self.target_data)
        else:
            target_pep621 = self.target_data.copy()

        # Merge dependencies
        merged = self.framework_data.copy()

        # Merge [project] dependencies
        if "project" in target_pep621 and "dependencies" in target_pep621["project"]:
            merged["project"]["dependencies"] = self._merge_dependencies(
                self.framework_data["project"].get("dependencies", []),
                target_pep621["project"]["dependencies"]
            )

        # Merge [dependency-groups] dev dependencies
        if "dependency-groups" in target_pep621:
            if "dependency-groups" not in merged:
                merged["dependency-groups"] = {}

            for group, deps in target_pep621["dependency-groups"].items():
                framework_deps = merged["dependency-groups"].get(group, [])
                merged["dependency-groups"][group] = self._merge_dependencies(
                    framework_deps, deps
                )

        # Preserve target's extra metadata
        for key in ["authors", "maintainers", "urls", "license", "keywords", "classifiers"]:
            if "project" in target_pep621 and key in target_pep621["project"]:
                if key not in merged["project"]:
                    merged["project"][key] = target_pep621["project"][key]

        return merged

    def _detect_format(self, toml_data: Dict) -> str:
        """
        Detect TOML format (PEP 621, Poetry, or Setuptools).

        Args:
            toml_data: Parsed TOML data

        Returns:
            Format string: "pep621", "poetry", or "setuptools"
        """
        if "tool" in toml_data and "poetry" in toml_data["tool"]:
            return "poetry"
        elif "project" in toml_data:
            return "pep621"
        else:
            return "setuptools"

    def _convert_poetry_to_pep621(self, poetry_data: Dict) -> Dict:
        """
        Convert Poetry format to PEP 621 format.

        Args:
            poetry_data: Poetry-formatted TOML data

        Returns:
            PEP 621-formatted TOML data
        """
        pep621 = {"project": {}, "dependency-groups": {}}
        poetry = poetry_data["tool"]["poetry"]

        # Convert basic metadata
        pep621["project"]["name"] = poetry.get("name", "")
        pep621["project"]["version"] = poetry.get("version", "0.1.0")
        pep621["project"]["description"] = poetry.get("description", "")

        # Convert dependencies (Poetry uses dict format)
        if "dependencies" in poetry:
            pep621["project"]["dependencies"] = []
            for pkg, version in poetry["dependencies"].items():
                if pkg == "python":
                    pep621["project"]["requires-python"] = version
                else:
                    # Convert Poetry version syntax to PEP 440
                    pep621["project"]["dependencies"].append(
                        self._poetry_dep_to_pep621(pkg, version)
                    )

        # Convert dev-dependencies
        if "dev-dependencies" in poetry:
            pep621["dependency-groups"]["dev"] = [
                self._poetry_dep_to_pep621(pkg, version)
                for pkg, version in poetry["dev-dependencies"].items()
            ]

        return pep621

    def _poetry_dep_to_pep621(self, package: str, version) -> str:
        """
        Convert Poetry dependency to PEP 621 format.

        Args:
            package: Package name
            version: Poetry version specifier (string or dict)

        Returns:
            PEP 621 dependency string
        """
        if isinstance(version, dict):
            # Complex Poetry dep (e.g., {version = "^1.0", extras = ["dev"]})
            version_str = version.get("version", "")
        else:
            version_str = str(version)

        # Convert Poetry caret (^) to PEP 440
        # ^1.2.3 → >=1.2.3,<2.0.0
        if version_str.startswith("^"):
            major = version_str[1:].split(".")[0]
            version_str = f">={version_str[1:]},<{int(major)+1}.0.0"

        # Convert Poetry tilde (~) to PEP 440
        # ~1.2.3 → >=1.2.3,<1.3.0
        elif version_str.startswith("~"):
            parts = version_str[1:].split(".")
            if len(parts) >= 2:
                version_str = f">={version_str[1:]},<{parts[0]}.{int(parts[1])+1}.0"

        return f"{package}{version_str}" if version_str else package

    def _convert_setuptools_to_pep621(self, setuptools_data: Dict) -> Dict:
        """
        Convert Setuptools format to PEP 621 format.

        Args:
            setuptools_data: Setuptools-formatted TOML data

        Returns:
            PEP 621-formatted TOML data
        """
        # Basic conversion - Setuptools typically has minimal pyproject.toml
        pep621 = {"project": {}}

        # Copy build-system if present
        if "build-system" in setuptools_data:
            pep621["build-system"] = setuptools_data["build-system"]

        return pep621

    def _merge_dependencies(self, framework_deps: List[str], target_deps: List[str]) -> List[str]:
        """
        Merge two dependency lists with version intersection.

        Args:
            framework_deps: Framework dependencies (list of "package>=version" strings)
            target_deps: Target project dependencies

        Returns:
            Merged dependency list with unified versions

        Raises:
            ValueError: If version conflict detected (no intersection)
        """
        # Parse dependencies into {package: specifiers} dicts
        framework_map = self._parse_dependencies(framework_deps)
        target_map = self._parse_dependencies(target_deps)

        # Merge
        merged_map = {}
        all_packages = set(framework_map.keys()) | set(target_map.keys())

        for package in all_packages:
            framework_spec = framework_map.get(package)
            target_spec = target_map.get(package)

            if framework_spec and target_spec:
                # Compute intersection
                try:
                    intersection = framework_spec & target_spec
                    if not intersection:
                        raise ValueError(
                            f"❌ Dependency conflict: {package}\n"
                            f"   Framework requires: {framework_spec}\n"
                            f"   Target requires: {target_spec}\n"
                            f"   No compatible version exists.\n"
                            f"🔧 Resolution:\n"
                            f"   1. Update target project to use compatible version\n"
                            f"   2. Or update framework dependencies in tools/pyproject.toml"
                        )
                    merged_map[package] = intersection
                except InvalidSpecifier as e:
                    raise ValueError(
                        f"❌ Invalid version specifier for {package}: {e}\n"
                        f"🔧 Check dependency syntax in pyproject.toml"
                    )
            elif framework_spec:
                merged_map[package] = framework_spec
            else:
                merged_map[package] = target_spec

        # Convert back to list format
        return [
            f"{pkg}{spec}" if str(spec) else pkg
            for pkg, spec in sorted(merged_map.items())
        ]

    def _parse_dependencies(self, deps: List[str]) -> Dict[str, SpecifierSet]:
        """
        Parse dependency list into {package: SpecifierSet} dict.

        Args:
            deps: List of dependency strings (e.g., ["pyyaml>=6.0", "click"])

        Returns:
            Dict mapping package name to SpecifierSet
        """
        result = {}
        for dep in deps:
            # Split package name and version specifier
            # Examples: "pyyaml>=6.0", "click", "requests[security]>=2.0"

            # Handle extras (e.g., requests[security]>=2.0)
            if "[" in dep:
                pkg_with_extras, version = dep.split("[", 1)
                extras, version = version.split("]", 1)
                package = pkg_with_extras
                # Note: We ignore extras for version intersection
            else:
                # Find where version spec starts
                for i, char in enumerate(dep):
                    if char in "<>=!~":
                        package = dep[:i]
                        version = dep[i:]
                        break
                else:
                    # No version spec
                    package = dep
                    version = ""

            # Create SpecifierSet
            try:
                spec = SpecifierSet(version) if version else SpecifierSet()
                result[package.strip()] = spec
            except InvalidSpecifier:
                # Skip invalid specifiers
                continue

        return result

    def write(self, output_path: Path):
        """
        Write merged TOML to file.

        Args:
            output_path: Path to write merged pyproject.toml
        """
        merged = self.merge()

        with open(output_path, "wb") as f:
            tomli_w.dump(merged, f)

    def validate_claude_api_key(self) -> Tuple[bool, str]:
        """
        Validate Claude API key (non-fatal).

        Returns:
            Tuple of (is_valid, message)
        """
        api_key = os.getenv("ANTHROPIC_API_KEY")

        if not api_key:
            return (False,
                "⚠️  ANTHROPIC_API_KEY not set\n"
                "🔧 To use Claude-powered features, set:\n"
                "   export ANTHROPIC_API_KEY=sk-ant-...\n"
                "   (Installation will continue without this)"
            )

        return (True, "✓ ANTHROPIC_API_KEY configured")
```

**IMPORTANT - Strategy Pattern Refactoring Required**:

The above implementation is **245 lines** which violates CLAUDE.md's **100-line class limit**.

**Refactoring Strategy** (to be applied during implementation):

Split TomlMerger into 5 smaller classes:

1. **TomlMerger** (core orchestration, ~60 lines):
   - `__init__()`, `merge()`, `write()`, `validate_claude_api_key()`
   - Delegates to format handlers and version resolver

2. **PEP621Handler** (`tools/ce/toml_formats/pep621_handler.py`, ~35 lines):
   - `parse(toml_data)` - Parse PEP 621 format
   - `write(data)` - Write PEP 621 format
   - No conversion needed (native format)

3. **PoetryHandler** (`tools/ce/toml_formats/poetry_handler.py`, ~45 lines):
   - `parse(toml_data)` - Parse Poetry format
   - `convert_to_pep621(poetry_data)` - Convert to PEP 621
   - `_convert_dependency(pkg, version)` - Poetry syntax conversion (^, ~)

4. **SetuptoolsHandler** (`tools/ce/toml_formats/setuptools_handler.py`, ~35 lines):
   - `parse(toml_data)` - Parse Setuptools format
   - `convert_to_pep621(setuptools_data)` - Convert to PEP 621

5. **VersionResolver** (`tools/ce/toml_formats/version_resolver.py`, ~45 lines):
   - `merge_dependencies(framework_deps, target_deps)` - Version intersection
   - `_parse_dependencies(deps)` - Parse dep strings to SpecifierSet
   - Uses `packaging.specifiers.SpecifierSet` for intersection

**Refactored TomlMerger.merge() method**:
```python
def merge(self) -> Dict:
    if not self.target_data:
        return self.framework_data.copy()

    # Detect format and get handler
    if "tool" in self.target_data and "poetry" in self.target_data["tool"]:
        handler = PoetryHandler()
        target_pep621 = handler.convert_to_pep621(self.target_data)
    elif "project" in self.target_data:
        handler = PEP621Handler()
        target_pep621 = handler.parse(self.target_data)
    else:
        handler = SetuptoolsHandler()
        target_pep621 = handler.convert_to_pep621(self.target_data)

    # Merge dependencies using resolver
    resolver = VersionResolver()
    merged = self.framework_data.copy()

    if "project" in target_pep621 and "dependencies" in target_pep621["project"]:
        merged["project"]["dependencies"] = resolver.merge_dependencies(
            self.framework_data["project"].get("dependencies", []),
            target_pep621["project"]["dependencies"]
        )

    # Preserve metadata
    # ... (metadata preservation logic)

    return merged
```

**Benefits**:
- ✓ Each class under 100 lines (CLAUDE.md compliant)
- ✓ Single responsibility per class
- ✓ Easy to test format handlers independently
- ✓ Easy to add new formats (e.g., Flit, PDM)
- ✓ Clearer separation of concerns

**Implementation Note**: The monolithic code above shows the logic flow. During implementation, refactor into the 5-class structure shown here.

**Step 2.2**: Integrate with init_project.py

Modify `tools/ce/init_project.py` to use TomlMerger during extract phase:

```python
# Add import at top
from .toml_merger import TomlMerger

# In extract() method, after unpacking infrastructure.xml:
def extract(self) -> Dict:
    # ... existing extraction logic ...

    # Step 4: Merge pyproject.toml
    framework_toml = self.ce_dir / "tools" / "pyproject.toml"
    target_toml = self.target_project / "pyproject.toml"

    if framework_toml.exists():
        try:
            merger = TomlMerger(framework_toml, target_toml)

            # Validate Claude API key (non-fatal warning)
            is_valid, msg = merger.validate_claude_api_key()
            if not is_valid:
                print(msg)

            # Merge TOMLs
            merger.write(target_toml)
            status["message"] += f"\n✓ Merged pyproject.toml ({len(merger.merge()['project']['dependencies'])} dependencies)"

        except ValueError as e:
            # Version conflict
            status["message"] = str(e)
            return status
        except Exception as e:
            status["message"] = f"❌ TOML merge failed: {e}\n🔧 Check pyproject.toml syntax"
            return status

    # ... rest of extraction ...
```

### Phase 3: Testing and Validation (1 hour)

**Step 3.1**: Create test cases

Test file: `tools/tests/test_toml_merger.py`

```python
#!/usr/bin/env python3
"""Tests for TOML merger."""

import pytest
from pathlib import Path
from ce.toml_merger import TomlMerger


def test_no_target_toml(tmp_path):
    """Test merge with no target TOML."""
    framework_toml = tmp_path / "framework.toml"
    framework_toml.write_text("""
[project]
name = "ce-tools"
dependencies = ["pyyaml>=6.0"]
""")

    merger = TomlMerger(framework_toml)
    result = merger.merge()

    assert result["project"]["name"] == "ce-tools"
    assert "pyyaml>=6.0" in result["project"]["dependencies"]


def test_version_intersection_compatible(tmp_path):
    """Test version intersection with compatible versions."""
    framework_toml = tmp_path / "framework.toml"
    framework_toml.write_text("""
[project]
dependencies = ["pyyaml>=6.0,<7.0"]
""")

    target_toml = tmp_path / "target.toml"
    target_toml.write_text("""
[project]
dependencies = ["pyyaml>=6.2"]
""")

    merger = TomlMerger(framework_toml, target_toml)
    result = merger.merge()

    # Intersection: >=6.2,<7.0
    deps = result["project"]["dependencies"]
    assert any("pyyaml" in d for d in deps)


def test_version_intersection_incompatible(tmp_path):
    """Test version intersection with incompatible versions."""
    framework_toml = tmp_path / "framework.toml"
    framework_toml.write_text("""
[project]
dependencies = ["pyyaml>=6.0"]
""")

    target_toml = tmp_path / "target.toml"
    target_toml.write_text("""
[project]
dependencies = ["pyyaml~=5.4"]
""")

    merger = TomlMerger(framework_toml, target_toml)

    with pytest.raises(ValueError, match="Dependency conflict"):
        merger.merge()


def test_poetry_format_conversion(tmp_path):
    """Test Poetry format conversion."""
    framework_toml = tmp_path / "framework.toml"
    framework_toml.write_text("""
[project]
dependencies = ["click>=8.0"]
""")

    target_toml = tmp_path / "target.toml"
    target_toml.write_text("""
[tool.poetry]
name = "my-project"
version = "1.0.0"

[tool.poetry.dependencies]
python = "^3.10"
click = "^7.0"
""")

    merger = TomlMerger(framework_toml, target_toml)
    result = merger.merge()

    # Should compute intersection of click versions
    assert "project" in result
    assert "dependencies" in result["project"]
```

**Step 3.2**: Run tests

```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_toml_merger.py -v
```

Expected output:
```
tests/test_toml_merger.py::test_no_target_toml PASSED
tests/test_toml_merger.py::test_version_intersection_compatible PASSED
tests/test_toml_merger.py::test_version_intersection_incompatible PASSED
tests/test_toml_merger.py::test_poetry_format_conversion PASSED
```

### Phase 4: Integration Testing (1 hour)

**Step 4.1**: Test E2E with init-project

```bash
# Create test target project
cd /tmp
mkdir test-target-project
cd test-target-project
git init

# Create target pyproject.toml with conflicting deps
cat > pyproject.toml << 'EOF'
[project]
name = "test-project"
version = "0.1.0"
dependencies = [
    "pyyaml>=6.0",  # Compatible
    "click>=7.0",   # Compatible
]
EOF

# Run init-project
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
uv run ce init-project /tmp/test-target-project
```

**Step 4.2**: Verify merged TOML

```bash
cat /tmp/test-target-project/pyproject.toml
```

Expected output:
- All framework dependencies present
- Target dependencies merged with version intersection
- No duplicates

**Step 4.3**: UV validation

```bash
cd /tmp/test-target-project/.ce/tools
uv sync
uv run ce --help
```

Expected: UV sync succeeds, ce command works.

## 4. Validation Gates

### Gate 1: Unit Tests Pass

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_toml_merger.py -v
```

**Expected**: All 4+ tests pass

**Critical**:
- ✓ No target TOML handled
- ✓ Version intersection works (compatible versions)
- ✓ Version conflict detected (incompatible versions)
- ✓ Poetry format conversion works

### Gate 2: Multi-Format Support Verified

**Test**: Create sample TOMLs in all 3 formats and verify conversion

**Command**:
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "
from ce.toml_merger import TomlMerger
from pathlib import Path

# Test PEP 621 detection
print('Testing format detection...')
# (Manual verification with sample files)
"
```

**Expected**: All 3 formats detected and handled correctly

### Gate 3: Python 3.10 Compatibility

**Command**:
```bash
python3.10 -c "from ce.toml_merger import TomlMerger; print('✓ Python 3.10 compatible')"
```

**Expected**: No ImportError for tomllib/tomli

### Gate 4: Claude API Key Validation (Non-Fatal)

**Test 1**: With API key set
```bash
export ANTHROPIC_API_KEY=sk-ant-test
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.toml_merger import TomlMerger; merger = TomlMerger(Path('pyproject.toml')); print(merger.validate_claude_api_key())"
```

**Expected**: `(True, '✓ ANTHROPIC_API_KEY configured')`

**Test 2**: Without API key
```bash
unset ANTHROPIC_API_KEY
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.toml_merger import TomlMerger; merger = TomlMerger(Path('pyproject.toml')); print(merger.validate_claude_api_key())"
```

**Expected**: `(False, '⚠️  ANTHROPIC_API_KEY not set...')` with warning message

### Gate 5: E2E Integration Test

**Command**:
```bash
# Clean test
rm -rf /tmp/test-target-toml-merge
mkdir -p /tmp/test-target-toml-merge
cd /tmp/test-target-toml-merge
git init

# Create conflicting pyproject.toml
cat > pyproject.toml << 'EOF'
[project]
name = "test-app"
version = "1.0.0"
dependencies = ["pyyaml>=6.0", "click>=8.0"]
EOF

# Run init
cd /Users/bprzybyszi/nc-src/ctx-eng-plus
uv run ce init-project /tmp/test-target-toml-merge

# Verify merge
cd /tmp/test-target-toml-merge/.ce/tools
uv sync
uv run ce --help
```

**Expected**:
- ✓ pyproject.toml merged (no overwrites)
- ✓ UV sync succeeds
- ✓ ce command works
- ✓ All framework + target deps installed

### Gate 6: Edge Case Coverage

Test all 11 edge cases:

1. ✓ No target TOML
2. ✓ Target TOML empty
3. ✓ No dependency conflicts
4. ✓ Version conflict (incompatible)
5. ✓ Poetry format target
6. ✓ Setuptools format target
7. ✓ Dev dependencies merged
8. ✓ Missing [project] section
9. ✓ Extra metadata preserved
10. ✓ UV validation fails (error reported)
11. ✓ Claude API key missing (warning only)

## 5. Testing Strategy

### Test Framework
pytest

### Test Command
```bash
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_toml_merger.py -v
```

### Test Coverage

**Unit Tests** (tools/tests/test_toml_merger.py):
- Format detection (PEP 621, Poetry, Setuptools)
- Version intersection (compatible, incompatible, no spec)
- Poetry dependency conversion (^, ~, dict format)
- Dependency parsing (with/without extras)
- TOML writing

**Integration Tests**:
- init_project.py integration
- UV validation after merge
- Real-world Poetry project merge
- Real-world Setuptools project merge

### Test Data

Create `tools/tests/fixtures/toml/` with sample TOMLs:
- `framework.toml` - Framework pyproject.toml
- `target-pep621.toml` - PEP 621 target
- `target-poetry.toml` - Poetry target
- `target-setuptools.toml` - Setuptools target
- `target-conflict.toml` - Conflicting versions

## 6. Rollout Plan

### Phase 1: Development (2 hours)

1. ✓ Add dependencies (packaging, tomli, tomli-w)
2. ✓ Implement TomlMerger class (245 lines)
3. ✓ Add unit tests (50 lines)
4. ✓ Verify Python 3.10 compatibility

### Phase 2: Integration (1 hour)

1. ✓ Integrate with init_project.py extract phase
2. ✓ Add error handling and validation
3. ✓ Test E2E with real target projects
4. ✓ Verify UV sync succeeds after merge

### Phase 3: Validation (1 hour)

1. ✓ Run all 6 validation gates
2. ✓ Test all 11 edge cases
3. ✓ Verify conflict resolution logic
4. ✓ Test on 3 target formats (PEP 621, Poetry, Setuptools)

### Phase 4: Documentation (Included)

1. ✓ Update PRP with implementation details
2. ✓ Add inline code comments
3. ✓ Document version intersection strategy
4. ✓ Add troubleshooting guide for common errors

---

## Conflict Analysis

### File Conflicts with Other PRPs: NONE

**Files Created by This PRP**:
- `tools/ce/toml_merger.py` (new file, no conflicts)

**Files Modified by This PRP**:
- `tools/ce/init_project.py` (extract phase only)
- `tools/pyproject.toml` (dependencies only)

**Other PRPs in Stage 2**:
- PRP-37.2.1: Modifies blend logic (no overlap with extract)
- PRP-37.2.3: Modifies settings.local.json (no overlap)

### Dependency Conflict Risk: HIGH

**Risk**: Target project has incompatible dependency versions

**Mitigation**:
1. Version intersection strategy (not "higher wins")
2. Fail fast with actionable error messages
3. UV validation after merge
4. User can resolve by updating target or framework deps

**Example Error**:
```
❌ Dependency conflict: pyyaml
   Framework requires: >=6.0
   Target requires: ~=5.4
   No compatible version exists.
🔧 Resolution:
   1. Update target project to use compatible version
   2. Or update framework dependencies in tools/pyproject.toml
```

### Merge Order: 4 (After PRP-37.2.1 and PRP-37.2.3)

**Rationale**: TOML merger must be available before blend phase (PRP-37.2.1) runs

**Sequential Dependencies**:
1. PRP-37.1.1 (extract) → Sets up .ce/ structure
2. PRP-37.2.2 (this) → Merges pyproject.toml
3. PRP-37.2.1 (blend) → Uses merged TOML for initialization
4. PRP-37.2.3 (settings) → Blends settings.local.json

---

## Success Criteria

1. ✓ TomlMerger supports PEP 621, Poetry, Setuptools formats
2. ✓ Version intersection works correctly (SpecifierSet)
3. ✓ Python 3.10 compatible (tomli fallback)
4. ✓ Claude API key validation non-fatal
5. ✓ All 11 edge cases handled
6. ✓ UV validation passes after merge
7. ✓ init-project phase succeeds with merged dependencies
8. ✓ No silent failures or data loss
9. ✓ Actionable error messages for conflicts
10. ✓ Tests pass (unit + integration)
