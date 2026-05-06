---
title: Claude Code 入门手册
version: v0.1
status: review
owner: 六哥
created: 2026-05-04
updated: 2026-05-04
module: 11_系统产品与PRD/Claude Code 官方文档学习包
tags:
  - ClaudeCode
  - 入门手册
  - 操作SOP
  - token控制
  - skills
  - subagents
  - 三个月生存战
source_type: reference
confidence: medium
related:
  - "[[README]]"
  - "[[09_Claude_Code使用手册_v0.1]]"
  - "[[01_上下文与记忆机制总结_v0.1]]"
  - "[[08_token与额度控制规范_v0.1]]"
  - "[[10_待核验问题清单_v0.1]]"
---

# Claude Code 入门手册

> 这是一份"用得起、用得对、用得久"的 Claude Code 入门操作指南。
>
> **快速定位**：从未用过 → 第 1–3 章；用过但没系统化 → 第 4–8 章；想升级 → 第 14 章。
>
> **本手册的边界**：所有事实来自官方文档（2026-05-04 抓取）；未亲自验证项保留「待核验」标记，集中在 [[10_待核验问题清单_v0.1]]。

---

## 目录

- 第 1 章 — 这本手册写给谁
- 第 2 章 — 30 分钟入门：从安装到第一次有用的会话
- 第 3 章 — 心智模型：Claude Code 内部到底在做什么
- 第 4 章 — 让 Claude 持续懂你：CLAUDE.md 与 `.claude/rules/`
- 第 5 章 — 会话工作法：开 / 中 / 收 三段 SOP
- 第 6 章 — Token 与额度高效消耗（**核心**）
- 第 7 章 — Skills：让重型 SOP 按需调用（**核心**）
- 第 8 章 — Subagents 与 Fork：让上下文不被淹没（**核心**）
- 第 9 章 — Slash 命令：真正高频的 12 个
- 第 10 章 — 权限与安全
- 第 11 章 — Hooks：默认不开，但要看懂
- 第 12 章 — StatusLine：仪表盘
- 第 13 章 — 日志、transcript 与复盘
- 第 14 章 — 30 / 60 / 90 天能力升级路线
- 第 15 章 — 故障排查 FAQ
- 附录 A — 本 vault 推荐配置（建议方向，不实施）
- 附录 B — 术语表

---

## 第 1 章 — 这本手册写给谁

写给四种人：

1. **第一次用 Claude Code** —— 想知道"它和 ChatGPT 网页版有什么本质区别"
2. **用了几次但凭感觉** —— 想知道"为什么我的 token 用得这么快 / 输出这么飘"
3. **要把它嵌进真实工作流** —— 想知道"怎么和我们的 Obsidian 知识库 / 客户咨询项目共生"
4. **打算培训别人** —— 想要一份能直接发给学员的标准教材

不写给两种人：
- 想要"一键生成完整应用"的——Claude Code 是工具不是奇迹
- 不愿意建立基础纪律的——纪律是 Claude Code 与"普通 AI 助手"拉开 10 倍差距的关键

### 1.1 与"普通 AI 网页版"的本质区别

| 维度 | 普通 AI 网页 | Claude Code |
|---|---|---|
| 文件读写 | 上传 / 复制粘贴 | 直接读写本机文件 |
| 工具调用 | 受限 | Bash / Edit / Write / WebFetch / MCP / 子代理 |
| 上下文 | 单会话 | 跨会话有 CLAUDE.md / auto memory / `/resume` |
| 行为定制 | Prompt | CLAUDE.md + `.claude/rules/` + skills + hooks + permissions |
| 失误代价 | 输出文本而已 | 可能改你的代码 / 删你的文件 / 推你的 git → 必须有权限纪律 |

**Claude Code 的核心命题不是"AI 更聪明"，而是"AI 进了你的工作环境"**。环境意味着权力，权力意味着边界，边界意味着方法论。

---

## 第 2 章 — 30 分钟入门：从第一次有用的会话开始

如果你只有 30 分钟，做这五件事：

### 步骤 1（5 分钟）— 先看自己的牌面

```
/status     # 当前模型 / 账户 / 连接
/usage      # 本会话花了多少 / 5 小时与 7 天额度还剩多少
/memory     # 哪些 CLAUDE.md / rules 已加载
```

这三条命令是"开局牌面"。每次新开会话先过一遍，30 秒。

### 步骤 2（5 分钟）— 决定本会话目标

写一句话：**"本次会话要解决的一件事是 X，不做 Y / Z。"**

这一句话比任何 prompt 工程都重要。Claude 偏离方向的 80% 原因是用户自己没想清楚边界。

### 步骤 3（10 分钟）— 试一次"小而完整"的任务

候选任务清单（按本知识库场景）：

- "读 `04_商品诊断与商品力提升/` 下所有 README，总结每个文件的定位差异"
- "我把 X 门店的 SKU Excel 转写成了 markdown 在 `90_素材暂存与待整理/`，帮我提取 Top 20 单品并按 ABCD 分类规则归类"
- "看 `09_门店案例与项目复盘/乐易购花厅坊店/`，告诉我哪些子目录还没写"

任务要小（10 分钟内能完成）、要完整（有明确产出）、要容易判对错。

### 步骤 4（5 分钟）— 收尾

```
/usage          # 看花了多少
/rename 主题名   # 命名本会话（重要）
/clear          # 切下一主题，旧会话仍可 /resume 找回
```

### 步骤 5（5 分钟）— 复盘三问

1. 哪个动作我能少做（让 Claude 做）？
2. 哪个动作我多做了（不该让 Claude 做）？
3. 这次会话花的 token 值不值？

---

## 第 3 章 — 心智模型：Claude Code 内部到底在做什么

### 3.1 一次会话的"启动加载"

按时间顺序，这些东西默认就吃了你的上下文：

1. System prompt（约 4 KB，Claude 自带）
2. Auto memory `MEMORY.md` 前 200 行 / 25 KB
3. 环境信息（cwd、平台、git 状态）
4. MCP 工具名单（schema 默认延迟加载）
5. Skill 名 + 一行描述（**body 不加载**，按需调用）
6. CLAUDE.md 全量（按目录树拼接，从根到 cwd）
7. `.claude/rules/*.md` 中**没有 `paths:` 前缀**的规则

**关键观察**：你还没说话，**已经用了几千 token**。这就是为什么 CLAUDE.md 控制在 200 行内重要。

### 3.2 一次会话的"压缩与重置"

| 动作 | 行为 | 旧会话 |
|---|---|---|
| `/compact [指令]` | 用结构化摘要替换历史；CLAUDE.md / auto memory / 环境 / MCP **重新注入**；skill 列表**不重注入**（只保留已调用过的） | 同一会话继续 |
| `/clear` | 开新会话，全清 | **保留**，可 `/resume` |
| `/resume` | 恢复旧会话 | — |

**关键观察**：`/compact` 不是"无损压缩"。口头补充的"特殊指令"会丢；嵌套子目录的 CLAUDE.md 与 `paths:` 规则也不会自动重注入。**真要长期生效的指令，永远写进 CLAUDE.md / `.claude/rules/`**。

### 3.3 上下文窗口的物理限制

200K tokens（约 50 万字汉字 / 15 万字英文 / 5000 行代码）。

听起来很多。但是：

```
启动加载         ~5–10 KB tokens
读 5 个大 markdown ~30–50 KB tokens
跑一次 grep      ~2–10 KB tokens
读一次 Excel     ~20–80 KB tokens
长会话来回 20 轮  ~50 KB+ tokens
─────────────────────────
合计很容易就 100K，离 200K 不远
```

**结论**：上下文不是免费的。本手册第 6 章（token 控制）和第 8 章（subagent）都是为了这件事。

### 3.4 模型分层

| 模型 | 强项 | 用法 |
|---|---|---|
| Opus | 架构 / 复杂推理 / 长链思考 | 重大方法论、跨模块整合、关键决策 |
| Sonnet | 主力工作马 | 默认主会话、日常编辑、读 / 写 / 改 |
| Haiku | 快、便宜 | 子代理首选、简单批处理 |

**default = Sonnet，已经够你 80% 的活**。Opus 留给"我要做一次年度方法论梳理"这种场合。

---

## 第 4 章 — 让 Claude 持续懂你：CLAUDE.md 与 `.claude/rules/`

### 4.1 CLAUDE.md 是什么

四级位置（高到低，全部拼接、不互相覆盖）：

| 级别 | 路径 | 适合放 |
|---|---|---|
| 管理策略 | `/Library/Application Support/ClaudeCode/CLAUDE.md`（macOS） | 组织合规规则（个人不用） |
| 项目 | `./CLAUDE.md` 或 `./.claude/CLAUDE.md` | 团队共享的项目规则 |
| 用户 | `~/.claude/CLAUDE.md` | 你的跨项目偏好 |
| 本地 | `./CLAUDE.local.md` | 只你自己看（应 .gitignore） |

### 4.2 写 CLAUDE.md 的三条铁律

1. **具体到能验证**：「用 2 空格缩进」优于「格式化代码」；「淘汰 SKU 必须同时看销售额、毛利、库存」优于「商品诊断要全面」。
2. **不超过 200 行**：超了官方明确说"遵从率下降"。本知识库当前 567 行，**第 14 章给出拆分路线**。
3. **不互相矛盾**：CLAUDE.md 不是日记，是宪法。看到两条规则在打架——立即合并或删一条。

### 4.3 `.claude/rules/` 是 CLAUDE.md 的拆分器

```
.claude/rules/
├── 反幻觉.md           # 无 paths：每会话都加载
├── 陈列.md             # paths: ["06_陈列规划与DisplayMap/**"]
├── 商品诊断.md          # paths: ["04_商品诊断与商品力提升/**"]
└── 方法论.md           # paths: ["01_科学零售方法论/**"]
```

**带 `paths:` 的规则只在你打开匹配文件时才加载**。这是降低每次启动 token 消耗的最干净办法。

### 4.4 Auto memory 是 Claude 自己的笔记

- 位置：`~/.claude/projects/<repo>/memory/MEMORY.md` + 主题文件
- 加载：`MEMORY.md` 前 200 行 / 25 KB；主题文件按需读
- 内容：Claude 自动记下"build command 是什么 / 你纠正过它哪些事 / 这个项目的某个怪癖"
- 控制：`/memory` 开关；环境变量 `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` 可禁

**你可以读、改、删它**，全是明文 markdown。

### 4.5 一个简单决策：规则该写到哪？

```
这条规则要不要每次会话都加载？
├── 是 → CLAUDE.md（如果短）/ .claude/rules/无paths（如果长）
└── 否 → 只在某模块下加载？
        ├── 是 → .claude/rules/ 带 paths:
        └── 否 → 这是"任务级流程"？
                ├── 是 → 写成 skill（第 7 章）
                └── 否 → 写成提问模板，临时用
```

---

## 第 5 章 — 会话工作法：开 / 中 / 收 三段 SOP

### 5.1 开（< 1 分钟）

```
1. 写一句"本次目标"
2. /status 看模型
3. 简单任务 → /effort low；复杂 → /effort medium 或 high
4. 大改 vault 前 → 进 plan 模式（Shift+Tab）
```

### 5.2 中（持续）

时刻问自己三个问题：

1. **这个 token 值不值？** —— 若否，停下来，换 subagent / `/clear` 重开
2. **这个动作能不能委派？** —— 长扫描 → subagent；重型 SOP → skill；查命令 → CLI
3. **这个指令会不会被 `/compact` 吃掉？** —— 若是关键指令，立即写进 CLAUDE.md

### 5.3 收（< 1 分钟）

```
1. /usage    看花费
2. /rename   命名（值得保留的会话）
3. /clear    切主题
```

### 5.4 一周一次的"会话纪律自检"

每周看一次自己的 `~/.claude/history.jsonl`（你输入过的 prompt 流水），问自己：

- 哪类问题我重复问了 5 次以上？→ 应该写进 CLAUDE.md / skill
- 哪次会话最贵？为什么？→ 是不是该用 subagent
- 哪次会话最有用？为什么？→ 那个模式能不能复制

---

## 第 6 章 — Token 与额度高效消耗（核心）

### 6.1 心法：贵的不是模型，是**没纪律的会话**

同样一个任务，纪律好的人能用 1/5 的 token 跑出 5 倍质量。**纪律不是抠门，是把 token 花在刀刃上**。

### 6.2 11 条降本规则（背下来）

**A. 会话纪律**

1. 切主题先 `/clear`（先 `/rename` 再清，便于 `/resume`）
2. 长任务前 `/compact 关注 X`
3. 简单任务 `/effort low`，复杂任务 `/effort high`，做完降回来
4. "扫全库 / 跨多门店比对 / 读长 Excel" → subagent

**B. 模型分层**

5. 主会话 Sonnet 兜底，方法论级用 Opus
6. 子代理 Haiku 优先

**C. 上下文优化**

7. CLAUDE.md < 200 行；本 vault 拆 `.claude/rules/`（路线见第 14 章）
8. 重型 SOP 写成 skill（第 7 章）
9. 关闭未用的 MCP（`/mcp`）；CLI 优于 MCP server

**D. 思考 token**

10. 默认 thinking 开；简单任务 `/effort low`；批量场景 `MAX_THINKING_TOKENS=8000`

**E. 监控**

11. statusLine 持续显示 `context %` + `5h %`；会话尾 `/usage` 一眼

### 6.3 高频降本套路

| 场景 | 反模式 | 正确做法 |
|---|---|---|
| 写周报 | Opus + max effort | Sonnet + effort medium，5 分钟出稿 |
| 全库找一个概念 | 主会话 grep 一堆文件 | "用 Explore subagent 查 X，只回我引用文件路径列表" |
| 长讨论后转新任务 | 直接问下一题 | 先 `/compact 保留方法论结论` 再问 |
| 多文件批量改字 | 主会话逐文件改 | 写成 prompt 模板，让 Claude 一次列出 diff，你一次确认 |
| Excel 大表 | 让 Claude 全文读 | 先用 Bash `head` / `wc` / `awk` 抽样，再让 Claude 看摘要 |
| 重复问 SOP | 反复粘 SOP 进 prompt | 一次性写成 skill，调用一次抵 100 次粘贴 |

### 6.4 反馈回路

```
工作中 → statusLine 看 ctx % 与 5h %
       │
       ├── ctx > 70% → /compact
       ├── ctx > 90% → /clear（必要时 /rename + /resume）
       └── 5h > 80% → 当天主任务收尾，停一停

会话结束 → /usage 看结算

每周 → 蒸馏"哪些任务花得不值"

每月 → 见第 13 章复盘机制
```

### 6.5 一个反直觉的数字

官方数据：**Agent teams（多代理协同）会使用约 7× 普通会话的 token**。换句话说，"开 agent team 跑一周"约等于"普通会话跑两个月"。三个月生存战内**坚决不开**。

---

## 第 7 章 — Skills：让重型 SOP 按需调用（核心）

### 7.1 Skill 是什么

简单一句话：**"打包好的 SOP，平时不在上下文，调用时才进。"**

启动时，Claude 只看到 skill 的**名字和一行描述**；当你或 Claude 判断需要时，**body 才被加载**。这是把 CLAUDE.md 之外、又不便每次都加载的"重型流程"塞进系统的最干净办法。

> ⚠️ **待核验**：skills.md 完整页本轮未抓全文。下文 Skill 创建机制以官方 memory.md / context-window.md / claude-directory.md 中的交叉引用为准；详细 frontmatter 字段表与 [[10_待核验问题清单_v0.1]] #11 一同消化。

### 7.2 什么时候用 Skill（不是 CLAUDE.md）

| 场景 | 写成 | 理由 |
|---|---|---|
| "整个项目都要遵守的反幻觉规则" | CLAUDE.md / `.claude/rules/` 无 paths | 每会话必加载 |
| "改陈列文件时的层位匹配规则" | `.claude/rules/陈列.md` 带 paths | 仅在需要时加载，不打扰其他工作 |
| "30 天商品提效项目的标准流程（多步、长、有判分点）" | **Skill** | 平时完全不进上下文，调用时才用 |
| "DisplayMap 检查清单 + 检查脚本 + 模板" | **Skill** | 多文件打包，按需调用 |

### 7.3 Skill 的关键属性（已确认部分）

- 文件位置：`.claude/skills/<name>/SKILL.md`（项目级）/ `~/.claude/skills/<name>/`（用户级）
- 启动时只加载**名 + 描述**
- 调用方式：用户 `/<name>` 或 Claude 根据描述自动判断
- 可设 `disable-model-invocation: true` → 完全隐藏，仅手动 `/name` 唤起
- `/compact` 后**只保留已被调用过**的 skill；其它要重新调用

### 7.4 本 vault 推荐的 Skill 候选（建议方向，不实施）

| 候选 | 内容 | 优先级 |
|---|---|---|
| `displaymap-check` | DisplayMap 检查清单 + 包装尺寸库 + 层位规则 + 现场照片对照规则 | 高 |
| `sku-diagnosis` | SKU ABCD 分类规则 + 销售-毛利-库存-动销-缺货-活动六维诊断模板 | 高 |
| `52week-md` | 52 周 MD 框架 + 季节 / 节假日表 + 商品波段表 | 中 |
| `ops-monthly-report` | 老板月报标准结构 + 数据反幻觉清单 | 中 |
| `category-tree` | 标准品类表 + CDT 顾客决策树模板 | 中 |
| `case-study-skeleton` | 门店案例标准目录 + 各章节生成提示 | 低（先用模板） |

### 7.5 Skill vs CLAUDE.md vs `.claude/rules/` 的取舍

```
要不要每会话都加载？
├── 要 → CLAUDE.md（短，<200 行）或 rules 无 paths
├── 仅在某模块下要 → rules 带 paths（自动按文件路径触发）
└── 仅在我或 Claude 主动需要时 → Skill（按需调用，不进启动上下文）
```

**判分标准**：上下文常驻成本 vs 调用成本。Skill 牺牲了一点点"调用一次的开销"，换来了"99% 时间不占上下文"的好处。重型 SOP 一定走 Skill。

---

## 第 8 章 — Subagents 与 Fork：让上下文不被淹没（核心）

### 8.1 一句话区分四种"分身"

| 概念 | 是什么 | 看什么上下文 | 何时用 |
|---|---|---|---|
| 主会话 | 你正在用的这个 | 全部启动加载 + 对话历史 | 默认 |
| Named Subagent | `.claude/agents/<name>.md` 定义的专精代理 | **独立 context**：CLAUDE.md + MCP + skill 重新加载，无你的对话历史 | 重复任务、需要工具白名单 |
| Fork | 临时分身，**继承你当前对话历史** | 主会话的全部上下文 | 一次性 / 需要前情 |
| Agent Team | 多代理协同（≈ 7× token） | 多个独立 context | 三个月生存战内**不开** |

### 8.2 Subagent 真正的价值

不是"另一个 AI 帮你跑活"，而是 **"把高吞吐工作隔离在另一个上下文窗口"**。

举例：你想知道"花厅坊店所有陈列方案里有几处违反层位规则"。

| 方案 | 主会话 token 成本 | 主会话上下文污染 |
|---|---|---|
| 你自己一个个 grep | 30 KB | 30 KB（每次 grep 输出都进） |
| 让主会话 Claude 全做 | 50 KB+ | 50 KB+（每个文件都被读进） |
| **委派 Explore 子代理** | **3 KB**（只回摘要） | **几乎为 0** |

### 8.3 何时该派 / 不该派

**该派**：
- 一次性高吞吐"读多写少"（扫库、跨多门店比对、长 Excel 抽样）
- 重复出现的同类副任务（写成 named subagent，配 Haiku，限工具）
- 想限制工具集做受控审查

**不该派**：
- 信息少、回合短（spawn 自己就有冷启动成本）
- 需要主会话的对话历史 → 用 **fork**，不是 named subagent
- 多代理需互相通信 → 想清楚再用 agent team（贵）

### 8.4 Named Subagent 的写法骨架（待核验）

```yaml
---
name: 陈列规则巡检员
description: 扫描 06_陈列规划与DisplayMap/ 与各门店陈列整改文件，检出违反层位 / 包装尺寸 / 主通道规则的条目
model: claude-haiku-4-5-20251001
tools: [Read, Grep, Glob]
memory: project
---

# 系统提示
你是一名陈列规则巡检员……
```

> ⚠️ **待核验**：完整 frontmatter 字段表（见 [[10_待核验问题清单_v0.1]] #6）。上面的字段名以官方文档抓取片段为准，实施前需对照 sub-agents.md 完整版。

### 8.5 Subagent 操作铁律

1. `description` 写得**精确**——它决定 Claude 是否自动派发；写得宽容易被滥用
2. 工具白名单**最小化**——能 `Read+Grep` 完成的，不给 `Edit`
3. 优先 Haiku——除非任务要求高推理
4. **主任务每天问一次：今天有没有该派而没派的活？**

---

## 第 9 章 — Slash 命令：真正高频的 12 个

不是"全部命令"，是**真正高频用、用错代价大**的 12 个。完整表见 [[03_slash命令速查_v0.1]]。

| # | 命令 | 何时用 | 注意 |
|---|---|---|---|
| 1 | `/usage`（=`/cost`） | 每次会话末必看 | 订阅用户美元数仅供参考（**待核验**） |
| 2 | `/context` | 怀疑爆窗时 | — |
| 3 | `/compact [指令]` | 长会话 / 切子主题前 | 口头指令会丢，关键指令进 CLAUDE.md |
| 4 | `/clear`（`/reset`、`/new`） | 切大主题 | **先 `/rename` 再清** |
| 5 | `/resume` | 找回旧会话 | 名字随机难找，靠 `/rename` |
| 6 | `/rename` | 长 / 重要会话开头 | — |
| 7 | `/memory` | "指令没生效"排查 | 列出当前加载的 CLAUDE.md / rules |
| 8 | `/effort low\|medium\|high` | 任务难度切换 | 简单任务 low，做完升回来 |
| 9 | `/model` | 切模型 | 切完不重读历史 |
| 10 | `/permissions` | 加白 / 降扰 | 配置在 settings.json |
| 11 | `/agents` | 管理子代理 | 见第 8 章 |
| 12 | `/rewind`（双击 ESC） | 翻车回滚 | 依赖 `~/.claude/file-history/` 完整性（**待核验**） |

**`/btw` 在官方主表未列**——可能是 skill / 别名 / 已废弃，**待核验**（见 [[10_待核验问题清单_v0.1]] #1）。

---

## 第 10 章 — 权限与安全

### 10.1 心智模型

```
评估顺序：deny → ask → allow
任何层 deny 一票否决
```

### 10.2 模式速选

| 模式 | 用途 | 推荐场景 |
|---|---|---|
| `default` | 首次提示 | 默认 |
| `plan` | 只读分析 | **大改前 / 复盘 / 扫库** |
| `acceptEdits` | 自动接受工作区内编辑 | 信任会话时 |
| `dontAsk` | 未预批一律拒 | 高度受控 SOP |
| `bypassPermissions` | 全跳过 | **仅容器 / VM**，绝不日常用 |

### 10.3 本 vault 的红线（建议方向，不实施）

```jsonc
{
  "permissions": {
    "deny": [
      "Edit(/99_归档/**)",          // 防误改归档
      "Edit(./CLAUDE.md)",          // 主治理规则只能人工改
      "Edit(/00_入口与总索引/**)",  // 保护治理文件
      "Bash(git push *)"            // 防误推
    ],
    "ask": [
      "Bash(rm *)",
      "Bash(mv */99_*)",            // 进归档
      "Edit(/.claude/**)"           // 改配置
    ],
    "allow": [
      "Read",                        // 全可读（默认行为）
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ]
  }
}
```

### 10.4 不要做的事

- ❌ `Bash(curl http://x.com/*)` 限 URL —— 官方说**不可靠**（参数顺序、redirect、变量都能绕）
- ❌ `bypassPermissions` 当日常用
- ❌ `*` 当 `**` 用（gitignore 中 `*` 不跨目录）
- ❌ 把 `Read/Edit deny` 当 OS 级保护——**它不拦 Bash 子进程的 `cat .env`**

更多见 [[07_权限与安全红线_v0.1]]。

---

## 第 11 章 — Hooks：默认不开，但要看懂

### 11.1 为什么默认不开

Hooks 拥有完整用户权限。一行配置就能：
- 偷凭据
- 静默改你给 Claude 的命令
- 把 transcript 发到第三方
- 给 Claude 注入"忽略之前指令"的提示

**风险密度高**，三个月生存战内"省 token"价值不抵失误代价。

### 11.2 但你要看懂，因为：

1. 装第三方插件时要审它的 hooks
2. 看到"我的 Claude 行为很怪"时要能查 hook
3. 未来确实有些场景值得开（**只读审计 + 输出过滤**两类）

### 11.3 安全开 hook 的两个候选

**候选 A：只读审计**
```bash
# PostToolUse 把工具调用记到本地 jsonl
jq '.tool_name, .tool_input' < /dev/stdin >> ~/.claude/audit.log
exit 0
```

**候选 B：输出过滤降本**（来自官方 costs 页例子）
```bash
# PreToolUse：跑测试时只保留失败行，省 token
CMD=$(jq -r '.tool_input.command' < /dev/stdin)
if [[ "$CMD" =~ ^(npm test|pytest|go test) ]]; then
  filtered="$CMD 2>&1 | grep -A 5 -E '(FAIL|ERROR)' | head -100"
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"allow\",\"updatedInput\":{\"command\":\"$filtered\"}}}"
fi
```

### 11.4 永远不做

- 任何 HTTP 出站到非自有域
- `permissionDecision: "allow"` + 通配 matcher
- 把指令性文本（"Run X""Ignore Y"）放进 `additionalContext`
- 安装含上述任一项的第三方插件

详见 [[05_hooks使用规范_v0.1]]。

---

## 第 12 章 — StatusLine：仪表盘

### 12.1 它是什么

Claude Code 把会话 JSON 通过 stdin 传给你的脚本，脚本输出文本，Claude Code 显示——**一个永远在的状态栏**。

### 12.2 推荐显示

最小三件事：

```
[Sonnet | high]  ctx 23%  5h 41%  retail-knowledge-vault
```

字段映射：
- `model.display_name` + `effort.level`
- `context_window.used_percentage`（**最关键**）
- `rate_limits.five_hour.used_percentage`
- `workspace.current_dir` 末段

### 12.3 不要在 statusLine 里做的事

- ❌ 网络调用（卡住整个 UI）
- ❌ 写文件（不是它的责任）
- ❌ 显示 `session_id` 给客户演示（**会被截图**）

详见 [[06_statusLine使用规范_v0.1]]。

---

## 第 13 章 — 日志、transcript 与复盘

### 13.1 落盘位置

| 路径 | 内容 |
|---|---|
| `~/.claude/projects/<repo>/<session>.jsonl` | 完整 transcript（每条消息 / 工具调用 / 工具结果） |
| `~/.claude/projects/<repo>/<session>/tool-results/` | 大块工具输出 |
| `~/.claude/projects/<repo>/memory/` | Auto memory |
| `~/.claude/file-history/<session>/` | 文件改动快照（`/rewind` 用） |
| `~/.claude/history.jsonl` | 你输入过的所有 prompt |

### 13.2 隐私铁律

- 全部明文 markdown / jsonl
- **任何过工具的内容都会落盘**：粘贴的客户数据、命令输出、文件内容、API 输出，统统在内
- 不上云、不跨机器
- **不要同步到 iCloud Drive 默认目录 / Dropbox / OneDrive**

### 13.3 复盘机制（建议方向，不实施）

每月一次，做"transcript 蒸馏"：

```
扫 ~/.claude/projects/<repo>/*.jsonl
    │
    ├── 高频问题（你重复问过 3+ 次的）→ 进 CLAUDE.md / skill
    ├── 翻车案例（你纠正 Claude 的）→ 进 [[反幻觉检查清单]]
    ├── 平均 ctx % / 5h % → 入个人月度复盘
    └── 常用 slash 分布 → 找出"该用没用"的命令

输出：15_刻意练习与成长/月度复盘/2026-MM_ClaudeCode复盘.md
```

**只入库统计与去标识案例，不入库 jsonl 原文**。

详见 [[02_日志与transcript机制总结_v0.1]]。

---

## 第 14 章 — 30 / 60 / 90 天能力升级路线

### 第 1 周（基础就位）

- [ ] 通读本手册 + [[09_Claude_Code使用手册_v0.1]]
- [ ] 配置 statusLine（参考第 12 章 / 待核验配置）
- [ ] 确立"开 / 中 / 收"三段 SOP（第 5 章）
- [ ] 建立"会话先 `/rename`"习惯
- [ ] 启动 [[10_待核验问题清单_v0.1]] 中 5 条优先核验

### 第 2 周（CLAUDE.md 拆分）

- [ ] 起草 `.claude/rules/反幻觉.md`、`陈列.md`、`商品诊断.md`、`方法论.md` 四个文件骨架
- [ ] 把 CLAUDE.md 的 §4–§16 中适合拆出去的段落迁出
- [ ] CLAUDE.md 收敛到 < 200 行
- [ ] **变更前**：`[[变更影响检查清单]]` + 备份 + plan 模式确认
- [ ] **变更后**：在 `00_入口与总索引/版本更新记录.md` 登记

### 第 3 周（Skill 启用）

- [ ] 第一个 skill：`displaymap-check` 或 `sku-diagnosis`（按当前最痛的需求选）
- [ ] 调用 5 次以上，验证调用质量
- [ ] 第二个 skill 跟上

### 第 4 周（Subagent 启用）

- [ ] 第一个 named subagent：`陈列规则巡检员`（Haiku + Read/Grep/Glob）
- [ ] 第二个：`反幻觉巡检员`
- [ ] 周末跑一次"全库巡检"，看输出

### 第 60 天（Permissions 与监控）

- [ ] 部署本手册第 10 章红线
- [ ] StatusLine 三件套稳定运行
- [ ] 每周做一次 `/usage` 自检 + history 蒸馏
- [ ] 完成 [[10_待核验问题清单_v0.1]] 全部 12 项核验

### 第 90 天（复盘机制）

- [ ] 第一个月度复盘（蒸馏 transcript → `15_刻意练习与成长/`）
- [ ] 决定要不要开第一个 hook（仅审计 / 输出过滤）
- [ ] 把"Claude Code 使用手册"派生一份**给客户 / 学员**的精简版

---

## 第 15 章 — 故障排查 FAQ

### Q1：Claude 不听 CLAUDE.md 里的指令

```
1. /memory  看 CLAUDE.md 是不是真加载了（路径 / .gitignore 排除）
2. 如果加载了，检查指令是否够具体（"用 2 空格"vs"格式化代码"）
3. 检查是否有冲突（CLAUDE.md 与 CLAUDE.local.md 与 ~/.claude/CLAUDE.md 自相矛盾）
4. 如果是 /compact 之后丢的——某些信息只在对话里说过，不在 CLAUDE.md
   → 把关键指令补进 CLAUDE.md
```

### Q2：会话越来越慢

```
/context 看占用
├── ctx > 70% → /compact
├── ctx > 90% → /clear（先 /rename）
└── 仍慢 → /usage 看 5h % 是不是逼近上限（被限速）
```

### Q3：一次会话 5 美金没了

```
1. /usage 看是哪个工具最贵
2. 回想：是不是让主会话扫了大文件 / 大目录？
   → 该用 subagent
3. effort 是不是开了 max 跑简单任务？
   → /effort medium
4. 是不是 Opus 跑了周报？
   → /model 切 Sonnet
```

### Q4：Claude 改坏了文件

```
立即 /rewind 或双击 ESC（前提：file-history 完整，待核验）
不行就找 git（如果你有 git）
都不行：~/.claude/file-history/<session>/ 翻快照
```

### Q5：装了第三方插件后行为很怪

```
1. 看插件目录的 hooks/hooks.json
2. 是不是有 type: "http" 出站？
3. 是不是有 permissionDecision: "allow" + 通配？
4. 任一是 → 卸载
```

### Q6：找不到几天前的会话

```
/resume   列出旧会话（按时间）
找不到？ → 翻 ~/.claude/projects/<repo>/*.jsonl 文件名时间戳
仍找不到？ → 下次记得开会话先 /rename
```

### Q7：不确定某个机制是不是这样

```
查 [[10_待核验问题清单_v0.1]]
↓
没列 → 抓官方文档（https://code.claude.com/docs/）
↓
仍不确定 → 先打"待核验"标记，不要写成事实
```

---

## 附录 A — 本 vault 推荐配置（建议方向，不实施）

### A.1 `~/.claude/settings.json` 起步版

```jsonc
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 1
  },
  "permissions": {
    "deny": [
      "Edit(/99_归档/**)",
      "Edit(./CLAUDE.md)",
      "Edit(/00_入口与总索引/**)",
      "Bash(git push *)"
    ],
    "ask": [
      "Bash(rm *)",
      "Bash(mv */99_*)",
      "Edit(/.claude/**)"
    ],
    "allow": [
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)"
    ]
  }
}
```

### A.2 `.claude/rules/` 拆分目标

```
.claude/rules/
├── 反幻觉.md             # 无 paths
├── 逻辑一致性.md          # 无 paths
├── 陈列.md               # paths: ["06_陈列规划与DisplayMap/**"]
├── 商品诊断.md            # paths: ["04_商品诊断与商品力提升/**", "09_门店案例与项目复盘/**/03_商品诊断/**"]
├── 品类管理.md            # paths: ["05_品类管理与商品规划/**"]
├── 营销活动.md            # paths: ["07_营销活动策划与实施/**"]
├── 经营分析.md            # paths: ["08_经营分析与数据看板/**"]
├── 案例与复盘.md          # paths: ["09_门店案例与项目复盘/**"]
└── 方法论.md             # paths: ["01_科学零售方法论/**"]
```

### A.3 第一批 Skill 候选

见第 7.4 节。

### A.4 第一批 Subagent 候选

| 名称 | 工具 | 模型 | 触发条件 |
|---|---|---|---|
| `陈列规则巡检员` | Read / Grep / Glob | Haiku | 主会话提到"陈列" + "扫描"或"检查" |
| `反幻觉巡检员` | Read / Grep / Glob | Haiku | 主会话写完"诊断结论""门店报告"时 |
| `品类一致性检查员` | Read / Grep / Glob | Haiku | 修改品类树或标准品类表后 |

**所有上述配置均需单独授权后实施**。本手册仅作建议方向。

---

## 附录 B — 术语表

| 术语 | 简短解释 |
|---|---|
| Context window | 200K token 的"工作内存"；启动加载 + 对话历史都吃这里 |
| CLAUDE.md | 你写给 Claude 的项目宪法，每会话必加载 |
| Auto memory | Claude 自己写的笔记，存在 `~/.claude/projects/<repo>/memory/` |
| Skill | 打包好的 SOP；启动只显示名 + 描述，调用时才进上下文 |
| Subagent | 独立 context 的专精代理；适合扫库 / 受控审查 |
| Fork | 临时分身，**继承**当前会话上下文 |
| Agent Team | 多代理协同，约 7× token，本阶段不开 |
| Hook | 事件触发的 shell 命令；权力大、风险高，默认不开 |
| StatusLine | 永远在的状态栏，读 stdin JSON 输出文本 |
| Permission Mode | `default / plan / acceptEdits / dontAsk / bypassPermissions` |
| Plan Mode | 只读分析模式，Shift+Tab 进入；大改前必用 |
| `/compact` | 用结构化摘要替换对话历史；CLAUDE.md / auto memory 重新注入；skill 列表不重注 |
| `/clear` | 开新会话；旧会话保留可 `/resume` |
| `/effort` | 推理深度：low / medium / high / xhigh / max / auto |
| `/usage` | 本会话 token + 订阅额度 |
| transcript | `~/.claude/projects/<repo>/*.jsonl`，全明文，含敏感内容 |

---

## 关联

- **上游**：[[README]] · [[00_官方文档目录索引_v0.1]]
- **平级**：[[09_Claude_Code使用手册_v0.1]]（决策树版，深度互补）· [[10_待核验问题清单_v0.1]]
- **下游模块**：[[01_上下文与记忆机制总结_v0.1]] · [[02_日志与transcript机制总结_v0.1]] · [[03_slash命令速查_v0.1]] · [[04_subagents使用规范_v0.1]] · [[05_hooks使用规范_v0.1]] · [[06_statusLine使用规范_v0.1]] · [[07_权限与安全红线_v0.1]] · [[08_token与额度控制规范_v0.1]]
- **vault 治理**：[[知识库治理规范]] · [[反幻觉检查清单]] · [[文档工程化标准]]

---

## 版本记录

| 版本 | 日期 | 修改内容 | 修改人 |
|---|---|---|---|
| v0.1 | 2026-05-04 | 初次创建：综合学习包 01–10 全部主题，写成入门级 + 强指导性手册；含决策树、降本规则、Skill / Subagent 心法、30/60/90 升级路线、FAQ、术语表 | 六哥 + Claude |

---

> **使用本手册的最后一句话**：
> Claude Code 不是越用越省心，是**越有纪律越省心**。建立纪律的成本是前两周的不适，回报是后面 12 个月的复利。
