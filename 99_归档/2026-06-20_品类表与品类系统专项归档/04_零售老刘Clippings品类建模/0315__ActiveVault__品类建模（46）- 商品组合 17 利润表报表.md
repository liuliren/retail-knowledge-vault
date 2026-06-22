---
title: 品类建模（46）- 商品组合 17 利润表报表
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486485&idx=1&sn=647cad6dc7545cd55637dd60e03f1ce8&chksm=9b06be2bac71373d63f4cf31fd71975c908112f05f517b9ada623816f7aa1306337b714acb10&cur_album_id=4032598383209709579&scene=189#wechat_redirect
author:
  - "[[2026-06-19_零售老刘Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节主要介绍一些利润表相关的维度以及对应的报表。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2025年3月30日 07:34*

序言：本节主要介绍一些利润表相关的维度以及对应的报表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcUdxv0FjibVGZJFIict58kVC6nlW9dRJ3jyclae7iaY2ocVneqWBMcfEYag/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

零售利润表的语义建模

1、利润表核心语义。包括前面讨论的核心指标，包括：营业收入、营业成本、毛利润、营业费用、净利润等。

这些指标，可能来自不同的“零售数据表”，并涉及不同的后台数据管理模块，例如：采购模块、配送库管模块、销售报表模块、财务模块等。

图表1 如下图表所示。某连锁零售企业的利润表计算明细表一例。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcUKzicTWOPfibMFL5jCq5W8wiaRslBpUFfuJPqXib9TynVDYBrTuMKhU1tjA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

上表中的关键指标说明。其中：

（1）毛利率：反映核心业务盈利能力，零售业通常需要 >30% 的毛利率（一般需要加上营业外收入等），以覆盖费用率（20%-25%）。

（2）净利率：净利润占营业收入比例，体现整体经营效率。净利润率一般在3%-8%左右。

（3）费用比：一般来说，零售实体门店的费用中，其中的租金和人工费用通常为最大支出项，需控制在合理范围（如总费用应 < 25%）。

2、利润表关键维度。

（1）时间维度：月度、季度、年度对比，分析季节性波动等。

（2）品类维度：不同类别、品类、节点货位收入、成本及利润率。

（3）区域维度：不同分店、部门、课组或区域的经营表现。

（4）渠道维度：自采、联营、自营、线上线下等销售占比对利润的影响。

（5）空间维度：表现为：不同位置的不同分配不同的毛利率权重。

零售利润表的相关报表

1、利润与利润分配表。一般零售企业可以根据自身经营业态特点，绘制利润及利润分配表。如下图所示的示例表。

图表2 如下图表所示。某连锁零售企业的利润及利润分配表（示例，示例数据可能未作结果核对）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcUdOAKRd21vGLkn3hxIjCd0JTbbdY778JkibtY5SAfHda8tmEnvcT6bOA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

2、财务费用明细表。 实际上，零售门店经营中各种费用很多，不同的企业涉及的费用也会不一样。建议创建经营中涉及的费用明细汇总表，按年、月统计。

图表3 如下图表所示。某连锁零售企业的费用明细表（示例表仅供参考）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcU2X1x2MMKHanibTpV23nvCW71GIaLZZhicqlHCQOLy0oQEBt1EyRgNm4A/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

3、自动利润分析报表。除了以上这些需要财务手工制作的报表外，日常经营中，不同的部分都应具备一定的“财务思维”，对成本、利润等指标需要有专门的分析系统。例如BI类建模分析表。

零售门店中，大部分的成本来自同供应商的“商品采购”，因而产生与供应商之间的商品“账款单据”。

图表4 如下图表所示。某连锁零售企业的部门费用明细表

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcUwRibaicoS54fyrBIRntQ0UHKFkkpKBp2LbSI8GdOVtEBhQc9mTH5Q8dA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

一般，与供应商的“货款单据”，按商品流转过程会产生“应付或待付、已付、未付、应付已付、应付未付”等状态。

图表5 如下图表所示。某连锁零售企业的供应商货款单据流转表（示例）

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcU8iaWhia1uF5yhWfk3jaibDFbWyshqYBncsAZtUGtgLcRtYloaujeK0PWw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

图表6 如下图表所示。某连锁零售企业的供应商货款单据汇总表（示例）

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcU8ajHvfFPB9LsEJOvQ8aV2w4Pzib9qFTD676lAWgvtVhPSxF2uLzibyOA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

图表7 如下图表所示。某零售的供应商货款单据已付单据费用表（示例）

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcUKibsicYRBe1icsKTPpKiavbURwcNBhkmORACqRHcpT9x2IsNzibehKibPYNg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

图表8 如下图表所示。某零售的供应商货款已付单据费用表（示例）

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Ggx40iaGsa8MGjYvcZ1VOcUFr2GO70noNxJhPO7KXmI2Er3IrCwJD7ZfuMCG544md2dLtAAp8ibvdA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=9)

一般零售门店老板，都会关注两个数据：销售额 和 费用，但是值得注意的是：这两个数据应保证的一致性方向、相同的维度。

例如，无论是采购、营运或财务，使用统一的业务宽表等，同时，也不能总是把控制费用当成第一目标。所谓“开源节流”，开源在前，节流在后。

未完待续。

商品组合 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个