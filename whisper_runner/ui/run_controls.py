"""Run controls: Start transcribing, Pause/Resume and Cancel."""

import tkinter as tk

from ..i18n import tr
from ..theme import PANEL, RED, px
from ..widgets import Button


class RunControls(tk.Frame):
    def __init__(self, parent, on_start, on_pause, on_cancel):
        super().__init__(parent, bg=PANEL)
        self.start_btn = Button(self, tr("Start transcribing"), on_start, height=40, padx=24)
        self.start_btn.grid(row=0, column=0)
        self.pause_btn = Button(self, tr("Pause"), on_pause, style="outline", width=110, height=40)
        self.pause_btn.grid(row=0, column=1, padx=(px(10), 0))
        self.cancel_btn = Button(self, tr("Cancel"), on_cancel, color=RED, style="outline", width=110, height=40)
        self.cancel_btn.grid(row=0, column=2, padx=(px(10), 0))
        self.set_state(start=False, pause=False, cancel=False)

    def set_state(self, start=None, pause=None, cancel=None):
        """Enable or disable the buttons; None leaves one as it is."""
        for button, on in ((self.start_btn, start), (self.pause_btn, pause), (self.cancel_btn, cancel)):
            if on is not None:
                button.set_enabled(on)

    def set_paused(self, paused):
        """The pause button reads Resume while Whisper is paused."""
        self.pause_btn.text = tr("Resume" if paused else "Pause")
        self.pause_btn.draw()
