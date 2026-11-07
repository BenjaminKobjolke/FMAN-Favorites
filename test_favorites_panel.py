import os
import tempfile
import unittest
from unittest.mock import Mock, patch

from test_ftp_favorites import FavoritesTestBase


class FavoritesPanelTests(FavoritesTestBase):
    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.favorite_file = os.path.join(self.temp_dir.name, 'favorites')
        self.pair_file = os.path.join(self.temp_dir.name, 'pairs')

    def _write(self, path, contents):
        with open(path, 'w') as file:
            file.write(contents)

    def test_build_panel_sections_contains_favorites_pairs_and_history(self):
        from favorites import favorite_commands, pair_commands, pop_dir
        from favorites.panel_entries import EntryKind, build_panel_sections

        self._write(self.favorite_file, 'Work|~/work\n')
        self._write(self.pair_file, 'Code|~/code|~/other\n')
        pop_dir.POPDIR = ['/new', '/old'] + [''] * 8
        pop_dir.LASTPOP = 1
        self.settings['show_ftp'] = True
        self.bookmarks['ftp://example.test'] = ('ftp://example.test', '/')
        self.connections.append(('ftp://connected.test', 'ftp://connected.test/docs'))

        with patch.object(favorite_commands, 'FAVORITELIST', self.favorite_file), \
                patch.object(pair_commands, 'FAVORITEPAIRS', self.pair_file):
            sections = build_panel_sections()

        self.assertEqual(['Favorites', 'Favorite pairs', 'History'],
                         [section.title for section in sections])
        self.assertEqual(
            [(EntryKind.FAVORITE, 'Home'), (EntryKind.FAVORITE, 'Work'),
             (EntryKind.FAVORITE, 'FTP: ftp://example.test'),
             (EntryKind.FAVORITE, 'FTP open: ftp://connected.test')],
            [(entry.kind, entry.label) for entry in sections[0].entries])
        self.assertEqual(
            [(EntryKind.PAIR, 'Home'), (EntryKind.PAIR, 'Code')],
            [(entry.kind, entry.label) for entry in sections[1].entries])
        self.assertEqual(
            [(EntryKind.HISTORY, '/old'), (EntryKind.HISTORY, '/new')],
            [(entry.kind, entry.label) for entry in sections[2].entries])

    def test_recent_dirs_walks_wrapped_ring_newest_first_without_duplicates(self):
        from favorites import pop_dir

        pop_dir.POPDIR = ['/dup', '/one', '/two', '/dup', '', '/five',
                          '/six', '/seven', '/eight', '/nine']
        pop_dir.LASTPOP = 5

        self.assertEqual(['/five', '/dup', '/two', '/one', '/nine',
                          '/eight', '/seven', '/six'], pop_dir.recent_dirs())

    def test_open_panel_entry_routes_each_kind_and_focuses(self):
        from favorites.favorites_panel import OpenFavoritesPanelEntry
        from favorites import favorites_panel
        from favorites.panel_entries import EntryKind

        pane = Mock(spec=['run_command', 'set_path', 'focus', 'get_colors',
                          'get_mounted_widget', 'window', 'get_path'])
        pair_panes = [Mock(spec=['run_command', 'set_path', 'focus', 'get_path']),
                      Mock(spec=['run_command', 'set_path', 'focus', 'get_path'])]
        pane.window.get_panes.return_value = pair_panes
        command = OpenFavoritesPanelEntry()
        command.pane = pane

        with patch.object(favorites_panel, 'open_favorite') as open_favorite, \
                patch.object(favorites_panel, 'open_favorite_pair') as open_pair:
            command(EntryKind.FAVORITE.value, 'Work')
            open_favorite.assert_called_once_with(pane, 'Work')
            command(EntryKind.PAIR.value, 'Code')
            open_pair.assert_called_once_with(pane.window, 'Code')
            command(EntryKind.HISTORY.value, '/recent')

        pane.set_path.assert_called_once_with('/recent')
        self.assertEqual(3, pane.focus.call_count)

    def test_open_panel_entry_rejects_unknown_kind(self):
        from favorites.favorites_panel import OpenFavoritesPanelEntry

        command = OpenFavoritesPanelEntry()
        command.pane = Mock(spec=['focus'])

        with self.assertRaises(ValueError):
            command('unknown', 'value')

    def test_path_change_refreshes_open_panels(self):
        from favorites import pop_dir
        from favorites import favorites_panel

        pane = Mock(spec=['get_path', 'window'])
        pane.get_path.return_value = '/visited'
        listener = pop_dir.PopdirectoryListener()
        listener.pane = pane

        with patch.object(favorites_panel, 'refresh_open_panels') as refresh:
            listener.on_path_changed()

        refresh.assert_called_once_with(pane.window)


try:
    from PyQt5.QtCore import Qt
    from PyQt5.QtWidgets import QApplication, QListWidgetItem
    from PyQt5.QtTest import QTest
except ImportError:
    Qt = QApplication = QTest = None


@unittest.skipIf(QApplication is None, 'PyQt5 is not installed')
class FavoritesPanelWidgetTests(FavoritesTestBase):
    @classmethod
    def setUpClass(cls):
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'
        cls.app = QApplication.instance() or QApplication([])

    def test_keyboard_activation_and_panel_controls(self):
        from favorites.favorites_panel import FavoritesPanelView

        source = Mock(spec=['run_command', 'set_path', 'focus', 'get_path'])
        panel = Mock(spec=['run_command', 'set_path', 'focus', 'get_colors',
                           'get_mounted_widget', 'window'])
        other = Mock(spec=['run_command', 'set_path', 'focus', 'get_path'])
        panel.window.get_panes.return_value = [source, panel, other]
        view = FavoritesPanelView(source, panel, ('#101010', '#eeeeee'))
        view.refresh = Mock()
        view.setCurrentItem(view.item(1))
        QTest.keyClick(view, Qt.Key_Return)
        source.run_command.assert_called_once_with(
            'open_favorites_panel_entry', {'kind': 'favorite', 'value': 'Home'})

        source.run_command.reset_mock()
        view.setCurrentItem(view.item(0))
        QTest.keyClick(view, Qt.Key_Return)
        source.run_command.assert_not_called()

        QTest.keyClick(view, Qt.Key_Escape)
        panel.run_command.assert_called_once_with('remove_pane')
        QTest.keyClick(view, Qt.Key_Tab)
        panel.run_command.assert_called_with('switch_panes')

    def test_activation_falls_back_when_source_pane_was_removed(self):
        from favorites.favorites_panel import FavoritesPanelView
        from favorites.panel_entries import EntryKind, PanelEntry

        source = Mock(spec=['run_command', 'set_path', 'focus', 'get_path'])
        panel = Mock(spec=['run_command', 'set_path', 'focus', 'get_colors',
                           'get_mounted_widget', 'window'])
        other = Mock(spec=['run_command', 'set_path', 'focus', 'get_path'])
        panel.window.get_panes.return_value = [other, panel]
        view = FavoritesPanelView(source, panel, ('#101010', '#eeeeee'))
        entry = PanelEntry(EntryKind.HISTORY, '/recent', '/recent')
        item = QListWidgetItem(entry.label)
        view.addItem(item)
        item.setData(Qt.UserRole, entry)
        view.setCurrentItem(item)

        QTest.keyClick(view, Qt.Key_Return)

        other.run_command.assert_called_once_with(
            'open_favorites_panel_entry', {'kind': 'history', 'value': '/recent'})
