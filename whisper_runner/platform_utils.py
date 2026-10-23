"""Operating-system specifics: process control and usage, file manager, OS name, package
managers."""

import ctypes
import os
import platform
import shutil
import signal
import subprocess

from .config import IS_MAC, IS_WIN, NO_WINDOW
from .util import run_quiet

if IS_WIN:
    import winreg
    from ctypes import wintypes


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


if IS_WIN:
    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", wintypes.DWORD), ("cntUsage", wintypes.DWORD),
                    ("th32ProcessID", wintypes.DWORD), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", wintypes.DWORD), ("cntThreads", wintypes.DWORD),
                    ("th32ParentProcessID", wintypes.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wintypes.DWORD), ("szExeFile", ctypes.c_wchar * 260)]

    class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
        _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                    ("PeakWorkingSetSize", ctypes.c_size_t), ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t), ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t), ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t)]

    K32 = ctypes.WinDLL("kernel32")
    K32.OpenProcess.restype = wintypes.HANDLE
    K32.OpenProcess.argtypes = (wintypes.DWORD, wintypes.BOOL, wintypes.DWORD)
    K32.CreateToolhelp32Snapshot.restype = wintypes.HANDLE
    K32.CloseHandle.argtypes = (wintypes.HANDLE,)
    K32.GetProcessTimes.argtypes = (wintypes.HANDLE,) + (ctypes.POINTER(wintypes.FILETIME),) * 4
    K32.K32GetProcessMemoryInfo.argtypes = (wintypes.HANDLE, ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
                                            wintypes.DWORD)

    def win_tree(pid):
        """The process and everything it started. A venv's python.exe is only a launcher that
        starts the real Python as a child, so the work happens one level down."""
        snap = K32.CreateToolhelp32Snapshot(0x2, 0)  # TH32CS_SNAPPROCESS
        if not snap or snap == wintypes.HANDLE(-1).value:
            return [pid]
        children = {}
        try:
            e = PROCESSENTRY32W()
            e.dwSize = ctypes.sizeof(e)
            ok = K32.Process32FirstW(snap, ctypes.byref(e))
            while ok:
                children.setdefault(e.th32ParentProcessID, []).append(e.th32ProcessID)
                ok = K32.Process32NextW(snap, ctypes.byref(e))
        finally:
            K32.CloseHandle(snap)
        tree, todo = [], [pid]
        while todo:
            p = todo.pop()
            if p not in tree:
                tree.append(p)
                todo += children.get(p, [])
        return tree


def suspend_tree(pid, pause):
    """Freeze (pause=True) or continue a process and everything it started.
    Returns False if the process couldn't be reached."""
    if IS_WIN:
        ntdll = ctypes.WinDLL("ntdll")
        call = ntdll.NtSuspendProcess if pause else ntdll.NtResumeProcess
        call.argtypes = (wintypes.HANDLE,)
        done = False
        for p in win_tree(pid):
            handle = K32.OpenProcess(0x0800, False, p)  # PROCESS_SUSPEND_RESUME
            if handle:
                done = call(handle) == 0 or done
                K32.CloseHandle(handle)
        return done
    try:
        os.killpg(os.getpgid(pid), signal.SIGSTOP if pause else signal.SIGCONT)
        return True
    except (ProcessLookupError, PermissionError):
        return False


def process_usage(pid):
    """(CPU seconds used so far, memory in use in bytes) for a process and what it started,
    or None if it can't be read."""
    try:
        if IS_WIN:
            cpu = mem = 0
            found = False
            for p in win_tree(pid):
                handle = K32.OpenProcess(0x1000, False, p)  # PROCESS_QUERY_LIMITED_INFORMATION
                if not handle:
                    continue
                times = [wintypes.FILETIME() for _ in range(4)]
                counters = PROCESS_MEMORY_COUNTERS()
                counters.cb = ctypes.sizeof(counters)
                if (K32.GetProcessTimes(handle, *map(ctypes.byref, times))
                        and K32.K32GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb)):
                    cpu += sum(t.dwHighDateTime << 32 | t.dwLowDateTime for t in times[2:]) / 1e7
                    mem += counters.WorkingSetSize
                    found = True
                K32.CloseHandle(handle)
            return (cpu, mem) if found else None
        if IS_MAC:
            # TIME is [[dd-]hh:]mm:ss.ss, RSS is in KB
            used, rss = run_quiet(["ps", "-o", "time=,rss=", "-p", str(pid)]).split()
            days, _, clock = used.rpartition("-")
            secs = sum(float(x) * 60 ** i for i, x in enumerate(reversed(clock.split(":"))))
            return secs + int(days or 0) * 86400, int(rss) * 1024
        with open(f"/proc/{pid}/stat", encoding="ascii") as f:
            fields = f.read().rsplit(")", 1)[1].split()  # fields after the process name
        cpu = (int(fields[11]) + int(fields[12])) / os.sysconf("SC_CLK_TCK")  # utime + stime
        return cpu, int(fields[21]) * os.sysconf("SC_PAGE_SIZE")  # rss in pages
    except (OSError, ValueError, IndexError):
        return None


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


def prepare_process():
    """Settings that have to be made before any window exists."""
    if IS_WIN:
        # Without its own app ID the taskbar groups the window under pythonw.exe and shows Python's icon.
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WhisperRunner")
        except Exception:
            pass

        # Per-monitor DPI awareness.
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
