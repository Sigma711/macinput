"""Keyboard control helpers built on macOS CGEvent APIs."""

from __future__ import annotations

import time
from typing import Iterable

import Quartz


_KEYCODES: dict[str, int] = {
    "a": 0,
    "s": 1,
    "d": 2,
    "f": 3,
    "h": 4,
    "g": 5,
    "z": 6,
    "x": 7,
    "c": 8,
    "v": 9,
    "b": 11,
    "q": 12,
    "w": 13,
    "e": 14,
    "r": 15,
    "y": 16,
    "t": 17,
    "1": 18,
    "2": 19,
    "3": 20,
    "4": 21,
    "6": 22,
    "5": 23,
    "=": 24,
    "9": 25,
    "7": 26,
    "-": 27,
    "8": 28,
    "0": 29,
    "]": 30,
    "o": 31,
    "u": 32,
    "[": 33,
    "i": 34,
    "p": 35,
    "l": 37,
    "j": 38,
    "'": 39,
    "k": 40,
    ";": 41,
    "\\": 42,
    ",": 43,
    "/": 44,
    "n": 45,
    "m": 46,
    ".": 47,
    "tab": 48,
    "space": 49,
    "return": 36,
    "enter": 76,
    "escape": 53,
    "delete": 51,
    "forward_delete": 117,
    "left": 123,
    "right": 124,
    "down": 125,
    "up": 126,
    "home": 115,
    "end": 119,
    "page_up": 116,
    "page_down": 121,
    "f1": 122,
    "f2": 120,
    "f3": 99,
    "f4": 118,
    "f5": 96,
    "f6": 97,
    "f7": 98,
    "f8": 100,
    "f9": 101,
    "f10": 109,
    "f11": 103,
    "f12": 111,
}

_MODIFIER_FLAGS: dict[str, int] = {
    "command": Quartz.kCGEventFlagMaskCommand,
    "cmd": Quartz.kCGEventFlagMaskCommand,
    "shift": Quartz.kCGEventFlagMaskShift,
    "option": Quartz.kCGEventFlagMaskAlternate,
    "alt": Quartz.kCGEventFlagMaskAlternate,
    "control": Quartz.kCGEventFlagMaskControl,
    "ctrl": Quartz.kCGEventFlagMaskControl,
    "fn": Quartz.kCGEventFlagMaskSecondaryFn,
}


def _keycode_for(key: str | int) -> int:
    if isinstance(key, int):
        return key
    value = _KEYCODES.get(key.lower())
    if value is None:
        raise ValueError(f"Unsupported key: {key}")
    return value


def _build_flags(modifiers: Iterable[str] | None) -> int:
    flags = 0
    for modifier in modifiers or ():
        value = _MODIFIER_FLAGS.get(modifier.lower())
        if value is None:
            raise ValueError(f"Unsupported modifier: {modifier}")
        flags |= value
    return flags


def key_down(key: str | int, modifiers: Iterable[str] | None = None) -> None:
    keycode = _keycode_for(key)
    flags = _build_flags(modifiers)
    event = Quartz.CGEventCreateKeyboardEvent(None, keycode, True)
    if flags:
        Quartz.CGEventSetFlags(event, flags)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def key_up(key: str | int, modifiers: Iterable[str] | None = None) -> None:
    keycode = _keycode_for(key)
    flags = _build_flags(modifiers)
    event = Quartz.CGEventCreateKeyboardEvent(None, keycode, False)
    if flags:
        Quartz.CGEventSetFlags(event, flags)
    Quartz.CGEventPost(Quartz.kCGHIDEventTap, event)


def press_key(
    key: str | int,
    modifiers: Iterable[str] | None = None,
    *,
    hold: float = 0.0,
) -> None:
    """Press and release a key with optional modifiers."""
    key_down(key, modifiers=modifiers)
    if hold > 0:
        time.sleep(hold)
    key_up(key, modifiers=modifiers)


def type_text(text: str, *, interval: float = 0.0) -> None:
    """Type unicode text using keyboard events."""
    source = Quartz.CGEventSourceCreate(Quartz.kCGEventSourceStateCombinedSessionState)
    for char in text:
        down_event = Quartz.CGEventCreateKeyboardEvent(source, 0, True)
        up_event = Quartz.CGEventCreateKeyboardEvent(source, 0, False)
        Quartz.CGEventKeyboardSetUnicodeString(down_event, len(char), char)
        Quartz.CGEventKeyboardSetUnicodeString(up_event, len(char), char)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, down_event)
        Quartz.CGEventPost(Quartz.kCGHIDEventTap, up_event)

        if interval > 0:
            time.sleep(interval)
