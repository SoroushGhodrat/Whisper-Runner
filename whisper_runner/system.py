"""Hardware checks: processor, memory, graphics cards, and whether Whisper can use the GPU."""

import ctypes
import json
import os
import platform
import re
import shutil

from .config import IS_MAC, IS_WIN, PY
from .models import recommend_model
from .platform_utils import os_name
from .util import run_quiet

if IS_WIN:
    import winreg


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


def check_system(report):
    """Look at this computer and call report(info) twice: first with the quick facts ("cuda" None),
    then again once torch has said whether it can use the GPU, with the suggested model. Slow (it starts
    Python to import torch), so run it off the UI thread."""
    info = {"os": os_name(), "cpu": cpu_name(), "threads": os.cpu_count() or 0, "ram": ram_gb(),
            "adapters": display_adapters(), "nvidia": nvidia_gpus(), "cuda": None}
    report(dict(info))
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
    report(info)
