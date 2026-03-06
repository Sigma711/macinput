"""Mouse control helpers built on macOS CGEvent APIs."""

from __future__ import annotations

import ctypes
import time
from typing import Literal

import Quartz


class _CGPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_double), ("y", ctypes.c_double)]


_APP_SERVICES = ctypes.CDLL(
    "/System/Library/Frameworks/ApplicationServices.framework/ApplicationServices"
)
_CORE_FOUNDATION = ctypes.CDLL(
    "/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation"
)

_APP_SERVICES.CGEventCreate.argtypes = [ctypes.c_void_p]
_APP_SERVICES.CGEventCreate.restype = ctypes.c_void_p
_APP_SERVICES.CGEventGetLocation.argtypes = [ctypes.c_void_p]
_APP_SERVICES.CGEventGetLocation.restype = _CGPoint
_CORE_FOUNDATION.CFRelease.argtypes = [ctypes.c_void_p]
_CORE_FOUNDATION.CFRelease.restype = None

_MOUSE_BUTTONS: dict[str, int] = {
    "left": Quartz.kCGMouseButtonLeft,
    "right": Quartz.kCGMouseButtonRight,
}

_DOWN_EVENTS: dict[str, int] = {
    "left": Quartz.kCGEventLeftMouseDown,
    "right": Quartz.kCGEventRightMouseDown,
}

_UP_EVENTS: dict[str, int] = {
    "left": Quartz.kCGEventLeftMouseUp,
    "right": Quartz.kCGEventRightMouseUp,
}


Button = Literal["left", "right"]


def move_to(x: float, y: float) -> None:
    """Move mouse cursor to absolute coordinates."""
    event = Quartz.CGEventCreateMouseEvent(
        None,
        Quartz.kCGEventMouseMoved,
        (float(x), float(y)),
        Quartz.kCGMouseButtonLeft,
    )
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def get_position() -> tuple[float, float]:
    """Get current cursor position as (x, y)."""
    event_ref = _APP_SERVICES.CGEventCreate(None)
    if not event_ref:
        raise RuntimeError("CGEventCreate returned NULL")

    try:
        point = _APP_SERVICES.CGEventGetLocation(event_ref)
        return float(point.x), float(point.y)
    finally:
        _CORE_FOUNDATION.CFRelease(event_ref)


def click(
    button: Button = "left",
    *,
    x: float | None = None,
    y: float | None = None,
    double: bool = False,
    interval: float = 0.08,
) -> None:
    """Click mouse button at current or supplied coordinates."""
    if button not in _MOUSE_BUTTONS:
        raise ValueError("button must be 'left' or 'right'")

    if x is None or y is None:
        x, y = get_position()

    count = 2 if double else 1
    for click_state in range(1, count + 1):
        down_event = Quartz.CGEventCreateMouseEvent(
            None,
            _DOWN_EVENTS[button],
            (float(x), float(y)),
            _MOUSE_BUTTONS[button],
        )
        up_event = Quartz.CGEventCreateMouseEvent(
            None,
            _UP_EVENTS[button],
            (float(x), float(y)),
            _MOUSE_BUTTONS[button],
        )
        Quartz.CGEventSetIntegerValueField(
            down_event,
            Quartz.kCGMouseEventClickState,
            click_state,
        )
        Quartz.CGEventSetIntegerValueField(
            up_event,
            Quartz.kCGMouseEventClickState,
            click_state,
        )
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)

        if double and click_state == 1:
            time.sleep(max(0.0, interval))


def left_click(*, x: float | None = None, y: float | None = None) -> None:
    click("left", x=x, y=y)


def right_click(*, x: float | None = None, y: float | None = None) -> None:
    click("right", x=x, y=y)


def double_click(*, x: float | None = None, y: float | None = None) -> None:
    click("left", x=x, y=y, double=True)
