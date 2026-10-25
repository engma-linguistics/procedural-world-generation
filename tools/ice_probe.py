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

Hysteresis probe (PW-555 stage 0):

    uv run python tools/ice_probe.py --stair 0 -2 -4 -6 -8 -10 -8 -6 -4 -2 0 2 4 6 [--iters 4]
        [--source DIR/seed11_L6_at400.pkl] [--json OUT.json] [--plot OUT.png]

walks dT down and back up as a staircase, carrying the ice from step to step (each step --iters climate
updates, as a run's), so the ice going in and coming out can be compared at the same dT: the gap between
the two legs is the rule's hysteresis, and the dT where the cold leg's extra ice is gone is the planet's
way out of a cold era. Per step it prints the sea level from ice, the iced share of the land, the
snowfall on the ice and the sheets' total snow gain (the moisture brake: Chandler & Sohl 2000's starving
accumulation as the air cools and the sea freezes), the frozen sea and the ice's lowest latitude.
--source: a generated planet's moment (tools/ice_diag.py --moments) instead of Earth; the steps are then
offsets from the moment's own dT.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import planet  # noqa: E402,F401  (first: its thread caps)
import numpy as np  # noqa: E402
from planet import climate, ocean, timezoom  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.tectonics import earth  # noqa: E402
from planet.tectonics.isostasy import ice_load, land_view  # noqa: E402
from planet.tectonics.params import Params  # noqa: E402


def _source(path, level):
    """(grid, bed unloaded of its ice, ice, the moment's dT, tilt) for Earth or a pickled moment."""
    if path is None:
        src = timezoom.source_earth(level)
        return src["grid"], src["elev"] + ice_load(src["grid"], src["ice"]), src["ice"], 0.0, 23.44
    import pickle
    from planet.grid import build_grid
    src = pickle.loads(Path(path).read_bytes())
    g = build_grid(src["level"])
    return g, src["elev"] + ice_load(g, src["ice"]), src["ice"], float(src["dT"]), float(src["tilt"])


def stair(a):
    """The hysteresis staircase (see the module's docstring)."""
    from planet import icemass
    g, bed0, ice_start, dT0, tilt = _source(a.source, a.level)
    p = Params()
    p.tilt = tilt
    cell = 4 * np.pi / g.n
    ice = ice_start.copy() if a.start == "earth" else np.zeros(g.n)
    sim = SimpleNamespace(grid=g, params=p, cell_area=cell, precip=None, p_jul=None, p_jan=None)
    rows = []
    for dT in a.stair:
        for _ in range(a.iters):
            bed = bed0 - ice_load(g, ice)
            e, ice0, _ = land_view(bed, np.where(bed0 > 0, ice, 0.0))
            land = e > 0
            c = climate.compute(g, e, dT0 + dT, p.tilt, np.where(land, ice0, 0.0))
            sim.precip, sim.p_jul, sim.p_jan = c["precip"], c["p_jul"], c["p_jan"]
            ice = earth.ice_sheets(sim, land, e, c["ground"], ice0, ice_load(g, ice),
                                   marine=earth.marine_view(bed, c))
        on = (ice > 0) & land
        sl = -0.9 * (ice[land] / 1000).sum() / max((~land).sum(), 1) * 1000
        il = np.where(land, ice, 0.0)
        smb, _ = icemass.balance(g.lat, land, c["ground"][0], c["ground"][1], sim.p_jul, sim.p_jan, il,
                                 icemass.sheet_cover(g, il), tilt=p.tilt)
        gain = float(np.maximum(smb, 0)[on].sum()) * 0.917 * 0.9 / max((~land).sum(), 1) * 1000.0  # m SL/kyr
        frozen = (~land) & (c["sea_ice_growth"] > 0.05)  # (sea that freezes in winter)
        r = {"dT": dT, "sea_ice": round(float(sl), 1), "ice_pct": round(100 * float(on.mean()), 2),
             "iced_land_pct": round(100 * float(on.sum()) / max(int(land.sum()), 1), 2),
             "snow_on_ice": round(float(c["precip"][on].mean()), 0) if on.any() else 0.0,
             "snow_gain": round(gain, 3), "precip": round(float(c["precip"].mean()), 0),
             "frozen_sea_pct": round(100 * float(frozen.sum()) / max(int((~land).sum()), 1), 1),
             "lat_min": round(float(np.abs(g.lat[on]).min()), 1) if on.any() else None}
        rows.append(r)
        print(f"dT {dT:+5.1f}: ice {r['sea_ice']:7.1f} m, {r['iced_land_pct']:5.1f}% of land, snow on ice "
              f"{r['snow_on_ice']:4.0f} mm, gain {r['snow_gain']:.2f} m/kyr, rain {r['precip']:.0f} mm,"
              f" frozen sea {r['frozen_sea_pct']}%, ice to {r['lat_min']} deg", flush=True)
    if a.json:
        import json
        Path(a.json).write_text(json.dumps({"source": a.source or "earth", "dT0": dT0, "iters": a.iters,
                                            "rows": rows}, indent=1))
    if a.plot:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        x = [r["dT"] for r in rows]
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        ax[0].plot(x, [r["sea_ice"] for r in rows], "-o", ms=3, color="#2a6fdb")
        for i in range(len(x) - 1):
            ax[0].annotate("", (x[i + 1], rows[i + 1]["sea_ice"]), (x[i], rows[i]["sea_ice"]),
                           arrowprops=dict(arrowstyle="->", color="#2a6fdb", lw=0.6))
        ax[0].set_xlabel("dT (C)")
        ax[0].set_ylabel("sea level from ice (m)")
        ax[1].plot(x, [r["snow_on_ice"] for r in rows], "-o", ms=3, color="#3a9a4a", label="snow on ice (mm/yr)")
        ax[1].plot(x, [r["frozen_sea_pct"] * 10 for r in rows], "-o", ms=3, color="#888888",
                   label="frozen sea (% x10)")
        ax[1].set_xlabel("dT (C)")
        ax[1].legend(fontsize=8)
        fig.suptitle(f"hysteresis staircase: {a.source or 'Earth'} ({a.iters} climate updates per step)")
        fig.tight_layout()
        fig.savefig(a.plot, dpi=90)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("dT", type=float, nargs="*")
    ap.add_argument("--stair", type=float, nargs="*", help="the hysteresis staircase's dT steps (C)")
    ap.add_argument("--source", help="a pickled moment (tools/ice_diag.py --moments) instead of Earth")
    ap.add_argument("--json")
    ap.add_argument("--plot")
    ap.add_argument("--iters", type=int, default=8, help="climate updates")
    ap.add_argument("--start", choices=("earth", "none"), default="earth")
    ap.add_argument("--regions", action="store_true", help="per region iced cells and snowfall at the end")
    ap.add_argument("--level", type=int, default=6, help="grid level (Earth resampled onto it)")
    a = ap.parse_args()
    if a.stair:
        return stair(a)
    src = timezoom.source_earth(a.level)
    g = src["grid"]
    bed0 = src["elev"] + ice_load(g, src["ice"])  # (ETOPO's bed is pressed down by today's ice: unload it)
    p = Params()
    p.tilt = 23.44
    cell = 4 * np.pi / g.n
    w = ocean.cell_area_km2(g)
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
            aw = float((on * w).sum() / w.sum())  # (the area-weighted share: earth.EARTH_ICE's, PW-873)
            rows.append(f"{sl:7.1f} m {100 * on.mean():5.2f}% (area {100 * aw:5.3f}%) "
                        f"{ice[on].mean() if on.any() else 0:5.0f}/{ice.max():5.0f}")
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
