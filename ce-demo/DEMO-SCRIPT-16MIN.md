# Context Engineering Demo Script (16 Minutes - Condensed)

**By Cole Medin (@coleam00)**
**GitHub:** https://github.com/coleam00/context-engineering-intro

---

## Slide 1: Title + Hook (1.5 min)

### Visual
- Title: **"Context Engineering: Stop Vibe Coding, Start Building"**
- Subtitle: "The systematic approach to making AI assistants actually work"
- Background: Light gradient (white → cream)
- Emoji: 🎯

### Script
> "Quick question: How many of you have asked AI to build a feature, and it broke your patterns, missed edge cases, or just didn't fit your codebase?"

> "That's **vibe coding**—and it fails 80% of the time on complex tasks."

> "Today, I'll show you **Context Engineering**—a framework that's 10x better than prompt engineering, with 85% success rate on production code."

**Transition:** "First, the problem..."

---

## Slide 2: The Problem (1.5 min)

### Visual
- Comparison table (3 columns)

| Approach | Success Rate | Example |
|----------|--------------|---------|
| ❌ **Vibe Coding** | ~20% | "Add user auth" |
| ⚠️ **Prompt Engineering** | ~40% | "Add JWT-based auth using bcrypt..." |
| ✅ **Context Engineering** | ~85% | Full framework with rules, examples, validation |

### Script
> "**Vibe coding**—just describing what you want—works for trivial tasks, fails on complexity."

> "**Prompt engineering**—crafting perfect prompts—is better but brittle. Change your codebase, prompt breaks."

> "**Context Engineering**—instead of *how* you ask, engineer *what context* the AI has. Rules, examples, validation—everything it needs."

**Transition:** "What is Context Engineering?"

---

## Slide 3: Definition (1 min)

### Visual
- Definition box centered
- Emoji: 💡

### Content
> **Context Engineering** is systematically preparing AI coding assistants for complex tasks by providing comprehensive, structured information—rules, examples, patterns, and validation—rather than relying on clever prompts.

**Key Insight:**
> 💡 Most AI failures = **insufficient context**, not model limitations.

### Script
> "Simple: Build a complete information system telling the AI *how your project works*."

> "Like onboarding a new dev. You don't say 'go build X.' You give them the style guide, architecture docs, code examples, testing patterns."

> "Context Engineering does the same—for AI assistants."

**Transition:** "Let me show you the framework..."

---

## Slide 4: Framework Overview (1.5 min)

### Visual
- Mermaid diagram (workflow.mermaid)

### Script
> "Four core components:"

> "**1. CLAUDE.md** - Your project's rules. Testing, style, gotchas."

> "**2. PRPs** - Implementation blueprints. Not just *what*, but *how* using your patterns."

> "**3. /generate-prp** - AI researches your code, writes comprehensive PRP."

> "**4. /execute-prp** - AI implements with continuous validation—lint, tests, integration."

**Transition:** "Now live demo—10 minutes..."

---

## Slides 5-8: Live Demo (8 min)

### Demo Part 1: Project Structure (1 min)

**Show terminal:**

```bash
tree -L 2 -I 'node_modules|.git'
```

> "Here's a Context Engineering project:"
> - **CLAUDE.md** - Project rules
> - **PRPs/** - Implementation plans
> - **examples/** - Code patterns
> - **INITIAL.md** - Feature requests

---

### Demo Part 2: Feature Request (1 min)

**Show INITIAL.md:**

```markdown
FEATURE: Add API endpoint for user profile export

GET /api/users/{id}/export → JSON with:
- Basic info (name, email, created date)
- Preferences
- Activity history (last 30 days)

EXAMPLES:
See examples/api/user-endpoint.ts
See examples/tests/api-test.test.ts

GOTCHAS:
- Respect privacy settings
- Rate limit: 10 req/hour
- Requires auth token
```

> "Notice: Feature description + **your examples** + **gotchas**."

---

### Demo Part 3: Generate PRP (3 min)

**Run command:**

```bash
/generate-prp INITIAL.md
```

**Show progress:**
```
✓ Reading INITIAL.md
✓ Analyzing examples/
✓ Fetching docs
✓ Generating validation checklist
✓ Writing PRP to PRPs/executed/PRP-1-user-export.md
```

> "It researched our codebase, read docs, analyzed patterns, wrote complete plan."

**Show PRP excerpt:**

```markdown
# PRP-1: User Profile Export

## Goal
Create GET /api/users/{id}/export endpoint

## Implementation Blueprint
1. Create endpoint handler in api/users.py
2. Add ExportProfileSerializer
3. Implement privacy filtering
4. Add rate limiting
5. Write unit tests (3 cases)
6. Integration test with curl

## Validation Gates
- ✓ Lint with Ruff
- ✓ Type check with MyPy
- ✓ Unit tests pass
- ✓ Manual curl test
```

> "**Complete screenplay.** AI knows exactly how to implement using our patterns."

---

### Demo Part 4: Execute PRP (3 min)

**Run command:**

```bash
/execute-prp PRPs/executed/PRP-1-user-export.md
```

**Show execution:**

```
✓ Task 1: Create endpoint handler
  ✓ Lint check passed
✓ Task 2: Add serializer
  ✓ Type check passed
✓ Task 3: Privacy filtering
  ✓ Unit tests pass (3/3)
✓ Task 4: Rate limiting
  ✓ Integration test passed
✅ PRP-1 completed successfully
```

> "After *every step*, it validates. Linting, type checking, tests."

> "If test fails? Reads error, fixes, re-runs. **Self-correcting.**"

**Test:**

```bash
curl -H "Authorization: Bearer token" \
  http://localhost:8000/api/users/1/export | jq
```

```json
{
  "user_id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "activity_last_30_days": [...]
}
```

> "Production-ready code. Follows our patterns, includes tests, just works."

---

## Slide 9: Key Components (1.5 min)

### Visual
- Three cards horizontal

**CLAUDE.md** 📋
- Code structure
- Testing conventions
- Style guidelines
- Known gotchas

**PRPs** 📝
- Goal & Context
- Implementation Blueprint
- Validation Gates
- Anti-Patterns

**examples/** 💻
- Real code patterns
- Test structures
- Integration methods

### Script
> "Three components:"

> "**CLAUDE.md** - Global rules. 'Always TypeScript strict,' 'Test with pytest,' 'Never hardcode keys.'"

> "**PRPs** - Implementation blueprints. Context, ordered tasks, pseudocode, validation."

> "**Examples/** - Shows AI what 'good' looks like. It pattern-matches these."

**Transition:** "Results..."

---

## Slide 10: Benefits & Results (1 min)

### Visual
- 2x2 grid

**🎯 Consistency**
Code follows your patterns 100%

**🔄 Self-Correction**
Built-in validation catches errors

**🏗️ Complex Tasks**
Multi-file features end-to-end

**⚡ Speed**
10x faster than manual

**Stats:**
- **85%+ success rate** on complex tasks
- **11,000+ GitHub stars** in 2 months
- **50+ production projects** using framework

### Script
> "**Consistency:** Every feature follows your architecture."

> "**Self-correction:** Validation loops catch mistakes. Failed test? AI fixes it."

> "**Complex tasks:** Multi-file features with migrations, API changes, tests—all correct."

> "**Speed:** Features that took days now take hours."

> "11,000+ developers starred the repo. Dozens in production."

**Transition:** "Try it yourself..."

---

## Slide 11: Get Started (1 min)

### Visual
- QR code (left)
- Quick start (right)

### Content

**🚀 Quick Start**

```bash
1. git clone https://github.com/coleam00/
   context-engineering-intro

2. Customize CLAUDE.md

3. Add examples/

4. Write INITIAL.md

5. /generate-prp
   /execute-prp
```

**📖 Full Tutorial**
[QR code → TUTORIAL.md]

**🔗 Resources**
- GitHub: coleam00/context-engineering-intro
- Discord: [Community]
- Twitter: @coleam00

### Script
> "Want to try?"

> "1. Clone template"
> "2. Customize CLAUDE.md with your rules"
> "3. Add examples"
> "4. Write feature request"
> "5. Run the commands"

> "Full tutorial [point to QR]—deep dive with advanced patterns."

> "Template is free, open-source, works with Claude Code out of the box."

---

## Q&A Setup (1 min remaining)

### Script
> "That's Context Engineering. Questions?"

**Quick Answers:**

**Q: "Only Claude Code?"**
A: "Works with any AI assistant. Claude Code has best tooling, but principles are universal."

**Q: "Setup time?"**
A: "First project: 2-3 hours. After that, 30 minutes—you reuse patterns."

**Q: "Existing projects?"**
A: "Absolutely. Document current patterns in CLAUDE.md, add examples, start using PRPs for new features."

---

## Timing Breakdown

- Slides 1-3 (Problem + Solution): 4 min
- Slide 4 (Framework): 1.5 min
- Slides 5-8 (Demo): 8 min
- Slides 9-10 (Components + Benefits): 2.5 min
- Slide 11 (Get Started): 1 min
- Buffer/Q&A: 1 min

**Total: 16 minutes**

---

## Differences from 20-Minute Version

**Cut from 20 min → 16 min:**

1. **Shorter intros** (2 min → 1.5 min each for Slides 1-2)
2. **Combined concepts** (Philosophy slide removed, integrated into Slide 3)
3. **Faster demo** (12 min → 8 min)
   - Quick file tree (2 min → 1 min)
   - Condensed PRP generation (3 min → 3 min, but faster narration)
   - Faster execution (3 min → 3 min, but less detail)
4. **Simplified components** (2 min → 1.5 min)
5. **Shorter benefits** (2 min → 1 min, removed detailed stats discussion)

**Keep:**
- Full live demo (critical centerpiece)
- All core concepts
- QR code for deep dive
- Q&A time

---

## Presenter Notes

### Pacing Tips
- **Speak faster** in intro/components sections
- **Slow down** during demo (audience needs to see commands)
- **Don't add extra stories** (stick to script)
- **Practice transitions** (save 10-15 seconds each)

### Demo Optimization
- **Pre-type INITIAL.md** (copy-paste during demo)
- **Use fast terminal** (zsh with instant prompt)
- **Have PRP pre-generated** (backup if /generate-prp slow)
- **Speed up command output** (if possible, or use pre-captured)

### Energy Management
- **High energy** for problem/solution (Slides 1-3)
- **Focused** during demo (Slides 5-8)
- **Enthusiastic** for results (Slide 10)
- **Inviting** for get started (Slide 11)

---

**END OF 16-MINUTE SCRIPT**

*Optimized for time while preserving core message and live demo*
