# MCP 与开发工具链验证报告（交付版）

**验证日期：** 2026-04-08  
**验证环境：** Windows（本机命令行），仓库路径 `CUHKSZ-GroupDiscussionSystem`  
**范围说明：** 区分 **Cursor 内置能力**、**本机 Shell 工具链**、**仓库内 `.cursor/mcp.json` 声明的 MCP**。未在 Cursor UI 内对 MCP 工具做逐条点击测试；MCP 服务端进程用命令行做了**可启动性**探测。

**禁止事项（本报告遵守）：** 未伪造结果；未修改业务代码；未记录任何真实 token、本机绝对路径或浏览器缓存内容。

---

## 1. 能力矩阵最终版

| 能力 | 实现方式（内置 / MCP / 本机 CLI） | 配置位置 | 验证命令 / 方法 | 状态 |
|------|-----------------------------------|----------|-----------------|------|
| 文件读写（工作区） | **内置**：Cursor 编辑器与 Agent 默认文件工具（非 MCP 专属） | 无仓库 JSON | 日常编辑与 Agent 读写 | **可用**（IDE 能力，未做独立 CLI 单测） |
| 文件读写（MCP 限定目录） | **MCP**：`project-code` → `@modelcontextprotocol/server-filesystem`，根为 `app/`、`docs/`、`tests/` | `.cursor/mcp.json` | `npx -y @modelcontextprotocol/server-filesystem app docs tests`（出现 `Secure MCP Filesystem Server running on stdio` 后需 Ctrl+C；由 Cursor 作为客户端连接） | **包可启动**；**未**在 Cursor 内对 list/read/write 做端到端工具调用验证 |
| 全局搜索 / 符号搜索 | **内置**：Cursor / VS Code 搜索、索引、语言服务 | 可选 `.cursorignore` 影响索引范围 | 无标准 CLI；使用 IDE「搜索 / 转到符号」 | **未自动化验证**（属 IDE 行为） |
| Shell 命令执行 | **内置**：Agent `run_terminal_cmd` 类能力 | 无仓库配置 | `echo shell_ok` → 输出 `shell_ok` | **通过** |
| `git status` / `git diff` | **内置**：Agent Shell | 无仓库配置 | `git status -sb`；`git diff --stat`（工作区无已跟踪文件变更时 diff 为空属正常） | **通过**（当时仅有未跟踪 `.cursor/`、`.cursorignore`） |
| Python / pytest | **本机 Python** + 项目测试 | `pyproject.toml`；虚拟环境为用户级 | `python --version` → `Python 3.11.3`；`python -m pytest -q --tb=no` → exit 0 | **通过**（**172** 个用例收集，全量运行通过） |
| node / npm / pnpm | **本机** | 用户级安装 | `node --version` → `v24.14.1`；`npm --version` → `11.11.0`；`pnpm --version` → `10.28.2` | **通过** |
| HTTP / OpenAPI / `GET /health` | **应用内**：FastAPI `TestClient`（不启动真实端口） | `app/api/` | `python -c`：`TestClient(create_app()).get("/health")` 已由 `tests/test_api_system_info.py` 覆盖；另测 `GET /openapi.json` → **200** 且 JSON 含 `openapi` 键 | **通过** |
| Browser / Playwright | **未**在仓库 `.cursor/mcp.json` 中配置 Browser MCP；**本机** `npx playwright --version` 可用 | 无仓库 MCP 项 | `npx playwright --version` → `Version 1.59.1`（首次执行时 npm 拉取包）；`npx @playwright/mcp@latest --version` → `0.0.70` | **CLI 可用**；**仓库未配置** Playwright/Browser MCP；**未**做浏览器端到端自动化 |
| sqlite | **Python 标准库** `sqlite3`（非独立 sqlite3.exe） | 无 | `python -c "import sqlite3; print(sqlite3.sqlite_version)"` → `3.40.1` | **通过**（标准库） |
| docker | **本机** Docker CLI | 用户级 | `docker --version` → `29.1.3`；`docker compose version` → `v5.0.1` | **通过** |
| GitHub | **未**在仓库配置 GitHub MCP；**本机** `gh` 未安装；相关 env **未**设置 | 无仓库密钥 | `gh auth status` → **失败**（`gh` 不是可识别命令）；`GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN` 均为 **not set** | **未配置 / 未验证**（需用户自行安装 `gh` 或在用户级 MCP 配 token，见第 3 节） |

---

## 2. 仓库内新增 / 修改文件（与本工具链相关）

| 路径 | 说明 |
|------|------|
| `.cursor/mcp.json` | 项目级 MCP：仅 `project-code`（filesystem，限定 `app`、`docs`、`tests`） |
| `.cursor/MCP_SECURITY.md` | MCP 与安全边界说明 |
| `.cursorignore` | 降低 `storage/`、`.env*` 等进入默认 AI 上下文的几率 |
| `.env.mcp.example` | 本地 MCP 相关环境变量模板（**不含**秘密）；复制为 `.env.mcp` 使用 |
| `docs/MCP_TOOLCHAIN_VALIDATION.md` | 本交付文档 |
| `.gitignore` | 增加 `.env.mcp`、`.cursor/mcp.local.json`、Playwright 产物目录、本地 sqlite scratch 等 |

**不应提交的内容（由 `.gitignore` 与流程约束）：** 见第 3 节。

---

## 3. 用户级 / 宿主级配置说明

- **项目级 MCP（可提交）：** `.cursor/mcp.json` — 团队共享的 MCP 进程声明（当前无密钥）。
- **用户级 MCP（不提交）：** 在 Cursor **Settings → MCP** 中配置的个人服务器；或本机 `%USERPROFILE%\.cursor\mcp.json`（路径随 Cursor 版本可能变化，以官方文档为准）。**勿**将含 token 的 JSON 拷入仓库。
- **本地环境文件（不提交）：** 复制 `.env.mcp.example` 为 `.env.mcp`，仅在本地填写；**勿**提交 `.env.mcp`。
- **可选本地覆盖文件（不提交）：** `.cursor/mcp.local.json` — 若你使用「本地合并」策略，仅放本机；**勿**提交。
- **浏览器 / Playwright：** 缓存与报告目录通常在本机用户目录或仓库下 `playwright-report/`、`test-results/`；已加入 `.gitignore` 常见项。
- **GitHub：** PAT **仅**存环境变量或系统密钥链，**勿**写入仓库；安装 GitHub CLI（`gh`）后可在用户环境使用。

---

## 4. 阻塞项与剩余人工步骤

1. **MCP 端到端：** 需在 Cursor 重启后于 **MCP 面板**确认 `project-code` 无报错；并任选 `app/` 下路径做一次 **read**/**list** 工具调用自测（本报告未替代该 UI 验证）。
2. **GitHub MCP：** `gh` 未安装且未设置 token → 无法在**本环境**验证 GitHub MCP；需用户自行安装/配置后重测。
3. **Browser MCP：** 仓库未声明浏览器 MCP；若需与 Agent 联动浏览器，请在**用户级**添加官方 Playwright/Browser 类 MCP，并自行审查权限范围。
4. **「全局搜索」：** 无 CLI 回归命令；依赖 IDE 行为与 `.cursorignore`。
5. **长期运行 HTTP：** 本验证用 `TestClient` + pytest；**未**启动 `uvicorn` 监听端口；联调时需单独执行 `python main.py run-api` 等（见 `README.md`）。

6. **本地 `storage/`：** 若曾在本机跑过 UI/API，`git status` 可能出现大量 `storage/` 下未跟踪或已修改文件，属**本地运行产物**，与 MCP 工具链验证无直接关系；提交前请按团队策略清理或保持忽略。

---

## 5. 对当前项目是否足以支持下列开发任务的判断

| 任务 | 判断 | 依据（简要） |
|------|------|----------------|
| 在当前仓库新增 `agent_runtime_v2` | **足够（以 Python/测试为主）** | 全量 `pytest` 通过；代码与测试均在 `app/`、`tests/` 内，**处于 MCP filesystem 允许目录**；编辑根目录 `main.py` 等需靠**编辑器**或临时扩大 MCP 范围（见 `.cursor/MCP_SECURITY.md`）。 |
| 重构 provider abstraction | **足够** | 同上与运行时/LLM 相关模块多在 `app/`；依赖测试与静态分析为主。 |
| 初始化 TypeScript 前端 | **部分：本机工具具备，仓库未初始化前端** | Node/npm/pnpm 可用；**仓库当前无前端包管理配置**；新建 `frontend/` 等时若需 MCP 文件工具，需将目录**纳入** `mcp.json` 的 args 或仅用内置编辑器。 |
| 前后端联调 | **足够（运行时 + 本机网络）** | `/health` 与 `/openapi.json` 经 `TestClient` 验证；真实联调需启动 API/UI；**未**在本报告验证浏览器 MCP。 |
| Playwright 回归 | **CLI 具备；项目内无现成 E2E 配置** | `npx playwright --version` 可用；仓库**未**包含 Playwright 配置与 MCP 浏览器流水线；若引入 E2E，需新增依赖与 CI，并注意 `.gitignore` 报告目录。 |

---

## 附录 A：复现验证命令（可复制）

在项目根目录（已安装 `pip install -e ".[dev]"` 的前提下）：

```powershell
# Shell
echo shell_ok

# Git
git status -sb
git diff --stat

# Python / pytest
python --version
python -m pytest -q --tb=no

# Node 工具链
node --version
npm --version
pnpm --version

# OpenAPI + health（不启动服务器）
python -c "from app.api.main import create_app; from fastapi.testclient import TestClient; c=TestClient(create_app()); print('health', c.get('/health').status_code); print('openapi', c.get('/openapi.json').status_code)"

# sqlite（标准库）
python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Docker
docker --version
docker compose version

# Playwright CLI（可选）
npx playwright --version

# MCP filesystem 包可启动性（会阻塞，Ctrl+C 结束）
npx -y @modelcontextprotocol/server-filesystem app docs tests
```

---

## 附录 B：刻意不纳入仓库的内容

以下内容**不应**提交到 Git：**任何 token**、用户级 MCP JSON、含本机绝对路径的私密配置、浏览器缓存、GitHub 凭据、本地 sqlite/测试垃圾文件。请使用 `.env.mcp.example` 与 `.gitignore` 中的规则配合团队流程。

---

## 附录 C：空白能力矩阵模板（复测时复制）

| 能力 | 实现方式（内置 / MCP / 本机 CLI） | 配置位置 | 验证命令 / 方法 | 状态 |
|------|-----------------------------------|----------|-----------------|------|
| （填写） | （填写） | （填写） | （填写） | （填写） |

---

## 附录 D：`.env.mcp.example`

仓库根目录提供 **`.env.mcp.example`**（仅注释与占位说明，无秘密）。本地复制为 **`.env.mcp`**（已被 `.gitignore` 忽略）后再填写；**切勿**将 `.env.mcp` 提交到 Git。
