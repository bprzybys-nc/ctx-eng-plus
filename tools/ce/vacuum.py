"""Vacuum command for project cleanup."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import List

from .vacuum_strategies import (
    BackupFileStrategy,
    CleanupCandidate,
    CommentedCodeStrategy,
    DeadLinkStrategy,
    ObsoleteDocStrategy,
    OrphanTestStrategy,
    TempFileStrategy,
    UnreferencedCodeStrategy,
)


class VacuumCommand:
    """Main vacuum command for project cleanup."""

    def __init__(self, project_root: Path):
        """Initialize vacuum command.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = project_root
        self.strategies = {
            "temp-files": TempFileStrategy,
            "backup-files": BackupFileStrategy,
            "obsolete-docs": ObsoleteDocStrategy,
            "unreferenced-code": UnreferencedCodeStrategy,
            "orphan-tests": OrphanTestStrategy,
            "dead-links": DeadLinkStrategy,
            "commented-code": CommentedCodeStrategy,
        }

    def run(
        self,
        dry_run: bool = True,
        min_confidence: int = 0,
        exclude_strategies: List[str] = None,
        execute: bool = False,
        force: bool = False,
        nuclear: bool = False,
    ) -> int:
        """Run vacuum command.

        Args:
            dry_run: If True, only generate report without deleting
            min_confidence: Minimum confidence threshold (0-100)
            exclude_strategies: List of strategy names to skip
            execute: Delete HIGH confidence items
            force: Delete HIGH + MEDIUM confidence items
            nuclear: Delete ALL items (requires confirmation)

        Returns:
            Exit code: 0 = clean, 1 = candidates found, 2 = error
        """
        exclude_strategies = exclude_strategies or []

        # Determine deletion threshold
        if nuclear:
            delete_threshold = 0  # Delete everything
            if not self._confirm_nuclear():
                print("❌ Nuclear mode cancelled by user")
                return 2
        elif force:
            delete_threshold = 60  # Delete MEDIUM + HIGH
        elif execute:
            delete_threshold = 100  # Delete HIGH only
        else:
            delete_threshold = 101  # Dry-run: delete nothing

        # Run all strategies
        all_candidates = []
        for strategy_name, strategy_class in self.strategies.items():
            if strategy_name in exclude_strategies:
                print(f"⏭️  Skipping {strategy_name}")
                continue

            print(f"🔍 Running {strategy_name}...")
            strategy = strategy_class(self.project_root)
            candidates = strategy.find_candidates()

            # Filter by minimum confidence
            candidates = [c for c in candidates if c.confidence >= min_confidence]

            all_candidates.extend(candidates)
            print(f"   Found {len(candidates)} candidates")

        # Generate report
        report_path = self.project_root / ".ce" / "vacuum-report.md"
        self._generate_report(all_candidates, report_path)
        print(f"\n📄 Report generated: {report_path}")

        # Delete files if not dry-run
        if delete_threshold <= 100:
            deleted_count = self._delete_candidates(all_candidates, delete_threshold)
            print(f"\n🗑️  Deleted {deleted_count} items")

        # Return exit code
        if not all_candidates:
            print("\n✅ No cleanup candidates found - project is clean!")
            return 0
        else:
            print(f"\n⚠️  Found {len(all_candidates)} cleanup candidates")
            return 1

    def _generate_report(self, candidates: List[CleanupCandidate], output_path: Path):
        """Generate vacuum report.

        Args:
            candidates: List of cleanup candidates
            output_path: Path to output report file
        """
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Group by confidence
        high = [c for c in candidates if c.confidence >= 100]
        medium = [c for c in candidates if 60 <= c.confidence < 100]
        low = [c for c in candidates if c.confidence < 60]

        # Calculate total size
        total_size = sum(c.size_bytes for c in candidates)

        # Generate report
        report = [
            f"# Vacuum Report - {datetime.now().isoformat()}",
            "",
            "## Summary",
            f"- Candidates found: {len(candidates)}",
            f"- Bytes reclaimable: {self._format_size(total_size)}",
            f"- HIGH confidence: {len(high)} items (safe to delete)",
            f"- MEDIUM confidence: {len(medium)} items (review recommended)",
            f"- LOW confidence: {len(low)} items (manual verification required)",
            "",
        ]

        # HIGH confidence section
        if high:
            report.extend([
                "## HIGH Confidence (Safe to Delete)",
                "",
                "| Path | Reason | Size | Last Modified |",
                "|------|--------|------|---------------|",
            ])
            for c in high:
                rel_path = c.path.relative_to(self.project_root)
                report.append(
                    f"| {rel_path} | {c.reason} | {self._format_size(c.size_bytes)} | {c.last_modified[:10]} |"
                )
            report.append("")

        # MEDIUM confidence section
        if medium:
            report.extend([
                "## MEDIUM Confidence (Review Needed)",
                "",
                "| Path | Reason | Confidence | Git History |",
                "|------|--------|------------|-------------|",
            ])
            for c in medium:
                rel_path = c.path.relative_to(self.project_root)
                report.append(
                    f"| {rel_path} | {c.reason} | {c.confidence}% | {c.git_history} |"
                )
            report.append("")

        # LOW confidence section
        if low:
            report.extend([
                "## LOW Confidence (Manual Verification Required)",
                "",
                "| Path | Reason | Confidence | References |",
                "|------|--------|------------|------------|",
            ])
            for c in low:
                rel_path = c.path.relative_to(self.project_root)
                refs = ", ".join(c.references[:3]) if c.references else "None"
                report.append(f"| {rel_path} | {c.reason} | {c.confidence}% | {refs} |")
            report.append("")

        # Write report
        output_path.write_text("\n".join(report), encoding="utf-8")

    def _delete_candidates(self, candidates: List[CleanupCandidate], threshold: int) -> int:
        """Delete candidates meeting confidence threshold.

        Args:
            candidates: List of cleanup candidates
            threshold: Minimum confidence to delete

        Returns:
            Number of items deleted
        """
        import shutil

        deleted_count = 0

        for candidate in candidates:
            if candidate.confidence < threshold:
                continue

            try:
                if candidate.path.is_file():
                    candidate.path.unlink()
                    deleted_count += 1
                elif candidate.path.is_dir():
                    shutil.rmtree(candidate.path)
                    deleted_count += 1
            except Exception as e:
                print(f"❌ Failed to delete {candidate.path}: {e}")

        return deleted_count

    def _confirm_nuclear(self) -> bool:
        """Ask user to confirm nuclear mode.

        Returns:
            True if user confirms, False otherwise
        """
        response = input("⚠️  NUCLEAR MODE: Delete ALL candidates including LOW confidence? (yes/no): ")
        return response.lower() == "yes"

    @staticmethod
    def _format_size(size_bytes: int) -> str:
        """Format file size in human-readable format.

        Args:
            size_bytes: Size in bytes

        Returns:
            Formatted size string
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


def main():
    """CLI entry point for vacuum command."""
    parser = argparse.ArgumentParser(description="Clean up project noise")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Generate report only (default)",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Delete HIGH confidence items",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Delete HIGH + MEDIUM confidence items",
    )
    parser.add_argument(
        "--nuclear",
        action="store_true",
        help="Delete ALL items (requires confirmation)",
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=0,
        help="Minimum confidence threshold (0-100)",
    )
    parser.add_argument(
        "--exclude-strategy",
        action="append",
        dest="exclude_strategies",
        help="Skip specific strategy",
    )

    args = parser.parse_args()

    # Find project root (where .ce/ directory exists)
    current = Path.cwd()
    project_root = None

    for parent in [current] + list(current.parents):
        if (parent / ".ce").exists():
            project_root = parent
            break

    if not project_root:
        print("❌ Error: Not in a Context Engineering project (.ce/ not found)")
        return 2

    # Run vacuum command
    vacuum = VacuumCommand(project_root)
    return vacuum.run(
        dry_run=not (args.execute or args.force or args.nuclear),
        min_confidence=args.min_confidence,
        exclude_strategies=args.exclude_strategies or [],
        execute=args.execute,
        force=args.force,
        nuclear=args.nuclear,
    )


if __name__ == "__main__":
    sys.exit(main())
