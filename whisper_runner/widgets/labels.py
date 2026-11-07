"""Label helpers: create, translate, wrap."""

import tkinter as tk

from ..i18n import tr
from ..theme import FONT, TEXT, px


def label(parent, text="", font="body", fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=FONT[font], fg=fg, bg=parent["bg"], **kw)


def say(lbl, text, fg=None, **kw):
    """Show translated text in a label and remember its source, so it can be shown again in
    another language. Fields work as in tr."""
    lbl.src = (text, kw)
    lbl.config(text=tr(text, **kw))
    if fg:
        lbl.config(fg=fg)


def label_state(lbl):
    return getattr(lbl, "src", None), lbl["text"], lbl["fg"]


def set_label_state(lbl, state):
    src, text, fg = state
    if src:
        say(lbl, src[0], fg, **src[1])
    else:
        lbl.config(text=text, fg=fg)


def autowrap(lbl, inset=0):
    """Wrap a label's text to whatever width the layout gives it."""
    lbl.config(wraplength=px(160))
    lbl.bind("<Configure>", lambda e: lbl.config(wraplength=max(px(80), e.width - inset)), add="+")
    return lbl


def clear(frame):
    for w in frame.winfo_children():
        w.destroy()
