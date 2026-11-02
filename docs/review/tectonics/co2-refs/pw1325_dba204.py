"""Lane 135, PW-1325: dba204's warm month before/after the finished frame's orbit at the seasons response (read-only).

    PLANET_DATA=<repo> PYTHONPATH=. uv run python docs/review/tectonics/co2-refs/pw1325_dba204.py

'before' is the old finish rule (the time zoom's own orbit_resp, 'run' for 56dee1: 0.25 C per W/m2 on land);
'after' is planet/finish.py::orbit_dt now ('seasons'). Both re-solve the world's climate on its stored elevation and
ice at its frame's dT with its plants (vegetation.coupled_climate's feedback), as lane 121's world_bands.py --orbit,
which reproduces the stored world under 'run'.
"""
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
import numpy as np  # noqa: E402
from planet import climate, finish as F, store as S, timezoom as TZ, vegetation, world  # noqa: E402
from tools.earth_data import cell_areas  # noqa: E402

w = world.load(S.find_world("dba204"))
L, g, wm_ = w["layers"], w["grid"], w["meta"]
tz_dir = S.find_run(wm_["timezoom"])
run = json.loads((tz_dir / "run.json").read_text())
i = F.frame_index(run, wm_["timezoom_kyr"])
st = F.frame_state(tz_dir, i)
m = run["meta"]
p = TZ.TZParams(**{k: v for k, v in m.get("timezoom", {}).items() if k in TZ.TZParams.__dataclass_fields__})
s = st["stats"]
print("tz orbit_resp", p.orbit_resp, "frame", run["frames"][i]["t"],
      {k: s[k] for k in ("obliquity", "eccentricity", "perihelion")})
land_tz = st["elevation"] + st["ice"] > 0
old = TZ.orbit_anomaly(g, (s["obliquity"], s["eccentricity"], s["perihelion"]), m["params"].get("tilt", 23.4),
                       dataclasses.replace(p, orbit_resp="run"), land_tz, st["ice"], None,
                       earth=m["source_run"] == "earth", phases=m.get("orbit_phases_deg"))
bright = np.clip(st["ice"] / p.snow_h, 0, 1)
for j, v in m.get("anchor", []):
    old[j] += v * bright[j]
new = F.orbit_dt(run, st)
elev = L["elevation"].astype(float)
ice = L.get("ice", np.zeros(g.n)).astype(float)
land = (elev > 0) | (ice > 0)
open_land = land & (ice <= 0)
alat = np.abs(g.lat)
area = cell_areas(g)
dT = float(st["dT"])
tilt = float(m["params"].get("tilt", 23.4))


def wm(x, msk):
    return float((x * area)[msk].sum() / area[msk].sum())


def row(tw, tag):
    bands = " / ".join(f"{wm(tw, open_land & (alat >= lo) & (alat < hi)):.1f}" for lo, hi in ((0, 20), (20, 40), (40, 60)))
    print(f"{tag:28s} warm 0-20/20-40/40-60 {bands}   land>=30 {100 * wm((tw >= 30) * 1.0, open_land):.1f}%"
          f"  >=35 {100 * wm((tw >= 35) * 1.0, open_land):.1f}%", flush=True)


row(L["warm_month"], "stored")
_, fb = vegetation.coupled_climate(g, elev, dT, tilt, ice)
for tag, d in (("before ('run', old finish)", old), ("after (finish now)", new), ("no orbit", None)):
    c = climate.compute(g, elev, dT, tilt, ice, veg=fb, orbit_dt=d)
    row(c["t_warm"], tag)
    if d is not None:
        print(f"{'':28s} |July anomaly| on 0-20 deg land {wm(np.abs(d[:, 3]), open_land & (alat < 20)):.2f} C")
