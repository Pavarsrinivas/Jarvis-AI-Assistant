"""
helpers.py
----------
Small, dependency-free utility functions shared across JARVIS modules
(text cleanup, time formatting, safe casting, etc.).
"""

import re
from datetime import datetime
from typing import Optional


def clean_text(text: str) -> str:
    """Collapse whitespace and strip leading/trailing spaces from `text`."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def contains_any(text: str, keywords: list) -> bool:
    """Case-insensitive check for whether any keyword appears in `text`."""
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def human_readable_time(dt: Optional[datetime] = None) -> str:
    """Return a friendly 12-hour clock string, e.g. '3:45 PM'."""
    dt = dt or datetime.now()
    return dt.strftime("%I:%M %p").lstrip("0")


def human_readable_date(dt: Optional[datetime] = None) -> str:
    """Return a friendly date string, e.g. 'Monday, September 07, 2026'."""
    dt = dt or datetime.now()
    return dt.strftime("%A, %B %d, %Y")


def safe_int(value: str, default: int = 0) -> int:
    """Convert `value` to int, returning `default` on failure."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def truncate(text: str, max_len: int = 200, suffix: str = "...") -> str:
    """Shorten `text` to at most `max_len` characters, appending `suffix` if cut."""
    if not text or len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)].rstrip() + suffix
