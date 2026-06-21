---
title: 品类建模（08）品类度量 – 购买率（2）
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486074&idx=1&sn=966ce14f9a38f9351e9390bb92e9fa51&chksm=9b06b844ac713152c272cbee4f95e85694b9be31ec77798e1c579e4531eefdff0f2659612d50&cur_album_id=4070868752030728194&scene=189#wechat_redirect
author:
  - "[[零售老刘]]"
published:
created: 2026-06-18
description: 本节主要讨论：简易购买率分析系统制作步骤
tags:
  - clippings
---
零售老刘 零售数据化企划 *2024年10月25日 08:54*

序言：上节内容讨论到“购买率”，本节内容以及后面3节内容讨论“购买率”度量在建模中（这里为Excel-版本至少Excel2016或以上）的实现。

简易购买率分析系统

前一节中说到的 客流统计分析，一般超市不会使用（原因你懂的）。本节内容，我们使用Excel“建模”的方式，制作一个简易的“ **成交率（购买率）** ”分析系统。

步骤如下：

第一步，如果有现成的、已完成的数据模型，可共享其中的事实表（例如Sales销售流水表），以及“时期表、商品结构表、机构表”等维度表；可以直接在这类现有的模型中“扩展”即可完成；省很多步骤且“背靠”现有模型，可以有更大的分析“延展性”。

第二步，首先，创建一个“客流时段记录明细表”。人工记录或使用“红外线客流记录器”等方法，统计每天的各时段进店客流数；目的是记录每个门店，每个时段（按小时）的进店人数。

如下表（门店时段人流统计表），可使用Excel表按需要的列（主要是时段、客流数两列数据）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GJfRS2wnjDViczfGgmffBDdAomFX6SiaWiawBiaiaxPvLVtXFfB3NAjV9r7HlKPicEpJALiar6wvgUHQtow/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

然后，将“时段人流表”加载到已有数据模型中（使用PQ加载），或单独加载为模型，参与建模计算，如下图：

第三步，依据 事实表里（这里为Sales表）的【时期】列，复制该列，并重命名为【 **时间** 】列，数据设置为“时间”（00：00）格式。这一步是关键，为模型增加“时段”维度。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GJfRS2wnjDViczfGgmffBDdicIY7Rk2z1wKmlpYyEKyiccdxouDk43wFnib5hicBlOujw2rb0ibYaPju1Q/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

并且在模型中再依据【时间】列，根据零售实际的经营时间将其按每小时分段（例如：7:00-8:00）；

为了方便分析，最好还创建一个时段参数表，因为实际运用时，会出现【时段】列内容不是按实际的时段的自然顺序先后出现。这时候，我们在参数表设置【数字序号】列就能解决次问题，之外，设计时段参数表，还能与其关系其他表。

本例中，我们以事实表（Sales表）的【时段】列和时段参数表的【时段】列作为主键建立关系。

这样，我们在Sales表里新建【时间段】列，即将【时间】列的数值按其所在时间，分配在某个时段，例如，所有7:00-8:00时间行，都属于07-08这个时段。

如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GJfRS2wnjDViczfGgmffBDdMXgGwDecrTM2GAuhTwJToZ9UkTx033Rwcas4ibpic4qibAVHSQKKbPJ7w/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

第四步，基于之前步骤的建模完成后，使用透视表输出需要的结果表。

例如，将“课名称、时期列放入行，时段列（可使用事实表里的时段列，因为已建立关系）。如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GJfRS2wnjDViczfGgmffBDdDFLKOhJliauT9uouHV9FTAryCgicffEfGWLX4m8MibLCKM9n9ylU6tDzw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

第五步，上一步主要是直接查询出某个门店（机构）的每个课在某一天的“时段”客流数（即：购物小票数）。

可能已有人发现，那进店人数呢？

我们在第二步里，已经建立了一个“时段客流记录表”并加载到了模型里。但是，由于该表仅有【时段】和【客流数】两列，无法与其他维度（如库位表）或其他维度结构表（如商品结构表）建立关系。

因此，我们采用了一种较为灵活的方式，即：在Excel里运用“单元格”数据来配合处理后续的分析。

本例采用的是：在第四步里完成的同一Excel表里，将“时段客流记录表”透视出如下结果：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GJfRS2wnjDViczfGgmffBDdXu5ZxjC18CUMafaRKLyHW1jKTIjlseGCtwyTcc3mFE2ibpric0pfJx6w/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

如下图，是完成后的一个分析实例图表：

（因为不涉及分析，因而将分析内容模糊化处理了）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GJfRS2wnjDViczfGgmffBDdv636gQs8hAlo91LX5jbdaFCwiaSX3k2l5v2flRCAjdnXZbUURhRWayA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

以上就是简易 “购买率”分析建模系统的描述。下一节讨论该模型的实际分析运用，并就与Excel的“灵活”结合处理，主要是完成三个内容：

1、“实际购物”区域，来自“模型”数据；

2、“进店人数”区域，来自“进店人流统计表”；

3、“分析结论”区域，就以上区域数据的分析洞察。

这种分析报表，在之前的系列文章中，有过类似的“三部分数据区域”分析模式的讨论（应该是关于“促销分析”的文章，也懒得爬楼梯寻找了）。

未完待续。

度量指标 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个