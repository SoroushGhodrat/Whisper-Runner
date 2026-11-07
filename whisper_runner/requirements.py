"""What the app needs, and whether it is installed and up to date: Python, openai-whisper, torch, FFmpeg
and (optional) tkinterdnd2. Each item gets the install or update command for this operating system.

Notes are English text, or (text, fields) for tr_note(), so they are translated when shown."""

import platform
import re
import shutil
import sys

from .config import CUDA_INDEX, IS_MAC, IS_WIN, PIP
from .platform_utils import linux_install, linux_package_tool, torch_cpu_only
from .system import nvidia_gpus
from .util import fetch, fetch_json, installed, pypi_latest, run_quiet, vtuple


def check_requirements(dnd_available):
    """List of items: name, installed and latest version, state (ok, update, missing, warn, unknown,
    optional), cmd and note. Goes online, so run it off the UI thread."""
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
            note = ("{same} is the latest {cycle} release." if cmd else
                    "{same} is the latest {cycle} release. Get it from python.org.")
            item.update(state="update", cmd=cmd, note=(note, {"same": same, "cycle": cycle}))
        else:
            item["state"] = "ok"
            if newest and vtuple(newest)[:2] > vtuple(inst)[:2]:
                item["note"] = ("Python {version} is a separate install; Whisper and torch would need "
                                "installing there again.", {"version": ".".join(newest.split(".")[:2])})
    items.append(item)

    inst = installed("openai-whisper")
    latest = pypi_latest("openai-whisper")
    cmd = f"{PIP} install -U openai-whisper"
    items.append(requirement("openai-whisper", inst, latest, cmd, cmd))
    items.append(torch_requirement(nvidia))

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
        item = requirement("FFmpeg", inst, latest, "winget install -e --id Gyan.FFmpeg",
                           "winget upgrade -e --id Gyan.FFmpeg")
    elif IS_MAC:
        item = requirement("FFmpeg", inst, latest, "brew install ffmpeg", "brew upgrade ffmpeg")
        if item["cmd"] and not shutil.which("brew"):
            item["note"] = "Needs Homebrew first: see brew.sh."
    else:
        item = requirement("FFmpeg", inst, latest, linux_install("ffmpeg"), None)
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
    item = requirement("tkinterdnd2", inst, pypi_latest("tkinterdnd2"), cmd, cmd)
    item["name"] = "tkinterdnd2 (optional)"
    if not inst:
        item.update(state="optional", note="Lets you drop files onto the window. "
                                           "Restart the app after installing it.")
    elif not dnd_available:
        item["note"] = ("Installed, but drag-and-drop didn't start. If you just installed it, "
                        "restart the app.")
    items.append(item)
    return items


def torch_requirement(nvidia):
    inst = installed("torch")
    latest = pypi_latest("torch")
    index = "https://download.pytorch.org/whl/"
    if IS_MAC:
        cmd = f"{PIP} install -U torch"
        return requirement("torch", inst, latest, cmd, cmd)
    if not inst:
        if IS_WIN:
            cmd = f"{PIP} install torch --index-url {index}{CUDA_INDEX if nvidia else 'cpu'}"
        else:
            # On Linux the PyPI build already includes CUDA; the CPU build is a much smaller download.
            cmd = f"{PIP} install torch" + ("" if nvidia else f" --index-url {index}cpu")
        return requirement("torch", None, latest, cmd, cmd)
    if nvidia and torch_cpu_only(inst):
        cmd = (f"{PIP} install --force-reinstall torch --index-url {index}{CUDA_INDEX}" if IS_WIN
               else f"{PIP} install --force-reinstall torch")
        item = requirement("torch", inst, latest, None, None)
        item.update(state="warn", cmd=cmd, note="CPU-only build. Install the CUDA build to use your NVIDIA card.")
        return item
    # Never plain "pip install -U torch" on Windows: that swaps a CUDA build for the CPU build.
    tag = re.search(r"\+(cu\d+|cpu)", inst)
    if tag:
        cmd = f"{PIP} install -U torch --index-url {index}{tag.group(1)}"
    elif IS_WIN:
        cmd = f"{PIP} install -U torch --index-url {index}cpu"
    else:
        cmd = f"{PIP} install -U torch"
    return requirement("torch", inst, latest, None, cmd)


def requirement(name, inst, latest, install_cmd, update_cmd):
    item = {"name": name, "installed": inst, "latest": latest, "state": "unknown", "cmd": None, "note": None}
    if not inst:
        item.update(state="missing", cmd=install_cmd)
    elif latest and vtuple(inst) < vtuple(latest):
        item.update(state="update", cmd=update_cmd)
    elif latest:
        item["state"] = "ok"
    return item
