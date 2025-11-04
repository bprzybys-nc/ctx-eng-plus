---
type: regular
category: documentation
tags: [code-style, conventions, standards]
created: "2025-11-04T17:30:00Z"
updated: "2025-11-04T17:30:00Z"
---

# Code Style and Conventions

## Communication Style
**Direct, token-efficient. No fluff.**
- Short sentences, maximum clarity
- Call out problems directly
- Real talk, zero BS

## Core Principles

### No Fishy Fallbacks - MANDATORY
- ✅ Fast Failure: Let exceptions bubble up
- ✅ Actionable Errors: Include 🔧 troubleshooting guidance
- ✅ No Silent Corruption: Make failures visible
- ❌ No hardcoded default values that bypass business logic
- ❌ No silent exception catches that hide data corruption
- ❌ No broad exception catches that mask root causes

### KISS (Keep It Simple, Stupid)
- Simple solutions first
- Clear code over clever code
- Minimal dependencies (stdlib only for this project)
- Single responsibility per function
- Direct implementation
- Fast failure

## File and Function Limits (Guidelines)
- **Functions**: ~50 lines max - single, clear responsibility
- **Files**: ~300-500 lines max - break into logical modules if approaching
- **Classes**: ~100 lines max - represent single concept

## Naming Conventions
```python
# AVOID: Version-specific naming
def get_v2_processor()

# PREFER: Business-focused naming
def get_processor()
```

## Type Hints
Use Python type hints throughout:
```python
def run_cmd(cmd: str, timeout: int = 60) -> Dict[str, Any]:
    """Execute shell command with timeout."""
    pass
```

## Docstrings (Google Style)
```python
def run_cmd(cmd: str, timeout: int = 60) -> Dict[str, Any]:
    """Execute shell command with timeout.

    Args:
        cmd: Shell command to execute
        timeout: Command timeout in seconds

    Returns:
        Dict with: success, stdout, stderr, exit_code, duration

    Raises:
        TimeoutError: If command exceeds timeout
        RuntimeError: If command execution fails

    Note: No fishy fallbacks - exceptions thrown for troubleshooting.
    """
```

## Exception Handling
```python
# ✅ GOOD - Clear troubleshooting
def git_checkpoint(message: str) -> str:
    result = run_cmd(f'git tag -a "{tag}" -m "{message}"')
    if not result["success"]:
        raise RuntimeError(
            f"Failed to create checkpoint: {result['stderr']}\n"
            f"🔧 Troubleshooting: Ensure you have commits to tag"
        )
    return tag

# ❌ BAD - Silent failure
def git_checkpoint(message: str) -> str:
    try:
        result = run_cmd(f'git tag -a "{tag}" -m "{message}"')
        return tag
    except:
        return "checkpoint-failed"  # FISHY FALLBACK!
```

## Function Design
```python
# ✅ GOOD - Single responsibility, clear purpose
def git_status() -> Dict[str, Any]:
    """Get git repository status."""
    # ... implementation

# ❌ BAD - Multiple responsibilities
def git_stuff(action: str) -> Any:
    """Do various git things."""
    if action == "status": ...
    elif action == "diff": ...
    elif action == "commit": ...
```

## Mock/Placeholder Policy - MANDATORY
**Always mark non-test mocks with FIXME comments.**

```python
# ❌ FORBIDDEN - Unmarked placeholder
def process_data(params):
    return {"success": True}  # Hidden fake implementation

# ✅ REQUIRED - Clearly marked placeholder
def process_data(params):
    # FIXME: Placeholder implementation - returns fake values
    # TODO: Implement real processing
    return {"success": True}  # FIXME: Hardcoded value
```

**Rules**:
- Production code: ALWAYS add `# FIXME:` comment
- Test files: Mocks are intentional, no FIXME needed
- Temporary implementations: Must have FIXME + TODO

## File Management
- **Update Existing Files**: Always modify rather than create new versions
- **No Variants**: Never create `enhanced_`, `optimized_`, `v2_` variants
- **Minimal File Count**: Smallest number that maintains best practices
- **Single Source of Truth**: Each concept in exactly one location