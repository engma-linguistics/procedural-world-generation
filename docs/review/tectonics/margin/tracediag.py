"""margindiag.py plus a land, sea-level, sediment and CO2 trace (PW-950, lane 100d): where the land goes and why the
world cools when the sea floor's sediment creeps (slope_k), and what removes the start-up shelves (80-200 Myr).

Adds to each recorded step a "trace" dict:
- every step: land / cont % of the surface, sea_level / sea_tect / sea_cont (m), the CO2 source and sink against their
  references (rates / refs), pco2, the weathering supply (km of bare ground eroded on land per step, / scale^2), the
  sink per land cell, the creep's net km moved off continental crust onto oceanic (creep_c2o, this step, km x cells,
  / scale^2), the shelf share (0..-200 m, % of the ocean) and the shelf on continental crust
- hollow: % of the surface that is land below sea level (cut off from the sea, PW-1229)
- every 10 Myr, and every step over 80-200 Myr ("hyps"): the continental crust's area shares in elevation bands, its mean thickness and cover (km),
  the oceanic crust's mean cover (km), and ocean_sed_m: the mean m by which the oceanic crust's sediment raises its
  floor (water it displaces; sea level does not count it: earth.sea_tect reads the floor's age only), and the
  continental crust's budget by process so far (sim.budget, km x level-5 cells; "erosion" includes the creep), and
  sed_born / sed_born_sub / sed_born_med: continental crust of rock SEDIMENT (born from a sediment pile), % of the
  surface, its submerged part, its median elevation (m)
Run from the code checkout being judged (cwd), same arguments as ice_diag / margindiag. Harness only: reads the sim.
"""
import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import climate, surface  # noqa: E402
from planet.tectonics import diag  # noqa: E402
from planet.tectonics.isostasy import elevation, sediment_km  # noqa: E402
from planet.surface import SEDIMENT  # noqa: E402

_creep = surface._creep
_step = diag.Recorder.step
STASH = {"cont": None, "c2o": 0.0}
BANDS = (500, 200, 0, -60, -200, -400, -1000)


def creep(h, iso, movable, ea, eb, k, dref, n_sub):
    net = _creep(h, iso, movable, ea, eb, k, dref, n_sub)
    c = STASH["cont"]
    if c is not None and len(c) == len(net):
        STASH["c2o"] += float(-net[c].sum())  # (net sums to 0: what continental cells lost net went to oceanic)
    return net


surface._creep = creep

from planet.tectonics import earth  # noqa: E402
_gt = earth.global_temperature


def global_temperature(sim, growth, newc, rng, plume=None):
    # (the CO2 source's parts this step, before the drift: ridge (new floor), arc (20 x the arcs' nominal growth,
    # the slab's melt: crust.arc_growth), plume; lane 100e)
    out = _gt(sim, growth, newc, rng, plume=plume)
    STASH["parts"] = (newc * (sim.dt / sim.dt_now) / sim.scale**2, 20.0 * float(growth.sum()) / sim.scale**2,
                      float(sim.plume_src))
    return out


earth.global_temperature = global_temperature

from planet.tectonics import crust  # noqa: E402
_ag = crust.arc_growth


def arc_growth(sim, bd, conv, thermostat):
    # (the slab: trench edges subducting now (conv > 0), their mean convergence, and their sum, per scale^2)
    c = bd.at_trenches(conv)
    on = c > 0
    STASH["slab"] = (int(on.sum()) / sim.scale**2, float(c[on].mean()) if on.any() else 0.0,
                     float(c.sum()) / sim.scale**2, int(len(np.unique(bd.overriding[on]))) / sim.scale**2)
    return _ag(sim, bd, conv, thermostat)


crust.arc_growth = arc_growth
_birth, _coh = crust.birth_and_cratons, crust.coherence
from planet.surface import HOTSPOT  # noqa: E402
from planet.tectonics.isostasy import BECOMES_CONT_KM, OCEAN_KM  # noqa: E402
# (PW-1292, lane 112: births by kind, cumulative cells / scale^2: arc, sediment pile next to its plate's continent,
# isolated pile (a candidate at 20 km; born or not), isolated pile born, isolated candidate on a hotspot, and the
# coherence shreds: all, and of continental rock SEDIMENT)
BIRTHS = dict.fromkeys(("arc", "pile_touch", "pile_iso_cand", "pile_iso_born", "pile_iso_hot", "shred", "shred_sed"), 0.0)


def birth_and_cratons(sim, col, arcky, squeezed):
    t, cont, rock = col.t, col.cont, col.rock.copy()
    sedim = (col.cover > 0.5 * (t - OCEAN_KM)) | (col.cover > 0.8 * sim.params.metamorphic_depth)
    cand = ~cont & (t >= BECOMES_CONT_KM) & ((rock != HOTSPOT) | sedim)
    touch = crust.touches_own_continent(sim, cont)
    born = _birth(sim, col, arcky, squeezed)
    k = 1.0 / sim.scale**2
    BIRTHS["arc"] += k * int((born & ~sedim).sum())
    BIRTHS["pile_touch"] += k * int((born & sedim & touch).sum())
    BIRTHS["pile_iso_cand"] += k * int((cand & sedim & ~touch).sum())
    BIRTHS["pile_iso_born"] += k * int((born & sedim & ~touch).sum())
    BIRTHS["pile_iso_hot"] += k * int((cand & sedim & ~touch & (rock == HOTSPOT)).sum())
    return born


def coherence(sim, col, trench=None):
    rock = col.rock.copy()
    weld, shred = _coh(sim, col, trench)
    BIRTHS["shred"] += int(shred.sum()) / sim.scale**2
    BIRTHS["shred_sed"] += int((shred & (rock == SEDIMENT)).sum()) / sim.scale**2
    return weld, shred


crust.birth_and_cratons, crust.coherence = birth_and_cratons, coherence


def step(self, sim):
    _step(self, sim)
    rec = self.steps[-1]
    land = sim.land()
    cont = sim.w_cont
    e = sim.bed()
    sea = e <= 0
    se = e[sea]
    tr = {"land": round(100 * float(land.mean()), 2), "cont": round(100 * float(cont.mean()), 2),
          "sl": round(float(sim.sea_level), 1), "st": round(float(sim.sea_tect), 1),
          "sc": round(float(sim.sea_cont), 1),
          "shelf": round(100 * float((se > -200).mean()), 2),
          "shelf_c": round(100 * float((sea & cont & (e > -200)).sum() / max(sea.sum(), 1)), 2),
          "c2o": round(STASH["c2o"] / sim.scale**2, 4)}
    STASH["c2o"] = 0.0
    STASH["cont"] = cont.copy()
    if sim.rates is not None and sim.refs is not None:
        tr["src"], tr["sink"] = [round(float(v), 4) for v in sim.rates]
        tr["src_ref"], tr["sink_ref"] = [round(float(v), 4) for v in sim.refs]
    if "parts" in STASH:
        tr["ridge"], tr["arc"], tr["plume"] = [round(float(v), 2) for v in STASH["parts"]]
    if "slab" in STASH:
        tr["trench_n"], tr["conv"], tr["conv_sum"], tr["over_n"] = [round(float(v), 3) for v in STASH["slab"]]
    tr["births"] = {k: round(v, 2) for k, v in BIRTHS.items()}
    tr["pco2"] = round(float(climate.pco2(sim.co2)), 1)
    if sim.weathered is not None:
        sup = np.asarray(sim.weathered) * land
        tr["supply"] = round(float(sup.sum()) / sim.scale**2, 4)
        tr["supply_per_land"] = round(float(sup.sum()) / max(int(land.sum()), 1) * 1e3, 4)
    if sim.temp is not None:
        tr["t_land"] = round(float(np.mean(sim.temp[land])), 2)
    tr["thermo"] = [round(float(v), 3) for v in np.ravel(sim.thermo)]
    tr["cvol"] = round(float((sim.w_thick * cont).mean()), 3)
    t = float(sim.t)
    tr["hollow"] = round(100 * float((land & sea).mean()), 2)  # (ground below the sea cut off from it: land, PW-1229)
    if abs(t / 10 - round(t / 10)) < 1e-6 or 80 <= t <= 200:
        a = cont
        ec = e[a]
        edges = (np.inf,) + BANDS + (-np.inf,)
        tr["hyps"] = [round(100 * float(((ec <= edges[i]) & (ec > edges[i + 1])).mean()), 2) for i in range(len(edges) - 1)]
        tr["c_thick"] = round(float(sim.w_thick[a].mean()), 2)
        cov = np.asarray(sim.w_cover)
        tr["c_cover"] = round(float(cov[a].mean()), 3)
        tr["c_cover_sea"] = round(float(cov[a & sea].mean()), 3) if (a & sea).any() else 0.0
        tr["o_cover"] = round(float(cov[~a].mean()), 3)
        o = ~a
        x = sim.w_extra
        sed = sediment_km(cov, x)
        e1 = elevation(sim.w_thick[o], sim.w_age[o], cont[o], sim.w_rock[o], 0.0, sed[o])
        e0 = elevation(sim.w_thick[o] - sed[o], sim.w_age[o], cont[o], sim.w_rock[o], 0.0, 0 * sed[o])
        tr["ocean_sed_m"] = round(float((e1 - e0).mean()), 1)
        sb = a & (sim.w_rock == SEDIMENT)  # (continental crust born from a sediment pile, crust.birth_and_cratons)
        tr["sed_born"] = round(100 * float(sb.mean()), 2)  # % of the surface
        tr["sed_born_sub"] = round(100 * float((sb & sea).mean()), 2)
        tr["sed_born_med"] = int(np.median(e[sb])) if sb.any() else 0
        tr["budget"] = {k: round(float(v), 1) for k, v in sim.budget.items()}
    rec["trace"] = tr


diag.Recorder.step = step
here = Path(__file__).resolve().parent
sys.argv = [str(here / "margindiag.py")] + sys.argv[1:]
runpy.run_path(sys.argv[0], run_name="__main__")
