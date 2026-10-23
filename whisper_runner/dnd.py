"""Optional drag-and-drop: dropping files on the window needs the tkinterdnd2 package (Tkinter can't
do it alone)."""

import tkinter as tk

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES, TkinterDnD = None, None

available = False  # set by enable() once the tkdnd library has loaded


def enable(root):
    """Load the tkdnd library into this Tk. Without it (package missing, or no build for this
    platform) the app works, just without drag-and-drop."""
    global available
    if TkinterDnD:
        try:
            TkinterDnD._require(root)
            available = True
        except (RuntimeError, tk.TclError):
            pass
