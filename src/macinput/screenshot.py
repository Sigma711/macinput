"""Screenshot helpers using macOS screencapture."""

from __future__ import annotations

import atexit
import subprocess
import tempfile
import threading
from pathlib import Path

_CLEANUP_LOCK = threading.Lock()
_CLEANUP_TIMERS: dict[str, threading.Timer] = {}


def _remove_file(path: str) -> bool:
    try:
        Path(path).unlink(missing_ok=True)
    except OSError:
        return False
    return True


def _auto_cleanup(path: str) -> None:
    with _CLEANUP_LOCK:
        _CLEANUP_TIMERS.pop(path, None)
    _remove_file(path)


def capture_screen(*, cleanup_after: float | None = 5.0) -> str:
    """Capture the full screen and return a temporary image path."""
    if cleanup_after is not None and cleanup_after < 0:
        raise ValueError("cleanup_after must be >= 0 or None")

    with tempfile.NamedTemporaryFile(
        prefix="macinput-screenshot-",
        suffix=".png",
        delete=False,
    ) as handle:
        path = handle.name

    result = subprocess.run(
        ["screencapture", "-x", path],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.returncode != 0:
        _remove_file(path)
        message = result.stderr.strip() or "screencapture failed"
        raise RuntimeError(message)

    if cleanup_after is not None:
        timer = threading.Timer(cleanup_after, _auto_cleanup, args=(path,))
        timer.daemon = True
        with _CLEANUP_LOCK:
            _CLEANUP_TIMERS[path] = timer
        timer.start()

    return path


def cleanup_screenshot(path: str) -> bool:
    """Manually remove a screenshot file created by ``capture_screen``."""
    with _CLEANUP_LOCK:
        timer = _CLEANUP_TIMERS.pop(path, None)
    if timer is not None:
        timer.cancel()
    return _remove_file(path)


def _cleanup_all() -> None:
    with _CLEANUP_LOCK:
        items = list(_CLEANUP_TIMERS.items())
        _CLEANUP_TIMERS.clear()

    for path, timer in items:
        timer.cancel()
        _remove_file(path)


atexit.register(_cleanup_all)
