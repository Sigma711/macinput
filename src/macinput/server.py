"""MCP server wrapper for macinput."""

from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any, Literal

from .keyboard import key_down, key_up, paste_text, press_key, type_text
from .mouse import click, get_position, move_to
from .screenshot import capture_screen, cleanup_screenshot
from .settings import ServerSettings

try:
    from mcp.server.fastmcp import FastMCP
except ImportError as exc:  # pragma: no cover - exercised only without MCP installed
    FastMCP = None  # type: ignore[assignment]
    _IMPORT_ERROR = exc
else:
    _IMPORT_ERROR = None


Button = Literal["left", "right"]

SERVER_INSTRUCTIONS = """
You control a macOS machine through keyboard, mouse, and screenshot tools.

Operate conservatively:
- Capture a screenshot before interacting with an unfamiliar screen.
- Prefer small, reversible actions.
- Confirm coordinates from the latest screenshot before clicking.
- Type only the minimum necessary text.
- Clean up screenshots after the host no longer needs them.
""".strip()

BEST_PRACTICES_TEXT = """
# macinput best practices

1. Observe first, then act. Take a screenshot before the first click on a new screen state.
2. Keep actions atomic. Prefer `move_mouse` + `click_mouse` over large speculative chains.
3. Re-check after mutations. If a click changes the UI, capture a new screenshot before the next decision.
4. Keep typing bounded. Paste or type only task-relevant text, never large opaque payloads.
5. Clean temporary screenshots. Remove them once the client or agent no longer needs the file.
6. Expect macOS permission failures. Accessibility and Screen Recording permissions are mandatory.
7. Slow down when uncertain. Small delays reduce missed clicks and stale-screen errors.
""".strip()

PERMISSIONS_TEXT = """
# Required macOS permissions

- Accessibility: required for keyboard and mouse event injection.
- Screen Recording: required for screenshots on recent macOS versions.

Grant both permissions to the host application that launches the MCP server, for example:
- Terminal / iTerm2
- Claude Desktop
- Cursor / VS Code
- Any custom launcher wrapping `macinput-mcp`
""".strip()


@dataclass
class ActionResult:
    ok: bool
    message: str


@dataclass
class MousePosition:
    x: float
    y: float


@dataclass
class ScreenshotResult:
    path: str
    cleanup_after: float | None


@dataclass
class SettingsResult:
    default_screenshot_ttl: float
    max_screenshot_ttl: float
    max_typing_length: int
    min_action_delay: float
    default_typing_interval: float


def _ensure_mcp_import() -> None:
    if FastMCP is None:
        raise RuntimeError(
            "The MCP SDK is not installed. Install dependencies with `uv sync` or "
            "`pip install -e .` using Python 3.10+."
        ) from _IMPORT_ERROR


def _sleep(settings: ServerSettings) -> None:
    if settings.min_action_delay > 0:
        time.sleep(settings.min_action_delay)


def _resolve_cleanup_after(settings: ServerSettings, cleanup_after: float | None) -> float | None:
    if cleanup_after is None:
        return None
    value = cleanup_after
    if value < 0:
        raise ValueError("cleanup_after must be >= 0 or None")
    if value > settings.max_screenshot_ttl:
        raise ValueError(
            f"cleanup_after must be <= MACINPUT_MAX_SCREENSHOT_TTL ({settings.max_screenshot_ttl})"
        )
    return value


def create_server(settings: ServerSettings | None = None) -> Any:
    _ensure_mcp_import()

    active_settings = (settings or ServerSettings.from_env()).validate()
    server = FastMCP(
        name="macinput",
        instructions=SERVER_INSTRUCTIONS,
    )

    @server.tool()
    def get_server_settings() -> SettingsResult:
        """Return the active safety-related server settings."""
        return SettingsResult(**active_settings.to_dict())

    @server.tool()
    def get_mouse_position() -> MousePosition:
        """Return the current mouse position."""
        x, y = get_position()
        return MousePosition(x=x, y=y)

    @server.tool()
    def move_mouse(x: float, y: float) -> ActionResult:
        """Move the cursor to absolute screen coordinates."""
        move_to(x, y)
        _sleep(active_settings)
        return ActionResult(ok=True, message=f"Moved mouse to ({x}, {y}).")

    @server.tool()
    def click_mouse(
        button: Button = "left",
        x: float | None = None,
        y: float | None = None,
        double: bool = False,
        interval: float = 0.08,
    ) -> ActionResult:
        """Click at the current cursor location or at explicit coordinates."""
        click(button=button, x=x, y=y, double=double, interval=interval)
        _sleep(active_settings)
        target = "current cursor position" if x is None or y is None else f"({x}, {y})"
        detail = "double click" if double else f"{button} click"
        return ActionResult(ok=True, message=f"Performed {detail} at {target}.")

    @server.tool()
    def press_keyboard_key(
        key: str,
        modifiers: list[str] | None = None,
        hold: float = 0.0,
    ) -> ActionResult:
        """Press and release a key with optional modifiers."""
        press_key(key, modifiers=modifiers, hold=hold)
        _sleep(active_settings)
        modifier_text = f" with modifiers {modifiers}" if modifiers else ""
        return ActionResult(ok=True, message=f"Pressed key `{key}`{modifier_text}.")

    @server.tool()
    def keyboard_key_down(key: str, modifiers: list[str] | None = None) -> ActionResult:
        """Hold a key down. Pair with `keyboard_key_up` if you need manual control."""
        key_down(key, modifiers=modifiers)
        _sleep(active_settings)
        return ActionResult(ok=True, message=f"Held key `{key}` down.")

    @server.tool()
    def keyboard_key_up(key: str, modifiers: list[str] | None = None) -> ActionResult:
        """Release a key previously pressed down."""
        key_up(key, modifiers=modifiers)
        _sleep(active_settings)
        return ActionResult(ok=True, message=f"Released key `{key}`.")

    @server.tool()
    def type_text_input(text: str, interval: float | None = None) -> ActionResult:
        """Type unicode text into the currently focused macOS input target."""
        if len(text) > active_settings.max_typing_length:
            raise ValueError(
                f"text is too long: {len(text)} > {active_settings.max_typing_length}"
            )
        resolved_interval = active_settings.default_typing_interval if interval is None else interval
        if resolved_interval < 0:
            raise ValueError("interval must be >= 0")
        type_text(text, interval=resolved_interval)
        _sleep(active_settings)
        return ActionResult(ok=True, message=f"Typed {len(text)} characters.")

    @server.tool()
    def paste_text_input(text: str, restore_clipboard: bool = True) -> ActionResult:
        """Paste plain text into the focused target via clipboard and Cmd+V."""
        if len(text) > active_settings.max_typing_length:
            raise ValueError(
                f"text is too long: {len(text)} > {active_settings.max_typing_length}"
            )
        paste_text(text, restore_clipboard=restore_clipboard)
        _sleep(active_settings)
        restore_note = " and restored clipboard text" if restore_clipboard else ""
        return ActionResult(
            ok=True,
            message=f"Pasted {len(text)} characters{restore_note}.",
        )

    @server.tool()
    def capture_screenshot(cleanup_after: float | None = None) -> ScreenshotResult:
        """Capture the full screen and return a temporary PNG path."""
        ttl = active_settings.default_screenshot_ttl if cleanup_after is None else cleanup_after
        resolved_ttl = _resolve_cleanup_after(active_settings, ttl)
        path = capture_screen(cleanup_after=resolved_ttl)
        return ScreenshotResult(path=path, cleanup_after=resolved_ttl)

    @server.tool()
    def cleanup_screenshot_file(path: str) -> ActionResult:
        """Remove a screenshot file created by `capture_screenshot`."""
        removed = cleanup_screenshot(path)
        return ActionResult(ok=removed, message=f"Removed screenshot: {removed}.")

    @server.resource("macinput://overview")
    def overview() -> str:
        return SERVER_INSTRUCTIONS

    @server.resource("macinput://best-practices")
    def best_practices() -> str:
        return BEST_PRACTICES_TEXT

    @server.resource("macinput://permissions")
    def permissions() -> str:
        return PERMISSIONS_TEXT

    @server.prompt()
    def ui_action_protocol(goal: str, current_context: str = "") -> str:
        """Guide an agent to use the server safely for a UI control task."""
        context_block = (
            f"Current context:\n{current_context.strip()}\n\n" if current_context.strip() else ""
        )
        return (
            "You are controlling a macOS UI through macinput.\n\n"
            f"Goal:\n{goal.strip()}\n\n"
            f"{context_block}"
            "Protocol:\n"
            "1. Capture a screenshot before the first click or key action.\n"
            "2. Inspect the latest screenshot and identify the exact target.\n"
            "3. Prefer one atomic action at a time.\n"
            "4. Capture a new screenshot after any action that may change the UI.\n"
            "5. Stop and reassess when the screen differs from expectation.\n"
            "6. Clean up temporary screenshot files when done.\n"
        )

    return server


def get_server_metadata(settings: ServerSettings | None = None) -> dict[str, Any]:
    active_settings = (settings or ServerSettings.from_env()).validate()
    return {
        "name": "macinput",
        "instructions": SERVER_INSTRUCTIONS,
        "settings": asdict(active_settings),
        "resources": [
            "macinput://overview",
            "macinput://best-practices",
            "macinput://permissions",
        ],
        "prompt": "ui_action_protocol",
    }
