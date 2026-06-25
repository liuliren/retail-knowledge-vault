---
title: 品类建模（56）- 商品组合 27 系统类报表
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486589&idx=1&sn=579f08283b65d98800a330dff3fc26b6&chksm=9b06be43ac713755ee673cebb0d4bc176e978e2de0337e34258ce35beb56cf4ac23deaa5239a&cur_album_id=4032598383209709579&scene=189#wechat_redirect
author:
  - "[[Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节内容主要讨论商品组合的日常经营中，涉及的系统维护、分析报表支持等。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2025年5月14日 02:39*

序言： 本节内容主要讨论商品组合的日常经营中，涉及的系统维护、分析报表支持等。本节作为过渡章节，内容仅基于结构语义需要的简单描述。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIK00WHepDDYjkDOq8KD1hEhPSV9krOR5xFQmXMkkksXVJUTWgOxzJqAw/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

商品组合的系统实现与报表支持

1、系统支持。

为了支持商品组合的业务性落地，实践中，需要提供建模系统（模型），以及一些业务报表的支持。以帮助零售门店在实际进行商品组合管理时，可以更快捷、更高效、更动态、更好地管理商品组合的整个业务过程。

例如，在新开门店或老店的大幅度调整中，提供商圈内需求品类及商品区域品类“占比分析”报表，以帮助门店设置各品类区域的卖场陈列布局，以及各品类的商品组合配置等。

在系统中可以维护常规品类，和主分类建立映射关系。有了上述讨论的商品组合的逻辑语义。这些就变得相对容易了。

第一、系统实现。

图1 如下图所示。一些零售门店的后台系统，可能会提供商品组合的功能模块设置，如下图所示。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIKJON5mJTJFetmxwZBqr3hmo6ic24Dw871jD1Gj9a4icuhjfIe2SXjxbng/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

不管是系统本身提供的商品组合设置，还是自创的此类分析模块，依据的都是：“商品组合”的相关语义，因此，了解其设置与维护过程对熟练运用“商品组合”很重要。

对于品类，上图系统中分为两类：常规品类 与 特殊品类。例如，特殊品类，对应所有那些经营中被视为特殊的商品。它由系统自动生成，主要包括：试销组合、促销组合、滞销组合、临期处理组合以及一些异常商品组合等特殊的商品业务场景。

因为是特殊的一类，实际并不用太关注于：是否分成多个组合。

那些在商品资料中的新品引入、老品淘汰、生命周期等将自动按照原来所属的类别，自动对应到常规品类和特殊品类结构里面。

如果是新品，则需要找到所属品类（一般为小类），然后在该品类新增该新品信息，老品淘汰则反之，减少某品类下属商品。

2、报表支持。

第二、报表支持。

实际上，系统支持离不开报表，报表展示需要系统数据，两者构成一个整体。

商品组合以品类为基础，根据事先的商品组合品项数规划，依据商品ABC、价格带、包装类型、可售区域等因素进行 选品。

基于零售门店的实际，最好是建立一套除后台系统以外，专门的“商品组合”的分析系统，这样就能依据业务需要提供更切合实际的业务报表。

基于目前的BI（敏捷性商务数据分析）系统。

商品组合的系统里维护

1、商品组合的维护。

一些后台系统都自带商品组合维护功能，可以直接在系统中进行维护。这步工作一般由对应品类业务 和 信息员来完成。这些维护人员需要对一些品类知识（特别是商品组合）相当熟悉，才能信任。

有的企业可能有专门的品类管理专门人员，则由这类专业人员主导。

值得注意的是：很多零售门店，并没有这方面的相关维护人员，或者根本没有这类作业流程，则需要另外建立一套适合自己企业的“商品组合”管理系统。该系统需要设计有基本的维护功能。

图2 如下图所示。是某零售企业的后台的商品组合维护模块部分。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIKHopUaOlrXFxAHt8HThCER2sXcicRciab3SvKa7JZwl21KnT5LoAq1U5w/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

上图的维护模块完全符合“商品组合”的思维逻辑。

门店组的商品组合维护

1、商品组的差异化逻辑。

关于差异化，本系列的后续章节-关于“大众品”一节中，还会专门有讨论。

在连锁零售中，将相同属性的几个门店组合在一起，并作为一个新的管理单元，这就是：门店组（行政管理上，类似一个区域经理，同时管理几个门店）。

这里，我们也可以以“门店组”单元，来表述该“组”类的具体商品组合方式有哪些，它包括3个类型部分，例如：

第一部分、组间必需商品。指一个或多个门店组的所有门店组之间，需要共享的商品。即：连锁门店中所有门店（全部区域门店组）都必需经营的商品组合，属于：核心商品项；

第二部分、组内必选商品。指单个门店组内的几个门店所共享的商品组合。这是连锁门店中，某一类门店（同属性门店）必须经营的商品，属于：特色商品项。

第三部分、组外可选商品。指门店自组的商品，一般不做限制（或确定具体的指标数），这是各个门店基于自身的商圈等需求的不同，属于：差异性商品项。

图3 某超市后台系统中，对店组间商品组合的选择。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIKH0V1o6ESWMBMu7RqXurhkIYNFG8Yh22czTKTKIdMsIMWu3wibMrFDPA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

图4 如下图所示。是某零售企业的后台的商品组合维护表（Excel）。 v

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIK45TXHuwarack63nmbxY6Jd6ibCRvqlEqap1TVXBRzwMeCkiaibOVKtSVQ/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

门店经营方案，则是通过这些商品组合的形式来进行管理。特别适合连锁门店商品之间的灵活调配，以体现在统筹的同时也充分体现门店商圈的差异性。

简单来说：

首先，门店依据经营需要，灵活选择所需的商品品类；

然后，选择商品组合，例如，一个门店可以在一个品类内选择多个组合，最终是取这多个组合的商品并集等。

图5 如下图表所示，是一家连锁超市门店的选品（搜组合）的商品选择，打√的视为门店选择该商品为经营商品，否则视为不经营（某些零售后台系统具有该项：商品组合 的设置）。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIKH0V1o6ESWMBMu7RqXurhkIYNFG8Yh22czTKTKIdMsIMWu3wibMrFDPA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

本图来自某超市后台系统的截图。

我们后续的品类选品系统的建立，其依据就是上述讨论的：商品组合逻辑。

图6 如下图所示。商品组合由组间必选商品、组内必选商品和可选商品3部分构成。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5EUvKORY9CetgtBvxwmZUIKCPQ856s4UVZm5Adia8up87Nmw7M9jldMlFnSxvjBPUx14bRwu2icB1cQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

由上图知，组间必选和组内必选的商品共同构成门店的 必选商品。经营业务上，需要重点管理。

例如，配合自动配货，可以给门店配货建议或强制配货，要求门店必须经营这类商品，反之，只有 可选商品 才可以给予门店足够的自由度。

总之，基于不同门店的商品需求，进行灵活的商品组合（选择匹配），从而最终得到各个门店的商品经营范围。

每个门店的商品组合经过组内、组间必选，以及自己的可选过程，实际上，已经是一种：组合中的组合。

未完待续。

商品组合 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个