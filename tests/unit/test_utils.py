"""
Unit tests for utility functions
"""
import pytest
from src.utils import generate_id, get_timestamp, get_ttl, truncate_text


def test_generate_id():
    """Test ID generation"""
    id1 = generate_id()
    id2 = generate_id()

    assert id1 != id2
    assert len(id1) == 36  # UUID length

    # Test with prefix
    prefixed = generate_id("test-")
    assert prefixed.startswith("test-")
    assert len(prefixed) == 41  # prefix + UUID


def test_get_timestamp():
    """Test timestamp generation"""
    ts1 = get_timestamp()
    ts2 = get_timestamp()

    assert isinstance(ts1, int)
    assert ts2 >= ts1


def test_get_ttl():
    """Test TTL calculation"""
    ttl = get_ttl(7)

    assert isinstance(ttl, int)
    assert ttl > get_timestamp() / 1000  # TTL should be in the future


def test_truncate_text():
    """Test text truncation"""
    text = "This is a long text that needs to be truncated"

    # Test normal truncation
    truncated = truncate_text(text, max_length=20)
    assert len(truncated) == 20
    assert truncated.endswith("...")

    # Test text shorter than max_length
    short = "Short text"
    assert truncate_text(short, max_length=20) == short
