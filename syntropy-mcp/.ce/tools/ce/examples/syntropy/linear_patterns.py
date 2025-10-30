"""
Linear MCP Project Management Patterns

Linear provides issue tracking operations through Syntropy.
Pattern: mcp__syntropy__linear__<operation>
"""


# ✅ PATTERN 1: Create Issue
# Use when: Generate new task from PRP or feature request
def example_create_issue():
    """Create new Linear issue."""
    from mcp__syntropy import syntropy_linear_create_issue
    
    result = syntropy_linear_create_issue(
        team="Blaise78",
        title="PRP-18: Syntropy Server Examples",
        description="""
        Add example patterns for all Syntropy servers.
        
        ## Tasks
        - [ ] Add serena_patterns.py
        - [ ] Add filesystem_patterns.py
        - [ ] Add git_patterns.py
        - [ ] Add linear_patterns.py
        
        ## Acceptance Criteria
        - All patterns documented with examples
        - Error handling demonstrated
        - Anti-patterns highlighted
        """,
        assignee="blazej.przybyszewski@gmail.com"
    )
    # Returns: {id: "BLA-123", identifier: "BLA-123", ...}
    print(f"✅ Created issue: {result['identifier']}")


# ✅ PATTERN 2: List Issues
# Use when: Check project status, find assigned work
def example_list_issues():
    """List issues with optional filtering."""
    from mcp__syntropy import syntropy_linear_list_issues
    
    # List all issues in project
    result = syntropy_linear_list_issues(team="Blaise78")
    print(f"📊 Total issues: {len(result)}")
    
    # List my assigned issues
    result = syntropy_linear_list_issues(
        team="Blaise78",
        assignee="blazej.przybyszewski@gmail.com"
    )
    
    for issue in result:
        print(f"{issue['id']} - {issue['title']} [{issue['status']}]")


# ✅ PATTERN 3: Get Issue Details
# Use when: Read issue description, see comments, check status
def example_get_issue():
    """Retrieve specific issue details."""
    from mcp__syntropy import syntropy_linear_get_issue
    
    result = syntropy_linear_get_issue(issue_id="BLA-123")
    # Returns: {
    #     id: "BLA-123",
    #     identifier: "BLA-123",
    #     title: "...",
    #     description: "...",
    #     status: "in_progress",
    #     assignee: {...},
    #     created_at: "...",
    #     updated_at: "...",
    #     labels: [...]
    # }
    
    print(f"Issue: {result['identifier']}")
    print(f"Status: {result['status']}")
    print(f"Assigned to: {result['assignee']['displayName']}")


# ✅ PATTERN 4: Update Issue
# Use when: Change status, update assignee, modify description
def example_update_issue():
    """Update issue properties."""
    from mcp__syntropy import syntropy_linear_update_issue
    
    # Update status
    result = syntropy_linear_update_issue(
        issue_id="BLA-123",
        updates={
            "state": "in_progress"  # todo, in_progress, completed, cancelled
        }
    )
    
    # Update multiple fields
    result = syntropy_linear_update_issue(
        issue_id="BLA-123",
        updates={
            "title": "PRP-18: Complete Syntropy Examples",
            "description": "Add patterns for all servers with error handling",
            "state": "in_progress"
        }
    )
    
    if result.get("success"):
        print("✅ Issue updated")
    else:
        print(f"❌ Update failed: {result.get('error')}")


# ✅ PATTERN 5: List Projects
# Use when: Find available projects for issue creation
def example_list_projects():
    """List all Linear projects."""
    from mcp__syntropy import syntropy_linear_list_projects
    
    result = syntropy_linear_list_projects()
    # Returns: List of projects
    
    for project in result:
        print(f"📁 {project['name']} (ID: {project['id']})")


# 📊 PERFORMANCE CHARACTERISTICS
# - create_issue: O(1) - immediate creation
# - list_issues: O(n) where n = issues in project
# - get_issue: O(1) - direct lookup
# - update_issue: O(1) - immediate update
# - list_projects: O(1) - cached


# 🎯 WORKFLOW EXAMPLE: PRP Integration
def prp_integration_workflow():
    """Typical workflow: Generate PRP → Create issue → Track."""
    from mcp__syntropy import (
        syntropy_linear_create_issue,
        syntropy_linear_get_issue,
        syntropy_linear_update_issue
    )
    
    # Step 1: /generate-prp creates PRP and automatically creates issue
    # (This happens in generate.py workflow)
    
    # Step 2: Get issue ID from PRP YAML header
    # prp_yaml["issue"] = "BLA-123"
    
    # Step 3: Update issue status as we progress
    syntropy_linear_update_issue(
        issue_id="BLA-123",
        updates={"state": "in_progress"}
    )
    
    # Step 4: Check progress
    issue = syntropy_linear_get_issue(issue_id="BLA-123")
    print(f"📊 Status: {issue['status']}")
    
    # Step 5: Mark done when complete
    syntropy_linear_update_issue(
        issue_id="BLA-123",
        updates={"state": "completed"}
    )


# 🎯 WORKFLOW EXAMPLE: Issue Triage
def triage_workflow():
    """Typical workflow: Daily triage of new issues."""
    from mcp__syntropy import (
        syntropy_linear_list_issues,
        syntropy_linear_get_issue,
        syntropy_linear_update_issue
    )
    
    # Get all open issues
    issues = syntropy_linear_list_issues(team="Blaise78")
    
    # Filter unstarted
    unstarted = [i for i in issues if i['status'] == 'todo']
    
    for issue in unstarted[:5]:  # Process first 5
        print(f"\n🔍 Reviewing: {issue['id']} - {issue['title']}")
        
        # Get full details
        details = syntropy_linear_get_issue(issue_id=issue['id'])
        print(f"Description: {details['description'][:100]}...")
        
        # Update if ready
        if is_ready_to_start(details):
            syntropy_linear_update_issue(
                issue_id=issue['id'],
                updates={
                    "state": "in_progress",
                    "assignee": "blazej.przybyszewski@gmail.com"
                }
            )
            print(f"✅ Started: {issue['id']}")


# 🎯 WORKFLOW EXAMPLE: Joining Multiple PRPs to Same Issue
def join_prp_workflow():
    """Workflow: Related PRPs sharing one Linear issue."""
    from mcp__syntropy import (
        syntropy_linear_create_issue,
        syntropy_linear_update_issue
    )
    
    # First PRP creates issue
    # /generate-prp auth-part1.md → Creates BLA-25 + PRP-10
    
    # Second related PRP joins same issue
    # /generate-prp auth-part2.md --join-prp 10
    # → Creates PRP-11, uses BLA-25 from PRP-10
    
    # Both PRPs now reference same Linear issue
    # Issue description includes both PRP details
    # Simplifies tracking related work


# 🔧 ERROR HANDLING PATTERNS

# ✅ PATTERN: Safe Update with Validation
def safe_update_pattern():
    """Update issue safely with pre-validation."""
    from mcp__syntropy import (
        syntropy_linear_get_issue,
        syntropy_linear_update_issue
    )
    
    issue_id = "BLA-123"
    
    # Step 1: Get current state
    current = syntropy_linear_get_issue(issue_id=issue_id)
    
    # Step 2: Validate transition
    valid_transitions = {
        "todo": ["in_progress", "cancelled"],
        "in_progress": ["completed", "cancelled", "todo"],
        "completed": ["todo"],
        "cancelled": ["todo"]
    }
    
    new_state = "in_progress"
    if new_state not in valid_transitions.get(current['status'], []):
        raise ValueError(
            f"❌ Invalid state transition: {current['status']} → {new_state}\n"
            f"🔧 Valid transitions: {valid_transitions[current['status']]}"
        )
    
    # Step 3: Update
    result = syntropy_linear_update_issue(
        issue_id=issue_id,
        updates={"state": new_state}
    )
    
    if not result.get("success"):
        raise RuntimeError(f"🔧 Update failed: {result.get('error')}")


# ✅ PATTERN: Batch Issue Creation
def batch_create_pattern():
    """Create multiple related issues."""
    from mcp__syntropy import syntropy_linear_create_issue
    
    features = [
        ("Feature 1", "Description 1"),
        ("Feature 2", "Description 2"),
        ("Feature 3", "Description 3")
    ]
    
    created_issues = []
    for title, description in features:
        result = syntropy_linear_create_issue(
            team="Blaise78",
            title=title,
            description=description,
            assignee="blazej.przybyszewski@gmail.com"
        )
        created_issues.append(result['id'])
        print(f"✅ Created: {result['identifier']}")
    
    return created_issues


# ✅ PATTERN: Track Implementation Progress
def track_progress_pattern():
    """Update issue status as implementation progresses."""
    from mcp__syntropy import syntropy_linear_update_issue
    
    issue_id = "BLA-123"
    
    # Phase 1: Research & Design
    syntropy_linear_update_issue(
        issue_id=issue_id,
        updates={
            "state": "in_progress",
            "description": "Phase 1: Research & Design - IN PROGRESS"
        }
    )
    print("📋 Phase 1: Research & Design")
    
    # Phase 2: Implementation
    syntropy_linear_update_issue(
        issue_id=issue_id,
        updates={
            "description": "Phase 2: Implementation - IN PROGRESS"
        }
    )
    print("🔨 Phase 2: Implementation")
    
    # Phase 3: Testing & Review
    syntropy_linear_update_issue(
        issue_id=issue_id,
        updates={
            "description": "Phase 3: Testing & Review - IN PROGRESS"
        }
    )
    print("✅ Phase 3: Testing & Review")
    
    # Complete
    syntropy_linear_update_issue(
        issue_id=issue_id,
        updates={
            "state": "completed",
            "description": "✅ All phases complete"
        }
    )


# 🔧 TROUBLESHOOTING
def troubleshooting():
    """Common issues and solutions."""
    # Issue: create_issue returns 401 Unauthorized
    # Solution: Check Linear API token in environment
    # Set: export LINEAR_API_KEY=...
    
    # Issue: Team ID not found
    # Solution: Use list_projects() to find correct team ID
    # Common teams: "Blaise78", check .ce/linear-defaults.yml
    
    # Issue: Issue update fails silently
    # Solution: Check update permissions
    # Verify assignee email is valid in Linear
    
    # Issue: Can't find issue after creation
    # Solution: Linear has eventual consistency
    # Issue may take 1-2 seconds to appear in list
    # Use get_issue(issue_id) immediately
    
    # Issue: Invalid state transition
    # Solution: Check current state first
    # Use get_issue() to see valid transitions
    # Linear state machine: todo → in_progress → completed


def is_ready_to_start(issue: dict) -> bool:
    """Check if issue is ready to start implementation."""
    # Stub for triage workflow
    return True
