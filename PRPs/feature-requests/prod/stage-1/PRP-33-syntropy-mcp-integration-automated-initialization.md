---
prp_id: PRP-33
feature_name: Syntropy-MCP Integration & Automated Initialization
status: pending
created: 2025-11-05T00:00:00Z
updated: 2025-11-05T00:00:00Z
complexity: high
estimated_hours: 8-12
dependencies: repomix, uv, syntropy-mcp
issue: TBD
---

# Syntropy-MCP Integration & Automated Initialization

## 1. TL;DR

**Objective**: Enable one-command CE framework initialization via syntropy-mcp integration

**What**: Create build pipeline and automated initialization workflow that extracts CE framework packages to target projects with intelligent settings blending

**Why**: Manual 5-phase initialization is error-prone and time-consuming (45 min). Automated workflow reduces to single command (<5 min).

**Effort**: 8-12 hours across 6 phases

**Dependencies**:

- Repomix CLI for package generation
- UV package manager for Python tooling
- Syntropy-MCP server for init procedure
- Infrastructure package with unpacker tool

## 2. Context

### Background

Current CE framework initialization requires manual 5-phase workflow:

1. Bucket collection (Serena memories, examples, PRPs)
2. User files migration (YAML headers)
3. Package extraction (repomix unpacker)
4. Blending (CLAUDE.md, settings, commands)
5. Cleanup (artifacts, verification)

**Problems**:

- Infrastructure package missing repomix_unpack.py
- No automated initialization option
- Packages not distributed via syntropy-mcp
- Manual workflow takes 45 minutes
- Error-prone (path confusion, missed steps)

**Solution**: Build pipeline + syntropy-mcp integration for automated one-command setup

### Constraints and Considerations

**Cross-Repo Changes**:

- ctx-eng-plus: Build script, package regeneration
- syntropy-mcp: Init procedure implementation
- Coordination required between repos

**Package Integrity**:

- Infrastructure package size increases ~5KB (unpacker tool)
- Total package size must stay <210KB
- Manifest must document new unpacker inclusion

**Backwards Compatibility**:

- Manual initialization must still work
- INITIALIZATION.md becomes automation-first, manual-fallback
- Existing users can choose automated or manual

**Settings Blending**:

- Infrastructure package must include `.claude/settings.local.json`
- Init procedure must intelligently blend CE and target settings
- Three blending rules ensure CE permissions take precedence
- Prevents tool permission conflicts in target projects

**Testing Requirements**:

- Test unpacker extraction from infrastructure package
- Test settings.local.json blending (3 rules)
- Test syntropy-mcp init (if available)
- Test manual init with updated docs
- Verify both workflows produce identical results

### Documentation References

- Repomix: <https://repomix.com>
- UV package manager: <https://github.com/astral-sh/uv>
- Existing: .ce/repomix-manifest.yml (package manifest)
- Existing: examples/INITIALIZATION.md (manual workflow)
- Existing: tools/ce/repomix_unpack.py (unpacker tool)

## 3. Implementation Steps

### Phase 1: Infrastructure Package Update (2 hours)

**Goal**: Add repomix_unpack.py to infrastructure package

1. Read current infrastructure profile:

   ```bash
   cat .ce/repomix-profile-infrastructure.json
   ```

2. Verify unpacker tool exists:

   ```bash
   ls -lh tools/ce/repomix_unpack.py
   ```

3. Update `.ce/repomix-profile-infrastructure.json`:

   - Ensure `tools/ce/*.py` includes repomix_unpack.py
   - Add `.claude/settings.local.json` to infrastructure package
   - No explicit exclusion of unpacker or settings

4. Verify settings file included in profile:

   ```bash
   grep "settings.local.json" .ce/repomix-profile-infrastructure.json
   ```

5. Regenerate infrastructure package:

   ```bash
   npx repomix --config .ce/repomix-profile-infrastructure.json
   ```

6. Verify unpacker and settings in package:

   ```bash
   grep -c "repomix_unpack.py" ce-32/builds/ce-infrastructure.xml
   grep -c "settings.local.json" ce-32/builds/ce-infrastructure.xml
   ```

**Validation Gate**:

```bash
# Check unpacker and settings in package
grep "repomix_unpack.py" ce-32/builds/ce-infrastructure.xml
grep "settings.local.json" ce-32/builds/ce-infrastructure.xml
# Expected: Both file paths present in XML
```

### Phase 2: Build and Distribute Script (1.5 hours)

**Goal**: Create automated build pipeline

1. Create `.ce/build-and-distribute.sh`:

   ```bash
   #!/bin/bash
   set -e

   echo "🔨 Regenerating CE framework packages..."

   # Regenerate packages
   npx repomix --config .ce/repomix-profile-workflow.json
   npx repomix --config .ce/repomix-profile-infrastructure.json

   echo "✅ Packages regenerated"

   # Validate package integrity
   WORKFLOW_SIZE=$(wc -c < ce-32/builds/ce-workflow-docs.xml)
   INFRA_SIZE=$(wc -c < ce-32/builds/ce-infrastructure.xml)
   TOTAL_SIZE=$((WORKFLOW_SIZE + INFRA_SIZE))

   echo "📊 Package sizes:"
   echo "  Workflow: $WORKFLOW_SIZE bytes"
   echo "  Infrastructure: $INFRA_SIZE bytes"
   echo "  Total: $TOTAL_SIZE bytes"

   # Copy to syntropy-mcp boilerplate
   SYNTROPY_MCP_DIR="../syntropy-mcp"
   BOILERPLATE_DIR="$SYNTROPY_MCP_DIR/boilerplate/ce-framework"

   if [ ! -d "$SYNTROPY_MCP_DIR" ]; then
     echo "❌ Syntropy MCP directory not found: $SYNTROPY_MCP_DIR"
     exit 1
   fi

   mkdir -p "$BOILERPLATE_DIR"
   cp ce-32/builds/ce-workflow-docs.xml "$BOILERPLATE_DIR/"
   cp ce-32/builds/ce-infrastructure.xml "$BOILERPLATE_DIR/"

   echo "✅ Packages distributed to syntropy-mcp"
   ```

2. Make script executable:

   ```bash
   chmod +x .ce/build-and-distribute.sh
   ```

3. Test script:

   ```bash
   .ce/build-and-distribute.sh
   ```

**Validation Gate**:

```bash
# Verify packages copied
ls -lh ../syntropy-mcp/boilerplate/ce-framework/
# Expected: ce-workflow-docs.xml, ce-infrastructure.xml
```

### Phase 3: Syntropy-MCP Init Procedure (3 hours)

**Goal**: Implement automated initialization in syntropy-mcp

**Note**: This phase modifies syntropy-mcp repo, not ctx-eng-plus

1. Create init procedure in syntropy-mcp:
   - Location: `syntropy-mcp/src/init/ce-framework.ts`
   - Implement bootstrap (extract unpacker + pyproject.toml)
   - Install uv package manager
   - Extract infrastructure package
   - Reorganize tools to .ce/tools/
   - Copy workflow package to .ce/examples/
   - Verify installation

2. Pseudocode reference (from INITIAL.md):
   ```typescript
   function initCEFramework(targetProjectDir: string) {
     // Step 1: Bootstrap - extract unpacker
     const infraXml = loadFile('boilerplate/ce-framework/ce-infrastructure.xml')
     extractFile(infraXml, 'tools/ce/repomix_unpack.py', targetProjectDir)
     extractFile(infraXml, 'tools/pyproject.toml', targetProjectDir)

     // Step 2: Ensure uv installation
     exec('curl -LsSf https://astral.sh/uv/install.sh | sh')

     // Step 2.5: Backup target settings BEFORE extraction (critical!)
     const settingsPath = `${targetProjectDir}/.claude/settings.local.json`
     const settingsBackup = `${settingsPath}.backup`
     if (fileExists(settingsPath)) {
       copyFile(settingsPath, settingsBackup)
     }

     // Step 3: Extract infrastructure package (will overwrite settings if exists)
     exec(`python3 tools/ce/repomix_unpack.py boilerplate/ce-framework/ce-infrastructure.xml --target ${targetProjectDir}`)

     // Step 4: Reorganize tools
     exec('mkdir -p .ce/tools')
     exec('mv tools/* .ce/tools/')
     exec('rmdir tools')

     // Step 5: Copy workflow package
     copyFile('boilerplate/ce-framework/ce-workflow-docs.xml', `${targetProjectDir}/.ce/examples/ce-workflow-docs.xml`)

     // Step 6: Blend settings.local.json
     blendSettings(targetProjectDir, settingsBackup)

     // Step 7: Verify installation
     verifyFile('.ce/PRPs/executed/system/PRP-0-CONTEXT-ENGINEERING.md')
     verifyFile('.ce/tools/ce/repomix_unpack.py')
     verifyFile('.claude/commands/generate-prp.md')

     console.log('✅ CE framework initialized')
   }
   ```

3. Implement settings.local.json blending logic:

   **Algorithm**:

   ```typescript
   function blendSettings(targetProjectDir: string, settingsBackupPath: string) {
     // Load CE framework settings (just extracted from infrastructure package)
     const ceSettings = loadJson(`${targetProjectDir}/.claude/settings.local.json`)

     // Load target project settings from backup (created before extraction)
     const targetSettings = fileExists(settingsBackupPath)
       ? loadJson(settingsBackupPath)
       : { allow: [], deny: [], ask: [] }

     // Rule 1: Remove from target's allow list entries that are in CE's deny list
     targetSettings.allow = targetSettings.allow.filter(
       entry => !ceSettings.deny.includes(entry)
     )

     // Rule 2: Add CE entries to target's respective lists (deduplicate)
     for (const list of ['allow', 'deny', 'ask']) {
       targetSettings[list] = [
         ...new Set([...targetSettings[list], ...ceSettings[list]])
       ]
     }

     // Rule 3: Ensure CE entries only appear in one list
     // For each CE entry, remove it from other lists
     for (const list of ['allow', 'deny', 'ask']) {
       for (const entry of ceSettings[list]) {
         const otherLists = ['allow', 'deny', 'ask'].filter(l => l !== list)
         for (const otherList of otherLists) {
           targetSettings[otherList] = targetSettings[otherList].filter(
             e => e !== entry
           )
         }
       }
     }

     // Write blended settings
     const targetSettingsPath = `${targetProjectDir}/.claude/settings.local.json`
     writeJson(targetSettingsPath, targetSettings)

     // Cleanup backup file
     if (fileExists(settingsBackupPath)) {
       deleteFile(settingsBackupPath)
     }
   }
   ```

   **Rules Summary**:

   - **Rule 1**: Target allow entries in CE deny list → Remove from target allow
   - **Rule 2**: CE entries → Add to target's respective lists (deduplicate)
   - **Rule 3**: CE entries → Ensure not in other lists (CE list takes precedence)

   **Example Blending Scenario**:

   ```json
   // CE settings (from infrastructure package)
   {
     "allow": ["Bash(git:*)", "Read(//)"],
     "deny": ["mcp__syntropy__filesystem_read_file"],
     "ask": ["Bash(rm:*)", "Bash(mv:*)"]
   }

   // Target project settings (before blending)
   {
     "allow": ["mcp__syntropy__filesystem_read_file", "Write(//)"],
     "deny": ["Bash(cp:*)"],
     "ask": []
   }

   // After blending (applying Rules 1-3)
   {
     "allow": [
       // Rule 1: Removed "mcp__syntropy__filesystem_read_file" (in CE deny)
       "Write(//)",           // Target entry preserved
       "Bash(git:*)",        // CE entry added
       "Read(//)"            // CE entry added
     ],
     "deny": [
       "Bash(cp:*)",         // Target entry preserved
       "mcp__syntropy__filesystem_read_file"  // CE entry added
     ],
     "ask": [
       "Bash(rm:*)",         // CE entry added
       "Bash(mv:*)"          // CE entry added
     ]
   }
   ```

4. Add CLI command:

   ```bash
   npx syntropy-mcp init ce-framework
   ```

5. Test init procedure (if syntropy-mcp available):
   ```bash
   mkdir -p tmp/init-test
   cd tmp/init-test
   npx syntropy-mcp init ce-framework
   ```

**Validation Gate**:
```bash
# Verify files extracted
ls -lh tmp/init-test/.ce/tools/ce/repomix_unpack.py
ls -lh tmp/init-test/.claude/commands/generate-prp.md
ls -lh tmp/init-test/.ce/PRPs/executed/system/PRP-0-CONTEXT-ENGINEERING.md
# Expected: All files present
```

### Phase 4: INITIALIZATION.md Update (2 hours)

**Goal**: Restructure docs for automation-first approach

1. Read current INITIALIZATION.md:
   ```bash
   cat examples/INITIALIZATION.md
   ```

2. Update structure:
   ```markdown
   # CE Framework Initialization

   ## Quick Start (Automated) - RECOMMENDED

   Use syntropy-mcp for one-command setup:

   \`\`\`bash
   npx syntropy-mcp init ce-framework
   \`\`\`

   This automatically:
   - Extracts unpacker tool (tools/ce/repomix_unpack.py)
   - Installs uv package manager
   - Extracts infrastructure package (50 files: 23 memories, 11 commands, 27 tools, PRP-0, unpacker, settings)
   - Reorganizes tools to .ce/tools/
   - Copies workflow docs to .ce/examples/
   - Blends settings.local.json with target project settings
   - Verifies installation

   **Time**: <5 minutes

   ## Manual Initialization (Fallback)

   If not using syntropy-mcp, follow the 5-phase workflow.

   **Time**: 45 minutes

   ### Phase 1: Bucket Collection
   [Existing content, update paths to .ce/tools/]

   ### Phase 2: User Files Migration
   [Existing content]

   ### Phase 3: Package Extraction
   \`\`\`bash
   # Extract infrastructure package using unpacker
   python3 .ce/tools/ce/repomix_unpack.py ce-infrastructure.xml --target .

   # Reorganize tools (already done in automated workflow)
   mkdir -p .ce/tools
   mv tools/* .ce/tools/
   rmdir tools
   \`\`\`

   ### Phase 4: Blending
   [Existing content]

   ### Phase 5: Cleanup
   [Existing content]

   ## Troubleshooting

   ### Automated Initialization
   - **Issue**: `syntropy-mcp command not found`
     - **Fix**: Install with `npm install -g syntropy-mcp`

   - **Issue**: `repomix_unpack.py not found`
     - **Fix**: Verify infrastructure package includes unpacker (Phase 1)

   ### Manual Initialization
   [Existing troubleshooting content]
   ```

3. Update all code blocks with `.ce/tools/` paths

4. Add cross-references between automated and manual sections

**Validation Gate**:
```bash
# Verify INITIALIZATION.md structure
grep -c "Quick Start (Automated)" examples/INITIALIZATION.md
# Expected: 1
grep -c "Manual Initialization (Fallback)" examples/INITIALIZATION.md
# Expected: 1
```

### Phase 5: Documentation Updates (1.5 hours)

**Goal**: Update manifest, REPORT.md, CLAUDE.md

1. Update `.ce/repomix-manifest.yml`:

   - Add unpacker and settings.local.json to infrastructure package contents
   - Update infrastructure package size estimate (~5KB increase)
   - Add build-and-distribute procedure note

2. Create/update `ce-32/builds/REPORT.md`:
   ```markdown
   # CE Framework Package Build Report

   Generated: 2025-11-05

   ## Packages

   ### Workflow Docs
   - **File**: ce-workflow-docs.xml
   - **Size**: ~83KB
   - **Contents**: 13 examples, CLAUDE.md

   ### Infrastructure
   - **File**: ce-infrastructure.xml
   - **Size**: ~207KB (increased from ~202KB)
   - **Contents**: 50 files (23 memories, 11 commands, 27 tools, PRP-0, settings)
   - **New**: Includes repomix_unpack.py and .claude/settings.local.json

   ## Build Procedure

   Regenerate packages:
   \`\`\`bash
   .ce/build-and-distribute.sh
   \`\`\`

   Distributes to: `syntropy-mcp/boilerplate/ce-framework/`
   ```

3. Update `CLAUDE.md`:
   - Add "Syntropy-MCP Integration" section
   - Document build-and-distribute script
   - Link to INITIALIZATION.md for automated setup

**Validation Gate**:
```bash
# Verify manifest updated
grep "repomix_unpack.py" .ce/repomix-manifest.yml
# Expected: Mention of unpacker in infrastructure package
```

### Phase 6: Cleanup (1 hour)

**Goal**: Remove test artifacts and verify installation

1. Purge test directory:
   ```bash
   rm -rf tmp/init-test/
   ```

2. Remove from git tracking:
   ```bash
   git status
   # If tmp/init-test/ appears, add to .gitignore
   echo "tmp/init-test/" >> .gitignore
   ```

3. Verify installation files:
   ```bash
   ls -lh .ce/build-and-distribute.sh
   ls -lh ce-32/builds/ce-infrastructure.xml
   ls -lh ce-32/builds/ce-workflow-docs.xml
   ls -lh ../syntropy-mcp/boilerplate/ce-framework/
   ```

**Validation Gate**:
```bash
# Verify cleanup
ls tmp/init-test/ 2>&1 | grep "No such file"
# Expected: Directory removed
```

## 4. Validation Gates

### Gate 1: Infrastructure Package Includes Required Files

**Command**:

```bash
grep "repomix_unpack.py" ce-32/builds/ce-infrastructure.xml
grep "settings.local.json" ce-32/builds/ce-infrastructure.xml
```

**Expected**: Both file paths present in XML

**On Failure**:

- Check `.ce/repomix-profile-infrastructure.json` includes `tools/ce/*.py` and `.claude/settings.local.json`
- Verify files not in `exclude` list
- Regenerate package

### Gate 2: Build Script Copies Packages

**Command**:
```bash
ls -lh ../syntropy-mcp/boilerplate/ce-framework/
```

**Expected**: ce-workflow-docs.xml, ce-infrastructure.xml present

**On Failure**:
- Check syntropy-mcp directory exists at `../syntropy-mcp`
- Verify build script has execute permissions
- Run script manually with verbose output

### Gate 3: Syntropy-MCP Init Works

**Command**:

```bash
cd tmp/test-project
npx syntropy-mcp init ce-framework
ls .ce/tools/ce/repomix_unpack.py
ls .claude/settings.local.json
```

**Expected**: Unpacker and settings files exist after init

**Verify Settings Blending**:

```bash
# Check that CE deny list entries are not in target allow list
# Example: If CE denies "mcp__syntropy__filesystem_read_file",
# verify it's not in allow list
grep "\"allow\"" .claude/settings.local.json -A 50 | grep -v "mcp__syntropy__filesystem_read_file"

# Check that CE entries are in respective lists
grep "mcp__syntropy__serena" .claude/settings.local.json

# Check no duplicates exist (if jq available)
# cat .claude/settings.local.json | jq '.allow + .deny + .ask' | sort | uniq -d
# Expected: Empty (no duplicates)
```

**On Failure**:

- Check syntropy-mcp installed: `npm list -g syntropy-mcp`
- Verify boilerplate packages exist
- Check init procedure logs
- Verify blendSettings() function implemented correctly

### Gate 4: INITIALIZATION.md Structure

**Command**:
```bash
grep -E "(Quick Start|Manual Initialization)" examples/INITIALIZATION.md
```

**Expected**: Both sections present

**On Failure**:
- Verify INITIALIZATION.md not overwritten
- Check section headings match expected format
- Ensure automation section comes first

### Gate 5: Manifest Updated

**Command**:

```bash
grep "repomix_unpack.py" .ce/repomix-manifest.yml
grep "settings.local.json" .ce/repomix-manifest.yml
```

**Expected**: Both files mentioned in infrastructure contents

**On Failure**:

- Manually add unpacker and settings to infrastructure package contents list
- Update package size estimate (~207KB)

### Gate 6: Cleanup Complete

**Command**:
```bash
ls tmp/init-test/ 2>&1
```

**Expected**: "No such file or directory"

**On Failure**:
- Manually delete tmp/init-test/
- Check .gitignore includes tmp/init-test/

## 5. Testing Strategy

### Test Framework

Manual testing + validation gates (no automated tests for cross-repo integration)

### Test Command

N/A - Use validation gates in section 4

### Test Coverage

**Infrastructure Package**:

- [ ] Unpacker tool present in package
- [ ] Settings.local.json present in package
- [ ] Package size within limits (<290KB total)
- [ ] Package extracts cleanly

**Build Script**:
- [ ] Script is executable
- [ ] Regenerates both packages
- [ ] Copies to syntropy-mcp
- [ ] Validates package integrity

**Syntropy-MCP Init** (if available):

- [ ] Bootstrap extracts unpacker
- [ ] UV installation succeeds
- [ ] Infrastructure extraction completes
- [ ] Tools reorganized to .ce/tools/
- [ ] Workflow package copied
- [ ] Settings.local.json blending works correctly
  - [ ] Rule 1: Target allow entries in CE deny → Removed
  - [ ] Rule 2: CE entries added to target lists (deduplicated)
  - [ ] Rule 3: CE entries only in one list
- [ ] Verification checks pass

**Documentation**:
- [ ] INITIALIZATION.md automation-first
- [ ] Manifest includes unpacker
- [ ] CLAUDE.md documents integration
- [ ] REPORT.md reflects changes

**Backwards Compatibility**:
- [ ] Manual initialization still works
- [ ] Existing users not affected
- [ ] Both workflows produce same result

## 6. Rollout Plan

### Phase 1: Development

1. Update infrastructure package (Phase 1)
2. Create build script (Phase 2)
3. Test package regeneration
4. Commit to ctx-eng-plus

### Phase 2: Syntropy-MCP Integration

1. Implement init procedure in syntropy-mcp (Phase 3)
2. Test with local packages
3. Commit to syntropy-mcp

### Phase 3: Documentation

1. Update INITIALIZATION.md (Phase 4)
2. Update manifest, REPORT.md, CLAUDE.md (Phase 5)
3. Commit documentation changes

### Phase 4: Cleanup and Verification

1. Remove test artifacts (Phase 6)
2. Verify all validation gates pass
3. Test full workflow end-to-end

### Phase 5: Rollback Plan

**If issues found**:
1. Keep previous packages as backup:
   ```bash
   cp ce-32/builds/ce-infrastructure.xml ce-32/builds/ce-infrastructure.xml.backup
   cp ce-32/builds/ce-workflow-docs.xml ce-32/builds/ce-workflow-docs.xml.backup
   ```

2. Rollback steps:
   ```bash
   # Restore old packages
   cp ce-32/builds/ce-infrastructure.xml.backup ce-32/builds/ce-infrastructure.xml
   cp ce-32/builds/ce-workflow-docs.xml.backup ce-32/builds/ce-workflow-docs.xml

   # Copy old packages to syntropy-mcp
   .ce/build-and-distribute.sh

   # Revert INITIALIZATION.md
   git checkout HEAD~1 examples/INITIALIZATION.md
   ```

3. Test rollback:
   ```bash
   # Verify old packages work
   grep -c "repomix_unpack.py" ce-32/builds/ce-infrastructure.xml
   # Expected: 0 (old package without unpacker)
   ```

---

## Research Findings

### Codebase Analysis

**Repomix Usage**:
- Infrastructure package profile: `.ce/repomix-profile-infrastructure.json`
- Workflow package profile: `.ce/repomix-profile-workflow.json`
- Unpacker tool exists: `tools/ce/repomix_unpack.py`
- Manifest: `.ce/repomix-manifest.yml` (documents package contents)

**Syntropy-MCP**:
- Located at: `syntropy-mcp/` (sibling directory)
- Has boilerplate system (likely for init procedures)
- 9 MCP servers, 78 tools
- Production-ready (17/17 tests passing)

**Current Package Sizes**:
- Workflow: 83,365 tokens (~270KB)
- Infrastructure: 201,724 tokens (~727KB)
- Total: 285,089 tokens (~997KB)
- Target: <210KB total (currently 35% over on infrastructure)

**Key Files**:
- `tools/ce/repomix_unpack.py`: 50+ lines, parses repomix XML, extracts files
- `.ce/repomix-manifest.yml`: Documents package contents, sizes, use cases
- `examples/INITIALIZATION.md`: 5-phase manual workflow
- `.ce/reorganize-infrastructure.sh`: Post-extraction reorganization

### Similar Patterns

**Build Scripts**:
- `.ce/reorganize-infrastructure.sh`: Moves files to /system/ subfolders
- Pattern: Regenerate packages → validate → distribute

**Init Procedures**:
- PRP-24, PRP-25, PRP-26: Syntropy MCP server setup
- Pattern: Bootstrap tool → install deps → extract package → verify

**Package Extraction**:
- `repomix_unpack.py`: Parse XML → extract files → write to disk
- Pattern: Load XML → regex match `<file path="...">` → clean content → write

### Documentation Sources

- Repomix: <https://repomix.com> (external)
- UV: <https://github.com/astral-sh/uv> (external)
- Internal: .ce/repomix-manifest.yml (package manifest)
- Internal: examples/INITIALIZATION.md (manual workflow)
- Internal: tools/ce/repomix_unpack.py (unpacker implementation)

**Context7 Tools**: Unavailable during generation (graceful degradation)
