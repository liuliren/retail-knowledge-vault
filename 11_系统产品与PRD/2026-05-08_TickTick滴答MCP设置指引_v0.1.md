---
title: TickTick / 滴答 MCP 设置指引 v0.1
version: v0.1
status: active
quadrant: III
owner: 六哥
created: 2026-05-08
updated: 2026-05-08
module: 11_系统产品与PRD
project: vault 工具栈 / Claude Code MCP
tags:
  - MCP
  - TickTick
  - 滴答
  - ClaudeCode
  - 工具栈
source_type: data
confidence: medium
client_safety: internal_only
related:
  - "[[CLAUDE.md]]"
  - "[[2026-05-08_滴答任务导出_v1.0]]"
  - "[[2026-05-08_5个月主控仪表_v1.0]]"
---

# 🔌 TickTick / 滴答 MCP 设置指引 v0.1

> **目的**：让 Claude Code 直接管理你的滴答任务（创建 / 列出 / 完成 / 标签 等）/ 替代手工 markdown 复制粘贴
> **当前状态**：claude.ai **未内建** TickTick connector / 必须自配 MCP server
> **推荐方案**：[liadgez/ticktick-mcp-server](https://github.com/liadgez/ticktick-mcp-server)（100% API 覆盖 / 112 操作 / Claude Code 原生）

---

## §1. 4 个候选方案对比

| 方案 | 来源 | 覆盖 | 推荐度 |
|---|---|---|---|
| **liadgez/ticktick-mcp-server** | GitHub | 100% API / 112 操作 | ⭐⭐⭐ **推荐** |
| jacepark12/ticktick-mcp | GitHub | 基础 CRUD | ⭐⭐ |
| jen6/ticktick-mcp | GitHub | 增强 filtering | ⭐⭐ |
| Composio TickTick toolkit | Composio SaaS | 完整 / 但需付费 | ⭐ |

---

## §2. 设置步骤（liadgez/ticktick-mcp-server / 推荐）

### Step 1：TickTick Developer 创建 OAuth App（5 min）

1. 访问 [developer.ticktick.com](https://developer.ticktick.com/)（国际版）或 [developer.dida365.com](https://developer.dida365.com)（国内版滴答）
2. 登录你的 TickTick / 滴答账号
3. **My Apps** → **Create App**
4. 填写：
   - App Name：`Claude-Code-vault-MCP`
   - Description：`vault 5 个月跑道任务管理`
   - Redirect URI：`http://localhost:8000/callback`（开发）
5. 创建后获取：
   - **Client ID**
   - **Client Secret**
6. 选 OAuth Scopes：
   - ✅ `tasks:read`
   - ✅ `tasks:write`

### Step 2：克隆并安装 MCP server（3 min）

```bash
# 选个目录（建议 ~/tools/ticktick-mcp/）
mkdir -p ~/tools && cd ~/tools

# 克隆
git clone https://github.com/liadgez/ticktick-mcp-server.git
cd ticktick-mcp-server

# 安装依赖（按 README）
# 一般是 Python：
pip install -r requirements.txt
# 或 Node：
# npm install
```

### Step 3：配置 OAuth credentials（2 min）

按 server README 的方式，通常是在项目根目录创建 `.env`：

```bash
TICKTICK_CLIENT_ID=你的 Client ID
TICKTICK_CLIENT_SECRET=你的 Client Secret
TICKTICK_REDIRECT_URI=http://localhost:8000/callback
```

### Step 4：注册到 Claude Code（2 min）

编辑 `~/.claude/mcp.json`（或 vault 项目级 `.claude/mcp.json`）：

```json
{
  "mcpServers": {
    "ticktick": {
      "command": "python",
      "args": ["/Users/davidliu/tools/ticktick-mcp-server/main.py"],
      "env": {
        "TICKTICK_CLIENT_ID": "你的 Client ID",
        "TICKTICK_CLIENT_SECRET": "你的 Client Secret"
      }
    }
  }
}
```

或者用 CLI 命令（更安全）：

```bash
claude mcp add ticktick --command "python" --args "/Users/davidliu/tools/ticktick-mcp-server/main.py"
```

### Step 5：第一次 OAuth 授权（3 min）

1. 重启 Claude Code（关闭再打开）
2. 在 Claude Code 内问我："列出我的滴答任务"
3. MCP server 触发 OAuth 授权 URL → 浏览器打开
4. 你登录 TickTick → 同意授权
5. 授权完成 / token 自动存储 / 此后无感

---

## §3. 验证（5 min / 你做 + 我配合）

setup 完成后，在 Claude Code 内对我说：

```
"列出我滴答清单"5 个月跑道（5/8-10/8）"内的所有任务"
```

我会调用 MCP 工具 `mcp__ticktick__*` 查询并展示。

如果成功 → 之后我可以：
- ✅ 自动创建任务（从 vault 文件提取）
- ✅ 标记完成（基于 vault 进度）
- ✅ 列出今日 / 本周任务
- ✅ 调整截止日 / 优先级
- ✅ 加标签 / 移动清单

---

## §4. 反幻觉红线（HHH / Anthropic）

```
[[CLAUDE.md]] §13 + Anthropic HHH 应用：

❌ 不允许 LLM 全自动改变任务（必须 user sign off）
❌ 不允许批量删除任务（destructive）
❌ 不允许对未理解的任务擅自标完成
❌ 不允许任务内容编造客户原话
✅ 我可以建议 / 你最终拍板
✅ 重大任务变更前先列清单等确认
```

---

## §5. 备选方案（如不想配 MCP）

如果你**不想配 MCP**（嫌麻烦），保持当前流程：

```
vault 内 → markdown 任务文件 → 你手工复制粘贴到滴答
```

**选项**：
1. **保持现状** — 完全手工 / 滴答为单纯执行 app / 我每次给 markdown
2. **轻量自动化** — 我给 Python 脚本 / 你本机跑 / 不进 Claude Code
3. **完整 MCP** — 本指引方案 / 一次配置 / 长期受益

---

## §6. 设置时间投入

| 选项 | 一次性时间 | 长期收益 |
|---|---|---|
| 保持现状 | 0 min | 每次 5-10 min 手工 |
| 轻量 Python | 30 min | 命令行触发 / 半自动 |
| **完整 MCP** | **15-20 min** | 自然语言对话 / 每次 0 min |

**推荐**：选项 3（完整 MCP）/ 一次配置 5 个月跑道全程受益。

---

## §7. 我能帮你做什么 vs 不能做什么

### ✅ 我能做（Claude Code 能力内）

- 写 setup 指引（本文件 ✅）
- 读你 GitHub 上克隆的 server 代码 / debug
- 写 mcp.json 配置 / 但**不能直接写**到你 `~/.claude/`（permission 问题）
- 配好后调用 MCP 工具操作任务

### ❌ 我不能做（技术 / 安全约束）

- 不能直接申请 TickTick OAuth App（需要你登录）
- 不能直接获取 Client Secret（敏感信息）
- 不能代替你完成 OAuth 授权（浏览器交互）
- 不能在 server 不存在时操作任务（必须先 setup）

---

## §8. Honest 警告

[[feedback_anthropic_claude_alignment]] HHH 应用：

⚠️ **OAuth credentials 是敏感信息** / 不要分享给我（我不需要 / setup 完成后自动用）
⚠️ **MCP server 是第三方代码** / setup 前看一眼源码 / 确认无恶意（liadgez/ 是开源 / 风险低）
⚠️ **滴答数据可能会被 LLM 看到** / 涉及客户敏感内容时考虑标记 confidential
⚠️ **第一次 OAuth 授权完成后** / token 存本地 / 不上云 / 你完全控制

---

## §9. 关联

### 上游
- [[CLAUDE.md]] §17 Claude Code 协作规则
- [[CLAUDE.md]] §23 gstack 工作流套件（其他 MCP 工具栈）
- [[2026-05-08_滴答任务导出_v1.0]]（当前手工方案）

### 资源
- 主推荐：[liadgez/ticktick-mcp-server](https://github.com/liadgez/ticktick-mcp-server)
- TickTick Developer：[developer.ticktick.com](https://developer.ticktick.com/)
- 滴答 Developer：[developer.dida365.com](https://developer.dida365.com)
- ticktick-py 库：[lazeroffmichael/ticktick-py](https://github.com/lazeroffmichael/ticktick-py)

---

## §10. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v0.1 | 2026-05-08 | 初版 / 4 候选方案对比 / 推荐 liadgez/ticktick-mcp-server / 5 步 setup / 反幻觉红线 / Honest 警告 |
