# Command Reference

**Document Version:** 1.0
**Last Updated:** 2025-10-10
**Status:** Production Ready

## Overview

This document provides a comprehensive reference for all commands available in the Context Engineering framework. The framework implements a systematic approach to AI-assisted software development through structured commands, MCP (Model Context Protocol) integrations, and automated workflows.

**Key Capabilities:**

- Structured feature implementation via Product Requirements Plans (PRPs)
- Semantic code understanding through Language Server Protocol integration
- Automated context management and self-healing mechanisms
- Multi-phase development workflows with validation gates
- Technology-agnostic patterns applicable to any software project

**Target Audience:**

- Software engineers implementing Context Engineering workflows
- AI agents executing structured development tasks
- Technical leads evaluating AI-assisted development frameworks
- Development teams seeking systematic code generation approaches

---

## 1. Command Categories Overview

The Context Engineering framework organizes commands into five primary categories:

| Category | Purpose | Command Count | Automation Level |
|----------|---------|---------------|------------------|
| **PRP Commands** | Feature planning and implementation | 7 | Manual trigger, automated execution |
| **Context Management** | Maintain system state and knowledge base | 4 | Automatic with manual override |
| **Development Workflow** | Code quality and debugging | 5 | Manual trigger |
| **MCP Commands** | Low-level tool integration | 33+ | API-level, invoked by higher commands |
| **Macro Features** | Cross-cutting capabilities | 5 | Embedded in command execution |

**Architectural Principles:**

- Commands follow consistent Input → Process → Output → Validation pattern
- Higher-level commands orchestrate lower-level MCP tools
- Automatic triggers reduce manual intervention for maintenance tasks
- All commands produce structured output suitable for logging and monitoring

---

## 2. PRP Commands

### 2.1 Creation Commands

Product Requirements Plans (PRPs) serve as implementation blueprints that bridge high-level requirements and executable code. Creation commands transform feature requests into comprehensive, validated plans.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`/generate-prp`** | `<INITIAL.md>` file path containing feature requirements | (1) Read and parse INITIAL.md content<br>(2) Execute Serena LSP indexing if not initialized<br>(3) Query codebase for related patterns via `find_symbol()`<br>(4) Optional: Retrieve library documentation via Context7<br>(5) Generate structured PRP with validation gates<br>(6) Save to `PRPs/` directory with timestamp | `PRPs/feature-name-YYYY-MM-DD.md` containing:<br>- YAML metadata header<br>- Implementation phases<br>- Validation criteria<br>- Context references<br>- Estimated complexity | **Manual:** User invokes command with INITIAL file<br>**Duration:** 10-15 minutes research phase | `/generate-prp docs/INITIAL-auth-system.md` → Creates `PRPs/auth-system-2025-10-10.md` with OAuth2 implementation plan |
| **`/create-base-prp`** | `<description>` natural language feature request (inline text, no file required) | (1) Parse natural language description<br>(2) Automatic codebase analysis via Serena<br>(3) Extract existing patterns and conventions<br>(4) Generate base PRP structure<br>(5) Populate with gathered context | Base PRP file with:<br>- Core requirements section<br>- Identified dependencies<br>- Initial implementation sketch<br>- Placeholder validation gates | **Manual:** Quick PRP creation without separate requirements document | `/create-base-prp "Add rate limiting to API endpoints using Redis"` → Generates PRP with Redis integration patterns |
| **`/planning-create`** | Project scope document, architecture requirements, stakeholder constraints | (1) Analyze project scope breadth<br>(2) Identify architectural decision points<br>(3) Generate mermaid diagrams for:<br>&nbsp;&nbsp;- System architecture<br>&nbsp;&nbsp;- Data flow<br>&nbsp;&nbsp;- Component interactions<br>(4) Document technology choices with rationale<br>(5) Create implementation roadmap | Planning document with:<br>- Architecture diagrams (mermaid syntax)<br>- Technology stack decisions<br>- Risk assessment<br>- Phased implementation timeline<br>- Resource requirements | **Manual:** For greenfield projects or major system redesigns | `/planning-create` on project scope → Produces architectural planning doc with component diagrams |
| **`/spec-create-adv`** | Complex feature specification with multiple subsystems | (1) Decompose specification into components<br>(2) Multi-phase research:<br>&nbsp;&nbsp;- Phase A: Technical feasibility<br>&nbsp;&nbsp;- Phase B: Integration points<br>&nbsp;&nbsp;- Phase C: Performance considerations<br>(3) Stakeholder requirement mapping<br>(4) Generate detailed specification with acceptance criteria | Advanced specification document:<br>- Multi-component breakdown<br>- API contracts<br>- Performance benchmarks<br>- Security considerations<br>- Rollback procedures | **Manual:** Enterprise-level features requiring formal specification | `/spec-create-adv` for payment processing system → Multi-subsystem specification with compliance requirements |

**PRP Structure (YAML Header Example):**

```yaml
---
title: "Authentication System Implementation"
type: "feature"
complexity: "high"
estimated_duration: "8-12 hours"
dependencies:
  - "Database schema migration"
  - "Redis session store"
validation_gates:
  - "Unit tests pass (>90% coverage)"
  - "Integration tests pass"
  - "Security audit checklist completed"
---
```

---

### 2.2 Execution Commands

Execution commands transform validated PRPs into production-ready implementations through phased, validated workflows.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`/execute-prp`** | `<PRP-file.md>` validated Product Requirements Plan | (1) Parse PRP YAML metadata and phases<br>(2) Create execution checkpoint (git commit)<br>(3) For each phase:<br>&nbsp;&nbsp;- Execute implementation steps<br>&nbsp;&nbsp;- Run validation gate (tests, lint, type-check)<br>&nbsp;&nbsp;- If validation fails: trigger `/heal-errors`<br>&nbsp;&nbsp;- Create phase checkpoint<br>(4) Generate final validation report<br>(5) Create git commit with structured message | Production code artifacts:<br>- Source files (src/)<br>- Test files (tests/)<br>- Documentation updates<br>- Git commit reference<br>- Validation report (JSON) | **Manual:** User triggers after human PRP validation<br>**Modes:**<br>- Interactive: Real-time feedback<br>- Headless: CI/CD integration<br>- Stream-JSON: Monitoring dashboards | `/execute-prp PRPs/auth-system-2025-10-10.md` → Implements OAuth2 with JWT tokens, creates 12 files, 450 lines of code, all tests passing |
| **`/execute-base-prp`** | `<PRP-file>` path to base PRP document | (1) Load base PRP requirements<br>(2) Scan existing codebase patterns via `list_symbols()`<br>(3) Apply pattern matching to maintain consistency<br>(4) Execute implementation with existing conventions<br>(5) Validate against project style guide<br>(6) Integrate with existing test suite | Code integrated with project:<br>- Follows existing naming conventions<br>- Matches architectural patterns<br>- Extends current test structure<br>- Updates relevant documentation | **Manual:** For adding features to established codebases requiring consistency | `/execute-base-prp PRPs/new-endpoint.md` → Adds API endpoint matching existing REST patterns, reuses auth middleware |
| **`/spec-execute`** | Technical specification document (formal spec, not PRP) | (1) Parse specification requirements<br>(2) Extract acceptance criteria<br>(3) Generate implementation plan (auto-PRP)<br>(4) Execute with specification as validation source<br>(5) Map implementation to spec requirements (traceability matrix) | Complete feature with:<br>- Specification compliance report<br>- Requirement traceability matrix<br>- Acceptance test suite<br>- Formal validation sign-off document | **Manual:** For pre-approved specifications requiring formal traceability | `/spec-execute docs/payment-spec-v2.3.pdf` → Implements to exact specification, generates compliance matrix |

**Execution Modes Comparison:**

| Mode | Use Case | Output | Monitoring |
|------|----------|--------|------------|
| **Interactive** | Local development, real-time debugging | Terminal output with progress indicators | Human observation |
| **Headless** | CI/CD pipelines, automated deployments | Exit codes, log files | Pipeline dashboard |
| **Stream-JSON** | Long-running tasks, remote execution | Structured JSON events over stdout | Real-time monitoring tools |

**Validation Loop (Embedded in Execution):**

```
Execute Phase → Run Tests → If FAIL → /heal-errors (max 3 attempts) → Revalidate
                         → If PASS → Checkpoint → Next Phase
```

---

## 3. Context Management Commands

Context management commands maintain system health, synchronize knowledge bases, and prevent degradation over long development sessions.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`/sync-context`** | None (automatic detection) | (1) Detect drift: `git diff --name-only HEAD~5`<br>(2) Re-index changed symbols via Serena:<br>&nbsp;&nbsp;- `list_symbols(changed_file)`<br>&nbsp;&nbsp;- `get_symbol_definition(symbol)`<br>&nbsp;&nbsp;- Update memory store<br>(3) Validate symbol references<br>(4) Prune obsolete memories (files no longer in git tree)<br>(5) Create sync checkpoint with metadata | Synchronization report:<br>- Files reindexed (count + list)<br>- Memories pruned (count + list)<br>- Drift score (0.0-1.0)<br>- Validation status (PASS/FAIL)<br>- Updated memory index | **Automatic:**<br>- Session start (if git diff ≠ 0)<br>- After 10+ file modifications<br>- Before PRP execution<br>**Manual:**<br>- User invokes `/sync-context` | Session with 15 modified files → Reindexes 45 symbols, prunes 8 obsolete memories, drift score 0.12 (LOW) |
| **`/heal-errors`** | Error type (compilation/runtime/test), error message/stack trace | (1) Classify error pattern:<br>&nbsp;&nbsp;- duplicate_import<br>&nbsp;&nbsp;- symbol_not_found<br>&nbsp;&nbsp;- type_mismatch<br>&nbsp;&nbsp;- stale_context<br>(2) Root cause analysis via Sequential Thinking MCP<br>(3) Apply healing strategy:<br>&nbsp;&nbsp;- Deduplicate imports via regex<br>&nbsp;&nbsp;- Fix symbol resolution via `find_symbol()`<br>&nbsp;&nbsp;- Correct type at source (not all usage sites)<br>&nbsp;&nbsp;- Trigger reindex for stale context<br>(4) Incremental validation (max 3 attempts)<br>(5) Create checkpoint on success | Healing report:<br>- Root cause identified<br>- Healing strategy applied<br>- Validation result<br>- Git commit reference (if fixed)<br>- Error pattern stored in memory | **Automatic:**<br>- Embedded in `/execute-prp` validation loop<br>- Triggered on compilation failure<br>**Manual:**<br>- User invokes `/heal-errors --verbose` | Type error "Property 'userId' not found" → Identifies incomplete interface, adds missing property, revalidates successfully |
| **`/prune-context`** | `--age=<days>` (default: 7)<br>`--merge-similar` (boolean)<br>`--target-reduction=<percentage>` (default: 30%) | (1) Inventory all memories with metadata:<br>&nbsp;&nbsp;- Age (days since creation)<br>&nbsp;&nbsp;- Access count (session reads)<br>&nbsp;&nbsp;- Relevance score (LLM-based)<br>(2) Calculate relevance scores via semantic similarity<br>(3) Apply pruning strategy:<br>&nbsp;&nbsp;- **Priority 1 (Keep):** Age < 24h, access > 5, PRP-referenced<br>&nbsp;&nbsp;- **Priority 2 (Compress):** Age 1-7d, access < 2<br>&nbsp;&nbsp;- **Priority 3 (Delete):** Age > 7d, obsolete refs<br>(4) Compress Priority 2 via summarization (Claude Haiku)<br>(5) Merge similar memories (cosine similarity > 0.85)<br>(6) Validate token reduction achieved | Pruning report:<br>- Token reduction (percentage)<br>- Memories deleted (count + list)<br>- Memories compressed (count + list)<br>- Memories merged (count + pairs)<br>- Updated memory index | **Automatic:**<br>- Token usage > 80% of window<br>- Memory count > 100<br>- Session duration > 2 hours<br>- Before PRP execution<br>**Manual:**<br>- User invokes with custom parameters | 120 memories → Deletes 35, compresses 40, merges 10 pairs → 75 memories, 42% token reduction |
| **`/validate-state`** | None (comprehensive scan) | (1) Compilation validation:<br>&nbsp;&nbsp;- `npm run check-all`<br>&nbsp;&nbsp;- Parse exit codes and errors<br>(2) Git state verification:<br>&nbsp;&nbsp;- `git status --porcelain`<br>&nbsp;&nbsp;- `git diff --stat`<br>&nbsp;&nbsp;- Check for large uncommitted diffs<br>(3) Serena index health:<br>&nbsp;&nbsp;- Test known symbols<br>&nbsp;&nbsp;- Verify symbol counts<br>(4) Memory consistency check:<br>&nbsp;&nbsp;- Validate file references<br>&nbsp;&nbsp;- Check memory age/access patterns<br>(5) Context drift detection:<br>&nbsp;&nbsp;- Compare current vs checkpoint symbols<br>&nbsp;&nbsp;- Calculate drift score<br>(6) Test coverage validation:<br>&nbsp;&nbsp;- Run coverage report<br>&nbsp;&nbsp;- Check against thresholds | Health report with scores:<br>- Compilation: PASS/FAIL<br>- Git cleanliness: CLEAN/DIRTY (% uncommitted)<br>- Serena index: HEALTHY/NEEDS_REINDEX<br>- Memory consistency: OK/PRUNING_NEEDED<br>- Context drift: LOW/MEDIUM/HIGH (percentage)<br>- Test coverage: percentage<br>- Recommended actions list | **Automatic:**<br>- Every session start<br>- Every 30 minutes during development<br>- Before PRP execution<br>- After refactoring > 20 files<br>**Manual:**<br>- User invokes `/validate-state` | Health check shows: Compilation PASS, Git 15% uncommitted, Index HEALTHY, Drift LOW (8%), Coverage 87% |

**Context Drift Calculation:**

```
drift_score = (new_symbols + deleted_symbols) / baseline_symbols
- LOW: < 0.15 (15% change)
- MEDIUM: 0.15 - 0.30 (15-30% change)
- HIGH: > 0.30 (30%+ change, triggers auto-sync)
```

---

## 4. Development Workflow Commands

Development workflow commands support code quality, debugging, and Git operations throughout the development lifecycle.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`/prime-core`** | None (auto-discovers project structure) | (1) Locate and parse CLAUDE.md (project rules)<br>(2) Initialize Serena LSP indexing:<br>&nbsp;&nbsp;- Scan all source files<br>&nbsp;&nbsp;- Build symbol index<br>&nbsp;&nbsp;- Extract type definitions<br>(3) Load code examples from `examples/` directory<br>(4) Index PRP templates from `PRPs/templates/`<br>(5) Create session context snapshot | Primed AI context:<br>- Project rules loaded<br>- Codebase indexed (symbol count)<br>- Example patterns indexed<br>- Ready for commands<br>- Session ID generated | **Manual:**<br>- Session initialization<br>- After major codebase changes<br>**Automatic:**<br>- First command invocation (if not primed) | `/prime-core` → Indexed 1,247 symbols from 156 files, loaded 23 patterns, session ready |
| **`/review-general`** | Code section (inline) or file paths (list) | (1) Read specified code<br>(2) Load project standards from CLAUDE.md<br>(3) Analyze against:<br>&nbsp;&nbsp;- Code style conventions<br>&nbsp;&nbsp;- Best practice violations<br>&nbsp;&nbsp;- Security anti-patterns<br>&nbsp;&nbsp;- Performance concerns<br>&nbsp;&nbsp;- Test coverage gaps<br>(4) Generate improvement suggestions with examples<br>(5) Prioritize findings (critical/high/medium/low) | Detailed review report:<br>- Findings by severity<br>- Code snippets with issues highlighted<br>- Suggested fixes with diffs<br>- Best practice references<br>- Refactoring recommendations | **Manual:**<br>- User requests code review<br>- Pre-merge review workflow | `/review-general src/auth/login.ts` → 3 findings: Missing error handling (high), hardcoded config (medium), unused imports (low) |
| **`/review-staged-unstaged`** | None (reads git state automatically) | (1) Execute `git diff --cached` (staged changes)<br>(2) Execute `git diff` (unstaged changes)<br>(3) Combine diffs for comprehensive analysis<br>(4) Review changes against project standards<br>(5) Check for:<br>&nbsp;&nbsp;- Accidental commits (debug code, secrets)<br>&nbsp;&nbsp;- Breaking changes without migration<br>&nbsp;&nbsp;- Test coverage for new code<br>&nbsp;&nbsp;- Documentation updates needed | Change analysis report:<br>- Summary of changes (files, lines)<br>- Issues detected (by severity)<br>- Commit readiness assessment<br>- Pre-commit checklist<br>- Recommendations before committing | **Manual:**<br>- Pre-commit workflow<br>- Before creating pull request | `/review-staged-unstaged` → 5 files staged, 2 unstaged; Recommendation: Add tests for new endpoints before commit |
| **`/refactor-simple`** | `<target>` file path or function name | (1) Read target code<br>(2) Identify refactoring opportunities:<br>&nbsp;&nbsp;- Extract long functions (>50 lines)<br>&nbsp;&nbsp;- Remove code duplication (DRY)<br>&nbsp;&nbsp;- Simplify complex conditionals<br>&nbsp;&nbsp;- Apply SOLID principles<br>(3) Generate refactored version<br>(4) Create tests to verify behavior unchanged<br>(5) Validate tests pass (before and after) | Refactored code:<br>- Original code backup (commented)<br>- Refactored implementation<br>- Behavior-preserving tests<br>- Refactoring rationale document<br>- Validation report (tests pass) | **Manual:**<br>- Technical debt reduction<br>- Code quality improvement sprints | `/refactor-simple src/utils/parser.ts` → Extracted 3 functions, reduced complexity from 45→22, all tests passing |
| **`/debug`** | `<error-description>` natural language or stack trace | (1) Parse error description/stack trace<br>(2) Locate error in codebase via Serena<br>(3) Analyze context:<br>&nbsp;&nbsp;- Related functions via `find_referencing_symbols()`<br>&nbsp;&nbsp;- Variable state at error point<br>&nbsp;&nbsp;- Recent changes via git history<br>(4) Generate hypotheses (Sequential Thinking MCP)<br>(5) Propose debugging steps and fixes | Debugging report:<br>- Root cause analysis<br>- Reproduction steps<br>- Proposed fixes (ranked by likelihood)<br>- Test cases to prevent regression<br>- Related issues (if pattern detected) | **Manual:**<br>- User encounters error<br>- Systematic debugging required | `/debug "NullPointerException in OrderProcessor.calculateTotal()"` → Identified missing null check, proposed fix with test case |
| **`/create-pr`** | Branch name and changes (auto-detected from git) | (1) Execute `git diff main...current-branch`<br>(2) Analyze changes comprehensively<br>(3) Load PRP context if branch linked to PRP<br>(4) Generate PR description:<br>&nbsp;&nbsp;- Summary of changes<br>&nbsp;&nbsp;- Motivation and context<br>&nbsp;&nbsp;- Testing performed<br>&nbsp;&nbsp;- Checklist for reviewers<br>(5) Create PR via GitHub MCP | GitHub/GitLab Pull Request:<br>- Comprehensive PR description<br>- Linked issues (if applicable)<br>- Reviewer suggestions<br>- PR URL<br>- CI/CD pipeline triggered | **Manual:**<br>- Feature branch ready for review<br>- After `/execute-prp` completion | `/create-pr` → Creates PR "Implement OAuth2 authentication" with detailed description, links to issue #123 |

**Review Priority Levels:**

- **Critical:** Security vulnerabilities, data corruption risks, production-breaking changes
- **High:** Logic errors, missing error handling, significant performance issues
- **Medium:** Code style violations, missing documentation, minor performance concerns
- **Low:** Unused imports, formatting inconsistencies, minor refactoring opportunities

---

## 5. MCP Commands

Model Context Protocol (MCP) commands provide low-level tool integration. Higher-level commands orchestrate these tools to accomplish complex workflows.

### 5.1 Serena MCP

Serena provides semantic code understanding through Language Server Protocol (LSP) integration, enabling precise code navigation and manipulation.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`find_symbol`** | `symbol_name` (string), optional `path` (string) | Query LSP index for symbol definition location | Symbol location (file, line, column) + preview of definition | Invoked by higher commands needing symbol context | `find_symbol("UserController")` → Found at `src/controllers/user.ts:15` |
| **`find_referencing_symbols`** | `symbol_name` (string) | Query LSP for all references to specified symbol | List of reference locations (file, line, column) with context | Impact analysis before refactoring | `find_referencing_symbols("authenticateUser")` → 23 references across 8 files |
| **`get_symbol_definition`** | `symbol_name` (string) | Retrieve complete symbol definition with documentation | Full definition including:<br>- Signature<br>- Docstring<br>- Type annotations<br>- Implementation | Understanding symbol details for code generation | `get_symbol_definition("Database.connect")` → Full method signature with connection parameters |
| **`insert_after_symbol`** | `symbol_name` (string), `code_block` (string) | Locate symbol and insert code immediately after its definition | Success confirmation + final file state | Precise code insertion by semantic location | `insert_after_symbol("class User", "  public roles: string[]")` → Added property to User class |
| **`list_symbols`** | `file_path` (string), optional `filter` (string) | Parse file and extract all symbols with hierarchy | Symbol tree structure:<br>- Classes → methods/properties<br>- Functions<br>- Type definitions<br>- Exports | Project structure understanding | `list_symbols("src/models/user.ts")` → Shows User class with 8 methods, 5 properties |
| **`execute_shell_command`** | `command` (string), `working_dir` (string) | Execute shell command in specified directory, capture output | stdout, stderr, exit code | Run tests, linters, build tools | `execute_shell_command("npm test", "/project/root")` → Exit code 0, "All tests passed (45/45)" |
| **`activate_project`** | `project_path` (string) or `project_name` (string) | Initialize LSP server for project, build symbol index | Activation confirmation + symbol count | Session initialization | `activate_project("/Users/dev/my-project")` → Activated, indexed 1,203 symbols |
| **`onboarding`** | None (uses current project context) | Comprehensive project initialization:<br>- Scan all source files<br>- Build complete symbol index<br>- Extract type definitions<br>- Analyze dependencies | Onboarding report:<br>- Files scanned<br>- Symbols indexed<br>- Project metadata | First-time project setup or re-indexing | `onboarding()` → Scanned 156 files, indexed 1,247 symbols, ready for queries |

**Serena Performance Characteristics:**

- Symbol lookup: < 100ms (indexed queries)
- Reference finding: < 500ms (typical codebase < 100k LOC)
- Onboarding: 1-5 minutes (depends on project size)

---

### 5.2 Context7 MCP

Context7 provides up-to-date documentation retrieval for libraries and frameworks, ensuring accurate usage patterns.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`c7_query`** | `project_name` (string), `query_text` (string), `format` ("txt" or "json"), `token_limit` (integer) | (1) Search Context7 documentation index<br>(2) Retrieve relevant sections matching query<br>(3) Format response with code examples<br>(4) Limit output to token budget | Documentation excerpt:<br>- Conceptual explanation<br>- Code examples<br>- API signatures<br>- Version compatibility notes | Invoked during PRP creation for library research | `c7_query("react", "useState hook", "txt", 2000)` → Returns useState documentation with 3 examples |
| **`c7_search`** | `keyword` (string) | Search Context7 index for matching projects/libraries | List of matching projects:<br>- Project title<br>- Project identifier<br>- Short description<br>- Popularity score | Discover available documentation sources | `c7_search("authentication")` → Returns 15 projects: OAuth2, Passport.js, Auth0, NextAuth... |
| **`c7_info`** | `project_name` (string) | Retrieve metadata for specified project | Project metadata:<br>- Source repository URL<br>- Last documentation update<br>- Version coverage<br>- Popularity metrics | Verify documentation freshness before querying | `c7_info("nextjs")` → Repository: vercel/next.js, Last update: 2025-10-05, Versions: 13.x, 14.x |

**Context7 Coverage (Typical):**

- JavaScript/TypeScript: 500+ libraries
- Python: 300+ libraries
- Go: 150+ libraries
- Rust: 100+ libraries

**Query Optimization:**

- Use specific queries: "React useEffect cleanup" (good) vs "React hooks" (too broad)
- Specify version in project_name if critical: "nextjs@14" vs "nextjs"
- Set token_limit conservatively (2000-4000 tokens optimal for focused queries)

---

### 5.3 GitHub MCP

GitHub MCP enables repository automation, issue tracking, and CI/CD integration through GitHub API.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`create_issue`** | `title` (string), `body` (string), `labels` (array), `assignees` (array) | Authenticate with GitHub, create issue via API | Issue URL + issue number | Automated issue creation from error patterns | `create_issue("Bug: Login fails", "Steps to reproduce...", ["bug", "urgent"], ["johndoe"])` → Created issue #456 |
| **`create_pull_request`** | `title` (string), `body` (string), `head_branch` (string), `base_branch` (string) | Validate branches exist, create PR via GitHub API | PR URL + PR number | Automated PR creation after `/execute-prp` | `create_pull_request("Add OAuth2", "Implements OAuth2...", "feature/oauth", "main")` → Created PR #789 |
| **`search_code`** | `query` (string), `repo` (string), `language` (string) | Search GitHub code using advanced search syntax | Code snippet results:<br>- File path<br>- Line numbers<br>- Context (surrounding code) | Find reference implementations | `search_code("function authenticateUser", "myorg/myrepo", "typescript")` → 3 matches with context |
| **`get_file_contents`** | `repo` (string), `path` (string), `ref` (string - branch/tag/commit) | Fetch file contents via GitHub API | File content (decoded) + metadata (size, encoding, SHA) | Fetch reference implementations from other projects | `get_file_contents("facebook/react", "packages/react/src/React.js", "main")` → Returns React.js source |
| **`list_commits`** | `repo` (string), `sha` (string), `path` (string) | Retrieve commit history with optional filtering | Commit history:<br>- Commit SHA<br>- Author + date<br>- Commit message<br>- Files changed | Analyze change patterns for context | `list_commits("myorg/myrepo", "main", "src/auth")` → Last 30 commits to auth module |
| **`get_workflow_run`** | `repo` (string), `run_id` (integer) | Fetch CI/CD workflow execution status | Workflow status:<br>- Status (success/failure/in_progress)<br>- Job details<br>- Logs URL | Monitor CI/CD after PR creation | `get_workflow_run("myorg/myrepo", 12345)` → Status: success, Duration: 3m 42s |
| **`fork_repository`** | `owner` (string), `repo` (string), optional `organization` (string) | Create fork of specified repository | Fork URL + clone URL | Automated fork creation for contribution workflows | `fork_repository("facebook", "react")` → Forked to myuser/react |
| **`create_branch`** | `repo` (string), `branch_name` (string), optional `from_branch` (string) | Create new branch from specified base | Branch reference + SHA | Automated branch creation for feature development | `create_branch("myorg/myrepo", "feature/oauth2", "main")` → Created branch from main@abc123 |
| **`merge_pull_request`** | `repo` (string), `pull_number` (integer), `merge_method` ("merge", "squash", "rebase") | Validate PR mergeable, execute merge via API | Merge commit SHA + status | Automated PR merging after validation passes | `merge_pull_request("myorg/myrepo", 789, "squash")` → Merged successfully, commit def456 |

**GitHub API Rate Limits:**

- Authenticated: 5,000 requests/hour
- Unauthenticated: 60 requests/hour
- Recommendation: Use personal access token (PAT) for automation

**Search Syntax Examples:**

```
search_code("class:User language:typescript", "myorg/myrepo", "typescript")
search_code("function authenticate path:src/auth", "myorg/myrepo", "javascript")
```

---

### 5.4 Filesystem MCP

Filesystem MCP provides secure file operations with built-in validation to prevent sensitive data exposure.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`read`** | `file_path` (string), optional `encoding` (string, default: utf-8) | (1) Validate file path (security check)<br>(2) Check file exists<br>(3) Read file contents with encoding | File contents (string) or binary data | Read configuration, source files | `read("/project/src/config.ts")` → Returns TypeScript configuration file contents |
| **`write`** | `file_path` (string), `content` (string) | (1) Validate file path<br>(2) Check for sensitive data patterns (API keys, credentials)<br>(3) Create parent directories if needed<br>(4) Write content atomically | Success confirmation + file metadata (size, permissions) | Create/update files during implementation | `write("/project/src/utils/helper.ts", "export function...")` → File created, 245 bytes |
| **`list`** | `directory_path` (string) | (1) Validate directory path<br>(2) Read directory contents<br>(3) Gather metadata (size, type, permissions) | File/directory listing:<br>- [FILE] file.ts (1.2 KB)<br>- [DIR] subdirectory/ | Navigate project structure | `list("/project/src")` → Shows 23 files, 4 directories |
| **`search`** | `directory` (string), `pattern` (regex string), `file_pattern` (glob string) | (1) Recursively traverse directory<br>(2) Filter files by glob pattern<br>(3) Search file contents with regex<br>(4) Return matching lines with context | Matching lines:<br>- File path<br>- Line number<br>- Matched line<br>- Context (±3 lines) | grep-like functionality for codebase search | `search("/project/src", "function authenticate", "**/*.ts")` → 5 matches across 3 files |
| **`edit`** | `file_path` (string), `edit_operations` (array of edits) | (1) Read current file contents<br>(2) Validate edit operations<br>(3) Apply edits sequentially<br>(4) Validate syntax (if applicable)<br>(5) Write updated file atomically | Success confirmation + diff preview | Partial file updates without rewriting entire file | `edit("/project/src/user.ts", [{op: "replace", line: 15, content: "..."}])` → Updated 1 line |
| **`mkdir`** | `directory_path` (string) | (1) Validate directory path<br>(2) Create directory and parents (mkdir -p) | Success confirmation + directory path | Create directory structures for new features | `mkdir("/project/src/modules/auth")` → Directory created |
| **`delete`** | `path` (string - file or directory) | (1) Validate path<br>(2) Confirm not protected path (e.g., .git)<br>(3) Delete file or directory recursively | Success confirmation + deletion summary | Remove obsolete files | `delete("/project/src/deprecated")` → Deleted directory with 15 files |
| **`move`** | `source` (string), `destination` (string) | (1) Validate source exists<br>(2) Validate destination path<br>(3) Move/rename atomically<br>(4) Update references if applicable | Success confirmation + new path | Rename or relocate files | `move("/project/src/old-name.ts", "/project/src/new-name.ts")` → File renamed |
| **`read_multiple_files`** | `paths` (array of strings) | (1) Validate all paths<br>(2) Read files in parallel<br>(3) Aggregate results | Array of file contents with paths | Efficient batch reading for analysis | `read_multiple_files(["/project/src/a.ts", "/project/src/b.ts"])` → Returns both files |
| **`get_file_info`** | `path` (string) | Retrieve detailed file/directory metadata | Metadata:<br>- Size (bytes)<br>- Created/modified timestamps<br>- Permissions<br>- Type (file/directory) | Understand file characteristics | `get_file_info("/project/package.json")` → 1,234 bytes, modified 2025-10-10 14:32 |
| **`directory_tree`** | `path` (string) | Recursively build directory tree structure | JSON tree structure:<br>- name, type (file/dir)<br>- children (for directories) | Visualize project structure | `directory_tree("/project/src")` → Nested JSON tree of entire src/ directory |
| **`list_allowed_directories`** | None | Query MCP configuration for allowed paths | List of allowed directory paths (security boundaries) | Verify filesystem access scope | `list_allowed_directories()` → ["/project", "/home/user/workspace"] |

**Security Features:**

- Sensitive data detection (API keys, passwords, secrets)
- Path traversal prevention (no access outside allowed directories)
- Atomic writes (prevents partial file corruption)
- Symlink validation (prevents escape from allowed paths)

**File Search Patterns:**

```
search("/project", "TODO|FIXME", "**/*.ts")          # Find TODOs in TypeScript files
search("/project", "class \w+Controller", "**/*.js")  # Find controller classes
```

---

### 5.5 Sequential Thinking MCP

Sequential Thinking MCP enables complex problem decomposition through structured reasoning chains.

| Command | Input | Process | Output | Triggers | Example |
|---------|-------|---------|--------|----------|---------|
| **`sequential_thinking`** | `thought` (string - current reasoning step)<br>`nextThoughtNeeded` (boolean)<br>`thoughtNumber` (integer - current step)<br>`totalThoughts` (integer - estimated total)<br>Optional:<br>`isRevision` (boolean)<br>`revisesThought` (integer)<br>`branchFromThought` (integer)<br>`branchId` (string) | (1) Record current thought step<br>(2) Analyze reasoning chain so far<br>(3) If revision flagged: revisit earlier thought<br>(4) If branching: explore alternative approach<br>(5) Determine if more thoughts needed<br>(6) Adjust totalThoughts estimate if needed | Structured reasoning output:<br>- Thought chain (numbered steps)<br>- Revisions (if any)<br>- Branches explored<br>- Final conclusion/hypothesis<br>- Confidence score | Invoked during:<br>- Root cause analysis (`/heal-errors`)<br>- Complex debugging (`/debug`)<br>- Architecture decisions (`/planning-create`) | **Root Cause Analysis Example:**<br>Step 1: "Error shows 'userId undefined'"<br>Step 2: "Check User interface definition"<br>Step 3: "Interface missing userId property"<br>Step 4: "Previous PR removed it accidentally"<br>Step 5 (Revision of 4): "Actually, migration script incomplete"<br>Conclusion: "Need to add userId to migration" |

**Sequential Thinking Patterns:**

**Linear Reasoning (No Branches):**

```
Thought 1: Define problem scope
Thought 2: Identify constraints
Thought 3: Evaluate solution A
Thought 4: Evaluate solution B
Thought 5: Select optimal solution
```

**Revision Pattern (Correcting Earlier Thoughts):**

```
Thought 1: Hypothesis - Database connection issue
Thought 2: Check connection logs - no errors found
Thought 3 (Revises Thought 1): Hypothesis incorrect, must be query issue
Thought 4: Analyze query structure - found SQL injection vulnerability
```

**Branching Pattern (Exploring Alternatives):**

```
Thought 1: Need to implement caching
Thought 2 (Branch A): Redis-based caching approach
Thought 3 (Branch A): Pros/cons of Redis
Thought 2 (Branch B): In-memory caching approach
Thought 3 (Branch B): Pros/cons of in-memory
Thought 4 (Merge): Select Redis for distributed system requirements
```

**Usage in Commands:**

- `/heal-errors`: Root cause analysis (5-10 thoughts typical)
- `/debug`: Bug hypothesis generation (3-7 thoughts typical)
- `/planning-create`: Architecture exploration (10-20 thoughts typical)

---

## 6. Macro Features & Variables

Macro features provide cross-cutting capabilities that enhance multiple commands simultaneously.

| Feature | Mechanism | Capabilities | Integration | Example |
|---------|-----------|--------------|-------------|---------|
| **`$ARGUMENTS` Variable** | Dynamic parameter injection into command invocations | - Pass runtime parameters to commands<br>- Customize command behavior without modifying definitions<br>- Enable command composition | Any command accepting parameters can reference `$ARGUMENTS` in its definition | User invokes: `/custom-command $ARGUMENTS` where `ARGUMENTS="--verbose --format=json"`<br>Command receives: `{verbose: true, format: "json"}` |
| **Research Phase Automation** | Automatic codebase and documentation analysis during PRP creation | - Pattern analysis via Serena `list_symbols()`<br>- Documentation retrieval via Context7<br>- Library compatibility checking<br>- Dependency graph analysis | Embedded in `/generate-prp`, `/create-base-prp`, `/spec-create-adv` | During PRP generation, automatically identifies existing auth patterns, retrieves OAuth2 docs from Context7, validates library versions |
| **TodoWrite Integration** | Task extraction and progress tracking from PRP phases | - Parse PRP phases into actionable tasks<br>- Track completion status<br>- Update checklists automatically<br>- Provide progress visibility | Embedded in `/execute-prp` execution loop | PRP with 5 phases → Generates 15 tasks → Updates progress: "Phase 1: 5/5 tasks complete, Phase 2: 2/10 tasks in progress" |
| **Multi-Phase Implementation** | Structured implementation workflow with validation gates between phases | - **Phase 1:** Skeleton (interfaces, types, structure)<br>- **Phase 2:** Production logic<br>- **Phase 3:** Test suite<br>- **Phase 4:** Documentation<br>- Validation gate after each phase | Core execution pattern in `/execute-prp` | Implements auth system:<br>Phase 1 → Defines IAuthService interface → validates (compiles)<br>Phase 2 → Implements OAuth2Provider → validates (tests pass)<br>Phase 3 → Adds integration tests → validates (coverage >90%)<br>Phase 4 → Generates API docs → validates (complete) |
| **Git Worktree Support** | Parallel Claude sessions on isolated branches | - Create multiple worktrees from same repository<br>- Isolate context per feature branch<br>- Enable simultaneous development<br>- Prevent context contamination | Available for any command workflow | Repository with 3 active features:<br>- Worktree 1: `feature/auth` (Claude session 1 executing PRP)<br>- Worktree 2: `feature/payments` (Claude session 2 debugging)<br>- Worktree 3: `main` (Claude session 3 reviewing PR) |

**Multi-Phase Implementation Flow (Detailed):**

```
Phase 1: Skeleton Generation
├─ Create interfaces/types
├─ Define class structures
├─ Stub method signatures
└─ Validation Gate: Type checking passes (tsc --noEmit)
    └─ If FAIL: /heal-errors type_mismatch → Retry
    └─ If PASS: Create checkpoint → Phase 2

Phase 2: Production Logic
├─ Implement method bodies
├─ Handle error cases
├─ Add logging/monitoring
└─ Validation Gate: Unit tests pass (npm test)
    └─ If FAIL: /heal-errors test_failure → Retry (max 3x)
    └─ If PASS: Create checkpoint → Phase 3

Phase 3: Test Suite
├─ Write unit tests (>90% coverage)
├─ Write integration tests
├─ Add edge case tests
└─ Validation Gate: All tests pass + coverage threshold
    └─ If FAIL: Review and add missing tests → Retry
    └─ If PASS: Create checkpoint → Phase 4

Phase 4: Documentation
├─ Generate API documentation
├─ Write usage examples
├─ Update README/guides
└─ Validation Gate: Documentation complete + examples runnable
    └─ If FAIL: Complete missing docs → Retry
    └─ If PASS: Create final checkpoint → Complete
```

**Git Worktree Setup Example:**

```bash
# Main repository
cd /project/main-repo

# Create worktrees for parallel development
git worktree add ../project-feature-auth feature/auth
git worktree add ../project-feature-payments feature/payments

# Each worktree gets independent Claude session
# Session 1: cd ../project-feature-auth && claude chat
# Session 2: cd ../project-feature-payments && claude chat
```

---

## 7. npm Scripts Reference (Enhanced package.json)

Automated scripts provide command-line integration for context management and validation workflows.

| Script | Command | Purpose | Typical Duration | Integration |
|--------|---------|---------|------------------|-------------|
| **`dev`** | `next dev` | Start development server | Continuous | Local development |
| **`build`** | `next build` | Production build with optimizations | 1-3 minutes | CI/CD pipeline |
| **`start`** | `next start` | Start production server | Continuous | Production deployment |
| **`lint`** | `eslint . --ext .ts,.tsx` | Run ESLint code linting | 10-30 seconds | Pre-commit hooks, CI |
| **`lint:fix`** | `eslint . --ext .ts,.tsx --fix` | Auto-fix ESLint violations | 15-40 seconds | Pre-commit hooks |
| **`type-check`** | `tsc --noEmit` | TypeScript type validation | 5-20 seconds | Pre-commit hooks, CI, validation gates |
| **`type-check:watch`** | `tsc --noEmit --watch` | Continuous type checking | Continuous | Local development |
| **`test`** | `jest` | Run test suite (unit + integration) | 30-120 seconds | CI/CD, validation gates |
| **`test:watch`** | `jest --watch` | Run tests in watch mode | Continuous | Local development |
| **`check-all`** | `npm run type-check && npm run lint && npm run test` | Comprehensive validation (types + linting + tests) | 1-3 minutes | **Primary validation gate** used by `/execute-prp`, `/validate-state` |
| **`context:sync`** | `node scripts/sync-serena-context.js` | Execute `/sync-context` workflow programmatically | 10-60 seconds | Automatic triggers, manual invocation |
| **`context:prune`** | `node scripts/prune-context.js` | Execute `/prune-context` workflow programmatically | 5-30 seconds | Automatic triggers, manual invocation |
| **`context:health`** | `node scripts/context-health-check.js` | Execute `/validate-state` workflow programmatically | 30-90 seconds | Session start, periodic checks |

**Example package.json:**

```json
{
  "name": "context-engineering-project",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "type-check": "tsc --noEmit",
    "type-check:watch": "tsc --noEmit --watch",
    "test": "jest",
    "test:watch": "jest --watch",
    "check-all": "npm run type-check && npm run lint && npm run test",
    "context:sync": "node scripts/sync-serena-context.js",
    "context:prune": "node scripts/prune-context.js",
    "context:health": "node scripts/context-health-check.js"
  },
  "devDependencies": {
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "jest": "^29.0.0"
  }
}
```

**Integration with Commands:**

- `/execute-prp` calls `npm run check-all` after each phase
- `/validate-state` calls `npm run context:health`
- `/heal-errors` calls `npm run type-check` or `npm run lint` for targeted validation
- CI/CD pipelines call `npm run check-all` before deployment

---

## 8. Command Integration Patterns

Integration patterns define how commands, MCP tools, and project structures work together to create cohesive workflows.

### 8.1 File Structure Requirements

The Context Engineering framework expects a specific directory structure:

```
project-root/
├─ .claude/
│  └─ commands/              # Custom slash command definitions
│     ├─ generate-prp.md     # /generate-prp command spec
│     ├─ execute-prp.md      # /execute-prp command spec
│     └─ ...
├─ PRPs/
│  ├─ templates/             # Base PRP templates
│  │  ├─ feature-template.md
│  │  ├─ bugfix-template.md
│  │  └─ refactor-template.md
│  ├─ scripts/               # PRP execution automation
│  │  ├─ prp-runner.js       # Headless execution
│  │  └─ prp-validator.js    # PRP syntax validation
│  ├─ ai_docs/               # Library documentation cache
│  │  ├─ react-hooks.md
│  │  ├─ nextjs-routing.md
│  │  └─ ...
│  └─ [generated PRPs]       # User-generated PRPs
│     ├─ auth-system-2025-10-10.md
│     └─ ...
├─ docs/
│  └─ INITIAL-*.md           # Feature request documents for /generate-prp
├─ examples/                 # Code pattern references
│  ├─ api-endpoint-pattern.ts
│  ├─ error-handling-pattern.ts
│  └─ ...
├─ scripts/                  # Automation scripts
│  ├─ sync-serena-context.js
│  ├─ prune-context.js
│  └─ context-health-check.js
├─ CLAUDE.md                 # Project-wide rules (single source of truth)
└─ package.json              # npm scripts integration
```

**Critical Files:**

- **CLAUDE.md:** Project-specific rules, coding standards, architectural decisions
- **PRPs/templates/:** Reusable templates ensure consistent PRP structure
- **examples/:** Reference implementations for code generation consistency
- **.claude/commands/:** Custom command definitions for project-specific workflows

### 8.2 Runner Modes

Three execution modes support different environments and use cases:

| Mode | Environment | Use Case | Output Format | Monitoring |
|------|-------------|----------|---------------|------------|
| **Interactive** | Local development terminal | Real-time development with immediate feedback | Human-readable terminal output with colors, progress bars | Developer observation in terminal |
| **Headless** | CI/CD pipelines, automated systems | Unattended execution, batch processing | Exit codes (0=success, non-zero=failure), structured log files (JSON) | Pipeline dashboard parsing exit codes |
| **Stream-JSON** | Remote execution, long-running tasks | Real-time monitoring of long executions (e.g., 30+ minute implementations) | Newline-delimited JSON events streamed to stdout:<br>`{"type": "phase_start", "phase": 1, "timestamp": "..."}`<br>`{"type": "validation", "status": "pass", ...}` | Real-time monitoring dashboards consuming JSON stream |

**Interactive Mode Example:**

```
$ /execute-prp PRPs/auth-system.md

🚀 Starting PRP Execution: auth-system.md
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Phase 1: Skeleton Generation                    [▓▓▓▓▓▓▓▓▓▓] 100%
  ✓ Created interfaces (5 files)
  ✓ Type checking: PASS

Phase 2: Production Logic                       [▓▓▓▓▓▓----] 60%
  ✓ Implemented OAuth2Provider (320 lines)
  ⏳ Running tests... (15/23 passing)
```

**Headless Mode Example:**

```bash
$ node PRPs/scripts/prp-runner.js PRPs/auth-system.md --mode=headless
$ echo $?  # Check exit code
0  # Success
$ cat execution.log
[2025-10-10T14:32:15Z] INFO: Starting PRP execution
[2025-10-10T14:32:20Z] INFO: Phase 1 complete
[2025-10-10T14:35:42Z] INFO: Phase 2 complete
[2025-10-10T14:38:10Z] INFO: All phases complete, exit 0
```

**Stream-JSON Mode Example:**

```bash
$ node PRPs/scripts/prp-runner.js PRPs/auth-system.md --mode=stream-json | tee execution.ndjson
{"event":"phase_start","phase":1,"name":"Skeleton Generation","timestamp":"2025-10-10T14:32:15Z"}
{"event":"file_created","path":"src/auth/IAuthService.ts","lines":45,"timestamp":"2025-10-10T14:32:18Z"}
{"event":"validation","type":"type_check","status":"pass","duration_ms":1250,"timestamp":"2025-10-10T14:32:20Z"}
{"event":"phase_complete","phase":1,"timestamp":"2025-10-10T14:32:20Z"}
{"event":"phase_start","phase":2,"name":"Production Logic","timestamp":"2025-10-10T14:32:21Z"}
...
```

### 8.3 Best Practices: Production-Grade Implementation

**1. RAG-First Strategy (Retrieval-Augmented Generation)**

Prefer context retrieval over model fine-tuning for operational flexibility and cost efficiency.

**Operational Expenditure (OpEx) vs Capital Expenditure (CapEx):**

- **RAG (OpEx):** Update documentation/examples dynamically, no model retraining, instant context updates
- **Fine-tuning (CapEx):** Expensive training runs, longer update cycles, version management overhead

**Implementation Pattern:**

```
Generate PRP → Query Context7 for library docs → Query Serena for existing patterns → Merge contexts → Generate code
(No fine-tuned model required, all context retrieved at runtime)
```

**2. Explicit & Comprehensive Context**

Never assume the model knows project conventions. Provide complete specifications.

**Anti-Pattern (Implicit Context):**

```yaml
# Vague PRP
task: "Add authentication"
```

**Best Practice (Explicit Context):**

```yaml
# Comprehensive PRP
task: "Add OAuth2 authentication"
context:
  auth_library: "passport@0.6.0"
  strategy: "passport-google-oauth20@2.0.0"
  session_store: "connect-redis@7.1.0"
  existing_patterns:
    - "src/auth/LocalStrategy.ts (reference for structure)"
    - "src/middleware/authenticate.ts (integration point)"
  constraints:
    - "Must support Google and GitHub providers"
    - "Session TTL: 7 days"
    - "CSRF protection required"
  gotchas:
    - "Passport serialize/deserialize must handle async"
    - "Callback URL must match Google Console exactly"
```

**3. Validation-First Design**

Define success criteria as executable tests before implementation.

**Pattern:**

```markdown
## Phase 2: Production Logic

### Validation Gate (MUST PASS before Phase 3):
```bash
# Unit tests
npm test src/auth/*.test.ts  # Must pass 100%

# Type checking
tsc --noEmit  # Must pass with 0 errors

# Integration test
npm test tests/integration/auth-flow.test.ts  # Must pass

# Security check
npm run security-audit  # Must show 0 high/critical vulnerabilities
```

If ANY validation fails:

1. Trigger `/heal-errors` (max 3 attempts)
2. If still failing, STOP and escalate to human
3. Do NOT proceed to Phase 3 with failing validations

```

**4. Incremental Complexity**

Build and validate small components before composing into complex systems.

**Pattern:**
```markdown
## Implementation Order

### Increment 1: Core Interface (30 minutes)
- Define IAuthService interface
- Validate: TypeScript compiles

### Increment 2: Simple Implementation (1 hour)
- Implement LocalAuthProvider (username/password only)
- Validate: Unit tests pass

### Increment 3: Session Management (1 hour)
- Add session storage (Redis)
- Validate: Session tests pass

### Increment 4: OAuth Provider (2 hours)
- Add GoogleOAuthProvider
- Validate: OAuth flow tests pass

(Each increment validated independently before proceeding)
```

**5. Context Hierarchy**

Organize context into layers with clear precedence rules.

**Hierarchy (Highest to Lowest Precedence):**

```
1. Task-specific (PRP) - Overrides all others for specific implementation
   Example: "For this feature, use MongoDB instead of Postgres"

2. Module-specific (feature-context.md) - Overrides project-wide for module
   Example: "Auth module uses bcrypt, not argon2"

3. Project-wide (CLAUDE.md) - Default rules for entire project
   Example: "All API endpoints use Express.js"

4. Framework defaults - Fallback to standard conventions
   Example: "Follow REST naming conventions"
```

**Resolution Example:**

```
Question: Which password hashing library to use?

CLAUDE.md says: "Use argon2 for password hashing"
auth-module-context.md says: "Use bcrypt (legacy compatibility)"
Current PRP says: (nothing specified)

Resolution: bcrypt (module-specific overrides project-wide)
```

**6. Continuous Context Updates**

Treat every modification as a mini-PRP that references existing patterns.

**Pattern:**

```markdown
## Modification Request: "Add rate limiting to /api/login endpoint"

### Context References:
1. Existing rate limiting pattern: `src/middleware/rateLimiter.ts`
2. Existing endpoint structure: `src/routes/auth.ts`
3. Project standard: Express middleware pattern
4. Library: express-rate-limit@6.7.0 (already in package.json)

### Mini-PRP:
1. Import rateLimiter from existing middleware
2. Apply to /api/login route using same pattern as /api/register
3. Configure: 5 attempts per 15 minutes (stricter than default)
4. Validate: Integration test with 6 rapid requests (6th should fail)

(References existing code, maintains consistency, includes validation)
```

### 8.4 Anti-Patterns to Avoid

| Anti-Pattern | Description | Why Harmful | Best Practice Alternative |
|--------------|-------------|-------------|---------------------------|
| **Context Dumping** | Providing excessive, unfocused information (e.g., entire codebase in context) | Dilutes relevant context, wastes tokens, confuses focus | Provide targeted context: specific files, relevant patterns, scoped documentation |
| **Trust Fall Execution** | Executing PRPs without human validation of plan quality | AI can misinterpret requirements, generate incorrect implementations | Always human-validate PRP before `/execute-prp` |
| **Vague Brain Dump** | One-line feature descriptions (e.g., "Add search feature") | Insufficient context leads to generic implementations that don't match project needs | Provide detailed requirements with examples, constraints, existing patterns |
| **Context-Free Updates** | Modifying features without referencing existing code patterns | Creates inconsistency, violates project conventions, causes integration issues | Always use `/prime-core`, reference existing patterns, maintain style consistency |
| **Inconsistent Guidance** | Conflicting rules across CLAUDE.md, PRPs, and examples | AI receives mixed signals, produces unpredictable results | Single source of truth (CLAUDE.md), PRPs inherit from it, examples demonstrate it |
| **Skipping Validation Gates** | Proceeding to next phase despite test failures | Compounds errors, makes debugging harder, leads to broken implementations | Enforce strict validation gates, auto-trigger `/heal-errors`, max 3 retry attempts |

---

## 9. Trigger Conditions Matrix

Trigger conditions determine when commands execute automatically versus requiring manual invocation.

| Command | Manual Triggers | Automatic Triggers | Trigger Conditions | Frequency |
|---------|----------------|-------------------|-------------------|-----------|
| **`/sync-context`** | User invokes `/sync-context` explicitly | - Session start (if `git diff` ≠ 0)<br>- After 10+ file modifications detected<br>- Before `/execute-prp` execution | Git diff detects changes:<br>`git diff --name-only HEAD~5 \| wc -l > 10`<br>Session start check:<br>`git status --porcelain \| wc -l > 0` | - Session start: Once<br>- During development: Every 10 modifications<br>- Pre-execution: Once per PRP |
| **`/heal-errors`** | User invokes `/heal-errors --verbose` for debugging | - Embedded in `/execute-prp` validation loop<br>- Triggered on compilation failure<br>- Triggered on test failure | Validation gate failures:<br>`npm run check-all` exit code ≠ 0<br>TypeScript errors:<br>`tsc --noEmit` exit code ≠ 0 | - Per validation gate: Up to 3 attempts<br>- On-demand: As needed |
| **`/prune-context`** | User invokes with custom parameters:<br>`/prune-context --age=14 --merge-similar` | - Token usage > 80% of context window<br>- Memory count > 100 entries<br>- Session duration > 2 hours<br>- Before PRP execution (ensure clean context) | Token threshold:<br>`current_tokens / max_tokens > 0.80`<br>Memory threshold:<br>`list_memories().length > 100`<br>Session duration:<br>`session_start_time - now > 7200 seconds` | - Token-based: When threshold exceeded<br>- Count-based: When threshold exceeded<br>- Time-based: Every 2 hours<br>- Pre-execution: Once per PRP |
| **`/validate-state`** | User invokes `/validate-state` for on-demand health check | - Every session start<br>- Every 30 minutes during development<br>- Before PRP execution<br>- After major refactoring (>20 files) | Session start:<br>`on_session_init()`<br>Periodic:<br>`setInterval(validate_state, 30 * 60 * 1000)`<br>File count:<br>`git diff --name-only \| wc -l > 20` | - Session start: Once<br>- Periodic: Every 30 minutes<br>- Pre-execution: Once per PRP<br>- Post-refactor: Once per large change |
| **`/prime-core`** | User invokes `/prime-core` to reinitialize context | - First command invocation (if not already primed)<br>- After project structure changes | Context not initialized:<br>`if (!context.primed)`<br>Project structure changed:<br>`package.json modified \|\| tsconfig.json modified` | - Session start: Once<br>- On-demand: As needed |
| **Checkpoint Creation** | User invokes `git commit` manually | - After compilation success following fixes<br>- After test suite passes<br>- Before major refactoring (>10 files)<br>- On session end | Compilation success:<br>`npm run check-all` exit code = 0 (after previous failure)<br>Test success:<br>`npm test` exit code = 0<br>Pre-refactor:<br>`upcoming_file_changes > 10` | - Post-fix: Once per successful fix<br>- Post-tests: Once per test pass<br>- Pre-refactor: Once per major change<br>- Session end: Once |

**Automatic Trigger Implementation (Conceptual):**

```javascript
// Session initialization
async function onSessionStart() {
  // Check git state
  const gitDiff = await exec("git status --porcelain");
  if (gitDiff.stdout.length > 0) {
    await runCommand("/sync-context");
  }

  // Validate state
  await runCommand("/validate-state");

  // Prime context if not already done
  if (!context.primed) {
    await runCommand("/prime-core");
  }
}

// Periodic monitoring
setInterval(async () => {
  // Validate state every 30 minutes
  await runCommand("/validate-state");

  // Check if pruning needed
  const memories = await listMemories();
  const tokens = await calculateTokens(memories);
  if (tokens > MAX_TOKENS * 0.8 || memories.length > 100) {
    await runCommand("/prune-context");
  }
}, 30 * 60 * 1000);  // 30 minutes

// File modification tracking
let fileModificationCount = 0;
onFileModified(() => {
  fileModificationCount++;
  if (fileModificationCount >= 10) {
    await runCommand("/sync-context");
    fileModificationCount = 0;
  }
});
```

---

## 10. Cross-References

### 10.1 Related Documentation Files

| Document | Purpose | Relationship to Commands |
|----------|---------|--------------------------|
| **CLAUDE.md** | Single source of truth for project-wide rules, coding standards, architectural decisions | Referenced by `/prime-core`, enforced by `/execute-prp`, validated by `/review-general` |
| **SERENA-INSTRUCTIONS.md** | Self-healing protocol specification, error recovery procedures | Defines behavior of `/heal-errors`, `/sync-context` workflows |
| **VSCODE-INTEGRATION.md** | VS Code integration patterns, editor configuration | Complementary to command workflows, provides IDE-level automation |
| **PRPs/templates/** | Base PRP templates for features, bugfixes, refactoring | Used by `/generate-prp`, `/create-base-prp` as structural templates |
| **examples/** | Code pattern references (API endpoints, error handling, testing patterns) | Referenced during code generation in `/execute-prp` for consistency |
| **docs/INITIAL-*.md** | Feature request documents for `/generate-prp` input | Input documents for PRP creation workflow |

**Cross-Reference Navigation:**

```
User Feature Request (docs/INITIAL-auth.md)
  ↓ input to
/generate-prp
  ↓ reads
CLAUDE.md (project rules) + examples/ (code patterns)
  ↓ produces
PRPs/auth-system-2025-10-10.md
  ↓ input to
/execute-prp
  ↓ invokes
Serena MCP + Context7 MCP + Filesystem MCP
  ↓ validates via
npm run check-all (package.json scripts)
  ↓ on failure, triggers
/heal-errors
  ↓ produces
Production code + tests + documentation
```

### 10.2 Key Concepts

| Concept | Definition | Related Commands |
|---------|------------|------------------|
| **PRP (Product Requirements Plan)** | Structured implementation blueprint with phases, validation gates, and context references | `/generate-prp`, `/create-base-prp`, `/execute-prp`, `/execute-base-prp` |
| **Context Engineering** | Systematic approach to providing structured context to AI models (10x improvement over prompt engineering) | All commands implement context engineering principles |
| **Serena Memories** | Long-term context storage mechanism (symbol definitions, patterns, project knowledge) | `/sync-context`, `/prune-context`, `/validate-state` |
| **Validation Gates** | Executable success criteria (tests, type checking, linting) that must pass before proceeding | Embedded in `/execute-prp`, enforced by `/validate-state` |
| **Checkpoints** | Git-based recovery points created after successful phases or fixes | Automatic checkpoint creation after validation passes |
| **LSP (Language Server Protocol)** | Protocol for semantic code understanding (used by Serena MCP) | Serena MCP commands: `find_symbol`, `find_referencing_symbols`, `get_symbol_definition` |
| **Self-Healing** | Automatic error detection, root cause analysis, and remediation | `/heal-errors`, validation loop in `/execute-prp` |
| **Context Drift** | Divergence between AI context and actual codebase state | Measured by `/validate-state`, remediated by `/sync-context` |
| **Multi-Phase Implementation** | Structured workflow: Skeleton → Logic → Tests → Documentation | Standard execution pattern in `/execute-prp` |

### 10.3 MCP Server References

| MCP Server | Purpose | Key Commands | Use Cases |
|------------|---------|--------------|-----------|
| **Serena** | Semantic code understanding via LSP | `find_symbol`, `find_referencing_symbols`, `get_symbol_definition`, `list_symbols` | - Locate functions/classes for context<br>- Impact analysis before refactoring<br>- Reference existing patterns during implementation |
| **Context7** | Library documentation retrieval (up-to-date) | `c7_query`, `c7_search`, `c7_info` | - Get current library usage patterns<br>- Verify documentation freshness<br>- Research new libraries during PRP creation |
| **GitHub** | Repository automation, issue tracking, CI/CD | `create_issue`, `create_pull_request`, `search_code`, `get_file_contents`, `list_commits` | - Automated PR creation after implementation<br>- Issue tracking from error patterns<br>- Reference implementations from other repos |
| **Filesystem** | Secure file operations with validation | `read`, `write`, `list`, `search`, `edit`, `mkdir`, `delete`, `move` | - Read/write source files during implementation<br>- Search codebase for patterns<br>- Navigate project structure |
| **Sequential Thinking** | Complex problem decomposition, reasoning chains | `sequential_thinking` | - Root cause analysis in `/heal-errors`<br>- Bug hypothesis generation in `/debug`<br>- Architecture exploration in `/planning-create` |

**MCP Integration Hierarchy:**

```
High-Level Commands (User-Facing)
  ├─ /generate-prp → Serena + Context7
  ├─ /execute-prp → Serena + Filesystem + GitHub
  ├─ /heal-errors → Serena + Sequential Thinking + Filesystem
  └─ /sync-context → Serena + Filesystem

Mid-Level Commands (Workflow-Specific)
  ├─ /review-general → Serena + Filesystem
  ├─ /debug → Serena + Sequential Thinking
  └─ /create-pr → GitHub + Filesystem

Low-Level Tools (MCP Commands)
  ├─ Serena MCP (Code Understanding)
  ├─ Context7 MCP (Documentation)
  ├─ GitHub MCP (Repository)
  ├─ Filesystem MCP (Files)
  └─ Sequential Thinking MCP (Reasoning)
```

### 10.4 Workflow Phases

The Context Engineering framework implements a six-phase methodology:

| Phase | Name | Purpose | Key Commands | Outputs |
|-------|------|---------|--------------|---------|
| **Phase 0** | Foundation Setup | One-time project initialization | `/prime-core`, manual setup of `.claude/`, `PRPs/`, `CLAUDE.md` | Project structure, configuration files |
| **Phase 1** | Context Engineering Foundation | Load project rules, index codebase, establish baseline | `/prime-core`, Serena `onboarding()` | Primed AI context, symbol index |
| **Phase 2** | PRP Creation with MCP-Enhanced Research | Transform feature requests into comprehensive implementation plans | `/generate-prp`, `/create-base-prp`, Context7 queries, Serena pattern analysis | Validated PRP document |
| **Phase 3** | MCP Command I/O Specification | Define execution workflow with MCP tool orchestration | PRP defines which MCP commands to invoke at each step | Executable implementation plan |
| **Phase 4** | Zero-Shot Execution Workflow | Autonomous implementation following PRP with validation gates | `/execute-prp`, Serena + Filesystem + GitHub MCP commands | Production code, tests, documentation |
| **Phase 5** | Validation & Self-Correction Loop | Continuous validation with automatic error healing | `/validate-state`, `/heal-errors`, `npm run check-all` | Validated implementation, health reports, checkpoints |

**Phase Progression Example (Complete Feature Implementation):**

```
Feature Request: "Add OAuth2 authentication"

Phase 0: (One-time setup, already complete)
└─ Project has .claude/, PRPs/, CLAUDE.md, Serena configured

Phase 1: Context Engineering Foundation
├─ User: /prime-core
├─ Serena: onboarding() → Indexed 1,247 symbols
└─ Context: Loaded CLAUDE.md rules + 23 examples

Phase 2: PRP Creation
├─ User: /generate-prp docs/INITIAL-auth-oauth2.md
├─ Context7: c7_query("passport", "oauth2 strategy") → Retrieved docs
├─ Serena: find_symbol("authenticate") → Found existing auth patterns
└─ Output: PRPs/auth-oauth2-2025-10-10.md (comprehensive PRP)

Phase 3: MCP Command I/O Specification (embedded in PRP)
└─ PRP specifies:
   - Phase 1: Create interfaces via Filesystem.write()
   - Phase 2: Implement logic, reference existing patterns via Serena.find_symbol()
   - Phase 3: Write tests via Filesystem.write()
   - Phase 4: Generate docs, create PR via GitHub.create_pull_request()

Phase 4: Zero-Shot Execution
├─ User: /execute-prp PRPs/auth-oauth2-2025-10-10.md
├─ Execution:
│  ├─ Phase 1: Skeleton (5 files) → Validates (tsc passes) → Checkpoint
│  ├─ Phase 2: Logic (320 lines) → Validates (tests pass) → Checkpoint
│  ├─ Phase 3: Tests (15 tests) → Validates (coverage 94%) → Checkpoint
│  └─ Phase 4: Docs + PR → Validates (docs complete) → Final Checkpoint
└─ Output: PR #789 created, all validations passing

Phase 5: Validation & Self-Correction (continuous during Phase 4)
├─ After Phase 2 implementation: npm run check-all
│  └─ Test failure: "OAuth2 callback missing CSRF token"
│     └─ Trigger: /heal-errors
│        ├─ Sequential Thinking: Root cause → CSRF middleware not applied
│        ├─ Fix: Add CSRF middleware to callback route
│        └─ Revalidate: Tests pass → Proceed to Phase 3
└─ Final: /validate-state → Health report shows all green
```

### 10.5 Script Integration Points

Context management scripts provide programmatic access to command workflows:

| Script | Location | Purpose | Invoked By | Key Operations |
|--------|----------|---------|------------|----------------|
| **`sync-serena-context.js`** | `scripts/sync-serena-context.js` | Execute `/sync-context` workflow programmatically | - `npm run context:sync`<br>- Automatic triggers (session start, file modifications) | - `git diff` to detect changes<br>- Serena `list_symbols()` for reindexing<br>- Memory store updates<br>- Validation and checkpoint creation |
| **`prune-context.js`** | `scripts/prune-context.js` | Execute `/prune-context` workflow programmatically | - `npm run context:prune`<br>- Automatic triggers (token threshold, memory count) | - Memory inventory with metadata<br>- Relevance scoring (LLM-based)<br>- Compression via summarization<br>- Memory deletion/merging |
| **`context-health-check.js`** | `scripts/context-health-check.js` | Execute `/validate-state` workflow programmatically | - `npm run context:health`<br>- Automatic triggers (session start, periodic, pre-execution) | - Compilation validation (`npm run check-all`)<br>- Git state verification<br>- Serena index health check<br>- Memory consistency validation<br>- Context drift detection |
| **`prp-runner.js`** | `PRPs/scripts/prp-runner.js` | Headless/Stream-JSON execution of PRPs | - CI/CD pipelines<br>- Automated deployments<br>- Remote execution | - Parse PRP phases<br>- Execute with validation gates<br>- Generate structured logs (JSON)<br>- Return exit codes |
| **`prp-validator.js`** | `PRPs/scripts/prp-validator.js` | Validate PRP syntax and structure | - Pre-execution validation<br>- PRP creation workflow | - YAML header validation<br>- Phase structure validation<br>- Required fields validation<br>- Validation gate syntax check |

**Example: Programmatic Invocation from CI/CD**

```yaml
# .github/workflows/context-engineering.yml
name: Context Engineering CI

on:
  push:
    branches: [main, feature/*]

jobs:
  execute-prp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm install

      - name: Validate context health
        run: npm run context:health

      - name: Execute PRP (Headless Mode)
        run: node PRPs/scripts/prp-runner.js PRPs/current-feature.md --mode=headless
        env:
          SERENA_API_KEY: ${{ secrets.SERENA_API_KEY }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Run comprehensive validation
        run: npm run check-all

      - name: Create PR on success
        if: success()
        run: node scripts/create-pr.js
```

---

## End of Document

**Document Statistics:**

- **Total Commands Documented:** 33+ (7 PRP, 4 Context Management, 5 Development Workflow, 17+ MCP)
- **Total Sections:** 10 major sections with 25+ subsections
- **Comprehensive Tables:** 15+ detailed command reference tables
- **Integration Patterns:** 6 architectural patterns documented
- **Cross-References:** 25+ internal references for navigation

**Usage Guidance:**

1. **For AI Agents:** Follow command specifications exactly as documented; respect trigger conditions and validation gates
2. **For Developers:** Use command reference tables for quick lookup; review integration patterns for workflow design
3. **For Technical Leads:** Review architectural principles and anti-patterns for framework evaluation

**Maintenance:**

- Update this document when adding new commands or modifying existing workflows
- Maintain synchronization with CLAUDE.md, SERENA-INSTRUCTIONS.md, and example files
- Version control this document alongside codebase changes

**Related Documentation:**

- Previous: [06-systematic-patterns.md](./06-systematic-patterns.md)
- Next: [08-implementation-guide.md](./08-implementation-guide.md) (if exists)
- Parent: [context-mastery-exploration.md](./context-mastery-exploration.md)
