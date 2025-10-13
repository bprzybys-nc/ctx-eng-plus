# PRP Decomposition Patterns

Practical patterns and examples for breaking down large PRPs into manageable sub-PRPs.

## Pattern 1: Phase-Based Decomposition

**When to Use**: PRP has 5+ sequential or semi-independent phases

**Structure**:
```
PRP-X.0: [Feature Name] Framework (Meta-PRP)
├─ PRP-X.1: Phase 1 Name
├─ PRP-X.2: Phase 2 Name
├─ PRP-X.3: Phase 3 Name
└─ PRP-X.4: Phase 4 Name
```

### Example: PRP-4 Decomposition

**Before (Monolithic)**:
```
PRP-4: Execute-PRP Command Orchestration
- 1259 lines, 18 hours, HIGH risk
- 6 phases, 27 functions, 30 criteria
- Complexity Score: 71.45/100 → RED
```

**After (Decomposed)**:
```
PRP-4.0: Execute-PRP Framework (Meta-PRP)
├─ PRP-4.1: Blueprint Parser
│   • 3 hours, LOW risk
│   • Parse PRP markdown → structured data
│   • Extract phases, validation gates, checkpoints
│
├─ PRP-4.2: Execution Orchestration Engine
│   • 5 hours, MEDIUM risk
│   • Phase-by-phase execution loop
│   • Progress tracking, logging
│
├─ PRP-4.3: Validation Loop Integration
│   • 4 hours, MEDIUM risk
│   • Run validation gates after each phase
│   • Collect results, determine pass/fail
│
├─ PRP-4.4: Self-Healing Implementation
│   • 4 hours, HIGH risk (isolated!)
│   • Error detection patterns
│   • Automatic retry logic with backoff
│
└─ PRP-4.5: CLI Integration & Testing
    • 2 hours, LOW risk
    • Wire up ce prp execute command
    • End-to-end integration tests
```

**Benefits**:
- Each sub-PRP is GREEN (≤5h, focused scope)
- HIGH risk isolated to PRP-4.4
- Clear dependencies: 4.1 → 4.2 → 4.3 → 4.4 → 4.5
- Can execute incrementally, validate each step

## Pattern 2: Feature-Based Decomposition

**When to Use**: PRP spans multiple functional areas (parser, validator, executor, formatter, etc.)

**Structure**: Split by architectural boundaries

### Example: Data Processing System

**Before (Monolithic)**:
```
PRP-X: Data Processing Pipeline
- 1100 lines, 15 hours, MEDIUM risk
- Ingestion + Validation + Transformation + Export
```

**After (Decomposed)**:
```
PRP-X.0: Data Processing System (Meta-PRP)
├─ PRP-X.1: CSV Input Parser
│   • Parse CSV/TSV files
│   • Handle encoding issues
│   • 3 hours, LOW risk
│
├─ PRP-X.2: Data Validator
│   • Schema validation
│   • Business rule checks
│   • 4 hours, MEDIUM risk
│
├─ PRP-X.3: Transformation Engine
│   • Apply data transformations
│   • Aggregations, calculations
│   • 5 hours, MEDIUM risk
│
└─ PRP-X.4: JSON/XML Exporter
    • Format output
    • Write to file system
    • 3 hours, LOW risk
```

**Benefits**:
- Each component independently testable
- Clear interfaces between modules
- Can swap implementations (e.g., XML parser instead of CSV)

## Pattern 3: Risk-Based Decomposition

**When to Use**: PRP contains HIGH-risk components mixed with safer features

**Strategy**: Isolate risky parts for focused attention

### Example: API Client with Authentication

**Before (Monolithic)**:
```
PRP-Y: External API Client
- 950 lines, 12 hours, HIGH risk
- OAuth2 + API calls + Error handling
```

**After (Decomposed)**:
```
PRP-Y.0: API Client System (Meta-PRP)
├─ PRP-Y.1: HTTP Client Core
│   • Basic request/response handling
│   • 3 hours, LOW risk
│
├─ PRP-Y.2: OAuth2 Authentication (HIGH RISK)
│   • Token acquisition flow
│   • Refresh token logic
│   • Credential storage
│   • 5 hours, HIGH risk → ISOLATED
│
├─ PRP-Y.3: API Endpoint Methods
│   • GET/POST/PUT/DELETE wrappers
│   • 2 hours, LOW risk
│
└─ PRP-Y.4: Error Handling & Retry
    • Network error detection
    • Exponential backoff
    • 2 hours, MEDIUM risk
```

**Benefits**:
- HIGH risk (OAuth2) gets dedicated focus
- Core functionality (Y.1, Y.3) can proceed independently
- Y.2 can be reviewed by security experts

## Pattern 4: Layer-Based Decomposition

**When to Use**: PRP spans multiple architectural layers (UI, business logic, data access)

### Example: User Management Feature

**Before (Monolithic)**:
```
PRP-Z: User Management System
- 1050 lines, 14 hours, MEDIUM risk
- UI forms + Business logic + Database
```

**After (Decomposed)**:
```
PRP-Z.0: User Management (Meta-PRP)
├─ PRP-Z.1: Database Schema & Migrations
│   • Users table, indexes
│   • 2 hours, LOW risk
│
├─ PRP-Z.2: User Service (Business Logic)
│   • CRUD operations
│   • Validation rules
│   • 5 hours, MEDIUM risk
│
├─ PRP-Z.3: REST API Endpoints
│   • HTTP routes
│   • Request/response handling
│   • 3 hours, LOW risk
│
└─ PRP-Z.4: Admin UI Components
    • User list, forms
    • Frontend validation
    • 4 hours, MEDIUM risk
```

**Benefits**:
- Bottom-up implementation (Z.1 → Z.2 → Z.3 → Z.4)
- Each layer independently testable
- Parallel development possible (Z.3 and Z.4)

## Pattern 5: Criteria-Based Decomposition

**When to Use**: PRP has >30 success criteria spanning multiple concerns

**Strategy**: Group related criteria into logical sub-features

### Example: Testing Infrastructure

**Before (Monolithic)**:
```
PRP-T: Testing Framework Enhancement
- 45 success criteria across unit, integration, E2E, performance
```

**After (Decomposed)**:
```
PRP-T.0: Testing Framework (Meta-PRP)
├─ PRP-T.1: Unit Test Infrastructure (10 criteria)
├─ PRP-T.2: Integration Test Setup (12 criteria)
├─ PRP-T.3: E2E Test Framework (15 criteria)
└─ PRP-T.4: Performance Test Suite (8 criteria)
```

## Anti-Patterns (What NOT to Do)

### ❌ Anti-Pattern 1: Atomic Splitting

**Don't**: Split every phase into its own PRP when they're tightly coupled

**Problem**:
```
PRP-A.1: Define data structure
PRP-A.2: Write getter for field 1
PRP-A.3: Write getter for field 2
PRP-A.4: Write getter for field 3
```

**Better**: Keep tightly coupled code together
```
PRP-A.1: Define data structure with all accessors
```

### ❌ Anti-Pattern 2: Artificial Boundaries

**Don't**: Split based on arbitrary criteria (e.g., "files starting with A-M vs N-Z")

**Problem**: No logical cohesion, dependencies span sub-PRPs

**Better**: Split based on functional boundaries or risk

### ❌ Anti-Pattern 3: Over-Decomposition

**Don't**: Create 10 sub-PRPs of 1 hour each

**Problem**: Coordination overhead exceeds benefit

**Better**: 3-4 sub-PRPs of 3-5 hours each

## Decision Tree

```
Start: Is PRP > 1000 lines OR HIGH risk?
│
├─ No → GREEN, proceed as-is
│
└─ Yes → Is it ≥5 phases?
    │
    ├─ Yes → Use Phase-Based Decomposition
    │
    └─ No → Does it span multiple functional areas?
        │
        ├─ Yes → Use Feature-Based Decomposition
        │
        └─ No → Does it mix HIGH risk with LOW/MEDIUM?
            │
            ├─ Yes → Use Risk-Based Decomposition
            │
            └─ No → Does it have >30 criteria?
                │
                ├─ Yes → Use Criteria-Based Decomposition
                │
                └─ No → Consider Layer-Based or custom split
```

## Meta-PRP Template

When decomposing a PRP, create a meta-PRP (PRP-X.0) to track the overall feature:

```markdown
---
prp_id: PRP-X.0
feature_name: [Feature Name] Framework
status: new
type: meta-prp
sub_prps:
  - PRP-X.1
  - PRP-X.2
  - PRP-X.3
---

# [Feature Name] Framework (Meta-PRP)

## Purpose
Coordinate implementation of [feature] across multiple sub-PRPs.

## Sub-PRPs
1. **PRP-X.1**: [Name] (Xh, RISK)
   - Description
   - Dependencies: None

2. **PRP-X.2**: [Name] (Xh, RISK)
   - Description
   - Dependencies: PRP-X.1

3. **PRP-X.3**: [Name] (Xh, RISK)
   - Description
   - Dependencies: PRP-X.1, PRP-X.2

## Execution Order
PRP-X.1 → PRP-X.2 → PRP-X.3

## Integration Points
- Describe how sub-PRPs integrate
- Shared interfaces, data structures

## Overall Success Criteria
- [ ] All sub-PRPs executed successfully
- [ ] Integration tests pass
- [ ] Feature delivers user value
```

## Real-World Example: PRP-4 Analysis

Run analyzer to see decomposition recommendations:

```bash
cd tools
uv run ce prp analyze ../PRPs/executed/PRP-4-execute-prp-orchestration.md
```

Output shows:
- Complexity Score: 71.45/100 (RED)
- Recommendations: Phase-based decomposition into 6 sub-PRPs
- Suggestion: Isolate HIGH-risk self-healing component

## Tips for Success

1. **Start with Meta-PRP**: Create PRP-X.0 first to plan decomposition
2. **Document Dependencies**: Make execution order explicit
3. **Keep Interfaces Clear**: Define how sub-PRPs interact
4. **Test Incrementally**: Validate each sub-PRP before next one
5. **Review Collectively**: Ensure all sub-PRPs together deliver feature

## Validation Checklist

After decomposition, verify:
- [ ] Each sub-PRP is GREEN (≤700 lines, ≤8h)
- [ ] HIGH risk components isolated
- [ ] Dependencies are minimal and explicit
- [ ] Integration points well-defined
- [ ] Can execute incrementally with validation gates

---

**See Also**:
- [PRP Sizing Guidelines](../docs/prp-sizing-guidelines.md)
- [PRP-8: Sizing Constraint Analysis](../PRPs/feature-requests/PRP-8-prp-sizing-constraint-analysis-and-optimal-breakdown-strategy.md)
