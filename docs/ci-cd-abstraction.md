# CI/CD Pipeline Abstraction

## Overview

Platform-agnostic CI/CD pipeline definition system enabling:
- **Portable pipeline definitions** - Abstract YAML format independent of CI/CD platform
- **Multi-platform support** - GitHub Actions (MVP), future: GitLab CI, Jenkins
- **Structure validation** - Catch errors before execution
- **Testable configurations** - Mock executor for testing without cloud execution

## Architecture

```
Abstract Pipeline (YAML)
         ↓
  Executor Interface (Protocol)
         ↓
   ┌─────┴─────┐
   ↓           ↓
GitHub Actions  (Future platforms)
```

**Components**:
- **Abstract Schema** - Platform-neutral YAML pipeline definition
- **PipelineExecutor Protocol** - Interface for platform-specific renderers
- **GitHub Actions Executor** - Renders to `.github/workflows/*.yml`
- **Mock Executor** - Testing without execution

## Quick Start

### 1. Define Abstract Pipeline

Create `ci/abstract/my-pipeline.yml`:

```yaml
name: my-pipeline
description: Example pipeline

stages:
  - name: build
    nodes:
      - name: compile
        command: make build
        timeout: 300
    parallel: false

  - name: test
    nodes:
      - name: unit-tests
        command: pytest tests/unit/ -v
        timeout: 600
    parallel: false
    depends_on: [build]
```

### 2. Validate Pipeline

```bash
cd tools
uv run ce pipeline validate ../ci/abstract/my-pipeline.yml
```

**Output**:
```
✅ Pipeline validation passed
```

### 3. Render to GitHub Actions

```bash
uv run ce pipeline render ../ci/abstract/my-pipeline.yml \
  --executor github-actions \
  -o ../.github/workflows/my-pipeline.yml
```

**Output**:
```
✅ Rendered to ../.github/workflows/my-pipeline.yml
```

## Abstract Pipeline Schema

### Required Fields

- `name` (string) - Pipeline name
- `stages` (array) - Pipeline stages

### Stage Fields

- `name` (string, required) - Stage name
- `nodes` (array, required) - Stage nodes/steps
- `parallel` (boolean, optional) - Run nodes in parallel
- `depends_on` (array of strings, optional) - Stage dependencies

### Node Fields

- `name` (string, required) - Node name
- `command` (string, required) - Shell command to execute
- `timeout` (integer, optional) - Timeout in seconds
- `strategy` (string, optional) - "real" or "mock" (for testing)

### Example with All Features

```yaml
name: comprehensive-pipeline
description: Shows all features

stages:
  # Stage 1: Lint (no dependencies)
  - name: lint
    nodes:
      - name: markdown-lint
        command: npm run lint:md
        timeout: 60
      - name: python-lint
        command: ruff check .
        timeout: 120
    parallel: false

  # Stage 2: Test (depends on lint, parallel nodes)
  - name: test
    nodes:
      - name: unit-tests
        command: pytest tests/unit/ -v
        timeout: 300
      - name: integration-tests
        command: pytest tests/integration/ -v
        timeout: 600
    parallel: true
    depends_on: [lint]

  # Stage 3: Deploy (depends on test)
  - name: deploy
    nodes:
      - name: deploy-staging
        command: ./deploy.sh staging
        timeout: 900
    parallel: false
    depends_on: [test]
```

## Platform Mappings

### GitHub Actions

| Abstract | GitHub Actions |
|----------|----------------|
| `stages` | `jobs` |
| `nodes` | `steps` |
| `depends_on` | `needs` |
| `timeout` (seconds) | `timeout-minutes` (minutes) |
| `parallel: true` | Jobs without `needs` field |

**Automatic Additions**:
- Checkout step (`actions/checkout@v4`) added to all jobs
- Trigger: `on: [push, pull_request]`
- Runner: `runs-on: ubuntu-latest`

## CLI Commands

### pipeline validate

Validate abstract pipeline structure and dependencies.

```bash
ce pipeline validate <pipeline-file>
```

**Example**:
```bash
cd tools
uv run ce pipeline validate ../ci/abstract/validation.yml
```

**Success Output**:
```
✅ Pipeline validation passed
```

**Failure Output**:
```
❌ Pipeline validation failed:
  - Stage 'test' depends on unknown stage 'nonexistent'
  - 🔧 Troubleshooting: Available stages: [lint, build]
```

### pipeline render

Render abstract pipeline to platform-specific format.

```bash
ce pipeline render <pipeline-file> [--executor <type>] [-o <output>]
```

**Options**:
- `--executor`: Platform executor (`github-actions`, `mock`)
- `-o, --output`: Output file path (stdout if not specified)

**Examples**:
```bash
# Render to stdout
uv run ce pipeline render ../ci/abstract/validation.yml

# Render to file
uv run ce pipeline render ../ci/abstract/validation.yml \
  --executor github-actions \
  -o ../.github/workflows/ci.yml

# Test with mock executor
uv run ce pipeline render ../ci/abstract/validation.yml --executor mock
```

## Validation Rules

### Schema Validation

- Required fields: `name`, `stages`
- Each stage must have: `name`, `nodes`
- Each node must have: `name`, `command`

### Semantic Validation

- **Dependency validation**: `depends_on` stages must exist
- **No circular dependencies**: (future enhancement)
- **Valid timeout**: Must be positive integer

### Error Messages

All validation errors include:
- Clear description of the problem
- 🔧 Troubleshooting guidance
- Context (e.g., available stages for invalid `depends_on`)

## Adding New Executors

### 1. Implement PipelineExecutor Protocol

```python
from ce.executors.base import BaseExecutor, PipelineExecutor
from typing import Dict, Any

class GitLabCIExecutor(BaseExecutor):
    def render(self, pipeline: Dict[str, Any]) -> str:
        # Render to GitLab CI YAML format
        gitlab_ci = {
            "stages": [s["name"] for s in pipeline["stages"]],
            # ... map abstract pipeline to GitLab CI
        }
        return self.format_yaml(gitlab_ci)

    def validate_output(self, output: str) -> Dict[str, Any]:
        # Validate GitLab CI YAML
        pass

    def get_platform_name(self) -> str:
        return "gitlab-ci"
```

### 2. Add to CLI

Update `tools/ce/__main__.py`:

```python
from .executors.gitlab_ci import GitLabCIExecutor

# In pipeline render command:
elif args.executor == "gitlab-ci":
    executor = GitLabCIExecutor()
```

### 3. Add Tests

Create `tools/tests/test_gitlab_ci.py`:

```python
def test_gitlab_ci_render():
    executor = GitLabCIExecutor()
    pipeline = load_abstract_pipeline("test.yml")
    output = executor.render(pipeline)
    # Assert GitLab CI format
```

## Testing

### Unit Tests

```bash
cd tools
uv run pytest tests/test_pipeline.py tests/test_executors.py -v
```

### Integration Tests

```bash
uv run pytest tests/test_github_actions.py -v
```

### Coverage

```bash
uv run pytest tests/test_pipeline.py tests/test_executors.py tests/test_github_actions.py \
  --cov=ce.pipeline --cov=ce.executors --cov-report=term-missing
```

## Best Practices

### Pipeline Design

1. **Keep stages focused** - Each stage has single responsibility
2. **Use dependencies wisely** - Only add `depends_on` when necessary
3. **Parallelize independent work** - Set `parallel: true` for concurrent nodes
4. **Set reasonable timeouts** - Prevent runaway processes

### Naming Conventions

- **Stages**: Lowercase with hyphens (`build`, `run-tests`)
- **Nodes**: Descriptive names (`unit-tests`, `deploy-staging`)
- **Files**: Match pipeline name (`validation.yml`, `deployment.yml`)

### Validation Workflow

1. **Validate locally** before committing
2. **Test with mock executor** to verify structure
3. **Render to file** and review output
4. **Commit rendered workflows** to `.github/workflows/`

## Troubleshooting

### Validation Fails with "Pipeline file not found"

**Cause**: Incorrect file path

**Solution**: Use path relative to current directory
```bash
cd tools
uv run ce pipeline validate ../ci/abstract/validation.yml
```

### Rendered Workflow Invalid on GitHub

**Cause**: Platform-specific features not in abstract schema

**Solution**: Keep abstract pipelines simple, add platform-specific features manually if needed

### Timeout Too Short

**Cause**: Timeout in seconds, but execution takes longer

**Solution**: Increase timeout value (will be converted to minutes for GitHub Actions)

```yaml
nodes:
  - name: long-test
    command: pytest tests/
    timeout: 1800  # 30 minutes
```

## Examples

### Basic CI Pipeline

```yaml
name: ci
description: Continuous integration

stages:
  - name: test
    nodes:
      - name: pytest
        command: pytest tests/ -v
        timeout: 600
```

### Multi-Stage Pipeline

```yaml
name: build-test-deploy
description: Full pipeline

stages:
  - name: build
    nodes:
      - name: compile
        command: make build
    parallel: false

  - name: test
    nodes:
      - name: unit
        command: pytest tests/unit/
      - name: integration
        command: pytest tests/integration/
    parallel: true
    depends_on: [build]

  - name: deploy
    nodes:
      - name: deploy-prod
        command: ./deploy.sh
    depends_on: [test]
```

## Future Enhancements

- **GitLab CI executor** - Render to `.gitlab-ci.yml`
- **Jenkins executor** - Generate Jenkinsfile
- **Matrix builds** - Parameterized job execution
- **Artifacts** - Pass files between stages
- **Environment variables** - Configurable per-stage
- **Conditional execution** - Run stages based on conditions
- **DAG visualization** - Generate pipeline diagrams

## References

- [GitHub Actions Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [Protocol Pattern (PEP 544)](https://peps.python.org/pep-0544/)
- [Strategy Pattern](https://refactoring.guru/design-patterns/strategy)
