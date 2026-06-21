# 全品类社区超市商品标准化归类引擎
## 资料准备与落地总控方案 v1

## 1. 文档目的

本文件用于把“全品类社区超市商品标准化归类引擎”的资料准备、目录结构、规则建设、工具开发与 Skill 封装方式一次性梳理清楚，作为后续逐个生成模板、逐个补充资料、逐步工程化落地的总控文档。

本文件解决四件事：

1. 明确要准备哪些资料模板。
2. 明确这些资料在整体系统中的位置。
3. 明确工具与规则应如何升级。
4. 明确如何把整套流程封装为可复用的 Skill。

---

## 2. 项目定义

### 2.1 项目名称

**全品类社区超市商品标准化归类引擎**

### 2.2 项目目标

基于全品类标准品类表、规则库、品牌词典、别名字典、规格单位词典、历史确认样本等资料资产，构建一套面向社区超市商品的标准化归类系统，实现以下闭环：

- 商品名标准化
- 多层规则匹配
- 品牌与规格加权
- 冲突排除与待复核控制
- 人工确认结果回流
- 样本持续学习与规则持续优化

### 2.3 方法链条

**标准品类树 → 商品名标准化 → 多层规则匹配 → 品牌与规格加权 → 人工复核回流 → 样本持续学习**

---

## 3. 三层资产体系

## 3.1 第一层：标准层

作用：定义统一标准，保证所有结果最终都落到唯一标准口径。

包含内容：

- 品类主数据
- 编码规则
- 输出模板

核心文件：

- `category_master.template.json`
- `编码规则模板.md`（后续单独生成）
- `输出模板说明.md`（后续单独生成）

## 3.2 第二层：判断层

作用：定义系统如何判断商品属于哪个品类。

包含内容：

- 别名字典
- 品牌字典
- 规格单位词典
- 规则库
- 冲突排除逻辑
- 复核阈值控制

核心文件：

- `alias_dict.template.json`
- `brand_dict.template.json`
- `spec_pack_rules.template.json`
- `domain_rules.template.json`
- `category_rules.template.json`
- `conflict_rules.template.json`
- `review_rules.template.json`

## 3.3 第三层：学习层

作用：让系统从人工修正中持续变好。

包含内容：

- 人工确认样本
- 未识别词回收
- 错配修正记录
- 历史条码商品知识库

核心文件：

- `reviewed_samples.template.jsonl`
- `历史条码商品表.xlsx`（后续模板）
- `未识别词回收表.xlsx`（后续模板）
- `错配修正记录表.xlsx`（后续模板）

---

## 4. 8 份核心资料模板清单

下面 8 份资料，是这套系统从“可用”走向“稳定”的最核心基础。

| 序号 | 资料名称 | 作用 | 所属层级 | 当前状态 | 后续动作 |
|---|---|---|---|---|---|
| 1 | 全品类标准品类表 | 定义标准品类树和唯一归属口径 | 标准层 | 已有原始模板基础 | 需转为标准主数据模板 |
| 2 | 品牌清单 | 辅助判断大类/中类，提升短品名匹配准确率 | 判断层 | 需建设 | 先按大类拆分品牌清单 |
| 3 | 别名词典 | 统一俗称、简称、错别字、混写 | 判断层 | 需建设 | 先从历史商品名中抽取高频词 |
| 4 | 规格单位词典 | 抽取重量、容量、包装数、包装形式 | 判断层 | 需建设 | 建统一单位识别口径 |
| 5 | 历史条码商品表 | 沉淀已有商品基础事实库 | 学习层 | 需建设 | 优先导入现有经营系统商品表 |
| 6 | 人工确认的映射表 | 形成高质量监督样本 | 学习层 | 已有部分 seed 样本 | 需持续累积 |
| 7 | 冲突词表 | 排除口味词、活动词、误导词引发的误判 | 判断层 | 需建设 | 先做高频冲突词 |
| 8 | 每个末级品类的样例商品表 | 为每个叶子品类沉淀典型样本 | 学习层/判断层 | 需建设 | 先覆盖高频销售类目 |

---

## 5. 每份资料的模板口径

## 5.1 全品类标准品类表

建议字段：

- category_id
- l1
- l2
- l3
- l4
- leaf
- enabled
- priority
- include_keywords
- exclude_keywords
- example_products
- review_required

目标：

- 一行一个最末级品类
- 确保每个叶子品类可唯一落表
- 保留启用状态与优先级字段，便于后期维护

## 5.2 品牌清单

建议字段：

- brand_name
- brand_aliases
- domain
- possible_l1
- possible_l2
- possible_l3
- possible_l4
- priority
- status
- remark

目标：

- 品牌先锁大类，再缩小候选范围
- 尤其优先补齐家清、纸品、个护、粮油、饮料、休闲食品等类目品牌

## 5.3 别名词典

建议字段：

- alias
- normalized_text
- alias_type
- applicable_domain
- applicable_categories
- confidence
- source
- status
- remark

目标：

- 统一俗称、简称、错字、地区叫法、英文/拼音混写
- 让商品名先标准化，再参与规则匹配

## 5.4 规格单位词典

建议字段：

- unit_text
- normalized_unit
- unit_group
- regex_pattern
- conversion_factor
- examples
- status
- remark

目标：

- 统一 ml/L/g/kg/抽/卷/包/片/只/个/瓶/袋/盒/桶/罐 等单位口径
- 为规则引擎提供规格解析能力

## 5.5 历史条码商品表

建议字段：

- barcode
- product_name
- brand
- spec_text
- package_text
- supplier
- old_category_l1
- old_category_l2
- old_category_l3
- old_category_l4
- sales_amount
- sales_qty
- gross_profit
- confirmed_flag
- source_system
- import_date
- remark

目标：

- 沉淀历史商品事实库
- 为近似匹配、样本学习、错配分析提供底层数据

## 5.6 人工确认的映射表

建议字段：

- barcode
- product_name
- system_pred_category_id
- system_pred_path
- manual_final_category_id
- manual_final_path
- review_result
- review_reason
- reviewer
- review_date
- reusable_flag
- remark

目标：

- 形成高质量人工确认样本
- 为后续自动回灌样本库做准备

## 5.7 冲突词表

建议字段：

- conflict_text
- conflict_type
- example_context
- do_not_map_to
- preferred_domains
- preferred_categories
- severity
- status
- remark

目标：

- 排除“蜂蜜味”“牛奶味”“柠檬味”等口味词导致的误判
- 排除“赠品”“促销装”“家庭装”“补充装”等活动/包装词干扰

## 5.8 每个末级品类的样例商品表

建议字段：

- category_id
- l1
- l2
- l3
- l4
- sample_product_name
- sample_brand
- sample_spec
- sample_feature_keywords
- source
- confirmed_flag
- remark

目标：

- 每个末级品类至少沉淀一批代表商品
- 为规则建设和近似匹配提供参考样本

---

## 6. 整体目录结构建议

建议项目根目录如下：

```text
all_category_product_engine/
├─ docs/
│  ├─ 00_总控方案/
│  │  └─ 全品类归类引擎_资料准备与落地总控方案_v1.md
│  ├─ 01_标准层/
│  │  ├─ 标准品类表说明.md
│  │  ├─ 编码规则说明.md
│  │  └─ 输出模板说明.md
│  ├─ 02_判断层/
│  │  ├─ 规则设计说明.md
│  │  ├─ 品牌规则说明.md
│  │  ├─ 别名规则说明.md
│  │  └─ 冲突排除规则说明.md
│  ├─ 03_学习层/
│  │  ├─ 样本回流机制.md
│  │  ├─ 未识别词处理机制.md
│  │  └─ 错配修正机制.md
│  └─ 04_Skill封装/
│     ├─ Hermes_Skill说明.md
│     └─ ChatGPT_Project说明.md
├─ data/
│  ├─ assets/
│  │  ├─ category_master.template.json
│  │  ├─ alias_dict.template.json
│  │  ├─ brand_dict.template.json
│  │  ├─ spec_pack_rules.template.json
│  │  ├─ domain_rules.template.json
│  │  ├─ category_rules.template.json
│  │  ├─ conflict_rules.template.json
│  │  ├─ review_rules.template.json
│  │  ├─ reviewed_samples.template.jsonl
│  │  └─ category_examples.template.json
│  ├─ master/
│  │  ├─ 全品类标准品类表.xlsx
│  │  ├─ 品牌清单.xlsx
│  │  ├─ 别名词典.xlsx
│  │  ├─ 规格单位词典.xlsx
│  │  ├─ 历史条码商品表.xlsx
│  │  ├─ 人工确认映射表.xlsx
│  │  ├─ 冲突词表.xlsx
│  │  └─ 末级品类样例商品表.xlsx
│  ├─ seeds/
│  │  ├─ reviewed_samples_seed.jsonl
│  │  └─ category_examples_seed.xlsx
│  └─ output/
│     ├─ 条码品类映射/
│     ├─ 待复核清单/
│     ├─ 未识别词清单/
│     ├─ 品牌命中统计/
│     └─ 匹配摘要/
├─ rules/
│  ├─ domain/
│  ├─ category/
│  ├─ brand/
│  ├─ conflict/
│  └─ review/
├─ app/
│  ├─ engine.py
│  ├─ normalizer.py
│  ├─ rule_loader.py
│  ├─ reviewer.py
│  ├─ learner.py
│  ├─ exporter.py
│  └─ io_helpers.py
├─ tools/
│  ├─ assets_builder.py
│  ├─ category_mapper_v2.py
│  └─ streamlit_app.py
├─ skill/
│  ├─ hermes_skill_template.md
│  ├─ chatgpt_project_instructions.md
│  └─ tool_contract.md
└─ package/
   └─ 发布包
```

---

## 7. 工具与规则升级建议

## 7.1 规则要从“一层匹配”升级成“多层判断”

推荐的判断顺序：

1. 先做商品名清洗与标准化
2. 先判断大域（食品/饮料/酒水/家清/纸品/个护等）
3. 再进入中类判断
4. 最后进入末级品类判断
5. 做品牌和规格加权
6. 做冲突排除
7. 输出置信度与待复核状态

## 7.2 建议新增的规则类型

至少增加以下规则：

1. 大类网关规则
2. 中类细分规则
3. 品牌加权规则
4. 规格包装加权规则
5. 冲突排除规则
6. 复核阈值规则
7. 历史样本优先匹配规则
8. 未识别词回收规则

## 7.3 冲突排除要重点建设的几类词

建议优先建设以下冲突词：

- 口味词：蜂蜜味、牛奶味、柠檬味、橙味、草莓味
- 活动词：赠品、促销装、买赠、满减装
- 包装词：补充装、家庭装、旅行装、组合装、礼盒装
- 非品类识别词：新品、升级版、经典款、旗舰款
- 误导词：奶香、果味、蜂蜜味、清香型、去屑型

## 7.4 复核机制建议

建议固定三档：

- 高置信度：自动通过
- 中置信度：进入待复核清单
- 低置信度：直接标记未归类/强制复核

建议输出至少 5 个 sheet：

1. 条码品类映射
2. 待复核清单
3. 未识别词清单
4. 品牌命中统计
5. 匹配摘要

## 7.5 学习闭环建议

每次人工修正后，至少做三件事：

1. 回灌到 `reviewed_samples`
2. 提炼新增 alias / brand / conflict 词条
3. 补充或调整 category rules

---

## 8. 代码与工具打包说明

当前建议保留以下交付件作为基础资源包：

### 8.1 已有资源

- 全品类 JSON 资产模板包
- 全品类规则表 Excel 模板
- 全品类商品归类引擎 V2.0 资源包

### 8.2 建议后续统一打包为总包

总包建议包含：

- 本总控文档
- JSON 资产模板
- Excel 规则模板
- Python 工具源码
- Streamlit 小工具源码
- 示例样本
- README
- Skill 接入模板
- 发布说明

---

## 9. Skill 模式封装建议

## 9.1 Skill 的定位

Skill 不是单个脚本，而是一套固定流程。

建议定义为：

**输入两张表或多张资料表 → 执行标准化归类 → 输出固定结果包 → 回收人工修正 → 更新资产库**

## 9.2 Hermes 中的 Skill 封装建议

建议 Skill 包含以下模块：

1. 输入检查器
2. 资产加载器
3. 规则执行器
4. 结果导出器
5. 复核回流器
6. 资产更新器

Skill 输入：

- 商品条码清单
- 品类标准模板
- 可选品牌清单
- 可选别名词典
- 可选人工确认样本

Skill 输出：

- 主映射结果表
- 待复核清单
- 未识别词清单
- 品牌命中统计
- 匹配摘要
- 规则建议清单（可选）

## 9.3 ChatGPT Project / GPT 的封装建议

建议把以下内容固化进 Instructions：

- 输入文件校验规则
- 标准品类树优先原则
- 规则匹配优先级
- 低置信度强制进入待复核
- 输出 sheet 固定要求
- 人工确认样本回灌规则
- 只允许落到标准品类主数据中的合法叶子节点

---

## 10. 后续逐个生成模板的推荐顺序

为了保证效率，建议按以下顺序一份一份生成。

### 第一批：优先搭底座

1. 全品类标准品类表模板
2. 品牌清单模板
3. 别名词典模板
4. 规格单位词典模板

### 第二批：优先解决匹配质量

5. 冲突词表模板
6. 人工确认映射表模板
7. 历史条码商品表模板

### 第三批：优先做学习闭环

8. 每个末级品类的样例商品表模板
9. 未识别词回收表模板
10. 错配修正记录表模板

### 第四批：优先做工程化固化

11. 编码规则模板
12. 输出模板说明
13. Skill 输入输出契约模板
14. 规则维护 SOP
15. 人工复核 SOP

---

## 11. 当前验收口径

本阶段的验收不要求一次性把所有资料填满，而要求：

1. 所有资料模板已明确分类。
2. 每份资料的作用、字段与用途已定义。
3. 整体目录结构已明确。
4. 工具升级方向已明确。
5. Skill 封装方式已明确。
6. 后续逐个生成模板的顺序已明确。

达到以上 6 点，即可进入下一阶段：

**逐个模板、逐个资料、逐个字段做工程化充实。**

---

## 12. 下一步建议

下一步不建议再泛泛讨论，而是直接按顺序进入模板生产。

推荐从以下 3 个模板开始：

1. **全品类标准品类表模板**
2. **品牌清单模板**
3. **别名词典模板**

原因：

- 这 3 份模板决定了整个归类引擎的基础可用性。
- 先把这 3 份做扎实，后面的规则、冲突、学习层资料才有根。

