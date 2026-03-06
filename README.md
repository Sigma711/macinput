# macinput

Language: [English](README.md) | [中文](README.zh-CN.md)

`macinput` is a macOS keyboard, mouse, and screenshot control tool for AI agents. This repository is now structured as an installable Python project and an MCP server so desktop agents can control a macOS GUI through standard MCP tool calls.

The project has two goals:

- Provide stable low-level macOS input and screenshot primitives.
- Provide an MCP server with a practical tool surface, runtime safety limits, and deployment guidance.

## Features

- Mouse move, left click, right click, and double click
- Current mouse position lookup
- Key press, key down, key up, and modifier combinations
- Unicode text input
- Full-screen screenshots with automatic cleanup
- MCP resources and prompt templates for agent guidance

## Use cases

- Desktop AI agents controlling macOS applications
- UI automation prototypes
- Human-in-the-loop desktop workflows
- Screenshot-observe plus keyboard/mouse-act agent loops

## Requirements

- macOS
- Python 3.10+
- The launching host app must have:
  - Accessibility permission
  - Screen Recording permission

Important: permissions apply to the program that launches the MCP server, not only to Python. If you launch through Claude Desktop, Terminal, iTerm2, Cursor, or VS Code, that host app must be granted permission.

## Installation

### `uv`

```bash
uv sync
```

### `pip`

```bash
python -m pip install -e .
```

## Run the MCP server

`stdio` is the recommended default for desktop AI clients:

```bash
macinput-mcp
```

If your MCP host requires HTTP transport:

```bash
macinput-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

## Example MCP client config

Generic `stdio` configuration:

```json
{
  "mcpServers": {
    "macinput": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/macinput",
        "run",
        "macinput-mcp"
      ]
    }
  }
}
```

If the package is already installed into the current environment:

```json
{
  "mcpServers": {
    "macinput": {
      "command": "macinput-mcp",
      "args": []
    }
  }
}
```

## Available tools

- `get_server_settings`
- `get_mouse_position`
- `move_mouse`
- `click_mouse`
- `press_keyboard_key`
- `keyboard_key_down`
- `keyboard_key_up`
- `type_text_input`
- `capture_screenshot`
- `cleanup_screenshot_file`

## Available resources and prompt

Resources:

- `macinput://overview`
- `macinput://best-practices`
- `macinput://permissions`

Prompt:

- `ui_action_protocol(goal, current_context="")`

These are part of the product surface, not decoration. They let hosts ship usage guidance together with the server instead of rewriting it in every system prompt.

## Recommended usage

For users:

1. Prefer `stdio` for desktop agent integrations.
2. Verify macOS permissions before the first real run.
3. Prefer a dedicated macOS account, test machine, or VM for automation.
4. Keep screenshot TTLs short to reduce data residue.

For agents:

1. Capture a screenshot before acting.
2. Make one state-changing action at a time.
3. Capture a fresh screenshot after clicks, shortcuts, or text submission.
4. Do not reuse old coordinates after the UI changes.
5. Keep typed text short and task-specific.
6. Clean up screenshots when they are no longer needed.

## Environment variables

- `MACINPUT_DEFAULT_SCREENSHOT_TTL`
  - Default screenshot cleanup timeout in seconds. Default: `30`
- `MACINPUT_MAX_SCREENSHOT_TTL`
  - Maximum allowed screenshot retention in seconds. Default: `300`
- `MACINPUT_MAX_TYPING_LENGTH`
  - Maximum characters per typing action. Default: `2000`
- `MACINPUT_MIN_ACTION_DELAY`
  - Minimum delay after each tool action. Default: `0.05`
- `MACINPUT_DEFAULT_TYPING_INTERVAL`
  - Default per-character typing interval. Default: `0.02`

## Use as a Python library

```python
from macinput import click, move_to, press_key, type_text, capture_screen

move_to(400, 300)
click()
type_text("hello macOS")
press_key("a", modifiers=["command"])
path = capture_screen(cleanup_after=10)
print(path)
```

## Development

### Project layout

```text
src/macinput/
  __init__.py
  __main__.py
  cli.py
  keyboard.py
  mouse.py
  screenshot.py
  server.py
  settings.py
docs/
  mcp-engineering.md
tests/
```

### Local workflow

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

### GitHub Actions

- CI workflow: [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Release workflow: [`.github/workflows/release.yml`](.github/workflows/release.yml)

The CI workflow runs lint and tests on `push` and `pull_request`. The release workflow builds distributions on `workflow_dispatch` and on version tags such as `v0.1.0`, then uploads artifacts and publishes to PyPI if your repository is configured for trusted publishing.

### Project rules

- Keep low-level automation separate from the MCP server layer.
- Keep MCP tools small and stable.
- Prefer `stdio` by default.
- Keep state-changing actions explainable and composable.
- Document both user integration and developer maintenance workflows.

## Documentation

- Engineering notes: [docs/mcp-engineering.md](docs/mcp-engineering.md)
- User guide: [docs/user-guide.md](docs/user-guide.md)
- Agent best practices: [docs/agent-best-practices.md](docs/agent-best-practices.md)
- Developer guide: [docs/developer-guide.md](docs/developer-guide.md)

## Limitations

- macOS only
- Requires a real GUI session
- CI can validate imports and configuration, but real machine validation is still necessary for UI injection
- Does not include OCR, UI element detection, or semantic window understanding

## Recommended follow-up work

1. Add `LICENSE`.
2. Add release automation.
3. Add smoke tests on a real macOS runner.
4. Add an `examples/` directory for common MCP hosts.
5. Add optional region screenshots, output directories, and audit logging.
