"""Commands for favorite directory pairs."""

import os
from typing import Any

from core.quicksearch_matchers import contains_chars
from fman import (
    DirectoryPaneCommand, QuicksearchItem, clear_status_message,
    show_prompt, show_quicksearch, show_status_message,
)
from fman.url import as_url
from .paths import FAVORITEPAIRS, expandDirPath, shortenDirPath


#
# Function:    GoToFavoritePair
#
# Description: This class performs the operation of going
#              to a favorite directory pair that the user
#              selects.
#


def favorite_pair_names() -> list[str]:
    """Return the favorite pair names displayed by GoToFavoritePair."""
    directories = ["Home|~|~"]
    if os.path.isfile(FAVORITEPAIRS):
        with open(FAVORITEPAIRS, "r") as f:
            directories = directories + f.readlines()
    return [directory.split('|')[0] for directory in directories
            if '|' in directory]


def open_favorite_pair(window: Any, dir_name: str) -> None:
    """Navigate the first two panes to the named favorite pair."""
    directories = ["Home|~|~"]
    if os.path.isfile(FAVORITEPAIRS):
        with open(FAVORITEPAIRS, "r") as f:
            directories = directories + f.readlines()
    panes = window.get_panes()
    for dir_tuple in directories:
        if '|' in dir_tuple:
            fav_name, fav_path1, fav_path2 = dir_tuple.strip().split('|')[0:3]
            if fav_name == dir_name:
                if '://' in fav_path1:
                    new_path = expandDirPath(fav_path1)
                    panes[0].set_path(new_path)
                else:
                    new_path = as_url(expandDirPath(fav_path1))
                    panes[0].set_path(new_path)
                if '://' in fav_path2:
                    new_path = expandDirPath(fav_path2)
                    panes[1].set_path(new_path)
                else:
                    new_path = as_url(expandDirPath(fav_path2))
                    panes[1].set_path(new_path)
                break


class GoToFavoritePair(DirectoryPaneCommand):
    #
    # This directory command is for selecting a project
    # and going to that directory.
    #

    def __call__(self):
        show_status_message('Favorite Pair Selection')
        result = show_quicksearch(self._suggest_directory)
        if result:
            _, dir_name = result
            open_favorite_pair(self.pane.window, dir_name)
        clear_status_message()

    def _suggest_directory(self, query):
        for name in favorite_pair_names():
            match = contains_chars(name.lower(), query.lower())
            if match or not query:
                yield QuicksearchItem(name, highlight=match)


#
# Function:    RemoveFavoriteDirectoryPairs
#
# Description: This class performs the function of
#              removing a favorite directory.
#


class RemoveFavoriteDirectoryPairs(DirectoryPaneCommand):
    #
    # This directory command is for selecting a favorite pair
    # and deleting it.
    #

    def __call__(self):
        show_status_message('Remove Favorite Directory Pair')
        result = show_quicksearch(self._suggest_favorite)
        if result:
            query, dirName = result
            if os.path.isfile(FAVORITEPAIRS):
                with open(FAVORITEPAIRS, "r") as f:
                    directories = f.readlines()
                with open(FAVORITEPAIRS, "w") as f:
                    for dirTuple in directories:
                        favName = dirTuple.split('|')[0]
                        if favName != dirName:
                            f.write(dirTuple)
        clear_status_message()

    def _suggest_favorite(self, query):
        favorites = [""]
        if os.path.isfile(FAVORITEPAIRS):
            with open(FAVORITEPAIRS, "r") as f:
                favorites = f.readlines()
        for favTuple in favorites:
            if '|' in favTuple:
                favName = favTuple.split('|')[0]
                match = contains_chars(favName.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(favName, highlight=match)


#
# Function:    SetFavoriteDirectoryPairs
#
# Description: This class performs the command to set
#              a favorite directory pair. If the directory
#              path contains a directory specified as a
#              shortener, then the path is shortened to that
#              shortener. Otherwise, it will shorten the path
#              to the home directory.
#


class SetFavoriteDirectoryPairs(DirectoryPaneCommand):
    #
    # This dirctory command is for setting up a new project
    # directory. It will add to the list of project directories
    # and set the current project directory to the directory.
    #

    def __call__(self):
        #
        # Get a name from the user.
        #
        favName, checked = show_prompt("Name this Favorite:")

        #
        # Find and remove the name from favorites.
        #
        if os.path.isfile(FAVORITEPAIRS):
            with open(FAVORITEPAIRS, "r") as f:
                directories = f.readlines()
            with open(FAVORITEPAIRS, "w") as f:
                for dirTuple in directories:
                    oldDirName = dirTuple.split('|')[0]
                    if favName != oldDirName:
                        f.write(dirTuple)

        #
        # Add name to favorites.
        #
        panes = self.pane.window.get_panes()
        dirName1 = shortenDirPath(panes[0].get_path())
        dirName2 = shortenDirPath(panes[1].get_path())
        favEntry = favName + "|" + dirName1 + "|" + dirName2
        writeappend = 'w'
        if os.path.isfile(FAVORITEPAIRS):
            writeappend = 'a'
        with open(FAVORITEPAIRS, writeappend) as f:
            f.write(favEntry + "\n")
