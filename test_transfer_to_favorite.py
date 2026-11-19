"""Tests for copying and moving selected files to favorite directories."""

import os
import tempfile
from unittest.mock import Mock

from test_ftp_favorites import FavoritesTestBase


class _Pane:
    def get_path(self):
        pass

    def run_command(self, command, arguments):
        pass

    def set_path(self, path):
        pass


class TransferToFavoriteTests(FavoritesTestBase):

    def setUp(self):
        super().setUp()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.favorites.paths.FAVORITELIST = os.path.join(
            self.temp_dir.name, '.favoritedirs')
        self.favorites.paths.SHORTENERLIST = os.path.join(
            self.temp_dir.name, '.shortenerdirs')
        self.favorite_commands = self.favorites.favorite_commands
        self.favorite_commands.FAVORITELIST = self.favorites.paths.FAVORITELIST

    def _write_favorites(self, contents):
        with open(self.favorites.paths.FAVORITELIST, 'w') as file:
            file.write(contents)

    def test_favorite_url_resolves_plain_shortened_and_home_paths(self):
        root = self.temp_dir.name
        self._write_favorites(
            'Plain|' + os.path.join(root, 'plain') + '\n'
            'Shortened|{{work}}/project\n')
        with open(self.favorites.paths.SHORTENERLIST, 'w') as file:
            file.write('work|' + root + '\n')

        self.assertEqual(
            os.path.join(root, 'plain'),
            self.favorite_commands.favorite_url('Plain'))
        self.assertEqual(
            os.path.normpath(os.path.join(root, 'project')),
            os.path.normpath(
                self.favorite_commands.favorite_url('Shortened')))
        self.assertEqual(os.path.expanduser('~'),
                         self.favorite_commands.favorite_url('Home'))
        self.assertIsNone(self.favorite_commands.favorite_url('Unknown'))

    def test_copy_to_favorite_runs_copy_to_resolved_url(self):
        destination = os.path.join(self.temp_dir.name, 'destination')
        self._write_favorites('Project|' + destination + '\n')
        command = self.favorites.CopyToFavorite()
        command.pane = Mock(spec=_Pane)
        self.fman.show_quicksearch.return_value = ('', 'Project')

        command()

        command.pane.run_command.assert_called_once_with(
            'copy', {'dest_dir': destination})

    def test_move_to_favorite_runs_move_to_resolved_url(self):
        destination = os.path.join(self.temp_dir.name, 'destination')
        self._write_favorites('Project|' + destination + '\n')
        command = self.favorites.MoveToFavorite()
        command.pane = Mock(spec=_Pane)
        self.fman.show_quicksearch.return_value = ('', 'Project')

        command()

        command.pane.run_command.assert_called_once_with(
            'move', {'dest_dir': destination})

    def test_cancelled_transfer_does_not_run_command(self):
        command = self.favorites.CopyToFavorite()
        command.pane = Mock(spec=_Pane)
        self.fman.show_quicksearch.return_value = None

        command()

        command.pane.run_command.assert_not_called()

    def test_transfer_suggestions_include_only_local_favorites(self):
        self._write_favorites('Project|' + self.temp_dir.name + '\n')
        self.settings['show_ftp'] = True
        self.bookmarks['ftp://example.test'] = (
            'ftp://example.test', '/home')
        command = self.favorites.CopyToFavorite()

        self.assertEqual(
            ['Home', 'Project'],
            [item.item for item in command._suggest_directory('')])

    def test_remove_suggestions_exclude_virtual_home(self):
        self._write_favorites('Project|' + self.temp_dir.name + '\n')
        command = self.favorites.RemoveFavoriteDirectory()

        self.assertEqual(
            ['Project'],
            [item.item for item in command._suggest_favorite('')])

    def test_remove_preserves_raw_lines_while_using_shared_name_parser(self):
        contents = 'Keep|/keep\nmalformed line\nRemove|/remove\n'
        self._write_favorites(contents)
        command = self.favorites.RemoveFavoriteDirectory()
        self.fman.show_quicksearch.return_value = ('', 'Remove')

        command()

        with open(self.favorites.paths.FAVORITELIST, 'r') as file:
            self.assertEqual('Keep|/keep\nmalformed line\n', file.read())

    def test_set_replaces_name_and_preserves_unparsed_raw_lines(self):
        self._write_favorites('Keep|/old\nmalformed line\nOther|/other\n')
        command = self.favorites.SetFavoriteDirectory()
        command.pane = Mock(spec=_Pane)
        command.pane.get_path.return_value = os.path.join(
            self.temp_dir.name, 'new')
        self.fman.show_prompt.return_value = ('Keep', True)

        command()

        with open(self.favorites.paths.FAVORITELIST, 'r') as file:
            contents = file.read()
        self.assertIn('malformed line\n', contents)
        self.assertIn('Other|/other\n', contents)
        self.assertEqual(1, sum(line.startswith('Keep|')
                                for line in contents.splitlines()))

    def test_open_favorite_preserves_navigation_and_unknown_name_behavior(self):
        destination = os.path.join(self.temp_dir.name, 'destination')
        self._write_favorites('Project|' + destination + '\n')
        pane = Mock(spec=_Pane)

        self.favorite_commands.open_favorite(pane, 'Project')
        self.favorite_commands.open_favorite(pane, 'Unknown')

        pane.set_path.assert_called_once_with(destination)

