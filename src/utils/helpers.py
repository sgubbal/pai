"""
Helper utilities for PAI Agent
"""
import uuid
import time
from datetime import datetime, timedelta
from typing import Optional


def generate_id(prefix: str = "") -> str:
    """
    Generate a unique ID

    Args:
        prefix: Optional prefix for the ID

    Returns:
        Unique identifier string
    """
    unique_id = str(uuid.uuid4())
    return f"{prefix}{unique_id}" if prefix else unique_id


def get_timestamp() -> int:
    """
    Get current Unix timestamp in milliseconds

    Returns:
        Current timestamp as integer
    """
    return int(time.time() * 1000)


def get_ttl(days: int) -> int:
    """
    Get TTL (time to live) timestamp for DynamoDB

    Args:
        days: Number of days until expiration

    Returns:
        Unix timestamp for TTL
    """
    expiration = datetime.utcnow() + timedelta(days=days)
    return int(expiration.timestamp())


def parse_timestamp(timestamp: int) -> datetime:
    """
    Parse Unix timestamp to datetime

    Args:
        timestamp: Unix timestamp in milliseconds

    Returns:
        datetime object
    """
    return datetime.fromtimestamp(timestamp / 1000)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to maximum length

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def chunk_list(items: list, chunk_size: int) -> list:
    """
    Split a list into chunks

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get(dictionary: dict, key: str, default: Optional[any] = None) -> any:
    """
    Safely get value from dictionary

    Args:
        dictionary: Dictionary to get value from
        key: Key to retrieve
        default: Default value if key not found

    Returns:
        Value from dictionary or default
    """
    return dictionary.get(key, default)
