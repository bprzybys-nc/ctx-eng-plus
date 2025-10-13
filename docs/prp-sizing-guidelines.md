# PRP Sizing Guidelines

**Version**: 1.0
**Status**: Active
**Last Updated**: 2025-10-13

## TL;DR

- **GREEN** (optimal): ≤700 lines, ≤8h, ≤3 phases, LOW-MEDIUM risk
- **YELLOW** (warning): 700-1000 lines, 8-12h, 3-5 phases, MEDIUM risk
- **RED** (too large): >1000 lines, >12h, >5 phases, HIGH risk

**Rule**: HIGH risk or >1000 lines → decompose into sub-PRPs

## Purpose

Prevent "PRP obesity" by establishing measurable size constraints and automated decomposition recommendations for Product Requirements Prompts (PRPs).

## Background

Analysis of executed PRPs (PRP-1 through PRP-7) revealed correlation between PRP size and execution quality:

| PRP | Lines | Hours | Risk | Outcome |
|-----|-------|-------|------|---------|
| PRP-1 | 336 | 2-3 | LOW | ✅ Successful |
| PRP-2 | 860 | 15 | MEDIUM | ⚠️ Complex |
| PRP-3 | 918 | 15 | MEDIUM | ⚠️ Complex |
| **PRP-4** | **1259** | **18** | **HIGH** | ❌ **Difficult** |
| PRP-5 | 796 | 13 | MEDIUM | ✅ Successful |

**Key Finding**: PRP-4 exceeded optimal thresholds, resulting in:
- 18 hours estimated effort (highest)
- HIGH risk rating
- 27 functions across 6 phases
- 30 success criteria
- Implementation challenges during execution

## Size Categories

### GREEN (Optimal) ✅

**Thresholds**:
- Lines: ≤700
- Estimated hours: ≤8
- Phases: ≤3
- Risk: LOW or MEDIUM
- Functions: ≤15
- Success criteria: ≤25
- Complexity score: <50

**Characteristics**:
- Single focused feature
- Clear scope boundaries
- Manageable testing surface
- Low coordination overhead

**Recommendation**: Proceed with implementation

### YELLOW (Approaching Limits) ⚠️

**Thresholds**:
- Lines: 700-1000
- Estimated hours: 8-12
- Phases: 3-5
- Risk: MEDIUM
- Functions: 15-20
- Success criteria: 25-30
- Complexity score: 50-70

**Characteristics**:
- Multiple related features
- Some interdependencies
- Moderate testing complexity
- Requires careful planning

**Recommendation**: Consider splitting if possible, proceed with caution

### RED (Too Large) 🚨

**Thresholds**:
- Lines: >1000
- Estimated hours: >12
- Phases: >5
- Risk: HIGH (automatic RED)
- Functions: >20
- Success criteria: >30
- Complexity score: >70

**Characteristics**:
- Multiple distinct features
- High interdependencies
- Complex testing requirements
- Significant coordination overhead
- Elevated risk of implementation issues

**Recommendation**: **Decompose before execution**

## Complexity Scoring Formula

PRPs are assigned a complexity score (0-100) using weighted metrics:

```
Score = (Lines × 0.40) + (Functions × 0.25) + (Criteria × 0.20)
        + (Phases × 0.10) + (Risk × 0.05)
```

**Normalization**:
- Lines: /1500 max
- Functions: /40 max
- Criteria: /50 max
- Phases: /15 max
- Risk: LOW=0, MEDIUM=50, HIGH=100

**Rationale**: Lines are the strongest predictor of complexity, followed by implementation scope (functions), validation burden (criteria), execution phases, and inherent risk.

## Decomposition Strategies

### 1. Phase-Based Decomposition

**When**: PRP has ≥5 distinct phases

**Pattern**:
```
PRP-X.0: Feature Framework (Meta-PRP)
├─ PRP-X.1: Phase 1 Implementation
├─ PRP-X.2: Phase 2 Implementation
├─ PRP-X.3: Phase 3 Implementation
└─ PRP-X.4: Phase 4 Implementation
```

**Example**: PRP-4 decomposition
```
PRP-4.0: Execution Framework (Meta)
├─ PRP-4.1: Blueprint Parser (3h, LOW)
├─ PRP-4.2: Orchestration Engine (5h, MEDIUM)
├─ PRP-4.3: Validation Loop (4h, MEDIUM)
├─ PRP-4.4: Self-Healing Logic (4h, HIGH)
└─ PRP-4.5: CLI Integration (2h, LOW)
```

### 2. Feature-Based Decomposition

**When**: PRP contains >20 functions spanning multiple functional areas

**Pattern**: Split by architectural boundaries (parser, validator, executor, etc.)

**Example**:
```
PRP-X: Data Processing System
├─ PRP-X.1: Input Parser
├─ PRP-X.2: Data Validator
├─ PRP-X.3: Transformation Engine
└─ PRP-X.4: Output Formatter
```

### 3. Risk-Based Decomposition

**When**: PRP has HIGH risk rating

**Pattern**: Isolate high-risk components into separate PRPs for focused attention

**Example**:
```
PRP-X.1: Core Feature (MEDIUM risk)
PRP-X.2: External API Integration (HIGH risk) ← Isolated
PRP-X.3: Testing & Validation (LOW risk)
```

### 4. Criteria-Based Decomposition

**When**: PRP has >30 success criteria

**Pattern**: Group related criteria into logical sub-features

## Using the PRP Analyzer

### Command

```bash
cd tools
uv run ce prp analyze <path-to-prp.md>
```

### Output

```
================================================================================
PRP Size Analysis: PRP-4-execute-prp-orchestration
================================================================================

Metrics:
  Lines:            1259
  Estimated Hours:  18
  Phases:           6
  Risk Level:       HIGH
  Functions:        27
  Success Criteria: 30

Complexity Score: 71.45/100
Size Category:    RED

Recommendations:
  • 🚨 PRP TOO LARGE - decomposition strongly recommended
  • Lines (1259) exceed RED threshold - split into sub-PRPs
  • HIGH risk rating - isolate risky components into separate PRPs
  • Functions (27) indicate multiple features - create sub-PRPs
  • Phases (6) could be independent PRPs
  • ACTION REQUIRED: Decompose before execution

Decomposition Suggestions:
  • Phase-based decomposition: Create 6 sub-PRPs (PRP-X.1 through PRP-X.6)
  • Group related phases if some are interdependent
  • Feature-based decomposition: Split by functional area
  • Risk-based decomposition: Isolate HIGH-risk components
================================================================================
```

### Exit Codes

- **0** (GREEN): Optimal size, proceed
- **1** (YELLOW): Warning, consider review
- **2** (RED): Too large, decompose recommended

### JSON Output

```bash
uv run ce prp analyze <path-to-prp.md> --json
```

Returns structured JSON for automation/CI integration.

## Integration with PRP Generation

### Pre-Generation Size Check

Before creating a PRP, estimate complexity:
- How many features?
- How many phases needed?
- What's the risk level?
- Could this be 2-3 smaller PRPs?

### During Generation

The `/generate-prp` command should (future enhancement):
1. Analyze generated PRP size
2. Flag YELLOW/RED categories
3. Suggest decomposition before finalization

### Post-Generation Validation

Run analyzer on newly generated PRPs:
```bash
uv run ce prp analyze PRPs/feature-requests/PRP-X-new-feature.md
```

## Best Practices

### DO ✅

- **Prefer small, focused PRPs** over monolithic ones
- **Split at natural boundaries** (features, phases, risk levels)
- **Create meta-PRPs** for tracking decomposed work
- **Run analyzer** on all new PRPs before execution
- **Document dependencies** between sub-PRPs

### DON'T ❌

- **Don't ignore RED warnings** - decompose before executing
- **Don't over-decompose** - too many tiny PRPs increases overhead
- **Don't skip analyzer** - "it feels small" is subjective
- **Don't mix risk levels** - isolate HIGH risk components

## Exception Cases

Some PRPs may legitimately be large:

1. **Database Migrations**: Single logical change, many LOC
2. **Configuration Overhauls**: Repetitive changes across files
3. **Test Suite Additions**: Many similar test cases

**Escape Hatch**: Document why decomposition isn't appropriate in PRP header:

```yaml
size_override: true
size_justification: "Database migration - logically atomic change"
```

## Metrics & Monitoring

Track PRP size distribution over time:
- % GREEN vs YELLOW vs RED
- Average complexity score
- Correlation with execution success

Goal: >80% of PRPs in GREEN zone

## References

- **PRP-8**: PRP Sizing Constraint Analysis (this feature)
- **PRP-4**: Case study of oversized PRP (1259 lines, HIGH risk)
- **Analyzer Tool**: `tools/ce/prp_analyzer.py`
- **Tests**: `tools/tests/test_prp_analyzer.py`

## Changelog

### 2025-10-13 - v1.0 (Initial Release)
- Defined GREEN/YELLOW/RED thresholds based on PRP-1 through PRP-7 analysis
- Created complexity scoring formula
- Documented decomposition strategies
- Implemented `ce prp analyze` command
- 80% test coverage achieved

---

**Next Steps**: Integrate size validation into `/generate-prp` workflow
