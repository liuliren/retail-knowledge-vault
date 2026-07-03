---
title: Claude Code 项目级上下文管理协议 v1.0
summary: Claude Code 上下文管理协议，4 层策略、阶段闸门、强制边界 11 条。
version: v1.0
status: active
quadrant: III
project: cross_client
client: cross_client
store: cross_client
phase: tools
business_module: 上下文治理
source_type: tool
created: 2026-05-10
updated: 2026-05-10
tags:
  - 工具
  - claude_code
  - context_management
  - compact
  - handoff
  - 跨客户复用
  - vault治理
---

# Claude Code 项目级上下文管理协议 v1.0

## 1. 协议定位

- 本协议是 vault 项目级 **Claude Code 长对话上下文治理协议**。
- 解决问题：
  - 终端对话过长 / 上下文膨胀
  - Claude 反复遗忘边界
  - 每次手动整理交接 prompt 成本高
- 服务：晟果新零售咨询 / 乐易购花厅坊店 / 商品数据底座主线 / **跨客户复用**。
- 跨客户：本协议**不含任何客户私有数据** / 可复用到凤凰计划 / 破晓 / 等其他战役。

---

## 2. 工具链架构

```
┌─────────────────────────────────────────────────────────┐
│ 用户                                                       │
│   ↓ 主动触发或长会话                                        │
│                                                          │
│  ┌──────────────────────────────────────────────┐        │
│  │ project-compact-governance skill（决策层）    │        │
│  │  - 检查工作区 git status                      │        │
│  │  - 判断是否该 compact / clear                 │        │
│  │  - 给优先级建议                                │        │
│  └────────────┬─────────────────────────────────┘        │
│               ↓ 决策结果                                   │
│  ┌──────────────────────────────────────────────┐        │
│  │ project-handoff skill（执行层）              │        │
│  │  - 生成 handoff 文档                          │        │
│  │  - 落 13_/_claude_context/handoff_*.md       │        │
│  │  - 输出新会话启动 prompt                      │        │
│  └────────────┬─────────────────────────────────┘        │
│               ↓ 输出                                      │
│  ┌──────────────────────────────────────────────┐        │
│  │ 用户决定 /compact 或 /clear 或 继续             │        │
│  │  - /compact：保留 handoff 作 audit-log         │        │
│  │  - /clear：用 prompt 启动新会话                 │        │
│  │  - 继续：handoff 仅备查                         │        │
│  └──────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────┘
```

---

## 3. 文件清单

| 文件 | 路径 | 用途 |
|---|---|---|
| **决策 skill** | `.claude/skills/project-compact-governance/SKILL.md` | 何时 compact / clear / 边界检查 |
| **执行 skill** | `.claude/skills/project-handoff/SKILL.md` | 生成 handoff 文档 + 启动 prompt |
| **协议主文档**（本文件）| `13_数据分析与工具脚本/_claude_context/README.md` | 总入口 + 跨客户复用说明 |
| handoff 落档目录 | `13_数据分析与工具脚本/_claude_context/handoff_*.md` | 每次 handoff 历史归档 |

---

## 4. 优先级（自动 > 手动 > 人工兜底）

```
1. 优先依赖 Claude Code 内置 auto-compaction
2. 用户主动判断需要 → 触发 project-compact-governance skill
3. skill 建议 → 用户决定 → project-handoff 生成文档
4. 用户 /compact 或 /clear（用户主动 / 不自动）
5. handoff 文档作 audit-log 永久保留
```

### 4.1 4 层策略（推荐 / TOOLING-CTX-002 §二.3）

```
┌─────────────────────────────────────────────────────────┐
│ 层 1：Claude Code 内置 auto-compaction（系统层 / 默认开）│
│   优先依赖 / 不外部干预                                   │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 层 2：project-compact-governance skill（决策层）        │
│   长对话节点 / 给安全 compact 判断与指令                 │
│   - 检查 git status                                     │
│   - 判断"何时 compact" vs "何时 clear" vs "继续"        │
│   - 输出建议 / 不自动执行                                │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 层 3：project-handoff skill（执行层）                  │
│   /clear 或新会话前 / 生成完整交接包                     │
│   - 落 handoff_<timestamp>.md                           │
│   - 含强制边界 + fact_layer + 启动 prompt               │
└─────────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────────┐
│ 层 4：阶段闸门（强制三步 / 高风险任务前）                │
│   触发：BUS-DATA-008 真实清洗 / SKU 输出 / 调改启动      │
│   1. 必须 /clear（不允许带污染上下文进高风险任务）        │
│   2. 必须 handoff + 闸门 prompt（明示边界 + fact）       │
│   3. 用户主动确认 / 不自动                                │
└─────────────────────────────────────────────────────────┘
```

### 4.2 阶段闸门（4 层策略关键 / BUS-DATA-008 / 调改 / 等高风险触发）

**何时触发阶段闸门**：

| 触发场景 | 必须强制三步 |
|---|---|
| **BUS-DATA-008 真实数据清洗执行** | ✅ /clear + handoff + 闸门 prompt |
| **首次输出 SKU 调整清单** | ✅ 同上 |
| **冲调正式调改启动**（5/30 G05 + 5 件齐 / 章程 §3.1 OUT 触发后）| ✅ 同上 |
| **方便速食 v0.6 升级**（4 前置齐：库存 + 0206% + sign off + 数据等级）| ✅ 同上 |
| **跨客户切换**（花厅坊 → 凤凰计划 / 破晓）| ✅ 同上 |
| **方法论主定义升级 v1.0**（M-DEC v0.5 → v1.0 跨战役晋级）| ⚠️ 推荐三步 |

**闸门 prompt 模板**（在 §8 启动 prompt 基础上加）：

```text
[阶段闸门 / <任务名>]

我即将启动 <高风险任务>。

启动前 / 务必复读：
1. project-compact-governance §强制边界（11 条 / README §5）
2. project-handoff §fact_layer.client_told（README §6）
3. 当前战役状态（README §7）

明确确认（请打 ✅ 或停止）：
- ✅ 我已 review handoff 文档
- ✅ 我已确认 git status clean
- ✅ 我已确认无 /tmp 真实数据残留
- ✅ 我已 fact_layer 标注 4 元字段
- ✅ 我已确认前置条件全部满足

如以上任一未满足 / 立即停止 / 不启动任务。
```

**闸门违反 = vault 反幻觉硬约束失守**：

```
❌ 不允许带污染上下文进 BUS-DATA-008
❌ 不允许跳过 handoff 直接 SKU 输出
❌ 不允许在高风险任务中途 compact / clear
✅ 用户主动 / 显式触发闸门 / 三步缺一不可
```

**反例**（不允许）：
- ❌ 自动执行 `/compact` 或 `/clear`
- ❌ 在写文件 / 复查 / commit 中途 compact
- ❌ 在 /tmp 真实数据未清理时 compact
- ❌ 丢弃 fact_layer.client_told 等关键事实

---

## 5. 强制边界（vault 治理纪律 / 任何 compact / clear / handoff 不可丢失）

无论压缩到什么程度 / 必须保留以下 11 条：

```
1. 不清洗真实数据，除非用户明确授权
2. 不生成商品基础档案候选表，除非进入 BUS-DATA-008 且前置条件通过
3. 不输出 SKU 清单
4. 不输出商品名 / 品牌名 / 条码 / 销售金额 / 销量明细
5. 不生成方便速食 v0.6 结论
6. 不启动冲调正式调改
7. 不提交 xls / xlsx / rar / csv / 真实经营数据
8. 不把 /tmp 转换文件写回 vault
9. 不修改已完成 BUS-DATA 文件，除非用户明确授权
10. 不自动 commit
11. 不自动 /compact 或 /clear
```

---

## 6. 关键 fact_layer.client_told（必须在 handoff 中保留）

> 这些是 vault 反幻觉机制的核心 / 失去后 Claude 会重蹈覆辙。

| 事实 | 来源 | 状态 |
|---|---|---|
| 4/25 调改 = **4/25 晚上**完成 | 六哥 5/10 confirm | ✅ active |
| 供应商字段系统可导出 | 六哥 5/10 confirm | ✅ active |
| 进价字段系统可导出 / **生鲜进价未入系统** | 六哥 5/10 confirm | ✅ active |
| 0206% = 方便食品独立大类（不是休闲下子类）| BUS-DATA-007A §9 探测 | ✅ system level |
| 0206% **是否完全等同原"方便速食"调改口径** | 启明业务定义 | ⚠️ **待 5/13 confirm** |
| 020601 = 方便面（0206 下子类）| BUS-DATA-007B §4 探测 | ✅ system level |
| 020202% = 冲调（休闲下子类）| BUS-DATA-007A §9 探测 | ✅ system level |
| 0202% = 休闲大类 | 同上 | ✅ |
| 启明 sign off **5+2 = 7 件**（4/25 + 方便面 3 选 1 + 排面 + POS + 责任 + 0206% + 完整库存）| BUS-DATA-007C §9 | ⏳ **5/13-5/15 启明** |

---

## 7. 当前战役状态（W20-Day1 EOD）

```
战役 #1: 花厅坊样板（W18-W22 / 5/30 G05）
当前周: W20-Day1
当前主线: 商品数据底座 BUS-DATA 系列

数据底座产出（11 文件 / 全 commit）：
- BUS-DATA-001 模块设计
- BUS-DATA-002 字段模板（111 字段）
- BUS-DATA-002A 字段口径修正（B+）
- BUS-DATA-003 阶段作业包
- BUS-DATA-004 Excel 空模板（13 sheet / 142 字段字典）
- BUS-DATA-005 自动生成 + 人工校准
- BUS-DATA-006 真实数据导入与清洗任务单
- BUS-DATA-007 5/12 拉数日志骨架
- BUS-DATA-007A 5/10 实际拉数回填（15 文件接收）
- BUS-DATA-007B 5/8 vs 20260510 方便食品口径对比
- BUS-DATA-007C 方便食品库存缺口 + 0206% 口径任务单

工具链：BUS-TOOL-001 xls→xlsx + header 探测（README + sh + py）

治理：vault v3.0 设计稿 v0.5 + 命名规范三件套 + GOV-NAMING-002 + GOV-AUDIT-001

业务：W20-Day2 收口纪要 + W20-Day3 POS 增量 + W20-Day4 现场口袋卡 v0.2 +
      子组×流程双轴重组 + 命名分隔符固化 + SOP_6机位拍摄法 v0.5 +
      方便速食 4/25 confirm + 客户验证日志

下一步触发：
- 5/12 启明拉数（BUS-DATA-007C P0 3 问 + 拉数清单）
- 5/13 启明现场访谈（13 P0 + 4 补 + sign off 7 件）
- W21 BUS-DATA-008 真实清洗（前置 ≥ 7/8 满足后）
- 方便速食 v0.6 升级（4 前置齐：库存 / 0206% / sign off / 数据等级）
- 5/30 G05 阶段门 + 冲调正式调改触发判定
```

---

## 8. 跨客户复用说明

本协议**不含客户私有数据** / 可复用到任何战役 / 客户。

跨客户使用时：

1. 复制 `.claude/skills/project-compact-governance/` + `.claude/skills/project-handoff/` 到目标 vault
2. 复制本 README 到目标 vault `13_/_claude_context/`
3. 调整 §6 fact_layer.client_told 为目标客户事实
4. 调整 §7 当前战役状态为目标战役
5. **不动** §5 强制边界（这是普适规则）

---

## 9. 与 vault 治理协同

| vault 治理项 | 本协议如何配合 |
|---|---|
| `.gitignore` line 51 `**/*.xlsx` 全局 + 单文件白名单 | handoff 文档不入 git 真实数据（仅 markdown 索引）|
| `CLAUDE.md` §13.16 客户视角防火墙 | handoff §3 强制边界 + §6 fact_layer 标注 |
| 命名规范 v0.4 + 三件套 | handoff 文件命名 `handoff_YYYYMMDD_HHMMSS.md` 合规 |
| BUS-DATA-006 真实数据导入任务单 §4 数据接收登记 | handoff §2 vault 治理状态部分摘要 |
| BUS-DATA-007A 拉数结果回填 | handoff §6 关键 fact_layer 引用同步 |
| GOV-AUDIT-001 W20-Day1 审计 | handoff 引用最新审计 commit |

---

## 10. 限制与边界

| # | 限制 | 影响 |
|---|---|---|
| 1 | 仅适用 Claude Code（不适用 ChatGPT 网页 / 其他工具）| — |
| 2 | 依赖用户主动触发 / 不自动执行 | 用户疏忽时仍可能上下文膨胀 |
| 3 | handoff 文档质量取决于 LLM 总结准确度 | 关键 fact 用户应主动 review |
| 4 | 不替代 vault 治理硬约束（如 .gitignore）| 协议是软建议 / .gitignore 是硬约束 |
| 5 | 不替代用户审阅决策 | LLM 建议 / 用户最终决定 |

---

## 11. 使用例（典型）

### 11.1 长会话末尾 / 准备 commit + 短暂休息

```
用户: "差不多了 / 该 compact 吗？"
    ↓
project-compact-governance skill 检查 git status / 给建议
    ↓
若建议 compact / 调用 project-handoff 生成 handoff 文档
    ↓
用户 review handoff
    ↓
用户决定：/compact / 继续 / 等明天
```

### 11.2 跨业务模块切换 / 新任务前

```
用户: "现在切到凤凰计划 / 先帮我整理交接"
    ↓
project-compact-governance / 给"建议 /clear" 信号
    ↓
project-handoff / 落 handoff_<timestamp>.md
    ↓
用户 /clear → 用 §8 启动 prompt 启动新会话
```

### 11.3 高风险任务前 / 上下文清场

```
用户: "下一步要清洗真实数据 / 先把上下文清干净"
    ↓
project-compact-governance / 给"建议 /clear"（数据清洗是高风险）
    ↓
project-handoff / 强调 §强制边界 + §fact_layer
    ↓
用户 /clear → 新会话从 prompt 启动
```

---

## 12. 版本

| 版本 | 日期 | 说明 |
|---|---|---|
| v1.0 | 2026-05-10 W20-Day1 | 初版 / TOOLING-CTX-002 / 跨客户复用 / 含决策 skill + 执行 skill + 主协议 README |
