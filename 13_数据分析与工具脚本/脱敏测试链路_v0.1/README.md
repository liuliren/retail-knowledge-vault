---
title: 脱敏测试链路 v0.1
version: v0.1
status: candidate
owner: 六哥
created: 2026-06-25
module: 13_数据分析与工具脚本
source_type: data_tool
client_safety: internal_only
tags: [脱敏, 测试链路, 疯狂测试, 工程化资产]
aliases:
  - "脱敏测试链路_v0.1"
---

# 脱敏测试链路 v0.1

> 把客户 D 层 raw 商品明细 .xls,**自动脱敏 → 分层失真分析 → 诊断**。
> 落地 [[多品类疯狂测试_总方案与数据计划_v0.1]] 的"脱敏+测试链"。

## 为什么存在（keys not prompts）

CLAUDE.md §7:对 Agent 说"别外传"是建议不是安全。客户机密的保护必须落在**权限层 + 脚本中介**:
**raw 裸值(货号=条码 / 进价 / 供应商)只流过脚本,不进 Agent 上下文。** 脚本吞进吐出,Agent 只见脱敏后的标准表。

## 链路

```
D层 raw .xls (只读 · .no-ingest)
  └─ sanitize.py : calamine 读 → 按 SKU 聚合(日级→SKU级) → 脱敏 → 脱敏SKU表 csv
  └─ analyze.py  : 品牌密度(HHI)/价格带分位/集中度(CR5)/复杂度判级/失真型预判
  └─ 诊断 md (+ report-export 诊断卡)
```

## 脱敏规则（输出保证:0条码 0进价 0供应商）

| 源字段 | 处理 |
|--------|------|
| 货号 / 自编码(条码) | → SKU 序号(S001…);**丢弃裸条码** |
| 进价 / 进销差价 | 现场算毛利率即弃 → **只留毛利率档**(<10%/10-20%/…) |
| 主供应商 / 供应商名称 | **整列丢弃** |
| 品名为条码(源误填) | 刷为"(未命名SKU)",防条码经品名漏出 |
| ERP 小计/合计行(货号="小计") | 跳过(否则重复计入 → 伪垄断) |

**脱敏自检**:输出表扫描任何 8+ 位纯数字(条码)→ 必须 0 残留。

## 用法

```bash
# 1. 脱敏单个品类
python3 sanitize.py <raw.xls> <out.csv> --category 巧克力
# 2. 分析整个脱敏目录
python3 analyze.py <脱敏目录>
```

## 依赖

```bash
python3 -m pip install --user python-calamine   # 治国产 ERP 怪 .xls(OLE2非标BOF)
# pandas/xlrd 对这批 .xls 报 "Expected BOF record",故用 calamine。
```

## 已跑案例

- **波次2 品牌密度型**(2026-06-25):巧克力/糖果果冻/酒水 → [[疯狂测试波次2_品牌密度型_测试示例诊断_v0.1]]
  - 脱敏产物:`09_/乐易购花厅坊店/03_商品诊断/01_清洗输出/_疯狂测试脱敏/`

## 已知限制

- 品牌为启发式(品名前2字),生产级需接商品档案品牌字段。
- 进价不准(全店已知)→ 毛利率档仅参考。
