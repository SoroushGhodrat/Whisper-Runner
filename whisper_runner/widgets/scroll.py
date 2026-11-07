"""Scroll bar and a vertically scrolling area."""

import tkinter as tk

from ..config import IS_MAC
from ..theme import MUTED, mix, px, round_rect


class ScrollBar(tk.Canvas):
    def __init__(self, parent, command):
        super().__init__(parent, width=px(10), height=px(40), bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.command, self.first, self.last, self.drag = command, 0.0, 1.0, None
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._motion)

    def set(self, first, last):
        self.first, self.last = float(first), float(last)
        self.draw()

    def draw(self):
        self.delete("all")
        if self.last - self.first >= 1:
            return
        w, h = self.winfo_width(), self.winfo_height()
        y1 = self.first * h
        y2 = max(self.last * h, y1 + px(24))
        color = mix(MUTED, self["bg"], 0.45)
        round_rect(self, px(2), y1, w - px(2), y2, (w - px(4)) / 2, fill=color, outline=color)

    def _press(self, e):
        h = max(1, self.winfo_height())
        y = e.y / h
        first = self.first
        if not self.first <= y <= self.last:
            first = max(0.0, y - (self.last - self.first) / 2)
            self.command("moveto", first)
        self.drag = (e.y, first)

    def _motion(self, e):
        if self.drag:
            y0, f0 = self.drag
            self.command("moveto", f0 + (e.y - y0) / max(1, self.winfo_height()))


class ScrollArea(tk.Frame):
    """Vertically scrolling frame (`inner`); the scrollbar only shows when the content overflows."""

    def __init__(self, parent):
        bg = parent["bg"]
        super().__init__(parent, bg=bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, width=px(40), height=px(40),
                                yscrollincrement=px(16))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.sb = ScrollBar(self, self.canvas.yview)
        self.sb.grid(row=0, column=1, sticky="ns", padx=(px(6), 0))
        self.sb.grid_remove()
        self.canvas.config(yscrollcommand=self._set)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.config(scrollregion=(0, 0, e.width, e.height)))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))

    def _set(self, first, last):
        if float(last) - float(first) >= 1:
            self.sb.grid_remove()
            if float(first) != 0:  # content fits: keep it pinned to the top
                self.canvas.yview_moveto(0)
        else:
            self.sb.grid()
        self.sb.set(first, last)

    def wheel(self, e, units=None):
        """Scroll on a wheel event over this area. Windows sends steps of 120, macOS small steps,
        and Linux Button-4/5 events (passed with `units`)."""
        first, last = self.canvas.yview()
        if last - first >= 1:  # nothing to scroll; Tk would otherwise shift the content into empty space
            return
        if units is None:
            units = -e.delta if IS_MAC else -3 * int(e.delta / 120)
        w = self.winfo_containing(e.x_root, e.y_root)
        while w is not None:
            if w is self:
                self.canvas.yview_scroll(units, "units")
                return
            w = w.master

    def see(self, widget):
        """Scroll so `widget` is visible, showing its top if it is taller than the view."""
        self.update_idletasks()
        total = max(1, self.inner.winfo_height())
        view = self.canvas.winfo_height()
        top = self.canvas.canvasy(0)
        y1 = widget.winfo_rooty() - self.inner.winfo_rooty()
        y2 = y1 + widget.winfo_height()
        new_top = top
        if y2 > top + view:
            new_top = y2 - view
        new_top = min(new_top, y1)
        if new_top != top:
            self.canvas.yview_moveto(new_top / total)
