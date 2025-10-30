# /generate-prp - Generate PRP from INITIAL.md or Batch Input

Automates PRP (Product Requirements Prompt) generation from INITIAL.md with comprehensive codebase research, documentation fetching, and context synthesis.

**Supports two modes**:
- **Solo Mode**: Interactive generation from INITIAL.md file (user-facing)
- **Batch Mode**: Automated generation from structured JSON input (subagent-facing, used by `/batch-gen-prp`)

## Mode Detection

The command automatically detects which mode to use:
- **Contains `"batch_mode": true` in prompt** → Batch Mode
- **Otherwise** → Solo Mode (default)

## Usage

### Solo Mode

```
/generate-prp <initial-md-path>                        # Creates new PRP + Linear issue
/generate-prp <initial-md-path> --join-prp <prp-ref>  # Joins existing PRP's Linear issue
```

**PRP Reference Formats**:
- Number: `--join-prp 12` (searches for PRP-12)
- ID: `--join-prp PRP-12`
- File path: `--join-prp PRPs/executed/PRP-12-feature.md`

### Batch Mode (Subagent)

**Used by**: `/batch-gen-prp` coordinator spawning parallel subagents

**Input Format**: Structured JSON in prompt
```json
{
  "batch_mode": true,
  "prp_id": "43.2.1",
  "feature_name": "Command Permission Lists",
  "goal": "Add comprehensive command permission patterns",
  "estimated_hours": 0.42,
  "complexity": "low",
  "files_modified": [".claude/settings.local.json"],
  "dependencies": ["43.1.1"],
  "implementation_steps": [
    "Remove GitButler pattern",
    "Add 35 auto-allow patterns",
    "Add 14 ask-first patterns"
  ],
  "validation_gates": [
    "JSON syntax validates",
    "72 Bash patterns present"
  ],
  "stage": "stage-2-parallel",
  "execution_order": 1,
  "merge_order": 4,
  "conflict_potential": "MEDIUM",
  "conflict_notes": "Shared file with PRP-43.1.1",
  "worktree_path": "../ctx-eng-plus-prp-43-2-1",
  "branch_name": "prp-43-2-1-command-permissions",
  "create_linear_issue": true,
  "plan_context": "Part of tool lockdown initiative"
}
```

**Output Format**: JSON report for coordinator
```json
{
  "prp_id": "43.2.1",
  "status": "SUCCESS",
  "file_path": "PRPs/feature-requests/PRP-43.2.1-command-permissions.md",
  "linear_issue": "CTX-123",
  "linear_url": "https://linear.app/...",
  "execution_time_seconds": 45,
  "errors": []
}
```

**Heartbeat Protocol**: Writes progress to `.tmp/batch-gen/PRP-{prp_id}.status` every 10-15 seconds
```json
{
  "prp_id": "43.2.1",
  "status": "WRITING",
  "progress": 60,
  "timestamp": 1730000000,
  "current_step": "Generating Implementation Steps section"
}
```

**Status Values**: `STARTING`, `PARSING`, `RESEARCHING`, `WRITING`, `LINEAR`, `COMPLETE`, `FAILED`

## What It Does

### Solo Mode Workflow

1. **Parses INITIAL.md structure**:
   - Extracts FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS sections
   - Validates required sections present (FEATURE and EXAMPLES are mandatory)

2. **Proposes clean code**:
   - Follows project code quality standards (50-line functions, 500-line files)
   - Applies KISS principle (simple solutions, minimal dependencies)
   - Ensures no fishy fallbacks or silent error masking
   - All mocks marked with FIXME comments in production code
   - Includes actionable error messages with troubleshooting guidance

3. **Researches codebase** (via Serena MCP):
   - Searches for similar patterns using keywords
   - Analyzes symbol structure and relationships
   - Infers test framework (pytest/unittest/jest)
   - Identifies architectural patterns

3. **Fetches documentation** (via Context7 MCP):
   - Resolves library names to Context7 IDs
   - Fetches relevant library documentation
   - Extracts topics from feature description
   - Includes external documentation links

4. **Generates complete PRP**:
   - Synthesizes 6-section PRP structure (TL;DR, Context, Implementation Steps, Validation Gates, Testing Strategy, Rollout Plan)
   - Creates YAML header with metadata
   - Auto-generates next PRP ID (PRP-N+1)
   - Validates completeness (ensures all required sections present)

5. **Creates/Updates Linear issue**:
   - **Without --join-prp**: Creates new Linear issue with project defaults (from `.ce/linear-defaults.yml`)
   - **With --join-prp**: Updates existing PRP's Linear issue with new PRP information
   - Updates PRP YAML header with `issue: {ISSUE-ID}`

6. **Outputs to**: `PRPs/feature-requests/PRP-{id}-{feature-slug}.md`

### Batch Mode Workflow

**Used by `/batch-gen-prp` coordinator for parallel PRP generation**

1. **Parse JSON input** from prompt:
   - Extract `prp_id`, `feature_name`, `goal`, metadata
   - No INITIAL.md file parsing needed

2. **Write heartbeat**: `.tmp/batch-gen/PRP-{prp_id}.status`
   ```json
   {"status": "STARTING", "progress": 0, "timestamp": now()}
   ```

3. **Optional: Research codebase** (if needed for context):
   - Use Serena MCP for symbol lookup
   - Lightweight research (< 30 seconds)
   - Update heartbeat: `{"status": "RESEARCHING", "progress": 20}`

4. **Generate PRP file**:
   - Build YAML header with provided metadata
   - Create 6-section structure using `implementation_steps` and `validation_gates` from input
   - Synthesize TL;DR, Context, Testing Strategy, Rollout Plan sections
   - Write to: `PRPs/feature-requests/PRP-{prp_id}-{slug}.md`
   - Update heartbeat: `{"status": "WRITING", "progress": 60}`

5. **Create Linear issue** (if `create_linear_issue: true`):
   - Use Linear MCP: `linear_create_issue`
   - Title: `PRP-{prp_id}: {feature_name}`
   - Description: Link to PRP file + plan context
   - Update PRP YAML header with `issue: {ISSUE-ID}`
   - Update heartbeat: `{"status": "LINEAR", "progress": 90}`

6. **Return JSON report**:
   ```json
   {
     "prp_id": "43.2.1",
     "status": "SUCCESS",
     "file_path": "PRPs/feature-requests/PRP-43.2.1-feature.md",
     "linear_issue": "CTX-123",
     "linear_url": "https://linear.app/...",
     "execution_time_seconds": 45,
     "errors": []
   }
   ```
   - Update heartbeat: `{"status": "COMPLETE", "progress": 100}`

**Error Handling**:
- On error, write final heartbeat: `{"status": "FAILED", "progress": XX, "error": "message"}`
- Return JSON report with `"status": "FAILED"` and `"errors": ["error details"]`
- Parent coordinator continues with other PRPs (graceful degradation)

**Heartbeat Timing**:
- Write heartbeat every 10-15 seconds during long operations
- Always write on status transitions (STARTING → PARSING → etc.)
- Final heartbeat on COMPLETE or FAILED

## INITIAL.md Structure

Your INITIAL.md must follow this structure:

```markdown
# Feature: <Feature Name>

## FEATURE
<What to build - user story, acceptance criteria>

## EXAMPLES
<Similar code patterns from codebase, inline code blocks, or file references>

## DOCUMENTATION
<Library docs, API references, external resources>

## OTHER CONSIDERATIONS
<Gotchas, constraints, security concerns, edge cases>
```

**Required sections**: FEATURE, EXAMPLES
**Optional sections**: DOCUMENTATION, OTHER CONSIDERATIONS

## Example

```bash
# Create INITIAL.md
cat > feature-requests/user-auth/INITIAL.md << 'EOF'
# Feature: User Authentication System

## FEATURE
Build JWT-based user authentication with:
- User registration with email/password
- Login with JWT token generation
- Token refresh mechanism

**Acceptance Criteria:**
1. Users can register with valid email and password
2. Login returns JWT access token and refresh token
3. Protected endpoints validate JWT tokens

## EXAMPLES
```python
async def authenticate_user(email: str, password: str) -> dict:
    user = await db.users.find_one({"email": email})
    if not user or not verify_password(password, user["password_hash"]):
        raise AuthenticationError("Invalid credentials")

    access_token = create_jwt(user["id"], expires_in=3600)
    return {"access_token": access_token}
```

See src/oauth.py:42-67 for similar async authentication pattern

## DOCUMENTATION
- [JWT Best Practices](https://jwt.io/introduction)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- "pytest" for testing
- "bcrypt" for password hashing

## OTHER CONSIDERATIONS
**Security:**
- Hash passwords with bcrypt (cost factor 12)
- Rate limiting on login endpoint (5 attempts per 15 min)
EOF

# Generate PRP
cd tools
uv run ce prp generate feature-requests/user-auth/INITIAL.md

# Output: PRPs/feature-requests/PRP-6-user-authentication-system.md
```

## CLI Command

```bash
# Basic usage (creates new PRP + Linear issue)
cd tools
uv run ce prp generate <path-to-initial.md>

# Join existing PRP's Linear issue
uv run ce prp generate <path-to-initial.md> --join-prp 12
uv run ce prp generate <path-to-initial.md> --join-prp PRP-12
uv run ce prp generate <path-to-initial.md> --join-prp PRPs/executed/PRP-12-feature.md

# Custom output directory
uv run ce prp generate <path-to-initial.md> -o /custom/path

# JSON output (for scripting)
uv run ce prp generate <path-to-initial.md> --json

# Combined options
uv run ce prp generate <path-to-initial.md> --join-prp 12 --json
```

**Use Cases for --join-prp**:
- **Related features**: Multiple PRPs implementing parts of same initiative
- **Incremental work**: Breaking large PRP into smaller chunks
- **Follow-up work**: Additional PRP for same feature area

**Example workflow**:
```bash
# Create first PRP for auth system
uv run ce prp generate auth-part1.md
# Output: PRP-10 created, Linear issue BLA-25 created

# Create second PRP, join same issue
uv run ce prp generate auth-part2.md --join-prp 10
# Output: PRP-11 created, BLA-25 updated with PRP-11 info
```

## Output Structure

The generated PRP will have:

```markdown
---
prp_id: TBD
feature_name: User Authentication System
status: pending
created: 2025-10-13T00:00:00Z
updated: 2025-10-13T00:00:00Z
complexity: medium
estimated_hours: 3-5
dependencies: JWT Best Practices, FastAPI Security, pytest
---

# User Authentication System

## 1. TL;DR
**Objective**: ...
**What**: ...
**Why**: ...
**Effort**: ...
**Dependencies**: ...

## 2. Context
### Background
...
### Constraints and Considerations
...
### Documentation References
...

## 3. Implementation Steps
### Phase 1: Setup and Research (30 min)
...
### Phase 2: Core Implementation (2-3 hours)
...
### Phase 3: Testing and Validation (1-2 hours)
...

## 4. Validation Gates
### Gate 1: Unit Tests Pass
**Command**: `uv run pytest tests/unit/ -v`
...

## 5. Testing Strategy
### Test Framework
pytest
### Test Command
```bash
uv run pytest tests/ -v
```
...

## 6. Rollout Plan
### Phase 1: Development
...
### Phase 2: Review
...
### Phase 3: Deployment
...

---

## Research Findings
### Serena Codebase Analysis
...
### Documentation Sources
...
```

## Graceful Degradation

The tool works even if MCP servers are unavailable:
- **Without Serena**: No codebase research, but PRP still generated with user-provided examples
- **Without Context7**: No library documentation fetched, but external links preserved
- **Without Sequential Thinking**: Heuristic-based topic extraction used

## Code Quality Standards Applied

All generated implementations follow:
- **Function limits**: Target 50 lines max per function
- **File limits**: Target 500 lines max per file
- **KISS principle**: Simple solutions first, clear code over clever code
- **Error handling**: Fast failure with actionable troubleshooting messages
- **No silent failures**: Exceptions bubble up, never swallowed
- **Real functionality**: No hardcoded success messages or fake results
- **Naming conventions**: Business-focused (no version numbers or placeholders)

## Tips

1. **Be specific in FEATURE section**: Include clear acceptance criteria
2. **Provide relevant EXAMPLES**: Reference similar code in your codebase
3. **Link to DOCUMENTATION**: Include library docs and external resources
4. **Note OTHER CONSIDERATIONS**: Security concerns, edge cases, constraints
5. **Code quality alignment**: Generated code will follow project standards - review for consistency

## Haiku-Ready PRP Checklist

Before executing a generated PRP, verify it's optimized for Claude 4.5 Haiku execution:

- [ ] **Goal**: Exact end state described, not vague improvement
- [ ] **Output**: File paths and line numbers specified
- [ ] **Limits**: Scope boundaries explicit (what's IN/OUT)
- [ ] **Data**: All required context inline in PRP (no external references)
- [ ] **Evaluation**: Validation gates are copy-paste bash commands
- [ ] **Decisions**: All architectural choices made (Haiku executes, doesn't decide)
- [ ] **Code Snippets**: Before/after code provided for major changes
- [ ] **No Vague Language**: Check for "appropriate", "suitable", "handle appropriately"

**Reference**: See [PRP-23: Haiku-Optimized PRP Guidelines](../../PRPs/feature-requests/PRP-23-haiku-optimized-prp-guidelines.md) for detailed patterns.

## Next Steps After Generation

1. Review generated PRP for completeness
2. Fill in TBD fields (prp_id will be auto-assigned on execution)
3. Adjust estimated hours if needed
4. **Check Haiku-Ready checklist above**
5. Execute PRP using `/execute-prp <prp-file>`

## Implementation Details

- **Module**: `tools/ce/generate.py`
- **Tests**: `tools/tests/test_generate.py` (24 tests)
- **PRP Reference**: `PRPs/feature-requests/PRP-3-command-automation.md`
