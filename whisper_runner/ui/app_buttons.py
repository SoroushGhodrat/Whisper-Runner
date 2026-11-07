"""App buttons at the top right of the window: the interface-language dropdown, then About."""

import tkinter as tk

from .. import i18n
from ..i18n import UI_LANGS, tr
from ..theme import PANEL, px
from ..widgets import Button, PopupMenu, flag_image


class AppButtons(tk.Frame):
    def __init__(self, parent, on_about, on_language):
        super().__init__(parent, bg=PANEL)
        self.on_language = on_language
        own_name = next(name for code, name, _ in UI_LANGS if code == i18n.UI_LANG)
        self.lang_btn = Button(self, f"{own_name} ▾", self._pick_language, style="ghost", height=28,
                               padx=12, image=flag_image(i18n.UI_LANG, px(20), px(14)))
        self.lang_btn.grid(row=0, column=0, padx=(0, px(8)))
        Button(self, tr("About"), on_about, style="ghost", height=28, padx=12).grid(row=0, column=1)

    def _pick_language(self):
        if PopupMenu.just_closed():  # this click closed the open list
            return
        # Each language in its own name, with its name in the current language as a hint.
        items = [(code, name, tr(english) if tr(english) != name else "", code)
                 for code, name, english in UI_LANGS]
        PopupMenu(self.lang_btn, items, i18n.UI_LANG, self.on_language, align="right",
                  min_width=max(px(190), self.lang_btn.winfo_width()))
