"""The app's panels. Each is a widget that builds and owns its part of the window and offers a few
methods to update it; state() and restore() carry its state over when the window is rebuilt."""

from .about_dialog import AboutDialog
from .file_picker import FilePicker
from .header import Header
from .language_selector import LanguageSelector
from .model_selector import ModelSelector
from .progress_view import ProgressView
from .run_controls import RunControls
from .session_panel import SessionPanel
from .transcript_view import TranscriptView

__all__ = ["AboutDialog", "FilePicker", "Header", "LanguageSelector", "ModelSelector", "ProgressView",
           "RunControls", "SessionPanel", "TranscriptView"]
