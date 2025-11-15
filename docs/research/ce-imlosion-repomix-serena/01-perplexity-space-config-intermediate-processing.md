---
type: research
source: perplexity-ai
category: ce-graph-framework
tags: [perplexity-space, configuration, preprocessing, intermediate-files]
created: "2025-11-15"
indexed: "2025-11-15"
denoise_status: completed
kb_integration: pending
---

# Perplexity Space Configuration for Context Preprocessing

## Constraints

- **Instructions:** 1,500 characters max
- **Files:** 50 max (Pro tier), 25 MB per file
- **Context window:** 128k-200k tokens
- **Primary source:** GitHub repo link (unlimited files, real-time)

## Architecture

```
perplexity-space-context/
├── meta/
│   ├── goals.md
│   └── requirements.md
├── patterns/
│   └── validation.md
└── work/
    └── (active tasks)
```

## Space Setup (15 minutes)

### 1. Create Repository

```bash
gh repo create perplexity-space-context --public
cd perplexity-space-context
mkdir meta patterns work
echo "# Goals" > meta/goals.md
git add . && git commit -m "init" && git push
```

### 2. Configure Space in Perplexity UI

- **Sources → Links:** Add `github.com/bprzybysz/perplexity-space-context`
- **Sources → Files:** Upload 2-3 critical files (goals, requirements, validation rules)
- **Answer instructions** (400 characters):

```
Context preprocessing agent.

SOURCE: GitHub perplexity-space-context repo

PRINCIPLES: KISS, SOLID, YAGNI

PROCESS:
• Review meta/ for goals/requirements
• Apply patterns/validation rules
• Check work/ for active tasks
• Generate actionable next steps

OUTPUT: Markdown with headers, code blocks, citations

VALIDATE: Solution in ≤3 sentences, requirements mapped, testable
```

## Iteration Workflow

**3-step cycle:**

1. **Query Space:** "Review work/ directory and suggest preprocessing improvements"
2. **Update GitHub:** Commit validated changes manually
3. **Repeat:** Space reads updated repo automatically

## Validation Checklist

Each iteration must pass:

- ✓ Solution explained in ≤3 sentences (KISS)
- ✓ Single responsibility per component (SOLID)
- ✓ All components map to requirements (YAGNI)

## GitHub Integration Options

### Option 1: GitHub Repo Link (Recommended - Free)

- Read-only access via repo link
- No file upload limits
- Real-time updates
- Works with all Perplexity tiers

**Capabilities:**

- Query: "Analyze files in perplexity-space-context repo and suggest next steps"
- Space indexes all markdown files automatically
- Natural language queries about repo content

**Limitations:**

- Cannot create issues, push files, or automate workflows
- Manual file management required

### Option 2: Enterprise GitHub Connector

- **Requirements:** Enterprise Pro or Enterprise Max subscription
- Native GitHub integration in Perplexity
- Query repositories without context switching
- Not available for individual Pro accounts

### Option 3: GitHub MCP Server (Desktop/CLI Only)

- **Note:** Cannot integrate directly with Perplexity Spaces
- Designed for Claude Desktop, Cursor, and similar MCP clients
- Separate from Perplexity's MCP capabilities

## Implementation Timeline

### Phase 1: MVP Setup (30 min)

- Create repo with 3 directories
- Add GitHub link to Space
- Upload 2-3 core files
- Set 400-char instructions
- Test basic workflow

### Phase 2: First Iteration (10 min)

- Create `work/task-001.md` with test task
- Query Space for preprocessing plan
- Verify response quality

### Phase 3: Refine (10 min)

- Update based on Space output
- Commit to GitHub
- Run validation checklist

## Success Metrics

| Metric | Target |
|--------|--------|
| Setup time | <30 min |
| Iteration cycle | <15 min |
| Space response | <10 sec |
| Files uploaded | 2-3 max |

## Key Refinements

1. Eliminated unnecessary complexity (5-level structure → 3 directories)
2. GitHub Actions removed (manual validation faster for small projects)
3. Removed automated snapshots and validation scripts
4. Simplified from 50-file allocation strategy to just uploading essentials
5. Practical 30-minute implementation path with exact commands

This follows KISS/SOLID/YAGNI principles: eliminates speculative features, focuses on core requirement (preprocessing context via Perplexity Space with GitHub as source).
