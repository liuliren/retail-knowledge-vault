---
name: ingest-retail-deprecated
description: 【已废弃·改用根层跨库版 /ingest】本 retail 局部版已被根层 .claude/skills/ingest 取代(2026-06-26·B案)。canonical 在根层,全库生效。本文件不再触发,保留仅防误用。
allowed-tools: Bash, Read, Write, Edit
status: deprecated
---

# ⚠️ /ingest（retail 局部版 · 已废弃 2026-06-26）

> **本 skill 已废弃**。canonical 跨库版在 **`/Users/davidliu/KnowledgeBase/.claude/skills/ingest/SKILL.md`**(全库生效·进料中枢为输入源·路由到任意子库·带机制A相位+机制B复盘闭环)。
> **为何废弃**:本版长在 retail、路径 retail 中心,违背"一处定义全库通用 + 进料 infra 系统级"(B案)+ SSOT(同名概念一处权威定义)。
> **请用根层版**。删除本文件需六哥签(§3④)。

---
> 以下为历史内容(失效·勿用):
> [[输入系统架构_v0.1]] 的执行引擎。把 raw 内容(L1)**编译一次**成可检索的概念页(L3),之后查询只读编译层、0 raw。
> **铁律**:LLM 编译在**进料时**发生(一次性);raw 冻结 `.no-ingest`,查询永不读 raw。**理解前移到编译,LLM 只推理不阅读。**
> **跨库通用**:retail / growth / build / 家庭库共用一套方法(这就是"输入问题解决后形成的那套方法")。

## 何时用
- 六哥说"ingest 这篇 / 消化这条 clip / 编译进 wiki / 把 X 收进知识库"。
- 批量:整理 Clippings 某主题目录。

## 步骤

### Step 1 — 结构化提取 + 路由 + 台账登记(脚本)
```bash
python3 "13_数据分析与工具脚本/脱敏测试链路_v0.1/ingest_helper.py" "<clip.md路径>" --date 2026-06-25
```
输出:标题/来源/标签/**域(路由)**/消化摘要,并追加台账一行。
路由:零售老刘·门店·商品研究→retail;AI·Claude→build/主库;一人公司·营销→growth/media。

### Step 2 — LLM 编译(判断层·一次性)
据 raw 正文 + Step1 摘要,产出 **L2/L3 概念页**(落 Step1 建议目录):
- frontmatter:`summary:`(≤150词·结论先行)+ `source_attribution`(原 clip 链接,§6 A层)+ tags + status `seed`。
- 正文:**去冗去噪标准化** → 核心观点 MECE + **so-what(对六哥域的用法)** + `[[wikilink]]` 关联已有概念页(建即入链,治孤儿)。
- **保真**:不改六哥第一人称;外部观点标来源;不大段复制原文(A层§6)。

### Step 3 — 挂 MOC(治孤儿)
把新概念页挂到对应 MOC/索引(retail→[[科学零售知识树_MOC]];主库→各库 MOC)。

### Step 4 — 回填台账 + 收口
- 用编译后概念页路径回填台账"编译进"列(或重跑 helper 带 `--note`)。
- 报六哥:一句话——这篇讲什么 + 编译进哪 + 关联了哪些已有节点。

## 铁律清单
- raw 只在 ingest 时读(显式授权动作);概念页带 `summary:` 供 G02 廉价检索。
- 外部内容 = A 层 `external_reference`,必标 source;不进对外交付大段复制。
- 多模态:音视频→先转录文本再 ingest;图→caption。**不在查询时读媒体。**
- 概念页 status `seed`→`draft`→`stable`,升级需六哥(§3②)。

## 复用资产
- 结构化/台账:`ingest_helper.py`。架构:[[输入系统架构_v0.1]]。体系:[[体系个人知识库与内容板块_方案_v0.1]]。

## 已跑案例
- 零售老刘《品类建模227 论类要清晰》→ retail 零售老刘体系(见台账)。
