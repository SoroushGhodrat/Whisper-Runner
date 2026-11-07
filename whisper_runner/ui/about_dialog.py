"""About: what the app is, its version, and whether a newer release is out (with an option to skip it)."""

import base64
import threading
import tkinter as tk
import webbrowser

from .. import updates
from ..config import APP_VERSION, REPO_URL
from ..i18n import tr
from ..theme import ACCENT, BG, GREEN, MUTED, ORANGE, PANEL, px
from ..util import latest_app_version
from ..widgets import Button, Card, label
from ..window import icon_png, style_titlebar


class AboutDialog(tk.Toplevel):
    current = None  # the open dialog

    @classmethod
    def show(cls, root, post, latest, on_latest, on_skip):
        """Open the dialog, or bring it to the front.

        `latest`: the newest released version if already known, None if the check failed, False if it
        hasn't been made. When not known, the dialog asks GitHub and passes the answer to on_latest.
        `on_skip(version)`: the user chose not to be reminded about that version.
        `post(fn, *args)` runs fn on the UI thread."""
        if cls.current and cls.current.winfo_exists():
            cls.current.lift()
        else:
            cls.current = cls(root, post, latest, on_latest, on_skip)

    def __init__(self, root, post, latest, on_latest, on_skip):
        super().__init__(root, bg=BG)
        self.on_latest, self.on_skip = on_latest, on_skip
        self.withdraw()
        self.title(tr("About Whisper Runner"))
        self.resizable(False, False)
        self.transient(root)
        card = Card(self, PANEL, radius=18, pad=24)
        card.pack(fill="both", expand=True, padx=px(14), pady=px(14))
        p = card.inner
        p.grid_columnconfigure(1, weight=1)
        wrap = px(420)

        self.icon_img = tk.PhotoImage(master=self, data=base64.b64encode(icon_png(px(64))))
        tk.Label(p, image=self.icon_img, bg=PANEL, bd=0).grid(row=0, column=0, rowspan=2, padx=(0, px(14)))
        label(p, "Whisper Runner", "title").grid(row=0, column=1, sticky="sw")
        label(p, tr("Version {version}", version=APP_VERSION), "small", MUTED).grid(row=1, column=1, sticky="nw")
        label(p, tr("Whisper Runner transcribes audio and video files with OpenAI Whisper and shows the work as it "
                    "happens: progress, time left, speed, and the transcript line by line. The transcript is saved "
                    "as a text file next to the recording.\n\nEverything runs on this computer. Your recordings "
                    "are never uploaded."),
              "body", justify="left", wraplength=wrap).grid(row=2, column=0, columnspan=2, sticky="w",
                                                            pady=(px(18), 0))
        self.latest_lbl = label(p, tr("Checking for a newer version…"), "small", MUTED, justify="left",
                                wraplength=wrap)
        self.latest_lbl.grid(row=3, column=0, columnspan=2, sticky="w", pady=(px(14), 0))
        link = label(p, tr("Project page on GitHub"), "small", ACCENT, cursor="hand2")
        link.grid(row=4, column=0, columnspan=2, sticky="w", pady=(px(6), 0))
        link.bind("<Button-1>", lambda e: webbrowser.open(REPO_URL))
        label(p, tr("MIT license"), "tiny", MUTED).grid(row=5, column=0, columnspan=2, sticky="w", pady=(px(2), 0))
        buttons = tk.Frame(p, bg=PANEL)
        buttons.grid(row=6, column=0, columnspan=2, sticky="e", pady=(px(18), 0))
        self.skip_btn = Button(buttons, tr("Skip this version"), self._skip, style="ghost", height=34, padx=20)
        self.skip_btn.grid(row=0, column=0, padx=(0, px(8)))
        self.skip_btn.grid_remove()  # only while a newer version is shown
        Button(buttons, tr("Close"), self.destroy, style="ghost", height=34, padx=20).grid(row=0, column=1)
        self.bind("<Escape>", lambda e: self.destroy())

        self.update_idletasks()
        x = root.winfo_rootx() + (root.winfo_width() - self.winfo_reqwidth()) // 2
        y = root.winfo_rooty() + (root.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        style_titlebar(self)
        self.deiconify()
        self.focus_set()
        try:
            self.grab_set()  # modal, so the language can't change underneath it
        except tk.TclError:
            pass

        self.latest = None
        if latest:
            self._show_latest(latest)
        else:  # not checked yet, or the last check failed: ask now
            threading.Thread(target=lambda: post(self._checked, latest_app_version()), daemon=True).start()

    def _checked(self, latest):
        self.on_latest(latest)
        self._show_latest(latest)

    def _show_latest(self, latest):
        self.latest = latest
        if not self.latest_lbl.winfo_exists():  # closed before the answer came
            return
        if latest is None:
            self.latest_lbl.config(text=tr("Couldn't check for a newer version. Are you online?"), fg=MUTED)
        elif updates.is_newer(latest):
            self.latest_lbl.config(text=tr("Version {version} is available. Get it from the project page below.",
                                           version=latest), fg=ORANGE)
            if updates.is_skipped(latest):
                self.latest_lbl.config(text=self.latest_lbl["text"] + "\n" +
                                       tr("You won't be reminded about version {version}.", version=latest))
            else:
                self.skip_btn.grid()
        else:
            self.latest_lbl.config(text=tr("You have the latest version."), fg=GREEN)

    def _skip(self):
        self.skip_btn.grid_remove()
        self.on_skip(self.latest)
        self._show_latest(self.latest)
