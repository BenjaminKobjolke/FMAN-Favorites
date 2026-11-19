"""Commands for opening and managing favorite directories."""

import os
from typing import Any
from urllib.parse import urlparse

import fman
from fman import (
    DirectoryPaneCommand, QuicksearchItem,
    clear_status_message, show_quicksearch, show_status_message, show_prompt,
)
from fman.url import as_human_readable, as_url
from .ftp_support import _ftp, _show_ftp
from .matching import match_query
from .paths import FAVORITELIST, expandDirPath, shortenDirPath


#
# Function:    GoToFavaorite
#
# Description: This class performs the operation of going
#              to a favorite directory that the user
#              selects.
#


def _local_favorite_entries() -> list[tuple[str, str]]:
    """Return local favorite names and paths, including the Home entry."""
    directories = ["Home|~"]
    if os.path.isfile(FAVORITELIST):
        with open(FAVORITELIST, "r") as f:
            directories = directories + f.readlines()

    return [tuple(directory.strip().split('|')[0:2])
            for directory in directories if '|' in directory]


def favorite_url(dir_name: str) -> str | None:
    """Return the URL for a local favorite, or None when it is unknown."""
    for favorite_name, favorite_path in _local_favorite_entries():
        if favorite_name == dir_name:
            expanded_path = expandDirPath(favorite_path)
            if '://' in favorite_path:
                return expanded_path
            return as_url(expanded_path)
    return None


def local_favorite_names() -> list[str]:
    """Return names of local favorites without FTP entries."""
    return [name for name, _ in _local_favorite_entries()]


def favorite_items() -> list[str]:
    """Return the favorite names displayed by GoToFavorite."""
    items = local_favorite_names()
    ftp = _ftp()
    if _show_ftp() and ftp:
        _, ftp_module = ftp
        bookmarks = fman.load_json('FTP Bookmarks.json', default={})
        items.extend('FTP: ' + alias for alias in bookmarks)
        items.extend(
            'FTP open: ' + base_url
            for base_url, _ in ftp_module.FtpWrapper.get_open_connections())
    return items


def open_favorite(pane: Any, dir_name: str) -> None:
    """Navigate a pane to the favorite selected by name."""
    ftp = _ftp()
    if dir_name.startswith('FTP: ') and ftp:
        commands, _ = ftp
        alias = dir_name[len('FTP: '):]
        bookmarks = fman.load_json('FTP Bookmarks.json', default={})
        url = urlparse(alias)._replace(
            path=bookmarks[alias][1]).geturl()
        commands._goto_ftp(pane, url)
        clear_status_message()
        return
    if dir_name.startswith('FTP open: ') and ftp:
        _, ftp_module = ftp
        base_url = dir_name[len('FTP open: '):]
        for open_base_url, last_url in \
                ftp_module.FtpWrapper.get_open_connections():
            if open_base_url == base_url:
                pane.set_path(last_url)
                break
        else:
            pane.set_path(base_url + '/')
        clear_status_message()
        return
    url = favorite_url(dir_name)
    if url is not None:
        pane.set_path(url)
    clear_status_message()


class GoToFavorite(DirectoryPaneCommand):
    #
    # This directory command is for selecting a project
    # and going to that directory.
    #

    def __call__(self):
        show_status_message('Favorite Selection')
        result = show_quicksearch(self._suggest_directory)
        if result:
            _, dir_name = result
            open_favorite(self.pane, dir_name)
        else:
            clear_status_message()

    def _suggest_directory(self, query):
        for item in favorite_items():
            match = match_query(item, query)
            if match or not query:
                yield QuicksearchItem(item, highlight=match)


class _TransferToFavorite(DirectoryPaneCommand):
    _command: str

    def __call__(self) -> None:
        show_status_message('Favorite Selection')
        try:
            result = show_quicksearch(self._suggest_directory)
            if result:
                _, dir_name = result
                url = favorite_url(dir_name)
                if url is not None:
                    self.pane.run_command(self._command, {'dest_dir': url})
        finally:
            clear_status_message()

    def _suggest_directory(self, query):
        # shortcut: FTP favorites need a login step before they can be transfer targets.
        for item in local_favorite_names():
            match = match_query(item, query)
            if match or not query:
                yield QuicksearchItem(item, highlight=match)


class CopyToFavorite(_TransferToFavorite):
    _command = 'copy'


class MoveToFavorite(_TransferToFavorite):
    _command = 'move'


#
# Function:    RemoveFavoriteDirectory
#
# Description: This class performs the function of
#              removing a favorite directory.
#


class RemoveFavoriteDirectory(DirectoryPaneCommand):
    #
    # This directory command is for selecting a favorite
    # and deleting it.
    #

    def __call__(self):
        show_status_message('Remove Favorite Directory')
        result = show_quicksearch(self._suggest_favorite)
        if result:
            query, dirName = result
            if os.path.isfile(FAVORITELIST):
                favorite_entries = iter(_local_favorite_entries()[1:])
                with open(FAVORITELIST, "r") as f:
                    directories = f.readlines()
                with open(FAVORITELIST, "w") as f:
                    for dirTuple in directories:
                        if '|' not in dirTuple:
                            f.write(dirTuple)
                            continue
                        favName, _ = next(favorite_entries)
                        if favName != dirName:
                            f.write(dirTuple)
        clear_status_message()

    def _suggest_favorite(self, query):
        for favName, favPath in _local_favorite_entries():
            if (favName, favPath) == ('Home', '~'):
                continue
            match = match_query(favName, query)
            if match or not query:
                yield QuicksearchItem(favName, highlight=match)


#
# Function:    SetFavoriteDirectory
#
# Description: This class performs the command to set
#              a favorite directory. If the directory
#              path contains a directory specified as a
#              shortener, then the path is shortened to that
#              shortener. Otherwise, it will shorten the path
#              to the home directory.
#


class SetFavoriteDirectory(DirectoryPaneCommand):
    #
    # This dirctory command is for setting up a new project
    # directory. It will add to the list of project directories
    # and set the current project directory to the directory.     #

    def __call__(self):
        #
        # Get the directory path.
        #
        dirName = as_human_readable(self.pane.get_path())

        #
        # Add to the list of projects. Get a name
        # from the user.
        #
        dirName = shortenDirPath(dirName)
        favName, checked = show_prompt("Name this Favorite:")

        #
        # Find and remove the name from favorites.
        #
        if os.path.isfile(FAVORITELIST):
            with open(FAVORITELIST, "r") as f:
                directories = f.readlines()
            favorite_entries = iter(_local_favorite_entries()[1:])
            with open(FAVORITELIST, "w") as f:
                for dirTuple in directories:
                    if '|' not in dirTuple:
                        f.write(dirTuple)
                        continue
                    oldDirName, _ = next(favorite_entries)
                    if favName != oldDirName:
                        f.write(dirTuple)

        #
        # Add name to favorites.
        #
        favEntry = favName + "|" + dirName
        writeappend = 'w'
        if os.path.isfile(FAVORITELIST):
            writeappend = 'a'
        with open(FAVORITELIST, writeappend) as f:
            f.write(favEntry + "\n")
