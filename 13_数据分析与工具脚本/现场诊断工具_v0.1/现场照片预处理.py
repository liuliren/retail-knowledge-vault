#!/usr/bin/env python3
"""现场照片预处理 v0.1 — 巡店诊断照片批量转换/预处理

第一性原理: 把现场照片"做对做好"地变成 AI 能读、诊断够用的图 —— 省 token 是顺带。
职责:
  1. 把 Read 工具读不了的格式 → JPG (可读)
  2. 可选 resize 到诊断够用分辨率 (默认长边 1600px, 质量足够看清货架/价签/分档; 0=原尺寸)
  3. 可选抽样 (--sample N = 每 N 张取 1; 默认全转)
  4. 绝不改动源文件 (只读) —— 客户原始照片属 D 层 raw, 输出到独立工作目录

依赖: macOS 内置 sips (无需 pip)。sips 读不了的极冷门 RAW 会如实报错跳过、不静默吞。

用法:
  python3 现场照片预处理.py <源目录|文件...> --out <输出目录> [--resize 1600] [--sample 1] [--format jpg]
  # 例: 抽样每8张、压到1400、转JPG
  python3 现场照片预处理.py ".../04_现场照片/2026-07-03" --out ~/scratch/hct --sample 8 --resize 1400
"""
import argparse, os, subprocess, sys

# Read 工具原生可读(无需转换): jpg/jpeg/png/gif/webp
READABLE = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
# 需转换的格式(Read 读不了)——手机/相机/扫描常见
NEED_CONVERT = {
    ".heic", ".heif",          # iPhone 默认
    ".tif", ".tiff",           # 扫描件/高清
    ".bmp",                    # 老截图
    ".dng",                    # 通用 RAW
    ".cr2", ".cr3",            # Canon RAW
    ".nef", ".nrw",            # Nikon RAW
    ".arw", ".sr2", ".srf",    # Sony RAW
    ".raf",                    # Fuji RAW
    ".orf",                    # Olympus RAW
    ".rw2",                    # Panasonic RAW
    ".pef",                    # Pentax RAW
    ".srw",                    # Samsung RAW
    ".3fr", ".fff",            # Hasselblad
}
ALL_IMG = READABLE | NEED_CONVERT


def sips_convert(src, dst, fmt, resize):
    cmd = ["sips", "-s", "format", fmt]
    if resize and resize > 0:
        cmd += ["-Z", str(resize)]     # -Z = 等比缩放到长边 resize
    cmd += [src, "--out", dst]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def collect(inputs):
    files = []
    for p in inputs:
        if os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                if os.path.splitext(f)[1].lower() in ALL_IMG:
                    files.append(os.path.join(p, f))
        elif os.path.isfile(p):
            files.append(p)
    return files


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inputs", nargs="+", help="源目录或文件(只读)")
    ap.add_argument("--out", required=True, help="输出目录(源不动)")
    ap.add_argument("--resize", type=int, default=1600, help="长边像素;0=不缩放(默认1600,诊断够用)")
    ap.add_argument("--sample", type=int, default=1, help="每N张取1;默认1=全转")
    ap.add_argument("--format", default="jpeg", choices=["jpeg", "png"], help="输出格式")
    a = ap.parse_args()

    os.makedirs(a.out, exist_ok=True)
    files = collect(a.inputs)
    if not files:
        print("⚠️ 未找到图片文件"); sys.exit(0)

    picked = files[::a.sample] if a.sample > 1 else files
    ext = ".jpg" if a.format == "jpeg" else ".png"

    done, skipped, failed, fmt_count = 0, 0, [], {}
    for src in picked:
        e = os.path.splitext(src)[1].lower()
        fmt_count[e] = fmt_count.get(e, 0) + 1
        base = os.path.splitext(os.path.basename(src))[0]
        dst = os.path.join(a.out, base + ext)
        # 已可读且不需缩放 → 只复制(仍走 sips 保证 EXIF 方向正)
        ok, msg = sips_convert(src, dst, a.format, a.resize)
        if ok:
            done += 1
        else:
            failed.append((os.path.basename(src), msg[:80]))

    print(f"✓ 转换 {done} 张 → {a.out}")
    print(f"  源 {len(files)} 张, 抽样 {len(picked)} 张 (每{a.sample}取1), 长边 {a.resize or '原尺寸'}px")
    print(f"  格式分布: " + ", ".join(f"{k}×{v}" for k, v in sorted(fmt_count.items())))
    if failed:
        print(f"  ⚠️ 失败 {len(failed)} 张(sips 读不了·如实报,不静默):")
        for n, m in failed[:10]:
            print(f"     ✗ {n}: {m}")


if __name__ == "__main__":
    main()
