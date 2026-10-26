"""FTP detection and the command that controls FTP favorites visibility."""

import fman
from fman import DirectoryPaneCommand, show_alert


class ToggleFtpInFavorites(DirectoryPaneCommand):
    def is_visible(self):
        return _ftp() is not None

    def __call__(self):
        enabled = not _show_ftp()
        _set_show_ftp(enabled)
        state = 'on' if enabled else 'off'
        show_alert('FTP in Favorites is ' + state + '.')


def _ftp():
    try:
        from ftpclient import commands, ftp
        return commands, ftp
    except ImportError:
        return None


def _show_ftp():
    settings = fman.load_json('Favorites Settings.json', default={})
    return settings.get('show_ftp', False)


def _set_show_ftp(enabled):
    settings = fman.load_json(
        'Favorites Settings.json', default={}, save_on_quit=True)
    settings['show_ftp'] = enabled
    fman.save_json('Favorites Settings.json')
