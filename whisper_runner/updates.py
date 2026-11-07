"""Is there a newer release of the app? Asks GitHub at most once a day and remembers the answer, and
which version the user chose to skip, in the settings. Never downloads anything."""

import threading
import time

from . import settings
from .config import APP_VERSION
from .util import latest_app_version, vtuple

DAY = 24 * 60 * 60


def check(post, on_result):
    """Call on_result(version) with the newest released version (None if it couldn't be found). Uses the
    answer from the last day if there is one; otherwise asks GitHub in the background and calls
    on_result through post(fn, *args), which runs it on the UI thread."""
    s = settings.SETTINGS
    if time.time() - s.get("update_checked", 0) < DAY and s.get("update_latest"):
        on_result(s["update_latest"])
        return
    threading.Thread(target=lambda: post(on_result, latest_app_version()), daemon=True).start()


def remember(version):
    """Keep a successful answer for a day. A failed one (offline) isn't kept, so the next start asks again."""
    s = settings.SETTINGS
    if version and (version != s.get("update_latest") or time.time() - s.get("update_checked", 0) >= DAY):
        s["update_latest"], s["update_checked"] = version, time.time()
        settings.save_settings(s)


def is_newer(version):
    return bool(version) and vtuple(version) > vtuple(APP_VERSION)


def is_skipped(version):
    return bool(version) and settings.SETTINGS.get("update_skipped") == version


def skip(version):
    """Don't point this version out again (a later one will be)."""
    settings.SETTINGS["update_skipped"] = version
    settings.save_settings(settings.SETTINGS)


def should_notify(version):
    """Show the header's update badge for this version?"""
    return is_newer(version) and not is_skipped(version)
