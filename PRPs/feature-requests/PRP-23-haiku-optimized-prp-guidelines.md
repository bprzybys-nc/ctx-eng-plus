---
name: "Haiku-Optimized PRP Writing Guidelines"
description: "Write PRPs that Claude 4.5 Haiku can execute without making decisions - front-load thinking into PRP"
prp_id: "PRP-23"
status: "draft"
created_date: "2025-10-19T20:30:00Z"
priority: "MEDIUM"
complexity: "low"
estimated_hours: "2-4"
risk_level: "LOW"
cwe_ids: []
cvss_score: 0
context_sync:
  ce_updated: false
  serena_updated: false
  last_sync: null
  validation_status: "PENDING"
dependencies:
  - "PRP-22 (reference example of good practices)"
  - "Anthropic GOLD framework documentation"
related_prp: ["PRP-22"]
version: 1
---

# PRP-23: Haiku-Optimized PRP Writing Guidelines

## 🎯 TL;DR

**Problem**: PRPs written for Sonnet/Opus require Haiku to make decisions during execution (choosing approaches, handling edge cases). Haiku excels at mechanics but struggles with reasoning.

**Solution**: Front-load all decisions into PRP document. Haiku executes concrete steps, not abstract thinking.

**Key Principle**: **"Decide in PRP, Execute in Haiku"**

**Impact**:
- ✅ Haiku costs 15x less than Opus - use it for execution, not reasoning
- ✅ Haiku is 2-3x faster - well-structured PRPs execute quickly
- ✅ Fewer errors - less decision-making during execution
- ✅ Scalable - template makes consistency easy

---

## 🔧 The Pattern: What Haiku Needs

### ✅ DO This (Front-load decisions)

| Category | Good | Bad |
|----------|------|-----|
| **Code Changes** | "Replace lines 35-40 with: [exact code]" | "Refactor run_cmd() for safety" |
| **Validation** | `uv run pytest tests/test_security.py -q` | "Ensure security is verified" |
| **Decisions** | "Use shlex.split() for string parsing" | "Choose safe string parsing approach" |
| **Edge Cases** | "Empty commands raise ValueError" | "Handle edge cases appropriately" |
| **References** | File paths with line numbers | Vague section references |

### ❌ DON'T Do This (Delegate reasoning)

```
❌ "Decide between approach A and B based on performance"
✅ "Use approach A (selected for: lower memory, faster execution)"

❌ "Handle error cases appropriately"
✅ "On timeout, raise TimeoutError with message: 'Command timed out after Xs: ...'"

❌ "Optimize the function"
✅ "Replace shell=True with shell=False to eliminate CWE-78 injection vector"
```

---

## 📐 GOLD Framework Quick Reference

Apply this structure to every PRP:

### **G**oal
**What exactly should be achieved?** Not "improve X" but "achieve state Y".

Example (good):
```
✅ Eliminate CWE-78 command injection vulnerability by replacing all
   subprocess.run(shell=True) with shell=False + shlex.split()
```

Example (bad):
```
❌ Improve security and make command execution safer
```

### **O**utput
**What is the exact deliverable format?** Be specific about structure, not vague about quality.

Example (good):
```
✅ Python functions with:
   - Function signature with type hints
   - Docstring (Args, Returns, Raises sections)
   - Implementation using shell=False
   - Tests with 3+ test cases
```

Example (bad):
```
❌ Well-written functions that are secure and documented
```

### **L**imits
**What are the scope boundaries?** Define what's IN and OUT.

Example (good):
```
✅ Scope: tools/ce/ directory only
✅ Time budget: 2 hours for implementation
✅ Test coverage: 80%+ for new code
❌ Out of scope: Update other projects, modify dependencies
```

### **D**ata
**What context does Haiku need?** Include it inline, don't reference external docs.

Example (good):
```
✅ Inline: Current code snippet at tools/ce/core.py:35
✅ Inline: Before/after code comparison in PRP body
✅ Inline: Git status, file structure, dependencies
```

Example (bad):
```
❌ "See context.py for details"
❌ "Review the architecture document"
```

### **E**valuation
**How do you verify success?** Make it binary - PASS/FAIL, not subjective.

Example (good):
```
✅ Gate 1: cd tools && grep -r "shell=True" ce/ | wc -l
   Expected: 0 matches (PASS if zero, FAIL otherwise)

✅ Gate 2: cd tools && uv run pytest tests/test_security.py -q
   Expected: All tests pass (FAIL if any test fails)
```

Example (bad):
```
❌ "Verify implementation is correct"
❌ "Check that code quality is high"
```

---

## ✅ Haiku-Ready PRP Checklist

Use this before committing a PRP. All answers should be **YES**.

- [ ] **Goal**: Can I state the exact end state in 1 sentence?
- [ ] **Output**: Do I specify exact file paths and line numbers?
- [ ] **Limits**: Are scope boundaries explicit (what's IN/OUT)?
- [ ] **Data**: Is all required context inline in the PRP (no "see file X")?
- [ ] **Evaluation**: Are validation gates copy-paste bash commands?
- [ ] **Decisions**: Did I make all architectural decisions, or am I asking Haiku to choose?
- [ ] **Code Snippets**: Do I include before/after examples for major changes?
- [ ] **Testing**: Are expected test outputs documented?
- [ ] **Edge Cases**: Are specific edge cases called out with handling instructions?
- [ ] **No Vague Language**: Are there any words like "appropriate", "suitable", "reasonable", "handle"?

---

## 📚 Reference Examples

### PRP-22 (Command Injection Fix) - Well Structured
✅ **Why it works for Haiku:**
- Line 35: Exact vulnerable code location
- Lines 42-46: Exact replacement code with comments
- Lines 548-650: Concrete helper function implementations
- Lines 720-850: 38 specific test cases (not "verify security")
- Validation gates: Copy-paste bash commands with expected output

### What Made It Haiku-Ready
1. Every code change had file:line reference
2. Before/after code was inline, not referenced
3. Test cases were concrete (not "test injection scenarios")
4. Decision made: Use shlex.split() (not "choose safe approach")
5. Edge cases explicit: Empty commands raise ValueError

---

## 🔄 Implementation Steps

### Step 1: Apply GOLD to PRP Template
**File**: `.claude/commands/generate-prp.md`

Update the generated PRP template to include GOLD sections with examples.

```markdown
# Generated PRP Structure

## Goal (1-2 sentences, exact end state)
## Output (Exact deliverables: files, functions, tests)
## Limits (What's IN scope, what's OUT)
## Data (Inline code, file references, context)
## Evaluation (Validation gates: bash commands + expected output)
```

### Step 2: Add Checklist to Template
Include the 10-question checklist in every generated PRP.

### Step 3: Validate Existing PRPs
Run checklist against PRP-20 through PRP-22 as examples.

### Step 4: Document Pattern
Add section to CLAUDE.md: "Haiku-Optimized PRP Checklist"

---

## 🧪 Validation Gates

### Gate 1: Template Includes GOLD
**Command:**
```bash
grep -E "^## (Goal|Output|Limits|Data|Evaluation)" PRPs/feature-requests/PRP-*.md | head -5
```
**Expected:** Each generated PRP has these 5 sections

### Gate 2: Checklist Present
**Command:**
```bash
grep -c "Haiku-Ready PRP Checklist" PRPs/feature-requests/PRP-*.md | tail -1
```
**Expected:** New PRPs include checklist

### Gate 3: No Vague Language
**Command:**
```bash
grep -i "appropriate\|suitable\|reasonable\|handle\|ensure quality" PRPs/feature-requests/PRP-23-*.md | wc -l
```
**Expected:** 0 matches (excepting within examples/docs)

---

## 📊 Why This Matters

**Cost Impact** (Real Numbers):
- Opus cost: ~$15 per 1M input tokens
- Haiku cost: ~$0.80 per 1M input tokens
- Well-structured PRPs let Haiku execute complex tasks at 15-20x lower cost

**Speed Impact**:
- Opus latency: 2-5s per request
- Haiku latency: 0.5-1s per request
- Haiku executes 2-3x faster for straightforward tasks

**Quality Impact**:
- Fewer decisions = fewer errors
- Explicit validation gates catch issues early
- Reproducible execution (same PRP → same result)

---

## 📖 Web References

**Anthropic Resources:**
- [GOLD Framework for Prompting](https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/claude-4-best-practices) - Anthropic official documentation
- [Claude 3.5 Haiku Model Card](https://www.prompthub.us/models/claude-3-5-haiku) - Model specifications

**Industry Best Practices:**
- AWS: [Best Practices for Fine-tuning Claude 3 Haiku](https://aws.amazon.com/blogs/machine-learning/best-practices-and-lessons-for-fine-tuning-anthropics-claude-3-haiku-on-amazon-bedrock/) - Production patterns
- Stack Overflow: [A practical guide to writing technical specs](https://stackoverflow.blog/2020/04/06/a-practical-guide-to-writing-technical-specs/) - Specification methodology

---

## 📝 Success Criteria

- [ ] GOLD framework applied to generate-prp.md template
- [ ] Haiku-Ready checklist included in generated PRPs
- [ ] PRP-22 used as reference example
- [ ] CLAUDE.md updated with link to PRP-23
- [ ] All new PRPs pass checklist before execution

---

## Generated by
`/generate-prp` command with GOLD framework validation
Status: Ready for review
