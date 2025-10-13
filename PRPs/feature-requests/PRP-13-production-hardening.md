---
prp_id: PRP-13
feature_name: Production Hardening & Comprehensive Documentation
status: partial
created: 2025-01-13
updated: 2025-01-13
last_updated: "2025-01-13T20:45:00Z"
complexity: high
estimated_hours: 15-25
dependencies: [PRP-1, PRP-2, PRP-3, PRP-4, PRP-5, PRP-6, PRP-7, PRP-8, PRP-9, PRP-10, PRP-11, PRP-12]
updated_by: execute-prp-command
context_sync:
  ce_updated: true
  serena_updated: false
implementation_notes: |
  Phases 1-3 and partial Phase 5 completed:
  - ✅ Phase 1: Error recovery (retry + circuit breaker) with 15 passing tests
  - ✅ Phase 2: Structured logging & metrics with 26 passing tests
  - ✅ Phase 3: Profiling utilities (caching, timing, monitoring)
  - ✅ Phase 5 (partial): Metrics CLI command
  - ⏳ Phase 4: Comprehensive documentation (deferred)
  - ⏳ Phase 5 (remaining): Model.md sync (deferred)
---

# Production Hardening & Comprehensive Documentation

## 1. TL;DR

**Objective**: Production-ready system with error recovery, monitoring, optimization, and complete documentation

**What**: Retry logic + circuit breaker + structured logging + metrics + deployment guides + API docs + Model.md sync

**Why**: Production systems require robustness, observability, and maintainability for reliable operation

**Effort**: High (15-25 hours) - Error recovery, monitoring, optimization, comprehensive docs

**Dependencies**: All previous PRPs (1-12) - Final integration and hardening phase

## 2. Context

### Background

Current state: Context Engineering Management System MVP complete (PRPs 1-12 executed). System functional but lacks production-grade features:
- ❌ No retry logic for transient failures (network errors, API rate limits)
- ❌ No circuit breaker for cascading failures
- ❌ Logging inconsistent (print statements vs logger)
- ❌ No metrics collection (success rates, timing data)
- ❌ Documentation scattered and incomplete
- ❌ Model.md out of sync with implementation

Target state: Enterprise-grade system ready for production deployment with 85%+ first-pass success rate.

### Problem

**Reliability Issues**:
1. **Transient failures**: Network errors cause PRP execution failures (no retry)
2. **Cascading failures**: MCP server downtime breaks entire pipeline (no circuit breaker)
3. **Silent failures**: Errors not logged properly (troubleshooting difficult)
4. **No observability**: Can't track success rates, performance metrics

**Documentation Gaps**:
1. **Deployment**: No installation guide for new users
2. **Troubleshooting**: Common errors undocumented
3. **API reference**: Function signatures not documented
4. **Model sync**: Model.md shows planned features, not actual implementation

### Solution

**Production Hardening Architecture**:

```
┌─────────────────────────────────────────┐
│         Error Recovery Layer            │
│  ┌─────────────┐    ┌───────────────┐  │
│  │ Retry Logic │    │Circuit Breaker│  │
│  │  (backoff)  │    │  (MCP guard)  │  │
│  └─────────────┘    └───────────────┘  │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│      Logging & Monitoring Layer         │
│  ┌──────────────┐  ┌─────────────────┐ │
│  │ Structured   │  │ Metrics         │ │
│  │ Logging      │  │ Collection      │ │
│  │ (JSON)       │  │ (success rates) │ │
│  └──────────────┘  └─────────────────┘ │
└─────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────┐
│         Documentation Layer             │
│  ┌──────────┐ ┌─────────┐ ┌──────────┐ │
│  │Deployment│ │Troublesh│ │API Docs  │ │
│  │  Guide   │ │ -ooting │ │          │ │
│  └──────────┘ └─────────┘ └──────────┘ │
└─────────────────────────────────────────┘
```

**Key Components**:
- Retry with exponential backoff (transient errors)
- Circuit breaker (prevent cascading failures)
- Structured logging (JSON format for parsing)
- Metrics collection (track performance targets)
- Deployment guide (installation → configuration)
- Troubleshooting guide (common errors → solutions)
- API documentation (comprehensive docstrings)
- Model.md sync (✅ vs 🔜 status)

**Benefits**:
- ✅ Resilience: Automatic recovery from transient failures
- ✅ Observability: Structured logs enable monitoring
- ✅ Metrics: Track success rates (85%/97% targets)
- ✅ Maintainability: Complete documentation reduces onboarding time
- ✅ Production-ready: Passes deployment checklist

### Impact

- **Reliability**: 95%+ uptime with automatic error recovery
- **Observability**: Structured logs enable real-time monitoring
- **Quality**: Metrics tracking ensures performance targets met
- **Adoption**: Complete docs reduce friction for new users
- **Confidence**: Production checklist validates readiness

### Constraints and Considerations

**Design Constraints**:
- Lightweight monitoring (structured logs, not full telemetry stack)
- Stdlib-first (avoid heavy dependencies like structlog if possible)
- Graceful degradation (log failures don't break system)
- Security-first (no secrets in logs)

**Integration Points**:
- All modules (error recovery, logging)
- MCP adapters (circuit breaker)
- CLI commands (metrics output)
- Documentation (deployment, troubleshooting, API)
- Model.md (sync with implementation status)

**Performance Targets** (from Model.md):
- First-pass success rate: 85%
- Second-pass success rate: 97%
- Self-healing success rate: 92%
- Production-ready rate: 94%
- Speed improvement: 10-24x vs manual

**Gotchas**:
- Retry logic must handle idempotent operations only (avoid duplicate side effects)
- Circuit breaker state must persist across executions
- Structured logging adds overhead (~5-10ms per log call)
- Metrics collection must not slow down execution significantly

### Documentation References

**Error Recovery**:
- [Exponential Backoff](https://en.wikipedia.org/wiki/Exponential_backoff)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Tenacity (retry library)](https://tenacity.readthedocs.io/)

**Logging & Monitoring**:
- [Python logging HOWTO](https://docs.python.org/3/howto/logging.html)
- [Structured Logging Best Practices](https://www.loggly.com/ultimate-guide/python-logging-basics/)
- [JSON Logging](https://github.com/madzak/python-json-logger)

**Performance**:
- [cProfile Documentation](https://docs.python.org/3/library/profile.html)
- [Python Performance Tips](https://wiki.python.org/moin/PythonSpeed/PerformanceTips)

## 3. Implementation Steps

### Phase 1: Error Recovery Infrastructure (4-5 hours)

**Goal**: Implement retry logic and circuit breaker for resilient execution

**Approach**: Decorator-based retry, stateful circuit breaker

**Files to Create**:
- `tools/ce/resilience.py` - Retry and circuit breaker implementations

**Files to Modify**:
- `tools/ce/mcp_adapter.py` - Add retry/circuit breaker to MCP calls
- `tools/ce/execute.py` - Add retry to validation loops

**Key Functions**:

```python
# tools/ce/resilience.py
import time
import functools
from typing import Callable, Any, Type, Tuple
from datetime import datetime, timedelta


def retry_with_backoff(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """Retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay in seconds (default: 60.0)
        exponential_base: Backoff multiplier (default: 2.0)
        exceptions: Tuple of exception types to retry (default: all)

    Returns:
        Decorator function

    Example:
        @retry_with_backoff(max_attempts=5, base_delay=2.0)
        def fetch_data():
            return api.get("/data")

    Note: Only retries on specified exceptions. Non-retryable errors propagate immediately.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        # Final attempt failed - propagate with context
                        raise RuntimeError(
                            f"Failed after {max_attempts} attempts: {func.__name__}\n"
                            f"Last error: {str(e)}\n"
                            f"🔧 Troubleshooting: Check network connectivity, API rate limits"
                        ) from e

                    # Calculate backoff delay (exponential with max cap)
                    delay = min(base_delay * (exponential_base ** attempt), max_delay)
                    time.sleep(delay)

            # Should never reach here, but satisfy type checker
            raise last_exception

        return wrapper
    return decorator


class CircuitBreaker:
    """Circuit breaker for preventing cascading failures.

    State machine: CLOSED → OPEN → HALF_OPEN → CLOSED
    - CLOSED: Normal operation, requests pass through
    - OPEN: Failure threshold exceeded, requests fail fast
    - HALF_OPEN: Testing recovery, limited requests pass through

    Example:
        breaker = CircuitBreaker(name="serena-mcp", failure_threshold=5)

        @breaker.call
        def call_serena():
            return serena.read_file("test.py")

    Attributes:
        state: Current circuit state (closed/open/half_open)
        failure_count: Consecutive failure count
        last_failure_time: Timestamp of last failure
    """

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_max_calls: int = 3
    ):
        """Initialize circuit breaker.

        Args:
            name: Circuit breaker identifier
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds to wait before half-open attempt
            half_open_max_calls: Max calls in half-open state
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls

        # State
        self.state = "closed"  # closed, open, half_open
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None

    def call(self, func: Callable) -> Callable:
        """Decorator to protect function with circuit breaker.

        Args:
            func: Function to protect

        Returns:
            Protected function

        Raises:
            CircuitBreakerOpenError: If circuit is open
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Check circuit state
            if self.state == "open":
                if self._should_attempt_reset():
                    self._transition_to_half_open()
                else:
                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN\n"
                        f"Failures: {self.failure_count}/{self.failure_threshold}\n"
                        f"🔧 Troubleshooting: Wait {self.recovery_timeout}s or check service health"
                    )

            # Execute function
            try:
                result = func(*args, **kwargs)
                self._on_success()
                return result
            except Exception as e:
                self._on_failure()
                raise

        return wrapper

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False

        elapsed = (datetime.now() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

    def _transition_to_half_open(self):
        """Transition from open to half-open state."""
        self.state = "half_open"
        self.half_open_calls = 0

    def _on_success(self):
        """Handle successful call."""
        if self.state == "half_open":
            self.success_count += 1
            if self.success_count >= self.half_open_max_calls:
                # Recovered - close circuit
                self.state = "closed"
                self.failure_count = 0
                self.success_count = 0
        else:
            # Reset failure count on success in closed state
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == "half_open":
            # Failed in half-open - reopen circuit
            self.state = "open"
            self.success_count = 0
        elif self.failure_count >= self.failure_threshold:
            # Threshold exceeded - open circuit
            self.state = "open"


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
```

**Integration Example** (tools/ce/mcp_adapter.py):

```python
# Add circuit breaker for MCP calls
serena_breaker = CircuitBreaker(name="serena-mcp", failure_threshold=5)

@retry_with_backoff(max_attempts=3, base_delay=1.0)
@serena_breaker.call
def read_file_with_mcp(relative_path: str) -> str:
    """Read file via Serena MCP with retry and circuit breaker."""
    serena = _import_serena_mcp()
    return serena.read_file(relative_path=relative_path)
```

**Validation Command**: `uv run pytest tools/tests/test_resilience.py -v`

**Checkpoint**: `git add tools/ce/resilience.py && git commit -m "feat(PRP-13): add retry and circuit breaker"`

---

### Phase 2: Structured Logging & Metrics (4-5 hours)

**Goal**: Implement JSON logging and metrics collection for observability

**Approach**: Python stdlib logging with JSON formatter, metrics dict collection

**Files to Create**:
- `tools/ce/logging_config.py` - Logging configuration
- `tools/ce/metrics.py` - Metrics collection framework

**Files to Modify**:
- All `tools/ce/*.py` modules - Replace print statements with logger calls
- `tools/ce/execute.py` - Add metrics collection

**Key Functions**:

```python
# tools/ce/logging_config.py
import logging
import json
import sys
from typing import Dict, Any


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging.

    Outputs logs in JSON format for machine parsing.

    Example output:
        {"timestamp": "2025-01-13T10:30:45", "level": "INFO",
         "message": "prp.execution.started", "prp_id": "PRP-003"}
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.

        Args:
            record: Log record to format

        Returns:
            JSON string
        """
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Add extra fields from record
        if hasattr(record, "prp_id"):
            log_data["prp_id"] = record.prp_id
        if hasattr(record, "phase"):
            log_data["phase"] = record.phase
        if hasattr(record, "duration"):
            log_data["duration"] = record.duration

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_logging(
    level: str = "INFO",
    json_output: bool = False,
    log_file: str = None
) -> logging.Logger:
    """Setup application logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        json_output: If True, use JSON formatter
        log_file: Optional file path for file logging

    Returns:
        Configured root logger

    Example:
        setup_logging(level="DEBUG", json_output=True)
        logger = logging.getLogger(__name__)
        logger.info("prp.started", extra={"prp_id": "PRP-003"})
    """
    # Get root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))

    # Remove existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler(sys.stderr)
    if json_output:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
    logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(JSONFormatter())
        logger.addHandler(file_handler)

    return logger


# tools/ce/metrics.py
from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path


class MetricsCollector:
    """Collect and persist performance metrics.

    Tracks success rates, timing data, and validation results.

    Example:
        metrics = MetricsCollector()
        metrics.record_prp_execution(
            prp_id="PRP-003",
            success=True,
            duration=1200.5,
            first_pass=True
        )
        metrics.save()
    """

    def __init__(self, metrics_file: str = "metrics.json"):
        """Initialize metrics collector.

        Args:
            metrics_file: Path to metrics JSON file
        """
        self.metrics_file = Path(metrics_file)
        self.metrics: Dict[str, Any] = self._load_metrics()

    def _load_metrics(self) -> Dict[str, Any]:
        """Load existing metrics from file."""
        if self.metrics_file.exists():
            return json.loads(self.metrics_file.read_text())
        return {
            "prp_executions": [],
            "validation_results": [],
            "performance_stats": {}
        }

    def record_prp_execution(
        self,
        prp_id: str,
        success: bool,
        duration: float,
        first_pass: bool,
        validation_level: int
    ):
        """Record PRP execution metrics.

        Args:
            prp_id: PRP identifier
            success: Whether execution succeeded
            duration: Execution time in seconds
            first_pass: Whether succeeded on first pass
            validation_level: Highest validation level passed
        """
        self.metrics["prp_executions"].append({
            "prp_id": prp_id,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "duration": duration,
            "first_pass": first_pass,
            "validation_level": validation_level
        })

    def calculate_success_rates(self) -> Dict[str, float]:
        """Calculate success rate metrics.

        Returns:
            Dict with first_pass_rate, second_pass_rate, overall_rate
        """
        executions = self.metrics["prp_executions"]
        if not executions:
            return {"first_pass_rate": 0.0, "second_pass_rate": 0.0, "overall_rate": 0.0}

        total = len(executions)
        first_pass = sum(1 for e in executions if e["first_pass"])
        successful = sum(1 for e in executions if e["success"])

        return {
            "first_pass_rate": (first_pass / total) * 100,
            "second_pass_rate": (successful / total) * 100,
            "overall_rate": (successful / total) * 100,
            "total_executions": total
        }

    def save(self):
        """Persist metrics to file."""
        self.metrics_file.write_text(json.dumps(self.metrics, indent=2))
```

**Validation Command**: `uv run pytest tools/tests/test_logging.py tools/tests/test_metrics.py -v`

**Checkpoint**: `git add tools/ce/logging_config.py tools/ce/metrics.py && git commit -m "feat(PRP-13): add structured logging and metrics"`

---

### Phase 3: Performance Optimization (3-4 hours)

**Goal**: Profile bottlenecks and optimize critical paths

**Approach**: cProfile analysis, caching, token optimization

**Files to Create**:
- `tools/ce/profiling.py` - Profiling utilities

**Files to Modify**:
- `tools/ce/execute.py` - Add caching for repeated operations
- `tools/ce/generate.py` - Token usage optimization

**Key Functions**:

```python
# tools/ce/profiling.py
import cProfile
import pstats
import io
from typing import Callable, Any
import functools


def profile_function(func: Callable) -> Callable:
    """Decorator to profile function execution.

    Args:
        func: Function to profile

    Returns:
        Wrapped function that prints profile stats

    Example:
        @profile_function
        def slow_function():
            # ... expensive operations ...
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        profiler = cProfile.Profile()
        profiler.enable()

        result = func(*args, **kwargs)

        profiler.disable()

        # Print stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 functions

        print(f"\n🔍 Profile for {func.__name__}:")
        print(stream.getvalue())

        return result

    return wrapper


def cache_result(ttl_seconds: int = 300):
    """Decorator to cache function results with TTL.

    Args:
        ttl_seconds: Time-to-live in seconds

    Returns:
        Decorator function

    Example:
        @cache_result(ttl_seconds=600)
        def expensive_computation():
            return complex_calculation()
    """
    from datetime import datetime, timedelta

    cache = {}

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key
            cache_key = (args, tuple(sorted(kwargs.items())))

            # Check cache
            if cache_key in cache:
                result, timestamp = cache[cache_key]
                if datetime.now() - timestamp < timedelta(seconds=ttl_seconds):
                    return result

            # Compute and cache
            result = func(*args, **kwargs)
            cache[cache_key] = (result, datetime.now())

            return result

        return wrapper
    return decorator
```

**Optimization Areas**:
- Cache Serena MCP search results (same patterns)
- Cache Context7 documentation (same libraries)
- Reduce token usage in LLM calls (compress prompts)
- Batch file operations (reduce I/O)

**Validation Command**: `uv run python -m cProfile -o profile.stats tools/ce/__main__.py execute PRPs/test.md`

**Checkpoint**: `git add tools/ce/profiling.py && git commit -m "feat(PRP-13): add profiling and caching"`

---

### Phase 4: Comprehensive Documentation (4-6 hours)

**Goal**: Create complete deployment, troubleshooting, and API documentation

**Approach**: Structured docs with examples, decision trees, reference material

**Files to Create**:
- `docs/DEPLOYMENT.md` - Installation and configuration guide
- `docs/TROUBLESHOOTING.md` - Common errors and solutions
- `docs/API_REFERENCE.md` - Complete API documentation
- `docs/MCP_INTEGRATION.md` - MCP server setup guide

**Files to Modify**:
- All `tools/ce/*.py` modules - Add comprehensive docstrings
- `README.md` - Update with quick start guide
- `CLAUDE.md` - Sync with new features

**Documentation Structure**:

**DEPLOYMENT.md**:
```markdown
# Deployment Guide

## Prerequisites
- Python 3.10+
- UV package manager
- Git 2.30+
- Claude Code with MCP support

## Installation

### 1. Clone Repository
\`\`\`bash
git clone <repo-url>
cd ctx-eng-plus
\`\`\`

### 2. Setup UV Environment
\`\`\`bash
cd tools
uv venv
source .venv/bin/activate  # Unix/macOS
uv sync
\`\`\`

### 3. Configure MCP Servers
... (Serena, Context7, Sequential Thinking setup)

### 4. Verify Installation
\`\`\`bash
uv run ce --help
uv run ce validate --level 1
\`\`\`

## Configuration

### Environment Variables
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `METRICS_FILE`: Path to metrics file (default: metrics.json)

### Settings File
`.claude/settings.local.json` configuration...

## Production Checklist
- [ ] All tests pass (uv run pytest tests/ -v)
- [ ] Validation gates pass (L1-L4)
- [ ] MCP servers operational
- [ ] Metrics collection enabled
- [ ] Logging configured
- [ ] Documentation reviewed
```

**TROUBLESHOOTING.md**:
```markdown
# Troubleshooting Guide

## Common Errors

### MCP Server Connection Failed
**Symptom**: `Error: serena MCP not available`
**Cause**: Serena MCP server not running or misconfigured
**Solution**:
1. Check MCP server status: `ce context health`
2. Restart MCP servers in Claude Code
3. Verify `.claude/settings.local.json` configuration

### Validation Loop Timeout
**Symptom**: `TimeoutError: Command timed out after 60s`
**Cause**: Test suite taking too long
**Solution**:
1. Increase timeout: Edit `tools/ce/core.py` run_cmd timeout
2. Run tests selectively: `pytest tests/unit/ -v`
3. Profile slow tests: `pytest --durations=10`

... (more common errors)

## Decision Tree

\`\`\`
Error occurred?
├── MCP related?
│   ├── Serena: Check server status, restart
│   └── Context7: Verify API key, check connectivity
├── Validation failed?
│   ├── L1 (syntax): Run linter, check markdown
│   ├── L2 (tests): Fix failing tests
│   ├── L3 (integration): Check dependencies
│   └── L4 (pattern): Review EXAMPLES section
└── Performance issue?
    ├── Profile execution: Use profiling tools
    └── Check metrics: Review success rates
\`\`\`
```

**API_REFERENCE.md**:
```markdown
# API Reference

## Core Module (tools/ce/core.py)

### run_cmd
\`\`\`python
def run_cmd(
    cmd: str,
    cwd: Optional[str] = None,
    timeout: int = 60,
    capture_output: bool = True
) -> Dict[str, Any]
\`\`\`

Execute shell command with timeout and error handling.

**Parameters**:
- `cmd`: Shell command to execute
- `cwd`: Working directory (default: current)
- `timeout`: Command timeout in seconds
- `capture_output`: Whether to capture stdout/stderr

**Returns**:
Dict with: success, stdout, stderr, exit_code, duration

**Raises**:
- `TimeoutError`: If command exceeds timeout
- `RuntimeError`: If command execution fails

... (all functions documented)
```

**Validation Command**: Manual review of all documentation files

**Checkpoint**: `git add docs/ && git commit -m "docs(PRP-13): add comprehensive documentation"`

---

### Phase 5: Model.md Sync & Final Integration (2-3 hours)

**Goal**: Update Model.md with implementation status and integrate all hardening features

**Approach**: Systematic review of Model.md sections, mark ✅ vs 🔜, add metrics

**Files to Modify**:
- `PRPs/Model.md` - Sync with implementation
- `README.md` - Update with current state
- All modules - Final integration testing

**Model.md Updates**:
- Mark completed features: ✅
- Mark pending features: 🔜
- Add actual performance metrics (from metrics.json)
- Update success rate targets with real data
- Document lessons learned

**Final Integration**:
```python
# tools/ce/__main__.py - Add metrics command
@cli.command()
@click.option("--format", type=click.Choice(["text", "json"]), default="text")
def metrics(format):
    """Display system metrics and success rates.

    Example:
        ce metrics
        ce metrics --format json
    """
    from ce.metrics import MetricsCollector

    collector = MetricsCollector()
    rates = collector.calculate_success_rates()

    if format == "json":
        click.echo(json.dumps(rates, indent=2))
    else:
        click.echo("📊 Context Engineering Metrics")
        click.echo(f"  First-pass success rate: {rates['first_pass_rate']:.1f}%")
        click.echo(f"  Second-pass success rate: {rates['second_pass_rate']:.1f}%")
        click.echo(f"  Total executions: {rates['total_executions']}")
```

**Validation Command**: `uv run pytest tools/tests/ -v && uv run ce validate --level all`

**Checkpoint**: `git add PRPs/Model.md README.md && git commit -m "docs(PRP-13): sync Model.md with implementation"`

---

## 4. Validation Gates

### Gate 1: Error Recovery Tests Pass

**Command**: `uv run pytest tools/tests/test_resilience.py -v`

**Success Criteria**:
- Retry decorator works (exponential backoff correct)
- Circuit breaker state transitions (closed → open → half_open → closed)
- Integration with MCP adapter (retries on transient errors)
- Idempotency verified (no duplicate side effects)

### Gate 2: Logging & Metrics Functional

**Command**: `uv run pytest tools/tests/test_logging.py tools/tests/test_metrics.py -v`

**Success Criteria**:
- JSON logging outputs valid JSON
- Metrics collection records execution data
- Success rates calculated correctly
- Log files rotate properly (if configured)

### Gate 3: Performance Targets Met

**Command**: `uv run python -m cProfile -o profile.stats tools/ce/__main__.py execute PRPs/test.md && python -c "import pstats; stats = pstats.Stats('profile.stats'); stats.sort_stats('cumulative'); stats.print_stats(20)"`

**Success Criteria**:
- No single function >10% of total time
- Caching reduces repeated operations by 50%+
- Token usage optimized (measure before/after)
- Overall execution time acceptable (<5min for medium PRP)

### Gate 4: Documentation Complete

**Command**: Manual review of all documentation files

**Success Criteria**:
- DEPLOYMENT.md covers installation → verification
- TROUBLESHOOTING.md includes 10+ common errors
- API_REFERENCE.md documents all public functions
- MCP_INTEGRATION.md explains server setup
- README.md up to date

### Gate 5: Production Checklist Validated

**Command**: `uv run ce validate --level all && uv run pytest tools/tests/ --cov=ce --cov-report=term-missing`

**Success Criteria**:
- All validation levels pass (L1-L4)
- Test coverage ≥80% overall
- No critical TODOs or FIXMEs in code
- Model.md synchronized with implementation
- Metrics show 85%+ first-pass success rate

---

## 5. Testing Strategy

### Test Framework

pytest with unittest.mock, cProfile for performance

### Test Command

```bash
# All tests
uv run pytest tools/tests/ -v

# With coverage
uv run pytest tools/tests/ --cov=ce --cov-report=term-missing --cov-report=html

# Performance tests
uv run pytest tools/tests/test_performance.py -v --benchmark-only

# Integration tests
uv run pytest tools/tests/test_integration.py -v
```

### Coverage Requirements

- Error recovery: 90%+
- Logging: 85%+
- Metrics: 85%+
- Overall: 80%+

### Test Types

1. **Unit tests**: Retry logic, circuit breaker, logging, metrics
2. **Integration tests**: Error recovery with real MCP calls (mocked at boundary)
3. **Performance tests**: Profiling, caching effectiveness
4. **E2E tests**: Full PRP execution with metrics collection

---

## 6. Rollout Plan

### Phase 1: Development (Week 1)

1. Implement error recovery (Phase 1)
2. Add structured logging and metrics (Phase 2)
3. Profile and optimize (Phase 3)

### Phase 2: Documentation (Week 2)

1. Write comprehensive docs (Phase 4)
2. Sync Model.md (Phase 5)
3. Create production checklist

### Phase 3: Validation & Deployment

1. Run full test suite (all validation gates)
2. Measure performance against targets
3. Deploy to production environment
4. Monitor metrics for first week

### Success Metrics

- ✅ 85%+ first-pass success rate
- ✅ 97%+ second-pass success rate
- ✅ <5% error rate with retry/circuit breaker
- ✅ All documentation complete
- ✅ Production checklist validated

---

## Research Findings

### Serena Codebase Analysis

**Existing Error Handling** (from tools/ce/core.py):
- ✅ Clear exception raising (no fishy fallbacks)
- ✅ Troubleshooting guidance in error messages
- ✅ Structured result dicts (success, errors, duration)

**Logging Patterns** (from tools/ce/prp.py, tools/ce/generate.py):
- ✅ Python stdlib logging (logger = logging.getLogger(__name__))
- ❌ Inconsistent usage (mix of print and logger)
- ❌ No structured logging (plain text format)

**Performance Patterns**:
- ✅ Duration tracking in run_cmd
- ❌ No caching for repeated operations
- ❌ No profiling instrumentation

### Documentation Sources

**Error Recovery**:
- Exponential backoff algorithm (Wikipedia)
- Circuit breaker pattern (Martin Fowler)
- Tenacity library (Python retry library)

**Logging**:
- Python logging HOWTO (official docs)
- Structured logging best practices
- JSON logging (python-json-logger)

**Performance**:
- cProfile documentation
- Python performance tips

### Key Insights

1. **Lightweight approach**: Use stdlib logging (not structlog) to avoid dependencies
2. **Fail fast**: Circuit breaker prevents cascading failures
3. **Observable**: JSON logs enable monitoring without heavy infrastructure
4. **Pragmatic metrics**: Track what matters (success rates, not everything)
5. **Documentation-first**: Good docs reduce support burden

---

**Confidence Score**: 9/10

**Reasoning**:
- Clear requirements from Model.md performance targets
- Well-defined phases with executable validation gates
- Builds on proven patterns (retry, circuit breaker are standard)
- Risk: Logging overhead might slow execution (mitigation: measure and optimize)
- Risk: Documentation takes longer than estimated (mitigation: focus on essential docs first)

**Success Indicators**:
- System achieves 85%/97% success rate targets
- Error recovery handles transient failures automatically
- Metrics tracking enables continuous improvement
- Documentation reduces onboarding time to <1 hour
- Production deployment validated with checklist
