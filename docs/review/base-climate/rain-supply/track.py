"""track.py MAIN_CODE CAND_CODE ARM SEED OUT : run ARM's trajectory (main / cand) to 1000 Myr; at every climate update
also run the other arm's climate.compute on the same inputs, and record: overturning sites (both), and the
weathering sink each climate gives on this state (ln B/A), plus the 0-D parts of dT."""
import sys, json, copy, importlib.util
MAIN, CAND, ARM, SEED, OUT = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), sys.argv[5]
sys.path.insert(0, MAIN)
import planet  # noqa
import numpy as np
from planet import climate as climA
from planet.grid import build_grid
from planet.tectonics import Params, Simulation, earth
spec = importlib.util.spec_from_file_location("planet.climate_cand", f"{CAND}/planet/climate.py")
climB = importlib.util.module_from_spec(spec); sys.modules["planet.climate_cand"] = climB; spec.loader.exec_module(climB)
run_c = climB.compute if ARM == "cand" else climA.compute
oth_c = climA.compute if ARM == "cand" else climB.compute
sim = Simulation(build_grid(6), SEED, Params(run_end=1000.0, star_brightening=1.0, climate_offset=0.0005), 2.0)
rec = []
def sinkof(c, land):
    supply = sim.weathered * land
    warm = np.exp(earth.WEATHER_K * (c["temp"] - 15.0)) * (np.maximum(c["runoff"], 0.0) / earth.RUNOFF_REF) ** earth.WEATHER_RUNOFF
    return float((supply * warm * earth.plant_factor(sim.npp_w)).sum())
def icebits(a, b, land, ice, g):
    """same-state snow on the land ice and on the cold land: precip (mm/yr) and warm-half air over the ice, the
    precip on land whose warm half is below 5 C in A (where snow lasts), and that land's area (cells)"""
    on = land & (ice > 0)
    cold = land & (a["t_warm"] < 5.0)
    hi = land & (np.abs(np.degrees(g.lat) if np.abs(g.lat).max() <= 3.2 else g.lat) > 45)
    f = lambda x, m: round(float(x[m].mean()), 2) if m.any() else None
    return dict(n_ice=int(on.sum()), Pice_A=f(a["precip"], on), Pice_B=f(b["precip"], on),
                Twice_A=f(a["t_warm"], on), Twice_B=f(b["t_warm"], on), Twground_A=f(a["ground"][0], on),
                Twground_B=f(b["ground"][0], on), n_cold=int(cold.sum()), Pcold_A=f(a["precip"], cold),
                Pcold_B=f(b["precip"], cold), n_coldB=int((land & (b["t_warm"] < 5.0)).sum()),
                Phi_A=f(a["precip"], hi), Phi_B=f(b["precip"], hi), Twhi_A=f(a["t_warm"], hi), Twhi_B=f(b["t_warm"], hi))
def wrapped(g, e, dT, tilt, ice, **kw):
    kw_o = copy.deepcopy(kw)
    c = run_c(g, e, dT, tilt, ice, **kw)
    o = oth_c(g, e, dT, tilt, ice, **kw_o)
    land = climA.is_land(e, ice, g)
    a, b = (c, o) if ARM == "main" else (o, c)
    sa, sb = sinkof(a, land), sinkof(b, land)
    rec.append(dict(t=round(sim.t, 3), dT=round(float(sim.dT), 3), co2=round(float(sim.co2), 3), sea_ice=round(float(sim.sea_ice), 1),
                    sitesA=len(a["moc_sites"]), sitesB=len(b["moc_sites"]),
                    dln_sink=round(float(np.log(sb / sa)) if sa > 0 and sb > 0 else 0.0, 5),
                    landP_A=round(float(a["precip"][land].mean()), 1), landP_B=round(float(b["precip"][land].mean()), 1),
                    **icebits(a, b, land, ice, g)))
    return c
earth.climate.compute = wrapped
sim.run(1000.0)
json.dump(rec, open(OUT, "w"))
print("done", len(rec))
