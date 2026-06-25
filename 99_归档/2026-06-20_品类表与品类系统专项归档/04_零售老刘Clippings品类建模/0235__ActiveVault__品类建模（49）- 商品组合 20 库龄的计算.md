---
title: 品类建模（49）- 商品组合 20 库龄的计算
source: https://mp.weixin.qq.com/s?__biz=MzAwNjc5MzA0MQ==&mid=2247486518&idx=1&sn=5554ed0fdc3f8cdec9b65eff64eda819&chksm=9b06be08ac71371e90eb5e4a986543c14e9a5df8a2d1df08a8cd5403bc62d719480a991669ef&cur_album_id=4032598383209709579&scene=189#wechat_redirect
author:
  - "[[Clippings全量阅读台账_v0.1]]"
published:
created: 2026-06-18
description: 本节主要介绍库龄的有关计算方法。例如，库龄在不同业务场景中的计算。
tags:
  - clippings
---
零售老刘 零售数据化企划 *2025年4月18日 08:59*

序言：本节主要介绍库龄的有关计算方法。例如，库龄在不同业务场景中的计算。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxl4hDvF8YkZqZ2jxULRWTjcIBn0zFCaH2bWWeia2DXdpibQNm4E1iaSMjew/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=0)

零售中的账龄与库龄的计算

基于上述讨论，我们继续完善一下【库龄】这个度量指标。

1、账龄与库龄的相同计算方法。

（1）最简单的常规计算公式。

账龄 = 当前日期 - 商品入账日期

库龄 = 当前日期 - 商品入库日期

从上述内容得知：账龄与库龄均依赖时间差值计算（都可使用DATEDIFF函数），语义区别是：账龄关注资金回收风险，库龄聚焦库存效率。共同的计算式：

账龄（库龄）=DATEDIFF ( \[起始日期\], TODAY(), DAY )

上述模型的DAX公式中，两者均需结合DATEDIFF与上下文控制。库龄在批次场景下可能还需扩展为加权计算，以及涉及静态日期参数表和预计算，以提升库龄度量计算的性能。

2、账龄的Excel表计算。

（1）计算逻辑的区别。很多人刚开始都以为：库龄与账龄的计算方法一样。而实际上，如上所述，两者的计算逻辑不一样。例如，库龄多了批次概念，多了一个步骤。例如，要将结存数量跟入库数量（因为每次入库时，都可能会有前面批次的剩余库存）比较后再拆分。

（2）账龄的Excel表计算。

第一步、在Excel表中，导入（或录入）条码对应的库存表，设计好账龄的区间，然后使用VLOOKUP函数直接引用该区域值，计算出账龄。

图2 如下图所示，账龄的Excel计算表

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlEhrj5Gy3wGYs9sMxTt02lyXs9ktLPElRT0QFGXqal9PtCVF2DMg2ibg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=1)

上图中，计算公式的含义：VLOOKUP函数的第一个参数是“今天与入库时期的时间差”，第二参数是：按对应的时期，引用区间表的相应值（【账龄区间列】的值）。

这一步，实际是使用向账龄表（左表），新增一个【账龄区间】列（通过VLOOKUP函数）。

第二步、计算每个条码在不同账龄区间的值。

首先，将区间作为列，如下图所示。

图3 如下图所示，每个商品的账龄区间计算表

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlgAm26f99CicOy0A4zDINrKZcjjbaMz6ibSqaFKAic7asa02uF1IG1LAvA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=2)

其次，上图中，再根据编码（唯一值）、区间统计数量、区间，通过多条件求和（SUMIFS函数），就可以求出每个条码在不同区间的账龄期。

图4 如下图所示，每个商品的账龄区间计算表

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlia9yNmZdDVAKcWWvHT3WpGoXdo1FvbJHnrCKumCIJDTgtlicUmibaYWpQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=3)

公式：= SUMIFS($C:$C,$B:$B,$J3,$D:$D,K$2)，第一个参数是准备求值的列（计算哪个列的值，这里是C列），后面两个是两个条件。

到这里，账龄的Excel计算已完成，接下来就是库龄。

零售库存管理中的库龄计算

1、库龄的Excel计算。

图5 计算逻辑：如下图所示：

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlOib4BD9hHUA8s4RBaLyJjK3e5ah9ePibZOsh3BLicS9duITjjpkpUsm9g/640?wx_fmt=png&from=appmsg&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=4)

编码10055，结存数量60，而入库数量区间0-15段是5，不够60拆分，因此该区间任为5，剩下的（60-5=55），在30-60区间为110，足够60拆分，110拆分掉60后还剩下55（110-60-5 = 55），其他区间为0。

该逻辑的大概意思是：累计入库数，如果累计入库数量<= 结存数量，就返回区间本身的值，否则就用结存数量减去前一个区间之前的累计入库数量，最后如果小于0，则显示0。公式为：

\= MAX(0,IF(SUM($I3:I3)<=$G3,I3,$G3-SUM($H3:H3)))

公式中的MAX(0,IF) ，目的是让公式结果小于0时显示0（红色外套部分）。

注意：上述Excel表计算方式，是为了展示计算依据的语义逻辑，实际计算时，可以使用透视表等方法。

2、库龄的建模计算。

（1）库存方式与库龄。

在实际的库存管理中，依据安全库存、管道库存以及最佳定购批量这三个【点】，系统或数据分析中，往往会设计相应的库存管理【线】，以帮助企业实现库存管理业务的【面】。

一般来说，库存结果包含三类库存：基本面的周转库存、合适的安全库存、以及一定比例（一般较少）的呆滞库存。

图6 如下图：三种库存方式示意图。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlBicmFMQ8gtPywoyHI9uSlgsSsA3G2YNZIBoOdFbS5oGvruK2lfHPmmQ/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=5)

这里的【线】，是点和面之间的链接，在较为正式的库存管理中有点复杂，但是在一般的零售门店的库存管理中，最大的业务运用的现实意义是：基于批次。

例如，按照每个商品的入库单来显示库龄，并与设计的标准库龄比较，以关注到某一批入库的量的变化，确保没有过有效期，从而降低损耗。

因为，实际的业务流程中，【库龄】以“订单回货入库”为“分割线”，属于已经发生的业务事件。通过库龄来倒推报货、订货、陈列等业务的合理性。

（2）三条库存量线与库龄。

在之前的《库存管理》系列章节中，提到过：库存的三条理论库存线：安全库存线、再订购点、最大库存。

这三条库存管理【线】，无论怎样的业务表现，都会产生某种结果，并可能是某个量化的度量指标来衡量它。例如，这里的【库龄】。

也就是说，基于“结果”性指标的【库龄】。同时关联上三条线。例如：

安全库存线：通常，实际库存都应该高于安全库存线。过高、过低都会导致相应的业务“触发”。而且，一般的安全库存线的设计较难，也需要一定的技术。

这时候，我们使用【库龄】来代替它。例如，如果某个商品的库龄期过低（少于设定的库龄期），有可能在下次采购回货前耗尽库存。因此，应设计安全【库龄】（代替安全库存线）警戒，并触发配送、补货、订货业务提示。

再订购点、最大库存的【库龄】关系，也是如此。

因此，【库龄】在零售门店的库存管理中，是一个相当重要的指标。

（3）库龄的计算模型表

库龄计算模型，可在其他包含基本维度表的基础上创建，以节省建模的时间和精力。

第一步、业务宽表准备。

首先，是事实表的准备。一般零售企业中，库存管理涉及一个基本的事实表：出入库明细表（包含全部出入库记录）。

如果不涉及稍复杂的购物篮粒度级的计算，也可以使用更清晰、简单的“入库明细表”。

**图7** 某超市库存管理模型中，引用的基本维度表以及“出入库事实表”

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlGcQuXCqGNj0xCr8wSXIgYsCDJyu36Zwup04j75edibqL5h9aQiaePaHg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=6)

某超市的库存管理模型中，引用的基本维度表以及“出入库事实表”。

其次，如果门店系中出入库事实表中，缺少【当前库存】列字段，还需要一个：盘点表（手动盘点完成），以记录当前的库存量。

或者是，从系统中导出一份“当前库存表”。上图实例中的事实表包含【库存】。

最后，可能还需要“库龄参数表”，作为库龄分区间的参考等等。

图8 如下图所示，库龄区间参数表

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlRwNvqMMSOgZUFECQCwtWk1kN10MyRzxtS2GnprnWG5hGDXhyffthNA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=7)

有时，还可能需要“当前库存（实时库存）表”。这是业务分析中常用到的表，因为要知道当前时间的实时库存，从系统加载该表=时，“实时”指下载时的时间（可准确到时、分、秒）。

第二步、【库龄】度量的设计。接下来的这一步是难点和关键。因为，关于库龄，一个最大的问题就是：批次。

不同批次的入库、调拨等，会导致成本结算、业务流程很难跟踪和计算。例如：

业务想知道当前某日期或该时期之前的每一批次的存货还有多少？

这个问题就涉及到批次管理的概念。我们只有将商品的出入库记录信息，都对应到相应的批次才算是：批次计算。

真正的批次管理很复杂（例如只能系统能处理）。零售门店管理实践中，通常采用“先进先出”的方式。简单来说，先进先出是指：将早入库的商品（或其他维度），当需要时，也最先取出（处理）。

先进先出的现实意义在于：尽量确保商品不容易过期。

需要说明的是，良好的事实表是分析的基础。举两个不同事实表的库龄计算的设计。但无论使用哪种事实表，关键是得出【库龄】，以及衍生的另一个度量：【库存结余】。

第一种、使用“出入库”事实表。

这又分两种：一是，出入库事实表中，本来就包含【出库结余】的字段列，直接引用该列计算出【结余库存】即可。

【库龄】计算，直接使用 DATEDIFF函数，第一个参数（起始日期）使用事实表中的入库时期，第二参数（结束时期），取当前数据时期的最大值，或者今天。公式为：

账龄（库龄）=DATEDIFF(’出入库’\[入库日期\], TODAY(), DAY)

账龄（库龄）=DATEDIFF(’出入库’\[入库日期\], MAX（’出入库’\[日期\]）, DAY)。

图9 如下图所示，引用包含【结余库存】的出入库事实表计算【结余库存】。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlia2DEIcU9jl8ryFSf3qby5HYicg7vY09dbagStPAmYUY1axPEbzbELAg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=8)

二是，计算每个入库时期之间的差值（即：库龄）。有兴趣的可以去参考这方面的参考。这里略过。

图10 如下图所示，【库龄】度量计算公式一例（参考截图）

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlia2DEIcU9jl8ryFSf3qby5HYicg7vY09dbagStPAmYUY1axPEbzbELAg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=9)

第二种、使用“批次”事实表。

很多后台管理都提供有“批次管理”模块。其中的“批次明细表”可以作为事实表使用。这时候，该表包含的字段可能更适合做【库龄】、【结余库存】分析。

图11 来自“批次管理”模块的批次事实表。

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxlQ6pFn2zLDrkItqloicn4p41gf2cOZYtmokfk380gLxibMIZTdtajUO0w/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=10)

批次事实表中，可能存在【滞存天数】字段，这实际就是每个时期之间的【库龄】数，即每次入库到下次再入库时的间隔天数。这种情况下，直接引用该列技术那即可。

图11 来自“批次管理”模块的批次事实表

![Image](https://mmbiz.qpic.cn/sz_mmbiz_png/cpSGNibibev5Fib15r8hEEQubTa0afLGGxliaCr77ZPXadGBgmJYwtZicch0sARAoeoLv4oG3Jg5HMSV5Rfuf9TCwpA/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1#imgIndex=11)

因为，本节以库龄的语义为主，具体的建模场景运用，后续再讨论。

未完待续。

商品组合 系列 · 目录

继续滑动看下一个

零售数据化企划

向上滑动看下一个