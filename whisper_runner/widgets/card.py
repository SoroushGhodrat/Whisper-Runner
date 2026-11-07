"""Card: a rounded panel with a frame on top for content."""

import tkinter as tk

from ..theme import px, round_rect


class Card(tk.Canvas):
    """Rounded rectangle with a frame (`inner`) on top for content."""

    def __init__(self, parent, fill, radius=14, pad=16, **kw):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0,
                         width=px(40), height=px(40), **kw)
        self.fill, self.r, self.outline = fill, px(radius), None
        self.inner = tk.Frame(self, bg=fill)
        self.inner.grid(row=0, column=0, sticky="nsew", padx=px(pad), pady=px(pad))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.bind("<Configure>", self._draw)

    def _draw(self, _e=None):
        self.delete("bg")
        w, h = self.winfo_width(), self.winfo_height()
        if self.outline:
            inset = px(1)
            round_rect(self, inset, inset, w - 1 - inset, h - 1 - inset, self.r, fill=self.fill,
                       outline=self.outline, width=px(2), tags="bg")
        else:
            round_rect(self, 0, 0, w - 1, h - 1, self.r, fill=self.fill, outline=self.fill, tags="bg")
        self.tag_lower("bg")

    def set_outline(self, color):
        """Highlight the card with a colored border, or remove it with None."""
        self.outline = color
        self._draw()
