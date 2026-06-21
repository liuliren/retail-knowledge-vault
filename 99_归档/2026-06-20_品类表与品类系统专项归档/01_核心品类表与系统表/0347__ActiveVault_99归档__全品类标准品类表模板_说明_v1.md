# 全品类标准品类表模板 v1

## 本次交付

已生成一份可直接填充的 Excel 模板，用于作为“全品类社区超市商品标准化归类引擎”的标准品类主数据底座。

## 文件内容

Excel 内含 6 个 sheet：

1. 使用说明
2. 标准品类主表模板
3. 字段说明
4. 填写示例
5. 枚举值与校验
6. JSON映射说明

## 主表模板字段

### 一、基础标识
- version
- category_id
- parent_category_id
- category_level
- is_leaf
- is_enabled

### 二、层级信息
- l1_code
- l1_name
- l2_code
- l2_name
- l3_code
- l3_name
- l4_code
- l4_name
- full_path（公式自动生成）

### 三、匹配提示
- match_domain
- include_keywords
- exclude_keywords
- alias_keywords
- example_products
- brand_whitelist
- brand_blacklist
- spec_keywords
- pack_keywords

### 四、治理信息
- priority
- review_required
- owner
- effective_date
- remarks

## 模板设计要点

- 已预置 300 行可录入区域
- 已加入下拉校验：
  - category_level
  - is_leaf
  - is_enabled
  - match_domain
  - review_required
- 已加入优先级数值限制
- 已附 3 条工程化示例
- 已说明与 JSON 资产的映射关系

## 建议使用顺序

1. 先阅读“使用说明”
2. 再看“填写示例”理解口径
3. 最后在“标准品类主表模板”正式填充
4. 填完后再拆分生成 category_master / alias_dict / brand_dict / category_rules 等资产

## 下一步建议

下一份最该继续生成的是：

**品牌清单模板**

因为它直接决定全品类匹配时的品牌加权能力，尤其对家清日化、纸品卫品、个护、饮料、粮油这几大类影响很大。
