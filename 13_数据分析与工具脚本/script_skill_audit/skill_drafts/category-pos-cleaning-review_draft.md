---
name: category-pos-cleaning-review
status: draft
version: v0.1-draft
created: 2026-07-08
owner: Claude 起草 / 六哥（签字后才生效）
审议轮次: 1
---

# /category-pos-cleaning-review（草案）

> **⚠️ draft · 未过 skill 上线铁律三件套（触发词字段/SKILL-INDEX行/gitignore白名单）· 不得当可用命令引用。** 触发词字段故意留空；拟用词"品类清洗/品类映射复核"以与 /posclean 的"清洗POS/清洗数据"错开。

## 使用场景
Phase-Z 品类映射线：拿一份商品表（mock 或未来签字后的脱敏表）+ 品类表 v2/v3，跑 category_pos_cleaner 得到映射/未匹配/复核三张表和质量报告，再走人工复核回路。**当前阶段仅限 mock 数据。**

## 输入
商品表 csv（表头模糊识别）+ 品类表 csv（v2+ 映射列，v3 诊断列透传）+ 输出前缀。

## 输出
`<前缀>_output_mapping.csv / _output_unmatched.csv / _output_review.csv / _quality_report.md`（逐轮收敛统计、重复条码、品类表反哺建议三章）+ 一页复核意见。

## 执行步骤
1. 〔脚本〕跑 `13_数据分析与工具脚本/category_pos_cleaner/category_pos_cleaner_v0.3.py`（多轮双循环映射·先严后宽·收敛即停）。
2. 〔LLM〕读 _quality_report.md：匹配率、逐轮增量、review 占比是否异常。
3. 〔LLM·判断相〕抽查 review 表 Top 分歧条目，出复核意见（映射规则问题 vs 品类表缺口 vs 商品名脏数据）。
4. 品类表反哺建议单列——**改品类表本身须六哥裁决**（V6.0 是签字 SSOT）。

## 禁止事项 / 红线
- **未经六哥签字，禁止对真实客户数据运行**（v0.1–v0.3 文件头已内置此声明）。
- 不修改品类表 csv、不修改 V6.0 主数据；反哺只出建议清单。
- 输出如含真实条码/进价（未来真实数据阶段），按 GOV-001 落 gitignore 白名单外目录，不提交。

## 回滚/暂停机制
脚本只新增输出文件不改输入，回滚=删除本次输出目录（删除动作报六哥 D 档？——输出属临时产物，建议按 A 档清理临时件口径，待六哥定）；匹配率异常（如 <50%）→ 暂停复核，先查输入表质量。

## 与现有脚本关系
核心=category_pos_cleaner v0.3（Phase-Z 产·mock 8/8 通过）；上游=品类表迭代实验 v3；与 /posclean（POS原始导出→标准表）不同段：本 skill 管"标准表→品类映射"。

## 何时需六哥裁决
①上线三件套+签字；②首次接真实数据（硬门）；③品类表反哺建议是否采纳；④临时输出清理口径。
