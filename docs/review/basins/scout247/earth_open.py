"""Earth L6 through the model's hydrology with and without the HydroSHEDS closed basins / outlets imposed.
Nothing is saved (tools.earth_world.build returns the world dict)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import planet  # noqa
import numpy as np
from tools import earth_world as EW
from tools import health as Hh
from tools.scorecard import GROUP
from planet.grid import build_grid
from planet.geo import is_land
from planet import store as S

lvl = int(sys.argv[1]) if len(sys.argv) > 1 else 6
grid = build_grid(lvl)


def layer(w, name):
    return np.asarray(S.decode(np.asarray(w["layers"][name]["data"]) if isinstance(w["layers"][name], dict) and "data" in w["layers"][name] else w["layers"][name], None, grid)) if False else w["_raw"][name]


def measure(w, label):
    L = w["layers"]
    get = lambda k: np.asarray(L[k]["values"] if isinstance(L[k], dict) and "values" in L[k] else L[k])
    elev = get("elevation").astype(float); ice = get("ice").astype(float)
    land = is_land(elev, grid=grid); free = land & (ice <= 0)
    down = get("downstream").astype(np.int64); kind = get("lake_kind")
    real = Hh.real_hollows(grid, elev, kind)
    end = Hh.drain_ends(down, land)
    inland = land[end] & real[end]
    arid = GROUP[get("climate").astype(int)] == "B"
    nf = free.sum()
    print(f"{label}: inland {100*(inland&free).sum()/nf:.1f}% raw {Hh.inland_share(down, land, free):.1f}% "
          f"| arid (model) {100*(arid&free).sum()/nf:.1f}% of land; arid draining inland {100*(arid&inland&free).sum()/max(1,(arid&free).sum()):.1f}% "
          f"| inland that is arid {100*(arid&inland&free).sum()/max(1,(inland&free).sum()):.1f}%", flush=True)


w = EW.build(lvl)
print("layer type:", type(w["layers"]["elevation"]), (list(w["layers"]["elevation"].keys())[:5] if isinstance(w["layers"]["elevation"], dict) else ""))
measure(w, "Earth, HydroSHEDS closed + outlets (as stored)")
EW.earth_closed = lambda g: None
measure(EW.build(lvl), "Earth, outlets only, no closed basins imposed")
EW.earth_outlets = lambda g: None
measure(EW.build(lvl), "Earth, neither (terrain + climate only, as a generated world)")
