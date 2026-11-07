"""Progress view: the big percentage, a status line with details under it, and the progress bar."""

import tkinter as tk

from ..theme import MUTED, PANEL, px
from ..widgets import Progress, label, label_state, say, set_label_state


class ProgressView(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=PANEL)
        self.grid_columnconfigure(0, weight=1)
        row = tk.Frame(self, bg=PANEL)
        row.grid(row=0, column=0, sticky="ew", pady=(0, px(6)))
        row.grid_columnconfigure(1, weight=1)
        self.percent = label(row, "0%", "big")
        self.percent.grid(row=0, column=0, rowspan=2, sticky="w")
        self.status = label(row, "", "h", anchor="w")
        say(self.status, "Ready")
        self.status.grid(row=0, column=1, sticky="sew", padx=(px(16), 0))
        self.detail = label(row, "", "small", MUTED, anchor="w")
        say(self.detail, "Pick a file to start")
        self.detail.grid(row=1, column=1, sticky="new", padx=(px(16), 0))
        self.bar = Progress(self)
        self.bar.grid(row=1, column=0, sticky="ew")

    def set_percent(self, text):
        self.percent.config(text=text)

    def set_fraction(self, p, color):
        """Show progress p (0..1) as the percentage and on the bar."""
        self.set_percent(f"{int(p * 100)}%")
        self.bar.set(p, color)

    def set_status(self, text, fg=None, **fields):
        say(self.status, text, fg, **fields)

    def set_detail(self, text, fg=None, **fields):
        say(self.detail, text, fg, **fields)

    def state(self):
        return [label_state(w) for w in (self.percent, self.status, self.detail)], (self.bar.value, self.bar.color)

    def restore(self, state, moving):
        """`moving`: keep the bar animating (a run or download is going on)."""
        labels, bar = state
        for w, s in zip((self.percent, self.status, self.detail), labels):
            set_label_state(w, s)
        self.bar.set(*bar)
        if moving:
            self.bar.start()
