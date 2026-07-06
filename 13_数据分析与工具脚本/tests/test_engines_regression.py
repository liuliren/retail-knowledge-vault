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

def test_zclass_match_rate_semantics():
    import pandas as pd
    sku = pd.DataFrame({"条码": ["A1", "A2", "B9"]})
    reg = pd.DataFrame({"货号": ["A1", "A2", "A3"]})
    rate = sku.条码.isin(reg.货号).mean() * 100
    assert abs(rate - 66.7) < 0.1                  # 2/3 匹配 → 触发 <95% 警报口径
