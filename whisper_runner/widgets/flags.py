"""Flags of the interface languages, drawn as small images (Windows can't show emoji flags)."""

import tkinter as tk


def _cross(u, v, w, h, cx, half, bg, cross, inner=None, inner_half=0):
    """Nordic cross flag, in the flag's own units: w x h, cross centred at (cx, h / 2)."""
    x, y = u * w, v * h
    if inner and (abs(x - cx) < inner_half or abs(y - h / 2) < inner_half):
        return inner
    return cross if abs(x - cx) < half or abs(y - h / 2) < half else bg


def flag_color(code, u, v):
    """Color of the flag of interface language `code` at (u, v), both 0..1 from the top left.
    The flags are simplified (Spain's has no coat of arms)."""
    if code == "no":
        return _cross(u, v, 22, 16, 8, 2, "#BA0C2F", "#FFFFFF", "#00205B", 1)
    if code == "sv":
        return _cross(u, v, 16, 10, 6, 1, "#006AA7", "#FECC02")
    if code == "da":
        return _cross(u, v, 37, 28, 14, 2, "#C8102E", "#FFFFFF")
    if code == "de":
        return "#000000" if v < 1 / 3 else "#DD0000" if v < 2 / 3 else "#FFCE00"
    if code == "es":
        return "#F1BF00" if 0.25 <= v < 0.75 else "#AA151B"
    if code == "fr":
        return "#002654" if u < 1 / 3 else "#FFFFFF" if u < 2 / 3 else "#ED2939"
    if code == "pl":
        return "#FFFFFF" if v < 0.5 else "#DC143C"
    if code == "uk":
        return "#0057B7" if v < 0.5 else "#FFD700"
    # en: Union Jack, 60 x 30
    x, y = u * 60, v * 30
    if abs(x - 30) < 3 or abs(y - 15) < 3:
        return "#C8102E"
    if abs(x - 30) < 5 or abs(y - 15) < 5:
        return "#FFFFFF"
    diagonal = min(abs(30 * x - 60 * y), abs(30 * x + 60 * y - 1800)) / 67.08  # distance to either diagonal
    if diagonal < 1.3:
        return "#C8102E"
    return "#FFFFFF" if diagonal < 3.5 else "#012169"


FLAGS = {}


def flag_image(code, w, h):
    """Flag as a w x h image with soft edges (3 x 3 samples a pixel) and rounded corners."""
    key = (code, w, h)
    if key not in FLAGS:
        rows = []
        for py in range(h):
            row = []
            for qx in range(w):
                samples = [flag_color(code, (qx + (i + 0.5) / 3) / w, (py + (j + 0.5) / 3) / h)
                           for i in range(3) for j in range(3)]
                rgb = [sum(int(c[k:k + 2], 16) for c in samples) / 9 for k in (1, 3, 5)]
                row.append("#" + "".join(f"{round(c):02x}" for c in rgb))
            rows.append("{" + " ".join(row) + "}")
        img = tk.PhotoImage(width=w, height=h)
        img.put(" ".join(rows))
        for x, y in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
            img.transparency_set(x, y, True)
        FLAGS[key] = img
    return FLAGS[key]
