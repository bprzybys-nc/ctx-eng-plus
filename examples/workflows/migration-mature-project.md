# Migration Guide: Mature Project (No CE)

**Scenario**: Existing codebase with no Context Engineering installation
**Difficulty**: Moderate
**Time**: ~20 minutes
**Risk**: Low (framework installed separately, no code disruption)

---

## Overview

This guide covers adding the Context Engineering framework to an existing mature project that has no CE components.

**You should use this guide if**:
- Existing codebase with working code
- No `.ce/`, `.serena/`, `.claude/commands/` directories
- No CLAUDE.md file
- Want to add CE without disrupting existing structure

**Example projects that fit this pattern**:
- Standard Python/Node.js/Go projects
- Microservices with established patterns
- Libraries with existing documentation
- Any mature codebase adding CE retroactively

---

## Prerequisites

**Required**:
- Repomix CLI installed
- CE framework distribution file
- Existing git repository
- Project runs and tests pass

**Recommended**:
- Backup or feature branch
- Clean working directory (no uncommitted changes)
- CI/CD pipelines passing

---

## Pre-Migration Checks

### Step 1: Verify Project State

```bash
cd /path/to/your/project

# 1. Confirm no CE components
test ! -d .ce && echo "✓ No CE installed"
test ! -f CLAUDE.md && echo "✓ No CLAUDE.md"

# 2. Verify git clean
git status --porcelain | wc -l
# Expected: 0 (clean working directory)

# 3. Check for potential conflicts
test -d PRPs && echo "⚠️  PRPs/ exists - see conflict resolution"
test -d examples && echo "⚠️  examples/ exists - will be separate"
test -f .claude/settings.local.json && echo "⚠️  Settings exist - will merge"
```

### Step 2: Create Backup Branch

```bash
# Create backup branch before installation
git checkout -b pre-ce-backup
git push origin pre-ce-backup

# Return to main branch
git checkout main

# Or use git worktree for parallel work
git worktree add ../your-project-ce-install -b ce-installation
cd ../your-project-ce-install
```

---

## Installation Steps

### Step 3: Unpack Framework with Merge Strategy (5 minutes)

```bash
# Unpack CE framework with merge mode
repomix --unpack /path/to/ce-workflow-docs.xml --target ./ --merge

# What happens:
# - Creates .ce/ (new, no conflict)
# - Creates .serena/ (new, no conflict)
# - Creates/merges .claude/
# - Creates CLAUDE.md (or appends if exists)
# - Preserves existing examples/ (creates .ce/examples/ for framework)
# - Preserves existing PRPs/ (creates .ce/PRPs/ for framework)
```

**Result**:

```
your-project/
├── src/                         # Your code (unchanged)
├── tests/                       # Your tests (unchanged)
├── docs/                        # Your docs (unchanged)
├── .ce/                         # NEW: Framework components
│   ├── PRPs/
│   ├── examples/
│   └── RULES.md
├── .serena/                     # NEW: Knowledge base
│   └── memories/
├── .claude/                     # NEW or MERGED
│   ├── commands/                # NEW: CE commands
│   └── settings.local.json      # MERGED: CE + your settings
├── examples/                    # PRESERVED: Your project examples
│   └── [your files unchanged]
├── PRPs/                        # NEW or PRESERVED
│   ├── executed/
│   └── feature-requests/
├── tools/                       # NEW: CE CLI tools
│   ├── ce/
│   └── pyproject.toml
└── CLAUDE.md                    # NEW: Framework guide
```

### Step 4: Review Conflicts (if any)

**Conflict 1: existing examples/ directory**

```bash
# Check if examples/ exists
if [ -d examples ]; then
  echo "Conflict: examples/ already exists"

  # Solution: Framework examples go to .ce/examples/
  # Your examples stay in examples/

  # Verify separation
  ls .ce/examples/  # Framework docs
  ls examples/      # Your docs
fi
```

**Conflict 2: existing .claude/settings.local.json**

```bash
# Check if settings exist
if [ -f .claude/settings.local.json ]; then
  echo "Conflict: settings.local.json exists"

  # Backup your settings
  cp .claude/settings.local.json .claude/settings.local.json.pre-ce

  # Repomix merge should have combined them
  # Verify merge successful
  jq empty .claude/settings.local.json && echo "✓ Settings valid"

  # Check permission count increased
  echo "Allow patterns: $(jq '.bash.permissions.allow | length' .claude/settings.local.json)"
  # Expected: ~80 patterns (CE framework adds ~70-80)
fi
```

**Conflict 3: existing PRPs/ directory**

```bash
# Check if PRPs/ exists
if [ -d PRPs ]; then
  echo "Info: PRPs/ already exists - preserving your PRPs"

  # Framework PRPs go to .ce/PRPs/
  # Your PRPs stay in PRPs/

  # Create PRP-0 in your PRPs/
  cp .ce/PRPs/PRP-0-CONTEXT-ENGINEERING.md PRPs/executed/
fi
```

### Step 5: Initialize Tools (3 minutes)

```bash
cd tools
./bootstrap.sh

# Verify CE CLI works
uv run ce --version
# Expected: ce version 1.1.0

# Check validation
uv run ce validate --level 1
# Expected: Structure validation passes
```

### Step 6: Configure Project-Specific Settings (5 minutes)

Update CLAUDE.md with project-specific information:

```bash
# Edit CLAUDE.md
vim CLAUDE.md

# Add project-specific sections:
# - ## Project Structure (your codebase layout)
# - ## Development Workflow (your team's process)
# - ## Testing Standards (your test conventions)
# - ## Deployment Process (your CI/CD)

# Keep framework sections:
# - ## Context Engineering Tools
# - ## Quick Commands
# - ## Tool Naming Convention
# - etc.
```

Create Linear configuration (if using):

```bash
cat > .ce/linear-defaults.yml << 'EOF'
project: "Your Project Name"
assignee: "your.email@example.com"
team: "YourTeam"
EOF
```

### Step 7: Activate Serena and Customize Memories (5 minutes)

```bash
# Activate Serena
serena_activate("/absolute/path/to/your/project")

# Verify framework memories loaded
serena_list_memories()
# Expected: 23 framework memories

# Create project-specific memories
serena_write_memory(
  id="project-architecture",
  content="# Project Architecture\n\n[Your architecture details]",
  type="regular",
  category="architecture",
  tags=["architecture", "system-design"]
)

serena_write_memory(
  id="deployment-process",
  content="# Deployment Process\n\n[Your deployment workflow]",
  type="regular",
  category="guide",
  tags=["deployment", "ci-cd"]
)
```

### Step 8: Create PRP-0 (2 minutes)

```bash
# PRP-0 should exist from unpack
# Update variables for your project
cd /path/to/your/project

sed -i '' "s/{TIMESTAMP}/$(date -u +%Y-%m-%dT%H:%M:%SZ)/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
sed -i '' "s/{TARGET_PROJECT}/$(basename $(pwd))/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md
sed -i '' "s/{CE_VERSION}/CE 1.1/g" PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md

# Add project-specific notes to PRP-0
cat >> PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md << 'EOF'

## Project-Specific Notes

**Existing Structure Preserved**:
- src/ (application code)
- tests/ (test suite)
- docs/ (project documentation)
- examples/ (project examples - separate from .ce/examples/)

**Integration Points**:
- CI/CD: [Your CI/CD system]
- Testing: [Your test framework]
- Deployment: [Your deployment process]

**Custom Memories Created**:
- project-architecture
- deployment-process
EOF
```

---

## Validation

### Post-Installation Checks

```bash
# 1. Framework files installed
test -d .ce && echo "✓ Framework installed"
test -f .ce/RULES.md && echo "✓ Rules present"
test -f CLAUDE.md && echo "✓ Project guide"

# 2. Your code unchanged
git status src/ tests/ docs/
# Expected: No changes to your existing code

# 3. Settings merged correctly
jq '.bash.permissions.allow | length' .claude/settings.local.json
# Expected: ~80 patterns (CE + your settings)

# 4. Memories loaded
serena_list_memories() | wc -l
# Expected: ≥23 (framework + your project memories)

# 5. Commands available
ls .claude/commands/*.md | wc -l
# Expected: ≥7 commands

# 6. Validation passes
cd tools
uv run ce validate --level 3
# Expected: All gates pass

# 7. Your project still works
# Run your existing tests
pytest  # or npm test, go test, etc.
# Expected: All tests still pass
```

### Validation Checklist

- [ ] Framework installed in .ce/
- [ ] Your code unchanged (src/, tests/, docs/)
- [ ] Settings merged successfully
- [ ] Serena memories loaded (framework + project)
- [ ] CE commands available
- [ ] PRP-0 created with project notes
- [ ] Your tests still pass
- [ ] Validation level 3 passes
- [ ] No git conflicts
- [ ] Linear configured (if using)

---

## Conflict Resolution Strategies

### Strategy 1: Existing examples/ Directory

**Problem**: Project already has examples/ for code samples

**Solution**: Separate framework and project examples

```bash
# Framework examples → .ce/examples/
ls .ce/examples/
# CE framework documentation

# Project examples → examples/
ls examples/
# Your project's code examples

# Update examples/README.md to reference both:
cat >> examples/README.md << 'EOF'

## Framework Examples

For Context Engineering framework examples, see `.ce/examples/`.
EOF
```

### Strategy 2: Existing .claude/settings.local.json

**Problem**: Project has custom bash permissions or MCP settings

**Solution**: Merge settings (framework + project)

```bash
# Backup original
cp .claude/settings.local.json .claude/settings.backup.json

# repomix --merge should auto-merge, but verify:
jq '.bash.permissions.allow' .claude/settings.local.json | grep "your-custom-command"
# Your custom commands should still be present

# If merge failed, manual merge:
jq -s '.[0] * .[1]' .claude/settings.backup.json framework-settings.json > .claude/settings.local.json
```

### Strategy 3: Existing docs/ or documentation/

**Problem**: Project has established documentation structure

**Solution**: Keep both, cross-reference

```bash
# Your docs stay in docs/
# Framework docs in .ce/examples/

# Add cross-references
cat >> docs/README.md << 'EOF'

## Development Workflow

For Context Engineering workflow documentation, see:
- `.ce/examples/` - Framework patterns
- `examples/INITIALIZATION.md` - CE setup guide
- `CLAUDE.md` - Project guide with CE integration
EOF
```

---

## Post-Installation Tasks

### 1. Update CI/CD (5 minutes)

Add CE validation to your CI pipeline:

```yaml
# .github/workflows/ci.yml (or equivalent)
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install CE tools
        run: cd tools && ./bootstrap.sh
      - name: Validate CE framework
        run: cd tools && uv run ce validate --level 3
      - name: Check context drift
        run: cd tools && uv run ce analyze-context
```

### 2. Team Onboarding (10 minutes)

Create team onboarding document:

```bash
cat > docs/CE-ONBOARDING.md << 'EOF'
# CE Framework Onboarding

## For New Team Members

1. **Read framework guide**: `cat CLAUDE.md` (15 min)
2. **Review examples**: `ls .ce/examples/` (10 min)
3. **Understand PRPs**: See `PRPs/executed/PRP-0-CONTEXT-ENGINEERING.md`
4. **Try first PRP**: Generate and execute a simple feature PRP

## Key Commands

- `/generate-prp` - Create PRP from feature request
- `/execute-prp` - Run PRP with validation
- `/vacuum` - Clean temporary files
- `ce validate --level 3` - Validate project state

## Resources

- Framework examples: `.ce/examples/`
- Tool usage guide: `examples/TOOL-USAGE-GUIDE.md`
- Migration guides: `examples/workflows/`
EOF
```

### 3. Generate First PRP (10 minutes)

Test the framework with a simple feature:

```bash
# Create feature request
mkdir -p feature-requests/ce-test
cat > feature-requests/ce-test/INITIAL.md << 'EOF'
# Feature: CE Framework Test

## FEATURE
Add a simple utility function to test CE PRP workflow.

## EXAMPLES
[Reference your existing code patterns]

## DOCUMENTATION
[Link to your project docs]
EOF

# Generate PRP
/generate-prp feature-requests/ce-test/INITIAL.md

# Review and execute
/execute-prp PRPs/feature-requests/PRP-1-ce-framework-test.md
```

---

## Rollback (if needed)

If installation causes issues:

```bash
# Option 1: Revert to backup branch
git checkout pre-ce-backup
# Your project is back to pre-CE state

# Option 2: Remove CE components
rm -rf .ce .serena .claude/commands tools
git checkout .claude/settings.local.json CLAUDE.md

# Option 3: Use git worktree rollback
# If installed in worktree
cd /path/to/original/project
git worktree remove ../your-project-ce-install
# Installation attempt deleted, original unchanged
```

---

## Success Criteria

Your mature project CE installation is complete when:

- ✅ Framework installed without disrupting existing code
- ✅ Your tests still pass
- ✅ Settings merged (framework + project)
- ✅ Both examples/ and .ce/examples/ coexist
- ✅ PRP-0 documents installation with project notes
- ✅ First test PRP generated and executed successfully
- ✅ Team onboarded with CE-ONBOARDING.md
- ✅ CI/CD includes CE validation

**Total time**: ~20 minutes installation + ~25 minutes configuration = ~45 minutes

---

## Comparison: Before vs After

### Before

```
mature-project/
├── src/
├── tests/
├── docs/
├── examples/           # Your code examples
├── .github/
└── README.md
```

**No framework**, **manual PRP process**, **no automation**.

### After

```
mature-project/
├── .ce/                      # NEW: Framework
│   ├── examples/             # Framework docs (separate)
│   └── RULES.md
├── .serena/                  # NEW: Knowledge base
├── .claude/                  # NEW: Automation
├── tools/                    # NEW: CE CLI
├── PRPs/                     # NEW: PRP workspace
├── CLAUDE.md                 # NEW: Project guide
├── src/                      # UNCHANGED: Your code
├── tests/                    # UNCHANGED: Your tests
├── docs/                     # UNCHANGED: Your docs
├── examples/                 # UNCHANGED: Your examples
├── .github/                  # UPDATED: + CE validation
└── README.md                 # UNCHANGED
```

**Framework integrated**, **automation active**, **code untouched**.

---

## Real-World Example: Adding CE to mlx-trading Project

Based on actual migration of mlx-trading-pipeline-context-engineering:

**Before**:
- 2 custom commands
- project-context.md (6KB)
- rules.md (3KB)
- Minimal settings (198B)
- No Serena

**After**:
- 9 total commands (2 custom + 7 framework)
- CLAUDE.md (consolidated project-context.md + rules.md + framework guide)
- Settings expanded to 8KB (198B → 8KB with framework permissions)
- Serena added (23 framework memories + 5 project memories)
- .ce/ structure with framework components

**Time**: 35 minutes total
**Outcome**: Successful, all existing functionality preserved

---

## Related Guides

- **Overview**: [../INITIALIZATION.md](../INITIALIZATION.md)
- **Greenfield**: [migration-greenfield.md](migration-greenfield.md)
- **Existing CE**: [migration-existing-ce.md](migration-existing-ce.md)
- **Partial CE**: [migration-partial-ce.md](migration-partial-ce.md)

---

**Questions?** Consult [../INITIALIZATION.md](../INITIALIZATION.md) troubleshooting or `.ce/RULES.md` for framework rules.
