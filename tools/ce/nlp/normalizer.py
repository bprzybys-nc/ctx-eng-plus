"""Text normalization for markdown and code content."""
import re
from pathlib import Path


class TextNormalizer:
    """Normalizes text for semantic comparison.

    Handles:
    - Code block removal (preserves semantic indicators)
    - Whitespace normalization
    - Markdown structure extraction
    - YAML frontmatter extraction
    """

    def normalize(self, text: str) -> str:
        """Normalize text for embedding.

        Args:
            text: Raw markdown/code content

        Returns:
            Normalized text suitable for embedding
        """
        # Extract YAML frontmatter metadata
        text = self._extract_yaml_keys(text)

        # Remove code blocks, preserve indicators
        text = self._normalize_code_blocks(text)

        # Extract markdown structure
        text = self._normalize_markdown(text)

        # Normalize whitespace
        text = self._normalize_whitespace(text)

        return text.strip()

    def _extract_yaml_keys(self, text: str) -> str:
        """Extract YAML frontmatter keys as searchable terms."""
        match = re.match(r'^---\n(.*?)\n---', text, re.DOTALL)
        if not match:
            return text

        yaml_content = match.group(1)
        # Extract keys: "prp_id: 42" → "prp_id"
        keys = re.findall(r'^([a-z_]+):', yaml_content, re.MULTILINE)

        # Preserve YAML keys + original content
        return ' '.join(keys) + '\n' + text[match.end():]

    def _normalize_code_blocks(self, text: str) -> str:
        """Remove code blocks, preserve semantic indicators."""
        # Match ```language\ncode\n```
        def replace_code_block(match):
            language = match.group(1) or 'code'
            code = match.group(2)

            # Extract function/class names
            functions = re.findall(r'\b(def|class|function|const|let|var)\s+(\w+)', code)
            indicators = [f"{lang}: {name}" for lang, name in functions]

            return '\n'.join(indicators) if indicators else f'[{language} code]'

        pattern = r'```(\w*)\n(.*?)\n```'
        return re.sub(pattern, replace_code_block, text, flags=re.DOTALL)

    def _normalize_markdown(self, text: str) -> str:
        """Extract markdown structure (headers, links)."""
        # Headers: "## Title" → "Title"
        text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)

        # Links: "[text](url)" → "text"
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

        # Bold/italic: "**text**" → "text"
        text = re.sub(r'\*\*([^\*]+)\*\*', r'\1', text)
        text = re.sub(r'\*([^\*]+)\*', r'\1', text)

        return text

    def _normalize_whitespace(self, text: str) -> str:
        """Collapse multiple spaces/newlines."""
        # Collapse multiple spaces
        text = re.sub(r' +', ' ', text)

        # Collapse multiple newlines
        text = re.sub(r'\n\n+', '\n\n', text)

        return text
