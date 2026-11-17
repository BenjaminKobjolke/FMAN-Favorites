"""Tests for the favorites quicksearch matching helper."""

import importlib.util
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import patch


TEXT = 'FTP: ftp://_XIDA - erp.xida.de'
MATCHING_PATH = Path(__file__).parent / 'favorites' / 'matching.py'


def _contains_chars(text, query):
    positions = []
    start = 0
    for character in query:
        position = text.find(character, start)
        if position == -1:
            return None
        positions.append(position)
        start = position + 1
    return positions


def _contains_chars_any_order(text, query):
    positions = set()
    for word in query.split():
        start = text.find(word)
        if start == -1:
            return None
        positions.update(range(start, start + len(word)))
    return sorted(positions)


def _load_match_query():
    core = types.ModuleType('core')
    matchers = types.ModuleType('core.quicksearch_matchers')
    matchers.contains_chars = _contains_chars
    matchers.contains_chars_any_order = _contains_chars_any_order
    spec = importlib.util.spec_from_file_location(
        'favorites_matching_test_subject', MATCHING_PATH)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {
            'core': core,
            'core.quicksearch_matchers': matchers,
    }):
        spec.loader.exec_module(module)

    def match_query(text, query):
        with patch.dict(sys.modules, {
                'core': core,
                'core.quicksearch_matchers': matchers,
        }):
            return module.match_query(text, query)

    return match_query


class MatchQueryTests(unittest.TestCase):
    def test_module_import_does_not_require_fman_core(self):
        spec = importlib.util.spec_from_file_location(
            'favorites_matching_test_subject', MATCHING_PATH)
        module = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {
                'core': None,
                'core.quicksearch_matchers': None,
        }):
            spec.loader.exec_module(module)

        self.assertTrue(callable(module.match_query))

    def test_matches_words_in_any_order(self):
        match_query = _load_match_query()

        self.assertIsNotNone(match_query(TEXT, 'erp ftp'))

    def test_keeps_ordered_match_highlights(self):
        match_query = _load_match_query()

        self.assertEqual(
            _contains_chars(TEXT.lower(), 'ftp erp'),
            match_query(TEXT, 'ftp erp'),
        )

    def test_rejects_query_with_missing_word(self):
        match_query = _load_match_query()

        self.assertIsNone(match_query(TEXT, 'erp zzz'))


if __name__ == '__main__':
    unittest.main()
