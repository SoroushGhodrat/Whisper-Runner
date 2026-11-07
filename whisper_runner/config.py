"""App-wide constants: platform, version, Whisper models and languages, file types."""

import os
import re
import subprocess
import sys


IS_WIN = sys.platform == "win32"


IS_MAC = sys.platform == "darwin"

APP_VERSION = "1.1.0"  # keep in step with the git tag of the release (v1.1.0)


REPO = "SoroushGhodrat/Whisper-Runner"


REPO_URL = f"https://github.com/{REPO}"


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
