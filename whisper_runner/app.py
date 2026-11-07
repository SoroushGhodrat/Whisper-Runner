"""The app: puts the panels together, keeps the state, and runs Whisper and model downloads.

The panels in ui/ draw themselves; this class decides what they show."""

import datetime as dt
import functools
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import filedialog, messagebox

from . import dnd, i18n, settings, theme, updates
from .config import AUDIO_EXTS, MODEL_FILES, SEG_RE, TQDM_RE
from .i18n import num, tr
from .models import DownloadCancelled, download_model, model_downloaded, whisper_cache
from .platform_utils import reveal_file
from .requirements import check_requirements
from .system import check_system
from .theme import ACCENT, BG, GREEN, MUTED, ORANGE, PANEL, PURPLE, RED, TEXT, px, set_dpi
from .transcriber import Transcription
from .ui import (AboutDialog, FilePicker, Header, LanguageSelector, ModelSelector, ProgressView, RunControls,
                 SessionPanel, TranscriptView)
from .util import audio_duration, fmt_clock, fmt_size, free_space, ts_seconds
from .widgets import Card
from .window import fit_window, window_dpi

DASH = "—"


class App:
    def __init__(self, root):
        self.root = root
        self.q = queue.Queue()  # calls from worker threads, run on the UI thread by _poll
        self.file = None  # the chosen recording
        self.duration = None  # its length in seconds, once known
        self.lang = None  # language code for Whisper, None for auto-detect
        self.user_model = False  # the model was picked by hand, so don't replace it with the suggestion
        self.sys_info = None  # from check_system
        self.req_items = None  # from check_requirements
        self.latest_version = False  # newest released version of this app; None if unknown, False if not checked
        # a Whisper run
        self.run = None
        self.running = False
        self.cancelled = False
        self.paused_at = None  # time.time() when paused, else None
        self.start_time = 0.0
        self.processed = 0.0  # seconds of audio transcribed
        self.usage = None  # (time.monotonic(), CPU seconds) at the last CPU sample
        self.out_path = None
        # a model download
        self.downloading = None  # model being downloaded
        self.dl_cancel = False
        # moving between monitors
        self.dpi = round(theme.SCALE * 96)
        self.dpi_job = None
        self.logical_size = None

        root.title("Whisper Runner")
        root.configure(bg=BG)
        self._build()
        root.bind_all("<MouseWheel>", lambda e: self.session.wheel(e))
        root.bind_all("<Button-4>", lambda e: self.session.wheel(e, -3))
        root.bind_all("<Button-5>", lambda e: self.session.wheel(e, 3))
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._poll()
        threading.Thread(target=check_system, args=(lambda info: self.ui(self.show_system, info),),
                         daemon=True).start()
        threading.Thread(target=lambda: self.ui(self.show_requirements, check_requirements(dnd.available)),
                         daemon=True).start()
        updates.check(self.ui, self.on_latest)
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

        p = left.inner
        p.grid_columnconfigure(0, weight=1)
        self.header = Header(p, self.show_about)
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.show_update(updates.should_notify(self.latest_version))
        self.picker = FilePicker(p, self.choose_file)
        self.picker.grid(row=1, column=0, sticky="ew", pady=(px(18), 0))
        self.models = ModelSelector(p, self.on_model, self.start_download)
        self.models.grid(row=2, column=0, sticky="ew", pady=(px(18), 0))
        self.langs = LanguageSelector(p, self.on_lang, lambda: not self.busy)
        self.langs.grid(row=3, column=0, sticky="ew", pady=(px(16), 0))
        self.controls = RunControls(p, self.start, self.toggle_pause, self.cancel)
        self.controls.grid(row=4, column=0, sticky="ew", pady=(px(20), 0))
        self.progress = ProgressView(p)
        self.progress.grid(row=5, column=0, sticky="ew", pady=(px(14), 0))
        self.transcript = TranscriptView(p, self.open_folder)
        self.transcript.grid(row=6, column=0, sticky="nsew", pady=(px(20), 0))
        p.grid_rowconfigure(6, weight=1)

        right.inner.grid_columnconfigure(0, weight=1)
        right.inner.grid_rowconfigure(0, weight=1)
        self.session = SessionPanel(right.inner, self.show_about, self.set_ui_lang)
        self.session.grid(row=0, column=0, sticky="nsew")

        self._update_models()
        if dnd.available:
            self._enable_drop(outer)

    def _rebuild(self):
        """Build the UI again (new scale or language) and carry the current state over."""
        state = {"picker": self.picker.state(), "models": self.models.state(), "langs": self.langs.state(),
                 "progress": self.progress.state(), "transcript": self.transcript.state(),
                 "session": self.session.state()}
        self.outer.destroy()
        self._build()
        if self.sys_info:
            self.show_system(self.sys_info)
        if self.req_items:
            self.show_requirements(self.req_items)
        self.picker.restore(state["picker"])
        self.models.restore(state["models"])
        self.langs.restore(state["langs"])
        self.progress.restore(state["progress"], moving=self.busy and not self.paused_at)
        self.transcript.restore(state["transcript"])
        self.session.restore(state["session"])
        self.controls.set_paused(bool(self.paused_at))
        self._update_models()
        self._set_inputs(not self.busy)

    # ---- dropping files on the window (only with tkinterdnd2)

    def _enable_drop(self, target):
        # Drops on any widget inside `target` reach it; the root window itself can't be registered.
        target.drop_target_register(dnd.DND_FILES)
        target.dnd_bind("<<DropEnter>>", self._drag_enter)
        target.dnd_bind("<<DropPosition>>", lambda e: "refuse_drop" if self.running else e.action)
        target.dnd_bind("<<DropLeave>>", self._drag_leave)
        target.dnd_bind("<<Drop>>", self._drop)

    def _drag_enter(self, e):
        if self.busy:
            return "refuse_drop"
        self.picker.drag_over(True)
        return e.action

    def _drag_leave(self, e):
        self.picker.drag_over(False)
        return e.action

    def _drop(self, e):
        self.picker.drag_over(False)
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
            self.logical_size = (root.winfo_width() / theme.SCALE, root.winfo_height() / theme.SCALE)
            return
        self.dpi = dpi
        cx = root.winfo_rootx() + root.winfo_width() // 2
        cy = root.winfo_rooty() + root.winfo_height() // 2
        set_dpi(root, dpi)
        self._rebuild()
        if root.state() != "zoomed":
            lw, lh = self.logical_size or (1180, 820)
            fit_window(root, px(lw), px(lh), cx, cy)

    # ---- interface language and About

    def set_ui_lang(self, code):
        if code == i18n.UI_LANG:
            return
        i18n.set_language(code)
        settings.SETTINGS["ui_lang"] = code
        settings.save_settings(settings.SETTINGS)
        self._rebuild()

    def show_about(self):
        AboutDialog.show(self.root, self.ui, self.latest_version, self.on_latest, self.skip_version)

    # ---- newer releases of the app

    def on_latest(self, version):
        """The newest released version (None if GitHub couldn't be reached)."""
        self.latest_version = version
        updates.remember(version)
        self.header.show_update(updates.should_notify(version))

    def skip_version(self, version):
        updates.skip(version)
        self.header.show_update(False)

    # ---- calls from worker threads

    def ui(self, fn, *args):
        """Run fn(*args) on the UI thread. Safe to call from any thread."""
        self.q.put((fn, args))

    def _poll(self):
        try:
            while True:
                fn, args = self.q.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.root.after(50, self._poll)

    # ---- inputs

    @property
    def busy(self):
        """Transcribing or downloading a model."""
        return self.running or bool(self.downloading)

    def _set_inputs(self, on):
        """Enable the inputs (nothing running) or only the run controls."""
        self.controls.set_state(start=on and bool(self.file), pause=not on and self.running, cancel=not on)
        self.picker.set_enabled(on)
        self.models.set_enabled(on)
        self.langs.set_enabled(on)
        self.transcript.set_enabled(open_folder=on and bool(self.out_path) and os.path.isfile(self.out_path),
                                    copy=on and not self.transcript.empty)

    def on_model(self, model):
        if self.busy:
            return False
        self.user_model = True
        self.root.after_idle(self._update_models)  # after the tab is selected

    def _update_models(self):
        self.models.refresh(self.downloading, (self.sys_info or {}).get("model"), self.user_model)

    def on_lang(self, code):
        self.lang = code

    def choose_file(self):
        if self.busy:
            return
        exts = " ".join("*" + e for e in AUDIO_EXTS)
        path = filedialog.askopenfilename(
            parent=self.root, title=tr("Choose an audio file"),
            filetypes=[(tr("Audio and video"), exts), (tr("All files"), "*.*")])
        if path:
            self.set_file(path)

    def set_file(self, path):
        path = os.path.normpath(path)
        if os.path.isdir(path):
            self.picker.set_name("{name}", name=os.path.basename(path) or path)
            self.picker.set_info("That's a folder. Choose or drop an audio file.", RED)
            return
        if not os.path.isfile(path):
            if os.path.basename(path):
                self.picker.set_name("{name}", name=os.path.basename(path))
            else:
                self.picker.set_name("File not found")
            self.picker.set_info("Can't open this file. Files on a phone connected by USB must be copied to "
                                 "this PC first.", RED)
            return
        self.file, self.duration = path, None
        self.picker.set_name("{name}", name=os.path.basename(path))
        size = functools.partial(fmt_size, os.path.getsize(path))  # formatted when shown
        ext = os.path.splitext(path)[1].lower()
        self.picker.set_info("File size: {size} · Duration: {length} · Type: {ext}", MUTED,
                             size=size, length=lambda: tr("reading…"), ext=ext)
        self.controls.set_state(start=True)
        self.progress.set_status("Ready", TEXT)
        self.progress.set_detail("{path}", path=os.path.dirname(path))
        self.progress.set_percent("0%")
        self.progress.bar.set(0, ACCENT)

        def work():
            d = audio_duration(path)
            self.ui(self._got_duration, path, d, size, ext)
        threading.Thread(target=work, daemon=True).start()

    def _got_duration(self, path, d, size, ext):
        if path != self.file:
            return
        self.duration = d
        length = fmt_clock(d) if d else lambda: tr("unknown")
        self.picker.set_info("File size: {size} · Duration: {length} · Type: {ext}",
                             size=size, length=length, ext=ext)

    def open_folder(self):
        if self.out_path and os.path.isfile(self.out_path):
            reveal_file(self.out_path)

    # ---- running Whisper

    def start(self):
        if self.busy or not self.file:
            return
        model = self.models.value
        if not model_downloaded(model):
            # Never download on our own (Whisper would): tell the user and let them decide.
            messagebox.showinfo(
                tr("Model not installed"),
                tr("The {model} model isn't installed on this computer yet ({size}).\n\n"
                   "To use it, click Download under the model list. Or choose a model that's already installed.",
                   model=model, size=fmt_size(MODEL_FILES[model][1])), parent=self.root)
            return
        run = Transcription(self.file, model, self.lang, self.ui, self.on_line, self.on_exit)
        self.transcript.reset_log(run.command_line)
        try:
            run.start()
        except OSError as e:
            self.progress.set_status("Couldn't start Whisper", RED)
            self.progress.set_detail("{error}", error=str(e))
            return
        self.run, self.out_path = run, run.out_path
        self.running, self.cancelled, self.paused_at = True, False, None
        self.start_time, self.processed = time.time(), 0.0
        self.usage = None
        self.transcript.set_placeholder("Waiting for the first words…")
        self.session.reset_stats()
        self._set_inputs(False)
        self.progress.set_percent("0%")
        self.progress.set_status("Loading model", TEXT)
        self._show_run_detail()
        self.progress.bar.set(0, ACCENT)
        self.progress.bar.start()
        self._tick()

    def _show_run_detail(self):
        """Model and language of the run, under the status."""
        model = self.models.value
        if self.lang:
            self.progress.set_detail("{model} · {lang}", model=model, lang=self.lang)
        else:
            self.progress.set_detail("{model} · auto-detect language", model=model)

    def on_line(self, line):
        """A line of Whisper's output: a transcribed segment, download progress, or anything else."""
        m = SEG_RE.match(line)
        if m:
            start, end, words = ts_seconds(m.group(1)), ts_seconds(m.group(2)), m.group(3).strip()
            self.processed = max(self.processed, end)
            self.transcript.add_segment(fmt_clock(start), words)
            if not self.paused_at:  # lines already in the pipe still arrive after pausing
                self.progress.set_status("Transcribing", TEXT)
            if self.duration:
                self.progress.set_fraction(min(self.processed / self.duration, 1.0), ACCENT)
            else:
                self.progress.set_percent(fmt_clock(self.processed))
                self.progress.set_detail("Audio length unknown, showing time transcribed")
            self.transcript.log(line)
            self._update_stats()
            return
        t = TQDM_RE.match(line)
        if t:
            self.progress.set_status("Downloading model (first use only)", TEXT)
            self.progress.set_detail("{progress}", progress=line.split("|")[-1].strip())
            self.progress.bar.set(int(t.group(1)) / 100, PURPLE)
            return
        if self.progress.bar.color == PURPLE:  # model download finished; back to sliding until the first words
            self.progress.bar.set(0, ACCENT)
        if line.startswith("Detecting language"):
            self.progress.set_status("Detecting language", TEXT)
        elif line.startswith("Detected language:"):
            self.progress.set_detail("{model} · {lang}", model=self.models.value,
                                     lang=line.split(":", 1)[1].strip())
        self.transcript.log(line, "err" if "Error" in line or "Traceback" in line else None)

    def _tick(self):
        if self.running:
            self._update_stats()
            self._update_usage()
            self.root.after(500, self._tick)

    def _update_usage(self):
        """CPU and memory used by Whisper. CPU is the share of the whole processor since the last
        sample, like Task Manager shows it."""
        u = self.run.usage() if self.run else None
        if not u:
            return
        now = time.monotonic()
        if self.usage:
            t0, cpu0 = self.usage
            if now - t0 < 0.9:
                return
            pct = (u[0] - cpu0) / (now - t0) / (os.cpu_count() or 1) * 100
            self.session.set_stat("cpu", f"{max(0, min(pct, 100)):.0f}%")
        self.session.set_stat("ram", fmt_size(u[1]))
        self.usage = (now, u[0])

    def _update_stats(self):
        elapsed = (self.paused_at or time.time()) - self.start_time
        self.session.set_stat("elapsed", fmt_clock(elapsed))
        if self.processed > 0 and elapsed > 0:
            self.session.set_stat("speed", f"{num(self.processed / elapsed)}×")
        if self.duration and self.processed > 0:
            p = min(self.processed / self.duration, 1.0)
            left = elapsed * (1 - p) / p
            self.session.set_stat("left", fmt_clock(left))
            finish = dt.datetime.now() + dt.timedelta(seconds=left)
            self.session.set_stat("finish", DASH if self.paused_at else finish.strftime("%H:%M"))

    def on_exit(self, rc):
        if self.paused_at:  # killed while paused: count the time up to the pause only
            self.start_time += time.time() - self.paused_at
            self.paused_at = None
        self.controls.set_paused(False)
        self._update_stats()
        self.session.set_stat("cpu", DASH)
        self.session.set_stat("ram", DASH)
        self.running, self.run = False, None
        self.progress.bar.stop()
        self._update_models()  # the run may have downloaded the model
        if self.cancelled:
            self.progress.set_status("Cancelled", ORANGE)
            self.progress.set_detail("Whisper was stopped")
            self.progress.bar.set(self.progress.bar.value, ORANGE)
            self.session.set_stat("left", DASH)
            self.session.set_stat("finish", DASH)
        elif rc == 0 and os.path.isfile(self.out_path):
            with open(self.out_path, encoding="utf-8", errors="replace") as f:
                self.transcript.set_result(f.read().strip())
            self.progress.set_fraction(1, GREEN)
            self.progress.set_status("Done", GREEN)
            self.progress.set_detail("Saved as {name} next to the audio file", name=os.path.basename(self.out_path))
            self.session.set_stat("left", "00:00")
            self.session.set_stat("finish", dt.datetime.now().strftime("%H:%M"))
            self.transcript.show("t")
        else:
            lines = self.transcript.log_lines()
            self.progress.set_status("Failed", RED)
            if lines:
                self.progress.set_detail("{error}", error=lines[-1][:140])
            else:
                self.progress.set_detail("Exit code {rc}", rc=rc)
            self.progress.bar.set(self.progress.bar.value, RED)
            self.transcript.show("l")
        self._set_inputs(True)

    def cancel(self):
        if self.downloading:
            self.dl_cancel = True
            self.progress.set_status("Cancelling…", ORANGE)
            return
        if self.run and self.running:
            self.cancelled = True
            self.progress.set_status("Cancelling…", ORANGE)
            self.run.stop()

    def toggle_pause(self):
        """Freeze Whisper where it is, or let it continue. The model stays loaded while paused."""
        if not (self.run and self.running) or self.cancelled:
            return
        pause = not self.paused_at
        if not self.run.pause(pause):
            self.progress.set_detail("Couldn't pause Whisper" if pause else "Couldn't resume Whisper")
            return
        if pause:
            self.paused_at = time.time()
            self.progress.bar.stop()
            self.progress.bar.set(self.progress.bar.value, ORANGE)
            self.progress.set_status("Paused", ORANGE)
            self.progress.set_detail("Click Resume to continue where it stopped")
        else:
            self.start_time += time.time() - self.paused_at  # paused time doesn't count
            self.paused_at = None
            self.progress.bar.set(self.progress.bar.value, ACCENT)
            if self.processed:
                self.progress.set_status("Transcribing", TEXT)
            else:
                self.progress.bar.start()
                self.progress.set_status("Loading model", TEXT)
            self._show_run_detail()
        self.controls.set_paused(pause)
        self._update_stats()

    def on_close(self):
        self.dl_cancel = True  # a download thread stops and removes its partial file
        if self.run and self.running:
            self.run.stop(wait=True)
        self.root.destroy()

    # ---- downloading a model

    def _enough_space(self, model):
        """Check the drive has room for the model; show an error if not."""
        need = MODEL_FILES[model][1]
        free = free_space(whisper_cache())
        if free is not None and free < need * 1.1:
            messagebox.showerror(
                tr("Not enough disk space"),
                tr("The {model} model needs {need}, but only {free} is free on the drive where Whisper keeps its "
                   "models:\n\n{folder}\n\nFree up some space or choose a smaller model.",
                   model=model, need=fmt_size(need), free=fmt_size(free), folder=whisper_cache()),
                parent=self.root)
            return False
        return True

    def start_download(self, model):
        if self.busy or model_downloaded(model) or not self._enough_space(model):
            return
        self.downloading, self.dl_cancel = model, False
        self.dl_started = time.time()
        self._set_inputs(False)
        self._update_models()
        self.progress.set_percent("0%")
        self.progress.set_status("Downloading the {model} model", TEXT, model=model)
        self.progress.set_detail("Connecting…")
        self.progress.bar.set(0, PURPLE)
        self.progress.bar.start()
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
        speed = done / max(0.1, time.time() - self.dl_started)
        self.progress.set_fraction(done / total if total else 0, PURPLE)
        self.progress.set_detail("{done} of {total} · {speed}/s", done=functools.partial(fmt_size, done),
                                 total=functools.partial(fmt_size, total), speed=functools.partial(fmt_size, speed))

    def _download_done(self, model, error):
        self.downloading = None
        self.progress.bar.stop()
        self._set_inputs(True)
        self._update_models()
        if error is None:
            self.progress.set_fraction(1, GREEN)
            self.progress.set_status("Model downloaded", GREEN)
            self.progress.set_detail("{model} is ready", model=model)
        elif error == "cancelled":
            self.progress.set_status("Download cancelled", ORANGE)
            self.progress.set_detail("{model} wasn't downloaded", model=model)
            self.progress.bar.set(self.progress.bar.value, ORANGE)
        else:
            self.progress.set_status("Download failed", RED)
            self.progress.set_detail("{error}", error=error[:140])
            self.progress.bar.set(self.progress.bar.value, RED)

    # ---- system and requirements checks (results arrive from worker threads)

    def show_system(self, info):
        self.sys_info = info
        self.session.system.show(info)
        if info["cuda"] is None:  # GPU check still running
            return
        if info["cuda"]:
            self.header.set_device("GPU · CUDA", GREEN)
        else:
            self.header.set_device(tr("CPU only"), ORANGE)
        if not self.user_model and not self.running:
            self.models.select(info["model"])
        self._update_models()

    def show_requirements(self, items):
        self.req_items = items
        self.session.requirements.show(items)
