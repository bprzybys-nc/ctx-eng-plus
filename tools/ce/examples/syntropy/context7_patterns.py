"""
Context7 MCP Documentation Lookup Patterns

Context7 provides library documentation access through Syntropy.
Pattern: mcp__syntropy__context7__<operation>
"""


# ✅ PATTERN 1: Resolve Library ID
# Use when: Get machine-readable library identifier from human-readable name
def example_resolve_library_id():
    """Convert library name to Context7 ID."""
    from mcp__syntropy import syntropy_context7_resolve_library_id
    
    # Common libraries
    libraries = [
        "pytest",
        "fastapi",
        "django",
        "sqlalchemy",
        "pydantic",
        "numpy",
        "react",
        "typescript"
    ]
    
    for lib_name in libraries:
        lib_id = syntropy_context7_resolve_library_id(
            libraryName=lib_name
        )
        print(f"📚 {lib_name} → {lib_id}")
    
    # Returns: Context7-compatible ID (e.g., "/pytest/docs")


# ✅ PATTERN 2: Get Library Documentation
# Use when: Fetch API docs, usage patterns, configuration
def example_get_library_docs():
    """Fetch library documentation with optional topic focus."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    # Step 1: Resolve library ID
    lib_id = syntropy_context7_resolve_library_id(libraryName="pytest")
    
    # Step 2: Get documentation
    docs = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="fixtures",
        tokens=5000  # Max tokens in response
    )
    print(f"📖 Pytest fixtures documentation:\n{docs}")


# ✅ PATTERN 3: Get FastAPI Documentation
# Use when: Building FastAPI applications, need API patterns
def example_fastapi_docs():
    """FastAPI documentation for common patterns."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    lib_id = syntropy_context7_resolve_library_id(libraryName="fastapi")
    
    # Get routing docs
    routing = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="routing",
        tokens=3000
    )
    
    # Get dependency injection docs
    di = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="dependency-injection",
        tokens=3000
    )
    
    # Get async patterns
    async_patterns = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="async",
        tokens=2000
    )


# ✅ PATTERN 4: Get Django Documentation
# Use when: Building Django applications, need ORM/views patterns
def example_django_docs():
    """Django documentation for common patterns."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    lib_id = syntropy_context7_resolve_library_id(libraryName="django")
    
    # Get ORM docs
    orm = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="orm-models",
        tokens=4000
    )
    
    # Get views/requests
    views = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="views-requests",
        tokens=3000
    )
    
    # Get middleware patterns
    middleware = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="middleware",
        tokens=2000
    )


# ✅ PATTERN 5: Get SQLAlchemy Documentation
# Use when: Database operations, ORM patterns
def example_sqlalchemy_docs():
    """SQLAlchemy documentation for database operations."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    lib_id = syntropy_context7_resolve_library_id(libraryName="sqlalchemy")
    
    # Get session management
    sessions = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="session-management",
        tokens=3000
    )
    
    # Get query patterns
    queries = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="queries",
        tokens=3000
    )
    
    # Get relationships
    relationships = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="relationships",
        tokens=2000
    )


# ✅ PATTERN 6: Get Pydantic Documentation
# Use when: Data validation, schema definition
def example_pydantic_docs():
    """Pydantic documentation for data validation."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    lib_id = syntropy_context7_resolve_library_id(libraryName="pydantic")
    
    # Get validation docs
    validation = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="validation",
        tokens=3000
    )
    
    # Get field types
    fields = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="field-types",
        tokens=2000
    )


# ✅ PATTERN 7: Get React Documentation
# Use when: Frontend development, component patterns
def example_react_docs():
    """React documentation for common patterns."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    lib_id = syntropy_context7_resolve_library_id(libraryName="react")
    
    # Get hooks
    hooks = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="hooks",
        tokens=4000
    )
    
    # Get state management
    state = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="state-management",
        tokens=3000
    )


# 📊 PERFORMANCE CHARACTERISTICS
# - resolve_library_id: O(1) - cached lookup
# - get_library_docs: O(1) - API call with caching
# - Token limit: 5000 max (adjust topic to fit)
# - Response time: ~500ms-2s depending on network


# 🎯 WORKFLOW EXAMPLE: Knowledge-Grounded PRP Generation
def knowledge_grounded_prp_workflow():
    """Workflow: Generate PRP with real library documentation."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    # Feature: Build FastAPI service
    # Step 1: Get FastAPI best practices
    lib_id = syntropy_context7_resolve_library_id(libraryName="fastapi")
    
    routing_docs = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="routing",
        tokens=2000
    )
    
    di_docs = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=lib_id,
        topic="dependency-injection",
        tokens=2000
    )
    
    # Step 2: Use real docs in PRP context
    # This ensures PRP reflects actual FastAPI patterns
    # Not guesses or outdated knowledge
    
    # Step 3: Generate PRP with real examples
    # PRP will include:
    # - Actual FastAPI routing patterns
    # - Real dependency injection patterns
    # - Correct async patterns
    # - Current best practices
    
    print("✅ PRP generated with knowledge-grounded FastAPI documentation")


# 🎯 WORKFLOW EXAMPLE: Framework Comparison
def framework_comparison_workflow():
    """Workflow: Compare patterns across frameworks."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    # Async patterns in FastAPI vs Django
    
    # FastAPI
    fastapi_id = syntropy_context7_resolve_library_id(libraryName="fastapi")
    fastapi_async = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=fastapi_id,
        topic="async",
        tokens=2000
    )
    
    # Django
    django_id = syntropy_context7_resolve_library_id(libraryName="django")
    django_async = syntropy_context7_get_library_docs(
        context7CompatibleLibraryID=django_id,
        topic="async",
        tokens=2000
    )
    
    print("📊 FastAPI async patterns:")
    print(fastapi_async)
    print("\n📊 Django async patterns:")
    print(django_async)


# 🎯 WORKFLOW EXAMPLE: Multi-library Integration
def multi_library_workflow():
    """Workflow: Build service using multiple libraries."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    # Feature: Build REST API with auth
    # Libraries: FastAPI, SQLAlchemy, Pydantic, pytest
    
    docs_cache = {}
    
    for lib_name in ["fastapi", "sqlalchemy", "pydantic", "pytest"]:
        lib_id = syntropy_context7_resolve_library_id(libraryName=lib_name)
        
        docs = syntropy_context7_get_library_docs(
            context7CompatibleLibraryID=lib_id,
            topic="getting-started",  # Start with basics
            tokens=2000
        )
        
        docs_cache[lib_name] = docs
    
    # Now have real documentation for all libraries
    # Use to generate accurate PRP with integration patterns


# 🔧 ERROR HANDLING PATTERNS

# ✅ PATTERN: Graceful Library Lookup
def graceful_lookup_pattern():
    """Handle missing or unmapped libraries gracefully."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    def get_docs_safe(lib_name: str, topic: str) -> dict:
        try:
            # Try to resolve library
            lib_id = syntropy_context7_resolve_library_id(
                libraryName=lib_name
            )
            
            # Get documentation
            docs = syntropy_context7_get_library_docs(
                context7CompatibleLibraryID=lib_id,
                topic=topic,
                tokens=3000
            )
            
            return {
                "success": True,
                "docs": docs,
                "library": lib_name
            }
            
        except Exception as e:
            # Library not found or error
            return {
                "success": False,
                "error": str(e),
                "library": lib_name,
                "troubleshooting": f"🔧 Library '{lib_name}' not available in Context7. "
                                 f"Check spelling or see supported libraries."
            }


# ✅ PATTERN: Token Budget Management
def token_budget_pattern():
    """Manage documentation token budget efficiently."""
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    # For large feature with multiple libraries
    TOTAL_TOKENS = 15000
    TOKENS_PER_LIB = 3000
    
    libraries = ["fastapi", "sqlalchemy", "pydantic"]
    
    for lib_name in libraries:
        lib_id = syntropy_context7_resolve_library_id(libraryName=lib_name)
        
        docs = syntropy_context7_get_library_docs(
            context7CompatibleLibraryID=lib_id,
            topic="best-practices",  # Concise topic
            tokens=TOKENS_PER_LIB
        )
        
        print(f"📚 {lib_name}: {len(docs.split())} words")


# ✅ PATTERN: Cache Documentation Locally
def caching_pattern():
    """Cache documentation to avoid repeated requests."""
    import json
    from pathlib import Path
    from mcp__syntropy import (
        syntropy_context7_resolve_library_id,
        syntropy_context7_get_library_docs
    )
    
    CACHE_DIR = Path("/tmp/context7-cache")
    CACHE_DIR.mkdir(exist_ok=True)
    
    def get_docs_cached(lib_name: str, topic: str) -> str:
        cache_file = CACHE_DIR / f"{lib_name}_{topic}.md"
        
        # Return cached if exists
        if cache_file.exists():
            return cache_file.read_text()
        
        # Fetch from Context7
        lib_id = syntropy_context7_resolve_library_id(libraryName=lib_name)
        docs = syntropy_context7_get_library_docs(
            context7CompatibleLibraryID=lib_id,
            topic=topic,
            tokens=3000
        )
        
        # Cache for future use
        cache_file.write_text(docs)
        return docs


# 🔧 TROUBLESHOOTING
def troubleshooting():
    """Common issues and solutions."""
    # Issue: resolve_library_id returns None
    # Solution: Library name may be misspelled or not in Context7
    # Try: "pytest" not "py-test"
    # Try: "django" not "django-framework"
    
    # Issue: get_library_docs returns incomplete documentation
    # Solution: Increase tokens parameter
    # Try: tokens=5000 (maximum)
    # Or narrow topic: "routing" not "all"
    
    # Issue: Documentation outdated or wrong version
    # Solution: Context7 may not have latest version
    # Check documentation date in response
    # Cross-reference with official project docs
    
    # Issue: Rate limiting / timeout
    # Solution: Wait before next request
    # Cache results to avoid repeated requests
    # Check Context7 rate limits


# 📚 SUPPORTED LIBRARIES
def supported_libraries():
    """Commonly available libraries in Context7."""
    return {
        "python": [
            "pytest",
            "fastapi",
            "django",
            "sqlalchemy",
            "pydantic",
            "numpy",
            "pandas",
            "requests",
            "celery",
            "redis"
        ],
        "javascript": [
            "react",
            "typescript",
            "nodejs",
            "express",
            "next.js",
            "vue",
            "angular"
        ],
        "other": [
            "docker",
            "kubernetes",
            "postgresql",
            "mongodb"
        ]
    }


# 💡 BEST PRACTICES
def best_practices():
    """Context7 usage best practices."""
    return {
        "do": [
            "✅ Resolve library ID once, reuse multiple times",
            "✅ Cache documentation locally to reduce API calls",
            "✅ Use specific topics to fit token budget",
            "✅ Include documentation links in generated PRPs",
            "✅ Cross-reference with official docs",
            "✅ Verify documentation is for correct version"
        ],
        "dont": [
            "❌ Assume documentation is 100% current",
            "❌ Use outdated library knowledge from training",
            "❌ Ignore token limits",
            "❌ Fetch entire library docs at once",
            "❌ Trust incomplete or partial documentation",
            "❌ Skip validation of documentation patterns"
        ]
    }
