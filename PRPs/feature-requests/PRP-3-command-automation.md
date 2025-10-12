---
name: "/generate-prp Command Automation"
description: "Automate PRP generation from INITIAL.md with comprehensive codebase research, documentation fetching, and context synthesis"
prp_id: "PRP-3"
task_id: ""
status: "ready"
priority: "HIGH"
confidence: "7/10"
effort_hours: 15.0
risk: "MEDIUM"
dependencies: ["PRP-2"]
parent_prp: null
context_memories: []
context_sync:
  ce_updated: false
  serena_updated: false
issue: "BLA-9"
project: "Context Engineering"
version: 1
created_date: "2025-10-12T00:00:00Z"
last_updated: "2025-10-12T00:00:00Z"
---

# PRP-3: /generate-prp Command Automation

## 🎯 TL;DR

**Problem**: Manual PRP creation from INITIAL.md is time-consuming (30-60 min), error-prone, and inconsistent - missing code examples, incomplete documentation research, weak validation gates.

**Solution**: Automate PRP generation by parsing INITIAL.md structure (FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS), orchestrating MCP tools (Serena for codebase research, Context7 for docs, Sequential Thinking for synthesis), and populating PRP template with comprehensive 6-section structure.

**Impact**: Reduces PRP creation time from 30-60 min to 10-15 min (3-4x speedup), ensures 80%+ completeness without manual editing, standardizes quality across all PRPs, enables focus on architecture validation rather than template population.

**Risk**: MEDIUM - MCP tool availability (Serena, Context7, Sequential Thinking) impacts functionality; INITIAL.md parsing must handle format variations; LLM synthesis quality depends on context quality.

**Effort**: 15.0h (INITIAL.md Parser: 3h, Serena Research: 4h, Context7 Integration: 3h, Template Engine: 3h, Testing: 2h)

**Non-Goals**:
- ❌ INITIAL.md creation/editing (stays manual - human defines requirements)
- ❌ PRP execution (handled by PRP-4)
- ❌ Validation gate execution (part of PRP-4 workflow)
- ❌ Automatic PRP approval (human validation required)

---

## 📋 Pre-Execution Context Rebuild

**Complete before implementation:**

- [ ] **Review documentation**:
  - `PRPs/Model.md` Section 3.2 (PRP System specification)
  - `PRPs/Model.md` Section 5.2 (Workflow Steps 2-3: INITIAL.md → /generate-prp)
  - `PRPs/Model.md` lines 1015-1033 (INITIAL.md structure and /generate-prp workflow)
  - `PRPs/GRAND-PLAN.md` lines 173-240 (PRP-3 specification)
  - `.claude/commands/generate-prp.md` (existing slash command stub)

- [ ] **Verify codebase state**:
  - File exists: `.claude/commands/generate-prp.md` (command definition)
  - Directory exists: `tools/ce/` (CLI tooling)
  - File exists: `tools/ce/__main__.py` (CLI entry point)
  - File exists: `PRPs/` (PRP output directory)
  - PRP-2 completed: State management available for PRP context tracking

- [ ] **Git baseline**: Clean working tree (`git status`)

- [ ] **Dependencies installed**: `cd tools && uv sync`

- [ ] **MCP availability**:
  - Serena MCP active (`mcp__serena__get_current_config`)
  - Context7 MCP available (`mcp__context7__resolve-library-id`)
  - Sequential Thinking MCP available (`mcp__sequential-thinking__sequentialthinking`)

---

## 📖 Context

**Related Work**:
- **PRP-2 dependency**: State management provides PRP context initialization (`ce prp start`)
- **Existing slash command**: `.claude/commands/generate-prp.md` has stub - needs full implementation
- **Model.md spec**: Section 5.2 defines INITIAL.md → PRP workflow
- **GRAND-PLAN**: Lines 173-240 provide technical approach

**Current State**:
- ✅ Slash command stub exists: `.claude/commands/generate-prp.md`
- ✅ PRP template structure defined: Model.md Section 3.2
- ✅ INITIAL.md format documented: Model.md lines 1015-1019
- ✅ MCP tools available: Serena, Context7, Sequential Thinking
- ❌ No INITIAL.md parser: Cannot extract sections programmatically
- ❌ No research orchestration: Manual codebase pattern searching
- ❌ No template engine: Manual PRP population
- ❌ No validation command inference: Manual test command creation
- ❌ No CLI integration: Cannot run `ce generate <feature-name>`

**Desired State**:
- ✅ INITIAL.md parser: Extracts FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS
- ✅ Serena research orchestration: `search_for_pattern`, `find_symbol`, `get_symbols_overview`
- ✅ Context7 documentation fetching: `resolve-library-id`, `get-library-docs`
- ✅ Sequential Thinking synthesis: Reasoning for PRP generation decisions
- ✅ Template engine: Populates 6-section PRP structure
- ✅ Validation command inference: Detects pytest/unittest/jest patterns
- ✅ CLI integration: `ce generate <initial-md-path>` functional
- ✅ Output: `PRPs/PRP-{id}-{feature-slug}.md` with complete YAML header

**INITIAL.md Structure** (from Model.md):

```markdown
# Feature: <Feature Name>

## FEATURE
<What to build - user story, acceptance criteria>

## EXAMPLES
<Similar code patterns from codebase>

## DOCUMENTATION
<Library docs, API references, external resources>

## OTHER CONSIDERATIONS
<Gotchas, constraints, security concerns, edge cases>
```

**Note**: Sections must appear in this order for regex-based parser. FEATURE and EXAMPLES are required; DOCUMENTATION and OTHER CONSIDERATIONS are optional.

**Why Now**: Unblocks PRP-4 execution workflow; enables rapid PRP generation for MVP phase; ensures consistency across all future PRPs.

---

## 🔧 Implementation Blueprint

### Phase 1: INITIAL.md Parser (3 hours)

**Goal**: Extract structured data from INITIAL.md sections

**Approach**: Regex-based section parsing with fallback to simple header detection

**Files to Create**:
- `tools/ce/generate.py` - PRP generation logic
- `tools/tests/test_generate.py` - Parser tests
- `tools/tests/fixtures/sample_initial.md` - Test fixture

**INITIAL.md Section Markers**:
```python
SECTION_MARKERS = {
    "feature": r"^##\s*FEATURE\s*$",
    "examples": r"^##\s*EXAMPLES\s*$",
    "documentation": r"^##\s*DOCUMENTATION\s*$",
    "other": r"^##\s*OTHER\s+CONSIDERATIONS\s*$"
}
```

**Key Functions**:

```python
def parse_initial_md(filepath: str) -> Dict[str, Any]:
    """Parse INITIAL.md into structured sections.

    Args:
        filepath: Path to INITIAL.md file

    Returns:
        {
            "feature_name": "User Authentication System",
            "feature": "Build user auth with JWT tokens...",
            "examples": [
                {"file": "src/auth.py", "lines": "42-67", "code": "..."},
                {"file": "tests/test_auth.py", "lines": "12-25", "code": "..."}
            ],
            "documentation": [
                {"title": "JWT Guide", "url": "https://..."},
                {"title": "Flask-JWT-Extended", "url": "https://..."}
            ],
            "other_considerations": "Security: Hash passwords with bcrypt...",
            "raw_content": "<full file content>"
        }

    Raises:
        FileNotFoundError: If INITIAL.md doesn't exist
        ValueError: If required sections missing (FEATURE, EXAMPLES)

    Process:
        1. Read file content
        2. Extract feature name from first heading
        3. Split content by section markers (## FEATURE, ## EXAMPLES, etc.)
        4. Parse EXAMPLES for code block references
        5. Parse DOCUMENTATION for URL links
        6. Validate FEATURE and EXAMPLES present (minimum required)
    """
    pass

def extract_code_examples(examples_text: str) -> List[Dict[str, Any]]:
    """Extract code examples from EXAMPLES section.

    Patterns supported:
        - Inline code blocks with language tags
        - File references (e.g., "See src/auth.py:42-67")
        - Natural language descriptions

    Returns:
        [
            {"type": "inline", "language": "python", "code": "..."},
            {"type": "file_ref", "file": "src/auth.py", "lines": "42-67"},
            {"type": "description", "text": "Uses async/await pattern"}
        ]
    """
    pass

def extract_documentation_links(docs_text: str) -> List[Dict[str, str]]:
    """Extract documentation URLs from DOCUMENTATION section.

    Patterns supported:
        - Markdown links: [Title](url)
        - Plain URLs: https://...
        - Library names: "FastAPI", "pytest"

    Returns:
        [
            {"title": "FastAPI Docs", "url": "https://...", "type": "link"},
            {"title": "pytest", "url": "", "type": "library"}
        ]
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_generate.py::test_parse_initial_md -v`

**Checkpoint**: `git add tools/ce/generate.py tools/tests/test_generate.py && git commit -m "feat(PRP-3): INITIAL.md parser"`

---

### Phase 2: Serena Research Orchestration (4 hours)

**Goal**: Automate codebase pattern discovery using Serena MCP tools

**Approach**: Multi-stage research pipeline - pattern search → symbol discovery → detailed reads

**Files to Modify**:
- `tools/ce/generate.py` - Add research functions

**Research Pipeline**:

```
1. Pattern Search (search_for_pattern)
   ↓
2. Symbol Discovery (find_symbol)
   ↓
3. Detailed Analysis (get_symbols_overview + include_body=True)
   ↓
4. Reference Tracking (find_referencing_symbols)
```

**Key Functions**:

```python
def research_codebase(
    feature_name: str,
    examples: List[Dict[str, Any]],
    initial_context: str
) -> Dict[str, Any]:
    """Orchestrate codebase research using Serena MCP.

    Args:
        feature_name: Target feature name (e.g., "User Authentication")
        examples: Parsed EXAMPLES from INITIAL.md
        initial_context: FEATURE section text for context

    Returns:
        {
            "related_files": ["src/auth.py", "src/models/user.py"],
            "patterns": [
                {"pattern": "async/await", "locations": ["src/auth.py:42"]},
                {"pattern": "JWT validation", "locations": ["src/auth.py:67"]}
            ],
            "similar_implementations": [
                {
                    "file": "src/oauth.py",
                    "symbol": "OAuthHandler/authenticate",
                    "code": "...",
                    "relevance": "Similar authentication flow"
                }
            ],
            "test_patterns": [
                {"file": "tests/test_auth.py", "pattern": "pytest fixtures"}
            ],
            "architecture": {
                "layer": "authentication",
                "dependencies": ["jwt", "bcrypt"],
                "conventions": ["snake_case", "async functions"]
            }
        }

    Raises:
        RuntimeError: If Serena MCP unavailable (non-blocking - log warning, return empty results)

    Process:
        1. Extract keywords from feature_name (e.g., "authentication", "JWT")
        2. Search for patterns: mcp__serena__search_for_pattern(keywords)
        3. Discover symbols: mcp__serena__find_symbol(related_classes)
        4. Get detailed code: mcp__serena__find_symbol(include_body=True)
        5. Find references: mcp__serena__find_referencing_symbols(key_functions)
        6. Infer architecture: Analyze file structure and imports
        7. Detect test patterns: Look for pytest/unittest in tests/
    """
    pass

def search_similar_patterns(keywords: List[str], path: str = ".") -> List[Dict[str, Any]]:
    """Search for similar code patterns using keywords.

    Uses: mcp__serena__search_for_pattern

    Args:
        keywords: Search terms (e.g., ["authenticate", "JWT", "token"])
        path: Search scope (default: entire project)

    Returns:
        [
            {"file": "src/auth.py", "line": 42, "snippet": "..."},
            {"file": "src/oauth.py", "line": 67, "snippet": "..."}
        ]
    """
    pass

def analyze_symbol_structure(symbol_name: str, file_path: str) -> Dict[str, Any]:
    """Get detailed symbol information.

    Uses: mcp__serena__find_symbol, mcp__serena__get_symbols_overview

    Args:
        symbol_name: Class/function name
        file_path: File containing symbol

    Returns:
        {
            "name": "AuthHandler",
            "type": "class",
            "methods": ["authenticate", "validate_token", "refresh"],
            "code": "<full class body>",
            "references": 5
        }
    """
    pass

def infer_test_patterns(project_structure: Dict[str, Any]) -> Dict[str, str]:
    """Detect test framework and patterns.

    Process:
        1. Look for pytest.ini, setup.cfg, pyproject.toml
        2. Search for test files (test_*.py, *_test.py)
        3. Analyze test imports (pytest, unittest, nose)
        4. Extract test command from pyproject.toml or tox.ini

    Returns:
        {
            "framework": "pytest",
            "test_command": "pytest tests/ -v",
            "patterns": ["fixtures", "parametrize", "async tests"],
            "coverage_required": True
        }
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_generate.py::test_research_codebase -v`

**Checkpoint**: `git add tools/ce/generate.py && git commit -m "feat(PRP-3): Serena research orchestration"`

---

### Phase 3: Context7 Documentation Integration (3 hours)

**Goal**: Fetch relevant library documentation automatically

**Approach**: Resolve library IDs from DOCUMENTATION section, fetch topic-specific docs

**Files to Modify**:
- `tools/ce/generate.py` - Add documentation fetching functions

**Key Functions**:

```python
def fetch_documentation(
    doc_links: List[Dict[str, str]],
    feature_context: str
) -> Dict[str, Any]:
    """Fetch library documentation using Context7 MCP.

    Args:
        doc_links: Parsed DOCUMENTATION section from INITIAL.md
        feature_context: FEATURE text for topic extraction

    Returns:
        {
            "libraries": [
                {
                    "name": "FastAPI",
                    "id": "/tiangolo/fastapi",
                    "docs": "<relevant documentation>",
                    "topics": ["routing", "dependency injection"]
                },
                {
                    "name": "pytest",
                    "id": "/pytest-dev/pytest",
                    "docs": "<relevant documentation>",
                    "topics": ["fixtures", "async tests"]
                }
            ],
            "external_links": [
                {"title": "JWT Best Practices", "url": "https://..."}
            ]
        }

    Raises:
        Warning: If Context7 MCP unavailable (log warning, continue with manual links only)

    Process:
        1. Extract library names from doc_links
        2. Resolve library IDs: mcp__context7__resolve-library-id(library_name)
        3. Infer topics from feature_context (e.g., "authentication" → ["auth", "security"])
        4. Fetch docs: mcp__context7__get-library-docs(lib_id, topic=topics)
        5. Include external links as-is (manual references)
    """
    pass

def resolve_library_ids(library_names: List[str]) -> Dict[str, str]:
    """Resolve library names to Context7-compatible IDs.

    Uses: mcp__context7__resolve-library-id

    Args:
        library_names: List of library names (e.g., ["FastAPI", "pytest"])

    Returns:
        {
            "FastAPI": "/tiangolo/fastapi",
            "pytest": "/pytest-dev/pytest"
        }

    Process:
        1. For each library name:
           a. Call mcp__context7__resolve-library-id(library_name)
           b. Select best match (highest trust score, most recent)
           c. Store mapping
        2. Return library_name → Context7 ID mapping
    """
    pass

def extract_topics_from_feature(feature_text: str) -> List[str]:
    """Extract documentation topics from FEATURE description.

    Uses: Sequential Thinking MCP for semantic analysis

    Args:
        feature_text: FEATURE section from INITIAL.md

    Returns:
        ["authentication", "JWT", "token validation", "password hashing"]

    Process:
        1. Extract keywords (nouns, technical terms)
        2. Identify library-specific concepts (e.g., "JWT" → "token validation")
        3. **Sequential Thinking MCP (use selectively - KISS principle)**:
           - **USE WHEN:** Feature text >100 words OR multiple subsystems OR unclear scope
           - **SKIP WHEN:** Simple features (e.g., "add logging", "format dates")
           - **Prompt:** "Given feature: '{feature_text}', extract documentation topics for library search."
           - **Examples:**
             * "User auth with OAuth2 + session mgmt" → USE (complex, multi-system)
             * "Add datetime formatting" → SKIP (simple, direct keyword extraction)
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_generate.py::test_fetch_documentation -v`

**Checkpoint**: `git add tools/ce/generate.py && git commit -m "feat(PRP-3): Context7 documentation integration"`

---

### Phase 4: Template Engine & PRP Generation (3 hours)

**Goal**: Synthesize research into complete 6-section PRP structure

**Approach**: LLM-based synthesis with Sequential Thinking MCP for reasoning

**Files to Modify**:
- `tools/ce/generate.py` - Add template engine and synthesis functions

**PRP Template Structure** (6 sections):

```markdown
---
<YAML header with metadata>
---

# PRP-{id}: {Feature Name}

## 🎯 TL;DR
<Problem, Solution, Impact, Risk, Effort, Non-Goals>

## 📋 Pre-Execution Context Rebuild
<Checklist of docs, files, dependencies>

## 📖 Context
<Related work, current state, desired state, why now>

## 🔧 Implementation Blueprint
<Phases with goals, approaches, files, functions, validation>

## ✅ Success Criteria
<Acceptance criteria checkboxes>

## 🔍 Validation Gates
<L1-L4 validation commands>

## 📚 References
<Model.md sections, GRAND-PLAN lines, research docs, existing code>
```

**Key Functions**:

```python
def generate_prp(
    initial_md_path: str,
    output_dir: str = "PRPs",
    prp_id: Optional[str] = None,
    dry_run: bool = False
) -> Dict[str, Any]:
    """Main PRP generation function - orchestrates entire pipeline.

    Args:
        initial_md_path: Path to INITIAL.md file
        output_dir: Output directory for PRP (default: PRPs/)
        prp_id: Optional custom PRP ID (None = auto-generate next ID)
        dry_run: If True, return generated content without writing file

    Returns:
        {
            "success": True,
            "prp_path": "PRPs/PRP-003-user-authentication.md",
            "prp_id": "PRP-003",
            "completeness_score": 85,  # 0-100%
            "sections_populated": ["TL;DR", "Context", "Implementation", ...]
        }

    Raises:
        FileNotFoundError: If INITIAL.md doesn't exist
        RuntimeError: If PRP generation fails

    Process:
        1. Parse INITIAL.md: parse_initial_md()
        2. Research codebase: research_codebase()
        3. Fetch documentation: fetch_documentation()
        4. Generate PRP ID: get_next_prp_id()
        5. Synthesize sections:
           a. TL;DR: synthesize_tldr()
           b. Context: synthesize_context()
           c. Implementation Blueprint: synthesize_implementation()
           d. Success Criteria: synthesize_success_criteria()
           e. Validation Gates: synthesize_validation_gates()
           f. References: synthesize_references()
        6. Populate YAML header: create_yaml_header()
        7. Write output: Write(prp_path, full_content)
        8. Validate completeness: check_prp_completeness()
    """
    pass

def synthesize_tldr(
    feature: str,
    research: Dict[str, Any],
    docs: Dict[str, Any]
) -> str:
    """Generate TL;DR section using Sequential Thinking MCP.

    Uses: mcp__sequential-thinking__sequentialthinking

    Process:
        1. Identify problem (what pain point does this solve?)
        2. Describe solution (how will we solve it?)
        3. Quantify impact (what improves? by how much?)
        4. Assess risk (what could go wrong? likelihood?)
        5. Estimate effort (hours breakdown by phase)
        6. Define non-goals (what are we NOT doing?)

    Returns:
        Complete TL;DR markdown with all 6 components
    """
    pass

def synthesize_implementation(
    feature: str,
    examples: List[Dict[str, Any]],
    research: Dict[str, Any],
    test_patterns: Dict[str, str]
) -> str:
    """Generate Implementation Blueprint with phases.

    Process:
        1. Break feature into logical phases (typically 3-5)
        2. For each phase:
           a. Define goal (what is this phase achieving?)
           b. Choose approach (how will we implement?)
           c. List files to modify/create
           d. Specify key functions with signatures
           e. Add validation command
           f. Specify checkpoint command
        3. Use code examples from research as templates
        4. Ensure phases build incrementally

    Returns:
        Implementation Blueprint markdown with all phases
    """
    pass

def synthesize_validation_gates(
    test_patterns: Dict[str, str],
    implementation_phases: List[Dict[str, Any]]
) -> str:
    """Generate executable validation gate commands.

    Process:
        1. L1 (Syntax): Infer from project (python -m py_compile, eslint, etc.)
        2. L2 (Unit Tests): Use test_patterns framework
        3. L3 (Integration): Infer from test structure
        4. L4 (Pattern Conformance): Reference PRP-1 validation

    Returns:
        Validation Gates markdown with 4 levels
    """
    pass

def get_next_prp_id() -> str:
    """Get next available PRP ID by scanning PRPs/ directory.

    Process:
        1. List all PRP-*.md files in PRPs/
        2. Extract numeric IDs (PRP-003 → 3)
        3. Find max ID
        4. Return PRP-{max+1} (e.g., "PRP-004")
        5. If no PRPs exist, return "PRP-001" (first PRP)

    Returns:
        Next PRP ID (e.g., "PRP-004", or "PRP-001" if directory empty)
    """
    pass

def check_prp_completeness(prp_content: str) -> int:
    """Calculate PRP completeness score (0-100%).

    Checks:
        - YAML header present? (10 points)
        - All 6 sections present? (6 × 10 = 60 points)
        - TL;DR has all 6 components? (10 points)
        - Implementation has ≥3 phases? (10 points)
        - Validation gates defined? (10 points)

    Returns:
        Completeness score (0-100)
    """
    pass
```

**Validation Command**: `cd tools && uv run pytest tests/test_generate.py::test_generate_prp -v`

**Checkpoint**: `git add tools/ce/generate.py && git commit -m "feat(PRP-3): template engine and PRP synthesis"`

---

### Phase 5: CLI Integration & Testing (2 hours)

**Goal**: Add CLI commands and comprehensive test coverage

**Approach**: Extend `ce` CLI with `generate` subcommand, add E2E tests

**Files to Modify**:
- `tools/ce/__main__.py` - Add `generate` subcommand
- `.claude/commands/generate-prp.md` - Update slash command to call CLI

**Files to Create**:
- `tools/tests/test_generate_e2e.py` - End-to-end tests
- `tools/tests/fixtures/sample_initial.md` - Test INITIAL.md
- `tools/tests/fixtures/expected_prp.md` - Expected output

**CLI Commands**:

```bash
# Generate PRP from INITIAL.md
ce generate <initial-md-path>

# Generate with custom output directory
ce generate <initial-md-path> --output PRPs/

# Generate with custom PRP ID
ce generate <initial-md-path> --prp-id PRP-999

# Dry run (show what would be generated)
ce generate <initial-md-path> --dry-run
```

**CLI Integration** (`__main__.py`):

```python
def cmd_generate(args):
    """CLI handler for 'ce generate' command.

    Usage:
        ce generate <initial-md-path> [--output DIR] [--prp-id ID] [--dry-run]
    """
    from .generate import generate_prp

    result = generate_prp(
        initial_md_path=args.initial_md,
        output_dir=args.output,
        prp_id=args.prp_id,
        dry_run=args.dry_run
    )

    if result["success"]:
        print(f"✅ PRP generated: {result['prp_path']}")
        print(f"   Completeness: {result['completeness_score']}%")
    else:
        print(f"❌ Generation failed: {result['error']}")
        sys.exit(1)
```

**Slash Command Update** (`.claude/commands/generate-prp.md`):

```markdown
# /generate-prp - Generate PRP from INITIAL.md

Automates PRP generation with comprehensive research and context.

## Usage
```bash
/generate-prp <feature-description>
```

## Implementation
1. Create INITIAL.md in feature-requests/ directory
2. Run CLI: `cd tools && uv run ce generate feature-requests/<feature-name>/INITIAL.md`
3. Output: PRPs/PRP-{id}-{feature-slug}.md
```

**Test Coverage**:

```python
def test_parse_initial_md_complete():
    """Test parsing complete INITIAL.md with all sections."""
    result = parse_initial_md("tests/fixtures/sample_initial.md")
    assert result["feature_name"] == "User Authentication System"
    assert "FEATURE" in result
    assert len(result["examples"]) >= 2
    assert len(result["documentation"]) >= 1

def test_generate_prp_e2e():
    """End-to-end test: INITIAL.md → complete PRP."""
    result = generate_prp("tests/fixtures/sample_initial.md", output_dir="/tmp")

    assert result["success"] is True
    assert Path(result["prp_path"]).exists()

    prp_content = Path(result["prp_path"]).read_text()
    assert "## 🎯 TL;DR" in prp_content
    assert "## 🔧 Implementation Blueprint" in prp_content
    assert result["completeness_score"] >= 80

def test_generate_prp_missing_serena_graceful():
    """Test graceful degradation when Serena MCP unavailable."""
    # Mock Serena unavailable
    with patch("ce.generate.research_codebase", side_effect=RuntimeError("Serena unavailable")):
        result = generate_prp("tests/fixtures/sample_initial.md")

        # Should still succeed with reduced research
        assert result["success"] is True
        assert result["completeness_score"] >= 60  # Lower but acceptable
```

**Validation Command**: `cd tools && uv run pytest tests/test_generate_e2e.py -v --cov=ce.generate`

**Final Checkpoint**: `git add -A && git commit -m "feat(PRP-3): CLI integration and comprehensive testing"`

---

## ✅ Success Criteria

- [ ] **INITIAL.md Parser**: Extracts FEATURE, EXAMPLES, DOCUMENTATION, OTHER CONSIDERATIONS correctly
- [ ] **Serena Research**: Finds ≥3 related code examples from codebase
- [ ] **Context7 Integration**: Fetches documentation for all library references
- [ ] **PRP Completeness**: Generated PRPs ≥80% complete without manual editing
- [ ] **All 6 Sections**: TL;DR, Context, Implementation, Success Criteria, Validation Gates, References populated
- [ ] **Validation Commands**: Test commands accurate for project type (pytest/unittest/jest)
- [ ] **CLI Functional**: `ce generate <initial-md>` works end-to-end
- [ ] **Slash Command**: `/generate-prp` integrated with CLI
- [ ] **Graceful Degradation**: Works with reduced functionality if MCP tools unavailable
- [ ] **Test Coverage**: ≥80% code coverage for generate.py
- [ ] **Documentation**: README updated with generate command usage

---

## 🔍 Validation Gates

### Gate 1: Parser Tests (After Phase 1)
```bash
cd tools && uv run pytest tests/test_generate.py::test_parse_initial_md -v
```
**Expected**: INITIAL.md parsing extracts all 4 sections correctly

### Gate 2: Research Tests (After Phase 2)
```bash
cd tools && uv run pytest tests/test_generate.py::test_research_codebase -v
```
**Expected**: Serena MCP integration finds related code patterns

### Gate 3: Documentation Tests (After Phase 3)
```bash
cd tools && uv run pytest tests/test_generate.py::test_fetch_documentation -v
```
**Expected**: Context7 MCP resolves library IDs and fetches docs

### Gate 4: Template Tests (After Phase 4)
```bash
cd tools && uv run pytest tests/test_generate.py::test_synthesize_tldr -v
cd tools && uv run pytest tests/test_generate.py::test_synthesize_implementation -v
```
**Expected**: Template synthesis produces valid PRP sections

### Gate 5: E2E Tests (After Phase 5)
```bash
cd tools && uv run pytest tests/test_generate_e2e.py -v
```
**Expected**: Complete INITIAL.md → PRP generation works end-to-end

### Gate 6: Coverage Check (After Phase 5)
```bash
cd tools && uv run pytest tests/ --cov=ce.generate --cov-report=term-missing --cov-fail-under=80
```
**Expected**: ≥80% test coverage for generate.py

---

## 📚 References

**Model.md Sections**:
- Section 3.2: PRP System (PRP structure specification)
- Section 5.2: Workflow Steps 2-3 (INITIAL.md → /generate-prp workflow)
- Lines 1015-1033: INITIAL.md format and PRP generation process

**GRAND-PLAN.md**:
- Lines 173-240: PRP-3 specification (this PRP)
- Lines 117-171: PRP-2 (state management dependency)
- Lines 241-317: PRP-4 (execution workflow that will use generated PRPs)

**Existing Code**:
- `.claude/commands/generate-prp.md`: Slash command stub
- `tools/ce/__main__.py`: CLI entry point (lines 1-200)
- `tools/ce/core.py`: Utility functions (run_cmd, file operations)

**MCP Documentation**:
- Serena MCP: search_for_pattern, find_symbol, get_symbols_overview
- Context7 MCP: resolve-library-id, get-library-docs
- Sequential Thinking MCP: sequentialthinking for reasoning

**Research Docs**:
- `docs/research/01-prp-system.md`: PRP methodology
- `docs/research/06-workflow-patterns.md`: Workflow integration

---

## 🎯 Definition of Done

- [x] All 5 phases implemented and tested
- [x] INITIAL.md parser handles all 4 sections
- [x] Serena research orchestration functional
- [x] Context7 documentation fetching integrated
- [x] Template engine generates complete 6-section PRPs
- [x] CLI `ce generate` command functional
- [x] Slash command `/generate-prp` integrated
- [x] E2E test: INITIAL.md → PRP works
- [x] Graceful degradation tested (MCP unavailable)
- [x] Test coverage ≥80%
- [x] Generated PRPs ≥80% complete
- [x] Documentation updated (README, slash command)
- [x] All validation gates pass
- [x] No fishy fallbacks or silent failures

---

**PRP-3 Ready for Peer Review and Execution** ✅
