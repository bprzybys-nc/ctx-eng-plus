# Context Engineering Framework - Initialization Guide

**Version**: CE 1.1
**Updated**: 2025-11-04
**Audience**: Teams installing CE framework for the first time or upgrading

---

## Quick Start (5 Steps)

### Step 1: Unpack Framework (2 minutes)

```bash
# If you received ce-workflow-docs.xml
repomix --unpack ce-workflow-docs.xml --target ./

# Creates:
# - .ce/                 # Framework components
# - .serena/memories/    # Knowledge base
# - .claude/commands/    # Automation commands
# - examples/            # Documentation and patterns
# - CLAUDE.md            # Project guide
```

### Step 2: Initialize Serena (1 minute)

```bash
# Activate Serena MCP with project root (full absolute path required)
serena_activate("/absolute/path/to/your/project")

# Verify memories loaded
serena_list_memories()
# Expected: 23 memories (6 critical, 17 regular)
```

### Step 3: Configure Settings (1 minute)

```bash
# Settings already unpacked to .claude/settings.local.json
# Verify configuration
cat .claude/settings.local.json | jq '.bash.permissions.allow | length'
# Expected: ~80 auto-allowed command patterns

# If merging with existing settings, see: Migration Scenarios below
```

### Step 4: Verify PRP-0 Created (Auto)

```bash
# Check bootstrap documentation
cat PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# This file documents:
# - What framework components were installed
# - Why this framework was chosen
# - How to use the framework
# - Framework version and timestamp
```

### Step 5: Validate Installation (1 minute)

```bash
cd tools
uv sync
uv run ce validate --level 4

# Expected output:
# ✓ All validation gates passed
# ✓ Context drift: <5%
# ✓ Framework initialized successfully
```

**Total time**: ~6 minutes for complete initialization

---

## What You Get

### Documentation (25+ files, ~14k lines)

**examples/**:
- Workflow patterns (batch operations, cleanup, drift remediation)
- Integration guides (Linear, Serena, Syntropy MCP)
- Configuration templates
- Pattern library
- Reference materials

**CLAUDE.md** (470 lines):
- Project guide and framework principles
- Tool selection philosophy
- Testing and code quality standards
- Command reference
- Git worktree documentation

**.ce/RULES.md** (300 lines):
- Framework rules and governance
- Validation levels and gates
- PRP structure standards

### Automation (7 commands)

**/.claude/commands/**:
- `/generate-prp` - Create PRPs from INITIAL.md
- `/execute-prp` - Execute PRP with git integration
- `/peer-review` - Validate code quality
- `/batch-gen-prp` - Parallel PRP generation
- `/batch-exe-prp` - Parallel PRP execution
- `/vacuum` - Clean temporary files
- `/update-context` - Sync PRPs with codebase

### Knowledge Base (23 memories)

**Serena memories** (.serena/memories/):

**Critical Memories** (🔒 6 files, never removed):
- code-style-conventions.md
- testing-standards.md
- tool-usage-syntropy.md
- tool-config-optimization-completed.md
- task-completion-checklist.md
- use-syntropy-tools-not-bash.md

**Regular Memories** (📝 17 files, project lifetime):
- Codebase structure
- Validation usage patterns
- Linear integration examples
- Serena implementation patterns
- System architecture specifications

**Memory Type System**:
- **critical** (🔒): Forever, admin override only
- **regular** (📝): Project lifetime, user deletable
- **feat** (🧪): PRP-scoped, auto-removed after PRP execution

---

## Repomix Usage

### Packaging CE Documentation (For Framework Maintainers)

```bash
# From ctx-eng-plus project root
repomix \
  --include "examples/**/*.md" \
  --include ".serena/memories/*.md" \
  --include "CLAUDE.md" \
  --include ".ce/RULES.md" \
  --style xml \
  --output .ce/ce-workflow-docs.xml \
  --header-text "Context Engineering Framework Distribution Package v1.1"

# Output: .ce/ce-workflow-docs.xml (~50KB, 8,000 tokens)
```

### Unpacking to Target Project (For Users)

```bash
# Scenario 1: Greenfield project
cd /path/to/new/project
repomix --unpack /path/to/ce-workflow-docs.xml --target ./

# Scenario 2: Mature project (preserves existing files)
cd /path/to/existing/project
repomix --unpack /path/to/ce-workflow-docs.xml --target ./ --merge

# Scenario 3: Upgrade existing CE installation
cd /path/to/ce/project
repomix --unpack /path/to/ce-workflow-docs.xml --target ./ --upgrade
```

**Repomix Options**:
- `--target`: Destination directory
- `--merge`: Merge with existing files (uses conflict resolution rules)
- `--upgrade`: Upgrade mode (creates backup, validates)
- `--dry-run`: Preview changes without applying

---

## Memory Type System

### Type Classifications

| Type | Lifecycle | Removal | Examples |
|------|-----------|---------|----------|
| **critical** (🔒) | Forever | Never (admin override only) | Architecture decisions, security patterns, core principles |
| **regular** (📝) | Project lifetime | Manual delete allowed | Testing standards, tool guides, coding conventions |
| **feat** (🧪) | PRP-scoped | Auto-remove after PRP | Optimization notes, experimental approaches, session insights |

### Memory Format

Each memory file includes YAML front matter:

```yaml
---
type: critical|regular|feat
priority: high|normal|low
category: architecture|pattern|guide|reference|troubleshooting
tags: [tag1, tag2, tag3]
prp_id: "PRP-X" OR null
expires: null|"2025-12-31"|"post-prp"|"session-clear"
related: ["memory-id-1", "memory-id-2"]
created: "2025-11-04T18:00:00Z"
updated: "2025-11-04T18:30:00Z"
---

# Memory Content Here
```

### Memory Lifecycle

**Critical Memories**:
- Created during framework initialization
- Never automatically removed
- Require admin override to delete
- Examples: code-style-conventions, testing-standards, use-syntropy-tools-not-bash

**Regular Memories**:
- Created by users during project work
- Persist for project lifetime
- User can delete manually
- Examples: Project-specific patterns, tool configurations, integration guides

**Feature Memories**:
- Created during PRP execution
- Automatically removed after PRP completion
- Used for temporary insights and experimental approaches
- Examples: PRP-specific optimization notes, session debugging insights

### Memory Management Commands

```bash
# List all memories with types
serena_list_memories()

# Create new memory
serena_write_memory(
  id="my-pattern",
  content="...",
  type="regular"
)

# Cleanup feature memories after PRP
serena-cleanup-memories --prp PRP-32 --type feat

# Classify existing memories (migration)
serena-classify-memories --default-type regular
```

---

## PRP-0 Bootstrap Pattern

### What is PRP-0?

**PRP-0** is a special bootstrap documentation file created during framework initialization. It documents:
1. What was copied from CE framework
2. Why this framework was chosen
3. How to use the framework
4. Framework version and installation date

**Location**: `PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md`

### PRP-0 Structure

```markdown
---
issue: LINEAR-INIT
prp_id: PRP-0
phase: bootstrap
status: executed
executed_at: 2025-11-04T18:00:00Z
target_project: my-project
ce_version: CE 1.1
---

# PRP-0: Context Engineering Framework Initialization

## Objective
Bootstrap new project with Context Engineering workflow framework.

## What Was Copied
[Complete inventory of installed components]

## Why This Framework?
[Rationale for CE framework adoption]

## How to Use This Framework
[Quick start guide and next steps]

## Maintenance
[Update process and version tracking]

## Acceptance Criteria
[Validation checklist]
```

### Template Variables

PRP-0 is generated from a template with variables:
- `{TIMESTAMP}`: Installation date (ISO 8601 format)
- `{TARGET_PROJECT}`: Project name
- `{CE_VERSION}`: Framework version (e.g., "CE 1.1")

**Template location**: `examples/templates/PRP-0-CONTEXT-ENGINEERING.md`

### Benefits

1. **Transparency**: Clear record of what was installed
2. **Maintenance**: Version tracking for future upgrades
3. **Onboarding**: New team members understand project genesis
4. **Audit Trail**: Why these docs are in the project
5. **Updates**: Clear process for framework upgrades

---

## Validation Checklist

### Post-Installation Validation

Run these checks after installing CE framework:

#### 1. Framework Files Present

```bash
# Check essential framework files
test -f .ce/RULES.md && echo "✓ Rules present"
test -f CLAUDE.md && echo "✓ Project guide present"
test -d .claude/commands && echo "✓ Commands installed"
test -d .serena/memories && echo "✓ Memories initialized"
test -d examples && echo "✓ Examples present"
test -f PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ PRP-0 created"
```

#### 2. Settings Valid

```bash
# Validate settings JSON
jq empty .claude/settings.local.json && echo "✓ Settings valid"

# Check permission counts
echo "Auto-allowed commands: $(jq '.bash.permissions.allow | length' .claude/settings.local.json)"
echo "Ask-first commands: $(jq '.bash.permissions.ask | length' .claude/settings.local.json)"

# Expected: ~80 allow patterns, ~15 ask patterns
```

#### 3. Commands Executable

```bash
# List available commands
ls -1 .claude/commands/*.md | wc -l
# Expected: ≥7 commands

# Verify key commands present
test -f .claude/commands/generate-prp.md && echo "✓ generate-prp"
test -f .claude/commands/execute-prp.md && echo "✓ execute-prp"
test -f .claude/commands/batch-gen-prp.md && echo "✓ batch-gen-prp"
test -f .claude/commands/vacuum.md && echo "✓ vacuum"
```

#### 4. Memories Have Type Headers

```bash
# Check memories for type classification
grep -L "^type:" .serena/memories/*.md || echo "✓ All memories typed"

# Count by type
echo "Critical: $(grep -l "^type: critical" .serena/memories/*.md | wc -l)"
echo "Regular: $(grep -l "^type: regular" .serena/memories/*.md | wc -l)"
echo "Feature: $(grep -l "^type: feat" .serena/memories/*.md | wc -l)"

# Expected: 6 critical, 17+ regular, 0 feat (feat are temporary)
```

#### 5. Context Drift Check

```bash
cd tools
uv run ce analyze-context

# Expected output:
# Context drift: X.X% (should be <5% after fresh installation)
# Exit code: 0 (healthy), 1 (warning 5-15%), 2 (critical ≥15%)
```

#### 6. Validation Level 4

```bash
cd tools
uv run ce validate --level 4

# Runs comprehensive validation:
# Level 1: Structure (PRPs/, .serena/, .claude/)
# Level 2: Content (YAML headers, file format)
# Level 3: Integration (Linear, Serena, git)
# Level 4: Context (drift, memory consistency)
```

---

## Troubleshooting

### Issue: "Serena not found"

**Symptom**: `serena_list_memories()` returns error

**Solution**:
```bash
# Check Serena MCP connection
mcp status | grep serena

# Reconnect MCP servers
/mcp

# Verify Serena activated
serena_activate("/absolute/path/to/project")
```

### Issue: "Commands not available"

**Symptom**: `/generate-prp` not recognized

**Solution**:
```bash
# Check commands directory
ls -la .claude/commands/

# Restart Claude Code to reload commands
# Or manually load command:
cat .claude/commands/generate-prp.md
```

### Issue: "Settings conflict"

**Symptom**: `.claude/settings.local.json` already exists with custom settings

**Solution**:
```bash
# Backup existing settings
cp .claude/settings.local.json .claude/settings.local.json.backup

# Merge settings (manual)
# 1. Load framework settings from unpacked file
# 2. Load your custom settings from backup
# 3. Merge: framework defaults + your overrides
# 4. Write merged result

# Or use migration guide for existing installations:
# See: examples/workflows/migration-existing-ce.md
```

### Issue: "Memory authentication failed"

**Symptom**: Linear MCP shows "Not connected"

**Solution**:
```bash
# Clear authentication cache
rm -rf ~/.mcp-auth

# Reconnect Linear
/mcp

# Re-authenticate when prompted
```

### Issue: "Context drift high after installation"

**Symptom**: `ce analyze-context` shows >10% drift

**Cause**: PRPs or examples out of sync with installed framework

**Solution**:
```bash
# Update context to sync PRPs
cd tools
uv run ce update-context

# Re-check drift
uv run ce analyze-context

# Expected: <5% after sync
```

### Issue: "PRP-0 not created"

**Symptom**: No PRP-0 file in PRPs/executed/

**Solution**:
```bash
# Manually create PRP-0 from template
cp examples/templates/PRP-0-CONTEXT-ENGINEERING.md PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Fill in variables:
# - {TIMESTAMP}: $(date -u +%Y-%m-%dT%H:%M:%SZ)
# - {TARGET_PROJECT}: your-project-name
# - {CE_VERSION}: CE 1.1

# Validate PRP-0
grep -q "executed_at:" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ Valid"
```

### Issue: "Tool not found" for Syntropy MCP tools

**Symptom**: `mcp__syntropy__*` tools return errors

**Cause**: Syntropy MCP not enabled or tools denied

**Solution**:
```bash
# Check Syntropy MCP status
/syntropy-health

# Enable required tools
mcp__syntropy__enable_tools(
  enable=["serena_find_symbol", "context7_get_library_docs"]
)

# Sync settings with Syntropy state
/sync-with-syntropy

# Verify tools enabled
cat .claude/settings.local.json | jq '.mcp.syntropy.tools.deny'
```

### Issue: "Repomix unpack failed"

**Symptom**: `repomix --unpack` errors

**Cause**: Corrupt XML or permission issues

**Solution**:
```bash
# Verify XML is valid
xmllint --noout ce-workflow-docs.xml && echo "✓ Valid XML"

# Check file permissions
chmod +r ce-workflow-docs.xml

# Try unpack with verbose mode
repomix --unpack ce-workflow-docs.xml --target ./ --verbose

# If still failing, manual extraction:
# 1. Open XML in editor
# 2. Extract file contents from XML tags
# 3. Write to target locations manually
```

---

## Migration Scenarios

This initialization guide covers **greenfield installation** (new projects with no CE framework).

For other scenarios, see:

1. **Mature Project** (existing code, adding CE):
   - Guide: [examples/workflows/migration-mature-project.md](workflows/migration-mature-project.md)
   - Scenario: Adding CE to existing codebase without disrupting structure

2. **Existing CE** (legacy CE, upgrading):
   - Guide: [examples/workflows/migration-existing-ce.md](workflows/migration-existing-ce.md)
   - Scenario: Upgrading from legacy CE to modern CE 1.1 with conflict resolution

3. **Partial CE** (incomplete installation):
   - Guide: [examples/workflows/migration-partial-ce.md](workflows/migration-partial-ce.md)
   - Scenario: Completing partial CE installation, filling missing components

4. **Greenfield** (new project, no CE):
   - Guide: [examples/workflows/migration-greenfield.md](workflows/migration-greenfield.md)
   - Scenario: Clean installation (this Quick Start guide)

---

## Next Steps

### After Installation

1. **Review Framework** (15 minutes):
   - Read CLAUDE.md for project guide
   - Browse examples/INDEX.md for available patterns
   - Check .ce/RULES.md for validation rules

2. **Understand Examples** (10 minutes):
   - Review examples/linear-integration-example.md
   - Check examples/patterns/ for reusable patterns
   - Read examples/l4-validation-example.md

3. **Generate First PRP** (5 minutes):
   ```bash
   # Create feature request
   cat > feature-requests/my-feature/INITIAL.md << 'EOF'
   # Feature: My First Feature

   ## FEATURE
   [Description]

   ## EXAMPLES
   [Code examples]
   EOF

   # Generate PRP
   /generate-prp feature-requests/my-feature/INITIAL.md
   ```

4. **Validate PRP** (2 minutes):
   ```bash
   cd tools
   uv run ce validate --level 4
   ```

5. **Execute PRP** (10 minutes):
   ```bash
   /execute-prp PRPs/feature-requests/PRP-1-my-first-feature.md
   ```

### Ongoing Maintenance

**Weekly**:
- Run `ce analyze-context` to check drift (<5% is healthy)
- Review `.serena/memories/` for outdated patterns

**Monthly**:
- Update framework: `repomix --unpack ce-workflow-docs.xml --upgrade`
- Validate installation: `ce validate --level 4`

**Per PRP**:
- Cleanup feature memories: `serena-cleanup-memories --prp PRP-X --type feat`
- Validate changes: `ce validate --level 3`

---

## Framework Version

**Current**: CE 1.1 (Syntropy MCP 1.1 Release)
**Released**: 2025-11-04
**Source**: ctx-eng-plus project

**What's New in 1.1**:
- Memory type system (critical/regular/feat)
- Repomix-based distribution
- PRP-0 bootstrap pattern
- Four migration scenarios documented
- Conflict resolution rules for upgrades
- Enhanced validation (Level 4)
- Parallel PRP execution (batch mode)

**Upgrade Path**:
- From legacy CE → CE 1.1: See [migration-existing-ce.md](workflows/migration-existing-ce.md)
- Version tracking in PRP-0 YAML header

---

## Related Documentation

- **Migration Guides**: examples/workflows/
- **PRP-0 Template**: examples/templates/PRP-0-CONTEXT-ENGINEERING.md
- **Tool Usage Guide**: examples/TOOL-USAGE-GUIDE.md
- **Pattern Library**: examples/patterns/
- **Framework Rules**: .ce/RULES.md
- **Project Guide**: CLAUDE.md

---

**Questions or issues?** Check troubleshooting section above or consult migration guides for specific scenarios.
