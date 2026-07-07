---
title: 脚本mock测试报告（Phase-Y·Y7）
summary: tool_drafts 4个新脚本v0.1的mock实测结果：4/4通过，含边界用例（缺目录/非git仓库）。
version: v0.1
status: draft
owner: Claude（Phase-Y）/ 六哥（裁决）
created: 2026-07-08
source_type: audit_note
client_safety: internal_only
---

# 脚本 mock 测试报告 draft（Y7 · 2026-07-08 实跑）

> mock 数据：`13_数据分析与工具脚本/tool_drafts/mock_test_data/` 5 个**全虚构** md（正常页阴性对照 / active缺signoff / status污染+缺summary / 非法status值 / 假 M-DEC 卡含1个断链wikilink）。零真实客户数据。

| 脚本 | 测试方式 | 结果 | 问题 | 下一步 |
|---|---|---|---|---|
| frontmatter_status_checker_v0.1 | `--dir mock_test_data` 实跑（5文件） | ✅ 4/4 类问题全部命中且无误报：污染×1、缺summary×1、active缺signoff×1、非法值×1；阴性对照页0报警；exit=1（有问题时）符合设计 | 无 | 六哥确认7值合法集口径后可对真实目录试跑（仍只读） |
| mdec_promote_checker_v0.1 | 对假 M-DEC 卡 + `--vault mock_test_data` 实跑 | ✅ 9项检查全部按预期：①②④⑤⑥通过、③正确抓出断链 `[[不存在的证据页XYZ]]`、promoted_to 正确跳过；exit=1 | 无 | ⑥三件套是关键词级痕迹检查（易假阳性），对真实卡试跑后校准关键词 |
| evidence_pack_indexer_v0.1 | `--dir mock_test_data` 实跑 | ✅ 5文件按 source_type 分5节（signoff_package/promote_review/audit_note/aar/未分类），缺 source_type 正确落"未分类"并出提示；exit=0 | 状态污染值原样透传进索引（属如实反映，非bug） | 可对 16_/花厅坊样板证据目录试跑（只读） |
| nightly_resume_builder_v0.1 | `--since "48 hours ago" --repo <retail vault>` 只读实跑（真实repo·仅git log/status两条只读命令） | ✅ 48h窗口抓到215条commit、UNCOMMITTED四类分拣正常、NEXT留空位符合"判断相不自动生成"设计；exit=0 | 215条全量列出偏长——大窗口下骨架超"参考件"体量 | 加 `--max-commits` 截断参数（v0.2 候选）；known-dirty 清单实跑待六哥提供 |

## 边界用例

| 用例 | 期望 | 实测 |
|---|---|---|
| checker `--dir /nonexistent_xyz` | 明确报错 exit=2 | ✅ |
| resume builder `--repo /tmp`（非git仓库） | 明确报错 exit=2 | ✅ |
| `--out` 不带 `--write` | 不落盘、提示 dry-run | ✅（设计内建） |

## 结论

4/4 通过，无需修复即达 v0.1 验收线。四脚本均为只读+默认stdout，未修改任何 vault 文件；nightly_resume_builder 对真实 repo 只执行了 `git log`/`git status --porcelain` 两条只读命令，**未执行任何 git add/commit**。
