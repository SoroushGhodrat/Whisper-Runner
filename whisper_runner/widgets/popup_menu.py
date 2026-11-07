"""Dark dropdown list in the app's style."""

import math
import time
import tkinter as tk

from ..config import IS_WIN
from ..theme import ACCENT, BG, CARD, FONT, MUTED, TEXT, mix, px
from ..window import work_area
from .card import Card
from .flags import flag_image


class PopupMenu(tk.Toplevel):
    """Dark dropdown list shown under `anchor`, in the app's style (Tk's own menus can't be styled
    on Windows). `items` is [(value, text, hint)] or [(value, text, hint, flag code)]; the hint is
    shown muted on the right, the flag left of the text.
    `command(value)` runs when an item is picked. Closes on Escape or a click outside."""

    closed_at = 0.0  # time the last popup closed: a click that closes one mustn't reopen it

    def __init__(self, anchor, items, current, command, align="left", min_width=0):
        root = anchor.winfo_toplevel()
        key = "#010203"  # see-through color on Windows, so the corners come out rounded
        super().__init__(root, bg=key if IS_WIN else BG)
        self.withdraw()
        self.overrideredirect(True)
        if IS_WIN:
            self.attributes("-transparentcolor", key)
        self.attributes("-topmost", True)
        self.items, self.command, self.hot, self.had_focus = items, command, -1, False

        self.fill = mix(CARD, "#FFFFFF", 0.03)
        self.hover_fill = mix(ACCENT, self.fill, 0.72)
        card = Card(self, self.fill, radius=12, pad=6)
        card.set_outline(mix(MUTED, self.fill, 0.55))
        card.pack(fill="both", expand=True)
        box = card.inner
        per_col = len(items) if len(items) <= 10 else math.ceil(len(items) / 2)  # long lists: two columns
        for c in range(math.ceil(len(items) / per_col)):
            box.grid_columnconfigure(c, weight=1, uniform="col")
        self.rows = []
        for i, (value, text, hint, *flag) in enumerate(items):
            selected = value == current
            row = tk.Frame(box, bg=self.fill, cursor="hand2")
            row.grid(row=i % per_col, column=i // per_col, sticky="ew")
            row.grid_columnconfigure(2, weight=1)
            parts = [
                tk.Label(row, text="✓" if selected else "", width=2, font=FONT["btn"], fg=ACCENT,
                         bg=self.fill),
                tk.Label(row, text=text, font=FONT["btn" if selected else "body"],
                         fg=ACCENT if selected else TEXT, bg=self.fill, anchor="w"),
                tk.Label(row, text=hint, font=FONT["small"], fg=MUTED, bg=self.fill, anchor="e"),
            ]
            parts[0].grid(row=0, column=0, padx=(px(6), 0), pady=px(6))
            parts[1].grid(row=0, column=2, sticky="w", padx=(px(2), px(16)))
            parts[2].grid(row=0, column=3, sticky="e", padx=(0, px(10)))
            if flag:
                parts.append(tk.Label(row, image=flag_image(flag[0], px(22), px(15)), bg=self.fill, bd=0))
                parts[3].grid(row=0, column=1, padx=(px(2), px(8)))
            for w in (row, *parts):
                w.bind("<Enter>", lambda e, i=i: self._highlight(i))
                w.bind("<ButtonRelease-1>", lambda e, i=i: self._pick(i))
            self.rows.append((row, parts))
            if selected:
                self.hot = i

        self.bind("<Escape>", lambda e: self.close())
        self.bind("<Up>", lambda e: self._move(-1))
        self.bind("<Down>", lambda e: self._move(1))
        self.bind("<Return>", lambda e: self.hot >= 0 and self._pick(self.hot))
        self.bind("<ButtonPress-1>", self._press)
        self._place(anchor, align, min_width)
        self.deiconify()
        self.lift()
        self.focus_force()
        try:
            self.grab_set()  # clicks elsewhere in the app come here, so they can close it
        except tk.TclError:
            pass
        if self.hot >= 0:
            self._highlight(self.hot)
        self.after(150, self._watch_focus)

    def _place(self, anchor, align, min_width):
        self.update_idletasks()
        w = max(self.winfo_reqwidth(), min_width)
        h = self.winfo_reqheight()
        ax, ay = anchor.winfo_rootx(), anchor.winfo_rooty()
        x = ax if align == "left" else ax + anchor.winfo_width() - w
        y = ay + anchor.winfo_height() + px(4)
        left, top, right, bottom = work_area(anchor.winfo_toplevel())
        if y + h > bottom:  # no room below: open above
            y = max(top, ay - h - px(4))
        x = max(left, min(x, right - w))
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _highlight(self, i):
        for j, (row, parts) in enumerate(self.rows):
            bg = self.hover_fill if j == i else self.fill
            for w in (row, *parts):
                w.config(bg=bg)
        self.hot = i

    def _move(self, step):
        self._highlight((self.hot + step) % len(self.rows) if self.hot >= 0 else 0)

    def _pick(self, i):
        value = self.items[i][0]
        self.close()
        self.command(value)

    def _press(self, e):
        w = self.winfo_containing(e.x_root, e.y_root)
        if w is None or w.winfo_toplevel() is not self:
            self.close()

    def _watch_focus(self):
        """Close when another program is brought to the front."""
        if not self.winfo_exists():
            return
        focused = self.focus_get() is not None
        if self.had_focus and not focused:
            self.close()
            return
        self.had_focus = self.had_focus or focused
        self.after(150, self._watch_focus)

    def close(self):
        PopupMenu.closed_at = time.time()
        if self.winfo_exists():
            self.grab_release()
            self.destroy()

    @staticmethod
    def just_closed():
        return time.time() - PopupMenu.closed_at < 0.3
