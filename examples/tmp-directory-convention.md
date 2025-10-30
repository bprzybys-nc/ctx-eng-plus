# tmp/ Directory Convention

## Rule: Keep Working Directory Clean

**Only final deliverables in tracked directories. All work-in-progress goes to tmp/**

## Directory Structure

```
ctx-eng-plus/
├── PRPs/                    # ONLY final PRP documents
│   ├── executed/
│   └── feature-requests/
├── tmp/                     # ALL work-in-progress (gitignored)
│   ├── batch-gen/          # Batch generation heartbeat files
│   ├── feature-requests/   # INITIAL.md and PLAN.md files
│   └── scratch/            # Any other temporary work
└── examples/               # Documentation and examples
```

## Rules

### 1. INITIAL.md and PLAN.md

**Location**: `tmp/feature-requests/<feature-name>/`

**Example**:
```bash
# ✅ CORRECT
tmp/feature-requests/syntropy-tool-management/INITIAL.md
tmp/feature-requests/syntropy-tool-management/PLAN.md

# ❌ WRONG
feature-requests/syntropy-tool-management/INITIAL.md
feature-requests/syntropy-tool-management/PLAN.md
```

### 2. Batch Generation Heartbeat Files

**Location**: `tmp/batch-gen/`

**Example**:
```bash
# ✅ CORRECT
tmp/batch-gen/PRP-30.1.1.status
tmp/batch-gen/PRP-30.2.1.status

# ❌ WRONG
.tmp/batch-gen/PRP-30.1.1.status  # No leading dot
```

### 3. PRPs (Final Deliverables)

**Location**: `PRPs/feature-requests/` or `PRPs/executed/`

**Example**:
```bash
# ✅ CORRECT
PRPs/feature-requests/PRP-30.1.1-syntropy-mcp-tool-management.md
PRPs/executed/PRP-29-haiku-optimized-prp-guidelines.md

# ❌ WRONG
tmp/PRPs/PRP-30.1.1-syntropy-mcp-tool-management.md
```

## Workflow Example

### Generate PRP from INITIAL.md

```bash
# Step 1: Create INITIAL.md in tmp/
mkdir -p tmp/feature-requests/my-feature
vim tmp/feature-requests/my-feature/INITIAL.md

# Step 2: Generate PRP (output goes to PRPs/)
/generate-prp tmp/feature-requests/my-feature/INITIAL.md
# Output: PRPs/feature-requests/PRP-X-my-feature.md

# Step 3: Clean up (optional)
rm -rf tmp/feature-requests/my-feature
```

### Batch Generation from PLAN.md

```bash
# Step 1: Create PLAN.md in tmp/
mkdir -p tmp/feature-requests/big-feature
vim tmp/feature-requests/big-feature/PLAN.md

# Step 2: Generate batch PRPs
/batch-gen-prp tmp/feature-requests/big-feature/PLAN.md
# Heartbeat files: tmp/batch-gen/PRP-X.Y.Z.status
# Output PRPs: PRPs/feature-requests/PRP-X.Y.Z-*.md

# Step 3: Clean up (automatic)
# Heartbeat files cleaned up after generation completes
```

## Git Configuration

**Ensure tmp/ is gitignored**:

```gitignore
# .gitignore
tmp/
.tmp/
*.tmp
```

## Benefits

1. **Clean working directory**: Only final deliverables tracked in git
2. **Easy cleanup**: Delete `tmp/` anytime without losing work
3. **Clear separation**: Work-in-progress vs. deliverables
4. **No git noise**: No accidental commits of INITIAL.md or heartbeat files

## Migration

If you have existing files in wrong locations:

```bash
# Move INITIAL.md files
mkdir -p tmp/feature-requests/
mv feature-requests/* tmp/feature-requests/

# Move batch-gen files (if any)
mkdir -p tmp/batch-gen/
mv .tmp/batch-gen/* tmp/batch-gen/ 2>/dev/null || true
rmdir .tmp/batch-gen .tmp 2>/dev/null || true
```
