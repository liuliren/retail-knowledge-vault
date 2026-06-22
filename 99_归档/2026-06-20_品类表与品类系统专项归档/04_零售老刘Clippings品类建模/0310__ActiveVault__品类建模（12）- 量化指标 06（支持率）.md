---
title: 品类建模（12）- 量化指标 06（支持率）
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486154&idx=1&sn=30e7019804e0e0341b2611b3f5107b47&chksm=9b06b8f4ac7131e29b353cf80742f131412780802ec37603c0d8623bee4ba9b04cc940321c54&cur_album_id=4070868752030728194&scene=189#wechat_redirect
author:
  - "[[2026-06-19_零售老刘Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节接着上一节的“支持率”介绍，讨论实际的建模分析场景。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2024年11月5日 22:08*

序言：上一节是重复发（见谅）。本节接着上一节的“支持率”介绍，讨论实际的建模分析场景。本节重点是：需要了解其中的占比关系，以及设计的思维。

支持率 与串岗率

知道了“支持率”与“串岗率”之间的关系（逻辑），设计其计算就相对简单了。

前面一节里，我们实现了“购物率”计算的三大区域（回忆一下）。由于“支持率”和“串岗率”都基于“客流数”，因此，我们在上一节的三大数据区域上，在加上一个计算“支持率”和“串岗率”的数据区域。

如下图所示，我们在“数据模型”得出的数据区的右边新增结构列，以用来分别计算“支持率”和“串岗率”。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoSTXJjoiaRLYKpIW2ldGUMG5Bh5t0tu4opia97T4h7gmvZYmRanVkfianurA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

对新增的列，分别做一个简单解释，以便加深对两个度量的理解。

1、我们先来看左边“客流透视表”的总汇总行结果是：10855，这是实际的总客流数（即不含串岗率部分）。

注意：这个总数由“数据模型”内部计算逻辑（行筛选逻辑）获得，Excel处理起来很难（看得懂的就懂）。

2、再来看每个课的客流汇总行：

百货：1559；

联营：929；

前厅：1274；

生鲜：7708，

食品：3926，共计：15396。

15396-10855 = 4541 （这就是由于串岗，而多出来的客流部分）。

**含串岗的“支持率”**

3、第一个列：【课分流占比】，实际就是“串岗支持率”；已知各课分解（分配）的是：10855这个客流总数（分母），这才是计算的关键。

这时候，分子分解的是：15396这个总客流数，由于分子大于分母，因此，实际的值要大于100%，即：计算的是“串岗支持率”。

因此，得出【课分流占比】- 串岗支持率列的计算公式，如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoSTRfQr0DokCib42zYTw2RiaQuzic8N0z7Ud6w67LlEVzDJdXsGku9OSFxKQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

其中的Q5单元值1559，就是课（这里是百货课）分得的客流数，作为分子，除以总数10855（分母），结果是：14.4%（1559 ÷ 10855 = 14.4%）。

不妨优化一下：

- 公式加入IF函数，使不参与计算的行等于空值（空白）；
- 后面的分母部分，使用表格数据模型的CUBE类公式（相当于Excel的绝对值计算，本例中为 Q34 单元格的绝对引用）。但相对更强大，
- 因为每次维度改变或刷新数据后，分母的单元格位置会变化），将公式拖满整列，就完成S列【各课分流占比】（串岗支持率）的计算。

**不含串岗“支持率”**

**4、** 第二个列：【课实际分流占比】，就是不含串岗的“支持率”计算；不同的是，现在已知各课分解（分配）到的是：15396这个客流总数（分母），计算的分子还是各课的客流数。如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoSTQ4n0HqODpibdDSgQhWNicKIAibIusCKgyJRTp7ahkfnwmTrdkvnKRzL3g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

与前面计算不同的是，这里分母变成为：15396这个客流总数，而各课的分子部分，相加也是15396，因而累计的和为100%，这就是不含“串岗率”的支持率计算。

例如，还是以百货课为例，其中的Q5单元值1559，是百货课分得的客流数，作为分子，除以总数15396（分母，不再是除以10855），结果是：10.1%（1559 ÷ 15396 = 10.1%）。

注意：上述的公式与上一个公式一样，分母（总数绝对值计算）采用的也是CUBE类公式，相当于：百货+生鲜+食品+,,,（所有课）的客流数（结果是15396的CUBE计算表示方式）。

加上其他各课的支持率分别是：

百货：10.1% ；

联营：6.0%；

前厅：8.3%；

生鲜：50.1%；

食品：25.5%。

合计：10.1 + 6.0 + 8.3 + 50.1+ 25.5 = 100 （100%）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoSTkNiclNLRlLoh3r64QkXleTAqWfib0DWQO3PwVoujcPqeia7d1746CKqKQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

**单独的串岗率计算**

5、第三个列：【串岗率】，计算公式：串岗率 = 串岗支持率 – 实际支持率 ，将前面计算的两列相减即可。由上图知道：整体串岗率是：141.8% - 100% = 41.8%。

6、如果是其他维度的“购买率计算”呢？

我们以分析课、区位（来自模型里的库位结构表，前面已讨论）的支持率与串岗率为例。

这里将时期（天）置于页面筛选，课、区位为行，列继续是【时段】列，数据为【客流数】。公式设置同上，如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoST9JCAHcPSw2bpWEEKdCMXFSXwSDhgwNc07ubeyPJ6XFtibQPoK1qGw1w/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

上图为截图（部分）。

由于分析的是区位，相对于课，区位的实际客流相加的和要比所在的课的客流更大一些，因为，区位数远大于课（部门）数，相互之间串岗数更多。也就是说，粒度越小，结果越大。

因此，我们说，支持率 与 串岗率 需要同粒度（同层级）维度比较。显然，这里的各课百分比相加应该等于前面的结论：141.8%。

如上图；（为了展示出每个课的占比数据，图例中隐藏了部分区位的行数据）

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoSTjZCSiaic1yJm7ibO9MSmJAwNJjhKlOy4k8HJg0ay2CT6GjK0kVxrd3aaA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

上图中，除了各课的客流占比分析外，还有课下面的各个区位的“支持率”和“串岗率”的对应分析。

我们展开一个课的全部区位，来看看每个区位的数据。即“支持率（两个）”与“串岗率”的计算结果。如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HW5ZdCQBY0JUQcxCktaoSTzkvMtDKqwLfefBLreZDSPSYjFsZLFEmzR2QpqtHwDnC1LiaJELrzKaA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

当然，还可以将“ **支持率** ”度量与其他维度结合起来参与计算分析。“ **支持率** ”度量主要提供基于“ **顾客** ”的角度，来了解某个维度（例如门店、课位、区位）的综合性效率指标。是一个相当重要的“ **效率判断指标** ”。

具体一些场景分析，后续会聊到，这里从略。

本节“购买率”小系列内容到这里结束、

未完待续。

度量指标 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个