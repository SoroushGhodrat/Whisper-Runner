"""Animated progress bar."""

import time
import tkinter as tk

from ..theme import ACCENT, CARD, mix, px, round_rect


class Progress(tk.Canvas):
    """Progress bar. While active it glides to new values, a shine sweeps across the fill, and
    before there is any progress a short segment slides along the track."""

    FRAME_MS = 16
    SHINE_PERIOD = 1.8   # seconds per sweep
    SLIDE_PERIOD = 1.3

    def __init__(self, parent, height=10):
        super().__init__(parent, width=px(100), height=px(height), bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.value, self.shown, self.color = 0.0, 0.0, ACCENT
        self.active, self.job, self.t0 = False, None, time.time()
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Destroy>", lambda e: self._cancel() if e.widget is self else None)

    def set(self, value, color=None):
        self.value = max(0.0, min(1.0, value))
        if color:
            self.color = color
        if self.value < self.shown or not self.winfo_ismapped():
            self.shown = self.value  # going back (new run) or not visible: no glide
        self._run()

    def start(self):
        self.active, self.t0 = True, time.time()
        self._run()

    def stop(self):
        self.active = False
        self._run()

    def _cancel(self):
        if self.job:
            self.after_cancel(self.job)
            self.job = None

    def _run(self):
        if not self.job:
            self._frame()

    def _frame(self):
        self.job = None
        diff = self.value - self.shown
        self.shown = self.value if abs(diff) < 0.0015 else self.shown + diff * 0.12
        self.draw()
        if self.active or self.shown != self.value:
            self.job = self.after(self.FRAME_MS, self._frame)

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        r = h / 2
        round_rect(self, 0, 0, w - 1, h - 1, r, fill=CARD, outline=CARD)
        t = time.time() - self.t0
        if self.shown > 0:
            fw = max(h, (w - 1) * self.shown)
            round_rect(self, 0, 0, fw, h - 1, r, fill=self.color, outline=self.color)
            if self.active and fw > 3 * h:
                self._shine(fw, h, t)
        elif self.active:
            seg = w * 0.22
            x = ((t / self.SLIDE_PERIOD) % 1) * (w + seg) - seg
            x1, x2 = max(0, x), min(w - 1, x + seg)
            if x2 - x1 > 2:
                fill = mix(self.color, CARD, 0.25)
                round_rect(self, x1, 0, x2, h - 1, r, fill=fill, outline=fill)

    def _shine(self, fw, h, t):
        """Soft light band moving left to right, kept inside the straight part of the fill."""
        band = max(h * 4, fw * 0.18)
        center = ((t / self.SHINE_PERIOD) % 1) * (fw + band) - band / 2
        left, right = h / 2, fw - h / 2
        strips = 14
        sw = band / strips
        for i in range(strips):
            x1 = center - band / 2 + i * sw
            x2 = x1 + sw + 1
            x1, x2 = max(left, x1), min(right, x2)
            if x2 <= x1:
                continue
            k = 1 - abs((i + 0.5) / strips * 2 - 1)  # 0 at the edges, 1 in the middle
            c = mix(self.color, "#FFFFFF", 0.32 * k * k)
            self.create_rectangle(x1, 0, x2, h - 1, fill=c, outline="")
