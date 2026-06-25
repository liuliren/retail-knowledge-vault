---
title: 品类建模（14）- 量化指标 08（购买次数）
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486189&idx=1&sn=85f6c58d530011580bbd8783dbebe63b&chksm=9b06b8d3ac7131c52f084cb608048be0cff39d57d315d7ee4b32a7efbc3c4d91072718e074cd&cur_album_id=4070868752030728194&scene=189#wechat_redirect
author:
  - "[[Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节继续聊会员购买次数的问题
tags:
  - clippings
---
零售老刘 零售数据化企划 *2024年11月14日 07:39*

**序言：** 本节继续聊会员购买次数的问题。需要特别说明：本系列中，很多度量指标之间都存在关系，即：关系指标。

因此，经常会出现一些“指标“度量的来回“串岗”，重点不是“对错”。而可能是由于每个人心中的“不同的业务”场景的侧重度不同 造成的影响。

因为，你觉得将某个指标放在什么位置，肯定与你心中的“场景”联系着，只要心中有了一个系统化的“指标”结构体系后，自然就清晰了。

关键还是要与“业务场景”（也是一个维度体系）建立关系。

#### 购买次数与复购

实际上，上述的“购买次数”，其客流部分我们仅指“老顾客”（表述为：“老顾客复购”），而不包括那些“新顾客”。

显然，如果要计算出准确的销售额，应该还包括“新顾客”（之前没有过购买行为），前面的购买次数，计算的是：在期间内（这里是一个月）不止 1次 购物，即购买次数大于1，所谓这期间的“ **新顾客** ”，就是购买次数为“1”的部分。

我们讨论“购买次数”（整数），也可以说是“复购率”（百分比），不过是两种表示方式而已。要统一的话，就是：购买次数 = 复购次数 + 1（已购次数N）。

“复购率”很重要。几乎决定零售企业的“生死”，接下来，是如何计算“ **购买次数** ”（量化它）。实践中，由于维度不同，有几种情形：

一张购物小票（或订单号、小票号）就是一个客流（客流度量）；

是否是会员购物，要看某个小票号同时是否还对应着一个会员卡号，如果对应有会员卡号，则判断其为“会员”，否则是“非会员”行。

如下表所示，标注的行就是会员。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWzibIibqXdaN6KkNZaTlwtibKJUqddZYPqYN9LpdxaSx3baK03onkfFZqg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

表现为：一张小票的序列号与同一顾客的所有订单列表中的升序排序值相同。因而，可以计算会员的“购物次数”。

这也是【会员购物次数】公式计算的关键逻辑（编号顺序号就是次数），如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWTWZfMRa8o7FUpB3nrrum5spsjlL6BN7cjBbib6L242sGwNvrOGayF1Q/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

如果不做特别说明，【客流数】度量一般是指针对“小票号”的不重复计数：

客流数 = DISTINCTCOUNT( 'Sales'\[小票号\] ) ) -- 不重复的小票数量。

显然，会员数就是上述【是否会员】列中所有包含“会员”记录的行的计数。

这里的购物次数为1 的为新会员，>=2 的为复购会员，即“老会员”，对它们计数或销售求和等。当然，还可以以第一次购物时期来作为计算条件（一般采用此法）。

如下图的DAX公式：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWJvarkcWxlmjFwF9UedoYxibT21gwKJ0ic0jBtUHicNP35OtznEicfuqkcw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

还有一种情形，当需要以时间（小时：分），而不是日期（天）为粒度计算时，需要事实表里有一列【时间】字段，否则创建该列，DAX公式如下：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZW3MV0HSm2WMj6Naw2vIASOI5JAETT1e7Gmj63zAcYH41ZzMt467zibww/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

当然，一般情况下，由于会员有一列【会员号】字段列，那么，最好的会员计数计算，直接对【会员号】列进行不重复计数就行 ，这与计算客流的公式相同：

客流数 = DISTINCTCOUNT( 'Sales'\[**会员号**\] ) ) -- 不重复的会员号数量（不是小票号）。

#### 购买次数的运用

购买次数指标，反映的是门店经营好坏（特别是基于顾客为主的角度）的综合性结果指标。例如，购买次数反映超市经营费的商品储备、补货能力。

如果已进店人流不能成交（转化低，导致“购买率低”），其中就包括：门店商品储备的品种、数量和补货能力的这些一方面原因。

有时候，我常和一些店长说：你没事时呆在店里，找人或安排人记录，统计一下进入门店的顾客，那些没有成交的（出去时没有购物），搞清楚：

具体有多少顾客没有购物？

他逛了几个商品区域，哪个呆的时间长？

哪个商品区域，期间进去逛的人多，到收银区结账的却不多？等等。

然后，结合观察，再到现场看看有多少商品缺断货了，搞清缺断货原因：

有多少是因为有货但门店请货计划不合理未储备造成的；

有多少是因为公司仓库缺货造成的；

有多少是因为员工对补货流程不熟悉一时不知去哪补货造成的；

有多少是因为公司内部扯皮或不配合或沟通差造的；等等。

最后总结一下，主观原因的，自己努力改进，是公司原因的，不断反映，推动公司改进。

零售经营中，没有完全独立的业务，建模中体现为：没有完全独立的维度和度量。所谓：理论指导实践，实践不断迭代理论。

#### 购买次数分段分析

当然，会员购买次数“ **建模** ”后，就可以参与计算分析运用。

例1 如下图，不同价格区间的会员购买次数表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWicee0V8vUOWTHkQkOWLUpqbcEqkiaoN9lSHVuNIO7ic2MiajcwgiaIzvWAQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

由上图可知， 0-5价格区间的会员购买人数最多，其次是15-20区间。其中，20-25区间可能存在问题（检查是否选品问题，还是其他问题）。

例2 如果将会员购买次数分段，以查看每个购买次数段的销售，，应创建一个“会员频次分段表”

注意：请参考“价格带”系列文章中的价格带分段方法。

如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWYeGaVSPB1egUib0AToE86lZf2gDsAF2tXgFUedSjVdfT4LE3icaMIGLA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

加载到数据模型，就可以参与计算。

当然还需要创建一个按会员购买频段计算的【会员次数】的分段计算度量，然后参与计算。如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWIRlMy7JAB3V1YYMk86ta81w9lb4LSCQKotj3QR5ibIRvwfZdN1QtxgA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

例3 会员消费频次分布图：如下图所示，是某超市当月每个购买次数段的销售分布的条形图，其中，横坐标是金额，纵坐标是“频次段”。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWpW7EkLD0L0O3YSs3iaV7uBALczibM6aa9nOwLq6r5E56oM0KZzZMTZow/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

例4 上图，也可以改成占比方式，如下图样表：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWUHBeWCeRwQZY6kEOPlXAtd9vskiajDFW6nyHe8KssMqF2T7QU9g8QTw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

这类：N个维度 + 购买次数度量 的图表可以无限多（符合“模型”即“业务立方体”）。我们将其称为“业务立方体”。

实践中，我们先“模拟”出某个业务场景，只要有“模型”，然后就可以使用“模型”中的 维度 + 度量 的组合方式，基本上就可以将“业务场景”的分析表体现出来。

例5 如下图，先模拟一个购买次数的业务场景分析表，然后在“模型”中使用相关的维度和度量来将它表现出来。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWgm4wwa6odJgq0ZGIQz1MtrKLia2ib1pXBvgIzILgfxZpbpf6k5qmjFnw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=9)

例6 模拟后，不妨件模拟实现了。举个例子：

不用分析，大家都知道，前厅服务台区域的香烟类，其本身的购物频次一直都很高，因为，很多人一天至少买1盒香烟。但是它的会员购买次数很低，因为买烟的人一般都不是“家庭式”购物（很少使用会员卡的情况）。

但是，因为各种原因，一段时间以来，香烟的购物频次都在下降（与2017年的短时性鸡蛋的下降不同）。

因此，一个现实的业务场景问题是：在没有这部分香烟频次的时候（降低时），用什么可以增加这部分损失？换句话说，如何进行有效弥补（例如，增加一些辅助服务项目、特色品类等）。

#### 购买次数计算列

为了解会员在某个时期，共购买了几次（频次），以下是在事实表中，新建的【购买次数】计算列，与前面的度量不同的是，计算列可作为维度参与模型计算（例如筛选）。

如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5H919PtdCAWbQKicxmFplibZWhTOFmop1n8DUR7AsakOx7fHFiaiaHxbRPaZd57jZEZ8rBsr1jWr8yNGg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=10)

未完待续

度量指标 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个