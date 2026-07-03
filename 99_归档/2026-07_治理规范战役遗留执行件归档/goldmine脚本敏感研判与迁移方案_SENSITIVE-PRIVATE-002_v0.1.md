---
title: goldmine 脚本敏感研判与迁移方案 SENSITIVE-PRIVATE-002
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
---

# goldmine 脚本敏感研判与迁移方案 v0.1（只读·不执行）

> SENSITIVE-PRIVATE-002:对 goldmine .py 做**只读内容研判** + 出迁移方案。**不执行迁移、不 git rm --cached、不移动文件、不改脚本正文、不 push。** 最终是否迁移由六哥在 SENSITIVE-PRIVATE-003 裁决。

## 0. 关键事实(只读核出)
1. **所有 .py 均无真实数据值**(无 EAN-13 条码、无进价裸值)——敏感点 = ①客户名在**路径/注释/输出文件名**;②脚本**编码了花厅坊数据结构与金矿口径**(咨询 IP + 客户数据结构暴露)。
2. 「6 个 goldmine .py」= 6 个 `goldmine_` 前缀文件(数量吻合);merge/full_dryrun/通用件作扩查一并研判。

## 1. 6 个 goldmine .py 研判
| 文件 | 客户耦合 | 逻辑性质 | 分类 |
|---|---|---|---|
| goldmine_sample_pack.py | 花厅坊默认路径/输出名 | 分层抽样(通用)| **可脱敏保留** |
| goldmine_sample_pack_003.py | 同上 | 5桶分层抽样(通用)| **可脱敏保留** |
| goldmine_prejudge.py | 同上 | 机器预判规则(通用)| **可脱敏保留** |
| goldmine_bucketB_detail.py | 同上 | 控补货明细(通用)| **可脱敏保留** |
| goldmine_bucketD_detail.py | 同上 | 清库明细(通用)| **可脱敏保留** |
| goldmine_bucketCE_detail.py | 同上 | 缩面/复核明细(通用)| **可脱敏保留** |
> 6 个共性:**算法/分桶逻辑通用,客户耦合仅在 default 路径 + 输出文件名(花厅坊)**。无数据值。脱敏=把客户名/路径从硬编码 default 抽到 **CLI 参数或 gitignored client_config**,逻辑即通用复用。

## 2. 扩查 tools/ 父目录(全部 .py)
| 文件 | tracked | 客户命中 | 分类 |
|---|:--:|:--:|---|
| abc_classifier.py | ✅ | 2(注释泛称「如花厅坊」)| **通用脚本**(核心 ABC+金矿口径;2 处泛称可顺手脱敏)|
| ir_calculator.py | ✅ | 0 | **通用脚本** |
| safety_stock.py | ✅ | 0 | **通用脚本** |
| test_retail_tools.py | ✅ | 0 | **通用脚本** |
| full_dryrun_90d.py | ✅ | 4(默认路径/输出名)| **可脱敏保留** |
| merge_full_90d.py | ✅ | 12(输入结构+供应商汇总文件名+生鲜档案config)| **客户专用·待裁决**(最深耦合)|
| goldmine_*.py ×6 | ✅ | 3-4 | 可脱敏保留(见 §1)|
| retail_tools_dryrun.py | ❌ untracked | 0 | 不在 git,无迁移动作 |

## 3. 分类汇总
- **通用脚本(留 tracked·纯方法)**:abc_classifier / ir_calculator / safety_stock / test_retail_tools(abc 2 处泛称可脱敏)。
- **可脱敏保留(参数化客户名/路径后留 tracked)**:full_dryrun_90d + 6 个 goldmine_*.py(共 7)。
- **客户专用·待人工裁决**:merge_full_90d(深耦合花厅坊输入结构/文件名/生鲜 config)。
- **无需动作**:retail_tools_dryrun.py(已 untracked)。

## 4. 迁移方案(两选项·供 SENSITIVE-PRIVATE-003 裁决·本轮不执行)

### 方案 A（推荐）：脱敏参数化保留——脚本留 tracked,客户配置外移私有区
- 把所有「花厅坊默认路径 / 输出文件名 / 生鲜档案 config」从脚本**抽到一个 gitignored `client_config_花厅坊.py`(或 .json,放私有区)**;脚本读配置,**default 改通用占位**;
- 效果:脚本=**通用方法论工具留 git**(可复用第二客户);**客户耦合(路径/文件名/生鲜清单)进私有区不入 git**;
- 适用:认定脚本逻辑是可复用 Harness、客户专用部分仅是配置。
- 改动量:中(7 脱敏 + merge 深参数化);**属代码改动,须另轮授权(非本只读轮)**。

### 方案 B：整体迁私有区——goldmine 全链 .py 迁出 git
- 把 6 goldmine + merge + full_dryrun 整体 `git mv` 到私有 gitignored 区;
- 效果:客户口径 IP 完全脱离版本库(最保守);
- 代价:**丢失方法论复用**(下个客户要重写)、与已 active 的 §3.1.x 注册表口径脱节;
- 适用:认定「金矿全链口径」本身即客户机密、不宜留 git。

### 方案 C（折中）：通用件留 + 客户专用件迁
- 通用脚本(abc/ir/safety/test)+ 可脱敏件(full_dryrun + 6 goldmine,参数化后)留 tracked;
- **仅 merge_full_90d 迁私有区**(它最客户专用);
- 适用:只隔离最深耦合的一个。

> **AI 倾向方案 A**:无 .py 含数据值,逻辑是 90/10 的可复用 Harness;把"客户配置"隔进私有区,既保复用又隔敏感,最符合 §1 护城河与 §3.1.3 客户级数据质量精神。但**最终由六哥裁决**。

## 5. 本轮边界(已守)
- **只读研判**:未执行迁移、未 git rm --cached、未移动文件、未改任何脚本正文、未 push;
- 仅新增本方案 md(+ 债务队列登记);
- 真实数据/明细/客户配置均未动。

## 6. 待六哥裁决(进 SENSITIVE-PRIVATE-003 前)
1. 选方案 A(脱敏参数化保留)/ B(整体迁私有)/ C(折中只迁 merge)?
2. 私有区路径确认(SENSITIVE-PRIVATE-001 已建的私有区在哪)?
3. 若选 A/C,代码改动(参数化/迁移)须**另轮授权**(本只读轮不动代码)。

## 版本记录
| v0.1 | 2026-06-24 | SENSITIVE-PRIVATE-002 只读研判:6 goldmine_*.py=可脱敏保留(逻辑通用·客户耦合仅路径/文件名);扩查 tools/ 13 .py 分类(通用4/可脱敏保留7/客户专用待裁决1=merge/untracked1);所有.py无数据值。迁移方案A脱敏参数化保留(荐)/B整体迁私有/C折中只迁merge。不执行迁移不改正文不push,待六哥裁决进PRIVATE-003 |
