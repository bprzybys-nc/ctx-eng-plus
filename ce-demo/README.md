# Context Engineering Presentation Kit

**Complete presentation materials for introducing Context Engineering to developer audiences**

Based on Cole Medin's Context Engineering framework: https://github.com/coleam00/context-engineering-intro

---

## Contents

### 1. DEMO-SCRIPT.md
**20-minute presentation script** with:
- Slide-by-slide narration
- Timing breakdown (2 min per section)
- Live demo walkthrough (10 min centerpiece)
- Q&A preparation
- Presenter notes and tips

**Target audience:** Developers familiar with AI coding assistants

**Format:** Read alongside slides for smooth delivery

---

### 2. slides/SLIDE-CONTENT.md
**Complete slide deck content** with:
- 11 main slides (+ 3 optional backup slides)
- Detailed visual design specifications
- Code examples and terminal outputs
- Layout instructions for PowerPoint/Google Slides
- Color palette and typography guidelines

**How to use:**
1. Open PowerPoint or Google Slides
2. Set up slide master (16:9, fonts, colors per spec)
3. Create slides following the content structure
4. Import Mermaid chart images (see mermaid-charts/)
5. Add terminal screenshots (see assets/)

---

### 3. mermaid-charts/
**Three Mermaid diagrams** for slides:

- **workflow.mermaid** - Complete CE workflow (INITIAL.md → Feature)
- **components.mermaid** - Framework architecture (CLAUDE.md, PRPs, examples, commands)
- **validation-loop.mermaid** - Self-correction validation cycle

**How to render:**
```bash
# Option 1: Use Mermaid CLI
npm install -g @mermaid-js/mermaid-cli
mmdc -i workflow.mermaid -o workflow.png -w 1200 -H 600 -b white

# Option 2: Use online editor
# Visit https://mermaid.live/
# Paste chart code, export as PNG (1200x600)

# Option 3: Use VS Code extension
# Install "Markdown Preview Mermaid Support"
# Right-click diagram → Export to PNG
```

**Design notes:**
- Light theme optimized for presentation (white/cream backgrounds)
- High contrast text (color:#000) for readability
- Render at 1200x600px minimum for crisp display

---

### 4. TUTORIAL.md
**In-depth tutorial** (~4000 words) covering:

**Sections:**
1. Introduction: Why Context Engineering?
2. Core Philosophy (context > prompts)
3. Quick Start Guide (5 steps to first PRP)
4. CLAUDE.md: Your Project Constitution
5. Writing Effective PRPs (manual vs /generate-prp)
6. The Custom Commands (/generate-prp, /execute-prp)
7. Validation & Testing Patterns (3-level validation)
8. Real-World Examples (3 complete scenarios)
9. Advanced Techniques (batch PRPs, custom validation)
10. Troubleshooting & Common Issues
11. Resources & Community

**Use cases:**
- Link from presentation QR code for deep dive
- Onboarding document for team adoption
- Reference guide during implementation

---

## Usage Instructions

### For Presenters

**1. Preparation (1-2 hours before presentation)**

Clone Context Engineering repo for live demo:
```bash
git clone https://github.com/coleam00/context-engineering-intro demo-repo
cd demo-repo
```

Set up demo environment:
```bash
# Install dependencies if needed
npm install

# Pre-create INITIAL.md for demo (copy from DEMO-SCRIPT.md)
cat > INITIAL.md << 'EOF'
FEATURE: Add API endpoint for user profile export
[... copy from script Section "Demo Part 2" ...]
EOF
```

Test commands:
```bash
# Test /generate-prp (verify it works)
/generate-prp INITIAL.md

# Test /execute-prp (optional, or use pre-captured screenshots)
/execute-prp PRPs/executed/PRP-1-*.md
```

**2. Slide Deck Creation (2-3 hours)**

1. Open PowerPoint/Google Slides
2. Create new 16:9 presentation
3. Set up slide master:
   - Font: Inter or Helvetica
   - Title: 36pt bold
   - Body: 18pt
   - Code: Consolas 14pt
   - Colors: Blue #1976d2, Green #388e3c, Orange #f57c00
4. Follow slides/SLIDE-CONTENT.md structure
5. Import Mermaid chart PNGs (render first, see above)
6. Add terminal screenshots from demo prep
7. Generate QR code linking to TUTORIAL.md (use qr-code-generator.com)

**3. Rehearsal (30-45 min)**

- Run through entire script with timer
- Practice live demo (muscle memory for commands)
- Verify QR code scans correctly
- Test screen sharing setup
- Prepare backup screenshots (in case demo fails)

**4. Delivery Tips**

- **Hook early:** Start with "show of hands" question
- **Demo is key:** 10 minutes showing /generate-prp and /execute-prp
- **Use pauses:** Let code blocks sink in (3-5 seconds)
- **Show enthusiasm:** This framework is genuinely exciting
- **Invite questions:** Throughout, not just at end

---

### For Attendees

**1. Quick Start (After Presentation)**

Scan QR code → Read TUTORIAL.md → Follow "Quick Start Guide" (Section 3)

**Time investment:**
- Read tutorial: 30-40 minutes
- Set up first project: 2-3 hours
- First PRP: 30 minutes
- Ongoing: 10-15 minutes per PRP

**2. Resources**

- **GitHub template:** github.com/coleam00/context-engineering-intro
- **Tutorial:** [Link to hosted TUTORIAL.md or repo]
- **Community:** Discord, Twitter (@coleam00)
- **Examples:** See tutorial Section 8 (Real-World Examples)

---

## Directory Structure

```
ce-demo/
├── README.md                  # This file
├── DEMO-SCRIPT.md            # 20-min presentation script
├── TUTORIAL.md               # In-depth tutorial (~4000 words)
├── slides/
│   └── SLIDE-CONTENT.md      # Slide deck content (11 slides)
├── mermaid-charts/           # Diagrams for slides
│   ├── workflow.mermaid
│   ├── components.mermaid
│   └── validation-loop.mermaid
└── assets/                   # Screenshots, QR codes (add during prep)
    ├── demo-screenshots/     # Terminal outputs from demo
    ├── qr-code-tutorial.png  # QR → TUTORIAL.md
    └── workflow.png          # Rendered Mermaid charts
```

---

## Customization

### Adapt for Different Audiences

**For junior developers:**
- Add more context on AI coding assistants
- Simplify technical examples
- Focus on "why" over "how"
- Extend Q&A time

**For senior developers:**
- Speed up basics, dive into advanced techniques
- Show complex refactoring example
- Discuss integration with CI/CD
- Compare with other frameworks (Cursor Rules, Aider)

**For non-technical stakeholders:**
- Focus on business benefits (speed, consistency)
- Show before/after metrics
- Simplify technical jargon
- Add case studies (Slide 13 backup)

### Adjust Timing

**10-minute version:**
- Slides 1-3 (Problem + Solution): 3 min
- Live demo condensed: 5 min
- Benefits + Get Started: 2 min

**30-minute version:**
- Add backup slides (Advanced Patterns, Case Studies)
- Extend demo (show full PRP execution)
- Add 10 min Q&A at end

**Workshop (2 hours):**
- 20-min presentation
- 30-min hands-on setup (attendees clone repo, customize CLAUDE.md)
- 60-min guided PRP creation (attendees write first PRP)
- 10-min wrap-up and Q&A

---

## Technical Requirements

**For Presenters:**
- Laptop with terminal (macOS/Linux/Windows WSL)
- Claude Code CLI installed
- Screen sharing setup (large font, high contrast)
- Internet connection (for /generate-prp docs fetching)
- Backup: Pre-captured screenshots in assets/

**For Slide Deck:**
- PowerPoint 2016+ or Google Slides
- Mermaid renderer (CLI, online, or VS Code)
- QR code generator (online tools work fine)
- Image editor (optional, for screenshot cropping)

**For Attendees:**
- No requirements during presentation
- Post-talk: Git, text editor, AI assistant (Claude Code recommended)

---

## Troubleshooting

### Issue: Mermaid charts not rendering

**Solution:**
- Use online editor: https://mermaid.live/
- Copy chart code, click "PNG" export
- Download at 1200x600px resolution

### Issue: Live demo /generate-prp fails

**Solution:**
- Use backup screenshots (pre-captured)
- Explain what would happen (narrate from script)
- Show pre-generated PRP instead

### Issue: QR code doesn't scan

**Solution:**
- Increase QR code size (300x300px minimum)
- Use high contrast (black on white)
- Test with multiple phones before presentation
- Backup: Display short URL verbally

### Issue: Slides too text-heavy

**Solution:**
- Use build animations (reveal bullets one by one)
- Split dense slides into 2 slides
- Move details to "Notes" section (for you, not shown)

---

## License & Attribution

**Based on:**
- Context Engineering framework by Cole Medin
- GitHub: https://github.com/coleam00/context-engineering-intro
- License: [Check repo for current license]

**Presentation materials:**
- Created for educational purposes
- Free to use and adapt
- Attribution appreciated (link to original repo)

**Sharing:**
- Feel free to remix for your talks/workshops
- Share TUTORIAL.md with your team
- Contribute improvements back to community

---

## Feedback & Contributions

**Found an issue?**
- Typo in tutorial? Submit a fix
- Better example? Share it
- Presentation tip? Add to README

**Success story?**
- Share on Twitter with #ContextEngineering
- Write a blog post about your experience
- Present at your local meetup (use these materials!)

---

**Questions?**

- GitHub Discussions: https://github.com/coleam00/context-engineering-intro/discussions
- Twitter: @coleam00
- Discord: [Community server]

---

**Good luck with your presentation!**

Remember: Context Engineering is powerful because it's simple. Focus on the core insight—comprehensive context beats clever prompts—and the rest follows naturally.

Now go make some developers' lives better!
