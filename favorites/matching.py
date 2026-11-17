"""Quicksearch matching helpers for favorite names."""

from typing import List, Optional

def match_query(text: str, query: str) -> Optional[List[int]]:
    """Match a query in order first, then allow its words in any order."""
    from core.quicksearch_matchers import contains_chars, contains_chars_any_order

    text, query = text.lower(), query.lower()
    return contains_chars(text, query) or contains_chars_any_order(text, query)
