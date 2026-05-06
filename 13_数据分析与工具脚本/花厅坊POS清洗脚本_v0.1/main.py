#!/usr/bin/env python3
"""
花厅坊 POS 清洗主控脚本 v0.1

模式：
  python3 main.py            # dry-run（默认，不写正式输出）
  python3 main.py --execute  # 正式执行（需用户预审 dry-run 后授权）
"""
import sys
import json
from datetime import datetime, timezone
from pathlib import Path

# 确保脚本目录在 sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from config import (INPUT_FILES, EXECUTE_OUTPUT_DIR, DRYRUN_PREVIEW_DIR,
                    PRIORITY_ORDER, ANOMALY_THRESHOLDS, PROTECTED_PATHS,
                    SALES_FIELD_MAP, ERP_CATEGORY_MAP, ERP_CATEGORY_CONFIDENCE)
from loaders import (compute_sha256, load_excel_readonly, verify_no_modification)
from normalizers import (detect_pattern, strip_print_metadata, parse_period,
                          parse_print_date)
from mappers import (build_field_index, map_sales_record, build_baseline_dict,
                     apply_baseline_match, apply_erp_category_match,
                     dedup_by_barcode, extract_inventory_snapshots,
                     build_archive_from_sales, extract_scale_specials)
from anomaly_rules import detect_anomalies, evaluate_gate
from writer import write_dryrun_preview, write_xlsx_outputs, write_log


def main(execute: bool = False) -> dict:
    started_at = datetime.now(timezone.utc)
    log = {
        "started_at": started_at.isoformat(),
        "mode": "execute" if execute else "dry-run",
        "vault_protection_paths": [str(p) for p in PROTECTED_PATHS],
    }

    print(f"\n{'='*60}")
    print(f"花厅坊 POS 清洗脚本 v0.1 — {log['mode'].upper()}")
    print(f"启动时间: {started_at.isoformat()}")
    print(f"{'='*60}\n")

    # === 阶段 1: SHA256 输入校验 ===
    print("[阶段 1] 计算输入文件 SHA256...")
    sha_before = {}
    missing = []
    for fid, path in INPUT_FILES.items():
        if not path.exists():
            missing.append(fid)
            continue
        sha_before[fid] = compute_sha256(path)
    if missing:
        print(f"  ⚠️  缺失文件: {missing}")
        log["missing_files"] = missing
        sys.exit(f"FATAL: 输入文件缺失 {missing}")
    log["sha_before"] = sha_before
    print(f"  ✓ {len(sha_before)} 张输入文件 SHA256 已记录")

    # === 阶段 2: 只读加载 ===
    print("\n[阶段 2] 只读加载 Excel...")
    raw_data = {}
    for fid, path in INPUT_FILES.items():
        try:
            raw_data[fid] = load_excel_readonly(path)
            sheet_count = len(raw_data[fid])
            row_count = sum(s["nrows"] for s in raw_data[fid].values())
            print(f"  ✓ {fid}: {sheet_count} sheets, {row_count} rows")
        except Exception as e:
            print(f"  ✗ {fid}: {e}")
            log.setdefault("load_errors", {})[fid] = str(e)

    # === 阶段 3: 模式识别 + 元信息剥离 ===
    print("\n[阶段 3] 模式识别...")
    patterns = {}
    cleaned_sheets = {}  # fid -> sheet_name -> {header_row, data_rows, period_start, period_end, snapshot_date}
    for fid in ["S01", "S02", "S03", "S04", "S05", "S06", "S07"]:
        if fid not in raw_data:
            continue
        cleaned_sheets[fid] = {}
        for sheet_name, sheet in raw_data[fid].items():
            rows = sheet["rows"]
            pattern = detect_pattern(rows)
            patterns.setdefault(fid, {})[sheet_name] = pattern
            data_rows, skip = strip_print_metadata(rows, pattern)
            period_start, period_end = parse_period(rows)
            snapshot_date = parse_print_date(rows)
            if not data_rows:
                continue
            cleaned_sheets[fid][sheet_name] = {
                "pattern": pattern,
                "header": data_rows[0] if data_rows else [],
                "data": data_rows[1:] if len(data_rows) > 1 else [],
                "period_start": period_start,
                "period_end": period_end,
                "snapshot_date": snapshot_date,
            }
            print(f"  - {fid}/{sheet_name}: 模式={pattern} 跳过={skip} 数据行={len(data_rows)-1 if data_rows else 0}")
    log["pattern_detection"] = patterns

    # === 阶段 4: 字段映射 ===
    print("\n[阶段 4] 字段映射 → 销售记录...")
    sales_records = []
    for fid, sheets in cleaned_sheets.items():
        # 选最大数据行的 sheet 作主 sheet（合计行/标题 sheet 自然落选）
        if not sheets:
            continue
        main_sheet_name = max(sheets.keys(), key=lambda s: len(sheets[s]["data"]))
        main_sheet = sheets[main_sheet_name]
        if not main_sheet["header"]:
            continue
        field_index = build_field_index(main_sheet["header"], SALES_FIELD_MAP)
        # 调试：打印命中字段
        hit_fields = list(field_index.keys())
        print(f"  - {fid}/{main_sheet_name}: 命中字段 {len(hit_fields)} 个")
        for row in main_sheet["data"]:
            rec = map_sales_record(
                row, field_index, fid,
                main_sheet["period_start"], main_sheet["period_end"],
                main_sheet["snapshot_date"],
                header_row=main_sheet["header"],   # v0.1.1
            )
            if rec is None:
                continue
            sales_records.append(rec)
    print(f"  ✓ 总销售记录数（含跨表重复）: {len(sales_records)}")

    # === 阶段 5a: 基础匹配层吸入（4077 行 M01） ===
    print("\n[阶段 5a] 基础匹配层（M01）吸入...")
    if "M01" in raw_data:
        baseline = build_baseline_dict(raw_data["M01"])
        print(f"  ✓ 基础匹配字典构建: {len(baseline)} 条")
        hit, miss = apply_baseline_match(sales_records, baseline)
        print(f"  ✓ 命中: {hit}, 未命中: {miss} ({miss/(hit+miss)*100 if (hit+miss)>0 else 0:.1f}%)")
        log["baseline_match"] = {"baseline_size": len(baseline), "hit": hit, "miss": miss}
    else:
        log["baseline_match"] = {"error": "M01 缺失"}

    # === 阶段 5b: ERP 类别推断兜底（v0.1.1） ===
    print("\n[阶段 5b] ERP 类别推断兜底...")
    erp_hit, erp_miss = apply_erp_category_match(
        sales_records, ERP_CATEGORY_MAP, ERP_CATEGORY_CONFIDENCE
    )
    print(f"  ✓ ERP 字典: {len(ERP_CATEGORY_MAP)} 项")
    print(f"  ✓ ERP 兜底命中: {erp_hit}, 仍未命中: {erp_miss}")
    log["erp_category_match"] = {
        "dict_size": len(ERP_CATEGORY_MAP),
        "hit": erp_hit, "miss": erp_miss,
    }

    # === 阶段 6: 去重 + 冲突处理 ===
    print("\n[阶段 6] 去重 + 多源字段冲突...")
    sales_main, conflicts = dedup_by_barcode(
        sales_records, PRIORITY_ORDER,
        conflict_fields=["零售价", "进价", "商品名称", "品牌", "规格"]
    )
    print(f"  ✓ 去重后销售主表: {len(sales_main)}")
    print(f"  ✓ 多源字段冲突: {len(conflicts)}")
    log["dedup"] = {
        "input_records": len(sales_records),
        "deduped_records": len(sales_main),
        "conflicts": len(conflicts),
    }

    # === 阶段 7a: 抽取库存快照 + 构建商品档案 ===
    print("\n[阶段 7a] 库存快照 + 商品档案...")
    inventory_snapshots = extract_inventory_snapshots(sales_main)
    archive_main = build_archive_from_sales(sales_main)
    print(f"  ✓ 库存快照: {len(inventory_snapshots)}")
    print(f"  ✓ 商品档案: {len(archive_main)}")

    # === 阶段 7b: 散称专题抽取（v0.1.1） ===
    print("\n[阶段 7b] 散称专题抽取...")
    scale_specials = extract_scale_specials(sales_main)
    scale_dist = {}
    for s in scale_specials:
        c = s.get("散称大类(推断)", "未知")
        scale_dist[c] = scale_dist.get(c, 0) + 1
    print(f"  ✓ 散称专题: {len(scale_specials)}")
    print(f"  ✓ 大类分布: {scale_dist}")
    log["scale_special_summary"] = {
        "count": len(scale_specials),
        "ratio": (len(scale_specials) / len(sales_main)) if sales_main else 0,
        "by_category": scale_dist,
    }

    # === 阶段 8: 异常检测（17 类）===
    print("\n[阶段 8] 异常检测...")
    anomaly_result = detect_anomalies(sales_main)
    summary = anomaly_result["统计"]
    log["anomaly_summary"] = summary
    print(f"  阻断: {summary.get('blocking_count', 0)} ({summary.get('blocking_ratio', 0):.2%})")
    print(f"  标记: {summary.get('marking_count', 0)} ({summary.get('marking_ratio', 0):.2%})")
    print(f"  不阻断: {summary.get('info_count', 0)}")
    print(f"  阻断异常按类: {summary.get('blocking_by_type', {})}")
    print(f"  标记异常按类 TOP: {dict(sorted(summary.get('marking_by_type', {}).items(), key=lambda x: -x[1])[:5])}")

    # === 阶段 9: 异常率守门 ===
    gate = evaluate_gate(summary, ANOMALY_THRESHOLDS)
    log["gate_decision"] = gate
    print(f"\n[阶段 9] 守门决策: {gate}")
    if gate == "BLOCK":
        print("  ❌ 阻断异常 > 15%，停止执行")
        log["finished_at"] = datetime.now(timezone.utc).isoformat()
        log["sha_verify"] = verify_no_modification(INPUT_FILES, sha_before)
        return log

    # === 阶段 10: 资料索引表（13 张输入登记）===
    print("\n[阶段 10] 资料索引表构建...")
    index_table = []
    for fid, path in INPUT_FILES.items():
        sha = sha_before.get(fid, "")
        try:
            size = path.stat().st_size
            mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()
        except Exception:
            size, mtime = 0, ""
        index_table.append({
            "文件ID": fid,
            "文件名": path.name,
            "相对路径": str(path.relative_to(path.parents[3])) if len(path.parents) >= 4 else str(path),
            "文件类型": path.suffix.lstrip("."),
            "大小KB": round(size / 1024, 1),
            "数据维度": ("销售" if fid.startswith("S") else
                       "字典/档案" if fid.startswith("D") else
                       "基础匹配层"),
            "修改时间": mtime,
            "SHA256_前缀": sha[:16] if sha else "",
            "是否进入本轮": "是",
            "状态": "原始",
            "备注": "",
        })

    # === 阶段 11: 输出（dry-run 仅写预览）===
    print(f"\n[阶段 11] 输出（mode={log['mode']}）...")
    if execute:
        write_xlsx_outputs(
            EXECUTE_OUTPUT_DIR,
            sales_main=sales_main, archive_main=archive_main,
            inventory_snapshots=inventory_snapshots,
            anomalies=(anomaly_result["阻断"] + anomaly_result["标记"] +
                       anomaly_result["不阻断"]),
            index_table=index_table, conflicts=conflicts,
            scale_specials=scale_specials,        # v0.1.1
            protected_paths=PROTECTED_PATHS,
        )
        log_path = EXECUTE_OUTPUT_DIR / "清洗日志_v0.1.1.md"
        log["finished_at"] = datetime.now(timezone.utc).isoformat()
        log["counts"] = {
            "销售主表": len(sales_main), "商品档案": len(archive_main),
            "库存快照": len(inventory_snapshots),
            "异常_阻断": len(anomaly_result["阻断"]),
            "异常_标记": len(anomaly_result["标记"]),
            "异常_信息": len(anomaly_result["不阻断"]),
            "冲突": len(conflicts), "索引": len(index_table),
            "散称专题": len(scale_specials),       # v0.1.1
        }
        write_log(log_path, log, PROTECTED_PATHS)
        print(f"  ✓ 写入正式输出 → {EXECUTE_OUTPUT_DIR}")
    else:
        # Dry-run: 抽样 10 行
        sales_sample = sales_main[:10]
        archive_sample = archive_main[:10]
        inventory_sample = inventory_snapshots[:10]
        all_anomalies = (anomaly_result["阻断"] + anomaly_result["标记"] +
                         anomaly_result["不阻断"])
        anomalies_sample = all_anomalies[:10]
        index_sample = index_table[:10]
        conflicts_top20 = conflicts[:20]
        scale_specials_sample = scale_specials[:10]   # v0.1.1
        result = write_dryrun_preview(
            DRYRUN_PREVIEW_DIR,
            summary={
                "log": log,
                "counts": {
                    "销售主表": len(sales_main),
                    "商品档案": len(archive_main),
                    "库存快照": len(inventory_snapshots),
                    "异常_阻断": len(anomaly_result["阻断"]),
                    "异常_标记": len(anomaly_result["标记"]),
                    "异常_信息": len(anomaly_result["不阻断"]),
                    "冲突": len(conflicts),
                    "索引": len(index_table),
                    "散称专题": len(scale_specials),
                },
                "anomaly_summary": summary,
            },
            sales_sample=sales_sample,
            archive_sample=archive_sample,
            inventory_sample=inventory_sample,
            anomalies_sample=anomalies_sample,
            index_sample=index_sample,
            conflicts_top20=conflicts_top20,
            scale_specials_sample=scale_specials_sample,   # v0.1.1
            protected_paths=PROTECTED_PATHS,
        )
        print(f"  ✓ 写入预览 → {result['preview_dir']}")
        for f in result["written_files"]:
            print(f"    - {Path(f).name}")

    # === 阶段 12: SHA256 后置校验 ===
    print("\n[阶段 12] SHA256 前后对比...")
    verify = verify_no_modification(INPUT_FILES, sha_before)
    log["sha_verify"] = verify
    if verify["all_match"]:
        print("  ✓ 全部输入文件 SHA256 前后一致，原始数据未被修改")
    else:
        print(f"  ❌ 检测到原始文件被修改: {verify['mismatches']}")
        sys.exit("FATAL: 原始文件被修改")

    log["finished_at"] = datetime.now(timezone.utc).isoformat()
    print(f"\n{'='*60}")
    print(f"完成时间: {log['finished_at']}")
    print(f"{'='*60}")
    return log


if __name__ == "__main__":
    execute_mode = "--execute" in sys.argv
    final_log = main(execute=execute_mode)
    # 简洁日志输出
    print("\n=== 最终日志摘要 ===")
    print(json.dumps({
        "mode": final_log.get("mode"),
        "started_at": final_log.get("started_at"),
        "finished_at": final_log.get("finished_at"),
        "counts": final_log.get("counts", {}),
        "anomaly_summary": final_log.get("anomaly_summary", {}),
        "gate_decision": final_log.get("gate_decision"),
        "sha_verify_all_match": final_log.get("sha_verify", {}).get("all_match"),
    }, ensure_ascii=False, indent=2, default=str))
