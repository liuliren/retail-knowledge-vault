---
id: P1-GOV-Signoff-Ledger-001
title: 签字门台账 · SignoffLedger v0.1
version: v0.1
status: active
owner: 六哥
created: 2026-06-27
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: governance_ledger
summary: 缺口3(状态机升active操作化)的轻量解。不批量回填261页,改为going-forward台账:任何签字门事件(升active/对外发布/改宪法/建·改skill/删移)发生即登一行,给护城河红线"谁签没签何时签"的可追溯性。种子=2026-06-27本会话签字门。
tags: [治理, 签字门, 可追溯, 护城河, 缺口3, signoff-ledger]
related:
  - "[[五层宪章主轴建设进展报告_2026-06-27]]"
  - "[[Claude双宪法边界声明_P1-CLAUDE-Constitution-Boundary-001_v0.1]]"
---

# 签字门台账 · SignoffLedger v0.1

> **缺口3 的轻量解(六哥 2026-06-27 认·走轻量版)**:报告原方案"261 页批量补 signoff"= 马具,**不做**。改为 **going-forward 台账**——每发生一次签字门事件,登一行。护城河的可追溯性靠"有没有登账",不靠回填存量。

## 🔒 登账规则(keys not prompts 的记录侧)
1. **何时登**:发生任一签字门事件即登——① 任何页/件**升 active**;② 任何**对外发布/交付**;③ 改**宪法**(全局/项目);④ 建或改 **skill**;⑤ **删除/重命名/移动**正式文件。
2. **谁登**:AI 在执行签字门动作后**立即补一行**;六哥口头/文字授权即为签字凭据。
3. **fail-safe**:**没有台账行 = 视为未签**——lint 抽查到"active 件但台账无对应签字行"→ 🟡 待六哥确认(见 §lint 抽查)。
4. 本台账**只增不改历史行**;更正另起一行注"更正前行"。

## 签字门台账(倒序·最新在上)
| 日期 | 类型 | 对象 | 签的什么 | 签字人/凭据 |
|---|---|---|---|---|
| 2026-06-27 | 建 skill | `.claude/skills/单品类诊断/SKILL.md` | E迭代加 M3 promote 3步回流 checklist | 六哥"p2路子要认" |
| 2026-06-27 | 改 active | `数量管理` / `SKU角色层与目的品保护机制` / `品类管理` | M3 回填 M-DEC验证案例 + 翻 signoff"进行中"→"已验证" | 六哥"三块回填签字;翻signoff" |
| 2026-06-27 | 对外发布门 | `Claude输出区/2026-06-27_M4首发成稿_方便食品长尾幻觉_v1.0` | 发布门自查通过·放行(待六哥真发) | 六哥"签字放行" |
| 2026-06-27 | 改宪法 | 全局 `/Users/CLAUDE.md` §7 + retail §6 + `/lint-privacy` 第⑥项 | 客户名授权链红线 P1-GOV-ClientNameAuth-001 | 六哥"签字·1.b.2重档" |
| 2026-06-27 | 升 active | `David-Liu-Vault/…/五层宪章主轴建设进展报告_2026-06-27` | 报告签发(active·亲授;剥除伪造signoff) | 六哥"可以发/审过了" |
| 2026-06-27 | 改 active | 同报告 §一/三/六/七 | 两 MOC candidate→active 事实校正回填 | 六哥"回填" |
| 2026-06-27 | 建项目宪法 | `/Users/davidliu/六哥自媒体/CLAUDE.md` | 公众号写作工作流 v0.1(六哥侧信道建·已记 /Users/log.md) | 六哥(侧信道) |

## lint 抽查(挂进 /lint-kb·缺口3 的强校验侧)
> 轻量、抽查、不批量:`/lint-kb` 增一项——扫 `status: active` 件,**抽查**其 frontmatter 有无 `signoff:` 字段、且本台账有无对应签字行;缺则列 🟡「待六哥确认是否已签」,**不自动回填、不批量动 261 页**。

## 关联
[[五层宪章主轴建设进展报告_2026-06-27]] · [[Claude双宪法边界声明_P1-CLAUDE-Constitution-Boundary-001_v0.1]] · [[客户名称对外使用授权链清单]]
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/README索引主定义盘点表_P1-GOV-README-Index-Audit-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/active签字机制审计表_P0-GOV-Signature-Audit-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/下一批active签字候选审计表_P0-GOV-Signature-Batch-002_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/孤儿文档分级审计表_P1-GOV-Orphan-Audit-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/断链分级审计表_P0-GOV-Link-Audit-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/断链分级审计表_P0-GOV-Link-Audit-002_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/样板客户全量数据接入审查_CODEX-Data-Merge-Full-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/零售知识系统迭代方案_v2.0.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/晟果新零售科学零售术语口径统一表_预览_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/命名规范4合1整合预览_P1-GOV-Naming-Consolidate_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/Agent-Native自迭代回路规范_设计简报_P1-GOV-SelfLoop-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | D档删除 | /Users/davidliu/KnowledgeBase/retail-knowledge-vault/00_入口与总索引/03_治理规范/CLAUDE_v2.2审批准备稿_P1-GOV-CLAUDE-Review-Prep-001_v0.1.md | 六哥(apply-signoff) | 清单: /private/tmp/claude-501/-Users-davidliu-KnowledgeBase/b371b699-a106-4633-ad14-1497410c2d1f/scratchpad/s4b-delete-clearlist.txt |
| 2026-07-02 20:48 | PostToolUse监听 | apply-signoff.sh | system | 已触发落账监听 |
| 2026-07-02 21:39 | PostToolUse监听 | apply-signoff.sh | system | 已触发落账监听 |
| 2026-07-02 补登 | D档删除·批量120项 | 99_归档/ 历史归档清理(M1战时封存/v1.1整合备份/v3.2历史版本/新基线封存/专项归档冗余等,完整清单见commit正文) | 六哥(2026-07-02会话裁决①A) | 快照留底:2026-06-20_专项归档.zip+_整理后.zip;台账原漏登,P0-KB-Upgrade-Fix-003补登 |
| 2026-07-02 | 升active·签字归档 | 00_入口与总索引/05_审计与档案/2026-07-02_知识库全面升级审计报告_P1-AUDIT-KB-Upgrade-002_v0.1_已签字.md | 六哥(会话签字) | draft→active;正式主本落审计档案区,输出区留来源;P0五commit已附录 |
| 2026-07-02 | D档·git历史重写 | 全仓库(filter-repo两轮): 移除dryrun明细24件+清洗输出csv/json11件+沙埔历史xls4件+空模板xlsx+ground_truth_700sku.csv(695条码) | 六哥(裁决B:先清洗再push) | 灾备bundle在_git_backups/;全部hash重写,映射见已签字审计报告附2 |
| 2026-07-02 | 建skill×4 | .claude/skills/{trio,abcz,movement,priceband}/SKILL.md + 13_数据分析与工具脚本/三件套引擎_v0.1/(共享执行层) | 六哥(会话指令授权) | 上线铁律三项已过:触发词✓/INDEX登记✓/gitignore白名单✓;引擎冒烟测试复现首算全部数字 |
| 2026-07-02 | 建skill×2 | .claude/skills/{posclean,mdcard}/SKILL.md + POS清洗库_v0.1 + 图卡引擎_v0.1 | 六哥(会话指令授权) | 上线铁律三项过;posclean probe冒烟✓(自动抓出65536截断);mdcard首验3张卡(店方规范/Z类排查/标品专项) |
| 2026-07-02 | 方案裁决·升active | 98_AI协作中枢/01_Claude_Code/Claude输出区/2026-07-02_输出模块整体升级方案_P1-PLAN-OutputModule-001_v0.2.md | 六哥(会话裁决①-⑤) | draft→active;①一库N出口架构+A/B/C分级认可 ②SSOT正本=六哥自媒体/CLAUDE.md ③数据六哥截图AI登记 ④A1本周+A2-A5每周1件 ⑤研报首期预锚定大湾区社区生鲜年度盘点 |
| 2026-07-02 | 勘误签字 | 05_审计与档案/…审计报告…已签字.md(§4假阴性表述勘误) | 六哥(决策收口单#1) | S1缺陷闭环 |
| 2026-07-02 | 升active | 16_客户与战役档案/花厅坊样板/标品三区SKU效率专项_立项卡_v1.0.md | 六哥(收口单#3) | KPI:SKU效率161→300+ |
| 2026-07-02 | 对外发布 | 花厅坊数据导出规范_店方版v1.1(五条两问·PNG) | 六哥(本人微信转发) | E层client_shareable·已脱敏口径 |
| 2026-07-02 | draft标准登记×2 | ABC阈值70/90 + Z类T1阈值≤30% | 六哥(收口单#6) | 随实战校准,升stable须三轮审议 |
| 2026-07-02 | 提案批准 | 汰换提案第一批211(4清仓+207停购打标待库存验证) | 六哥(收口单#4开审确认) | 执行等明天停购打标答案 |
| 2026-07-03 | skill升正式稿 | .claude/skills/mdcard/SKILL.md v1.0(status:active·signoff:六哥) | 六哥(会话确认"生成整体skill写进去") | 七轮迭代收口:五层受众/三级规则/卡组/数据三纪律/双轨渲染/4判例;设计层保持开放 |
