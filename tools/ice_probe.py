"""The run's ice rule on Earth's bed at a fixed global temperature (PW-308).

    uv run python tools/ice_probe.py 0 -6 -9 [--iters 8] [--start earth|none] [--level 6]

Runs earth.ice_sheets, as earth.update_climate does every climate step
(climate.compute on the bed as the ice presses it down, glacial isostasy
settled at once), on Earth's L6 bed at each dT (C against today's Earth),
starting from Earth's real ice (or none). Sea level stays fixed. A fixed
planet, so unlike a run it isn't chaotic: a quick check of how the ice
rule and the climate answer cooling. Prints, per climate update, the sea
level from the ice (m), the ice share of the surface (%) and the mean / max
thickness (m), and after the last update the iced cells and their mean
snowfall (mm/yr) on Antarctica, Greenland and elsewhere (--regions). Earth
for scale: today ~3% of the surface (Antarctica ~950 L6 cells, Greenland
~150); the last glacial maximum (~dT -6) ~120 m below today.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps)
import numpy as np  # noqa: E402
from planet import climate, timezoom  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.tectonics import earth  # noqa: E402
from planet.tectonics.isostasy import ice_load, land_view  # noqa: E402
from planet.tectonics.params import Params  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dT", type=float, nargs="+")
    ap.add_argument("--iters", type=int, default=8, help="climate updates")
    ap.add_argument("--start", choices=("earth", "none"), default="earth")
    ap.add_argument("--regions", action="store_true", help="per region iced cells and snowfall at the end")
    ap.add_argument("--level", type=int, default=6, help="grid level (Earth resampled onto it)")
    a = ap.parse_args()
    src = timezoom.source_earth(a.level)
    g = src["grid"]
    bed0 = src["elev"] + ice_load(g, src["ice"])  # (ETOPO's bed is pressed down by today's ice: unload it)
    p = Params()
    p.tilt = 23.44
    cell = 4 * np.pi / g.n
    for dT in a.dT:
        ice = src["ice"].copy() if a.start == "earth" else np.zeros(g.n)
        sim = SimpleNamespace(grid=g, params=p, cell_area=cell, precip=None, p_jul=None, p_jan=None)
        rows = []
        for _ in range(a.iters):
            bed = bed0 - ice_load(g, ice)
            e, ice0, _ = land_view(bed, np.where(bed0 > 0, ice, 0.0))
            land = e > 0
            c = climate.compute(g, e, dT, p.tilt, np.where(land, ice0, 0.0))
            sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
            ice = earth.ice_sheets(sim, land, e, c["ground"], ice0, ice_load(g, ice), marine=earth.marine_view(bed, c))
            on = ice > 0
            sl = -0.9 * (ice[land] / 1000).sum() / max((~land).sum(), 1) * 1000
            rows.append(f"{sl:7.1f} m {100 * on.mean():5.2f}% {ice[on].mean() if on.any() else 0:5.0f}/{ice.max():5.0f}")
        print(f"dT {dT:+5.1f}:  " + " | ".join(rows), flush=True)
        if a.regions:
            ant = g.lat < -60
            grl = (g.lat > 58) & (g.lon > -75) & (g.lon < -10)
            out = []
            for name, m in (("Antarctica", ant), ("Greenland", grl), ("elsewhere", ~ant & ~grl)):
                on = m & (ice > 0)
                snow = c["precip"][on].mean() if on.any() else 0.0
                out.append(f"{name} {on.sum()} cells, {snow:.0f} mm/yr")
            print("           " + ", ".join(out), flush=True)


if __name__ == "__main__":
    main()
