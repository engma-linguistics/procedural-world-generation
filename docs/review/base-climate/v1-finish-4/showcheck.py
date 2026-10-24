"""Checks a showcase world (PW-202): its 'now' is an interglacial of its time zoom (PW-700), its resource and coast
layers exist, and its zooms carry islands (land masses not touching the zoom's edge) and resource deposits.
Read only. Usage (repo root, PLANET_DATA set): uv run python docs/review/base-climate/v1-finish-4/showcheck.py WORLD ..."""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401
import json  # noqa: E402

import numpy as np  # noqa: E402

from planet import store as S  # noqa: E402



def label(mask):
    """4-connected components of a 2-D mask: (labels, n)."""
    from collections import deque
    lab = np.zeros(mask.shape, np.int32)
    n = 0
    ny, nx = mask.shape
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n += 1
        lab[y0, x0] = n
        q = deque([(y0, x0)])
        while q:
            y, x = q.popleft()
            for yy, xx in ((y + 1, x), (y - 1, x), (y, x + 1), (y, x - 1)):
                if 0 <= yy < ny and 0 <= xx < nx and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    q.append((yy, xx))
    return lab, n


root = S.root()
for wid in sys.argv[1:]:
    w = json.loads((root / "worlds" / f"{wid}.json").read_text())
    m = w["meta"]
    tz = json.loads((root / "runs" / m["timezoom"] / "run.json").read_text())
    fr = tz["frames"]
    now = min(fr, key=lambda f: abs(f["t"] - m["timezoom_kyr"]))["stats"]
    I = np.array([f["stats"]["glacial_index"] for f in fr])
    vol = np.array([f["stats"]["ice_volume_mkm3"] for f in fr])
    res = sum(k.startswith("res_") for k in w["layers"])
    coast = all(k in w["layers"] for k in ("coast_type", "barrier", "cliff"))
    print(f"world {wid} (run {m['source_run']} @{m['t_myr']:g}, tz {m['timezoom']}): now {m['timezoom_kyr']:g} kyr "
          f"'{now['ice_age']}' index {now['glacial_index']:.2f} (tz range {I.min():.2f}..{I.max():.2f}), ice "
          f"{m['ice_volume_mkm3']:.1f} Mkm3 (tz {vol.min():.1f}..{vol.max():.1f}), sea level change "
          f"{m['sea_level_change_m']:+.0f} m, {m['global_temp_c']} C; res layers {res}, coast layers {coast}")
    for z in sorted((root / "zooms").iterdir()):
        zj = z / "zoom.json"
        if not zj.exists():
            continue
        d = json.loads(zj.read_text())
        if (d.get("source_world") or {}).get("id") != wid:
            continue
        L = d["layers"]["elevation"]
        e = np.fromfile(z / L["file"], L["dtype"]).reshape(L["shape"]) * L["scale"] + L["offset"]
        lab, n = label(e > 0)
        edge = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
        sizes = np.bincount(lab.ravel())[1:]
        islands = sum(1 for i in range(1, n + 1) if i not in edge and sizes[i - 1] >= 4)
        dep = len((d.get("resources") or {}).get("deposits", []))
        print(f"  zoom {d['id']} {d['size_km']:g} km @ {d['res_km']:g}: land {d['stats']['land_pct']:.0f}%, "
              f"islands {islands}, deposits {dep}, barrier px {d['stats'].get('barrier_px', 0)}")
