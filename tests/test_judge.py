"""tools/judge.py (PW-1393): the climate judge, moved out of docs/review (passrate4, pjudge). Judges small fixed series;
the numbers pin the rules (hellhouse dT median > +10.5 or max > +15.5, frozen over = 40% of land under ice at the end, PW-1425)."""
import numpy as np

from tools import judge as J

T = np.arange(300.0, 1000.0, 4.0)
SI = np.zeros_like(T)  # no sea-level ice at all
STAR = np.linspace(-10.0, 0.0, T.size)  # dim young star brightening to the finish


def test_calm_world_passes():
    j = J.judge(T, SI, np.full_like(T, 0.5), 300, 1e9, np.full_like(T, 0.02), STAR)
    assert j["ok"] and not j["hell"] and not j["frozen"]
    assert j["never"] and not j["icehouse"] and not j["glacial_max"]
    assert j["med"] == 0.5 and j["mx"] == 0.5
    assert J.line(j).endswith("NEVER-ICE -> ok")


def test_hellhouse_rules():
    dT = np.full_like(T, 10.0)
    assert not J.judge(T, SI, dT, 300, 1e9)["hell"]
    dT[0] = 15.5  # max exactly at the limit is not over it
    assert not J.judge(T, SI, dT, 300, 1e9)["hell"]
    dT[0] = 15.6
    assert J.judge(T, SI, dT, 300, 1e9)["hell"]
    assert J.judge(T, SI, np.full_like(T, 10.6), 300, 1e9)["hell"]


def test_frozen_over_means_the_world_ends_frozen():
    """Owner 11-03 (D47, PW-1425): frozen over fails when the world ends frozen (or stays frozen to the end), not when
    some moment of the hard window crosses 40%; that peak is reported."""
    dT = np.zeros_like(T)
    il = np.where(T < 500, 0.5, 0.01)  # 50% of land iced, only under the dim young star
    j = J.judge(T, SI, dT, 300, 1e9, il, STAR)
    assert j["frozen_any"] and not j["frozen"] and not j["frozen_peak"] and j["ok"]
    il = np.where((T > 900) & (T < 950), 0.45, 0.1)  # a frozen glacial late in the run, recovered by the end
    j = J.judge(T, SI, dT, 300, 1e9, il, STAR)
    assert j["frozen_peak"] and not j["frozen"] and j["ok"]
    il = np.where(T > 950, 0.45, 0.1)  # frozen at the end
    j = J.judge(T, SI, dT, 300, 1e9, il, STAR)
    assert j["frozen"] and not j["ok"] and "FROZEN-OVER" in J.flags(j)
    assert not J.judge(T, SI, dT, 300, 1e9, il, STAR, fin_ice=True)["frozen"]  # (a finish moment passes for ice)
    il = np.full_like(T, 0.5)  # iced to the end
    j = J.judge(T, SI, dT, 300, 1e9, il, STAR)
    assert j["frozen"] and not j["ok"]
    assert J.judge(T, SI, dT, 2000, 3000) is None  # empty window
