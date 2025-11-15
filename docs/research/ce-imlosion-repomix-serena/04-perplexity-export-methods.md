---
type: research
source: perplexity-ai
category: ce-graph-framework
tags: [export-methods, bulk-export, browser-extensions, markdown]
created: "2025-11-15"
indexed: "2025-11-15"
denoise_status: completed
kb_integration: pending
---

<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

## Export Methods

### Individual Thread Export

Perplexity provides built-in export for single threads via the Export button, offering **PDF, Markdown, or DOCX** formats. This works for individual conversations but requires manual export per thread.[^1_1]

### Browser Extensions for Bulk Export

**Perplexity to Obsidian — Batch Export** (Chrome/Edge/Brave compatible)

- One-click bulk export of all conversations as Markdown[^1_2]
- Privacy-first, processes locally[^1_2]
- Designed for Obsidian, Notion, or offline backup[^1_2]

**Alternative: Save my Chatbot** (Chrome/Firefox)

- Single-thread export to formatted Markdown[^1_3]
- Compatible with Obsidian.md workflow[^1_3]
- Limited to one thread at a time[^1_3]

**Perplexity to Notion - Batch Export**

- Batch export all conversations to Notion or Markdown files[^1_4]
- One-click bulk download[^1_4]


### Workflow for Claude Projects

1. **Export**: Use batch extension to download all Space/thread content as Markdown[^1_4][^1_2]
2. **Structure**: Organize exports by topic/project folder on macOS
3. **Import**: Upload Markdown files to Claude Code project
4. **Context**: Claude can process structured Markdown with preserved formatting, citations, code blocks

### Why Markdown Export Works

Markdown preserves:

- Conversation structure (queries → responses)
- Code blocks with syntax
- Citations and source references[^1_3]
- Tool usage context
- Dense information hierarchy


## Refined Instructions Template

```markdown
SOURCE: Perplexity Space exports (Markdown bulk download)

CONTENT: Explorations, user requests, codebase samples, AI responses

STRUCTURE: Thread-based conversations with citations, code, reasoning chains

PURPOSE: Create training corpus for [model/RAG/fine-tuning]

PROCESS: 
1. Export Spaces via batch extension
2. Validate Markdown structure
3. Extract patterns/templates
4. Feed to Claude for preprocessing

OUTPUT: Context-engineered prompts + code artifacts

VALIDATE: Information density, citation integrity, code executability
```

<span style="display:none">[^1_10][^1_11][^1_12][^1_13][^1_14][^1_15][^1_16][^1_17][^1_18][^1_19][^1_20][^1_5][^1_6][^1_7][^1_8][^1_9]</span>

<div align="center">⁂</div>

[^1_1]: https://www.perplexity.ai/help-center/en/articles/10354769-what-is-a-thread

[^1_2]: https://chrome-stats.com/d/afmlkbanimddphcomahlfbaandfphjfk?hl=en

[^1_3]: https://www.reddit.com/r/perplexity_ai/comments/16n2g3d/i_made_an_extension_to_export_perplexity_threads/

[^1_4]: https://chromewebstore.google.com/detail/perplexity-to-notion/gfmjaemghnjokjhafjiiijhllkkfcjpk?hl=de

[^1_5]: https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research

[^1_6]: https://www.perplexity.ai/help-center/en/

[^1_7]: https://www.perplexity.ai/hub/getting-started

[^1_8]: https://www.perplexity.ai/changelog/what-we-shipped-april-25th

[^1_9]: https://www.perplexity.ai/help-center/en/articles/10354810-security-and-privacy-with-file-uploads

[^1_10]: https://www.perplexity.ai/help-center/en/articles/10354775-technical-capabilities-of-threads

[^1_11]: https://www.perplexity.ai/help-center/en/articles/11132456-how-to-use-the-perplexity-voice-assistant-for-ios

[^1_12]: https://www.perplexity.ai/help-center/en/articles/12067853-introduction-to-organization-admins

[^1_13]: https://www.perplexity.ai/help-center/en/articles/10968016-memory

[^1_14]: https://www.reddit.com/r/perplexity_ai/comments/1h9h3ji/anyone_else_want_a_full_backupexport_feature_for/

[^1_15]: https://docs.perplexity.ai/getting-started/quickstart

[^1_16]: https://www.storylane.io/tutorials/how-to-export-perplexity-data

[^1_17]: https://crawlbase.com/blog/how-to-use-perplexity-ai-for-web-scraping/

[^1_18]: https://www.youtube.com/watch?v=LnURCxwsB34

[^1_19]: https://www.perplexity.ai/help-center/en/articles/11844346-enterprise-usage-analytics

[^1_20]: https://docs.spring.io/spring-ai/reference/api/chat/perplexity-chat.html


---

## Workflow Pipeline

### Perplexity → Obsidian (Fitting Proxy)

**Chrome Extension: Perplexity to Obsidian — Batch Export**

- One-click bulk export all Spaces/threads as Markdown[^2_1]
- Auto-saves to configured Obsidian vault folder[^2_1]
- Preserves structure: citations, code blocks, formatting[^2_2]

**Obsidian Plugins for Perplexity Integration**

- **Perplexed Plugin**: Native Perplexity API integration, generates cited content in-vault[^2_3]
- **Perpsidian**: Run Perplexity queries directly in Obsidian (requires Python setup)[^2_4]


### Obsidian → Linear

**Linear Integration Plugin** (native Obsidian plugin)

- Bidirectional sync between notes and Linear issues[^2_5]
- Inline syntax: `@assignee/name`, `@status/done`, `@label/bug`, `@priority/1`[^2_5]
- Auto-creates Linear issues from markdown with frontmatter[^2_5]
- Smart conflict resolution and autocomplete[^2_5]

**Setup**:

1. Install Linear Integration plugin in Obsidian[^2_5]
2. Add Linear API key (`lin_api_...`) in settings[^2_5]
3. Tag notes with `@team/`, `@status/`, etc.[^2_5]
4. Run "Create Linear Issue" command[^2_5]

### Obsidian → Google Drive

**OGD Sync Plugin** (macOS/iOS optimized)

- Direct Obsidian vault sync to Google Drive[^2_6]
- Works across macOS, iOS, Windows[^2_6]
- Push/pull commands via button or palette[^2_6]
- Auto-pulls before pushing to prevent conflicts[^2_6]


### Automation Layer (Optional)

**n8n Self-Hosted** (recommended over Zapier)

- Free/cheap (\$8/month Digital Ocean)[^2_7]
- Unlimited workflows vs Zapier's pricing[^2_7]
- Template: "Workflow Results to Markdown Notes" → Obsidian via Google Drive[^2_8]
- Use case: Auto-process Perplexity exports → tag → route to Linear/Drive[^2_8]

**Workflow**:

1. n8n watches Drive folder for new Perplexity markdown[^2_8]
2. AI agent analyzes content, extracts metadata[^2_9]
3. Routes to Linear (tasks) or Archives (reference)[^2_8]

## Recommended macOS Flow

```
Perplexity Space
    ↓ (batch export extension)
Markdown files → Obsidian vault
    ↓ (Linear Integration plugin)
Linear issues (tasks/bugs)
    ↓ (OGD Sync plugin)
Google Drive (backup/archive)
```

**Alternative with automation**:

```
Perplexity → Obsidian → n8n → {Linear, Google Drive}
                              ↓ (conditional routing)
                         AI classification
```


### Key Advantages

- **No Comet needed**: Browser extensions handle export[^2_1]
- **Native macOS**: All plugins work on Mac[^2_6][^2_5]
- **Obsidian as middleware**: Single source of truth, flexible routing[^2_5]
- **Cost-effective**: Free plugins + optional \$8/mo n8n[^2_7]
<span style="display:none">[^2_10][^2_11][^2_12][^2_13][^2_14][^2_15][^2_16][^2_17][^2_18][^2_19][^2_20][^2_21][^2_22]</span>

<div align="center">⁂</div>

[^2_1]: https://chrome-stats.com/d/afmlkbanimddphcomahlfbaandfphjfk?hl=en

[^2_2]: https://www.reddit.com/r/perplexity_ai/comments/16n2g3d/i_made_an_extension_to_export_perplexity_threads/

[^2_3]: https://github.com/lossless-group/perplexed-plugin

[^2_4]: https://github.com/v4ndn/Perpsidian

[^2_5]: https://github.com/casals/obsidian-linear-integration-plugin

[^2_6]: https://ogd.richardxiong.com

[^2_7]: https://www.reddit.com/r/ObsidianMD/comments/1gllf68/i_created_an_n8n_automation_that_takes_a_yt_video/

[^2_8]: https://n8n.io/workflows/2794-workflow-results-to-markdown-notes-in-your-obsidian-vault-via-google-drive/

[^2_9]: https://forum.obsidian.md/t/i-made-a-local-agentic-ai-that-sorts-my-fleeting-notes-using-n8n-and-context-engineering-overnight/102675

[^2_10]: https://forum.obsidian.md/t/perplexity-ai-plugin/70209

[^2_11]: https://docs.perplexity.ai/cookbook/showcase/daily-news-briefing

[^2_12]: https://www.xda-developers.com/pairing-obsidian-with-perplexity/

[^2_13]: https://www.reddit.com/r/ObsidianMD/comments/1f0pe9j/obsidian_needs_a_perplexityai_plugin/

[^2_14]: https://www.obsidianstats.com/plugins/linear

[^2_15]: https://www.reddit.com/r/ObsidianMD/comments/18zugld/obsidian_google_drive_sync_beta_a_simpler/

[^2_16]: https://forum.obsidian.md/t/integrating-zapier-to-automate-tasks-across-obsidian-and-all-other-common-workflow-apps/17641

[^2_17]: https://n8n.io/workflows/2615-get-airtable-data-via-ai-and-obsidian-notes/

[^2_18]: https://github.com/Tr3ffel/linear-md

[^2_19]: https://www.xda-developers.com/automation-platform-is-zapier-and-n8n-on-steroids/

[^2_20]: https://linear.app/docs/import-issues

[^2_21]: https://n8n.io/integrations/agent/

[^2_22]: https://www.linkedin.com/posts/linearapp_every-linear-docs-page-can-now-be-copied-activity-7350524590575501314-Tp7p


---

## Full Scrum Project Management in Obsidian

### Core Plugins for Agile/Scrum

**Kanban Plugin** (most popular)

- Drag-and-drop cards across columns (Backlog → To Do → In Progress → Done)[^3_1]
- Markdown-based: each card = task with metadata[^3_1]
- WIP limits per column[^3_1]
- Tags for sprint assignment, story points, priority[^3_1]
- Auto-sync between board and markdown files[^3_1]

**Projects Plugin** (structured PM)

- Multi-view support: Kanban, Table, Calendar, Gallery[^3_2]
- Frontmatter-based metadata (status, assignee, priority, sprint)[^3_3]
- Query tasks across vault with filters[^3_2]
- Task dependencies and sequencing[^3_2]

**Tasks Plugin** (query engine)

- Advanced task filtering by due date, priority, tags, path[^3_4]
- Auto-completion timestamps[^3_5]
- Recurring tasks for sprint ceremonies[^3_4]
- Global task aggregation: `not done AND tags include #sprint-current`[^3_5]


### Scrum Workflow Setup

**User Story Template** (`templates/user-story.md`)

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

## Notes
```

**Sprint Board Setup** (Kanban plugin)

- Column 1: **Backlog** (all user stories tagged `#backlog`)
- Column 2: **Sprint Backlog** (stories moved during planning, tagged `#sprint-N`)
- Column 3: **In Progress** (WIP limit: 3)
- Column 4: **Review** (awaiting acceptance)
- Column 5: **Done** (completed in sprint)

**Task Aggregation Query** (in daily note)

```markdown
## Today's Sprint Tasks
\```
not done
(tags include #sprint-current) OR (tags include #today)
group by priority
sort by due
\```
```


### Sprint Management Structure

**Sprint Note** (`sprints/sprint-05.md`)

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

**Product Backlog** (Projects plugin or Dataview)

```markdown
\```
TABLE status, priority, story-points, assignee
FROM "user-stories"
WHERE type = "user-story"
SORT priority ASC, story-points DESC
\```
```


### Recommended Plugin Stack

1. **Kanban** - Visual board management[^3_1]
2. **Tasks** - Query and filter tasks[^3_4]
3. **Dataview** - Aggregate user stories, generate reports[^3_5]
4. **Templater** - Auto-create user story/sprint templates[^3_4]
5. **Projects** - Alternative to Kanban for structured views[^3_2]
6. **CardBoard** - Enhanced Kanban with subtask visualization[^3_1]

### Agile-Specific Features

**Story Points \& Velocity Tracking**

- Add `story-points:: 5` in frontmatter[^3_6]
- Calculate velocity via Dataview query:

```markdown
\```
TABLE SUM(rows.story-points) AS "Total Points"
FROM "user-stories"
WHERE sprint = 5 AND status = "done"
\```
```

**Burndown Chart** (manual or via Charts plugin)

- Track completed story points daily[^3_7]
- Update in sprint note or dashboard[^3_8]

**Epic Management**

- Create epic notes: `epics/authentication-epic.md`[^3_7]
- Link user stories: `epic:: [[authentication-epic]]`[^3_7]
- Query all stories in epic via backlinks[^3_7]


### Daily Workflow

1. **Morning Standup**: Open daily note, review tasks query[^3_5]
2. **Work Session**: Move cards on Kanban board[^3_8]
3. **Task Completion**: Check off in-note or on board (auto-syncs)[^3_1]
4. **EOD**: Update sprint note, log blockers[^3_6]

### Limitations vs. Linear/Jira

**What Obsidian handles well**:

- Solo/small team projects[^3_6]
- Flexible structure (customize everything)[^3_7]
- Knowledge management + task tracking in one place[^3_8]

**What requires workarounds**:

- No native time tracking (use Toggl integration)[^3_7]
- Manual sprint planning (no auto-rollover)[^3_6]
- Limited real-time collaboration (use Obsidian Sync)[^3_7]


### Combined with Your Pipeline

```
Perplexity research → Obsidian user story → Kanban sprint board → Linear (optional sync via plugin)
```

User story stays in Obsidian for context, Linear Integration plugin creates issue for external tracking.[^3_9]
<span style="display:none">[^3_10][^3_11][^3_12][^3_13][^3_14][^3_15][^3_16][^3_17][^3_18]</span>

<div align="center">⁂</div>

[^3_1]: https://www.obsidianstats.com/tags/kanban

[^3_2]: https://www.obsidianstats.com/tags/project-management

[^3_3]: https://forum.obsidian.md/t/development-for-projects-plugin-needed/101089

[^3_4]: https://dev.to/erikaheidi/setting-up-obsidian-for-content-planning-and-project-management-38f1

[^3_5]: https://www.reddit.com/r/ObsidianMD/comments/178dq4s/how_to_have_an_effective_backlog/

[^3_6]: https://www.reddit.com/r/ObsidianMD/comments/1ha3orv/is_there_a_setup_for_obsidian_to_make_sprints_for/

[^3_7]: https://www.dartai.com/blog/obsidian-for-project-management

[^3_8]: https://www.linkedin.com/pulse/supercharge-your-project-management-obsidian-deep-forero-martinez-rrkje

[^3_9]: https://github.com/casals/obsidian-linear-integration-plugin

[^3_10]: https://obsidian.md/plugins

[^3_11]: https://obsidian.md/plugins?search=task

[^3_12]: https://www.obsidian.global/agiledevelopment

[^3_13]: https://www.atlassian.com/agile/project-management/user-stories

[^3_14]: https://www.youtube.com/watch?v=2G15qE2tx8o

[^3_15]: https://www.stephanmiller.com/how-i-built-two-obsidian-plugins-while-kiro-ai-did-most-of-the-work/

[^3_16]: https://dev.to/dev_tips/why-i-switched-from-obsidian-a-real-developers-story-and-what-im-using-now-ndn

[^3_17]: https://www.youtube.com/watch?v=6UZemN4EVA0

[^3_18]: https://www.youtube.com/watch?v=13mElDSs0a8

