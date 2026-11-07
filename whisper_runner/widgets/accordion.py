"""Accordion: a card that opens to show its body; one in a group is open at a time."""

import tkinter as tk

from ..i18n import tr
from ..theme import CARD, FONT, MUTED, TEXT, px
from .card import Card


class Accordion(Card):
    def __init__(self, parent, title, group, on_open=None):
        super().__init__(parent, CARD, radius=14, pad=14)
        self.group, self.is_open, self.on_open = group, False, on_open
        group.append(self)
        inner = self.inner
        inner.grid_columnconfigure(0, weight=1)
        self.header = tk.Frame(inner, bg=CARD, cursor="hand2")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)
        tk.Label(self.header, text=title, font=FONT["h"], fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w")
        self.summary = tk.Label(self.header, text=tr("Checking\u2026"), font=FONT["small"], fg=MUTED, bg=CARD)
        self.summary.grid(row=0, column=1, sticky="e", padx=(px(8), px(8)))
        self.chevron = tk.Label(self.header, text="\u25B8", font=FONT["h"], fg=MUTED, bg=CARD)
        self.chevron.grid(row=0, column=2, sticky="e")
        for w in (self.header, *self.header.winfo_children()):
            w.bind("<Button-1>", lambda e: self.toggle())
            w.config(cursor="hand2")
        self.body = tk.Frame(inner, bg=CARD)
        self.body.grid(row=1, column=0, sticky="nsew", pady=(px(12), 0))
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_remove()

    def toggle(self):
        opening = not self.is_open
        for a in self.group:
            a.set_open(a is self and opening)
        if opening and self.on_open:
            self.after_idle(self.on_open, self)

    def set_open(self, on):
        self.is_open = on
        if on:
            self.body.grid()
            self.summary.grid_remove()
        else:
            self.body.grid_remove()
            self.summary.grid()
        self.chevron.config(text="\u25BE" if on else "\u25B8")

    def set_summary(self, text, color=MUTED):
        self.summary.config(text=text, fg=color)
