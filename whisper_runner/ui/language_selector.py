"""Language selector: the language Whisper transcribes in. Tabs for the common ones, and a More list
for the rest; the More tab then shows the chosen language."""

import tkinter as tk

from ..config import LANGS, MORE_LANGS
from ..i18n import tr
from ..theme import MUTED, PANEL, px
from ..widgets import PopupMenu, Tabs, label

MORE = len(LANGS) - 1  # index of the More tab


class LanguageSelector(tk.Frame):
    def __init__(self, parent, on_change, allowed):
        """`on_change(code)` gets the language code (None for Auto); changes are ignored while
        `allowed()` is false."""
        super().__init__(parent, bg=PANEL)
        self.on_change, self.allowed = on_change, allowed
        self.code = None
        self.grid_columnconfigure(0, weight=1)
        head = tk.Frame(self, bg=PANEL)
        head.grid(row=0, column=0, sticky="ew", pady=(0, px(8)))
        head.grid_columnconfigure(0, weight=1)
        label(head, tr("Language"), "h").grid(row=0, column=0, sticky="w")
        label(head, tr("Auto detects from the first 30 seconds"), "small", MUTED).grid(row=0, column=1, sticky="e")
        self.tabs = Tabs(self, [(tr(name), code) for name, code in LANGS], self._on_tab)
        self.tabs.grid(row=1, column=0, sticky="ew")

    def _on_tab(self, i, code):
        if not self.allowed():
            return False
        if i != MORE:
            self.tabs.set_option(MORE, tr(LANGS[MORE][0]), None)
            self.code = code
            self.on_change(code)
            return None
        if PopupMenu.just_closed():  # this click closed the open list
            return False
        items = sorted(((c, tr(n), "") for n, c in MORE_LANGS), key=lambda x: x[1])
        width = self.tabs.winfo_width() - self.tabs.segment_x(MORE)
        PopupMenu(self.tabs, items, self.code, self._pick_more, align="right", min_width=max(px(200), width))
        return False

    def _pick_more(self, code):
        self._show_more(code)
        self.code = code
        self.on_change(code)

    def _show_more(self, code):
        name = next((n for n, c in MORE_LANGS if c == code), code)
        self.tabs.set_option(MORE, f"{tr(name)} ▾", code)
        self.tabs.select(MORE)

    def set_enabled(self, on):
        self.tabs.set_enabled(on)

    def state(self):
        return self.tabs.sel, self.code

    def restore(self, state):
        sel, self.code = state
        self.tabs.select(sel)
        if sel == MORE and self.code:
            self._show_more(self.code)
