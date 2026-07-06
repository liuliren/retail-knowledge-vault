# 验收 Checker v0.1 — 机械门禁独立校验脚本

> P3-3 交付：把品类表验收框架中的**机械门禁**脚本化，实现「机械项不由生成器自证」
> （见《品类表生成验收标准与评分框架_v0.3》§五③ T1 修订）。

## 用法

```bash
python3 gate_checker.py <md文件路径>
```

- 单文件 CLI，只读被检文件，**绝不修改**。
- 输出：G2/G4/G5/G6 四门逐条 PASS/FAIL + 违规明细（含行号）。
- 退出码：`0` = 四门全过；`1` = 至少一门 FAIL（含文件不存在/非文件的情况）。

pytest 单测：

```bash
python3 -m pytest test_gate_checker.py -v
```

## 四门判据来源

| 门 | 判据 | 来源引用 |
|---|---|---|
| **G2 · 机械可核字段** | frontmatter 必填齐（`title/version/status/client_safety/fact_layer/summary`），`summary` ≤40字 | 《验收框架v0.3》§二 G5 第一条「frontmatter 必填齐」；`summary≤40字` 同时见全局 CLAUDE.md §5 KB 页规范 与 retail CLAUDE.md §10.2-6 分层检索标准 |
| **G4 · 客户安全红线** | 正文 0 条码(EAN-13)/ 0 进价裸值 / 0 已知供应商真名 | 《验收框架v0.3》§二 **G4** 逐字对应：「正文 0 条码（EAN-13）、0 进价裸值、0 供应商明细——只允许汇总口径」 |
| **G5 · summary 规范** | summary 存在、≤40字、单句、无换行 | 同 G2 来源；本脚本把「summary 规范」拆成独立门，供只关心 summary 质量的场景单独复核 |
| **G6 · 状态机合法** | `status` ∈ 合法枚举值；`status=stable/active` 时警告需查 `signoff` 字段 | 全局 CLAUDE.md 状态机（draft/candidate/active/stable/deprecated）+ retail CLAUDE.md §11.3 状态机进入条件（active 必须签字+落 SignoffLedger）+ `delivered/executed/active_plan/superseded` 扩展值（见 §11.3 交付件例外轨、G03_Lint_v2 `CANONICAL_STATUSES` 同构扩展） |

红线正则（EAN-13 / 进价裸值）与 `13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py` 的判据**刻意保持一致**，避免同一红线两套口径互相打架。

## ⚠️ 字母口径说明（重要）

本脚本的 **G2/G4/G5/G6 命名对齐 P3-3 任务下达时给定的口径**（机械可核字段 / 客户安全 /
summary 规范 / 状态机），与《验收框架v0.3》§二原文的 G-label 定义**不是逐字重合**：

| 字母 | 本脚本含义 | 原框架文档 §二 含义 |
|---|---|---|
| G2 | 机械可核字段（frontmatter 必填+summary长度） | T码作用域正确（8分法/12分法混用检测） |
| G4 | 客户安全红线 | 客户安全红线（**逐字一致**） |
| G5 | summary 规范 | Schema 与链接完整（frontmatter必填齐 + 0断链 + 生成器只能标draft） |
| G6 | 状态机合法 | 词表闭合与角色合法（`category_l3`值域/品类角色枚举） |

即：本脚本**实际覆盖**原文档 G4（逐字对应）+ G5 第一条子项（frontmatter必填齐）+ 全局
状态机规则；**不覆盖**原文档 G2（T码作用域）、G6（词表闭合）、G1（SSOT对齐）、G3（数据锚定）。
六哥/后续 Agent 引用本 checker 结果时，请按上表换算字母含义，不要直接等同于原框架文档的
G2/G6 判定。

## 已知局限（G1/G3 不脚本化的声明）

- **G1（SSOT 对齐）**、**G3（数据锚定）** 属《验收框架v0.3》定义的**判断门禁**，需要
  领域语义判断（是否与 V6.0/ARCH-001 逐一对上、数字是否可溯源至 posclean 标准 master
  表），**本脚本不覆盖，也不应该由零 token 脚本覆盖**——保留 LLM + 六哥复核（原文档
  §二开篇："判断门禁 G1/G3……需领域判断，保留 LLM + 六哥复核"）。
- **原框架文档的 G2（T码作用域）与 G6（词表闭合）** 本次也未脚本化：T码 8/12 分法混用
  检测、`category_l3` 词表集合差校验，需要读取表格列数据（非纯 frontmatter/正文文本
  扫描），留作 v0.2 扩展；本脚本当前只处理 frontmatter + 正文纯文本层面的机械项。
- **供应商真名词表（`SUPPLIER_NAME_PATTERNS`）当前为空**——需六哥按需补充真实供应商
  名单；出于客户机密铁律，建议名单本身存放在 `David-Liu-Vault/80_个人资料_敏感/` 只读
  区并在运行时注入，不直接写入本脚本明文提交版本库。
- **`signoff` 检查只警告不判 FAIL**：`status=stable/active` 但无 `signoff` 字段时，
  是否已签字属签字核验的判断门（谁签的字、是否真实签字事件），脚本只能查字段是否存在，
  不能验证签字真实性，因此归入警告而非硬性 FAIL。
- **summary「单句」判定为启发式**：去掉末尾句末标点后若内部仍出现「。！？!?」视为多句；
  对包含书名号/引号内标点等边界情况可能有误判，非语义级判断。
- 只做单文件校验，不扫描整库；整库层面的孤儿/断链/敏感值扫描仍由
  `13_数据分析与工具脚本/G03_Lint_v2/lint_v2.py` 承担，两者不重叠。

## 冒烟实跑记录（2026-07-07）

- `09_门店案例与项目复盘/ZQ_破晓计划/05_富城首跑作业包/01_富城店数据基线摘要_v0.1.md`：
  G4/G6 PASS；G2/G5 FAIL——`summary` 实际 44 字，超过 40 字上限（真实发现，非脚本 bug）。
- `02_零售企业生意诊断/4D诊断映射表_IF-01.md`（deprecated）：
  G4/G6 PASS（deprecated 属合法枚举值，不要求 signoff）；G2/G5 FAIL——缺 `fact_layer`
  字段 + summary 56 字超长。
