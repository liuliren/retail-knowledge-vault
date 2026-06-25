---
title: 品类建模（57）- 商品组合 28 属性的设置
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486602&idx=1&sn=35627521f8ba6c78703cf86eec05010c&chksm=9b06beb4ac7137a2c5704264f639907f8320760d34f06d12033d123504e063dad1879e4e68e4&cur_album_id=4032598383209709579&scene=189#wechat_redirect
author:
  - "[[Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节继续介绍“商品组合”的另外一些关键性基础“语义”，以及相关的属性维度的设置等。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2025年5月16日 04:08*

序言：本节继续介绍“商品组合”的另外一些关键性基础“语义”，以及相关的属性维度的设置等。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJa6XFB04hSD75dOlLXgm1iaxO3o4fIkiajIiaubxlA7lcokEF1icUhHtgCBw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

**商品组合的属性设置**

商品问题，始终是零售业最大的经营问题。基于日常业务管理 与 建模分析的需要，我们说，“商品群”的具体表现（前提）是：商品组合，而商品组合的前提基础则是：商品属性。

回忆一下之前讨论的商品属性的两大部分：商品本身的“固有属性”，以及在销售中表现出来的各类“销售属性”。例如：

图1 如下图所示，是商品组合需要的“固有属性”表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJaxSSpnX3KdKouRB1A2sUhZofYeWlAyG9reaKN7xLVgnAWGGg0HhwurA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

要想做好“商品组合”，需要建立、完善、维护好商品的上述两大属性维度结构。简单说，就是：商品信息表（Product）。

这里仅就讨论几个与商品组合相关的商品属性设置。

注意：最详细的商品属性是：商品信息表。这里列举的是部分属性维度。

第一项设置、商品组合的全维度结构设置。

基于长期性业务经营和建模的需要，最好是建立一套完整的“商品组合”的系统性维度结构。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJa0pzbk0aUFZsDCf9x1WlNvhAFMH0sEHia963x38BDjbnWEggic46WsibJQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

图2 如下图所示，是商品组合涉及的维度架构因素，每个维度因素各自可能又涉及不同的结构，建模上，体现为一个或多个表，将这些表设计组合起来，就是商品组合的全部维度结构宽表（对应业务宽表）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJa3diaRcPl1sDic9YG9dcughqJQz1QPUk3lInCvMTiciaickyUNj6zYxym6BQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

第2项设置、商品的生命周期。

在实际的“商品组合”业务中，例如，选品与日常商品组合的维护等，特别需要注意的一点是，商品组合也是具有“生命周期”的，它决定于“商品组合”中其中的每个单品在不同经营时期的销售表现。

每一个“商品组合”中，其各项生命周期的占比，需要符合企业的经营需要，从而保证整体商品的“生命力”价值，例如整个门店商品的“新鲜度（0鲜活度）”等。

基于业务需要，零售超市的后台系统，一般都会提供商品生命周期的信息管理模块。

图3 如下图所示。是某超市的商品生命周期的系统信息表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJacSdpd9rfhdIrIsxPWp5UyI0F10ARElZeHeLyXys8lU1pXMTYYZX0FQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

一般来说，新品和正常品是重点管理类型。商品的生命周期属性设置非常重要，它反映出零售门店经营的商品的健康状态，需要时常进行“健康体检”。

有一个最简单的分析方法：直接使用门店搜信息表进行透视，将商品状态（生命周期属性在数据表中的字段列），拖入列，行放入小类编码列（或其他维度），再将条码（或品名列）拖入透视表的数值区（用以统计商品SKU数）。

图4 如下图表所示，卡伊直观地了解到每个小类的各项生命周期属性的商品SKU数，进而了解各项商品属性的占比状态等。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJajHN54G59Q0UAASHwHlpzS8GeLWVicNzBaNOnVn9GAjibVbQvVia0XiafnQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

第3项设置、商品的基础代码设置。

很多零售超市的后台信息很乱，其中的一个原因就是，没有按照完整的、规范的系统维护流程进行，自己想当然的、约定俗成式的制定一些所谓的规范。

前面我们讨论过商品组合的划分依据有很多种，一般超市的后台系统都会提供基于是属性的一些维度设置。

图5 例如，在某超市的系统中的 基础代码 设置：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJaPjsPsLqe8SZpiapTtLsQcvKN6utcib6HpnlSNibibFR1FlIdIsEWlNzBdw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

上图中的季节、区域、单位、盘点差异原因等记录就是商品的一些基本属性设置。你可以任意添加自己需要的一些属性。

一般来说，商品的属性越详细，提供的业务或分析越详细，并越能为精细化管理提供必要的基础信息。当然，最详细的商品属性设置还是在“商品信息表”。

**商品组合管理存在的问题**

商品组合，是零售门店商品管理的基础，需要系统的、长期的、持续的合理的科学管理。实践中，可能存在以下一些问题。例如：

1、（从不更新）；大部分零售门店一直延续陈旧的商品组合的结构分类表；

2、（从不调整）；没有根据门店商圈市场、顾客需求变化进行有效的调整；

3、（从不改变）；商品组合分类、配置、选品盲目而没有依据推动逻辑；

4、（从不优化）；无法准确、动态地进行商品组合分类的调整、优化等；

5、（从不分析）；没有系统性数据分析，无法进行商品的精细化管理；

6、（从不整改）；无法保证商品组合后的合理陈列和分区域布局。

**商品组合管理的部分原则**

要改变以上这些问题，还是前面的那句话：需要长期主义的坚持。例如，坚持一些基本的原则，包括但不限于一些方式、方法、思维逻辑：

1、易于选择：商品组合，必须要站在顾者的立场；例如，便利顾客选择；

2、易于识别: 通过组合，容易识别出商品所属品牌、范畴、用途、功能等；

商品组合分类层次鲜明，不给人以杂乱无章的感觉；让顾客感觉到：能买到自己想买的东西；

3、易于找到: 不需要导购引导，能最快的看到并找到需要的商品；商品的布局、陈列和摆放醒目，有提示作用和诉求性等；

**商品组合的管理视觉**

商品组合的执行，涉及零售门店的各个部门（包含总部）。一般的零售分析认为，商品组合涉及的“品类”，包含以下5大维度（角度或视角）。

图6 商品组合（品类）的5大经营和分析维度结构。如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJa1pNzJCFS1C6uQRFcZ0K9sTx0SbbXNKiaExibV1CTkylfn8je7pYWbHWg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

基于网络资料图整理。

实际上，品类管理实践也建议，基于商品组合的品类管理，需要更新原有的一些组织架构，以便更好地开展品类管理。

图7 如下图所示。是品类管理建议的一种矩形式组织架构示例。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5GUTC7Evu4ecicZ32boIFnJa1xxgibkFm1PLRpGHt0uwqsy4NfJsbB9tBBJGaflMb4cHGgO74jicO0NQ/640?wx_fmt=png#imgIndex=8)

实际上，我们并不赞同成立这样的人员结构（除非已有成熟的模式）。还是那句话：品类管理的商品组合等，是一套业务系统、思维、工具、方法等，而不是具体的业务。

主要你的结构设置的每一级中的主要工作内容，包含有品类管理。

当然，基于业务需要，你可以在商品信息表中添加任何需要的属性维度（字段），以便它们参与计算。

未完待续。

商品组合 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个