"""Whisper models: where they are cached, downloading them, and which one suits this PC."""

import hashlib
import importlib.util
import os
import re
import urllib.request

from .config import MODEL_FILES
from .i18n import tr


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
        raise RuntimeError(tr("Couldn't find the download link. Is openai-whisper installed?"))
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
            raise RuntimeError(tr("The downloaded file is damaged (checksum mismatch). Please try again."))
        os.replace(part, dest)
    finally:
        if os.path.exists(part):
            os.remove(part)


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
