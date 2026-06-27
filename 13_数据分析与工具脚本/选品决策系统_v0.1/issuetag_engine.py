#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
issuetag_engine.py — 选品决策系统 v0.1(IssueTag 的 H-Score 核心层 / 选品准入校验器)

定位升级(v0.3):IssueTag 从「汰换解释层」升为「选品决策核心层」。三用途:
  ① 解释层   — 候选 SKU 为什么被汰(已落地·见 SKU汰换标签体系_IssueTag_v0.1)
  ② 输入特征 — 标签命中数/类型作为 H-Score 的特征(扣分项),反哺汰换排序
  ③ 准入校验 — 本文件:新品引进时,按 selection_guardrail 做「撤⇄选镜像」的准入判定

核心思想:**每条汰换标签都有一条镜像的选品门槛**——撤什么 ⇄ 不进什么。
汰换是事后纠错,准入是事前拦截;同一套规则两个方向用。

⚠️ signal 阈值待花厅坊真实 POS 校准;本引擎用「结构/毛利/角色」可得字段先跑准入逻辑,
   不依赖复购等暂缺数据(那部分留 WARN 人工判)。

用法:
    python3 issuetag_engine.py          # 跑内置示例(花厅坊方便食品场景)
"""
from dataclasses import dataclass, field

PASS, WARN, BLOCK = "✅ 准入", "⚠️ 附条件", "⛔ 拦截"

@dataclass
class Candidate:
    name: str
    cdt_leaf: str                  # 所属 CDT 叶节点(口味/规格分支)
    price_band: str                # 价格带
    gross_margin: float            # 毛利率
    is_traffic_driver: bool = False
    is_novelty: bool = False       # 猎奇/尝鲜品
    is_seasonal: bool = False
    differentiated: bool = True     # 是否差异化于同分支已有
    overlap_with_main: float = 0.0  # 与主推款属性重合度 0-1

@dataclass
class CategoryContext:
    cdt_leaf_counts: dict          # {叶节点: 现有SKU数}
    price_band_counts: dict        # {价格带: 现有SKU数}
    main_structure_leaves: set     # 主品类结构内的叶节点
    avg_margin: float
    margin_std: float
    cdt_branch_max: int = 2        # 同分支 SKU 上限(CULL-DUP 镜像)
    price_band_max: int = 4        # 每价格带 SKU 上限(CULL-PRICE 镜像)

def check_admission(c: Candidate, ctx: CategoryContext):
    """返回 (总判定, [逐条理由])。镜像 selection_guardrail 7 条规则。"""
    verdicts = []
    def add(level, tag, msg): verdicts.append((level, tag, msg))

    # 规则1 结构上限(CULL-DUP/PRICE 镜像)
    n_leaf = ctx.cdt_leaf_counts.get(c.cdt_leaf, 0)
    if n_leaf >= ctx.cdt_branch_max:
        add(BLOCK, "CULL-DUP", f"同分支「{c.cdt_leaf}」已有 {n_leaf} 款 ≥ 上限 {ctx.cdt_branch_max},撞型,不进")
    n_band = ctx.price_band_counts.get(c.price_band, 0)
    if n_band >= ctx.price_band_max:
        add(WARN, "CULL-PRICE", f"价格带「{c.price_band}」已有 {n_band} 款,接近/超上限,需评估边际贡献")
    # 规则2 差异化准入
    if not c.differentiated:
        add(BLOCK, "CULL-DUP", "未差异化于同分支已有款,视为撞型,不进")
    # 规则3 主结构优先(CULL-EDGE 镜像)
    if c.cdt_leaf not in ctx.main_structure_leaves:
        add(BLOCK, "CULL-EDGE", f"「{c.cdt_leaf}」不在主品类结构内,边缘品类不进或单独立项")
    # 规则4 毛利下限(CULL-MARGIN 镜像)
    floor = ctx.avg_margin - ctx.margin_std
    if c.gross_margin < floor and not c.is_traffic_driver:
        add(BLOCK, "CULL-MARGIN", f"毛利 {c.gross_margin:.0%} < 下限 {floor:.0%} 且非引流款,不进")
    # 规则5 猎奇限流(CULL-FAD 镜像)
    if c.is_novelty:
        add(WARN, "CULL-FAD", "猎奇/尝鲜品:限量试销 + 强制设零动销退出线")
    # 规则6 季节日历(CULL-SEASON 镜像)
    if c.is_seasonal:
        add(WARN, "CULL-SEASON", "季节品:设入场/退场日历,过季自动清退")
    # 规则7 蚕食评估(CULL-CANNIBAL 镜像)
    if c.overlap_with_main >= 0.7:
        add(WARN, "CULL-CANNIBAL", f"与主推款重合度 {c.overlap_with_main:.0%},做蚕食评估再定")

    if not verdicts:
        return PASS, [(PASS, "—", "无触发任何汰换镜像门槛,准入")]
    overall = BLOCK if any(v[0] == BLOCK for v in verdicts) else WARN
    return overall, verdicts

def _demo():
    ctx = CategoryContext(
        cdt_leaf_counts={"红烧牛肉": 3, "板面": 2, "意面": 1, "米线": 1},
        price_band_counts={"3-5元": 5, "5-8元": 4, "20-30元": 0},
        main_structure_leaves={"红烧牛肉", "板面", "海鲜", "酸辣", "意面"},
        avg_margin=0.28, margin_std=0.06, cdt_branch_max=2, price_band_max=4,
    )
    cands = [
        Candidate("某新红烧牛肉面", "红烧牛肉", "3-5元", 0.27),                       # 撞型(满)
        Candidate("莫小仙自热火锅", "自热速食", "20-30元", 0.35, differentiated=True),  # 边缘?但高端差异
        Candidate("某网红黑松露意面", "意面", "8-12元", 0.18, is_novelty=True),         # 低毛利+猎奇
        Candidate("某高端拉面", "拉面", "20-30元", 0.33, differentiated=True),          # 新分支
    ]
    print("=" * 60); print("选品准入校验(IssueTag 选品决策系统 v0.1 · 示例)"); print("=" * 60)
    for c in cands:
        overall, vs = check_admission(c, ctx)
        print(f"\n【{c.name}】→ {overall}")
        for lvl, tag, msg in vs:
            print(f"   {lvl} [{tag}] {msg}")
    print("\n注:自热速食/拉面不在主结构→按规则拦截或单独立项;")
    print("    这正是「撤边缘 ⇄ 不进边缘」的镜像。是否破例(如莫小仙做差异化锚点)= 六哥判断相。")

if __name__ == "__main__":
    _demo()
