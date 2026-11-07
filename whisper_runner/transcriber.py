"""One Whisper run: the command, the process, reading its output, pausing and stopping it."""

import codecs
import os
import re
import subprocess
import threading

from .config import PY
from .platform_utils import kill_tree, popen_options, process_usage, suspend_tree


class Transcription:
    """Runs `python -m whisper` on a file in the background. Each output line goes to on_line(line) and
    the exit code to on_exit(code), both through post(fn, *args), which runs them on the UI thread."""

    def __init__(self, path, model, lang, post, on_line, on_exit):
        folder = os.path.dirname(path)
        self.cmd = [PY, "-m", "whisper", path, "--model", model, "--output_format", "txt", "--output_dir", folder]
        if lang:
            self.cmd += ["--language", lang]
        self.folder = folder
        self.out_path = os.path.join(folder, os.path.splitext(os.path.basename(path))[0] + ".txt")
        self.post, self.on_line, self.on_exit = post, on_line, on_exit
        self.proc = None

    @property
    def command_line(self):
        return subprocess.list2cmdline(self.cmd)

    def start(self):
        """Start Whisper. Raises OSError if it can't be started."""
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        env["PYTHONIOENCODING"] = "utf-8"
        self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     stdin=subprocess.DEVNULL, env=env, cwd=self.folder, **popen_options())
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self):
        # Whisper's progress bar ends lines with \r, so split on both \r and \n.
        dec = codecs.getincrementaldecoder("utf-8")("replace")
        buf = ""
        while True:
            chunk = self.proc.stdout.read1(4096)
            if not chunk:
                break
            buf += dec.decode(chunk)
            parts = re.split(r"[\r\n]", buf)
            buf = parts.pop()
            for line in parts:
                if line.strip():
                    self.post(self.on_line, line)
        buf += dec.decode(b"", final=True)
        if buf.strip():
            self.post(self.on_line, buf)
        self.post(self.on_exit, self.proc.wait())

    def pause(self, on):
        """Freeze (on=True) or continue Whisper and everything it started. False if that failed."""
        return suspend_tree(self.proc.pid, on)

    def stop(self, wait=False):
        """Stop Whisper and everything it started; on_exit follows."""
        if wait:
            kill_tree(self.proc.pid)
        else:
            threading.Thread(target=kill_tree, args=(self.proc.pid,), daemon=True).start()

    def usage(self):
        """(CPU seconds so far, memory in bytes), or None."""
        return process_usage(self.proc.pid)
