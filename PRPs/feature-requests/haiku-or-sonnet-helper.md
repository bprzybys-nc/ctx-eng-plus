## NL-Optimized Model Selection Command for Claude Code 2.0

### Primary Orchestrator Configuration

```bash
# Start session with Sonnet 4.5 as orchestrator
claude --model claude-sonnet-4-5-20251001
```

### Subagent Model Selection (Parallel Processing)

**In `.claude/agents/<agent-name>.md`:**

```yaml
---
name: executor-worker
model: haiku
allowed_tools: ["Read", "Write", "Grep", "Bash"]
---
Execute implementation tasks from provided plan.
Focus: speed, accuracy, isolated context.
```

### Decision Rule (Copy-Paste Ready)

```markdown
# Model Selection Rule for Subagent Tasks

## Orchestrator: Sonnet 4.5
- Main session planning
- Architecture decisions
- Task decomposition
- Result aggregation
- Quality verification

## Workers: Haiku 4.5
- Implementation from plan
- Parallel file operations
- Test generation
- Documentation writing
- Code analysis/search
- Simple refactors

## Usage Pattern:
1. Sonnet creates execution plan
2. Spawn Haiku subagents for parallel work
3. Sonnet reviews & integrates results
```

### Inline Session Commands

```bash
# Switch orchestrator model mid-session
/model sonnet

# Create subagent with model override
/agent create executor-1 --model haiku

# Check current configuration
/status
```

### Environment Default (Optional)

```bash
# Set permanent default orchestrator
export ANTHROPIC_MODEL=claude-sonnet-4-5-20251001
```

### Subagent Template (Production-Ready)

```yaml
---
name: parallel-executor
model: haiku  # Forces Haiku 4.5 for cost/speed
allowed_tools: ["Read", "Write", "Bash"]
---
You execute well-defined implementation tasks.
Context: Isolated. Speed: Critical. Cost: Optimized.
Accept detailed plan → implement → return results.
```

### Quick Reference Table

| Task Type | Model | Command |
|-----------|-------|---------|
| **Main orchestration** | Sonnet 4.5 | `claude --model sonnet` |
| **Parallel workers** | Haiku 4.5 | `model: haiku` in agent YAML |
| **Ad-hoc switch** | Any | `/model <alias>` in session |
| **Verify config** | — | `/status` |

### Cost-Optimized Pattern

```
Sonnet 4.5 (orchestrator) → [Haiku worker-1 ‖ Haiku worker-2 ‖ Haiku worker-3] → Sonnet (review)
```

**Result**: 70% cost reduction, 35% faster completion vs Sonnet-only.

### Key Aliases

- `sonnet` = claude-sonnet-4-5-20251001
- `haiku` = claude-haiku-4-5-20251001
- `opusplan` = Opus planning → Sonnet execution (not recommended for parallel workflows)

**For parallel subagent optimization**: Always use `model: haiku` in worker agent definitions while keeping Sonnet 4.5 as your main orchestrator.

# EXPANDED

## Claude Model Selection: Haiku 4.5 vs Sonnet 4.5 in Agent SDK

### Executive Summary

**Haiku 4.5 excels at execution; Sonnet 4.5 excels at planning.** The optimal strategy: use Sonnet 4.5 as orchestrator to plan and coordinate, then spawn Haiku 4.5 subagents for parallel execution. This hybrid approach delivers 35-70% cost savings while maintaining high quality.

### Performance Benchmarks

| Metric | Haiku 4.5 | Sonnet 4.5 | Advantage |
|--------|-----------|------------|-----------|
| **Pricing** | $1/$5 per 1M tokens | $3/$15 per 1M tokens | Haiku: 66% cheaper |
| **Latency** | <200ms | 500-800ms | Haiku: 2-4× faster |
| **SWE-bench** | 73.3% | 77.2% | Sonnet: +3.9% |
| **Computer Use** | 50.7% | ~42% (Sonnet 4) | Haiku: +8.5% |
| **Code Quality** | 7.29 (thinking) | 6.60 (thinking) | Haiku: +0.69 |
| **MMLU Reasoning** | 75-78% | 85-88% | Sonnet: +10% |
| **Context Window** | 200K tokens | 200K tokens | Tie |



### Model Selection Rules



### Core Decision Framework

#### **Use Haiku 4.5 When:**
- **Task is well-defined** with explicit requirements and clear success criteria
- **Execution speed matters**: real-time apps, chat interfaces, high-frequency tool calls
- **Cost optimization**: high-volume operations, parallel subagents, batch processing
- **Pattern-based work**: test generation, documentation, single-file code, style checks
- **Research/exploration**: token-heavy codebase searches with isolated context
- **Following a plan**: when Sonnet provides detailed implementation specs

**Community insight**: "Haiku 4.5 is a rapid and relentless workhorse" ideal for MVPs and execution-heavy workflows.

#### **Use Sonnet 4.5 When:**
- **Planning & architecture**: breaking down ambiguous requirements into actionable steps
- **Complex reasoning**: multi-step logic, architectural decisions, edge case handling
- **High-stakes work**: production refactors, critical debugging, accuracy >95% required
- **Cross-file refactoring**: coordinating changes across multiple modules
- **Orchestration**: managing subagent workflows and task delegation
- **Deep code review**: evaluating logic, design patterns, security implications

**Community insight**: "Sonnet excels at figuring out what needs to be done; Haiku excels at executing it".

### Optimal Patterns for Claude Agent SDK

#### **Pattern 1: Orchestrator + Workers**
```
Sonnet 4.5 (Orchestrator)
├── Plans overall architecture
├── Breaks down complex tasks
└── Spawns Haiku 4.5 subagents:
    ├── Worker 1: Frontend implementation
    ├── Worker 2: Backend API
    └── Worker 3: Test generation
```
**Result**: 35% faster completion, 70% cost reduction vs Sonnet-only.

#### **Pattern 2: Plan → Execute → Verify**
```
1. Sonnet creates detailed plan ($0.50)
2. Haiku executes implementation ($0.30)
3. Sonnet verifies & reviews ($0.10)
Total: $0.90 vs $2.00 Sonnet-only
```
**Result**: 55% cost savings, higher quality than Haiku-only.

#### **Pattern 3: Parallel Specialist Subagents**
```
Sonnet orchestrates:
├── Haiku: Code analysis (parallel)
├── Haiku: Security scan (parallel)
├── Haiku: Documentation (parallel)
└── Sonnet: Aggregate & decide
```
**Result**: 3× faster with isolated contexts preventing bloat.

### Critical Warnings

#### **When Haiku Fails**
- **Without detailed plans**: Haiku misses wiring details and edge cases
- **Complex debugging**: Cannot trace multi-layer root causes reliably
- **Architectural decisions**: Makes shallow plans (~93 lines vs Sonnet's 300+)
- **Critical review**: Accepts flawed assumptions without challenge

**Pro tip**: "If Haiku created a bad plan → Sonnet builds from it → everything fails → restart with Sonnet".

#### **When Sonnet is Overkill**
- **Repetitive tasks**: 3× cost with minimal quality improvement
- **High-volume operations**: Latency bottleneck in real-time systems
- **Simple execution**: Haiku matches Sonnet 4 at 1/3 cost

### SDK Implementation Guidelines

#### **Model Selection in Subagents**

**Via YAML frontmatter** (`.claude/agents/`):
```yaml
---
name: sql-optimizer
model: haiku  # or 'sonnet', 'opus', 'inherit'
allowed_tools: ["Read", "Grep"]
---
You are an SQL optimization expert.
```


**Via Agent SDK** (programmatic):
```typescript
agents: [
  {
    name: 'planner',
    model: 'sonnet',  // orchestrator
    systemPrompt: 'Break down tasks...'
  },
  {
    name: 'executor',
    model: 'haiku',   // worker
    systemPrompt: 'Implement from plan...'
  }
]
```


**Model aliases**: `'sonnet'`, `'haiku'`, `'opus'`, or `'inherit'` (match parent).

#### **Dynamic Model Routing**
```python
def route_task(complexity_score):
    if complexity_score <= 3:
        return "haiku"   # simple tasks
    elif complexity_score <= 6:
        return "sonnet"  # analyze first
    else:
        return "sonnet"  # complex reasoning
```


### Real-World Performance

#### **Case Study: 10,000 Document Analysis**
- **Sonnet only**: $1,800, 5 hours
- **Haiku only**: $360, 1.5 hours, 95% accuracy
- **Hybrid (80% Haiku / 20% Sonnet)**: $378, 1.5 hours, 98% accuracy

**Verdict**: Hybrid approach optimal for quality + speed.

#### **Community Feedback Summary**
- **Haiku praise**: "Balance between speed and quality is impressive" for MVPs; "First appropriately scaled frontier model for agentic tasks"
- **Haiku limitations**: "Accepts flawed assumptions without challenge"; "Can become stubborn in long sessions"
- **Sonnet strength**: "Superior for architecture and complex explorations"; "Catches logical mistakes Haiku misses"
- **Hybrid consensus**: "Use Haiku with Sonnet backup" for best results

### Cost-Benefit Analysis

| Scenario | Recommended Model | Reasoning |
|----------|------------------|-----------|
| **Real-time chatbot** | Haiku 4.5 | Sub-200ms latency required; 3× cheaper at scale |
| **Feature planning** | Sonnet 4.5 | Needs comprehensive 300+ line plans |
| **Parallel code analysis** | Haiku 4.5 workers | 70% cost reduction, isolated contexts |
| **Production refactor** | Sonnet 4.5 | Accuracy >95% non-negotiable |
| **Test generation** | Haiku 4.5 | Pattern-based, repetitive work |
| **Debugging unknown issue** | Sonnet 4.5 | Multi-layer root cause analysis |
| **10+ subagent teams** | Hybrid | Sonnet orchestrates, Haiku executes |

### Key Takeaways

1. **Cost**: Haiku is 66% cheaper—use for high-volume work
2. **Speed**: Haiku is 2-5× faster—critical for real-time apps
3. **Quality**: Sonnet wins reasoning (+10%) but Haiku wins practical code quality in thinking mode (+0.69)
4. **Pattern**: Sonnet plans → Haiku executes → Sonnet verifies = optimal workflow
5. **Accuracy**: Haiku needs detailed plans; fails on ambiguous tasks
6. **Scale**: Haiku enables cost-effective parallel subagent armies

**Final Rule**: "Use Sonnet to figure out WHAT needs to be done; use Haiku to DO it".