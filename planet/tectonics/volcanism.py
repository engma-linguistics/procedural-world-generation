"""Hotspots (mantle plumes) and volcanoes.

Plumes are fixed in the mantle (= world frame) while plates slide over them
(sim.hotspots). Volcanoes are point objects that ride with their plate
(sim.volcanoes), of two kinds:

- hotspot vents: while the plate slides over a plume, a new vent opens every
  ~50-120 km of plate motion (set by the plate's flexural wavelength). Each
  is fed for as long as it sits over the plume (~1 Myr at Hawaii's speed),
  then carried off: a chain of separate volcanoes, youngest over the plume
  (Hawaii -> Midway -> Emperor seamounts).
- arc volcanoes along subduction zones (Fuji, Rainier, the Andes' peaks).

Each volcano keeps its own volume and height. Its crust goes onto the
world grid as a narrow Gaussian (VENT_KM, ~30 km), so at level 7 (55 km
cells) and finer consecutive vents stand as separate islands; at level 6
they blur. After it dies a volcano sinks with its sea floor (thermal
subsidence plus the plume swell decaying behind it: isostasy's base
level), its part above the sea erodes, and in warm water a reef keeps its
top at sea level as it sinks: fringing reef, barrier reef, then atoll;
carried out of the tropics the reef drowns (a guyot).

Both lists are part of the simulation state. A volcano is a dict:
  id, kind (ARC / VENT), plume (the feeding plume's id, -1 for arcs),
  plate (slot), label (that plate's label), ppos (unit vector in the plate's
  frame), ref (its cell in the plate's frame), pos (world frame, now),
  born, life (arcs: Myr active), active, cont (on continental crust),
  vol (km3 of crust it added), height (m: its relief above the floor if
  uneroded), hmax (m: the most it can grow), r (km: its cone's radius),
  floor0, base0 (m: the ground under it and the isostatic base level, at
  birth), floor, top (m: ground under it and its summit, now), eroded (m),
  reef (NO_REEF / REEF / DROWNED), shore (km: radius of its widest
  shoreline, where a reef grows).
rows() turns them into the table worlds and zooms get (COLUMNS).
"""

from __future__ import annotations

import numpy as np

from ..geo import R_KM, latlon
from . import mantle
from .isostasy import ISO_LAND, ISO_VOLCANO, LIFT, OCEAN_KM, elevation, isostasy, ocean_depth, sediment_km
from ..surface import HOTSPOT

ARC, VENT = 0, 1  # kinds
NO_REEF, REEF, DROWNED = 0, 1, 2
# the table of volcanoes in snapshots, worlds and zooms (rows())
COLUMNS = ("lat", "lon", "kind", "age", "active", "top_m", "floor_m", "height_m", "radius_km",
           "volume_km3", "reef", "shore_km")

PLUME_KM = 150.0  # radius of a plume's head and swell
HEAD_MYR = 6.0  # a new plume's head: a huge outpouring for this long (flood basalts)
VENT_KM = 30.0  # radius of a hotspot vent's Gaussian cone (Hawaii's shields: ~30-60 km)
TOP_MAX = (4200.0, 3500.0)  # m: highest summit at sea (Mauna Kea), on a continent
APRON_TOP = (-2000.0, 1500.0)  # m: lava that can't pile higher spreads into a broad apron up to here
ARC_SLOPE = 0.6  # an arc volcano's height / its cone's e-folding radius (a ~30 deg stratocone top)
H_WAVES = 1000.0  # m: the sea's own share of eroding an island (cliff retreat), as if this much higher
AWASH, WAVE_BASE = 50.0, -20.0  # m: an island eroded this low is planed off by the waves to this depth
VENT_KEEP_MYR = 250.0  # forget seamounts older than this...
SEAMOUNT_FORGET = -3000.0  # ... or once their top is this deep
ARC_KEEP_MYR = 20.0  # ... and arc volcanoes this long extinct


def hotspots(sim, rng, bd):
    """Mantle plumes: fixed in the mantle while plates slide over them.
    A new plume's head arrives as a short, huge outpouring (flood basalts,
    like the Deccan Traps); after that it feeds a vent at a time (see the
    module docstring). Most plumes sit under ridges or rifts (Iceland,
    Galapagos, Afar: hot mantle and spreading plates find each other); the
    rest anywhere (Hawaii, mid-plate). Either way they rise from warm
    mantle more often than cold, and most from the edges of the big warm
    regions (mantle.plume_odds; Earth's plumes ring its two big warm
    regions under Africa and the Pacific).
    Returns, on each world cell: the plume head's crust (km/Myr, broad,
    for cap_plumes), the vents' apron (km/Myr, broad, for cap_plumes), the
    vents' own crust (km/Myr, already capped per vent) and the dome (m)."""
    p, g, pl, dt = sim.params, sim.grid, sim.plates, sim.dt
    follow_plates(sim)
    sim.hotspots = [h for h in sim.hotspots if sim.t - h["born"] < h["life"]]
    n_new = rng.poisson(p.hotspots * sim.heat() * sim.dt / p.hotspot_life)
    if sim.step_no == 1:
        n_new = int(round(p.hotspots * sim.heat()))  # start with a full set, of mixed ages
    spreading = bd.spreading
    odds = mantle.plume_odds(sim) if n_new else None
    for j in range(n_new):
        cells = spreading if len(spreading) and rng.random() < p.hotspot_at_ridges else np.arange(g.n)
        w = odds[cells]
        v = g.centers[rng.choice(cells, p=w / w.sum())] + rng.normal(size=3) * 100.0 / R_KM
        life = rng.uniform(0.4, 1.6) * p.hotspot_life
        born = sim.t - (rng.uniform(0, life) if sim.step_no == 1 else 0.0)
        sim.hotspots.append({"pos": v / np.linalg.norm(v), "born": born, "life": life,
                             "strength": rng.uniform(0.5, 1.5), "id": sim.step_no * 1000 + j,
                             "label": -1, "ppos": None, "run": 0.0, "gap": 0.0, "vent": -1})
    n = g.n
    head, apron, vents, dome = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
    r = PLUME_KM / R_KM  # radians
    area = 4 * np.pi * R_KM**2 / n  # km2 per cell
    by_id = {}
    for v in sim.volcanoes:
        if v["kind"] == VENT:
            v["active"] = False
            by_id[v["id"]] = v
    seq = 0
    # (the vents draw from their own stream, so they don't shift everything
    # drawn after them in the step: climate drift, forces, rifts)
    vrng = np.random.default_rng([sim.seed, sim.step_no, 7])
    for h in sim.hotspots:
        age = sim.t - h["born"]
        d2 = 2 * (1 - g.centers @ h["pos"])  # chord^2 ~ angle^2
        near = np.flatnonzero(d2 < (3 * r) ** 2)
        wn = np.exp(-d2[near] / r**2)
        rate = p.hotspot_rate * h["strength"]  # km/Myr at the centre
        if age < HEAD_MYR:
            head[near] += 3 * rate * wn
        dome = np.maximum(dome, 1000.0 * h["strength"] * np.exp(-d2 / (4 * r) ** 2))
        # the tail: what the vents get this step (the Gaussian's volume)
        c = int(g.locate(h["pos"][None])[0])
        k = int(sim.owner[c])
        p_now = pl.Q[k].T @ h["pos"]
        vol = rate * np.pi * PLUME_KM**2 * dt * (0.25 if sim.w_cont[c] else 1.0)  # km3
        cur = by_id.get(h["vent"])
        if cur is None or h["label"] != pl.label[k] or h["ppos"] is None:
            # a fresh start (new plume, or the plume is under another plate now)
            cur = new_vent(sim, vrng, VENT, k, p_now, c, sim.step_no * 1000 + 500 + seq, plume=h["id"])
            seq += 1
            h["run"], h["gap"] = 0.0, vent_gap(sim, vrng, c)
            segs = [(cur, 1.0)]
        else:
            d = float(np.arccos(np.clip(h["ppos"] @ p_now, -1, 1))) * R_KM  # km the plate moved
            segs, at = [], 0.0
            while d > 0 and at + h["gap"] - h["run"] < d:
                at += h["gap"] - h["run"]
                f = at / d
                q = _slerp(h["ppos"], p_now, f)
                cb = int(g.locate((pl.Q[k] @ q)[None])[0])
                segs.append((cur, f))
                cur = new_vent(sim, vrng, VENT, k, q, cb, sim.step_no * 1000 + 500 + seq, plume=h["id"])
                seq += 1
                h["run"], h["gap"] = 0.0, vent_gap(sim, vrng, cb)
            h["run"] += d - at
            # each vent's share: the fraction of the step it spent over the plume
            fs = [f for _, f in segs] + [1.0]
            segs = [(v, fs[i] - (fs[i - 1] if i else 0.0)) for i, (v, _) in enumerate(segs)] + \
                   [(cur, 1.0 - (fs[-2] if len(fs) > 1 else 0.0))]
        h["ppos"], h["label"], h["vent"] = p_now, int(pl.label[k]), cur["id"]
        for v, _ in segs:
            v["active"] = v is cur
        excess = 0.0
        for v, share in segs:
            add = min(vol * share, _room(v))
            excess += vol * share - add
            if add > 0:
                _grow(v, add)
                cells, w = stencil(g, v["pos"], v["r"])
                np.add.at(vents, cells, add * w / (area * dt))
        if excess > 0:
            apron[near] += excess / dt * wn / wn.sum() / area
    return head, apron, vents, dome


def _slerp(a, b, f):
    om = np.arccos(np.clip(a @ b, -1, 1))
    if om < 1e-12:
        return a.copy()
    q = (np.sin((1 - f) * om) * a + np.sin(f * om) * b) / np.sin(om)
    return q / np.linalg.norm(q)


def vent_gap(sim, rng, c):
    """km of plate motion before the plume opens its next vent. Magma finds
    its way up through the plate where the bending under the last volcano's
    load helps it, about a flexural wavelength away (ten Brink 1991;
    Hieronymus & Bercovici 1999): alpha = (4D / (drho g))^(1/4), with the
    plate's elastic thickness ~2.7 km x sqrt(age in Myr) at sea (Watts) and
    ~40 km under a continent. Hawaii (90 Myr floor, Te ~25 km): alpha ~65
    km, volcanoes ~40-60 km apart and islands ~100 km apart. The gap is
    params.vent_spacing x alpha, give or take 25%, and 50-150 km."""
    te = 40.0 if sim.w_cont[c] else max(2.7 * np.sqrt(max(sim.w_age[c], 0.0)), 3.0)
    alpha = 65.0 * (te / 25.0) ** 0.75
    return float(np.clip(sim.params.vent_spacing * alpha * rng.uniform(0.75, 1.25), 50.0, 150.0))


def stencil(g, pos, r_km):
    """The cells a volcano's crust goes to: a Gaussian of radius r_km around
    pos, sampled at the cells within 2 r_km (at least the nearest cell and
    its neighbours), normalised to 1. Returns (cells, weights)."""
    c = int(g.locate(pos[None])[0])
    cells = {c}
    ring = [c]
    reach = np.cos(2.0 * r_km / R_KM)
    for depth in range(4):
        nxt = []
        for i in ring:
            for j in g.nbr_idx[g.nbr_off[i]:g.nbr_off[i + 1]]:
                j = int(j)
                if j not in cells and (depth == 0 or g.centers[j] @ pos > reach):
                    cells.add(j)
                    nxt.append(j)
        ring = nxt
        if not ring:
            break
    cells = np.fromiter(sorted(cells), np.int64)
    d2 = 2 * (1 - g.centers[cells] @ pos) * R_KM**2
    w = np.exp(-d2 / r_km**2)
    return cells, w / w.sum()


def _iso(v):
    return ISO_LAND if v["cont"] else ISO_VOLCANO


def _room(v):
    """km3 of crust a hotspot vent can still take: it grows until its summit
    reaches its height limit (see new_vent) or TOP_MAX."""
    top_max = TOP_MAX[1 if v["cont"] else 0]
    target = min(v["hmax"], top_max - v["floor"])
    return max(target - v["height"], 0.0) * np.pi * v["r"] ** 2 / _iso(v)


def _grow(v, add):
    """A hotspot vent takes add km3 of crust: a Gaussian cone of radius r."""
    v["vol"] += add
    v["height"] = v["vol"] * _iso(v) / (np.pi * v["r"] ** 2)
    v["top"] = v["floor"] + v["height"] - v["eroded"]


def base_level(sim, v):
    """m: the isostatic base level a volcano sinks with: its plate's sea
    floor's depth from its age (half-space cooling; none on a continent),
    plus the plume swell it carries, minus the sea level."""
    k, r = v["plate"], v["ref"]
    sink = 0.0 if v["cont"] else float(ocean_depth(sim.plates.age[k, r]))
    return sink + float(sim.plates.extra[k, r, LIFT]) - sim.sea_level


def new_vent(sim, rng, kind, k, ppos, c, vid, plume=-1, vol=0.0, life=0.0):
    """A new volcano on plate slot k at ppos (plate frame), over world cell
    c, appended to sim.volcanoes. A hotspot vent can grow until its relief
    reaches hmax: magma only rises as high as the plate's thickness lets
    it (Vogt 1974: the older and thicker the plate, the taller its
    volcanoes; Hawaii's on 90 Myr floor stand ~9-10 km above it, Iceland's
    and the Galapagos' on young floor much less), 2500 + 800 m x sqrt(age
    in Myr), at most 10.5 km; on a continent ~3 km."""
    pl = sim.plates
    cont = bool(sim.w_cont[c])
    if kind == VENT:
        hmax = 3000.0 * rng.uniform(0.8, 1.1) if cont else \
            min(2500.0 + 800.0 * np.sqrt(max(sim.w_age[c], 0.0)), 10500.0) * rng.uniform(0.85, 1.1)
    else:
        hmax = 0.0
    # the ground it starts on: the lowest of its cell and their neighbours (a
    # cell's mean also holds the narrow cones of earlier vents in it; a
    # broad plateau or apron raises them all)
    g = sim.grid
    floor = float(sim.w_elev[np.append(g.nbr_idx[g.nbr_off[c]:g.nbr_off[c + 1]], c)].min())
    v = {"id": int(vid), "kind": kind, "plume": int(plume), "plate": int(k), "label": int(pl.label[k]),
         "ppos": np.asarray(ppos, float), "ref": int(pl.idx[k, c]), "pos": pl.Q[k] @ ppos, "born": sim.t,
         "life": float(life), "active": True, "cont": cont, "vol": 0.0, "height": 0.0, "hmax": hmax,
         "r": VENT_KM, "floor0": floor, "base0": 0.0, "floor": floor, "top": floor,
         "eroded": 0.0, "reef": NO_REEF, "shore": 0.0}
    v["base0"] = base_level(sim, v)
    if kind == ARC:
        # a stratocone: z = H exp(-r / lam), H = ARC_SLOPE lam, volume 2 pi lam^2 H (of relief)
        relief_km3 = vol * float(isostasy(np.array([cont]), np.array([sim.w_rock[c]]))[0]) / 1000.0
        H = (ARC_SLOPE**2 * relief_km3 / (2 * np.pi)) ** (1 / 3)  # km
        v.update(vol=float(vol), height=H * 1000.0, r=H / ARC_SLOPE, top=floor + H * 1000.0)
    sim.volcanoes.append(v)
    return v


def follow_plates(sim):
    """Move every volcano with its plate; forget those whose crust has
    gone (subducted). After a rift or a suture the crust may sit on
    another plate: re_home() (at the end of each step) moves it there."""
    pl = sim.plates
    keep = []
    for v in sim.volcanoes:
        k = v["plate"]
        if pl.alive[k] and pl.label[k] == v["label"] and pl.owned[k, v["ref"]]:
            v["pos"] = pl.Q[k] @ v["ppos"]
            keep.append(v)
    sim.volcanoes = keep


def re_home(sim):
    """After the step's events: a volcano whose plate was welded to another
    or split moves to the plate that now has its crust (if that crust is
    at least as old as the volcano), else it's gone."""
    pl, g = sim.plates, sim.grid
    keep = []
    for v in sim.volcanoes:
        k = v["plate"]
        if pl.alive[k] and pl.label[k] == v["label"] and pl.owned[k, v["ref"]]:
            keep.append(v)
            continue
        c = int(g.locate(v["pos"][None])[0])
        k2 = int(sim.owner[c])
        r2 = int(pl.idx[k2, c])
        if pl.age[k2, r2] + 2 * sim.dt >= sim.t - v["born"]:
            b = base_level(sim, v)
            v.update(plate=k2, label=int(pl.label[k2]), ref=r2, ppos=pl.Q[k2].T @ v["pos"])
            v["base0"] += base_level(sim, v) - b  # (no jump in its floor)
            keep.append(v)
    sim.volcanoes = keep


def tend(sim):
    """End of a step: every volcano sinks with its base level, its part
    above the sea erodes, and its reef grows or drowns; arc volcanoes go
    extinct after their life; old ones are forgotten.

    Erosion: the summit's height above the sea (plus H_WAVES for the
    waves cutting the coast back) decays with an e-folding time of
    params.vent_erosion Myr at 1500 mm/yr of rain (slower in dry climates,
    ~sqrt); once it's down to AWASH the waves plane it off to their base
    (Hawaii: Kauai, 5 Myr old, has lost about half its height; by ~10 Myr
    Necker is an 80 m stump). Then it only sinks, flat-topped. A summit
    above TOP_MAX (lifted by its swell) slides away in giant landslides.
    Reefs (params.reef_temp, annual sea temperature): an island in warm
    water gets a fringing reef along its shore; as the island sinks the
    reef keeps growing up at the same place (~1 mm/yr, faster than any
    subsidence): a barrier reef round a shrinking island, then an atoll
    round a lagoon once the volcano is gone (Darwin's sequence). A reef
    carried into water 1.5 C too cold for it drowns (the Darwin point)."""
    re_home(sim)
    if not sim.volcanoes:
        return
    p, g, dt = sim.params, sim.grid, sim.dt
    pos = np.array([v["pos"] for v in sim.volcanoes])
    cells = g.locate(pos)
    keep = []
    for v, c in zip(sim.volcanoes, cells):
        c = int(c)
        age = sim.t - v["born"]
        if v["kind"] == ARC:
            v["active"] = age < v["life"]
            if age > v["life"] + ARC_KEEP_MYR:
                continue
        elif age > VENT_KEEP_MYR or (v["top"] < SEAMOUNT_FORGET and age > 10 and not v["active"]):
            continue
        v["floor"] = v["floor0"] + base_level(sim, v) - v["base0"]
        top = v["floor"] + v["height"] - v["eroded"]
        if v["active"]:  # fresh lava keeps resurfacing it (but its flanks still collapse)
            cut = max(top - TOP_MAX[1 if v["cont"] else 0], 0.0)
            v["eroded"] += cut
            top -= cut
        elif top > 0:
            rain = float(sim.precip[c]) if sim.precip is not None else 1000.0
            tau = p.vent_erosion * np.sqrt(1500.0 / np.clip(rain, 150.0, 6000.0))
            # dh/dt = -(h + H_WAVES) / tau: the slopes wear down, the sea cuts its cliffs back
            cut = (top + H_WAVES) * (1 - np.exp(-dt / tau))
            cut += max(top - cut - TOP_MAX[1 if v["cont"] else 0], 0.0)  # giant landslides
            v["eroded"] += cut
            top -= cut
            if top < AWASH:  # the waves plane what's left down to their base: an atoll or guyot to be
                v["eroded"] += top - WAVE_BASE
                top = WAVE_BASE
        v["top"] = top
        if sim.temp is not None:
            sst = float(sim.temp[c]) + 0.0065 * max(float(sim.w_elev[c]), 0.0)
            if v["reef"] == NO_REEF and top > 0 and sst >= p.reef_temp:
                v["reef"] = REEF
            elif v["reef"] == REEF and sst < p.reef_temp - 1.5:
                v["reef"] = DROWNED
            if v["reef"] == REEF and top > 0:
                v["shore"] = max(v["shore"], shore_km(v))
        keep.append(v)
    sim.volcanoes = keep


def shore_km(v):
    """km from the summit to the shore of the (uneroded) cone today."""
    H, f = v["height"], v["floor"]
    if f >= 0 or H <= -f:
        return 0.0
    if v["kind"] == VENT:  # z = f + H exp(-(x/r)^2)
        return float(v["r"] * np.sqrt(np.log(H / -f)))
    return float(v["r"] * np.log(H / -f))  # z = f + H exp(-x/r)


def rows(sim) -> list:
    """The volcanoes as a table (COLUMNS), for snapshots, worlds and zooms."""
    out = []
    for v in sim.volcanoes:
        la, lo = latlon(v["pos"])
        out.append([round(float(la), 3), round(float(lo), 3), int(v["kind"]), round(float(sim.t - v["born"]), 1),
                    int(bool(v["active"])), int(round(v["top"])), int(round(v["floor"])), int(round(v["height"])),
                    round(float(v["r"]), 1), int(round(v["vol"])), int(v["reef"]), round(float(v["shore"]), 1)])
    return out


def as_dicts(table) -> list[dict]:
    """rows() back into dicts keyed by COLUMNS."""
    return [dict(zip(COLUMNS, row)) for row in (table or []) if len(row) == len(COLUMNS)]


def cap_plumes(sim, col, plume, tops, cont_share=0.25):
    """Lava can't pile up forever. Magma rises only as high as its own
    buoyancy can push it; runny basalt spreads out into broad shields and
    aprons instead of piling higher; steep flanks slide away in giant
    landslides. So growth slows as the pile nears the height tops = (at
    sea, on a continent), m: for a plume head's flood basalts ~3 km at sea
    (Iceland) and ~2 km on land (Deccan); for the apron of lava round a
    chain of vents APRON_TOP. Returns the crust growth (km/Myr) after that;
    under continents cont_share of it (a plume head's melt mostly stalls
    under thick continental crust)."""
    dt, cont = sim.dt, col.cont
    as_volcano = elevation(col.t, sim.w_age, cont, np.where(cont, col.rock, HOTSPOT), sim.swell - sim.sea_level,
                           sediment_km(col.cover, col.x))
    head = np.where(cont, tops[1], tops[0])
    taper = np.clip((head - as_volcano) / 1500.0, 0, 1)
    room = np.maximum(head - as_volcano, 0) / np.where(cont, ISO_LAND, ISO_VOLCANO)
    return np.minimum(plume * np.where(cont, cont_share, 1.0) * taper * dt, room) / dt


def volcanoes(sim, growth, t, rng):
    """The ring of fire: individual volcanoes along active arcs (Fuji,
    Rainier, the Andes' peaks). Each is far smaller than a cell: a point
    on the map with its own cone, plus a modest bump of crust on its cell
    (params.volcano_km3, give or take 50%). It rides with its plate, stays
    active for a few Myr, then goes extinct and erodes (tend()). Spaced
    out (params.volcano_spacing) so that only a representative few show,
    not every vent. In place on t (km of crust); returns t."""
    p, g, dt = sim.params, sim.grid, sim.dt
    area = 4 * np.pi * R_KM**2 / g.n
    # only on established arcs: continental margins (Andes, Cascades) or
    # island arcs that have built up near the surface (Japan, Aleutians)
    near_top = elevation(t, sim.w_age, sim.w_cont, sim.w_rock, sim.swell - sim.sea_level,
                         sediment_km(sim.w_cover, sim.w_extra)) > -1500
    cand = np.flatnonzero((growth * dt > 0.15) & near_top & (sim.w_cont | (t > OCEAN_KM + 8)))
    if len(cand) == 0:
        return t
    cand = cand[rng.random(len(cand)) < dt / p.volcano_life]
    min_cos = np.cos(p.volcano_spacing / R_KM)
    pts = [v["pos"] for v in sim.volcanoes if v["kind"] == ARC and v["active"]]
    jitter = 0.3 * g.spacing
    made = 0
    vrng = np.random.default_rng([sim.seed, sim.step_no, 8])  # (see hotspots())
    for i in rng.permutation(cand):
        c = g.centers[i]
        if pts and (np.asarray(pts) @ c).max() > min_cos:
            continue
        k = int(sim.owner[i])
        q = c + vrng.normal(size=3) * jitter  # somewhere in the cell
        q /= np.linalg.norm(q)
        vol = p.volcano_km3 * vrng.uniform(0.5, 1.5)
        new_vent(sim, vrng, ARC, k, sim.plates.Q[k].T @ q, int(i), sim.step_no * 1000 + made, vol=vol,
                 life=rng.uniform(0.5, 1.5) * p.volcano_life)
        pts.append(c)
        made += 1
        t[i] += vol / area
    return t
