"""Start the app."""

import tkinter as tk

from . import dnd, i18n
from .app import App
from .config import IS_WIN
from .platform_utils import prepare_process
from .settings import SETTINGS, load_settings
from .theme import px, set_dpi
from .window import fit_window, set_icon, style_titlebar, window_dpi


def main():
    prepare_process()  # before any window exists
    SETTINGS.update(load_settings())
    code = SETTINGS.get("ui_lang")
    i18n.set_language(code if code in [c for c, _, _ in i18n.UI_LANGS] else i18n.system_ui_lang())
    root = tk.Tk()
    root.withdraw()
    dnd.enable(root)
    root.update_idletasks()
    set_dpi(root, window_dpi(root))
    set_icon(root)
    app = App(root)
    fit_window(root, px(1180), px(820))
    root.update_idletasks()
    style_titlebar(root)
    root.deiconify()
    if IS_WIN:
        app.watch_dpi()  # macOS and Linux handle moving between screens themselves
    root.mainloop()
