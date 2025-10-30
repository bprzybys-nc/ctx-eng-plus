# Google Slides Import Template

**Context Engineering Presentation**
**Import this structure into Google Slides for instant deck creation**

---

## Import Instructions

### Method 1: Manual Creation (Recommended)
1. Go to slides.google.com
2. Click "Blank" presentation
3. Go to Slide → Edit master
4. Set theme: Background #FFFFFF, Accent #1976D2
5. Exit master view
6. Follow slide-by-slide structure below

### Method 2: Import from Markdown (if using md2gslides)
```bash
npm install -g md2gslides
md2gslides GOOGLE-SLIDES-TEMPLATE.md \
  --title "Context Engineering" \
  --style template-styles.json
```

---

## Master Slide Settings

### Theme
```
Background: #FFFFFF (white)
Accent 1: #1976D2 (blue)
Accent 2: #388E3C (green)
Accent 3: #F57C00 (orange)
Accent 4: #C62828 (red)
```

### Fonts
```
Title: Roboto Bold, 36pt
Subtitle: Roboto Regular, 24pt
Body: Roboto Regular, 18pt
Code: Roboto Mono, 14pt
```

### Slide Size
```
16:9 (Widescreen)
```

---

## Slide 1: Title

**Layout:** Title slide

**Title:**
```
Context Engineering:
Stop Vibe Coding, Start Building
```

**Subtitle:**
```
The systematic approach to making AI assistants actually work

By Cole Medin (@coleam00)
github.com/coleam00/context-engineering-intro
```

**Design:**
- Add emoji 🎯 in top-right corner (72pt)
- Light gradient background (Insert → Image → Gradient: white to #FAFAFA)
- Title: Roboto Bold, 48pt, centered
- Subtitle: Roboto, 20pt, centered, gray (#616161)

---

## Slide 2: The Problem

**Layout:** Title and table

**Title:** Why Most AI Coding Fails

**Content:**
Insert table (3 columns × 4 rows)

| Approach | Description | Success Rate | Example |
|:--------:|:-----------:|:------------:|:--------|
| ❌<br/>**Vibe Coding** | Just ask the AI<br/>"Build me X" | ~20%<br/>(complex tasks) | "Add user authentication" |
| ⚠️<br/>**Prompt Engineering** | Clever wording<br/>Detailed instructions | ~40%<br/>(brittle, breaks) | "Add JWT-based auth using bcrypt, with email validation..." |
| ✅<br/>**Context Engineering** | Systematic context<br/>Rules + Examples + Validation | ~85%<br/>(production-ready) | Full framework with CLAUDE.md, PRPs, examples, validation gates |

**Design:**
- Table: Insert → Table
- Header row: Fill #1976D2, white text
- Emoji column: 48pt size
- Success rate column: Bold, colored (red/orange/green)
- Alternate row colors: #FAFAFA and white
- Border: 1px #E0E0E0

---

## Slide 3: What is Context Engineering?

**Layout:** Title and body

**Title:** Context Engineering

**Content:**

**Definition Box:** (Insert → Shape → Rounded rectangle, fill #E3F2FD)
```
Context Engineering is the discipline of systematically
preparing AI coding assistants for complex tasks by
providing comprehensive, structured information—including
rules, examples, patterns, and validation mechanisms—
rather than relying on clever prompts alone.
```

**Key Insight:** (Insert → Shape → Rounded rectangle, fill #FFF9C4)
```
💡 Most AI failures aren't due to model limitations—
   they're due to insufficient context.
```

**Design:**
- Definition box: Rounded corners, padding 20px, centered
- Font: Roboto, 20pt, centered
- Key insight box: Below definition, emoji 48pt
- Box shadow: Subtle (2px blur)

---

## Slide 4: Framework Overview

**Layout:** Title and image

**Title:** The Context Engineering Workflow

**Content:**
- Insert workflow.png (rendered Mermaid chart)
- Image size: 80% slide width, centered

**Bottom section:** (Text boxes)
```
📋 CLAUDE.md (Rules)  |  📝 PRPs (Plans)  |  💻 examples/ (Patterns)  |  ⚙️ Commands (Automation)
```

**Design:**
- Mermaid chart: Import from assets/workflow.png
- Bottom: 4 text boxes, equal width, light backgrounds
- Emoji: 36pt above each label

---

## Slide 5: Demo Part 1 - Project Structure

**Layout:** Two columns

**Title:** Live Demo: Project Structure

**Left Column (60%):**
```
project/
├── .ce/                    # Framework boilerplate
│   ├── RULES.md
│   └── examples/
├── CLAUDE.md              # ← Project rules
├── PRPs/
│   ├── templates/
│   │   └── prp_base.md
│   └── executed/          # ← Implementation plans
├── examples/              # ← Code patterns
│   ├── api/
│   └── tests/
└── INITIAL.md            # ← Feature request
```

**Right Column (40%):**
```
🎯 Key Files

CLAUDE.md
Your project's rules and conventions

PRPs/
Implementation blueprints with validation

examples/
Real code for AI to pattern-match

INITIAL.md
Where you describe features
```

**Design:**
- Left: Insert → Text box, monospace font (Roboto Mono, 14pt)
- Right: 4 cards (Insert → Shape → Rounded rectangle)
- Cards: Light blue fill (#E3F2FD), emoji 36pt
- Tree syntax highlighting: Folders #1976D2, files #616161

---

## Slide 6: Demo Part 2 - Feature Request

**Layout:** Title and two sections

**Title:** Writing a Feature Request (INITIAL.md)

**Code Block (60% height):**
Insert → Text box, fill #FAFAFA, monospace font
```markdown
FEATURE: Add API endpoint for user profile export

User should be able to GET /api/users/{id}/export
and receive their complete profile as JSON.

EXAMPLES:
See examples/api/user_endpoints.py for REST patterns
See examples/serializers/user_serializer.py for JSON

DOCUMENTATION:
- FastAPI docs: https://fastapi.tiangolo.com
- Our API auth: docs/authentication.md

OTHER CONSIDERATIONS:
- Respect privacy settings (hide private fields)
- Rate limit: 10 req/hour per user
- Requires authentication token
```

**Bottom Section (40% height):**
Insert → Shape → Rounded rectangle, fill #C8E6C9
```
✅ What Makes This Good

• Clear feature description
• Points to your codebase examples
• Links external docs
• Highlights gotchas (rate limits, privacy)
```

**Design:**
- Code block: Rounded corners, padding 15px
- Bottom: Green accent, large checkmark emoji (48pt)
- Bullets: 18pt, bold

---

## Slide 7: Demo Part 3 - Generate PRP

**Layout:** Title and three sections

**Title:** /generate-prp in Action

**Command (top, 10% height):**
```bash
/generate-prp INITIAL.md
```

**Progress Output (30% height):**
```
✓ Reading INITIAL.md
✓ Analyzing codebase patterns from examples/
✓ Fetching FastAPI documentation
✓ Checking existing API endpoints
✓ Generating validation checklist
✓ Writing PRP to PRPs/executed/PRP-1-user-export.md
```

**PRP Preview (60% height):**
Insert → Text box, fill #E3F2FD
```markdown
# PRP-1: User Profile Export Endpoint

## Goal
Create GET /api/users/{id}/export endpoint
returning complete user profile as JSON.

## Implementation Blueprint

1. Create endpoint handler in api/users.py
2. Add ExportProfileSerializer in serializers/
3. Implement privacy filtering logic
4. Add rate limiting decorator
5. Write unit tests (3 test cases)
6. Integration test with curl

## Validation Gates
- ✓ Lint with Ruff (no errors)
- ✓ Type check with MyPy
- ✓ Unit tests pass (pytest)
- ✓ Manual curl test succeeds
```

**Design:**
- Command: Dark background (#263238), white monospace text
- Progress: Green checkmarks (✓ = #388E3C)
- PRP preview: Light blue box, numbered list visible

---

## Slide 8: Demo Part 4 - Execute PRP

**Layout:** Title and three sections

**Title:** /execute-prp - Build with Validation

**Command (top):**
```bash
/execute-prp PRPs/executed/PRP-1-user-export.md
```

**Execution Log (middle, 50% height):**
```
✓ Task 1: Create endpoint handler
  ✓ Lint check passed
  ✓ Type check passed

✓ Task 2: Add serializer
  ✓ Lint check passed
  ✓ Type check passed

✓ Task 3: Implement privacy filtering
  ✓ Unit tests pass (3/3)

✓ Task 4: Add rate limiting
  ✓ Integration test passed

✅ PRP-1 completed successfully
```

**Bottom Section (two boxes):**

**Left (50%):**
Badge - Insert → Shape → Rounded rectangle, fill #C8E6C9
```
🎉 Production Ready

✓ All tests passing
✓ Linting clean
✓ Pattern-matched
```

**Right (50%):**
Test result - Insert → Text box, fill #263238 (dark), white text
```bash
$ curl -H "Authorization: Bearer token" \
  http://localhost:8000/api/users/1/export

{
  "user_id": 1,
  "name": "Alice",
  "created_at": "2024-01-15",
  "activity_last_30_days": [...]
}
```

**Design:**
- Execution log: Green checkmarks, indented
- Badge: Large green box, emoji 48pt
- Test result: Terminal style (dark bg, monospace, white text)

---

## Slide 9: Key Components Deep Dive

**Layout:** Three columns

**Title:** What Makes This Work

**Column 1 (33%):**
Insert → Shape → Rounded rectangle, fill #E1F5FE
```
📋 CLAUDE.md
Project Rules

✓ Code structure
✓ Testing conventions
✓ Style guidelines
✓ Known gotchas

Example:
"Always use TypeScript strict mode"
"Test with pytest, 80% coverage"
"Never hardcode API keys"
```

**Column 2 (33%):**
Insert → Shape → Rounded rectangle, fill #F3E5F5
```
📝 PRPs
Implementation Blueprints

✓ Goal & Context
✓ Ordered tasks
✓ Pseudocode
✓ Validation gates
✓ Anti-patterns

Example sections:
- All Needed Context
- Implementation Blueprint
- Validation Checklist
```

**Column 3 (33%):**
Insert → Shape → Rounded rectangle, fill #E8F5E9
```
💻 examples/
Code Patterns

✓ Real implementations
✓ Test structures
✓ Integration methods
✓ Best practices

AI learns by example:
"This is how we do REST APIs"
"This is our test pattern"
```

**Design:**
- Three equal-width cards
- Emoji at top (48pt)
- Checkmarks for bullets
- Example text in smaller font, gray

---

## Slide 10: Benefits & Results

**Layout:** Title and 2×2 grid + stats

**Title:** Why Teams Are Switching

**Grid (4 quadrants):**

**Top-left:**
```
🎯 Consistency

Code follows your
patterns 100% of
the time

No more "AI went
rogue"
```

**Top-right:**
```
🔄 Self-Correction

Built-in
validation loops
catch errors

Failed test? AI
fixes and re-runs
```

**Bottom-left:**
```
🏗️ Complex Tasks

Multi-file
features
implemented
end-to-end
```

**Bottom-right:**
```
⚡ Speed

10x faster than
manual coding

Features that took
days → now hours
```

**Stats Box (bottom, full width):**
Insert → Shape → Rounded rectangle, gradient fill (#1976D2 → #0D47A1)
```
📊 Real Results

• 85%+ success rate on complex tasks
• 11,000+ GitHub stars in 2 months
• 50+ production projects using framework
• 10x speed improvement (average)
```

**Design:**
- Four equal quadrants, light backgrounds
- Large emojis (48pt) at top
- Stats box: Blue gradient, white text, bold numbers

---

## Slide 11: Get Started

**Layout:** Two columns

**Title:** Try It Yourself

**Left Column (40%):**

Insert → Image → QR code (300×300px)
```
📖 Full Tutorial
Scan for in-depth guide

github.com/coleam00/
context-engineering-intro
```

**Right Column (60%):**

```
🚀 Quick Start (5 Steps)

1. Clone the template
   git clone https://github.com/coleam00/
   context-engineering-intro

2. Customize CLAUDE.md
   Add your project rules

3. Add code examples
   examples/ folder

4. Write feature request
   INITIAL.md

5. Run the commands
   /generate-prp
   /execute-prp

🔗 Resources

• Discord: [Community link]
• Twitter: @coleam00
• YouTube: Tutorials & walkthroughs
```

**Design:**
- QR code: Large, centered in left column
- Right: Numbered list, monospace for commands
- Resources: Icon bullets, blue links
- Call-to-action style for GitHub link

---

## Bonus Slide: Advanced Patterns

**Layout:** Title and four cards

**Title:** Advanced Patterns (Bonus)

**Four cards (2×2):**

```
1. Batch PRP Generation
Create multiple PRPs from
feature plans in parallel

2. Custom Validation Rules
Add security scans, performance
benchmarks, a11y checks

3. PRP Templates
Specialized templates for
API endpoints, migrations, refactors

4. Context Versioning
Switch contexts for different
project versions (MVP, production, enterprise)
```

**Design:**
- Four cards, light backgrounds
- Numbered, concise descriptions
- Use for extended presentation time

---

## Bonus Slide: Case Studies

**Layout:** Title and three examples

**Title:** Real-World Success Stories

**Three cards:**

```
Company A - Fintech
Reduced feature dev time from
5 days → 8 hours (6x faster)

85% test coverage maintained
Zero production bugs in Q1

Company B - E-commerce
Onboarded junior dev using CE
Output quality matched senior devs

Consistency across 200+ API endpoints

Company C - SaaS
Refactored legacy codebase
50,000 LOC in 2 weeks

All tests passing, zero regressions
```

**Design:**
- Three vertical cards
- Company name bold
- Metrics highlighted (percentages, time)
- Use for longer presentations or if asked

---

## Animations (Optional)

**Slide 2 (Problem table):**
- Fade in row by row (0.5s delay each)

**Slide 4 (Workflow):**
- Wipe from left (1s duration)

**Slide 7 (Progress output):**
- Appear line by line (0.3s delay each)

**Slide 8 (Execution log):**
- Fade in per task (0.5s delay)

**Slide 10 (Grid):**
- Zoom in quadrants (0.3s delay each)

**All other slides:**
- No animations (instant for faster pacing)

---

## Export Settings

### For Presentation:
```
File → Download → PDF Document (.pdf)
- Include speaker notes: No
- Include slide transitions: Yes
```

### For Sharing:
```
File → Download → Microsoft PowerPoint (.pptx)
- Preserves fonts and formatting
```

### For Web:
```
File → Publish to web
- Auto-advance slides: No
- Restart after last slide: No
```

---

## Speaker Notes (Add to each slide)

**How to add:**
1. Click slide in editor
2. View → Show speaker notes
3. Copy corresponding section from DEMO-SCRIPT.md

**Benefits:**
- Script visible only to you during presentation
- Timing reminders
- Key talking points

---

## Tips for Best Results

1. **Use high-quality images:**
   - Render Mermaid charts at 1200×600px minimum
   - Export terminal screenshots at 2x resolution
   - Generate QR code at 300×300px minimum

2. **Test on projector:**
   - Colors may look different on projector
   - Increase font sizes if text too small
   - Check contrast (light room vs dark room)

3. **Backup plan:**
   - Export to PDF before presentation
   - Have offline copy (internet might fail)
   - Screenshot all demo outputs

4. **Accessibility:**
   - High contrast text/backgrounds
   - Large fonts (18pt minimum for body)
   - Avoid red/green for colorblind audience

---

## Template Files Needed

**Before creating slides, prepare:**

1. **workflow.png** - Render from mermaid-charts/workflow.mermaid
2. **components.png** - Render from mermaid-charts/components.mermaid
3. **validation-loop.png** - Render from mermaid-charts/validation-loop.mermaid (optional, for bonus slides)
4. **qr-code-tutorial.png** - Generate from https://qr-code-generator.com, link to TUTORIAL.md
5. **demo-screenshots/** - Capture during demo preparation

**Rendering Mermaid charts:**
```bash
# Option 1: Use mermaid.live
Visit https://mermaid.live/
Paste chart code
Export PNG (1200×600)

# Option 2: Use CLI
npm install -g @mermaid-js/mermaid-cli
cd mermaid-charts
mmdc -i workflow.mermaid -o ../assets/workflow.png -w 1200 -H 600 -b white
```

---

**END OF GOOGLE SLIDES TEMPLATE**

*Import this structure into Google Slides for instant presentation deck*
*Estimated creation time: 1-2 hours*
*Difficulty: Medium (requires basic Slides knowledge)*
