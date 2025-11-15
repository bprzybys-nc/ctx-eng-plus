# /generate-prp - Generate PRP from INITIAL.md

Automates PRP (Product Requirements Prompt) generation from INITIAL.md with comprehensive codebase research, documentation fetching, and context synthesis.

## Usage

```
/generate-prp <initial-md-path>                        # Creates new PRP + Linear issue
/generate-prp <initial-md-path> --join-prp <prp-ref>  # Joins existing PRP's Linear issue
```

**PRP Reference Formats**:
- Number: `--join-prp 12` (searches for PRP-12)
- ID: `--join-prp PRP-12`
- File path: `--join-prp PRPs/executed/PRP-12-feature.md`

## What It Does

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

5. **Runs L1 validation with timeout and retry** (30s max):
   - Lints markdown (markdownlint: MD031, MD032, etc.)
   - Auto-fixes formatting issues (max 3 attempts, 10s timeout each)
   - Detects infinite loops (abort if same error repeats)
   - Update heartbeat every 5s during linting (batch mode)
   - **Graceful degradation**: Output PRP with warning if linting fails
   - **Note**: This is markdown-specific L1, not code linting

6. **Creates/Updates Linear issue**:
   - **Without --join-prp**: Creates new Linear issue with project defaults (from `.ce/linear-defaults.yml`)
   - **With --join-prp**: Updates existing PRP's Linear issue with new PRP information
   - Updates PRP YAML header with `issue: {ISSUE-ID}`

7. **Outputs to**: `PRPs/feature-requests/PRP-{id}-{feature-slug}.md`

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

## Linting Workflow (L1 Markdown Validation)

**Responsibility Split**:

- **Python module** (tools/ce/generate.py): Writes PRP file, does NOT run linting
- **Claude Code interpreter**: Runs markdownlint after file is written (optional, graceful degradation)

When Claude Code interprets this command, implement the following linting logic:

**Step 1: Write PRP file first**
```python
# Always write PRP content to file before linting
with open(prp_file_path, 'w') as f:
    f.write(prp_content)
```

**Step 2: Run markdownlint with retry and timeout**
```python
import subprocess
import time
import json
from pathlib import Path

def write_heartbeat(prp_id, status, progress, current_step):
    """Write heartbeat file for monitoring progress

    Args:
        prp_id: PRP ID (e.g., "31" or "30.2.1")
        status: Current status (e.g., "LINTING", "WRITING")
        progress: Progress percentage (0-100)
        current_step: Description of current step
    """
    heartbeat_dir = Path("tmp/batch-gen")
    heartbeat_dir.mkdir(parents=True, exist_ok=True)

    heartbeat_file = heartbeat_dir / f"PRP-{prp_id}.status"
    heartbeat_data = {
        "prp_id": str(prp_id),
        "status": status,
        "progress": progress,
        "timestamp": int(time.time()),
        "current_step": current_step
    }

    with open(heartbeat_file, 'w') as f:
        json.dump(heartbeat_data, f, indent=2)

def auto_fix_with_retry(file_path, prp_id=None, max_attempts=3):
    """Auto-fix markdown with retry limit and heartbeat

    Args:
        file_path: Path to markdown file
        prp_id: PRP ID for heartbeat (None for solo mode)
        max_attempts: Max retry attempts (default: 3)

    Returns: (success: bool, attempts: int, errors: list)
    """
    errors = []
    previous_error = None

    for attempt in range(1, max_attempts + 1):
        # Update heartbeat (batch mode only)
        if prp_id:
            write_heartbeat(prp_id, "LINTING", 75,
                          f"Auto-fix attempt {attempt}/{max_attempts}")

        try:
            # Run markdownlint with 10s timeout
            result = subprocess.run(
                ["markdownlint", "--fix", file_path],
                timeout=10,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                # Success: linting passed
                if prp_id:
                    write_heartbeat(prp_id, "LINTING", 80, "Linting complete")
                return (True, attempt, [])

            # Errors found
            current_error = result.stderr.strip()
            errors.append(current_error)

            # Check for infinite loop (same error twice)
            if attempt > 1 and current_error == previous_error:
                if prp_id:
                    write_heartbeat(prp_id, "LINTING", 80,
                                  "Infinite loop detected, continuing anyway")
                return (False, attempt, errors)

            previous_error = current_error

        except subprocess.TimeoutExpired:
            error_msg = f"Timeout on attempt {attempt}"
            errors.append(error_msg)
            if prp_id:
                write_heartbeat(prp_id, "LINTING", 75, error_msg)

        except FileNotFoundError:
            # markdownlint not installed
            if prp_id:
                write_heartbeat(prp_id, "LINTING", 80,
                              "markdownlint not found, skipping")
            return (False, 1, ["markdownlint not installed"])

    # Failed after max attempts
    if prp_id:
        write_heartbeat(prp_id, "LINTING", 80, "Linting failed, continuing anyway")
    return (False, max_attempts, errors)
```

**Step 3: Handle linting result with graceful degradation**
```python
# Try to lint (best effort, don't block on failure)
success, attempts, lint_errors = auto_fix_with_retry(prp_file_path, prp_id)

if not success:
    # Log warning but don't fail
    print(f"⚠️ Warning: Linting failed after {attempts} attempts")
    for error in lint_errors:
        print(f"   {error}")
    print(f"   PRP generated successfully but may have formatting issues")
    # Continue to next step (Linear issue creation)
else:
    print(f"✓ Linting passed after {attempts} attempt(s)")
```

**Step 4: Continue to Linear issue creation**
- Linting failures don't block PRP generation
- PRP file is already written in Step 1
- Proceed to create/update Linear issue

## Solo Mode Heartbeat (Optional)

**Current Status**: NOT implemented for solo /generate-prp (only batch mode has heartbeat)

**Batch Mode**: Heartbeat implemented in /batch-gen-prp (writes tmp/batch-gen/PRP-X.status)

**Solo Mode** (if needed): Could implement similar monitoring at tmp/solo-gen/PRP-X.status

For monitoring solo mode generation progress (if implemented):

1. Create heartbeat directory: `tmp/solo-gen/`
2. Determine next PRP ID: Read existing PRPs, increment by 1
3. Write heartbeat: `tmp/solo-gen/PRP-{next_id}.status`
4. Update every 15s during generation
5. Cleanup on completion (delete heartbeat file)

**Format** (same as batch mode):
```json
{
  "prp_id": "31",
  "status": "WRITING",
  "progress": 60,
  "timestamp": 1730000000,
  "current_step": "Generating Implementation Steps section"
}
```

**Note**: Solo mode heartbeat is optional and not required by `/batch-gen-prp`. Use only if user wants to monitor solo generation progress.

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
