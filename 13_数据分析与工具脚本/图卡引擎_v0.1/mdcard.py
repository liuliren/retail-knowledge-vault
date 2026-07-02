#!/usr/bin/env python3
"""图卡引擎 v0.1 — md 交付件的配套 PNG 卡片(微信直发友好)

JSON spec → 1080px宽 PNG。设计原则:大字号、指标瓦片+表格两段式、零图表垃圾。
用法: python3 mdcard.py --spec card.json --out card.png
spec 结构:
{
  "title": "标题", "subtitle": "副标题(期间/口径)",
  "tiles": [{"label": "指标名", "value": "57.5%", "note": "补充", "warn": true}],
  "table": {"header": ["列1","列2"], "rows": [["a","b"]], "warn_rows": [0]},
  "footer": "落款/口径说明"
}
依赖: matplotlib (中文字体自动探测 PingFang/Hiragino/Heiti)
"""
import argparse, json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

INK, MUTE, WARN, ACCENT, BG, LINE = "#1a1a1a", "#666666", "#c0392b", "#0f6f4f", "#fbfaf7", "#e5e0d8"


def zh_font():
    for name in ("PingFang SC", "Hiragino Sans GB", "Heiti SC", "STHeiti", "Arial Unicode MS"):
        try:
            font_manager.findfont(name, fallback_to_default=False)
            return name
        except Exception:
            continue
    return "sans-serif"


def _wrap(t, n):
    t = str(t)
    if len(t) <= n:
        return [t]
    import math
    k = math.ceil(len(t) / n)          # 行数
    w = math.ceil(len(t) / k)          # 均衡每行宽度,杜绝孤字行
    return [t[i:i+w] for i in range(0, len(t), w)]


def render(spec, out):
    plt.rcParams["font.family"] = zh_font()
    tiles = spec.get("tiles", [])
    table = spec.get("table", {})
    rows = table.get("rows", [])
    n_tile_rows = (len(tiles) + 3) // 4 if tiles else 0
    tlines = _wrap(spec.get("title", ""), 24)  # 行动标题支持折行(咨询式=一句结论)
    h = (1.15 + (0.3 if spec.get("kicker") else 0) + 0.55*len(tlines)
         + n_tile_rows * 1.5 + (0.62 * (len(rows) + 1) + 0.5 if rows else 0)
         + (0.55 if spec.get("source") or spec.get("footer") else 0.2) + (0.3 if spec.get("note") else 0))
    fig = plt.figure(figsize=(10.8, h), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 10.8); ax.set_ylim(0, h)
    y = h - 0.5
    if spec.get("kicker"):  # 眉题:项目线·小号加宽
        ax.text(0.55, y, spec["kicker"], fontsize=10, color=ACCENT, va="center", fontweight="bold")
        y -= 0.42
    if spec.get("badge"):
        bcol = WARN if spec["badge"] in ("DRAFT", "草案") else MUTE
        ax.text(10.25, h - 0.5, spec["badge"], fontsize=10.5, color="white", va="center", ha="right",
                bbox=dict(boxstyle="round,pad=0.35", facecolor=bcol, edgecolor="none"))
    for i, tl in enumerate(tlines):  # 行动标题(结论句)可折行
        ax.text(0.55, y, tl, fontsize=20, fontweight="bold", color=INK, va="center")
        y -= 0.55
    y += 0.13
    if spec.get("subtitle"):
        y -= 0.4
        ax.text(0.55, y, spec["subtitle"], fontsize=11, color=MUTE, va="center")
    y -= 0.35
    ax.plot([0.55, 10.25], [y, y], color=LINE, lw=1.2)
    # 指标瓦片(每行4个)
    if tiles:
        tw = 9.7 / 4
        for i, t in enumerate(tiles):
            r, c = divmod(i, 4)
            x0, y0 = 0.55 + c * tw, y - 0.42 - r * 1.5
            col = WARN if t.get("warn") else (ACCENT if t.get("good") else INK)  # 咨询式克制:默认墨色
            ax.text(x0, y0, t.get("label", ""), fontsize=10.5, color=MUTE, va="top")
            ax.text(x0, y0 - 0.34, str(t.get("value", "")), fontsize=19, fontweight="bold", color=col, va="top")
            if t.get("note"):
                ax.text(x0, y0 - 0.82, t["note"], fontsize=9, color=MUTE, va="top")
        y -= 0.42 + n_tile_rows * 1.5
    # 表格
    if rows:
        header = table.get("header", [])
        ncol = max(len(header), max(len(r) for r in rows))
        widths = table.get("widths") or [1] * ncol
        total_w = sum(widths)
        xs, acc = [], 0.55
        for wd in widths:
            xs.append(acc); acc += wd / total_w * 9.7
        y -= 0.5
        for j, htxt in enumerate(header):
            ax.text(xs[j], y, str(htxt), fontsize=11, fontweight="bold", color=MUTE, va="center")
        y -= 0.18
        ax.plot([0.55, 10.25], [y, y], color=LINE, lw=1)
        warn_rows = set(table.get("warn_rows", []))
        for ri, r in enumerate(rows):
            y -= 0.58
            col = WARN if ri in warn_rows else INK
            for j, cell in enumerate(r):
                fw = "bold" if j == 0 else "normal"
                ax.text(xs[j], y, str(cell), fontsize=11.5, color=col, va="center", fontweight=fw)
    yb = 0.32
    if spec.get("note"):
        ax.text(0.55, yb + 0.3, "注: " + spec["note"], fontsize=8.5, color=MUTE, va="center")
    src = spec.get("source") or spec.get("footer")
    if src:
        pre = "" if spec.get("footer") and not spec.get("source") else "资料来源: "
        ax.text(0.55, yb, pre + src, fontsize=8.5, color=MUTE, va="center")
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    print(f"✓ {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--spec", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    render(json.load(open(a.spec)), a.out)
