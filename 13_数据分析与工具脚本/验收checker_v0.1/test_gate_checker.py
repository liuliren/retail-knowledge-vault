"""gate_checker.py 的 pytest 单测。

全部用临时构造的 md 字符串测试(tmp_path)，不依赖任何真实客户文件。
覆盖: 全过件 / 缺字段 / 含13位条码 / 超长summary / 非法status / deprecated合法(≥6例)。
"""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate_checker import check_file  # noqa: E402

SCRIPT = Path(__file__).resolve().parent / "gate_checker.py"


def write(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(content, encoding="utf-8")
    return p


# ---- 1. 全过件：G2/G4/G5/G6 均应 PASS ----
GOOD_MD = """---
title: 测试全过件
version: v0.1
status: draft
client_safety: internal
fact_layer: observed
summary: 这是一句不超过四十字的合法摘要用于测试
---

# 正文

净销 225.4 万，条码匹配率 97.6%，无供应商明细，无进价裸值。
"""


def test_all_pass(tmp_path):
    p = write(tmp_path, "good.md", GOOD_MD)
    ok, results = check_file(p)
    assert ok is True
    for name, (gate_ok, details) in results.items():
        assert gate_ok is True, f"{name} 不应 FAIL: {details}"


# ---- 2. 缺字段：G2 应 FAIL(缺 fact_layer / client_safety) ----
MISSING_FIELD_MD = """---
title: 缺字段测试件
version: v0.1
status: draft
summary: 缺少 client_safety 与 fact_layer 两个必填字段
---

正文无红线内容。
"""


def test_missing_required_field_fails_g2(tmp_path):
    p = write(tmp_path, "missing_field.md", MISSING_FIELD_MD)
    ok, results = check_file(p)
    assert ok is False
    g2_ok, g2_details = results["G2 机械可核字段"]
    assert g2_ok is False
    joined = " ".join(g2_details)
    assert "client_safety" in joined
    assert "fact_layer" in joined


# ---- 3. 含13位连续数字(EAN条码)：G4 应 FAIL ----
BARCODE_MD = """---
title: 含条码测试件
version: v0.1
status: draft
client_safety: internal
fact_layer: observed
summary: 正文混入一条13位条码用于测试G4红线
---

商品条码为 6901234567890，属于违规裸值。
"""


def test_barcode_in_body_fails_g4(tmp_path):
    p = write(tmp_path, "barcode.md", BARCODE_MD)
    ok, results = check_file(p)
    assert ok is False
    g4_ok, g4_details = results["G4 客户安全红线"]
    assert g4_ok is False
    assert any("6901234567890" in d for d in g4_details)


# ---- 3b. 含进价裸值：G4 应 FAIL ----
PRICE_MD = """---
title: 含进价裸值测试件
version: v0.1
status: draft
client_safety: internal
fact_layer: observed
summary: 正文混入进价裸值用于测试G4红线
---

该商品进价: 12.5 元，属于违规裸值。
"""


def test_price_value_in_body_fails_g4(tmp_path):
    p = write(tmp_path, "price.md", PRICE_MD)
    ok, results = check_file(p)
    assert ok is False
    g4_ok, g4_details = results["G4 客户安全红线"]
    assert g4_ok is False
    assert any("进价" in d for d in g4_details)


# ---- 4. summary 超长(>40字)：G2 与 G5 均应 FAIL ----
LONG_SUMMARY_MD = """---
title: 超长summary测试件
version: v0.1
status: draft
client_safety: internal
fact_layer: observed
summary: 这是一句故意写得非常非常非常非常非常非常非常非常长的摘要用来测试超过四十字上限是否会被正确拦截
---

正文正常。
"""


def test_long_summary_fails_g2_and_g5(tmp_path):
    p = write(tmp_path, "long_summary.md", LONG_SUMMARY_MD)
    ok, results = check_file(p)
    assert ok is False
    g2_ok, _ = results["G2 机械可核字段"]
    g5_ok, g5_details = results["G5 summary规范"]
    assert g2_ok is False
    assert g5_ok is False
    assert any("超过40字" in d for d in g5_details)


# ---- 5. 非法status：G6 应 FAIL ----
INVALID_STATUS_MD = """---
title: 非法status测试件
version: v0.1
status: 已完成
client_safety: internal
fact_layer: observed
summary: status用了不在合法枚举值内的中文自造状态
---

正文正常。
"""


def test_invalid_status_fails_g6(tmp_path):
    p = write(tmp_path, "invalid_status.md", INVALID_STATUS_MD)
    ok, results = check_file(p)
    assert ok is False
    g6_ok, g6_details = results["G6 状态机合法"]
    assert g6_ok is False
    assert any("非法" in d for d in g6_details)


# ---- 6. deprecated 合法：G6 应 PASS(deprecated 在合法枚举内,不要求signoff) ----
DEPRECATED_MD = """---
title: deprecated合法测试件
version: v0.2
status: deprecated
deprecated_reason: 被新版取代
client_safety: internal
fact_layer: observed
summary: 状态为deprecated且在合法枚举值内应当通过G6
---

正文正常，已废弃仅存档。
"""


def test_deprecated_status_passes_g6(tmp_path):
    p = write(tmp_path, "deprecated.md", DEPRECATED_MD)
    ok, results = check_file(p)
    g6_ok, g6_details = results["G6 状态机合法"]
    assert g6_ok is True, g6_details
    # deprecated 不在 signoff 强制提醒范围内(只有 stable/active 才提醒)
    assert not any("signoff" in d for d in g6_details)


# ---- 7. stable 但缺 signoff：G6 仍应 PASS(只警告不 FAIL)，但警告应出现 ----
STABLE_NO_SIGNOFF_MD = """---
title: stable缺签字测试件
version: v1.0
status: stable
client_safety: internal
fact_layer: observed
summary: 状态为stable但frontmatter未见signoff字段应仅警告
---

正文正常。
"""


def test_stable_without_signoff_warns_but_passes_g6(tmp_path):
    p = write(tmp_path, "stable_no_signoff.md", STABLE_NO_SIGNOFF_MD)
    ok, results = check_file(p)
    g6_ok, g6_details = results["G6 状态机合法"]
    assert g6_ok is True
    assert any("signoff" in d for d in g6_details)


# ---- 8. CLI 层烟测：exit code 应与全过/有FAIL 对应 ----
def test_cli_exit_code_pass(tmp_path):
    p = write(tmp_path, "cli_good.md", GOOD_MD)
    result = subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)
    assert result.returncode == 0
    assert "全过" in result.stdout


def test_cli_exit_code_fail(tmp_path):
    p = write(tmp_path, "cli_bad.md", BARCODE_MD)
    result = subprocess.run([sys.executable, str(SCRIPT), str(p)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "FAIL" in result.stdout


def test_cli_missing_file(tmp_path):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), str(tmp_path / "not_exist.md")],
        capture_output=True, text=True,
    )
    assert result.returncode == 1
    assert "不存在" in result.stderr
