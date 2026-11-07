"""Header: the app's name, an "Update available" button when there is a newer release, and the CPU/GPU
badge. (The language and About buttons are at the top of the session panel.)"""

import tkinter as tk

from ..i18n import tr
from ..theme import GREEN, MUTED, PANEL, px
from ..widgets import Badge, Button, label


class Header(tk.Frame):
    def __init__(self, parent, on_update):
        """`on_update`: the "Update available" button was clicked."""
        super().__init__(parent, bg=PANEL)
        self.grid_columnconfigure(0, weight=1)
        label(self, "Whisper Runner", "title").grid(row=0, column=0, sticky="w")
        label(self, tr("Transcribe audio with OpenAI Whisper"), "small", MUTED).grid(row=1, column=0, sticky="w")
        self.update_btn = Button(self, "↑ " + tr("Update available"), on_update, color=GREEN, style="outline",
                                 height=28, padx=12)
        self.update_btn.grid(row=0, column=1, rowspan=2, sticky="e", padx=(0, px(10)))
        self.update_btn.grid_remove()
        self.badge = Badge(self, tr("Checking…"), MUTED)
        self.badge.grid(row=0, column=2, rowspan=2, sticky="e")

    def show_update(self, on):
        """Show or hide the "Update available" button."""
        if on:
            self.update_btn.grid()
        else:
            self.update_btn.grid_remove()

    def set_device(self, text, color):
        """The badge saying whether Whisper runs on the GPU or the CPU."""
        self.badge.set(text, color)
