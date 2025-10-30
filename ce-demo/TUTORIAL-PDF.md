---
title: "Context Engineering: Complete Tutorial"
author: "Based on Cole Medin's Framework"
date: "2025"
geometry: "landscape, margin=0.5in"
fontsize: 10pt
columns: 2
mainfont: "Helvetica"
sansfont: "Helvetica"
monofont: "Menlo"
fontfamily: helvet
header-includes:
  - \usepackage{fancyhdr}
  - \usepackage{helvet}
  - \renewcommand{\familydefault}{\sfdefault}
  - \pagestyle{fancy}
  - \fancyhead[L]{Context Engineering Tutorial}
  - \fancyhead[R]{\thepage}
  - \fancyfoot[C]{github.com/coleam00/context-engineering-intro}
---

# Context Engineering: Complete Tutorial

**Master the art of making AI coding assistants actually work**

**GitHub:** https://github.com/coleam00/context-engineering-intro

---

## 1. Why Context Engineering?

### The Problem with "Vibe Coding"

**Vibe coding** = asking AI to build something without proper context. Success rate: **~20%** on complex tasks.

**Common experience:**
1. ✨ Initial excitement: "AI generated 100 lines in seconds!"
2. 😟 Growing concern: "Doesn't follow our architecture..."
3. 😤 Frustration: "Tests don't pass, uses outdated patterns"
4. 🚫 Abandonment: "I'll just write it myself"

### Prompt Engineering Limitations

**Better but brittle** - Success rate: **~40%**

```
"Create REST API with FastAPI, JWT auth, PostgreSQL,
rate limiting at 100 req/min, error handling, pytest
tests with 80% coverage, PEP 8 style, type hints."
```

**Problems:**
- Brittleness: Change project → prompt breaks
- Not scalable: Can't fit all conventions in prompt
- No memory: Each request starts from scratch
- No validation: No way to verify AI followed rules

### Context Engineering Solution

**Success rate: 85%+**

Build comprehensive information system teaching AI your project:
- **Rules:** CLAUDE.md (conventions + architecture)
- **Examples:** Real code showing "how we do things"
- **Plans:** PRPs breaking down complex tasks
- **Validation:** Built-in checkpoints verifying correctness

**Analogy:**
- Vibe coding: "Make me a sandwich"
- Prompt eng: "Make turkey sandwich with lettuce, tomato, mayo, wheat bread"
- Context eng: Rules + examples + detailed plan + validation gates

---

## 2. Core Philosophy

### Context Over Prompts

**Key insight:** AI failures = **context failures**, not capability failures.

When AI produces poor code:
1. Didn't know project conventions
2. Wasn't given relevant examples
3. Didn't have structured plan
4. Had no way to validate work

### The Three Pillars

**1. Comprehensive Context**
- Document everything AI needs
- Rules, patterns, gotchas, edge cases
- Make implicit knowledge explicit

**2. Structured Guidance**
- Break tasks into ordered steps
- Provide pseudocode + integration points
- Make "how" as clear as "what"

**3. Continuous Validation**
- Verify correctness at every step
- Linting, type checking, tests
- Self-correction loops when checks fail

### Mental Model: Onboarding Senior Dev

When senior dev joins team:
1. **Onboard:** Show codebase structure, conventions, testing
2. **Examples:** "Here's how we built similar features"
3. **Requirements:** User stories, acceptance criteria, edge cases
4. **Validation:** Linting, tests, code review process

Context Engineering does same for AI.

---

## 3. Quick Start (5 Steps)

### Prerequisites
- Claude Code CLI (recommended) or any AI assistant
- Git
- A project to enhance

### Step 1: Clone Template

```bash
git clone https://github.com/coleam00/\
  context-engineering-intro.git my-project
cd my-project
```

### Step 2: Structure

```
my-project/
├── .ce/              # Framework core (don't modify)
├── CLAUDE.md        # YOUR rules (customize!)
├── PRPs/
│   ├── templates/
│   └── executed/    # Completed PRPs
├── examples/        # YOUR code patterns
└── INITIAL.md      # Feature request template
```

### Step 3: Customize CLAUDE.md

```markdown
# My Project - AI Guidelines

## Stack
- Language: TypeScript (strict mode)
- Framework: Next.js 14 (App Router)
- Database: PostgreSQL + Prisma
- Testing: Jest + React Testing Library

## Code Style
- Functional components with hooks
- Prefer const over let, never var
- Always TypeScript types (no any)
- File naming: kebab-case.tsx

## Testing
- Unit tests for all business logic
- Integration tests for API routes
- 80% minimum coverage
- Use describe/it blocks

## Gotchas
- Always use dynamic in route handlers
- Prisma queries need await
- Env vars: NEXT_PUBLIC_ prefix for client
```

### Step 4: Add Examples

```bash
mkdir -p examples/{api,components,tests}
```

Add representative files showing your patterns.

### Step 5: Write Feature Request

```markdown
FEATURE: User profile export endpoint

GET /api/users/{id}/export returns JSON with:
- Basic info (name, email, created date)
- Preferences
- Activity history (last 30 days)

EXAMPLES:
See examples/api/user-endpoint.ts
See examples/tests/api-test.test.ts

DOCUMENTATION:
- Next.js: https://nextjs.org/docs/...
- Our auth: docs/authentication.md

GOTCHAS:
- Respect privacy settings
- Rate limit: 10 req/hour
- Requires auth token
```

### Step 6: Generate + Execute

```bash
/generate-prp INITIAL.md
/execute-prp PRPs/executed/PRP-1-*.md
```

---

## 4. CLAUDE.md Guide

### What to Include

**1. Stack & Tools**
```markdown
## Technology Stack
- Backend: Python 3.11 + FastAPI
- Database: PostgreSQL 15 + SQLAlchemy 2.0
- Testing: pytest + pytest-asyncio
- Linting: Ruff
- Type checking: MyPy (strict)
```

**2. Code Structure**
```markdown
## Project Structure
- app/api/      # Route handlers
- app/models/   # SQLAlchemy models
- app/schemas/  # Pydantic schemas
- app/services/ # Business logic
- tests/        # Mirrors app/ structure

## Naming
- Files: snake_case.py
- Classes: PascalCase
- Functions: snake_case
- Constants: UPPER_SNAKE_CASE
```

**3. Code Style & Patterns**
```markdown
## Style
- Max line: 100 chars
- Type hints for all functions
- Docstrings: Google style
- Prefer async/await over callbacks

## Patterns
- Dependency injection for DB sessions
- Services return domain models
- Controllers handle HTTP only
- Context managers for DB transactions
```

**4. Testing Standards**
```markdown
## Testing
- Unit: Test functions in isolation
- Integration: Test API endpoints E2E
- Fixtures: pytest fixtures in conftest.py
- Coverage: 80% minimum

## Structure
def test_feature_scenario():
    # Given (setup)
    # When (action)
    # Then (assertion)
```

**5. Common Gotchas**
```markdown
## Database
- Use async session methods
- Don't forget await session.commit()
- Relationships need selectinload

## FastAPI
- Path params match function params
- Use Depends(), don't instantiate
- BackgroundTasks for non-blocking

## Testing
- @pytest.mark.asyncio for async
- Rollback after tests
- Use pytest-mock, not unittest.mock
```

**6. Examples**
```markdown
## Reference Examples
- API: examples/api/user_create.py
- Service: examples/services/user_service.py
- Model: examples/models/user.py
- Schema: examples/schemas/user_schema.py
- Unit test: examples/tests/test_user_service.py
```

### Best Practices

**✅ Do:**
- Be specific and concrete
- Include code examples
- Document anti-patterns
- Keep updated
- Clear section headers

**❌ Don't:**
- Write vague guidelines
- Assume AI knows best practices
- Forget edge cases
- Let it get stale

---

## 5. Writing Effective PRPs

### PRP Anatomy

```markdown
# PRP-X: Feature Name

## Goal & Context
- Goal: What to build
- Why: Business value
- What: User-visible behavior
- Success Criteria: Measurable outcomes

## All Needed Context
- External docs
- Current codebase tree
- Desired codebase tree
- Library quirks
- Codebase gotchas

## Implementation Blueprint
- Data models & structures
- Ordered task list
- Pseudocode per task
- Integration points

## Validation Gates
- Level 1: Syntax & Style
- Level 2: Unit Tests
- Level 3: Integration Test

## Final Checklist
- Tests pass
- Linting clean
- Manual testing success
- Error handling
- Logging
- Docs updated

## Anti-Patterns
- Explicit "don't do this" list
```

### Manual vs /generate-prp

**Manual PRPs** (15-30 min)
- Small features
- Copy templates/prp_base.md
- Fill each section

**/generate-prp** (2-5 min + review)
- Complex features
- Write INITIAL.md
- AI generates draft
- Review and refine

**Hybrid (Recommended):**
1. Use /generate-prp for draft
2. Review accuracy
3. Add project-specific details
4. Refine pseudocode

---

## 6. Custom Commands

### /generate-prp

**What it does:** Reads feature request, analyzes codebase, fetches docs, generates comprehensive PRP.

**Usage:**
```bash
/generate-prp INITIAL.md
/generate-prp path/to/feature.md
```

**Process:**
1. Parses feature request
2. Reads CLAUDE.md
3. Analyzes examples/
4. Fetches external docs
5. Generates file trees
6. Creates task list with pseudocode
7. Adds validation gates
8. Writes PRP to PRPs/executed/

### /execute-prp

**What it does:** Implements feature with continuous validation at each step.

**Usage:**
```bash
/execute-prp PRPs/executed/PRP-1-feature.md
```

**Process:**
1. Reads PRP completely
2. For each task:
   - Implements code
   - Runs validation (lint, type check)
   - If fail: reads error, fixes, retries
   - If pass: moves to next task
3. Runs unit tests
4. Runs integration tests
5. Reports results

**Self-correction example:**
```
Task 2: Add service method
  ✓ Code written
  ✓ Lint... ❌ FAILED
    Error: 'result' used before defined
  🔧 Fixing: Moving declaration
  ✓ Lint... ✅ PASSED
  ✓ Type check... ✅ PASSED
```

---

## 7. Validation Patterns

### Three-Level Validation

**Level 1: Syntax & Style**
```bash
# Python
ruff check .
mypy app/

# TypeScript
npm run lint
npm run type-check

# Go
go vet ./...
golangci-lint run
```

**Level 2: Unit Tests**
```bash
# Python
pytest tests/unit/ -v --cov

# TypeScript
npm test -- --coverage

# Go
go test ./... -cover
```

**Level 3: Integration Tests**
```bash
# Start service
npm run dev

# Test endpoints
curl -X POST http://localhost:3000/api/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","email":"test@example.com"}'

# Check logs
tail -f logs/app.log
```

### Test Design

**Unit Test Checklist:**
- ✓ Happy path
- ✓ Edge cases (empty, null, boundaries)
- ✓ Error conditions
- ✓ Clear names (test_feature_scenario)
- ✓ Isolated (no dependencies)

**Integration Test Checklist:**
- ✓ Full user flow
- ✓ HTTP status codes
- ✓ Response body structure
- ✓ Auth/authorization
- ✓ Side effects verification

**Example:**
```python
class TestUserService:
    def test_create_user_happy_path(self, db):
        service = UserService(db)
        data = UserCreate(name="Alice",
                         email="alice@example.com")
        result = service.create_user(data)
        assert result.id is not None
        assert result.name == "Alice"

    def test_create_user_duplicate_email(self, db):
        service = UserService(db)
        data = UserCreate(name="Alice",
                         email="alice@example.com")
        service.create_user(data)

        with pytest.raises(ValueError,
                          match="Email exists"):
            service.create_user(data)

    @pytest.mark.parametrize("name,email", [
        ("", "test@example.com"),
        ("Alice", ""),
        (None, "test@example.com"),
    ])
    def test_create_user_missing_fields(
        self, db, name, email
    ):
        service = UserService(db)
        with pytest.raises(ValueError):
            service.create_user(
                UserCreate(name=name, email=email)
            )
```

---

## 8. Real-World Examples

### Example 1: JWT Authentication

**INITIAL.md:**
```markdown
FEATURE: Add JWT auth to all API endpoints

All /api/ endpoints require valid JWT in
Authorization header. Exclude /api/auth/login
and /api/auth/register.

Token includes: user_id, email, role, exp
Expiration: 24 hours

EXAMPLES:
- examples/middleware/auth-check.ts
- examples/api/protected-route.ts

DOCUMENTATION:
- jose library: npmjs.com/package/jose
- Next.js middleware: nextjs.org/docs/...

GOTCHAS:
- Don't break existing tests
- Log failed auth attempts
- Return 401, not 403
- Verify signature, not just decode
```

**PRP Tasks:**
1. Create JWT utilities (sign/verify)
2. Create auth middleware
3. Add token to test helpers
4. Update all API tests
5. Add auth logging

### Example 2: Database Migration

**INITIAL.md:**
```markdown
FEATURE: Premium subscription tracking

Add subscription_type, start_date, end_date,
stripe_subscription_id, auto_renew to users.

Types: free, premium_monthly, premium_yearly

Business rules:
- Free: end_date is NULL
- Premium: Check current_date < end_date
- Auto-downgrade on expiry (separate PRP)

EXAMPLES:
- examples/models/user.py
- examples/migrations/

DOCUMENTATION:
- SQLAlchemy enums
- Alembic migrations

GOTCHAS:
- Migration reversible
- Default existing users to 'free'
- Index on end_date
- Don't expose stripe_subscription_id
```

**PRP Tasks:**
1. Create Alembic migration
2. Update User model
3. Create SubscriptionService
4. Add GET /api/users/{id}/subscription
5. Add POST (admin only)
6. Update test fixtures

### Example 3: Refactoring

**INITIAL.md:**
```markdown
FEATURE: Refactor to service layer

Current: app/api/users.py (450 lines)
- HTTP + business logic + DB + email

Desired:
- app/api/users.py: HTTP only
- app/services/user_service.py: Logic
- app/repositories/user_repository.py: DB
- app/notifications/email.py: Email

EXAMPLES:
- examples/refactoring/before-after/
- examples/services/product_service.py

GOTCHAS:
- Keep tests passing
- Don't change API responses
- Extract incrementally
- Use dependency injection
```

**PRP Approach:**
1. Create UserRepository
2. Update tests (verify no change)
3. Create UserService
4. Update tests
5. Refactor API handler
6. Remove dead code
7. Run full test suite

---

## 9. Advanced Techniques

### Batch PRP Generation

**Feature plan:**
```markdown
# User Dashboard Overhaul

## Sub-features:
1. Backend API for dashboard data
2. Frontend Dashboard component
3. Real-time WebSocket updates
4. Dashboard customization
5. Export dashboard to PDF

## Dependencies:
- PRP-2 depends on PRP-1
- PRP-3 depends on PRP-2
- PRP-4 and PRP-5 independent
```

**Generate:**
```bash
/generate-prp plan.md --section "Backend API"
/generate-prp plan.md --section "Frontend"
```

### Custom Validation

**In CLAUDE.md:**
```markdown
## Custom Validation

After each PRP:

```bash
# Security
npm audit
bandit -r app/

# Performance
pytest tests/performance/ --benchmark

# Accessibility
npm run a11y-check
```

Treat failures as validation failures.
```

### PRP Templates

**Specialized templates:**
- PRPs/templates/prp-api-endpoint.md
- PRPs/templates/prp-database-migration.md
- PRPs/templates/prp-refactor.md

**Usage:**
```bash
/generate-prp feature.md \
  --template PRPs/templates/prp-api-endpoint.md
```

### Context Versioning

```
.ce/versions/
├── v1-mvp/
├── v2-production/
└── v3-enterprise/
```

**Switch:**
```bash
cp .ce/versions/v2-production/CLAUDE.md ./
```

---

## 10. Troubleshooting

### Issue: AI Ignores CLAUDE.md

**Symptoms:** Code doesn't follow conventions

**Solutions:**
1. **Be specific:**
   - ❌ "Write good tests"
   - ✅ "pytest fixtures, test_ prefix, Given-When-Then"

2. **Add negative examples:**
   ```markdown
   ## Anti-Patterns
   ❌ DON'T use any in TypeScript
   ❌ DON'T mix async/await with .then()
   ✅ DO use specific types
   ✅ DO use consistent async/await
   ```

3. **Reference explicitly:**
   ```markdown
   Task 1: Create endpoint
   Pattern: Follow examples/api/product.ts exactly
   ```

### Issue: Incomplete PRPs

**Symptoms:** Missing sections, sparse pseudocode

**Solutions:**
1. Improve INITIAL.md detail
2. Review/edit before execution
3. Compare to prp_base.md template

### Issue: Validation Loop

**Symptoms:** AI stuck retrying same fix

**Solutions:**
1. Check test correctness
2. Manually break loop
3. Add specific guidance:
   ```markdown
   ## Common pitfall:
   Don't forget await session.commit()
   Without it, test won't see record.
   ```

### Issue: Context Too Large

**Symptoms:** Token limit errors

**Solutions:**
1. **Modularize CLAUDE.md:**
   ```markdown
   See docs/api-guidelines.md
   See docs/testing-guidelines.md
   ```

2. **Prune examples:**
   - Keep 2-3 per pattern
   - Archive old examples

3. **Use focused PRPs:**
   - Break into smaller PRPs
   - Each focuses on one area

### Issue: Wrong Architecture

**Symptoms:** Files in wrong directories

**Solutions:**
1. **Explicit tree in CLAUDE.md:**
   ```markdown
   ## Structure (MUST FOLLOW)
   app/
   ├── api/          # Controllers
   ├── services/     # Business logic
   ├── repositories/ # Database
   └── schemas/      # Pydantic

   Rule: Services import repositories
   Rule: API imports services
   ```

2. **Include tree in PRPs:**
   ```markdown
   ## Current Structure
   ```bash
   tree app/ -L 2
   ```
   ```

---

## 11. Resources

### Official
- **GitHub:** github.com/coleam00/context-engineering-intro
- **Template:** Clone and customize
- **Videos:** [YouTube channel]
- **Docs:** [Wiki]

### Community
- **Discord:** [Server invite]
  - #general, #show-and-tell, #troubleshooting
- **Twitter:** @coleam00
- **Discussions:** github.com/coleam00/.../discussions

### Contributing
1. Improve docs (submit PR)
2. Add examples (share templates)
3. Report issues
4. Share patterns

### Recommended Reading
- "Pragmatic Programmer" - Hunt & Thomas
- "Clean Code" - Martin
- "Domain-Driven Design" - Evans

---

## Conclusion

**Key Takeaways:**

1. **Context > Prompts** - Comprehensive info beats clever wording
2. **Structure Matters** - CLAUDE.md + PRPs + Examples = Success
3. **Validation Critical** - Self-correction catches errors early
4. **Iterative** - Start simple, refine over time

**Your Next Steps:**

1. Clone template
2. Customize CLAUDE.md (1-2 hours)
3. Add 3-5 examples
4. Write first INITIAL.md
5. Run /generate-prp
6. Run /execute-prp
7. Refine based on results

**Remember:**
- First PRP feels slow
- By 5th PRP, you're flying
- By 20th PRP, you'll wonder how you coded without it

**Welcome to Context Engineering.**

---

**Questions?**
- Discord: [Community]
- GitHub: github.com/coleam00/context-engineering-intro/issues
- Twitter: @coleam00

**Share your wins!**
#ContextEngineering on Twitter

---

*Tutorial v1.0 | github.com/coleam00/context-engineering-intro*
§