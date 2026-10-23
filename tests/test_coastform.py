import numpy as np

from planet import coastform as CF
from planet import store as S


def _scores(n, **kw):
    s = {"near": np.ones(n, bool), "fjord": np.zeros(n), "delta": np.zeros(n, bool), "tide": np.zeros(n),
         "relief": np.full(n, 50.0), "mud": np.zeros(n), "barrier": np.zeros(n), "reef_nbr": np.zeros(n),
         "cliff": np.zeros(n), "rocky": np.zeros(n), "wave": np.zeros(n)}
    s.update(kw)
    return s


def test_classes_first_match_wins():
    n = 6
    s = _scores(n, barrier=np.array([0.9, 0.9, 0, 0, 0, 0]), cliff=np.array([0.9, 0, 0.9, 0, 0, 0]),
                wave=np.array([0, 0, 0, 0, 5.0, 0]), rocky=np.array([0, 0, 0, 0.8, 0, 0]))
    L = {"ice": np.array([1.0, 0, 0, 0, 0, 0])}
    ct = CF.classify(L, s)
    assert list(ct) == [CF.ICE, CF.BARRIER, CF.CLIFF, CF.ROCKY, CF.BEACH, CF.LOW]
    s["near"][5] = False
    assert CF.classify(L, s)[5] == 0  # not a coast cell


def test_tidal_needs_big_tides_on_low_or_muddy_coast():
    s = _scores(3, tide=np.array([5.0, 5.0, 5.0]), relief=np.array([50.0, 400.0, 400.0]),
                mud=np.array([0, 0, 0.8]))
    assert list(CF.classify({}, s)) == [CF.TIDAL, CF.LOW, CF.TIDAL]


def test_specs_and_legend():
    assert set(CF.LAYERS) <= set(S.LAYERS)
    ids = [e["id"] for e in CF.legend()]
    assert ids == list(range(len(ids)))
    assert "coast" in S.legends()
