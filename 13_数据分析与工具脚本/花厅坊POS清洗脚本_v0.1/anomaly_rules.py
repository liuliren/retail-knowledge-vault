"""
17 类异常检测规则。
分类：阻断 (P0) / 标记 (P1) / 不阻断 (P2)
"""
from typing import List, Dict


def make_anomaly(record: dict, anomaly_type: str, severity: str,
                 action: str, field: str = "", value=None,
                 suggestion: str = "") -> dict:
    """构造异常记录。"""
    return {
        "异常类型": anomaly_type,
        "严重等级": severity,
        "处理动作": action,
        "商品条码": record.get("商品条码", ""),
        "货号": record.get("货号", ""),
        "品名": record.get("商品名称", ""),
        "异常字段": field,
        "异常值": value,
        "处理建议": suggestion,
        "数据来源文件": record.get("数据来源文件", ""),
    }


def detect_anomalies(records: List[dict]) -> Dict[str, list]:
    """
    遍历所有记录，按 17 类异常分类输出。
    返回 {阻断, 标记, 不阻断, 统计摘要}。
    """
    blocking = []
    marking = []
    info = []

    for r in records:
        # 类 1: 无条码（无效）
        if r.get("条码源类型") == "无效":
            blocking.append(make_anomaly(r, "无条码", "P0", "阻断",
                                          "商品条码", r.get("商品条码"),
                                          "条码与货号均缺失，不进主表"))
            continue  # 阻断后不再检查其他异常

        # 类 2: 商品名异常
        name = r.get("商品名称", "")
        if not name or name in ("0", "0.0"):
            blocking.append(make_anomaly(r, "商品名异常", "P0", "阻断",
                                          "商品名称", name, "品名缺失或为占位值"))
            continue

        # 类 4: 散称代理键标记
        if r.get("条码源类型") == "散称代理":
            marking.append(make_anomaly(r, "散称代理键", "P2", "标记",
                                         "商品条码", r.get("商品条码"),
                                         "散称商品已用「散称_+货号」代理键"))

        # 类 5: 负库存
        inv = r.get("库存即时快照")
        if inv is not None and inv < 0:
            marking.append(make_anomaly(r, "负库存", "P0", "标记",
                                         "库存即时快照", inv,
                                         "进售退多于实际入库，需门店复核"))

        # 类 6: 进价为 0
        cost = r.get("进价")
        if cost is not None and cost == 0:
            marking.append(make_anomaly(r, "进价为0_毛利不可算", "P0", "标记",
                                         "进价", cost, "毛利字段填 NULL，需补进价"))

        # 类 7: 退货金额非零
        ret_amt = r.get("退货金额")
        if ret_amt is not None and ret_amt != 0:
            marking.append(make_anomaly(r, "退货金额非零", "P1", "标记",
                                         "退货金额", ret_amt,
                                         "确认是否正常退货行为"))

        # 类 8: L4 缺失
        if not r.get("L4"):
            marking.append(make_anomaly(r, "L4缺失", "P1", "标记",
                                         "L4", "", "需补录或人工映射"))

        # 类 9: L3 缺失
        if not r.get("L3"):
            marking.append(make_anomaly(r, "L3缺失", "P1", "标记",
                                         "L3", "", "需补录"))

        # 类 10/11: 品牌/规格 (v0.1.1 调整)
        # 区分'字段不可用'(源表无该列, 静默跳过, 不污染异常清单)
        # vs 'cross-source 仍空'(标 P2 信息层, 不影响通过率)
        brand_available = r.get("_brand_field_available", True)
        spec_available = r.get("_spec_field_available", True)

        if not r.get("品牌"):
            if brand_available:
                info.append(make_anomaly(r, "品牌待补", "P2", "信息",
                                          "品牌", "",
                                          "字段在源表存在但值缺失，待补录"))
            # else: 字段不可用，静默跳过

        if not r.get("规格"):
            if spec_available:
                info.append(make_anomaly(r, "规格待补", "P2", "信息",
                                          "规格", "",
                                          "字段在源表存在但值缺失，待补录"))
            # else: 字段不可用，静默跳过

        # 类 12: ERP 类别缺失（不阻断）
        if not r.get("ERP类别名称"):
            info.append(make_anomaly(r, "ERP类别缺失", "P2", "不阻断",
                                      "ERP类别名称", "", "正常情况"))

        # 类 16: 金额小计 vs 销售金额原值差异
        amt_main = r.get("销售金额")
        amt_orig = r.get("销售金额原值")
        if amt_main is not None and amt_orig is not None:
            if abs(amt_main - amt_orig) > 0.01:
                marking.append(make_anomaly(r, "金额双口径差异", "P1", "标记",
                                             "金额小计_vs_销售金额", f"{amt_main}/{amt_orig}",
                                             "退货导致差异，已保留双值"))

        # 类 17: 数量小计 vs 销售数量原值差异
        qty_main = r.get("销售数量")
        qty_orig = r.get("销售数量原值")
        if qty_main is not None and qty_orig is not None:
            if abs(qty_main - qty_orig) > 0.001:
                marking.append(make_anomaly(r, "数量双口径差异", "P1", "标记",
                                             "数量小计_vs_销售数量", f"{qty_main}/{qty_orig}",
                                             "退货导致差异，已保留双值"))

    summary = summarize_anomalies(blocking, marking, info, len(records))
    return {
        "阻断": blocking,
        "标记": marking,
        "不阻断": info,
        "统计": summary,
    }


def summarize_anomalies(blocking: list, marking: list, info: list, total: int) -> dict:
    """汇总异常分布。"""
    if total == 0:
        return {"total_records": 0}

    # 按类型分桶
    blocking_by_type = {}
    marking_by_type = {}
    for a in blocking:
        t = a["异常类型"]
        blocking_by_type[t] = blocking_by_type.get(t, 0) + 1
    for a in marking:
        t = a["异常类型"]
        marking_by_type[t] = marking_by_type.get(t, 0) + 1

    # 唯一阻断行数（去重，因为类 1+2 已 continue）
    blocking_records = len(blocking)

    return {
        "total_records": total,
        "blocking_count": blocking_records,
        "blocking_ratio": round(blocking_records / total, 4),
        "marking_count": len(marking),
        "marking_ratio": round(len(marking) / total, 4),
        "info_count": len(info),
        "info_ratio": round(len(info) / total, 4),
        "blocking_by_type": blocking_by_type,
        "marking_by_type": marking_by_type,
    }


def evaluate_gate(summary: dict, thresholds: dict) -> str:
    """
    异常率守门：
    - < blocking_pass (5%) → "PASS"
    - < blocking_warn (15%) → "WARN"
    - 否则 → "BLOCK"
    """
    ratio = summary.get("blocking_ratio", 0)
    if ratio < thresholds["blocking_pass"]:
        return "PASS"
    elif ratio < thresholds["blocking_warn"]:
        return "WARN"
    else:
        return "BLOCK"
