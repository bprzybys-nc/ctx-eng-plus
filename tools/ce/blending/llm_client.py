"""LLM client for blending operations with Haiku + Sonnet hybrid support."""

import os
import logging
from typing import Dict, Any, Optional, List
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Model configurations
HAIKU_MODEL = "claude-3-5-haiku-20241022"
SONNET_MODEL = "claude-sonnet-4-5-20250929"

# Blending philosophy system prompt
BLENDING_PHILOSOPHY = """
Blending Philosophy: "Copy ours (framework), import theirs (target) where not contradictory"

Rules:
1. Framework content is authoritative - preserve all framework sections
2. Target customizations that don't contradict framework are preserved
3. When conflict exists, framework wins (with explanation comment)
4. Additive merging preferred - combine rather than replace
5. User-specific content (names, paths, project details) always preserved
"""


class BlendingLLM:
    """
    Claude SDK wrapper for blending operations.

    Provides hybrid model support:
    - Haiku: Fast/cheap classification and similarity checks
    - Sonnet: High-quality document blending

    Usage:
        >>> llm = BlendingLLM()
        >>> result = llm.blend_content(framework, target, rules)
        >>> similarity = llm.check_similarity(text1, text2)
        >>> classification = llm.classify_file(content)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 60,
        max_retries: int = 3
    ):
        """
        Initialize LLM client.

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            timeout: Request timeout in seconds (default: 60)
            max_retries: Max retry attempts for rate limits (default: 3)

        Raises:
            ValueError: If API key not provided and not in environment
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if not self.api_key:
            raise ValueError(
                "Anthropic API key required\n"
                "🔧 Troubleshooting:\n"
                "  1. Set ANTHROPIC_API_KEY environment variable\n"
                "  2. Or pass api_key parameter to BlendingLLM()\n"
                "  3. Get key from: https://console.anthropic.com/settings/keys"
            )

        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize Anthropic client
        try:
            self.client = Anthropic(
                api_key=self.api_key,
                timeout=timeout,
                max_retries=max_retries
            )
            logger.debug("✓ BlendingLLM initialized")
        except Exception as e:
            raise RuntimeError(
                f"Failed to initialize Anthropic client: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Verify network connectivity\n"
                f"  3. Check Anthropic status: https://status.anthropic.com"
            ) from e

        # Token usage tracking
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def get_token_usage(self) -> Dict[str, int]:
        """
        Get cumulative token usage.

        Returns:
            Dict with input_tokens, output_tokens, total_tokens
        """
        return {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }

    def _track_tokens(self, usage: Any) -> None:
        """Track tokens from API response usage object."""
        if usage:
            self.total_input_tokens += getattr(usage, 'input_tokens', 0)
            self.total_output_tokens += getattr(usage, 'output_tokens', 0)

    def blend_content(
        self,
        framework_content: str,
        target_content: Optional[str],
        rules_content: Optional[str] = None,
        domain: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Blend framework and target content using Sonnet.

        Uses high-quality model for semantic understanding of blending philosophy.

        Args:
            framework_content: Framework version (authoritative)
            target_content: Target version (may be None)
            rules_content: Framework rules (e.g., RULES.md content)
            domain: Domain name for context (e.g., "claude_md", "memories")

        Returns:
            Dict with:
                - blended: Blended content (str)
                - model: Model used (str)
                - tokens: Token usage dict
                - confidence: Blend confidence 0.0-1.0 (float)

        Raises:
            RuntimeError: If API call fails after retries
        """
        logger.info(f"Blending {domain} content with Sonnet...")

        # Build prompt
        prompt_parts = [BLENDING_PHILOSOPHY]

        if rules_content:
            prompt_parts.append(f"\n## Framework Rules\n\n{rules_content}")

        prompt_parts.append(f"\n## Framework Content\n\n{framework_content}")

        if target_content:
            prompt_parts.append(f"\n## Target Content\n\n{target_content}")
        else:
            # No target content - just validate framework
            prompt_parts.append("\n## Target Content\n\n(No existing content)")

        prompt_parts.append(
            f"\n## Task\n\n"
            f"Blend the framework and target content for the '{domain}' domain. "
            f"Follow the blending philosophy above. Output ONLY the blended content, "
            f"no explanations or markdown code blocks."
        )

        prompt = "".join(prompt_parts)

        try:
            # Call Sonnet
            response = self.client.messages.create(
                model=SONNET_MODEL,
                max_tokens=8192,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Track tokens
            self._track_tokens(response.usage)

            # Extract blended content
            blended = response.content[0].text

            # Calculate confidence (heuristic: presence of both framework and target markers)
            confidence = 1.0
            if target_content and target_content.strip():
                # Check if blend includes elements from both
                has_framework = any(
                    marker in blended
                    for marker in ["## Core Principles", "## Quick Commands"]
                )
                has_target = len(blended) > len(framework_content) * 0.8
                confidence = 0.9 if (has_framework and has_target) else 0.7

            logger.info(
                f"✓ Blended {domain} "
                f"({response.usage.input_tokens} in, "
                f"{response.usage.output_tokens} out)"
            )

            return {
                "blended": blended,
                "model": SONNET_MODEL,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                },
                "confidence": confidence
            }

        except Exception as e:
            logger.error(f"❌ Blending failed: {e}")
            raise RuntimeError(
                f"Sonnet blend_content() failed for {domain}: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Check network connectivity\n"
                f"  3. Verify content size < 200k tokens\n"
                f"  4. Check rate limits: https://console.anthropic.com/settings/limits"
            ) from e

    def check_similarity(
        self,
        text1: str,
        text2: str,
        threshold: float = 0.9
    ) -> Dict[str, Any]:
        """
        Check semantic similarity between two texts using Haiku.

        Fast, cheap operation for similarity scoring.

        Args:
            text1: First text
            text2: Second text
            threshold: Similarity threshold 0.0-1.0 (default: 0.9)

        Returns:
            Dict with:
                - similar: Boolean (similarity >= threshold)
                - score: Similarity score 0.0-1.0 (float)
                - model: Model used (str)
                - tokens: Token usage dict

        Raises:
            RuntimeError: If API call fails after retries
        """
        logger.debug("Checking similarity with Haiku...")

        prompt = f"""Compare these two texts for semantic similarity.

Text 1:
{text1[:1000]}...

Text 2:
{text2[:1000]}...

Rate similarity on scale 0.0-1.0 where:
- 0.0 = Completely different topics/purposes
- 0.5 = Related but distinct content
- 0.9 = Very similar, likely duplicates
- 1.0 = Identical or nearly identical

Output ONLY a number between 0.0 and 1.0, nothing else."""

        try:
            response = self.client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Track tokens
            self._track_tokens(response.usage)

            # Parse similarity score
            score_text = response.content[0].text.strip()
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))  # Clamp to [0.0, 1.0]
            except ValueError:
                # Failed to parse - default to low similarity
                logger.warning(f"Failed to parse similarity score: {score_text}")
                score = 0.0

            similar = score >= threshold

            logger.debug(
                f"Similarity: {score:.2f} ({'similar' if similar else 'different'})"
            )

            return {
                "similar": similar,
                "score": score,
                "model": HAIKU_MODEL,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"❌ Similarity check failed: {e}")
            raise RuntimeError(
                f"Haiku check_similarity() failed: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Check network connectivity\n"
                f"  3. Verify text size reasonable (< 1000 chars per text)\n"
                f"  4. Check rate limits"
            ) from e

    def classify_file(
        self,
        content: str,
        expected_patterns: List[str],
        file_path: str = "unknown"
    ) -> Dict[str, Any]:
        """
        Classify file content for CE pattern compliance using Haiku.

        Fast validation for Phase B classification.

        Args:
            content: File content to classify
            expected_patterns: List of expected CE patterns (e.g., ["YAML header", "## sections"])
            file_path: File path for context

        Returns:
            Dict with:
                - valid: Boolean (passes CE pattern checks)
                - confidence: Confidence score 0.0-1.0 (float)
                - issues: List of validation issues (List[str])
                - model: Model used (str)
                - tokens: Token usage dict

        Raises:
            RuntimeError: If API call fails after retries
        """
        logger.debug(f"Classifying {file_path} with Haiku...")

        patterns_text = "\n".join(f"- {p}" for p in expected_patterns)

        prompt = f"""Validate this file against CE (Context Engineering) patterns.

File: {file_path}

Expected patterns:
{patterns_text}

Content (first 2000 chars):
{content[:2000]}...

Respond in this format:
VALID: yes/no
CONFIDENCE: 0.0-1.0
ISSUES: comma-separated list of issues (or "none")

Example:
VALID: yes
CONFIDENCE: 0.95
ISSUES: none"""

        try:
            response = self.client.messages.create(
                model=HAIKU_MODEL,
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Track tokens
            self._track_tokens(response.usage)

            # Parse classification result
            result_text = response.content[0].text.strip()

            valid = False
            confidence = 0.0
            issues = []

            for line in result_text.split('\n'):
                line = line.strip()
                if line.startswith('VALID:'):
                    valid = 'yes' in line.lower()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':')[1].strip())
                        confidence = max(0.0, min(1.0, confidence))
                    except (ValueError, IndexError):
                        confidence = 0.5
                elif line.startswith('ISSUES:'):
                    issues_text = line.split(':', 1)[1].strip()
                    if issues_text.lower() != 'none':
                        issues = [i.strip() for i in issues_text.split(',')]

            logger.debug(
                f"Classification: {'valid' if valid else 'invalid'} "
                f"(confidence: {confidence:.2f})"
            )

            return {
                "valid": valid,
                "confidence": confidence,
                "issues": issues,
                "model": HAIKU_MODEL,
                "tokens": {
                    "input": response.usage.input_tokens,
                    "output": response.usage.output_tokens
                }
            }

        except Exception as e:
            logger.error(f"❌ Classification failed: {e}")
            raise RuntimeError(
                f"Haiku classify_file() failed for {file_path}: {e}\n"
                f"🔧 Troubleshooting:\n"
                f"  1. Check API key is valid\n"
                f"  2. Check network connectivity\n"
                f"  3. Verify content size < 200k tokens\n"
                f"  4. Check rate limits"
            ) from e
