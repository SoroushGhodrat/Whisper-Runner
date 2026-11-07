"""Small helpers: time and size formatting, version numbers, subprocesses, web requests."""

import json
import os
import re
import shutil
import subprocess
import urllib.request
import wave
from importlib import metadata

from .config import NO_WINDOW, REPO
from .i18n import num


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


def latest_app_version():
    """Newest released version of this app, from the project's git tags (v1.2.3), or None."""
    data = fetch_json(f"https://api.github.com/repos/{REPO}/tags")
    if not isinstance(data, list):  # offline, or an error message from GitHub
        return None
    names = [t.get("name", "") for t in data if isinstance(t, dict)]
    versions = [n.lstrip("vV") for n in names if re.fullmatch(r"[vV]?\d+(\.\d+)*", n)]
    return max(versions, key=vtuple, default=None)


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
            return f"{n:.0f} {unit}" if unit == "B" else f"{num(n)} {unit}"
        n /= 1024
