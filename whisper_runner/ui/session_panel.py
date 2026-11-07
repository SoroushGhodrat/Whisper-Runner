"""Session panel (right side): the language and About buttons, live stats for the run, and the Your
system and Requirements sections."""

import tkinter as tk

from ..i18n import tr
from ..system import ram_gb
from ..theme import ACCENT, CARD, GREEN, MUTED, ORANGE, PANEL, PINK, PURPLE, TEAL, px
from ..widgets import Card, ScrollArea, label
from .app_buttons import AppButtons
from .requirements_section import RequirementsSection
from .system_section import SystemSection

DASH = "—"


class StatTiles(tk.Frame):
    """Two columns of tiles, each with a title, a big value and a note."""

    def __init__(self, parent):
        super().__init__(parent, bg=PANEL)
        self.grid_columnconfigure((0, 1), weight=1, uniform="s")
        ram = ram_gb()
        items = [("elapsed", "Elapsed", ACCENT, "since start"),
                 ("left", "Time left", PURPLE, "estimate"),
                 ("finish", "Finishes at", GREEN, "local time"),
                 ("speed", "Speed", ORANGE, "audio time per second"),
                 ("cpu", "CPU use", TEAL, "Whisper, of the whole CPU"),
                 ("ram", "Memory use", PINK, tr("Whisper, of {gb} GB", gb=ram) if ram else "Whisper")]
        self.values = {}
        for i, (key, title, color, sub) in enumerate(items):
            title, sub = tr(title), tr(sub)
            c = Card(self, CARD, radius=14, pad=14)
            c.grid(row=i // 2, column=i % 2, sticky="nsew",
                   padx=(0, px(6)) if i % 2 == 0 else (px(6), 0), pady=(0, px(12)))
            head = tk.Frame(c.inner, bg=CARD)
            head.grid(row=0, column=0, sticky="w")
            dot = tk.Canvas(head, width=px(8), height=px(8), bg=CARD, highlightthickness=0, bd=0)
            dot.create_oval(0, 0, px(8) - 1, px(8) - 1, fill=color, outline="")
            dot.grid(row=0, column=0, padx=(0, px(6)))
            label(head, title, "small", MUTED).grid(row=0, column=1)
            value = label(c.inner, DASH, "stat", anchor="w")
            value.grid(row=1, column=0, sticky="w", pady=(px(4), 0))
            label(c.inner, sub, "tiny", MUTED).grid(row=2, column=0, sticky="w")
            self.values[key] = value

    def set(self, key, text):
        self.values[key].config(text=text)

    def reset(self):
        for key in self.values:
            self.set(key, DASH)

    def state(self):
        return {k: v["text"] for k, v in self.values.items()}

    def restore(self, state):
        for k, text in state.items():
            self.set(k, text)


class SessionPanel(tk.Frame):
    def __init__(self, parent, on_about, on_language):
        super().__init__(parent, bg=PANEL)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)
        self.buttons = AppButtons(self, on_about, on_language)
        self.buttons.grid(row=0, column=0, sticky="e", pady=(0, px(10)))
        label(self, tr("Session"), "title").grid(row=1, column=0, sticky="w")
        label(self, tr("Live stats for the current run"), "small", MUTED).grid(row=2, column=0, sticky="w")

        self.area = ScrollArea(self)
        self.area.grid(row=3, column=0, sticky="nsew", pady=(px(16), 0))
        body = self.area.inner
        body.grid_columnconfigure(0, weight=1)
        self.tiles = StatTiles(body)
        self.tiles.grid(row=0, column=0, sticky="ew")
        group = []  # one section open at a time
        self.system = SystemSection(body, group, self.area.see)
        self.system.grid(row=1, column=0, sticky="ew", pady=(px(4), 0))
        self.requirements = RequirementsSection(body, group, self.area.see)
        self.requirements.grid(row=2, column=0, sticky="ew", pady=(px(12), 0))

    def wheel(self, e, units=None):
        self.area.wheel(e, units)

    def set_stat(self, key, text):
        self.tiles.set(key, text)

    def reset_stats(self):
        self.tiles.reset()

    def state(self):
        return self.tiles.state(), (self.system.is_open, self.requirements.is_open)

    def restore(self, state):
        stats, (system_open, requirements_open) = state
        self.tiles.restore(stats)
        self.system.set_open(system_open)
        self.requirements.set_open(requirements_open)
