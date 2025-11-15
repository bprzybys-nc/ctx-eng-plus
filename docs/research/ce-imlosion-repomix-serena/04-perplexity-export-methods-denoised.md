---
type: research
source: perplexity-ai
category: workflow-integration
tags: [export-methods, perplexity, obsidian, linear]
created: "2025-11-15"
indexed: "2025-11-15"
denoise_status: completed
---

# Perplexity Export & Integration Methods

## Export Options

**Individual Thread Export**

- Built-in: PDF, Markdown, DOCX formats
- Manual per thread

**Bulk Export Extensions**

Perplexity to Obsidian — Batch Export (Chrome/Edge/Brave)

- One-click bulk export as Markdown
- Privacy-first, local processing
- Obsidian/Notion/backup compatible

Alternative: Save my Chatbot (Chrome/Firefox)

- Single-thread → Markdown
- Obsidian.md workflow
- One thread at a time

Perplexity to Notion - Batch Export

- Batch all conversations → Notion or Markdown
- One-click download

---

## Recommended macOS Workflow

```
Perplexity Space
    ↓ (batch export extension)
Markdown files → Obsidian vault
    ↓ (Linear Integration plugin)
Linear issues (tasks/bugs)
    ↓ (OGD Sync plugin)
Google Drive (backup/archive)
```

**With Automation**:

```
Perplexity → Obsidian → n8n → {Linear, Google Drive}
                             ↓ (AI classification)
```

---

## Markdown Export Advantages

Preserves:

- Conversation structure (queries → responses)
- Code blocks with syntax highlighting
- Citations and source references
- Tool usage context
- Dense information hierarchy

---

## Integration Pipeline

**Obsidian → Linear**

Linear Integration Plugin (native)

- Bidirectional sync: notes ↔ Linear issues
- Inline syntax: `@assignee/name`, `@status/done`, `@label/bug`, `@priority/1`
- Auto-creates issues from Markdown frontmatter
- Smart conflict resolution

Setup:

1. Install Linear Integration plugin
2. Add API key (`lin_api_...`)
3. Tag notes: `@team/`, `@status/`, etc.
4. Run "Create Linear Issue" command

**Obsidian → Google Drive**

OGD Sync Plugin (macOS/iOS optimized)

- Direct vault sync to Google Drive
- macOS, iOS, Windows compatible
- Push/pull commands
- Auto-pulls before pushing

**Automation Layer**

n8n Self-Hosted (recommended over Zapier)

- Free/cheap ($8/month Digital Ocean)
- Unlimited workflows vs Zapier pricing
- Template: "Workflow Results to Markdown" → Obsidian → Google Drive

Workflow:

1. n8n watches Drive for new Perplexity markdown
2. AI agent analyzes content, extracts metadata
3. Routes to Linear (tasks) or Archives (reference)

---

## Scrum in Obsidian

**Core Plugins**

Kanban Plugin

- Drag-drop cards across columns: Backlog → To Do → In Progress → Done
- Markdown-based, auto-sync
- WIP limits, tags (sprint, points, priority)

Projects Plugin

- Multi-view: Kanban, Table, Calendar, Gallery
- Frontmatter metadata: status, assignee, priority, sprint
- Task filtering and dependencies

Tasks Plugin

- Advanced filtering: due date, priority, tags, path
- Auto-completion timestamps
- Recurring tasks for ceremonies
- Global aggregation: `not done AND tags include #sprint-current`

**Setup**

User Story Template (templates/user-story.md):

```markdown
---
type: user-story
status: backlog
sprint:
priority:
story-points:
assignee:
epic: [[]]
---

# User Story: {{title}}

**As a** [role]
**I want** [feature]
**So that** [benefit]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Tasks
- [ ] Subtask 1 #task
- [ ] Subtask 2 #task
```

Sprint Board (Kanban):

- Column 1: Backlog (tag: #backlog)
- Column 2: Sprint Backlog (tag: #sprint-N)
- Column 3: In Progress (WIP: 3)
- Column 4: Review
- Column 5: Done

Sprint Note (sprints/sprint-05.md):

```markdown
---
sprint: 5
start: 2025-11-11
end: 2025-11-25
goal: "Implement user authentication flow"
---

# Sprint 5

## Sprint Goal
[Goal statement]

## Sprint Backlog
![[kanban-sprint-05]]

## Daily Standups
- [[2025-11-11]] - Standup notes
- [[2025-11-12]] - Standup notes

## Retrospective
### What went well
### What needs improvement
### Action items
```

Product Backlog Query (Dataview):

```markdown
\```
TABLE status, priority, story-points, assignee
FROM "user-stories"
WHERE type = "user-story"
SORT priority ASC, story-points DESC
\```
```

**Story Points & Velocity**

Add to frontmatter: `story-points:: 5`

Velocity calculation (Dataview):

```markdown
\```
TABLE SUM(rows.story-points) AS "Total Points"
FROM "user-stories"
WHERE sprint = 5 AND status = "done"
\```
```

**Recommended Plugin Stack**

1. Kanban - Visual boards
2. Tasks - Query/filter
3. Dataview - Aggregation
4. Templater - Auto-create templates
5. Projects - Structured views
6. CardBoard - Enhanced Kanban

**Daily Workflow**

1. Morning: Open daily note, review tasks query
2. Work: Move cards on Kanban board
3. Complete: Check off in-note or board (auto-syncs)
4. EOD: Update sprint note, log blockers

**Limitations vs Linear/Jira**

Handles well:

- Solo/small team projects
- Flexible structure
- Knowledge + task tracking in one place

Requires workarounds:

- No native time tracking (use Toggl integration)
- Manual sprint planning (no auto-rollover)
- Limited real-time collaboration (Obsidian Sync)

---

## Processing Instructions

**Source**: Perplexity Space exports (Markdown bulk download)

**Content**: Explorations, user requests, codebase samples, AI responses

**Structure**: Thread-based conversations with citations, code, reasoning chains

**Purpose**: Create training corpus for [model/RAG/fine-tuning]

**Process**:

1. Export Spaces via batch extension
2. Validate Markdown structure
3. Extract patterns/templates
4. Feed to Claude for preprocessing

**Output**: Context-engineered prompts + code artifacts

**Validation**: Information density, citation integrity, code executability
