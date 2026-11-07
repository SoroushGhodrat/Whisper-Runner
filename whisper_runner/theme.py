"""Colors, the pixel scale for the monitor's DPI, fonts, and drawing helpers."""

import tkinter.font as tkfont

from .config import IS_MAC, IS_WIN


BG = "#1E1F31"


PANEL = "#2A2C43"


CARD = "#33354F"


ACCENT = "#5C7CFA"


PURPLE = "#8B6CF6"


GREEN = "#3DD68C"


ORANGE = "#F5A524"


RED = "#F2546B"


TEAL = "#2CC4D4"


PINK = "#E86BA8"


MUTED = "#8C90B5"


TEXT = "#ECEDF7"


SCALE = 1.0


FONT = {}


def px(n):
    return int(round(n * SCALE))


def mix(a, b, t):
    """Blend color a toward b by t (0..1)."""
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb))


def colorref(c):
    c = c.lstrip("#")
    return int(c[0:2], 16) | int(c[2:4], 16) << 8 | int(c[4:6], 16) << 16


def round_rect(c, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return c.create_polygon(pts, smooth=True, **kw)


def first_font(families, *names):
    return next((n for n in names if n in families), names[-1])


def set_dpi(root, dpi):
    """Set the pixel scale and fonts for a monitor's DPI. Fonts use pixel sizes so they follow it."""
    global SCALE
    SCALE = dpi / 96
    if not IS_MAC:
        root.tk.call("tk", "scaling", dpi / 72)
    families = set(tkfont.families(root))
    if IS_WIN:
        ui = first_font(families, "Segoe UI Variable Text", "Segoe UI")
        semi = (first_font(families, "Segoe UI Semibold", ui), "normal")
        mono = first_font(families, "Cascadia Mono", "Consolas")
    elif IS_MAC:
        ui = first_font(families, "SF Pro Text", "Helvetica Neue", "Helvetica")
        semi = (ui, "bold")
        mono = first_font(families, "SF Mono", "Menlo", "Monaco", "Courier")
    else:
        ui = first_font(families, "Inter", "Cantarell", "Ubuntu", "Noto Sans", "DejaVu Sans", "Helvetica")
        semi = (ui, "bold")
        mono = first_font(families, "JetBrains Mono", "Ubuntu Mono", "Noto Sans Mono", "DejaVu Sans Mono",
                          "Courier")
    regular = (ui, "normal")
    points = dict(title=(semi, 16), h=(semi, 11), body=(regular, 10), text=(regular, 11),
                  small=(regular, 9), tiny=(regular, 8), big=(semi, 34), stat=(semi, 17),
                  btn=(semi, 10), tab=(semi, 9), badge=(semi, 8), mono=((mono, "normal"), 9))
    FONT.update({k: (fam, -round(pt * dpi / 72), weight) for k, ((fam, weight), pt) in points.items()})
