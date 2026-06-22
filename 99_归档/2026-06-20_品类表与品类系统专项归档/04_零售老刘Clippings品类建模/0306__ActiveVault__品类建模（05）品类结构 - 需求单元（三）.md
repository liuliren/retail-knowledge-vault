---
title: 品类建模（05）品类结构 - 需求单元（三）
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486027&idx=1&sn=82ef93206105cc66a23c599b50d1b425&chksm=9b06b875ac713163f6d98fa4724d476460b9a8745f11396ae6ce72e7f3a096757478e02ad0d8&cur_album_id=4239878941940301836&scene=189#wechat_redirect
author:
  - "[[2026-06-19_零售老刘Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节主要讨论分析实践中较为重要的两类单元：一个是场结构的货位BAY，一个是零售中的最细的维度“粒度”单元。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2024年10月19日 05:24*

**序言：** 前面一节中，我们谈到结构单元中的需求与需求点（需求区块）。由于品类单元的概念比较重要，本节继续讨论另外几个重要的“结构单元”，所例举案例并没有做详细介绍 ，后续会分别讨论。

#### 需求货位（需求BAY）

在卖场中，展示“ **需求** ”的方式则是陈列，其基本单元是货位（一个货位称为1个ＢＡＹ，一个BAY就是我们常说的一组货架、端架、一个堆头等）。

之前我们在经营与分析中，常常基于“一个小类为一个需求单元”，即一切业务作业或分析要回到“小类”。

由于之前介绍的“场”结构的结构设计，弥补了“人。货、场”的场结构这一块的缺失，后续我们更多会使用“货位”单元作为“需求点”单位。

也就是说，除了“小类”这个基本单元外，还有一个“需求单元”- 货位（BAY）。

我们以货位为单元，简单列举两类运用：

第一类，以“ **货位** ”单元的结构表，参与建模。

例1，如下图，是以“货位”为单元建模后的分析报表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5H4h7TcDLyW3iasCHqJygXI5OZwJIvUxMAfB4ibk80icAXaSiaiahdJugibicEA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

上图中，我们将区位、货位编码名称放置在行，进行的相关度量值下的分析。

**第二类，以“货位”单元的结构表，在实际业务中的运用。**

例1，一组陈列BAY的制作：

实践中，我们经常性需要对货位进行必要的调整，在上一节内容后，我们可以按如下步骤制作出一个陈列BAY。

第一步：以需定编。了解每组BAY（一个需求货位）陈列的类别（品类）包含的所有“需求”有哪些？具体方法这里从略。

第二步：如下图：从“ **需求** ”到“ **选品** ”，再到实际陈列落地。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HLFlQVzbNlxZBdY6TA9IYQFL4YiaMicaYltOkocdFWyDj3vSFap0xicBFg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

第三步， **修改维护（略）。**

**例2** ， **一切商品问题，总是表现为“结构”问题。** 我们先来看下图。图中的文字内容，当然有不同的表述，这不是重点。重点是结论：糟糕的“商品结构”可能影响 效率 和 利润。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HbYjibiaZceORN1SMiaAYKicYmatluF30RN2oJhFlYj1qyYeDFea4d0zBAw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

光是看这张图，你可能还不太明白我要表述的是什么，再看张分析图：按结构“层级占比”分析“区位”的销售度量占比情况：

还是前面第一个货位分析图表，我们在后面加上“ **层级占比** ”类度量。如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HEneBDl0achKvlNOvtVGV0JZA7qX7JRMCFiaI9biclxLUtglTia22PWXaQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

通过层级占比度量，我们很容易 **洞察** （这里因为与需求有关系，因而使用“洞察”而不是发现、知道等词汇）出某个货位在其“区位”里的各项销售度量的占比情况......。

#### 粒度单元

零售业的数据分析还处于较“低级”阶段。所谓“低级”，并不是说不“高、大、上”，不多么的无难度。而是 “维度”单元。简单说，不是一个维度粒度。

因为，通常的零售数据分析（有的话），其维度和度量都比较的单一或粒度较粗，不能深入分析的原因是：“粒度”不够（比如到课组、大类就分析不下去了）。

例如不能分析到“某一天，某一个单品”的客流，分析不到“今天的哪个单品”出了问题等等。

这种时常管理中经营要用到的以“一天、一张小票、一个单品（条码）”等，为单位的维度，就是一种最细的“粒度单元”。

前面讨论的“ **货位、小类** ”也是一种粒度单元，包括之前或你能想出来的“维度”结构，其实都是一种“粒度”。

我们说，某个课组、大类本月销售了多少，其类别粒度（课组、大类）的粒度单元，以及时期粒度（月）都较粗，我们可能需要“ **下钻** ”到更细的粒度（小类、货位）甚至到单品，直到不能再往下细分为止.....。

零售行业中，常用维度结构的最细粒度有：

时期类：一天 （有时为小时）；

商品类：一个单品（SKU条码或自编码）；

库位类：一组货位（一个BAY）。等等。

显然，我们是用粒度来表示一种“结构”单元，与之前任何的“需求结构”相同。也还是建模的两个方面： **维度 + 度量** 。

#### 度量与维度的复合结构

显然，度量也是有“结构”的。这些“度量结构”与某些维度组合，构成业务分析体系。

例3，如下图，零售度量的简单分类。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HAxLPjISzH1MNniaML0PPmD9DT8DRdoib5w9xayUaXQ8gFz56MrFXVIqQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

例4，常见单个度量指标汇总，如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HtSGrGgSC75j4R8B7NIPzE5pvTTGwNhX5iaQFRoBibbgXViba1EXRju6IA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

例5，客流类指标与月份维度组合分析表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HdmUZQbGPFnYJ6iaotP2V5hibhiccLMFQ19AIRLbmsNrLFCpu8MhQFicibCQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

例6，零售业经营，越来越需要精细化作业。这种精细化作业，很多时候都需要“较细”的粒度分析来支撑。

例如，生鲜品类与单品管理，往往需要按每天、半天。甚至按小时来进行日常管理，也就是说，需要更精细化一些。这就是生鲜的“时段化管理”。

这里的难点不是“流程、制度”，而是维度“粒度”。例如时期粒度要到每个小时，那么，其他的业务“粒度”也需要配合以“ **小时粒度** ”为管理单元。

如下图，我们以小时、单品为维度分析单元，分析出每小时、每个单品的销售情况。比如：

什么时段，某个单品销售完 **50%，** 销售完 ****100%** ，** 呢？

在某个当前时段（例如下午16:00-17:00点）。当前预计要售完的单品，已销售完多少（百分比）；

在预计的折扣时段。还有多少个单品未销售完，以及售完的单品占比。等等。

如下图，某生鲜时段销售分析模型设置表。为生鲜时段管理提供更细的“粒度”分析。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5HTjhXtLebicVKE0Bk1r9d5HVdkpLtnhP1dCpeKMnkUq6R6pPQtKt8YL6UULvK7meBNYfWjcjzURlg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

未完待续。

品类需求 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个