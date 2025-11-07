#!/usr/bin/env python3
"""
CE Framework Project Initializer - Core Module

Implements the 4-phase pipeline for installing CE framework on target projects:
1. Extract: Unpack ce-infrastructure.xml to target project
2. Blend: Merge framework + user files (CLAUDE.md, settings, commands)
3. Initialize: Run uv sync to install dependencies
4. Verify: Validate installation and report status
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional


class ProjectInitializer:
    """
    Core initializer for CE Framework installation on target projects.

    Handles 4-phase pipeline:
    - extract: Unpack repomix package to .ce/
    - blend: Merge framework + user files
    - initialize: Install Python dependencies
    - verify: Validate installation
    """

    def __init__(self, target_project: Path, dry_run: bool = False):
        """
        Initialize ProjectInitializer.

        Args:
            target_project: Path to target project root
            dry_run: If True, show actions without executing
        """
        self.target_project = Path(target_project).resolve()
        self.dry_run = dry_run
        self.ce_dir = self.target_project / ".ce"
        self.tools_dir = self.ce_dir / "tools"

        # Paths to framework packages (in ctx-eng-plus repo)
        self.ctx_eng_root = Path(__file__).parent.parent.parent.resolve()
        self.infrastructure_xml = self.ctx_eng_root / ".ce" / "ce-infrastructure.xml"
        self.workflow_xml = self.ctx_eng_root / ".ce" / "ce-workflow-docs.xml"

    def run(self, phase: str = "all") -> Dict:
        """
        Run initialization pipeline.

        Args:
            phase: Which phase(s) to run - "all", "extract", "blend", "initialize", "verify"

        Returns:
            Dict with status info for each phase executed

        Raises:
            ValueError: If invalid phase specified
        """
        valid_phases = ["all", "extract", "blend", "initialize", "verify"]
        if phase not in valid_phases:
            raise ValueError(f"Invalid phase '{phase}'. Must be one of: {valid_phases}")

        results = {}

        if phase == "all":
            results["extract"] = self.extract()
            results["blend"] = self.blend()
            results["initialize"] = self.initialize()
            results["verify"] = self.verify()
        else:
            # Run single phase
            method = getattr(self, phase)
            results[phase] = method()

        return results

    def extract(self) -> Dict:
        """
        Extract ce-infrastructure.xml to target project.

        Steps:
        1. Check if ce-infrastructure.xml exists
        2. Extract to .ce/ directory
        3. Reorganize tools/ to .ce/tools/
        4. Copy ce-workflow-docs.xml to .ce/

        Returns:
            Dict with extraction status and file counts
        """
        status = {"success": False, "files_extracted": 0, "message": ""}

        # Check for infrastructure package
        if not self.infrastructure_xml.exists():
            status["message"] = (
                f"❌ ce-infrastructure.xml not found at {self.infrastructure_xml}\n"
                f"🔧 Ensure you're running from ctx-eng-plus repo root"
            )
            return status

        if self.dry_run:
            status["success"] = True
            status["message"] = f"[DRY-RUN] Would extract to {self.ce_dir}"
            return status

        # Check for existing .ce/ directory - rename to .ce.old
        ce_old_dir = self.target_project / ".ce.old"
        renamed_existing = False
        if self.ce_dir.exists():
            # Remove old .ce.old if it exists
            if ce_old_dir.exists():
                shutil.rmtree(ce_old_dir)

            # Rename .ce to .ce.old
            shutil.move(str(self.ce_dir), str(ce_old_dir))
            renamed_existing = True

        try:
            # Import repomix_unpack module
            from ce.repomix_unpack import extract_files

            # Extract to temporary location first
            temp_extract = self.target_project / "tmp" / "ce-extraction"
            temp_extract.mkdir(parents=True, exist_ok=True)

            # Extract files
            files_extracted = extract_files(
                xml_path=self.infrastructure_xml,
                target_dir=temp_extract,
                verbose=False
            )

            if files_extracted == 0:
                status["message"] = "❌ No files extracted from package"
                return status

            # Reorganize extracted files to .ce/ structure
            self.ce_dir.mkdir(parents=True, exist_ok=True)

            # Move all extracted contents to .ce/ (preserving structure for blending)
            # This includes: .ce/, .claude/, .serena/, tools/, CLAUDE.md, examples/
            for item in temp_extract.iterdir():
                dest = self.ce_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))

            # Copy ce-workflow-docs.xml (reference package)
            if self.workflow_xml.exists():
                shutil.copy2(self.workflow_xml, self.ce_dir / "ce-workflow-docs.xml")

            # Cleanup temp directory
            shutil.rmtree(temp_extract.parent)

            status["success"] = True
            status["files_extracted"] = files_extracted

            # Include rename message if applicable
            if renamed_existing:
                status["message"] = (
                    f"ℹ️  Renamed existing .ce/ to .ce.old/\n"
                    f"💡 .ce.old/ will be included as additional context source during blend\n"
                    f"✅ Extracted {files_extracted} files to {self.ce_dir}"
                )
            else:
                status["message"] = f"✅ Extracted {files_extracted} files to {self.ce_dir}"

        except Exception as e:
            status["message"] = f"❌ Extraction failed: {str(e)}\n🔧 Check error details above"

        return status

    def blend(self) -> Dict:
        """
        Blend framework + user files.

        Delegates to: uv run ce blend --all --target-dir <target>

        Returns:
            Dict with blend status and stdout/stderr
        """
        status = {"success": False, "stdout": "", "stderr": ""}

        if self.dry_run:
            status["success"] = True
            status["stdout"] = f"[DRY-RUN] Would run: uv run ce blend --all --target-dir {self.target_project}"
            return status

        try:
            # Run blend command with explicit config path
            blend_config = self.ce_dir / "blend-config.yml"
            result = subprocess.run(
                ["uv", "run", "ce", "blend", "--all",
                 "--config", str(blend_config),
                 "--target-dir", str(self.target_project)],
                cwd=self.ctx_eng_root / "tools",
                capture_output=True,
                text=True,
                timeout=120
            )

            status["stdout"] = result.stdout
            status["stderr"] = result.stderr
            status["success"] = result.returncode == 0

            if not status["success"]:
                status["message"] = (
                    f"❌ Blend phase failed (exit code {result.returncode})\n"
                    f"🔧 Check blend tool output:\n{result.stderr}"
                )
            else:
                # Check if .ce.old exists to mention it
                ce_old_dir = self.target_project / ".ce.old"
                if ce_old_dir.exists():
                    status["message"] = (
                        "✅ Blend phase completed\n"
                        "💡 Note: .ce.old/ detected - blend tool will include it as additional source"
                    )
                else:
                    status["message"] = "✅ Blend phase completed"

        except subprocess.TimeoutExpired:
            status["message"] = "❌ Blend phase timed out (120s limit)\n🔧 Check for hanging processes"
        except FileNotFoundError:
            status["message"] = (
                "❌ uv not found in PATH\n"
                "🔧 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
        except Exception as e:
            status["message"] = f"❌ Blend phase failed: {str(e)}"

        return status

    def initialize(self) -> Dict:
        """
        Initialize Python environment.

        Runs: uv sync in .ce/tools/ directory

        Returns:
            Dict with initialization status and command output
        """
        status = {"success": False, "stdout": "", "stderr": ""}

        if not self.tools_dir.exists():
            status["message"] = (
                f"❌ Tools directory not found: {self.tools_dir}\n"
                f"🔧 Run extract phase first"
            )
            return status

        if self.dry_run:
            status["success"] = True
            status["stdout"] = f"[DRY-RUN] Would run: uv sync in {self.tools_dir}"
            return status

        try:
            # Run uv sync
            result = subprocess.run(
                ["uv", "sync"],
                cwd=self.tools_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for dependency installation
            )

            status["stdout"] = result.stdout
            status["stderr"] = result.stderr
            status["success"] = result.returncode == 0

            if not status["success"]:
                status["message"] = (
                    f"❌ UV sync failed (exit code {result.returncode})\n"
                    f"🔧 Check pyproject.toml and dependency versions:\n{result.stderr}"
                )
            else:
                status["message"] = "✅ Python environment initialized"

        except subprocess.TimeoutExpired:
            status["message"] = "❌ UV sync timed out (300s limit)\n🔧 Check network connection or package mirrors"
        except FileNotFoundError:
            status["message"] = (
                "❌ uv not found in PATH\n"
                "🔧 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
        except Exception as e:
            status["message"] = f"❌ Initialize phase failed: {str(e)}"

        return status

    def verify(self) -> Dict:
        """
        Verify installation.

        Checks:
        1. Critical files exist (.ce/tools/, .claude/, .serena/)
        2. settings.local.json is valid JSON
        3. pyproject.toml exists
        4. Reports summary

        Returns:
            Dict with verification results and warnings
        """
        status = {"success": True, "warnings": [], "checks": []}

        # Critical files to check
        critical_files = [
            self.ce_dir / "tools" / "pyproject.toml",
            self.target_project / ".claude" / "settings.local.json",
            self.target_project / ".serena" / "memories",
            self.ce_dir / "RULES.md"
        ]

        for file_path in critical_files:
            if file_path.exists():
                status["checks"].append(f"✅ {file_path.relative_to(self.target_project)}")
            else:
                status["warnings"].append(f"⚠️  Missing: {file_path.relative_to(self.target_project)}")
                status["success"] = False

        # Validate settings.local.json
        settings_file = self.target_project / ".claude" / "settings.local.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    json.load(f)
                status["checks"].append("✅ settings.local.json is valid JSON")
            except json.JSONDecodeError as e:
                status["warnings"].append(f"⚠️  Invalid JSON in settings.local.json: {str(e)}")
                status["success"] = False
        else:
            status["warnings"].append("⚠️  settings.local.json not found")

        # Check Python installation
        venv_dir = self.tools_dir / ".venv"
        if venv_dir.exists():
            status["checks"].append("✅ Python virtual environment created")
        else:
            status["warnings"].append("⚠️  Virtual environment not found (run initialize phase)")

        # Summary message
        if status["success"]:
            status["message"] = f"✅ Installation verified ({len(status['checks'])} checks passed)"
        else:
            status["message"] = (
                f"⚠️  Installation incomplete ({len(status['warnings'])} warnings)\n"
                f"🔧 Review warnings above and re-run failed phases"
            )

        return status


def main():
    """CLI entry point for testing."""
    if len(sys.argv) < 2:
        print("Usage: python init_project.py <target-project-path> [--dry-run]")
        sys.exit(1)

    target = Path(sys.argv[1])
    dry_run = "--dry-run" in sys.argv

    initializer = ProjectInitializer(target, dry_run=dry_run)
    results = initializer.run(phase="all")

    # Print results
    for phase, result in results.items():
        print(f"\n=== Phase: {phase} ===")
        print(result.get("message", "No message"))
        if not result.get("success", True):
            sys.exit(1)

    print("\n✅ Initialization complete!")


if __name__ == "__main__":
    main()
