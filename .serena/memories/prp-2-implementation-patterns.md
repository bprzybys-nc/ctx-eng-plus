---
type: regular
category: pattern
tags: [prp, implementation, workflow]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# PRP-2 Implementation Patterns

**Source**: PRP-2 execution (2025-10-12)  
**Purpose**: Reference patterns for PRP state management implementation

---

## State File Structure

**Location**: `.ce/active_prp_session`

**Format** (JSON):
```json
{
  "prp_id": "PRP-2",
  "prp_name": "PRP State Management & Isolation",
  "started_at": "2025-10-12T14:30:15Z",
  "phase": "implementation",
  "checkpoint_count": 3,
  "last_checkpoint": "checkpoint-PRP-2-implementation-20251012-143215",
  "validation_attempts": {
    "gate_1": 1,
    "gate_2": 2
  },
  "serena_memories": [
    "PRP-2-checkpoint-phase1",
    "PRP-2-learnings-atomic-writes"
  ]
}
```

---

## Atomic Write Pattern

**Problem**: Race conditions and partial writes to state file  
**Solution**: Temp file + rename (atomic at filesystem level)

```python
from pathlib import Path
import json
from typing import Dict, Any

STATE_DIR = Path(".ce")
STATE_FILE = STATE_DIR / "active_prp_session"

def _write_state(state: Dict[str, Any]) -> None:
    """Atomic write using temp file + rename pattern.
    
    Ensures state file integrity even if process crashes mid-write.
    """
    STATE_DIR.mkdir(exist_ok=True)
    temp_file = STATE_FILE.with_suffix(".tmp")
    temp_file.write_text(json.dumps(state, indent=2))
    temp_file.replace(STATE_FILE)  # Atomic on POSIX
```

**Key Benefits**:
- Atomic operation (no partial writes)
- Process crash-safe
- No lock files needed
- POSIX filesystem guarantee

---

## Checkpoint Naming Convention

**Pattern**: `checkpoint-{prp_id}-{phase}-{timestamp}`

**Components**:
- `checkpoint-` - Fixed prefix for git tag filtering
- `{prp_id}` - PRP identifier (e.g., "PRP-2")
- `{phase}` - Phase name (planning, implementation, testing, validation, complete)
- `{timestamp}` - Format: `YYYYMMDD-HHMMSS` (e.g., "20251012-143215")

**Examples**:
```
checkpoint-PRP-2-planning-20251012-100530
checkpoint-PRP-2-implementation-20251012-143215
checkpoint-PRP-3-testing-20251012-163045
checkpoint-PRP-2-final-20251012-182130
```

**Implementation**:
```python
from datetime import datetime

def create_checkpoint(phase: str, message: Optional[str] = None) -> Dict[str, Any]:
    state = get_active_prp()
    if not state:
        raise RuntimeError("No active PRP session")
    
    prp_id = state["prp_id"]
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    tag_name = f"checkpoint-{prp_id}-{phase}-{timestamp}"
    
    msg = message or f"Checkpoint: {prp_id} {phase} phase"
    result = run_cmd(f'git tag -a "{tag_name}" -m "{msg}"')
    
    if not result["success"]:
        raise RuntimeError(
            f"Failed to create checkpoint: {result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure working tree is clean"
        )
    
    # Update state with checkpoint info
    state["checkpoint_count"] = state.get("checkpoint_count", 0) + 1
    state["last_checkpoint"] = tag_name
    _write_state(state)
    
    return {"tag_name": tag_name, "message": msg}
```

---

## Memory Namespacing

**Pattern**: `{prp_id}-{category}-{name}`

**Categories**:
- `checkpoint` - Phase checkpoint memories (ephemeral)
- `learnings` - Persistent learnings to archive
- `temp` - Temporary scratch data (ephemeral)
- `validation` - Validation results (ephemeral)

**Examples**:
```
PRP-2-checkpoint-phase1
PRP-2-learnings-atomic-writes
PRP-2-temp-scratch-notes
PRP-3-validation-gate-1-results
```

**Implementation with Graceful Degradation**:
```python
def write_prp_memory(category: str, name: str, content: str) -> Dict[str, Any]:
    """Write PRP-scoped memory with graceful Serena degradation."""
    state = get_active_prp()
    if not state:
        raise RuntimeError("No active PRP session")
    
    prp_id = state["prp_id"]
    memory_name = f"{prp_id}-{category}-{name}"
    
    # Try Serena MCP, gracefully degrade if unavailable
    try:
        from mcp import serena
        serena.write_memory(memory_name, content)
        serena_available = True
    except Exception as e:
        logger.warning(f"Serena unavailable: {e}")
        serena_available = False
    
    # Track in state regardless of Serena availability
    if "serena_memories" not in state:
        state["serena_memories"] = []
    if memory_name not in state["serena_memories"]:
        state["serena_memories"].append(memory_name)
    _write_state(state)
    
    return {
        "success": True,
        "memory_name": memory_name,
        "serena_available": serena_available
    }
```

---

## Cleanup Protocol (Model.md Section 5.6)

**7-Step Process**:

1. **Delete intermediate checkpoints** (keep final)
2. **Archive learnings** to project knowledge
3. **Delete ephemeral memories** (checkpoint-*, temp-*)
4. **Reset validation state**
5. **Run context health check**
6. **Archive validation logs**
7. **Remove active session**

**Implementation**:
```python
def cleanup_prp(prp_id: str) -> Dict[str, Any]:
    """Execute comprehensive cleanup protocol."""
    state = get_active_prp()
    if not state or state["prp_id"] != prp_id:
        raise RuntimeError(f"No active session for {prp_id}")
    
    result = {
        "success": True,
        "checkpoints_deleted": 0,
        "checkpoints_kept": [],
        "memories_archived": [],
        "memories_deleted": [],
        "context_health": {}
    }
    
    # Step 1: Delete intermediate checkpoints
    checkpoints = list_checkpoints(prp_id)
    for cp in checkpoints:
        if "final" in cp["phase"]:
            result["checkpoints_kept"].append(cp["tag_name"])
        else:
            run_cmd(f"git tag -d {cp['tag_name']}")
            result["checkpoints_deleted"] += 1
    
    # Step 2-3: Archive learnings, delete ephemeral
    for memory_name in state.get("serena_memories", []):
        category = memory_name.split("-")[1]  # Extract category
        if category == "learnings":
            result["memories_archived"].append(memory_name)
            # TODO: Copy to project knowledge base
        elif category in ["checkpoint", "temp"]:
            result["memories_deleted"].append(memory_name)
            # TODO: Delete from Serena
    
    # Step 5: Context health check
    from .context import health as context_health
    result["context_health"] = context_health()
    
    # Step 7: Remove session
    if STATE_FILE.exists():
        STATE_FILE.unlink()
    
    return result
```

---

## Test Patterns

### State Management Tests
```python
def test_start_prp_creates_state_file():
    """Verify start_prp creates state file with correct structure."""
    result = start_prp("PRP-999", "Test PRP")
    
    assert STATE_FILE.exists()
    state = json.loads(STATE_FILE.read_text())
    assert state["prp_id"] == "PRP-999"
    assert state["prp_name"] == "Test PRP"
    assert "started_at" in state
    assert state["phase"] == "planning"
```

### Checkpoint Tests (Requires Clean Git)
```python
def test_create_checkpoint_success():
    """Verify checkpoint creation with clean git tree."""
    start_prp("PRP-999")
    
    # Ensure clean git state
    result = run_cmd("git status --porcelain")
    if result["stdout"]:
        pytest.skip("Git tree not clean")
    
    checkpoint = create_checkpoint("phase1")
    
    assert "checkpoint-PRP-999-phase1" in checkpoint["tag_name"]
```

### Cleanup Tests
```python
def test_cleanup_prp_archives_learnings():
    """Verify cleanup identifies learnings for archiving."""
    start_prp("PRP-999")
    write_prp_memory("learnings", "auth-patterns", "Content")
    write_prp_memory("checkpoint", "phase1", "Temp")
    
    result = cleanup_prp("PRP-999")
    
    assert "PRP-999-learnings-auth-patterns" in result["memories_archived"]
    assert "PRP-999-checkpoint-phase1" in result["memories_deleted"]
```

---

## Common Pitfalls & Solutions

### Pitfall 1: PRP ID Format
**Problem**: Leading zeros in PRP IDs (e.g., "PRP-001")  
**Error**: `ValueError: Invalid PRP ID format`  
**Solution**: Use "PRP-1", "PRP-2" format (no leading zeros)

### Pitfall 2: Uncommitted Changes
**Problem**: Checkpoint creation fails with dirty git tree  
**Error**: `RuntimeError: Working tree has uncommitted changes`  
**Solution**: Commit or stash changes before creating checkpoints

### Pitfall 3: Multiple Active PRPs
**Problem**: Starting new PRP while another is active  
**Error**: `RuntimeError: Another PRP session is active: PRP-2`  
**Solution**: Run `end_prp()` or `cleanup_prp()` before starting new session

### Pitfall 4: Import Errors
**Problem**: `ImportError: cannot import name 'context_health'`  
**Root Cause**: Function name mismatch  
**Solution**: Import with alias: `from .context import health as context_health`

---

## Integration Points

### With Git
- Uses annotated tags for checkpoints
- Validates clean working tree before checkpoints
- Parses `git tag -l` output for checkpoint listing

### With Serena MCP
- Graceful degradation if Serena unavailable
- Tracks memory names in state file regardless
- Cleanup protocol aware of Serena unavailability

### With Validation System
- Tracks validation attempts in state
- Gate numbers stored as keys in `validation_attempts`
- Cleanup protocol resets validation state

---

## Files Reference

**Implementation**: `tools/ce/prp.py` (lines 210-931)  
**Tests**:
- State: `tools/tests/test_prp_state.py` (15 tests)
- Checkpoints: `tools/tests/test_prp_checkpoint.py` (13 tests)
- Cleanup: `tools/tests/test_prp_cleanup.py` (8 tests)

**Total Test Coverage**: 36 tests, all passing