"""Requirements: Python, Whisper, torch, FFmpeg and tkinterdnd2, each with its installed and latest
version and, when needed, the command that installs or updates it (click to copy)."""

import tkinter as tk

from ..i18n import tr, tr_note
from ..platform_utils import os_name
from ..theme import ACCENT, BG, CARD, FONT, GREEN, MUTED, ORANGE, PURPLE, RED, mix, px
from ..widgets import Accordion, Badge, autowrap, clear, label

BADGES = {"ok": ("Up to date", GREEN), "update": ("Update", ORANGE), "missing": ("Missing", RED),
          "warn": ("CPU build", ORANGE), "unknown": ("Couldn't check", MUTED), "optional": ("Optional", PURPLE)}


class RequirementsSection(Accordion):
    def __init__(self, parent, group, on_open):
        super().__init__(parent, tr("Requirements"), group, on_open)
        label(self.body, tr("Checking…"), "small", MUTED).grid(row=0, column=0, sticky="w")

    def show(self, items):
        """`items` from requirements.check_requirements()."""
        body = self.body
        clear(body)
        label(body, tr("Commands for {os}", os=os_name()), "tiny", MUTED).grid(row=0, column=0, sticky="w",
                                                                              pady=(0, px(10)))
        for i, it in enumerate(items):
            block = tk.Frame(body, bg=CARD)
            block.grid(row=i * 2 + 1, column=0, sticky="ew", pady=(0 if i == 0 else px(8), 0))
            block.grid_columnconfigure(0, weight=1)
            label(block, tr(it["name"]), "h").grid(row=0, column=0, sticky="w")
            text, color = BADGES[it["state"]]
            Badge(block, tr(text), color).grid(row=0, column=1, sticky="e")
            versions = (tr("Installed {version}", version=it["installed"]) if it["installed"]
                        else tr("Not installed")) + " · " + tr("Latest {version}",
                                                                   version=it["latest"] or tr("unknown"))
            label(block, versions, "tiny", MUTED).grid(row=1, column=0, columnspan=2, sticky="w")
            r = 2
            if it["note"]:
                autowrap(label(block, tr_note(it["note"]), "tiny", MUTED, justify="left", anchor="w")).grid(
                    row=r, column=0, columnspan=2, sticky="w", pady=(px(2), 0))
                r += 1
            if it["cmd"]:
                self._copyable(block, it["cmd"]).grid(row=r, column=0, columnspan=2, sticky="ew",
                                                      pady=(px(6), 0))
            if i < len(items) - 1:
                tk.Frame(body, bg=mix(MUTED, CARD, 0.75), height=1).grid(
                    row=i * 2 + 2, column=0, sticky="ew", pady=(px(8), 0))
        if any(it["cmd"] for it in items):
            label(body, tr("Click a command to copy it, then paste it in a terminal."), "tiny", MUTED).grid(
                row=len(items) * 2 + 1, column=0, sticky="w", pady=(px(10), 0))

        missing = sum(it["state"] == "missing" for it in items)
        updates = sum(it["state"] in ("update", "warn") for it in items)
        if missing:
            self.set_summary(tr("{n} missing", n=missing), RED)
        elif updates:
            self.set_summary(tr("{n} updates available", n=updates) if updates > 1
                             else tr("1 update available"), ORANGE)
        elif all(it["state"] == "unknown" or it["state"] == "ok" for it in items) and \
                any(it["state"] == "unknown" for it in items):
            self.set_summary(tr("Installed · couldn't check online"), MUTED)
        else:
            self.set_summary(tr("All up to date"), GREEN)

    def _copyable(self, parent, cmd):
        """A command that copies itself to the clipboard when clicked."""
        bg = mix(BG, CARD, 0.4)
        lbl = tk.Label(parent, text=cmd, font=FONT["mono"], fg=ACCENT, bg=bg, anchor="w", justify="left",
                       padx=px(8), pady=px(5), cursor="hand2")
        autowrap(lbl, 2 * px(8) + 2)

        def copy(_e):
            lbl.clipboard_clear()
            lbl.clipboard_append(cmd)
            lbl.config(text=tr("Copied ✓"), fg=GREEN)
            lbl.after(1200, lambda: lbl.winfo_exists() and lbl.config(text=cmd, fg=ACCENT))
        lbl.bind("<Button-1>", copy)
        lbl.bind("<Enter>", lambda e: lbl.config(bg=mix(BG, CARD, 0.15)))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=bg))
        return lbl
