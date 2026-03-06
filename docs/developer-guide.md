# macinput developer guide

Language: [English](developer-guide.md) | [中文](developer-guide.zh-CN.md)

## Architecture

The repository is split into two layers:

- `src/macinput/keyboard.py`, `mouse.py`, `screenshot.py`
  - low-level macOS automation primitives
- `src/macinput/server.py`, `cli.py`, `settings.py`
  - MCP server surface, validation, defaults, and runtime policy

This separation is deliberate. The low-level layer should stay simple and close to system APIs. The server layer should own:

- tool naming
- input validation
- safe defaults
- operator-facing configuration
- MCP resources and prompts

## Development workflow

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## GitHub Actions

The repository includes:

- [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
  - runs lint and tests on `push` and `pull_request`
- [`.github/workflows/release.yml`](../.github/workflows/release.yml)
  - builds `sdist` and `wheel` artifacts on manual dispatch or version tags
  - publishes to PyPI on `v*` tags if trusted publishing is configured

These workflows intentionally avoid GUI injection tests because GitHub-hosted runners do not provide a reliable, permissioned macOS desktop session for end-to-end input automation.

## Extending the server

When adding a new MCP tool:

1. Add or reuse a low-level primitive only if the system interaction is genuinely reusable.
2. Keep the MCP tool small and composable.
3. Validate all inputs in the server layer.
4. Document the tool in `README.md`.
5. Decide whether the capability also needs a resource or prompt update.

## Tool design rules

Prefer:

- explicit parameters
- small reversible actions
- outputs that help the agent decide the next step

Avoid:

- monolithic multi-step tools
- host-specific behavior hidden inside tools
- tools that guess UI state without observation

## Testing strategy

### Safe to automate in CI

- import tests
- config validation
- metadata shape
- docs linting

### Requires real macOS validation

- keyboard injection
- mouse movement and clicking
- screenshot capture
- permission-denied behavior

## Suggested next engineering steps

1. Add `LICENSE`.
2. Add `examples/` for common MCP hosts.
3. Add smoke tests on a macOS runner.
4. Add optional region screenshot support.
5. Add optional audit logging for regulated environments.
