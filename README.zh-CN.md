# macinput

Language: [English](README.md) | [中文](README.zh-CN.md)

`macinput` 是一个面向 AI Agent 的 macOS 键盘、鼠标与截图控制工具。当前仓库已经整理为一个可安装的 Python 项目，并提供工程化的 MCP Server，使桌面 Agent 可以通过标准 MCP 调用来模拟人类操作 macOS 图形界面。

项目目标有两个：

- 作为底层能力库，提供稳定的 macOS 键鼠控制与截图接口。
- 作为 MCP Server，提供适合 AI Agent 使用的工具契约、运行时安全边界与接入文档。

## 能力范围

- 鼠标移动、单击、双击、右击
- 获取当前鼠标坐标
- 键盘按键按下、释放、组合键
- Unicode 文本输入
- 基于剪贴板的粘贴输入
- 全屏截图与临时文件自动清理
- MCP resources 与 prompt，用于向 Agent 注入使用规范

## 适用场景

- 桌面 AI Agent 控制 macOS 应用
- 自动化 UI 测试原型
- 人机协同操作桌面软件
- 需要截图观察加键鼠执行闭环的 Agent 工作流

## 系统要求

- macOS
- Python 3.10 及以上
- 已授予启动进程以下系统权限
  - Accessibility
  - Screen Recording

注意：权限是授予“启动 MCP Server 的宿主程序”，而不只是 Python 本身。例如你通过 Claude Desktop、Terminal、iTerm2、Cursor 或 VS Code 启动它，就需要给对应宿主授权。

## 安装

### `uv`

```bash
uv sync
```

### `pip`

```bash
python -m pip install -e .
```

## 启动 MCP Server

默认推荐 `stdio`，这也是大多数桌面 Agent 客户端的首选方式。

```bash
macinput-mcp
```

如果你的 MCP Host 需要 HTTP transport，可以使用：

```bash
macinput-mcp --transport streamable-http --host 127.0.0.1 --port 8000 --path /mcp
```

## MCP 客户端配置示例

下面是一个通用的 `stdio` 型 MCP 配置示例，适合支持命令式启动的客户端：

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

如果你已经把项目安装到当前 Python 环境，也可以直接使用：

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

## 可用 Tools

- `get_server_settings`
- `get_mouse_position`
- `move_mouse`
- `click_mouse`
- `press_keyboard_key`
- `keyboard_key_down`
- `keyboard_key_up`
- `type_text_input`
- `paste_text_input`
- `capture_screenshot`
- `cleanup_screenshot_file`

## 可用 Resources 与 Prompt

Resources:

- `macinput://overview`
- `macinput://best-practices`
- `macinput://permissions`

Prompt:

- `ui_action_protocol(goal, current_context="")`

这部分不是装饰，而是服务的一部分。它可以把 Agent 使用规范和服务器一起分发，避免每个客户端都重复编写系统提示词。

## 推荐使用方式

对于用户：

1. 优先通过 `stdio` 把服务接到桌面 Agent。
2. 在真实工作环境中先确认权限已经授予。
3. 尽量把自动化运行在独立 macOS 账号、测试机或虚拟机中。
4. 把截图 TTL 设短一些，避免遗留敏感数据。

对于 Agent：

1. 先截图，再操作。
2. 每次只做一个状态改变动作。
3. 点击、快捷键、输入之后重新截图。
4. 不要在 UI 已变化时继续复用旧坐标。
5. 文本输入保持短小、明确、任务相关。
6. 用完截图及时清理。

## 环境变量

- `MACINPUT_DEFAULT_SCREENSHOT_TTL`
  - 默认截图自动清理秒数，默认 `30`
- `MACINPUT_MAX_SCREENSHOT_TTL`
  - 允许的最大截图保留秒数，默认 `300`
- `MACINPUT_MAX_TYPING_LENGTH`
  - 单次输入最大字符数，默认 `2000`
- `MACINPUT_MIN_ACTION_DELAY`
  - 每次 tool 执行后的最小延迟，默认 `0.05`
- `MACINPUT_DEFAULT_TYPING_INTERVAL`
  - 文本输入字符间隔，默认 `0.02`

## 作为 Python 库直接使用

```python
from macinput import click, move_to, press_key, type_text, capture_screen

move_to(400, 300)
click()
type_text("hello macOS")
press_key("a", modifiers=["command"])
path = capture_screen(cleanup_after=10)
print(path)
```

## 开发说明

### 项目结构

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

### 本地开发

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

### GitHub Actions

- CI 工作流：[`.github/workflows/ci.yml`](.github/workflows/ci.yml)
- Release 工作流：[`.github/workflows/release.yml`](.github/workflows/release.yml)

CI 会在 `push` 和 `pull_request` 时执行 lint 与测试。Release workflow 会在 `workflow_dispatch` 和版本标签（例如 `v0.1.0`）触发时构建分发包、上传工件，并在仓库配置了 trusted publishing 时发布到 PyPI。

### 开发原则

- 底层控制逻辑与 MCP 暴露层分离
- MCP tools 保持小而稳定
- 默认优先 `stdio`
- 所有状态变化动作都应可解释、可组合、可恢复
- 文档必须覆盖用户接入与开发者维护两个维度

## 文档

- 工程化与最佳实践文档：[docs/mcp-engineering.zh-CN.md](docs/mcp-engineering.zh-CN.md)
- 用户接入手册：[docs/user-guide.zh-CN.md](docs/user-guide.zh-CN.md)
- Agent 使用准则：[docs/agent-best-practices.zh-CN.md](docs/agent-best-practices.zh-CN.md)
- 开发维护手册：[docs/developer-guide.zh-CN.md](docs/developer-guide.zh-CN.md)

## 已知限制

- 只支持 macOS
- 必须运行在有图形会话的真实桌面环境
- CI 很难完整覆盖 UI 注入行为，真实机器验证仍然必要
- `paste_text_input` 通过系统剪贴板工作，当前只保留并恢复纯文本剪贴板内容
- 不包含 OCR、元素识别或窗口语义理解，这些应由上层 Agent 负责

## 面向维护者的建议

1. 增加 `LICENSE`
2. 增加发布自动化
3. 在真实 macOS runner 上增加冒烟测试
4. 增加常见 MCP Host 的 `examples/`
5. 增加可选的区域截图、输出目录和审计日志
