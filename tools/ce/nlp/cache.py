"""JSON-based embedding cache with mtime invalidation."""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


class EmbeddingCache:
    """Caches document embeddings with mtime-based invalidation.

    Cache format:
    {
        "version": "1.0",
        "cache": {
            "path/to/file.md": {
                "mtime": 1699900000,
                "embedding": [0.12, -0.34, ...],
                "backend": "sentence-transformers"
            }
        }
    }
    """

    VERSION = "1.0"

    def __init__(self, cache_path: Optional[Path] = None):
        """Initialize cache.

        Args:
            cache_path: Path to cache file (default: .ce/nlp-embeddings-cache.json)
        """
        if cache_path is None:
            cache_path = Path(".ce/nlp-embeddings-cache.json")

        self.cache_path = cache_path
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load()

    def get(self, file_path: Path, backend: str) -> Optional[list]:
        """Get cached embedding if valid.

        Args:
            file_path: Path to file
            backend: Backend name (for cache tagging)

        Returns:
            Cached embedding or None if invalid/missing
        """
        key = str(file_path)

        if key not in self._cache:
            return None

        entry = self._cache[key]

        # Check mtime (invalidate if file modified)
        try:
            current_mtime = int(os.path.getmtime(file_path))
            if entry["mtime"] != current_mtime:
                return None  # Stale cache
        except (OSError, KeyError):
            return None

        # Return embedding if backend matches
        if entry.get("backend") == backend:
            return entry["embedding"]

        return None

    def set(self, file_path: Path, embedding: list, backend: str):
        """Cache embedding with current mtime.

        Args:
            file_path: Path to file
            embedding: Embedding vector
            backend: Backend name
        """
        try:
            mtime = int(os.path.getmtime(file_path))
        except OSError:
            return  # Can't cache if file doesn't exist

        key = str(file_path)
        self._cache[key] = {
            "mtime": mtime,
            "embedding": embedding,
            "backend": backend
        }

    def save(self):
        """Persist cache to disk."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "version": self.VERSION,
            "cache": self._cache
        }

        with open(self.cache_path, 'w') as f:
            json.dump(data, f, indent=2)

    def _load(self):
        """Load cache from disk."""
        if not self.cache_path.exists():
            return

        try:
            with open(self.cache_path, 'r') as f:
                data = json.load(f)

            # Validate version (cache version bumps when format changes)
            if data.get("version") != self.VERSION:
                import warnings
                warnings.warn(
                    f"Cache version mismatch (got {data.get('version')}, expected {self.VERSION}). "
                    f"Delete {self.cache_path} to rebuild."
                )
                return

            self._cache = data.get("cache", {})
        except (json.JSONDecodeError, IOError) as e:
            import warnings
            warnings.warn(f"Cache corrupted ({e}), rebuilding from scratch")
            self._cache = {}

    def clear(self):
        """Clear cache."""
        self._cache = {}
        if self.cache_path.exists():
            self.cache_path.unlink()
