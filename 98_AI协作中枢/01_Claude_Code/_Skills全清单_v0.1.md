---
title: Skills 全清单 v0.1
created: 2026-06-28
owner: 六哥
status: active
summary: 知识库全部已注册 Skill 的分类索引、功能说明与使用场景。
tags: [skills, 索引, AI操作层]
---

# Skills 全清单 v0.1

> **15 个 Skill（含1个废弃）分属 6 大类**。触发方式：对话中直接说触发词，或输入 `/skill名`。
> 根层 skill（`KnowledgeBase/.claude/skills/`）全库生效；retail 层 skill 仅 retail-knowledge-vault 内生效。

---

## 类别一：知识进料与编译（Input OS）

> **核心价值**：把外部原文自动变成可查询的 wiki 页，LLM 编译一次、查询零成本。这是 Karpathy 原则的落地——`10_sources/` 存进冻结，`30_wiki/` 可随模型进步重新编译。

### `/ingest` · 跨库内容编译引擎（根层 · 全库生效）
- **路径**：`KnowledgeBase/.claude/skills/ingest/`
- **功能**：把 `Clippings/` 进料中枢里的 raw 内容（文章/clip/转录/caption）编译成带 `summary+标签+wikilink` 的概念页，自动路由到对应子库（retail/build/growth/AI/家庭）→ 挂 MOC → 登记台账。
- **触发词**：`ingest这篇` / `消化clip` / `编译进wiki` / `把X收进知识库` / `消化中枢某主题`
- **价值**：消灭"读了就忘"漏洞；每篇输入自动变为可检索资产；支持批量并行。
- **版本**：v1.1（B案·独立进料中枢，retail 库零 raw）

### `/process-inbox` · Inbox 分流引擎（根层 · 全库生效）
- **路径**：`KnowledgeBase/.claude/skills/process-inbox/`
- **功能**：扫描 `Clippings/_inbox/` 与各库 `20_inbox/`，逐条分类路由（source/wiki/decision/task/delete），不留孤儿，登记台账。
- **触发词**：`处理inbox` / `分流inbox` / `清空收件箱` / `消化积压` / `process-inbox`
- **铁律**：留孤儿数 = 0；有决策质量的必建 M-DEC stub；先问不明确的，不自行裁断。
- **版本**：v0.1（2026-06-28 首建）

### ~~`/ingest`（retail 局部版 · 已废弃）~~
- **路径**：`retail-knowledge-vault/.claude/skills/ingest/`
- **状态**：`deprecated`（2026-06-26·被根层版取代）
- **说明**：保留防误用，不再触发。

---

## 类别二：知识库治理（Governance）

> **核心价值**：系统默认腐烂（熵增），治理 skills 是主动做功的负熵工具。定期跑，防孤儿、防断链、防隐私越界。

### `/lint-kb` · 知识库健康体检（根层）
- **路径**：`KnowledgeBase/.claude/skills/lint-kb/`
- **功能**：全库健康扫描——孤儿页、断链、缺 summary、status 非法、陈旧（超期未更）、空白占位页。输出健康仪表盘 + 修复建议。
- **触发词**：`跑下lint` / `知识库体检` / `查孤儿` / `查断链` / `kb lint`
- **价值**：把"系统腐烂"从隐性变成可见；每次写入配一次凋亡审计，落实第 9 条原则（熵减纪律）。

### `/lint-privacy` · 隐私越界自查（根层）
- **路径**：`KnowledgeBase/.claude/skills/lint-privacy/`
- **功能**：专项检查客户原始数据是否漂出只读区、开放层/媒体稿是否残留客户真名、T2/T3 内容是否进入公开层。对外发布前必跑。
- **触发词**：`隐私检查` / `lint隐私` / `查隐私越界` / `发布前查脱敏` / `上云前自查`
- **价值**：「keys not prompts」第一道权限挡——客户机密违规从 AI 行为问题变成可审计的检测问题。

### `/doc-merge` · 双文档冲突裁定（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/doc-merge/`
- **功能**：读取两份内容相近的文档，逐字对比，判定 IDENTICAL / OVERLAP / DIVERGENT，产出：删除建议 OR 合并草稿 OR 新建正本。裁定结果放输出区，六哥确认后执行。
- **触发词**：`双文档对比` / `文件重复` / `版本取舍` / `文档合并` / `副本裁定` / `doc-merge`
- **决策树**：IDENTICAL → 保留路径规范的那份，删副本 | OVERLAP → 提取各自独有部分合并 | DIVERGENT → 以完整版为骨架综合新正本
- **价值**：把归档治理中最耗判断力的"哪个是正本"问题标准化，防止重复文件漂移积累。
- **版本**：v0.1（2026-06-28 首次使用·裁定3个99_归档冲突）

### `/promote` · M-DEC 决策闭环（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/promote/`
- **功能**：对已知结果的决策：回填 `actual_outcome + lessons` → 蒸馏进对应概念页（追加"M-DEC验证案例"块）→ 状态 open → closed。
- **触发词**：`决策有结果了` / `回填M-DEC` / `方法论回补` / `结项` / `蒸馏决策` / `promote`
- **铁律**：不代替六哥写教训（Step 2 必须六哥口述）；只追加不覆盖概念页；一次只 promote 一个 M-DEC。
- **版本**：v0.1（2026-06-28 首建·M-DEC 缺的那座桥）

---

## 类别三：精读与语料处理（Reading Engine）

> **核心价值**：把"买了没读"变成"读了有产出"；支撑公开构建（第 8 条原则），让输入自动变为方法论资产的上游。

### `/深度精读` · 逐字精读引擎（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/深度精读/`
- **功能**：对长语料系列（如 99_归档 526 篇、零售老刘 321 篇）逐批全文精读，产出精读卡（核心论点 + 关键词 + 回填候选）→ 更新进度表 → 更新 RESUME → 精确 commit。支持断点续传、节奏自适应，遇需六哥判断的签字门自动暂停。
- **触发词**：`深度精读` / `逐字精读` / `续读` / `精读下一批` / `读语料` / `deep read`
- **价值**：把"大量输入无从消化"转为可复用精读卡；精读卡是方法论回补（/promote）的上游，形成输入→精读→wiki→对外的完整复利环。
- **特色**：项目模式（中途不问是否继续）+ 批次大小自适应 + ⭐⭐⭐ 签字门

### `/语料巡检` · 每日新语料巡检（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/语料巡检/`
- **功能**：每日定时（或手动触发）扫描 `Clippings/` 进料中枢中自上次以来新增的语料，逐条分类路由（短 clip → ingest 编译 / 长系列 → 深度精读队列 / raw → 冻结待 ingest）→ 登记台账 → 报告六哥，不留孤儿。
- **触发词**：`语料巡检` / `扫新语料` / `今天有什么新输入` / `检查新clip` / `daily corpus scan`
- **价值**：让进料成为无感的工作流副产品，而非额外动作（第 4 条原则：自动化深嵌业务流）；防止 Clippings 积压成"知识泄漏区"。

---

## 类别四：诊断与交付（Diagnosis & Delivery）

> **核心价值**：这是 90/10 护城河中"90%可商品化"的自动化引擎——诊断报告、交付卡从手工整理变成一条命令。

### `/单品类诊断` · 端到端商品诊断（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/单品类诊断/`
- **功能**：给一个品类名或 raw `.xls` 数据，一条指令跑完：脱敏 → 分层失真分析 → 可发客户的诊断卡（Markdown + PDF/PNG）。核心产物：A 卡（诊断洞察）+ B 卡（行动建议）。
- **触发词**：`诊断X类` / `测X类` / `出X的诊断卡` / `category diagnosis`
- **依赖**：`gen_card.py`（编译器）+ `render.py`（Playwright 渲染器）+ `design_tokens` SSOT
- **价值**：首个实现「商品诊断即产品」的执行引擎；花厅坊已验证（饼干/方便食品/巧克力/库存订货 4 个品类全跑通），可直接复制给沙埔大道第二店。
- **版本**：v0.3（含 IssueTag 选品决策 + 品牌密度型失真 + 脱敏链路）

### `/report-export` · 诊断卡导出引擎（根层）
- **路径**：`KnowledgeBase/.claude/skills/report-export/`
- **功能**：把诊断数据编译成可直接发给店长/老板的一页诊断卡（A 卡诊断 + B 卡行动），支持 JSON→HTML→PDF/PNG 全链路。遵守 E 层（client_shareable：0 术语 0 条码 0 进价）发布标准。
- **触发词**：`出诊断卡` / `导出报告` / `生成PDF` / `做张图发店长` / `发客户的报告`
- **依赖**：`gen_card.py` + `render.py` + `design_tokens.json`
- **价值**：把 6 哥的判断力打包成可发送的一页纸——这是变现的最后一公里；`/单品类诊断` 的下游出口。

### `/draft` · 媒体稿起草引擎（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/draft/`
- **功能**：从 wiki 取料，按六哥风格起草公众号/视频号/小红书稿（骨架确认 → 正文 → 隐私检查 → 写入输出区 → 回流台账）；停在签字门。
- **触发词**：`帮我写一篇` / `起草公众号稿` / `draft这个主题` / `出稿` / `视频号` / `小红书`
- **铁律**：不主动对外发布（D档强制签字）；案例必须脱敏；产物必须回流台账；>1000字必先确认骨架。
- **版本**：v0.1（2026-06-28 首建）

---

## 类别五：会话管理（Session Management）

> **核心价值**：长会话下防止上下文丢失；跨会话保持工作连续性；确保压缩前关键信息已落地。

### `/project-compact-governance` · 上下文压缩治理（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/project-compact-governance/`
- **功能**：长会话压缩前的安全治理——检查未提交变更、梳理当前进度、确保关键内容已写入 RESUME 断点，输出"可安全压缩"的确认报告。
- **触发词**：`会话太长了` / `准备compact` / `上下文快满了` / `compress` / `压缩前检查`
- **价值**：防止"压缩后丢失关键决策"；是 Task 系统 v1.0 RESUME 收敛机制的前置步骤。

### `/project-handoff` · 会话交接文档（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/project-handoff/`
- **功能**：在 `/compact` 或 `/clear` 前生成结构化交接文档，包含：当前进度快照、活跃文件指针、未完成任务、下一步 3 条，让新会话即开即用。
- **触发词**：`生成交接文档` / `准备新会话` / `handoff` / `交接` / `新会话prompt`
- **价值**：实现跨会话的工作记忆连续性；与 RESUME 断点互为补充（RESUME 是常驻导航层，handoff 是一次性深度快照）。

### `/review` · 周月复盘引擎（retail 层）
- **路径**：`retail-knowledge-vault/.claude/skills/review/`
- **功能**：从 logs+decisions+outputs 合成复盘稿；**强制对照 2026 三目标**（营收30万/5客户/30诊断）和花厅坊交付窗口；产出复盘稿 + 3 件下期撬动任务 + parking lot → 写入 life-vault + 更新 RESUME。
- **触发词**：`周复盘` / `月复盘` / `总结这周` / `review week` / `review month` / `帮我复盘`
- **铁律**：三目标必须对照；禁止粉饰（卡住的必诚实列）；3件下期任务停在签字门等确认。
- **版本**：v0.1（2026-06-28 首建）

---

## 类别六：调度（Scheduling）

> **核心价值**：把每日启动/关机例程自动化，防止"开机不知干啥"和"关机未收口"的注意力损耗。

### `/zero-scheduler` · 佐罗调度器（根层）
- **路径**：`KnowledgeBase/.claude/skills/zero-scheduler/`
- **功能**：每日两次固定回路——`Zero boot`（晨起：拉今日仪表盘 + 排 3 件撬动任务）和 `Zero flush`（晚间：回流今日产出 + 更新 RESUME + 标记完成）。
- **触发词**：`Zero boot` / `晨起` / `开机` / `今日任务` / `Zero flush` / `晚间回流` / `收工` / `关机`
- **价值**：把六哥从"手动维护知识"中解放出来——开机即知道干什么，关机自动完成收口。是第 4 条原则（自动化深嵌业务流）在时间管理层的落地。

---

## 新建 Skill（2026-06-28 完成）

| Skill | 类别 | 层级 | 核心价值 |
|---|---|---|---|
| `/promote` | 知识治理 | retail层 | M-DEC 决策记忆闭环·方法论回补的关键桥梁 |
| `/review` | 会话管理 | retail层 | 周月复盘引擎·强制对照2026三目标+花厅坊窗口 |
| `/draft` | 诊断交付 | retail层 | 媒体稿起草引擎·wiki取料→产物回流·签字门前止步 |
| `/process-inbox` | 进料编译 | 根层 | inbox分流·留孤儿数=0·source/wiki/decision/task路由 |

---

## 快速索引（完整·12个活跃+1个废弃）

| Skill | 类别 | 层级 | 状态 | 最近使用/建立 |
|---|---|---|---|---|
| `/ingest` | 进料编译 | 根层 | active v1.1 | 2026-06-28 |
| `/process-inbox` | 进料编译 | 根层 | active v0.1 | 2026-06-28 ★新建 |
| `/lint-kb` | 知识治理 | 根层 | active | — |
| `/lint-privacy` | 知识治理 | 根层 | active | — |
| `/doc-merge` | 知识治理 | retail层 | active v0.1 | 2026-06-28 ★新建 |
| `/promote` | 知识治理 | retail层 | active v0.1 | 2026-06-28 ★新建 |
| `/深度精读` | 精读引擎 | retail层 | active | 2026-06-28 |
| `/语料巡检` | 精读引擎 | retail层 | active | — |
| `/单品类诊断` | 诊断交付 | retail层 | active v0.3 | 2026-06-27 |
| `/report-export` | 诊断交付 | 根层 | active | 2026-06-27 |
| `/draft` | 诊断交付 | retail层 | active v0.1 | 2026-06-28 ★新建 |
| `/review` | 会话管理 | retail层 | active v0.1 | 2026-06-28 ★新建 |
| `/project-compact-governance` | 会话管理 | retail层 | active | — |
| `/project-handoff` | 会话管理 | retail层 | active | — |
| `/zero-scheduler` | 调度 | 根层 | active | — |
| ~~`/ingest`（retail局部版）~~ | 进料编译 | retail层 | **deprecated** | 2026-06-26废弃 |
