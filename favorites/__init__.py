"""Expose commands and listeners that fman registers from this package."""

try:
    from .favorite_commands import (
        GoToFavorite,
        RemoveFavoriteDirectory,
        SetFavoriteDirectory,
    )
    from .ftp_support import ToggleFtpInFavorites
    from .favorites_panel import OpenFavoritesPanelEntry, ShowFavoritesPanel
    from .hot_dirs import (
        ClearHotdirs,
        GoToHotDir,
        ListAllHotdirs,
        SetHotDir,
    )
    from .pair_commands import (
        GoToFavoritePair,
        RemoveFavoriteDirectoryPairs,
        SetFavoriteDirectoryPairs,
    )
    from .pop_dir import PopDir, PopdirectoryListener
    from .shortener_commands import RemoveShortenerDirectory, SetShortenDirectory
except ModuleNotFoundError as error:
    if error.name != "core":
        raise
    # fman's core runtime is only available inside fman; unittest discovery
    # imports this package while looking for tests outside that runtime.
    __all__ = []
else:
    __all__ = [
        "GoToFavoritePair",
        "ToggleFtpInFavorites",
        "GoToFavorite",
        "RemoveFavoriteDirectoryPairs",
        "RemoveFavoriteDirectory",
        "RemoveShortenerDirectory",
        "SetFavoriteDirectoryPairs",
        "SetFavoriteDirectory",
        "SetShortenDirectory",
        "SetHotDir",
        "GoToHotDir",
        "PopdirectoryListener",
        "PopDir",
        "ListAllHotdirs",
        "ClearHotdirs",
        "ShowFavoritesPanel",
        "OpenFavoritesPanelEntry",
    ]
