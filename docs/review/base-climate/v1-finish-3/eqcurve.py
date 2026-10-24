"""The ice's equilibrium against dT on one planet at two resolutions (PW-725): an L7 run's checkpoint, and the same
planet averaged onto the L6 grid (L6's cells are L7's first n6 vertices; each L6 cell = the mean of the L7 cells
nearest it). At a fixed dT the climate and the ice sheets are updated N times (as update_climate: climate.compute on
the ice-loaded bed, then earth.ice_sheets, then the load), from no ice or from the checkpoint's ice; vegetation
held at the checkpoint's. Read only. Variants:
  L7       the checkpoint's own L7 fields
  L7s      L7 grid, every field (elevation included) its L6 parent's mean: the L6 planet on the L7 grid
  L6       the averaged planet on the L6 grid
Usage (repo root): uv run python docs/review/base-climate/v1-finish-3/eqcurve.py RUN_DIR T "dT..." [N] [--from-ice]"""
import os
import sys

sys.path[:0] = [os.getcwd()]
import planet  # noqa: E402,F401  (first: thread caps before numpy's BLAS)
import json  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402
from types import SimpleNamespace  # noqa: E402

import numpy as np  # noqa: E402

from planet import climate, icemass, store  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.tectonics import earth  # noqa: E402
from planet.tectonics.isostasy import ice_load, land_view  # noqa: E402
from planet.tectonics.params import Params  # noqa: E402
from planet.tectonics.simulation import Simulation  # noqa: E402


def patch_margin(km):
    """Test only (MARGIN_KM): the margin band, whose snow and melt are its edge's, is the old ice within km of bare
    land (rings = round(km / cell spacing)), not one ring whatever the cell size."""
    import inspect
    src = inspect.getsource(earth._ice_pass)
    old = "bare_nb = np.add.reduceat((land & (old <= 0))[g.nbr_idx], g.nbr_off[:-1]) > 0"
    assert old in src
    new = ("bare_nb = land & (old <= 0)\n"
           "    for _r in range(max(1, int(round(MARGIN_KM / (g.spacing * R_KM))))):\n"
           "        bare_nb = bare_nb | (np.add.reduceat(bare_nb[g.nbr_idx], g.nbr_off[:-1]) > 0)")
    ns = earth.__dict__
    ns["MARGIN_KM"] = km
    exec(compile(src.replace(old, new), earth.__file__, "exec"), ns)


if os.environ.get("MARGIN_KM"):
    patch_margin(float(os.environ["MARGIN_KM"]))


def make(grid, params, e, ice, veg_frac, veg_lai):
    return SimpleNamespace(grid=grid, params=params, e=e, ice=ice, ice_sink=ice_load(grid, ice), veg_frac=veg_frac,
                           veg_lai=veg_lai, rain_state=None, t=500.0, cell_area=4 * np.pi / grid.n,
                           precip=None, p_jul=None, p_jan=None)


def update(s, dT):
    """earth.update_climate's climate and ice part, at dT."""
    g, p = s.grid, s.params
    bed = s.e - s.ice_sink
    e, ice0, _ = land_view(bed, np.where(s.e > 0, s.ice, 0.0))
    land = e > 0
    veg = earth.vegetation.feedback(s.veg_frac, s.veg_lai)
    c = climate.compute(g, e, dT, p.tilt, np.where(land, ice0, 0.0), veg=veg, rain_start=s.rain_state)
    s.rain_state = c["rain_state"]
    s.temp, s.precip, s.p_jul, s.p_jan = c["temp"], c["precip"], c["p_jul"], c["p_jan"]
    marine, info = earth.marine_view(bed, c), {}
    s.ice = earth.ice_sheets(s, land, e, c["ground"], ice0, s.ice_sink, info, marine=marine)
    ice = np.where(land, s.ice, 0.0)
    vol = (ice / 1000.0).sum() * s.cell_area * R_KM**2
    ocean = (~land).sum() * s.cell_area * R_KM**2
    t_warm, t_cold, _ = c["ground"]
    smb0, _ = icemass.balance(g.lat, land, t_warm, t_cold, s.p_jul, s.p_jan, 0.0, 0.0, tilt=p.tilt)
    s.ice_sink = ice_load(g, s.ice)
    nl = max(int(land.sum()), 1)
    return {"sea_ice": round(-0.9 * vol / ocean * 1000.0, 1), "ice_frac": round(float((s.ice > 0).mean()), 4),
            "iced_land": round(float((land & (ice > 0)).sum()) / nl, 4),
            "snow_land": round(float((land & (smb0 > 0)).sum()) / nl, 4),
            "temp": round(float(c["temp"].mean()), 2), "temp_land": round(float(c["temp"][land].mean()), 2),
            "land": round(float(land.mean()), 4), "passes": info.get("passes"),
            "e_land_mean": round(float(e[land].mean())), "e_land_p99": round(float(np.percentile(e[land], 99)))}


def main():
    run_dir, t, dts = Path(sys.argv[1]), float(sys.argv[2]), [float(x) for x in sys.argv[3].split()]
    n_up = int(sys.argv[4]) if len(sys.argv) > 4 and not sys.argv[4].startswith("--") else 6
    from_ice = "--from-ice" in sys.argv
    variants = [a.split("=")[1].split(",") for a in sys.argv if a.startswith("--only=")]
    variants = variants[0] if variants else ["L7", "L7s", "L6"]
    meta = json.loads((run_dir / "run.json").read_text())["meta"]
    g7, g6 = build_grid(7), build_grid(6)
    params = Params(**meta["params"])
    sim = Simulation.from_state(g7, meta["seed"], params, meta["dt"], store.load_checkpoint(run_dir, t, g7))
    print("checkpoint dT", round(float(sim.dT), 3), "sea_ice", round(float(sim.sea_ice), 1), flush=True)
    e7 = np.asarray(sim.w_elev, float)
    ice7 = np.asarray(sim.ice, float) if from_ice else np.zeros(g7.n)
    vf7, vl7 = np.asarray(sim.veg_frac, float), np.asarray(sim.veg_lai, float)
    par = g6.locate(g7.centers)  # each L7 cell's L6 cell
    cnt = np.bincount(par, minlength=g6.n)

    def down(f):  # L7 -> L6 cell means (last axis)
        if f.ndim == 1:
            return np.bincount(par, weights=f, minlength=g6.n) / cnt
        return np.stack([down(r) for r in f])

    def up(f6):
        return f6[..., par]

    e6, ice6, vf6, vl6 = down(e7), down(ice7), down(vf7), down(vl7)
    sims = {"L7": make(g7, params, e7, ice7, vf7, vl7),
            "L7s": make(g7, params, up(e6), up(ice6), up(vf6), up(vl6)),
            "L6": make(g6, params, e6, ice6, vf6, vl6)}
    out = {"run": run_dir.name, "t": t, "from_ice": from_ice, "res": {}}
    for dT in dts:
        for name in variants:
            s0 = sims[name]
            s = make(s0.grid, params, s0.e, s0.ice.copy(), s0.veg_frac, s0.veg_lai)
            recs = []
            for k in range(n_up):
                t0 = time.time()
                r = update(s, dT)
                r["sec"] = round(time.time() - t0, 1)
                recs.append(r)
                print(name, dT, k, r, flush=True)
            out["res"][f"{name} {dT:g}"] = recs
    tag = f"{run_dir.name}_{t:g}_{'ice' if from_ice else 'free'}_{'-'.join(variants)}_{'_'.join(f'{d:g}' for d in dts)}"
    Path(os.environ.get("OUT", ".")).joinpath(f"eq_{tag}.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
