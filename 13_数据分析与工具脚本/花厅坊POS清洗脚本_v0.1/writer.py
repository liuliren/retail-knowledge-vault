"""
输出层：dry-run 预览输出 + 正式 xlsx 输出。
所有写入路径必须严格隔离原始数据。
"""
import csv
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List


def ensure_output_safe(output_path: Path, protected_paths: list):
    """检查输出路径不在受保护路径下，否则抛错。"""
    output_resolved = output_path.resolve()
    for protected in protected_paths:
        protected_resolved = Path(protected).resolve()
        try:
            output_resolved.relative_to(protected_resolved)
            raise PermissionError(
                f"FATAL: 输出路径 {output_path} 位于受保护路径 {protected} 下，禁止写入"
            )
        except ValueError:
            continue  # 不在受保护路径下，OK


def write_dryrun_preview(preview_dir: Path, *,
                         summary: dict,
                         sales_sample: List[dict],
                         archive_sample: List[dict],
                         inventory_sample: List[dict],
                         anomalies_sample: List[dict],
                         index_sample: List[dict],
                         conflicts_top20: List[dict],
                         scale_specials_sample: List[dict] = None,   # v0.1.1
                         protected_paths: list) -> dict:
    """
    Dry-run 模式：写预览到 _dryrun_preview/ 目录。
    全部 CSV/JSON 格式，便于审阅。
    """
    ensure_output_safe(preview_dir, protected_paths)
    preview_dir.mkdir(parents=True, exist_ok=True)

    written = []

    # summary.json
    p = preview_dir / "dryrun_summary.json"
    with open(p, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
    written.append(str(p))

    # 抽样 CSV
    csv_files = [
        ("dryrun_sales_sample.csv", sales_sample),
        ("dryrun_archive_sample.csv", archive_sample),
        ("dryrun_inventory_sample.csv", inventory_sample),
        ("dryrun_anomalies_sample.csv", anomalies_sample),
        ("dryrun_index_sample.csv", index_sample),
        ("dryrun_conflicts_top20.csv", conflicts_top20),
    ]
    if scale_specials_sample is not None:
        csv_files.append(("dryrun_scale_specials_sample.csv", scale_specials_sample))

    for fname, data in csv_files:
        p = preview_dir / fname
        write_csv(p, data)
        written.append(str(p))

    return {"written_files": written, "preview_dir": str(preview_dir)}


def write_csv(path: Path, records: List[dict]):
    """写 CSV，UTF-8 with BOM（Excel 兼容）。"""
    if not records:
        with open(path, "w", encoding="utf-8-sig") as f:
            f.write("(empty)\n")
        return
    fieldnames = list(records[0].keys())
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            # 兼容 None / float / dict 值
            safe = {k: (v if not isinstance(v, dict) else json.dumps(v, ensure_ascii=False))
                    for k, v in r.items()}
            writer.writerow(safe)


def write_xlsx_outputs(output_dir: Path, *, sales_main, archive_main,
                       inventory_snapshots, anomalies, index_table,
                       conflicts, scale_specials=None,    # v0.1.1
                       protected_paths: list):
    """
    Execute 模式：写正式 xlsx 输出。
    本脚本 v0.1.1 暂以 CSV 形式预留接口；xlsx 写入待 v0.2 升级 openpyxl 多 sheet。
    """
    ensure_output_safe(output_dir, protected_paths)
    output_dir.mkdir(parents=True, exist_ok=True)
    backup_existing(output_dir)

    # 简化首版：暂用 CSV，后续 v0.2 升级 openpyxl 写入 xlsx
    write_csv(output_dir / "销售统计汇总_合并版_v0.1.1.csv", sales_main)
    write_csv(output_dir / "商品档案_合并版_v0.1.1.csv", archive_main)
    write_csv(output_dir / "库存即时快照_v0.1.1.csv", inventory_snapshots)
    write_csv(output_dir / "异常清单_v0.1.1.csv", anomalies)
    write_csv(output_dir / "资料索引表_v0.1.1.csv", index_table)
    write_csv(output_dir / "多源字段冲突清单_v0.1.1.csv", conflicts)
    if scale_specials is not None:
        write_csv(output_dir / "散称_专题_v0.1.1.csv", scale_specials)


def backup_existing(output_dir: Path):
    """同名输出文件加 UTC 时间戳后缀作备份。"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%MUTC")
    if not output_dir.exists():
        return
    for f in output_dir.glob("*.csv"):
        backup = output_dir / f"{f.stem}_backup_{timestamp}{f.suffix}"
        f.rename(backup)
    for f in output_dir.glob("*.xlsx"):
        backup = output_dir / f"{f.stem}_backup_{timestamp}{f.suffix}"
        f.rename(backup)
    for f in output_dir.glob("*.md"):
        backup = output_dir / f"{f.stem}_backup_{timestamp}{f.suffix}"
        f.rename(backup)


def write_log(path: Path, log_data: dict, protected_paths: list):
    """生成 Markdown 清洗日志。"""
    ensure_output_safe(path.parent, protected_paths)
    path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# 花厅坊 POS 清洗日志 v0.1\n")
    lines.append(f"**清洗时间：** {log_data.get('started_at', '')} → {log_data.get('finished_at', '')}\n")
    lines.append(f"**执行模式：** {log_data.get('mode', '')}\n")
    lines.append("\n## 1. 输入文件 SHA256 校验\n")
    for fid, sha in log_data.get("sha_before", {}).items():
        lines.append(f"- {fid}: `{sha[:16]}...`")
    lines.append("\n## 2. SHA256 前后对比\n")
    verify = log_data.get("sha_verify", {})
    lines.append(f"- 全部一致：{verify.get('all_match', False)}")
    if not verify.get("all_match", True):
        lines.append("- ⚠️ 检测到原始文件被修改：")
        for m in verify.get("mismatches", []):
            lines.append(f"  - {m}")
    lines.append("\n## 3. 模式识别结果\n")
    for fid, p in log_data.get("pattern_detection", {}).items():
        lines.append(f"- {fid}: 模式 {p}")
    lines.append("\n## 4. 行数统计\n")
    counts = log_data.get("counts", {})
    for k, v in counts.items():
        lines.append(f"- {k}: {v}")
    lines.append("\n## 5. 异常分布\n")
    summary = log_data.get("anomaly_summary", {})
    lines.append(f"- 阻断: {summary.get('blocking_count', 0)} ({summary.get('blocking_ratio', 0):.2%})")
    lines.append(f"- 标记: {summary.get('marking_count', 0)} ({summary.get('marking_ratio', 0):.2%})")
    lines.append(f"- 不阻断: {summary.get('info_count', 0)}")
    lines.append("\n## 6. 已知未处理项\n")
    lines.append("- 库存表数据缺失：现有数据无独立库存导出，仅 POS 表「库存」列即时快照；不能输出 P2-04C §S6 标准库存表；二访 P1-B B.6 必须补采。")
    lines.append("- 零动销 SKU 不在档案内：现有商品档案 = 有动销 SKU；零动销 SKU 未知占比；二访 P1-B B.7 必须补采。")
    lines.append("\n## 7. P2-04C v0.2 校准建议\n")
    lines.append("1. 新增「销售统计汇总表」为独立表型（区别于销售流水表）")
    lines.append("2. 新增「货号-条码双轨」统一规则（散称代理键）")
    lines.append("3. 新增「品类双编码体系」映射规则（ERP 类别 ↔ 晟果 L1-L4）")
    lines.append("4. 新增「打印元信息剥离」规则（前 N 行非数据头识别）")
    lines.append("5. 新增「金额字段口径核对表」（4 口径对账）")
    lines.append("6. v0.1.1 新增：ERP 类别 → 晟果 L1-L2 映射作 4 级匹配兜底层")
    lines.append("7. v0.1.1 新增：跨源字段补全规则（dedup 时回填空字段）")

    # v0.1.1 新增 §8 散称专题
    lines.append("\n## 8. 散称商品专题（v0.1.1）\n")
    scale_summary = log_data.get("scale_special_summary", {})
    lines.append(f"- 散称 SKU 数 / 占比：{scale_summary.get('count', 0)} / "
                 f"{scale_summary.get('ratio', 0):.2%}")
    lines.append("- 业态分布：")
    for cat, n in scale_summary.get("by_category", {}).items():
        lines.append(f"  - {cat}: {n}")
    lines.append("- 处理规则：")
    lines.append("  - 主表保留（条码源类型=散称代理）")
    lines.append("  - 单独「散称_专题」sheet 输出")
    lines.append("  - L3/L4 字段允许空，不阻断")
    lines.append("  - 不强行映射到标准品类（生鲜需独立的散称品类体系）")
    lines.append("- 后续工作：")
    lines.append("  - 二访 P1-B B.7 全量商品档案补采时，需含散称 SKU 称重规则")
    lines.append("  - 待建立散称专属品类体系（生鲜 L1-L4 与休食独立）")

    # v0.1.1 新增 §9 v0.2 backlog
    lines.append("\n## 9. v0.2 Backlog（v0.1.1 暂不处理）\n")
    lines.append("- 4 位短码 5 类（0202/0205/0206/0207/0209）：待 v0.2 处理")
    lines.append("- D03/D04/D05 加入字典：ROI 仅 11.7%，已记 v0.2 backlog")
    lines.append("- 中置信度 7 类待用户拍板：肉制品/油炸食品/低温面/其他冻品/即食类/茶叶/吐司系")
    lines.append("- 散称专属 L1-L4 体系（生鲜独立树）")
    lines.append("- 4 级匹配 Tier 2-4（关键词 / 品牌+规格 / 人工复核）")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
