# macinput 用户手册

Language: [English](user-guide.md) | [中文](user-guide.zh-CN.md)

## 这个服务是做什么的

`macinput` 通过 MCP 向兼容客户端暴露 macOS 的键盘、鼠标和截图控制能力。

适合以下场景：

- 让 Agent 通过截图观察当前桌面
- 点击或移动鼠标
- 输入文本或触发快捷键
- 向不稳定响应直接键入事件的输入框粘贴短文本

## 首次使用前

### 1. 确认 macOS 权限

给启动服务的应用授予以下权限：

- Accessibility
- Screen Recording

常见宿主：

- Terminal / iTerm2
- Claude Desktop
- Cursor
- VS Code

如果权限缺失：

- 键鼠工具可能静默失效
- 截图工具可能直接报权限错误

### 2. 在真实 GUI 会话中运行

服务必须运行在激活的 macOS 桌面会话中，不适合无头或锁屏环境。

## 安装

```bash
uv sync
```

或者：

```bash
python -m pip install -e .
```

## 启动服务

### 推荐：`stdio`

```bash
macinput-mcp
```

### 可选：`streamable-http`

```bash
macinput-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

## MCP 客户端配置示例

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

## 运行时控制

环境变量：

- `MACINPUT_DEFAULT_SCREENSHOT_TTL`
- `MACINPUT_MAX_SCREENSHOT_TTL`
- `MACINPUT_MAX_TYPING_LENGTH`
- `MACINPUT_MIN_ACTION_DELAY`
- `MACINPUT_DEFAULT_TYPING_INTERVAL`

示例：

```bash
MACINPUT_DEFAULT_SCREENSHOT_TTL=15 MACINPUT_MAX_TYPING_LENGTH=500 macinput-mcp
```

## 使用建议

1. 尽量使用独立 macOS 账号或测试机。
2. 把截图保留时间设短。
3. 当 Agent 不需要时，不要让敏感应用暴露在当前桌面。
4. 除非宿主明确要求 HTTP，否则优先使用 `stdio`。
5. 输入文本前确认当前焦点，因为文本总是发送给当前聚焦应用。
6. 如果目标应用对 `type_text_input` 响应不稳定，优先使用 `paste_text_input`。

## 故障排查

### 截图失败

检查宿主应用是否获得了 Screen Recording 权限。

### 键鼠工具没有效果

检查宿主应用是否获得了 Accessibility 权限。

### Agent 点错位置

要求 Agent 在每次界面变化后点击前都重新截图。

### 导入或安装失败

请使用 Python 3.10 及以上。当前 MCP SDK 不支持更老的 Python 版本。
