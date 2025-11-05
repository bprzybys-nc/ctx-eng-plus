# /peer-review - Context-Naive Peer Review Command

Perform context-naive peer review of specified PRP work with optional execution review.

## Usage

```bash
/peer-review [prp-reference] [exe|execution]
```

## Parameters

### 1. prp-reference (optional, default: latest)
Specify which PRP to review using one of these formats:

- **PRP ID**: `PRP-8.8` or `8.8` or `34.2.1` (batch notation)
- **File path**: `context-engineering/PRPs/PRP-8.8-web-ui-ux-improvements.md`
- **Natural language**: `"shift pattern logic"` or `"web ui ux improvements"`
- **Keyword**: `latest` (most recent PRP from conversation)
- **Batch context**: If batch active, searches within batch PRPs first

### 2. exe|execution (optional)
Control review mode:

- **Absent**: Document review only (default mode)
- **exe**: Review PRP execution results (assumes PRP already executed)
- **execution**: Alias for `exe` (same behavior, clearer intent)

## Batch Context Integration

When working within a batch workflow, `/peer-review` automatically understands batch context:

```bash
# After /batch-gen-prp or during /batch-exe-prp
/peer-review 34.2.1              # Review specific PRP from batch 34
/peer-review latest              # Review latest PRP in batch context
/peer-review "classification"    # Search within batch 34 PRPs first

# Execution review within batch
/peer-review 34.2.1 exe          # Review execution of one PRP in batch
/peer-review latest execution    # Review execution of latest PRP in batch
```

**Batch Context Detection**:
- Checks for active batch in conversation (from `/batch-gen-prp` or `/batch-exe-prp`)
- Prioritizes PRPs within active batch when searching
- Falls back to all PRPs if not found in batch
- **For full batch review**: Use `/batch-peer-review` for systematic review of all PRPs with inter-PRP consistency checks

**When to Use Single vs Batch Review**:
- **Use `/peer-review`** (this command): Deep dive into one specific PRP, detailed analysis, spot checks
- **Use `/batch-peer-review`**: Systematic review of all PRPs, inter-PRP consistency, parallel efficiency

## Examples

```bash
# Review latest PRP document (no execution review)
/peer-review

# Review specific PRP by ID
/peer-review PRP-8.8

# Review specific PRP in batch (batch notation)
/peer-review 34.2.1

# Find PRP by natural language description
/peer-review "shift pattern logic"

# Review execution of already-executed PRP
/peer-review PRP-8.8 exe

# Review execution of batch PRP
/peer-review 34.2.1 execution

# Review execution of most recent PRP
/peer-review latest execution

# Batch workflow examples
/peer-review 34.2.1              # Document review (before execution)
/peer-review 34.2.1 exe          # Execution review (after execution)
/peer-review latest              # Latest PRP in active batch
```

## Review Process

### Phase 1: Document Review (Always Performed)

1. **Locate PRP**: Find PRP file from reference parameter
2. **Read Fresh**: Read PRP as standalone artifact, ignoring generation conversation
3. **Evaluate Quality**:
   - ✅ Completeness: All sections present and detailed?
   - ✅ Clarity: Technical requirements unambiguous?
   - ✅ Feasibility: Implementation approach sound?
   - ✅ Testability: Acceptance criteria measurable?
   - ✅ Edge Cases: Potential issues identified?
   - ✅ Alignment with CLAUDE.md guidelines.
   - ✅ Existing patterns (ce examples) and architecture respectation
   - ✅ Existing code reuse
   - ✅ Check also serena memories for more guidelines

4. **Provide Recommendations**: Actionable improvements
5. **Apply Improvements**: Update PRP unless profound questions arise
6. **Document Review**: Add review notes to PRP appendix

### Phase 2: Execution Review (Only if exe|execution flag present)

**Prerequisite**: PRP must already be executed via `/execute-prp` or manual implementation

1. **Read PRP Requirements**: Review what was supposed to be implemented
2. **Read Changed Files Fresh**: Read implementation as standalone artifacts, ignoring implementation conversation
3. **Evaluate Execution**:
   - ✅ Implementation matches PRP requirements?
   - ✅ Code quality meets project standards?
   - ✅ Acceptance criteria satisfied?
   - ✅ Unintended side effects detected?
   - ✅ Edge cases handled?
   - ✅ No implementation violating guidelines specified in Document Review (CLAUDE.md)
   - ✅ No implementation violating existing patterns (ce examples) and architecture respectation
   - ✅ No implementation duplicating existing code (should extend existing code)
   - ✅ Check also serena memories for more guidelines not to violate

4. **Provide Recommendations**: Actionable fixes
5. **Apply Fixes**: Update code unless profound questions arise
6. **Document Execution Review**: Add notes to PRP execution section

## Output Format

### Document Review Output

```markdown
## Context-Naive Peer Review: Document

**PRP**: PRP-8.8-web-ui-ux-improvements.md
**Reviewed**: 2025-10-02T19:55:00Z

### Findings
- ✅ Strength 1: Clear structure with before/after code examples
- ✅ Strength 2: Specific line numbers for all changes
- ⚠️ Issue 1: React Hooks violation in Change #4
- ⚠️ Issue 2: className inconsistency in documentation

### Recommendations Applied
1. Fixed React Hooks pattern: Moved to Set-based state management
2. Removed gap-2 from button className
3. Added explicit useState import statement
4. Fixed target state diagram to show flat ZIP structure

### Questions for User
(None - all issues resolved)
```

### Execution Review Output (if exe|execution flag used)

```markdown
## Context-Naive Peer Review: Execution

**PRP**: PRP-8.8-web-ui-ux-improvements.md
**Execution Reviewed**: 2025-10-02T20:00:00Z

### Implementation Findings
- ✅ Change #1: ZIP structure simplified correctly (main.py:609)
- ✅ Change #2: Section numbering removed (App.tsx:91,100,146)
- ✅ Change #3: Download button text updated (App.tsx:202)
- ⚠️ Issue: useState import missing from App.tsx
- ❌ Critical: expandedJobs state not initialized at component level

### Fixes Applied
1. Added useState import to App.tsx line 2
2. Initialized expandedJobs Set state at component level
3. Tested expanded state persistence during polling

### Questions for User
(None - all issues resolved)
```

## Context-Naive Definition

**What It Means**:
- **IGNORE**: Conversation that generated PRP or implementation code
- **USE**: Project context (CLAUDE.md, codebase structure, ce examples, existing PRPs, serena memories)
- **GOAL**: Fresh perspective as if first time reading the artifact

**Why It Matters**:
- Catches inconsistencies between plan and code
- Identifies assumptions made during rapid development
- Validates documentation matches implementation
- Ensures artifacts are self-documenting

## Error Handling

### PRP Not Found
```
❌ PRP not found: "shift pattern logic"

Available PRPs matching search:
- PRP-5.2: Shift Patterns Logic Implementation
- PRP-5.3: Critical Validation Enum Fixes

Please specify: /peer-review PRP-5.2
```

### Multiple Matches
```
⚠️ Multiple PRPs match "shift pattern":
1. PRP-5.2: Shift Patterns Logic Implementation
2. PRP-6.9.3: Shift Pattern Hour Ranges

Please clarify which PRP to review.
```

### Execution Review Without Execution
```
⚠️ Execution review requested but PRP not executed: PRP-8.8

Please execute PRP first:
/execute-prp PRP-8.8

Then review execution:
/peer-review PRP-8.8 exe
```

## Integration with Workflow

### Single PRP Workflow

#### After Generate PRP (Document Review)
```bash
# Generate PRP
/generate-prp "Web UI UX improvements"

# Immediately review document quality
/peer-review latest

# Result: PRP improved before any coding starts
```

#### After Execute PRP (Execution Review)
```bash
# Execute PRP implementation
/execute-prp PRP-8.8

# Review execution results with fresh eyes
/peer-review PRP-8.8 execution

# Result: Catches implementation issues vs spec
```

#### Complete Single PRP Workflow
```bash
# Step 1: Generate and review PRP document
/generate-prp "simplify ZIP structure"
/peer-review latest

# Step 2: Execute PRP
/execute-prp latest

# Step 3: Review execution
/peer-review latest exe

# Result: High-quality PRP + implementation
```

### Batch PRP Workflow

#### During Batch Execution (Individual PRP Review)
```bash
# Generate batch
/batch-gen-prp PRP-34-INITIAL.md

# Review individual PRP in batch (if needed)
/peer-review 34.2.1              # Review doc before batch execution
/peer-review "classification"    # Search by keyword in batch

# Execute batch
/batch-exe-prp --batch 34

# Review individual PRP execution (if issues found)
/peer-review 34.2.1 exe          # Review execution of one PRP
/peer-review latest execution    # Review latest executed PRP in batch
```

#### When to Use Single vs Batch Review

**Use `/peer-review` (single) when**:
- Reviewing one specific PRP in detail
- Fixing issues in one PRP during batch workflow
- Iterating on one PRP before batch execution
- Deep dive into one PRP's execution

**Use `/batch-peer-review` (batch) when**:
- Reviewing all PRPs in batch systematically
- Checking inter-PRP consistency (deps, terminology, file conflicts)
- Quality gate before/after batch execution
- Parallel review of multiple PRPs

### Quality Gate Before Merge
```bash
# Review completed PRP execution (single)
/peer-review PRP-8.8 execution

# Review completed batch execution (batch)
/batch-peer-review --batch 34 --exe

# Validates:
# - All changes implemented correctly
# - No unintended side effects
# - Acceptance criteria met
# - (Batch only) Inter-PRP integration correct
```

## Command Implementation

This command should:
1. **Detect Batch Context**:
   - Search conversation for recent `/batch-gen-prp` or `/batch-exe-prp` calls (last 10 messages)
   - Extract batch ID from command: `/batch-gen-prp PRP-34-INITIAL.md` → batch 34
   - OR detect batch notation in PRP reference: `34.2.1` → batch 34
   - OR scan for batch PRP files in recent context (e.g., `PRP-34.2.1.md`)
   - Use detected batch ID to prioritize batch PRPs when searching (search `PRPs/feature-requests/PRP-{batch_id}.*` first)
2. **Parse prp-reference parameter**:
   - ID formats: `PRP-8.8`, `8.8`, `34.2.1` (batch notation)
   - Filepath: `context-engineering/PRPs/PRP-8.8.md` or `PRPs/feature-requests/PRP-34.2.1.md`
   - Natural language: Search within batch PRPs first (if batch active), then all PRPs
   - "latest": Most recent PRP from conversation (prioritize batch context)
3. **Locate PRP file**:
   - If batch notation (e.g., `34.2.1`): Search `PRPs/feature-requests/PRP-34.2.1*.md`
   - If standard notation: Search `.ce/PRPs/` or `PRPs/` or `context-engineering/PRPs/`
   - If NL search: Prioritize batch PRPs (if batch active), then search all PRPs
4. **Phase 1 - Document Review**:
   - Read PRP document (ignoring generation conversation)
   - Perform systematic quality review (9 checks)
   - Apply recommendations to PRP file
5. **Phase 2 - Execution Review** (if exe|execution flag):
   - Check PRP has been executed (look for changed files from PRP specs)
   - Read implementation files (ignoring implementation conversation)
   - Validate implementation vs PRP requirements (9 checks)
   - Apply fixes to code
6. **Output review summary** with findings + fixes

## Best Practices

**When to Use Document Review Only**:
- After generating new PRP (validate quality before execution)
- Reviewing PRPs created by others
- Planning phase - want to improve docs before coding

**When to Use Execution Review**:
- After `/execute-prp` completes (validate implementation matches spec)
- Before marking PRP as complete
- Quality gate before merging to main branch
- Troubleshooting implementation issues

**Command Efficiency**:
- Use natural language for quick PRP lookup
- Use `latest` to review most recent work
- Separate document and execution reviews for focused feedback

## Related Commands

**Single PRP Commands**:
- `/generate-prp` - Generate new PRP from natural language
- `/execute-prp` - Execute PRP implementation
- `/peer-review` - Review single PRP (document or execution)

**Batch PRP Commands**:
- `/batch-gen-prp` - Generate multiple PRPs from master plan
- `/batch-exe-prp` - Execute batch of PRPs in parallel
- `/batch-peer-review` - Review entire batch (document or execution)

**Context Management**:
- `/update-context` - Update project context after PRP execution

## Workflow Integration

### Single PRP Workflow

```
┌─────────────────┐
│  /generate-prp  │  Create PRP
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  /peer-review   │  Review document quality
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  /execute-prp   │  Implement changes
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ /peer-review exe│  Review execution results
└─────────────────┘
```

### Batch PRP Workflow (with single peer-review for spot checks)

```
┌──────────────────────┐
│  /batch-gen-prp      │  Create batch of PRPs
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ /batch-peer-review   │  Review all PRPs (document)
└──────────┬───────────┘
           │
           ↓  (optional spot checks)
    ┌──────┴──────┐
    │             │
    ↓             ↓
┌──────────────┐ Continue
│ /peer-review │ (individual PRP fixes)
│   34.2.1     │
└──────────────┘
           │
           ↓
┌──────────────────────┐
│  /batch-exe-prp      │  Execute batch (parallel)
└──────────┬───────────┘
           │
           ↓
┌──────────────────────┐
│ /batch-peer-review   │  Review all executions
│       --exe          │
└──────────┬───────────┘
           │
           ↓  (optional spot checks)
    ┌──────┴──────┐
    │             │
    ↓             ↓
┌──────────────┐ Continue
│ /peer-review │ (individual execution fixes)
│  34.2.1 exe  │
└──────────────┘
           │
           ↓
      ✅ Done
```
