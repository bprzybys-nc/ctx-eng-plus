"""Document similarity with 3-tier fallback."""
from pathlib import Path
from typing import Optional, Tuple
import difflib

from .normalizer import TextNormalizer
from .cache import EmbeddingCache


class DocumentSimilarity:
    """Computes document similarity with 3-tier fallback.

    Tier 1: sentence-transformers (0.85+ accuracy, requires install)
    Tier 2: sklearn TF-IDF (0.70+ accuracy, requires scikit-learn)
    Tier 3: difflib (0.50+ accuracy, stdlib baseline)
    """

    def __init__(self, cache_path: Optional[Path] = None):
        """Initialize similarity engine.

        Args:
            cache_path: Path to embedding cache
        """
        self.normalizer = TextNormalizer()
        self.cache = EmbeddingCache(cache_path)
        self.backend_name = self._detect_backend()
        self._backend = self._init_backend()

    def _detect_backend(self) -> str:
        """Detect available backend (Tier 1 → Tier 2 → Tier 3)."""
        try:
            import sentence_transformers
            return "sentence-transformers"
        except ImportError:
            pass

        try:
            import sklearn
            return "sklearn"
        except ImportError:
            pass

        return "difflib"

    def _init_backend(self):
        """Initialize detected backend with graceful fallback."""
        if self.backend_name == "sentence-transformers":
            try:
                from sentence_transformers import SentenceTransformer
                # Model auto-downloads to ~/.cache/huggingface/
                return SentenceTransformer('all-MiniLM-L6-v2')
            except ImportError:
                # Fallback to next tier if import fails
                self.backend_name = "sklearn"
                return self._init_backend()  # Recursive fallback

        elif self.backend_name == "sklearn":
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                return TfidfVectorizer(max_features=384)  # Match embedding dim
            except ImportError:
                # Fallback to difflib baseline
                self.backend_name = "difflib"
                return self._init_backend()  # Recursive fallback

        else:
            return None  # difflib doesn't need initialization

    def compare(self, file_a: Path, file_b: Path) -> float:
        """Compute similarity between two files.

        Args:
            file_a: First file path
            file_b: Second file path

        Returns:
            Similarity score 0.0-1.0 (higher = more similar)
        """
        # Read and normalize content
        text_a = self._read_and_normalize(file_a)
        text_b = self._read_and_normalize(file_b)

        if self.backend_name == "sentence-transformers":
            return self._compare_transformers(file_a, file_b, text_a, text_b)
        elif self.backend_name == "sklearn":
            return self._compare_sklearn(text_a, text_b)
        else:
            return self._compare_difflib(text_a, text_b)

    def _read_and_normalize(self, file_path: Path) -> str:
        """Read file and normalize content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self.normalizer.normalize(content)
        except (IOError, UnicodeDecodeError):
            return ""  # Binary or unreadable file

    def _compare_transformers(self, file_a: Path, file_b: Path, text_a: str, text_b: str) -> float:
        """Compare using sentence-transformers with caching."""
        # Try cache first
        emb_a = self.cache.get(file_a, "sentence-transformers")
        emb_b = self.cache.get(file_b, "sentence-transformers")

        # Compute missing embeddings
        if emb_a is None:
            emb_a = self._backend.encode(text_a).tolist()
            self.cache.set(file_a, emb_a, "sentence-transformers")

        if emb_b is None:
            emb_b = self._backend.encode(text_b).tolist()
            self.cache.set(file_b, emb_b, "sentence-transformers")

        # Cosine similarity
        import numpy as np
        emb_a = np.array(emb_a)
        emb_b = np.array(emb_b)

        similarity = np.dot(emb_a, emb_b) / (np.linalg.norm(emb_a) * np.linalg.norm(emb_b))
        return float(similarity)

    def _compare_sklearn(self, text_a: str, text_b: str) -> float:
        """Compare using sklearn TF-IDF."""
        vectors = self._backend.fit_transform([text_a, text_b])

        # Cosine similarity between sparse vectors
        from sklearn.metrics.pairwise import cosine_similarity
        similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
        return float(similarity)

    def _compare_difflib(self, text_a: str, text_b: str) -> float:
        """Compare using difflib SequenceMatcher."""
        matcher = difflib.SequenceMatcher(None, text_a, text_b)
        return matcher.ratio()

    def __del__(self):
        """Save cache on cleanup."""
        try:
            self.cache.save()
        except Exception as e:
            # Log warning instead of silent failure
            import warnings
            warnings.warn(f"Failed to save NLP cache: {e}")
