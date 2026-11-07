"""Build the typed, Qt-free sections shown by the favorites panel."""

from dataclasses import dataclass
from enum import Enum

from .favorite_commands import favorite_items
from .pair_commands import favorite_pair_names
from .pop_dir import recent_dirs


class EntryKind(str, Enum):
    FAVORITE = 'favorite'
    PAIR = 'pair'
    HISTORY = 'history'


@dataclass(frozen=True)
class PanelEntry:
    kind: EntryKind
    label: str
    value: str


@dataclass(frozen=True)
class PanelSection:
    title: str
    entries: tuple[PanelEntry, ...]


FAVORITES_SECTION = 'Favorites'
PAIRS_SECTION = 'Favorite pairs'
HISTORY_SECTION = 'History'


def build_panel_sections() -> list[PanelSection]:
    """Return favorite, pair, and recent-directory sections in display order."""
    favorites = tuple(
        PanelEntry(EntryKind.FAVORITE, name, name)
        for name in favorite_items())
    pairs = tuple(
        PanelEntry(EntryKind.PAIR, name, name)
        for name in favorite_pair_names())
    history = tuple(
        PanelEntry(EntryKind.HISTORY, path, path)
        for path in recent_dirs())
    return [
        PanelSection(FAVORITES_SECTION, favorites),
        PanelSection(PAIRS_SECTION, pairs),
        PanelSection(HISTORY_SECTION, history),
    ]
