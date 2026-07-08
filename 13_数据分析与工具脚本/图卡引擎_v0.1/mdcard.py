#!/usr/bin/env python3
"""图卡引擎 v0.5 — 五层受众卡片体系 · Apple系极简设计语言

设计原则(六哥 2026-07-03 定调):
  信息传递漂亮 > 装饰漂亮。纯白底/近黑墨/单一品牌绿/大数字主角/留白分隔(几乎零线条)。
  咨询三纪律保留:标题即结论 / 眉题-标题-证据-来源四层 / 红色仅标行动点。

受众芯片(chip): 内部·六哥 / 店方·老板 / 店方·店长 / 店方·采购 / 店方·店员 / 公域 / DRAFT
布局(layout): standard=瓦片+表格 | hero=大数字营销卡(朋友圈/公众号/小红书)

用法: python3 mdcard.py --spec card.json --out card.png
spec: {layout?, kicker?, title, subtitle?, chip?, tiles?[{label,value,note,warn,good}],
       table?{header,rows,widths,warn_rows}, hero?{number,unit?,line}, punch?, note?, source?}
"""
import argparse, json, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ── Apple系设计令牌 ──
BG, INK, MUTE, LINE = "#ffffff", "#1d1d1f", "#86868b", "#ebebf0"
ACCENT, WARN = "#0a7d54", "#bf1d2c"
CHIP_BG, CHIP_INK = "#f5f5f7", "#1d1d1f"

# ── emoji/缺字形 → CJK 安全字符自动映射(防 PingFang 缺字形空框,免重渲) ──
EMOJI_SAFE = {
    "⭐": "★", "🌟": "★", "✨": "★",
    "✅": "√", "☑": "√", "✔": "√", "✔️": "√",
    "❌": "×", "✗": "×", "❎": "×",
    "🟢": "●", "🟩": "●", "🔴": "●", "🟥": "●", "🟡": "●", "🟨": "●", "⚪": "○",
    "⚠️": "！", "⚠": "！", "🚩": "▶", "📌": "·", "🎯": "◎", "⭐️": "★",
    "▪️": "▪", "◾": "▪", "➡️": "→", "⬆️": "↑", "⬇️": "↓", "🔺": "▲", "🔻": "▼",
    "①": "①", "🔑": "★",  # 保留圈码;钥匙→星
}


def _safe(s):
    """把 emoji/缺字形替换成 CJK 字体保证有的字符,防渲染空框。"""
    if not isinstance(s, str):
        return s
    for k, v in EMOJI_SAFE.items():
        if k in s:
            s = s.replace(k, v)
    # 兜底:删掉高位 emoji 区段(U+1F000+ / 杂项符号)残留
    return "".join(ch for ch in s if ord(ch) < 0x1F000)


def _sanitize(obj):
    """递归清洗 spec 内所有字符串。"""
    if isinstance(obj, str):
        return _safe(obj)
    if isinstance(obj, list):
        return [_sanitize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    return obj


def zh_font():
    for name in ("PingFang SC", "Hiragino Sans GB", "Heiti SC", "Arial Unicode MS"):
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
    k = math.ceil(len(t) / n)
    w = math.ceil(len(t) / k)  # 均衡行宽,杜绝孤字行
    return [t[i:i + w] for i in range(0, len(t), w)]


def _chip(ax, x, y, text):
    warn = text in ("DRAFT", "草案")
    ax.text(x, y, text, fontsize=10, color=("white" if warn else CHIP_INK),
            va="center", ha="right",
            bbox=dict(boxstyle="round,pad=0.38", facecolor=(WARN if warn else CHIP_BG),
                      edgecolor="none"))


def render(spec, out):
    spec = _sanitize(spec)  # emoji/缺字形自动替换,免因空框重渲
    plt.rcParams["font.family"] = zh_font()
    if spec.get("layout") == "hero":
        return render_hero(spec, out)
    tiles = spec.get("tiles", [])
    table = spec.get("table", {})
    rows = table.get("rows", [])
    tlines = _wrap(spec.get("title", ""), 24)
    ntr = (len(tiles) + 3) // 4 if tiles else 0
    plines = _wrap(spec.get("punch", ""), 40) if spec.get("punch") else []
    h = (1.35 + (0.34 if spec.get("kicker") else 0) + 0.68 * len(tlines)
         + (0.42 if spec.get("subtitle") else 0) + ntr * 2.05
         + (0.78 * (len(rows) + 1) + 0.6 if rows else 0)
         + (0.5 * len(plines) + 0.2 if plines else 0)
         + (0.34 if spec.get("note") else 0) + (0.5 if spec.get("source") else 0.15))
    fig = plt.figure(figsize=(10.8, h), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 10.8); ax.set_ylim(0, h)
    y = h - 0.62
    if spec.get("kicker"):
        ax.text(0.62, y, spec["kicker"], fontsize=11, color=ACCENT, va="center", fontweight="bold")
    if spec.get("chip"):
        _chip(ax, 10.18, y, spec["chip"])
    if spec.get("kicker") or spec.get("chip"):
        y -= 0.5
    for tl in tlines:  # 行动标题(结论句)
        ax.text(0.62, y, tl, fontsize=25.5, fontweight="bold", color=INK, va="center")
        y -= 0.68
    if spec.get("subtitle"):
        ax.text(0.62, y, spec["subtitle"], fontsize=11.5, color=MUTE, va="center")
        y -= 0.42
    # 瓦片区(无边框,留白分隔;数值默认墨色,红=行动点,绿=正向亮点)
    if tiles:
        y -= 0.28
        tw = 9.56 / 4
        for i, t in enumerate(tiles):
            r, c = divmod(i, 4)
            x0, y0 = 0.62 + c * tw, y - r * 2.05
            col = WARN if t.get("warn") else (ACCENT if t.get("good") else INK)
            ax.text(x0, y0, t.get("label", ""), fontsize=11.5, color=MUTE, va="top")
            ax.text(x0, y0 - 0.36, str(t.get("value", "")), fontsize=30, fontweight="bold",
                    color=col, va="top")
            if t.get("note"):
                ax.text(x0, y0 - 1.06, t["note"], fontsize=10, color=MUTE, va="top")
        y -= ntr * 2.05
    # 表格区(仅表头下一条发丝线,行间靠留白)
    if rows:
        header = table.get("header", [])
        ncol = max(len(header), max(len(r) for r in rows))
        widths = table.get("widths") or [1] * ncol
        tot = sum(widths)
        xs, acc = [], 0.62
        for wd in widths:
            xs.append(acc); acc += wd / tot * 9.56
        y -= 0.42
        for j, htxt in enumerate(header):
            ax.text(xs[j], y, str(htxt), fontsize=11.5, fontweight="bold", color=MUTE, va="center")
        y -= 0.2
        ax.plot([0.62, 10.18], [y, y], color=LINE, lw=0.8)
        warn_rows = set(table.get("warn_rows", []))
        for ri, r in enumerate(rows):
            y -= 0.74
            col = WARN if ri in warn_rows else INK
            for j, cell in enumerate(r):
                ax.text(xs[j], y, str(cell), fontsize=13, color=col, va="center",
                        fontweight="bold" if j == 0 else "normal")
    if plines:  # 收尾钩子(standard布局)
        y -= 0.5
        for tl in plines:
            ax.text(0.62, y, tl, fontsize=17, fontweight="bold", color=ACCENT, va="center")
            y -= 0.5
    if spec.get("note"):
        ax.text(0.62, 0.66, "注: " + spec["note"], fontsize=9.5, color=MUTE, va="center")
    if spec.get("source"):
        ax.text(0.62, 0.3, "资料来源: " + spec["source"], fontsize=9.5, color=MUTE, va="center")
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    print(f"✓ {out}")


def render_hero(spec, out):
    """营销卡: 大数字主角,一卡一钩子。竖幅1080×1350(朋友圈/小红书友好)"""
    fig = plt.figure(figsize=(10.8, 13.5), dpi=150)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1]); ax.axis("off"); ax.set_xlim(0, 10.8); ax.set_ylim(0, 13.5)
    if spec.get("kicker"):
        ax.text(0.9, 12.5, spec["kicker"], fontsize=12, color=ACCENT, fontweight="bold")
    if spec.get("chip"):
        _chip(ax, 9.9, 12.5, spec["chip"])
    hero = spec.get("hero", {})
    num, unit = str(hero.get("number", "")), hero.get("unit", "")
    ax.text(0.9, 8.6, num, fontsize=110, fontweight="bold", color=INK, va="center")
    if unit:
        ax.text(0.9 + len(num) * 0.98, 8.25, unit, fontsize=26, color=MUTE, va="center")
    y = 6.6
    for tl in _wrap(hero.get("line", ""), 15):
        ax.text(0.9, y, tl, fontsize=30, fontweight="bold", color=INK, va="center")
        y -= 0.95
    if spec.get("subtitle"):
        y -= 0.25
        for tl in _wrap(spec["subtitle"], 26):
            ax.text(0.9, y, tl, fontsize=14, color=MUTE, va="center")
            y -= 0.55
    if spec.get("punch"):  # 收尾钩子
        ax.text(0.9, 2.2, spec["punch"], fontsize=17, color=ACCENT, fontweight="bold")
    if spec.get("source"):
        ax.text(0.9, 0.85, spec["source"], fontsize=10, color=MUTE)
    fig.savefig(out, facecolor=BG)
    plt.close(fig)
    print(f"✓ {out}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--spec", required=True)
    p.add_argument("--out", required=True)
    a = p.parse_args()
    render(json.load(open(a.spec)), a.out)
