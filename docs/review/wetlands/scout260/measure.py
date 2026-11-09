"""measure.py DATA_ROOT: health's per-frame measures of each forked run, frames after the fork (t > 200):
inland median (p10-p90), lakes % of land (mean), largest lake median, giant-lake frames % (largest > 1 Mkm2), the
same over t >= 300 (health's window), as a table sorted by name; also writes measure.json."""
import json
import sys
from pathlib import Path

import numpy as np
sys.path.insert(0, str(Path.cwd()))
from tools import health as Hh
from planet.hydrology import discharge as _dis

Hh.MEASURE_LAYERS = tuple(Hh.MEASURE_LAYERS) + tuple(k for k in ("flow",) if k not in Hh.MEASURE_LAYERS)
_mf = Hh.measure_frame


def _measure_frame(grid, L, stats):
    out = _mf(grid, L, stats)
    elev = np.asarray(L["elevation"], float)
    land = Hh.is_land(elev, grid=grid)
    down = np.asarray(L["downstream"]).astype(np.int64)
    mouth = land & (down >= 0) & ~land[np.maximum(down, 0)]
    out["sea_q"] = float(_dis(grid, np.asarray(L["flow"], float)[mouth]).sum())  # m3/s into the sea
    return out


Hh.measure_frame = _measure_frame

root = Path(sys.argv[1])
rows = {}
for rd in sorted((root / "runs").iterdir()):
    try:
        head = json.loads((rd / "run.json").read_text())
    except Exception:
        continue
    if head.get("status") == "running" or "frames" not in head:
        continue
    r = Hh.measure_run(rd)
    fr = [f for f in r["frames"] if f["t"] > 200 + 1e-6 and f["inland_pct"] is not None]
    v = np.array([f["inland_pct"] for f in fr])
    mx = np.array([f["lake_max_mkm2"] for f in fr])
    late = np.array([f["lake_max_mkm2"] for f in fr if f["t"] >= 300])
    rows[head["name"]] = dict(id=rd.name, n=len(fr), inland=float(np.median(v)), p10=float(np.percentile(v, 10)),
                              p90=float(np.percentile(v, 90)), lakes=float(np.mean([f["lake_pct"] for f in fr])),
                              lmax=float(np.median(mx)), giant=float(100 * (mx > 1).mean()),
                              giant300=float(100 * (late > 1).mean()), ngiant=int((mx > 1).sum()),
                              secs=head["meta"].get("generated_in_s"),
                              sea_q=float(np.mean([f["sea_q"] for f in fr])))
for k in sorted(rows):
    d = rows[k]
    print(f"{k:16s} {d['id']} n={d['n']} inland {d['inland']:.1f} ({d['p10']:.1f}-{d['p90']:.1f}) lakes {d['lakes']:.2f}% "
          f"lmax {d['lmax']:.2f} giant {d['giant']:.1f}% ({d['ngiant']}) giant>=300 {d['giant300']:.1f}% sea_q {d['sea_q']/1e3:.0f}k {d['secs']} s")
(Path(sys.argv[1]).parent / "measure.json").write_text(json.dumps(rows, indent=1))
