"""tools/health.py's measures (PW-246): one L4 keyframe, drainage ends, spells."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from planet import timeline as T  # noqa: E402
from tools import health as H  # noqa: E402


def test_measure_frame(sim4):
    g, snap = sim4.grid, sim4.snapshot()
    vals = T.frame_values(g, snap, np.zeros((g.n, 3)))
    L = {k: vals[k] for k in H.MEASURE_LAYERS}
    st = sim4.stats()
    m = H.measure_frame(g, L, st)
    assert abs(m["land_pct"] - st["land_pct"]) < 0.1
    assert abs(m["cont_pct"] - st["continental_pct"]) < 0.1
    assert m["plates"] == st["plates"] and m["temp"] == st["global_temp_c"]
    assert 20 < m["cont_km"] < 50 and 0 < m["ocean_age"] < 300
    assert 0 <= m["inland_pct"] <= 100 and 0 <= m["lake_pct"] < 20 and m["lake_max_mkm2"] >= 0
    assert 0 <= m["trees_pct"] <= 100 and m["npp"] >= 0 and 0 <= m["dry_pct"] <= 100
    assert m["sea_ice_m"] <= 0 and abs(m["max_elev_km"] * 1000 - snap.elevation.max()) < 10
    assert set(H.ENVELOPES) <= set(m)  # every envelope has its measure


def test_drainage_ends():
    # 0 -> 1 -> 2 (sea); 3 -> 4 (a pit on land); 5 ice-covered land -> 4
    land = np.array([1, 1, 0, 1, 1, 1], bool)
    down = np.array([1, 2, -1, 4, -1, 4])
    assert list(H.drain_ends(down, land)) == [2, 2, 2, 4, 4, 4]
    free = land & (np.arange(6) != 5)
    assert H.inland_share(down, land, free) == 50.0  # 3 and 4 of 0, 1, 3, 4
    assert H.inland_share(np.full(6, -1), land, free) is None  # no rivers routed yet


def test_spells_and_outliers():
    ts = [0, 50, 54, 58, 62, 66, 70, 74]
    vals = [99, 1, 9, 9, 1, 12, 1, 1]  # (t=0: spin-up, not flagged)
    assert H.windows(ts, vals, 0, 5) == [{"t0": 54, "t1": 66, "frames": 3, "worst": 12}]  # one frame between: joined
    vals[5:7] = [1, 12]
    assert len(H.windows(ts, vals, 0, 5)) == 2  # two between: two spells
    assert H.out_of(3, 0, 5) == 0 and H.out_of(-2, 0, None) == -2 and H.out_of(7, None, 5) == 2
    frames = [{k: 1.0 for k in H.ENVELOPES} | {"t": t} for t in ts]
    for f in frames:
        f.update(land_pct=30, cont_pct=40, cont_km=35, plates=10, ocean_age=60, speed=4, temp=15, dry_pct=30,
                 inland_pct=15, lake_pct=1, trees_pct=30, npp=400, landmasses=20, largest_pct=15)
    frames[3]["max_elev_km"] = 11.0
    r = {"seed": 7, "level": 6, "frames": frames,
         "checks": {"dT_range": 3, "peak_frames": 1, "giant_lake_frames": 0, "volume_ratio": 1.0,
                    "sea_ice_below_150": 0, "low_plates": 0}}
    got = {(o["metric"], o["t0"]) for o in H.outliers(r)}
    assert got == {("max_elev_km", 58), ("peak_frames", None)}
