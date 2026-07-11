# mdcard · spec 模板与样例（cp 改值即用·免读引擎 docstring）

> 目的：出卡时直接从这里 cp 一个样例改数值，不必读 `图卡引擎_v0.1/mdcard.py` 反推结构（省 token）。
> 引擎已内置 emoji→CJK 安全字符自动替换（⭐→★/✅→√/🟢→●/⚠️→！等），spec 里写 emoji 也不会缺字重渲。

## spec 全字段（standard 布局）

```json
{
  "layout": "standard",
  "chip": "内部·六哥",
  "kicker": "眉题·日期·场景",
  "title": "标题即结论(So-What前置)",
  "subtitle": "副标·一句展开",
  "tiles": [
    {"label": "指标名(权重/口径)", "value": "数值", "note": "小字上下文", "good": true},
    {"label": "指标名", "value": "待现场", "note": "小字", "warn": true}
  ],
  "table": {
    "header": ["列1", "列2"],
    "widths": [0.36, 0.64],
    "rows": [["行1格1", "行1格2"], ["行2格1", "行2格2"]],
    "warn_rows": [1]
  },
  "punch": "一句话钩子/目标(可含数字)",
  "note": "补充口径/纪律",
  "source": "数据源·期间·样本量·口径 | 密级标注"
}
```
- `good:true`=绿(正向亮点) / `warn:true`=红(要行动/风险) / 都不填=墨色
- `warn_rows`=表格中标红的行(0-indexed)
- tiles 建议 ≤6、table rows ≤8（>10 行清单不上卡，配 xlsx）

## 样例 A · L0 内部作战卡（六哥·决策/KPI/跟进）
```json
{"chip":"内部·六哥","kicker":"XX项目·YYYY-MM-DD","title":"结论先行一句话","tiles":[{"label":"关键指标","value":"数值","note":"So-What","warn":true}],"table":{"header":["动作","谁做/何时"],"widths":[0.4,0.6],"rows":[["动作1","负责人·期限"]]},"punch":"撬动点一句","source":"数据源·口径 | 内部件"}
```

## 样例 B · L1 老板诊断卡（内联括注·白话·数字翻成钱/动作）
```json
{"chip":"店方·老板","kicker":"XX店体检·YYYY-MM","title":"一句话老板听得懂的结论","tiles":[{"label":"动销率(在卖占比)","value":"60%","note":"每10样有4样在睡觉","warn":true}],"punch":"翻成钱:睡觉商品压着X万现金","source":"POS·30天 | 社区生鲜样板店"}
```

## 样例 C · L2 店长执行卡（任务话·做什么/谁做/多久/怎么算完）
```json
{"chip":"店方·店长","kicker":"XX调改·第N周","title":"这周要完成的一件事","table":{"header":["任务","验收"],"widths":[0.55,0.45],"rows":[["下架207个停购货号","系统0库存+货架清空"]]},"punch":"完成标准:X日前全部清完","source":"调改清单 | 执行件"}
```

## 样例 D · L4 营销卡（hero 竖幅·故事+数字钩子·脱敏）
```json
{"layout":"hero","chip":"公域","kicker":"社区生鲜样板店","hero":{"number":"14.2","unit":"%","line":"90天客单增长,靠的不是打折"},"punch":"一个动作,让老客多买一样","source":"样板店实测 | 真名须过授权链"}
```

## 出卡最简流程（优化后·省 token）
```
① cp 上面对应样例 → scratchpad/xxx.json 改值
② python3 13_数据分析与工具脚本/图卡引擎_v0.1/mdcard.py --spec <json> --out <落点.png>
③ 内部卡(L0/L2/L3):渲染✓即定稿,不读回图  ｜  门面卡(L1/L4·要发):才读回逐数校验
```
> 缺字不用管(引擎自动替换)；spec 过程件留 scratchpad 不落库；PNG 落 §存放规范对应目录。

## 卡组批量流程（v1.2新增·一份诊断一次出多受众）
```
① 把对应样例(A/B/C任选)按受众拼成一个字典 → scratchpad/specset.json:
   {"L0": {...样例A改值...}, "L1": {...样例B改值...}, "L2": {...样例C改值...}}
② python3 13_数据分析与工具脚本/图卡引擎_v0.1/mdcard.py --spec-set specset.json --basename <名称> --client <客户名>
   (--client 自动路由到 09_门店案例与项目复盘/{客户}/；查无该目录会报错退出，不自动建；也可用 --out-dir 直接指定落点)
③ 输出 <名称>_L0.png / <名称>_L1.png / <名称>_L2.png，且自动记一行到 图卡引擎_v0.1/output_ledger.csv
```
> 单张卡仍用 `--spec`/`--out`（原有流程不变），只有需要一次出多受众卡组时才用 `--spec-set`。
