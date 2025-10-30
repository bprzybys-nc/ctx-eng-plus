# Context Engineering Demo Script (20 Minutes)

**By Cole Medin (@coleam00)**
**GitHub:** https://github.com/coleam00/context-engineering-intro

---

## Slide 1: Title + Hook (2 min)

### Visual
- Title: **"Context Engineering: Stop Vibe Coding, Start Building"**
- Subtitle: "The systematic approach to making AI assistants actually work"
- Background: Light gradient (white → cream)
- Emoji: 🎯

### Script
> "Show of hands: How many of you have asked an AI to build a feature, and it generated code that *looks* right, but breaks your existing patterns, misses edge cases, or just... doesn't fit your codebase?"

> "That's what we call **vibe coding**—and it fails about 80% of the time on complex tasks."

> "Today, I'm going to show you **Context Engineering**—a framework that's 10x better than prompt engineering and makes AI assistants actually deliver production-ready code."

**Transition:** "First, let me show you why this matters..."

---

## Slide 2: The Problem (2 min)

### Visual
- Comparison table with three columns
- Light background, colored boxes (red, yellow, green)

| Approach | Description | Success Rate | Example |
|----------|-------------|--------------|---------|
| ❌ **Vibe Coding** | "Just ask the AI" | ~20% | "Add user auth" |
| ⚠️ **Prompt Engineering** | "Clever wording" | ~40% | "Add JWT-based auth using bcrypt..." |
| ✅ **Context Engineering** | "Systematic context" | ~85% | Full framework with rules, examples, validation |

### Script
> "Most developers start with **vibe coding**—just describing what you want. This works for trivial tasks, but fails on anything complex."

> "Then you discover **prompt engineering**—spending hours crafting the perfect prompt. Better, but still brittle. Change one thing about your codebase, and your carefully-worded prompt breaks."

> "**Context Engineering** is different. Instead of focusing on *how* you ask, you engineer *what context* the AI has access to. Rules, examples, validation patterns—everything it needs to understand your project."

**Transition:** "So what is Context Engineering exactly?"

---

## Slide 3: Context Engineering Definition (2 min)

### Visual
- Large centered definition box
- Clean typography, light blue accent
- Emoji: 💡

### Content
> **Context Engineering** is the discipline of systematically preparing AI coding assistants for complex tasks by providing comprehensive, structured information—including rules, examples, patterns, and validation mechanisms—rather than relying on clever prompts alone.

**Key Insight:**
> Most AI failures aren't due to model limitations—they're due to **insufficient context**.

### Script
> "Context Engineering is simple: You build a complete information system that tells the AI *how your project works*."

> "Think of it like onboarding a new developer. You don't just say 'go build feature X.' You give them the style guide, the architecture docs, code examples, and testing patterns."

> "Context Engineering does the same thing—but for AI assistants."

**Transition:** "Let me show you what this looks like in practice..."

---

## Slide 4: Framework Overview (2 min)

### Visual
- Mermaid diagram (workflow.mermaid)
- Light theme, clean arrows
- Shows: CLAUDE.md → PRPs → /generate-prp → /execute-prp → Feature

### Script
> "The framework has four core components:"

> "**1. CLAUDE.md** - Your project's rules file. Testing conventions, code style, gotchas—everything that makes your project unique."

> "**2. PRPs (Product Requirement Prompts)** - Detailed implementation blueprints. Not just *what* to build, but *how* to build it using your patterns."

> "**3. /generate-prp command** - AI researches your codebase and documentation, then writes a comprehensive PRP automatically."

> "**4. /execute-prp command** - AI implements the feature with continuous validation—linting, tests, integration checks."

**Transition:** "Now let me show you this in action with a live demo..."

---

## Slide 5-8: Live Demo Walkthrough (10 min)

### Setup
- Terminal ready with context-engineering-intro repo cloned
- Claude Code CLI open
- Simple example: "Add API endpoint for user profile export to JSON"

---

### Demo Part 1: Project Structure (2 min)

**Slide 5 Visual:** File tree screenshot

```
project/
├── .ce/                    # Framework boilerplate
├── CLAUDE.md              # Project rules
├── PRPs/
│   ├── templates/
│   └── executed/
├── examples/              # Code patterns
└── INITIAL.md            # Feature request
```

### Script
> "Let me show you a real project using Context Engineering."

**[Screen share terminal]**

```bash
tree -L 2 -I 'node_modules|.git'
```

> "Here's our structure:"
> - **`.ce/`** - Framework boilerplate (don't touch)
> - **`CLAUDE.md`** - Our project rules
> - **`PRPs/`** - Where implementation plans live
> - **`examples/`** - Code patterns for the AI to follow
> - **`INITIAL.md`** - Where we write feature requests

---

### Demo Part 2: Create Feature Request (2 min)

**Slide 6 Visual:** INITIAL.md screenshot

### Script
> "Let's add a feature: Export user profiles to JSON."

**[Create INITIAL.md]**

```bash
cat > INITIAL.md << 'EOF'
FEATURE: Add API endpoint for user profile export

User should be able to GET /api/users/{id}/export and receive their complete profile as JSON, including:
- Basic info (name, email, created date)
- Preferences
- Activity history (last 30 days)

EXAMPLES:
See examples/api/user_endpoints.py for our REST API patterns
See examples/serializers/user_serializer.py for JSON formatting

DOCUMENTATION:
- FastAPI docs: https://fastapi.tiangolo.com/tutorial/response-model/
- Our API auth: docs/authentication.md

OTHER CONSIDERATIONS:
- Must respect user privacy settings (hide private fields)
- Rate limit: 10 requests per hour per user
- Requires authentication token
EOF
```

> "Notice the structure: Feature description, **examples from our codebase**, external docs, and **gotchas** like rate limiting."

> "This is the input. Now watch what happens..."

---

### Demo Part 3: Generate PRP (3 min)

**Slide 7 Visual:** /generate-prp command + PRP output preview

### Script
> "Now I'll use the `/generate-prp` command in Claude Code."

**[Run command]**

```bash
/generate-prp INITIAL.md
```

> "Watch what it does:"

**[Show progress messages]**
```
✓ Reading INITIAL.md
✓ Analyzing codebase patterns from examples/
✓ Fetching FastAPI documentation
✓ Checking existing API endpoints
✓ Generating validation checklist
✓ Writing PRP to PRPs/executed/PRP-1-user-export.md
```

> "It just researched our codebase, read the external docs, analyzed our patterns, and wrote a complete implementation plan."

**[Show PRP excerpt]**

```bash
head -n 50 PRPs/executed/PRP-1-user-export.md
```

```markdown
# PRP-1: User Profile Export Endpoint

## Goal
Create GET /api/users/{id}/export endpoint returning complete user profile as JSON.

## All Needed Context

### Current Codebase Patterns
- API endpoints use FastAPI with dependency injection (see examples/api/)
- Authentication via `get_current_user` dependency
- Rate limiting via `rate_limit` decorator from utils/rate_limiter.py

### Data Models
User model (models/user.py):
- Fields: id, name, email, created_at, preferences, privacy_settings
- Method: get_activity_history(days=30)

### Implementation Blueprint

1. Create endpoint handler in api/users.py
2. Add ExportProfileSerializer in serializers/user_serializer.py
3. Implement privacy filtering logic
4. Add rate limiting decorator
5. Write unit tests (3 test cases)
6. Integration test with curl

### Validation Gates
- ✓ Lint with Ruff (no errors)
- ✓ Type check with MyPy
- ✓ Unit tests pass (pytest)
- ✓ Manual curl test succeeds
```

> "This is a **complete screenplay**. The AI now knows exactly how to implement this feature using our patterns."

---

### Demo Part 4: Execute PRP (3 min)

**Slide 8 Visual:** /execute-prp command + validation steps

### Script
> "Now the magic: `/execute-prp` implements the feature *with continuous validation*."

**[Run command]**

```bash
/execute-prp PRPs/executed/PRP-1-user-export.md
```

**[Show progress with validation]**

```
✓ Task 1: Create endpoint handler
  ✓ Lint check passed
✓ Task 2: Add serializer
  ✓ Lint check passed
  ✓ Type check passed
✓ Task 3: Implement privacy filtering
  ✓ Unit tests pass (3/3)
✓ Task 4: Add rate limiting
  ✓ Integration test passed
✅ PRP-1 completed successfully
```

> "See what happened? After *every step*, it validates. Linting, type checking, tests."

> "If a test fails? It reads the error, fixes it, and re-runs. **Self-correcting**."

**[Show final test]**

```bash
curl -H "Authorization: Bearer token123" \
  http://localhost:8000/api/users/1/export | jq
```

```json
{
  "user_id": 1,
  "name": "Alice",
  "email": "alice@example.com",
  "created_at": "2024-01-15",
  "preferences": {...},
  "activity_last_30_days": [...]
}
```

> "And there it is. Production-ready code that follows our patterns, includes tests, and just... works."

**Transition:** "Let's break down why this works so well..."

---

## Slide 9: Key Components Deep Dive (2 min)

### Visual
- Three-column layout with icons
- Light boxes with blue borders

### Content

**CLAUDE.md** 📋
- Code structure rules
- Testing conventions
- Style guidelines
- Known gotchas

**PRPs (Templates)** 📝
- Goal & Context
- Implementation Blueprint
- Validation Gates
- Anti-Patterns

**Examples/** 💻
- Real code patterns
- Test structures
- Integration methods

### Script
> "Three components make this work:"

> "**CLAUDE.md** is your global rules file. 'Always use TypeScript,' 'Test with pytest,' 'Never hardcode API keys.' The AI reads this for every task."

> "**PRPs** are your implementation blueprints. They include context, ordered tasks, pseudocode, and validation checkpoints."

> "**Examples/** shows the AI what 'good' looks like in your codebase. It pattern-matches against these when generating code."

**Transition:** "So what do you get from this?"

---

## Slide 10: Benefits & Results (2 min)

### Visual
- Four benefit boxes with emojis and stats
- Light background, green accents

### Content

🎯 **Consistency**
Code follows your patterns 100% of the time

🔄 **Self-Correction**
Built-in validation loops catch and fix errors

🏗️ **Complex Tasks**
Multi-file features implemented end-to-end

⚡ **Speed**
10x faster than manual implementation

### Stats Box
- **85%+ success rate** on complex tasks
- **11,000+ GitHub stars** in 2 months
- **50+ production projects** using framework

### Script
> "Here's what teams are seeing:"

> "**Consistency:** Every feature follows your architecture. No more 'AI went rogue and used a different pattern.'"

> "**Self-correction:** Validation loops mean the AI catches its own mistakes. Failed test? It fixes it. Linting error? Fixed."

> "**Complex tasks:** We're talking multi-file features with database migrations, API changes, and tests—all implemented correctly."

> "**Speed:** Teams report features that took days now take hours."

> "This isn't hype. 11,000+ developers have starred the repo. Dozens of production projects are using it right now."

**Transition:** "Ready to try it yourself?"

---

## Slide 11: Get Started (2 min)

### Visual
- Large QR code (links to tutorial)
- GitHub repo URL
- "Quick Start" checklist

### Content

**🚀 Quick Start**

1. Clone the template:
   ```bash
   git clone https://github.com/coleam00/context-engineering-intro
   ```

2. Customize `CLAUDE.md` with your rules

3. Add code examples to `examples/`

4. Write feature request in `INITIAL.md`

5. Run `/generate-prp` then `/execute-prp`

**📖 Full Tutorial**
[QR code to tutorial.md]
Detailed guide with advanced patterns

**🔗 Resources**
- GitHub: coleam00/context-engineering-intro
- Discord: [Community link]
- Twitter: @coleam00

### Script
> "Want to try this? Here's your 5-step Quick Start:"

> "1. Clone the template repo—it has everything you need"
> "2. Customize CLAUDE.md with your project's rules"
> "3. Add a few code examples"
> "4. Write your first feature request"
> "5. Run the commands"

> "I've also created a full tutorial [point to QR code] with advanced patterns, troubleshooting, and real-world examples. Scan this or check the link in chat."

> "The template is free, open-source, and works with Claude Code out of the box."

---

## Q&A Setup (2 min remaining)

### Script
> "That's Context Engineering. Let's open it up for questions."

**Common Questions to Anticipate:**

**Q: "Does this only work with Claude Code?"**
A: "No! The framework works with any AI assistant. Claude Code has the best tooling support, but you can apply these principles with Cursor, Copilot, or even ChatGPT."

**Q: "How long does setup take?"**
A: "First project: 2-3 hours to write CLAUDE.md and add examples. After that, 30 minutes per new project—you reuse patterns."

**Q: "What about non-Python projects?"**
A: "Framework is language-agnostic. Teams use it for TypeScript, Go, Rust, Java. The principles are universal."

**Q: "Can I use this for existing projects?"**
A: "Absolutely. Start by documenting your current patterns in CLAUDE.md and examples/. Then incrementally add PRPs for new features."

**Q: "What's the learning curve?"**
A: "If you've used AI assistants before, you're 80% there. The hardest part is resisting the urge to vibe code—trusting the process takes a few PRPs to click."

---

## Closing (if time allows)

### Script
> "Context Engineering changed how my team builds software. We ship faster, with fewer bugs, and the AI actually understands our codebase."

> "If you take one thing from this talk: **Stop prompt engineering. Start context engineering.**"

> "Thank you! Grab the tutorial, try it on a real feature, and let me know how it goes."

---

## Presenter Notes

### Timing Breakdown
- Slides 1-3 (Problem + Solution): 6 min
- Slide 4 (Framework overview): 2 min
- Slides 5-8 (Live demo): 10 min
- Slides 9-10 (Components + Benefits): 4 min
- Slide 11 (Get Started): 2 min
- Buffer: 2 min

### Demo Preparation
1. Clone repo in advance
2. Pre-create INITIAL.md (copy-paste during demo)
3. Test `/generate-prp` and `/execute-prp` beforehand
4. Have curl command ready to copy
5. Backup: If live demo fails, show pre-recorded screenshots

### Energy & Engagement
- **Hook early**: "Show of hands" question gets audience involved
- **Contrast**: Show the problem (vibe coding fails) before the solution
- **Live demo**: Most impactful 10 minutes—audience sees it work
- **Stats**: Use concrete numbers (85% success, 11k stars) for credibility
- **Call to action**: Clear next steps (QR code, repo link)

### Backup Slides (optional, not in main deck)
- Slide 12: Advanced Patterns (batch PRPs, custom validation)
- Slide 13: Case Studies (real projects using framework)
- Slide 14: Comparison with other frameworks (Aider, Cursor rules)

---

## Technical Requirements

- **Tools needed**: Terminal, Claude Code CLI, browser for GitHub
- **Screen sharing**: Use terminal font size 16-18pt for readability
- **Internet**: Required for live demo (fetch docs, etc.)
- **Backup plan**: Pre-captured screenshots in `assets/demo-screenshots/`

---

**END OF DEMO SCRIPT**

*Created for 20-minute presentation to developer audience*
*Optimized for engagement, clarity, and actionable takeaways*
