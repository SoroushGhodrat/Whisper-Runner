"""Model selector: the Whisper model tabs, whether the selected model is installed, and its Download
button."""

import tkinter as tk

from ..config import MODEL_FILES, MODELS
from ..i18n import tr
from ..models import model_downloaded
from ..theme import ACCENT, MUTED, ORANGE, PANEL, PURPLE, px
from ..util import fmt_size
from ..widgets import Button, Tabs, autowrap, label, say


class ModelSelector(tk.Frame):
    def __init__(self, parent, on_select, on_download):
        """`on_select(model)` returning False keeps the old selection; `on_download(model)`."""
        super().__init__(parent, bg=PANEL)
        self.grid_columnconfigure(0, weight=1)
        head = tk.Frame(self, bg=PANEL)
        head.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, px(8)))
        head.grid_columnconfigure(0, weight=1)
        label(head, tr("Model"), "h").grid(row=0, column=0, sticky="w")
        self.note = label(head, tr("Checking your system…"), "small", MUTED)
        self.note.grid(row=0, column=1, sticky="e")
        self.tabs = Tabs(self, [(m, m) for m in MODELS], lambda i, value: on_select(value))
        self.tabs.set_value("base")
        self.tabs.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.status = autowrap(label(self, "", "small", MUTED, anchor="w", justify="left"))
        self.status.grid(row=2, column=0, sticky="ew", pady=(px(6), 0))
        self.download_btn = Button(self, tr("Download"), lambda: on_download(self.value), style="outline",
                                   height=28, padx=14)
        self.download_btn.grid(row=2, column=1, sticky="e", padx=(px(10), 0), pady=(px(6), 0))

    @property
    def value(self):
        return self.tabs.value

    def select(self, model):
        self.tabs.set_value(model)

    def set_enabled(self, on):
        self.tabs.set_enabled(on)
        self.download_btn.set_enabled(on)

    def refresh(self, downloading, suggested, user_model):
        """Update the line under the tabs (is the model on this computer?) and the note above them
        (which model suits this PC)."""
        model = self.value
        if downloading:
            say(self.status, "↓ Downloading {model}…", PURPLE, model=downloading)
            self.download_btn.grid_remove()
        elif model_downloaded(model):
            say(self.status, "✓ {model} is installed and ready", MUTED, model=model)
            self.download_btn.grid_remove()
        else:
            say(self.status, "{model} isn't installed yet ({size}). Click Download to install it "
                             "(needs internet).", ORANGE, model=model, size=fmt_size(MODEL_FILES[model][1]))
            self.download_btn.grid()
        if suggested and model == suggested:
            say(self.note, "Suggested for this PC: {model}", MUTED, model=suggested)
        elif suggested:
            say(self.note, "Selected manually · suggested for this PC: {model}", ACCENT, model=suggested)
        elif user_model:
            say(self.note, "Selected manually · checking your system…", ACCENT)
        else:
            say(self.note, "Checking your system…", MUTED)

    def state(self):
        return self.tabs.sel

    def restore(self, state):
        self.tabs.select(state)
