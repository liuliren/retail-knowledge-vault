---
title: 品类建模（10）- 量化指标 04（会员率）
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486110&idx=1&sn=710bece76642e09890ac99d74fd1f5c3&chksm=9b06b8a0ac7131b66f048ce13149b8075b2e9e3b8344263c815c612f5771a1f0212a4e9ad55b&cur_album_id=4070868752030728194&scene=189#wechat_redirect
author:
  - "[[2026-06-19_零售老刘Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节插播，简单聊下：会员的购买率。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2024年10月31日 11:10*

### 序言：本节本来计划讨论的是“支持率”指标的。但是，实践中，基于很多零售超市都有“会员”服务。本节插播，简单聊下：会员的购买率。

### 会员数 与“购物客流”

品类需求的变化，主要变现在某些“品类度量”的量化指标上。例如：客流数、会员数等。业务实践和分析建模时，常常用到“购物小票（一个小票对应一个单号）”，对事实表中的这一列的“不重复计数”，就是通常的“购物客流”数。

这里，还有一个“客流”状态：会员数。即：会员购物，是指在收银时出示或使用了会员卡，并被系统记录。因为使用“会员卡”购物的顾客人数一般少于“实际的购物客流数”。

前面一节讨论的“购买率”指的是“购物客流”的计算，因此，“会员购买率”是“购买率”的一种。

实践中，有一个分析场景：我们希望知道本店商圈中，满足了多少“常住户”（家庭）的“购物需求”？我们不妨称之为“家庭式购物”。

显然，这是一个更抽象和难以实现量化的业务场景。因为无法得知：

Ÿ无法定义什么才是“家庭式需求”，“家庭式”购物；

Ÿ到底购买了哪些品类或单品，才算是“家庭式购物”；

我们假如能定义出“家庭式”购物，从建模的角度，要确定有哪些维度和度量来“建模”？例如：

可能的维度，首先考虑的是：“需求单元”（小类或货位BAY），以小类为维度结构为例，可能需要建立一个类似：“家庭购物小类组合明细表”这样的表。

该表记录了哪些小类的组合方式，代表“家庭式购物”（（可能还包括已购单品的配置方式），一旦“某个购物小票”中的单品所在小类的组合，符合该表设定的“家庭式购物（小类组合）”，这张小票就被认为是：“家庭式购物”小票（单据），接下来就能计算了...。

如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZtIzAsTfZ8htw7uzhF2hjNpQiaaSWBBbvrlDqClIIUewFfXtrZsXPd7g/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

同样，可设置“需求货位BAY单元”的类似的表。不幸的是，由于缺乏可参考的这类“标准指标”（由于不同的商圈特点、经营特点、商品结构表的不同等）。维护起来几乎不太可能...。

既然是不可能的事，为什么还要讨论？为了展示一下“品类思维”，这个思考的过程才最重要。

#### “家庭式购买率”计算

现在，我们只得寻求一个能表示出“家庭式购物”的量化指标。从大量的实践中，我们发现，使用会员数或会员销售占比，可以近似表示为：家庭购物率。

很多超市的会员卡（或会员式经营）情况是：会员与会员卡几乎是标配。但是，要让“家庭购物率”生效（或有用），至少具备且不限于以下几个条件：

- 有“会员式管理”，且会员卡发行并有效运行3-5年以上；
- 期间分析的维度中， **购买的会员数** 占 **实际购物客流** 的占比 **60-70%** 以上；
- 适合的商圈且使用类似“会员卡”方式结账；
- “会员卡”由收银系统记录，并在销售表中有“会员卡”明细记录列；
- 以及其他限定指标（例如，适合的超市形态）；

如下图，是一个已完成的实例图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZLibXI0s9GJ5CI5cbz54NMeCU3VRbXZV0AGWYIFrCyu02mQU8jjn6cBA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

注意：上图中的会员数（用以近似表示为： **家庭购物率** ，特别是县、乡级超市，该指标很有用。

一般来说，如果某个品类或单品的会员购买率超过 70% 以上（即购物时使用了会员卡），则视为该品类为：明显的家庭式购物，这类商品，多以“大众化商品”为主。

注意：这类品类商品，常容易造成“缺、断货”…。

#### “家庭式购买率”度量

接下来，介绍“ **家庭购买率** ”指标在“模型”里的度量设计。

如上所说，首先，事实表（如Sales表）中，必须有一列表示“会员”的编码列。例如【会员卡编码】列，如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZ7CrTeVnl8wGEOLiagXbIbcRjetYQLuPqwsJOJGf3akszCPWYiae8c6tw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

然后，对该列定义度量【会员数】，如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZ3yVnWiciaTbgs7iaibEmJwN6PnVzx8pBPeG5DwQLxlPgHyVxicB7d5o0uKQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

上图中的公式表示：对【 **会员卡** 】列的行，进行不重复值计数，即：会员数计算。

由于是“建模”，该度量可与“模型”中的其他维度和度量。构成涉及“会员”类计算的业务场景与有关分析。

如下图，输出一个“小类”的会员数与客流数的分析表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZ4UqaOmdmPnho9ZKEeOdZ7L51VVAbvEglUFWzx71m7aFJTjdib0H5iaMg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

“建模”目的当然是为了洞悉某些业务问题，如下图：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZJ69DEJs2m6CSJPQ97T9zajric5xYSTL5gAdj9nkrABIH0JWOUWfxnpw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

既然，“ **家庭式购物率** ”主要指“ **会员** ”的购买率，其实际是会员经营中的一种价值体系。如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5FBCXJFqaJHQHrF07UGaeQZiagzzznEyujwiamC7mvFIsCOpAaf66HibJIFz0eu8Fpg9jEZ05NhgAdcw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

本图来自网络公开资料。

我们的所有指标度量的讨论，基本不会涉及到太“深”。你可以参考上图，自行研究“会员的评估体系”中的相关部分。后续可能会在会员（顾客）分析系列的RFM模式中涉及到相关介绍...。

讨论到这里，本打算结束“购买率的这一部分。但是，还有一个较为重要的概念以及相关的分析，即顾客的：“支持率”与“串岗率”。下节内容单独讨论。

未完待续。

度量指标 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个