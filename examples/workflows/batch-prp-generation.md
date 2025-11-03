# Batch PRP Generation Workflow

Complete guide for decomposing large feature plans into staged, parallelizable PRPs using the `/batch-gen-prp` command with automatic dependency analysis and parallel subagent execution.

## Purpose

Batch PRP generation enables:

- **Parallel development**: Generate multiple PRPs simultaneously using subagents
- **Dependency management**: Automatic analysis of dependencies and file conflicts
- **Staged execution**: Group independent PRPs for concurrent implementation
- **Time savings**: 60% faster than sequential PRP generation
- **Linear integration**: Auto-create Linear issues for all generated PRPs

**When to Use**:

- Large features requiring 5+ PRPs
- Complex projects with clear phase dependencies
- Team coordination across parallel work streams
- Sprint planning with multiple related features

**When NOT to Use**:

- Single feature requiring 1-2 PRPs → Use `/generate-prp` directly
- Exploratory work without clear plan → Break down incrementally
- PRPs with unclear dependencies → Define dependencies first

## Prerequisites

- Plan document in markdown format (see structure below)
- Linear integration configured (`.ce/linear-defaults.yml`)
- Syntropy MCP active (`/syntropy-health`)
- Clean git working directory

## Plan Document Structure

### Required Format

```markdown
# Feature Name

Brief description of the overall feature.

## Phases

### Phase 1: Phase Name

**Goal**: One-sentence objective

**Estimated Hours**: 2.5

**Complexity**: low | medium | high

**Files Modified**:
- path/to/file1.py
- path/to/file2.py

**Dependencies**: None | Phase 2, Phase 3

**Implementation Steps**:
1. Step one
2. Step two
3. Step three

**Validation Gates**:
- L1: Syntax check
- L2: Unit tests pass
- L3: Integration tests pass
- L4: Pattern conformance

### Phase 2: Next Phase

[Same structure...]
```

### Example Plan Document

```markdown
# User Authentication System

Implement JWT-based authentication with refresh tokens and role-based access control.

## Phases

### Phase 1: Database Schema

**Goal**: Create user and role tables with appropriate indexes

**Estimated Hours**: 1.5

**Complexity**: low

**Files Modified**:
- migrations/001_create_users.sql
- models/user.py

**Dependencies**: None

**Implementation Steps**:
1. Create users table (id, email, password_hash, created_at)
2. Create roles table (id, name, permissions)
3. Create user_roles junction table
4. Add indexes on email and role lookups

**Validation Gates**:
- L1: SQL syntax valid
- L2: Migration runs successfully
- L3: Can create/query users
- L4: Schema matches design doc

### Phase 2: JWT Token Management

**Goal**: Implement token generation, validation, and refresh

**Estimated Hours**: 3.0

**Complexity**: medium

**Files Modified**:
- auth/tokens.py
- auth/middleware.py
- config/settings.py

**Dependencies**: Phase 1

**Implementation Steps**:
1. Create JWT token generation function
2. Implement token validation middleware
3. Add refresh token rotation logic
4. Configure token expiration settings

**Validation Gates**:
- L1: Type hints correct
- L2: Unit tests for token gen/validation
- L3: Integration test with test user
- L4: Security best practices followed

### Phase 3: API Endpoints

**Goal**: Create login, logout, refresh endpoints

**Estimated Hours**: 2.5

**Complexity**: medium

**Files Modified**:
- api/auth.py
- api/routes.py

**Dependencies**: Phase 2

**Implementation Steps**:
1. POST /auth/login endpoint
2. POST /auth/logout endpoint
3. POST /auth/refresh endpoint
4. Add rate limiting to auth endpoints

**Validation Gates**:
- L1: API contract matches OpenAPI spec
- L2: Unit tests for all endpoints
- L3: E2E test: login → access resource → refresh → logout
- L4: Error handling comprehensive

### Phase 4: Role-Based Access Control

**Goal**: Implement permission checking middleware

**Estimated Hours**: 2.0

**Complexity**: medium

**Files Modified**:
- auth/permissions.py
- auth/decorators.py
- api/middleware.py

**Dependencies**: Phase 2

**Implementation Steps**:
1. Create permission checking decorator
2. Implement role hierarchy (admin > user > guest)
3. Add route protection via @require_permission
4. Document permission model

**Validation Gates**:
- L1: Decorator syntax correct
- L2: Unit tests for permission checks
- L3: Integration test with various roles
- L4: Security audit checklist passed
```

## Workflow Steps

### Step 1: Create Plan Document

```bash
# Create plan file
vim AUTH-FEATURE-PLAN.md

# Structure: See "Plan Document Structure" above
# Tip: Start with phases, estimate hours, identify dependencies
```

**Dependency Guidelines**:

- **"None"**: Phase can start immediately (Stage 1)
- **"Phase X"**: Must wait for Phase X to complete
- **Multiple deps**: "Phase 1, Phase 3" → Stage = max(dep_stages) + 1

**File Conflict Detection**:

- If Phase A and Phase B modify same file → Implicit dependency
- System will detect and stage sequentially
- Avoid by splitting files or merging phases

### Step 2: Generate PRPs

```bash
# Run batch generation
/batch-gen-prp AUTH-FEATURE-PLAN.md
```

**What Happens**:

1. **Parse plan**: Extract phases, dependencies, files
2. **Build dependency graph**: Analyze explicit + implicit (file) deps
3. **Assign stages**: Group independent PRPs for parallel execution
4. **Create Linear issues**: One issue per PRP (optional)
5. **Spawn subagents**: Parallel Sonnet agents generate PRPs
6. **Monitor health**: 30-second heartbeat polling
7. **Collect results**: Aggregate PRPs from all subagents

**Output Example**:

```
📋 Batch PRP Generation: AUTH-FEATURE-PLAN
============================================================

Parsing plan: 4 phases identified
Building dependency graph...
Assigning stages:
  Stage 1: Phase 1 (database-schema)
  Stage 2: Phase 2 (jwt-tokens), Phase 4 (rbac)  [parallel]
  Stage 3: Phase 3 (api-endpoints)

Creating Linear issues:
  ✅ CTX-45: Phase 1 - Database Schema
  ✅ CTX-46: Phase 2 - JWT Token Management
  ✅ CTX-47: Phase 3 - API Endpoints
  ✅ CTX-48: Phase 4 - Role-Based Access Control

Spawning subagents (parallel generation):
  🚀 Stage 1: 1 agent
  🚀 Stage 2: 2 agents (parallel)
  🚀 Stage 3: 1 agent

Monitoring progress:
  ✅ Stage 1 complete (90s)
  ✅ Stage 2 complete (120s, parallel)
  ✅ Stage 3 complete (85s)

Generated PRPs:
  PRPs/feature-requests/PRP-43.1.1-database-schema.md
  PRPs/feature-requests/PRP-43.2.1-jwt-tokens.md
  PRPs/feature-requests/PRP-43.2.2-rbac.md
  PRPs/feature-requests/PRP-43.3.1-api-endpoints.md

Total time: 295s (4m 55s)
Sequential estimate: 720s (12m) → 59% time savings
============================================================
```

### Step 3: Review Generated PRPs

```bash
# List generated PRPs
ls PRPs/feature-requests/PRP-43.*

# Review first PRP
cat PRPs/feature-requests/PRP-43.1.1-database-schema.md
```

**Check**:

- ✅ Dependencies correctly specified
- ✅ Implementation steps detailed
- ✅ Validation gates comprehensive
- ✅ Estimated hours realistic
- ✅ Files to modify listed
- ✅ Linear issue ID present in frontmatter

### Step 4: Execute PRPs

```bash
# Execute entire batch (sequential by stage)
/batch-exe-prp --batch 43

# Or execute specific stage
/batch-exe-prp --batch 43 --stage 1
```

**See**: [batch-prp-execution.md](batch-prp-execution.md) for execution workflow.

## Dependency Graph Algorithm

### Stage Assignment Logic

```python
def assign_stages(phases):
    """Assign stages based on dependencies and file conflicts"""

    # Step 1: Build explicit dependency graph
    deps = {}
    for phase in phases:
        deps[phase.id] = parse_dependencies(phase.dependencies)

    # Step 2: Detect file conflicts (implicit dependencies)
    for phase_a in phases:
        for phase_b in phases:
            if phase_a.id != phase_b.id:
                files_a = set(phase_a.files_modified)
                files_b = set(phase_b.files_modified)
                if files_a & files_b:  # Intersection = conflict
                    # Add implicit dependency
                    if phase_a.id < phase_b.id:
                        deps[phase_b.id].append(phase_a.id)

    # Step 3: Assign stages via topological sort
    stages = {}
    for phase in topological_sort(phases, deps):
        if not deps[phase.id]:
            stages[phase.id] = 1  # No deps = Stage 1
        else:
            # Stage = max(dep_stages) + 1
            dep_stages = [stages[dep] for dep in deps[phase.id]]
            stages[phase.id] = max(dep_stages) + 1

    return stages
```

**Example**:

```
Plan:
  Phase 1: No deps, modifies file_a.py → Stage 1
  Phase 2: Depends on Phase 1, modifies file_b.py → Stage 2
  Phase 3: Depends on Phase 1, modifies file_c.py → Stage 2 (parallel with Phase 2)
  Phase 4: Depends on Phase 2, modifies file_b.py → Stage 3 (file conflict with Phase 2)

Result:
  Stage 1: [Phase 1]
  Stage 2: [Phase 2, Phase 3]  # Parallel
  Stage 3: [Phase 4]
```

## Health Monitoring

### Heartbeat Files

During generation, subagents write heartbeat files every 10 seconds:

```
/tmp/prp-batch-43-stage-2-agent-1.heartbeat
Content: {"status": "generating", "timestamp": "2025-11-03T12:34:56Z", "progress": 60}
```

**Monitoring Process**:

1. Poll heartbeat files every 30 seconds
2. If file not updated for 60s → Agent stalled
3. After 2 failed polls → Kill agent, retry or fail

**Error Handling**:

- **Agent timeout**: Retry generation once
- **Agent crash**: Report error, skip phase
- **Parse error**: Highlight phase with issue, continue others

## Common Patterns

### Pattern 1: Complex Feature Breakdown

For large features (10+ phases), create hierarchical plan:

```markdown
# Parent Feature: E-Commerce Platform

## Mega-Phase 1: User Management (4 sub-phases)

[Break down into AUTH-FEATURE-PLAN.md]

## Mega-Phase 2: Product Catalog (6 sub-phases)

[Break down into CATALOG-FEATURE-PLAN.md]

## Mega-Phase 3: Order Processing (5 sub-phases)

[Break down into ORDERS-FEATURE-PLAN.md]
```

Then generate each sub-plan separately:

```bash
/batch-gen-prp AUTH-FEATURE-PLAN.md     # Batch 43
/batch-gen-prp CATALOG-FEATURE-PLAN.md  # Batch 44
/batch-gen-prp ORDERS-FEATURE-PLAN.md   # Batch 45
```

### Pattern 2: Incremental Refinement

Start with high-level plan, generate PRPs, then refine:

```bash
# 1. Generate PRPs from initial plan
/batch-gen-prp INITIAL-PLAN.md

# 2. Review generated PRPs
cat PRPs/feature-requests/PRP-43.*.md

# 3. Refine plan based on generated PRPs
vim INITIAL-PLAN.md  # Add missing phases, clarify deps

# 4. Regenerate with batch ID override
/batch-gen-prp INITIAL-PLAN.md --batch 43 --overwrite
```

### Pattern 3: Mixed Batch Execution

Execute stages incrementally with review between:

```bash
# Execute Stage 1
/batch-exe-prp --batch 43 --stage 1

# Review results
git diff

# If good, execute Stage 2 (parallel PRPs)
/batch-exe-prp --batch 43 --stage 2

# Continue to Stage 3
/batch-exe-prp --batch 43 --stage 3
```

## Anti-Patterns

### ❌ Anti-Pattern 1: Vague Dependencies

**Bad**:

```markdown
**Dependencies**: Some database work needs to be done first
```

**Good**:

```markdown
**Dependencies**: Phase 1

(Or: **Dependencies**: None  if truly independent)
```

**Why**: System cannot parse vague dependency descriptions.

### ❌ Anti-Pattern 2: Missing File Conflicts

**Bad**:

```markdown
Phase 2:
**Files Modified**: api/routes.py

Phase 3:
**Files Modified**: api/routes.py  # Same file!
**Dependencies**: None  # Incorrect!
```

**Good**:

```markdown
Phase 3:
**Dependencies**: Phase 2  # Explicit dependency due to file conflict
```

**Why**: System detects file conflicts, but explicit deps are clearer.

### ❌ Anti-Pattern 3: Over-Parallelization

**Bad**: 20 phases all marked **Dependencies**: None

**Good**: Identify logical groupings, add dependencies for clarity

**Why**: Too many parallel PRPs overwhelm subagents and cause conflicts during execution.

## Related Examples

- [batch-prp-execution.md](batch-prp-execution.md) - Executing generated PRPs
- [../syntropy/linear-integration.md](../syntropy/linear-integration.md) - Linear issue creation
- [context-drift-remediation.md](context-drift-remediation.md) - Maintaining context health
- [../TOOL-USAGE-GUIDE.md](../TOOL-USAGE-GUIDE.md) - Tool selection during PRP generation

## Troubleshooting

### Issue: "Phase parse error"

**Symptom**: Batch generation fails with "Cannot parse Phase X"

**Cause**: Phase missing required fields (Goal, Estimated Hours, etc.)

**Solution**: Verify all phases have required structure:

```markdown
### Phase X: Name

**Goal**: ...
**Estimated Hours**: ...
**Complexity**: ...
**Files Modified**: ...
**Dependencies**: ...
**Implementation Steps**: ...
**Validation Gates**: ...
```

### Issue: Circular dependencies detected

**Symptom**: "Cannot assign stages: circular dependency"

**Cause**: Phase A depends on Phase B, which depends on Phase A

**Solution**: Review dependencies, break cycle:

```bash
# Identify cycle
grep "Dependencies:" PLAN.md

# Fix by removing circular dep or adding intermediate phase
```

### Issue: Subagent timeout

**Symptom**: "Agent X timed out after 120s"

**Cause**: Complex phase taking too long to generate

**Solution**: Break down complex phase into smaller phases

## Performance Tips

1. **Batch size**: 5-8 phases optimal, 10+ phases split into multiple batches
2. **Parallel stages**: Aim for 2-3 PRPs per parallel stage (not 10+)
3. **File conflicts**: Minimize file overlap to maximize parallelization
4. **Dependencies**: Only specify necessary deps, avoid over-constraining
5. **Monitoring**: Check heartbeat files if generation takes >5 minutes

## Resources

- Slash Command: `.claude/commands/batch-gen-prp.md`
- Batch Execution: [batch-prp-execution.md](batch-prp-execution.md)
- Linear Integration: `.ce/linear-defaults.yml`
- Health Monitoring: `/tmp/prp-batch-*.heartbeat`
