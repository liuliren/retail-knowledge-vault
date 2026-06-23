---
title: CODEX-Full-DryRun-Execute-001 执行 Prompt
version: v0.1
status: draft
owner: 六哥
created: 2026-06-23
updated: 2026-06-23
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
related:
  - "[[花厅坊90天全量合并_字段映射与质量预审_v0.1]]"
  - "[[Codex执行前置状态登记表_v0.1]]"
  - "[[全量合并版execute前置方案_CODEX-Data-Merge-Full-001_v0.1]]"
---

# CODEX-Full-DryRun-Execute-001 执行 Prompt v0.1

> 下一轮可**直接复制**的 Prompt。**前提：六哥签字授权 full dry-run（execute 类）。** 未签字前不得跑。

---

## 复制以下内容作为下一轮任务

```
任务名称：CODEX-Full-DryRun-Execute-001｜90天脱敏合并表 full dry-run

授权前提：六哥已签字授权本轮 full dry-run（execute 类·只读脱敏表+出dry-run结果，不写回真实数据）。

目标：
1. 读取脱敏合并表 processed/花厅坊_90天全量合并_脱敏_v0.1_<日期>.xlsx（gitignored）；
2. 跑 ABC 九宫格（abc_classifier.py，§3.1 active 口径，9 格+需复核）；
3. 跑库存/IR/安全库存模块（ir_calculator / safety_stock，缺字段按 blocked）；
4. 生成 dry-run 结果（每工具覆盖率/blocked率/异常率/9格分布/需复核数）；
5. 结果输出到 gitignored processed/ 目录，文件名带日期戳。

最高标准：
1. 只读脱敏表，不读原始 xls，不写回真实数据；
2. dry-run 结果 xlsx/csv 不入 git；
3. 只提交脱敏审阅报告 md（无真实条码/进价/供应商裸名/逐SKU明细）；
4. 不生成正式 SKU 裁决、不生成正式商品诊断结论；
5. 不改 abc_classifier.py / 注册表 §3.1。

允许：
1. 读 processed/ 脱敏合并表；
2. 调 abc_classifier.apply_abc / ir_calculator / safety_stock；
3. 写 dry-run 结果到 processed/（gitignored）；
4. 出 dry-run 审阅报告 md（覆盖率/分布/blocked/异常，纯统计）；
5. 更新 Codex执行前置状态登记表 #8（dry-run 已审）；
6. 追加执行日志；可 commit（仅 md + 脚本，不含结果表）。

禁止：
1. 不写回真实数据 / 不改原始 xls；
2. 不提交 dry-run 结果 xlsx/csv；
3. 不把真实条码/进价/供应商裸名写入 md；
4. 不生成正式裁决/诊断结论（dry-run=覆盖率验证，非业务交付）；
5. 不改 §3.1 / abc_classifier；
6. 不 git add .。

已知降级（dry-run 中按 blocked 呈现，不阻断）：
- ITO 67% 覆盖（其余 blocked_缺ITO）；
- 负毛利异常分支 0 样本（供应商汇总层无负毛利，需人工核或接受空）；
- 促销无字段（blocked_无促销字段）；
- 品类仅单层（无三级路径）；
- 最近销售日期 24% 覆盖（库龄靠建档日期兜底 99.8%）。

输出：
1. dry-run 覆盖率/分布审阅报告（md，纯统计）；
2. 9 格裁决分布（各格 SKU 计数，不出逐 SKU 明细）；
3. 需复核(C+乙)计数；
4. blocked 字段汇总；
5. 是否可进入 CODEX-Execute-Approval-001（真实写回，需再签字）。
```

---

## 闸门提醒
- 本 Prompt 本身**不触发** dry-run；
- 跑 full dry-run **需六哥先签字**（[[Codex执行前置状态登记表_v0.1]] #8/#9）；
- full dry-run 之后的**真实写回**(execute)=另一道签字门(CODEX-Execute-Approval-001)。

## 版本记录
| v0.1 | 2026-06-23 | Batch-015：生成 full dry-run execute 下一轮 Prompt(读脱敏表/跑9格+库存IR/出dry-run/结果gitignored/只提交审阅md/不出正式裁决)。含已知降级清单。需六哥签字方可跑 |
