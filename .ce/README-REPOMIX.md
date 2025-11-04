# CE Framework Repomix Packages

Distribution packages for Context Engineering framework components.

## Overview

Two consolidated XML packages containing CE framework documentation and infrastructure:

1. **Workflow Documentation** (ce-32/builds/ce-workflow-docs.xml)
   - 15 files: 13 workflow examples (IsWorkflow=Yes) + CLAUDE.md + INDEX.md
   - Current size: 88,213 tokens (288,431 chars)
   - Target size: <60KB tokens (exceeds by 47%)
   - Location: ce-32/builds/ (development artifact for ctx-eng-plus)
   - Distribution: Will be refined in Phase 5 after doc optimization

2. **Infrastructure Files** (ce-32/builds/ce-infrastructure.xml)
   - 61 files total:
     - 13 framework examples → `.ce/examples/system/`
     - 23 framework memories (6 critical + 17 regular) → `.serena/memories/system/`
     - 11 framework slash commands → `.claude/commands/`
     - 27 CE tool source files → `tools/`
     - CLAUDE.md (complete file for blending)
   - Current size: 278,476 tokens (977,615 chars)
   - Target size: <150KB tokens (exceeds by 86%)
   - Requires: Post-processing for /system/ organization during extraction
   - Distribution: Will be refined in Phase 5 after doc optimization

**Total Size**: 366,689 tokens (target was <210K, exceeds by 75%)

**Status**: Initial generation complete. Phase 4 will refine documentation, Phase 5 will regenerate packages with optimized content to meet token targets.

## Package Contents

See [.ce/repomix-manifest.yml](.ce/repomix-manifest.yml) for detailed contents, file lists, and token breakdowns.

## Usage

### Generate Packages

```bash
# Workflow documentation package
npx repomix --config .ce/repomix-profile-workflow.json

# Infrastructure package
npx repomix --config .ce/repomix-profile-infrastructure.json

# Both packages
npx repomix --config .ce/repomix-profile-workflow.json && \
npx repomix --config .ce/repomix-profile-infrastructure.json
```

### Verify Token Counts

```bash
# Workflow package
wc -c ce-32/builds/ce-workflow-docs.xml
# Expected: ~288,431 chars (88,213 tokens)

# Infrastructure package
wc -c ce-32/builds/ce-infrastructure.xml
# Expected: ~977,615 chars (278,476 tokens)

# Total
du -h ce-32/builds/ce-*.xml
```

### View Generated Packages

```bash
# XML packages (AI-friendly format)
ls -lh ce-32/builds/ce-workflow-docs.xml
ls -lh ce-32/builds/ce-infrastructure.xml

# View in editor or XML viewer
code ce-32/builds/ce-workflow-docs.xml
code ce-32/builds/ce-infrastructure.xml
```

## Use Cases

### New Project Onboarding

```bash
# Copy workflow examples to new project
cp ce-32/builds/ce-workflow-docs.xml /path/to/new-project/docs/

# Initialize with infrastructure
cp ce-32/builds/ce-infrastructure.xml /path/to/new-project/docs/
```

### Distribution (Future)

```bash
# Upload to documentation site (after Phase 5 regeneration)
aws s3 cp ce-32/builds/ce-workflow-docs.xml s3://docs/ce-framework/

# Or attach to GitHub release
gh release upload v1.1 ce-32/builds/ce-workflow-docs.xml ce-32/builds/ce-infrastructure.xml
```

### Token Analysis

```bash
# Estimate token usage (rough: 1 token ≈ 4 chars)
echo "Workflow: $(($(wc -c < ce-32/builds/ce-workflow-docs.xml) / 4)) tokens"
echo "Infrastructure: $(($(wc -c < ce-32/builds/ce-infrastructure.xml) / 4)) tokens"
```

## Profiles

### Workflow Profile (.ce/repomix-profile-workflow.json)

- **Includes**:
  - examples/syntropy/*.md (6 files)
  - examples/workflows/*.md (5 files)
  - examples/config/*.md (2 files)
  - examples/patterns/dedrifting-lessons.md, examples/patterns/mocks-marking.md
  - examples/TOOL-USAGE-GUIDE.md, examples/INDEX.md
  - examples/model/SystemModel.md (35.6K tokens, 40% of package)
  - CLAUDE.md (complete file)
- **Excludes**: Project-specific examples (IsWorkflow=No in INDEX.md)
- **Output**: ce-32/builds/ce-workflow-docs.xml
- **Top Contributors**:
  - SystemModel.md: 35,618 tokens (40.4%)
  - CLAUDE.md: 7,714 tokens (8.7%)
  - TOOL-USAGE-GUIDE.md: 6,450 tokens (7.3%)

### Infrastructure Profile (.ce/repomix-profile-infrastructure.json)

- **Includes**:
  - 13 framework examples (same as workflow package)
  - 23 framework memories (6 critical + 17 regular)
  - 11 framework slash commands
  - 27 CE tool source files (*.py + pyproject.toml + bootstrap.sh)
  - CLAUDE.md (complete file)
- **Excludes**: Project-specific examples, tests/, .git/, .tmp/
- **Output**: ce-32/builds/ce-infrastructure.xml
- **Post-processing**: .ce/reorganize-infrastructure.sh adds /system/ organization
- **Top Contributors**:
  - SystemModel.md: 35,618 tokens (12.8%)
  - generate.py: 20,030 tokens (7.2%)
  - update_context.py: 20,020 tokens (7.2%)
  - batch-exe-prp.md: 10,772 tokens (3.9%)
  - batch-gen-prp.md: 9,951 tokens (3.6%)

## Regeneration

Packages will be regenerated in Phase 5 (PRP-32.5.1) after documentation refinement in Phase 4.

**Trigger**: Documentation updates or framework refinement

**Process**:
1. Phase 4: Refine documentation to reduce token counts
2. Phase 5: Regenerate packages with existing profiles
3. New packages incorporate optimized documentation
4. Manifest updated with new file counts/sizes
5. Target: <60KB workflow, <150KB infrastructure, <210KB total

**Timeline**: Phase 5 execution (after Phase 4 completion)

## Size Analysis

### Current Token Distribution

**Workflow Package (88,213 tokens)**:
- SystemModel.md: 35,618 tokens (40.4%) - Candidate for optimization
- CLAUDE.md: 7,714 tokens (8.7%)
- TOOL-USAGE-GUIDE.md: 6,450 tokens (7.3%)
- INDEX.md: 6,203 tokens (7%)
- Other 11 files: 32,228 tokens (36.6%)

**Infrastructure Package (278,476 tokens)**:
- SystemModel.md: 35,618 tokens (12.8%)
- generate.py: 20,030 tokens (7.2%)
- update_context.py: 20,020 tokens (7.2%)
- Commands (11 files): ~50,000 tokens (18%)
- Memories (23 files): ~60,000 tokens (21.5%)
- Other files: ~92,808 tokens (33.3%)

### Optimization Opportunities (Phase 4)

1. **SystemModel.md** (35.6K tokens): Primary optimization target
   - Consider splitting into modular sections
   - Extract diagrams to separate files
   - Reduce redundancy with other docs

2. **Large tool files** (generate.py, update_context.py: 40K tokens combined):
   - Review for inline documentation reduction
   - Extract large docstrings to separate docs

3. **Command files** (batch-exe-prp.md, batch-gen-prp.md: 20K tokens combined):
   - Compress verbose examples
   - Reference external documentation instead of inline

4. **CLAUDE.md** (7.7K tokens):
   - Extract project-specific sections
   - Keep only framework-level guidance

**Expected Reduction**: 30-40% token savings after Phase 4 optimization

## Notes

- **Initial Generation**: Uses current framework documentation as-is
- **Phase 4**: Documentation refinement and optimization
- **Phase 5**: Regenerate packages with optimized content
- **Size Monitoring**: Current packages exceed targets but provide complete functionality
- **Validation**: Profiles tested and working with repomix v1.8.0

## Troubleshooting

### Package Too Large

**Current Status**: Both packages exceed targets (expected for Phase 1)

**Solution**: Wait for Phase 4 documentation refinement and Phase 5 regeneration

**Manual Optimization** (if needed before Phase 5):
```bash
# Check file sizes
npx repomix --config .ce/repomix-profile-workflow.json --verbose

# Adjust exclude patterns in profiles to remove large files
# Edit .ce/repomix-profile-workflow.json or .ce/repomix-profile-infrastructure.json
```

### Missing Files

```bash
# Verify include patterns match files
find examples -name "*.md" | grep -v "examples/patterns/example-simple-feature"
find .serena/memories -name "*.md" | wc -l  # Should be 23
find .claude/commands -name "*.md" | wc -l  # Should be 11
```

### Repomix Not Found

```bash
# Install repomix globally
npm install -g repomix

# Or use npx (no install needed)
npx repomix --version
```

### Config Format Error

**Issue**: "Unsupported config file format"

**Solution**: Use JSON format (.json) not YAML (.yml)
- Correct: `.ce/repomix-profile-workflow.json`
- Incorrect: `.ce/repomix-profile-workflow.yml`

## Related Documentation

- [.ce/repomix-manifest.yml](.ce/repomix-manifest.yml) - Detailed package manifest
- [examples/INDEX.md](../examples/INDEX.md) - Example catalog with IsWorkflow classification
- [CLAUDE.md](../CLAUDE.md) - Project guide and framework documentation

---

**Version**: 1.0.0 (Initial Generation)
**Last Updated**: 2025-11-04
**Status**: Phase 1 complete, awaiting Phase 4 optimization and Phase 5 regeneration
