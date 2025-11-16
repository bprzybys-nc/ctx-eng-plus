# PLAN: Vacuum Enhancement - NLP-Powered PRP Lifecycle Detection

## Problem Statement

Current vacuum misses temporary docs throughout PRP lifecycle and uses naive text matching:

**Example 1**: Superseded feature requests (PRP-42)
- `INIT-PROJECT-WORKFLOW-INITIAL.md`, `*-ANALYSIS.md`, `*-PLAN.md`
- All superseded by `PRP-42-init-project-workflow-overhaul.md`
- Vacuum flagged as LOW confidence (55%) - requires manual review

**Example 2**: INITIAL.md files with generated PRPs
- `PRPs/feature-requests/auth-system/INITIAL.md` → `PRP-23-auth-system.md` (executed)
- Not detected (vacuum doesn't scan subdirectories)

**Example 3**: Obsolete docs with weak similarity detection
- Current: Filename patterns only (`-SUMMARY-`, `-PLAN-`)
- Misses: Docs without standard prefixes but same content as executed PRPs

**Root cause**:
- Naive text matching (difflib SequenceMatcher)
- No semantic understanding
- Filename-based only (no content analysis)
- No subdirectory scanning (misses INITIAL.md in subdirs)

**Impact**: Users manually review 30-40% of candidates that could be auto-detected with NLP.

## Proposed Solution

New `prp_lifecycle_docs` strategy with NLP-powered 3-tier detection:

**Tier 1: Local NLP (sentence-transformers)** (semantic, no API cost)
- Use pre-trained all-MiniLM-L6-v2 model (80MB, runs locally on M1 Pro 16GB)
- Generate 384-dimensional embeddings for all PRPs and lifecycle docs
- Compute cosine similarity between doc pairs
- Cache embeddings in `.ce/nlp-embeddings-cache.json` for performance
- Confidence: 70-95% (semantic understanding)
- Fallback: sklearn TF-IDF → difflib SequenceMatcher

**Detection Types**:
1. **INITIAL→PRP**: INITIAL.md files that became formal PRPs
2. **Temporary→PRP**: PLAN/ANALYSIS/REPORT docs integrated into executed PRPs
3. **Superseded**: Feature requests replaced by executed PRPs

**Tier 2: LLM Batch Analysis** (Haiku, for uncertain cases)
- For 40-70% confidence candidates only:
  - Batch all uncertain docs into single LLM call
  - Ask Haiku: "Does PRP-X fully implement doc Y?"
  - Response: YES (boost to 90%) / NO (keep) / PARTIAL (keep)
- Cost reduction: 100 docs × $0.003 = $0.30 → 30 docs × $0.001 = $0.03 (90% savings)

**Tier 3: Universal Scanning** (recursive subdirectory detection)
- Scan all markdown files with `rglob("*.md")` (not just top-level)
- Detect lifecycle docs across entire PRPs/ directory tree
- Apply to PRPs/feature-requests/, PRPs/executed/, PRPs/ subdirs

## Decomposition into Phases

### Phase 1: NLP Foundation Layer

**Goal**: Create general-purpose NLP utilities for doc/code semantic analysis with 3-tier fallback

**Estimated Hours**: 2.5

**Complexity**: MEDIUM

**Files Modified**:
- `tools/ce/nlp/similarity.py` (new - DocumentSimilarity class)
- `tools/ce/nlp/normalizer.py` (new - TextNormalizer class)
- `tools/ce/nlp/cache.py` (new - EmbeddingCache class)
- `tools/ce/nlp/__init__.py` (new - exports)
- `tools/pyproject.toml` (add sentence-transformers>=2.2.0, scikit-learn>=1.0.0, numpy>=1.21.0)
- `examples/nlp-semantic-search.md` (new - usage examples for Claude Code)

**Dependencies**: None

**Implementation Steps**:
1. Create `ce/nlp/similarity.py` with `DocumentSimilarity` class:
   - Tier 1: sentence-transformers (all-MiniLM-L6-v2) - 0.85+ accuracy
     - Model auto-downloads via HuggingFace, cached to ~/.cache/huggingface/ (~80MB on first run)
   - Tier 2: sklearn TfidfVectorizer - 0.70+ accuracy
   - Tier 3: difflib SequenceMatcher - 0.50+ accuracy (baseline)
2. Create `ce/nlp/normalizer.py` with `TextNormalizer`:
   - Remove code blocks (preserve semantic indicators: "function", "class")
   - Normalize whitespace (collapse multiple spaces/newlines)
   - Extract markdown structure (headers → plain text, links → anchor text)
   - Preserve YAML frontmatter keys for metadata matching
3. Create `ce/nlp/cache.py` with `EmbeddingCache`:
   - JSON serialization (not pickle) for safety
   - mtime-based invalidation (recompute if file modified)
   - Cache location: `.ce/nlp-embeddings-cache.json`
4. Add `examples/nlp-semantic-search.md` with Claude Code usage patterns:
   - Finding similar PRPs for duplicate detection
   - Doc-code matching for orphan test detection
   - Semantic clustering for misplaced doc detection
5. Graceful 3-tier fallback with explicit import error handling

**Validation Gates**:
- Unit test: `test_three_tier_fallback_chain()` - verify each tier falls back correctly
- Unit test: `test_cache_invalidation_on_file_change()` - mtime triggers recomputation
- Unit test: `test_embedding_performance_baseline()` - 10 docs, <50ms on M1 (cached), 1-2s (uncached)
- Integration test: sentence-transformers detects similar docs (>0.7 similarity on real PRPs)

### Phase 2: PRP Lifecycle Docs Strategy

**Goal**: Detect INITIAL.md, PLAN/ANALYSIS/REPORT, superseded docs using NLP

**Estimated Hours**: 2.5

**Complexity**: MEDIUM

**Files Modified**:
- `tools/ce/vacuum_strategies/prp_lifecycle_docs.py` (new)
- `tools/ce/vacuum.py` (register new strategy)

**Dependencies**: Phase 1 (needs ce.nlp module)

**Implementation Steps**:
1. Create `PRPLifecycleDocsStrategy` class extending `VacuumStrategy`
2. Import `from ce.nlp import DocumentSimilarity, TextNormalizer`
3. Implement recursive scanning (`rglob("*.md")`) for all PRPs/ subdirectories
4. Add `_detect_lifecycle_doc()` dispatcher (3 detection types)
5. Implement `_check_initial_md()` (INITIAL.md → executed PRP using semantic similarity)
6. Implement `_check_temporary_doc()` (PLAN/ANALYSIS/REPORT → PRP)
7. Implement `_check_superseded_request()` (feature-request → PRP)
8. Use `DocumentSimilarity.compare(doc_a, doc_b)` for semantic matching
9. Implement confidence threshold logic:
   - Similarity ≥75%: Flag as HIGH (no LLM needed)
   - Similarity 40-70%: Flag as MEDIUM (queue for Haiku batch review)
   - Similarity <40%: Keep as-is (not a lifecycle doc)

**Validation Gates**:
- Unit test: Detects INITIAL.md with matching executed PRP
- Unit test: Detects PLAN-*.md integrated into PRP
- Unit test: Recursive scan finds docs in subdirectories
- Integration test: No false positives on active feature requests

### Phase 3: Enhance Existing Strategies with NLP

**Goal**: Apply NLP to obsolete-docs and orphan-tests strategies (non-disruptive refactor)

**Estimated Hours**: 1.5

**Complexity**: LOW

**Files Modified**:
- `tools/ce/vacuum_strategies/obsolete_docs.py` (add NLP similarity)
- `tools/ce/vacuum_strategies/orphan_tests.py` (add semantic test-code matching)

**Dependencies**: Phase 1 (needs ce.nlp module)

**Implementation Steps**:
1. **obsolete_docs.py**: Add semantic similarity to existing filename patterns
   - Use NLP as confidence booster (+20% if semantic match)
   - Keep existing logic (non-disruptive)
2. **orphan_tests.py**: Add semantic test-code matching
   - Match test files to code files beyond filename conventions
   - Detect orphaned tests when code semantically changed

**Validation Gates**:
- Unit test: obsolete_docs detects more candidates with NLP
- Unit test: orphan_tests matches semantic relationships
- Regression test: Existing detections still work (no breakage)

### Phase 4: LLM Batch Analysis (Haiku)

**Goal**: Add Haiku batch processing for 40-70% confidence candidates

**Estimated Hours**: 2

**Complexity**: MEDIUM

**Files Modified**:
- `tools/ce/vacuum_strategies/llm_analyzer.py` (new - Haiku batch client)

**Dependencies**: Phase 2 (needs candidate format from prp_lifecycle_docs)

**Implementation Steps**:
1. Create `LLMBatchAnalyzer` class with Haiku client
2. Design batch prompt with limits:
   - Maximum 10-15 docs per batch (Haiku 200K context limit)
   - Prompt template: "Compare each [doc A] vs [doc B], output YES/NO/PARTIAL per line"
   - Token budget: ~15K per batch (safe margin for 200K context)
3. Implement response parser (extract YES/NO/PARTIAL per doc)
4. Add confidence boost logic (YES → 90%, NO → keep, PARTIAL → keep)
5. Implement fallback to individual calls on batch failure
6. Add error handling for API failures

**Validation Gates**:
- Unit test: Batch analyzes 10 uncertain docs in single call
- Unit test: Haiku correctly identifies superseded docs as YES
- Integration test: Batch mode reduces API calls by 90%
- Integration test: API failure doesn't break vacuum

### Phase 5: Integration and Testing

**Goal**: Integrate all strategies into vacuum CLI with NLP backend flag

**Estimated Hours**: 1.5

**Complexity**: LOW

**Files Modified**:
- `tools/ce/vacuum.py` (add --nlp-backend flag, register prp_lifecycle_docs)
- `tools/ce/vacuum_strategies/__init__.py` (export new strategies)
- `tests/test_vacuum_nlp.py` (new - integration tests)

**Dependencies**: Phase 1, 2, 3, 4 (all strategies and NLP foundation)

**Implementation Steps**:
1. Register `prp_lifecycle_docs` strategy in vacuum CLI
2. Add CLI flag: `--nlp-backend [auto|sentence-transformers|sklearn|difflib]`
3. Update vacuum report format (show detection type, confidence)
4. Write integration tests: Full vacuum with NLP backend
5. Add performance benchmarks (with/without NLP)
6. Update CLAUDE.md with NLP backend documentation

**Validation Gates**:
- Integration test: `uv run ce vacuum --dry-run` detects INITIAL.md files
- Integration test: Detects PLAN/ANALYSIS/REPORT integrated into PRPs
- Integration test: Recursive scan finds docs in subdirectories
- Performance test: Embedding cache reduces computation by 95%
- Regression test: No false positives on active feature requests

## Success Criteria

- [ ] NLP backend detects INITIAL.md → executed PRP matches (confidence ≥70%)
- [ ] Detects PLAN/ANALYSIS/REPORT docs integrated into PRPs (confidence ≥75%)
- [ ] Detects superseded feature requests (confidence ≥70%)
- [ ] Recursive scan finds lifecycle docs in all subdirectories
- [ ] 40-70% confidence → triggers Haiku batch analysis automatically
- [ ] Batch mode: 10-30 docs analyzed in single LLM call
- [ ] Zero false positives on active feature requests
- [ ] Embedding cache reduces computation by 95%
- [ ] 3-tier fallback: sentence-transformers → sklearn → difflib
- [ ] Manual review reduced from 30-40% to <10%
- [ ] CLI flag `--nlp-backend` selects similarity algorithm

## Test Cases

**Test Case 1: INITIAL.md Detection**

Input:
```
PRPs/feature-requests/auth-system/INITIAL.md
PRPs/executed/PRP-23-auth-system-implementation.md
```

Expected:
- ✅ Flag: `auth-system/INITIAL.md` → "Generated as PRP-23" (confidence 85%+, type: INITIAL→PRP)

**Test Case 2: Temporary Lifecycle Docs**

Input:
```
PRPs/feature-requests/PLAN-vacuum-optimization.md
PRPs/feature-requests/ANALYSIS-vacuum-performance.md
PRPs/feature-requests/REPORT-vacuum-benchmark.md
PRPs/executed/PRP-38-vacuum-optimization.md
```

Expected:
- ✅ Flag: `PLAN-vacuum-optimization.md` → "Integrated into PRP-38" (confidence 80%+, type: Temporary→PRP)
- ✅ Flag: `ANALYSIS-vacuum-performance.md` → "Integrated into PRP-38" (confidence 80%+, type: Temporary→PRP)
- ✅ Flag: `REPORT-vacuum-benchmark.md` → "Integrated into PRP-38" (confidence 80%+, type: Temporary→PRP)

**Test Case 3: Superseded Feature Requests**

Input:
```
PRPs/feature-requests/INIT-PROJECT-WORKFLOW-INITIAL.md
PRPs/feature-requests/INIT-PROJECT-WORKFLOW-ROOT-CAUSE-ANALYSIS.md
PRPs/feature-requests/INIT-PROJECT-WORKFLOW-OVERHAUL-PLAN.md
PRPs/executed/PRP-42-init-project-workflow-overhaul.md
```

Expected:
- ✅ Flag: `INIT-PROJECT-WORKFLOW-INITIAL.md` → "Superseded by PRP-42" (confidence 85%+, type: Superseded)
- ✅ Flag: `INIT-PROJECT-WORKFLOW-ROOT-CAUSE-ANALYSIS.md` → "Superseded by PRP-42" (confidence 85%+)
- ✅ Flag: `INIT-PROJECT-WORKFLOW-OVERHAUL-PLAN.md` → "Superseded by PRP-42" (confidence 85%+)

**Test Case 4: Active Feature Requests (No False Positives)**

Input:
```
PRPs/feature-requests/INITIAL-critical-memory-consolidation.md (no matching PRP)
PRPs/feature-requests/migrating-project-serena-memories.md (no matching PRP)
```

Expected:
- ❌ Should NOT flag: `INITIAL-critical-memory-consolidation.md` (active, no executed PRP)
- ❌ Should NOT flag: `migrating-project-serena-memories.md` (active, no executed PRP)

## Implementation Order

**Stage 1** (Sequential - Foundation):
- Phase 1: NLP Foundation Layer (2h)

**Stage 2** (Parallel - Strategy Implementation):
- Phase 2: PRP Lifecycle Docs Strategy (2.5h)
- Phase 3: Enhance Existing Strategies (1.5h)
- Phase 4: LLM Batch Analysis (2h)

**Stage 3** (Sequential - Integration):
- Phase 5: Integration and Testing (1.5h)

**Total Time**: 9.5 hours
- Sequential execution: 9.5h
- Parallel execution (Stage 2): ~6h (with batch-gen-prp)
- Time savings: 37% with parallel execution

## Risk Mitigation

**Risk 1**: False positives (deletes valid feature requests)
- Mitigation: Require ≥70% NLP confidence for HIGH classification
- Mitigation: Always show in report for manual review before --execute
- Mitigation: 3-tier fallback ensures robust detection

**Risk 2**: sentence-transformers not installed
- Mitigation: Auto-fallback to sklearn TF-IDF (no ML required)
- Mitigation: Final fallback to difflib (stdlib only)
- Mitigation: CLI flag `--nlp-backend` allows explicit selection

**Risk 3**: Haiku API failures
- Mitigation: Only used for 40-70% confidence candidates (minority)
- Mitigation: Graceful degradation (continue vacuum without LLM)
- Mitigation: API failure keeps original NLP confidence

**Risk 4**: M1 Pro 16GB memory constraints
- Mitigation: all-MiniLM-L6-v2 only 80MB (tiny model)
- Mitigation: Embedding cache pre-computes PRP embeddings once
- Mitigation: Process docs in batches if needed

**Risk 5**: Slow first run (embedding generation)
- Mitigation: Cache embeddings to `.ce/vacuum-embeddings.pkl`
- Mitigation: Subsequent runs use cache (95% faster)
- Mitigation: Show progress bar for first-run embedding generation

## Dependencies

**Required (stdlib only)**:
- difflib, pathlib, re, typing

**Optional (NLP tier 1)**:
- sentence-transformers (80MB model, pre-trained)
- torch (backend for sentence-transformers)

**Optional (NLP tier 2)**:
- scikit-learn (TF-IDF vectorizer)

**Optional (LLM)**:
- anthropic (Haiku API, batch processing)

**Testing**:
- pytest, existing test infrastructure

**Installation**:
```bash
# Minimal (difflib only, no NLP)
uv sync

# With sklearn (TF-IDF)
uv add scikit-learn

# Full NLP (sentence-transformers)
uv add sentence-transformers
```

## Documentation Updates

- `CLAUDE.md`: Add vacuum NLP backend documentation
- `tools/ce/vacuum.py`: Update --help text with --nlp-backend flag
- `tools/ce/nlp_utils.py`: Comprehensive docstrings for NLP foundation
- `.serena/memories/vacuum-nlp-strategy.md`: Document NLP strategy patterns

## Future Enhancements

**Phase 6: Misplaced Docs Detection** (HIGH PRIORITY)
- Detect docs in wrong directories using NLP semantic analysis
- Suggest moves to correct locations within defined domains:
  - PRPs/ → feature-requests/ or executed/
  - .serena/memories/ → categorize by type (architecture, patterns, tools)
  - examples/ → organize by topic (templates, guides, patterns)
  - .claude/ → settings vs commands vs documentation
- Use semantic similarity to find correct destination
- Report: "Doc X should move to Y (confidence Z%, reason: semantic match with docs in Y)"
- Integration with vacuum: `uv run ce vacuum --check-placement`

**Phase 7: Duplicate PRP Detection**
- Detect multiple PRPs implementing same feature (semantic similarity)
- Flag for consolidation or archival

**Phase 8: Obsolete Examples Detection**
- Detect examples superseded by framework changes
- Use semantic similarity against latest framework patterns

**Phase 9: Auto-Archive Mode**
- Instead of delete, move to archived/ subdirectory
- Preserve history while cleaning active workspace
- CLI flag: `uv run ce vacuum --archive` (vs `--execute`)
