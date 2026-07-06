# G03_Lint v2 知识库体检仪表盘

- 扫描时间：2026-07-05 21:17:53 EDT
- Vault：`/Users/davidliu/KnowledgeBase/retail-knowledge-vault`
- 扫描文件总数：2526
- 排除目录：`.git, 99_归档, Clippings, 13_数据分析与工具脚本/知识库自动化_v1/runtime`

## 顶部指标卡

| 指标 | 数量 |
|:--|:--|
| 断链目标数 | 416 |
| 孤儿文件数 | 21 |
| active 无签字数 | 525 |
| 缺字段文件数 | 1450 |
| 红线命中文件项 | 14 |
| 版本不一致数 | 373 |
| candidate 越权签字数 | 0 |
| execute 前置登记表 | 存在·已声明阻断 |
| provenance warning | 2 |
| supersession warning | 12 |
| failed 记录 warning | 0 |
| 核心知识缺 summary | 26 |
| 非规范 status | 174 |

## 1. 断链查

| 断链目标 | 引用数 | 引用文件数 | 示例引用文件 |
|:--|:--|:--|:--|
| 2026-05-04_知识库重构方案_v0.2_完整作战方案 | 94 | 49 | .claude/_镜像图.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/01_战略层/三回归仪表.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/01_战略层/品牌资产手册_v0.1.md |
| project_陈氏家族客户结构 | 40 | 24 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-09_vault反幻觉连环错误事件复盘_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-09_花厅坊综合诊断与调改规划报告_v1.1_对内版.md |
| 2026-05-07_休食SKU去留表_v0.1 | 36 | 16 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-07_封存断链清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-07_休食专项作战手册_v0.1.md |
| 2026-05-07_新商品引进表_v0.1 | 29 | 13 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-07_封存断链清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-07_休食专项作战手册_v0.1.md |
| 2026-05-04_G4-A冲调首战军师简报_v0.3 | 29 | 19 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/历史设计稿/知识库总索引.md; .claude/worktrees/sg-sci-61-wave1-4-5/06_陈列规划与DisplayMap/README.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-06_二访_读图分析_v0.2.md |
| 2026-05-04_重构_Phase0_会话执行计划_v1.0 | 27 | 11 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/版本更新记录.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/00_战役指挥板.md |
| M-DEC-005_错品类货架重建SOP_v0 | 26 | 14 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-07_休食专项作战手册_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/2026-05-06_读图分析待确认分桶派发表_v0.1.md |
| 单品类诊断 | 24 | 14 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-STATE-001_品类动态状态机_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/数据与系统能力底座.md |
| 2026-05-31_老板_方案Y双件验收_v0.1 | 23 | 17 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-23_W21-Day7方案Y成果成熟推进计划_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-26_W21-Day10_G3-B_v0.6_finalize分支判定_v0.1.md |
| 花厅坊_商品管理全流程手工诊断工具包_晟果新零售_V4 | 23 | 15 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/2026-05-07_花厅坊休食商品品类表_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/2026-05-07_花厅坊新商品引进表_v1.0.md |
| 05_品类管理与商品规划 | 17 | 9 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/链接债与孤岛_分级分析_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/10_咨询交付模板/00_战役SOP/S04_商品诊断与品类规划.md |
| 08_经营分析与数据看板 | 17 | 7 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/10_咨询交付模板/00_战役SOP/S07_经营复盘与凭证沉淀.md; .claude/worktrees/sg-sci-61-wave1-4-5/10_咨询交付模板/04_老板看板与凭证模板/README.md |
| 2026-05-30_G4-A_G05阶段门评审_有缺版_v0.1 | 16 | 16 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-26_W21-Day10_G3-B_v0.6_finalize分支判定_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-28_方案Y_5月31日验收人待确认清单_v0.1.md |
| M-DEC-006_陈列层数确认与区域落位SOP_v0 | 16 | 8 | .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-07_休食专项作战手册_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/2026-05-10_糕点子组调改作战手册_v0.5.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-007_商品动销综合诊断与调整SOP_v0.1_候选.md |
| 2026-05-10_休食区其它品类调改作战手册_v0.2 | 14 | 8 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-09_休食类调改规划诊断报告_v1.0_对内版.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-09_休食类调改规划诊断报告_v1.0_对外版.md |
| POS数据清洗与商品标准化规范 | 14 | 6 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-07_休食专项作战手册_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-007_商品动销综合诊断与调整SOP_v0.1_候选.md |
| reference_花厅坊休食区8货架与5人组织架构 | 14 | 8 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-27_花厅坊项目已确认事实登记表_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/05_陈列整改/2026-05-19_花厅坊陈列资源命名适配表_v1.0.md |
| 2026-05-08_组织调整行动计划_v0 | 14 | 8 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/15_刻意练习与成长/客户验证日志/2026-05/2026-05-08_启明_组织架构与权责利共识_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/2026-05-08_核心人员盘点_v0.1.md |
| 2026-05-08_核心人员盘点_v0 | 14 | 8 | .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-07-03_链接债清偿登记清单_v1.0.md; .claude/worktrees/sg-sci-61-wave1-4-5/15_刻意练习与成长/客户验证日志/2026-05/2026-05-08_启明_组织架构与权责利共识_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/2026-05-08_组织架构与权责利体系_v0.1.md |
| B3c_DisplayMap_G2B_G3A_V1_1 | 14 | 6 | .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-18_晟果商品调改方法论落地系统_v0.1.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/05_陈列整改/2026-05-18_休食区剩余子组5月底调改闭环计划_v0.2.md; .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/05_陈列整改/2026-05-19_休食区G货架现场实测与拍照采集清单_v0.1.md |

## 2. 孤儿查

| 文件 | title |
|:--|:--|
| 01_科学零售方法论/KB-CONCEPT-GOALDECOMP-001_经营目标拆解_v0.1.md | 经营目标拆解（老板营收目标 → 可执行动作链） |
| 01_科学零售方法论/KB-CONCEPT-GPCONTRIB-001_毛利贡献_v0.1.md | 毛利贡献（品类/单品对全店毛利额的贡献占比） |
| 01_科学零售方法论/KB-CONCEPT-STOCKDEPTH-001_库存深度_v0.1.md | 库存深度（单SKU备货量与周转的平衡） |
| 09_门店案例与项目复盘/ZQ_破晓计划/肇庆好家源鼎湖店/好家源业务体系框架_v0.1.md | 肇庆好家源 业务体系框架 v0.1 |
| 09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-05_二访_30秒找到率测试者清单_v0.1.md | 2026-05-05 30秒找到率测试 — 测试者清单 v0.1(A4 打印版) |
| 09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-07-04_花厅坊到店全诊执行清单_补半张卡_v1.0.md | 花厅坊到店全诊执行清单（补半张卡→整张·今日用） |
| 09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-W27_花厅坊周进展摘要_v0.1.md | 花厅坊周进展摘要 2026-W27 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/2026-05-12_BUS-DATA-007D_伴件_启明微信话术与签字单据_v0.1.md | 2026-05-12_BUS-DATA-007D_伴件_启明微信话术与签字单据_v0.1 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/2026-06-12_5月全月动销原始包/00_导出说明.md | 5 月全月动销原始数据包 导出说明 v0.1 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/2026-06-19_T03饼干_积压清理动作封存包_v0.1.md | T03饼干 积压清理动作封存包 v0.1 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/2026-06-19_T03饼干_门店现场确认任务清单_v0.1_A4打印版.md | T03饼干 门店现场确认清单 A4打印版 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/商品基础表草表/沙埔大道_Normalizer即插验证_v0.1.md | 沙埔大道店 · Normalizer 两层设计即插验证 v0.1 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/商品基础表草表/花厅坊_商品基础表_覆盖与待校准_v0.1.md | 花厅坊 商品基础表草表 · 覆盖与待校准报告 v0.1 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/商品基础表草表/花厅坊_校准工作表_说明_v0.1.md | 花厅坊 校准工作表 · 使用说明 v0.1（脱敏） |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/花厅坊_3件立即动作_店长放行单_v0.1.md | 花厅坊 · 3件立即动作 · 店长放行单 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/花厅坊_下次到店采数清单_v0.1.md | 花厅坊 · 下次到店采数清单 |
| 09_门店案例与项目复盘/乐易购花厅坊店/03_商品诊断/花厅坊_生鲜损耗每日登记表_可打印_v0.1.md | 花厅坊 · 生鲜每日损耗登记表（可打印 A4） |
| 16_客户与战役档案/_模板/02_战役进展模板.md | 战役进展模板 |
| 16_客户与战役档案/_模板/04_风险登记表模板.md | 风险登记表模板 |
| 16_客户与战役档案/_模板/06_交付物清单模板.md | 交付物清单模板 |

## 3. 状态查

| 文件 | title | owner | 豁免类 |
|:--|:--|:--|:--|
| .claude/skills/merge/SKILL.md |  |  | 否 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/01_战略层/三回归仪表.md | 三回归仪表 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/01_战略层/科学零售知识地图.md | 科学零售知识地图 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/工作区待决项分流清单_v0.1.md | 工作区待决项分流清单 | 晟果新零售 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/晟果新零售科学零售Wiki治理阶段收口报告_v0.1.md | 晟果新零售科学零售 Wiki 治理阶段收口报告 | 晟果新零售 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/知识库测试用例.md | 知识库测试用例 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/签字门台账_SignoffLedger_v0.1.md | 签字门台账 · SignoffLedger v0.1 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/精读卡消化出口_v0.1.md | 精读卡消化出口 v0.1 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/2026-05-08_5个月主控仪表_v1.0.md | 晟果新零售 5 个月主控仪表 v1.0（5/8 - 10/8 / 4 主线协同 / Year 1 站稳锚定） | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/2026-05-09_商品库立项方案_v1.0.md | 2026-05-09 vault 商品库 v0.1 立项方案 v1.1（采纳 ChatGPT 8 项升级 / 5 阶段路径） | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/Vault健康仪表.md | Vault健康仪表 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/常用模板入口.md | 常用模板入口 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/当前重点项目看板.md | 当前重点项目看板 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/战役指挥板.md | 战役指挥板 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/花厅坊判断前必读索引.md | 花厅坊判断前必读索引 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-07_McKinsey审计报告_v1.0.md | 花厅坊知识库 McKinsey 工程化标准审计报告 v1.0 | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-07_vault升级方案_v2.0.md | 晟果 vault 升级方案 v2.0（6 大标准融合 + Karpathy 自然涌现 + 反哺迭代） | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-07_vault战略重构方案_v1.0.md | 晟果新零售 vault 战略重构方案 v1.0（McKinsey + Karpathy + 三力骨架） | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-07_封存断链清单_v1.0.md | 2026-05-07 新基线封存断链清单 v1.0（已封存文件 → 最新基线表格映射） | 六哥 | 是 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-09_vault全量审计与数据审计1月期机制_v1.0.md | 2026-05-09 vault 全量审计与数据审计 1 月期机制 v1.0（晟果新零售顶级咨询治理纲领） | 六哥 | 是 |

## 4. Schema 查

| 文件 | 缺失字段 |
|:--|:--|
| .agents/skills/project-compact-governance/SKILL.md | title, version, status, owner, source_type |
| .agents/skills/project-handoff/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/SKILL-INDEX.md | version, status, owner, source_type |
| .claude/skills/abcz/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/compact/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/critique/SKILL.md | title, source_type |
| .claude/skills/deep-read/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/diagnose/SKILL.md | title, status, owner, source_type |
| .claude/skills/diagnose/_复盘台账.md | title, version, status, owner, source_type |
| .claude/skills/draft/SKILL.md | title, status, owner, source_type |
| .claude/skills/handoff/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/ingest/SKILL.md | title, version, owner, source_type |
| .claude/skills/mdcard/SKILL.md | title, owner, source_type |
| .claude/skills/mdcard/spec模板与样例.md | title, version, status, owner, source_type |
| .claude/skills/merge/SKILL.md | title, owner, source_type |
| .claude/skills/movement/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/posclean/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/priceband/SKILL.md | title, version, status, owner, source_type |
| .claude/skills/promote/SKILL.md | title, status, owner, source_type |
| .claude/skills/publish/SKILL.md | title, status, owner, source_type |

## 5. 敏感查（红线）

| 文件 | 类型 | 命中数 | 掩码示例 |
|:--|:--|:--|:--|
| .claude/worktrees/sg-sci-61-wave1-4-5/13_数据分析与工具脚本/数据清洗匹配_v0.1/README.md | EAN13_69 | 1 | 690********90 |
| 13_数据分析与工具脚本/数据清洗匹配_v0.1/README.md | EAN13_69 | 1 | 690********90 |
| 14_外部案例与行业研究/消費投资与行业研究/精读卡/精读卡_消费笔记8_近10年美国消费10倍股.md | GENERAL_13_DIGIT | 1 | 004********98 |
| 98_AI协作中枢/01_Claude_Code/Claude输出区/2026-07-02_SG-SCI-RETAIL-6.1系统升级审计/2026-07-02_lint体检报告_v0.1.md | EAN13_69 | 1 | 690********90 |
| 99_原始素材/零售老刘/09-卖场经营指数.md | GENERAL_13_DIGIT | 1 | 498********03 |
| 99_原始素材/零售老刘/25 – 聊聊售罄率.md | GENERAL_13_DIGIT | 1 | 808********56 |
| 99_原始素材/零售老刘/32 – 安全库存建模（4）.md | GENERAL_13_DIGIT | 1 | 471********99 |
| 99_原始素材/零售老刘/品类建模（00）- 量化指标 00  （分割线）.md | GENERAL_13_DIGIT | 1 | 342********01 |
| 99_原始素材/零售老刘/品类建模（141）选品配置 09 采购的方式.md | PRICE_VALUE | 1 | masked |
| 99_原始素材/零售老刘/品类建模（152）- 商品 MD 19 效率与价值.md | GENERAL_13_DIGIT | 1 | 713********64 |
| 99_原始素材/零售老刘/品类建模（68）- 商品组合 39 零售的战略.md | GENERAL_13_DIGIT | 1 | 082********43 |
| 99_原始素材/零售老刘/品类建模（74）- 商品 MD 01 品类战术4P.md | GENERAL_13_DIGIT | 1 | 713********10 |
| 99_原始素材/零售老刘/品类建模（96）选品配置 05 门店供应链.md | GENERAL_13_DIGIT | 1 | 486********41 |
| 99_原始素材/零售老刘/零售超市数据分析架构系列 06.md | GENERAL_13_DIGIT | 1 | 104********73 |

## 6. 版本查

| 文件 | 文件名版本 | frontmatter version |
|:--|:--|:--|
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/M-DEC中层决策资产晋级机制_v0.1.md | v0.1 | v0.2 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/产出路由矩阵_GOV-ROUTE-001_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/标签命名空间规范_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/输入系统架构_v0.1.md | v0.1 | v0.2 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/04_作战指挥/2026-05-09_商品库立项方案_v1.0.md | v1.0 | v1.1 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-05-18_零售知识库接入校准记录_v0.1.md | v0.1 | v0.2 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/内容消化台账_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/历史设计稿/2026-05-12_vault_v3.0顶层结构设计稿_v0.1.md | v0.1 | v0.5 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/同名消歧清单_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/链接债与孤岛_分级分析_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/KB-BIZ-SMALLCHAIN-001_小连锁体系化战略分析_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/_主实施计划_商业闭环_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/_回签包_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/_回签包_v0.2.md | v0.2 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/_回签包_v0.3_作战队列.md | v0.3 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/_回签包_v0.4_ChecklistOS.md | v0.4 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/06_变现体系/笔记命名与链接消歧规范_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-ACTION-GUIDE-001_诊断行动指导体系_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-CDT-001_CDT应用与子格落位方法_v0.1.md | v0.1 |  |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-DX-MISMATCH-001_销售陈列错配诊断_v0.1.md | v0.1 |  |

## 7. candidate 越权签字查

无

> 规则：status=candidate 不得带 approved 签字（candidate 不得 approved）。命中=越权，需降签字或升 active 后再签。

## 8. execute 前置状态查

- 登记表：`00_入口与总索引/03_治理规范/Codex执行前置状态登记表_v0.1.md` → 存在
- 是否声明「不允许 execute」：是（闸门关闭）

## 9. provenance 弱检测（warning）

| 文件 | 原因 |
|:--|:--|
| 00_入口与总索引/03_治理规范/体系个人知识库与内容板块_方案_v0.1.md | 缺 source/来源/依据/原典/related 等来源信号 |
| 05_品类管理与商品规划/品类系统V6.0_精读卡_v0.1.md | 缺 source/来源/依据/原典/related 等来源信号 |

> 弱检测：优先目录(治理/方法论/04/05/16)的 candidate/active 缺来源信号。warning，不 fatal，不自动修。

## 10. supersession 弱检测（warning）

| 文件 | 原因 |
|:--|:--|
| .claude/skills/ingest/SKILL.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| .claude/worktrees/sg-sci-61-wave1-4-5/.claude/skills/ingest/SKILL.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/_wiki入口/科学零售wiki入口.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| .claude/worktrees/sg-sci-61-wave1-4-5/05_品类管理与商品规划/2026-05-09_品类表治理决议_v1.0.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/00_花厅坊调改进度看板.md | status=superseded 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 00_入口与总索引/05_审计与档案/2026-06-24_客户数据Git保密治理链_封板记录_v0.1.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 00_入口与总索引/_wiki入口/科学零售wiki入口.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 05_品类管理与商品规划/2026-05-09_品类表治理决议_v1.0.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 08_经营分析与数据看板/D7复盘卡_v0.1.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/00_花厅坊调改进度看板.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 60_archive/2026-07-05_孤儿归档批次/14_外部案例与行业研究/_Run2_质量报告.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |
| 60_archive/2026-07-05_孤儿归档批次/14_外部案例与行业研究/_Run3_质量报告.md | status=deprecated 但缺 superseded_by/replaced_by/被取代:: 目标 |

> 弱检测：status=superseded/deprecated 但无 superseded_by/replaced_by/被取代:: 目标。warning。

## 11. failed 记录保护弱检测（warning）

无

> failed/侥幸/果差但决策稳/blocked 是资产；须留原因/回填点/下一步。warning，**严禁据此删除 failed 记录**。

## 12. 核心知识 summary 查

| 文件 |
|:--|
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/ABC九宫格裁决口径扩展预览_CODEX-Execute-Decision-001_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/ABC九宫格裁决转正式补丁预览_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/M-DEC中层决策资产晋级机制_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/03_治理规范/高效批处理任务规范_v1.0.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/M-DEC/M-DEC分类法_5D12C_v1.0.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/05_品类管理与商品规划/KB-CAT-ARCH-001_全品类双投影架构_v1.2.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/09_门店案例与项目复盘/乐易购花厅坊店/00_项目总览/2026-05-18_晟果商品调改方法论落地系统_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/10_咨询交付模板/02_交付SOP/单小类诊断样板_L3到Item到SKU_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/10_咨询交付模板/30天商品提效包/社区超市30天商品提效包_主定义_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/14_外部案例与行业研究/零售老刘体系/2026-06-19_零售老刘全量深读执行标准_三层阅读法五张表_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/15_刻意练习与成长/科学零售刻意练习机制_v0.1.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-001_6组角色拆分判据_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-002_大包装区瘦身比例_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-003_调改商品供应链落实节奏_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-005_错品类货架重建SOP_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-006_陈列层数确认与区域落位SOP_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-007_商品动销综合诊断与调整SOP_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-007_商品动销综合诊断与调整SOP_v1.0.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-009_休食老品汰换时间维度防误判_v0.1_候选.md |
| .claude/worktrees/sg-sci-61-wave1-4-5/16_客户与战役档案/花厅坊样板/M-DEC-010_休食小类价格带结构预警_v1.0.md |

> 仅检查方法论、决策规则、产品定义与 `01_科学零售方法论`；按需回填，不批量改写全库。

## 13. status 枚举查

| 文件 | 当前 status |
|:--|:--|
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/2026-06-24_客户数据Git保密治理链_封板记录_v0.1.md | sealed |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/05_审计与档案/内容消化台账_v0.1.md | live |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/2026-06-30_KB页全量索引与方法论目录_v1.0.md | reference |
| .claude/worktrees/sg-sci-61-wave1-4-5/00_入口与总索引/晟果零售知识库_维基主页_v1.0.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/DisplayMap.md | pending |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-DX-MISMATCH-001_销售陈列错配诊断_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-ROLE-5WAY-001_五分法品类角色分配方法_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-TIMEEFF-001_时间效率主轴评价指标体系_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-CAT-ZONE-SOP-001_区域调改五步法_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-DX-FRAMEWORK-001_社区生鲜超市品类诊断框架_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-DX-MATH-001_零售数学诊断工具体系_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-DX-QUESTION-001_诊断题库完整版_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-DX-WIDTH-001_品类宽度诊断方法论_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-FRESH-001_生鲜护城河经营方法论_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-METHOD-CHAIN-001_晟果科学零售五层经营链_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-METHOD-PCV-001_实践验证回流机制_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-SELECTION-TOOLS-001_选品核心工具体系_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-SHOPPER-TASK-001_购物任务图谱_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/KB-ZONE-SNACK-ROLE-001_休食区区域级角色定位说明书（通用模板）_v0.1.md | stable |
| .claude/worktrees/sg-sci-61-wave1-4-5/01_科学零售方法论/M-DEC/M-DEC-004_夜班连续战节奏SOP.md | pending |

> 规范枚举：draft / candidate / active / deprecated / archived。非规范值只报告，不自动改写。

## 阻断项

- 阻断级：敏感查存在命中。需先复核并处理红线项。
- warning 级（不阻断）：provenance 2 / supersession 12 / failed 0。

## 运行说明

- 本报告由 `13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py` 生成。
- 脚本只扫描 Markdown，不读取 Excel/CSV，不修改被扫描文件。
- signoff/红线/越权审计豁免：`99_原始素材`（冻结源料）与执行日志（历史留痕）。
