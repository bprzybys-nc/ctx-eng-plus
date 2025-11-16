"""NLP utilities for semantic similarity detection."""
from .similarity import DocumentSimilarity
from .normalizer import TextNormalizer
from .cache import EmbeddingCache

__all__ = ['DocumentSimilarity', 'TextNormalizer', 'EmbeddingCache']
