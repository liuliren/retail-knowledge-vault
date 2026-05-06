"""
数据预处理：模式识别 + 元信息剥离 + 条码归一化 + 期间解析。
"""
import re
from typing import Optional, Tuple, List
from config import METADATA_KEYWORDS, SCALE_PREFIX


def detect_pattern(rows: list) -> str:
    """
    识别表头模式，返回 A/B/C/D/E/UNKNOWN/EMPTY。

    A: 行 0 全空，行 1 含「商品销售条码分组统计」（27 列原表）
    B: 行 0 含「打印时间」+ 行 2 是字段头（15 列）
    C: 行 0 直接是字段头（10 列），含「行号」「条码」
    D: 行 0 = 字段头，含「品牌」「主供应商」（21 列）
    E: 行 0 含「L1」（已含品类层级，4 月日均表 19 列）
    """
    if not rows:
        return "EMPTY"

    def to_str(c):
        return str(c).strip() if c is not None else ""

    row0 = [to_str(c) for c in rows[0]]
    row0_text = " ".join(row0)

    # 模式 E：含 L1
    if "L1" in row0:
        return "E"

    # 模式 C：行 0 直接含字段头关键字
    if "行号" in row0 and "条码" in row0:
        return "C"

    # 模式 D：行 0 含品牌 + 主供应商
    if "品牌" in row0 and "主供应商" in row0:
        return "D"

    # 模式 A：行 0 全空，行 1 含报表名
    if all(c == "" for c in row0) and len(rows) > 1:
        row1_text = " ".join(to_str(c) for c in rows[1])
        if "商品销售条码分组统计" in row1_text:
            return "A"

    # 模式 B：行 0 含打印时间
    if "打印时间" in row0_text:
        return "B"

    return "UNKNOWN"


def find_header_row(rows: list, max_scan: int = 10) -> int:
    """
    在前 max_scan 行内寻找真实字段头行号。
    判定：行内同时含「行号」「条码」或「条码」「品名」「销售数量」中至少 3 项。
    """
    target_keywords = {"行号", "条码", "商品条码", "品名", "商品名称", "销售数量",
                       "数量小计", "金额小计", "进价"}
    for i, row in enumerate(rows[:max_scan]):
        cells = [str(c).strip() if c is not None else "" for c in row]
        hits = sum(1 for kw in target_keywords if kw in cells)
        if hits >= 3:
            return i
    return -1  # 未找到


def strip_print_metadata(rows: list, pattern: str) -> Tuple[list, int]:
    """
    剥离前 N 行打印元信息，返回（数据行列表，跳过的行数）。
    数据行第一行是字段头，后续是数据。
    """
    if pattern in ("C", "D", "E"):
        # 字段头在行 0
        return rows, 0

    if pattern in ("A", "B", "UNKNOWN"):
        # 模式 A/B/UNKNOWN：动态查找字段头行
        header_idx = find_header_row(rows)
        if header_idx >= 0:
            return rows[header_idx:], header_idx
        return rows, 0  # 找不到就保持原样

    return rows, 0


def parse_period(rows: list, max_scan: int = 6) -> Tuple[Optional[str], Optional[str]]:
    """
    从打印元信息中解析期间起止日期。
    例: "日期：2026-03-01 到 2026-04-30"
    """
    pattern = re.compile(r"日期[：:]\s*(\d{4}-\d{2}-\d{2})\s*到\s*(\d{4}-\d{2}-\d{2})")
    for row in rows[:max_scan]:
        for c in row:
            text = str(c) if c is not None else ""
            m = pattern.search(text)
            if m:
                return m.group(1), m.group(2)
    return None, None


def parse_print_date(rows: list, max_scan: int = 6) -> Optional[str]:
    """从打印元信息中解析打印日期（作库存快照日期使用）。"""
    pattern = re.compile(r"打印时间[：:]\s*(\d{4}/\d{1,2}/\d{1,2})")
    for row in rows[:max_scan]:
        for c in row:
            text = str(c) if c is not None else ""
            m = pattern.search(text)
            if m:
                # 标准化为 YYYY-MM-DD
                parts = m.group(1).split("/")
                return f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"
    return None


def normalize_barcode(raw: any, goods_no: any) -> Tuple[str, str]:
    """
    归一化条码 + 条码源类型分类。
    返回（标准化条码, 类型）。
    类型: EAN-13 / EAN-14 / 短货号 / 散称代理 / 无效

    v0.1.2 修复: 模式 D 货号误标散称
    新增逻辑: raw 缺失时优先用 goods_no 判断（13/14 位 EAN / 4-12 位短货号），
             仅当 goods_no 含非数字时才标"散称代理"。
    """
    raw_s = str(raw).strip() if raw is not None else ""
    # 移除可能的 .0 后缀（xlrd 数字转字符串）
    if raw_s.endswith(".0"):
        raw_s = raw_s[:-2]

    goods_s = str(goods_no).strip() if goods_no is not None else ""
    if goods_s.endswith(".0"):
        goods_s = goods_s[:-2]

    # === v0.1.2 修复: 选择有效候选条码 ===
    raw_valid = bool(raw_s) and len(raw_s) >= 4 and raw_s not in ("0", "01", "00")

    if raw_valid:
        # raw_barcode 有效 — 按 v0.1 原逻辑（不变）
        if raw_s.isdigit():
            if len(raw_s) == 13:
                return raw_s, "EAN-13"
            if len(raw_s) == 14:
                return raw_s, "EAN-14"
            if len(raw_s) <= 8:
                return raw_s, "短货号"
        return raw_s, "其他"

    # === v0.1.2 修复: raw 缺失/无效, 退到 goods_no ===
    if not goods_s:
        return "", "无效"

    if goods_s.isdigit():
        # 模式 D 货号 — 13/14 位 EAN（修复关键）
        if len(goods_s) == 13:
            return goods_s, "EAN-13"
        if len(goods_s) == 14:
            return goods_s, "EAN-14"
        # 4-12 位 numeric → 短货号（不再误标散称）
        if 4 <= len(goods_s) <= 12:
            return goods_s, "短货号"
        # 长度 < 4 异常
        return "", "无效"

    # goods_no 含非数字 → 真散称代理键（极少数业态：含字母前缀的内部编码）
    if len(goods_s) >= 4:
        return f"{SCALE_PREFIX}{goods_s}", "散称代理"
    return "", "无效"


def safe_float(val: any) -> Optional[float]:
    """安全转 float。失败返回 None。"""
    if val is None or val == "":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def safe_str(val: any) -> str:
    """安全转字符串。"""
    if val is None:
        return ""
    s = str(val).strip()
    if s.endswith(".0"):
        try:
            f = float(s)
            if f.is_integer():
                return str(int(f))
        except ValueError:
            pass
    return s


# === v0.1.1 新增：散称大类推断 ===
SCALE_CATEGORY_KEYWORDS = {
    "生鲜":     ["水果", "蔬菜", "肉", "水产", "鸡", "鱼", "蛋"],
    "熟食":     ["熟食", "卤味", "烧腊", "凉菜"],
    "烘焙":     ["烘焙", "面包", "蛋糕", "糕点"],
    "散称零食": ["糖", "果干", "坚果", "炒货", "蜜饯", "凉果", "梅"],
}


def infer_scale_category(record: dict) -> str:
    """
    v0.1.1 新增: 推断散称商品大类。
    优先级: ERP 类别名称 → 商品名称关键词 → 散称-未识别
    """
    erp = str(record.get("ERP类别名称", "") or "")
    name = str(record.get("商品名称", "") or "")
    for cat, keywords in SCALE_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in erp:
                return cat
    for cat, keywords in SCALE_CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in name:
                return cat
    return "散称-未识别"


def is_field_in_source(header_row: list, candidates: list) -> bool:
    """
    v0.1.1 新增: 判断字段是否在源表 header 中存在。
    用于区分'字段不可用'(源表无该列) vs '字段缺值'(列存在但值空)。
    """
    if not header_row:
        return False
    header_str = [str(c).strip() if c is not None else "" for c in header_row]
    return any(c in header_str for c in candidates)
