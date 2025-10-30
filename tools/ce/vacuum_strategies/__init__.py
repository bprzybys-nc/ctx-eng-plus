"""Vacuum strategies for project cleanup."""

from .base import BaseStrategy, CleanupCandidate
from .temp_files import TempFileStrategy
from .backup_files import BackupFileStrategy
from .obsolete_docs import ObsoleteDocStrategy
from .unreferenced_code import UnreferencedCodeStrategy
from .orphan_tests import OrphanTestStrategy
from .commented_code import CommentedCodeStrategy

__all__ = [
    "BaseStrategy",
    "CleanupCandidate",
    "TempFileStrategy",
    "BackupFileStrategy",
    "ObsoleteDocStrategy",
    "UnreferencedCodeStrategy",
    "OrphanTestStrategy",
    "CommentedCodeStrategy",
]
