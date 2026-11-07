"""Button drawn on a canvas: filled, outlined or ghost style, with an optional image."""

import tkinter as tk
import tkinter.font as tkfont

from ..theme import ACCENT, CARD, FONT, TEXT, mix, px, round_rect


class Button(tk.Canvas):
    def __init__(self, parent, text, command, color=ACCENT, style="fill", height=38, padx=20,
                 width=None, image=None):
        self.font = FONT["btn"]
        self.image = image  # shown left of the text
        w = px(width) if width else tkfont.Font(font=self.font).measure(text) + px(padx) * 2 + self._image_w()
        super().__init__(parent, width=w, height=px(height), bg=parent["bg"],
                         highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.command, self.color, self.style = text, command, color, style
        self.enabled, self.hover = True, False
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<ButtonRelease-1>", self._click)

    def _image_w(self):
        return self.image.width() + px(8) if self.image else 0

    def _hover(self, h):
        self.hover = h
        self.draw()

    def _click(self, e):
        if self.enabled and 0 <= e.x < self.winfo_width() and 0 <= e.y < self.winfo_height():
            self.command()

    def set_enabled(self, on):
        self.enabled = on
        self.config(cursor="hand2" if on else "arrow")
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        bg = self["bg"]
        hot = self.hover and self.enabled
        if self.style == "fill":
            fill = mix(self.color, "#FFFFFF", 0.12) if hot else self.color
            outline, tc = fill, "#FFFFFF"
        elif self.style == "outline":
            fill = mix(self.color, bg, 0.72 if hot else 0.86)
            outline, tc = mix(self.color, bg, 0.35), self.color
        else:  # ghost
            fill = mix(CARD, "#FFFFFF", 0.08) if hot else CARD
            outline, tc = fill, TEXT
        if not self.enabled:
            fill, outline, tc = mix(fill, bg, 0.6), mix(outline, bg, 0.6), mix(tc, bg, 0.55)
        round_rect(self, 1, 1, w - 2, h - 2, px(10), fill=fill, outline=outline)
        if self.image:
            x = (w - tkfont.Font(font=self.font).measure(self.text) - self._image_w()) / 2
            self.create_image(x, h / 2, image=self.image, anchor="w")
            self.create_text(x + self._image_w(), h / 2, text=self.text, fill=tc, font=self.font, anchor="w")
        else:
            self.create_text(w / 2, h / 2, text=self.text, fill=tc, font=self.font)
