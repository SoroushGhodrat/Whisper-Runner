"""Tabs: a segmented control."""

import tkinter as tk

from ..theme import ACCENT, CARD, FONT, MUTED, TEXT, mix, px, round_rect


class Tabs(tk.Canvas):
    """Segmented control. `command(index, value)` returning False keeps the old selection."""

    def __init__(self, parent, options, command=None, height=34, track=CARD):
        super().__init__(parent, width=px(200), height=px(height), bg=parent["bg"],
                         highlightthickness=0, bd=0, cursor="hand2")
        self.options, self.command, self.track = list(options), command, track
        self.sel, self.hover, self.enabled = 0, -1, True
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", lambda e: self._set_hover(-1))
        self.bind("<Button-1>", self._click)

    @property
    def value(self):
        return self.options[self.sel][1]

    def _index(self, x):
        n = len(self.options)
        return max(0, min(n - 1, int(x / max(1, self.winfo_width()) * n)))

    def _set_hover(self, i):
        if i != self.hover:
            self.hover = i
            self.draw()

    def _motion(self, e):
        self._set_hover(self._index(e.x))

    def _click(self, e):
        if not self.enabled:
            return
        i = self._index(e.x)
        if self.command and self.command(i, self.options[i][1]) is False:
            return
        self.select(i)

    def segment_x(self, i):
        return int(self.winfo_width() / len(self.options) * i)

    def select(self, i):
        self.sel = i
        self.draw()

    def set_value(self, v):
        for i, (_, val) in enumerate(self.options):
            if val == v:
                self.select(i)
                return

    def set_option(self, i, label, value):
        self.options[i] = (label, value)
        self.draw()

    def set_enabled(self, on):
        self.enabled = on
        self.config(cursor="hand2" if on else "arrow")
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10:
            return
        pad = px(3)
        round_rect(self, 0, 0, w - 1, h - 1, px(10), fill=self.track, outline=self.track)
        sw = (w - 2 * pad) / len(self.options)
        for i, (label, _) in enumerate(self.options):
            x1 = pad + i * sw
            x2 = x1 + sw
            if i == self.sel:
                fill = ACCENT if self.enabled else mix(ACCENT, self.track, 0.55)
                round_rect(self, x1, pad, x2, h - pad - 1, px(8), fill=fill, outline=fill)
                tc = "#FFFFFF" if self.enabled else mix("#FFFFFF", self.track, 0.4)
            else:
                tc = TEXT if (i == self.hover and self.enabled) else MUTED
            self.create_text((x1 + x2) / 2, h / 2, text=label, fill=tc, font=FONT["tab"])
