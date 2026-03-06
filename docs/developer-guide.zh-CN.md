# macinput 开发者手册

Language: [English](developer-guide.md) | [中文](developer-guide.zh-CN.md)

## 架构

仓库分成两层：

- `src/macinput/keyboard.py`、`mouse.py`、`screenshot.py`
  - 底层 macOS 自动化原语
- `src/macinput/server.py`、`cli.py`、`settings.py`
  - MCP 服务接口、输入校验、默认策略和运行时配置

这是刻意设计的分层。底层应尽量简单并贴近系统 API；服务层应负责：

- tool 命名
- 输入校验
- 安全默认值
- 面向运维的配置
- MCP resources 和 prompts

## 开发流程

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
```

## GitHub Actions

仓库已经包含：

- [`.github/workflows/ci.yml`](../.github/workflows/ci.yml)
  - 在 `push` 和 `pull_request` 时执行 lint 与测试
- [`.github/workflows/release.yml`](../.github/workflows/release.yml)
  - 在手动触发或版本标签时构建 `sdist` 和 `wheel`
  - 如果仓库配置了 trusted publishing，则在 `v*` 标签时发布到 PyPI

这些 workflow 刻意不做 GUI 注入类测试，因为 GitHub 托管 runner 不提供稳定、已授权的 macOS 图形桌面环境来完成端到端输入自动化验证。

## 扩展服务时的规则

新增 MCP tool 时：

1. 只有在系统交互逻辑确实可复用时，才新增或复用底层原语。
2. MCP tool 保持小而可组合。
3. 所有输入校验放在服务层。
4. 在 `README.md` 中补文档。
5. 判断是否需要同步更新 resource 或 prompt。

## Tool 设计原则

优先：

- 显式参数
- 小而可逆的动作
- 能帮助 Agent 决策下一步的输出

避免：

- 多步骤的大而全工具
- 把宿主特定行为偷偷塞进工具内部
- 在未观察界面的情况下猜测 UI 状态

## 测试策略

### 适合在 CI 中自动化的内容

- 导入测试
- 配置校验
- 元数据结构
- 文档检查

### 必须在真实 macOS 环境验证的内容

- 键盘注入
- 鼠标移动和点击
- 截图能力
- 权限不足时的行为

## 建议的后续工程化工作

1. 增加 `LICENSE`
2. 为常见 MCP Host 增加 `examples/`
3. 在 macOS runner 上增加冒烟测试
4. 增加可选区域截图
5. 为受监管环境增加可选审计日志
