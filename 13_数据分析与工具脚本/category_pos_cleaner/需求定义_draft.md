---
title: category_pos_cleaner 需求定义（Phase-Z Z8）
version: v0.1
status: draft
created: 2026-07-08
owner: 六哥（Claude 起草，未签字）
summary: POS商品表→品类映射清洗器需求定义：7类输出、输入契约、与posclean链关系；全程mock数据实验件。
tags: [POS清洗, 品类映射, Phase-Z, draft]
---

# category_pos_cleaner 需求定义 · draft

## 1. 定位（与现有链不重叠）

```
POS原始导出 → [POS清洗库_v0.1 probe/sales/archive] → sales_master.csv / sku_registry.csv
                                                              ↓
                                    [本程序 category_pos_cleaner] × 品类表(v2/v3 csv)
                                                              ↓
                              商品→L1..L4 映射表 + 未匹配清单 + 人工复核清单 + 质量报告
                                                              ↓
                                        [/trio 三件套 · /diagnose 诊断] 按品类聚合
```

POS清洗库解决"格式脏"（假xls/截断/打印报表）；**本程序解决"品类脏"**（无品类/错品类/口径不一）。输入吃标准化后的商品表，不碰原始导出。

## 2. 输入契约

- **商品表**（csv）：字段自动识别，候选表头——名称(商品名称/品名/名称)、条码(条码/barcode/国条)、货号(货号/商品编码/编码)、规格(规格/规格型号)、原分类(原POS分类/分类/类别/品类)、售价(售价/单价/零售价)。缺名称列=致命错误。
- **品类表**（csv）：v2+ 字段（keywords/alias/exclude_keywords/mapping_priority/mapping_confidence_rule/manual_review_required），v3 诊断字段若存在则透传。

## 3. 七类输出定义

| # | 输出 | 内容 | 形态 |
|---|---|---|---|
| 1 | **映射表** mapping.csv | 每商品一行：原字段 + 标准化名称 + category_code/L1–L4 + score + confidence + 命中方式 | csv |
| 2 | **未匹配清单** unmatched.csv | 0 候选商品 + 未匹配原因（无关键词命中/被排除词否决/品类表空洞） | csv |
| 3 | **人工复核清单** review.csv | 多候选打平 / 低置信 / 品类 manual_review_required=Y / 与原POS分类冲突 | csv |
| 4 | **质量报告** quality_report.md | 映射率/复核率/未匹配率、置信度分布、逐轮收敛统计、未匹配 TopN 词根、误伤防护命中数 | md |
| 5 | **清洗日志** *.log | 字段识别结果、每轮 pass 统计、异常行、排除词否决记录 | log 文件+控制台 |
| 6 | **重复条码报告**（并入质量报告章节） | 同条码多行清单与保留策略 | md 章节 |
| 7 | **品类表反哺建议**（并入质量报告章节） | 高频未匹配词根 → 建议新增 keywords/节点 | md 章节 |

## 4. 核心处理要求

1. **字段自动识别**：表头模糊匹配，识别结果必须打印进日志（可审计）。
2. **名称标准化**：全角→半角、去首尾/多余空格、剥离混入名称的规格串（104g/500ml/10KG/×16 等）。
3. **多轮映射循环（六哥 2026-07-08 补充要求）**：映射不是单遍——按"严格→宽松"多轮迭代（关键词精确 → alias 扩展 → 原POS分类提示辅助 → 宽松子串），每轮只处理上轮未匹配，**循环直至收敛（本轮新增匹配=0）或达到 max-passes 上限**；默认上限 5 轮，可 `--max-passes` 加到 8–10 轮；每轮统计入质量报告。
4. **排除词一票否决**；**多候选按 priority→score 裁决**，打平进复核。
5. **置信分级**：high 直入 / mid 复核可选 / low 强制复核，规则读表（mapping_confidence_rule）。
6. **批处理**：可对目录内多份商品表逐一处理（v0.3）。
7. **红线**：不修改输入文件；mock 之外的真实数据接入须六哥授权 + 主线程红线检查；输出不含真实条码/进价/供应商（本实验全 mock）。

## 5. 验收口径（sample 级）

sample_pos_goods.csv（96 行 mock，含全角/空格/规格混写/无品类/错品类/重复条码/排除词陷阱）跑通 v0.3：映射率 ≥70%、已知陷阱品（牛奶糖/冰红茶/苹果醋饮/鱼皮花生/芒果干/皮蛋等）0 误入被排除品类、单测全过。
