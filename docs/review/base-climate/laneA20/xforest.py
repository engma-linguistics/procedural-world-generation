"""Cross test_glacial_cooling_turns_forest_to_tundra_and_cools_further: sim4 (L4, seed 1, 300 Myr) built with or
without _shelf_air (WORLD=on|off), then the test's numbers with or without it (CLIMATE=on|off).
usage: WORLD=on CLIMATE=off uv run python xforest.py"""
import os, sys
WT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", ".."))
sys.path.insert(0, WT)
sys.path.insert(0, os.path.join(WT, "tests"))
from planet import climate  # planet before numpy
import numpy as np

_orig = climate._shelf_air


def toggle(on):
    climate._shelf_air = _orig if on else (lambda grid, ocean, sst, *a, **k: sst)


toggle(os.environ.get("WORLD", "on") == "on")
from conftest import run_sim
from planet import timezoom as Z
from planet.timezoom.plants import Plants
from planet.timezoom.geometry import geometry

sim4 = run_sim()
toggle(os.environ.get("CLIMATE", "on") == "on")
src = Z.source_from_sim(sim4)
g, tilt = src["grid"], src["tilt"]
elev, H = np.asarray(src["elev"], float), np.maximum(np.asarray(src["ice"], float), 0.0)
grounded = (H > 1.0) & (elev > 0)
surf = np.where(grounded, elev + H, elev)
pl = Plants(g, src, Z.TZParams(), tilt, geometry(g)["area"])


def compute(dT):
    return lambda veg: climate.compute(g, surf, src["dT"] + dT, tilt, veg=veg)


pl.step(0.0, compute(0.0)(None), surf, grounded, H, 0.0, compute(0.0))
tree0 = pl.tree.copy()
c = compute(-4.0)(pl.feedback(grounded))
t0 = c["temp"].copy()
c = pl.step(10.0, c, surf, grounded, H, -1.0, compute(-4.0))
lost = (surf > 0) & ~grounded & (np.abs(g.lat) > 40) & (tree0 - pl.tree > 0.2)
print(f"WORLD={os.environ.get('WORLD', 'on')} CLIMATE={os.environ.get('CLIMATE', 'on')} run dT {src['dT']:+.2f}: "
      f"lost {lost.sum()} (>= 5), dtemp {(c['temp'] - t0)[lost].mean():+.2f} (< -0.1), "
      f"F {pl.series[-1]['F_wm2']:+.3f} W/m2 (< 0), dT_target {pl.dT_target:+.3f} (< 0)")
