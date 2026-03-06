"""macinput package exports."""

from .keyboard import key_down, key_up, paste_text, press_key, type_text
from .mouse import click, double_click, get_position, left_click, move_to, right_click
from .screenshot import capture_screen, cleanup_screenshot

__all__ = [
    "move_to",
    "get_position",
    "click",
    "left_click",
    "right_click",
    "double_click",
    "type_text",
    "paste_text",
    "key_down",
    "key_up",
    "press_key",
    "capture_screen",
    "cleanup_screenshot",
]
