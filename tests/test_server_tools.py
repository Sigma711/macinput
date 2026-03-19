import asyncio

import pytest
from mcp.server.fastmcp.exceptions import ToolError

import macinput.server as server_module


def _tool_schema_by_name(server):
    async def _main():
        tools = await server.list_tools()
        return {tool.name: tool.inputSchema for tool in tools}

    return asyncio.run(_main())


def test_press_keyboard_key_schema_accepts_string_or_integer():
    schema = _tool_schema_by_name(server_module.create_server())["press_keyboard_key"]
    key_schema = schema["properties"]["key"]
    assert {"type": "string"} in key_schema["anyOf"]
    assert {"type": "integer"} in key_schema["anyOf"]


def test_keyboard_key_tools_schema_accepts_string_or_integer():
    tools = _tool_schema_by_name(server_module.create_server())
    for name in ("keyboard_key_down", "keyboard_key_up"):
        key_schema = tools[name]["properties"]["key"]
        assert {"type": "string"} in key_schema["anyOf"]
        assert {"type": "integer"} in key_schema["anyOf"]


def test_scroll_mouse_schema_exists():
    tools = _tool_schema_by_name(server_module.create_server())
    schema = tools["scroll_mouse"]
    assert schema["properties"]["vertical"]["type"] == "integer"
    assert schema["properties"]["horizontal"]["type"] == "integer"


def test_press_keyboard_key_accepts_numeric_digit(monkeypatch):
    calls: list[tuple[object, object, object]] = []

    def fake_press_key(key, modifiers=None, hold=0.0):
        calls.append((key, modifiers, hold))

    monkeypatch.setattr(server_module, "press_key", fake_press_key)
    server = server_module.create_server()

    async def _main():
        await server.call_tool("press_keyboard_key", {"key": 3})

    asyncio.run(_main())

    assert calls == [("3", None, 0.0)]


def test_press_keyboard_key_rejects_non_digit_integer():
    server = server_module.create_server()

    async def _main():
        with pytest.raises(ToolError, match="single digits"):
            await server.call_tool("press_keyboard_key", {"key": 20})

    asyncio.run(_main())


def test_scroll_mouse_calls_core_scroll(monkeypatch):
    calls: list[tuple[int, int]] = []

    def fake_scroll(vertical=0, horizontal=0):
        calls.append((vertical, horizontal))

    monkeypatch.setattr(server_module, "scroll", fake_scroll)
    server = server_module.create_server()

    async def _main():
        await server.call_tool("scroll_mouse", {"vertical": -3, "horizontal": 1})

    asyncio.run(_main())

    assert calls == [(-3, 1)]
