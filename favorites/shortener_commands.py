"""Commands for adding and removing directory shorteners."""

import os
import re

from core.quicksearch_matchers import contains_chars
from fman import (
    DirectoryPaneCommand, QuicksearchItem,
    clear_status_message, show_quicksearch, show_status_message, show_prompt,
)
from fman.url import as_human_readable
from .paths import FAVORITELIST, SHORTENERLIST


#
# Function:    RemoveShortenerDirectory
#
# Description: This class performs the function of
#              removing a shortener directory.
#


class RemoveShortenerDirectory(DirectoryPaneCommand):
    #
    # This directory command is for selecting a favorite
    # and deleting it.
    #

    def __call__(self):
        show_status_message('Remove Shortener Directory')
        result = show_quicksearch(self._suggest_shortener)
        if result:
            #
            # Remove the shortener from the list of
            # shorteners.
            #
            query, shortName = result
            shortenDir = ''
            if os.path.isfile(SHORTENERLIST):
                with open(SHORTENERLIST, "r") as f:
                    directories = f.readlines()
                with open(SHORTENERLIST, "w") as f:
                    for dirTuple in directories:
                        if '|' in dirTuple:
                            shortenerName, shortDir = dirTuple.strip().split('|')[0:2]
                            if shortenerName != shortName:
                                f.write(dirTuple + '\n')
                            else:
                                shortenDir = shortDir
            #
            # Remove the shortener from all favorites.
            #
            if os.path.isfile(FAVORITELIST):
                favorties = ["Home|~"]
                with open(FAVORITELIST, "r") as f:
                    favorties = f.readlines()
                pattern = re.compile(r"\{\{" + shortName + r"\}\}(.*)$")
                with open(FAVORITELIST, "w") as f:
                    for fav in favorties:
                        if '|' in fav:
                            favName, favPath = fav.strip().split('|')[0:2]
                            match = pattern.search(favPath)
                            if match:
                                favPath = shortenDir + match.group(1)
                            f.write(favName + "|" + favPath + "\n")
        clear_status_message()

    def _suggest_shortener(self, query):
        shorteners = ["No shorteners are setup."]
        if os.path.isfile(SHORTENERLIST):
            with open(SHORTENERLIST, "r") as f:
                shorteners = f.readlines()
        for shortTuple in shorteners:
            if shortTuple.strip() != "":
                shortName = shortTuple.split('|')[0]
                match = contains_chars(shortName.lower(), query.lower())
                if match or not query:
                    yield QuicksearchItem(shortName, highlight=match)


#
# Function:    SetShortenDirectory
#
# Description: This class will set a new shortener directory. It
#              will ask the user for a name for the shortener.
#


class SetShortenDirectory(DirectoryPaneCommand):
    #
    # This dirctory command is for setting up a new project
    # directory. It will add to the list of project directories
    # and set the current project directory to the directory.     #

    def __call__(self):
        #
        # Get the directory path.
        #
        selected_files = self.pane.get_selected_files()
        if len(selected_files) >= 1 or (
                len(selected_files) == 0 and self.get_chosen_files()):
            if len(selected_files) == 0 and self.get_chosen_files():
                selected_files.append(self.get_chosen_files()[0])
            dirName = as_human_readable(selected_files[0])
            if os.path.isfile(dirName):
                #
                # It's a file, not a directory. Get the directory
                # name for this file's parent directory.
                #
                dirName = os.path.dirname(dirName)
            #
            # Add to the list of projects. Get a name
            # from the user.
            #
            shortener, checked = show_prompt("Name this Directory Shortener:")
            shortEntry = shortener + "|" + dirName
            writeappend = 'w'
            if os.path.isfile(SHORTENERLIST):
                writeappend = 'a'
            with open(SHORTENERLIST, writeappend) as f:
                f.write(shortEntry + "\n")
