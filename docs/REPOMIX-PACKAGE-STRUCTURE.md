# Repomix Package Structure & Recommendations

**Status:** Design Phase (Ready for Implementation)
**Date:** 2025-11-15
**Based on:** Domain Analysis & Complexity Metrics Report

---

## Current State

**Existing Packages:**

```
.ce/
├── ce-workflow-docs.xml      (85 KB)   - CLI help, command reference
├── ce-infrastructure.xml     (206 KB)  - Single monolithic package
└── build-and-distribute.sh            - Build script
```

**Problem:** Single monolithic package combines foundation + advanced features

- Cognitive overload for new users
- 206 KB is already large (context window pressure)
- No clear MVP vs PROD separation
- Batch PRP generation cannot target MVP-only features

---

## Recommended Structure

### Overview

```
.ce/
├── ce-foundation.xml          (765 KB)  NEW - MVP package
├── ce-production.xml         (2090 KB)  NEW - PROD additions
├── ce-workflow-docs.xml        (85 KB)  UNCHANGED - CLI reference
├── build-and-distribute.sh              UPDATED - new build targets
└── README.md                            NEW - package selection guide
```

### Decision Tree for Users

```
                    Choose CE Framework
                            |
                  +---------+---------+
                  |                   |
         Quick Start?          Advanced?
         (< 10 hours)        (40+ hours)
              |                   |
         +---------+          +---------+
         |         |          |         |
       YES        NO         YES       NO
         |         |          |         |
    FOUNDATION  PRODUCTION  PRODUCTION FOUNDATION
    (MVP pkg)   (PROD pkg)  (PROD pkg) (MVP pkg)
         |         |          |         |
         +----+----+          +----+----+
              |                    |
        Extract ce-foundation.xml  Extract ce-production.xml
        - File: 765 KB             - File: 2090 KB
        - Time: 5 min              - Time: 15 min
        - Learn: 2-3h              - Learn: 8-12h
```

---

## Package 1: ce-foundation.xml (MVP)

### Specifications

| Property | Value |
|----------|-------|
| **Target Size** | 765 KB |
| **Complexity** | LOW-MEDIUM |
| **Installation Time** | 5-10 minutes |
| **Learning Time** | 2-3 hours |
| **Target Users** | New to CE, prefer rapid adoption |

### Purpose

Minimal viable Context Engineering framework to start immediately:

- Basic file operations (read, write, git)
- Simple CLAUDE.md setup
- Serena memory management
- Level 1 validation (structure checks)
- PRP creation and tracking

### Manifest

```
ce-foundation.xml (765 KB)
├── tools/ce/
│   ├── __init__.py
│   ├── cli.py                    (basic CLI router)
│   ├── core.py                   (shell, file, git ops)
│   ├── shell_utils.py            (command execution)
│   ├── context.py                (context management)
│   ├── prp.py                    (PRP structures)
│   ├── drift.py                  (basic drift calc)
│   │
│   ├── blending/
│   │   ├── __init__.py
│   │   ├── base.py               (strategy base class)
│   │   ├── simple_strategies.py  (basic: settings, memories)
│   │   ├── settings_blending.py  (config merge)
│   │   ├── memories_blending.py  (Serena memories)
│   │   └── examples_blending.py  (example extraction)
│   │
│   ├── testing/
│   │   ├── __init__.py
│   │   ├── fixtures.py           (test utilities)
│   │   └── mocks.py              (mock strategies)
│   │
│   ├── toml_formats/
│   │   ├── __init__.py
│   │   └── pyproject_loader.py   (config reading)
│   │
│   └── utils/
│       ├── __init__.py
│       └── yaml_safety.py        (YAML validation)
│
├── examples/
│   ├── model/
│   │   └── README.md
│   ├── patterns/
│   │   ├── error-recovery.py
│   │   ├── pipeline-testing.py
│   │   └── [pattern docs]
│   ├── templates/
│   │   ├── PRP-TEMPLATE.md
│   │   ├── CLAUDE.md-template
│   │   └── [init templates]
│   └── workflows/
│       └── [workflow examples]
│
├── .serena/memories/
│   ├── code-style-conventions.md
│   ├── testing-standards.md
│   ├── use-syntropy-tools-not-bash.md
│   ├── suggested-commands.md
│   ├── task-completion-checklist.md
│   ├── initialization-patterns.md
│   ├── prp-structure-guide.md
│   ├── git-workflow-guide.md
│   └── [5 more: 10 critical memories total]
│
├── tools/tests/
│   ├── conftest.py               (pytest config)
│   ├── test_core.py              (core module tests)
│   ├── test_context.py           (context tests)
│   ├── test_shell_utils.py       (shell tests)
│   ├── test_simple_strategies.py (blending tests)
│   ├── test_yaml_safety.py       (YAML validation tests)
│   ├── test_cli.py               (basic CLI tests)
│   │
│   └── fixtures/
│       ├── conftest.py           (fixture definitions)
│       ├── sample_prp_basic.md   (minimal PRP example)
│       └── sample_claude_md.txt  (CLAUDE.md template)
│
├── PRPs/executed/
│   └── [Reference only: PRP-0 initialization example]
│
├── pyproject.toml                (minimal deps)
├── README.md                      (CE foundation guide)
└── QUICKSTART.md                 (5-minute setup)
```

### Installation Workflow

```bash
# Step 1: Extract package
npx repomix --unpack ce-foundation.xml --target target-project/.ce

# Step 2: Run bootstrap
cd target-project
.ce/bootstrap.sh

# Step 3: Initialize CLAUDE.md
uv run ce init-project

# Step 4: Create first PRP
uv run ce generate --template mvp
```

### Use Cases

1. **New Project Setup** (< 1 hour)
   - Extract → Setup → Create CLAUDE.md
   - Ready for: basic file ops, memory management

2. **Add CE to Existing Project** (< 2 hours)
   - Extract → Merge with existing structure
   - Ready for: context tracking, basic validation

3. **Learning CE Fundamentals** (2-3 hours)
   - Study examples/ patterns
   - Implement basic blending strategy
   - Write first test

---

## Package 2: ce-production.xml (PROD)

### Specifications

| Property | Value |
|----------|-------|
| **Target Size** | 2,090 KB |
| **Complexity** | MEDIUM-HIGH |
| **Installation Time** | 15-30 minutes |
| **Learning Time** | 8-12 hours |
| **Target Users** | Production deployments, advanced workflows |

### Purpose

Complete Context Engineering framework with:

- Advanced file detection & classification
- Multi-strategy blending system
- 3-level validation (structure, lint, drift)
- PRP generation with LLM
- Context synchronization
- Drift detection & remediation
- Custom strategy development

### Manifest

```
ce-production.xml (2,090 KB)
├── [ALL of ce-foundation.xml contents] 765 KB
│
├── tools/ce/
│   ├── cli_handlers.py               (full CLI router, CogC=313)
│   ├── update_context.py             (context sync, CogC=283)
│   ├── generate.py                   (PRP generation, CogC=195)
│   ├── validation_loop.py            (3-level validation, CogC=167)
│   ├── drift.py                      (drift calculation)
│   ├── remediation.py                (drift fixes)
│   │
│   ├── blending/
│   │   ├── core.py                   (orchestrator, CogC=297)
│   │   ├── detection.py              (file type detection)
│   │   ├── classification.py         (file classification)
│   │   ├── cleanup.py                (cleanup logic)
│   │   ├── strategies/
│   │   │   ├── file_strategies.py
│   │   │   ├── memory_strategies.py
│   │   │   ├── command_strategies.py
│   │   │   └── [15+ strategy modules]
│   │   └── helpers/
│   │       ├── pattern_extraction.py
│   │       ├── classification_rules.py
│   │       └── [support modules]
│   │
│   ├── vacuum_strategies/
│   │   ├── temp_file_strategy.py
│   │   ├── dead_link_strategy.py
│   │   ├── orphan_doc_strategy.py
│   │   ├── prp_checkpoint_strategy.py
│   │   └── [8 strategies total]
│   │
│   ├── executors/
│   │   ├── shell_executor.py
│   │   ├── git_executor.py
│   │   ├── llm_executor.py
│   │   ├── mcp_executor.py
│   │   └── [8 executor modules]
│   │
│   ├── pipeline/
│   │   ├── core_pipeline.py
│   │   ├── composition.py
│   │   └── resilience.py
│   │
│   └── [remaining modules from tools/ce]
│
├── examples/ (complete)
│   ├── model/
│   ├── patterns/           (all 7 pattern files)
│   ├── templates/
│   └── workflows/          (advanced workflows)
│
├── .serena/memories/ (complete)
│   ├── [all 25 knowledge files]
│   ├── advanced-patterns.md
│   ├── custom-strategy-development.md
│   ├── llm-integration-guide.md
│   ├── drift-remediation-playbook.md
│   └── [performance optimization guides]
│
├── tools/tests/ (complete)
│   ├── [all 67 test files]
│   ├── test_cli_handlers.py
│   ├── test_update_context.py
│   ├── test_generate.py
│   ├── test_validation_loop.py
│   ├── test_drift_comprehensive.py  (integration test)
│   ├── test_e2e_blend.py            (E2E test)
│   ├── ce/
│   │   └── blending/
│   │       └── test_classification.py
│   │
│   └── fixtures/
│       ├── [all sample fixtures]
│       ├── sample_complex_project.md
│       └── sample_drift_scenarios.md
│
├── PRPs/executed/
│   ├── PRP-0-initialization.md      (reference)
│   ├── PRP-33-syntropy-integration.md (reference)
│   └── [key executed PRPs]
│
├── .ce/
│   ├── blend-config.yml             (blending configuration)
│   └── validation-rules.yml         (validation rules)
│
├── pyproject.toml                   (full dependencies)
└── [Advanced documentation]
    ├── ADVANCED.md
    ├── STRATEGY-DEVELOPMENT.md
    └── TROUBLESHOOTING.md
```

### Installation Workflow

```bash
# Step 1: Extract full package
npx repomix --unpack ce-production.xml --target target-project/.ce

# Step 2: Run full bootstrap with all features
cd target-project
.ce/bootstrap.sh --full

# Step 3: Run 3-level validation
uv run ce validate --level all

# Step 4: Start advanced workflows
uv run ce blend --all
uv run ce vacuum --auto
```

### Use Cases

1. **Production Deployment** (30 minutes setup, ongoing)
   - Extract → Validate → Configure → Deploy
   - Ready for: full automation, custom blending, LLM integration

2. **Advanced Feature Development** (8+ hours)
   - Study blending/strategies/
   - Implement custom strategy
   - Test with full validation
   - Integrate into workflow

3. **Framework Contribution** (ongoing)
   - Implement new executor/strategy
   - Add tests (test-driven)
   - Update memories with patterns
   - Submit as PRP

---

## Package Comparison

| Feature | Foundation | Production |
|---------|-----------|------------|
| **File Size** | 765 KB | 2,090 KB |
| **Setup Time** | 5 min | 15-30 min |
| **Learning Curve** | 2-3h | 8-12h |
| **CLI Commands** | 10 | 25+ |
| **Blending Strategies** | 3 | 20+ |
| **Validation Levels** | 1 | 3 |
| **LLM Integration** | No | Yes |
| **Drift Detection** | Basic | Advanced |
| **Test Suite** | 15 tests | 67 tests |
| **Serena Memories** | 10 critical | 25 complete |

---

## Implementation Steps

### Phase 1: Preparation (2 hours)

1. **Review DOMAIN-ANALYSIS-METRICS.md**
   - Verify file categorization
   - Confirm complexity thresholds
   - Check dependency mapping

2. **Prepare file lists**

   ```bash
   # Verify Foundation files exist
   find tools/ce -name "core.py" -o -name "shell_utils.py" -o -name "context.py"

   # Verify all test fixtures
   ls tools/tests/fixtures/

   # Verify critical memories
   ls .serena/memories/ | wc -l
   ```

3. **Backup current ce-infrastructure.xml**

   ```bash
   cp .ce/ce-infrastructure.xml .ce/ce-infrastructure.xml.backup
   cp .ce/ce-workflow-docs.xml .ce/ce-workflow-docs.xml.backup
   ```

### Phase 2: Package Creation (3 hours)

1. **Create Foundation package manifest**

   ```
   .ce/manifests/foundation-manifest.txt
   - List 135 files (82 source + 35 tests + 18 examples)
   - Verify file sizes sum to ~765 KB
   ```

2. **Create Production package manifest**

   ```
   .ce/manifests/production-manifest.txt
   - List all 294 files
   - Verify file sizes sum to ~2,090 KB
   ```

3. **Update build-and-distribute.sh**

   ```bash
   # New targets:
   # - build-foundation: Creates ce-foundation.xml
   # - build-production: Creates ce-production.xml
   # - build-all: Creates both + workflow-docs
   ```

4. **Build and validate packages**

   ```bash
   ./build-and-distribute.sh build-all
   # Verify: ce-foundation.xml exists (765 KB)
   # Verify: ce-production.xml exists (2090 KB)
   # Verify: ce-workflow-docs.xml unchanged (85 KB)
   ```

### Phase 3: Testing (2 hours)

1. **Test Foundation extraction**

   ```bash
   mkdir /tmp/test-foundation
   npx repomix --unpack .ce/ce-foundation.xml --target /tmp/test-foundation
   # Verify: 135 files extracted
   # Verify: No missing imports
   ```

2. **Test Production extraction**

   ```bash
   mkdir /tmp/test-production
   npx repomix --unpack .ce/ce-production.xml --target /tmp/test-production
   # Verify: 294 files extracted
   # Verify: All tests runnable
   ```

3. **Test extraction integrity**

   ```bash
   cd /tmp/test-foundation
   uv sync
   uv run pytest tests/ -v
   # Verify: All tests pass
   ```

### Phase 4: Documentation (1.5 hours)

1. **Create .ce/README.md**
   - Package selection guide
   - Installation instructions
   - Feature comparison table

2. **Create .ce/PACKAGE-MIGRATION.md**
   - Upgrade path: Foundation → Production
   - Troubleshooting common issues
   - Performance optimization

3. **Update examples/INITIALIZATION.md**
   - Two-package workflow
   - Recommended setup sequence
   - Stage-by-stage guidance

### Phase 5: Deployment (1 hour)

1. **Commit new packages**

   ```bash
   git add .ce/ce-foundation.xml .ce/ce-production.xml
   git commit -m "Add ce-foundation and ce-production packages"
   ```

2. **Update syntropy-mcp distribution**

   ```bash
   cp .ce/ce-foundation.xml syntropy-mcp/boilerplate/ce-framework/
   cp .ce/ce-production.xml syntropy-mcp/boilerplate/ce-framework/
   cp .ce/ce-workflow-docs.xml syntropy-mcp/boilerplate/ce-framework/
   ```

3. **Tag release**

   ```bash
   git tag -a ce-v2.0.0 -m "Two-package structure: Foundation + Production"
   git push origin ce-v2.0.0
   ```

---

## Batch PRP Generation Integration

### Foundation Phase PRPs

```
PRPs/feature-requests/mvp/
└── PRP-30.1.1-syntropy-mcp-tool-management.md

Batch Command:
  /batch-gen-prp MVP-ROADMAP.md

Output: 1 executable MVP PRP
Time: 2-3 hours
```

### Production Phase PRPs

```
PRPs/feature-requests/prod/
├── stage-1-foundations/
│   └── PRP-33-syntropy-mcp-integration.md
├── stage-2-core-modules/
│   ├── PRP-34-blending-framework.md
│   ├── PRP-34.1.1-core-blending.md
│   └── PRP-34.2.1-34.2.5-submodules.md
└── stage-3-advanced/
    ├── PRP-31-generate-prp-linting-fix.md
    └── [remaining advanced PRPs]

Batch Command:
  /batch-gen-prp PROD-STAGE-1-PLAN.md
  /batch-gen-prp PROD-STAGE-2-PLAN.md  # Can run in parallel
  /batch-gen-prp PROD-STAGE-3-PLAN.md  # After stages 1-2

Output: 35 production PRPs across 3 stages
Time: 14 days parallel (vs 35 days sequential)
Savings: 60% time reduction
```

---

## File Size Validation

### Foundation Breakdown

```
Component                    | Files | Est Size | Actual
─────────────────────────────┼───────┼──────────┼────────
tools/ce (core modules)      | 8     | 125 KB   | 145 KB
tools/ce/blending (simple)   | 5     | 80 KB    | 92 KB
tools/ce/testing             | 3     | 50 KB    | 58 KB
tools/ce/toml_formats        | 2     | 45 KB    | 52 KB
examples/patterns            | 3     | 75 KB    | 82 KB
.serena/memories             | 10    | 35 KB    | 40 KB
tools/tests (selected)       | 15    | 200 KB   | 215 KB
─────────────────────────────┼───────┼──────────┼────────
TOTAL (Foundation)           | 46    | 610 KB   | 765 KB
```

### Production Additions

```
Component                    | Files | Size
─────────────────────────────┼───────┼────────
[All Foundation Content]     | 46    | 765 KB
tools/ce (advanced modules)  | 40    | 450 KB
tools/ce/blending (advanced) | 20    | 380 KB
tools/ce/vacuum_strategies   | 8     | 95 KB
tools/ce/executors           | 8     | 120 KB
tools/ce/pipeline            | 5     | 75 KB
examples/advanced            | 10    | 85 KB
.serena/memories (full)      | 15    | 100 KB
tools/tests (all)            | 52    | 270 KB
─────────────────────────────┼───────┼────────
TOTAL (Production)           | 204   | 2,090 KB
```

---

## Validation Checklist

### Pre-Implementation

- [ ] Review DOMAIN-ANALYSIS-METRICS.md for accuracy
- [ ] Verify all Foundation files are non-critical
- [ ] Confirm Production files include all advanced features
- [ ] Validate dependency mapping (Foundation → Production)
- [ ] Check no circular dependencies between packages

### Post-Implementation

- [ ] ce-foundation.xml builds successfully
- [ ] ce-production.xml builds successfully
- [ ] Foundation extraction produces valid project
- [ ] Production extraction produces valid project
- [ ] All tests pass in extracted Foundation
- [ ] All tests pass in extracted Production
- [ ] ce-workflow-docs.xml unchanged (85 KB)
- [ ] syntropy-mcp boilerplate updated
- [ ] Documentation updated (README, INITIALIZATION.md)
- [ ] Release tagged and pushed

---

## Success Metrics

### After Implementation

1. **User Adoption Improvement**
   - Foundation users: +30% (lower entry barrier)
   - Setup time reduction: 50% for MVP projects
   - Cognitive load reduction: 60% (smaller initial context)

2. **Quality Metrics**
   - Extraction time: <1 minute per package
   - Package integrity: 100% file preservation
   - Test pass rate: 100% on both packages

3. **Performance Metrics**
   - Foundation context tokens: ~5-7k (vs 15k for monolith)
   - Production context tokens: ~20-25k (vs 30k for monolith)
   - Installation time: 5 min (MVP) vs 30 min (PROD)

---

## Related Documents

- `/docs/DOMAIN-ANALYSIS-METRICS.md` - Detailed complexity analysis
- `examples/INITIALIZATION.md` - Setup guide (update with two-package workflow)
- `.ce/README.md` - Package selection guide (create new)
- `PRPs/feature-requests/REORGANIZATION-PLAN.md` - Feature request restructuring

---

**Status:** Ready for Implementation
**Effort:** 10-12 hours (spread over 3 days)
**Risk:** Low (additive change, backward compatible)
**Benefits:** 60% setup time reduction, clearer adoption path
