#!/usr/bin/env python3
"""图卡引擎 v0.7 — 五层受众卡片体系 · Apple系极简设计语言 + 卡组批量/客户路由/输出台账/品牌色参数化

设计原则(六哥 2026-07-03 定调,v0.6 视觉不变):
  信息传递漂亮 > 装饰漂亮。纯白底/近黑墨/单一品牌绿/大数字主角/留白分隔(几乎零线条)。
  咨询三纪律保留:标题即结论 / 眉题-标题-证据-来源四层 / 红色仅标行动点。

受众芯片(chip): 内部·六哥 / 店方·老板 / 店方·店长 / 店方·采购 / 店方·店员 / 公域 / DRAFT
布局(layout): standard=瓦片+表格 | hero=大数字营销卡(朋友圈/公众号/小红书)

v0.6 新增(2026-07-08 卡片生成模块审计·六哥签字·决策点3):
  1. --spec-set specset.json --basename <名称> [--out-dir <目录>]
     specset.json = {"L0": {...spec...}, "L1": {...}, "L2": {...}}
     每层出一张 <out-dir>/<basename>_L{n}.png,受众后缀自动加,一份诊断一次出多受众卡组
  2. --client <客户名>
     若不给 --out-dir,自动路由到 09_门店案例与项目复盘/{client}/(需已存在,不自动建目录)
  3. 每次成功渲染(单卡--spec/--out 或卡组--spec-set)都追加一行到
     图卡引擎_v0.1/output_ledger.csv:时间戳,spec路径,输出路径,chip(受众)
     (对齐 report-export 的台账格式,补 mdcard 此前零审计记录的缺口)

v0.7 新增(2026-07-11 P0-2待裁小项·mdcard品牌色参数化):
  --brand brand.json  颜色覆盖(键: bg/ink/mute/line/accent/warn/chip_bg/chip_ink),
                       缺的键落回默认色(六哥品牌绿),不传则行为与 v0.6 完全一致。

用法:
  python3 mdcard.py --spec card.json --out card.png                              # 单卡(原有)
  python3 mdcard.py --spec-set specset.json --basename <名称> --client <客户名>   # 卡组(新)
  python3 mdcard.py --spec card.json --out card.png --brand brand.json           # 自定义品牌色(新)
"""
import argparse, csv, datetime, json, math, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager

# ── Apple系设计令牌(默认色·六哥品牌绿)── 可用 --brand 传 json 覆盖,未传则用此默认值 ──
DEFAULT_COLORS = {
    "bg": "#ffffff", "ink": "#1d1d1f", "mute": "#86868b", "line": "#ebebf0",
    "accent": "#0a7d54", "warn": "#bf1d2c",
    "chip_bg": "#f5f5f7", "chip_ink": "#1d1d1f",
}
BG, INK, MUTE, LINE = (DEFAULT_COLORS["bg"], DEFAULT_COLORS["ink"],
                       DEFAULT_COLORS["mute"], DEFAULT_COLORS["line"])
ACCENT, WARN = DEFAULT_COLORS["accent"], DEFAULT_COLORS["warn"]
CHIP_BG, CHIP_INK = DEFAULT_COLORS["chip_bg"], DEFAULT_COLORS["chip_ink"]


def _load_brand(path):
    """读 --brand json,只认 DEFAULT_COLORS 里已有的键,缺的键落回默认色,多余/拼错的键报错。"""
    overrides = json.load(open(path, encoding="utf-8"))
    unknown = set(overrides) - set(DEFAULT_COLORS)
    if unknown:
        sys.stderr.write(f"✗ --brand 含未知色键 {sorted(unknown)},合法键: {sorted(DEFAULT_COLORS)}\n")
        sys.exit(1)
    return {**DEFAULT_COLORS, **overrides}


def _apply_brand(colors):
    global BG, INK, MUTE, LINE, ACCENT, WARN, CHIP_BG, CHIP_INK
    BG, INK, MUTE, LINE = colors["bg"], colors["ink"], colors["mute"], colors["line"]
    ACCENT, WARN = colors["accent"], colors["warn"]
    CHIP_BG, CHIP_INK = colors["chip_bg"], colors["chip_ink"]

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

# ── v0.6 新增:客户目录路由根 + 输出台账路径 ──
VAULT_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
CLIENT_ROOT = os.path.join(VAULT_ROOT, "09_门店案例与项目复盘")
LEDGER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_ledger.csv")


def _safe(s):
    """把 emoji/缺字形替换成 CJK 字体保证有的字符,防渲染空框。"""
    if not isinstance(s, str):
        return s
    for k, v in EMOJI_SAFE.items():
        if k in s:
            s = s.replace(k, v)
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


# ── v0.6 新增:输出台账(治「零审计台账」问题) ──
def _log_ledger(spec_path, out_path, chip):
    is_new = not os.path.exists(LEDGER_PATH)
    with open(LEDGER_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if is_new:
            w.writerow(["timestamp", "spec_path", "output_path", "chip"])
        w.writerow([datetime.datetime.now().isoformat(timespec="seconds"),
                    spec_path or "(inline)", out_path, chip or ""])


# ── v0.6 新增:客户路由(--client) ──
def _resolve_client_dir(client):
    hits = [d for d in os.listdir(CLIENT_ROOT)
            if os.path.isdir(os.path.join(CLIENT_ROOT, d)) and client in d]
    if not hits:
        sys.stderr.write(f"✗ --client '{client}' 在 {CLIENT_ROOT} 下找不到匹配目录,不自动建目录。"
                          f"请先手动确认客户目录名,或直接用 --out-dir 指定落点。\n")
        sys.exit(1)
    if len(hits) > 1:
        sys.stderr.write(f"✗ --client '{client}' 匹配到多个目录: {hits},请用更精确的名字或改用 --out-dir。\n")
        sys.exit(1)
    return os.path.join(CLIENT_ROOT, hits[0])


# ── v0.6 新增:卡组模式(--spec-set) ──
def render_spec_set(specset_path, basename, out_dir):
    specs = json.load(open(specset_path, encoding="utf-8"))
    if not isinstance(specs, dict):
        sys.stderr.write("✗ --spec-set 文件须是 {\"L0\": {...}, \"L1\": {...}} 形式的字典。\n")
        sys.exit(1)
    os.makedirs(out_dir, exist_ok=True)
    for layer, spec in specs.items():
        out_path = os.path.join(out_dir, f"{basename}_{layer}.png")
        render(spec, out_path)
        _log_ledger(specset_path, out_path, spec.get("chip", layer))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--spec", help="单卡模式:spec json 路径")
    p.add_argument("--out", help="单卡模式:输出 png 路径")
    p.add_argument("--spec-set", help="卡组模式:{L0:{...},L1:{...}} 字典 json 路径")
    p.add_argument("--basename", help="卡组模式:输出文件名前缀(会自动加 _L{n}.png)")
    p.add_argument("--out-dir", help="卡组模式:输出目录(不给则用 --client 路由)")
    p.add_argument("--client", help="卡组模式:客户名,自动路由到 09_门店案例与项目复盘/{client}/(需已存在)")
    p.add_argument("--brand", help="品牌色覆盖:json 路径,键=bg/ink/mute/line/accent/warn/chip_bg/chip_ink,"
                                    "缺的键落回默认(六哥品牌绿)。不传则用默认色,行为不变。")
    a = p.parse_args()

    if a.brand:
        _apply_brand(_load_brand(a.brand))

    if a.spec_set:
        if not a.basename:
            sys.stderr.write("✗ --spec-set 模式必须给 --basename。\n"); sys.exit(1)
        out_dir = a.out_dir or (_resolve_client_dir(a.client) if a.client else None)
        if not out_dir:
            sys.stderr.write("✗ --spec-set 模式必须给 --out-dir 或 --client 之一。\n"); sys.exit(1)
        render_spec_set(a.spec_set, a.basename, out_dir)
    elif a.spec and a.out:
        spec = json.load(open(a.spec, encoding="utf-8"))
        render(spec, a.out)
        _log_ledger(a.spec, a.out, spec.get("chip", ""))
    else:
        sys.stderr.write("✗ 用 --spec/--out(单卡) 或 --spec-set/--basename/--client|--out-dir(卡组)。\n")
        sys.exit(1)
