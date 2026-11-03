"""tools/resave_checkpoints.py (PW-1408): the entry-by-entry comparison that decides whether a converted checkpoint may replace the old one."""

import importlib.util
from pathlib import Path

import numpy as np

_spec = importlib.util.spec_from_file_location("resave_checkpoints", Path(__file__).resolve().parent.parent / "tools" / "resave_checkpoints.py")
RC = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(RC)


def _state():
    return {"t": 5.0, "a": np.arange(6, dtype=np.float64).reshape(2, 3), "events": [{"k": np.ones(2, np.uint8)}, ("x", 1)],
            "plates": {"age": np.zeros((2, 3)), "alive": np.array([True, False])}}


def test_equal_states_have_no_differences():
    assert RC.differences(_state(), _state()) == []


def test_every_kind_of_difference_is_found():
    base = _state()
    for edit in (lambda s: s["a"].__setitem__((1, 2), 99.0),                    # one value
                 lambda s: s.__setitem__("a", s["a"].astype(np.float32)),       # dtype
                 lambda s: s.__setitem__("a", s["a"].reshape(3, 2)),            # shape
                 lambda s: s["events"][0].__setitem__("k", np.zeros(2, np.uint8)),
                 lambda s: s.__setitem__("t", 5.5),
                 lambda s: s["events"].append(1),
                 lambda s: s["plates"].pop("alive"),
                 lambda s: s.__setitem__("extra", 1)):
        other = _state()
        edit(other)
        assert RC.differences(base, other), edit
