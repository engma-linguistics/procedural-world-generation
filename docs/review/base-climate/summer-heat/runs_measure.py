"""Lane 121: late-run land climate of the L6 sanity seeds: runs_measure.py STORE [STORE ...]

Means over keyframes from 800 to 1000 Myr: dT (frame stats), arid % (Koppen B on ice-free land), warm month
(max of the July and January layers, 1 C steps) by band and its >=30 / >=35 land shares."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, timeline  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from tools.earth_data import cell_areas  # noqa: E402

B_IDS = [i for i, c, _, _ in climate.KOPPEN if c.startswith("B")]
for store in sys.argv[1:]:
    for rd in sorted(p.parent for p in (Path(store) / "runs").glob("*/run.json")):
        run, arr = timeline.load_frames(rd, ("elevation", "ice", "temperature_jul", "temperature_jan", "climate"))
        g = build_grid(run["meta"]["level"])
        w, alat = cell_areas(g), np.abs(g.lat)
        fr = run["frames"]
        idx = [i for i, f in enumerate(fr) if 800 <= f["t"] <= 1000]
        out = {k: [] for k in ("dT", "arid", "ge30", "ge35", "w0_20", "w20_40", "w40_60")}
        for i in idx:
            el, ice = (timeline.frame(run, arr, k, i, g) for k in ("elevation", "ice"))
            tw = np.maximum(*(timeline.frame(run, arr, k, i, g) for k in ("temperature_jul", "temperature_jan")))
            k = timeline.frame(run, arr, "climate", i, g)
            m = (el > 0) & (ice <= 0)

            def wm(x, b):
                return float((x * w)[b].sum() / w[b].sum())
            st = fr[i].get("stats", fr[i])
            out["dT"].append(float(st.get("global_temp_c", np.nan)) - timeline.T_REF_C)
            out["arid"].append(100 * wm(np.isin(k, B_IDS) * 1.0, m))
            out["ge30"].append(100 * wm((tw >= 30) * 1.0, m))
            out["ge35"].append(100 * wm((tw >= 35) * 1.0, m))
            for lo, hi in ((0, 20), (20, 40), (40, 60)):
                out[f"w{lo}_{hi}"].append(wm(tw, m & (alat >= lo) & (alat < hi)))
        print(f"{rd.name} {run['name']:16} frames {len(idx)} " + " ".join(
            f"{k} {np.nanmean(v):.1f}" for k, v in out.items()))
