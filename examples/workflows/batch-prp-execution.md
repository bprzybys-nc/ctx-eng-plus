# Batch PRP Execution Workflow

Complete guide for executing batches of PRPs in parallel using git worktrees, health monitoring via commits, and sequential merging with conflict resolution.

## Purpose

Batch PRP execution enables:

- **Parallel implementation**: Execute multiple PRPs simultaneously in isolated worktrees
- **Stage-based execution**: Run independent PRPs concurrently, dependent PRPs sequentially
- **Health monitoring**: Track progress via git commits (heartbeat mechanism)
- **Conflict resolution**: Detect and resolve merge conflicts during sequential merge
- **Time savings**: 55% faster than sequential execution
- **Safety**: Each PRP isolated until merge, rollback possible

**When to Use**:

- Executing PRPs from batch generation (Batch ID 43, 44, etc.)
- Multiple independent features ready for implementation
- Sprint execution with parallel development
- Large refactoring split into phases

**When NOT to Use**:

- Single PRP → Use `/execute-prp` directly
- PRPs with complex interdependencies → Execute sequentially
- Exploratory changes → Iterate without worktrees

## Prerequisites

- Generated PRPs from `/batch-gen-prp` (with batch ID and stage assignments)
- Clean git working directory
- Git worktree support (Git 2.5+)
- Sufficient disk space (~2GB per worktree for large repos)

## Workflow Steps

### Step 1: Review Batch Structure

```bash
# List PRPs in batch
ls PRPs/feature-requests/PRP-43.*

# Check stage assignments
for prp in PRPs/feature-requests/PRP-43.*.md; do
  echo "$(basename $prp): $(grep 'stage:' $prp | cut -d':' -f2)"
done
```

**Output**:

```
PRP-43.1.1-database-schema.md: 1
PRP-43.2.1-jwt-tokens.md: 2
PRP-43.2.2-rbac.md: 2
PRP-43.3.1-api-endpoints.md: 3
```

**Stage Interpretation**:

- **Stage 1**: Execute first (foundation)
- **Stage 2**: Execute after Stage 1 completes (parallel within stage)
- **Stage 3**: Execute after Stage 2 completes

### Step 2: Execute Batch

```bash
# Execute entire batch (all stages sequentially, parallel within stage)
/batch-exe-prp --batch 43

# Or execute specific stage
/batch-exe-prp --batch 43 --stage 2
```

**What Happens**:

1. **Create worktrees**: One worktree per PRP in current stage
2. **Spawn subagents**: Parallel Sonnet agents execute PRPs
3. **Monitor health**: Poll git commits every 60s
4. **Collect results**: Wait for all stage PRPs to complete
5. **Merge sequentially**: Merge worktrees one-by-one into main
6. **Cleanup worktrees**: Remove worktrees after successful merge
7. **Repeat**: Move to next stage

**Output Example**:

```
🚀 Batch PRP Execution: Batch 43
============================================================

Stage 1: Foundation (1 PRP)
  Creating worktree: ../ctx-eng-plus-prp-43.1.1
  Branch: prp-43-1-1-database-schema
  Executing PRP-43.1.1...
  ✅ Completed (120s)
  Merging prp-43-1-1-database-schema → main
  ✅ Merged successfully
  Cleanup: Removing worktree

Stage 2: Parallel Implementation (2 PRPs)
  Creating worktrees:
    ../ctx-eng-plus-prp-43.2.1 (jwt-tokens)
    ../ctx-eng-plus-prp-43.2.2 (rbac)
  Executing in parallel...
    PRP-43.2.1: ✅ Completed (180s)
    PRP-43.2.2: ✅ Completed (150s)
  Merging sequentially:
    prp-43-2-1-jwt-tokens → main: ✅
    prp-43-2-2-rbac → main: ⚠️  Conflict in auth/middleware.py
      Resolved: Kept both changes (manual review)
    ✅ All merged
  Cleanup: Removing worktrees

Stage 3: API Layer (1 PRP)
  Creating worktree: ../ctx-eng-plus-prp-43.3.1
  Executing PRP-43.3.1...
  ✅ Completed (140s)
  Merging prp-43-3-1-api-endpoints → main
  ✅ Merged successfully
  Cleanup: Removing worktree

============================================================
Total time: 590s (9m 50s)
Sequential estimate: 590s per PRP × 4 = 2360s (39m 20s)
Time savings: 75% (parallel execution within stages)

Final status:
  ✅ All 4 PRPs executed and merged
  🔧 1 conflict resolved manually
  📊 Validation: Run `cd tools && uv run ce validate --level 4`
============================================================
```

### Step 3: Verify Results

```bash
# Check git log
git log --oneline -10

# Run validation
cd tools && uv run ce validate --level 4

# Test application
uv run pytest tests/ -v
```

## Git Worktree Architecture

### Worktree Creation Pattern

```python
def create_worktree(prp_id, stage, order):
    """Create isolated worktree for PRP execution"""

    # Generate unique branch name
    branch_name = f"prp-{prp_id.replace('.', '-')}-{prp_name_slug}"

    # Calculate worktree path (sibling directory)
    worktree_path = f"../ctx-eng-plus-prp-{prp_id}"

    # Create worktree
    git worktree add {worktree_path} -b {branch_name}

    # Verify worktree created
    git worktree list | grep {worktree_path}

    return worktree_path, branch_name
```

**Worktree Layout**:

```
/Users/bprzybysz/nc-src/
├── ctx-eng-plus/              # Main repo (on main branch)
├── ctx-eng-plus-prp-43.1.1/   # Worktree for PRP-43.1.1
├── ctx-eng-plus-prp-43.2.1/   # Worktree for PRP-43.2.1 (parallel)
├── ctx-eng-plus-prp-43.2.2/   # Worktree for PRP-43.2.2 (parallel)
└── ctx-eng-plus-prp-43.3.1/   # Worktree for PRP-43.3.1
```

**Benefits**:

- **Isolation**: Each PRP modifies independent copy
- **Parallel safety**: No file conflicts during execution
- **Rollback**: Can abandon worktree without affecting main
- **Inspection**: Browse worktrees while execution continues

### Health Monitoring via Git Commits

**Heartbeat Mechanism**: Subagents commit progress every 5 minutes

```python
def monitor_health(worktree_path, branch_name):
    """Monitor PRP execution health via git commits"""

    last_commit_time = None

    while True:
        # Check latest commit in worktree
        commit_time = git -C {worktree_path} log -1 --format=%ct

        if commit_time > last_commit_time:
            # Commit made = agent alive
            last_commit_time = commit_time
            print(f"✅ {branch_name}: Active (commit at {commit_time})")
        else:
            # No commit for 10 minutes = stalled
            if time.now() - last_commit_time > 600:
                print(f"⚠️  {branch_name}: Stalled (no commits for 10m)")
                # Kill agent, retry or fail

        time.sleep(60)  # Poll every 60s
```

**Commit Pattern**:

```
Initial commit: "PRP-43.1.1: Start database schema"
Progress commit (5m): "PRP-43.1.1: Created users table"
Progress commit (10m): "PRP-43.1.1: Added indexes"
Final commit: "PRP-43.1.1: Validation L1-L4 passed"
```

### Sequential Merge Strategy

**Why Sequential?** Parallel merges cause race conditions on main branch.

```python
def merge_stage_results(stage_branches):
    """Merge all branches from stage into main sequentially"""

    for branch in stage_branches:
        # Switch to main
        git checkout main

        # Merge with no-ff (preserve branch history)
        result = git merge {branch} --no-ff

        if result.has_conflict:
            # Handle conflict (see Conflict Resolution below)
            resolve_conflict(branch)
            git add .
            git commit -m "Merge {branch}: Resolved conflicts"

        # Push to remote
        git push origin main

        # Verify merge successful
        assert git log -1 --oneline | grep "Merge {branch}"
```

**Merge Order**: Determined by PRP order within stage (PRP-43.2.1 before PRP-43.2.2)

## Conflict Resolution

### Conflict Types

1. **Content conflict**: Same line modified in both branches
2. **Structural conflict**: File added/removed in both branches
3. **Semantic conflict**: Changes compatible syntactically but break logic

### Resolution Workflow

```python
def resolve_conflict(branch):
    """Resolve merge conflict during batch execution"""

    # Step 1: Identify conflicting files
    conflicts = git diff --name-only --diff-filter=U

    for file in conflicts:
        print(f"⚠️  Conflict in {file}")

        # Step 2: Read file to see conflict markers
        content = Read(file_path=file)

        # Step 3: Analyze conflict
        print(content)  # Shows <<<<<<< HEAD / ======= / >>>>>>> branch

        # Step 4: Resolve (3 strategies)
        if is_trivial_conflict(content):
            # Strategy A: Automatic resolution (keep both changes)
            auto_resolve(file, content)
        elif can_ask_user(file):
            # Strategy B: Ask user for decision
            user_choice = ask_user_to_resolve(file, content)
            apply_user_choice(file, user_choice)
        else:
            # Strategy C: Manual review required
            print(f"🔧 Manual review required for {file}")
            print(f"   1. Edit file to resolve")
            print(f"   2. git add {file}")
            print(f"   3. Continue merge")
            # Pause execution, wait for manual resolution
```

**Example Conflict**:

```python
# File: auth/middleware.py
# PRP-43.2.1 added JWT validation
# PRP-43.2.2 added permission checking

<<<<<<< HEAD
def auth_middleware(request):
    # JWT validation from PRP-43.2.1
    token = request.headers.get('Authorization')
    user = validate_jwt_token(token)
    request.user = user
=======
def auth_middleware(request):
    # Permission checking from PRP-43.2.2
    user = get_current_user(request)
    check_permissions(user, request.route)
    request.user = user
>>>>>>> prp-43-2-2-rbac
```

**Resolution** (keep both):

```python
def auth_middleware(request):
    # JWT validation from PRP-43.2.1
    token = request.headers.get('Authorization')
    user = validate_jwt_token(token)

    # Permission checking from PRP-43.2.2
    check_permissions(user, request.route)

    request.user = user
```

## Common Patterns

### Pattern 1: Incremental Stage Execution

Execute stages one-by-one with validation between:

```bash
# Stage 1: Foundation
/batch-exe-prp --batch 43 --stage 1
cd tools && uv run ce validate --level 4

# Stage 2: Parallel features (if validation passed)
/batch-exe-prp --batch 43 --stage 2
cd tools && uv run ce validate --level 4

# Stage 3: Integration (if validation passed)
/batch-exe-prp --batch 43 --stage 3
cd tools && uv run ce validate --level 4
```

### Pattern 2: Inspect Worktree During Execution

Browse worktree while subagent executes:

```bash
# In terminal 1: Execute batch
/batch-exe-prp --batch 43 --stage 2

# In terminal 2: Inspect worktree
cd ../ctx-eng-plus-prp-43.2.1
git log --oneline
ls -la
cat auth/tokens.py  # See changes as they're made
```

### Pattern 3: Retry Failed PRP

If PRP execution fails, retry individually:

```bash
# Batch execution reports: "PRP-43.2.2 failed"

# Remove failed worktree
git worktree remove ../ctx-eng-plus-prp-43.2.2 --force

# Re-execute specific PRP
/execute-prp PRPs/feature-requests/PRP-43.2.2-rbac.md

# Or retry entire stage
/batch-exe-prp --batch 43 --stage 2 --retry
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Executing All Stages in Parallel

**Bad**:

```bash
# DON'T execute all stages at once
/batch-exe-prp --batch 43 --parallel-all  # No such flag!
```

**Good**:

```bash
# DO execute stages sequentially
/batch-exe-prp --batch 43  # Stages run in order
```

**Why**: Dependencies between stages require sequential execution.

### ❌ Anti-Pattern 2: Manual Worktree Creation

**Bad**:

```bash
# DON'T create worktrees manually
git worktree add ../ctx-eng-plus-prp-43.1.1 -b custom-branch
/execute-prp ...
```

**Good**:

```bash
# DO let batch execution manage worktrees
/batch-exe-prp --batch 43
```

**Why**: Batch execution handles worktree lifecycle, naming, and cleanup.

### ❌ Anti-Pattern 3: Ignoring Conflicts

**Bad**:

```bash
# DON'T force merge with conflicts
git merge --no-ff --strategy-option theirs  # Loses changes!
```

**Good**:

```bash
# DO resolve conflicts manually
# Edit conflicting files
git add .
git commit -m "Resolved conflicts: kept both changes"
```

**Why**: Force merging loses changes and breaks functionality.

## Related Examples

- [batch-prp-generation.md](batch-prp-generation.md) - Generating PRPs for batch execution
- [../syntropy/linear-integration.md](../syntropy/linear-integration.md) - Updating Linear issue status
- [context-drift-remediation.md](context-drift-remediation.md) - Post-execution context sync
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - Tool selection during execution

## Troubleshooting

### Issue: "Worktree already exists"

**Symptom**: `fatal: '/Users/.../ctx-eng-plus-prp-43.1.1' already exists`

**Cause**: Previous execution didn't cleanup worktree

**Solution**:

```bash
# List worktrees
git worktree list

# Remove stale worktree
git worktree remove ../ctx-eng-plus-prp-43.1.1

# Or force remove if locked
git worktree remove ../ctx-eng-plus-prp-43.1.1 --force

# Prune stale references
git worktree prune
```

### Issue: Agent stalled (no commits)

**Symptom**: "PRP-43.2.1 stalled: no commits for 10 minutes"

**Cause**: Complex task or agent error

**Solution**:

```bash
# Check worktree manually
cd ../ctx-eng-plus-prp-43.2.1
git log --oneline  # See last commit
git status  # Check working tree state

# If agent truly stalled, kill and retry
cd /Users/bprzybysz/nc-src/ctx-eng-plus
/batch-exe-prp --batch 43 --stage 2 --retry-prp 43.2.1
```

### Issue: Merge conflict - cannot auto-resolve

**Symptom**: "⚠️  Conflict in file.py - manual review required"

**Solution**:

```bash
# Edit file to resolve conflict
vim file.py

# Remove conflict markers (<<<, ===, >>>)
# Integrate both changes logically

# Mark as resolved
git add file.py

# Continue batch execution (will auto-resume)
```

## Performance Tips

1. **Stage size**: 2-3 PRPs per parallel stage optimal (not 10+)
2. **Disk space**: Ensure 5-10GB free for worktrees
3. **Health polling**: 60s interval balances responsiveness and overhead
4. **Conflict prevention**: Review PRPs for file overlaps before execution
5. **Sequential merge**: Merge order: foundation → features → integration

## Resources

- Slash Command: `.claude/commands/batch-exe-prp.md`
- Batch Generation: [batch-prp-generation.md](batch-prp-generation.md)
- Git Worktree Docs: `git help worktree`
- Conflict Resolution: Git merge conflict resolution guide
