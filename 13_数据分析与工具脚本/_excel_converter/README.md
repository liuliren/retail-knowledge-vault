---
title: XLS 到 XLSX 批量转换工具 v0.1
version: v0.1
status: active
quadrant: III
project: cross_client
client: cross_client
store: cross_client
phase: tools
business_module: 数据底座工具
source_type: tool
created: 2026-05-10
updated: 2026-05-10
tags:
  - 工具
  - Excel
  - xls
  - xlsx
  - 数据接收
  - LibreOffice
  - 跨客户复用
---

# XLS 到 XLSX 批量转换工具 v0.1

## 1. 工具定位

- 本工具用于将客户 POS 系统导出的**老式 .xls 文件批量转换为 .xlsx**。
- 主要服务**数据接收**、**字段结构探测**和后续清洗准备。
- **默认输出到 `/tmp`** / 不进入 vault / 不进入 git。
- 本工具**不清洗数据 / 不生成分析结论 / 不输出 SKU 清单**。
- 跨客户复用（quadrant: III / project: cross_client）。

---

## 2. 使用场景

| # | 场景 | 例 |
|---|---|---|
| 1 | 客户提供大量 .xls | 花厅坊 5/10 拉数 16+ .xls |
| 2 | pandas / xlrd 无法稳定读取 | xls97 CDFV2 BOF 异常 |
| 3 | 需要先转成 .xlsx | openpyxl 只支持 xlsx |
| 4 | 需要快速查看每个表的 sheet / 行数 / 列数 / 字段结构 | header 探测 |

**常见触发文件类型**（POS 打印格式 / 含分页标题）：
- 商品档案表（货号 / 品名 / 进价 / 售价 / 供应商 / 类别 / ...）
- 销售明细表（日期 / 货号 / 销售数量 / 销售金额 / ...）
- 库存积压报表 / 销量排行 / 客单分析 / 价格带分析 / 等

---

## 3. 依赖

依赖 **LibreOffice soffice**（headless mode）。

**自动查找路径优先级**：
1. `/opt/homebrew/bin/soffice`（macOS Apple Silicon Homebrew）
2. `/usr/local/bin/soffice`（macOS Intel Homebrew）
3. `/Applications/LibreOffice.app/Contents/MacOS/soffice`（macOS 应用包）
4. `PATH` 中的 `soffice`

**安装**（如未装）：
```bash
brew install --cask libreoffice
# 或下载 https://www.libreoffice.org/
```

---

## 4. 使用方法

### 4.1 批量转换（主用法）

```bash
bash 13_数据分析与工具脚本/_excel_converter/convert_xls_to_xlsx.sh \
  "<输入xls文件夹路径>" \
  "/tmp/_xls_convert_$(date +%Y%m%d_%H%M%S)"
```

**参数说明**：

| 参数 | 必填 | 含义 | 默认 |
|---|---|---|---|
| `$1` | ✅ | 输入目录（含 .xls 的文件夹）| — |
| `$2` | ⚠️ | 输出目录 | `/tmp/_xls_convert_<timestamp>/` |

**示例**（花厅坊 5/10 拉数）：

```bash
bash 13_数据分析与工具脚本/_excel_converter/convert_xls_to_xlsx.sh \
  "/Users/davidliu/KnowledgeBase/retail-knowledge-vault/09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料/" \
  "/tmp/_xls_convert_20260510"
```

### 4.2 字段结构探测（可选）

```bash
python3 13_数据分析与工具脚本/_excel_converter/inspect_excel_headers.py \
  "/tmp/_xls_convert_20260510"
```

**输出**：
- 文件名 / sheet 名 / max_row / max_column
- 前 15 行非空摘要
- 可能的 header 行候选（最大非空列数行）
- **不输出真实大段明细数据**

---

## 5. 安全边界（强制）

```
✅ 转换后的 xlsx 默认输出 /tmp / 不进入 git
❌ 不要把真实经营数据 xlsx 放入 vault（除非显式授权 + .gitignore 白名单）
❌ 不要覆盖原始 xls
❌ 不要在本工具里做清洗
❌ 不要在本工具里生成商品结论
✅ 本工具只做格式转换 + 结构探测
```

**与 vault 治理协同**：
- vault `.gitignore` line 51 `**/*.xlsx` 全局忽略真实数据
- 仅 BUS-DATA-004 单个空模板 xlsx 通过单文件白名单入 git
- 本工具产出的 xlsx 全部默认 `/tmp` / 自动符合此政策

**与 BUS-DATA 系列协同**：
- 上游：BUS-DATA-006 真实数据导入与清洗任务单（5/12 拉数后）
- 上游：BUS-DATA-007 5/12 拉数接收与字段完整性验证日志
- 下游：BUS-DATA-008 真实数据清洗执行（v0.5+ / 用本工具转换后产物作为输入）

---

## 6. 已知限制

| # | 限制 | 影响 |
|---|---|---|
| 1 | 仅支持 LibreOffice 可读的 xls / xlsx 之间转换 | 不支持 PDF / WPS 加密 / 等 |
| 2 | POS 打印格式（含分页标题 + 打印时间 + 页码 + 重复 header）转换后**结构不变** | 仍需 BUS-DATA-008 清洗去标题 / 去小计 |
| 3 | 大文件（> 100 MB）转换可能慢（每文件 5-30 秒）| 视 LibreOffice 性能 |
| 4 | 字段名跨多行（POS 系统常见）的 header 自动识别能力有限 | inspect 脚本仅取最大非空列数行作候选 / 仍需人工核对 |

---

## 7. 跨客户复用纪律

- 本工具**不含任何客户私有数据**。
- 不在脚本中硬编码客户名 / 文件名 / 字段名。
- 任何客户 POS 文件特异处理 / 应在 **BUS-DATA-008** 客户级清洗任务中实现 / 不污染本工具。

---

## 8. 版本记录

| 版本 | 日期 | 说明 |
|---|---|---|
| v0.1 | 2026-05-10 | 初版 / 用于花厅坊 20260510 POS 导出文件转换 / 含 README + sh 转换脚本 + py header 探测 |
