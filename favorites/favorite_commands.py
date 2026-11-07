"""Commands for opening and managing favorite directories."""

import os
from typing import Any
from urllib.parse import urlparse

import fman
from core.quicksearch_matchers import contains_chars
from fman import (
    DirectoryPaneCommand, QuicksearchItem,
    clear_status_message, show_quicksearch, show_status_message, show_prompt,
)
from fman.url import as_human_readable, as_url
from .ftp_support import _ftp, _show_ftp
from .paths import FAVORITELIST, expandDirPath, shortenDirPath


#
# Function:    GoToFavaorite
#
# Description: This class performs the operation of going
#              to a favorite directory that the user
#              selects.
#


def favorite_items() -> list[str]:
    """Return the favorite names displayed by GoToFavorite."""
    directories = ["Home|~"]
    if os.path.isfile(FAVORITELIST):
        with open(FAVORITELIST, "r") as f:
            directories = directories + f.readlines()

    items = [directory.split('|')[0] for directory in directories if '|' in directory]
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
    directories = ["Home|~"]
    if os.path.isfile(FAVORITELIST):
        with open(FAVORITELIST, "r") as f:
            directories = directories + f.readlines()
    for dir_tuple in directories:
        if '|' in dir_tuple:
            fav_name, fav_path = dir_tuple.strip().split('|')[0:2]
            if fav_name == dir_name:
                if '://' in fav_path:
                    new_path = expandDirPath(fav_path)
                    pane.set_path(new_path)
                else:
                    new_path = as_url(expandDirPath(fav_path))
                    pane.set_path(new_path)
                break
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
            match = contains_chars(item.lower(), query.lower())
            if match or not query:
                yield QuicksearchItem(item, highlight=match)


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
                with open(FAVORITELIST, "r") as f:
                    directories = f.readlines()
                with open(FAVORITELIST, "w") as f:
                    for dirTuple in directories:
                        favName = dirTuple.split('|')[0]
                        if favName != dirName:
                            f.write(dirTuple)
        clear_status_message()

    def _suggest_favorite(self, query):
        favorites = [""]
        if os.path.isfile(FAVORITELIST):
            with open(FAVORITELIST, "r") as f:
                favorites = f.readlines()
        for favTuple in favorites:
            if '|' in favTuple:
                favName = favTuple.split('|')[0]
                match = contains_chars(favName.lower(), query.lower())
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
            with open(FAVORITELIST, "w") as f:
                for dirTuple in directories:
                    oldDirName = dirTuple.split('|')[0]
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
