# Whisper Runner

A small desktop app that transcribes audio with [OpenAI Whisper](https://github.com/openai/whisper) and shows you what's happening while it works: live progress, time left, and the transcript appearing line by line.

It's a single Python file. There's nothing to build: on Windows you double-click it.

## Features

- **Live progress.** Percentage, a progress bar, elapsed time, time left, when it will finish, and speed.
- **Live transcript.** Text appears as Whisper produces it. When it's done, the transcript is saved as a `.txt` file next to the audio and shown in the app, ready to copy.
- **Picks a model for your computer.** The app checks your CPU, memory and graphics card, and suggests the Whisper model that fits. You can always choose another one.
- **Checks what's installed.** The Requirements section compares your Python, Whisper, PyTorch and FFmpeg with the latest versions and gives you the exact command to install or update each one, for your operating system. Click a command to copy it.
- **Works with phone recordings.** Samsung and iPhone formats are supported, along with the usual audio and video files.
- **Drag and drop** (optional). Drop a file onto the window to open it.
- **Windows, macOS and Linux.** It's built for Windows 11 first, and also runs on macOS and Linux.

## What you need

| | |
|---|---|
| **Python** | 3.9 or newer, 64-bit |
| **Whisper** | the `openai-whisper` package, which installs PyTorch |
| **FFmpeg** | Whisper uses it to read audio files |
| **Tkinter** | comes with Python on Windows and macOS; a separate package on some Linux distributions |
| **tkinterdnd2** | optional, for drag and drop |

Once the app is running, the **Requirements** section tells you if anything is missing or out of date and gives you the command to fix it.

## Installation

Download [`WhisperRunner.pyw`](WhisperRunner.pyw), or clone the repository:

```bash
git clone https://github.com/SoroushGhodrat/Whisper-Runner.git
```

Then follow the steps for your system.

### Windows

```powershell
winget install -e --id Python.Python.3.12
winget install -e --id Gyan.FFmpeg
python -m pip install -U openai-whisper
python -m pip install -U tkinterdnd2      # optional: drag and drop
```

Double-click `WhisperRunner.pyw` to start it. You can also drag an audio file onto the `.pyw` file's icon to open the app with that file.

**NVIDIA graphics card?** The standard PyTorch install on Windows can only use the CPU. To let Whisper use your graphics card, which is much faster, install the CUDA build of PyTorch:

```powershell
python -m pip install --force-reinstall torch --index-url https://download.pytorch.org/whl/cu128
```

Avoid `pip install -U torch` afterwards: it replaces the CUDA build with the CPU-only build. The app's Requirements section always shows an update command that keeps the build you have.

### macOS

Install [Homebrew](https://brew.sh) if you don't have it, then:

```bash
brew install python python-tk ffmpeg
python3 -m pip install -U openai-whisper
python3 -m pip install -U tkinterdnd2     # optional: drag and drop
python3 WhisperRunner.pyw
```

Whisper runs on the CPU on Macs, including Apple silicon.

### Linux

Ubuntu and Debian (on Fedora, Arch or openSUSE use `dnf`, `pacman` or `zypper`):

```bash
sudo apt install python3-tk python3-venv ffmpeg pciutils
python3 -m venv ~/whisper-env
source ~/whisper-env/bin/activate
pip install -U openai-whisper
pip install -U tkinterdnd2                # optional: drag and drop
python3 WhisperRunner.pyw
```

The virtual environment is there because recent Ubuntu and Debian releases don't allow `pip install` into the system Python. Start the app from the activated environment so it finds Whisper.

On Linux, the standard PyTorch install already supports NVIDIA graphics cards. On Fedora, FFmpeg comes from [RPM Fusion](https://rpmfusion.org), so enable that first.

## How to use it

1. **Choose a file.** Click **Choose file**, or drop a file onto the window.
2. **Pick a model.** The suggested one is selected for you; see [Choosing a model](#choosing-a-model).
3. **Pick a language**, or leave it on **Auto** to let Whisper detect it from the first 30 seconds.
4. Click **Start transcribing**.

The transcript is saved as `<audio name>.txt` in the same folder as the audio file. Use **Copy** to copy it, or **Open folder** to see the file. The **Log** tab shows Whisper's own output, which helps if something goes wrong.

Each model is downloaded once. The line under the model tabs tells you whether the selected model is installed. If it isn't, click **Download** next to it. The app never downloads anything on its own: if you start with a model that isn't installed, it tells you and waits for you to decide. While a model downloads, the progress bar turns purple and shows the size and speed, and **Cancel** stops it. The app checks there's enough disk space first, and verifies the file's checksum when it's done.

## Choosing a model

Bigger models are more accurate but slower and need more memory.

| Model | Download | Memory needed | Notes |
|---|---|---|---|
| `tiny` | 72 MB | ~1 GB | Fastest, least accurate |
| `base` | 139 MB | ~1 GB | |
| `small` | 461 MB | ~2 GB | A good default on a CPU |
| `medium` | 1.4 GB | ~5 GB | |
| `turbo` | 1.5 GB | ~6 GB | Close to `large-v3` quality, much faster |
| `large-v3` | 2.9 GB | ~10 GB | Most accurate |

The app suggests a model based on your computer:

- **With a usable NVIDIA graphics card:** `large-v3` from 11 GB of graphics memory, `turbo` from 6 GB, `medium` from 5 GB, `small` from 2 GB.
- **CPU only:** `small` with at least 16 GB of RAM and 8 CPU threads, `base` with 8 GB of RAM, otherwise `tiny`.

On a CPU, larger models can take longer than the recording itself. If you choose a model yourself, the app keeps your choice and shows "Selected manually" next to the suggestion.

## Supported files

- **Samsung:** `.m4a`, `.3ga`, `.amr`, `.3gp`
- **iPhone:** `.m4a`, `.qta`, `.mov`
- **Other:** `.mp3`, `.wav`, `.flac`, `.ogg`, `.opus`, `.wma`, `.aiff`, `.m4b`, `.webm`, `.mkv`, `.mp4`

Any other format FFmpeg can read should work too: choose **All files** in the file dialog.

## Troubleshooting

**"Can't open this file" for a recording on my phone.**
Files on a phone connected by USB can't be opened directly. Copy the file to your computer first, then open the copy.

**I have an NVIDIA card, but the app says "CPU only".**
Your PyTorch install can't use the card. On Windows, that usually means the CPU-only build is installed: see the CUDA command under [Windows](#windows). On Linux, check that the NVIDIA driver is installed and working (`nvidia-smi`). The **Your system** section explains what it found.

**Whisper fails straight away.**
Open the **Log** tab. A missing FFmpeg is the most common cause: check the **Requirements** section and run the command it shows.

**Linux: `ModuleNotFoundError: No module named 'tkinter'`.**
Install Tkinter with your package manager, for example `sudo apt install python3-tk`.

**macOS: the window doesn't open, or Python reports a Tk error.**
Homebrew's Python needs `brew install python-tk`.

**Drag and drop doesn't work.**
Install `tkinterdnd2` (see Installation) and restart the app. The **Requirements** section shows whether it's installed.

## How it works

The app runs the Whisper command-line tool in the background:

```
python -m whisper <file> --model <model> --output_format txt --output_dir <file's folder> [--language <code>]
```

It reads Whisper's output as it comes. Each line has a timestamp, which the app divides by the audio length (from `ffprobe`) to work out the progress and the time left. Cancel stops Whisper and everything it started.

The interface is plain Tkinter, with rounded shapes drawn on canvases. On Windows the app adapts to each monitor's display scaling, including when you move the window between screens.

## Contributing

Issues and pull requests are welcome. The app is deliberately one file with no build step and no required packages beyond Whisper. Please keep it that way, and keep it working on Windows, macOS and Linux.

## License

[MIT](LICENSE)
