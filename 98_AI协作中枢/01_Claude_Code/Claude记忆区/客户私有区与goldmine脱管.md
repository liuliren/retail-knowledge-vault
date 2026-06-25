---
name: goldmine
description: "_client_private/ 是 gitignored 客户私有区;goldmine 全链脚本/配置/明细已脱管入此,tracked 只留通用件"
metadata: 
  node_type: memory
  type: project
  originSessionId: 97f438a1-003b-4edb-9d77-afc931b30695
---

`_client_private/`(.gitignore 第113行)是**客户私有运行区**,gitignored,绝不入 git。

**goldmine 金矿候选数据线**(2026-06 花厅坊)已按**方案 B+**收口:
- 客户专用执行物——8 脚本(merge_full_90d / full_dryrun_90d / 6 个 goldmine_*.py)、真实配置 yaml、五桶明细(A保留/B控补货/C缩面/D清库/E复核)、review/detail md——**全在 `_client_private/花厅坊/goldmine/`(及 reviews/ details/),不在 git**(脱管提交 373aad2 / 4f2db98)。
- **tracked 区只留通用方法件**:`tools/abc_classifier.py`(ABC九宫格+金矿口径逻辑)、ir_calculator、safety_stock、test_retail_tools;以及治理说明(注册表 §3.1.1/§3.1.2/§3.1.3 金矿口径 active)。
- 私有脚本已参数化:通过 `--config`/`GOLDMINE_CONFIG` 读私有 yaml(`client_config.py` 也在私有区);第二客户复用=复制模板生成新私有 yaml,脚本零改。

**铁律**:① 不把 goldmine/merge/full_dryrun 脚本或客户配置重新加回 git;② 客户数据/条码/进价/供应商/逐SKU明细绝不入 git(全程红线 0);③ 不自动写回门店 ERP/POS;④ 生鲜剔除是**客户级数据质量排除(client_specific_excluded),非通用永久规则**(见 §3.1.3,[[花厅坊数据质量坑]])。

**待办(债务队列·暂缓)**:`SENSITIVE-PRIVATE-004｜Goldmine Harness 通用化重建`——触发=第二客户接入 或 产品化确认;届时从私有脚本重抽象无客户痕迹通用 tracked 版,不简单加回 git。

注:`Claude执行日志.md` 本会话起已被 gitignore,AI 执行日志现为本地、不版本化。相关 [[脱敏测试链路与授权模型]]。
