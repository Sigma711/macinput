# macinput user guide

Language: [English](user-guide.md) | [中文](user-guide.zh-CN.md)

## What this server is for

`macinput` exposes macOS keyboard, mouse, and screenshot control to MCP-compatible AI clients.

Use it when your agent needs to:

- inspect the current macOS desktop through screenshots
- click or move the mouse
- scroll vertically or horizontally
- type text or send shortcuts
- paste short text into inputs that do not reliably accept direct typing events

## Before first use

### 1. Confirm macOS permissions

Grant these permissions to the application that launches the server:

- Accessibility
- Screen Recording

Common launchers:

- Terminal / iTerm2
- Claude Desktop
- Cursor
- VS Code

If permissions are missing:

- mouse and keyboard tools may silently do nothing
- screenshot capture may fail with a permission error

### 2. Run in a real GUI session

The server must run in an active macOS desktop session. It is not intended for headless or locked-screen execution.

## Installation

```bash
uv sync
```

Or:

```bash
python -m pip install -e .
```

## Start the server

### Recommended: stdio

```bash
macinput-mcp
```

### Optional: streamable HTTP

```bash
macinput-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

## Example MCP client config

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

## Runtime controls

Environment variables:

- `MACINPUT_DEFAULT_SCREENSHOT_TTL`
- `MACINPUT_MAX_SCREENSHOT_TTL`
- `MACINPUT_MAX_TYPING_LENGTH`
- `MACINPUT_MIN_ACTION_DELAY`
- `MACINPUT_DEFAULT_TYPING_INTERVAL`

Example:

```bash
MACINPUT_DEFAULT_SCREENSHOT_TTL=15 MACINPUT_MAX_TYPING_LENGTH=500 macinput-mcp
```

## Operational recommendations

1. Use a dedicated macOS account or test machine when possible.
2. Keep screenshot retention short.
3. Avoid leaving sensitive apps visible when the agent does not need them.
4. Prefer `stdio` unless your host requires HTTP.
5. Verify focus before typing, because typing always goes to the currently focused app.
6. Prefer `paste_text_input` when a target app ignores or inconsistently handles `type_text_input`.

## Troubleshooting

### Screenshot tool fails

Check Screen Recording permission for the host app.

### Mouse and keyboard tools do nothing

Check Accessibility permission for the host app.

### Agent clicks the wrong place

Require the agent to capture a fresh screenshot before every click on a changed screen.

### Import or install fails

Use Python 3.10 or newer. Current MCP SDK releases do not target older Python versions.
