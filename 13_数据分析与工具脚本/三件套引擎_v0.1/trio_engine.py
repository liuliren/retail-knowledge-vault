#!/usr/bin/env python3
"""三件套引擎 v0.1 — 清洗 / ABCZ / 动销率 / 价格带(含毛利试算)

口径依据(已签字/已验证):
- ABC 按小类内累计净额 A<=70% / B<=90% / C>90%,禁止全场口径
  (SKU角色层与目的品保护机制_v0.1.6 §2.3, 六哥 2026-06-26 签)
- Z 类 = 档案在册(未停购)且期间零动销
- 毛利双轨: 标品=POS差价率; 生鲜无SKU级进价(结构性,2026-07-02 六哥确认),
  生鲜毛利须档口级月度倒算,本引擎只输出标品侧差价率并标注生鲜不可信

用法:
  python3 trio_engine.py clean     --src <分品类xls目录> --out <输出目录> [--prefix 花厅坊-202604-6月]
  python3 trio_engine.py abcz      --master <master.csv> --archive <档案xls目录> --out <输出目录>
  python3 trio_engine.py movement  --master <master.csv> --archive <档案xls目录> --out <输出目录>
  python3 trio_engine.py priceband --master <master.csv> --out <输出目录>
  python3 trio_engine.py all       --master <master.csv> --archive <档案xls目录> --out <输出目录>

依赖: pandas, python-calamine (pip3 install --break-system-packages pandas python-calamine)
首验: 花厅坊 2026.04-06, 19品类 15.2万行, 19/19 内部对账偏差 0.00% (2026-07-02)
"""
import argparse, os, re, sys, csv
from pathlib import Path
import pandas as pd
from python_calamine import CalamineWorkbook

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# 列映射/口径常量单一定义处: ../pos_schema.py (改口径只改那里,两引擎共享)
from pos_schema import (SALES_COLS, ARCH_STD, ARCH_ALT, DATE_ROW_RE, AGG_TABLE_RE,
                        EXCLUDE_BIGCLASS, SYS_TOTAL_COL, RECON_TOLERANCE_PCT)


def load_archive(archive_dir: str) -> pd.DataFrame:
    """档案 xls 目录 → 去重 SKU 注册表(自动识别两种版式)"""
    rows_out = []
    for f in sorted(os.listdir(archive_dir)):
        if "档案" not in f or not f.endswith(".xls"):
            continue
        rows = CalamineWorkbook.from_path(os.path.join(archive_dir, f)).get_sheet_by_index(0).to_python()
        hi, cmap = None, None
        for i, r in enumerate(rows[:8]):  # 表头行探测
            j = "|".join(str(c) for c in r)
            if re.search(r"货号|条码", j) and re.search(r"品名", j):
                hi = i
                cmap = ARCH_ALT if str(r[1]).strip() in ("货号", "条码") else ARCH_STD
                break
        if hi is None:
            print(f"⚠️ 跳过(未识别表头): {f}", file=sys.stderr)
            continue
        for r in rows[hi + 1:]:
            d = {v: (str(r[k]).strip() if k < len(r) else "") for k, v in cmap.items()}
            if d["货号"] and re.match(r"^\d", d["货号"]):
                d["来源文件"] = f
                rows_out.append(d)
    reg = pd.DataFrame(rows_out).drop_duplicates("货号", keep="first")
    reg["停购"] = reg.停购日期.str.len() > 4
    print(f"档案: {len(rows_out)}行 → 去重{len(reg)} → 在册(未停购){int((~reg.停购).sum())}")
    return reg


def check_aggregate_diff(src, prefix, covered_cats):
    """第八坑防护(2026-07-06·lessons回码): 被排除的合集表(生鲜/类别汇总表)中
    若存在分表未覆盖的类别 → 该类别销售会整体丢失(实证:禽蛋2293行/14.2万)。
    只报警不阻断; 类别列按表头含"类别名称"自动定位。"""
    import re as _re, os as _os
    aggs = [f for f in _os.listdir(src) if f.startswith(prefix) and f.endswith(".xls")
            and AGG_TABLE_RE.search(f)]
    problems = []
    for f in aggs:
        try:
            rows = CalamineWorkbook.from_path(_os.path.join(src, f)).get_sheet_by_index(0).to_python()
            col = None
            for r in rows[:10]:
                for i, c in enumerate(r):
                    if "类别名称" in str(c):
                        col = i; break
                if col is not None: break
            if col is None:
                problems.append((f, "未定位到'类别名称'列,无法差集校验")); continue
            agg_cats = {str(r[col]).strip() for r in rows
                        if col < len(r) and str(r[col]).strip()
                        and "类别" not in str(r[col]) and "合计" not in str(r[col])}
            only = {c for c in agg_cats if not any(c in cov or cov in c for cov in covered_cats)}
            if only:
                problems.append((f, f"合集表独有类别(分表未覆盖·销售可能丢失): {sorted(only)}"))
        except Exception as e:
            problems.append((f, f"差集校验失败: {str(e)[:60]}"))
    if problems:
        print("\n🔴 第八坑警报(合集表类别差集):", file=sys.stderr)
        for f, why in problems:
            print(f"  {f}: {why}", file=sys.stderr)
    return problems


def cmd_clean(a):
    """分品类销售 xls → 标准明细主表 csv, 逐表与系统合计行对账"""
    files = sorted(f for f in os.listdir(a.src) if f.startswith(a.prefix) and f.endswith("汇总表.xls")
                   and EXCLUDE_BIGCLASS not in f and not AGG_TABLE_RE.search(f))
    os.makedirs(a.out, exist_ok=True)
    mp = os.path.join(a.out, a.master_name)
    ok = True
    covered_cats = set()
    with open(mp, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["品类文件"] + list(SALES_COLS.values())[1:])
        for f in files:
            cat = re.sub(rf"^{re.escape(a.prefix)}|汇总表\.xls$", "", f)
            covered_cats.add(cat)
            rows = CalamineWorkbook.from_path(os.path.join(a.src, f)).get_sheet_by_index(0).to_python()
            n, amt, sys_total = 0, 0.0, None
            for r in rows:
                cells = [str(x).strip() for x in r]
                if any("合计" in x for x in cells[:4]):
                    try:
                        sys_total = float(r[SYS_TOTAL_COL])
                    except (ValueError, TypeError, IndexError):
                        pass
                    continue
                if (len(cells) > 9 and re.match(r"^\d+\.?\d*$", cells[0]) and DATE_ROW_RE.match(cells[9])):
                    w.writerow([cat] + [str(r[i]).strip() if i < len(r) else "" for i in list(SALES_COLS)[1:]])
                    n += 1
                    amt += float(r[13] or 0) - float(r[16] or 0)
            dev = None if not sys_total else (amt - sys_total) / sys_total * 100
            flag = "✓" if dev is not None and abs(dev) <= RECON_TOLERANCE_PCT else "⚠️"
            if flag == "⚠️":
                ok = False
            print(f"{flag} {cat}: {n}行 净额{amt:,.0f} 系统合计{sys_total or 0:,.0f} 偏差{dev if dev is not None else 'N/A'}%")
    print(f"master → {mp}")
    check_aggregate_diff(a.src, a.prefix, covered_cats)
    if not ok:
        print("⚠️ 存在对账偏差>0.5%的品类,数据可疑,判读前先查", file=sys.stderr)


def _load_sku(master):
    m = pd.read_csv(master, dtype={"条码": str, "类别编码": str})
    for c in ["销售数量", "销售金额", "退货数量", "退货金额", "进销差价"]:
        raw = pd.to_numeric(m[c], errors="coerce")
        n_bad = raw.isna().sum() - m[c].isna().sum()  # 排除本来就是空值的行,只数"转换失败"的脏值
        if n_bad > 0:
            print(f"⚠️ 字段「{c}」有 {n_bad} 行非数值内容(如文字/乱码)被当作0处理,判读前先核实这些行", file=sys.stderr)
        m[c] = raw.fillna(0)
    m["净额"] = m.销售金额 - m.退货金额
    m["净量"] = m.销售数量 - m.退货数量
    sku = m.groupby("条码").agg(品名=("品名", "first"), 大品类=("品类文件", "first"),
        小类=("类别名称", "first"), 净额=("净额", "sum"), 净量=("净量", "sum"),
        销售天数=("销售日期", "nunique"), 差价=("进销差价", "sum"),
        经营方式=("经营方式", "first")).reset_index()
    return sku[sku.净额 > 0]


def cmd_abcz(a, sku=None, reg=None):
    sku = sku if sku is not None else _load_sku(a.master)
    reg = reg if reg is not None else load_archive(a.archive)
    parts = []
    for _, g in sku.groupby("小类"):  # 铁律:小类内口径
        g = g.sort_values("净额", ascending=False).copy()
        cum = g.净额.cumsum() / g.净额.sum()
        g["ABC"] = ["A" if x <= 0.70 else ("B" if x <= 0.90 else "C") for x in cum]
        parts.append(g)
    sku = pd.concat(parts)
    active = reg[~reg.停购]
    # Z类匹配防呆(2026-07-06·科学性漏洞回码): 档案"货号"直接isin销售"条码"——
    # 两套编码体系若不一致(货号≠条码/自编码), 未匹配即被判Z, Z类会系统性虚增。
    # 校验: 销售条码能回匹配到档案货号的比例<95% → 硬警报(不阻断,判读前必查)。
    match_rate = sku.条码.isin(reg.货号).mean() * 100
    if match_rate < 95:
        print(f"\n🔴 Z类匹配警报: 销售条码↔档案货号 匹配率仅 {match_rate:.1f}% (<95%) — "
              f"两套编码体系疑似不一致, Z类清单可能大量虚增, 判读前先核对编码口径(货号/条码/自编码)",
              file=sys.stderr)
    z = active[~active.货号.isin(sku.条码)]
    os.makedirs(a.out, exist_ok=True)
    sku.to_csv(os.path.join(a.out, "ABCZ_SKU级.csv"), index=False)
    z[["货号", "品名", "类别名称", "供应商", "零售价"]].to_csv(os.path.join(a.out, "Z类_零动销清单.csv"), index=False)
    d = sku.ABC.value_counts()
    print(f"ABC(小类内): A={d.get('A',0)}({d.get('A',0)/len(sku)*100:.0f}%SKU→{sku[sku.ABC=='A'].净额.sum()/sku.净额.sum()*100:.0f}%销售) "
          f"B={d.get('B',0)} C={d.get('C',0)} | Z类={len(z)}")
    print("校准参照: 零售老刘实践 ≈15-17%SKU→60%销售; A显著偏宽=结构分散")
    return sku, z


def cmd_movement(a, sku=None, reg=None):
    sku = sku if sku is not None else _load_sku(a.master)
    reg = reg if reg is not None else load_archive(a.archive)
    active = reg[~reg.停购]
    mov = pd.concat([active.groupby("类别名称").size().rename("在册"),
                     active[active.货号.isin(sku.条码)].groupby("类别名称").size().rename("动销")],
                    axis=1).fillna(0)
    mov["动销率"] = mov.动销 / mov.在册
    os.makedirs(a.out, exist_ok=True)
    mov.reset_index().sort_values("动销率").to_csv(os.path.join(a.out, "动销率_小类.csv"), index=False)
    total = 1 - (len(active) - active.货号.isin(sku.条码).sum()) / len(active)
    print(f"全店动销率: {total:.1%} (在册{len(active)} 动销{int(active.货号.isin(sku.条码).sum())})")
    print("⚠️ 判读前置: 停购标记若未维护(花厅坊仅4/14674),分母虚大,真实动销率偏高")
    for i, r in mov[mov.在册 >= 30].sort_values("动销率").head(8).iterrows():
        print(f"  {str(i)[:14]:16s} 在册{int(r.在册):4d} 动销{int(r.动销):4d} {r.动销率:.0%}")
    return mov


def cmd_priceband(a, sku=None):
    sku = sku if sku is not None else _load_sku(a.master)
    sku = sku.copy()
    sku["单价"] = (sku.净额 / sku.净量.replace(0, pd.NA)).astype(float)
    cat = sku.groupby("大品类").agg(SKU数=("条码", "count"), 净额=("净额", "sum"), 差价=("差价", "sum"),
        P25=("单价", lambda s: s.quantile(.25)), 中位价=("单价", "median"),
        P75=("单价", lambda s: s.quantile(.75))).sort_values("净额", ascending=False)
    cat["差价率%"] = cat.差价 / cat.净额 * 100
    os.makedirs(a.out, exist_ok=True)
    cat.reset_index().to_csv(os.path.join(a.out, "品类概览_价格带毛利.csv"), index=False)
    print(f"{'品类':12s}{'SKU':>5}{'净额万':>8}{'差价率%':>8}{'P25':>7}{'中位':>7}{'P75':>7}")
    for i, r in cat.iterrows():
        print(f"{str(i):14s}{int(r.SKU数):5d}{r.净额/1e4:8.1f}{r['差价率%']:8.1f}{r.P25:7.1f}{r.中位价:7.1f}{r.P75:7.1f}")
    print("⚠️ 毛利双轨铁则: 差价率仅标品可信;生鲜档口无SKU级进价(差价率≈售价,虚高),生鲜毛利用档口月度进货总额倒算")
    return cat


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    pc = sub.add_parser("clean")
    pc.add_argument("--src", required=True)
    pc.add_argument("--out", required=True)
    pc.add_argument("--prefix", default="花厅坊-202604-6月")
    pc.add_argument("--master-name", default="sales_master.csv")
    for name in ("abcz", "movement", "all"):
        sp = sub.add_parser(name)
        sp.add_argument("--master", required=True)
        sp.add_argument("--archive", required=True)
        sp.add_argument("--out", required=True)
    pp = sub.add_parser("priceband")
    pp.add_argument("--master", required=True)
    pp.add_argument("--out", required=True)
    a = p.parse_args()
    if a.cmd == "clean":
        cmd_clean(a)
    elif a.cmd == "abcz":
        cmd_abcz(a)
    elif a.cmd == "movement":
        cmd_movement(a)
    elif a.cmd == "priceband":
        cmd_priceband(a)
    elif a.cmd == "all":
        sku, reg = _load_sku(a.master), load_archive(a.archive)
        sku2, _ = cmd_abcz(a, sku, reg)
        cmd_movement(a, sku, reg)
        cmd_priceband(a, sku2)


if __name__ == "__main__":
    main()
