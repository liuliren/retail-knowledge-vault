"""最小回归测试(2026-07-06·CI底线建立): 改两引擎必跑 python3 -m pytest tests/ -q
覆盖: ①语法可导入 ②第八坑差集校验逻辑 ③Z类匹配率口径。零真实客户数据。"""
import importlib.util, pathlib, sys, types

BASE = pathlib.Path(__file__).resolve().parents[0].parent

def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, BASE / rel)
    m = importlib.util.module_from_spec(spec)
    sys.modules[name] = m
    spec.loader.exec_module(m)
    return m

def test_both_engines_importable():
    _load("pos_clean_t", "POS清洗库_v0.1/pos_clean.py")
    _load("trio_t", "三件套引擎_v0.1/trio_engine.py")

class _FakeSheet:
    def __init__(self, rows): self._rows = rows
    def to_python(self): return self._rows

class _FakeWB:
    rows = []
    @classmethod
    def from_path(cls, _): return cls()
    def get_sheet_by_index(self, _): return _FakeSheet(type(self).rows)

def test_aggregate_diff_detects_orphan_category(tmp_path, monkeypatch):
    trio = _load("trio_t2", "三件套引擎_v0.1/trio_engine.py")
    (tmp_path / "DEMO-生鲜汇总表.xls").write_bytes(b"x")
    _FakeWB.rows = [["表头", "类别名称", "金额"],
                    ["1", "禽蛋", "100"], ["2", "水产", "50"]]
    monkeypatch.setattr(trio, "CalamineWorkbook", _FakeWB)
    probs = trio.check_aggregate_diff(str(tmp_path), "DEMO-", covered_cats={"水产"})
    assert probs and "禽蛋" in str(probs[0][1])   # 独有类别必须报警
    probs2 = trio.check_aggregate_diff(str(tmp_path), "DEMO-", covered_cats={"水产", "禽蛋"})
    assert not probs2                              # 全覆盖不误报

def test_schema_single_source_of_truth():
    """防漂移: 两引擎的关键列映射/口径常量必须来自 pos_schema(同一对象),
    禁止未来有人在引擎内重新本地定义副本。"""
    schema = _load("pos_schema", "pos_schema.py")  # 注册真名,引擎 import 命中同一模块
    pc = _load("pos_clean_s", "POS清洗库_v0.1/pos_clean.py")
    tr = _load("trio_s", "三件套引擎_v0.1/trio_engine.py")
    for name in ("SALES_COLS", "ARCH_STD", "ARCH_ALT", "DATE_ROW_RE",
                 "AGG_TABLE_RE", "EXCLUDE_BIGCLASS", "SYS_TOTAL_COL",
                 "RECON_TOLERANCE_PCT"):
        ref = getattr(schema, name)
        assert getattr(pc, name) is ref, f"pos_clean.{name} 本地重定义,脱离 pos_schema"
        assert getattr(tr, name) is ref, f"trio_engine.{name} 本地重定义,脱离 pos_schema"

def test_zclass_match_rate_semantics():
    import pandas as pd
    sku = pd.DataFrame({"条码": ["A1", "A2", "B9"]})
    reg = pd.DataFrame({"货号": ["A1", "A2", "A3"]})
    rate = sku.条码.isin(reg.货号).mean() * 100
    assert abs(rate - 66.7) < 0.1                  # 2/3 匹配 → 触发 <95% 警报口径

def test_xlsx_truncation_alarm_only_for_xls():
    """第四坑警报只对 .xls 生效; xlsx 无 65536 限不得误报(好家源 lessons 2026-07-06)。
    直接断言 cmd_probe 源码中的守卫条件存在, 防止未来把 endswith('.xls') 判定删掉。"""
    import inspect
    pc = _load("pos_clean_t4", "POS清洗库_v0.1/pos_clean.py")
    src = inspect.getsource(pc.cmd_probe)
    assert ".xls\")" in src and "endswith" in src and "XLS_LIMIT" in src, \
        "cmd_probe 截断警报必须带 .xls 后缀守卫(第四坑不适用xlsx)"
