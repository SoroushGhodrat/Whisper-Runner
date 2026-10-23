"""The main window: title bar, icon, monitor DPI and work area, size and position."""

import base64
import ctypes
import math
import struct
import tkinter as tk
import zlib

from .config import IS_MAC, IS_WIN
from .theme import ACCENT, BG, PURPLE, TEXT, colorref, px

if IS_WIN:
    from ctypes import wintypes


def style_titlebar(root):
    """Dark title bar: on Windows 11 colored to match the background, on macOS the dark appearance."""
    if IS_MAC:
        try:
            root.tk.call("::tk::unsupported::MacWindowStyle", "appearance", root, "darkaqua")
        except tk.TclError:
            pass
        return
    if not IS_WIN:
        return  # the window manager draws the title bar on Linux
    try:
        hwnd = hwnd_of(root)
        dwm = ctypes.windll.dwmapi

        def set_attr(attr, value):
            v = ctypes.c_int(value)
            dwm.DwmSetWindowAttribute(hwnd, attr, ctypes.byref(v), ctypes.sizeof(v))
        set_attr(20, 1)                  # immersive dark mode
        set_attr(34, colorref(BG))       # border
        set_attr(35, colorref(BG))       # caption
        set_attr(36, colorref(TEXT))     # caption text
    except Exception:
        pass


def _seg_dist(x, y, ax, ay, bx, by):
    """Distance from (x, y) to the segment a-b."""
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - ax - t * dx, y - ay - t * dy)


def icon_png(size):
    """App icon as PNG bytes: a white microphone and lines of text on a blue-to-purple rounded square.
    Shapes are distance fields, so edges come out anti-aliased at any size."""
    c1 = [int(ACCENT[i:i + 2], 16) for i in (1, 3, 5)]
    c2 = [int(PURPLE[i:i + 2], 16) for i in (1, 3, 5)]
    aa = 1 / size  # one pixel in unit coordinates
    lines = ((0.37, 0.80), (0.50, 0.86), (0.63, 0.74))  # text lines: y, right end
    rows = bytearray()
    for py in range(size):
        rows.append(0)  # PNG filter type: none
        y = (py + 0.5) / size
        for qx in range(size):
            x = (qx + 0.5) / size
            # Rounded square background.
            m, r = 0.04, 0.22
            dx, dy = max(abs(x - 0.5) - (0.5 - m - r), 0), max(abs(y - 0.5) - (0.5 - m - r), 0)
            bg = min(max((r - math.hypot(dx, dy)) / aa + 0.5, 0), 1)
            if bg <= 0:
                rows += b"\0\0\0\0"
                continue
            # Microphone: capsule, U-shaped holder, stem and base.
            d = _seg_dist(x, y, 0.36, 0.25, 0.36, 0.47) - 0.105
            if y > 0.47:
                d = min(d, abs(math.hypot(x - 0.36, y - 0.47) - 0.175) - 0.024)
            d = min(d, _seg_dist(x, y, 0.36, 0.645, 0.36, 0.76) - 0.024)
            d = min(d, _seg_dist(x, y, 0.27, 0.77, 0.45, 0.77) - 0.028)
            fg = min(max(-d / aa + 0.5, 0), 1)
            # Transcribed text.
            d = min(_seg_dist(x, y, 0.64, ly, rx, ly) for ly, rx in lines) - 0.03
            fg = max(fg, 0.85 * min(max(-d / aa + 0.5, 0), 1))
            t = (x + y) / 2
            rows += bytes(round(a + (b - a) * t + (255 - a - (b - a) * t) * fg) for a, b in zip(c1, c2))
            rows.append(round(255 * bg))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(bytes(rows))) + chunk(b"IEND", b""))


def set_icon(root):
    """Use the app's own icon for the window and taskbar instead of Python's."""
    try:
        root.icons = [tk.PhotoImage(master=root, data=base64.b64encode(icon_png(s)))
                      for s in (256, 64, 48, 32, 16)]
        root.iconphoto(True, *root.icons)
    except tk.TclError:
        pass  # Tk older than 8.6 can't read PNG


if IS_WIN:
    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD), ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT), ("dwFlags", wintypes.DWORD)]

    user32 = ctypes.WinDLL("user32")
    user32.GetParent.restype = wintypes.HWND
    user32.GetParent.argtypes = [wintypes.HWND]
    user32.MonitorFromWindow.restype = ctypes.c_void_p
    user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
    user32.GetMonitorInfoW.argtypes = [ctypes.c_void_p, ctypes.POINTER(MONITORINFO)]

    def hwnd_of(root):
        return user32.GetParent(root.winfo_id())


def window_dpi(root):
    """DPI of the monitor the window is on. macOS scales Retina screens itself, so it is always 96 there."""
    if IS_MAC:
        return 96
    if IS_WIN:
        try:
            dpi = user32.GetDpiForWindow(hwnd_of(root))
            if dpi:
                return dpi
        except Exception:
            pass
    return max(96, round(root.winfo_fpixels("1i")))


def work_area(root):
    """(left, top, right, bottom) of the usable area of the window's monitor (without the taskbar/dock)."""
    if IS_WIN:
        info = MONITORINFO()
        info.cbSize = ctypes.sizeof(info)
        mon = user32.MonitorFromWindow(hwnd_of(root), 1)  # nearest monitor
        if mon and user32.GetMonitorInfoW(mon, ctypes.byref(info)):
            r = info.rcWork
            return r.left, r.top, r.right, r.bottom
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    if IS_MAC:
        return 0, 25, w, h - 70  # menu bar and dock
    return 0, 0, w, h - px(40)  # panels


def fit_window(root, w, h, cx=None, cy=None):
    """Size the window and center it on (cx, cy), or on the work area, keeping it inside the work area."""
    left, top, right, bottom = work_area(root)
    frame = px(32)  # title bar and borders, which Tk's geometry leaves out
    w = min(w, right - left - px(24))
    h = min(h, bottom - top - frame - px(16))
    root.minsize(min(px(900), w), min(px(620), h))
    if not IS_WIN and not IS_MAC:
        # With several monitors the X screen spans them all, so centering on it could put the window
        # across two monitors. Let the window manager place it.
        root.geometry(f"{w}x{h}")
        return
    cx = (left + right) // 2 if cx is None else cx
    cy = (top + bottom) // 2 if cy is None else cy
    x = min(max(left, cx - w // 2), right - w)
    y = min(max(top, cy - (h + frame) // 2), bottom - h - frame)
    root.geometry(f"{w}x{h}+{x}+{y}")
