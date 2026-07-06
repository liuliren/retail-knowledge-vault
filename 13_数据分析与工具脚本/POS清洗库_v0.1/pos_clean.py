#!/usr/bin/env python3
"""POS清洗库 v0.1 — 国产POS导出的探查/销售清洗/档案清洗 三合一

血统: 花厅坊 2026-07-02 实战沉淀(19品类15.2万行,19/19对账0偏差)。
与既有工具关系: 本库=「POS原始导出→标准表」的权威入口;
  花厅坊POS清洗脚本_v0.1(dryrun/execute管道)与数据清洗匹配_v0.1(retail_clean字段硬化)
  处理的是「标准表→商品库」的下游环节,不重叠、不取代。

内置防坑(花厅坊实测七坑):
  ① 假xls检测(HTML/文本改后缀) — file magic 校验
  ② 非标OLE容器 — calamine引擎(xlrd会BOF报错)
  ③ 打印式报表(抬头/页脚/小计/合计混入) — 行级识别只取数据行
  ④ xls 65536行硬截断 — 触顶自动报警
  ⑤ 无表头行 — 列语义按位置映射+锚点数字校验
  ⑥ 逐表对账(自算净额 vs 系统合计行,偏差>0.5%报警)
  ⑦ 中文路径NFD/NFC — 全部走os.listdir真实字节

用法:
  python3 pos_clean.py probe   --src <目录>                      # 体检:格式/行数/表头/期间
  python3 pos_clean.py sales   --src <目录> --out <目录> [--prefix P] [--master-name N]
  python3 pos_clean.py archive --src <目录> --out <目录>          # 档案六件套→注册表csv

依赖: pandas, python-calamine
"""
import argparse, os, re, sys, csv
from pathlib import Path
import pandas as pd
from python_calamine import CalamineWorkbook

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pos_schema import (SALES_COLS, ARCH_STD, ARCH_ALT, DATE_ROW_RE, AGG_TABLE_RE,
                        EXCLUDE_BIGCLASS, SYS_TOTAL_COL, RECON_TOLERANCE_PCT)

DATE_ANY = re.compile(r"20\d{2}[-/.年]\d{1,2}([-/.月]\d{1,2})?")
XLS_LIMIT = 65536


def magic_ok(fp):
    """坑①: 真xls以OLE魔数 D0CF11E0 开头; HTML/CSV改后缀在此拦下"""
    with open(fp, "rb") as f:
        head = f.read(8)
    return head[:4] == b"\xd0\xcf\x11\xe0" or head[:2] == b"PK"  # PK=xlsx


def cmd_probe(a):
    files = sorted(f for f in os.listdir(a.src) if f.lower().endswith((".xls", ".xlsx")))
    print(f"{'文件':50s}{'格式':>5}{'行数':>8}{'截断':>4}  期间线索")
    for f in files:
        fp = os.path.join(a.src, f)
        if not magic_ok(fp):
            print(f"{f[:48]:50s}{'假xls⚠️':>5}")
            continue
        try:
            rows = CalamineWorkbook.from_path(fp).get_sheet_by_index(0).to_python()
        except Exception as e:
            print(f"{f[:48]:50s}{'ERR':>5}  {str(e)[:40]}")
            continue
        trunc = "🔴" if len(rows) >= XLS_LIMIT else ""
        period = ",".join(sorted({m.group() for r in rows[:8] for c in r
                                  for m in DATE_ANY.finditer(str(c))})[:2])
        print(f"{f[:48]:50s}{'ok':>5}{len(rows):8d}{trunc:>4}  {period}")


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


def cmd_sales(a):
    files = sorted(f for f in os.listdir(a.src) if f.startswith(a.prefix)
                   and f.endswith(".xls") and EXCLUDE_BIGCLASS not in f
                   and not AGG_TABLE_RE.search(f))
    if not files:
        sys.exit(f"src 下无匹配 --prefix '{a.prefix}' 的销售表")
    os.makedirs(a.out, exist_ok=True)
    mp = os.path.join(a.out, a.master_name)
    bad = []
    covered_cats = set()
    with open(mp, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["品类文件"] + list(SALES_COLS.values())[1:])
        for f in files:
            fp = os.path.join(a.src, f)
            if not magic_ok(fp):
                bad.append((f, "假xls")); continue
            cat = re.sub(rf"^{re.escape(a.prefix)}|汇总表\.xls$", "", f)
            covered_cats.add(cat)
            rows = CalamineWorkbook.from_path(fp).get_sheet_by_index(0).to_python()
            if len(rows) >= XLS_LIMIT:
                bad.append((f, f"疑似{XLS_LIMIT}行截断"))
            n, amt, sys_total = 0, 0.0, None
            for r in rows:
                cells = [str(x).strip() for x in r]
                if any("合计" in x for x in cells[:4]):
                    try:
                        sys_total = float(r[SYS_TOTAL_COL])
                    except (ValueError, TypeError, IndexError):
                        pass
                    continue
                if len(cells) > 9 and re.match(r"^\d+\.?\d*$", cells[0]) and DATE_ROW_RE.match(cells[9]):
                    w.writerow([cat] + [str(r[i]).strip() if i < len(r) else "" for i in list(SALES_COLS)[1:]])
                    n += 1
                    amt += float(r[13] or 0) - float(r[16] or 0)
            dev = None if not sys_total else (amt - sys_total) / sys_total * 100
            flag = "✓" if dev is not None and abs(dev) <= RECON_TOLERANCE_PCT else "⚠️"
            if flag == "⚠️":
                bad.append((f, f"对账偏差 {dev}%"))
            print(f"{flag} {cat}: {n}行 净额{amt:,.0f} 系统合计{sys_total or 0:,.0f}")
    print(f"master → {mp}")
    check_aggregate_diff(a.src, a.prefix, covered_cats)
    if bad:
        print("\n🔴 需人工处理:", file=sys.stderr)
        for f, why in bad:
            print(f"  {f}: {why}", file=sys.stderr)
        sys.exit(2)


def cmd_archive(a):
    rows_out = []
    for f in sorted(os.listdir(a.src)):
        if "档案" not in f or not f.endswith(".xls"):
            continue
        fp = os.path.join(a.src, f)
        if not magic_ok(fp):
            print(f"⚠️ 假xls跳过: {f}", file=sys.stderr); continue
        rows = CalamineWorkbook.from_path(fp).get_sheet_by_index(0).to_python()
        hi, cmap = None, None
        for i, r in enumerate(rows[:8]):
            j = "|".join(str(c) for c in r)
            if re.search(r"货号|条码", j) and re.search(r"品名", j):
                hi = i
                cmap = ARCH_ALT if str(r[1]).strip() in ("货号", "条码") else ARCH_STD
                break
        if hi is None:
            print(f"⚠️ 未识别表头跳过: {f}", file=sys.stderr); continue
        for r in rows[hi + 1:]:
            d = {v: (str(r[k]).strip() if k < len(r) else "") for k, v in cmap.items()}
            if d["货号"] and re.match(r"^\d", d["货号"]):
                d["来源文件"] = f
                rows_out.append(d)
    reg = pd.DataFrame(rows_out).drop_duplicates("货号", keep="first")
    reg["停购"] = reg.停购日期.str.len() > 4
    os.makedirs(a.out, exist_ok=True)
    op = os.path.join(a.out, "sku_registry.csv")
    reg.to_csv(op, index=False)
    print(f"档案: {len(rows_out)}行 → 去重{len(reg)} → 在册(未停购){int((~reg.停购).sum())} → {op}")
    if (~reg.停购).sum() / max(len(reg), 1) > 0.99:
        print("⚠️ 停购标记率<1%——字段疑似未维护,动销率分母将虚大", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("probe", "sales", "archive"):
        sp = sub.add_parser(name)
        sp.add_argument("--src", required=True)
        if name != "probe":
            sp.add_argument("--out", required=True)
        if name == "sales":
            sp.add_argument("--prefix", default="")
            sp.add_argument("--master-name", default="sales_master.csv")
    a = p.parse_args()
    {"probe": cmd_probe, "sales": cmd_sales, "archive": cmd_archive}[a.cmd](a)


if __name__ == "__main__":
    main()
