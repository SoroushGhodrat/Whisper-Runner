"""Transcript view: the transcript as Whisper writes it and Whisper's log, in two tabs, with Open folder
and Copy."""

import tkinter as tk

from ..i18n import tr
from ..theme import ACCENT, CARD, FONT, MUTED, PANEL, RED, TEXT, mix, px
from ..widgets import Button, Card, ScrollBar, Tabs

TAGS = ("muted", "ts", "err")  # muted placeholder text, timestamps, errors in the log


def text_area(parent, mono=False):
    """Read-only text with a scroll bar. Returns (frame, text)."""
    parent.grid_columnconfigure(0, weight=1)
    parent.grid_rowconfigure(0, weight=1)
    frame = tk.Frame(parent, bg=CARD)
    frame.grid(row=0, column=0, sticky="nsew")
    frame.grid_columnconfigure(0, weight=1)
    frame.grid_rowconfigure(0, weight=1)
    text = tk.Text(frame, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0,
                   highlightthickness=0, wrap="word", font=FONT["mono" if mono else "text"],
                   padx=px(8), pady=px(6), spacing3=px(3 if mono else 6), height=6, width=40,
                   selectbackground=ACCENT, selectforeground="#FFFFFF", state="disabled")
    text.grid(row=0, column=0, sticky="nsew")
    sb = ScrollBar(frame, text.yview)
    sb.grid(row=0, column=1, sticky="ns")
    text.config(yscrollcommand=sb.set)
    text.tag_config("muted", foreground=MUTED)
    text.tag_config("ts", foreground=mix(MUTED, CARD, 0.2), font=FONT["mono"])
    text.tag_config("err", foreground=RED)
    return frame, text


def write(text, s, tag=None, replace=False):
    """Add to a read-only text, following the end if it was scrolled to the end."""
    follow = text.yview()[1] >= 0.999
    text.config(state="normal")
    if replace:
        text.delete("1.0", "end")
    text.insert("end", s, tag)
    text.config(state="disabled")
    if follow or replace:
        text.see("end")


def dump(text):
    return text.get("1.0", "end-1c"), {tag: [str(i) for i in text.tag_ranges(tag)] for tag in TAGS}


def load(text, data):
    content, tags = data
    text.config(state="normal")
    text.delete("1.0", "end")
    text.insert("1.0", content)
    for tag, idx in tags.items():
        for a, b in zip(idx[::2], idx[1::2]):
            text.tag_add(tag, a, b)
    text.config(state="disabled")
    text.see("end")


class TranscriptView(tk.Frame):
    def __init__(self, parent, on_open_folder):
        super().__init__(parent, bg=PANEL)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        bar = tk.Frame(self, bg=PANEL)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, px(10)))
        bar.grid_columnconfigure(1, weight=1)
        self.tabs = Tabs(bar, [(tr("Transcript"), "t"), (tr("Log"), "l")], lambda i, view: self.show(view),
                         height=32)
        self.tabs.config(width=px(220))
        self.tabs.grid(row=0, column=0, sticky="w")
        self.open_btn = Button(bar, tr("Open folder"), on_open_folder, style="ghost", height=32, padx=14)
        self.open_btn.grid(row=0, column=2, padx=(px(8), 0))
        self.copy_btn = Button(bar, tr("Copy"), self.copy, style="ghost", height=32, padx=14)
        self.copy_btn.grid(row=0, column=3, padx=(px(8), 0))
        self.set_enabled(open_folder=False, copy=False)

        card = Card(self, CARD, radius=14, pad=8)
        card.grid(row=1, column=0, sticky="nsew")
        self.transcript_frame, self.text = text_area(card.inner)
        self.log_frame, self.log_text = text_area(card.inner, mono=True)
        self.log_frame.grid_remove()
        self.empty = True  # no transcript yet: the text shows a muted placeholder
        self.set_placeholder("The transcript appears here while Whisper works through the audio.")

    def show(self, view):
        """Show the transcript ("t") or the log ("l")."""
        self.tabs.select(0 if view == "t" else 1)
        if view == "t":
            self.log_frame.grid_remove()
            self.transcript_frame.grid()
        else:
            self.transcript_frame.grid_remove()
            self.log_frame.grid()

    def set_enabled(self, open_folder, copy):
        self.open_btn.set_enabled(open_folder)
        self.copy_btn.set_enabled(copy)

    # ---- transcript

    def set_placeholder(self, text):
        """Empty the transcript and show muted `text` (English; shown translated) in its place."""
        self.placeholder, self.empty = text, True
        write(self.text, tr(text), "muted", replace=True)

    def add_segment(self, clock, words):
        """A line from Whisper: its start time and the words."""
        if self.empty:
            write(self.text, "", replace=True)
            self.empty = False
        write(self.text, f"{clock}  ", "ts")
        write(self.text, words + "\n")

    def set_result(self, text):
        """The finished transcript, from Whisper's file."""
        if text:
            write(self.text, text, replace=True)
            self.empty = False
        else:
            self.set_placeholder("(Whisper found no speech in this file.)")
        self.text.see("1.0")

    def copy(self):
        text = self.text.get("1.0", "end").strip()
        if text and not self.empty:
            self.clipboard_clear()
            self.clipboard_append(text)
            self.copy_btn.text = tr("Copied ✓")
            self.copy_btn.draw()
            self.after(1200, self._reset_copy)

    def _reset_copy(self):
        self.copy_btn.text = tr("Copy")
        self.copy_btn.draw()

    # ---- log

    def reset_log(self, first_line):
        write(self.log_text, first_line + "\n\n", "muted", replace=True)

    def log(self, line, tag=None):
        write(self.log_text, line + "\n", tag)

    def log_lines(self):
        return [line for line in self.log_text.get("1.0", "end").splitlines() if line.strip()]

    # ---- rebuilding

    def state(self):
        return {"view": self.tabs.sel, "texts": (dump(self.text), dump(self.log_text)),
                "empty": self.empty, "placeholder": self.placeholder}

    def restore(self, state):
        self.show("t" if state["view"] == 0 else "l")
        load(self.text, state["texts"][0])
        load(self.log_text, state["texts"][1])
        self.empty, self.placeholder = state["empty"], state["placeholder"]
        if self.empty:
            self.set_placeholder(self.placeholder)  # again, in the current language
