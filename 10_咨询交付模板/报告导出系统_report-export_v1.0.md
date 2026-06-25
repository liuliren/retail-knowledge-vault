---
id: KB-DELIVERY-REPORT-EXPORT-001
title: 零售诊断报告导出系统 report-export v1.0
version: v1.0
status: candidate
owner: 六哥
source_type: method
created: 2026-06-25
module: 10_咨询交付模板
client_safety: internal_only
aliases:
  - report-export
  - 诊断卡导出系统
summary: SKU决策体系→门店执行→客户交付的最后一层封装。把复杂零售诊断自动转成店长/老板1页能懂、3分钟知道做什么的PDF+PNG诊断卡。渲染:HTML模板→无头Chrome→PDF+PNG。5段强结构+input schema+与SKU角色层/ABCZ/M-DEC对接。
tags:
  - 交付层
  - 诊断卡
  - report-export
  - 客户交付
  - candidate
---

# 零售诊断报告导出系统 report-export v1.0

> **定位**:SKU 决策体系 → 门店执行体系 → **客户交付体系的最后一层封装**。不是分析工具,是**交付工具**。
> **最高标准**:任何复杂 SKU 分析,都能在**1 页内被门店老板理解、3 分钟内知道"做什么"**。
> 实现:skill `report-export`(`.claude/skills/report-export/` = SKILL.md + template.html + render.sh)。

## 1. 核心输出
| 件 | 受众 | 用途 |
|---|---|---|
| **PDF**(A4 正式版) | 管理层/客户汇报 | 打印/正式交付 |
| **PNG**(一页卡片) | 店长/执行层 | **微信直发** |

## 2. 报告结构(强约束,所有卡统一)
| 段 | 内容 | 约束 |
|---|---|---|
| ① 一句话结论 | 顶部大字,**动作导向** | ≤20 字主句,含关键数字(例:"冲调区81%低效,优先砍咖啡长尾") |
| ② 红黄绿表 | L3子类 × 状态 × 核心问题 × 动作 | 🔴必砍/高风险 🟡调整 🟢保留/扩展 |
| ③ SKU结构拆解 | 长尾占比/低动销占比/高效集中度/库存风险区 | **只许"比例+结论",禁复杂解释**(放 KPI 条) |
| ④ 三步动作 | 保留Top / 压缩低效 / 清理替换 | 必须可执行,不抽象 |
| ⑤ 门店执行建议 | 明天做什么 / 谁做(店员/店长)/ 如何验证 | 落地层,最关键 |
| ⚠ 防误杀提示 | 低销≠该砍,引流/形象/特色款先保护 | 呼应 [[SKU角色层与目的品保护机制_v0.1]] |

## 3. 渲染路径(强制)
```
数据/草案 → HTML 模板(template.html) → 无头 Chrome → PDF + PNG
```
- 命令:`bash .claude/skills/report-export/render.sh <名>.html [输出目录] [png高度]`
- **禁止**:LaTeX 复杂链路 / 重型报表系统 / 非可控渲染引擎。

## 4. 输入结构(input schema)
```json
{
  "store": "花厅坊",
  "category": "G4-A冲调",
  "sku_analysis": { "n": 74, "head20_share": 0.48, "low_sale_ratio": 0.81, "overstock_ratio": 0.34, "avg_gm": 0.24 },
  "abcz_result": { "A": 0.20, "B": 0.35, "C": 0.25, "D": 0.10 },
  "role_layer": { "protected": ["引流","形象","GBA锁定"], "cull_pool": ["补充+D+无锚点"] },
  "mdec_flags": ["M-DEC-013长尾", "M-DEC-010价格带"]
}
```

## 5. 与现有体系对接(唯一输出层)
| 上游 | 喂给本系统 | 体现在卡的 |
|---|---|---|
| [[SKU角色层与目的品保护机制_v0.1]] | role_layer:谁不能砍 | ⚠ 防误杀提示 + ④保留 |
| [[单品管理]] §7.3 9维/ABCZ | abcz_result:排序优先级 | ②红黄绿 + ③结构拆解 |
| [[M-DEC-013_单小类长尾结构治理_v0.1_候选]] | mdec_flags:决策记忆写入 | ④压缩/清理依据 |
| **report-export** | —— | **最终客户交付(唯一输出)** |

## 6. 关键原则
不输出分析长文 · 必须门店可执行 · 弱化理论强化动作 · **所有内容可截图发微信**。

## 7. 跑通示例
**G4-A 冲调**(74 SKU 完整跑通):`report_output/G4-A冲调诊断卡_v0.1.{pdf,png}`。从拉数→9维ABCZ→角色防误杀→一页卡,链路验证通过。

## 8. 扩展(parking lot,未做)
自动周报系统(多门店 + M-DEC自动写入 + PDF批量)· 调改前后对比卡 · SKU趋势图 · 店长执行清单自动生成。

## 关联
[[SKU角色层与目的品保护机制_v0.1]] · [[单品管理]] · [[佐罗Zero宪章_ZERO-CHARTER-001_v0.2]]（§4 媒体/交付 App）· skill `report-export`
