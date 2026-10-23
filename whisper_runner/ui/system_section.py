"""Your system: operating system, processor, memory, graphics, whether Whisper can use the GPU, and the
model that suits this PC."""

from ..i18n import tr
from ..platform_utils import torch_cpu_only
from ..theme import ACCENT, GREEN, MUTED, ORANGE, TEXT, px
from ..widgets import Accordion, Badge, autowrap, clear, label


class SystemSection(Accordion):
    def __init__(self, parent, group, on_open):
        super().__init__(parent, tr("Your system"), group, on_open)
        label(self.body, tr("Checking…"), "small", MUTED).grid(row=0, column=0, sticky="w")

    def show(self, info):
        """`info` from system.check_system(); "cuda" is None until the GPU check is done."""
        body = self.body
        clear(body)
        body.grid_columnconfigure(1, weight=1)
        # NVIDIA cards come from nvidia-smi (with memory); the adapter list names them differently on Linux.
        gpus = [f"{name} · {mib / 1024:.0f} GB" for name, mib in info["nvidia"]]
        gpus += [a for a in info["adapters"] if not (info["nvidia"] and "nvidia" in a.lower())]
        rows = [("Operating system", info["os"]), ("Processor", info["cpu"]), ("Threads", str(info["threads"])),
                ("Memory", f"{info['ram']} GB"), ("Graphics", "\n".join(gpus) or tr("None found"))]
        r = 0
        for key, value in rows:
            label(body, tr(key), "small", MUTED).grid(row=r, column=0, sticky="nw", pady=px(3))
            label(body, value, "small", TEXT, justify="right", wraplength=px(220)).grid(
                row=r, column=1, sticky="ne", pady=px(3))
            r += 1
        label(body, tr("Whisper on GPU"), "small", MUTED).grid(row=r, column=0, sticky="w", pady=px(3))
        if info["cuda"] is None:
            badge = Badge(body, tr("Checking…"), MUTED)
        elif info["cuda"]:
            badge = Badge(body, tr("Yes · CUDA"), GREEN)
        else:
            badge = Badge(body, tr("No · CPU only"), ORANGE)
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
            autowrap(label(body, tr(why), "tiny", ORANGE, justify="left", anchor="w")).grid(
                row=r, column=0, columnspan=2, sticky="w", pady=(px(2), px(4)))
            r += 1
        if info["cuda"] is None:
            self.set_summary(tr("Checking GPU…"))
            return
        model = info["model"]
        label(body, tr("Suggested model"), "small", MUTED).grid(row=r, column=0, sticky="w", pady=px(3))
        label(body, model, "h", ACCENT).grid(row=r, column=1, sticky="e", pady=px(3))
        if info["cuda"]:
            self.set_summary(f"GPU · {info['vram']:.0f} GB · {model}")
        else:
            self.set_summary(tr("CPU · {threads} threads · {model}", threads=info["threads"], model=model))
