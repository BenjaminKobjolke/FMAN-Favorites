"""Track recently visited locations and provide the Pop Dir command."""

from fman import DirectoryPaneCommand, DirectoryPaneListener
from fman.url import as_human_readable, as_url


POPDIR = ['', '', '', '', '', '', '', '', '', '']
LASTPOP = -1
POPPING = False


def recent_dirs() -> list[str]:
    """Return recorded locations newest first, without empty or duplicate paths."""
    recent = []
    seen = set()
    for offset in range(len(POPDIR)):
        directory = POPDIR[(LASTPOP - offset) % len(POPDIR)]
        if directory and directory not in seen:
            seen.add(directory)
            recent.append(directory)
    return recent


class PopdirectoryListener(DirectoryPaneListener):
    def on_path_changed(self):
        global LASTPOP, POPDIR, POPPING

        if not POPPING:
            LASTPOP = (LASTPOP + 1) % 10
            POPDIR[LASTPOP] = as_human_readable(self.pane.get_path())

        POPPING = False
        # Delay this import because the panel reads history from this module.
        from .favorites_panel import refresh_open_panels
        refresh_open_panels(self.pane.window)


class PopDir(DirectoryPaneCommand):
    def __call__(self, dirNum=0):
        global LASTPOP, POPDIR, POPPING
        LASTPOP = abs(LASTPOP - 1 - dirNum)
        POPPING = True
        self.pane.set_path(as_url(POPDIR[LASTPOP]))
