#!/usr/bin/env python3
"""客户级配置加载器（SENSITIVE-PRIVATE-003·方案A 脱敏参数化）.

通用方法工具(本目录)**不硬编码任何客户名/路径/文件名**;客户耦合(输入路径、输出前缀、
ERP 文件名 glob、生鲜/客户级排除来源)一律从**客户配置文件**读取。
配置文件存于 gitignored 私有区(_client_private/<客户>/goldmine/...),不入 git。

解析顺序：--config 参数 > 环境变量 GOLDMINE_CONFIG > 报错(要求显式指定)。
"""
from __future__ import annotations

import json
import os
from pathlib import Path

# 通用占位默认(无任何客户名/客户文件名);真实值由客户配置(gitignored 私有 yaml)覆盖。
# 注:此处 *_glob 仅留通用占位 None,客户 ERP 文件名通配一律写在私有配置,不入 tracked。
DEFAULTS = {
    "client_name": "<client>",
    "input_dir": None,            # 客户原始数据目录(gitignored 私有配置提供)
    "processed_subdir": "processed",
    "backbone_glob": None,        # 主干销售汇总文件名通配(私有配置提供)
    "archive_glob": None,         # 商品档案文件名通配
    "slow_glob": None,            # 滞销/库存文件名通配
    "fresh_archive_glob": None,   # 生鲜档案/客户级排除来源(§3.1.3)
    "output_prefix": "<client>",  # 输出文件名前缀(私有配置提供真实客户名)
}


def resolve_config_path(arg_config: str | None) -> str | None:
    return arg_config or os.environ.get("GOLDMINE_CONFIG")


def load_config(arg_config: str | None) -> dict:
    p = resolve_config_path(arg_config)
    if not p:
        raise SystemExit(
            "BLOCKED: 未指定客户配置。请用 --config <path> 或环境变量 GOLDMINE_CONFIG 指向"
            " gitignored 私有配置(模板见 治理规范/goldmine客户配置模板)。"
        )
    path = Path(p)
    if not path.exists():
        raise SystemExit(f"BLOCKED: 客户配置不存在: {p}")
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml  # PyYAML(已安装 6.0.3)
        loaded = yaml.safe_load(text) or {}
    else:
        loaded = json.loads(text)
    cfg = dict(DEFAULTS)
    cfg.update(loaded)
    return cfg
