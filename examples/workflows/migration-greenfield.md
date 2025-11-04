# Migration Guide: Greenfield Project

**Scenario**: New project with no existing Context Engineering installation
**Difficulty**: Easy
**Time**: ~10 minutes
**Risk**: Low (no conflicts)

---

## Overview

This guide covers installing the Context Engineering framework into a brand new project that has no existing CE components.

**You should use this guide if**:
- Starting a new project from scratch
- No `.ce/`, `.serena/`, `.claude/commands/`, or `PRPs/` directories
- No CLAUDE.md file
- Clean slate installation

**If your project has existing code**, see [migration-mature-project.md](migration-mature-project.md) instead.

---

## Prerequisites

**Required**:
- Repomix CLI installed (`npm install -g repomix`)
- CE framework distribution file (`ce-workflow-docs.xml`)
- Project directory created
- Git initialized (`git init`)

**Optional**:
- Linear account (for issue tracking)
- Syntropy MCP configured
- UV package manager (for CE CLI tools)

---

## Installation Steps

### Step 1: Verify Clean State (1 minute)

```bash
cd /path/to/your/new/project

# Verify no CE components exist
test ! -d .ce && echo "✓ No .ce/"
test ! -d .serena && echo "✓ No .serena/"
test ! -d .claude/commands && echo "✓ No commands/"
test ! -d PRPs && echo "✓ No PRPs/"
test ! -f CLAUDE.md && echo "✓ No CLAUDE.md"

# Expected: All checks pass (5 ✓)
```

**If any checks fail**, your project has existing components. Use [migration-partial-ce.md](migration-partial-ce.md) instead.

### Step 2: Unpack Framework (2 minutes)

```bash
# Unpack CE framework distribution
repomix --unpack /path/to/ce-workflow-docs.xml --target ./

# Verify unpacked structure
ls -d .ce .serena .claude examples CLAUDE.md PRPs

# Expected output:
# .ce
# .serena
# .claude
# examples
# CLAUDE.md
# PRPs
```

**What was created**:

```
your-project/
├── .ce/
│   ├── PRPs/
│   │   └── PRP-0-CONTEXT-ENGINEERING.md
│   ├── examples/
│   │   └── [25 framework example files]
│   └── RULES.md
├── .serena/
│   └── memories/
│       └── [23 memory files with YAML headers]
├── .claude/
│   ├── commands/
│   │   ├── generate-prp.md
│   │   ├── execute-prp.md
│   │   ├── batch-gen-prp.md
│   │   ├── batch-exe-prp.md
│   │   ├── vacuum.md
│   │   ├── update-context.md
│   │   └── sync-with-syntropy.md
│   └── settings.local.json
├── examples/
│   ├── INDEX.md
│   ├── INITIALIZATION.md
│   ├── TOOL-USAGE-GUIDE.md
│   ├── patterns/
│   │   └── [pattern files]
│   └── workflows/
│       └── [workflow guides]
├── PRPs/
│   ├── executed/
│   │   └── PRP-0-CONTEXT-ENGINEERING.md (symlink to .ce/PRPs/)
│   └── feature-requests/
├── tools/
│   ├── ce/
│   ├── tests/
│   ├── pyproject.toml
│   └── bootstrap.sh
└── CLAUDE.md
```

### Step 3: Initialize Tools (3 minutes)

```bash
# Install CE CLI tools
cd tools
./bootstrap.sh

# This will:
# 1. Install UV package manager (if not present)
# 2. Create virtual environment
# 3. Install dependencies from pyproject.toml
# 4. Run initial validation

# Verify tools installed
uv run ce --version
# Expected: ce version 1.1.0
```

### Step 4: Configure Linear (2 minutes, optional)

If using Linear for issue tracking:

```bash
# Create Linear configuration
cat > .ce/linear-defaults.yml << 'EOF'
project: "Your Project Name"
assignee: "your.email@example.com"
team: "YourTeam"
EOF

# Test Linear connection
mcp status | grep linear

# If not connected:
rm -rf ~/.mcp-auth
/mcp
# Re-authenticate when prompted
```

**Skip this step** if not using Linear. PRPs will still work without issue tracking.

### Step 5: Activate Serena (1 minute)

```bash
# Activate Serena MCP with full project path
serena_activate("/absolute/path/to/your/project")

# Verify memories loaded
serena_list_memories()

# Expected output:
# Found 23 memories:
# - code-style-conventions (type: critical)
# - testing-standards (type: critical)
# - use-syntropy-tools-not-bash (type: critical)
# ... [20 more memories]
```

### Step 6: Create PRP-0 (1 minute)

```bash
# Create bootstrap documentation
cd /absolute/path/to/your/project

# PRP-0 should already exist from unpack
# Verify and customize if needed
cat PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Update variables (if using template)
sed -i '' "s/{TIMESTAMP}/$(date -u +%Y-%m-%dT%H:%M:%SZ)/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
sed -i '' "s/{TARGET_PROJECT}/your-project-name/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
sed -i '' "s/{CE_VERSION}/CE 1.1/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Verify PRP-0 valid
grep -q "executed_at:" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ PRP-0 valid"
```

---

## Validation

### Post-Installation Checks

Run these commands to verify successful installation:

```bash
# 1. Framework files present
test -f .ce/RULES.md && echo "✓ Rules"
test -f CLAUDE.md && echo "✓ Project guide"
test -d .claude/commands && echo "✓ Commands"
test -d .serena/memories && echo "✓ Memories"
test -d examples && echo "✓ Examples"
test -f PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md && echo "✓ PRP-0"

# 2. Settings valid JSON
jq empty .claude/settings.local.json && echo "✓ Settings valid"

# 3. Command count
echo "Commands: $(ls -1 .claude/commands/*.md | wc -l)"
# Expected: 7 commands

# 4. Memory count
echo "Memories: $(ls -1 .serena/memories/*.md | wc -l)"
# Expected: 23 memories

# 5. Memory types present
echo "Critical: $(grep -l "^type: critical" .serena/memories/*.md | wc -l)"
echo "Regular: $(grep -l "^type: regular" .serena/memories/*.md | wc -l)"
# Expected: 6 critical, 17 regular

# 6. Validation level 4
cd tools
uv run ce validate --level 4
# Expected: All gates pass

# 7. Context drift
uv run ce analyze-context
# Expected: <5% drift (healthy)
```

### Validation Checklist

- [ ] All framework files unpacked
- [ ] CLAUDE.md present with framework guide
- [ ] 7 commands in .claude/commands/
- [ ] 23 memories in .serena/memories/
- [ ] PRP-0 created with valid YAML
- [ ] Settings JSON valid
- [ ] CE tools installed (ce --version works)
- [ ] Serena activated and memories loaded
- [ ] Linear configured (if using)
- [ ] Validation level 4 passes
- [ ] Context drift <5%

---

## Next Steps

### 1. Review Framework (15 minutes)

```bash
# Read project guide
less CLAUDE.md

# Browse examples catalog
less examples/INDEX.md

# Check framework rules
less .ce/RULES.md
```

### 2. Generate First PRP (10 minutes)

```bash
# Create feature request
mkdir -p feature-requests/hello-world
cat > feature-requests/hello-world/INITIAL.md << 'EOF'
# Feature: Hello World

## FEATURE
Create a simple "Hello World" script to test PRP workflow.

**Acceptance Criteria**:
1. Script prints "Hello, World!"
2. Script is executable
3. Test validates output

## EXAMPLES
```python
# Simple Python script
print("Hello, World!")
```

## DOCUMENTATION
- Python 3.12+ standard library

## OTHER CONSIDERATIONS
None - this is a test feature.
EOF

# Generate PRP
/generate-prp feature-requests/hello-world/INITIAL.md

# Output: PRPs/feature-requests/PRP-1-hello-world.md
```

### 3. Execute First PRP (10 minutes)

```bash
# Review generated PRP
cat PRPs/feature-requests/PRP-1-hello-world.md

# Execute PRP
/execute-prp PRPs/feature-requests/PRP-1-hello-world.md

# Validates and commits changes automatically
```

### 4. Explore Examples (10 minutes)

```bash
# Linear integration
cat examples/linear-integration-example.md

# Batch operations
cat examples/patterns/example-simple-feature.md

# Validation patterns
cat examples/l4-validation-example.md

# Tool usage
cat examples/TOOL-USAGE-GUIDE.md
```

---

## Troubleshooting

### Issue: "Repomix command not found"

**Solution**:
```bash
# Install repomix globally
npm install -g repomix

# Or use npx
npx repomix --unpack ce-workflow-docs.xml --target ./
```

### Issue: "Bootstrap script fails"

**Solution**:
```bash
cd tools

# Install UV manually
curl -LsSf https://astral.sh/uv/install.sh | sh

# Retry bootstrap
./bootstrap.sh

# Or install dependencies directly
uv sync
```

### Issue: "Serena not found"

**Solution**:
```bash
# Check MCP status
mcp status | grep serena

# Reconnect MCP
/mcp

# Verify Serena in MCP list
mcp list | grep serena

# If missing, check Syntropy MCP configuration
cat ~/.claude/mcp-config.json | jq '.mcpServers.syntropy'
```

### Issue: "PRP-0 missing variables"

**Solution**:
```bash
# Manually update PRP-0
vim PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Replace placeholders:
# {TIMESTAMP} → 2025-11-04T18:00:00Z
# {TARGET_PROJECT} → your-project-name
# {CE_VERSION} → CE 1.1

# Or use sed
sed -i '' "s/{TIMESTAMP}/$(date -u +%Y-%m-%dT%H:%M:%SZ)/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
sed -i '' "s/{TARGET_PROJECT}/$(basename $(pwd))/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
sed -i '' "s/{CE_VERSION}/CE 1.1/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
```

### Issue: "Settings.local.json missing"

**Solution**:
```bash
# Verify unpack completed
test -f .claude/settings.local.json && echo "Present" || echo "Missing"

# If missing, extract from XML manually
# Or copy from CE framework source:
cp /path/to/ctx-eng-plus/.claude/settings.local.json .claude/

# Verify JSON valid
jq empty .claude/settings.local.json && echo "✓ Valid"
```

### Issue: "Commands not loading"

**Solution**:
```bash
# Check commands directory
ls -la .claude/commands/

# Verify command files present
test -f .claude/commands/generate-prp.md && echo "✓ generate-prp"
test -f .claude/commands/execute-prp.md && echo "✓ execute-prp"

# Restart Claude Code to reload commands
# Commands should appear in command palette
```

---

## Success Criteria

Your greenfield installation is complete when:

- ✅ All validation checks pass (6/6)
- ✅ CE tools installed and functional
- ✅ First PRP generated successfully
- ✅ Context drift <5%
- ✅ Serena memories loaded
- ✅ PRP-0 documents installation
- ✅ No errors in validation level 4

**Total time**: ~10 minutes for complete installation

---

## Comparison: Before vs After

### Before Installation

```
your-project/
├── src/
├── tests/
├── README.md
└── .git/
```

**No framework**, **no automation**, **no knowledge base**.

### After Installation

```
your-project/
├── .ce/                   # Framework components
├── .serena/               # Knowledge base (23 memories)
├── .claude/               # Automation (7 commands)
├── examples/              # Documentation (25+ files)
├── PRPs/                  # PRP workspace
├── tools/                 # CE CLI tools
├── CLAUDE.md              # Project guide
├── src/                   # Your code (unchanged)
├── tests/                 # Your tests (unchanged)
├── README.md              # Your docs (unchanged)
└── .git/                  # Your git (unchanged)
```

**Framework installed**, **automation ready**, **knowledge base active**.

---

## Related Guides

- **Overview**: [../INITIALIZATION.md](../INITIALIZATION.md)
- **Mature Project**: [migration-mature-project.md](migration-mature-project.md)
- **Existing CE**: [migration-existing-ce.md](migration-existing-ce.md)
- **Partial CE**: [migration-partial-ce.md](migration-partial-ce.md)
- **Tool Usage**: [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md)

---

**Questions?** Consult [../INITIALIZATION.md](../INITIALIZATION.md) troubleshooting section or check framework rules in `.ce/RULES.md`.
