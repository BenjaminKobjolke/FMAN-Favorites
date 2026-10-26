"""Path constants and helpers shared by favorite commands."""

import os
import re


# These files also feed an Alfred workflow that reads the same favorites.
HOMEDIR = os.path.expanduser("~")
FAVORITELIST = HOMEDIR + "/.favoritedirs"
SHORTENERLIST = HOMEDIR + "/.shortenerdirs"
FAVORITEPAIRS = HOMEDIR + "/.favoritepairs"
HOTDIRLIST = HOMEDIR + "/.hotdirs"


def expandDirPath(dir):
    dirName = dir
    pattern = re.compile(r"\{\{(.*)\}\}")
    match = pattern.search(dir)
    if match:
        if os.path.isfile(SHORTENERLIST):
            with open(SHORTENERLIST, "r") as f:
                shorteners = f.readlines()
                for shortener in shorteners:
                    if '|' not in shortener:
                        continue
                    shortName, shortPath = shortener.strip().split('|')
                    if match.group(1) == shortName:
                        dirName = shortPath + dir[match.end(1) + 2:]
    return os.path.expanduser(dirName)


def shortenDirPath(dir):
    dirName = dir
    if os.path.isfile(SHORTENERLIST):
        with open(SHORTENERLIST, "r") as f:
            shorteners = f.readlines()
            for shortener in shorteners:
                if '|' not in shortener:
                    continue
                pathName, path = shortener.strip().split('|')
                if path_is_parent(path, dirName):
                    dirName = "{{" + pathName + "}}/" + \
                        os.path.relpath(dirName, path)
    if path_is_parent(os.path.expanduser("~"), dirName):
        dirName = '~/' + os.path.relpath(dirName, os.path.expanduser("~"))
    return dirName


def path_is_parent(parent_path, child_path):
    # Smooth out relative path names. Use realpath too if symbolic links matter.
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    [parent_drive, _] = os.path.splitdrive(parent_path)
    [child_drive, _] = os.path.splitdrive(child_path)
    if parent_drive != child_drive:
        return False

    return (
        os.path.commonpath([parent_path])
        == os.path.commonpath([parent_path, child_path])
    )
