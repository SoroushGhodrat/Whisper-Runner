"""File picker: the chosen recording's name and details, and the Choose file button. Clicking anywhere
on the card also chooses a file."""

import tkinter as tk

from .. import dnd
from ..i18n import tr
from ..theme import ACCENT, CARD, FONT, MUTED, PURPLE, mix, px, round_rect
from ..widgets import Button, Card, label, label_state, say, set_label_state


class FilePicker(Card):
    def __init__(self, parent, on_choose):
        super().__init__(parent, CARD, radius=14, pad=14)
        self.drag_saved = None
        fc = self.inner
        fc.grid_columnconfigure(1, weight=1)
        icon = tk.Canvas(fc, width=px(44), height=px(44), bg=CARD, highlightthickness=0, bd=0)
        icon.grid(row=0, column=0, rowspan=2, padx=(0, px(12)))
        fill = mix(PURPLE, CARD, 0.7)
        round_rect(icon, 0, 0, px(43), px(43), px(10), fill=fill, outline=fill)
        icon.create_text(px(22), px(22), text="♪", fill=PURPLE, font=(FONT["title"][0], -px(21)))
        self.name = label(fc, "", "h", anchor="w")
        say(self.name, "No file selected")
        self.name.grid(row=0, column=1, sticky="ew")
        self.info = label(fc, "", "small", MUTED, anchor="w")
        say(self.info, "Choose a recording file, or drop one here." if dnd.available else "Choose a recording file.")
        self.info.grid(row=1, column=1, sticky="ew")
        self.button = Button(fc, tr("Choose file"), on_choose, style="outline", height=34)
        self.button.grid(row=0, column=2, rowspan=2, padx=(px(12), 0))
        for w in (self, fc, icon, self.name, self.info):
            w.bind("<Button-1>", lambda e: on_choose())

    def set_name(self, text, **fields):
        say(self.name, text, **fields)

    def set_info(self, text, fg=None, **fields):
        say(self.info, text, fg, **fields)

    def set_enabled(self, on):
        self.button.set_enabled(on)

    def drag_over(self, on):
        """Show (or stop showing) that a file dragged over the window will open when dropped."""
        if on:
            if not self.drag_saved:
                self.drag_saved = self.state()
            self.set_outline(ACCENT)
            self.set_name("Drop to open this file")
            self.set_info("Release the mouse button to choose it.", MUTED)
        else:
            self.set_outline(None)
            if self.drag_saved:
                self.restore(self.drag_saved)
                self.drag_saved = None

    def state(self):
        return label_state(self.name), label_state(self.info)

    def restore(self, state):
        set_label_state(self.name, state[0])
        set_label_state(self.info, state[1])
