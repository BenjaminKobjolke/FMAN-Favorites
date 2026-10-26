"""Hot-directory storage and commands."""

import os

from fman import DirectoryPaneCommand, show_alert
from fman.url import as_human_readable, as_url

from .paths import HOTDIRLIST, expandDirPath


# These locations are used for quick jumps with hotkeys.
HOTLIST = ["~", "~", "~", "~"]


def loadHotDirs():
    global HOTLIST
    if os.path.isfile(HOTDIRLIST):
        try:
            with open(HOTDIRLIST, "r") as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:4]):  # Only load first 4 lines
                    HOTLIST[i] = line.strip()
        except (OSError, ValueError):
            # If there's any error reading the file, use defaults.
            HOTLIST = ["~", "~", "~", "~"]


def saveHotDirs():
    try:
        with open(HOTDIRLIST, "w") as f:
            for hotdir in HOTLIST:
                f.write(hotdir + "\n")
    except (OSError, ValueError):
        # Silently ignore save errors.
        pass


# Load hot directories on module import.
loadHotDirs()


class SetHotDir(DirectoryPaneCommand):
    def __call__(self, dirNum=0):
        show_alert(f"Hot dir stored for index: {int(dirNum)}")

        if dirNum < 0 or dirNum > 4:
            dirNum = 0
        HOTLIST[dirNum] = as_human_readable(self.pane.get_path())

        # Save hot directories to file for persistence.
        saveHotDirs()


class GoToHotDir(DirectoryPaneCommand):
    def __call__(self, dirNum=0):
        if dirNum < 0 or dirNum > 4:
            dirNum = 0
        self.pane.set_path(as_url(expandDirPath(HOTLIST[dirNum])))


class ListAllHotdirs(DirectoryPaneCommand):
    def __call__(self):
        """Display all hot directories in an alert dialog."""
        hotdir_info = []

        for i in range(4):  # HOTLIST has 4 slots (0-3)
            if i < len(HOTLIST):
                path = HOTLIST[i]
                if path and path != "~":
                    # Expand the path to show full directory.
                    expanded_path = expandDirPath(path)
                    hotdir_info.append(f"Hot Dir {i}:\n{expanded_path}")
                else:
                    hotdir_info.append(f"Hot Dir {i}:\nNot set")
            else:
                hotdir_info.append(f"Hot Dir {i}:\nNot set")

        # Join all hotdir information with double newlines for spacing.
        message = "\n\n".join(hotdir_info)
        show_alert("All Hot Directories:\n\n" + message)


class ClearHotdirs(DirectoryPaneCommand):
    def __call__(self):
        """Clear all hot directories and reset to defaults."""
        global HOTLIST

        HOTLIST = ["~", "~", "~", "~"]
        saveHotDirs()
        show_alert("All hot directories have been cleared.")
