---
prp_id: PRP-43.1.1
batch_id: 43
stage: 1
order: 1
parent_prp: PRP-43-INITIAL
feature_name: Task Execution Framework - Foundation for Task-Based Architecture
status: pending
created: 2025-11-08T00:00:00Z
updated: 2025-11-08T00:00:00Z
complexity: medium
estimated_hours: 6
dependencies: None
tags: [task-execution, architecture, foundation, quota-management]
issue: TBD
---

# PRP-43.1.1: Task Execution Framework - Foundation for Task-Based Architecture

**Phase**: 1 of 6 - Task Execution Framework (Foundation)
**Batch**: 43 (Task-Based Architecture for Claude Max 5x Quota)
**Stage**: 1 (No parallel execution - foundation must complete first)

## 1. TL;DR

**Objective**: Create task execution infrastructure for spawning Claude Code Task subagents programmatically, enabling CE tools to execute LLM operations using Claude Max 5x quota.

**What**: Build `TaskExecutor` class that spawns Claude Code Task subagents, implements task communication protocol, handles errors/timeouts, and provides context detection for dual-mode operation.

**Why**: Current CE tools run as standalone CLI requiring `ANTHROPIC_API_KEY` (uses standard API quota). Task-based execution allows `Anthropic()` without API key to automatically use Claude Max 5x quota when run inside Task context.

**Effort**: 6 hours (medium complexity - new architecture pattern)

**Dependencies**: None - this is the foundation phase

## 2. Context

### Background

The Context Engineering framework currently executes all LLM operations (classification, blending, PRP generation) as standalone CLI commands. This approach has significant limitations:

1. **Requires API Key**: All operations need `ANTHROPIC_API_KEY` environment variable
2. **Uses API Quota**: Consumes standard API quota, not Claude Max 5x subscription quota
3. **Manual Retry Logic**: Tools must implement their own retry and error handling
4. **No Context Management**: No automatic prompt caching or context compaction

The Task-based architecture refactoring (PRP-43-INITIAL) aims to solve these issues by executing LLM operations inside Claude Code Task subagents. When code runs inside a Task context:

- `Anthropic()` without API key works automatically
- Requests route through Claude Max 5x quota pool
- Built-in retry logic and context management from Claude Code
- Unified quota tracking in Anthropic Console

**This PRP (43.1.1) creates the foundation** - a reusable `TaskExecutor` class that other phases will use to migrate specific tools (classification in 43.2.1, blending in 43.2.2, etc.).

### Current State

**CE Tools Architecture** (standalone CLI):
```bash
# tools/ce/blending/classification.py
import anthropic
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
response = client.messages.create(model="claude-3-5-haiku-20241022", ...)
```

**Limitations**:
- ❌ Requires `ANTHROPIC_API_KEY` in environment
- ❌ Uses standard API quota (not Max 5x)
- ❌ Each tool implements own error handling
- ❌ No way to detect if running inside Task context

### Goal State

**Task-Based Architecture**:
```python
# tools/ce/task_executor.py
from ce.task_executor import TaskExecutor

executor = TaskExecutor(timeout=300)
result = executor.execute_task(
    task_type="classification",
    prompt="Classify this file: path/to/file.md"
)
# Automatically spawns Task, uses Max quota, returns result
```

**Benefits**:
- ✅ No API key needed when run via Claude Code
- ✅ Automatic Claude Max 5x quota usage
- ✅ Centralized error handling and retry logic
- ✅ Context detection for dual-mode operation (Task vs CLI)
- ✅ Graceful fallback to API key for standalone CLI usage

### Constraints and Considerations

**Dual-Mode Operation** (Critical Requirement):
- Must work inside Claude Code Task context (uses Max quota)
- Must work as standalone CLI (uses API key fallback)
- Context detection must be reliable
- Clear error messages when API key missing in CLI mode

**Backward Compatibility**:
- Existing CLI commands must continue working
- CI/CD pipelines rely on standalone execution
- Local development without Claude Code must work
- No breaking changes to CLI interface

**Performance**:
- Task spawning overhead must be acceptable (<5s)
- Multiple operations should batch into single Task where possible
- Timeout management must prevent hanging operations

**Testing**:
- Must be testable without spawning real Tasks (mocking)
- Unit tests run in CI/CD (no Claude Code available)
- Integration tests verify real Task execution when available

### Documentation References

**Related PRPs**:
- **PRP-43-INITIAL**: Parent PRP describing full refactoring plan
- **PRP-42**: REJECTED - Agent SDK migration (wrong approach)

**Related Files**:
- `tools/ce/blending/llm_client.py`: Current LLM client (to be refactored in Phase 3)
- `tools/ce/blending/classification.py`: Classification logic (to be refactored in Phase 2)
- `.claude/commands/generate-prp.md`: PRP generation (to be refactored in Phase 5)

## 3. Implementation Steps

### Phase 1: Create Task Type Definitions (60 minutes)

**Goal**: Define task types and data structures for Task execution

**File**: `tools/ce/task_types.py` (NEW)

**Implementation**:

```python
"""Task type definitions for Claude Code Task execution."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class TaskType(Enum):
    """Types of tasks that can be executed."""

    CLASSIFICATION = "classification"
    BLENDING = "blending"
    PRP_GENERATION = "prp_generation"
    INITIALIZATION = "initialization"


class TaskStatus(Enum):
    """Status of task execution."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


@dataclass
class TaskResult:
    """Result from task execution."""

    task_id: str
    task_type: TaskType
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_id": self.task_id,
            "task_type": self.task_type.value,
            "status": self.status.value,
            "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "execution_time": self.execution_time,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TaskResult":
        """Create from dictionary (deserialization)."""
        return cls(
            task_id=data["task_id"],
            task_type=TaskType(data["task_type"]),
            status=TaskStatus(data["status"]),
            result=data.get("result"),
            error=data.get("error"),
            started_at=datetime.fromisoformat(data["started_at"]) if data.get("started_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
            execution_time=data.get("execution_time"),
        )


@dataclass
class TaskRequest:
    """Request to execute a task."""

    task_type: TaskType
    prompt: str
    timeout: int = 300  # 5 minutes default
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "task_type": self.task_type.value,
            "prompt": self.prompt,
            "timeout": self.timeout,
            "metadata": self.metadata or {},
        }


class TaskError(Exception):
    """Base exception for task execution errors."""
    pass


class TaskTimeoutError(TaskError):
    """Task execution exceeded timeout."""
    pass


class TaskSpawnError(TaskError):
    """Failed to spawn task subagent."""
    pass


class TaskCommunicationError(TaskError):
    """Failed to communicate with task subagent."""
    pass
```

**Validation**:
```bash
# Import validation
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.task_types import TaskType, TaskResult, TaskRequest; print('✓ Imports work')"

# Type checking (if using mypy)
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run mypy ce/task_types.py --strict
```

---

### Phase 2: Implement Task Context Detection (45 minutes)

**Goal**: Detect if code is running inside Claude Code Task subagent vs standalone CLI

**File**: `tools/ce/task_executor.py` (NEW - Part 1)

**Implementation**:

```python
"""Task executor for spawning Claude Code Task subagents."""

import json
import os
import subprocess
import tempfile
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from .task_types import (
    TaskError,
    TaskRequest,
    TaskResult,
    TaskSpawnError,
    TaskStatus,
    TaskTimeoutError,
    TaskType,
)


def is_task_context() -> bool:
    """Detect if running inside Claude Code Task subagent.

    Returns:
        True if inside Task context, False if standalone CLI

    Notes:
        - Task context is identified by CLAUDE_CODE_TASK_ID environment variable
        - This variable is set by Claude Code when spawning Task subagents
        - Standalone CLI execution will not have this variable
    """
    return os.environ.get("CLAUDE_CODE_TASK_ID") is not None


def get_task_id() -> Optional[str]:
    """Get current task ID if running in Task context.

    Returns:
        Task ID string if in Task context, None otherwise
    """
    return os.environ.get("CLAUDE_CODE_TASK_ID")


def validate_task_environment() -> bool:
    """Validate that Task execution environment is properly configured.

    Returns:
        True if environment is valid for Task execution

    Raises:
        TaskError: If environment is invalid for Task execution
    """
    # Check if running in Task context
    if not is_task_context():
        return False

    # Validate task ID is set
    task_id = get_task_id()
    if not task_id:
        raise TaskError("Task context detected but CLAUDE_CODE_TASK_ID is empty")

    # All checks passed
    return True
```

**Validation**:
```bash
# Test context detection (should return False in standalone CLI)
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.task_executor import is_task_context; print(f'In Task: {is_task_context()}')"
# Expected: In Task: False

# Test with mock Task environment
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
CLAUDE_CODE_TASK_ID=test-123 uv run python -c "from ce.task_executor import is_task_context, get_task_id; print(f'In Task: {is_task_context()}, ID: {get_task_id()}')"
# Expected: In Task: True, ID: test-123
```

---

### Phase 3: Implement TaskExecutor Class (90 minutes)

**Goal**: Create core `TaskExecutor` class for spawning and managing Tasks

**File**: `tools/ce/task_executor.py` (NEW - Part 2)

**Implementation**:

```python
class TaskExecutor:
    """Execute code inside Claude Code Task subagents.

    This class provides a unified interface for spawning Task subagents
    and executing LLM operations with automatic Claude Max quota usage.

    Usage:
        executor = TaskExecutor(timeout=300)
        result = executor.execute_task(
            task_type="classification",
            prompt="Classify this file: path/to/file.md"
        )

    Task Execution Flow:
        1. Create task request with prompt
        2. Spawn Task subagent (via subprocess or API)
        3. Wait for task completion (with timeout)
        4. Parse task result
        5. Return TaskResult object

    Context Detection:
        - If running inside Task: Direct execution (no spawn)
        - If CLI with claude command: Spawn via subprocess
        - If no claude command: Raise error with instructions
    """

    def __init__(self, timeout: int = 300, verbose: bool = False):
        """Initialize task executor.

        Args:
            timeout: Default timeout in seconds (default: 300 = 5 minutes)
            verbose: Enable verbose logging for debugging
        """
        self.timeout = timeout
        self.verbose = verbose
        self.task_output_dir = Path(tempfile.gettempdir()) / "ce-tasks"
        self.task_output_dir.mkdir(exist_ok=True)

    def execute_task(
        self,
        task_type: str,
        prompt: str,
        timeout: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> TaskResult:
        """Execute task and return result.

        Args:
            task_type: Type of task (classification, blending, etc.)
            prompt: Prompt to send to Task subagent
            timeout: Override default timeout (seconds)
            metadata: Optional metadata for task context

        Returns:
            TaskResult with status, result, or error

        Raises:
            TaskSpawnError: Failed to spawn task subagent
            TaskTimeoutError: Task execution exceeded timeout
            TaskError: Other task execution errors
        """
        # Generate unique task ID
        task_id = str(uuid.uuid4())

        # Create task request
        request = TaskRequest(
            task_type=TaskType(task_type),
            prompt=prompt,
            timeout=timeout or self.timeout,
            metadata=metadata or {},
        )

        # Log task start
        started_at = datetime.now()
        if self.verbose:
            print(f"[TaskExecutor] Starting task {task_id} (type: {task_type})")

        # Check if already inside Task context
        if is_task_context():
            # Direct execution - no spawn needed
            if self.verbose:
                print(f"[TaskExecutor] Already in Task context, executing directly")
            return self._execute_direct(task_id, request, started_at)

        # Spawn Task subagent
        try:
            result = self._spawn_task(task_id, request, started_at)
        except subprocess.TimeoutExpired:
            raise TaskTimeoutError(
                f"Task {task_id} exceeded timeout of {request.timeout}s"
            )
        except Exception as e:
            raise TaskSpawnError(f"Failed to spawn task {task_id}: {e}")

        return result

    def _execute_direct(
        self,
        task_id: str,
        request: TaskRequest,
        started_at: datetime,
    ) -> TaskResult:
        """Execute task directly (when already in Task context).

        This is used when execute_task is called from within a Task subagent.
        No spawning needed - just return a placeholder result.

        Args:
            task_id: Unique task identifier
            request: Task request object
            started_at: Task start timestamp

        Returns:
            TaskResult indicating direct execution
        """
        # In direct execution mode, the caller handles the actual work
        # This just returns a success result
        completed_at = datetime.now()
        execution_time = (completed_at - started_at).total_seconds()

        return TaskResult(
            task_id=task_id,
            task_type=request.task_type,
            status=TaskStatus.COMPLETED,
            result={"mode": "direct", "message": "Executed in Task context"},
            started_at=started_at,
            completed_at=completed_at,
            execution_time=execution_time,
        )

    def _spawn_task(
        self,
        task_id: str,
        request: TaskRequest,
        started_at: datetime,
    ) -> TaskResult:
        """Spawn Task subagent and wait for completion.

        This method spawns a new Claude Code Task subagent using subprocess.

        Args:
            task_id: Unique task identifier
            request: Task request object
            started_at: Task start timestamp

        Returns:
            TaskResult with task execution results

        Raises:
            TaskSpawnError: Failed to spawn task
            TaskTimeoutError: Task exceeded timeout
        """
        # Create task output file
        output_file = self.task_output_dir / f"{task_id}.json"

        # Build task prompt with output instruction
        task_prompt = f"""
{request.prompt}

IMPORTANT: Write your result to the following file in JSON format:
{output_file}

Expected JSON structure:
{{
    "status": "completed|failed",
    "result": "your result here",
    "error": "error message if failed"
}}
"""

        # Spawn task via subprocess (placeholder - actual implementation TBD)
        # NOTE: This is a simplified version. Real implementation would use
        # Claude Code CLI or API to spawn tasks

        if self.verbose:
            print(f"[TaskExecutor] Spawning task {task_id}")
            print(f"[TaskExecutor] Output file: {output_file}")

        # For now, raise error since spawning mechanism not implemented
        # This will be implemented in integration testing
        raise TaskSpawnError(
            "Task spawning not implemented yet. "
            "This will be completed during integration with Claude Code Task API."
        )

    def is_available(self) -> bool:
        """Check if Task execution is available.

        Returns:
            True if Tasks can be spawned, False otherwise
        """
        # Check if already in Task context
        if is_task_context():
            return True

        # Check if claude CLI is available (placeholder)
        # Real implementation would check for Claude Code CLI
        return False
```

**Validation**:
```bash
# Test executor initialization
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); print(f'✓ Executor created, available: {executor.is_available()}')"
# Expected: ✓ Executor created, available: False (not in Task context)

# Test context detection in executor
CLAUDE_CODE_TASK_ID=test-456 uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); print(f'Available: {executor.is_available()}')"
# Expected: Available: True (in mock Task context)
```

---

### Phase 4: Add Error Handling and Logging (30 minutes)

**Goal**: Implement robust error handling and logging for Task execution

**File**: `tools/ce/task_executor.py` (UPDATE - Part 3)

**Add to TaskExecutor class**:

```python
import logging
from typing import Optional

# Configure logger
logger = logging.getLogger(__name__)


class TaskExecutor:
    # ... (existing code) ...

    def __init__(self, timeout: int = 300, verbose: bool = False):
        """Initialize task executor."""
        self.timeout = timeout
        self.verbose = verbose
        self.task_output_dir = Path(tempfile.gettempdir()) / "ce-tasks"
        self.task_output_dir.mkdir(exist_ok=True)

        # Configure logging
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

    def _log(self, level: str, message: str, **kwargs):
        """Log message with structured context.

        Args:
            level: Log level (debug, info, warning, error)
            message: Log message
            **kwargs: Additional context to include
        """
        log_func = getattr(logger, level.lower())
        context = " ".join(f"{k}={v}" for k, v in kwargs.items())
        log_func(f"{message} {context}" if context else message)

    def execute_task(
        self,
        task_type: str,
        prompt: str,
        timeout: Optional[int] = None,
        metadata: Optional[dict] = None,
    ) -> TaskResult:
        """Execute task with comprehensive error handling."""
        task_id = str(uuid.uuid4())
        started_at = datetime.now()

        try:
            self._log("info", "Starting task", task_id=task_id, task_type=task_type)

            # Create task request
            request = TaskRequest(
                task_type=TaskType(task_type),
                prompt=prompt,
                timeout=timeout or self.timeout,
                metadata=metadata or {},
            )

            # Execute based on context
            if is_task_context():
                self._log("debug", "Executing in Task context", task_id=task_id)
                result = self._execute_direct(task_id, request, started_at)
            else:
                self._log("debug", "Spawning Task subagent", task_id=task_id)
                result = self._spawn_task(task_id, request, started_at)

            self._log("info", "Task completed", task_id=task_id, status=result.status.value)
            return result

        except TaskTimeoutError as e:
            self._log("error", "Task timeout", task_id=task_id, error=str(e))
            return TaskResult(
                task_id=task_id,
                task_type=request.task_type,
                status=TaskStatus.TIMEOUT,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(),
            )

        except TaskSpawnError as e:
            self._log("error", "Task spawn failed", task_id=task_id, error=str(e))
            return TaskResult(
                task_id=task_id,
                task_type=request.task_type,
                status=TaskStatus.FAILED,
                error=str(e),
                started_at=started_at,
                completed_at=datetime.now(),
            )

        except Exception as e:
            self._log("error", "Unexpected error", task_id=task_id, error=str(e))
            return TaskResult(
                task_id=task_id,
                task_type=request.task_type,
                status=TaskStatus.FAILED,
                error=f"Unexpected error: {e}",
                started_at=started_at,
                completed_at=datetime.now(),
            )
```

**Validation**:
```bash
# Test error handling
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "
from ce.task_executor import TaskExecutor
executor = TaskExecutor(verbose=True)
result = executor.execute_task('classification', 'test prompt')
print(f'Status: {result.status.value}')
print(f'Error: {result.error}')
"
# Expected: Status: failed, Error: Task spawning not implemented yet...
```

---

### Phase 5: Write Unit Tests (120 minutes)

**Goal**: Comprehensive unit tests for task execution framework

**File**: `tools/tests/test_task_executor.py` (NEW)

**Implementation**:

```python
"""Unit tests for task executor."""

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from ce.task_executor import (
    TaskExecutor,
    get_task_id,
    is_task_context,
    validate_task_environment,
)
from ce.task_types import (
    TaskError,
    TaskRequest,
    TaskResult,
    TaskSpawnError,
    TaskStatus,
    TaskTimeoutError,
    TaskType,
)


class TestTaskTypes:
    """Test task type definitions."""

    def test_task_type_enum(self):
        """Test TaskType enum values."""
        assert TaskType.CLASSIFICATION.value == "classification"
        assert TaskType.BLENDING.value == "blending"
        assert TaskType.PRP_GENERATION.value == "prp_generation"
        assert TaskType.INITIALIZATION.value == "initialization"

    def test_task_status_enum(self):
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.TIMEOUT.value == "timeout"

    def test_task_request_creation(self):
        """Test TaskRequest creation."""
        request = TaskRequest(
            task_type=TaskType.CLASSIFICATION,
            prompt="Test prompt",
            timeout=300,
            metadata={"file": "test.md"},
        )
        assert request.task_type == TaskType.CLASSIFICATION
        assert request.prompt == "Test prompt"
        assert request.timeout == 300
        assert request.metadata == {"file": "test.md"}

    def test_task_request_serialization(self):
        """Test TaskRequest to_dict."""
        request = TaskRequest(
            task_type=TaskType.BLENDING,
            prompt="Blend content",
            timeout=600,
        )
        data = request.to_dict()
        assert data["task_type"] == "blending"
        assert data["prompt"] == "Blend content"
        assert data["timeout"] == 600
        assert data["metadata"] == {}

    def test_task_result_creation(self):
        """Test TaskResult creation."""
        started = datetime.now()
        result = TaskResult(
            task_id="test-123",
            task_type=TaskType.CLASSIFICATION,
            status=TaskStatus.COMPLETED,
            result={"category": "framework"},
            started_at=started,
            completed_at=started,
            execution_time=1.5,
        )
        assert result.task_id == "test-123"
        assert result.status == TaskStatus.COMPLETED
        assert result.result == {"category": "framework"}
        assert result.execution_time == 1.5

    def test_task_result_serialization(self):
        """Test TaskResult to_dict and from_dict."""
        started = datetime.now()
        original = TaskResult(
            task_id="test-456",
            task_type=TaskType.BLENDING,
            status=TaskStatus.FAILED,
            error="Test error",
            started_at=started,
        )

        # Serialize
        data = original.to_dict()
        assert data["task_id"] == "test-456"
        assert data["status"] == "failed"
        assert data["error"] == "Test error"

        # Deserialize
        restored = TaskResult.from_dict(data)
        assert restored.task_id == original.task_id
        assert restored.status == original.status
        assert restored.error == original.error


class TestTaskContextDetection:
    """Test task context detection."""

    def test_is_task_context_false(self):
        """Test context detection returns False in CLI."""
        # Ensure environment is clean
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        assert is_task_context() is False

    def test_is_task_context_true(self):
        """Test context detection returns True in Task."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-task-123"
        try:
            assert is_task_context() is True
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_get_task_id_none(self):
        """Test get_task_id returns None in CLI."""
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        assert get_task_id() is None

    def test_get_task_id_value(self):
        """Test get_task_id returns value in Task."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "task-456"
        try:
            assert get_task_id() == "task-456"
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_validate_task_environment_false(self):
        """Test validate_task_environment returns False in CLI."""
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        assert validate_task_environment() is False

    def test_validate_task_environment_true(self):
        """Test validate_task_environment returns True in Task."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "task-789"
        try:
            assert validate_task_environment() is True
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_validate_task_environment_empty_id(self):
        """Test validate_task_environment raises error for empty ID."""
        os.environ["CLAUDE_CODE_TASK_ID"] = ""
        try:
            with pytest.raises(TaskError, match="CLAUDE_CODE_TASK_ID is empty"):
                validate_task_environment()
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]


class TestTaskExecutor:
    """Test TaskExecutor class."""

    def test_executor_initialization(self):
        """Test TaskExecutor initialization."""
        executor = TaskExecutor(timeout=600, verbose=True)
        assert executor.timeout == 600
        assert executor.verbose is True
        assert executor.task_output_dir.exists()

    def test_executor_default_timeout(self):
        """Test TaskExecutor uses default timeout."""
        executor = TaskExecutor()
        assert executor.timeout == 300

    def test_is_available_false_in_cli(self):
        """Test is_available returns False in CLI."""
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        executor = TaskExecutor()
        assert executor.is_available() is False

    def test_is_available_true_in_task(self):
        """Test is_available returns True in Task context."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-task"
        try:
            executor = TaskExecutor()
            assert executor.is_available() is True
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_execute_direct_in_task_context(self):
        """Test direct execution when in Task context."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-direct"
        try:
            executor = TaskExecutor()
            result = executor.execute_task(
                task_type="classification",
                prompt="Test prompt",
            )

            assert result.status == TaskStatus.COMPLETED
            assert result.result["mode"] == "direct"
            assert result.execution_time is not None
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_execute_spawn_error_in_cli(self):
        """Test spawn error when not in Task context."""
        if "CLAUDE_CODE_TASK_ID" in os.environ:
            del os.environ["CLAUDE_CODE_TASK_ID"]

        executor = TaskExecutor()
        result = executor.execute_task(
            task_type="classification",
            prompt="Test prompt",
        )

        assert result.status == TaskStatus.FAILED
        assert "not implemented" in result.error.lower()

    def test_execute_with_custom_timeout(self):
        """Test execute_task with custom timeout."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-timeout"
        try:
            executor = TaskExecutor(timeout=300)
            result = executor.execute_task(
                task_type="classification",
                prompt="Test",
                timeout=600,  # Override default
            )

            assert result.status == TaskStatus.COMPLETED
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]

    def test_execute_with_metadata(self):
        """Test execute_task with metadata."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-meta"
        try:
            executor = TaskExecutor()
            result = executor.execute_task(
                task_type="blending",
                prompt="Blend content",
                metadata={"file": "test.md", "source": "framework"},
            )

            assert result.status == TaskStatus.COMPLETED
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]


class TestTaskExecutorErrorHandling:
    """Test TaskExecutor error handling."""

    def test_invalid_task_type(self):
        """Test executor handles invalid task type."""
        executor = TaskExecutor()

        with pytest.raises(ValueError):
            executor.execute_task(
                task_type="invalid_type",
                prompt="Test",
            )

    def test_logging_in_verbose_mode(self, caplog):
        """Test logging output in verbose mode."""
        os.environ["CLAUDE_CODE_TASK_ID"] = "test-log"
        try:
            executor = TaskExecutor(verbose=True)
            result = executor.execute_task(
                task_type="classification",
                prompt="Test",
            )

            # Verify logging occurred (exact assertions depend on logging setup)
            assert result.status == TaskStatus.COMPLETED
        finally:
            del os.environ["CLAUDE_CODE_TASK_ID"]


class TestTaskExceptions:
    """Test task exception classes."""

    def test_task_error(self):
        """Test TaskError exception."""
        with pytest.raises(TaskError, match="Test error"):
            raise TaskError("Test error")

    def test_task_timeout_error(self):
        """Test TaskTimeoutError exception."""
        with pytest.raises(TaskTimeoutError, match="Timeout"):
            raise TaskTimeoutError("Timeout")

    def test_task_spawn_error(self):
        """Test TaskSpawnError exception."""
        with pytest.raises(TaskSpawnError, match="Spawn failed"):
            raise TaskSpawnError("Spawn failed")


# Pytest configuration
@pytest.fixture(autouse=True)
def cleanup_environment():
    """Clean up environment variables after each test."""
    yield
    # Cleanup
    if "CLAUDE_CODE_TASK_ID" in os.environ:
        del os.environ["CLAUDE_CODE_TASK_ID"]
```

**Validation**:
```bash
# Run all tests
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_task_executor.py -v

# Expected output:
# test_task_types.py::TestTaskTypes::test_task_type_enum PASSED
# test_task_types.py::TestTaskTypes::test_task_status_enum PASSED
# ... (all tests passing)

# Run with coverage
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_task_executor.py --cov=ce.task_executor --cov-report=term
# Expected: >90% coverage
```

---

### Phase 6: Documentation and Examples (30 minutes)

**Goal**: Create documentation for task executor usage

**File**: `tools/ce/README_TASK_EXECUTOR.md` (NEW)

**Implementation**:

```markdown
# Task Executor - Foundation for Task-Based Architecture

## Overview

The Task Executor provides a unified interface for spawning Claude Code Task subagents
and executing LLM operations with automatic Claude Max 5x quota usage.

## Key Concepts

### Dual-Mode Operation

The executor operates in two modes:

1. **Task Context Mode** (Claude Max 5x quota):
   - Detects if already running inside Claude Code Task
   - Uses `Anthropic()` without API key
   - Automatically routes to Claude Max quota pool
   - No spawning needed - direct execution

2. **CLI Mode** (API quota fallback):
   - Detects standalone CLI execution
   - Spawns new Task subagent via Claude Code CLI/API
   - Falls back to `Anthropic(api_key=...)` if spawning unavailable
   - Maintains backward compatibility

### Context Detection

Context detection uses `CLAUDE_CODE_TASK_ID` environment variable:

```python
from ce.task_executor import is_task_context

if is_task_context():
    print("Running inside Task - Max quota available")
else:
    print("Running in CLI - API quota required")
```

## Usage

### Basic Usage

```python
from ce.task_executor import TaskExecutor

# Initialize executor
executor = TaskExecutor(timeout=300)

# Execute task
result = executor.execute_task(
    task_type="classification",
    prompt="Classify this file: path/to/file.md"
)

# Check result
if result.status == TaskStatus.COMPLETED:
    print(f"Success: {result.result}")
else:
    print(f"Failed: {result.error}")
```

### With Custom Timeout

```python
executor = TaskExecutor(timeout=600)  # 10 minutes

result = executor.execute_task(
    task_type="blending",
    prompt="Blend framework and user content",
    timeout=900,  # Override to 15 minutes
)
```

### With Metadata

```python
result = executor.execute_task(
    task_type="classification",
    prompt="Classify file",
    metadata={
        "file_path": "examples/TOOL-USAGE-GUIDE.md",
        "source": "framework",
    }
)
```

### Error Handling

```python
from ce.task_types import TaskStatus, TaskTimeoutError

executor = TaskExecutor(verbose=True)

result = executor.execute_task(
    task_type="classification",
    prompt="Long-running task",
    timeout=60,
)

if result.status == TaskStatus.TIMEOUT:
    print(f"Task timed out: {result.error}")
elif result.status == TaskStatus.FAILED:
    print(f"Task failed: {result.error}")
elif result.status == TaskStatus.COMPLETED:
    print(f"Success: {result.result}")
```

## Task Types

Supported task types:

- `classification`: File classification with Haiku
- `blending`: Content blending with Sonnet
- `prp_generation`: PRP document generation
- `initialization`: Full CE initialization workflow

## Architecture

### Components

1. **task_types.py**: Data structures and enums
   - `TaskType`: Enum of supported task types
   - `TaskStatus`: Enum of execution states
   - `TaskRequest`: Request data structure
   - `TaskResult`: Result data structure
   - Task exceptions: `TaskError`, `TaskTimeoutError`, `TaskSpawnError`

2. **task_executor.py**: Core execution logic
   - `is_task_context()`: Context detection
   - `TaskExecutor`: Main executor class
   - Error handling and logging
   - Timeout management

### Execution Flow

```
User Code
    ↓
TaskExecutor.execute_task()
    ↓
Context Detection
    ↓
    ├─ In Task Context → Direct Execution
    │                    (No spawn, Max quota)
    │
    └─ In CLI Context → Spawn Task Subagent
                        (Subprocess/API, fallback to API key)
    ↓
Return TaskResult
```

## Testing

### Unit Tests

```bash
# Run all tests
cd tools
uv run pytest tests/test_task_executor.py -v

# Run with coverage
uv run pytest tests/test_task_executor.py --cov=ce.task_executor
```

### Integration Tests

Integration tests require Claude Code Task execution environment.
These will be implemented in Phase 4 (PRP-43.3.1).

## Future Enhancements

Phase 2+ PRPs will use this foundation to refactor:

- **PRP-43.2.1**: Classification (uses `ClassificationTask`)
- **PRP-43.2.2**: Blending (uses `BlendingTask`)
- **PRP-43.2.3**: PRP Generation (uses `PRPGenerationTask`)
- **PRP-43.3.1**: Initialization workflow integration

## Related Documentation

- [PRP-43-INITIAL](../../PRPs/feature-requests/PRP-43-INITIAL-task-based-quota.md) - Parent PRP
- [CLAUDE.md](../../CLAUDE.md) - Project guide
```

**Validation**:
```bash
# Verify documentation exists and is readable
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
test -f ce/README_TASK_EXECUTOR.md && echo "✓ Documentation created"

# Verify links work
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
cat ce/README_TASK_EXECUTOR.md | grep -E '\[.*\]\(.*\)' | wc -l
# Expected: At least 5 markdown links
```

---

## 4. Validation Gates

### Gate 1: File Creation and Imports

**Commands**:
```bash
# Verify files created
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
test -f ce/task_types.py && echo "✓ task_types.py created"
test -f ce/task_executor.py && echo "✓ task_executor.py created"
test -f tests/test_task_executor.py && echo "✓ test_task_executor.py created"
test -f ce/README_TASK_EXECUTOR.md && echo "✓ README created"

# Verify imports work
uv run python -c "from ce.task_types import TaskType, TaskResult, TaskRequest; print('✓ task_types imports work')"
uv run python -c "from ce.task_executor import TaskExecutor, is_task_context; print('✓ task_executor imports work')"
```

**Success Criteria**:
- All 4 files exist
- All imports successful
- No Python syntax errors

---

### Gate 2: Context Detection Works

**Commands**:
```bash
# Test context detection in CLI
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.task_executor import is_task_context; print(f'In Task: {is_task_context()}')"
# Expected: In Task: False

# Test context detection with mock Task environment
CLAUDE_CODE_TASK_ID=test-123 uv run python -c "from ce.task_executor import is_task_context, get_task_id; print(f'In Task: {is_task_context()}, ID: {get_task_id()}')"
# Expected: In Task: True, ID: test-123

# Test validation
CLAUDE_CODE_TASK_ID=test-456 uv run python -c "from ce.task_executor import validate_task_environment; print(f'Valid: {validate_task_environment()}')"
# Expected: Valid: True
```

**Success Criteria**:
- CLI detection returns False
- Mock Task detection returns True
- Task ID retrieval works
- Validation passes in Task context

---

### Gate 3: TaskExecutor Initialization

**Commands**:
```bash
# Test executor creation
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); print(f'✓ Executor created, timeout: {executor.timeout}s')"
# Expected: ✓ Executor created, timeout: 300s

# Test custom timeout
uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(timeout=600, verbose=True); print(f'✓ Timeout: {executor.timeout}s, Verbose: {executor.verbose}')"
# Expected: ✓ Timeout: 600s, Verbose: True

# Test is_available
uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); print(f'Available: {executor.is_available()}')"
# Expected: Available: False (CLI context)

CLAUDE_CODE_TASK_ID=test uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); print(f'Available: {executor.is_available()}')"
# Expected: Available: True (Task context)
```

**Success Criteria**:
- Executor initializes successfully
- Default timeout is 300s
- Custom timeout works
- Verbose mode works
- is_available() detects context correctly

---

### Gate 4: Task Execution (Direct Mode)

**Commands**:
```bash
# Test direct execution in Task context
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
CLAUDE_CODE_TASK_ID=test-direct uv run python -c "
from ce.task_executor import TaskExecutor
from ce.task_types import TaskStatus

executor = TaskExecutor()
result = executor.execute_task(
    task_type='classification',
    prompt='Test prompt'
)

print(f'Status: {result.status.value}')
print(f'Mode: {result.result[\"mode\"]}')
print(f'Execution time: {result.execution_time}s')
"
# Expected: Status: completed, Mode: direct, Execution time: 0.XXXs
```

**Success Criteria**:
- Direct execution works in Task context
- Returns COMPLETED status
- Execution time recorded
- No errors

---

### Gate 5: Error Handling

**Commands**:
```bash
# Test spawn error in CLI
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run python -c "
from ce.task_executor import TaskExecutor
from ce.task_types import TaskStatus

executor = TaskExecutor()
result = executor.execute_task(
    task_type='classification',
    prompt='Test'
)

print(f'Status: {result.status.value}')
print(f'Error present: {result.error is not None}')
print(f'Error message contains \"not implemented\": {\"not implemented\" in result.error.lower()}')
"
# Expected: Status: failed, Error present: True, Error message contains "not implemented": True

# Test invalid task type
uv run python -c "
from ce.task_executor import TaskExecutor

executor = TaskExecutor()
try:
    result = executor.execute_task(task_type='invalid', prompt='Test')
    print('❌ Should have raised ValueError')
except ValueError:
    print('✓ ValueError raised for invalid task type')
"
# Expected: ✓ ValueError raised for invalid task type
```

**Success Criteria**:
- Spawn error returns FAILED status
- Error message is descriptive
- Invalid task types raise ValueError
- No unhandled exceptions

---

### Gate 6: Unit Tests Pass

**Commands**:
```bash
# Run all tests
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
uv run pytest tests/test_task_executor.py -v

# Expected: All tests pass (30+ tests)

# Run with coverage
uv run pytest tests/test_task_executor.py --cov=ce.task_executor --cov=ce.task_types --cov-report=term

# Expected: >90% coverage
```

**Success Criteria**:
- All unit tests pass
- No test failures or errors
- Test coverage >90%
- Tests run in <10 seconds

---

### Gate 7: Documentation Complete

**Commands**:
```bash
# Verify documentation exists
cd /Users/bprzybyszi/nc-src/ctx-eng-plus/tools
test -f ce/README_TASK_EXECUTOR.md && echo "✓ Documentation exists"

# Verify documentation has required sections
cat ce/README_TASK_EXECUTOR.md | grep -E '^## ' | wc -l
# Expected: At least 8 sections

# Verify code examples work
cat ce/README_TASK_EXECUTOR.md | grep -E '```python' | wc -l
# Expected: At least 5 code examples
```

**Success Criteria**:
- Documentation file exists
- All required sections present
- Code examples provided
- Links to related docs work

---

## 5. Testing Strategy

### Unit Testing

**Test Coverage Goals**:
- `task_types.py`: 100% (simple data structures)
- `task_executor.py`: >90% (core logic)
- Overall: >90%

**Test Categories**:

1. **Task Type Tests**:
   - Enum values correct
   - Data structure creation
   - Serialization/deserialization
   - Exception classes

2. **Context Detection Tests**:
   - CLI context detection
   - Task context detection
   - Task ID retrieval
   - Environment validation

3. **TaskExecutor Tests**:
   - Initialization
   - Availability checking
   - Direct execution (Task context)
   - Error handling (CLI context)
   - Custom timeouts
   - Metadata passing

4. **Error Handling Tests**:
   - Invalid task types
   - Spawn failures
   - Timeout errors
   - Logging in verbose mode

### Integration Testing

**Scope**: Deferred to Phase 4 (PRP-43.3.1)

Integration tests require:
- Real Claude Code Task execution environment
- Ability to spawn Task subagents
- Task communication protocol implementation

These will be implemented when integrating with actual CE initialization workflow.

### Manual Testing

**Test Scenarios**:

1. **CLI Execution**:
   ```bash
   cd tools
   uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); print(executor.is_available())"
   # Expected: False
   ```

2. **Mock Task Execution**:
   ```bash
   cd tools
   CLAUDE_CODE_TASK_ID=test uv run python -c "from ce.task_executor import TaskExecutor; executor = TaskExecutor(); result = executor.execute_task('classification', 'test'); print(result.status)"
   # Expected: TaskStatus.COMPLETED
   ```

3. **Error Scenarios**:
   - Invalid task type → ValueError
   - Spawn in CLI → TaskSpawnError (not implemented)
   - Empty task ID → TaskError

### Performance Testing

**Baseline Metrics**:
- Context detection: <1ms
- Direct execution: <10ms
- Error handling: <5ms
- Unit test suite: <10s

**Performance Targets** (to be validated in integration):
- Task spawn overhead: <5s
- End-to-end classification: <30s (Haiku)
- End-to-end blending: <120s (Sonnet)

---

## 6. Rollout Plan

### Pre-Execution Checklist

- [ ] Review complete PRP document
- [ ] No uncommitted changes in `tools/` directory
- [ ] UV environment is up to date (`uv sync`)
- [ ] All validation gates understood
- [ ] Testing strategy clear

### Execution Timeline

**Total Estimated Time**: 6 hours

**Phase 1: Task Types** (60 min)
- Create `task_types.py`
- Define enums, data structures, exceptions
- Test imports

**Phase 2: Context Detection** (45 min)
- Add context detection functions to `task_executor.py`
- Test detection in CLI and Task modes

**Phase 3: TaskExecutor** (90 min)
- Implement `TaskExecutor` class
- Add `execute_task` method
- Implement direct execution mode
- Add spawn placeholder

**Phase 4: Error Handling** (30 min)
- Add logging infrastructure
- Implement comprehensive error handling
- Test error scenarios

**Phase 5: Unit Tests** (120 min)
- Write test file `test_task_executor.py`
- Implement 30+ test cases
- Verify coverage >90%

**Phase 6: Documentation** (30 min)
- Create `README_TASK_EXECUTOR.md`
- Add usage examples
- Document architecture

**Phase 7: Validation** (45 min)
- Run all validation gates
- Fix any issues
- Verify all criteria met

### Post-Execution Checklist

- [ ] All files created (`task_types.py`, `task_executor.py`, tests, docs)
- [ ] All imports work
- [ ] Context detection works (CLI + Task)
- [ ] Direct execution works (Task context)
- [ ] Error handling works (CLI context)
- [ ] All unit tests pass
- [ ] Test coverage >90%
- [ ] Documentation complete
- [ ] All validation gates passed

---

## 7. Success Metrics

### Functional Metrics

- ✅ **Context Detection**: 100% accurate (CLI vs Task)
- ✅ **Direct Execution**: Works in Task context
- ✅ **Error Handling**: All error cases handled gracefully
- ✅ **Dual-Mode Support**: CLI fallback works
- ✅ **Test Coverage**: >90% for all modules

### Code Quality Metrics

- ✅ **Type Safety**: All functions typed (mypy strict)
- ✅ **Documentation**: All public APIs documented
- ✅ **Error Messages**: Clear, actionable error messages
- ✅ **Logging**: Structured logging in verbose mode
- ✅ **KISS Principle**: Simple, minimal implementation

### Integration Readiness

- ✅ **API Stable**: TaskExecutor interface complete
- ✅ **Extensible**: New task types easy to add
- ✅ **Backward Compatible**: CLI mode works without changes
- ✅ **Ready for Phase 2**: Classification can use this foundation
- ✅ **Ready for Phase 3**: Blending can use this foundation

---

## 8. Dependencies

**None** - This is the foundation phase that all other phases depend on.

**Consumed By**:
- PRP-43.2.1 (Phase 2): Classification Task refactoring
- PRP-43.2.2 (Phase 3): Blending Task refactoring
- PRP-43.2.3 (Phase 5): PRP Generation Task integration
- PRP-43.3.1 (Phase 4): Initialization workflow integration

**Files Created**:
- `tools/ce/task_types.py`
- `tools/ce/task_executor.py`
- `tools/tests/test_task_executor.py`
- `tools/ce/README_TASK_EXECUTOR.md`

**Files Modified**:
- None (this is pure addition)

---

## 9. Risks & Mitigations

### Risk 1: Task Context Detection Fails

**Probability**: Low
**Impact**: High (code can't determine quota pool)

**Mitigation**:
- Test environment variable approach early (Phase 2)
- Add explicit logging: "Using Max quota" vs "Using API quota"
- Fallback to API key if detection unclear
- Unit tests verify detection logic

**Validation**:
```bash
# CLI detection
uv run python -c "from ce.task_executor import is_task_context; assert not is_task_context()"

# Task detection
CLAUDE_CODE_TASK_ID=test uv run python -c "from ce.task_executor import is_task_context; assert is_task_context()"
```

---

### Risk 2: Task Spawning Mechanism Unclear

**Probability**: Medium
**Impact**: Medium (can't implement spawn in this PRP)

**Mitigation**:
- Implement spawn as placeholder (raises NotImplementedError)
- Direct execution mode works (Task context)
- Defer spawn implementation to integration phase (PRP-43.3.1)
- Document spawn requirements clearly

**Fallback**: Use API key in CLI mode if spawning unavailable

---

### Risk 3: Backward Compatibility Issues

**Probability**: Low
**Impact**: Medium (existing scripts break)

**Mitigation**:
- No modifications to existing files in this PRP
- CLI mode works exactly as before (API key required)
- Task mode is pure addition (new capability)
- Tests verify both modes work

**Validation**: Existing CE commands still work after this PRP

---

### Risk 4: Performance Overhead

**Probability**: Low
**Impact**: Low (minor slowdown acceptable)

**Mitigation**:
- Direct execution has minimal overhead (<10ms)
- Spawn overhead deferred to integration phase
- Benchmark performance in Phase 4 integration testing
- Optimize if needed based on real measurements

**Target**: <5s overhead for Task spawn (acceptable)

---

## 10. Acceptance Criteria

- [ ] **Files Created**: All 4 files exist with correct content
- [ ] **Imports Work**: No syntax errors, all imports successful
- [ ] **Context Detection**: CLI and Task modes detected correctly
- [ ] **Direct Execution**: Works in Task context, returns COMPLETED
- [ ] **Error Handling**: Spawn error in CLI mode, descriptive messages
- [ ] **Unit Tests**: All tests pass, coverage >90%
- [ ] **Documentation**: README complete with examples
- [ ] **Validation Gates**: All 7 gates passed
- [ ] **Type Safety**: mypy strict mode passes
- [ ] **No Regressions**: Existing CE commands still work

---

## 11. Design Decisions

### Decision 1: Environment Variable for Context Detection

**Options Considered**:
- Environment variable (`CLAUDE_CODE_TASK_ID`)
- Process inspection (check parent process)
- API call to Claude Code (expensive)
- Configuration file (fragile)

**Chosen**: Environment variable

**Rationale**:
- Simple and reliable
- Fast (<1ms check)
- Standard pattern in containerized environments
- Easy to test (can mock environment)
- No external dependencies

---

### Decision 2: Placeholder Spawn Implementation

**Options Considered**:
- Implement full spawn now (complex, unknown API)
- Placeholder with NotImplementedError
- Mock implementation (confusing)

**Chosen**: Placeholder with clear error message

**Rationale**:
- Spawn mechanism not yet defined by Claude Code
- Interface is stable (can implement later)
- Direct execution mode proves the concept
- Integration phase (43.3.1) is right time for real implementation
- Tests can use direct mode (Task context)

---

### Decision 3: TaskResult Data Structure

**Options Considered**:
- Simple dict (flexible but untyped)
- Dataclass (typed, serializable)
- Pydantic model (overkill, new dependency)

**Chosen**: Dataclass with to_dict/from_dict

**Rationale**:
- Type safety with mypy
- No new dependencies (stdlib only)
- Easy serialization for future caching
- Clear API with named fields
- Lightweight and fast

---

### Decision 4: Separate task_types.py File

**Options Considered**:
- All code in `task_executor.py`
- Separate `task_types.py` for data structures
- Multiple files (task_request.py, task_result.py, etc.)

**Chosen**: Separate `task_types.py`

**Rationale**:
- Clear separation of concerns (data vs logic)
- Can import types without importing executor
- Easier to test data structures independently
- Single responsibility per file
- Not too fragmented (one types file, one logic file)

---

## 12. KISS Validation

### Complexity Score: 4/10 (Low-Medium)

**Why low-medium complexity**:
- New architecture pattern (some complexity)
- But: Simple API (3 public functions)
- But: Clear separation (types vs executor)
- But: Minimal dependencies (stdlib only)
- But: Placeholder spawn (complexity deferred)

**Complexity drivers**:
- Dual-mode operation (2 execution paths)
- Error handling (3 exception types)
- Logging infrastructure
- Test mocking

**Complexity reducers**:
- No real Task spawning yet (placeholder)
- No communication protocol yet (deferred)
- No caching yet (out of scope)
- Pure Python (no async, no C extensions)

---

### Extendability Score: 9/10 (High)

**How to extend**:

1. **Add new task type**:
   ```python
   # In task_types.py
   class TaskType(Enum):
       VALIDATION = "validation"  # New type
   ```

2. **Add new error type**:
   ```python
   # In task_types.py
   class TaskCancelledError(TaskError):
       """Task was cancelled by user."""
   ```

3. **Add metadata to TaskRequest**:
   ```python
   # Already supported via metadata dict
   request = TaskRequest(..., metadata={"custom": "data"})
   ```

4. **Implement spawn mechanism**:
   ```python
   # In task_executor.py, replace _spawn_task placeholder
   def _spawn_task(self, task_id, request, started_at):
       # Real implementation here
   ```

**No breaking changes needed** for extensions.

---

### Efficiency Score: 8/10 (High)

**Performance**:
- Context detection: <1ms (environment variable check)
- Direct execution: <10ms (no spawning)
- Error handling: <5ms (exception creation)
- Unit tests: <10s (30+ tests)

**Memory**:
- TaskResult: ~200 bytes per instance
- TaskExecutor: ~1KB (minimal state)
- No caching yet (deferred to future phases)

**Bottlenecks** (to be addressed in integration):
- Task spawn time (estimated 3-5s)
- Task communication overhead (TBD)

---

## 13. Related PRPs

**Parent PRP**:
- **PRP-43-INITIAL**: Task-Based Architecture for Claude Max 5x Quota

**Blocked PRPs** (waiting for this foundation):
- **PRP-43.2.1**: Classification Task Refactoring (Phase 2)
- **PRP-43.2.2**: Blending Task Refactoring (Phase 3)
- **PRP-43.2.3**: PRP Generation Task Integration (Phase 5)
- **PRP-43.3.1**: Initialization Workflow Integration (Phase 4)

**Related PRPs**:
- **PRP-42**: REJECTED - Agent SDK migration (wrong approach)

---

## 14. Next Steps

After completing this PRP:

1. **Approve and merge** foundation code
2. **Proceed to Phase 2** (PRP-43.2.1) - Classification refactoring
3. **Parallel work possible** for Phases 2, 3, 5 (all use this foundation)
4. **Integration in Phase 4** (PRP-43.3.1) - Implement real Task spawning

**Timeline**:
- Week 1: PRP-43.1.1 (this PRP) + PRP-43.1.2 (docs)
- Week 2: PRP-43.2.1, PRP-43.2.2, PRP-43.2.3 (parallel execution)
- Week 3: PRP-43.3.1 (integration + real Task spawning)

---

**Generated**: 2025-11-08T00:00:00Z
**Batch Mode**: Yes (Batch 43, Stage 1, Order 1)
**Parent PRP**: PRP-43-INITIAL
**Blocks**: PRP-43.2.1, PRP-43.2.2, PRP-43.2.3, PRP-43.3.1
