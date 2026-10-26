"""Track recently visited locations and provide the Pop Dir command."""

from fman import DirectoryPaneCommand, DirectoryPaneListener
from fman.url import as_human_readable, as_url


POPDIR = ['', '', '', '', '', '', '', '', '', '']
LASTPOP = -1
POPPING = False


class PopdirectoryListener(DirectoryPaneListener):
    def on_path_changed(self):
        global LASTPOP, POPDIR, POPPING

        if not POPPING:
            LASTPOP = (LASTPOP + 1) % 10
            POPDIR[LASTPOP] = as_human_readable(self.pane.get_path())

        POPPING = False


class PopDir(DirectoryPaneCommand):
    def __call__(self, dirNum=0):
        global LASTPOP, POPDIR, POPPING
        LASTPOP = abs(LASTPOP - 1 - dirNum)
        POPPING = True
        self.pane.set_path(as_url(POPDIR[LASTPOP]))
