"""
Git MCP Version Control Patterns

Git provides version control operations through Syntropy.
Pattern: mcp__syntropy__git__<operation>
"""


# ✅ PATTERN 1: Check Repository Status
# Use when: Understand current state before making changes
def example_git_status():
    """Get repository status (staged, unstaged, untracked)."""
    from mcp__syntropy import syntropy_git_git_status
    
    result = syntropy_git_git_status(repo_path="/Users/bprzybysz/nc-src/ctx-eng-plus")
    # Returns: {
    #     clean: bool,
    #     staged: [files],
    #     unstaged: [files],
    #     untracked: [files],
    #     branch: current_branch,
    #     ahead: commits_ahead,
    #     behind: commits_behind
    # }
    
    if result.get("clean"):
        print("✅ Repository is clean")
    else:
        print(f"📝 Unstaged: {len(result['unstaged'])} files")
        print(f"✏️ Staged: {len(result['staged'])} files")


# ✅ PATTERN 2: View Recent Changes
# Use when: Review what changed before committing
def example_git_diff():
    """View recent changes (staged or unstaged)."""
    from mcp__syntropy import syntropy_git_git_diff
    
    # Show unstaged changes
    result = syntropy_git_git_diff(
        repo_path="/Users/bprzybysz/nc-src/ctx-eng-plus",
        staged=False
    )
    # Returns: Unified diff format
    
    # Show staged changes only
    result = syntropy_git_git_diff(
        repo_path="/Users/bprzybysz/nc-src/ctx-eng-plus",
        staged=True
    )
    print(result)


# ✅ PATTERN 3: View Commit History
# Use when: Understand project history, find commits
def example_git_log():
    """View commit history."""
    from mcp__syntropy import syntropy_git_git_log
    
    # Get last 10 commits
    result = syntropy_git_git_log(
        repo_path="/Users/bprzybysz/nc-src/ctx-eng-plus",
        max_count=10
    )
    # Returns: List of commits with:
    # - SHA
    # - Author
    # - Date
    # - Message
    
    for commit in result:
        print(f"{commit['sha'][:7]} - {commit['message']}")


# ✅ PATTERN 4: Stage Files for Commit
# Use when: Prepare specific files before committing
def example_git_add():
    """Stage files for commit."""
    from mcp__syntropy import syntropy_git_git_add
    
    # Stage specific files
    result = syntropy_git_git_add(
        repo_path="/Users/bprzybysz/nc-src/ctx-eng-plus",
        paths=[
            "tools/ce/core.py",
            "tools/tests/test_core.py"
        ]
    )
    # Returns: {success: bool, message: str}
    
    if result.get("success"):
        print("✅ Files staged successfully")
    else:
        print(f"❌ Staging failed: {result['message']}")


# ✅ PATTERN 5: Create Commit
# Use when: Save changes with descriptive message
def example_git_commit():
    """Create commit with message."""
    from mcp__syntropy import syntropy_git_git_commit
    
    # Create commit
    result = syntropy_git_git_commit(
        repo_path="/Users/bprzybysz/nc-src/ctx-eng-plus",
        message="""feat: Add Syntropy server examples

- Add serena_patterns.py for code navigation
- Add filesystem_patterns.py for file operations
- Add git_patterns.py for version control
- Add linear_patterns.py for issue tracking
- Add context7_patterns.py for documentation lookup

🤖 Generated with Claude Code"""
    )
    # Returns: {success: bool, sha: commit_hash, message: str}


# 📊 PERFORMANCE CHARACTERISTICS
# - git_status: O(files) - scans working directory
# - git_diff: O(changes) - computes diff
# - git_log: O(commits) - scans history
# - git_add: O(files) - stages files
# - git_commit: O(1) - creates commit object


# 🎯 WORKFLOW EXAMPLE: Complete Commit Cycle
def complete_commit_workflow():
    """Typical workflow: Check status → review → stage → commit."""
    from mcp__syntropy import (
        syntropy_git_git_status,
        syntropy_git_git_diff,
        syntropy_git_git_add,
        syntropy_git_git_commit
    )
    
    repo = "/Users/bprzybysz/nc-src/ctx-eng-plus"
    
    # Step 1: Check status
    status = syntropy_git_git_status(repo_path=repo)
    print(f"📊 Status: {len(status['unstaged'])} unstaged files")
    
    # Step 2: Review changes
    if status['unstaged']:
        diff = syntropy_git_git_diff(repo_path=repo, staged=False)
        print(f"📝 Changes:\n{diff[:500]}...")  # Show first 500 chars
    
    # Step 3: Stage files
    result = syntropy_git_git_add(
        repo_path=repo,
        paths=status['unstaged']  # Stage all unstaged changes
    )
    print(f"✏️ Staged: {len(status['unstaged'])} files")
    
    # Step 4: Create commit
    commit = syntropy_git_git_commit(
        repo_path=repo,
        message="refactor: Update Syntropy examples"
    )
    print(f"✅ Committed: {commit['sha'][:7]}")


# 🎯 WORKFLOW EXAMPLE: Selective Staging
def selective_staging_workflow():
    """Typical workflow: Stage only specific files."""
    from mcp__syntropy import (
        syntropy_git_git_status,
        syntropy_git_git_diff,
        syntropy_git_git_add,
        syntropy_git_git_commit
    )
    
    repo = "/Users/bprzybysz/nc-src/ctx-eng-plus"
    
    # Check status
    status = syntropy_git_git_status(repo_path=repo)
    
    # Filter: Only stage .py files, not .md files
    py_files = [f for f in status['unstaged'] if f.endswith('.py')]
    
    # Stage only Python files
    syntropy_git_git_add(repo_path=repo, paths=py_files)
    
    # Commit
    syntropy_git_git_commit(
        repo_path=repo,
        message="feat: Add new patterns"
    )
    print(f"✅ Committed {len(py_files)} Python files")


# 🎯 WORKFLOW EXAMPLE: Review Changes Before Commit
def review_workflow():
    """Typical workflow: Review staged changes before committing."""
    from mcp__syntropy import (
        syntropy_git_git_status,
        syntropy_git_git_diff,
        syntropy_git_git_log
    )
    
    repo = "/Users/bprzybysz/nc-src/ctx-eng-plus"
    
    # Check status
    status = syntropy_git_git_status(repo_path=repo)
    
    # View staged changes
    if status['staged']:
        diff = syntropy_git_git_diff(repo_path=repo, staged=True)
        print(f"📝 Staged changes:\n{diff}")
        
        # View recent commits for context
        history = syntropy_git_git_log(repo_path=repo, max_count=3)
        print("\n📜 Recent commits:")
        for commit in history:
            print(f"  {commit['sha'][:7]} - {commit['message']}")


# 🔧 ERROR HANDLING PATTERNS

# ✅ PATTERN: Safe Commit with Pre-flight Checks
def safe_commit_pattern():
    """Commit safely with validation."""
    from mcp__syntropy import (
        syntropy_git_git_status,
        syntropy_git_git_add,
        syntropy_git_git_commit
    )
    
    repo = "/Users/bprzybysz/nc-src/ctx-eng-plus"
    
    # Check status
    status = syntropy_git_git_status(repo_path=repo)
    
    # Validate
    if not status['unstaged']:
        print("✅ No changes to commit")
        return
    
    # Stage changes
    result = syntropy_git_git_add(repo_path=repo, paths=status['unstaged'])
    if not result.get('success'):
        raise RuntimeError(f"🔧 Staging failed: {result.get('message')}")
    
    # Create commit
    commit = syntropy_git_git_commit(
        repo_path=repo,
        message="feat: Update patterns"
    )
    
    if not commit.get('success'):
        raise RuntimeError(f"🔧 Commit failed: {commit.get('message')}")
    
    print(f"✅ Committed: {commit['sha'][:7]}")


# ✅ PATTERN: Batch Commits with Grouping
def batch_commits_pattern():
    """Create multiple commits for different change groups."""
    from mcp__syntropy import (
        syntropy_git_git_status,
        syntropy_git_git_add,
        syntropy_git_git_commit
    )
    
    repo = "/Users/bprzybysz/nc-src/ctx-eng-plus"
    status = syntropy_git_git_status(repo_path=repo)
    
    # Group 1: Examples
    example_files = [f for f in status['unstaged'] if 'examples/' in f]
    if example_files:
        syntropy_git_git_add(repo_path=repo, paths=example_files)
        syntropy_git_git_commit(
            repo_path=repo,
            message="docs: Add Syntropy server examples"
        )
    
    # Group 2: Tests
    test_files = [f for f in status['unstaged'] if 'test_' in f]
    if test_files:
        syntropy_git_git_add(repo_path=repo, paths=test_files)
        syntropy_git_git_commit(
            repo_path=repo,
            message="test: Update Syntropy tests"
        )


# 🔧 TROUBLESHOOTING
def troubleshooting():
    """Common issues and solutions."""
    # Issue: git_add returns empty paths
    # Solution: Use git_status first to get exact file paths
    # Git uses relative paths from repo root
    
    # Issue: Commit fails with "nothing to commit"
    # Solution: Verify files are staged with git_status (check staged list)
    # Use git_add before git_commit
    
    # Issue: git_diff returns empty
    # Solution: Check staged parameter (True for staged, False for unstaged)
    # Verify changes exist with git_status
    
    # Issue: git_log shows no commits
    # Solution: Repository may have no commits
    # Verify with git_status
    
    # Issue: Permission denied on commit
    # Solution: Check git config (user.name, user.email)
    # Verify repo permissions
