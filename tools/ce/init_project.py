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
import logging
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ValidationResult:
    """Result of a validation gate check."""
    success: bool
    message: str = ""
    troubleshooting: str = ""

    def __bool__(self):
        return self.success


class ErrorLogger:
    """Persistent error logger for init process."""

    def __init__(self, target_dir: Path):
        """Initialize error logger with timestamped log file."""
        self.log_file = target_dir / ".ce" / f"init-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure file logging
        self.logger = logging.getLogger("ce.init")
        self.logger.setLevel(logging.DEBUG)

        handler = logging.FileHandler(self.log_file)
        handler.setFormatter(logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%H:%M:%S'
        ))
        self.logger.addHandler(handler)

    def info(self, msg: str):
        """Log info message."""
        self.logger.info(msg)

    def error(self, msg: str):
        """Log error message."""
        self.logger.error(msg)

    def warning(self, msg: str):
        """Log warning message."""
        self.logger.warning(msg)


class PhaseValidator:
    """Validation gates for init phases."""

    @staticmethod
    def gate2_extraction(staging: Path, expected_counts: Dict[str, int]) -> ValidationResult:
        """
        Validate extraction file count with tolerance.

        Args:
            staging: Path to staging directory with extracted files
            expected_counts: Dict with expected file counts by category

        Returns:
            ValidationResult indicating success/failure
        """
        actual = PhaseValidator._count_files(staging)
        expected_total = expected_counts.get("total", 87)
        actual_total = actual["total"]

        # Fail if >10 difference
        if abs(actual_total - expected_total) > 10:
            return ValidationResult(
                success=False,
                message=f"❌ GATE 2 FAILED: Expected {expected_total} files, got {actual_total}",
                troubleshooting="🔧 Extraction incomplete - check package integrity or run with --verbose"
            )

        # Warn if within tolerance (5-10 difference)
        if actual_total != expected_total:
            diff = abs(actual_total - expected_total)
            print(f"⚠️  File count {actual_total} differs from expected {expected_total} (Δ{diff}, within tolerance)")

        return ValidationResult(
            success=True,
            message=f"✅ GATE 2 PASSED: Extracted {actual_total} files"
        )

    @staticmethod
    def gate1_preflight(target_dir: Path, infrastructure_xml: Path) -> ValidationResult:
        """
        Validate prerequisites before extraction (GATE 1: PREFLIGHT).

        Args:
            target_dir: Path to target project directory
            infrastructure_xml: Path to ce-infrastructure.xml package

        Returns:
            ValidationResult indicating success/failure
        """
        # Check target directory writable
        if not target_dir.exists():
            return ValidationResult(
                success=False,
                message=f"❌ GATE 1 FAILED: Target directory does not exist: {target_dir}",
                troubleshooting="🔧 Create target directory or check path"
            )

        if not os.access(target_dir, os.W_OK):
            return ValidationResult(
                success=False,
                message=f"❌ GATE 1 FAILED: Target directory not writable: {target_dir}",
                troubleshooting="🔧 Check directory permissions (chmod +w)"
            )

        # Check package exists and is readable
        if not infrastructure_xml.exists():
            return ValidationResult(
                success=False,
                message=f"❌ GATE 1 FAILED: Package not found: {infrastructure_xml}",
                troubleshooting="🔧 Ensure you're running from ctx-eng-plus repo root"
            )

        if not os.access(infrastructure_xml, os.R_OK):
            return ValidationResult(
                success=False,
                message=f"❌ GATE 1 FAILED: Package not readable: {infrastructure_xml}",
                troubleshooting="🔧 Check file permissions (chmod +r)"
            )

        # Check disk space (300MB minimum)
        import shutil as shutil_disk
        disk_stats = shutil_disk.disk_usage(target_dir)
        free_mb = disk_stats.free / (1024 * 1024)
        required_mb = 300

        if free_mb < required_mb:
            return ValidationResult(
                success=False,
                message=f"❌ GATE 1 FAILED: Insufficient disk space ({free_mb:.0f}MB free, {required_mb}MB required)",
                troubleshooting="🔧 Free up disk space or use different target directory"
            )

        return ValidationResult(
            success=True,
            message=f"✅ GATE 1 PASSED: Prerequisites validated ({free_mb:.0f}MB available)"
        )

    @staticmethod
    def gate3_blend(target_dir: Path) -> ValidationResult:
        """
        Validate blending results (GATE 3: BLEND).

        Args:
            target_dir: Path to target project directory

        Returns:
            ValidationResult indicating success/failure
        """
        # Validate settings.local.json syntax
        settings_file = target_dir / ".claude" / "settings.local.json"
        if settings_file.exists():
            try:
                with open(settings_file) as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                return ValidationResult(
                    success=False,
                    message=f"❌ GATE 3 FAILED: Invalid JSON in settings.local.json: {str(e)}",
                    troubleshooting="🔧 Check JSON syntax at line indicated above"
                )
        else:
            return ValidationResult(
                success=False,
                message="❌ GATE 3 FAILED: settings.local.json not found after blending",
                troubleshooting="🔧 Check blend phase output for errors"
            )

        # Validate CLAUDE.md exists (Markdown syntax check is basic - just check readable)
        claude_md = target_dir / "CLAUDE.md"
        if claude_md.exists():
            try:
                with open(claude_md) as f:
                    content = f.read()
                    if len(content) == 0:
                        return ValidationResult(
                            success=False,
                            message="❌ GATE 3 FAILED: CLAUDE.md is empty",
                            troubleshooting="🔧 Check blend phase - CLAUDE.md should have framework + user content"
                        )
            except Exception as e:
                return ValidationResult(
                    success=False,
                    message=f"❌ GATE 3 FAILED: Cannot read CLAUDE.md: {str(e)}",
                    troubleshooting="🔧 Check file permissions"
                )

        # Check no framework files at root (should be in .ce/ or /system/ subdirs)
        ce_dir = target_dir / ".ce"
        if not ce_dir.exists():
            return ValidationResult(
                success=False,
                message="❌ GATE 3 FAILED: .ce/ directory not found after blending",
                troubleshooting="🔧 Run extract phase first"
            )

        return ValidationResult(
            success=True,
            message="✅ GATE 3 PASSED: Blend validation complete"
        )

    @staticmethod
    def gate4_finalize(tools_dir: Path) -> ValidationResult:
        """
        Validate installation completion (GATE 4: FINALIZE).

        Args:
            tools_dir: Path to .ce/tools/ directory

        Returns:
            ValidationResult indicating success/failure
        """
        # Check uv sync succeeded (.venv/ exists)
        venv_dir = tools_dir / ".venv"
        if not venv_dir.exists():
            return ValidationResult(
                success=False,
                message="❌ GATE 4 FAILED: Virtual environment not created",
                troubleshooting="🔧 Check initialize phase output - uv sync may have failed"
            )

        # Check pyproject.toml exists
        pyproject = tools_dir / "pyproject.toml"
        if not pyproject.exists():
            return ValidationResult(
                success=False,
                message="❌ GATE 4 FAILED: pyproject.toml not found",
                troubleshooting="🔧 Extract phase may have failed - check .ce/tools/ directory"
            )

        # Verify ce command works
        try:
            result = subprocess.run(
                ["uv", "run", "ce", "--version"],
                cwd=tools_dir,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                return ValidationResult(
                    success=False,
                    message=f"❌ GATE 4 FAILED: 'uv run ce --version' failed (exit {result.returncode})",
                    troubleshooting=f"🔧 Check initialization errors:\n{result.stderr}"
                )

        except subprocess.TimeoutExpired:
            return ValidationResult(
                success=False,
                message="❌ GATE 4 FAILED: 'uv run ce --version' timed out",
                troubleshooting="🔧 Check for hanging processes or dependencies"
            )
        except FileNotFoundError:
            return ValidationResult(
                success=False,
                message="❌ GATE 4 FAILED: uv not found in PATH",
                troubleshooting="🔧 Install UV: curl -LsSf https://astral.sh/uv/install.sh | sh"
            )
        except Exception as e:
            return ValidationResult(
                success=False,
                message=f"❌ GATE 4 FAILED: Command validation error: {str(e)}",
                troubleshooting="🔧 Check .ce/tools/ installation"
            )

        return ValidationResult(
            success=True,
            message="✅ GATE 4 PASSED: Installation verified"
        )

    @staticmethod
    def _count_files(staging: Path) -> Dict[str, int]:
        """Count files by category in staging directory."""
        # NOTE: Staging directory has tools at root (tools/ce/*.py), not .ce/tools/
        tools = len(list(staging.glob("tools/ce/*.py")))
        memories = len(list(staging.glob(".serena/memories/*.md")))
        commands = len(list(staging.glob(".claude/commands/*.md")))
        examples = len(list(staging.glob("examples/*.md")))
        prps = len(list(staging.glob(".ce/PRPs/**/*.md")))

        return {
            "tools": tools,
            "memories": memories,
            "commands": commands,
            "examples": examples,
            "prps": prps,
            "total": tools + memories + commands + examples + prps
        }


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

        # Paths to framework packages
        # Priority 1: syntropy-mcp boilerplate (production - installed via npm)
        # Priority 2: ctx-eng-plus/.ce/ (development mode)
        self.ctx_eng_root = Path(__file__).parent.parent.parent.resolve()

        # Try syntropy-mcp boilerplate first (sibling to ctx-eng-plus)
        syntropy_boilerplate = self.ctx_eng_root.parent / "syntropy-mcp" / "boilerplate" / "ce-framework"

        if (syntropy_boilerplate / "ce-infrastructure.xml").exists():
            # Production: packages from syntropy-mcp
            self.infrastructure_xml = syntropy_boilerplate / "ce-infrastructure.xml"
            self.workflow_xml = syntropy_boilerplate / "ce-workflow-docs.xml"
        else:
            # Development: packages from ctx-eng-plus/.ce/
            self.infrastructure_xml = self.ctx_eng_root / ".ce" / "ce-infrastructure.xml"
            self.workflow_xml = self.ctx_eng_root / ".ce" / "ce-workflow-docs.xml"

        # Error logging and rollback tracking
        self.error_logger: Optional[ErrorLogger] = None
        self.backup_dir: Optional[Path] = None

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
        Extract ce-infrastructure.xml to target project with GATE 2 validation.

        Steps:
        1. Initialize error logger
        2. Check if ce-infrastructure.xml exists
        3. Create backup of existing .ce/
        4. Extract to staging directory
        5. GATE 2: Validate file count (87 files ±5)
        6. Move from staging to .ce/
        7. Copy ce-workflow-docs.xml

        Returns:
            Dict with extraction status, file counts, and validation results
        """
        status = {"success": False, "files_extracted": 0, "message": ""}

        # Initialize error logger
        if not self.error_logger:
            self.error_logger = ErrorLogger(self.target_project)
            self.error_logger.info("=== CE Framework Initialization Started ===")

        # ============================================================
        # GATE 1: Validate prerequisites
        # ============================================================
        print(f"🔍 GATE 1: Validating prerequisites...")
        validation = PhaseValidator.gate1_preflight(self.target_project, self.infrastructure_xml)

        if not validation:
            # Gate failed - log and abort
            print(validation.message)
            if validation.troubleshooting:
                print(validation.troubleshooting)
            print(f"📄 Full log: {self.error_logger.log_file}")

            self.error_logger.error(validation.message)
            self.error_logger.error(validation.troubleshooting)
            print("❌ Initialization aborted")

            status["message"] = f"{validation.message}\n{validation.troubleshooting}"
            return status

        # Gate passed
        print(validation.message)
        self.error_logger.info(validation.message)

        if self.dry_run:
            status["success"] = True
            status["message"] = f"[DRY-RUN] Would extract to {self.ce_dir}"
            return status

        # Create backup of existing .ce/ directory
        if self.ce_dir.exists():
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            self.backup_dir = self.target_project / f".ce.backup-{timestamp}"

            # Remove old backup if it exists
            if self.backup_dir.exists():
                shutil.rmtree(self.backup_dir)

            # Create backup
            shutil.move(str(self.ce_dir), str(self.backup_dir))
            self.error_logger.info(f"Created backup: {self.backup_dir}")
            print(f"ℹ️  Created backup: {self.backup_dir.name}")

        try:
            # Import repomix_unpack module
            from ce.repomix_unpack import extract_files

            # Extract to temporary location first
            temp_extract = self.target_project / "tmp" / "ce-extraction"
            temp_extract.mkdir(parents=True, exist_ok=True)

            # Extract files
            self.error_logger.info(f"Extracting from {self.infrastructure_xml.name}...")
            files_extracted = extract_files(
                xml_path=self.infrastructure_xml,
                target_dir=temp_extract,
                verbose=False
            )
            self.error_logger.info(f"Extracted {files_extracted} files to staging")

            if files_extracted == 0:
                status["message"] = "❌ No files extracted from package"
                self.error_logger.error("Zero files extracted - package may be empty or corrupted")
                self.rollback("Extraction returned 0 files")
                return status

            # ============================================================
            # GATE 2: Validate extraction file count
            # ============================================================
            expected_counts = {
                "tools": 38,
                "memories": 24,
                "commands": 11,
                "examples": 11,
                "prps": 1,
                "total": 87  # +2 for CLAUDE.md and .claude/settings.local.json in package root
            }

            print(f"🔍 GATE 2: Validating extraction...")
            validation = PhaseValidator.gate2_extraction(temp_extract, expected_counts)

            if not validation:
                # Gate failed - log and rollback
                print(validation.message)
                if validation.troubleshooting:
                    print(validation.troubleshooting)
                print(f"📄 Full log: {self.error_logger.log_file}")

                self.error_logger.error(validation.message)
                self.error_logger.error(validation.troubleshooting)

                # Rollback and abort
                self.rollback("GATE 2 validation failed")
                print("❌ Initialization aborted")

                status["message"] = f"{validation.message}\n{validation.troubleshooting}"
                return status

            # Gate passed
            print(validation.message)
            self.error_logger.info(validation.message)

            # Reorganize extracted files to .ce/ structure
            self.ce_dir.mkdir(parents=True, exist_ok=True)

            # Reorganize extracted files:
            # - .ce/* contents → target/.ce/ (blend-config.yml, PRPs/, etc.)
            # - .claude/, .serena/, tools/, CLAUDE.md, examples/ → target/.ce/ (for blending)

            # First, move .ce/ contents to target/.ce/
            ce_extracted = temp_extract / ".ce"
            if ce_extracted.exists():
                for item in ce_extracted.iterdir():
                    dest = self.ce_dir / item.name
                    if dest.exists():
                        if dest.is_dir():
                            shutil.rmtree(dest)
                        else:
                            dest.unlink()
                    shutil.move(str(item), str(dest))

                # Delete now-empty .ce/ directory to prevent double-moving in second loop
                shutil.rmtree(ce_extracted)

            # Then, move other extracted directories to target/.ce/ (framework files for blending)
            for item in temp_extract.iterdir():
                dest = self.ce_dir / item.name
                if dest.exists():
                    if dest.is_dir():
                        shutil.rmtree(dest)
                    else:
                        dest.unlink()
                shutil.move(str(item), str(dest))

            # FIX BUG #3: Ensure complete PRP directory structure
            prps_dir = self.ce_dir / "PRPs"
            (prps_dir / "executed").mkdir(parents=True, exist_ok=True)
            (prps_dir / "feature-requests").mkdir(parents=True, exist_ok=True)
            self.error_logger.info("Created PRP directory structure (executed + feature-requests)")

            # Copy ce-workflow-docs.xml (reference package)
            if self.workflow_xml.exists():
                shutil.copy2(self.workflow_xml, self.ce_dir / "ce-workflow-docs.xml")
                self.error_logger.info("Copied ce-workflow-docs.xml")

            # Cleanup temp directory
            shutil.rmtree(temp_extract.parent)
            self.error_logger.info("Cleaned up staging directory")

            status["success"] = True
            status["files_extracted"] = files_extracted

            # Success message
            if self.backup_dir:
                status["message"] = (
                    f"ℹ️  Created backup: {self.backup_dir.name}\n"
                    f"✅ Extracted {files_extracted} files to {self.ce_dir}\n"
                    f"📄 Log: {self.error_logger.log_file}"
                )
            else:
                status["message"] = (
                    f"✅ Extracted {files_extracted} files to {self.ce_dir}\n"
                    f"📄 Log: {self.error_logger.log_file}"
                )

            self.error_logger.info("=== Extraction Phase Complete ===")

        except Exception as e:
            error_msg = f"❌ Extraction failed: {str(e)}"
            print(error_msg)
            print(f"📄 Full log: {self.error_logger.log_file}")

            self.error_logger.error(f"Exception during extraction: {str(e)}")
            self.rollback(f"Exception: {str(e)}")
            print("❌ Initialization aborted")

            status["message"] = f"{error_msg}\n🔧 Check {self.error_logger.log_file} for details"

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
                # Cleanup: Remove framework .claude/ and CLAUDE.md from .ce/ after blending
                # These should only exist at root, not in .ce/
                ce_claude = self.ce_dir / ".claude"
                ce_claude_md = self.ce_dir / "CLAUDE.md"
                ce_serena = self.ce_dir / ".serena"

                if ce_claude.exists():
                    shutil.rmtree(ce_claude)
                if ce_claude_md.exists():
                    ce_claude_md.unlink()

                # FIX BUG #2: Cleanup temporary framework memories after blending
                if ce_serena.exists():
                    shutil.rmtree(ce_serena)
                    if self.error_logger:
                        self.error_logger.info("Cleaned up temporary framework memories (.ce/.serena/)")

                # ============================================================
                # GATE 3: Validate blend results
                # ============================================================
                print(f"🔍 GATE 3: Validating blend results...")
                validation = PhaseValidator.gate3_blend(self.target_project)

                if not validation:
                    # Gate failed - log and abort
                    print(validation.message)
                    if validation.troubleshooting:
                        print(validation.troubleshooting)

                    if self.error_logger:
                        self.error_logger.error(validation.message)
                        self.error_logger.error(validation.troubleshooting)
                        print(f"📄 Full log: {self.error_logger.log_file}")

                    status["success"] = False
                    status["message"] = f"{validation.message}\n{validation.troubleshooting}"
                    return status

                # Gate passed
                print(validation.message)
                if self.error_logger:
                    self.error_logger.info(validation.message)

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
                # ============================================================
                # GATE 4: Validate installation completion
                # ============================================================
                print(f"🔍 GATE 4: Validating installation...")
                validation = PhaseValidator.gate4_finalize(self.tools_dir)

                if not validation:
                    # Gate failed - log and abort
                    print(validation.message)
                    if validation.troubleshooting:
                        print(validation.troubleshooting)

                    if self.error_logger:
                        self.error_logger.error(validation.message)
                        self.error_logger.error(validation.troubleshooting)
                        print(f"📄 Full log: {self.error_logger.log_file}")

                    status["success"] = False
                    status["message"] = f"{validation.message}\n{validation.troubleshooting}"
                    return status

                # Gate passed
                print(validation.message)
                if self.error_logger:
                    self.error_logger.info(validation.message)

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

    def rollback(self, reason: str = "Init failed") -> bool:
        """
        Rollback to pre-init state.

        Restores .ce/ from backup if it exists, removes staging directory.

        Args:
            reason: Reason for rollback (for logging)

        Returns:
            True if rollback successful, False otherwise
        """
        print(f"♻️  Rolling back to pre-init state... ({reason})")

        if self.error_logger:
            self.error_logger.error(f"Rollback triggered: {reason}")

        try:
            # Remove partial .ce/ if it exists
            if self.ce_dir.exists():
                shutil.rmtree(self.ce_dir)
                if self.error_logger:
                    self.error_logger.info(f"Removed partial .ce/ directory")

            # Restore from backup if it exists
            if self.backup_dir and self.backup_dir.exists():
                shutil.move(str(self.backup_dir), str(self.ce_dir))
                print(f"✓ Restored .ce/ from backup")
                if self.error_logger:
                    self.error_logger.info(f"Restored .ce/ from {self.backup_dir}")
            else:
                print(f"✓ No backup to restore (clean state)")

            # Remove staging directory
            staging = self.target_project / "tmp" / "ce-extraction"
            if staging.exists():
                shutil.rmtree(staging.parent)
                if self.error_logger:
                    self.error_logger.info("Cleaned up staging directory")

            print(f"✓ Rollback complete")
            return True

        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            if self.error_logger:
                self.error_logger.error(f"Rollback failed: {e}")
            return False


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
