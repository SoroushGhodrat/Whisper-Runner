"""Interface language: tr() looks up text in the translations of the chosen language."""

import ctypes
import os
import re
import subprocess
import sys

from .messages import TRANSLATIONS


# Languages of the interface: code (also picks the flag), name in that language, English name.
UI_LANGS = [("en", "English", "English"), ("no", "Norsk", "Norwegian"), ("sv", "Svenska", "Swedish"),
            ("da", "Dansk", "Danish"), ("de", "Deutsch", "German"), ("es", "Español", "Spanish"),
            ("fr", "Français", "French"), ("pl", "Polski", "Polish"), ("uk", "Українська", "Ukrainian")]
UI_LANG = "en"  # read it as i18n.UI_LANG; change it with set_language()


def set_language(code):
    global UI_LANG
    UI_LANG = code


def tr(text, **kw):
    """`text` in the interface language, with {fields} filled from kw. A callable value is called
    first, so text that is itself translated or formatted follows a later language change."""
    s = TRANSLATIONS.get(UI_LANG, {}).get(text, text)
    if kw:
        s = s.format(**{k: v() if callable(v) else v for k, v in kw.items()})
    return s


def tr_note(note):
    """A requirement note: plain text, or (text, fields) for tr."""
    return tr(note[0], **note[1]) if isinstance(note, tuple) else tr(note)


def num(x, digits=1):
    """Number with the interface language's decimal separator."""
    s = f"{x:.{digits}f}"
    return s if UI_LANG == "en" else s.replace(".", ",")  # all the other languages use a comma


# Windows primary language IDs and locale name prefixes (nb_NO, sv-SE, ...) of the interface languages.
WIN_LANG_IDS = {0x09: "en", 0x14: "no", 0x1D: "sv", 0x06: "da", 0x07: "de", 0x0A: "es", 0x0C: "fr",
                0x15: "pl", 0x22: "uk"}


LOCALE_PREFIXES = {"en": "en", "nb": "no", "nn": "no", "no": "no", "sv": "sv", "da": "da", "de": "de",
                   "es": "es", "fr": "fr", "pl": "pl", "uk": "uk"}


def system_ui_lang():
    """Interface language to start with when none was chosen: the system's language if the app has
    it, else English."""
    names = []
    try:
        if sys.platform == "win32":
            found = WIN_LANG_IDS.get(ctypes.windll.kernel32.GetUserDefaultUILanguage() & 0x3FF)
            if found:
                return found
        elif sys.platform == "darwin":
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"], capture_output=True,
                                 text=True, timeout=5).stdout
            names += re.findall(r"[A-Za-z]{2,3}(?=[-_\"\s,)])", out)[:1]  # the first preferred language
    except Exception:
        pass
    names += [os.getenv(v, "") for v in ("LC_ALL", "LC_MESSAGES", "LANG")]
    for name in names:
        if name and name.lower()[:2] in LOCALE_PREFIXES:
            return LOCALE_PREFIXES[name.lower()[:2]]
    return "en"
