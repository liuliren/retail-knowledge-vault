---
summary: goldmine客户完整明细配置模板,本地私有不进普通Git
title: goldmine 客户配置模板 SENSITIVE-PRIVATE-003
version: v0.1
status: draft
owner: 六哥
created: 2026-06-24
updated: 2026-06-24
module: 00_入口与总索引/03_治理规范
client_safety: internal_only
source_type: reference
---

# goldmine 客户配置模板 v0.1（SENSITIVE-PRIVATE-003）

> 本文件保留为**治理说明 + 模板示意**。
> **真实配置、配置加载器、配置 yaml 模板现统一存 gitignored 私有区 `_client_private/<客户>/goldmine/`，不入普通 Git。**
> 当前 tracked 区仅保留本说明文档，用于记录边界与后续通用化方向。

## 1. 用法
```bash
# 工具读配置:--config 优先,其次环境变量 GOLDMINE_CONFIG
python3 merge_full_90d.py --vault . --config _client_private/<客户>/goldmine/client_config_<客户>_goldmine.yaml
# 或
export GOLDMINE_CONFIG=_client_private/<客户>/goldmine/client_config_<客户>_goldmine.yaml
python3 full_dryrun_90d.py --vault .
```
未指定配置 → 脚本报 `BLOCKED: 未指定客户配置`(防止误用通用占位跑客户数据)。

## 2. 配置字段(模板·占位)
```yaml
client_name: <客户名>                  # 输出文件名前缀用;不入 tracked 脚本
input_dir: <客户原始数据目录>           # gitignored 路径,如 09_.../99_原始素材/01_门店数据材料
processed_subdir: processed            # 输出子目录(在 input_dir 下,gitignored)
backbone_glob: <主干销售汇总文件名通配>   # 如 供应商销售汇总_90天*.xls
archive_glob: <商品档案文件名通配>
slow_glob: <滞销/库存文件名通配>
fresh_archive_glob: <生鲜档案文件名通配>  # 客户级数据质量排除来源(§3.1.3)
output_prefix: <客户名>_90天            # 各明细/结果表前缀
```

## 2b. 当前裁决（2026-06-24 收口版）
1. 提交 `373aad2`「客户专用明细与 goldmine 脚本移出 git 跟踪」**继续有效,本轮不反转**;
2. goldmine/merge/full_dryrun 脚本贴客户数据结构,**维持在 `_client_private/`(gitignored)**,不重新加入 Git;
3. `client_config.py` 与 `client_config_template_goldmine.yaml` 虽不含真实客户值,但仍属于**客户配置框架临时件**,含客户字段、私有路径约定与 goldmine 口径参数,**本轮一并移出普通 Git**,落 `_client_private/花厅坊/goldmine/`;
4. **tracked 区只保留**:本模板说明文档(治理用途),不保留客户配置代码/模板;
5. **第二客户复用**:复制私有模板生成新 yaml,仅在私有区运行;
6. 如需把 goldmine 做成**通用 tracked 工具**,须另开 SENSITIVE-PRIVATE-004(从私有脚本重抽象无客户痕迹版本),**不得简单把私有脚本或配置框架加回 Git**。

## 3. 边界
- 真实配置(含客户名/路径/ERP 文件名)**只存私有区,gitignored,绝不入 git**;
- 配置加载器与配置 yaml 模板**当前也不入普通 Git**;
- 本模板**不写真实路径/明细路径/敏感值**;
- 若未来要恢复 tracked,前提是完成 SENSITIVE-PRIVATE-004 去客户化抽象并重新审查。

## 版本记录
| v0.1 | 2026-06-24 | 建立 goldmine 客户配置模板与边界说明。 |
| v0.1a | 2026-06-24 | 收口裁决：`client_config.py` + `client_config_template_goldmine.yaml` 一并移出普通 Git，tracked 区仅保留治理说明文档。 |
