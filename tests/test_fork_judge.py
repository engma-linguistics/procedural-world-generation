"""The forked paired judge's harness (docs/review/base-climate/v1-finish-16/fork.py, lane 144): a draw spun to the
fork and continued with the same code is the unforked tools/ice_diag.py run, bit for bit; a --set after the fork
leaves the spin-up (and so the frozen references) as they were."""

import gzip
import importlib.util
import json
from argparse import Namespace
from pathlib import Path

import pytest

from planet.tectonics import earth
from tools import ice_diag

ROOT = Path(__file__).resolve().parents[1]
SETS = ["climate_offset=-6.0", "finish_window=0"]


def _fork_module():
    spec = importlib.util.spec_from_file_location("fork_judge", ROOT / "docs/review/base-climate/v1-finish-16/fork.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _load(p):
    return json.loads(gzip.open(p, "rt").read())


@pytest.fixture(scope="module")
def forked(tmp_path_factory):
    tmp_path = tmp_path_factory.mktemp("fork_judge")
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(earth, "REF_FREEZE", 16.0)  # (a short spin-up: the same rule, frozen sooner, in every run here)
        F = _fork_module()
        F.spin(Namespace(code=str(ROOT), out=str(tmp_path / "fork"), seed=1, fork=16.0, myr=28.0, level=4, set=SETS))
        base = tmp_path / "fork" / "seed1_L4_at16"

        def cont(name, sets=()):
            return _load(F.cont(Namespace(code=str(ROOT), fork_base=str(base), out=str(tmp_path / name),
                                          set=list(sets), fill_missing=False)))
        yield tmp_path, cont, base


def test_fork_with_the_same_code_is_the_unforked_run(forked):
    tmp, cont, _ = forked
    u = _load(ice_diag.run(1, 28.0, 4, ice_diag.parse_sets(SETS), tmp))
    f = cont("same")
    assert f["params"] == u["params"]
    assert len(f["steps"]) == len(u["steps"]) == 14
    assert f["steps"] == u["steps"]
    assert f["updates"] == u["updates"]


def test_a_set_after_the_fork_leaves_the_spin_up(forked):
    tmp, cont, base = forked
    a, b = cont("a"), cont("b", ["climate_offset=-5.99999"])
    n = sum(r["t"] <= 16.0 for r in a["steps"])
    assert a["steps"][:n] == b["steps"][:n] and n == 8
    assert {r["offset"] for r in b["steps"][n:]} == {-5.99999}
    assert b["fork"]["refs"] == a["fork"]["refs"] == _load(f"{base}.json.gz")["refs"]
    assert b["fork"]["sets_after"] == {"climate_offset": -5.99999}
