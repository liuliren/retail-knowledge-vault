---
name: scan
description: 每日定时扫新语料的固定任务引擎。扫描 Clippings/素材暂存里自上次以来新增的语料→逐条分类路由(短clip→ingest编译/长系列→深度精读队列/raw→冻结待ingest)→登台账→报六哥,不留孤儿。停在签字门。触发:语料巡检/扫新语料/今天有什么新输入/巡检语料/检查新clip/daily corpus scan。
allowed-tools: Bash, Read, Write, Edit
---

# /scan skill（每日新语料巡检 · 固定任务引擎）

> **这是什么**:把"新语料进来了吗→该怎么处理"做成每天可定时跑的固定回路。它是 `/ingest`（编译单篇）和 `/deep-read`（逐字读系列）的**上游分流器**——先发现、分类、排队，再决定谁走 ingest、谁进精读、谁先冻结。
> **定位**:纯检测 + 分流 + 登记,**绝不擅自编译/发布/删除**;实际 ingest 或精读仍按各自 skill 的签字门走。

## 何时用
- 六哥说"语料巡检 / 扫新语料 / 今天有什么新输入 / 检查新 clip"。
- **每日定时任务**:由 launchd/cron 在固定时间自动调起(见末尾「定时设置」)。

## 铁律
1. **只读检测**:`scan.sh` 只 `find`,不碰内容文件。
2. **不留孤儿**:每个新语料必须给出一个去向(ingest / 深度精读队列 / 冻结待办 / 忽略并说明),不能扫完就完。
3. **停在签字门**:巡检只到"分类+登记+排队";真正 ingest 编译、升 active、对外发布,仍需六哥按 `/ingest`/`/deep-read` 的门走。
4. **去重**:对照已有台账(`内容消化台账_v0.1` / `Clippings全量阅读台账_v0.1` / 零售老刘深读台账),已读/已编译的不重复排队。
5. **巡检完打戳**:处理完调 `scan.sh --stamp`,下次只看增量。

## 步骤

### Step 1 — 扫增量
```bash
bash "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/.claude/skills/scan/scan.sh"
```
输出=自上次 marker 以来新增/改动的 `.md` 清单（首次无 marker → 最近 7 天）。监视目录默认 `Clippings/` + `90_素材暂存与待整理/`（在 scan.sh 顶部 `WATCH=()` 增减）。

### Step 2 — 逐条分类路由
对每个新文件，读首屏 + 标题，判定去向（结论先行，一行一条）：
| 类型 | 特征 | 去向 |
|---|---|---|
| **成系列长文**（如"零售老刘 XX 系列(NN)"） | 属某连载、需逐字精读 | → 排入 **`/deep-read`** 队列（更新对应进度表/有序索引；零售老刘归 321 工程） |
| **独立单篇/命题级** | 一篇一概念、可一次编译 | → 排入 **`/ingest`** 队列（短清单，等六哥批量 ingest） |
| **raw 素材**（xls/截图/转录草稿） | 未成文、待整理 | → 标"冻结待 ingest"，留 `90_素材暂存`，不进上下文 |
| **客户可识别原始数据** | 含门店名/条码/进价 | → ⚠️ 停！标隐私门，提示走 `/lint-privacy`，**不路由不读入** |
| **重复/已处理** | 已在台账 | → 忽略并标注来源台账行 |

### Step 3 — 登台账 + 报六哥
- 在根层唯一权威台账 `KnowledgeBase/_内容消化台账.md` 末尾追加本次巡检批次（日期/文件数/各去向计数/逐条一句话）。旧路径 `00_入口与总索引/05_审计与档案/内容消化台账_v0.1.md` 已废弃，不再写入。
- 给六哥一段**结论先行**的简报：新增 N 篇 → X 进深度精读队列、Y 进 ingest 队列、Z 冻结、W 触隐私门；**建议下一步动作 1-3 条**（如"零售老刘新增5篇已并入321有序索引，可继续 /deep-read"）。

### Step 4 — 打戳收口
```bash
bash "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/.claude/skills/scan/scan.sh" --stamp
```
> 若本次有未处理完的，先别打戳，下次继续。

## 定时设置（每日固定次数）
> ⚠️ 本库是**本地 Vault**。云端 `/schedule` 路由跑在 Anthropic 云、**读不到本地文件**,不适用。本地每日固定任务两条路:
- **A · launchd(推荐·真·每日无人值守)**:用本目录的 `com.liuge.yuliao-patrol.plist`（每日 09:00 / 18:00 两次，调起 `claude -p "/scan"`）。加载:
  ```bash
  cp "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/.claude/skills/scan/com.liuge.yuliao-patrol.plist" ~/Library/LaunchAgents/
  launchctl load ~/Library/LaunchAgents/com.liuge.yuliao-patrol.plist
  ```
  关掉:`launchctl unload ~/Library/LaunchAgents/com.liuge.yuliao-patrol.plist`。改时间/次数=编辑 plist 里的 `StartCalendarInterval`。
- **B · 会话内 /loop(轻量·仅当前终端开着时)**:`/loop 6h /scan`（每6小时扫一次，关终端即停）。适合"今天先盯着跑跑看"。

## 关联
`/ingest` · `/deep-read` · [[内容消化台账_v0.1]] · [[Clippings全量阅读台账_v0.1]] · `/lint-privacy`（隐私门）
