# Context Engineering: Complete Tutorial

**Master the art of making AI coding assistants actually work**

By Cole Medin (@coleam00)
GitHub: https://github.com/coleam00/context-engineering-intro

---

## Table of Contents

1. [Introduction: Why Context Engineering?](#1-introduction-why-context-engineering)
2. [Core Philosophy](#2-core-philosophy)
3. [Quick Start Guide](#3-quick-start-guide)
4. [CLAUDE.md: Your Project Constitution](#4-claudemd-your-project-constitution)
5. [Writing Effective PRPs](#5-writing-effective-prps)
6. [The Custom Commands](#6-the-custom-commands)
7. [Validation & Testing Patterns](#7-validation--testing-patterns)
8. [Real-World Examples](#8-real-world-examples)
9. [Advanced Techniques](#9-advanced-techniques)
10. [Troubleshooting & Common Issues](#10-troubleshooting--common-issues)
11. [Resources & Community](#11-resources--community)

---

## 1. Introduction: Why Context Engineering?

### The Problem with "Vibe Coding"

If you've used AI coding assistants like Claude, ChatGPT, or GitHub Copilot, you've probably experienced this:

- **Initial excitement:** "This AI just generated 100 lines of code in seconds!"
- **Growing concern:** "Wait, this doesn't follow our architecture..."
- **Frustration:** "The tests don't pass, and it's using outdated patterns."
- **Abandonment:** "I'll just write it myself."

This is **vibe coding**—asking an AI to build something without providing proper context. Success rate on complex tasks? About 20%.

### The Limitations of Prompt Engineering

Next, you discover prompt engineering: crafting detailed, specific prompts.

```
"Create a REST API endpoint using FastAPI with JWT authentication,
PostgreSQL database integration, rate limiting at 100 req/min,
comprehensive error handling, and pytest tests with 80% coverage.
Follow PEP 8 style guidelines and use type hints."
```

Better results—maybe 40% success rate. But there are problems:

1. **Brittleness:** Change one thing in your project, and the prompt breaks
2. **Not scalable:** You can't fit your entire codebase's conventions in a prompt
3. **No memory:** Each request starts from scratch
4. **No validation:** No way to verify the AI followed your guidelines

### Enter Context Engineering

**Context Engineering** solves this by building a *comprehensive information system* that teaches the AI how your project works:

- **Rules:** CLAUDE.md defines your conventions (like a style guide + architecture doc)
- **Examples:** Real code from your project that shows "how we do things here"
- **Plans:** PRPs (Product Requirement Prompts) that break down complex tasks
- **Validation:** Built-in checkpoints to verify correctness at each step

Success rate on complex tasks? **85%+**

The difference:
- Vibe coding: "Please make me a sandwich"
- Prompt engineering: "Please make me a turkey sandwich with lettuce, tomato, mayo on wheat bread"
- Context engineering: "Here's how we make sandwiches (rules), here are examples of sandwiches we've made (patterns), here's a detailed plan for making this specific sandwich (PRP), and here's how to verify it's correct (validation)"

---

## 2. Core Philosophy

### Context Over Prompts

The fundamental insight: **AI failures are usually context failures, not capability failures.**

Modern language models are incredibly capable. When they produce poor code, it's usually because they:
1. Didn't know your project's conventions
2. Weren't given relevant examples to pattern-match
3. Didn't have a structured plan to follow
4. Had no way to validate their work

Context Engineering addresses all four.

### The Three Pillars

**1. Comprehensive Context**
- Document everything the AI needs to know
- Rules, patterns, gotchas, edge cases
- Make implicit knowledge explicit

**2. Structured Guidance**
- Break complex tasks into ordered steps
- Provide pseudocode and integration points
- Make the "how" as clear as the "what"

**3. Continuous Validation**
- Verify correctness at every step
- Linting, type checking, tests
- Self-correction loops when checks fail

### Mental Model: Onboarding a Senior Developer

When a senior developer joins your team, you don't just say "build feature X." You:

1. **Onboard them:** Show them the codebase structure, conventions, testing approach
2. **Provide examples:** "Here's how we built similar features"
3. **Give detailed requirements:** User stories, acceptance criteria, edge cases
4. **Enable validation:** Set up linting, tests, code review process

Context Engineering does the same for AI assistants.

---

## 3. Quick Start Guide

### Prerequisites

- **Claude Code CLI** (recommended) or any AI coding assistant
- **Git** (for version control)
- A project you want to enhance

### Step 1: Clone the Template

```bash
git clone https://github.com/coleam00/context-engineering-intro.git my-project
cd my-project
```

### Step 2: Understand the Structure

```
my-project/
├── .ce/                    # Framework core (don't modify)
│   ├── RULES.md            # Framework rules
│   └── examples/           # Framework examples
├── .claude/                # Claude Code configuration
│   └── commands/           # Custom commands
├── CLAUDE.md              # YOUR project rules (customize this!)
├── PRPs/
│   ├── templates/
│   │   └── prp_base.md    # PRP template
│   └── executed/          # Completed PRPs
├── examples/              # YOUR code patterns (add here!)
└── INITIAL.md            # Feature request template
```

### Step 3: Customize CLAUDE.md

Open `CLAUDE.md` and add your project's conventions:

```markdown
# My Project - AI Coding Guidelines

## Stack
- **Language:** TypeScript (strict mode)
- **Framework:** Next.js 14 (App Router)
- **Database:** PostgreSQL + Prisma ORM
- **Testing:** Jest + React Testing Library

## Code Style
- Use functional components with hooks
- Prefer `const` over `let`, never use `var`
- Always use TypeScript types (no `any`)
- File naming: `kebab-case.tsx`

## Testing Requirements
- Unit tests for all business logic
- Integration tests for API routes
- Minimum 80% coverage
- Use `describe`/`it` blocks, clear test names

## Known Gotchas
- Always use `dynamic` in route handlers (Next.js 14)
- Prisma queries must use `await` (common mistake!)
- Environment variables must be prefixed with `NEXT_PUBLIC_` for client-side

## Example Feature
See examples/api-route-with-auth.ts for authenticated endpoints
```

### Step 4: Add Code Examples

Create `examples/` directory with real code from your project:

```bash
mkdir -p examples/api examples/components examples/tests
```

Add a few representative files:

**examples/api/user-endpoint.ts** (example of your API style)
```typescript
import { NextRequest, NextResponse } from 'next/server';
import { getServerSession } from 'next-auth';
import prisma from '@/lib/prisma';

export const dynamic = 'force-dynamic';

export async function GET(req: NextRequest) {
  const session = await getServerSession();

  if (!session?.user?.id) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const user = await prisma.user.findUnique({
    where: { id: session.user.id },
  });

  return NextResponse.json({ user });
}
```

**examples/tests/api-test.test.ts** (example of your testing style)
```typescript
import { GET } from '@/app/api/users/route';
import { NextRequest } from 'next/server';
import { getServerSession } from 'next-auth';

jest.mock('next-auth');

describe('GET /api/users', () => {
  it('returns 401 when not authenticated', async () => {
    (getServerSession as jest.Mock).mockResolvedValue(null);

    const req = new NextRequest('http://localhost/api/users');
    const res = await GET(req);

    expect(res.status).toBe(401);
  });

  it('returns user data when authenticated', async () => {
    (getServerSession as jest.Mock).mockResolvedValue({
      user: { id: '123', email: 'test@example.com' }
    });

    const req = new NextRequest('http://localhost/api/users');
    const res = await GET(req);
    const data = await res.json();

    expect(res.status).toBe(200);
    expect(data.user).toBeDefined();
  });
});
```

### Step 5: Write Your First Feature Request

Edit `INITIAL.md`:

```markdown
FEATURE: User profile export endpoint

Users should be able to download their complete profile data as JSON.
This should include:
- Basic profile info (name, email, avatar)
- Account settings and preferences
- Activity history (last 90 days)

The endpoint should be:
- GET /api/users/[id]/export
- Authenticated (requires valid session)
- Rate limited (5 requests per hour)

EXAMPLES:
See examples/api/user-endpoint.ts for our API patterns
See examples/tests/api-test.test.ts for our testing approach

DOCUMENTATION:
- Next.js App Router docs: https://nextjs.org/docs/app/building-your-application/routing/route-handlers
- Prisma aggregations: https://www.prisma.io/docs/concepts/components/prisma-client/aggregation-grouping-summarizing

OTHER CONSIDERATIONS:
- Don't forget `export const dynamic = 'force-dynamic'`
- Exclude sensitive fields (passwordHash, private notes)
- Log export requests for audit trail
```

### Step 6: Generate PRP

In Claude Code CLI:

```bash
/generate-prp INITIAL.md
```

Claude will:
1. Read your INITIAL.md
2. Analyze your CLAUDE.md rules
3. Study your examples/
4. Fetch referenced documentation
5. Generate a comprehensive PRP in PRPs/executed/

### Step 7: Execute PRP

```bash
/execute-prp PRPs/executed/PRP-1-user-export.md
```

Claude will:
1. Read the PRP
2. Implement each task in order
3. Run validation after each step
4. Self-correct if checks fail
5. Produce production-ready code

---

## 4. CLAUDE.md: Your Project Constitution

### What Goes in CLAUDE.md?

Think of CLAUDE.md as the "onboarding doc" for AI assistants. Include:

**1. Stack & Tools**
```markdown
## Technology Stack
- Backend: Python 3.11 + FastAPI
- Database: PostgreSQL 15 + SQLAlchemy 2.0
- Testing: pytest + pytest-asyncio
- Linting: Ruff
- Type checking: MyPy (strict mode)
```

**2. Code Structure & Organization**
```markdown
## Project Structure
- `app/api/` - API route handlers
- `app/models/` - SQLAlchemy models
- `app/schemas/` - Pydantic schemas
- `app/services/` - Business logic
- `tests/` - Test suite (mirrors app/ structure)

## Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
```

**3. Code Style & Patterns**
```markdown
## Code Style
- Max line length: 100 characters
- Use type hints for all function signatures
- Docstrings: Google style
- Prefer async/await over callbacks

## Patterns to Follow
- Use dependency injection for database sessions
- Services return domain models, not ORM objects
- Controllers handle HTTP, services handle business logic
- Always use context managers for database transactions
```

**4. Testing Requirements**
```markdown
## Testing Standards
- Unit tests: Test each function in isolation
- Integration tests: Test API endpoints end-to-end
- Fixtures: Use pytest fixtures, defined in conftest.py
- Coverage: Minimum 80% (run: pytest --cov)

## Test Structure
```python
def test_feature_name_scenario():
    # Given (setup)
    user = create_test_user()

    # When (action)
    result = perform_action(user)

    # Then (assertion)
    assert result.success is True
```
```

**5. Common Gotchas**
```markdown
## Known Issues & Gotchas

### Database
- **Always use async session methods** (`execute`, not `execute_sync`)
- **Common mistake:** Forgetting `await session.commit()` after inserts
- **Remember:** Relationships must be explicitly loaded (`selectinload`)

### FastAPI
- **Path parameters:** Must match function parameter names exactly
- **Dependency injection:** Use `Depends()`, don't instantiate directly
- **Background tasks:** Use `BackgroundTasks` for non-blocking operations

### Testing
- **Async tests:** Must use `@pytest.mark.asyncio` decorator
- **Database fixtures:** Always rollback after tests (see conftest.py)
- **Mocking external APIs:** Use `pytest-mock`, not unittest.mock
```

**6. Examples & References**
```markdown
## Reference Examples
- API endpoint: examples/api/user_create.py
- Service layer: examples/services/user_service.py
- Database model: examples/models/user.py
- Pydantic schema: examples/schemas/user_schema.py
- Unit test: examples/tests/test_user_service.py
- Integration test: examples/tests/test_user_api.py
```

### CLAUDE.md Best Practices

**✅ Do:**
- Be specific and concrete
- Include actual code examples (inline or references)
- Document what NOT to do (anti-patterns)
- Keep it updated as your project evolves
- Use clear section headers

**❌ Don't:**
- Write vague guidelines ("write good code")
- Assume the AI knows your stack's best practices
- Forget to document edge cases and gotchas
- Let it get stale (review quarterly)

### Example: Complete CLAUDE.md Template

See `examples/CLAUDE.md.template` in the repo for a comprehensive starting point you can customize.

---

## 5. Writing Effective PRPs

### What is a PRP?

A **PRP (Product Requirement Prompt)** is a detailed implementation blueprint. It's not just a feature description—it's a complete plan that includes:

- **Context:** What exists, what needs to be built, why
- **Implementation steps:** Ordered, specific tasks
- **Code patterns:** Pseudocode showing how to integrate with existing code
- **Validation gates:** Checkpoints to verify correctness
- **Anti-patterns:** What NOT to do

### PRP Anatomy (from prp_base.md)

```markdown
# PRP-X: Feature Name

## Goal & Context

### Goal
[What needs to be built, end state details]

### Why
[Business value, user impact, integration points]

### What
[User-visible behavior, technical requirements]

### Success Criteria
[Measurable outcomes for completion]

## All Needed Context

### External Documentation
- [Library/API docs with specific sections needed]

### Current Codebase Structure
```
[Output of `tree` command showing relevant files]
```

### Desired Codebase Structure
```
[Tree showing new files and their responsibilities]
```

### Library Quirks
[Known issues, version-specific behaviors, gotchas]

### Codebase Gotchas
[Project-specific pitfalls to avoid]

## Implementation Blueprint

### Data Models & Structures
[ORMs, Pydantic schemas, TypeScript interfaces, validators]

### Task List (Ordered)
1. [First task with clear completion criteria]
2. [Second task...]

### Pseudocode Per Task
[For each task: pattern to follow, integration points, error handling]

### Integration Points
[Database migrations, config changes, routing updates, env vars]

## Validation Gates

### Level 1: Syntax & Style
[Linting commands, type checking, formatting]

### Level 2: Unit Tests
[Test requirements, coverage targets, test patterns]

### Level 3: Integration Test
[Manual testing steps, curl commands, expected outputs]

## Final Checklist
- [ ] All tests pass
- [ ] Linting/type checking clean
- [ ] Manual testing successful
- [ ] Error handling comprehensive
- [ ] Logging added
- [ ] Documentation updated

## Anti-Patterns
[Explicit list of things NOT to do, common mistakes]
```

### Writing PRPs Manually vs. /generate-prp

**Option 1: Manual PRPs**
- For small features or when you know exactly what you want
- Copy `PRPs/templates/prp_base.md`
- Fill in each section carefully
- Takes 15-30 minutes for a detailed PRP

**Option 2: /generate-prp Command**
- For complex features or when you want AI assistance
- Write a feature request in INITIAL.md
- Run `/generate-prp INITIAL.md`
- Review and edit the generated PRP
- Takes 2-5 minutes + review time

**Hybrid Approach (Recommended):**
1. Use `/generate-prp` to create first draft
2. Review for accuracy and completeness
3. Add project-specific details AI might have missed
4. Refine pseudocode sections with concrete examples

### PRP Examples

#### Example 1: API Endpoint PRP

```markdown
# PRP-3: User Activity Feed Endpoint

## Goal & Context

### Goal
Create GET /api/users/{id}/activity endpoint that returns paginated user activity feed.

### Why
Users need to see their recent actions (posts, comments, likes) in chronological order.
This feeds into the "My Activity" dashboard page.

### Success Criteria
- Endpoint returns up to 50 activities per page
- Response time < 200ms for typical user (100-500 activities)
- Supports cursor-based pagination
- Properly handles edge cases (no activity, invalid user ID)

## All Needed Context

### Current Codebase Patterns
```
app/api/users/
├── route.ts (GET /api/users - list users)
└── [id]/
    ├── route.ts (GET /api/users/[id] - single user)
    └── activity/
        └── route.ts (← CREATE THIS)
```

### Data Model
User has many Activities:
- Activity table: id, user_id, type, target_id, created_at
- Types: 'post_created', 'comment_added', 'like_given'
- Pagination: Use created_at + id cursor

### External References
- Next.js App Router: https://nextjs.org/docs/app/api-reference/file-conventions/route
- See examples/api/paginated-endpoint.ts for pagination pattern

## Implementation Blueprint

### Task 1: Create Route Handler
File: `app/api/users/[id]/activity/route.ts`

```typescript
export const dynamic = 'force-dynamic';

export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } }
) {
  const { id } = params;
  const { searchParams } = new URL(req.url);
  const cursor = searchParams.get('cursor');
  const limit = Math.min(parseInt(searchParams.get('limit') || '50'), 100);

  // 1. Validate user exists
  // 2. Query activities with cursor
  // 3. Return paginated response with next cursor
}
```

### Task 2: Add Service Method
File: `lib/services/activity-service.ts`

```typescript
export async function getUserActivities(
  userId: string,
  cursor?: string,
  limit: number = 50
): Promise<{ activities: Activity[]; nextCursor?: string }> {
  // Prisma query with cursor pagination
  // Order by created_at DESC, id DESC
  // Return activities + nextCursor if more exist
}
```

### Task 3: Add Tests

**Unit Test:** `tests/services/activity-service.test.ts`
- Test pagination logic
- Test cursor boundary cases
- Test empty results

**Integration Test:** `tests/api/user-activity.test.ts`
- Test authenticated request returns activities
- Test pagination with cursor
- Test 404 for invalid user ID
- Test rate limiting

## Validation Gates

### Lint & Type Check
```bash
npm run lint
npm run type-check
```

### Unit Tests
```bash
npm test -- activity-service.test.ts
```

### Integration Test
```bash
# Start dev server
npm run dev

# Test endpoint
curl http://localhost:3000/api/users/123/activity?limit=10
curl http://localhost:3000/api/users/123/activity?cursor=eyJpZCI6NTB9&limit=10
```

## Anti-Patterns
- ❌ Don't use offset pagination (slow for large datasets)
- ❌ Don't fetch all activities then slice (memory issue)
- ❌ Don't forget to filter by user_id (security!)
- ❌ Don't return sensitive activity types (e.g., 'password_changed')
```

---

## 6. The Custom Commands

### /generate-prp

**What it does:**
Reads your feature request (INITIAL.md), analyzes your codebase, fetches external documentation, and generates a comprehensive PRP.

**Usage:**
```bash
/generate-prp INITIAL.md
/generate-prp path/to/feature-request.md
```

**What happens internally:**
1. Parses your feature request (FEATURE, EXAMPLES, DOCUMENTATION, GOTCHAS)
2. Reads CLAUDE.md to understand project conventions
3. Analyzes examples/ to learn code patterns
4. Fetches external documentation URLs
5. Generates file tree (current & desired state)
6. Creates ordered task list with pseudocode
7. Adds validation gates
8. Writes PRP to PRPs/executed/PRP-{N}-{name}.md

**Pro tips:**
- Reference real files in EXAMPLES section
- Include specific doc URLs, not just "read the docs"
- Be explicit about gotchas and edge cases
- Review the generated PRP before execution

### /execute-prp

**What it does:**
Implements the feature described in the PRP, with continuous validation at each step.

**Usage:**
```bash
/execute-prp PRPs/executed/PRP-1-feature.md
```

**What happens internally:**
1. Reads the PRP completely
2. For each task in Implementation Blueprint:
   - Implements the code
   - Runs validation gates (lint, type check)
   - If validation fails: reads error, fixes, retries
   - If validation passes: moves to next task
3. Runs unit tests after code changes
4. Runs integration tests at the end
5. Reports success or failure with details

**Self-correction in action:**
```
Task 2: Add service method
  ✓ Code written
  ✓ Lint check... ❌ FAILED
    Error: Line 42: 'result' is used before being defined
  🔧 Fixing: Moving declaration before use
  ✓ Lint check... ✅ PASSED
  ✓ Type check... ✅ PASSED
```

**Pro tips:**
- Let it run autonomously—don't interrupt
- If it gets stuck (rare), you can manually fix and re-run
- Check the final output carefully—AI is good but not perfect
- Run your own manual tests as final verification

---

## 7. Validation & Testing Patterns

### Three-Level Validation

**Level 1: Syntax & Style (Automated)**
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

**Level 2: Unit Tests (Automated)**
```bash
# Python
pytest tests/unit/ -v --cov

# TypeScript
npm test -- --coverage

# Go
go test ./... -cover
```

**Level 3: Integration Tests (Semi-automated)**
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

### Designing Effective Tests

**Unit Test Checklist:**
- [ ] Test happy path
- [ ] Test edge cases (empty input, null values, boundary conditions)
- [ ] Test error conditions (invalid input, missing dependencies)
- [ ] Use clear test names (`test_create_user_with_valid_data`)
- [ ] Isolate tests (no dependencies on other tests)

**Integration Test Checklist:**
- [ ] Test full user flow (API → service → database)
- [ ] Verify HTTP status codes
- [ ] Check response body structure
- [ ] Test authentication/authorization
- [ ] Verify side effects (database changes, external API calls)

**Example: Comprehensive Test Suite**

```python
# tests/test_user_service.py

import pytest
from app.services.user_service import UserService
from app.schemas.user import UserCreate

class TestUserService:
    def test_create_user_happy_path(self, db_session):
        """Should create user with valid data"""
        service = UserService(db_session)
        user_data = UserCreate(name="Alice", email="alice@example.com")

        result = service.create_user(user_data)

        assert result.id is not None
        assert result.name == "Alice"
        assert result.email == "alice@example.com"

    def test_create_user_duplicate_email(self, db_session):
        """Should raise error when email already exists"""
        service = UserService(db_session)
        user_data = UserCreate(name="Alice", email="alice@example.com")
        service.create_user(user_data)

        with pytest.raises(ValueError, match="Email already exists"):
            service.create_user(user_data)

    def test_create_user_invalid_email(self, db_session):
        """Should raise error when email format is invalid"""
        service = UserService(db_session)
        user_data = UserCreate(name="Alice", email="not-an-email")

        with pytest.raises(ValueError, match="Invalid email"):
            service.create_user(user_data)

    @pytest.mark.parametrize("name,email", [
        ("", "test@example.com"),  # Empty name
        ("Alice", ""),             # Empty email
        (None, "test@example.com"), # None name
    ])
    def test_create_user_missing_required_fields(self, db_session, name, email):
        """Should raise error when required fields are missing"""
        service = UserService(db_session)

        with pytest.raises(ValueError):
            service.create_user(UserCreate(name=name, email=email))
```

---

## 8. Real-World Examples

### Example 1: Adding Authentication to an API

**Scenario:** Existing REST API needs JWT authentication added to all endpoints.

**INITIAL.md:**
```markdown
FEATURE: Add JWT authentication to all API endpoints

All endpoints under /api/ should require valid JWT token in Authorization header.
Exclude /api/auth/login and /api/auth/register (public endpoints).

Token should include:
- user_id
- email
- role (admin, user)
- exp (expiration)

Token expiration: 24 hours
Refresh token support: Not needed yet (future feature)

EXAMPLES:
See examples/middleware/auth-check.ts for middleware pattern
See examples/api/protected-route.ts for authenticated endpoint

DOCUMENTATION:
- jose library (JWT): https://www.npmjs.com/package/jose
- Next.js middleware: https://nextjs.org/docs/app/building-your-application/routing/middleware

OTHER CONSIDERATIONS:
- Don't break existing tests (add auth tokens to test helpers)
- Log failed auth attempts (security audit)
- Return 401 for missing/invalid tokens, not 403
- Remember to verify token signature, not just decode
```

**Generated PRP** (excerpt):
```markdown
# PRP-5: JWT Authentication for API Endpoints

## Implementation Blueprint

### Task 1: Create JWT Utilities
File: `lib/auth/jwt.ts`

```typescript
import { SignJWT, jwtVerify } from 'jose';

const secret = new TextEncoder().encode(process.env.JWT_SECRET!);

export async function signToken(payload: { userId: string; email: string; role: string }) {
  return await new SignJWT(payload)
    .setProtectedHeader({ alg: 'HS256' })
    .setExpirationTime('24h')
    .setIssuedAt()
    .sign(secret);
}

export async function verifyToken(token: string) {
  const { payload } = await jwtVerify(token, secret);
  return payload as { userId: string; email: string; role: string };
}
```

### Task 2: Create Auth Middleware
File: `middleware.ts`

```typescript
export async function middleware(req: NextRequest) {
  const path = req.nextUrl.pathname;

  // Skip auth for public routes
  if (path.startsWith('/api/auth/')) {
    return NextResponse.next();
  }

  // Verify token for protected routes
  const token = req.headers.get('authorization')?.replace('Bearer ', '');

  if (!token) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const payload = await verifyToken(token);
    // Attach user to request (for downstream handlers)
    const requestHeaders = new Headers(req.headers);
    requestHeaders.set('x-user-id', payload.userId);
    requestHeaders.set('x-user-role', payload.role);

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  } catch (err) {
    console.error('JWT verification failed:', err);
    return NextResponse.json({ error: 'Invalid token' }, { status: 401 });
  }
}

export const config = {
  matcher: '/api/:path*',
};
```

[... rest of PRP with tests, validation, etc.]
```

**Execution Result:**
- JWT utils created with proper signing/verification
- Middleware added with public route exclusion
- All existing endpoints automatically protected
- Tests updated with auth token helpers
- Failed auth attempts logged to audit trail

---

### Example 2: Database Migration for New Feature

**Scenario:** Adding "premium subscription" feature to existing user system.

**INITIAL.md:**
```markdown
FEATURE: Premium subscription tracking for users

Add database schema and API for tracking user subscription status.

Subscription types:
- free (default)
- premium_monthly ($9.99/mo)
- premium_yearly ($99/year)

Data needed:
- subscription_type (enum)
- subscription_start_date
- subscription_end_date
- stripe_subscription_id (for payment tracking)
- auto_renew (boolean)

Business rules:
- Free users: subscription_end_date is NULL
- Premium users: Check if current date < end_date (is_active)
- Expired subscriptions: Auto-downgrade to free (cron job, separate PRP)

EXAMPLES:
See examples/models/user.py for SQLAlchemy model pattern
See examples/migrations/ for Alembic migration pattern
See examples/api/subscription-check.py for checking status

DOCUMENTATION:
- SQLAlchemy enums: https://docs.sqlalchemy.org/en/20/core/type_basics.html#sqlalchemy.types.Enum
- Alembic migrations: https://alembic.sqlalchemy.org/en/latest/tutorial.html

OTHER CONSIDERATIONS:
- Migration must be reversible (downgrade)
- Default all existing users to 'free' subscription
- Add database index on subscription_end_date (for cron job queries)
- Don't expose stripe_subscription_id in API responses (internal only)
```

**Generated PRP Tasks:**
1. Create Alembic migration (add columns, enum, index)
2. Update User SQLAlchemy model
3. Create SubscriptionService with business logic
4. Add API endpoint GET /api/users/{id}/subscription
5. Add API endpoint POST /api/users/{id}/subscription (admin only)
6. Write unit tests for SubscriptionService
7. Write integration tests for API endpoints
8. Update existing user fixtures in tests

**Key PRP Details:**
- Migration includes both upgrade and downgrade
- Enum type properly defined in PostgreSQL
- Index added for efficient cron queries
- Service layer handles "is_active" logic (not in model)
- API endpoint uses Pydantic schema to exclude stripe_subscription_id

---

### Example 3: Refactoring Legacy Code

**Scenario:** Monolithic API handler needs to be split into service layer + controller.

**INITIAL.md:**
```markdown
FEATURE: Refactor user management into service layer

Current problem:
File: app/api/users.py (450 lines, does everything)
- HTTP handling
- Business logic
- Database queries
- Email sending
- Logging

Desired architecture:
- app/api/users.py: HTTP layer only (parse request, call service, return response)
- app/services/user_service.py: Business logic
- app/repositories/user_repository.py: Database queries
- app/notifications/email.py: Email sending (separate)

EXAMPLES:
See examples/refactoring/before-after/ for similar refactor
See examples/services/product_service.py for service pattern

DOCUMENTATION:
N/A (internal refactoring)

OTHER CONSIDERATIONS:
- Keep existing tests passing during refactor (change implementation, not interface)
- Do NOT change API response format (breaking change)
- Extract in small steps: repository first, then service, then split API
- Use dependency injection for testability
```

**Generated PRP Approach:**
1. Create UserRepository with database methods
2. Update tests to use repository (verify no behavior change)
3. Create UserService with business logic
4. Update tests to use service
5. Refactor API handler to call service
6. Remove dead code from original file
7. Run full test suite (ensure no regressions)

**Why Context Engineering Helps Here:**
- AI understands your architecture from CLAUDE.md and examples
- PRP breaks scary refactor into safe, incremental steps
- Validation at each step ensures nothing breaks
- Examples show the "after" state clearly

---

## 9. Advanced Techniques

### Technique 1: Batch PRP Generation

For large features that need multiple related PRPs:

**Create a feature plan:**
```markdown
# Feature: User Dashboard Overhaul

## Sub-features (PRPs needed):
1. Backend API for dashboard data aggregation
2. Frontend Dashboard component with charts
3. Real-time WebSocket updates
4. Dashboard customization settings
5. Export dashboard to PDF

## Dependencies:
- PRP-2 depends on PRP-1 (needs API)
- PRP-3 depends on PRP-2 (needs frontend)
- PRP-4 and PRP-5 are independent
```

**Generate PRPs in order:**
```bash
/generate-prp feature-plan.md --section "Backend API"
/generate-prp feature-plan.md --section "Frontend Dashboard"
# ... etc
```

---

### Technique 2: Custom Validation Rules

Add project-specific validation to PRPs:

**In CLAUDE.md:**
```markdown
## Custom Validation

After each PRP execution, run:

```bash
# Security scan
npm audit
bandit -r app/  # Python security linter

# Performance check
pytest tests/performance/ --benchmark

# Accessibility check (frontend)
npm run a11y-check
```

If any fail, treat as validation failure and fix before continuing.
```

---

### Technique 3: PRP Templates for Common Tasks

Create specialized PRP templates:

**PRPs/templates/prp-api-endpoint.md** (for REST endpoints)
**PRPs/templates/prp-database-migration.md** (for schema changes)
**PRPs/templates/prp-refactor.md** (for refactoring)

Use as starting point for `/generate-prp`:
```bash
/generate-prp feature.md --template PRPs/templates/prp-api-endpoint.md
```

---

### Technique 4: Context Versioning

As your project evolves, version your context files:

```
.ce/versions/
├── v1-mvp/
│   ├── CLAUDE.md
│   └── examples/
├── v2-production/
│   ├── CLAUDE.md
│   └── examples/
└── v3-enterprise/
    ├── CLAUDE.md
    └── examples/
```

Switch contexts when working on different versions:
```bash
cp .ce/versions/v2-production/CLAUDE.md ./CLAUDE.md
```

---

## 10. Troubleshooting & Common Issues

### Issue 1: AI Ignores CLAUDE.md Rules

**Symptoms:**
- Generated code doesn't follow conventions
- Tests use wrong patterns
- Style is inconsistent

**Solutions:**
1. **Check CLAUDE.md specificity:** Vague rules → vague results
   - ❌ Bad: "Write good tests"
   - ✅ Good: "Use pytest fixtures, test_ prefix, Given-When-Then structure"

2. **Add negative examples:** Show what NOT to do
   ```markdown
   ## Anti-Patterns
   ❌ DON'T use `any` type in TypeScript
   ❌ DON'T mix async/await with .then() chains
   ✅ DO use specific types
   ✅ DO use consistent async/await
   ```

3. **Reference examples explicitly in PRPs:**
   ```markdown
   ## Implementation Blueprint
   Task 1: Create user endpoint
   Pattern: Follow examples/api/product-endpoint.ts exactly
   ```

---

### Issue 2: /generate-prp Produces Incomplete PRPs

**Symptoms:**
- Missing sections (no validation gates, sparse pseudocode)
- Doesn't reference your examples
- Generic advice instead of specific guidance

**Solutions:**
1. **Improve INITIAL.md detail:** More context → better PRP
   - Include specific examples to reference
   - Link to relevant docs (not just "read FastAPI docs")
   - List gotchas explicitly

2. **Review and edit generated PRP before execution:**
   - Add missing pseudocode sections
   - Clarify integration points
   - Add validation commands

3. **Use PRP template as guide:** Compare generated PRP to `prp_base.md` template

---

### Issue 3: /execute-prp Gets Stuck in Validation Loop

**Symptoms:**
- AI fixes error, lint passes, but test fails
- Retries same fix multiple times
- Eventually gives up

**Solutions:**
1. **Check test quality:** Is the failing test correct?
   - Review test expectations
   - Verify fixtures and mocks

2. **Manually break the loop:**
   - Pause execution
   - Fix the issue yourself
   - Resume with `/execute-prp --continue`

3. **Improve PRP pseudocode:** Give more specific guidance
   ```markdown
   ## Common pitfall:
   Don't forget to await session.commit() after database insert.
   Without this, the test won't see the new record.
   ```

---

### Issue 4: Context Grows Too Large

**Symptoms:**
- Token limit errors
- Slow response times
- AI "forgets" earlier context

**Solutions:**
1. **Modularize CLAUDE.md:**
   ```markdown
   # CLAUDE.md
   For detailed guidelines, see:
   - docs/api-guidelines.md
   - docs/testing-guidelines.md
   - docs/database-guidelines.md
   ```

2. **Prune examples/ directory:**
   - Keep 2-3 examples per pattern
   - Archive old/obsolete examples

3. **Use focused PRPs:**
   - Break large features into multiple smaller PRPs
   - Each PRP focuses on one area

---

### Issue 5: Generated Code Doesn't Match Project Architecture

**Symptoms:**
- Files created in wrong directories
- Imports use incorrect paths
- Doesn't follow project structure

**Solutions:**
1. **Add explicit file tree to CLAUDE.md:**
   ```markdown
   ## Project Structure (MUST FOLLOW)
   ```
   app/
   ├── api/              # API route handlers (controllers)
   │   └── v1/           # API version 1
   ├── services/         # Business logic
   ├── repositories/     # Database access
   ├── models/           # SQLAlchemy models
   └── schemas/          # Pydantic schemas
   ```

   **Rule:** Services import from repositories, not models directly.
   **Rule:** API handlers import from services, not repositories.
   ```

2. **Include tree output in PRPs:**
   ```markdown
   ## Current Structure
   ```bash
   tree app/ -L 2
   ```
   [output here]
   ```

---

## 11. Resources & Community

### Official Resources

- **GitHub Repository:** https://github.com/coleam00/context-engineering-intro
- **Template (Start Here):** Clone the repo and customize
- **Video Tutorials:** [YouTube channel link]
- **Documentation:** [Wiki link]

### Community

- **Discord:** [Community server invite]
  - #general - Discussions and questions
  - #show-and-tell - Share your PRPs and results
  - #troubleshooting - Get help

- **Twitter:** [@coleam00](https://twitter.com/coleam00)
  - Follow for updates and tips

- **GitHub Discussions:** https://github.com/coleam00/context-engineering-intro/discussions
  - Feature requests
  - Show and tell
  - Q&A

### Contributing

Context Engineering is open-source. Contributions welcome:

1. **Improve documentation:** Found something confusing? Submit a PR
2. **Add examples:** Share your project's CLAUDE.md and PRP templates
3. **Report issues:** Found a bug in the commands? Open an issue
4. **Share patterns:** Discovered a great technique? Write it up!

### Additional Learning

**Recommended Reading:**
- "The Pragmatic Programmer" - Andy Hunt & Dave Thomas
- "Clean Code" - Robert C. Martin
- "Domain-Driven Design" - Eric Evans

**Related Concepts:**
- **Prompt Engineering:** Crafting effective prompts (complementary to Context Engineering)
- **AI Pair Programming:** Using AI as a collaborative partner (vs autonomous agent)
- **Infrastructure as Code:** Similar philosophy of "codifying knowledge"

---

## Conclusion

Context Engineering transforms AI coding assistants from unreliable toys into production-ready collaborators.

**Key Takeaways:**

1. **Context > Prompts:** Comprehensive information beats clever wording
2. **Structure Matters:** CLAUDE.md + PRPs + Examples = Success
3. **Validation is Critical:** Self-correction loops catch errors early
4. **Iterative Improvement:** Start simple, refine your context over time

**Your Next Steps:**

1. Clone the template repo
2. Customize CLAUDE.md for your project (1-2 hours)
3. Add 3-5 code examples from your codebase
4. Write your first feature request (INITIAL.md)
5. Run `/generate-prp` and review the result
6. Run `/execute-prp` and watch it work
7. Refine your context based on results

**Remember:**
- First PRP will feel slow (learning curve)
- By the 5th PRP, you'll be flying
- By the 20th PRP, you'll wonder how you ever coded without it

Welcome to Context Engineering. Let's build something great.

---

**Questions? Feedback?**
- Discord: [Community server]
- GitHub Issues: https://github.com/coleam00/context-engineering-intro/issues
- Twitter: @coleam00

**Share your success stories!**
Tag #ContextEngineering on Twitter to show what you've built.

---

*Tutorial version 1.0*
*Last updated: May 2024*
*Maintained by Cole Medin and contributors*
