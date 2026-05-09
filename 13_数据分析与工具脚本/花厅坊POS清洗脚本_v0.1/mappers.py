"""
字段映射层：将各模式数据映射为标准 schema。
"""
from typing import Optional, Tuple, List, Dict
from config import SALES_FIELD_MAP, ARCHIVE_FIELD_MAP
from normalizers import (normalize_barcode, safe_float, safe_str,
                          is_field_in_source, infer_scale_category)


def build_field_index(header_row: list, field_map: dict) -> Dict[str, int]:
    """
    根据字段头行构建标准字段名 -> 列索引映射。
    一个标准字段对应多个候选原字段时，取第一个命中的列。
    """
    header = [safe_str(c) for c in header_row]
    index = {}
    for std_field, candidates in field_map.items():
        for cand in candidates:
            if cand in header:
                index[std_field] = header.index(cand)
                break
    return index


def map_sales_record(row: list, field_index: dict, source_file_id: str,
                     period_start: Optional[str], period_end: Optional[str],
                     snapshot_date: Optional[str],
                     header_row: Optional[list] = None) -> Optional[dict]:
    """
    将一行原始数据映射为标准销售记录。
    返回 None 表示该行应跳过（合计行 / 空行）。
    v0.1.1 新增 header_row: 用于判定字段在源表中是否存在(品牌/规格异常分级)。
    """
    def get(field: str):
        idx = field_index.get(field)
        if idx is None or idx >= len(row):
            return None
        return row[idx]

    # 跳过空行
    raw_barcode = get("商品条码")
    raw_goods_no = get("货号")
    raw_name = get("商品名称")
    if raw_barcode is None and raw_goods_no is None and raw_name is None:
        return None

    # 跳过合计行（行号为空 + 品名含「合计」/「总计」）
    name_str = safe_str(raw_name)
    if "合计" in name_str or "总计" in name_str:
        return None

    barcode, barcode_type = normalize_barcode(raw_barcode, raw_goods_no)

    sales_qty_main = safe_float(get("销售数量"))      # 数量小计
    sales_qty_orig = safe_float(get("销售数量原值"))  # 销售数量
    sales_amt_main = safe_float(get("销售金额"))      # 金额小计
    sales_amt_orig = safe_float(get("销售金额原值"))  # 销售金额
    cost = safe_float(get("进价"))
    inventory = safe_float(get("库存即时快照"))

    # 毛利计算
    gross_profit = None
    gross_rate = None
    if sales_amt_main is not None and sales_qty_main is not None and cost is not None and cost > 0:
        gross_profit = round(sales_amt_main - sales_qty_main * cost, 2)
        if sales_amt_main != 0:
            gross_rate = round(gross_profit / sales_amt_main, 4)

    return {
        "商品条码": barcode,
        "货号": safe_str(raw_goods_no),
        "条码源类型": barcode_type,
        "商品名称": name_str,
        "品牌": safe_str(get("品牌")),
        "规格": safe_str(get("规格")),
        "单位": safe_str(get("单位")),
        "统计期间起": period_start,
        "统计期间止": period_end,
        "销售数量": sales_qty_main,
        "销售数量原值": sales_qty_orig,
        "销售金额": sales_amt_main,
        "销售金额原值": sales_amt_orig,
        "零售价": safe_float(get("零售价")),
        "进价": cost,
        "退货数量": safe_float(get("退货数量")),
        "退货金额": safe_float(get("退货金额")),
        "毛利额": gross_profit,
        "毛利率": gross_rate,
        "库存即时快照": inventory,
        "库存快照日期": snapshot_date,
        "ERP类别编码": safe_str(get("ERP类别编码")),
        "ERP类别名称": safe_str(get("ERP类别名称")),
        "主供应商": safe_str(get("主供应商")),
        # L1-L4 + 商品角色等待匹配层填充
        "L1": "",
        "L2": "",
        "L3": "",
        "L4": "",
        "商品角色": "",
        "价格带": "",
        "场景标签": "",
        "顾客标签": "",
        "匹配状态": "",
        "匹配置信度": None,
        "匹配依据": "",
        "匹配来源": "",
        "数据来源文件": source_file_id,
        "备注": "",
        # v0.1.1: 字段可用性标志(用于异常分级,不出现在最终输出)
        "_brand_field_available": is_field_in_source(header_row, ["品牌"]),
        "_spec_field_available": is_field_in_source(header_row, ["规格"]),
    }


def apply_baseline_match(records: List[dict], baseline: dict) -> Tuple[int, int]:
    """
    用 4077 行基础匹配层吸入 L1-L4 + 商品角色等。
    返回（命中数, 未命中数）。
    """
    hit, miss = 0, 0
    for r in records:
        bc = r["商品条码"]
        if bc in baseline:
            b = baseline[bc]
            r["L1"] = b.get("L1", "")
            r["L2"] = b.get("L2", "")
            r["L3"] = b.get("L3", "")
            r["L4"] = b.get("L4", "")
            r["商品角色"] = b.get("商品角色", "")
            r["价格带"] = b.get("价格带", "")
            r["场景标签"] = b.get("场景标签", "")
            r["顾客标签"] = b.get("顾客标签", "")
            r["匹配状态"] = b.get("匹配状态", "")
            r["匹配置信度"] = b.get("匹配置信度")
            r["匹配依据"] = b.get("匹配依据", "")
            r["匹配来源"] = "基础匹配层(M01)"
            hit += 1
        else:
            r["匹配状态"] = "未匹配-需人工确认"
            r["匹配来源"] = "未匹配"
            miss += 1
    return hit, miss


def apply_erp_category_match(records: List[dict],
                              erp_map: dict,
                              confidence: float = 0.65) -> Tuple[int, int]:
    """
    v0.1.1 新增: 对未匹配的 SKU, 用 ERP 类别名称兜底推断 L1-L2.
    仅当记录的 L1 仍为空时生效; 已匹配 M01 的不覆盖.
    L3/L4 保持空, 待 4 级匹配补全.
    置信度 0.65 < M01 的 0.95.
    返回 (兜底命中数, 仍未命中数).
    """
    hit = 0
    miss = 0
    for r in records:
        if r.get("L1"):
            continue  # 已被 M01 命中, 不覆盖
        erp_name = r.get("ERP类别名称", "")
        if not erp_name:
            miss += 1
            continue
        mapped = erp_map.get(erp_name)
        if mapped is None or not isinstance(mapped, tuple):
            miss += 1
            continue
        l1, l2 = mapped
        r["L1"] = l1
        r["L2"] = l2
        # L3/L4 保持空 — 不强行推断
        r["匹配状态"] = "ERP类别推断-中"
        r["匹配置信度"] = confidence
        r["匹配依据"] = f"ERP类别={erp_name} → {l1}/{l2}"
        r["匹配来源"] = "ERP类别字典(v0.1.1)"
        hit += 1
    return hit, miss


def build_baseline_dict(m01_data: dict) -> dict:
    """
    从 4077 行过程表「01_单品匹配明细」sheet 构建基础匹配字典。
    主键：商品条码。
    """
    sheet_data = m01_data.get("01_单品匹配明细")
    if sheet_data is None:
        return {}
    rows = sheet_data["rows"]
    if not rows:
        return {}

    header = [safe_str(c) for c in rows[0]]

    def col(name):
        return header.index(name) if name in header else -1

    cols = {
        "条码": col("商品条码"),
        "L1": col("L1主类"),
        "L2": col("L2大类"),
        "L3": col("L3小类"),
        "L4": col("L4细类"),
        "商品角色": col("商品角色"),
        "价格带": col("价格带"),
        "场景标签": col("场景标签"),
        "顾客标签": col("顾客标签"),
        "匹配状态": col("匹配状态"),
        "匹配置信度": col("匹配置信度"),
        "匹配依据": col("匹配依据"),
    }

    baseline = {}
    for row in rows[1:]:
        if len(row) <= cols["条码"] or cols["条码"] < 0:
            continue
        bc_raw = row[cols["条码"]]
        bc = safe_str(bc_raw)
        if bc.endswith(".0"):
            bc = bc[:-2]
        if not bc or bc == "0":
            continue
        baseline[bc] = {
            "L1": safe_str(row[cols["L1"]]) if cols["L1"] >= 0 and cols["L1"] < len(row) else "",
            "L2": safe_str(row[cols["L2"]]) if cols["L2"] >= 0 and cols["L2"] < len(row) else "",
            "L3": safe_str(row[cols["L3"]]) if cols["L3"] >= 0 and cols["L3"] < len(row) else "",
            "L4": safe_str(row[cols["L4"]]) if cols["L4"] >= 0 and cols["L4"] < len(row) else "",
            "商品角色": safe_str(row[cols["商品角色"]]) if cols["商品角色"] >= 0 and cols["商品角色"] < len(row) else "",
            "价格带": safe_str(row[cols["价格带"]]) if cols["价格带"] >= 0 and cols["价格带"] < len(row) else "",
            "场景标签": safe_str(row[cols["场景标签"]]) if cols["场景标签"] >= 0 and cols["场景标签"] < len(row) else "",
            "顾客标签": safe_str(row[cols["顾客标签"]]) if cols["顾客标签"] >= 0 and cols["顾客标签"] < len(row) else "",
            "匹配状态": safe_str(row[cols["匹配状态"]]) if cols["匹配状态"] >= 0 and cols["匹配状态"] < len(row) else "",
            "匹配置信度": safe_float(row[cols["匹配置信度"]]) if cols["匹配置信度"] >= 0 and cols["匹配置信度"] < len(row) else None,
            "匹配依据": safe_str(row[cols["匹配依据"]]) if cols["匹配依据"] >= 0 and cols["匹配依据"] < len(row) else "",
        }
    return baseline


def dedup_by_barcode(records: List[dict], priority_order: List[str],
                     conflict_fields: List[str]) -> Tuple[List[dict], List[dict]]:
    """
    按 priority_order 文件优先级去重；同条码不同字段值生成冲突清单。
    """
    by_key = {}
    conflicts = []

    def priority_rank(source_id: str) -> int:
        try:
            return priority_order.index(source_id)
        except ValueError:
            return 99

    for r in records:
        bc = r["商品条码"]
        period_start = r.get("统计期间起", "")
        # 联合主键：条码 + 期间，但去重以条码为主
        key = bc
        if not key:
            continue

        if key not in by_key:
            by_key[key] = r
        else:
            existing = by_key[key]
            new_p = priority_rank(r["数据来源文件"])
            old_p = priority_rank(existing["数据来源文件"])

            for field in conflict_fields:
                v_existing = existing.get(field)
                v_new = r.get(field)
                if v_existing != v_new and v_new not in (None, "", 0, 0.0):
                    keep = existing if old_p <= new_p else r
                    drop = r if old_p <= new_p else existing
                    conflicts.append({
                        "商品条码": bc,
                        "字段": field,
                        "值_保留": keep.get(field),
                        "值_丢弃": drop.get(field),
                        "保留来源": keep["数据来源文件"],
                        "丢弃来源": drop["数据来源文件"],
                    })

            if new_p < old_p:
                # 新记录优先级更高，替换
                by_key[key] = r

            # v0.1.1 新增: 跨源字段补全 — kept 中空字段从 source 拾取非空值
            _fill_missing_fields_from_source(
                by_key[key], r,
                fill_fields=["品牌", "规格", "单位", "L3", "L4",
                             "ERP类别名称", "ERP类别编码"]
            )

    return list(by_key.values()), conflicts


def _fill_missing_fields_from_source(target: dict, source: dict,
                                      fill_fields: List[str]):
    """v0.1.1 辅助: target 中空字段从 source 拾取非空值, 标'来源回填'。"""
    filled = []
    for f in fill_fields:
        t_val = target.get(f)
        if t_val in (None, "", 0, 0.0):
            s_val = source.get(f)
            if s_val not in (None, "", 0, 0.0):
                target[f] = s_val
                filled.append(f)
    if filled:
        existing_note = target.get("备注", "")
        tag = f"来源回填_{source.get('数据来源文件', '')}: {','.join(filled)}"
        target["备注"] = (existing_note + "; " + tag) if existing_note else tag


def extract_inventory_snapshots(sales_records: List[dict]) -> List[dict]:
    """从销售记录抽取库存快照（多时点保留）。"""
    snapshots = []
    for r in sales_records:
        inv = r.get("库存即时快照")
        if inv is None:
            continue
        cost = r.get("进价")
        snapshots.append({
            "商品条码": r["商品条码"],
            "货号": r.get("货号", ""),
            "商品名称": r.get("商品名称", ""),
            "库存数量": inv,
            "进价": cost,
            "库存金额": round(inv * cost, 2) if cost is not None else None,
            "库存快照日期": r.get("库存快照日期"),
            "是否负库存": inv < 0 if inv is not None else False,
            "数据来源文件": r["数据来源文件"],
            "备注": "负库存" if (inv is not None and inv < 0) else "",
        })
    return snapshots


def build_archive_from_sales(sales_main: List[dict]) -> List[dict]:
    """
    从合并去重后的销售主表构建商品档案（条码维度）。
    本轮全部为有动销 SKU。
    """
    archive = []
    for r in sales_main:
        archive.append({
            "商品条码": r["商品条码"],
            "货号": r.get("货号", ""),
            "条码源类型": r.get("条码源类型", ""),
            "商品名称": r.get("商品名称", ""),
            "品牌": r.get("品牌", ""),
            "规格": r.get("规格", ""),
            "单位": r.get("单位", ""),
            "L1": r.get("L1", ""),
            "L2": r.get("L2", ""),
            "L3": r.get("L3", ""),
            "L4": r.get("L4", ""),
            "商品角色": r.get("商品角色", ""),
            "价格带": r.get("价格带", ""),
            "场景标签": r.get("场景标签", ""),
            "顾客标签": r.get("顾客标签", ""),
            "进价": r.get("进价"),
            "当前售价": r.get("零售价"),
            "匹配状态": r.get("匹配状态", ""),
            "匹配置信度": r.get("匹配置信度"),
            "匹配依据": r.get("匹配依据", ""),
            "是否有动销": "是",
            "数据来源": r["数据来源文件"],
            "备注": "",  # v0.1.3: 本轮 archive 全部为有动销 SKU（line 340 注释已说明）/ 零动销 SKU 待 P1-B B.7 单独补采 / 不在本字段
        })
    return archive


def extract_scale_specials(sales_main: List[dict]) -> List[dict]:
    """
    v0.1.1 新增 / v0.1.2 调整:
    从主表抽取散称 SKU 单列专题。
    v0.1.2 扩展 criterion: 包含 '散称代理' + '短货号'(均属"非标准 EAN 体系外")。
    """
    NON_EAN_TYPES = {"散称代理", "短货号"}
    specials = []
    for r in sales_main:
        if r.get("条码源类型") not in NON_EAN_TYPES:
            continue
        scale_cat = infer_scale_category(r)
        specials.append({
            "散称代理键": r["商品条码"],
            "货号": r.get("货号", ""),
            "商品名称": r.get("商品名称", ""),
            "销售数量": r.get("销售数量"),
            "销售金额": r.get("销售金额"),
            "进价": r.get("进价"),
            "当前库存": r.get("库存即时快照"),
            "ERP类别编码": r.get("ERP类别编码", ""),
            "ERP类别名称": r.get("ERP类别名称", ""),
            "晟果L1": r.get("L1", ""),
            "晟果L2": r.get("L2", ""),
            "散称大类(推断)": scale_cat,
            "是否可匹配标准品类": "是" if r.get("L1") else "否",
            "匹配置信度": r.get("匹配置信度"),
            "数据来源文件": r.get("数据来源文件", ""),
            "备注": r.get("备注", ""),
        })
    return specials
