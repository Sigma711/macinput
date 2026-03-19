# macinput MCP 工程化说明

Language: [English](mcp-engineering.md) | [中文](mcp-engineering.zh-CN.md)

## 项目定位

`macinput` 是一个仅面向 macOS 的自动化服务，通过 MCP 暴露键盘、鼠标和截图原语。项目分为两层：

- 核心自动化库：直接封装 Quartz 和 `screencapture`
- MCP 服务层：面向 AI Agent 的校验、文档化、带节流策略的工具包装

这样的拆分可以保留底层代码的可复用性，同时让 MCP 接口独立演进。

## 推荐的服务边界

当前导出的 MCP 能力刻意保持精简：

- `get_mouse_position`
- `move_mouse`
- `click_mouse`
- `scroll_mouse`
- `press_keyboard_key`
- `keyboard_key_down`
- `keyboard_key_up`
- `type_text_input`
- `paste_text_input`
- `capture_screenshot`
- `cleanup_screenshot_file`
- `get_server_settings`

这是一个比较实际的 UI 控制边界：

- 足以操作任意 macOS 应用
- 足够小，便于 Agent 规划与解释
- 足够克制，能降低误操作风险

对于键盘相关 tool，MCP 层同时接受字符串数字键（如 `"3"`）和数字输入（如 `3`），并统一规范化为数字键本身，避免宿主把单个数字序列化成 JSON number 时出现脆弱校验失败。

## 安全默认值

服务器通过环境变量应用保守的运行时配置：

- `MACINPUT_DEFAULT_SCREENSHOT_TTL`
- `MACINPUT_MAX_SCREENSHOT_TTL`
- `MACINPUT_MAX_TYPING_LENGTH`
- `MACINPUT_MIN_ACTION_DELAY`
- `MACINPUT_DEFAULT_TYPING_INTERVAL`

这些配置是给运维者和集成方的，不是给最终用户逐项调参的。它们把主机级策略固化成运行时约束，而不需要改代码。

## 用户和 Agent 的最佳实践

### 用户侧

1. 第一次使用前先授予 Accessibility 和 Screen Recording 权限。
2. 除非明确需要网络传输，否则优先使用 `stdio`。
3. 运行时保持宿主会话处于解锁状态，并停留在预期的桌面空间。
4. 把截图视为敏感数据，保留时间尽量短。
5. 如果自动化可能触达敏感应用，优先使用独立的 macOS 账号或虚拟机。

### Agent 侧

1. 先观察再行动，未知界面先截图。
2. 每次只做一个状态改变动作。
3. 点击、快捷键或提交文本后重新截图。
4. 避免在界面切换后继续复用缓存坐标。
5. 保持输入文本简短且任务相关。
6. 当前步骤结束后清理截图。
7. 当界面与预期不符时停止，而不是继续叠加错误。

## 传输建议

以下场景默认使用 `stdio`：

- Claude Desktop
- Cursor
- VS Code MCP Host
- 本地子进程式调度器

只有在以下情况才建议使用 `streamable-http`：

- 宿主应用不能拉起子进程 MCP 服务
- 你需要把服务挂在内部自动化网关之后

## 建议的发布与运维流程

1. `uv sync`
2. `uv run pytest`
3. `uv run ruff check .`
4. 在已授权的真实 macOS 会话中验证
5. 至少完成一个桌面 MCP Host 的 `stdio` 集成测试
6. 打版本标签并发布包

## 兼容性说明

- 当前 MCP SDK 需要 Python 3.10 及以上
- 服务必须运行在真实的 macOS 图形会话中
- 无头 CI 可以验证导入、配置和文档，但无法完整验证 UI 注入行为
