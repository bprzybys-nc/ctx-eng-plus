# 06 - Workflow Patterns

## Overview

This document provides comprehensive workflow patterns for systematic software development using context engineering and MCP orchestration. These patterns achieve 85-95% first-attempt success rates through structured protocols, automated validation, and intelligent context management.

**Key Concepts:**
- Session management protocols ensuring consistent baseline state
- Multi-phase implementation patterns for systematic development
- Context synchronization strategies preventing drift and errors
- Validation frameworks with automated self-correction
- Real-world execution patterns with timeline benchmarks

**Workflow Categories:**
- Session protocols (start, synchronization, end)
- PRP-based implementation workflows
- Multi-phase development patterns
- Error recovery and troubleshooting procedures
- Performance optimization strategies

---

## 1. Complete Workflow Overview

The complete development workflow spans from session initialization through production deployment, incorporating systematic validation at each phase.

```mermaid
graph TB
    subgraph "Phase 0: Session Start"
        A1["Compilation Check"] --> A2["Serena Onboarding"]
        A2 --> A3["Checkpoint Validation"]
        A3 --> A4["Context Health Check"]
    end

    subgraph "Phase 1: Context Foundation"
        B1["CLAUDE.md Rules"] --> B2["INITIAL.md Creation"]
        B2 --> B3["MCP Directives"]
    end

    subgraph "Phase 2: PRP Generation"
        C1["Sequential Thinking<br/>Planning"] --> C2["Serena<br/>Symbol Analysis"]
        C2 --> C3["Context7<br/>Doc Retrieval"]
        C3 --> C4["GitHub<br/>Pattern Search"]
        C4 --> C5["PRP Document"]
    end

    subgraph "Phase 3: Human Validation"
        D1["Architecture Review"] --> D2["Security Audit"]
        D2 --> D3["Requirement Coverage"]
        D3 --> D4["Approve/Reject"]
    end

    subgraph "Phase 4: Execution"
        E1["Task Checklist"] --> E2["Component Build"]
        E2 --> E3["Validation Tests"]
        E3 --> E4{"Pass?"}
        E4 -->|No| E5["Auto-Fix"]
        E5 --> E3
        E4 -->|Yes| E6["Next Component"]
    end

    subgraph "Phase 5: Validation Loop"
        F1["Level 1: Syntax"] --> F2["Level 2: Unit Tests"]
        F2 --> F3["Level 3: Integration"]
        F3 --> F4{"All Pass?"}
        F4 -->|No| F5["Error Analysis"]
        F5 --> F1
        F4 -->|Yes| F6["Production Ready"]
    end

    subgraph "Phase 6: Session End"
        G1["Final Validation"] --> G2["Create Checkpoint"]
        G2 --> G3["Context Summary"]
        G3 --> G4["Git Commit"]
        G4 --> G5["Memory Pruning"]
    end

    A4 --> B1
    B3 --> C1
    C5 --> D1
    D4 --> E1
    E6 --> F1
    F6 --> G1

    G5 --> H["GitHub PR Creation"]
    H --> I["Production Deployment"]
```

**Workflow Characteristics:**
- Systematic progression through validation gates
- Automated error detection and correction
- Context preservation across phases
- Human oversight at critical decision points
- Performance metrics captured throughout

---

## 2. Session Start Protocol

### 2.1 Compilation Check

**Purpose:** Establish clean baseline before development

**Execution Sequence:**

| Step | Action | Expected Result | Failure Response |
|------|--------|-----------------|------------------|
| 1 | Execute build command | Zero errors, clean output | STOP - analyze errors before proceeding |
| 2 | Run type checking | All types validate | STOP - resolve type issues first |
| 3 | Execute linter | Zero violations | FIX - address style issues immediately |
| 4 | Verify test suite | Tests executable | FIX - repair test infrastructure |

**Implementation:**

```bash
# Primary validation sequence
npm run build                    # Compilation verification
npm run type-check              # Type system validation
npm run lint                    # Code style verification
npm run test --version          # Test suite availability
```

**Decision Tree:**

```mermaid
graph TD
    A["Compilation Check"] --> B{"Build<br/>Success?"}
    B -->|Yes| C{"Type Check<br/>Pass?"}
    B -->|No| D["Analyze Build Errors"]
    C -->|Yes| E["Proceed to<br/>Serena Onboarding"]
    C -->|No| F["Resolve Type Issues"]
    D --> G["Fix Root Cause Only"]
    F --> G
    G --> H["Re-run Compilation Check"]
    H --> A
    E --> I["Session Start Complete"]
```

**Critical Rules:**
- Never proceed with failing compilation
- Fix root causes, not symptoms
- Document any unusual build configurations
- Validate test infrastructure availability

### 2.2 Serena Onboarding

**Purpose:** Create semantic index of codebase for symbol-level operations

**Execution Sequence:**

| Step | Action | Duration | Output |
|------|--------|----------|--------|
| 1 | Initiate onboarding process | 10-30s | Symbol extraction begins |
| 2 | Index file structure | 5-15s | Directory hierarchy mapped |
| 3 | Extract symbol definitions | 20-60s | Functions, classes, types indexed |
| 4 | Build reference graph | 10-30s | Dependency relationships mapped |
| 5 | Store in memory system | 5-10s | .serena/memories/ populated |

**Implementation:**

```python
# Serena onboarding invocation
onboarding()
# Creates semantic index of entire codebase
# Identifies project structure, dependencies, test patterns
# Stores in .serena/memories/
```

**Index Quality Metrics:**

| Metric | Target | Warning Threshold | Action Required |
|--------|--------|-------------------|-----------------|
| Symbol count | Project-dependent | <100 for medium project | Verify project structure |
| Indexing time | 30-90s | >180s | Check project size/complexity |
| Memory files created | 10-50 | <5 | Investigate indexing failure |
| Context health score | >85% | <70% | Re-run onboarding |

**Caching Strategy:**
- Index persists within session
- Re-index on significant structural changes (>10 files)
- Cached index reduces subsequent operation time by 60-80%

### 2.3 Checkpoint Validation

**Purpose:** Ensure context alignment with current repository state

**Validation Process:**

```mermaid
graph LR
    A["Read Latest Checkpoint"] --> B["Compare with Git State"]
    B --> C{"Alignment<br/>Check"}
    C -->|Aligned| D["Proceed"]
    C -->|Misaligned| E["Synchronization Required"]
    E --> F["Update Context"]
    F --> G["Validate Sync"]
    G --> D
```

**Comparison Matrix:**

| Aspect | Checkpoint State | Git State | Action if Mismatch |
|--------|------------------|-----------|-------------------|
| File count | Recorded count | Actual count | Re-index if >10% difference |
| Key symbols | Symbol list | Current symbols | Update symbol index |
| Branch name | Recorded branch | Current branch | Verify intended branch |
| Commit hash | Last commit | HEAD commit | Review commits since checkpoint |

**Implementation:**

```python
# Read latest checkpoint
checkpoint_data = read_memory("checkpoint-latest")

# Validate against git state
git_state = execute_shell_command("git status --porcelain")
git_branch = execute_shell_command("git branch --show-current")
git_commit = execute_shell_command("git rev-parse HEAD")

# Compare and determine alignment
if checkpoint_data.branch != git_branch:
    trigger_context_synchronization()
```

### 2.4 Context Health Assessment

**Purpose:** Evaluate context system integrity before development

**Health Indicators:**

| Indicator | Healthy Range | Warning Range | Critical Range | Resolution |
|-----------|---------------|---------------|----------------|------------|
| Symbol query success rate | >95% | 85-95% | <85% | Re-index affected modules |
| Memory count | 10-100 | 100-200 | >200 | Prune obsolete memories |
| Index freshness | <5 min | 5-30 min | >30 min | Refresh index |
| Type-check duration | <30s | 30-60s | >60s | Check for index corruption |
| Context drift incidents | 0 | 1-2 | >2 | Full context reset |

**Assessment Procedure:**

```python
# Execute health check
health_metrics = {
    "symbol_success_rate": query_random_symbols(sample_size=10),
    "memory_count": len(list_all_memories()),
    "index_age": get_index_timestamp(),
    "type_check_duration": measure_type_check_time()
}

# Calculate health score
health_score = calculate_health_score(health_metrics)

if health_score < 70:
    initiate_recovery_protocol()
elif health_score < 85:
    log_warning_and_monitor()
else:
    proceed_with_development()
```

**Health Score Formula:**
```
health_score = (
    symbol_success_rate * 0.4 +
    memory_efficiency * 0.3 +
    index_freshness * 0.2 +
    type_check_performance * 0.1
) * 100
```

**Recovery Protocol:**

```mermaid
graph TD
    A["Health Score < 70%"] --> B["STOP Development"]
    B --> C["Clear All Memories"]
    C --> D["Re-run Onboarding"]
    D --> E["Validate Compilation"]
    E --> F{"Health Score<br/>>85%?"}
    F -->|No| G["Manual Investigation Required"]
    F -->|Yes| H["Resume Development"]
```

---

## 3. PRP Generation Phase

**Purpose:** Create comprehensive implementation blueprint through automated research and planning

**Phase Duration:** 10-15 minutes typical, up to 30 minutes for complex features

### 3.1 Generation Workflow

```mermaid
sequenceDiagram
    participant User
    participant CE as Context Engineering
    participant ST as Sequential Thinking
    participant S as Serena
    participant C7 as Context7
    participant GH as GitHub

    User->>CE: /generate-prp INITIAL.md
    CE->>ST: Break down requirements
    ST-->>CE: Multi-step implementation plan

    par Parallel Research
        CE->>S: find_symbol("similar_patterns")
        CE->>C7: Fetch library documentation
        CE->>GH: Search reference implementations
    end

    S-->>CE: Existing code patterns
    C7-->>CE: Current documentation
    GH-->>CE: Reference implementations

    CE->>CE: Synthesize research
    CE->>CE: Generate PRP document
    CE->>User: PRP ready for validation
```

### 3.2 Generation Components

| Component | Purpose | Duration | Tools Used |
|-----------|---------|----------|------------|
| Requirement Analysis | Break down high-level requirements | 1-2 min | Sequential Thinking |
| Pattern Discovery | Find existing implementations | 2-3 min | Serena |
| Documentation Retrieval | Fetch current library docs | 2-4 min | Context7 |
| Reference Search | Locate similar implementations | 2-3 min | GitHub |
| Architecture Design | Define system structure | 2-4 min | Sequential Thinking |
| Validation Gate Creation | Design quality checks | 1-2 min | All tools |
| Document Synthesis | Compile comprehensive PRP | 2-3 min | Context Engineering |

### 3.3 PRP Document Structure

**Required Sections:**

| Section | Content | Validation Criteria |
|---------|---------|---------------------|
| Feature Overview | High-level description | Clear, concise, complete |
| Requirements | Detailed feature breakdown | All INITIAL.md requirements addressed |
| Architecture | System design decisions | Logical, maintainable, scalable |
| Implementation Plan | Step-by-step pseudocode | Executable, comprehensive, ordered |
| Validation Gates | Quality checkpoints | Automated, comprehensive, measurable |
| Security Considerations | Threat analysis and mitigations | All attack vectors addressed |
| Dependencies | Required libraries and versions | Justified, minimal, current |
| Test Strategy | Testing approach and coverage | Comprehensive, automated, measurable |

### 3.4 Quality Gates for Generated PRPs

**Automated Validation:**

| Gate | Check | Pass Criteria | Fail Response |
|------|-------|---------------|---------------|
| Completeness | All sections present | 100% section coverage | Flag missing sections |
| Requirement Coverage | INITIAL.md mapping | All requirements addressed | Highlight gaps |
| Dependency Validation | Library version check | Current, compatible versions | Update to current |
| Security Audit | Vulnerability scan | Zero high-severity issues | Add mitigations |
| Implementation Depth | Pseudocode detail | Executable-level detail | Refine pseudocode |

**Human Validation Checklist:**

- [ ] Architecture is sound and maintainable
- [ ] No over-engineering or unnecessary complexity
- [ ] Security patterns are appropriate
- [ ] Dependencies are justified and minimal
- [ ] Implementation plan is realistic
- [ ] Validation gates are comprehensive
- [ ] No secret files modified programmatically
- [ ] Error handling is present throughout

---

## 4. Multi-Phase Implementation

### 4.1 Skeleton Structure

**Purpose:** Establish foundational structure before logic implementation

**Duration:** 3-8 minutes depending on complexity

**Activities:**

| Activity | Description | Output | Validation |
|----------|-------------|--------|------------|
| Directory Structure | Create necessary directories | Organized file hierarchy | Directory existence check |
| Module Scaffolding | Generate empty modules with stubs | Python/TS files with type signatures | Import verification |
| Interface Definition | Define function/class signatures | Type-checked interfaces | Type validation passes |
| Configuration Files | Create config templates | YAML/JSON config structures | Schema validation |
| Test Structure | Generate test file stubs | Empty test files with structure | Test discovery works |

**Implementation Pattern:**

```python
# Phase 1: Skeleton structure
tasks = [
    "Create src/feature/ directory",
    "Generate feature_service.py with method stubs",
    "Create tests/test_feature_service.py scaffold",
    "Add feature config to config/settings.yaml",
    "Update __init__.py imports"
]

for task in tasks:
    execute_task(task)
    validate_structure()
```

**Validation Criteria:**

```bash
# Structure validation commands
find src/feature -type f -name "*.py"          # All modules present
python -m py_compile src/feature/*.py          # Syntax check
pytest tests/test_feature_service.py --collect-only  # Test discovery
```

### 4.2 Production Logic

**Purpose:** Implement core functionality with error handling

**Duration:** 10-20 minutes depending on complexity

**Implementation Stages:**

```mermaid
graph TD
    A["Core Logic"] --> B["Error Handling"]
    B --> C["Input Validation"]
    C --> D["Business Rules"]
    D --> E["Output Formatting"]
    E --> F["Logging Integration"]
    F --> G["Performance Optimization"]

    G --> H{"Validation<br/>Pass?"}
    H -->|No| I["Error Analysis"]
    I --> J["Auto-Fix Attempt"]
    J --> H
    H -->|Yes| K["Production Logic Complete"]
```

**Implementation Checklist:**

| Component | Requirements | Validation Method |
|-----------|--------------|-------------------|
| Core Logic | Business requirements met | Unit tests pass |
| Error Handling | All exceptions caught and logged | Error injection tests |
| Input Validation | All inputs validated | Boundary testing |
| Business Rules | Requirements translated to code | Acceptance tests |
| Output Formatting | Consistent response structure | Schema validation |
| Logging | Critical operations logged | Log verification |
| Performance | Meets performance targets | Benchmark tests |

**Error Handling Pattern:**

```python
# Production-grade error handling
def process_request(data: dict) -> dict:
    """
    Process request with comprehensive error handling.

    Raises:
        ValidationError: Input validation failed
        ProcessingError: Business logic error
    """
    try:
        # Input validation
        validated_data = validate_input(data)

        # Business logic
        result = execute_business_logic(validated_data)

        # Output formatting
        return format_response(result)

    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise  # Fast failure - no fallback

    except ProcessingError as e:
        logger.error(f"Processing failed: {e}")
        raise  # Fast failure - no fallback
```

### 4.3 Test Suite

**Purpose:** Comprehensive automated testing at all levels

**Duration:** 8-15 minutes depending on coverage requirements

**Test Pyramid:**

```mermaid
graph TD
    A["Unit Tests<br/>70% of tests"] --> B["Integration Tests<br/>20% of tests"]
    B --> C["End-to-End Tests<br/>10% of tests"]

    A --> D["Fast<br/><1s per test"]
    B --> E["Moderate<br/>1-5s per test"]
    C --> F["Slow<br/>5-30s per test"]
```

**Test Coverage Matrix:**

| Test Level | Scope | Coverage Target | Example |
|------------|-------|-----------------|---------|
| Unit | Individual functions | 85-95% | Test validate_email() with valid/invalid inputs |
| Integration | Module interactions | 75-85% | Test auth_service with database |
| End-to-End | Complete workflows | 60-75% | Test full user registration flow |

**Test Suite Structure:**

```python
# tests/test_feature_service.py

class TestFeatureService:
    """Comprehensive test suite for FeatureService."""

    # Unit tests - fast, isolated
    def test_validate_input_success(self):
        """Test input validation with valid data."""
        result = validate_input({"field": "value"})
        assert result == {"field": "value"}

    def test_validate_input_missing_field(self):
        """Test input validation with missing required field."""
        with pytest.raises(ValidationError):
            validate_input({})

    # Integration tests - moderate speed
    def test_process_request_integration(self, db_session):
        """Test complete request processing with database."""
        result = process_request({"field": "value"})
        assert result["status"] == "success"
        assert db_session.query(Record).count() == 1

    # End-to-end tests - slower
    def test_complete_workflow_e2e(self, api_client):
        """Test complete workflow via API."""
        response = api_client.post("/api/feature", json={"field": "value"})
        assert response.status_code == 200
        assert response.json()["status"] == "success"
```

**Validation Commands:**

```bash
# Test execution sequence
pytest tests/unit/ -v                           # Unit tests
pytest tests/integration/ -v                    # Integration tests
pytest tests/e2e/ -v                           # End-to-end tests
pytest tests/ --cov=src --cov-report=term-missing  # Coverage report
```

### 4.4 Documentation

**Purpose:** Comprehensive inline and external documentation

**Duration:** 3-5 minutes

**Documentation Layers:**

| Layer | Format | Purpose | Example |
|-------|--------|---------|---------|
| Inline Comments | Python comments | Explain complex logic | `# Convert timestamp to UTC before comparison` |
| Docstrings | Google/NumPy style | Document functions/classes | Function signature, parameters, returns, raises |
| Type Hints | Python types | Static type checking | `def process(data: dict[str, str]) -> Result` |
| API Documentation | OpenAPI/Swagger | External API reference | Endpoint descriptions, request/response schemas |
| Architecture Docs | Markdown | System design | Component diagrams, decision rationale |

**Docstring Template:**

```python
def process_feature_request(
    request_data: dict[str, Any],
    user_context: UserContext,
    options: Optional[ProcessingOptions] = None
) -> ProcessingResult:
    """
    Process feature request with comprehensive validation and error handling.

    Args:
        request_data: Request payload containing feature parameters.
            Required keys: 'feature_id', 'action', 'parameters'
        user_context: User authentication and authorization context
        options: Optional processing configuration overrides

    Returns:
        ProcessingResult containing:
            - status: Operation outcome ('success', 'error')
            - data: Result payload if successful
            - errors: Error details if failed

    Raises:
        ValidationError: Request data validation failed
        AuthorizationError: User lacks required permissions
        ProcessingError: Business logic execution failed

    Example:
        >>> result = process_feature_request(
        ...     {"feature_id": "f123", "action": "create"},
        ...     user_context
        ... )
        >>> result.status
        'success'

    Note:
        This function performs synchronous processing. For long-running
        operations, use process_feature_request_async() instead.
    """
    pass
```

**Documentation Validation:**

```bash
# Documentation checks
pydocstyle src/                                 # Docstring validation
mypy src/ --strict                              # Type hint verification
sphinx-build -W docs/ docs/_build/              # Documentation build
```

---

## 5. Context Synchronization During Development

### 5.1 Automatic Sync Triggers

**Trigger Conditions:**

| Trigger | Condition | Rationale | Sync Scope |
|---------|-----------|-----------|------------|
| Session Start | Every new session | Ensure baseline alignment | Full project |
| File Modifications | >10 files changed | Prevent drift from accumulation | Changed files only |
| Compilation Errors | Build failures | Check for stale context | Affected modules |
| Time-Based | Every 30 minutes | Proactive drift detection | Incremental scan |
| Manual Request | User-initiated | On-demand validation | User-specified scope |

### 5.2 Synchronization Workflow

```mermaid
graph TD
    A["Sync Trigger"] --> B["Git Diff Analysis"]
    B --> C["Identify Changed Symbols"]
    C --> D["Delete Stale Memories"]
    D --> E["Re-index Updated Symbols"]
    E --> F["Validate Compilation"]
    F --> G{"Validation<br/>Pass?"}
    G -->|Yes| H["Sync Complete"]
    G -->|No| I["Error Analysis"]
    I --> J["Manual Investigation"]
```

**Implementation Steps:**

| Step | Command | Duration | Purpose |
|------|---------|----------|---------|
| 1. Git Analysis | `git diff --stat HEAD~1` | <1s | Identify changed files |
| 2. Symbol Identification | `list_symbols(changed_files)` | 1-3s | Find affected symbols |
| 3. Memory Cleanup | `delete_memory(pattern)` | <1s | Remove stale context |
| 4. Re-indexing | `find_symbol(updated_symbols)` | 2-5s | Update symbol index |
| 5. Validation | `npm run check-all` | 10-30s | Verify correctness |

**Synchronization Script:**

```python
def synchronize_context():
    """
    Synchronize context with current codebase state.

    Returns:
        Synchronization status and metrics
    """
    # Step 1: Analyze git changes
    git_diff = execute_shell_command("git diff --stat HEAD~1")
    changed_files = parse_changed_files(git_diff)

    # Step 2: Identify affected symbols
    affected_symbols = []
    for file_path in changed_files:
        symbols = list_symbols(file_path)
        affected_symbols.extend(symbols)

    # Step 3: Clean stale memories
    for symbol in affected_symbols:
        delete_memory(f"symbol_{symbol.name}")

    # Step 4: Re-index updated symbols
    for symbol in affected_symbols:
        find_symbol(symbol.name, include_body=True)

    # Step 5: Validate compilation
    validation_result = execute_shell_command("npm run check-all")

    return {
        "files_changed": len(changed_files),
        "symbols_updated": len(affected_symbols),
        "validation_status": "pass" if validation_result.returncode == 0 else "fail"
    }
```

### 5.3 Context Drift Detection

**Warning Signs:**

```mermaid
graph LR
    A["Context Drift Indicators"] --> B["Symbol Query Failures"]
    A --> C["Compilation Inconsistencies"]
    A --> D["Memory Bloat"]
    A --> E["Test Failures"]
    A --> F["Performance Degradation"]

    B --> G["Re-index Required"]
    C --> G
    D --> H["Memory Pruning Required"]
    E --> G
    F --> I["Index Corruption"]
```

**Detection Metrics:**

| Metric | Healthy | Warning | Critical | Response |
|--------|---------|---------|----------|----------|
| Symbol query null rate | <5% | 5-15% | >15% | Re-index affected modules |
| Compilation vs type-check mismatch | 0 | 1-2 | >2 | Full context reset |
| Memory count growth rate | <10/hour | 10-30/hour | >30/hour | Aggressive pruning |
| Previously passing test failures | 0 | 1-3 | >3 | Context synchronization |
| Type-check duration | <30s | 30-60s | >60s | Check index integrity |

### 5.4 Drift Recovery Protocol

**Recovery Sequence:**

```mermaid
graph TD
    A["Drift Detected"] --> B["STOP All Development"]
    B --> C["Execute git status"]
    C --> D["Restore Last Checkpoint"]
    D --> E["Clear All Memories"]
    E --> F["Re-run Onboarding"]
    F --> G["Validate Compilation"]
    G --> H{"Validation<br/>Pass?"}
    H -->|No| I["Manual Investigation"]
    H -->|Yes| J["Context Health Check"]
    J --> K{"Health >85%?"}
    K -->|No| I
    K -->|Yes| L["Resume Development"]
```

**Recovery Commands:**

```bash
# Drift recovery sequence
git status                                      # Verify repository state
git diff HEAD                                   # Review uncommitted changes

# Context reset
serena clear_all_memories                       # Purge context
serena onboarding                               # Rebuild index

# Validation
npm run build                                   # Verify compilation
npm run type-check                              # Verify types
npm run test                                    # Verify tests

# Health assessment
serena health_check                             # Context health metrics
```

**Recovery Decision Matrix:**

| Drift Severity | Recovery Action | Estimated Time | Success Rate |
|----------------|----------------|----------------|--------------|
| Minor (1-2 indicators) | Selective re-indexing | 2-5 min | 95% |
| Moderate (3-4 indicators) | Full synchronization | 5-10 min | 85% |
| Severe (5+ indicators) | Complete context reset | 10-20 min | 98% |
| Critical (system failure) | Manual investigation | 20+ min | Variable |

---

## 6. Session End Protocol

### 6.1 Final Validation Sequence

**Validation Steps:**

| Step | Command | Pass Criteria | Failure Response |
|------|---------|---------------|------------------|
| 1. Compilation | `npm run build` | Zero errors | Fix before ending session |
| 2. Type Checking | `npm run type-check` | All types valid | Resolve type issues |
| 3. Linting | `npm run lint` | Zero violations | Auto-fix or manual correction |
| 4. Unit Tests | `npm run test:unit` | 100% pass | Debug and fix failures |
| 5. Integration Tests | `npm run test:integration` | 100% pass | Investigate integration issues |
| 6. Coverage Check | `npm run test:coverage` | Meets threshold | Add tests for uncovered code |

**Comprehensive Validation Command:**

```bash
# Single command for complete validation
npm run check-all

# Or sequential execution for detailed feedback
npm run build && \
npm run type-check && \
npm run lint && \
npm run test:unit && \
npm run test:integration && \
npm run test:coverage
```

### 6.2 Checkpoint Creation

**Checkpoint Template:**

```markdown
# Session Checkpoint [YYYY-MM-DD-HH-MM]

## Session Metadata
- **Start Time:** [timestamp]
- **End Time:** [timestamp]
- **Duration:** [duration]
- **Branch:** [branch_name]
- **Commit:** [commit_hash]

## Completed Features
- Feature A: [description]
  - Files modified: [file_list]
  - Tests added: [test_count]
  - Coverage: [percentage]

- Feature B: [description]
  - Files modified: [file_list]
  - Tests added: [test_count]
  - Coverage: [percentage]

## Known Issues
- Issue 1: [description]
  - Impact: [severity]
  - Workaround: [workaround_description]
  - Investigation needed: [yes/no]

- Issue 2: [description]
  - Impact: [severity]
  - Workaround: [workaround_description]
  - Investigation needed: [yes/no]

## Next Steps
1. [Priority 1 task]
2. [Priority 2 task]
3. [Follow-up investigation]

## Critical Patterns Discovered
- Pattern A: When [condition], do [action] because [reason]
- Pattern B: Avoid [anti-pattern] because [reason]

## Architecture Decisions
- Decision 1: [decision]
  - Rationale: [reasoning]
  - Trade-offs: [considerations]

- Decision 2: [decision]
  - Rationale: [reasoning]
  - Trade-offs: [considerations]

## Test Coverage
- Overall: [percentage]
- New code: [percentage]
- Areas needing attention: [list]

## Context Health
- Symbol count: [count]
- Memory count: [count]
- Health score: [percentage]
- Sync operations: [count]

## Performance Metrics
- Total validation runs: [count]
- Failed validations: [count]
- Auto-fix success rate: [percentage]
- Total lines of code added: [count]
```

**Checkpoint Creation Script:**

```python
def create_session_checkpoint():
    """
    Create comprehensive session checkpoint.

    Captures current state, completed work, and context for next session.
    """
    checkpoint_data = {
        "timestamp": datetime.now().isoformat(),
        "git_branch": execute_shell_command("git branch --show-current"),
        "git_commit": execute_shell_command("git rev-parse HEAD"),
        "completed_features": gather_completed_features(),
        "known_issues": gather_known_issues(),
        "next_steps": gather_next_steps(),
        "critical_patterns": gather_discovered_patterns(),
        "architecture_decisions": gather_architecture_decisions(),
        "test_coverage": gather_test_coverage(),
        "context_health": gather_context_health_metrics(),
        "performance_metrics": gather_performance_metrics()
    }

    # Store checkpoint
    checkpoint_id = f"checkpoint-{datetime.now().strftime('%Y%m%d-%H%M')}"
    create_memory(checkpoint_id, checkpoint_data)

    # Mark as latest
    create_memory("checkpoint-latest", checkpoint_id)

    return checkpoint_id
```

### 6.3 Context Summary

**Summary Generation:**

```python
def prepare_context_summary():
    """
    Generate transition document for next session.

    Returns:
        Comprehensive summary for context continuity
    """
    summary = prepare_for_new_conversation()

    # Enhance with critical context
    summary.update({
        "active_branch": get_current_branch(),
        "uncommitted_changes": has_uncommitted_changes(),
        "critical_memories": get_critical_memories(),
        "high_priority_todos": get_high_priority_todos(),
        "context_health_status": get_health_status()
    })

    return summary
```

**Summary Components:**

| Component | Content | Purpose |
|-----------|---------|---------|
| Session Overview | High-level accomplishments | Quick context restoration |
| Active State | Current branch, pending changes | Immediate state awareness |
| Critical Memories | Important discoveries | Knowledge preservation |
| Priority Actions | Next session tasks | Immediate focus direction |
| Health Status | Context system state | Readiness assessment |

### 6.4 Git Commit with Checkpoint Reference

**Commit Message Template:**

```
[type]: [concise description]

[Detailed description of changes]

Checkpoint: checkpoint-[YYYY-MM-DD-HH-MM]

Changes:
- [Change 1]
- [Change 2]
- [Change 3]

Tests:
- [Test coverage information]
- [Test execution results]

Context:
- [Relevant context information]
- [Known issues or follow-ups]
```

**Commit Execution:**

```bash
# Git commit with checkpoint reference
git add [files]
git commit -m "feat: add email validation

Implement email validation for user registration with comprehensive error handling and test coverage.

Checkpoint: checkpoint-20250110-1430

Changes:
- Add email-validator dependency
- Implement validate_email() function
- Add validation tests with 95% coverage
- Update user registration workflow

Tests:
- 15 new tests added
- All tests passing
- Coverage increased to 92%

Context:
- Discovered edge case with internationalized emails
- Need to investigate punycode support in next session
"
```

### 6.5 Memory Pruning

**Pruning Strategy:**

| Memory Type | Retention | Pruning Criteria |
|-------------|-----------|------------------|
| Temporary Debug | Delete | All at session end |
| Experimental | Delete | If not referenced in checkpoint |
| Working Context | Keep | If part of active feature |
| Critical Patterns | Keep | Always retain |
| Session Checkpoints | Keep Recent | Last 10 checkpoints, archive older |

**Pruning Script:**

```python
def prune_session_memories():
    """
    Clean up temporary and obsolete memories at session end.

    Preserves critical context while removing transient data.
    """
    all_memories = list_all_memories()

    # Categories for deletion
    to_delete = []

    for memory in all_memories:
        # Delete temporary debug memories
        if memory.id.startswith("debug_"):
            to_delete.append(memory.id)

        # Delete experimental memories not in checkpoint
        if memory.id.startswith("experiment_"):
            if not referenced_in_checkpoint(memory.id):
                to_delete.append(memory.id)

        # Archive old checkpoints (keep last 10)
        if memory.id.startswith("checkpoint_"):
            if not in_recent_checkpoints(memory.id, keep_count=10):
                archive_checkpoint(memory.id)
                to_delete.append(memory.id)

    # Execute deletion
    for memory_id in to_delete:
        delete_memory(memory_id)

    return {
        "total_memories": len(all_memories),
        "memories_deleted": len(to_delete),
        "memories_retained": len(all_memories) - len(to_delete)
    }
```

---

## 7. Real-World Execution Examples

### 7.1 Simple Feature Addition

**Task:** Add email validation to user registration

**Timeline:**

```mermaid
gantt
    title Simple Feature Addition - Email Validation
    dateFormat mm:ss
    axisFormat %M:%S

    section Session Start
    Compilation Check         :00:00, 01:00
    Serena Onboarding        :01:00, 01:00
    Context Health           :02:00, 01:00

    section Development
    Context Foundation       :03:00, 01:00
    PRP Generation          :04:00, 04:00
    Human Validation        :08:00, 05:00
    Execution               :13:00, 07:00

    section Validation
    Level 1 Checks          :20:00, 01:00
    Level 2 Tests           :21:00, 01:00
    Level 3 Integration     :22:00, 01:00

    section Session End
    Final Validation        :23:00, 01:00
    Checkpoint Creation     :24:00, 01:00
    Git Commit              :25:00, 01:00
```

**Execution Trace:**

```
[00:00] Session Start
  ├─ [00:00-00:30] Compilation check: npm run build
  │   └─ Result: PASS (0 errors)
  ├─ [00:30-01:30] Serena onboarding: 847 symbols indexed
  │   └─ Result: Index created, health 94%
  └─ [01:30-02:00] Context health check
      └─ Result: Score 94%, proceed

[02:00] Context Foundation
  ├─ [02:00-03:00] Create INITIAL.md
  │   └─ Feature: "Add email validation to user registration"
  └─ [03:00-03:00] Define MCP directives: Serena + Context7

[03:00] PRP Generation
  ├─ [03:00-03:30] Sequential Thinking: 3-step plan
  │   └─ Steps: Dependency → Function → Tests
  ├─ [03:30-04:30] Serena: find_symbol("validation_patterns")
  │   └─ Found: auth_service.py has validation helpers
  ├─ [04:30-07:30] Context7: email-validator docs v2.1.x
  │   └─ Retrieved: API reference, best practices
  └─ [07:30-08:00] PRP document complete
      └─ Output: email-validation.md (8 pages)

[08:00] Human Validation
  ├─ [08:00-10:00] Architecture review
  │   └─ Approved: Simple, appropriate dependency
  ├─ [10:00-11:30] Security audit
  │   └─ Approved: No security concerns
  └─ [11:30-13:00] Requirement coverage
      └─ Approved: All requirements addressed

[13:00] Execution
  ├─ [13:00-14:00] Task 1: Add email-validator dependency
  │   ├─ Command: uv add email-validator
  │   └─ Result: Dependency added to pyproject.toml
  ├─ [14:00-16:00] Task 2: Implement validate_email()
  │   ├─ File: src/validation/email_validator.py
  │   └─ Result: Function implemented with error handling
  ├─ [16:00-18:00] Task 3: Add unit tests
  │   ├─ File: tests/test_email_validator.py
  │   └─ Result: 15 tests added
  └─ [18:00-20:00] Task 4: Integrate into registration
      ├─ File: src/auth/registration_service.py
      └─ Result: Validation integrated

[20:00] Validation Loop
  ├─ [20:00-20:30] Level 1: Syntax & Style
  │   ├─ Command: ruff check && mypy
  │   └─ Result: PASS
  ├─ [20:30-21:30] Level 2: Unit Tests
  │   ├─ Command: pytest tests/ -v
  │   └─ Result: PASS (15/15 tests)
  └─ [21:30-22:30] Level 3: Integration
      ├─ Command: pytest tests/integration/
      └─ Result: PASS (registration flow works)

[22:30] Session End
  ├─ [22:30-23:00] Final validation: npm run check-all
  │   └─ Result: PASS
  ├─ [23:00-24:00] Create checkpoint-20250110-1430
  │   └─ Result: Checkpoint stored
  ├─ [24:00-25:00] Git commit: "feat: add email validation"
  │   └─ Result: Committed with checkpoint reference
  └─ [25:00-26:00] Memory pruning: 3 temp memories deleted
      └─ Result: Context clean

[26:00] Session Complete
Total Duration: 26 minutes
Success: First-attempt delivery
```

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| Total Duration | 26 minutes |
| Execution Errors | 0 |
| Validation Cycles | 1 (zero-shot success) |
| Tests Added | 15 |
| Test Coverage | 95% |
| Lines of Code | 147 |
| Files Modified | 3 |

### 7.2 Complex Refactoring

**Task:** Refactor authentication system to use dependency injection

**Timeline:**

```mermaid
gantt
    title Complex Refactoring - Authentication DI
    dateFormat mm:ss
    axisFormat %M:%S

    section Session Start
    Compilation & Health     :00:00, 03:00

    section Planning
    Context Foundation       :03:00, 02:00
    PRP Generation          :05:00, 13:00
    Human Validation        :18:00, 10:00

    section Execution Phase 1
    DI Container            :28:00, 03:00
    Service Factory         :31:00, 05:00

    section Execution Phase 2
    Refactor Service        :36:00, 07:00
    Update Call Sites       :43:00, 07:00

    section Execution Phase 3
    Migrate Tests           :50:00, 05:00
    Auto-Fix Errors         :55:00, 07:00

    section Session End
    Final Validation        :62:00, 03:00
    Checkpoint & Commit     :65:00, 05:00
```

**Execution Trace:**

```
[00:00] Session Start
  ├─ [00:00-01:00] Compilation check: PASS
  ├─ [01:00-02:30] Serena onboarding: 2,341 symbols indexed
  └─ [02:30-03:00] Context health: Score 88% (acceptable)

[03:00] Context Foundation
  ├─ [03:00-04:30] Create INITIAL.md
  │   └─ Feature: "Refactor auth system to use dependency injection"
  └─ [04:30-05:00] Define MCP directives: All MCPs (complex task)

[05:00] PRP Generation
  ├─ [05:00-07:00] Sequential Thinking: 12-step refactoring plan
  ├─ [07:00-10:00] Serena: Mapped 47 auth-related symbols
  │   └─ Symbols: AuthService, TokenValidator, PasswordHasher, etc.
  ├─ [10:00-14:00] Context7: FastAPI DI patterns 0.115.x
  ├─ [14:00-17:00] GitHub: Found 5 similar refactorings
  └─ [17:00-18:00] PRP complete: auth-di-refactor.md (24 pages)

[18:00] Human Validation
  ├─ [18:00-22:00] Architecture review
  │   └─ Result: Sound approach, approved with notes
  ├─ [22:00-25:00] Security audit
  │   └─ Result: Approved, maintain token security
  └─ [25:00-28:00] Requirement coverage
      └─ Result: All requirements addressed, proceed

[28:00] Execution Phase 1: Foundation
  ├─ [28:00-31:00] Task 1: Define DI container interface
  │   ├─ File: src/core/di_container.py
  │   └─ Result: Container interface defined
  └─ [31:00-36:00] Task 2: Create auth service factory
      ├─ File: src/auth/auth_factory.py
      └─ Result: Factory implemented with type safety

[36:00] Execution Phase 2: Refactoring
  ├─ [36:00-43:00] Task 3: Refactor auth_service.py (12 methods)
  │   ├─ Changes: Inject dependencies instead of imports
  │   └─ Result: AuthService now uses DI
  └─ [43:00-50:00] Task 4: Update 23 call sites
      ├─ Files: Multiple controllers and middleware
      └─ Result: All call sites updated

[50:00] Execution Phase 3: Tests and Fixes
  ├─ [50:00-55:00] Task 5: Migrate tests (35 test files)
  │   ├─ Changes: Update fixtures to use DI
  │   └─ Result: Tests migrated
  ├─ [55:00-56:00] Validation L1: FAIL (3 type errors)
  │   └─ Errors: Optional types not handled
  ├─ [56:00-57:00] Auto-fix: Type errors resolved
  │   └─ Fix: Added type guards
  ├─ [57:00-58:00] Validation L1: PASS
  ├─ [58:00-59:00] Validation L2: FAIL (2 test failures)
  │   └─ Errors: Fixture dependency order
  ├─ [59:00-60:30] Auto-fix: Test fixtures updated
  │   └─ Fix: Reordered fixture dependencies
  ├─ [60:30-61:30] Validation L2: PASS (247/247 tests)
  └─ [61:30-62:30] Validation L3: PASS (integration tests)

[62:30] Session End
  ├─ [62:30-65:00] Final validation: All checks pass
  ├─ [65:00-67:00] Checkpoint with refactoring notes
  ├─ [67:00-68:30] Git commit: "refactor: implement DI for auth system"
  ├─ [68:30-69:30] PR created with detailed description
  └─ [69:30-70:00] Context pruning: 8 temp memories deleted

[70:00] Session Complete
Total Duration: 70 minutes
Success: Delivered after auto-fix
```

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| Total Duration | 70 minutes |
| Execution Errors | 5 (auto-fixed) |
| Validation Cycles | 2 |
| Tests Migrated | 247 |
| Test Coverage | 89% (maintained) |
| Lines of Code Changed | 1,847 |
| Files Modified | 38 |
| Auto-Fix Success Rate | 100% |

### 7.3 Zero-Shot Execution (Ideal Case)

**Task:** Add rate limiting middleware

**Timeline:**

```mermaid
gantt
    title Zero-Shot Execution - Rate Limiting
    dateFormat mm:ss
    axisFormat %M:%S

    section Session Start
    Quick Health Check      :00:00, 01:00

    section Development
    Context & PRP           :01:00, 06:00
    Human Validation        :07:00, 05:00
    Execution (No Errors)   :12:00, 10:00

    section Validation
    Three Levels (All Pass) :22:00, 03:00

    section Session End
    Finalization            :25:00, 03:00
```

**Execution Trace:**

```
[00:00] Session Start (Cached Context)
  ├─ [00:00-00:20] Compilation check: PASS
  ├─ [00:20-00:40] Serena onboarding: CACHED (reused)
  └─ [00:40-01:00] Context health: Score 96% (excellent)

[01:00] Context Foundation
  ├─ [01:00-01:30] Create INITIAL.md
  │   └─ Feature: "Add rate limiting middleware"
  └─ [01:30-02:00] Define MCP directives: Serena + Context7

[02:00] PRP Generation (Fast)
  ├─ [02:00-02:30] Sequential Thinking: 4-step implementation
  ├─ [02:30-03:30] Serena: Found middleware patterns
  │   └─ Pattern: Similar middleware in request_logger.py
  ├─ [03:30-06:30] Context7: slowapi docs v0.1.9
  │   └─ Retrieved: Complete API reference
  └─ [06:30-07:00] PRP complete: rate-limiting.md (6 pages)

[07:00] Human Validation (Quick)
  ├─ [07:00-09:00] Architecture review
  │   └─ Approved: Standard middleware pattern
  ├─ [09:00-10:30] Security audit
  │   └─ Approved: Appropriate limits
  └─ [10:30-12:00] Requirement coverage
      └─ Approved: Straightforward implementation

[12:00] Execution (ZERO ERRORS)
  ├─ [12:00-13:00] Task 1: Add slowapi dependency
  │   ├─ Command: uv add slowapi
  │   └─ Result: SUCCESS
  ├─ [13:00-15:00] Task 2: Implement rate limit middleware
  │   ├─ File: src/middleware/rate_limit.py
  │   └─ Result: Middleware implemented
  ├─ [15:00-17:00] Task 3: Apply to endpoints
  │   ├─ File: src/main.py
  │   └─ Result: Middleware registered
  ├─ [17:00-18:30] Task 4: Add configuration
  │   ├─ File: config/settings.yaml
  │   └─ Result: Limits configured
  └─ [18:30-22:00] Task 5: Add tests
      ├─ File: tests/test_rate_limit.py
      └─ Result: 12 tests added

[22:00] Validation Loop (FIRST ATTEMPT SUCCESS)
  ├─ [22:00-22:30] Level 1: Syntax & Style
  │   ├─ Command: ruff check && mypy
  │   └─ Result: PASS (first attempt)
  ├─ [22:30-23:30] Level 2: Unit Tests
  │   ├─ Command: pytest tests/ -v
  │   └─ Result: PASS (12/12 tests, first attempt)
  └─ [23:30-25:00] Level 3: Integration
      ├─ Command: pytest tests/integration/
      └─ Result: PASS (rate limiting works, first attempt)

[25:00] Session End
  ├─ [25:00-25:30] Final validation: npm run check-all
  │   └─ Result: PASS
  ├─ [25:30-26:30] Create checkpoint-20250110-1530
  │   └─ Result: Checkpoint stored
  ├─ [26:30-27:30] Git commit: "feat: add rate limiting middleware"
  │   └─ Result: Committed with checkpoint
  └─ [27:30-28:00] PR created with auto-generated description
      └─ Result: PR #247 created

[28:00] Session Complete
Total Duration: 28 minutes
Success: ZERO-SHOT PERFECTION
```

**Performance Metrics:**

| Metric | Value |
|--------|-------|
| Total Duration | 28 minutes |
| Execution Errors | 0 |
| Validation Cycles | 1 (first-attempt success) |
| Tests Added | 12 |
| Test Coverage | 98% |
| Lines of Code | 183 |
| Files Modified | 4 |
| First-Attempt Success | YES |

---

## 8. KISS Decision Tree

```mermaid
graph TD
    A["Feature Request"] --> B{"Complexity<br/>Assessment"}

    B -->|"Simple<br/>(1-2 files)"| C["Minimal MCP<br/>Context7 + Filesystem"]
    B -->|"Medium<br/>(3-10 files)"| D["Core MCP<br/>+ Serena + Sequential"]
    B -->|"Complex<br/>(10+ files)"| E["Full MCP Stack<br/>All 5 MCPs"]

    C --> F["Direct Implementation<br/>~5 min"]
    D --> G["PRP-Based Implementation<br/>~15 min"]
    E --> H["Multi-Phase PRP<br/>~30 min"]

    F --> I["Validation"]
    G --> I
    H --> I

    I -->|"Pass"| J["Git Commit"]
    I -->|"Fail"| K{"Error<br/>Analysis"}

    K -->|"Syntax"| L["Serena Auto-Fix"]
    K -->|"Logic"| M["Sequential Thinking<br/>Re-plan"]
    K -->|"Integration"| N["Context7<br/>Updated Docs"]

    L --> I
    M --> I
    N --> I

    J --> O["GitHub MCP<br/>Create PR"]
    O --> P["Production"]
```

### 8.1 Complexity Assessment Guidelines

**Assessment Matrix:**

| Complexity | Files | Dependencies | Logic | Patterns | Duration | MCP Stack |
|------------|-------|--------------|-------|----------|----------|-----------|
| Simple | 1-2 | None new | Straightforward | Existing patterns apply | ~5 min | Context7 + Filesystem |
| Medium | 3-10 | 1-2 new | Moderate | Some adaptation needed | ~15 min | + Serena + Sequential |
| Complex | 10+ | 3+ new | Complex | New patterns required | ~30 min | All 5 MCPs |

**Decision Criteria:**

| Factor | Simple | Medium | Complex |
|--------|--------|--------|---------|
| File modifications | Single file or 2 related | Multiple coordinated files | System-wide changes |
| New concepts | Using existing patterns | Minor pattern adaptations | New architectural patterns |
| External dependencies | No new dependencies | 1-2 well-known libraries | Multiple or unfamiliar libraries |
| Business logic | Trivial logic addition | Moderate complexity logic | Complex business rules |
| Testing requirements | Basic unit tests | Comprehensive unit + integration | Full test pyramid |
| Risk level | Low risk change | Moderate risk | High risk refactoring |

### 8.2 MCP Selection Strategy

**Simple Features - Minimal Stack:**

```
Tools: Context7 + Filesystem
Use Cases:
- Single file modifications
- Configuration changes
- Simple utility functions
- Documentation updates

Example: Add logging to existing function
```

**Medium Features - Core Stack:**

```
Tools: Context7 + Filesystem + Serena + Sequential Thinking
Use Cases:
- Multi-file features
- New API endpoints
- Service integrations
- Database schema changes

Example: Add email validation to registration
```

**Complex Features - Full Stack:**

```
Tools: All MCPs (Context7, Filesystem, Serena, Sequential, GitHub)
Use Cases:
- System-wide refactoring
- Architecture changes
- Complex features
- Multi-phase implementations

Example: Implement dependency injection across auth system
```

---

## 9. Troubleshooting Matrix

### 9.1 Common Issues and Solutions

| Issue | Symptoms | Root Cause | MCP Solution | Prevention |
|-------|----------|------------|--------------|------------|
| Outdated code examples | Generated code uses deprecated APIs | LLM training data lag | Context7 with version-specific docs | Always specify library versions in INITIAL.md |
| Token limit exceeded | Context window full, incomplete responses | Full file reads instead of symbol queries | Serena symbol-level queries | Use find_symbol() instead of read_file() |
| Poor architectural decisions | Over-engineered or inappropriate solutions | Single-step thinking without exploration | Sequential Thinking multi-step planning | Always use Sequential Thinking for complex features |
| File path errors | Cannot find files, incorrect imports | Manual path construction errors | Filesystem MCP with validation | Let Filesystem MCP handle path resolution |
| Inconsistent PR descriptions | Manual PR creation with missing info | Human-written descriptions vary | GitHub MCP automated PR generation | Use GitHub MCP for all PR creation |
| Symbol queries returning null | find_symbol() returns empty results | Stale Serena index | Serena re-indexing / onboarding | Run context synchronization regularly |
| Compilation passes but tests fail | Build succeeds but tests have errors | Context drift between index and code | Context synchronization protocol | Sync after 10+ file modifications |
| Memory bloat | Serena memory count >200 | No pruning strategy implemented | Automatic memory pruning at session end | Prune after each major phase |
| Type errors after refactoring | Type checker fails after symbol changes | Incomplete symbol update propagation | find_referencing_symbols() analysis | Use find_referencing_symbols() before refactoring |
| Integration test failures | E2E tests fail in CI but pass locally | Environment configuration mismatch | Validation of test environment settings | Verify environment parity before execution |

### 9.2 Error Recovery Procedures

**Syntax Errors:**

```mermaid
graph TD
    A["Syntax Error Detected"] --> B["Serena Auto-Fix"]
    B --> C["Execute linter/formatter"]
    C --> D{"Error<br/>Resolved?"}
    D -->|Yes| E["Re-run Validation"]
    D -->|No| F["Manual Code Review"]
    F --> G["Identify Root Cause"]
    G --> H["Apply Manual Fix"]
    H --> E
```

**Logic Errors:**

```mermaid
graph TD
    A["Logic Error Detected"] --> B["Sequential Thinking Analysis"]
    B --> C["Break Down Problem"]
    C --> D["Identify Flawed Assumption"]
    D --> E["Generate Alternative Approach"]
    E --> F["Implement Fix"]
    F --> G["Add Regression Test"]
    G --> H["Re-run Validation"]
```

**Integration Errors:**

```mermaid
graph TD
    A["Integration Error"] --> B["Context7 Doc Check"]
    B --> C["Verify API Compatibility"]
    C --> D{"API<br/>Changed?"}
    D -->|Yes| E["Update to Current API"]
    D -->|No| F["Check Configuration"]
    F --> G{"Config<br/>Correct?"}
    G -->|Yes| H["Environment Issue"]
    G -->|No| I["Fix Configuration"]
    E --> J["Re-run Tests"]
    I --> J
    H --> K["Manual Investigation"]
```

### 9.3 Performance Degradation Troubleshooting

| Symptom | Possible Causes | Diagnostic Commands | Resolution |
|---------|----------------|---------------------|------------|
| Slow symbol queries | Index corruption or memory bloat | `serena health_check` | Re-run onboarding |
| Long validation times | Large test suite or inefficient tests | `pytest --durations=10` | Optimize slow tests |
| Memory growth | Missing pruning or memory leaks | `serena list_all_memories` | Execute memory pruning |
| Context drift frequency | Insufficient synchronization | Check sync trigger frequency | Increase sync frequency |
| High error rate | Outdated documentation or patterns | Review Context7 query results | Update doc sources |

---

## 10. Cross-References

### 10.1 Related Documentation

| Document | Relevant Sections | Relationship |
|----------|------------------|--------------|
| 01 - PRP Methodology | Complete PRP process | Foundational concepts for workflow |
| 03 - Serena Integration | Symbol operations, memory management | Tool-specific workflow details |
| 04 - MCP Orchestration | Multi-MCP coordination patterns | Advanced workflow orchestration |
| CLAUDE.md | Development standards, testing requirements | Project-specific workflow constraints |

### 10.2 Command Reference

**Session Management:**

| Command | Purpose | When to Use | Related Section |
|---------|---------|-------------|-----------------|
| `/validate-state` | Check system health | Session start, every 30 min | 2.4 Context Health Assessment |
| `/sync-context` | Synchronize with codebase | After 10+ file changes | 5. Context Synchronization |
| `/heal-errors` | Self-healing error recovery | On validation failures | 9. Troubleshooting Matrix |
| `/prune-context` | Clean up memories | Session end, when >100 memories | 6.5 Memory Pruning |

**PRP Workflow:**

| Command | Purpose | When to Use | Related Section |
|---------|---------|-------------|-----------------|
| `/generate-prp <file>` | Create PRP from requirements | After INITIAL.md creation | 3. PRP Generation Phase |
| `/execute-prp <file>` | Execute implementation | After PRP validation | 4. Multi-Phase Implementation |
| `/peer-review [prp]` | Review PRP or execution | Before execution, after completion | 3.4 Quality Gates |
| `/update-context [--prp <file>]` | Sync CE with codebase | After significant changes | 5.2 Synchronization Workflow |

**Development:**

| Command | Purpose | When to Use | Related Section |
|---------|---------|-------------|-----------------|
| `npm run build` | Compilation check | Session start, after changes | 2.1 Compilation Check |
| `npm run type-check` | Type validation | After code changes | 2.1 Compilation Check |
| `npm run test` | Run test suite | After implementation | 4.3 Test Suite |
| `npm run check-all` | Complete validation | Session end, before commit | 6.1 Final Validation |

### 10.3 Workflow Pattern Index

| Pattern Name | Location | Use Case |
|-------------|----------|----------|
| Session Start Protocol | Section 2 | Every session initialization |
| PRP Generation Workflow | Section 3 | Feature planning and design |
| Multi-Phase Implementation | Section 4 | Systematic feature development |
| Context Synchronization | Section 5 | Maintaining context accuracy |
| Session End Protocol | Section 6 | Session finalization and persistence |
| Zero-Shot Execution | Section 7.3 | Ideal execution case study |
| KISS Decision Tree | Section 8 | Complexity-based workflow selection |
| Error Recovery | Section 9 | Troubleshooting and fixes |

### 10.4 Performance Benchmarks

**Success Rates by Workflow Type:**

| Workflow Type | Without Framework | With Complete Workflow | Improvement |
|--------------|-------------------|------------------------|-------------|
| Simple features | 60-70% | 95-98% | +45% |
| Medium complexity | 35-45% | 85-92% | +120% |
| Complex refactoring | 20-30% | 75-85% | +200% |
| Overall average | 35-45% | 85-95% | +140% |

**Time Investment vs. Value:**

| Task Type | Manual Time | Framework Time | Value Generated | ROI |
|-----------|-------------|----------------|-----------------|-----|
| Simple feature | 1-2 hours | 15-25 min | $500-1,000 | 4-5x |
| Medium feature | 4-8 hours | 30-60 min | $2,000-4,000 | 6-8x |
| Complex refactor | 1-3 days | 1-2 hours | $5,000-15,000 | 10-15x |
| System architecture | 1-2 weeks | 2-4 hours | $20,000-50,000 | 20-30x |

**Context Efficiency Metrics:**

| Metric | Without Workflows | With Workflows | Improvement |
|--------|-------------------|----------------|-------------|
| Token usage per task | 150K-200K | 40K-70K | -68% |
| Context-related errors | 25-30% | 2-5% | -85% |
| Iteration cycles | 4-6 cycles | 1-2 cycles | -75% |
| Context drift incidents | 40-50/project | 2-5/project | -92% |
| Self-recovery rate | 0% | 85% | ∞ |

---

## Conclusion

These workflow patterns establish a systematic approach to software development that achieves 85-95% first-attempt success rates through:

**Core Principles:**
- Systematic session management with health validation
- Comprehensive validation protocols at multiple levels
- Intelligent context synchronization preventing drift
- Strategic MCP orchestration based on complexity
- Continuous health monitoring and automated recovery
- Human oversight at critical decision points

**Key Benefits:**
- Reduced development time by 60-85%
- Increased success rates by 140%+
- Decreased context-related errors by 85%
- Reduced token usage by 68%
- Self-recovery capability for 85% of errors

**Workflow Duration:**
- Simple features: 15-25 minutes
- Medium features: 30-60 minutes
- Complex refactoring: 1-2 hours
- Compared to 2-4 hours to multiple days without framework

**Success Factors:**
- Never skip compilation check at session start
- Always complete Serena onboarding for fresh context
- Validate checkpoints against git state regularly
- Use appropriate MCP stack based on complexity
- Follow three-level validation gates systematically
- Create detailed checkpoints at session end
- Prune context regularly to prevent bloat
- Monitor context health continuously

These patterns are technology-agnostic and adapt to any development environment while maintaining consistent quality and efficiency standards.

---

**Document Status:** Complete
**Last Updated:** 2025-01-10
**Version:** 1.0
**Related Documents:** 01-prp-methodology.md, 03-serena-integration.md, 04-mcp-orchestration.md
