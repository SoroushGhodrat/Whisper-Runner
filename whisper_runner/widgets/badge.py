"""Badge: a small rounded label."""

import tkinter as tk
import tkinter.font as tkfont

from ..theme import FONT, MUTED, mix, px, round_rect


class Badge(tk.Canvas):
    def __init__(self, parent, text="", color=MUTED):
        super().__init__(parent, height=px(22), width=px(20), bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.set(text, color)

    def set(self, text, color):
        self.text, self.color = text, color
        w = tkfont.Font(font=FONT["badge"]).measure(text) + px(18)
        self.config(width=w)
        self.delete("all")
        h = px(22)
        fill = mix(color, self["bg"], 0.8)
        round_rect(self, 0, 0, w - 1, h - 1, h / 2, fill=fill, outline=fill)
        self.create_text(w / 2, h / 2, text=text, fill=color, font=FONT["badge"])
