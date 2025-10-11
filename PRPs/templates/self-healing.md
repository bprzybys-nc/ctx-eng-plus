# PRP Template: Self-Healing Edition

**Use Case:** Complex features requiring extensive validation and checkpointing

---

## GOAL
[Clear, single objective statement]

---

## WHY
[Business value and user impact justification in 1-3 sentences]

---

## WHAT (Success Criteria)
- [ ] Specific measurable criterion 1
- [ ] Specific measurable criterion 2
- [ ] Specific measurable criterion 3
- [ ] Specific measurable criterion 4

---

## SERENA PRE-FLIGHT CHECKS
# Execute BEFORE starting implementation
1. Compilation check: `npm run build` (verify clean baseline)
2. Serena onboarding: `onboarding()` (sync with codebase)
3. Latest checkpoint: `read_memory("checkpoint-latest")` (restore context)
4. Git status verification: `git diff --stat` (confirm clean working tree)

---

## CONTEXT (Serena-Enhanced)

### Project Structure
- [Use Serena list_symbols() output to map relevant modules]
- Key files and their roles
- Module dependencies and relationships

### Existing Patterns
- [Use find_symbol() to locate similar implementations]
- Reference code with file paths and line numbers
- Design system patterns to follow

### Library Documentation
- [Use Context7 MCP for version-specific documentation]
- Critical API references with section numbers
- Known gotchas and breaking changes

### Validation Commands
**Syntax:**
```bash
npm run type-check  # TypeScript type validation
npm run lint        # ESLint style checks
```

**Tests:**
```bash
npm test -- --coverage --verbose  # Jest unit tests
```

**Integration:**
```bash
curl -X POST http://localhost:3000/api/endpoint \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

---

## IMPLEMENTATION BLUEPRINT

### Phase 1: Type Definitions
**Goal:** Define all interfaces and types
**Approach:** Symbol-first development
**Validation:** `npm run type-check` succeeds

**Pseudocode:**
```typescript
interface FeatureConfig {
  id: string;
  name: string;
  settings: Record<string, unknown>;
}

type FeatureStatus = 'active' | 'inactive' | 'pending';
```

**Checkpoint:** After type definitions complete and validated

### Phase 2: Core Logic
**Goal:** Implement business logic
**Approach:** TDD with unit tests first
**Validation:** Unit tests pass with > 80% coverage

**Pseudocode:**
```typescript
async function processFeature(config: FeatureConfig): Promise<Result> {
  // 1. Validate input
  // 2. Transform data
  // 3. Execute business logic
  // 4. Return result
}
```

**Checkpoint:** After core logic complete and unit tests pass

### Phase 3: Integration
**Goal:** Wire up components and external dependencies
**Approach:** Integration tests validate connections
**Validation:** API endpoints respond correctly

**Pseudocode:**
```typescript
app.post('/api/feature', async (req, res) => {
  const config = parseConfig(req.body);
  const result = await processFeature(config);
  res.json(result);
});
```

**Checkpoint:** After integration complete and all tests pass

### Phase 4: Error Handling & Edge Cases
**Goal:** Robust error handling
**Approach:** Test failure scenarios
**Validation:** Error cases handled gracefully

**Checkpoint:** Final checkpoint before code review

---

## VALIDATION LOOPS

### Level 1: Syntax & Style
```bash
# Fast feedback (< 10 seconds)
npm run type-check && npm run lint && npm run format:check
```
**Expected:** All checks pass with no errors
**On Failure:** Auto-fix formatting, resolve type errors, re-run

### Level 2: Unit Tests
```bash
# Logic validation (30-60 seconds)
npm test -- --coverage --verbose
```
**Expected:** 100% tests pass, coverage > 80%
**On Failure:**
1. Analyze test failure message
2. Use Sequential Thinking to identify root cause
3. Apply fix to implementation
4. Re-run tests
5. Repeat until pass

### Level 3: Integration Tests
```bash
# System validation (1-2 minutes)
# Start test server
npm run dev:test &
sleep 5

# Execute integration tests
npm run test:integration

# Verify with manual API call
curl -X POST http://localhost:3000/api/feature \
  -H "Content-Type: application/json" \
  -d @test-fixtures/valid-request.json
```
**Expected:** All endpoints return expected responses, data persists correctly
**On Failure:**
1. Check server logs: `tail -f logs/dev.log`
2. Verify environment: `npm run env:check`
3. Debug with Serena execute_shell_command
4. Fix issues systematically
5. Re-run integration tests

---

## SELF-HEALING GATES

### Gate 1: After Type Definitions
**Actions:**
1. Run `npm run type-check`
2. If errors: use `find_symbol()` to locate root cause
3. Fix at source (interface/type definition level)
4. Re-run type-check
5. Create checkpoint: `write_memory("checkpoint-types", "Type definitions complete and validated")`

### Gate 2: After Core Logic
**Actions:**
1. Run unit tests: `npm test`
2. If failures: analyze with Sequential Thinking MCP
3. Apply fix to implementation (not tests, unless test is wrong)
4. Re-test until pass
5. Create checkpoint: `write_memory("checkpoint-logic", "Core logic implemented with N tests passing")`

### Gate 3: After Integration
**Actions:**
1. Run full test suite: `npm run test:all`
2. Run integration tests: `npm run test:integration`
3. If failures: use Serena execute_shell_command for debugging
4. Fix issues systematically (check logs, verify config, test dependencies)
5. Re-validate until all pass
6. Final checkpoint: `write_memory("checkpoint-final", "Feature complete, all tests passing")`

---

## CONTEXT SYNCHRONIZATION PROTOCOL

### During Implementation
- **Every 5 file changes:** Sync context with `sync_context()`
- **After each validation gate:** Create checkpoint
- **On any error:** Analyze drift, prune outdated context if needed

### On Completion
1. Final validation: `npm run check-all`
2. Create detailed checkpoint with summary
3. Update Serena memories with learnings: `write_memory("learnings-[feature]", "...")`
4. Git commit with checkpoint reference in message
5. Create PR if applicable

---

## CONFIDENCE SCORING
**Scale:** 1-10 based on validation passes and error count

- **Initial estimate:** 6/10 (untested, based on design)
- **After unit tests pass:** 8/10 (core logic validated)
- **After integration tests pass:** 9/10 (full system validated)
- **Production-ready threshold:** 9/10 minimum

**Current Confidence:** [Update during execution]

---

## COMPLETION CHECKLIST
- [ ] All validation gates passed
- [ ] Compilation successful (no type errors)
- [ ] Tests passing (coverage > 80%)
- [ ] Integration tests validated
- [ ] Error handling tested
- [ ] Checkpoint created in Serena
- [ ] Memories updated with learnings
- [ ] Git commit completed
- [ ] PR created (if applicable)
- [ ] Documentation updated
