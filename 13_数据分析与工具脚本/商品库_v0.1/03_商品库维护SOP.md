---
title: 商品库维护 SOP v1.1（日常维护 + 错误处理 7 项 / 与 G11 月度审计互补）
version: v1.1
status: active
owner: 六哥
created: 2026-05-09
updated: 2026-05-09
module: 13_数据分析与工具脚本/商品库_v0.1
quadrant: I
client_safety: internal_only
related:
  - "[[商品库_v0.1/README]]"
  - "[[01_字段字典]]"
  - "[[02_商品库使用规则]]"
  - "[[G11_商品库治理]]"
---

# vault 商品库维护 SOP v1.1

> **目的**：商品库**日常维护规则**（与 G11 月度审计互补）/ 含错误处理机制 7 项。

---

## §1. 日常维护流程

| 频率 | 动作 | 责任人 |
|---|---|---|
| 每次客户战役 | C 层接入 raw + mapped | 顾问 + Claude |
| 每周 | keyword_rule 新增 / 修改 review | 6 哥 |
| 每周 | brand_alias 新增 review | 6 哥 |
| 每月 | G11 月度审计（去重 / FK / 跨客户匿名化）| 6 哥 sign off |
| 每季度 | A 层 SKU 来源校核（OFF / 客户反哺）| Claude |
| 每年 | V4.0 升级时商品库重新分类 | 6 哥 + Claude |

---

## §2. 新 SKU 入库流程

### 2.1 进入 B 层（品类骨架）

```
触发：V4.0 新增 / 修改 L4 节点
流程：
  1. V4.0 升级 sign off（5/9 V4.0 治理决议）
  2. B_category_skeleton.csv 加新行
  3. 按 §1.字段字典 P0 字段全填
  4. P1 字段（representative_brands / business_role 等）按知识填
  5. update_log.md 记录变更
  6. 触发 V4.0 → 商品库一致性 lint（自动 / W22+ 实施）
```

### 2.2 进入 A 层（标准 SKU）

```
触发：客户反哺 + 启明 sign off / 或 OFF 种子导入
流程：
  1. 候选 SKU 通过算法匹配 + 启明 sign off
  2. A_core_sku_seed.csv 加新行
  3. P0 字段全填（sku_id / standard_product_name / brand_name / category_l4_code / source_type / status / created_date / updated_date）
  4. 商品级稳定属性（package_for_family / is_premium / is_gift_pack）按需填
  5. 重复检测（同 barcode / 同 standard_product_name）
  6. update_log.md 记录变更
```

### 2.3 进入 C 层（客户独有）

```
触发：客户战役接入新 SKU
流程：raw 层 → mapped 层（详见 02 使用规则 §2.1）
```

---

## §3. 客户 SKU 反哺流程

```
Step 1：mapped 层 feedback_to_library = true 的 SKU 候选
Step 2：6 哥 + 启明每月 review
Step 3：通过的 SKU 标准化后入 A 层
Step 4：新规则 / 新别名沉淀至 keyword_rule + brand_alias
Step 5：客户独有 SKU（不通用）保留在 C 层 / 不入 A 层
Step 6：update_log.md 记录反哺动作

边界：
  - 客户销售数据 / 毛利数据 / 库存数据**不入 A 层**（脱敏后仅做跨客户统计）
  - 客户内部码（client_internal_code）**不入 A 层**（仅本客户用）
```

---

## §4. 规则新增流程（keyword_rule）

```
Step 1：发现匹配错误 / 顾问经验
Step 2：在 keyword_rule.csv 加新行
Step 3：必填 13 列治理字段（详见 §1.字段字典 §7）
  - rule_id / pattern / rule_type / target_type / target_id
  - category_l4_code / priority / confidence / source_type / status
  - created_date
Step 4：source_client 标注（哪个客户战役沉淀）
Step 5：与现有规则冲突检测（priority + confidence）
Step 6：沉淀至 update_log.md

冲突处理：
  - 高 priority 优先
  - 同 priority 时 / 高 confidence 优先
  - 同 priority + confidence / 后建议 / 标 [需人工裁决]
```

---

## §5. 人工修正记录规则

```
触发：mapped 层 manual_review_status 变化
要求：
  - manual_reviewer 必填（启明 / 顾问 / 6 哥）
  - 修改 updated_date
  - update_log.md 记录修正内容（修改前 → 修改后 / 原因）
  - 不可删除原值（可标"已订正" / 保留 audit log）

跨会话纪律（与 §13.19 用户订正优先协同）：
  - 用户最早表述与后续订正冲突时 / 优先订正版
  - 旧版表述作 audit-log 留存
```

---

## §6. 错误处理机制 7 项 ⭐⭐ ChatGPT 控制点 4

### 6.1 重复 SKU 如何合并

```
场景：A 层同 barcode / 同 standard_product_name 但 sku_id 不同
处理：
  1. G11 月度审计自动检出（每月）
  2. 6 哥 sign off 合并方案：
     - 保留来源更可靠的 sku_id（source_confidence high）
     - 另一个标 status = archived / 加 remark 指向保留的
  3. C 层 mapped 表中 matched_sku_id 自动更新到保留的
  4. update_log.md 记录合并动作
  5. 不允许物理删除（保留 audit log）
```

### 6.2 错误品类如何回滚

```
场景：商品被错配到错品类（category_l4_code）
处理：
  1. 在 mapped 层修正 category_l4_code（不动 raw）
  2. manual_reviewer 必填 / 修正原因记 remark
  3. update_log.md 记录品类变化
  4. 如影响多个 mapped 行 / 批量修正前先 sign off

V4.0 升级时（如 V4.0 → V4.1 重命名 L4 节点）：
  1. 商品库自动 category_l4_code 升级（脚本驱动）
  2. 升级前 backup（snapshot at YYYY-MM-DD）
  3. 升级后 6 哥 sign off
  4. 异常情况 rollback 用 backup
```

### 6.3 人工修正如何记录

```
原则：人工修正不可丢
执行：
  1. mapped 层 manual_review_status / manual_reviewer / updated_date 必填
  2. update_log.md 文本记录（修改前 → 修改后 / 原因 / 修正人）
  3. 旧值保留 / 不物理删除
  4. 周度 review 累积到 keyword_rule（如果是规则级修正）
```

### 6.4 规则冲突如何处理

```
场景：keyword_rule 多条同 pattern 但 target_id 不同
处理：
  1. priority 高的优先（数字越大）
  2. 同 priority / confidence 高的优先
  3. 同 priority + confidence / 标 status = pending_review / 后建议
  4. 6 哥 / 顾问 sign off 后 / 标 status = active 或 archived
  5. 冲突日志 update_log.md 记录
```

### 6.5 客户独有商品是否进入标准库

```
判定标准（必须全过 / 启明 sign off）：
  ✅ 商品有标准条码（非客户内部码）
  ✅ 商品在多个客户战役中出现（≥ 2 客户）
  ✅ 商品在中国零售市场普遍可见（非地方独有）
  ✅ 6 哥 + 启明 sign off

如果不满足：
  - 保留 C 层 / 不入 A 层
  - 跨客户统计时仅作客户独有标记
```

### 6.6 哪些数据允许跨客户复用

```
✅ 允许跨客户复用：
  - 标准 SKU（A 层 / 脱敏后）
  - 品类骨架（B 层）
  - keyword_rule（规则）
  - brand_alias（品牌别名）
  - package_unit（包装单位）

❌ 不允许跨客户复用：
  - 销售数据 / 毛利数据 / 库存数据（仅脱敏后聚合统计）
  - 客户内部码（client_internal_code / store_id）
  - 门店级经营判断（is_traffic / business_action 等 / 仅本客户）
  - 客户特殊业务规则（如 hcp 启明的特殊安排）
```

### 6.7 哪些数据必须脱敏

```
脱敏要求：
  - client_internal_code → 不上 git / 仅本地
  - 销售金额 / 毛利 / 库存（如要跨客户统计）→ 转为相对值或区间
  - 客户名 / 门店名（如要跨客户统计）→ 用 client_id（hcp / lyg / zq）替代
  - 客户内部联系人 → 不入商品库（仅在客户战役档案 16_）
```

---

## §7. update_log.md 规范

```
每条变更记录格式：
| 日期 | 版本 | 变更类型 | 变更内容 | 操作人 | 原因 / 来源 |
|---|---|---|---|---|---|
| 2026-05-09 | v1.1 | 初版 | 基础架构 + 4 文件套 + 经营属性三层归属 | 6 哥+Claude | ChatGPT 8 项升级采纳 |
| 2026-06-15 | v1.1.1 | A 层加新 SKU | A-00001 海天金标生抽 500ml | 6 哥 sign off | 花厅坊战役反哺 |
| ... | ... | ... | ... | ... | ... |
```

变更类型：初版 / B 加 / A 加 / C 加 / 规则加 / 修正 / 合并 / 归档 / V4.0 升级

---

## §7. 客户数据安全同步与跨设备管理（5/9 W19 新增 / P1）⭐

### 7.1 git 边界（强制）

```
✅ git 只管理结构资产：
  - A_core_sku_seed.csv（标准 SKU seed）
  - B_category_skeleton.csv（品类骨架）
  - C_client_specific/_客户SKU模板.csv（接入模板）
  - _maintenance/*.csv（品牌别名 / 容量单位 / 关键词规则）
  - 所有 .md 文档（README / 字段字典 / 使用规则 / 维护 SOP / _future / update_log）

❌ git 不管理客户经营数据：
  - C_client_specific/<客户>_SKU_raw.csv（客户原始数据）
  - C_client_specific/<客户>_SKU_mapped.csv（客户匹配结果 / 含销售/毛利/库存敏感字段）
  - 任何客户内部码 / 客户内部联系人 / 客户私有业务规则
```

### 7.2 跨设备同步规则

| 数据类型 | 同步方式 | 备注 |
|---|---|---|
| 结构资产（git 跟踪）| git push / pull | 跨设备 / 顾问可复用 |
| 客户 raw/mapped 数据 | **加密备份 / 私有云盘 / 本地安全存储** | ❌ 不通过 git |
| 客户敏感字段（销售 / 毛利 / 库存）| 加密 + 客户 sign off 才共享 | 默认本地 |

### 7.3 未来 _anonymized/ 跨客户匿名化（Year 2+ 预留）

如未来需要跨客户匿名化共享 mapped 数据 / 必须**先**完成：

```
1. 脱敏字段白名单（明确哪些字段可入 _anonymized/）
   - 允许：标准 SKU / 品类骨架 / 匹配规则
   - 禁止：销售金额 / 毛利 / 库存 / 客户内部码 / 门店级判断
2. 客户脱敏规则（如客户名 → client_id / 销售额 → 区间）
3. 审计机制（G11 月度审计专项）
4. 6 哥 + 启明 sign off
5. 单独 .gitignore 白名单管理
```

→ **当前阶段（v1.1）不允许建立 _anonymized/ 目录** / 只是预留方案。

### 7.4 不允许通过 git 同步客户经营数据 ⛔

任何情况下：
- 不允许 `git add -f <客户>_raw.csv`
- 不允许 `git add -f <客户>_mapped.csv`
- 不允许把客户销售 / 毛利 / 库存数据写入结构层 CSV（如 A 层 / B 层）
- 误加入立即 `git reset HEAD <file>` + 沉淀 [[工程操作错误案例库]]

---

## §8. 与 G11 月度审计的关系

```
本 SOP（日常维护）：每次操作 / 每周 / 每月低频审计
G11 SOP（月度审计）：每月 1 日 / 系统化审计 / 6 哥 sign off
两者互补 / 形成日常 + 月度双层治理
```

---

## §9. 关联

- [[商品库_v0.1/README]]
- [[01_字段字典]]
- [[02_商品库使用规则]]
- [[G11_商品库治理]]（月度审计）
- [[CLAUDE.md]] §13.16-20 + §17.11+

## §10. 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| **v1.1** | **2026-05-09** | **初版**：日常维护 + 新 SKU 入库 3 类 + 客户反哺 + 规则新增 + 人工修正 + **错误处理 7 项**（重复合并 / 品类回滚 / 修正记录 / 规则冲突 / 独有入库 / 跨客户复用 / 脱敏）+ update_log 规范 + 与 G11 协同 |
