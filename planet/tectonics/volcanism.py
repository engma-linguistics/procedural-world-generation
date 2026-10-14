"""Hotspots (mantle plumes) and arc volcanoes.

Plumes are fixed in the mantle (= world frame) while plates slide over
them; arc volcanoes ride with their plate. Both are lists of dicts on the
simulation (sim.hotspots, sim.volcanoes) and part of its state.
"""

from __future__ import annotations

import numpy as np

from ..geo import R_KM
from . import mantle
from .isostasy import ISO_LAND, ISO_VOLCANO, OCEAN_KM, elevation
from ..surface import HOTSPOT


def hotspots(sim, rng, bd):
    """Mantle plumes: fixed in the mantle while plates slide over them, so
    each leaves a trail of volcanoes that drift away, erode and sink as
    their sea floor ages (Hawaii -> Emperor seamounts). A new plume's
    head arrives as a short, huge outpouring (flood basalts, like the
    Deccan Traps). Most plumes sit under ridges or rifts (Iceland,
    Galapagos, Afar: hot mantle and spreading plates find each other);
    the rest anywhere (Hawaii, mid-plate). Either way they rise from warm
    mantle more often than cold, and most from the edges of the big warm
    regions (mantle.plume_odds; Earth's plumes ring its two big warm
    regions under Africa and the Pacific).
    Returns (crust added per Myr, dome height in m) on each world cell."""
    p, g = sim.params, sim.grid
    sim.hotspots = [h for h in sim.hotspots if sim.t - h["born"] < h["life"]]
    n_new = rng.poisson(p.hotspots * sim.heat() * sim.dt / p.hotspot_life)
    if sim.step_no == 1:
        n_new = int(round(p.hotspots * sim.heat()))  # start with a full set, of mixed ages
    spreading = bd.spreading
    odds = mantle.plume_odds(sim) if n_new else None
    for _ in range(n_new):
        cells = spreading if len(spreading) and rng.random() < p.hotspot_at_ridges else np.arange(g.n)
        w = odds[cells]
        v = g.centers[rng.choice(cells, p=w / w.sum())] + rng.normal(size=3) * 100.0 / R_KM
        life = rng.uniform(0.4, 1.6) * p.hotspot_life
        born = sim.t - (rng.uniform(0, life) if sim.step_no == 1 else 0.0)
        sim.hotspots.append({"pos": v / np.linalg.norm(v), "born": born, "life": life,
                             "strength": rng.uniform(0.5, 1.5)})
    out = np.zeros(g.n)
    dome = np.zeros(g.n)
    r = 150.0 / R_KM  # plume radius, radians
    for h in sim.hotspots:
        age = sim.t - h["born"]
        head = 4.0 if age < 6 else 1.0
        d2 = 2 * (1 - g.centers @ h["pos"])  # chord^2 ~ angle^2
        near = d2 < (3 * r) ** 2
        out[near] += p.hotspot_rate * h["strength"] * head * np.exp(-d2[near] / r**2)
        dome = np.maximum(dome, 1000.0 * h["strength"] * np.exp(-d2 / (4 * r) ** 2))
    return out, dome


def cap_plumes(sim, col, plume):
    """Volcanoes can't build forever. Magma rises only as high as its own
    buoyancy can push it (Mauna Kea's summit, 4.2 km up and 10 km above
    its sea floor, is about the limit); runny basalt spreads out into
    broad shields instead of piling higher; steep flanks slide away in
    giant landslides. So growth slows as the pile nears that height.
    A cell is ~100 km across, so its *average* tops out lower than a
    summit: ~3 km for an ocean island, ~2 km for a continental lava
    plateau (Yellowstone, Deccan). Returns the plume's crust growth
    (km/Myr) after that; under continents a quarter of it."""
    dt, cont = sim.dt, col.cont
    as_volcano = elevation(sim.w_thick, sim.w_age, cont, np.where(cont, col.rock, HOTSPOT), sim.swell - sim.sea_level)
    head = np.where(cont, 2000.0, 3000.0)
    taper = np.clip(1 - (np.maximum(as_volcano, 0) / head) ** 2, 0, 1)
    room = np.maximum(head - as_volcano, 0) / np.where(cont, ISO_LAND, ISO_VOLCANO)
    return np.minimum(plume * np.where(cont, 0.25, 1.0) * taper * dt, room) / dt


def volcanoes(sim, growth, t, rng):
    """The ring of fire: individual volcanoes along active arcs (Fuji,
    Rainier, the Andes' peaks). Each is far smaller than a cell, so it's a
    point on the map plus a modest bump of crust; it rides with its plate,
    stays active for a few Myr and then erodes away. Spaced out so that
    only a representative few show, not every vent. In place on t (km of
    crust); returns t."""
    p, g, dt, pl = sim.params, sim.grid, sim.dt, sim.plates
    live = []
    for v in sim.volcanoes:
        k, r = v["plate"], v["ref"]
        if sim.t - v["born"] < v["life"] and pl.alive[k] and pl.owned[k, r]:
            v["pos"] = g.centers[r] @ pl.Q[k].T
            live.append(v)
    sim.volcanoes = live
    # only on established arcs: continental margins (Andes, Cascades) or
    # island arcs that have built up near the surface (Japan, Aleutians)
    near_top = elevation(t, sim.w_age, sim.w_cont, sim.w_rock, sim.swell - sim.sea_level) > -1500
    cand = np.flatnonzero((growth * dt > 0.15) & near_top & (sim.w_cont | (t > OCEAN_KM + 8)))
    if len(cand) == 0:
        return t
    cand = cand[rng.random(len(cand)) < dt / p.volcano_life]
    min_cos = np.cos(p.volcano_spacing / R_KM)
    pts = [v["pos"] for v in sim.volcanoes]
    for i in rng.permutation(cand):
        c = g.centers[i]
        if pts and (np.asarray(pts) @ c).max() > min_cos:
            continue
        k = int(sim.owner[i])
        sim.volcanoes.append({"plate": k, "ref": int(sim.w_ref[i]), "born": sim.t, "pos": c,
                              "life": rng.uniform(0.5, 1.5) * p.volcano_life})
        pts.append(c)
        t[i] += p.volcano_km
    return t
