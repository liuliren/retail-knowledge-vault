#!/usr/bin/env python3
"""花厅坊 90 天全量脱敏合并（CODEX-Data-Workstream-Batch-015）.

只读真实 xls，写脱敏合并表到 gitignored processed/ 目录。
- 主干：供应商销售汇总_90天（全店）；左连 商品档案（采购周期/建档日期）、滞销商品（最近销售/进货/引进日期）。
- 脱敏：条码=占位（不读真实条码）、供应商=SUP_xxx 代号、进价=内部列（不进 md/git）。
- 不打印真实条码/进价/供应商裸名到终端；关键字段缺失报 blocked，不硬猜。
- 不修改原始文件；不跑 full dry-run；不写回。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
from pathlib import Path

import pandas as pd
import python_calamine as pc

REF_DATE = dt.date(2026, 6, 23)
BANNER = ("打印时间", "打印人", "第", "页")
HEADER_KEYS = ("货号", "品名", "类别", "数量", "金额", "库存", "供应商", "进价", "售价", "毛利", "日期", "价")


def find_header(rows: list[list], max_scan: int = 25) -> int:
    for i, r in enumerate(rows[:max_scan]):
        cells = [str(c).strip() for c in r if str(c).strip()]
        if len(cells) < 3:
            continue
        if any(b in cells[0] for b in ("打印时间", "打印人")):
            continue
        if sum(1 for c in cells if any(k in c for k in HEADER_KEYS)) >= 2:
            return i
    return 0


def read_xls(path: Path) -> pd.DataFrame:
    wb = pc.load_workbook(str(path))
    rows = wb.get_sheet_by_name(wb.sheet_names[0]).to_python()
    hi = find_header(rows)
    header = [str(c).strip() for c in rows[hi]]
    data = rows[hi + 1 :]
    df = pd.DataFrame(data, columns=header)
    # 丢弃横幅/合计尾行：货号列为空的行
    return df


def col(df: pd.DataFrame, *names: str) -> str | None:
    for n in names:
        for c in df.columns:
            if n == str(c).strip():
                return c
    for n in names:  # 退化为包含匹配
        for c in df.columns:
            if n in str(c):
                return c
    return None


def to_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def to_date(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="09_门店案例与项目复盘/乐易购花厅坊店/99_原始素材/01_门店数据材料")
    ap.add_argument("--vault", default=".")
    args = ap.parse_args()
    base = Path(args.vault).resolve() / args.input
    outdir = base / "processed"
    outdir.mkdir(parents=True, exist_ok=True)

    qc: list[str] = []

    # ── 主干：供应商销售汇总_90天 ──
    bb_path = next(base.glob("供应商销售汇总_90天*.xls"), None)
    if bb_path is None:
        print("BLOCKED: 缺 供应商销售汇总_90天")
        return 2
    bb = read_xls(bb_path)
    k_code = col(bb, "货号", "商品编码")
    bb = bb[bb[k_code].astype(str).str.strip() != ""].copy()
    bb["货号"] = bb[k_code].astype(str).str.strip()
    bb = bb[bb["货号"].str.match(r"^[0-9A-Za-z]")].copy()  # 去尾部合计行
    n_bb = len(bb)
    qc.append(f"主干行数={n_bb}")

    out = pd.DataFrame()
    out["货号"] = bb["货号"]
    out["品名"] = bb[col(bb, "品名")].astype(str) if col(bb, "品名") else ""
    out["类别名称"] = bb[col(bb, "类别名称", "类别")].astype(str) if col(bb, "类别名称", "类别") else ""
    out["销售额"] = to_num(bb[col(bb, "销售金额")]) if col(bb, "销售金额") else pd.NA
    out["销量"] = to_num(bb[col(bb, "销售数量")]) if col(bb, "销售数量") else pd.NA
    out["毛利额"] = to_num(bb[col(bb, "毛利")]) if col(bb, "毛利") else pd.NA
    out["毛利率"] = to_num(bb[col(bb, "毛利率")]) if col(bb, "毛利率") else pd.NA
    out["库存数量"] = to_num(bb[col(bb, "库存数量")]) if col(bb, "库存数量") else pd.NA
    out["库存成本金额"] = to_num(bb[col(bb, "当前库存成本金额", "库存成本")]) if col(bb, "当前库存成本金额", "库存成本") else pd.NA
    out["销售成本"] = to_num(bb[col(bb, "销售成本")]) if col(bb, "销售成本") else pd.NA
    # 毛利额/毛利率 派生兜底：源「毛利」「毛利率」列在本导出中全空 → 由 销售额−销售成本 派生（标准定义）。
    gp_raw = to_num(out["毛利额"]).fillna(0)
    if float(gp_raw.abs().sum()) == 0 and col(bb, "销售成本"):
        out["毛利额"] = to_num(out["销售额"]) - to_num(out["销售成本"])
        qc.append("毛利额=派生(销售额−销售成本)[源毛利列全空]")
    gr_raw = to_num(out["毛利率"]).fillna(0)
    if float(gr_raw.abs().sum()) == 0:
        sa = to_num(out["销售额"])
        out["毛利率"] = (to_num(out["毛利额"]) / sa).where(sa != 0)
        qc.append("毛利率=派生(毛利额/销售额)[源毛利率列全空]")
    out["日均销量"] = to_num(bb[col(bb, "日均销量")]) if col(bb, "日均销量") else pd.NA
    out["售价"] = to_num(bb[col(bb, "档案售价", "零售价")]) if col(bb, "档案售价", "零售价") else pd.NA
    # 进价：内部列（不进 md/git）
    out["_进价_内部"] = to_num(bb[col(bb, "参考进价", "加权平均价")]) if col(bb, "参考进价", "加权平均价") else pd.NA
    # 供应商代号化（用编码生成 SUP_xxx；不留名）
    sup_code = col(bb, "主供应商编码", "供应商编码")
    if sup_code:
        codes = bb[sup_code].astype(str).str.strip()
        uniq = {c: f"SUP_{i+1:04d}" for i, c in enumerate(sorted(codes[codes != ""].unique()))}
        out["供应商代号"] = codes.map(uniq).fillna("SUP_NA")
        qc.append(f"供应商代号化={len(uniq)}家")
    else:
        out["供应商代号"] = "SUP_NA"

    # ── 左连 商品档案（采购周期/建档日期）──
    arch_parts = []
    for p in base.glob("*商品档案表*.xls*"):
        try:
            a = read_xls(p)
            ak = col(a, "货号", "商品编码")
            if not ak:
                continue
            cyc0 = col(a, "采购周期")
            cre0 = col(a, "创建日期", "建档日期", "引进日期")
            sub = pd.DataFrame({"货号": a[ak].astype(str).str.strip()})
            sub["采购周期"] = to_num(a[cyc0]) if cyc0 else pd.NA
            sub["建档日期"] = a[cre0] if cre0 else pd.NA
            arch_parts.append(sub)
        except Exception:
            pass
    cycle_match = 0
    if arch_parts:
        arch = pd.concat(arch_parts, ignore_index=True).drop_duplicates("货号")
        out = out.merge(arch, on="货号", how="left")
        cycle_match = int(to_num(out["采购周期"]).notna().sum())
        out["到货天数"] = to_num(out["采购周期"]).where(to_num(out["采购周期"]) > 0, 7)
        out["到货天数_默认标记"] = to_num(out["采购周期"]).isna() | (to_num(out["采购周期"]) <= 0)
        out["_建档日期"] = to_date(out["建档日期"])
    else:
        out["到货天数"], out["到货天数_默认标记"], out["_建档日期"] = 7, True, pd.NaT
    qc.append(f"商品档案匹配(采购周期非空)={cycle_match}")

    # ── 左连 滞销商品（最近销售/进货/引进日期，全店）──
    sl_path = next(base.glob("滞销商品*.xls"), None)
    inv_match = 0
    if sl_path:
        sl = read_xls(sl_path)
        slk = col(sl, "货号", "商品编码")
        sl["货号"] = sl[slk].astype(str).str.strip()
        last_sale = col(sl, "最近销售日期")
        last_buy = col(sl, "最近进货日期")
        intro = col(sl, "引进日期")
        keep = ["货号"] + [c for c in (last_sale, last_buy, intro) if c]
        sl = sl[keep].drop_duplicates("货号")
        out = out.merge(sl, on="货号", how="left")
        if last_sale:
            out["_最近销售日期"] = to_date(out[last_sale])
            inv_match = int(out["_最近销售日期"].notna().sum())
        if last_buy:
            out["_最近进货日期"] = to_date(out[last_buy])
        if intro and "_建档日期" in out:
            out["_建档日期"] = out["_建档日期"].fillna(to_date(out[intro]))
    qc.append(f"滞销/库存匹配(最近销售日期非空)={inv_match}")

    # ── 派生字段 ──
    ref = pd.Timestamp(REF_DATE)
    # 库龄：ref - 最近进货日期（无则用建档日期）
    base_age = out["_最近进货日期"] if "_最近进货日期" in out else pd.Series(pd.NaT, index=out.index)
    base_age = base_age.fillna(out["_建档日期"]) if "_建档日期" in out else base_age
    out["库龄天数"] = (ref - base_age).dt.days
    out["库龄_状态"] = out["库龄天数"].apply(lambda d: "blocked_缺库龄" if pd.isna(d) else ("正常" if d <= 30 else "预警" if d <= 60 else "滞销" if d <= 90 else "重滞"))
    # ITO 估算：销售成本 / 库存成本金额（90天）→ 年化 ×(365/90)
    ito = to_num(out["销售成本"]) / to_num(out["库存成本金额"])
    out["ITO估算"] = (ito * (365 / 90)).where(to_num(out["库存成本金额"]) > 0)
    out["ITO_状态"] = out["ITO估算"].apply(lambda v: "blocked_缺ITO" if pd.isna(v) else "估算")
    # 缺货：库存=0 且有销量
    out["缺货标记"] = (to_num(out["库存数量"]).fillna(-1) == 0) & (to_num(out["销量"]).fillna(0) > 0)
    # 清仓/负毛利
    out["负毛利清仓标记"] = (to_num(out["毛利额"]).fillna(0) < 0) | (to_num(out["毛利率"]).fillna(0) < 0)
    # 新品：建档/引进 90 天内
    out["新品标记"] = ("_建档日期" in out) and False
    if "_建档日期" in out:
        out["新品标记"] = (ref - out["_建档日期"]).dt.days.le(90).fillna(False)
    # 促销：无标记 → blocked 占位
    out["促销标记"] = "blocked_无促销字段"
    # 条码：脱敏占位（不读真实条码）
    out["条码脱敏"] = "{{EAN13_已脱敏}}"
    # 需复核/复核原因 占位（dry-run 时由 abc_classifier 填）
    out["需复核"] = pd.NA
    out["复核原因"] = ""

    # ── 输出（gitignored）──
    stamp = REF_DATE.strftime("%Y%m%d")
    out_path = outdir / f"花厅坊_90天全量合并_脱敏_v0.1_{stamp}.xlsx"
    # 写出含内部进价列（xlsx 在 gitignored 目录，允许）
    out.to_excel(out_path, index=False)

    # ── 质量检查（不打印敏感值）──
    n_out = len(out)
    def cov(c):
        return f"{int(to_num(out[c]).notna().sum())}/{n_out} ({to_num(out[c]).notna().mean()*100:.1f}%)" if c in out else "缺"
    qc.append(f"合并后行数={n_out}")
    qc.append(f"重复膨胀={'是' if n_out>n_bb else '否'}(主干{n_bb}→{n_out})")
    qc.append(f"毛利额覆盖={cov('毛利额')}")
    qc.append(f"毛利率覆盖={cov('毛利率')}")
    qc.append(f"库存覆盖={cov('库存数量')}")
    qc.append(f"库龄非blocked={int((out['库龄_状态']!='blocked_缺库龄').sum())}/{n_out}")
    qc.append(f"ITO非blocked={int((out['ITO_状态']!='blocked_缺ITO').sum())}/{n_out}")
    qc.append(f"缺货标记数={int(out['缺货标记'].sum())}")
    qc.append(f"负毛利清仓数={int(out['负毛利清仓标记'].sum())}")
    qc.append(f"新品数={int(out['新品标记'].sum())}")
    qc.append(f"条码全脱敏={'是' if (out['条码脱敏']=='{{EAN13_已脱敏}}').all() else '否'}")
    qc.append(f"输出文件={out_path.name}")

    print("=== QC SUMMARY (无敏感值) ===")
    for line in qc:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
