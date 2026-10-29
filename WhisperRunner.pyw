#!/usr/bin/env python3
"""Whisper Runner: transcribe an audio file with OpenAI Whisper and watch it happen.

Windows: double-click to run. macOS and Linux: python3 WhisperRunner.pyw. MIT license.
"""

import base64
import codecs
import ctypes
import datetime as dt
import functools
import hashlib
import importlib.util
import json
import math
import os
import platform
import queue
import re
import shutil
import signal
import struct
import subprocess
import sys
import threading
import time
import tkinter as tk
import tkinter.font as tkfont
import urllib.request
import wave
import zlib
from importlib import metadata
from tkinter import filedialog, messagebox

# Optional: dropping files on the window needs the tkinterdnd2 package (Tkinter can't do it alone).
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    TkinterDnD = None
DND = False  # set in main() once the tkdnd library has loaded

IS_WIN = sys.platform == "win32"
IS_MAC = sys.platform == "darwin"

if IS_WIN:
    import winreg
    from ctypes import wintypes

    # Without its own app ID the taskbar groups the window under pythonw.exe and shows Python's icon.
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WhisperRunner")
    except Exception:
        pass

    # Per-monitor DPI awareness has to be set before any window exists.
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))  # per-monitor v2
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

if IS_MAC:
    # Apps started from Finder don't get the shell's PATH, so Homebrew's ffmpeg wouldn't be found.
    for extra in ("/opt/homebrew/bin", "/usr/local/bin"):
        if os.path.isdir(extra) and extra not in os.environ.get("PATH", "").split(os.pathsep):
            os.environ["PATH"] = os.environ.get("PATH", "") + os.pathsep + extra

BG = "#1E1F31"
PANEL = "#2A2C43"
CARD = "#33354F"
ACCENT = "#5C7CFA"
PURPLE = "#8B6CF6"
GREEN = "#3DD68C"
ORANGE = "#F5A524"
RED = "#F2546B"
MUTED = "#8C90B5"
TEXT = "#ECEDF7"

NO_WINDOW = subprocess.CREATE_NO_WINDOW if IS_WIN else 0

# Windows: python.exe next to the running pythonw.exe, so Whisper runs without a console.
PY = sys.executable
if IS_WIN and os.path.isfile(os.path.join(os.path.dirname(sys.executable), "python.exe")):
    PY = os.path.join(os.path.dirname(sys.executable), "python.exe")

# How the copy-to-clipboard commands call pip.
PIP = "python -m pip" if IS_WIN else "python3 -m pip"

MODELS = ["tiny", "base", "small", "medium", "turbo", "large-v3"]
# File in Whisper's cache and its size in bytes (tiny and turbo approximate).
MODEL_FILES = {"tiny": ("tiny.pt", 75_572_083), "base": ("base.pt", 145_262_807),
               "small": ("small.pt", 483_617_219), "medium": ("medium.pt", 1_528_008_539),
               "turbo": ("large-v3-turbo.pt", 1_617_000_000), "large-v3": ("large-v3.pt", 3_087_371_615)}
LANGS = [("Auto", None), ("English", "en"), ("Norwegian", "no"), ("Swedish", "sv"),
         ("Danish", "da"), ("German", "de"), ("More \u25BE", None)]
MORE_LANGS = [("Arabic", "ar"), ("Chinese", "zh"), ("Dutch", "nl"), ("Finnish", "fi"),
              ("French", "fr"), ("Hindi", "hi"), ("Italian", "it"), ("Japanese", "ja"),
              ("Korean", "ko"), ("Persian", "fa"), ("Polish", "pl"), ("Portuguese", "pt"),
              ("Russian", "ru"), ("Spanish", "es"), ("Turkish", "tr"), ("Ukrainian", "uk")]

# Samsung, iPhone and common formats.
AUDIO_EXTS = [".m4a", ".3ga", ".amr", ".3gp", ".qta", ".mov", ".mp3", ".wav", ".flac", ".ogg",
              ".opus", ".wma", ".aiff", ".aif", ".m4b", ".webm", ".mkv", ".mp4"]

# CUDA build suggested when torch is CPU-only but an NVIDIA card is present.
CUDA_INDEX = "cu128"

SEG_RE = re.compile(r"^\[((?:\d+:)?\d+:\d+\.\d+) --> ((?:\d+:)?\d+:\d+\.\d+)\]\s*(.*)$")
TQDM_RE = re.compile(r"^\s*(\d+)%\|")

SCALE = 1.0
FONT = {}


def px(n):
    return int(round(n * SCALE))


# ---------------------------------------------------------------- helpers

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


def fmt_clock(sec):
    sec = max(0, int(round(sec)))
    h, rest = divmod(sec, 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def ts_seconds(s):
    total = 0.0
    for part in s.split(":"):
        total = total * 60 + float(part)
    return total


def vtuple(s):
    return tuple(int(x) for x in re.findall(r"\d+", s.split("+")[0])[:4])


def run_quiet(args, timeout=20):
    try:
        r = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           creationflags=NO_WINDOW, timeout=timeout, stdin=subprocess.DEVNULL)
        return r.stdout
    except Exception:
        return ""


def fetch(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": "WhisperRunner"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def fetch_json(url):
    try:
        return json.loads(fetch(url))
    except Exception:
        return None


def pypi_latest(name):
    data = fetch_json(f"https://pypi.org/pypi/{name}/json")
    return data["info"]["version"] if data else None


def installed(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def audio_duration(path):
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        out = run_quiet([ffprobe, "-v", "error", "-show_entries", "format=duration",
                         "-of", "default=noprint_wrappers=1:nokey=1", path])
        try:
            return float(out.strip().splitlines()[0])
        except (ValueError, IndexError):
            pass
    if path.lower().endswith(".wav"):
        try:
            with wave.open(path) as w:
                return w.getnframes() / w.getframerate()
        except Exception:
            pass
    return None


def whisper_cache():
    """Folder where Whisper keeps downloaded models (same rule as whisper itself)."""
    default = os.path.join(os.path.expanduser("~"), ".cache")
    return os.path.join(os.getenv("XDG_CACHE_HOME", default), "whisper")


def model_downloaded(model):
    """True if the model file is in the cache and complete. An interrupted download leaves a smaller file."""
    name, size = MODEL_FILES[model]
    try:
        return os.path.getsize(os.path.join(whisper_cache(), name)) >= size * 0.97
    except OSError:
        return False


def model_url(model):
    """Download URL of a model, read from the installed whisper package without importing it (that would
    load torch). The SHA-256 of the file is the second-to-last part of the URL."""
    name = MODEL_FILES[model][0]
    try:
        spec = importlib.util.find_spec("whisper")
        with open(spec.origin, encoding="utf-8") as f:
            for url in re.findall(r'"(https://[^"]+\.pt)"', f.read()):
                if url.rsplit("/", 1)[1] == name:
                    return url
    except (OSError, AttributeError, ImportError, ValueError):
        pass
    return None


class DownloadCancelled(Exception):
    pass


def download_model(model, progress, cancelled):
    """Download a model into Whisper's cache and check its SHA-256. Calls progress(done, total) as it goes."""
    url = model_url(model)
    if not url:
        raise RuntimeError("Couldn't find the download link. Is openai-whisper installed?")
    sha = url.rsplit("/", 2)[1]
    folder = whisper_cache()
    os.makedirs(folder, exist_ok=True)
    dest = os.path.join(folder, MODEL_FILES[model][0])
    part = dest + ".part"
    digest = hashlib.sha256()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "WhisperRunner"})
        with urllib.request.urlopen(req, timeout=30) as r, open(part, "wb") as f:
            total = int(r.headers.get("Content-Length") or MODEL_FILES[model][1])
            done = 0
            while True:
                if cancelled():
                    raise DownloadCancelled()
                chunk = r.read(1024 * 1024)
                if not chunk:
                    break
                f.write(chunk)
                digest.update(chunk)
                done += len(chunk)
                progress(done, total)
        if digest.hexdigest() != sha:
            raise RuntimeError("The downloaded file is damaged (checksum mismatch). Please try again.")
        os.replace(part, dest)
    finally:
        if os.path.exists(part):
            os.remove(part)


def free_space(path):
    """Free bytes on the drive holding `path`, which may not exist yet."""
    while path and not os.path.isdir(path):
        parent = os.path.dirname(path)
        if parent == path:
            break
        path = parent
    try:
        return shutil.disk_usage(path).free
    except OSError:
        return None


def fmt_size(n):
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024


# ---------------------------------------------------------------- platform specifics

def popen_options():
    """No console window on Windows; on macOS/Linux a process group so cancel can stop it all."""
    return {"creationflags": NO_WINDOW} if IS_WIN else {"start_new_session": True}


def kill_tree(pid):
    """Stop a process and everything it started."""
    if IS_WIN:
        run_quiet(["taskkill", "/T", "/F", "/PID", str(pid)], timeout=10)
    else:
        try:
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        except (ProcessLookupError, PermissionError):
            pass


def suspend_tree(pid, pause):
    """Freeze (pause=True) or continue a process; on macOS/Linux its whole process group.
    Returns False if the process couldn't be reached."""
    if IS_WIN:
        k32, ntdll = ctypes.WinDLL("kernel32"), ctypes.WinDLL("ntdll")
        k32.OpenProcess.restype = wintypes.HANDLE
        k32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
        handle = k32.OpenProcess(0x0800, False, pid)  # PROCESS_SUSPEND_RESUME
        if not handle:
            return False
        try:
            call = ntdll.NtSuspendProcess if pause else ntdll.NtResumeProcess
            call.argtypes = (wintypes.HANDLE,)
            return call(handle) == 0
        finally:
            k32.CloseHandle(wintypes.HANDLE(handle))
    try:
        os.killpg(os.getpgid(pid), signal.SIGSTOP if pause else signal.SIGCONT)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def reveal_file(path):
    """Show a file in the file manager."""
    if IS_WIN:
        subprocess.Popen(f'explorer /select,"{path}"')
    elif IS_MAC:
        subprocess.Popen(["open", "-R", path])
    else:
        subprocess.Popen(["xdg-open", os.path.dirname(path)])


MAC_NAMES = {11: "Big Sur", 12: "Monterey", 13: "Ventura", 14: "Sonoma", 15: "Sequoia", 26: "Tahoe"}
LINUX_TOOLS = {"apt": "sudo apt install", "dnf": "sudo dnf install", "pacman": "sudo pacman -S",
               "zypper": "sudo zypper install"}


@functools.lru_cache(maxsize=None)
def os_release():
    """Fields of /etc/os-release on Linux (ID, ID_LIKE, PRETTY_NAME, ...)."""
    data = {}
    try:
        with open("/etc/os-release", encoding="utf-8", errors="replace") as f:
            for line in f:
                key, _, value = line.strip().partition("=")
                if key:
                    data[key] = value.strip().strip('"')
    except OSError:
        pass
    return data


@functools.lru_cache(maxsize=None)
def os_name():
    """Readable name of the operating system, e.g. "Windows 11 Pro 24H2" or "Ubuntu 24.04.1 LTS"."""
    if IS_WIN:
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as k:
                def value(name):
                    try:
                        return str(winreg.QueryValueEx(k, name)[0]).strip()
                    except OSError:
                        return ""
                product, release, build = value("ProductName"), value("DisplayVersion"), value("CurrentBuild")
            if build.isdigit() and int(build) >= 22000:
                product = product.replace("Windows 10", "Windows 11")  # Windows 11 still says 10 here
            return f"{product} {release}".strip() or "Windows"
        except OSError:
            return f"Windows {platform.release()}"
    if IS_MAC:
        version = platform.mac_ver()[0]
        major = int(version.split(".")[0]) if version.split(".")[0].isdigit() else 0
        chip = "Apple silicon" if platform.machine() == "arm64" else "Intel"
        return f"macOS {version} {MAC_NAMES.get(major, '')}".strip() + f" ({chip})"
    return os_release().get("PRETTY_NAME") or f"Linux {platform.release()}"


def linux_package_tool():
    """apt, dnf, pacman or zypper, chosen from the distribution family in /etc/os-release."""
    rel = os_release()
    ids = f"{rel.get('ID', '')} {rel.get('ID_LIKE', '')}".lower().split()
    families = (("apt", ("debian", "ubuntu", "linuxmint", "pop")),
                ("dnf", ("fedora", "rhel", "centos", "rocky", "almalinux")),
                ("pacman", ("arch", "manjaro", "endeavouros")),
                ("zypper", ("suse", "opensuse")))
    for tool, names in families:
        if any(i == n or i.startswith(n + "-") for i in ids for n in names):
            return tool
    return next((tool for tool in LINUX_TOOLS if shutil.which(tool)), None)


def linux_install(package):
    """Install command for the distribution's package manager, or None."""
    tool = linux_package_tool()
    return f"{LINUX_TOOLS[tool]} {package}" if tool else None


def torch_cpu_only(version):
    """True for a torch build without CUDA. On Windows the PyPI build is CPU-only; on Linux it has CUDA."""
    if not version:
        return False
    if "+cpu" in version:
        return True
    return IS_WIN and "+cu" not in version


# ---------------------------------------------------------------- system check

if IS_WIN:
    class MEMORYSTATUSEX(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]


def cpu_name():
    try:
        if IS_WIN:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as k:
                return winreg.QueryValueEx(k, "ProcessorNameString")[0].strip()
        if IS_MAC:
            name = run_quiet(["sysctl", "-n", "machdep.cpu.brand_string"]).strip()
            if name:
                return name
        else:
            with open("/proc/cpuinfo", encoding="utf-8", errors="replace") as f:
                for line in f:
                    if line.lower().startswith(("model name", "hardware")):
                        return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return platform.processor() or platform.machine() or "Unknown"


def ram_gb():
    try:
        if IS_WIN:
            m = MEMORYSTATUSEX()
            m.dwLength = ctypes.sizeof(m)
            if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
                return round(m.ullTotalPhys / 1024 ** 3)
        elif IS_MAC:
            return round(int(run_quiet(["sysctl", "-n", "hw.memsize"]).strip()) / 1024 ** 3)
        else:
            return round(os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024 ** 3)
    except (OSError, ValueError, AttributeError):
        pass
    return 0


def display_adapters():
    if IS_MAC:
        try:
            data = json.loads(run_quiet(["system_profiler", "SPDisplaysDataType", "-json"], timeout=30))
            return [d["sppci_model"] for d in data.get("SPDisplaysDataType", []) if d.get("sppci_model")]
        except (ValueError, AttributeError):
            return []
    if not IS_WIN:
        names = []
        for line in run_quiet(["lspci"]).splitlines():
            if re.search(r"VGA|3D controller|Display controller", line) and ": " in line:
                name = re.sub(r"\s*\(rev [^)]*\)$", "", line.split(": ", 1)[1]).strip()
                if name not in names:
                    names.append(name)
        return names
    names = []
    path = r"SYSTEM\CurrentControlSet\Control\Class\{4d36e968-e325-11ce-bfc1-08002be10318}"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as cls:
            i = 0
            while True:
                try:
                    sub = winreg.EnumKey(cls, i)
                except OSError:
                    break
                i += 1
                if not sub.isdigit():
                    continue
                try:
                    with winreg.OpenKey(cls, sub) as k:
                        name = winreg.QueryValueEx(k, "DriverDesc")[0].strip()
                except OSError:
                    continue
                if name and name not in names and not name.startswith("Microsoft"):
                    names.append(name)
    except OSError:
        pass
    return names


def nvidia_gpus():
    """[(name, memory in MiB)] from nvidia-smi."""
    exe = shutil.which("nvidia-smi")
    if not exe and IS_WIN:
        exe = r"C:\Windows\System32\nvidia-smi.exe"
    if not exe or not os.path.isfile(exe):
        return []
    out = run_quiet([exe, "--query-gpu=name,memory.total", "--format=csv,noheader,nounits"])
    gpus = []
    for line in out.splitlines():
        parts = [p.strip() for p in line.split(",")]
        if len(parts) == 2 and parts[1].isdigit():
            gpus.append((parts[0], int(parts[1])))
    return gpus


def recommend_model(cuda, vram_gb, ram, threads):
    if cuda and vram_gb:
        if vram_gb >= 11:
            return "large-v3"
        if vram_gb >= 6:
            return "turbo"
        if vram_gb >= 5:
            return "medium"
        if vram_gb >= 2:
            return "small"
        return "base"
    if ram >= 16 and threads >= 8:
        return "small"
    if ram >= 8:
        return "base"
    return "tiny"


# ---------------------------------------------------------------- canvas widgets

class Card(tk.Canvas):
    """Rounded rectangle with a frame (`inner`) on top for content."""

    def __init__(self, parent, fill, radius=14, pad=16, **kw):
        super().__init__(parent, bg=parent["bg"], highlightthickness=0, bd=0,
                         width=px(40), height=px(40), **kw)
        self.fill, self.r, self.outline = fill, px(radius), None
        self.inner = tk.Frame(self, bg=fill)
        self.inner.grid(row=0, column=0, sticky="nsew", padx=px(pad), pady=px(pad))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.bind("<Configure>", self._draw)

    def _draw(self, _e=None):
        self.delete("bg")
        w, h = self.winfo_width(), self.winfo_height()
        if self.outline:
            inset = px(1)
            round_rect(self, inset, inset, w - 1 - inset, h - 1 - inset, self.r, fill=self.fill,
                       outline=self.outline, width=px(2), tags="bg")
        else:
            round_rect(self, 0, 0, w - 1, h - 1, self.r, fill=self.fill, outline=self.fill, tags="bg")
        self.tag_lower("bg")

    def set_outline(self, color):
        """Highlight the card with a colored border, or remove it with None."""
        self.outline = color
        self._draw()


class Button(tk.Canvas):
    def __init__(self, parent, text, command, color=ACCENT, style="fill", height=38, padx=20,
                 width=None):
        self.font = FONT["btn"]
        w = px(width) if width else tkfont.Font(font=self.font).measure(text) + px(padx) * 2
        super().__init__(parent, width=w, height=px(height), bg=parent["bg"],
                         highlightthickness=0, bd=0, cursor="hand2")
        self.text, self.command, self.color, self.style = text, command, color, style
        self.enabled, self.hover = True, False
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Enter>", lambda e: self._hover(True))
        self.bind("<Leave>", lambda e: self._hover(False))
        self.bind("<ButtonRelease-1>", self._click)

    def _hover(self, h):
        self.hover = h
        self.draw()

    def _click(self, e):
        if self.enabled and 0 <= e.x < self.winfo_width() and 0 <= e.y < self.winfo_height():
            self.command()

    def set_enabled(self, on):
        self.enabled = on
        self.config(cursor="hand2" if on else "arrow")
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        bg = self["bg"]
        hot = self.hover and self.enabled
        if self.style == "fill":
            fill = mix(self.color, "#FFFFFF", 0.12) if hot else self.color
            outline, tc = fill, "#FFFFFF"
        elif self.style == "outline":
            fill = mix(self.color, bg, 0.72 if hot else 0.86)
            outline, tc = mix(self.color, bg, 0.35), self.color
        else:  # ghost
            fill = mix(CARD, "#FFFFFF", 0.08) if hot else CARD
            outline, tc = fill, TEXT
        if not self.enabled:
            fill, outline, tc = mix(fill, bg, 0.6), mix(outline, bg, 0.6), mix(tc, bg, 0.55)
        round_rect(self, 1, 1, w - 2, h - 2, px(10), fill=fill, outline=outline)
        self.create_text(w / 2, h / 2, text=self.text, fill=tc, font=self.font)


class Tabs(tk.Canvas):
    """Segmented control. `command(index, value)` returning False keeps the old selection."""

    def __init__(self, parent, options, command=None, height=34, track=CARD):
        super().__init__(parent, width=px(200), height=px(height), bg=parent["bg"],
                         highlightthickness=0, bd=0, cursor="hand2")
        self.options, self.command, self.track = list(options), command, track
        self.sel, self.hover, self.enabled = 0, -1, True
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Motion>", self._motion)
        self.bind("<Leave>", lambda e: self._set_hover(-1))
        self.bind("<Button-1>", self._click)

    @property
    def value(self):
        return self.options[self.sel][1]

    def _index(self, x):
        n = len(self.options)
        return max(0, min(n - 1, int(x / max(1, self.winfo_width()) * n)))

    def _set_hover(self, i):
        if i != self.hover:
            self.hover = i
            self.draw()

    def _motion(self, e):
        self._set_hover(self._index(e.x))

    def _click(self, e):
        if not self.enabled:
            return
        i = self._index(e.x)
        if self.command and self.command(i, self.options[i][1]) is False:
            return
        self.select(i)

    def segment_x(self, i):
        return int(self.winfo_width() / len(self.options) * i)

    def select(self, i):
        self.sel = i
        self.draw()

    def set_value(self, v):
        for i, (_, val) in enumerate(self.options):
            if val == v:
                self.select(i)
                return

    def set_option(self, i, label, value):
        self.options[i] = (label, value)
        self.draw()

    def set_enabled(self, on):
        self.enabled = on
        self.config(cursor="hand2" if on else "arrow")
        self.draw()

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 10:
            return
        pad = px(3)
        round_rect(self, 0, 0, w - 1, h - 1, px(10), fill=self.track, outline=self.track)
        sw = (w - 2 * pad) / len(self.options)
        for i, (label, _) in enumerate(self.options):
            x1 = pad + i * sw
            x2 = x1 + sw
            if i == self.sel:
                fill = ACCENT if self.enabled else mix(ACCENT, self.track, 0.55)
                round_rect(self, x1, pad, x2, h - pad - 1, px(8), fill=fill, outline=fill)
                tc = "#FFFFFF" if self.enabled else mix("#FFFFFF", self.track, 0.4)
            else:
                tc = TEXT if (i == self.hover and self.enabled) else MUTED
            self.create_text((x1 + x2) / 2, h / 2, text=label, fill=tc, font=FONT["tab"])


class Progress(tk.Canvas):
    """Progress bar. While active it glides to new values, a shine sweeps across the fill, and
    before there is any progress a short segment slides along the track."""

    FRAME_MS = 16
    SHINE_PERIOD = 1.8   # seconds per sweep
    SLIDE_PERIOD = 1.3

    def __init__(self, parent, height=10):
        super().__init__(parent, width=px(100), height=px(height), bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.value, self.shown, self.color = 0.0, 0.0, ACCENT
        self.active, self.job, self.t0 = False, None, time.time()
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Destroy>", lambda e: self._cancel() if e.widget is self else None)

    def set(self, value, color=None):
        self.value = max(0.0, min(1.0, value))
        if color:
            self.color = color
        if self.value < self.shown or not self.winfo_ismapped():
            self.shown = self.value  # going back (new run) or not visible: no glide
        self._run()

    def start(self):
        self.active, self.t0 = True, time.time()
        self._run()

    def stop(self):
        self.active = False
        self._run()

    def _cancel(self):
        if self.job:
            self.after_cancel(self.job)
            self.job = None

    def _run(self):
        if not self.job:
            self._frame()

    def _frame(self):
        self.job = None
        diff = self.value - self.shown
        self.shown = self.value if abs(diff) < 0.0015 else self.shown + diff * 0.12
        self.draw()
        if self.active or self.shown != self.value:
            self.job = self.after(self.FRAME_MS, self._frame)

    def draw(self):
        self.delete("all")
        w, h = self.winfo_width(), self.winfo_height()
        if w < 4:
            return
        r = h / 2
        round_rect(self, 0, 0, w - 1, h - 1, r, fill=CARD, outline=CARD)
        t = time.time() - self.t0
        if self.shown > 0:
            fw = max(h, (w - 1) * self.shown)
            round_rect(self, 0, 0, fw, h - 1, r, fill=self.color, outline=self.color)
            if self.active and fw > 3 * h:
                self._shine(fw, h, t)
        elif self.active:
            seg = w * 0.22
            x = ((t / self.SLIDE_PERIOD) % 1) * (w + seg) - seg
            x1, x2 = max(0, x), min(w - 1, x + seg)
            if x2 - x1 > 2:
                fill = mix(self.color, CARD, 0.25)
                round_rect(self, x1, 0, x2, h - 1, r, fill=fill, outline=fill)

    def _shine(self, fw, h, t):
        """Soft light band moving left to right, kept inside the straight part of the fill."""
        band = max(h * 4, fw * 0.18)
        center = ((t / self.SHINE_PERIOD) % 1) * (fw + band) - band / 2
        left, right = h / 2, fw - h / 2
        strips = 14
        sw = band / strips
        for i in range(strips):
            x1 = center - band / 2 + i * sw
            x2 = x1 + sw + 1
            x1, x2 = max(left, x1), min(right, x2)
            if x2 <= x1:
                continue
            k = 1 - abs((i + 0.5) / strips * 2 - 1)  # 0 at the edges, 1 in the middle
            c = mix(self.color, "#FFFFFF", 0.32 * k * k)
            self.create_rectangle(x1, 0, x2, h - 1, fill=c, outline="")


class Badge(tk.Canvas):
    def __init__(self, parent, text="", color=MUTED):
        super().__init__(parent, height=px(22), width=px(20), bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.set(text, color)

    def set(self, text, color):
        self.text, self.color = text, color
        w = tkfont.Font(font=FONT["badge"]).measure(text) + px(18)
        self.config(width=w)
        self.delete("all")
        h = px(22)
        fill = mix(color, self["bg"], 0.8)
        round_rect(self, 0, 0, w - 1, h - 1, h / 2, fill=fill, outline=fill)
        self.create_text(w / 2, h / 2, text=text, fill=color, font=FONT["badge"])


class ScrollBar(tk.Canvas):
    def __init__(self, parent, command):
        super().__init__(parent, width=px(10), height=px(40), bg=parent["bg"],
                         highlightthickness=0, bd=0)
        self.command, self.first, self.last, self.drag = command, 0.0, 1.0, None
        self.bind("<Configure>", lambda e: self.draw())
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._motion)

    def set(self, first, last):
        self.first, self.last = float(first), float(last)
        self.draw()

    def draw(self):
        self.delete("all")
        if self.last - self.first >= 1:
            return
        w, h = self.winfo_width(), self.winfo_height()
        y1 = self.first * h
        y2 = max(self.last * h, y1 + px(24))
        color = mix(MUTED, self["bg"], 0.45)
        round_rect(self, px(2), y1, w - px(2), y2, (w - px(4)) / 2, fill=color, outline=color)

    def _press(self, e):
        h = max(1, self.winfo_height())
        y = e.y / h
        first = self.first
        if not self.first <= y <= self.last:
            first = max(0.0, y - (self.last - self.first) / 2)
            self.command("moveto", first)
        self.drag = (e.y, first)

    def _motion(self, e):
        if self.drag:
            y0, f0 = self.drag
            self.command("moveto", f0 + (e.y - y0) / max(1, self.winfo_height()))


class ScrollArea(tk.Frame):
    """Vertically scrolling frame (`inner`); the scrollbar only shows when the content overflows."""

    def __init__(self, parent):
        bg = parent["bg"]
        super().__init__(parent, bg=bg)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0, width=px(40), height=px(40),
                                yscrollincrement=px(16))
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.sb = ScrollBar(self, self.canvas.yview)
        self.sb.grid(row=0, column=1, sticky="ns", padx=(px(6), 0))
        self.sb.grid_remove()
        self.canvas.config(yscrollcommand=self._set)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self.win = self.canvas.create_window(0, 0, window=self.inner, anchor="nw")
        self.inner.bind("<Configure>", lambda e: self.canvas.config(scrollregion=(0, 0, e.width, e.height)))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(self.win, width=e.width))

    def _set(self, first, last):
        if float(last) - float(first) >= 1:
            self.sb.grid_remove()
            if float(first) != 0:  # content fits: keep it pinned to the top
                self.canvas.yview_moveto(0)
        else:
            self.sb.grid()
        self.sb.set(first, last)

    def wheel(self, e, units=None):
        """Scroll on a wheel event over this area. Windows sends steps of 120, macOS small steps,
        and Linux Button-4/5 events (passed with `units`)."""
        first, last = self.canvas.yview()
        if last - first >= 1:  # nothing to scroll; Tk would otherwise shift the content into empty space
            return
        if units is None:
            units = -e.delta if IS_MAC else -3 * int(e.delta / 120)
        w = self.winfo_containing(e.x_root, e.y_root)
        while w is not None:
            if w is self:
                self.canvas.yview_scroll(units, "units")
                return
            w = w.master

    def see(self, widget):
        """Scroll so `widget` is visible, showing its top if it is taller than the view."""
        self.update_idletasks()
        total = max(1, self.inner.winfo_height())
        view = self.canvas.winfo_height()
        top = self.canvas.canvasy(0)
        y1 = widget.winfo_rooty() - self.inner.winfo_rooty()
        y2 = y1 + widget.winfo_height()
        new_top = top
        if y2 > top + view:
            new_top = y2 - view
        new_top = min(new_top, y1)
        if new_top != top:
            self.canvas.yview_moveto(new_top / total)


class Accordion(Card):
    def __init__(self, parent, title, group, on_open=None):
        super().__init__(parent, CARD, radius=14, pad=14)
        self.group, self.is_open, self.on_open = group, False, on_open
        group.append(self)
        inner = self.inner
        inner.grid_columnconfigure(0, weight=1)
        self.header = tk.Frame(inner, bg=CARD, cursor="hand2")
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_columnconfigure(1, weight=1)
        tk.Label(self.header, text=title, font=FONT["h"], fg=TEXT, bg=CARD).grid(row=0, column=0, sticky="w")
        self.summary = tk.Label(self.header, text="Checking\u2026", font=FONT["small"], fg=MUTED, bg=CARD)
        self.summary.grid(row=0, column=1, sticky="e", padx=(px(8), px(8)))
        self.chevron = tk.Label(self.header, text="\u25B8", font=FONT["h"], fg=MUTED, bg=CARD)
        self.chevron.grid(row=0, column=2, sticky="e")
        for w in (self.header, *self.header.winfo_children()):
            w.bind("<Button-1>", lambda e: self.toggle())
            w.config(cursor="hand2")
        self.body = tk.Frame(inner, bg=CARD)
        self.body.grid(row=1, column=0, sticky="nsew", pady=(px(12), 0))
        self.body.grid_columnconfigure(0, weight=1)
        self.body.grid_remove()

    def toggle(self):
        opening = not self.is_open
        for a in self.group:
            a.set_open(a is self and opening)
        if opening and self.on_open:
            self.after_idle(self.on_open, self)

    def set_open(self, on):
        self.is_open = on
        if on:
            self.body.grid()
            self.summary.grid_remove()
        else:
            self.body.grid_remove()
            self.summary.grid()
        self.chevron.config(text="\u25BE" if on else "\u25B8")

    def set_summary(self, text, color=MUTED):
        self.summary.config(text=text, fg=color)


def label(parent, text="", font="body", fg=TEXT, **kw):
    return tk.Label(parent, text=text, font=FONT[font], fg=fg, bg=parent["bg"], **kw)


def autowrap(lbl, inset=0):
    """Wrap a label's text to whatever width the layout gives it."""
    lbl.config(wraplength=px(160))
    lbl.bind("<Configure>", lambda e: lbl.config(wraplength=max(px(80), e.width - inset)), add="+")
    return lbl


def clear(frame):
    for w in frame.winfo_children():
        w.destroy()


# ---------------------------------------------------------------- app

class App:
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()
        self.file = None
        self.duration = None
        self.proc = None
        self.running = False
        self.cancelled = False
        self.paused_at = None  # time.time() when paused, else None
        self.start_time = 0.0
        self.end_time = 0.0
        self.processed = 0.0
        self.user_model = False
        self.lang = None
        self.out_path = None
        self.transcript_empty = True
        self.cuda = None
        self.sys_info = None
        self.req_items = None
        self.dpi = round(SCALE * 96)
        self.dpi_job = None
        self.logical_size = None
        self.downloading = None  # model being downloaded
        self.dl_cancel = False

        root.title("Whisper Runner")
        root.configure(bg=BG)
        self._build()
        root.bind_all("<MouseWheel>", lambda e: self.area.wheel(e))
        root.bind_all("<Button-4>", lambda e: self.area.wheel(e, -3))
        root.bind_all("<Button-5>", lambda e: self.area.wheel(e, 3))

        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._poll()
        threading.Thread(target=self.system_check, daemon=True).start()
        threading.Thread(target=self.requirements_check, daemon=True).start()
        if len(sys.argv) > 1:
            root.after(100, lambda: self.set_file(sys.argv[1]))

    # ---- layout

    def _build(self):
        self.outer = outer = tk.Frame(self.root, bg=BG)
        outer.pack(fill="both", expand=True, padx=px(18), pady=px(18))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, minsize=px(380))
        outer.grid_rowconfigure(0, weight=1)

        left = Card(outer, PANEL, radius=18, pad=22)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, px(16)))
        right = Card(outer, PANEL, radius=18, pad=20)
        right.grid(row=0, column=1, sticky="nsew")
        self._build_left(left.inner)
        self._build_right(right.inner)
        if DND:
            self._enable_drop(outer)

    # ---- dropping files on the window (only with tkinterdnd2)

    def _enable_drop(self, target):
        # Drops on any widget inside `target` reach it; the root window itself can't be registered.
        self.drag_saved = None
        target.drop_target_register(DND_FILES)
        target.dnd_bind("<<DropEnter>>", self._drag_enter)
        target.dnd_bind("<<DropPosition>>", lambda e: "refuse_drop" if self.running else e.action)
        target.dnd_bind("<<DropLeave>>", self._drag_leave)
        target.dnd_bind("<<Drop>>", self._drop)

    def _drag_enter(self, e):
        if self.busy:
            return "refuse_drop"
        if not self.drag_saved:
            self.drag_saved = (self.file_name["text"], self.file_info["text"], self.file_info["fg"])
        self.file_card.set_outline(ACCENT)
        self.file_name.config(text="Drop to open this file")
        self.file_info.config(text="Release the mouse button to choose it.", fg=MUTED)
        return e.action

    def _drag_leave(self, e):
        self._end_drag()
        return e.action

    def _end_drag(self):
        self.file_card.set_outline(None)
        if self.drag_saved:
            name, info, fg = self.drag_saved
            self.file_name.config(text=name)
            self.file_info.config(text=info, fg=fg)
            self.drag_saved = None

    def _drop(self, e):
        self._end_drag()
        if self.busy:
            return "refuse_drop"
        files = self.root.tk.splitlist(e.data)
        if files:
            self.set_file(files[0])  # several files: the first one
        return e.action

    # ---- moving between monitors with different DPI

    def watch_dpi(self):
        # Tk doesn't rescale when the window moves to a monitor with another DPI, so check after
        # each move or resize settles and rebuild the UI at the new scale.
        self.root.bind("<Configure>", self._on_configure)
        self.root.after(300, self._check_dpi)

    def _on_configure(self, e):
        if e.widget is self.root:
            if self.dpi_job:
                self.root.after_cancel(self.dpi_job)
            self.dpi_job = self.root.after(300, self._check_dpi)

    def _check_dpi(self):
        self.dpi_job = None
        root = self.root
        dpi = window_dpi(root)
        if dpi == self.dpi:
            # Remember the size in 96-DPI units while the window sits on one monitor. When it is
            # dragged to another, Windows may already have resized it, so the size seen after
            # the move can't be trusted.
            self.logical_size = (root.winfo_width() / SCALE, root.winfo_height() / SCALE)
            return
        self.dpi = dpi
        cx = root.winfo_rootx() + root.winfo_width() // 2
        cy = root.winfo_rooty() + root.winfo_height() // 2
        state = self._snapshot()
        set_dpi(root, dpi)
        self.outer.destroy()
        self._build()
        self._restore(state)
        if root.state() != "zoomed":
            lw, lh = self.logical_size or (1180, 820)
            fit_window(root, px(lw), px(lh), cx, cy)

    def _snapshot(self):
        s = {name: (getattr(self, name)["text"], getattr(self, name)["fg"])
             for name in ("file_name", "file_info", "percent", "status", "detail")}
        s["stats"] = {k: v["text"] for k, v in self.stats.items()}
        s["bar"] = (self.bar.value, self.bar.color)
        s["model"] = self.model_tabs.sel
        s["lang"] = (list(self.lang_tabs.options), self.lang_tabs.sel)
        s["view"] = self.view_tabs.sel
        s["texts"] = [self._dump(self.transcript), self._dump(self.log)]
        s["open"] = self.sys_acc.is_open, self.req_acc.is_open
        return s

    def _restore(self, s):
        if self.sys_info:
            self.show_system(self.sys_info)
        if self.req_items:
            self.show_requirements(self.req_items)
        for name in ("file_name", "file_info", "percent", "status", "detail"):
            text, fg = s[name]
            getattr(self, name).config(text=text, fg=fg)
        for k, text in s["stats"].items():
            self.stats[k].config(text=text)
        self.bar.set(*s["bar"])
        if self.busy:
            self.bar.start()
        self.model_tabs.select(s["model"])
        self.lang_tabs.options, sel = s["lang"]
        self.lang_tabs.select(sel)
        self.view_tabs.select(s["view"])
        self.on_view(s["view"], "t" if s["view"] == 0 else "l")
        self._load(self.transcript, s["texts"][0])
        self._load(self.log, s["texts"][1])
        self.sys_acc.set_open(s["open"][0])
        self.req_acc.set_open(s["open"][1])
        self._update_model_note()
        self._set_inputs(not self.busy)

    @staticmethod
    def _dump(text):
        return text.get("1.0", "end-1c"), {tag: [str(i) for i in text.tag_ranges(tag)]
                                           for tag in ("muted", "ts", "err")}

    @staticmethod
    def _load(text, data):
        content, tags = data
        text.config(state="normal")
        text.delete("1.0", "end")
        text.insert("1.0", content)
        for tag, idx in tags.items():
            for a, b in zip(idx[::2], idx[1::2]):
                text.tag_add(tag, a, b)
        text.config(state="disabled")
        text.see("end")

    def _build_left(self, p):
        p.grid_columnconfigure(0, weight=1)

        head = tk.Frame(p, bg=PANEL)
        head.grid(row=0, column=0, sticky="ew")
        head.grid_columnconfigure(0, weight=1)
        label(head, "Whisper Runner", "title").grid(row=0, column=0, sticky="w")
        label(head, "Transcribe audio with OpenAI Whisper", "small", MUTED).grid(row=1, column=0, sticky="w")
        self.device_badge = Badge(head, "Checking\u2026", MUTED)
        self.device_badge.grid(row=0, column=1, rowspan=2, sticky="e")

        self.file_card = fcard = Card(p, CARD, radius=14, pad=14)
        fcard.grid(row=1, column=0, sticky="ew", pady=(px(18), 0))
        fc = fcard.inner
        fc.grid_columnconfigure(1, weight=1)
        icon = tk.Canvas(fc, width=px(44), height=px(44), bg=CARD, highlightthickness=0, bd=0)
        icon.grid(row=0, column=0, rowspan=2, padx=(0, px(12)))
        fill = mix(PURPLE, CARD, 0.7)
        round_rect(icon, 0, 0, px(43), px(43), px(10), fill=fill, outline=fill)
        icon.create_text(px(22), px(22), text="\u266A", fill=PURPLE, font=(FONT["title"][0], -px(21)))
        self.file_name = label(fc, "No file selected", "h", anchor="w")
        self.file_name.grid(row=0, column=1, sticky="ew")
        self.file_info = label(fc, "Choose a recording file, or drop one here." if DND else "Choose a recording file.",
                               "small", MUTED, anchor="w")
        self.file_info.grid(row=1, column=1, sticky="ew")
        self.choose_btn = Button(fc, "Choose file", self.choose_file, style="outline", height=34)
        self.choose_btn.grid(row=0, column=2, rowspan=2, padx=(px(12), 0))
        for w in (fcard, fc, icon, self.file_name, self.file_info):
            w.bind("<Button-1>", lambda e: self.choose_file())

        row = tk.Frame(p, bg=PANEL)
        row.grid(row=2, column=0, sticky="ew", pady=(px(18), px(8)))
        row.grid_columnconfigure(0, weight=1)
        label(row, "Model", "h").grid(row=0, column=0, sticky="w")
        self.model_note = label(row, "Checking your system\u2026", "small", MUTED)
        self.model_note.grid(row=0, column=1, sticky="e")
        model_box = tk.Frame(p, bg=PANEL)
        model_box.grid(row=3, column=0, sticky="ew")
        model_box.grid_columnconfigure(0, weight=1)
        self.model_tabs = Tabs(model_box, [(m, m) for m in MODELS], self.on_model)
        self.model_tabs.set_value("base")
        self.model_tabs.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.model_status = autowrap(label(model_box, "", "small", MUTED, anchor="w", justify="left"))
        self.model_status.grid(row=1, column=0, sticky="ew", pady=(px(6), 0))
        self.download_btn = Button(model_box, "Download", lambda: self.start_download(self.model_tabs.value),
                                   style="outline", height=28, padx=14)
        self.download_btn.grid(row=1, column=1, sticky="e", padx=(px(10), 0), pady=(px(6), 0))
        self._update_model_status()

        row = tk.Frame(p, bg=PANEL)
        row.grid(row=4, column=0, sticky="ew", pady=(px(16), px(8)))
        row.grid_columnconfigure(0, weight=1)
        label(row, "Language", "h").grid(row=0, column=0, sticky="w")
        label(row, "Auto detects from the first 30 seconds", "small", MUTED).grid(row=0, column=1, sticky="e")
        self.lang_tabs = Tabs(p, LANGS, self.on_lang)
        self.lang_tabs.grid(row=5, column=0, sticky="ew")

        actions = tk.Frame(p, bg=PANEL)
        actions.grid(row=6, column=0, sticky="ew", pady=(px(20), 0))
        self.go_btn = Button(actions, "Start transcribing", self.start, height=40, padx=24)
        self.go_btn.grid(row=0, column=0)
        self.go_btn.set_enabled(False)
        self.pause_btn = Button(actions, "Pause", self.toggle_pause, style="outline", width=110, height=40)
        self.pause_btn.grid(row=0, column=1, padx=(px(10), 0))
        self.pause_btn.set_enabled(False)
        self.cancel_btn = Button(actions, "Cancel", self.cancel, color=RED, style="outline", width=110, height=40)
        self.cancel_btn.grid(row=0, column=2, padx=(px(10), 0))
        self.cancel_btn.set_enabled(False)

        prog = tk.Frame(p, bg=PANEL)
        prog.grid(row=7, column=0, sticky="ew", pady=(px(14), px(6)))
        prog.grid_columnconfigure(1, weight=1)
        self.percent = label(prog, "0%", "big")
        self.percent.grid(row=0, column=0, rowspan=2, sticky="w")
        self.status = label(prog, "Ready", "h", anchor="w")
        self.status.grid(row=0, column=1, sticky="sew", padx=(px(16), 0))
        self.detail = label(prog, "Pick a file to start", "small", MUTED, anchor="w")
        self.detail.grid(row=1, column=1, sticky="new", padx=(px(16), 0))
        self.bar = Progress(p)
        self.bar.grid(row=8, column=0, sticky="ew")

        bar2 = tk.Frame(p, bg=PANEL)
        bar2.grid(row=9, column=0, sticky="ew", pady=(px(20), px(10)))
        bar2.grid_columnconfigure(1, weight=1)
        self.view_tabs = Tabs(bar2, [("Transcript", "t"), ("Log", "l")], self.on_view, height=32)
        self.view_tabs.config(width=px(220))
        self.view_tabs.grid(row=0, column=0, sticky="w")
        self.open_btn = Button(bar2, "Open folder", self.open_folder, style="ghost", height=32, padx=14)
        self.open_btn.grid(row=0, column=2, padx=(px(8), 0))
        self.copy_btn = Button(bar2, "Copy", self.copy_transcript, style="ghost", height=32, padx=14)
        self.copy_btn.grid(row=0, column=3, padx=(px(8), 0))
        self.open_btn.set_enabled(False)
        self.copy_btn.set_enabled(False)

        tcard = Card(p, CARD, radius=14, pad=8)
        tcard.grid(row=10, column=0, sticky="nsew")
        p.grid_rowconfigure(10, weight=1)
        self.transcript_view, self.transcript = self._text_area(tcard.inner)
        self.log_view, self.log = self._text_area(tcard.inner, mono=True)
        self.log_view.grid_remove()
        self._write(self.transcript, "The transcript appears here while Whisper works through the audio.", "muted")

    def _text_area(self, parent, mono=False):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(0, weight=1)
        frame = tk.Frame(parent, bg=CARD)
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        text = tk.Text(frame, bg=CARD, fg=TEXT, insertbackground=TEXT, relief="flat", bd=0,
                       highlightthickness=0, wrap="word", font=FONT["mono" if mono else "text"],
                       padx=px(8), pady=px(6), spacing3=px(3 if mono else 6), height=6, width=40,
                       selectbackground=ACCENT, selectforeground="#FFFFFF", state="disabled")
        text.grid(row=0, column=0, sticky="nsew")
        sb = ScrollBar(frame, text.yview)
        sb.grid(row=0, column=1, sticky="ns")
        text.config(yscrollcommand=sb.set)
        text.tag_config("muted", foreground=MUTED)
        text.tag_config("ts", foreground=mix(MUTED, CARD, 0.2), font=FONT["mono"])
        text.tag_config("err", foreground=RED)
        return frame, text

    def _build_right(self, p):
        p.grid_columnconfigure(0, weight=1)
        label(p, "Session", "title").grid(row=0, column=0, sticky="w")
        label(p, "Live stats for the current run", "small", MUTED).grid(row=1, column=0, sticky="w")

        self.area = area = ScrollArea(p)
        area.grid(row=2, column=0, sticky="nsew", pady=(px(16), 0))
        p.grid_rowconfigure(2, weight=1)
        body = area.inner
        body.grid_columnconfigure(0, weight=1)

        stats = tk.Frame(body, bg=PANEL)
        stats.grid(row=0, column=0, sticky="ew")
        stats.grid_columnconfigure((0, 1), weight=1, uniform="s")
        self.stats = {}
        items = [("elapsed", "Elapsed", ACCENT, "since start"),
                 ("left", "Time left", PURPLE, "estimate"),
                 ("finish", "Finishes at", GREEN, "local time"),
                 ("speed", "Speed", ORANGE, "audio time per second")]
        for i, (key, title, color, sub) in enumerate(items):
            c = Card(stats, CARD, radius=14, pad=14)
            c.grid(row=i // 2, column=i % 2, sticky="nsew",
                   padx=(0, px(6)) if i % 2 == 0 else (px(6), 0), pady=(0, px(12)))
            head = tk.Frame(c.inner, bg=CARD)
            head.grid(row=0, column=0, sticky="w")
            dot = tk.Canvas(head, width=px(8), height=px(8), bg=CARD, highlightthickness=0, bd=0)
            dot.create_oval(0, 0, px(8) - 1, px(8) - 1, fill=color, outline="")
            dot.grid(row=0, column=0, padx=(0, px(6)))
            label(head, title, "small", MUTED).grid(row=0, column=1)
            value = label(c.inner, "\u2014", "stat", anchor="w")
            value.grid(row=1, column=0, sticky="w", pady=(px(4), 0))
            label(c.inner, sub, "tiny", MUTED).grid(row=2, column=0, sticky="w")
            self.stats[key] = value

        group = []
        self.sys_acc = Accordion(body, "Your system", group, area.see)
        self.sys_acc.grid(row=1, column=0, sticky="ew", pady=(px(4), 0))
        self.req_acc = Accordion(body, "Requirements", group, area.see)
        self.req_acc.grid(row=2, column=0, sticky="ew", pady=(px(12), 0))
        label(self.sys_acc.body, "Checking\u2026", "small", MUTED).grid(row=0, column=0, sticky="w")
        label(self.req_acc.body, "Checking\u2026", "small", MUTED).grid(row=0, column=0, sticky="w")

    # ---- thread-safe UI calls

    def ui(self, fn, *args):
        self.q.put((fn, args))

    def _poll(self):
        try:
            while True:
                fn, args = self.q.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.root.after(50, self._poll)

    # ---- text helpers

    def _write(self, text, s, tag=None, replace=False):
        follow = text.yview()[1] >= 0.999
        text.config(state="normal")
        if replace:
            text.delete("1.0", "end")
        text.insert("end", s, tag)
        text.config(state="disabled")
        if follow or replace:
            text.see("end")

    # ---- inputs

    @property
    def busy(self):
        """Transcribing or downloading a model."""
        return self.running or bool(self.downloading)

    def on_model(self, i, value):
        if self.busy:
            return False
        self.user_model = True
        self.root.after_idle(self._update_model_note)  # after the tab is selected

    def _update_model_status(self):
        """Line under the model tabs: is the selected model already on this computer?"""
        model = self.model_tabs.value
        size = fmt_size(MODEL_FILES[model][1])
        if self.downloading:
            self.model_status.config(text=f"↓ Downloading {self.downloading}…", fg=PURPLE)
            self.download_btn.grid_remove()
        elif model_downloaded(model):
            self.model_status.config(text=f"✓ {model} is installed and ready", fg=MUTED)
            self.download_btn.grid_remove()
        else:
            self.model_status.config(text=f"{model} isn't installed yet ({size}). Click Download to "
                                          "install it (needs internet).", fg=ORANGE)
            self.download_btn.grid()

    def _update_model_note(self):
        self._update_model_status()
        suggested = (self.sys_info or {}).get("model")
        if suggested and self.model_tabs.value == suggested:
            self.model_note.config(text=f"Suggested for this PC: {suggested}", fg=MUTED)
        elif suggested:
            self.model_note.config(text=f"Selected manually · suggested for this PC: {suggested}", fg=ACCENT)
        elif self.user_model:
            self.model_note.config(text="Selected manually · checking your system…", fg=ACCENT)
        else:
            self.model_note.config(text="Checking your system…", fg=MUTED)

    def on_lang(self, i, value):
        if self.busy:
            return False
        last = len(LANGS) - 1
        if i != last:
            self.lang = value
            self.lang_tabs.set_option(last, LANGS[last][0], None)
            return None
        menu = tk.Menu(self.root, tearoff=0, bg=CARD, fg=TEXT, activebackground=ACCENT,
                       activeforeground="#FFFFFF", bd=0, font=FONT["body"])
        for name, code in MORE_LANGS:
            menu.add_command(label=name, command=lambda n=name, c=code: self._pick_more(n, c))
        x = self.lang_tabs.winfo_rootx() + self.lang_tabs.segment_x(last)
        y = self.lang_tabs.winfo_rooty() + self.lang_tabs.winfo_height()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
        return False

    def _pick_more(self, name, code):
        last = len(LANGS) - 1
        self.lang = code
        self.lang_tabs.set_option(last, f"{name} \u25BE", code)
        self.lang_tabs.select(last)

    def on_view(self, i, value):
        if value == "t":
            self.log_view.grid_remove()
            self.transcript_view.grid()
        else:
            self.transcript_view.grid_remove()
            self.log_view.grid()

    def choose_file(self):
        if self.busy:
            return
        exts = " ".join("*" + e for e in AUDIO_EXTS)
        path = filedialog.askopenfilename(
            parent=self.root, title="Choose an audio file",
            filetypes=[("Audio and video", exts), ("All files", "*.*")])
        if path:
            self.set_file(path)

    def set_file(self, path):
        path = os.path.normpath(path)
        if os.path.isdir(path):
            self.file_name.config(text=os.path.basename(path) or path)
            self.file_info.config(text="That's a folder. Choose or drop an audio file.", fg=RED)
            return
        if not os.path.isfile(path):
            self.file_name.config(text=os.path.basename(path) or "File not found")
            self.file_info.config(text="Can't open this file. Files on a phone connected by USB must be "
                                       "copied to this PC first.", fg=RED)
            return
        self.file, self.duration = path, None
        self.file_name.config(text=os.path.basename(path))
        size = fmt_size(os.path.getsize(path))
        ext = os.path.splitext(path)[1].lower()
        self.file_info.config(text=f"File size: {size} \u00B7 Duration: reading\u2026 \u00B7 Type: {ext}", fg=MUTED)
        self.go_btn.set_enabled(True)
        self.status.config(text="Ready", fg=TEXT)
        self.detail.config(text=os.path.dirname(path))
        self.percent.config(text="0%")
        self.bar.set(0, ACCENT)

        def work():
            d = audio_duration(path)
            self.ui(self._got_duration, path, d, size, ext)
        threading.Thread(target=work, daemon=True).start()

    def _got_duration(self, path, d, size, ext):
        if path != self.file:
            return
        self.duration = d
        length = fmt_clock(d) if d else "unknown"
        self.file_info.config(text=f"File size: {size} \u00B7 Duration: {length} \u00B7 Type: {ext}")

    # ---- running Whisper

    def start(self):
        if self.busy or not self.file:
            return
        model = self.model_tabs.value
        if not model_downloaded(model):
            # Never download on our own (Whisper would): tell the user and let them decide.
            messagebox.showinfo(
                "Model not installed",
                f"The {model} model isn't installed on this computer yet "
                f"({fmt_size(MODEL_FILES[model][1])}).\n\n"
                "To use it, click Download under the model list. Or choose a model that's already "
                "installed.", parent=self.root)
            return
        folder = os.path.dirname(self.file)
        cmd = [PY, "-m", "whisper", self.file, "--model", model, "--output_format", "txt",
               "--output_dir", folder]
        if self.lang:
            cmd += ["--language", self.lang]
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        self._write(self.log, subprocess.list2cmdline(cmd) + "\n\n", "muted", replace=True)
        try:
            self.proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                         stdin=subprocess.DEVNULL, env=env, cwd=folder,
                                         **popen_options())
        except OSError as e:
            self.status.config(text="Couldn't start Whisper", fg=RED)
            self.detail.config(text=str(e))
            return
        self.out_path = os.path.join(folder, os.path.splitext(os.path.basename(self.file))[0] + ".txt")
        self.running, self.cancelled, self.paused_at = True, False, None
        self.start_time, self.processed = time.time(), 0.0
        self.transcript_empty = True
        self._write(self.transcript, "Waiting for the first words\u2026", "muted", replace=True)
        for key in self.stats:
            self.stats[key].config(text="\u2014")
        self._set_inputs(False)
        self.percent.config(text="0%")
        self.status.config(text="Loading model", fg=TEXT)
        self.detail.config(text=f"{model} \u00B7 {self.lang or 'auto-detect language'}")
        self.bar.set(0, ACCENT)
        self.bar.start()
        threading.Thread(target=self._reader, args=(self.proc,), daemon=True).start()
        self._tick()

    def _enough_space(self, model):
        """Check the drive has room for the model; show an error if not."""
        need = MODEL_FILES[model][1]
        free = free_space(whisper_cache())
        if free is not None and free < need * 1.1:
            messagebox.showerror(
                "Not enough disk space",
                f"The {model} model needs {fmt_size(need)}, but only {fmt_size(free)} is free on the drive "
                f"where Whisper keeps its models:\n\n{whisper_cache()}\n\n"
                "Free up some space or choose a smaller model.", parent=self.root)
            return False
        return True

    # ---- downloading a model

    def start_download(self, model):
        if self.busy or model_downloaded(model) or not self._enough_space(model):
            return
        self.downloading, self.dl_cancel = model, False
        self.dl_started = time.time()
        self._set_inputs(False)
        self._update_model_status()
        self.percent.config(text="0%")
        self.status.config(text=f"Downloading the {model} model", fg=TEXT)
        self.detail.config(text="Connecting…")
        self.bar.set(0, PURPLE)
        self.bar.start()
        last = [0.0]

        def progress(done, total):
            now = time.time()
            if now - last[0] >= 0.15 or done >= total:
                last[0] = now
                self.ui(self._download_progress, done, total)

        def work():
            try:
                download_model(model, progress, lambda: self.dl_cancel)
                error = None
            except DownloadCancelled:
                error = "cancelled"
            except Exception as e:  # network, disk, checksum
                error = str(e) or e.__class__.__name__
            self.ui(self._download_done, model, error)
        threading.Thread(target=work, daemon=True).start()

    def _download_progress(self, done, total):
        if not self.downloading or self.dl_cancel:
            return
        p = done / total if total else 0
        speed = done / max(0.1, time.time() - self.dl_started)
        self.percent.config(text=f"{int(p * 100)}%")
        self.bar.set(p, PURPLE)
        self.detail.config(text=f"{fmt_size(done)} of {fmt_size(total)} · {fmt_size(speed)}/s")

    def _download_done(self, model, error):
        self.downloading = None
        self.bar.stop()
        self._set_inputs(True)
        self._update_model_status()
        if error is None:
            self.percent.config(text="100%")
            self.bar.set(1, GREEN)
            self.status.config(text="Model downloaded", fg=GREEN)
            self.detail.config(text=f"{model} is ready")
        elif error == "cancelled":
            self.status.config(text="Download cancelled", fg=ORANGE)
            self.detail.config(text=f"{model} wasn't downloaded")
            self.bar.set(self.bar.value, ORANGE)
        else:
            self.status.config(text="Download failed", fg=RED)
            self.detail.config(text=error[:140])
            self.bar.set(self.bar.value, RED)

    def _set_inputs(self, on):
        self.go_btn.set_enabled(on and bool(self.file))
        self.cancel_btn.set_enabled(not on)
        self.pause_btn.set_enabled(not on and self.running)
        self.choose_btn.set_enabled(on)
        self.model_tabs.set_enabled(on)
        self.lang_tabs.set_enabled(on)
        self.download_btn.set_enabled(on)
        self.open_btn.set_enabled(on and bool(self.out_path) and os.path.isfile(self.out_path))
        self.copy_btn.set_enabled(on and not self.transcript_empty)

    def _reader(self, proc):
        dec = codecs.getincrementaldecoder("utf-8")("replace")
        buf = ""
        while True:
            chunk = proc.stdout.read1(4096)
            if not chunk:
                break
            buf += dec.decode(chunk)
            parts = re.split(r"[\r\n]", buf)
            buf = parts.pop()
            for line in parts:
                if line.strip():
                    self.ui(self.on_line, line)
        buf += dec.decode(b"", final=True)
        if buf.strip():
            self.ui(self.on_line, buf)
        self.ui(self.on_exit, proc.wait())

    def on_line(self, line):
        m = SEG_RE.match(line)
        if m:
            start, end, words = ts_seconds(m.group(1)), ts_seconds(m.group(2)), m.group(3).strip()
            self.processed = max(self.processed, end)
            if self.transcript_empty:
                self._write(self.transcript, "", replace=True)
                self.transcript_empty = False
            self._write(self.transcript, f"{fmt_clock(start)}  ", "ts")
            self._write(self.transcript, words + "\n")
            if not self.paused_at:  # lines already in the pipe still arrive after pausing
                self.status.config(text="Transcribing", fg=TEXT)
            if self.duration:
                p = min(self.processed / self.duration, 1.0)
                self.percent.config(text=f"{int(p * 100)}%")
                self.bar.set(p, ACCENT)
            else:
                self.percent.config(text=fmt_clock(self.processed))
                self.detail.config(text="Audio length unknown, showing time transcribed")
            self._write(self.log, line + "\n")
            self._update_stats()
            return
        t = TQDM_RE.match(line)
        if t:
            pct = int(t.group(1))
            self.status.config(text="Downloading model (first use only)", fg=TEXT)
            self.detail.config(text=line.split("|")[-1].strip())
            self.bar.set(pct / 100, PURPLE)
            return
        if self.bar.color == PURPLE:  # model download finished; back to sliding until the first words
            self.bar.set(0, ACCENT)
        if line.startswith("Detecting language"):
            self.status.config(text="Detecting language", fg=TEXT)
        elif line.startswith("Detected language:"):
            self.detail.config(text=f"{self.model_tabs.value} \u00B7 {line.split(':', 1)[1].strip()}")
        self._write(self.log, line + "\n", "err" if "Error" in line or "Traceback" in line else None)

    def _tick(self):
        if self.running:
            self._update_stats()
            self.root.after(500, self._tick)

    def _update_stats(self):
        elapsed = (self.paused_at or time.time()) - self.start_time
        self.stats["elapsed"].config(text=fmt_clock(elapsed))
        if self.processed > 0 and elapsed > 0:
            self.stats["speed"].config(text=f"{self.processed / elapsed:.1f}\u00D7")
        if self.duration and self.processed > 0:
            p = min(self.processed / self.duration, 1.0)
            left = elapsed * (1 - p) / p
            self.stats["left"].config(text=fmt_clock(left))
            finish = dt.datetime.now() + dt.timedelta(seconds=left)
            self.stats["finish"].config(text="—" if self.paused_at else finish.strftime("%H:%M"))

    def on_exit(self, rc):
        if self.paused_at:  # killed while paused: count the time up to the pause only
            self.start_time += time.time() - self.paused_at
            self.paused_at = None
        self._set_pause_label("Pause")
        self._update_stats()
        self.running, self.proc = False, None
        self.bar.stop()
        self._update_model_status()  # the run may have downloaded the model
        if self.cancelled:
            self.status.config(text="Cancelled", fg=ORANGE)
            self.detail.config(text="Whisper was stopped")
            self.bar.set(self.bar.value, ORANGE)
            self.stats["left"].config(text="\u2014")
            self.stats["finish"].config(text="\u2014")
        elif rc == 0 and os.path.isfile(self.out_path):
            with open(self.out_path, encoding="utf-8", errors="replace") as f:
                text = f.read().strip()
            self._write(self.transcript, text or "(Whisper found no speech in this file.)",
                        None if text else "muted", replace=True)
            self.transcript.see("1.0")
            self.transcript_empty = not text
            self.percent.config(text="100%")
            self.bar.set(1, GREEN)
            self.status.config(text="Done", fg=GREEN)
            self.detail.config(text=f"Saved as {os.path.basename(self.out_path)} next to the audio file")
            self.stats["left"].config(text="00:00")
            self.stats["finish"].config(text=dt.datetime.now().strftime("%H:%M"))
            self.view_tabs.select(0)
            self.on_view(0, "t")
        else:
            lines = [l for l in self.log.get("1.0", "end").splitlines() if l.strip()]
            self.status.config(text="Failed", fg=RED)
            self.detail.config(text=(lines[-1] if lines else f"Exit code {rc}")[:140])
            self.bar.set(self.bar.value, RED)
            self.view_tabs.select(1)
            self.on_view(1, "l")
        self._set_inputs(True)

    def cancel(self):
        if self.downloading:
            self.dl_cancel = True
            self.status.config(text="Cancelling…", fg=ORANGE)
            return
        if self.proc and self.running:
            self.cancelled = True
            self.status.config(text="Cancelling\u2026", fg=ORANGE)
            threading.Thread(target=kill_tree, args=(self.proc.pid,), daemon=True).start()

    def toggle_pause(self):
        """Freeze Whisper where it is, or let it continue. The model stays loaded while paused."""
        if not (self.proc and self.running) or self.cancelled:
            return
        pause = not self.paused_at
        if not suspend_tree(self.proc.pid, pause):
            self.detail.config(text="Couldn't pause Whisper" if pause else "Couldn't resume Whisper")
            return
        if pause:
            self.paused_at = time.time()
            self.bar.stop()
            self.bar.set(self.bar.value, ORANGE)
            self.status.config(text="Paused", fg=ORANGE)
            self.detail.config(text="Click Resume to continue where it stopped")
            self._set_pause_label("Resume")
        else:
            self.start_time += time.time() - self.paused_at  # paused time doesn't count
            self.paused_at = None
            self.bar.set(self.bar.value, ACCENT)
            if self.processed:
                self.status.config(text="Transcribing", fg=TEXT)
            else:
                self.bar.start()
                self.status.config(text="Loading model", fg=TEXT)
            self.detail.config(text=f"{self.model_tabs.value} · {self.lang or 'auto-detect language'}")
            self._set_pause_label("Pause")
        self._update_stats()

    def _set_pause_label(self, text):
        self.pause_btn.text = text
        self.pause_btn.draw()

    def copy_transcript(self):
        text = self.transcript.get("1.0", "end").strip()
        if text and not self.transcript_empty:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.copy_btn.text = "Copied \u2713"
            self.copy_btn.draw()
            self.root.after(1200, self._reset_copy)

    def _reset_copy(self):
        self.copy_btn.text = "Copy"
        self.copy_btn.draw()

    def open_folder(self):
        if self.out_path and os.path.isfile(self.out_path):
            reveal_file(self.out_path)

    def on_close(self):
        self.dl_cancel = True  # a download thread stops and removes its partial file
        if self.proc and self.running:
            kill_tree(self.proc.pid)
        self.root.destroy()

    # ---- system check

    def system_check(self):
        info = {"os": os_name(), "cpu": cpu_name(), "threads": os.cpu_count() or 0, "ram": ram_gb(),
                "adapters": display_adapters(), "nvidia": nvidia_gpus(), "cuda": None}
        self.ui(self.show_system, dict(info))
        out = run_quiet([PY, "-c",
                         "import torch\n"
                         "print(torch.__version__)\n"
                         "ok = torch.cuda.is_available()\n"
                         "print(ok)\n"
                         "print(torch.cuda.get_device_properties(0).total_memory if ok else 0)"],
                        timeout=180).split()
        info["torch"] = out[0] if out else None
        info["cuda"] = len(out) > 1 and out[1] == "True"
        vram = max((mib for _, mib in info["nvidia"]), default=0) / 1024
        if not vram and len(out) > 2 and out[2].isdigit():
            vram = int(out[2]) / 1024 ** 3
        info["vram"] = vram
        info["model"] = recommend_model(info["cuda"], vram, info["ram"], info["threads"])
        self.ui(self.show_system, info)

    def show_system(self, info):
        self.sys_info = info
        body = self.sys_acc.body
        clear(body)
        body.grid_columnconfigure(1, weight=1)
        # NVIDIA cards come from nvidia-smi (with memory); the adapter list names them differently on Linux.
        gpus = [f"{name} \u00B7 {mib / 1024:.0f} GB" for name, mib in info["nvidia"]]
        gpus += [a for a in info["adapters"] if not (info["nvidia"] and "nvidia" in a.lower())]
        rows = [("Operating system", info["os"]), ("Processor", info["cpu"]), ("Threads", str(info["threads"])),
                ("Memory", f"{info['ram']} GB"), ("Graphics", "\n".join(gpus) or "None found")]
        r = 0
        for key, value in rows:
            label(body, key, "small", MUTED).grid(row=r, column=0, sticky="nw", pady=px(3))
            label(body, value, "small", TEXT, justify="right", wraplength=px(220)).grid(
                row=r, column=1, sticky="ne", pady=px(3))
            r += 1
        label(body, "Whisper on GPU", "small", MUTED).grid(row=r, column=0, sticky="w", pady=px(3))
        if info["cuda"] is None:
            badge = Badge(body, "Checking\u2026", MUTED)
        elif info["cuda"]:
            badge = Badge(body, "Yes \u00B7 CUDA", GREEN)
        else:
            badge = Badge(body, "No \u00B7 CPU only", ORANGE)
        badge.grid(row=r, column=1, sticky="e", pady=px(3))
        r += 1
        if info["cuda"] is False and info["nvidia"]:
            if not info.get("torch"):
                why = "torch is not installed."
            elif torch_cpu_only(info["torch"]):
                why = ("The installed torch is a CPU-only build, so your NVIDIA card can't be used. "
                       "See Requirements for the CUDA install command.")
            else:
                why = "torch has CUDA support but can't reach the card. Check the NVIDIA driver."
            autowrap(label(body, why, "tiny", ORANGE, justify="left", anchor="w")).grid(
                row=r, column=0, columnspan=2, sticky="w", pady=(px(2), px(4)))
            r += 1
        if info["cuda"] is None:
            self.sys_acc.set_summary("Checking GPU\u2026")
            return
        model = info["model"]
        label(body, "Suggested model", "small", MUTED).grid(row=r, column=0, sticky="w", pady=px(3))
        label(body, model, "h", ACCENT).grid(row=r, column=1, sticky="e", pady=px(3))

        self.cuda = info["cuda"]
        if self.cuda:
            self.sys_acc.set_summary(f"GPU \u00B7 {info['vram']:.0f} GB \u00B7 {model}")
            self.device_badge.set("GPU \u00B7 CUDA", GREEN)
        else:
            self.sys_acc.set_summary(f"CPU \u00B7 {info['threads']} threads \u00B7 {model}")
            self.device_badge.set("CPU only", ORANGE)
        if not self.user_model and not self.running:
            self.model_tabs.set_value(model)
        self._update_model_note()

    # ---- requirements check

    def requirements_check(self):
        items = []
        nvidia = bool(nvidia_gpus())

        inst = platform.python_version()
        cycle = ".".join(inst.split(".")[:2])
        data = fetch_json("https://endoflife.date/api/python.json")
        item = {"name": "Python", "installed": inst, "latest": None, "state": "unknown", "cmd": None, "note": None}
        if data:
            newest = data[0].get("latest")
            same = next((c.get("latest") for c in data if c.get("cycle") == cycle), None)
            item["latest"] = newest
            brew = IS_MAC and ("/homebrew/" in sys.executable or "/Cellar/" in sys.executable)
            if same and vtuple(inst) < vtuple(same) and not IS_WIN and not IS_MAC:
                # Linux: Python belongs to the distribution, which ships its own patch releases.
                item.update(state="ok", note="Python comes with your Linux distribution; "
                                             "its package manager keeps it updated.")
            elif same and vtuple(inst) < vtuple(same):
                cmd = (f"winget upgrade -e --id Python.Python.{cycle}" if IS_WIN else
                       f"brew upgrade python@{cycle}" if brew else None)
                note = f"{same} is the latest {cycle} release."
                if not cmd:
                    note += " Get it from python.org."
                item.update(state="update", cmd=cmd, note=note)
            else:
                item["state"] = "ok"
                if newest and vtuple(newest)[:2] > vtuple(inst)[:2]:
                    item["note"] = (f"Python {'.'.join(newest.split('.')[:2])} is a separate install; "
                                    "Whisper and torch would need installing there again.")
        items.append(item)

        inst = installed("openai-whisper")
        latest = pypi_latest("openai-whisper")
        cmd = f"{PIP} install -U openai-whisper"
        items.append(self._req("openai-whisper", inst, latest, cmd, cmd))
        items.append(self._torch_item(nvidia))

        ff = shutil.which("ffmpeg")
        inst = None
        if ff:
            m = re.search(r"ffmpeg version (\S+)", run_quiet([ff, "-version"]))
            if m:
                v = re.match(r"[\d.]+", m.group(1).lstrip("n"))
                inst = v.group(0).rstrip(".") if v else m.group(1)
        try:
            # gyan.dev publishes the version of the latest FFmpeg release.
            latest = fetch("https://www.gyan.dev/ffmpeg/builds/release-version").strip() or None
        except Exception:
            latest = None
        if IS_WIN:
            item = self._req("FFmpeg", inst, latest, "winget install -e --id Gyan.FFmpeg",
                             "winget upgrade -e --id Gyan.FFmpeg")
        elif IS_MAC:
            item = self._req("FFmpeg", inst, latest, "brew install ffmpeg", "brew upgrade ffmpeg")
            if item["cmd"] and not shutil.which("brew"):
                item["note"] = "Needs Homebrew first: see brew.sh."
        else:
            item = self._req("FFmpeg", inst, latest, linux_install("ffmpeg"), None)
            if item["state"] == "missing" and linux_package_tool() == "dnf":
                item["note"] = "FFmpeg comes from RPM Fusion: enable it first (rpmfusion.org)."
            elif item["state"] == "missing" and not item["cmd"]:
                item["note"] = "Install ffmpeg with your distribution's package manager."
            if item["state"] == "update":
                # Distributions lag behind FFmpeg releases; their version works fine with Whisper.
                item.update(state="ok", note="Your distribution's FFmpeg works fine with Whisper.")
        items.append(item)

        inst = installed("tkinterdnd2")
        cmd = f"{PIP} install -U tkinterdnd2"
        item = self._req("tkinterdnd2", inst, pypi_latest("tkinterdnd2"), cmd, cmd)
        item["name"] = "tkinterdnd2 (optional)"
        if not inst:
            item.update(state="optional", note="Lets you drop files onto the window. "
                                               "Restart the app after installing it.")
        elif not DND:
            item["note"] = ("Installed, but drag-and-drop didn't start. If you just installed it, "
                            "restart the app.")
        items.append(item)
        self.ui(self.show_requirements, items)

    @classmethod
    def _torch_item(cls, nvidia):
        inst = installed("torch")
        latest = pypi_latest("torch")
        index = "https://download.pytorch.org/whl/"
        if IS_MAC:
            cmd = f"{PIP} install -U torch"
            return cls._req("torch", inst, latest, cmd, cmd)
        if not inst:
            if IS_WIN:
                cmd = f"{PIP} install torch --index-url {index}{CUDA_INDEX if nvidia else 'cpu'}"
            else:
                # On Linux the PyPI build already includes CUDA; the CPU build is a much smaller download.
                cmd = f"{PIP} install torch" + ("" if nvidia else f" --index-url {index}cpu")
            return cls._req("torch", None, latest, cmd, cmd)
        if nvidia and torch_cpu_only(inst):
            cmd = (f"{PIP} install --force-reinstall torch --index-url {index}{CUDA_INDEX}" if IS_WIN
                   else f"{PIP} install --force-reinstall torch")
            item = cls._req("torch", inst, latest, None, None)
            item.update(state="warn", cmd=cmd,
                        note="CPU-only build. Install the CUDA build to use your NVIDIA card.")
            return item
        # Never plain "pip install -U torch" on Windows: that swaps a CUDA build for the CPU build.
        tag = re.search(r"\+(cu\d+|cpu)", inst)
        if tag:
            cmd = f"{PIP} install -U torch --index-url {index}{tag.group(1)}"
        elif IS_WIN:
            cmd = f"{PIP} install -U torch --index-url {index}cpu"
        else:
            cmd = f"{PIP} install -U torch"
        return cls._req("torch", inst, latest, None, cmd)

    @staticmethod
    def _req(name, inst, latest, install_cmd, update_cmd):
        item = {"name": name, "installed": inst, "latest": latest, "state": "unknown", "cmd": None, "note": None}
        if not inst:
            item.update(state="missing", cmd=install_cmd)
        elif latest and vtuple(inst) < vtuple(latest):
            item.update(state="update", cmd=update_cmd)
        elif latest:
            item["state"] = "ok"
        return item

    def show_requirements(self, items):
        self.req_items = items
        body = self.req_acc.body
        clear(body)
        badges = {"ok": ("Up to date", GREEN), "update": ("Update", ORANGE), "missing": ("Missing", RED),
                  "warn": ("CPU build", ORANGE), "unknown": ("Couldn't check", MUTED),
                  "optional": ("Optional", PURPLE)}
        label(body, f"Commands for {os_name()}", "tiny", MUTED).grid(row=0, column=0, sticky="w",
                                                                    pady=(0, px(10)))
        for i, it in enumerate(items):
            block = tk.Frame(body, bg=CARD)
            block.grid(row=i * 2 + 1, column=0, sticky="ew", pady=(0 if i == 0 else px(8), 0))
            block.grid_columnconfigure(0, weight=1)
            label(block, it["name"], "h").grid(row=0, column=0, sticky="w")
            Badge(block, *badges[it["state"]]).grid(row=0, column=1, sticky="e")
            versions = (f"Installed {it['installed']}" if it["installed"] else "Not installed") + \
                f" \u00B7 Latest {it['latest'] or 'unknown'}"
            label(block, versions, "tiny", MUTED).grid(row=1, column=0, columnspan=2, sticky="w")
            r = 2
            if it["note"]:
                autowrap(label(block, it["note"], "tiny", MUTED, justify="left", anchor="w")).grid(
                    row=r, column=0, columnspan=2, sticky="w", pady=(px(2), 0))
                r += 1
            if it["cmd"]:
                self._copyable(block, it["cmd"]).grid(row=r, column=0, columnspan=2, sticky="ew",
                                                      pady=(px(6), 0))
            if i < len(items) - 1:
                tk.Frame(body, bg=mix(MUTED, CARD, 0.75), height=1).grid(
                    row=i * 2 + 2, column=0, sticky="ew", pady=(px(8), 0))
        if any(it["cmd"] for it in items):
            label(body, "Click a command to copy it, then paste it in a terminal.", "tiny", MUTED).grid(
                row=len(items) * 2 + 1, column=0, sticky="w", pady=(px(10), 0))

        missing = sum(it["state"] == "missing" for it in items)
        updates = sum(it["state"] in ("update", "warn") for it in items)
        if missing:
            self.req_acc.set_summary(f"{missing} missing", RED)
        elif updates:
            self.req_acc.set_summary(f"{updates} update{'s' if updates > 1 else ''} available", ORANGE)
        elif all(it["state"] == "unknown" or it["state"] == "ok" for it in items) and \
                any(it["state"] == "unknown" for it in items):
            self.req_acc.set_summary("Installed \u00B7 couldn't check online", MUTED)
        else:
            self.req_acc.set_summary("All up to date", GREEN)

    def _copyable(self, parent, cmd):
        bg = mix(BG, CARD, 0.4)
        lbl = tk.Label(parent, text=cmd, font=FONT["mono"], fg=ACCENT, bg=bg, anchor="w", justify="left",
                       padx=px(8), pady=px(5), cursor="hand2")
        autowrap(lbl, 2 * px(8) + 2)

        def copy(_e):
            self.root.clipboard_clear()
            self.root.clipboard_append(cmd)
            lbl.config(text="Copied \u2713", fg=GREEN)
            self.root.after(1200, lambda: lbl.winfo_exists() and lbl.config(text=cmd, fg=ACCENT))
        lbl.bind("<Button-1>", copy)
        lbl.bind("<Enter>", lambda e: lbl.config(bg=mix(BG, CARD, 0.15)))
        lbl.bind("<Leave>", lambda e: lbl.config(bg=bg))
        return lbl


# ---------------------------------------------------------------- window

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


def main():
    global DND
    root = tk.Tk()
    root.withdraw()
    if TkinterDnD:
        try:
            TkinterDnD._require(root)  # loads the tkdnd library into this Tk
            DND = True
        except (RuntimeError, tk.TclError):
            pass  # no build for this platform; the app works without drag-and-drop
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


if __name__ == "__main__":
    main()
