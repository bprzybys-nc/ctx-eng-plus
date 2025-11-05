# /batch-peer-review - Universal Batch PRP Peer Review with Parallel Subagents

Performs comprehensive peer review of ANY batch of PRPs in parallel using staged subagents with shared context optimization.

**Architecture**: Coordinator (Sonnet) spawns parallel reviewers (Haiku for structural, Sonnet for semantic) organized in dependency-based stages.

**Universal**: Works for any batch ID, any project, any PRP content domain.

## Usage

```bash
/batch-peer-review --batch <batch-id> [flags]
/batch-peer-review <prp-file-1> <prp-file-2> ...

# Examples:
/batch-peer-review --batch 34                # Review all PRPs in batch 34 (document only)
/batch-peer-review --batch 34 --exe          # Review execution of entire batch
/batch-peer-review --batch 43 --fast         # Haiku only (structural)
/batch-peer-review --batch 12 --quality      # Sonnet only (deep semantic)
/batch-peer-review --batch 34 --retry-failed # Re-review failed PRPs
/batch-peer-review --batch 34 --exe --stage 2 # Review execution of Stage 2 only
/batch-peer-review PRP-34.1.1 PRP-43.2.5     # Specific PRPs (any batch)
```

## What It Does

1. **Auto-Discovers Batch PRPs**:
   - Scans PRPs/feature-requests/PRP-{batch_id}.*.md
   - Finds master plan: PRPs/feature-requests/PRP-{batch_id}-INITIAL.md (if exists)
   - No hardcoded assumptions about content domain

2. **Prepares Shared Context** (read ONCE):
   - CLAUDE.md (project instructions)
   - .ce/RULES.md (framework rules)
   - Master plan IF found (optional, for alignment checks)
   - No domain-specific files

3. **Groups PRPs by Stages**:
   - Parse dependencies from YAML frontmatter
   - Build dependency graph (generic)
   - Assign to stages via topological sort
   - Stage PRPs reviewed in parallel

4. **Stage-by-Stage Review** (parallel within stage):
   - Spawn N parallel subagents per stage
   - Pass shared context + PRP content
   - Haiku: Structural review (10 checks, fast)
   - Sonnet: Semantic review (8 checks, deep)
   - Monitor via heartbeat (30s polls)

5. **Aggregates Results**:
   - Individual PRP reviews (JSON)
   - Inter-PRP consistency checks (file conflicts, circular deps)
   - Summary report (approved/needs-revision/rejected)
   - Actionable recommendations

**Token Optimization**: ~75-85% savings via shared context (depends on batch size)

**Time Savings**: Typical 60-75% reduction (sequential → parallel)

---

## Shared Context Preparation

**Coordinator reads ONCE** (~10-30k tokens, varies by project):

```python
def prepare_shared_context(batch_id: str):
    """Universal context preparation - works for ANY batch"""

    # Always include: project instructions + framework rules
    shared_context = {
        "claude_md": Read("CLAUDE.md"),
        "rules_md": Read(".ce/RULES.md")
    }

    # Optional: Master plan (if exists)
    master_plan_path = f"PRPs/feature-requests/PRP-{batch_id}-INITIAL.md"
    if Path(master_plan_path).exists():
        shared_context["master_plan"] = Read(master_plan_path)

    # Discover all PRPs in batch
    prp_files = Glob(f"PRPs/feature-requests/PRP-{batch_id}.*.md")
    shared_context["batch_metadata"] = {
        "batch_id": batch_id,
        "total_prps": len(prp_files),
        "prp_files": [str(f) for f in prp_files]
    }

    return shared_context
```

**Token Breakdown** (typical):
- CLAUDE.md: ~5-15k tokens (project-specific)
- .ce/RULES.md: ~3-5k tokens (framework rules)
- Master plan: ~5-15k tokens (if exists)
- **Total**: ~10-30k tokens (read ONCE, pass to ALL subagents)

**Pass to ALL subagents** - No redundant reads!

---

## PRP Staging

**Stage Assignment** (based on dependencies):

```python
def assign_stages(prps: List[PRP]) -> List[Stage]:
    """Group PRPs by dependency stages for parallel review"""

    # Build dependency graph
    dep_graph = {}
    for prp in prps:
        prp_id = prp.frontmatter["prp_id"]
        deps = prp.frontmatter.get("dependencies", [])
        dep_graph[prp_id] = {
            "prp": prp,
            "dependencies": deps,
            "files_modified": prp.frontmatter["files_modified"]
        }

    # Topological sort to assign stages
    stages = []
    assigned = set()

    while len(assigned) < len(prps):
        # Find PRPs with all dependencies satisfied
        ready = [
            prp_id for prp_id in dep_graph
            if prp_id not in assigned
            and all(dep in assigned for dep in dep_graph[prp_id]["dependencies"])
        ]

        if not ready:
            raise CircularDependencyError("Circular dependency detected")

        stages.append({
            "stage_num": len(stages) + 1,
            "prps": ready,
            "parallel": len(ready) > 1
        })

        assigned.update(ready)

    return stages
```

**Example Staging** (varies by batch):
```
# Example: Batch 34 (11 PRPs)
Stage 1: [34.1.1] (1 PRP - core framework)
Stage 2: [34.2.1, 34.2.2, 34.2.3, 34.2.4, 34.2.5, 34.2.6] (6 PRPs - parallel)
Stage 3: [34.3.1, 34.3.2, 34.3.3] (3 PRPs - parallel)
Stage 4: [34.4.1] (1 PRP - integration)

# Example: Batch 43 (5 PRPs)
Stage 1: [43.1.1, 43.1.2] (2 PRPs - parallel, no deps)
Stage 2: [43.2.1, 43.2.2] (2 PRPs - parallel, depend on stage 1)
Stage 3: [43.3.1] (1 PRP - integration)
```

---

## Review Criteria

### Structural Review (Haiku - Fast)

**10 Checks** (~2k tokens per PRP):

1. ✓ YAML frontmatter complete (prp_id, title, status, estimated_hours, complexity, dependencies)
2. ✓ Problem section present with current pain points
3. ✓ Solution section present with clear approach
4. ✓ Implementation section with phased plan
5. ✓ Validation gates defined (≥5 gates, bash commands)
6. ✓ Files modified explicitly listed
7. ✓ Dependencies declared (matches actual deps)
8. ✓ Acceptance criteria present (testable)
9. ✓ Testing strategy defined (unit + integration)
10. ✓ Risks identified with mitigations

**Output Format**:
```json
{
  "prp_id": "34.2.1",
  "review_type": "structural",
  "model": "haiku",
  "score": 10,
  "checks_passed": 10,
  "checks_failed": 0,
  "issues": [],
  "recommendation": "APPROVE"
}
```

---

### Semantic Review (Sonnet - Deep)

**8 Universal Checks** (~15k tokens per PRP):

1. ✓ **Alignment with Master Plan**: Implementation matches corresponding section (if master plan exists)
2. ✓ **Dependencies Accurate**: Declared deps match actual file dependencies from files_modified
3. ✓ **Architecture Consistency**: Follows project's documented patterns (from CLAUDE.md)
4. ✓ **Project Rules Compliance**: Adheres to .ce/RULES.md principles
5. ✓ **No Contradictions**: No conflicts with sibling PRPs in batch (overlapping responsibilities)
6. ✓ **Effort Estimates**: Hours/complexity reasonable for scope
7. ✓ **Test Coverage**: Adequate test strategy (unit + integration where applicable)
8. ✓ **No Circular Dependencies**: Dependency graph is acyclic

**Output Format**:
```json
{
  "prp_id": "43.2.1",
  "review_type": "semantic",
  "model": "sonnet",
  "score": 8,
  "checks_passed": 8,
  "checks_failed": 0,
  "alignment_with_plan": "ALIGNED",
  "issues": [],
  "warnings": ["Estimated hours conservative"],
  "recommendation": "APPROVE"
}
```

---

### Inter-PRP Consistency Checks

**Batch-Level Validation** (after all individual reviews):

1. **File Conflict Detection**:
   ```python
   file_map = defaultdict(list)
   for prp in prps:
       for file in prp.files_modified:
           file_map[file].append(prp.prp_id)

   conflicts = {f: prps for f, prps in file_map.items() if len(prps) > 1}
   # Report: Which PRPs modify the same files (potential merge conflicts)
   ```

2. **Duplicate Deliverables**:
   - Check for PRPs implementing same feature (redundant work)
   - Detect overlapping responsibilities (unclear ownership)
   - Identify near-identical implementation sections

3. **Missing Integration Points**:
   - If batch has "integration" PRP (common pattern), verify it references all sibling PRPs
   - Check for orphaned PRPs (no PRP depends on them, not depended by any PRP)

4. **Terminology Consistency**:
   - Extract key terms from all PRPs in batch
   - Flag inconsistent terminology (e.g., "handler" vs "processor" for same concept)
   - Check naming conventions align with CLAUDE.md

---

## Execution Review Mode (--exe flag)

**When to Use**: After `/batch-exe-prp` completes, to validate implementation vs PRP requirements.

### What It Checks

**For Each PRP in Batch**:
1. ✓ **Implementation matches PRP**: Read changed files, verify requirements implemented
2. ✓ **Code quality**: Meets project standards (CLAUDE.md, .ce/RULES.md)
3. ✓ **Acceptance criteria**: All criteria from PRP satisfied
4. ✓ **No side effects**: No unintended changes outside PRP scope
5. ✓ **Edge cases handled**: Corner cases from PRP addressed
6. ✓ **No guideline violations**: Respects CLAUDE.md, serena memories, existing patterns
7. ✓ **No code duplication**: Extends existing code, doesn't duplicate
8. ✓ **Integration works**: Batch integration (Stage 4) correctly wires all components

**Batch-Level Checks**:
- File changes match declared files_modified in PRPs
- No conflicts from parallel execution (git merge issues)
- Integration PRP correctly references all sibling PRPs
- No missing files from implementation

### Execution Review Workflow

```bash
# Step 1: Execute entire batch
/batch-exe-prp --batch 34

# Step 2: Review execution results
/batch-peer-review --batch 34 --exe

# Step 3: Fix any issues found
# (Manual edits or re-execute failed PRPs)

# Step 4: Re-review execution
/batch-peer-review --batch 34 --exe --retry-failed
```

### Execution Review Output

```
✅ Batch Execution Review Complete
============================================================

Batch ID: 34
PRPs Executed: 11/11
Execution Reviewed: 11/11 (100%)

Stage 1 (1 PRP):
  ✅ PRP-34.1.1: Core Framework [EXECUTION APPROVED]
    → Implementation: 5/5 files modified correctly
    → Code Quality: Passes standards
    → Acceptance Criteria: 8/8 satisfied
    → Issues: None

Stage 2 (6 PRPs - executed in parallel):
  ⚠ PRP-34.2.2: Classification Module [NEEDS FIXES]
    → Implementation: 4/5 files modified (1 missing)
    → Code Quality: Passes standards
    → Acceptance Criteria: 9/10 satisfied (1 failed)
    → Issues:
      ✗ Missing test file: tools/tests/test_classification.py
      ✗ Haiku model constant incorrect (line 45)
    → Fixes Applied:
      ✓ Created missing test file with 20 tests
      ✓ Corrected model ID to claude-3-5-haiku-20241022

  ✅ PRP-34.2.4: Settings Strategy [EXECUTION APPROVED]
    → All 11 tests passing (82% coverage)
    → Blending rules correctly implemented
    → No issues

[... additional stages ...]

============================================================
Batch-Level Execution Checks
============================================================

✅ File Changes: All declared files_modified present
✅ Git Conflicts: NONE (parallel execution clean)
✅ Integration: PRP-34.4.1 correctly wires all 10 strategies
⚠ Missing Files: 1 test file missing (PRP-34.2.2) - FIXED

============================================================
Summary
============================================================

  ✅ Execution Approved: 10 PRPs
  ⚠ Execution Needs Fixes: 1 PRP (FIXED)
  ❌ Execution Rejected: 0 PRPs

Total Issues Found: 2
Total Issues Fixed: 2

Recommendations:
  1. ✅ All issues fixed during review
  2. ✅ Batch ready to commit
  3. 🚀 Proceed to: git commit + push
```

### Error: Execution Review Without Execution

```
⚠️ Execution review requested but batch not executed: batch 34

Please execute batch first:
  /batch-exe-prp --batch 34

Then review execution:
  /batch-peer-review --batch 34 --exe
```

---

## Subagent Prompt Templates

### Structural Review Prompt (Haiku)

```
You are performing a STRUCTURAL review of PRP-{prp_id}.

Your task: Check completeness of PRP document structure (NOT implementation correctness).

SHARED CONTEXT (master plan, architectural principles):
{shared_context_json}

PRP TO REVIEW:
{prp_content}

STRUCTURAL CHECKLIST (10 checks):
1. YAML frontmatter complete (prp_id, title, status, estimated_hours, complexity, dependencies)?
2. Problem section present with pain points?
3. Solution section present with approach?
4. Implementation section with phases?
5. Validation gates defined (≥5 gates, bash commands)?
6. Files modified listed?
7. Dependencies declared?
8. Acceptance criteria present?
9. Testing strategy defined?
10. Risks identified?

OUTPUT JSON (must be valid JSON):
{
  "prp_id": "{prp_id}",
  "review_type": "structural",
  "model": "haiku",
  "score": <0-10>,
  "checks_passed": <0-10>,
  "checks_failed": <0-10>,
  "issues": ["Missing YAML field: complexity", ...],
  "warnings": ["Validation gates only has 4, recommend ≥5", ...],
  "recommendation": "APPROVE|NEEDS_REVISION|REJECT"
}

IMPORTANT:
- Focus ONLY on structure, not semantic correctness
- Be strict: missing sections = NEEDS_REVISION
- Output ONLY valid JSON (no markdown, no explanation)
```

---

### Semantic Review Prompt (Sonnet)

```
You are performing a SEMANTIC review of PRP-{prp_id} in batch {batch_id}.

Your task: Verify implementation aligns with project requirements and architectural consistency.

PROJECT CONTEXT (CLAUDE.md - project instructions):
{claude_md_content}

FRAMEWORK RULES (.ce/RULES.md):
{rules_md_content}

MASTER PLAN (if provided):
{master_plan_content}

BATCH METADATA (sibling PRPs):
{batch_metadata_json}

PRP TO REVIEW:
{prp_content}

SEMANTIC CHECKLIST (8 universal checks):
1. Alignment: Does implementation match master plan section (if plan exists)?
2. Dependencies: Are declared deps accurate (match files_modified across PRPs)?
3. Architecture: Follows project patterns documented in CLAUDE.md?
4. Rules Compliance: Adheres to .ce/RULES.md principles?
5. Consistency: No contradictions with sibling PRPs (overlapping scope)?
6. Effort Estimates: Hours/complexity reasonable for described scope?
7. Test Coverage: Adequate test strategy (unit + integration where applicable)?
8. Dependency Graph: No circular dependencies (check against batch metadata)?

OUTPUT JSON (must be valid JSON):
{
  "prp_id": "{prp_id}",
  "batch_id": "{batch_id}",
  "review_type": "semantic",
  "model": "sonnet",
  "score": <0-8>,
  "checks_passed": <0-8>,
  "checks_failed": <0-8>,
  "alignment_with_plan": "ALIGNED|PARTIAL|DIVERGENT|N/A",
  "issues": ["Circular dependency with PRP-X.Y.Z", ...],
  "warnings": ["Effort estimate may be conservative", ...],
  "recommendation": "APPROVE|NEEDS_REVISION|REJECT",
  "detailed_analysis": "Brief analysis of alignment, dependencies, and consistency"
}

IMPORTANT:
- If master plan exists, compare implementation carefully
- Check dependency accuracy against files_modified in sibling PRPs
- Verify project-specific patterns from CLAUDE.md
- Output ONLY valid JSON (no markdown, no explanation)
```

---

### Execution Review Prompt (Sonnet)

```
You are performing an EXECUTION review of PRP-{prp_id} in batch {batch_id}.

Your task: Verify implementation matches PRP requirements and code quality standards.

PROJECT CONTEXT (CLAUDE.md - project instructions):
{claude_md_content}

FRAMEWORK RULES (.ce/RULES.md):
{rules_md_content}

PRP REQUIREMENTS:
{prp_content}

IMPLEMENTATION FILES (modified during execution):
{files_modified_content}

EXECUTION CHECKLIST (9 checks):
1. Implementation matches PRP: All requirements from PRP implemented?
2. Code quality: Meets project standards (CLAUDE.md, .ce/RULES.md)?
3. Acceptance criteria: All criteria from PRP satisfied?
4. No side effects: No unintended changes outside PRP scope?
5. Edge cases handled: Corner cases from PRP addressed?
6. No guideline violations: Respects CLAUDE.md, serena memories, existing patterns?
7. No code duplication: Extends existing code, doesn't duplicate?
8. Integration works: Batch integration (Stage 4) correctly wires all components?
9. Tests passing: All tests pass, coverage adequate?

OUTPUT JSON (must be valid JSON):
{
  "prp_id": "{prp_id}",
  "batch_id": "{batch_id}",
  "review_type": "execution",
  "model": "sonnet",
  "files_checked": <number of files reviewed>,
  "implementation_score": <0-9>,
  "checks_passed": <0-9>,
  "checks_failed": <0-9>,
  "issues": ["Missing test file: tools/tests/test_foo.py", ...],
  "warnings": ["Code coverage 75%, below 80% target", ...],
  "recommendation": "APPROVE|NEEDS_FIXES|REJECT",
  "detailed_analysis": "Brief analysis of implementation quality and issues found"
}

IMPORTANT:
- Read ALL files_modified from PRP
- Compare implementation to PRP requirements carefully
- Check code quality against CLAUDE.md standards
- Verify tests exist and pass
- Output ONLY valid JSON (no markdown, no explanation)
```

---

## Workflow

### Step 1: Parse Batch

```bash
# User invokes
/batch-peer-review --batch 34

# Coordinator parses batch
batch_prps = glob("PRPs/feature-requests/PRP-34.*.md")  # 11 files
```

---

### Step 2: Prepare Shared Context (ONCE)

```python
print(f"📋 Preparing shared context for batch {batch_id}...")

# Universal context (works for ANY batch, ANY project)
shared_context = {
    "claude_md": Read("CLAUDE.md"),
    "rules_md": Read(".ce/RULES.md")
}

# Optional: Master plan (if exists)
master_plan_path = f"PRPs/feature-requests/PRP-{batch_id}-INITIAL.md"
if Path(master_plan_path).exists():
    shared_context["master_plan"] = Read(master_plan_path)
    print(f"  ✓ Found master plan: {master_plan_path}")
else:
    print(f"  ℹ No master plan found (alignment checks will be skipped)")

# Batch metadata
prp_files = Glob(f"PRPs/feature-requests/PRP-{batch_id}.*.md")
shared_context["batch_metadata"] = {
    "batch_id": batch_id,
    "total_prps": len(prp_files),
    "prp_files": [str(f) for f in prp_files]
}

print(f"✓ Shared context prepared (~{estimate_tokens(shared_context)}k tokens)")
```

**Token Savings**: Read once, pass to N subagents = **typical 75-85% savings**

---

### Step 3: Assign Stages

```python
print("📊 Grouping PRPs by stages...")

stages = assign_stages(batch_prps)

print(f"✓ {len(stages)} stages identified")
for stage in stages:
    print(f"  Stage {stage.stage_num}: {len(stage.prps)} PRPs {'(parallel)' if stage.parallel else '(sequential)'}")
```

**Output**:
```
📊 Grouping PRPs by stages...
✓ 4 stages identified
  Stage 1: 1 PRP (sequential)
  Stage 2: 6 PRPs (parallel)
  Stage 3: 3 PRPs (parallel)
  Stage 4: 1 PRP (sequential)
```

---

### Step 4: Stage-by-Stage Review (Parallel within Stage)

```python
for stage in stages:
    print(f"\n🔍 Stage {stage.stage_num} Review ({len(stage.prps)} PRPs)")
    print("=" * 60)

    if stage.parallel and len(stage.prps) > 1:
        # Spawn parallel reviewers
        agents = []
        for prp_id in stage.prps:
            prp_content = Read(f"PRPs/feature-requests/PRP-{prp_id}.md")

            # Select model: Haiku for simple PRPs, Sonnet for complex
            model = select_model(prp_id, stage.stage_num)

            # Build review prompt
            if model == "haiku":
                prompt = build_structural_prompt(prp_id, prp_content, shared_context)
            else:
                prompt = build_semantic_prompt(prp_id, prp_content, shared_context)

            # Spawn subagent
            agent = Task(
                description=f"Review PRP-{prp_id}",
                prompt=prompt,
                subagent_type="general-purpose",
                model=model
            )
            agents.append((prp_id, agent))

            print(f"  Spawned {model} reviewer for PRP-{prp_id}")

        # Monitor agents
        results = monitor_parallel_reviews(agents, timeout=120)  # 2 min per PRP
    else:
        # Sequential review
        results = []
        for prp_id in stage.prps:
            result = review_prp_sequential(prp_id, shared_context)
            results.append(result)

    # Show stage results
    show_stage_results(stage, results)
```

**Display During Monitoring** (updates every 30s):
```
============================================================
📊 Monitoring 6 Reviewers (Stage 2)
============================================================

PRP-34.2.1: Detection Module
  Status: [ANALYZING........] ✓ HEALTHY (12s ago)
  Progress: Checking dependencies (5/10 checks)

PRP-34.2.2: Classification Module
  Status: [COMPLETE] ✓ DONE
  Result: APPROVED (10/10 structural, 8/8 semantic)

PRP-34.2.3: Cleanup Module
  Status: [ANALYZING........] ✓ HEALTHY (18s ago)
  Progress: Validating acceptance criteria (7/10 checks)

...

Health Summary: 4 HEALTHY, 2 DONE
Next poll in 30s...
```

---

### Step 5: Aggregate Results

```python
print("\n📊 Aggregating Results...")

# Collect individual reviews
all_reviews = []
for stage_results in stages:
    all_reviews.extend(stage_results.reviews)

# Perform inter-PRP checks
inter_prp_issues = check_inter_prp_consistency(all_reviews, shared_context)

# Generate summary
summary = {
    "batch_id": 34,
    "total_prps": len(all_reviews),
    "approved": sum(1 for r in all_reviews if r.recommendation == "APPROVE"),
    "needs_revision": sum(1 for r in all_reviews if r.recommendation == "NEEDS_REVISION"),
    "rejected": sum(1 for r in all_reviews if r.recommendation == "REJECT"),
    "avg_structural_score": avg([r.structural_score for r in all_reviews]),
    "avg_semantic_score": avg([r.semantic_score for r in all_reviews if r.semantic_score]),
    "inter_prp_issues": inter_prp_issues,
    "review_time_seconds": total_time
}
```

---

### Step 6: Output Summary

```
✅ Batch Peer Review Complete
============================================================

Batch ID: {batch_id}
PRPs Reviewed: {total}/{total} (100% success rate)
Review Time: {duration} minutes
Master Plan: {found|not_found}

Stage 1 ({count} PRP{'s' if count > 1 else ''}):
  ✓ PRP-{batch}.{stage}.{order}: {Title} [APPROVED]
    → Structural: 10/10 ({model})
    → Semantic: 8/8 ({model})
    → Issues: None

Stage 2 ({count} PRPs - parallel):
  ✓ PRP-{batch}.{stage}.{order}: {Title} [APPROVED]
    → Structural: 10/10 (haiku)
    → Semantic: 8/8 (sonnet)
    → Issues: None

  ⚠ PRP-{batch}.{stage}.{order}: {Title} [NEEDS REVISION]
    → Structural: 10/10 (haiku)
    → Semantic: 6/8 (sonnet)
    → Issues:
      ✗ {Issue description from review}
      ✗ {Another issue}

  ✓ PRP-{batch}.{stage}.{order}: {Title} [APPROVED]
    → Structural: 10/10 (haiku)
    → Semantic: 8/8 (sonnet)
    → Warnings: {Warning description}

[... additional stages ...]

============================================================
Inter-PRP Consistency Checks
============================================================

✓ File Conflicts: {count} detected
  {If conflicts: List of files modified by multiple PRPs}

✓ Duplicate Deliverables: {count} detected
  {If duplicates: Description of overlapping responsibilities}

✓ Missing Integration Points: {status}
  {If issues: Description of orphaned PRPs or missing references}

⚠ Terminology Consistency: {count} inconsistencies
  {If inconsistencies: List of terminology mismatches}

============================================================
Summary
============================================================

  ✅ Approved: {count} PRPs
  ⚠ Needs Revision: {count} PRPs
  ❌ Rejected: {count} PRPs

Average Scores:
  Structural: {avg}/10 ({pct}%)
  Semantic: {avg}/8 ({pct}%)

Failed Checks:
  {Numbered list of all issues across all PRPs}

Recommendations:
  1. Fix {count} issues in PRPs {list}
  2. {Context-specific recommendations from inter-PRP checks}
  3. Re-run review: /batch-peer-review --batch {batch_id} --retry-failed

Review completed in {duration} minutes ({pct}% faster than sequential)
Token usage: ~{count}k tokens ({pct}% savings via shared context)

Reports saved:
  - .tmp/batch-review/batch-{batch_id}-summary.json
  - .tmp/batch-review/batch-{batch_id}-report.md
  - Individual reviews: .tmp/batch-review/PRP-{batch_id}.*.review.json
```

---

## Model Selection Strategy

**Hybrid Haiku + Sonnet (Universal)**:

```python
def select_model(prp: PRP, batch_metadata: dict) -> str:
    """Select review model based on PRP complexity (universal heuristics)"""

    # Check complexity from YAML frontmatter
    complexity = prp.frontmatter.get("complexity", "medium")
    estimated_hours = prp.frontmatter.get("estimated_hours", 2.0)

    # Heuristic 1: Low complexity + short PRPs → Haiku
    if complexity == "low" and estimated_hours < 2.0:
        return "haiku"

    # Heuristic 2: High complexity or long PRPs → Sonnet
    if complexity == "high" or estimated_hours > 8.0:
        return "sonnet"

    # Heuristic 3: Core/Integration PRPs (keywords) → Sonnet
    title_lower = prp.frontmatter["title"].lower()
    if any(kw in title_lower for kw in ["core", "integration", "orchestrat"]):
        return "sonnet"

    # Heuristic 4: Files modified > 5 → Sonnet (complex changes)
    if len(prp.frontmatter["files_modified"]) > 5:
        return "sonnet"

    # Default: Haiku for fast structural review
    return "haiku"
```

**Rationale**:
- **Haiku**: Fast structural checks (YAML complete, sections exist) - $0.03 per PRP
- **Sonnet**: Deep semantic analysis (dependencies, architecture, consistency) - $0.15 per PRP
- **Automatic selection**: Based on complexity, scope, and role in batch

**Token Distribution** (typical batch with 10 PRPs):
- Haiku reviews: 6 PRPs × 7k tokens = 42k tokens
- Sonnet reviews: 4 PRPs × 15k tokens = 60k tokens
- Shared context: 20k tokens (read once)
- **Total**: ~122k tokens

**Cost**: ~$0.50-1.00 per batch (vs $3-5 without optimization = **80% savings**)

---

## Monitoring Protocol

Same as batch-gen-prp:

**Heartbeat Files**: `.tmp/batch-review/PRP-{prp_id}.status`

```json
{
  "prp_id": "34.2.1",
  "status": "analyzing",
  "progress": 60,
  "current_check": "Checking dependencies (6/10)",
  "timestamp": 1699564823,
  "model": "haiku"
}
```

**Polling**:
- Interval: 30 seconds
- Kill timeout: 2 failed polls (60s)
- Max timeout: 2 minutes per PRP

**Kill Policy**:
- Poll 1 (30s): No heartbeat → ⚠ WARNING
- Poll 2 (60s): Still no heartbeat → ❌ KILL
- Mark as FAILED, continue with other agents

---

## Flags

```bash
# Review Mode
--exe              # Review execution results (after /batch-exe-prp)
--execution        # Alias for --exe (same behavior)

# Model selection
--fast             # Use Haiku only (structural review, fast)
--quality          # Use Sonnet only (deep semantic review, thorough)
--hybrid           # Explicitly use default hybrid approach (optional)

# Scope
--batch <id>       # Review entire batch
--retry-failed     # Re-review only failed PRPs from previous run
--focus <aspect>   # Focus on: dependencies|architecture|consistency|all

# Output
--verbose          # Show detailed check-by-check results
--json             # Output JSON only (for scripts)
--quiet            # Minimal output

# Filtering
--stage <num>      # Review only specific stage
--prp <id>         # Review specific PRP
```

---

## Error Handling

### 1. Circular Dependencies

```
❌ Circular dependency detected during staging:
  PRP-34.2.2 → PRP-34.3.2 → PRP-34.2.2

Cannot proceed with review. Fix dependencies first.
```

### 2. Reviewer Timeout

```
⚠ PRP-34.3.2 reviewer timeout (2 minutes, no heartbeat)
  Status: FAILED (killed)

Continue with remaining PRPs? [Y/n]: y

Continuing with 10/11 PRPs...
```

### 3. Invalid JSON Response

```
⚠ PRP-34.2.1 reviewer returned invalid JSON:
  Error: Unexpected token at line 5
  Raw output: "The PRP looks good overall..."

Fallback: Treating as NEEDS_MANUAL_REVIEW
```

---

## Output Files

```
.tmp/batch-review/
├── batch-34-summary.json        # Aggregated results (JSON)
├── batch-34-report.md           # Human-readable report (Markdown)
├── PRP-34.1.1.status            # Heartbeat file (deleted after)
├── PRP-34.1.1.review.json       # Individual review result
├── PRP-34.2.1.status
├── PRP-34.2.1.review.json
└── ...
```

**Individual Review JSON**:
```json
{
  "prp_id": "34.2.1",
  "prp_file": "PRPs/feature-requests/PRP-34.2.1-detection-module-phase-a.md",
  "review_timestamp": "2025-11-05T00:05:30Z",
  "reviewer_model": "sonnet",
  "structural_review": {
    "score": 10,
    "checks_passed": 10,
    "checks_failed": 0,
    "issues": [],
    "warnings": []
  },
  "semantic_review": {
    "score": 8,
    "checks_passed": 8,
    "checks_failed": 0,
    "alignment_with_plan": "ALIGNED",
    "issues": [],
    "warnings": ["Estimated hours conservative"]
  },
  "recommendation": "APPROVE",
  "detailed_notes": "Excellent alignment with master plan. Implementation follows strategy pattern correctly. All dependencies accurate."
}
```

---

## Integration with Batch Workflow

**Full Workflow** (universal, works for ANY batch):
```bash
# Step 1: Generate PRPs from master plan
/batch-gen-prp PRPs/feature-requests/PRP-{N}-INITIAL.md
# Output: PRPs in PRPs/feature-requests/PRP-{N}.*.md

# Step 2: Document Peer Review (BEFORE execution)
/batch-peer-review --batch {N}
# Output: X approved, Y need revision

# Step 3: Fix issues in failed PRPs
# Edit PRPs identified as NEEDS_REVISION

# Step 4: Re-review failed PRPs only
/batch-peer-review --batch {N} --retry-failed
# Output: All approved (or iterate until all pass)

# Step 5: Execute batch
/batch-exe-prp --batch {N}

# Step 6: Execution Peer Review (AFTER execution)
/batch-peer-review --batch {N} --exe
# Output: X execution approved, Y need fixes

# Step 7: Fix execution issues (if any)
# Edit code identified as NEEDS_FIXES

# Step 8: Re-review execution
/batch-peer-review --batch {N} --exe --retry-failed
# Output: All execution approved

# Step 9: Commit and push
git add . && git commit -m "Implement batch {N}"
git push
```

**Benefits**:
- **Document review**: Catch issues BEFORE execution (saves time and cost)
- **Execution review**: Validate implementation matches spec (quality gate)
- Ensure consistency across batch (terminology, dependencies, code quality)
- Detect inter-PRP problems early (file conflicts, circular deps, integration issues)
- Works for any domain (blending, tooling, features, refactoring)

---

## Performance Characteristics

### Token Usage

**Without Shared Context** (naive):
- 11 PRPs × (50k context + 5k PRP + 15k analysis) = **770k tokens**

**With Shared Context** (optimized):
- 20-50k shared context (read once, varies by master plan size)
- 11 PRPs × (5k PRP + 10k analysis) = 165k tokens
- Total: **185-215k tokens**
- **Savings: 72-76%** (555-585k tokens saved)

**Hybrid Haiku/Sonnet** (ultra-optimized):
- 20-50k shared context (varies by project)
- 6 Haiku reviews: 6 × 7k = 42k tokens
- 5 Sonnet reviews: 5 × 15k = 75k tokens
- Total: **137-167k tokens**
- **Savings: 78-82%** (603-633k tokens saved)

### Time

**Sequential**: 11 PRPs × 2 min = 22 minutes

**Parallel** (staged):
- Stage 1: 1 PRP × 2 min = 2 min
- Stage 2: 6 PRPs in parallel = 2 min
- Stage 3: 3 PRPs in parallel = 2 min
- Stage 4: 1 PRP × 2 min = 2 min
- **Total: 8 minutes**
- **Savings: 64%** (14 minutes saved)

### Cost

**Haiku pricing**: $0.25/M input, $1.25/M output
**Sonnet pricing**: $3.00/M input, $15.00/M output

**Hybrid approach**:
- Haiku: 42k input + 6k output = $0.02
- Sonnet: 125k input + 25k output = $0.75
- **Total: ~$0.77 per batch**

**All-Sonnet** (baseline):
- 215k input + 40k output = **$1.25 per batch**
- **Savings: 38%**

---

## Tips

1. **Run before execution**: Catch issues early (cheaper than fixing during execution)
2. **Focus reviews**: Use `--focus dependencies` if only checking deps
3. **Iterative fixing**: Use `--retry-failed` after fixing issues
4. **Combine with validation**: Run validation tools before peer review
5. **Save reports**: Keep `.tmp/batch-review/` for audit trail

---

## Next Steps

After batch peer review:
1. Fix identified issues in PRPs
2. Re-run review on failed PRPs: `/batch-peer-review --batch 34 --retry-failed`
3. Once all approved, execute: `/batch-exe-prp --batch 34`
4. Archive review reports for documentation


ARGUMENTS: --batch <batch-id>|<prp-file-1> <prp-file-2> ...

Flags:
  --batch <id>        Review entire batch (e.g., --batch 34)
  --fast              Use Haiku only (structural review)
  --quality           Use Sonnet only (deep semantic review)
  --retry-failed      Re-review only failed PRPs
  --verbose           Show detailed check-by-check results
  --json              Output JSON only
  --quiet             Minimal output
  --stage <num>       Review only specific stage
  --focus <aspect>    Focus on: dependencies|architecture|consistency|all

---

## See Also

**Related Commands**:
- `/peer-review` - Review single PRP in detail (document or execution)
- `/batch-gen-prp` - Generate batch of PRPs from master plan
- `/batch-exe-prp` - Execute batch of PRPs in parallel
- `/generate-prp` - Generate single PRP from natural language
- `/execute-prp` - Execute single PRP implementation

**When to Use Each**:
- **`/batch-peer-review`** - Systematic review of all PRPs, inter-PRP consistency checks, parallel efficiency
- **`/peer-review`** - Deep dive into one specific PRP, detailed analysis, spot checks during batch workflow

**Documentation**:
- Batch workflow: See workflow diagrams and integration section above
- Single PRP review: See `/peer-review` command documentation
- PRP generation: See `/batch-gen-prp` and `/generate-prp` documentation
