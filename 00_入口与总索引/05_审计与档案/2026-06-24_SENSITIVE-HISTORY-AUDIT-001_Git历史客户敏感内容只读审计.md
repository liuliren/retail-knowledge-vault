---
id: SENSITIVE-HISTORY-AUDIT-001
title: Git 历史客户敏感内容只读审计
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/05_审计与档案
client_safety: internal_only
summary: 只读审计 retail-vault Git 历史的客户敏感范围；本报告本身为 B 区治理元数据，不回写客户数字/SKU/员工姓名。
tags:
  - 审计
  - Git历史
  - 客户隐私
  - SENSITIVE
---

# SENSITIVE-HISTORY-AUDIT-001｜Git 历史客户敏感内容只读审计

> 依据 [[SENSITIVE-GOV-001_客户数据脱敏与Git保密治理规范_v0.1]]。**纯只读**:未改写历史、未删除、未脱管、未改 .gitignore。本报告只记 hash/计数/风险级,不回写客户经营数字、SKU、条码、进价、供应商裸名、员工姓名。

## 1. 执行结论
- **发现历史敏感内容,最高风险 R4**(客户员工姓名,personal info)。
- **R2(客户派生结论)在历史中普遍存在**;**R3(明细类)疑似存在**(待内容级复核);**R0 原始数据 xls/csv/db 从未入 git**(唯一好消息)。
- **远端已暴露**:GitHub 远端 `origin/main` 已含 77 个客户文件;但**绝大部分敏感历史(235/243 commit)尚未推送**。
- **需后续裁决**:是否历史改写;**但本轮不执行,且改写前必须先确认远端仓库可见性**。

## 2. 审计边界
只读 `git log / show / ls-files / ls-tree / branch / tag / remote`。**未** filter-repo/BFG、未 rebase/reset/amend、未 git rm、未删文件、未改 .gitignore、未改业务正文、未脱敏写入、未碰 xls/csv/db、未 `git add .`。

## 3. 仓库状态
| 项 | 值 |
|---|---|
| 当前分支 | `main` |
| 远端 | `origin` = GitHub `liuliren/retail-knowledge-vault` |
| 总 commit | 243 |
| **已推送 origin/main** | **8 commit / 283 文件**(其中 **77 个含花厅坊**)|
| **本地未推送** | **235 commit**(领先 origin/main)|
| origin 领先本地 | 0 |
| 本地分支 | main + `claude/exciting-greider-d43782` + `claude/happy-knuth-15e49c`(两者**均 0 领先 main**,无额外风险)|
| tag | 0 |
| **远端推送风险** | **高**:一旦 `git push`,235 个含客户明细/金矿的 commit 将上传 GitHub |

## 4. 可疑 commit 范围(按 message 关键词,只读计数)
| 关键词 | commit 数 | 关键词 | commit 数 |
|---|--:|---|--:|
| 花厅坊 | 113 | dry-run | 32 |
| 候选 | 33 | execute | 29 |
| 毛利 | 18 | 供应商 | 15 |
| 条码 | 14 | 金矿 | 10 |
| 进价 | 10 | 明细 | 10 |
| 动销 | 8 | 沙埔 | 3 |
| 补货 | 2 | 库龄 | 2 |
| 清库 | 1 | PSD | 1 |

## 5. 当前 HEAD 树客户敏感文件计数(现况范围)
| 类别 | 数量 |
|---|--:|
| 路径含「花厅坊」的文件 | 290 |
| 路径含「金矿/候选/明细/清库/补货」 | 30 |
| 路径含疑似客户员工姓名 | 6 |
| goldmine 类 .py 工具 | 14 |
| **xls/xlsx/csv/db(历史+现况)** | **0** ✅ |

## 6. 重点 commit 审计(只读 name-status,不看内容)
| commit | 性质 | 新增/改动 | 级别 | 建议 |
|---|---|---|---|---|
| `b9aecbd` | 金矿池处置结构 review | 新增 Review-003 稿 + 改 Claude执行日志 | R2 | 待裁决 |
| `0cf4647` | D 清库「完整明细」说明 | 新增 D 明细稿 + `goldmine_bucketD_detail.py` + 改 Claude执行日志 | **R2–R3** | 待内容级复核 |
| `c4d8522` | B 控补货「完整明细」说明 | 新增 B 明细稿 + `goldmine_bucketB_detail.py` + 改 Claude执行日志 | **R2–R3** | 待内容级复核 |
| `b8e8bdb` | 金矿 5 桶分层抽样说明 | 新增抽样稿 + `goldmine_sample_pack_003.py` + 改 Claude执行日志 | R2 | 待裁决 |
> 这 4 个「完整明细/抽样」.md **当前仍 tracked**(在 `03_治理规范/`),既是历史风险也是**现况风险**——是未来 `git rm --cached` 候选(本轮不动)。

## 7. Claude执行日志历史残留
- `98_AI协作中枢/01_Claude_Code/Claude执行日志.md` 在 `3f78c77` 已脱管(GIT-HYGIENE-002);但**历史中有 67 个 commit 改动过它**,客户诊断内容嵌入这 67 个历史快照。
- 最高风险:R2(客户诊断聚合)。**脱管只停未来,历史快照仍在。**

## 8. 是否需要历史改写(初步判断,不执行)
**判断:不在本轮决定;先确认前置,再另起方案任务。**
- 否决"立即 filter-repo":前置未明(仓库可见性未知 / 改写影响 235 commit + 远端)。
- 倾向路径:**① 先确认 GitHub 仓库 private/public + 协作者范围 → ② 据此走 SENSITIVE-HISTORY-PLAN-001 制定改写或私有化方案。**
- 若仓库 private 且仅本人:可能"未来阻断 + 不再推送敏感 commit"即足,改写非必须。
- 若 public:R3/R4 已公开暴露,属高危,需优先私有化 + 评估改写。

## 9. 下一步建议(分层)
- **立即动作(本人,非 Agent)**:① 在 GitHub 确认 `liuliren/retail-knowledge-vault` 可见性与协作者;② **暂停 `git push main`**,避免把 235 个敏感 commit 推上去。
- **暂缓动作**:历史改写方案(待可见性确认后另起 SENSITIVE-HISTORY-PLAN-001)。
- **禁止动作(未授权前)**:filter-repo / BFG / rebase / reset / 强推。
- **需用户裁决**:(a) 仓库可见性结论;(b) 4 个「完整明细/抽样」现况文件 + 14 个 goldmine 脚本是否先 `git rm --cached`(类 Claude执行日志处理);(c) 是否需要历史改写。

## 10. 未触碰范围
未执行 filter-repo/BFG;未 rebase/reset/amend;未 git rm / git rm --cached;未删除文件;未改 .gitignore;未改业务正文;未脱敏写入;未碰 xls/xlsx/csv/db;未 `git add .`;未 push。
