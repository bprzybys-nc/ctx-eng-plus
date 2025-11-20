#!/usr/bin/env python3
"""
Workaround for repomix v1.9.1 bug - manually inject missing files into XML.
See: .serena/memories/repomix-glob-pattern-file-permissions-issue.md

IMPORTANT: If NLP or vacuum_strategies files are relocated/renamed, update both:
  1. This script (MISSING_FILES list)
  2. .ce/repomix-profile-infrastructure.json (include paths)
"""

import os
import shutil
from pathlib import Path

# Files that repomix collects but doesn't output to XML (bug in v1.9.1)
MISSING_FILES = [
    "tools/ce/nlp/__init__.py",
    "tools/ce/nlp/cache.py",
    "tools/ce/nlp/normalizer.py",
    "tools/ce/nlp/similarity.py",
    "tools/ce/vacuum_strategies/llm_analyzer.py",
    "tools/ce/vacuum_strategies/prp_lifecycle_docs.py",
]

def main():
    # Ensure we're in project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)

    infra_xml = Path("syntropy-mcp/boilerplate/ce-framework/ce-infrastructure.xml")

    # Check if infrastructure XML exists
    if not infra_xml.exists():
        print(f"❌ Infrastructure XML not found: {infra_xml}")
        return 1

    # Backup original
    shutil.copy(infra_xml, str(infra_xml) + ".backup")

    # Read current XML
    with open(infra_xml, 'r') as f:
        xml_content = f.read()

    injected_count = 0

    # For each missing file, create XML entry and inject before </repository>
    for file_path in MISSING_FILES:
        if not Path(file_path).exists():
            print(f"⚠️  File not found (may have been relocated): {file_path}")
            continue

        # Check if already in XML
        if f'<file path="{file_path}"' in xml_content:
            print(f"✓ Already included: {file_path}")
            continue

        print(f"📦 Injecting: {file_path}")

        # Read file content
        with open(file_path, 'r') as f:
            file_content = f.read()

        # Create XML entry (CDATA preserves content as-is)
        xml_entry = f'''<file path="{file_path}">
<source><![CDATA[
{file_content}
]]></source>
</file>
'''

        # Inject before </files>
        xml_content = xml_content.replace('</files>', xml_entry + '\n</files>')
        injected_count += 1

    # Write updated XML
    with open(infra_xml, 'w') as f:
        f.write(xml_content)

    final_count = xml_content.count('<file path=')
    print("✅ Missing files injected into infrastructure XML")
    print(f"📊 Updated file count: {final_count}")
    print(f"   Injected: {injected_count} files")

    return 0

if __name__ == "__main__":
    exit(main())
