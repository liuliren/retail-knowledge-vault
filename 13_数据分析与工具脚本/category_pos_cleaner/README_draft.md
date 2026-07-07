---
title: category_pos_cleaner README
version: v0.1
status: draft
created: 2026-07-08
owner: 六哥（Claude 起草，未签字）
summary: 商品表→品类映射清洗器实验件：三版py+mock样本+单测+质量报告；只准跑mock，接真实数据须六哥授权。
tags: [POS清洗, 品类映射, Phase-Z, draft]
---

# category_pos_cleaner · draft（Phase-Z 实验件）

**解决"品类脏"**：POS 商品表（无品类/错品类/口径乱）× 品类表（v2+ 含映射知识字段）→ 商品到 L1–L4 的映射表 + 未匹配 + 人工复核 + 质量报告。上游是 `POS清洗库_v0.1`（解决"格式脏"），下游是 /trio、/diagnose。

## 红线

- 本目录只准跑 **mock 数据**（假条码 6900000000011+ / 整数假价）。
- 接真实客户数据前：六哥授权 + 主线程红线检查 + V6.0 真表派生（sample_category_table.csv 只是 91 节点结构示例，**非 V6.0 替代品**）。

## 文件

| 文件 | 说明 |
|---|---|
| category_pos_cleaner_v0.1.py | 最小版：字段识别+标准化+单遍关键词（有误伤，教学用） |
| category_pos_cleaner_v0.2.py | 裁决版：+alias/exclude/priority/复核标记 |
| category_pos_cleaner_v0.3.py | **推荐版**：+评分/置信/多轮双重循环/批处理/质量报告/argparse |
| test_category_pos_cleaner.py | 最小单测 8 例（字段识别/标准化/排除词/评分置信） |
| sample_category_table.csv | 品类表 v3 示例（= 品类表迭代实验/category_table_v3.csv） |
| sample_pos_goods.csv | 96 行 mock 商品，含全角/空格/规格混写/无品类/错品类/重复条码/排除词陷阱 |
| sample_output_*.csv / sample_quality_report.md | v0.3 实跑产物 |
| v01_*.csv / v02_*.csv | v0.1/v0.2 对比跑产物 |
| 需求定义_draft.md / 迭代评估报告_draft.md | 需求与三版评估 |

## 用法

```bash
# 单测
python3 -m unittest test_category_pos_cleaner -v

# v0.3 实跑（多轮双重循环：内层最多6轮，外层3次宽松循环，收敛自动退出）
python3 category_pos_cleaner_v0.3.py sample_pos_goods.csv \
  --category sample_category_table.csv --outdir . --max-passes 6 --outer-loops 3

# 数据难洗时再加循环（六哥 2026-07-08 要求）：--max-passes 10 --outer-loops 5
# 批处理：第一个参数给目录即可
```

## 输出使用纪律

- `confidence_level=high/mid` 可作程序结论；`low` 与复核清单**必须人审**——判断相不下放（90/10）。
- 质量报告的"品类表反哺建议"章节回流品类表下一版迭代。
