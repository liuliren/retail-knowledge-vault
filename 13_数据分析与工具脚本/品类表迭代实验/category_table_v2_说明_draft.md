---
title: 品类表迭代 v2 说明（映射知识字段版）
version: v2
status: draft
created: 2026-07-08
owner: 六哥（Claude 起草，未签字）
summary: v2=v1+6个POS映射字段(keywords/alias/exclude/priority/confidence_rule/manual_review)，把映射知识资产化进表。
tags: [品类表, Phase-Z, draft]
---

# category_table_v2.csv 说明 · draft

> **声明**：结构示例/实验件，**非 V6.0 替代品，V6.0 仍是唯一 SSOT**。

## 必答 8 问

1. **本轮目标**：把"商品名→品类"的映射知识从人脑/临时 prompt 搬进表（评估报告问题 #11–#14 的解），让映射可复现、可审计、可增殖。
2. **改了什么**：在 v1 的 9 列上新增 6 列——`keywords`（|分隔命中词）、`alias`（同义词，格式 `别名=正名`）、`exclude_keywords`（否决词）、`mapping_priority`（0–100，多候选裁决）、`mapping_confidence_rule`（如 `kw_hit>=1:mid;kw_hit>=2:high`）、`manual_review_required`（Y/N，天然易错品类强制人审）。映射字段只填在 L4 行（L3 行留 review 位）。
3. **解决什么**：① "虾片≠水产/牛奶糖≠牛奶/冰红茶≠茶叶/苹果醋饮≠醋"类误伤有了 exclude 数据级防护；② "牛奶饼干"式多候选可按 priority 程序裁决；③ D13 茶叶、F12 粥罐头、H50 餐具（单字词）等标记强制复核。
4. **新风险**：① 关键词表本身成为需要维护的资产——错词会系统性错映射（对策：质量报告回流迭代）；② 单字关键词（碗/盘/筷/茶）误伤率高，目前靠低 priority+review 兜，不彻底；③ alias 是门店方言层，跨店复用时需按店覆写。
5. **POS 映射适配**：**本版核心**。cleaner v0.2/v0.3 直接消费这 6 列；映射逻辑与数据解耦——改词不改代码。
6. **社区超市适配**：关键词按大湾区社区店常见品命名习惯写（菜心/猪展/丝苗米/豉油），alias 层预留粤语别名位（通菜=空心菜）。
7. **诊断适配**：仍无诊断字段，诊断参数化留给 v3。
8. **是否推荐进下轮**：**是**。映射字段设计验证可行（见 cleaner sample 实跑），v3 在其上加诊断参数。

## 与 v1 差异

+6 列（15 列）；节点集合不变（91 节点）。
