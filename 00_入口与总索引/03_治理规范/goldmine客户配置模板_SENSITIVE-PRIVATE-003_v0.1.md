---
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

# goldmine 客户配置模板 v0.1（方案A·脱敏参数化）

> SENSITIVE-PRIVATE-003 方案 A:tracked goldmine 工具**不硬编码客户名/路径/文件名**,客户耦合外置于本配置。
> **真实配置存 gitignored 私有区 `_client_private/<客户>/goldmine/client_config_<客户>_goldmine.yaml`,不入 git。本文件仅模板(占位),不写真实客户路径/明细路径。**

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

## 2b. 为什么 goldmine 脚本不回 Git(方案 B+)
1. 提交 `373aad2`「客户专用明细与 goldmine 脚本移出 git 跟踪」**继续有效,本轮不反转**;
2. goldmine/merge/full_dryrun 脚本贴客户数据结构,**维持在 `_client_private/`(gitignored)**,不重新加入 Git;
3. **tracked 区只保留**:通用配置加载器 `client_config.py` + 本模板 + 说明;
4. 私有副本已**参数化**(读 client_config,去花厅坊硬编码路径/输出名),仅本地客户项目用;
5. **第二客户复用**:复制本模板生成新私有 yaml,私有脚本零改动跑;
6. 如需把 goldmine 做成**通用 tracked 工具**,须另开 SENSITIVE-PRIVATE-004(从私有脚本重抽象无客户痕迹版本),**不得简单把私有脚本加回 Git**。

## 3. 边界
- 真实配置(含客户名/路径/ERP 文件名)**只存私有区,gitignored,绝不入 git**;
- tracked 脚本只保留**通用占位 + CLI/env 读取**,无任何客户硬编码;
- 本模板**不写真实路径/明细路径/敏感值**;
- 配置驱动 ⇒ 第二客户只需新建一份私有 yaml,**脚本零改动**复用。

## 版本记录
| v0.1 | 2026-06-24 | SENSITIVE-PRIVATE-003 方案A:goldmine 客户配置模板(8字段占位)+用法。真实配置存_client_private gitignored不入git;tracked脚本通用参数化无客户硬编码;第二客户复用零改脚本 |
