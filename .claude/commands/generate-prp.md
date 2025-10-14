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

2. **Researches codebase** (via Serena MCP):
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

## Tips

1. **Be specific in FEATURE section**: Include clear acceptance criteria
2. **Provide relevant EXAMPLES**: Reference similar code in your codebase
3. **Link to DOCUMENTATION**: Include library docs and external resources
4. **Note OTHER CONSIDERATIONS**: Security concerns, edge cases, constraints

## Next Steps After Generation

1. Review generated PRP for completeness
2. Fill in TBD fields (prp_id will be auto-assigned on execution)
3. Adjust estimated hours if needed
4. Execute PRP using `/execute-prp <prp-file>`

## Implementation Details

- **Module**: `tools/ce/generate.py`
- **Tests**: `tools/tests/test_generate.py` (24 tests)
- **PRP Reference**: `PRPs/feature-requests/PRP-3-command-automation.md`
