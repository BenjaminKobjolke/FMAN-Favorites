import importlib
import sys
import types
import unittest
from unittest.mock import Mock


class FtpFavoritesTests(unittest.TestCase):
    def setUp(self):
        self.settings = {}
        self.bookmarks = {}
        self.connections = []
        self.saved = []
        self.fman = types.ModuleType('fman')
        self.fman.DirectoryPaneCommand = type('DirectoryPaneCommand', (), {})
        self.fman.DirectoryPaneListener = type('DirectoryPaneListener', (), {})
        self.fman.QuicksearchItem = lambda item, highlight=None: types.SimpleNamespace(
            item=item, highlight=highlight)
        self.fman.show_prompt = Mock()
        self.fman.show_alert = Mock()
        self.fman.show_quicksearch = Mock()
        self.fman.show_status_message = Mock()
        self.fman.clear_status_message = Mock()

        def load_json(name, default=None, **kwargs):
            if name == 'Favorites Settings.json':
                return self.settings
            if name == 'FTP Bookmarks.json':
                return self.bookmarks
            return default

        self.fman.load_json = load_json
        self.fman.save_json = self.saved.append
        self.url_module = types.ModuleType('fman.url')
        self.url_module.as_human_readable = str
        self.url_module.as_url = str
        self.url_module.splitscheme = lambda path: ('', path)
        self.fs_module = types.ModuleType('fman.fs')
        self.fs_module.is_dir = lambda path: False
        self.core_module = types.ModuleType('core')
        self.matchers_module = types.ModuleType('core.quicksearch_matchers')
        self.matchers_module.contains_chars = lambda text, query: query in text
        self.ftpclient = types.ModuleType('ftpclient')
        self.ftpclient.__path__ = []
        self.commands = types.ModuleType('ftpclient.commands')
        self.commands._goto_ftp = Mock()
        self.ftp = types.ModuleType('ftpclient.ftp')
        self.ftp.FtpWrapper = type('FtpWrapper', (), {})
        self.ftp.FtpWrapper.get_open_connections = classmethod(
            lambda cls: self.connections)
        self.ftpclient.commands = self.commands
        self.ftpclient.ftp = self.ftp
        sys.modules.update({
            'fman': self.fman,
            'fman.url': self.url_module,
            'fman.fs': self.fs_module,
            'core': self.core_module,
            'core.quicksearch_matchers': self.matchers_module,
            'ftpclient': self.ftpclient,
            'ftpclient.commands': self.commands,
            'ftpclient.ftp': self.ftp,
        })
        sys.modules.pop('favorites', None)
        self.favorites = importlib.import_module('favorites')

    def tearDown(self):
        sys.modules.pop('favorites', None)
        for name in ('fman', 'fman.url', 'fman.fs', 'core',
                     'core.quicksearch_matchers', 'ftpclient',
                     'ftpclient.commands', 'ftpclient.ftp'):
            sys.modules.pop(name, None)

    def test_missing_ftp_plugin_is_detected_and_toggle_hidden(self):
        for name in ('ftpclient', 'ftpclient.commands', 'ftpclient.ftp'):
            sys.modules.pop(name, None)
        self.assertIsNone(self.favorites._ftp())
        self.assertFalse(self.favorites.ToggleFtpInFavorites().is_visible())

    def test_toggle_persists_new_state_and_reports_it(self):
        command = self.favorites.ToggleFtpInFavorites()

        command()

        self.assertTrue(self.settings['show_ftp'])
        self.assertEqual(['Favorites Settings.json'], self.saved)
        self.fman.show_alert.assert_called_once_with('FTP in Favorites is on.')

    def test_suggestions_include_ftp_items_only_when_enabled(self):
        alias = 'ftp://example.test'
        self.bookmarks[alias] = ('ftp://example.test', '/home')
        self.connections.append(
            ('ftp://connected.test', 'ftp://connected.test/docs'))
        command = self.favorites.GoToFavorite()

        self.assertEqual(
            [], [item.item for item in command._suggest_directory('')
                 if item.item.startswith('FTP')])
        self.settings['show_ftp'] = True
        names = [item.item for item in command._suggest_directory('')]
        self.assertIn('FTP: ' + alias, names)
        self.assertIn('FTP open: ftp://connected.test', names)

    def test_bookmark_selection_opens_url_at_bookmark_default_path(self):
        alias = 'ftp://example.test'
        self.bookmarks[alias] = ('ftp://example.test', '/home/docs')
        command = self.favorites.GoToFavorite()
        command.pane = Mock()
        self.fman.show_quicksearch.return_value = ('', 'FTP: ' + alias)

        command()

        self.commands._goto_ftp.assert_called_once_with(
            command.pane, 'ftp://example.test/home/docs')

    def test_open_connection_selection_navigates_to_last_url(self):
        base_url = 'ftp://connected.test'
        last_url = base_url + '/docs'
        self.connections.append((base_url, last_url))
        command = self.favorites.GoToFavorite()
        command.pane = Mock()
        self.fman.show_quicksearch.return_value = (
            '', 'FTP open: ' + base_url)

        command()

        command.pane.set_path.assert_called_once_with(last_url)


if __name__ == '__main__':
    unittest.main()
