# macinput MCP engineering notes

Language: [English](mcp-engineering.md) | [中文](mcp-engineering.zh-CN.md)

## Positioning

`macinput` is a macOS-only automation server that exposes keyboard, mouse, and screenshot primitives through MCP. The project separates two layers:

- Core automation library: direct wrappers around Quartz and `screencapture`.
- MCP server layer: validated, documented, rate-limited tool wrappers intended for AI agents.

This split keeps the low-level code reusable while allowing the MCP surface to evolve independently.

## Recommended server surface

The exported MCP capabilities are intentionally small:

- `get_mouse_position`
- `move_mouse`
- `click_mouse`
- `press_keyboard_key`
- `keyboard_key_down`
- `keyboard_key_up`
- `type_text_input`
- `capture_screenshot`
- `cleanup_screenshot_file`
- `get_server_settings`

This is the practical boundary for a UI-control server:

- enough control to operate arbitrary macOS apps
- small enough to keep agent plans interpretable
- minimal enough to reduce accidental destructive actions

## Safety defaults

The server applies conservative runtime settings through environment variables:

- `MACINPUT_DEFAULT_SCREENSHOT_TTL`
- `MACINPUT_MAX_SCREENSHOT_TTL`
- `MACINPUT_MAX_TYPING_LENGTH`
- `MACINPUT_MIN_ACTION_DELAY`
- `MACINPUT_DEFAULT_TYPING_INTERVAL`

These settings are intended for operators, not end users. They encode host-level policy without forcing custom code changes.

## Best practices for users and agent builders

### User-side best practices

1. Grant Accessibility and Screen Recording permissions before first use.
2. Run the server over `stdio` for desktop AI clients unless you explicitly need network transport.
3. Keep the host session unlocked and on the expected Space/Desktop.
4. Treat screenshot files as sensitive data and keep TTLs short.
5. Prefer a dedicated macOS user account or VM when automation can touch sensitive apps.

### Agent-side best practices

1. Always observe before acting: take a screenshot on every unknown screen state.
2. Use one state-changing action at a time.
3. Re-screenshot after a click, shortcut, or text submission.
4. Avoid cached coordinates across screen transitions.
5. Keep typing short and task-specific.
6. Clean up screenshots when the task step completes.
7. Stop when the UI diverges from expectation rather than compounding errors.

## Transport recommendation

Use `stdio` as the default transport for:

- Claude Desktop
- Cursor
- VS Code MCP hosts
- local orchestrators launching subprocesses

Use `streamable-http` only when:

- the host application cannot spawn subprocess MCP servers
- you need to multiplex the server behind an internal automation gateway

## Suggested release and operational workflow

1. `uv sync`
2. `uv run pytest`
3. `uv run ruff check .`
4. Validate on a real macOS session with permissions enabled.
5. Test one desktop host integration over `stdio`.
6. Cut a version tag and publish the package.

## Compatibility notes

- Python 3.10+ is required for current MCP SDK releases.
- The server requires a real macOS GUI session.
- Headless CI can validate imports, config, and docs, but not UI injection behavior.
