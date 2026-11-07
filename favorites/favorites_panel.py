"""Commands and mounted widget for browsing favorites and directory history."""

from typing import Any, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QListWidget, QListWidgetItem

from fman import DirectoryPaneCommand
from fman.impl.util.qt.thread import run_in_main_thread
from fman.url import as_url

from .favorite_commands import open_favorite
from .pair_commands import open_favorite_pair
from .panel_entries import EntryKind, PanelEntry, build_panel_sections


class FavoritesPanelView(QListWidget):
    """Display favorites and recent locations inside a mounted fman pane."""

    def __init__(
        self, source_pane: Any, panel_pane: Any, colors: tuple[str, str]
    ) -> None:
        super().__init__()
        self._source_pane = source_pane
        self._panel_pane = panel_pane
        self.setStyleSheet(
            'QListWidget { background-color: %s; color: %s; }' % colors)
        self.itemActivated.connect(self._activate)
        self.refresh()

    def refresh(self) -> None:
        """Rebuild the list while keeping the current entry selected if possible."""
        current = self.currentItem()
        current_entry = current.data(Qt.UserRole) if current else None
        current_key = ((current_entry.kind, current_entry.value)
                       if current_entry else None)
        self.clear()
        first_entry_item = None
        preserved_item = None
        for section in build_panel_sections():
            header = QListWidgetItem(section.title)
            font = QFont(header.font())
            font.setBold(True)
            header.setFont(font)
            header.setFlags(header.flags() & ~Qt.ItemIsSelectable)
            self.addItem(header)
            for entry in section.entries:
                item = QListWidgetItem(entry.label)
                item.setData(Qt.UserRole, entry)
                self.addItem(item)
                if first_entry_item is None:
                    first_entry_item = item
                if current_key == (entry.kind, entry.value):
                    preserved_item = item
        if preserved_item is not None:
            self.setCurrentItem(preserved_item)
        elif first_entry_item is not None:
            self.setCurrentItem(first_entry_item)

    def keyPressEvent(self, event: Any) -> None:
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self._activate()
        elif event.key() in (Qt.Key_Escape, Qt.Key_Backspace):
            self._panel_pane.run_command('remove_pane')
        elif event.key() in (Qt.Key_Tab, Qt.Key_Backtab):
            self._panel_pane.run_command('switch_panes')
        else:
            super().keyPressEvent(event)

    def focusInEvent(self, event: Any) -> None:
        self.refresh()
        super().focusInEvent(event)

    def _activate(self, item: Optional[QListWidgetItem] = None) -> None:
        item = item or self.currentItem()
        entry = item.data(Qt.UserRole) if item else None
        if not isinstance(entry, PanelEntry):
            return
        panes = self._panel_pane.window.get_panes()
        if self._source_pane in panes:
            target = self._source_pane
        else:
            target = next((pane for pane in panes
                           if pane is not self._panel_pane), None)
        if target is not None:
            target.run_command(
                'open_favorites_panel_entry',
                {'kind': entry.kind.value, 'value': entry.value})


@run_in_main_thread
def refresh_open_panels(window: Any) -> None:
    """Refresh the mounted favorites view in every pane of a window."""
    for pane in window.get_panes():
        widget = pane.get_mounted_widget()
        if isinstance(widget, FavoritesPanelView):
            widget.refresh()


@run_in_main_thread
def _focus_panel(panel_pane: Any) -> None:
    panel_pane.get_mounted_widget().refresh()
    panel_pane.focus()


@run_in_main_thread
def _mount_panel(source_pane: Any, panel_pane: Any) -> None:
    view = FavoritesPanelView(
        source_pane, panel_pane, panel_pane.get_colors())
    panel_pane.mount_widget(view, focus=True)


class ShowFavoritesPanel(DirectoryPaneCommand):
    """Open or focus the favorites and history view in an extra pane."""

    def __call__(self) -> None:
        window = self.pane.window
        for pane in window.get_panes():
            if isinstance(pane.get_mounted_widget(), FavoritesPanelView):
                _focus_panel(pane)
                return
        panel_pane = window.add_pane()
        _mount_panel(self.pane, panel_pane)


class OpenFavoritesPanelEntry(DirectoryPaneCommand):
    """Open one panel entry from the pane command dispatched by its widget."""

    def is_visible(self) -> bool:
        return False

    def __call__(self, kind: str, value: str) -> None:
        entry_kind = EntryKind(kind)
        if entry_kind is EntryKind.FAVORITE:
            open_favorite(self.pane, value)
        elif entry_kind is EntryKind.PAIR:
            open_favorite_pair(self.pane.window, value)
        else:
            self.pane.set_path(as_url(value))
        self.pane.focus()
