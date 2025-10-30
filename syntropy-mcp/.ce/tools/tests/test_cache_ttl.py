"""Tests for cache TTL configuration (PRP-21 Phase 2.1).

Tests verify that cache TTL can be configured via environment and config file.
"""

import pytest
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path
from ce.update_context import get_cache_ttl, is_cache_valid


def test_get_cache_ttl_default():
    """Cache TTL should default to 5 minutes."""
    # Clear env var if set
    os.environ.pop("CONTEXT_CACHE_TTL", None)

    ttl = get_cache_ttl()
    assert ttl == 5


def test_get_cache_ttl_from_env(monkeypatch):
    """Cache TTL should read from CONTEXT_CACHE_TTL environment variable."""
    monkeypatch.setenv("CONTEXT_CACHE_TTL", "10")

    ttl = get_cache_ttl()
    assert ttl == 10


def test_get_cache_ttl_env_minimum(monkeypatch):
    """Cache TTL should enforce minimum of 1 minute."""
    monkeypatch.setenv("CONTEXT_CACHE_TTL", "0")

    ttl = get_cache_ttl()
    assert ttl >= 1


def test_is_cache_valid_fresh():
    """Fresh cache should be valid."""
    now = datetime.now(timezone.utc)
    cached = {
        "generated_at": now.isoformat(),
        "drift_score": 5.0,
        "report_path": "/tmp/report.md"
    }

    # Should be valid with 5 minute TTL
    is_valid = is_cache_valid(cached, ttl_minutes=5)
    assert is_valid is True


def test_is_cache_valid_expired():
    """Expired cache should be invalid."""
    # Cache from 10 minutes ago
    old_time = datetime.now(timezone.utc) - timedelta(minutes=10)
    cached = {
        "generated_at": old_time.isoformat(),
        "drift_score": 5.0,
        "report_path": "/tmp/report.md"
    }

    # Should be invalid with 5 minute TTL
    is_valid = is_cache_valid(cached, ttl_minutes=5)
    assert is_valid is False


def test_is_cache_valid_uses_configured_ttl(monkeypatch):
    """is_cache_valid should use configured TTL when not specified."""
    # Cache from 7 minutes ago
    old_time = datetime.now(timezone.utc) - timedelta(minutes=7)
    cached = {
        "generated_at": old_time.isoformat(),
        "drift_score": 5.0,
        "report_path": "/tmp/report.md"
    }

    # Set env to 10 minute TTL
    monkeypatch.setenv("CONTEXT_CACHE_TTL", "10")

    # Should be valid because env TTL is 10 minutes, cache is only 7 minutes old
    is_valid = is_cache_valid(cached, ttl_minutes=0)  # 0 means use configured
    assert is_valid is True
