"""Volcanoes in the regional zoom: each volcano of the world's table
(tectonics.volcanism.COLUMNS) drawn as its own edifice.

Shapes (x: km from the summit):
- hotspot shield: floor + H exp(-(x/r)^2), r ~30 km (the Gaussian the run
  put its crust into, so the zoom keeps its volume); an active one has a
  summit caldera.
- arc stratovolcano: floor + H exp(-x/r), a concave cone with a ~30 deg top
  and a summit crater.
Age, from the run's numbers: the summit is now at top_m. If it's still
above the sea, the part above the sea is lowered in proportion (erosion)
and gullied with radial valleys, the more the older it is; if the waves
have planed it, it's cut flat at top_m (a guyot as it sinks). Young
volcanoes (active, or younger than PIN_MYR) keep their smooth cone through
the landscape pass; older ones are left to it (it cuts the drainage).

Reefs (reef = 1, living, in warm water), at the radius of the island's
widest shore (shore_km): with the island still up, a fringing reef along
its coast, or a barrier reef with a lagoon once the island has shrunk
inside it; with the volcano below the sea, an atoll: a reef rim with
low islets (motu) round a lagoon. The reef front drops steeply outside.

Near hotspot vents on the sea floor, the zoom's terrain is replaced by
the vents' floor (their sea floor, from the run) with the cones on it, so
the sea between two vents is sea, whatever the coarse cells' means say
(at level 6-7 a cell holds a vent and its neighbours' flanks): it is
lowered by the cones' share of each cell's mean (zoom.py), so where the
cells stand higher than the floor plus the cones it stays ground. Elsewhere
(arcs, continental hotspots) the cones are added to the terrain (max).

A hotspot vent on a continent (floor above the sea) isn't a shield: a
plume under stiff continental crust makes a broad basalt plain with large
calderas (the Snake River Plain, Yellowstone), so it is drawn as an oval
caldera with a rim and a low resurgent dome on a lava plain twice its
radius, holding the same volume (PW-118).
"""

from __future__ import annotations

import numpy as np

from . import kernels as ZK
from ..geo import R_KM, xyz
from ..tectonics.volcanism import ARC, ARC_SLOPE, COLUMNS, DROWNED, PLUME_KM, REEF, SHORE_MAX

PIN_MYR = 1.5  # younger volcanoes keep their smooth cone in the landscape pass
# minor cones along active arcs (arc_infill, PW-116)
ARC_GAP_KM = 60.0  # km: a volcano about this often along a volcanic front (Java, Sumatra, the Aleutians: 50-70)
ARC_LINK_KM = 220.0  # km: active arc volcanoes this close are neighbours along the chain
ARC_LINK_DEG = 110.0  # deg: a second neighbour at least this far round from the first (the chain's other side)
ARC_OFF_KM = 6.0  # km: the minor cones' scatter off the line between them
ARC_MINOR = (0.6, 0.95)  # their height, of the lower of the pair (the run's spacing is its coarseness)
CALDERA_M = (180.0, 120.0)  # depth of an active hotspot shield's caldera, an arc volcano's crater
LAGOON_M = 35.0  # typical lagoon depth
MOTU_M = 2.5  # height of the reef islets...
MOTU_NOISE = -0.2  # ... on about 3/5 of the rim (the rest is reef flat awash)
FORE_REEF = 700.0  # m/km: the reef front's drop
VALLEY_KM = 6.0  # spacing of the radial valleys at the coast
FADE = 0.8  # coarse cells over which the vents' province fades out
# continental hotspot vents (_caldera): a lava plain PLAIN_R x the vent's
# radius, a caldera CALDERA_R x it (oval up to CALDERA_OVAL), rim, sunk floor
# and resurgent dome as fractions of the plain's height
PLAIN_R, CALDERA_R, CALDERA_OVAL = 2.0, 1.0, 1.9
CALDERA_RIM, CALDERA_DEPTH, CALDERA_DOME = 0.25, 0.5, 0.3


def table(world: dict) -> list[dict]:
    """The world's volcanoes as dicts (COLUMNS), [] for a world without them."""
    meta = world.get("meta", {})
    cols = meta.get("volcano_columns")
    if not cols or list(cols) != list(COLUMNS):
        return []
    return [dict(zip(cols, r)) for r in meta.get("volcanoes") or [] if len(r) == len(cols)]


# Status (active / dormant / extinct). The run knows two things about a
# volcano: whether it is fed now (a hotspot vent over its plume, an arc
# volcano within its ~8 Myr life: `active`), and where the live plumes are
# (meta "hotspots"). It has no eruptions, only Myr steps, so "erupted in the
# last few thousand years" can't be told from "quiet for 50,000 years": every
# fed volcano is "active". What it can tell: a hotspot vent the plate has
# carried off its plume but still within the plume's head (PLUME_KM, the
# melt region and swell) sits over hot, partly molten mantle and can erupt
# again (Hawaii's rejuvenated volcanoes, Haleakala; Yellowstone's older
# calderas): "dormant". Farther off, or with its plume dead, it is
# "extinct". An arc volcano past its life is extinct: the arc's magma has
# moved to a new centre (the run has no "still on a live arc" state of its own).
DORMANT_KM = PLUME_KM


def plumes(world: dict) -> np.ndarray:
    """Unit vectors of the world's live plumes (meta "hotspots": [lat, lon])."""
    hs = (world.get("meta") or {}).get("hotspots") or []
    if not hs:
        return np.zeros((0, 3))
    la, lo = np.radians(np.asarray(hs, float)[:, :2]).T
    return xyz(la, lo)


def status(v: dict, plume_xyz: np.ndarray) -> str:
    """"active", "dormant" or "extinct" (see DORMANT_KM)."""
    if v["active"]:
        return "active"
    if v["kind"] == ARC or not len(plume_xyz):
        return "extinct"
    p = xyz(np.radians(v["lat"]), np.radians(v["lon"]))
    d = float(np.arccos(np.clip(plume_xyz @ p, -1, 1)).min()) * R_KM
    return "dormant" if d <= DORMANT_KM else "extinct"


def statuses(world: dict, V: list[dict] | None = None) -> list[str]:
    """status() of each volcano of table(world) (or of V)."""
    P = plumes(world)
    return [status(v, P) for v in (table(world) if V is None else V)]


def arc_infill(V: list[dict], seed: int) -> list[dict]:
    """Minor cones along active arcs (PW-116). The run keeps one arc volcano
    per volcano_spacing (120 km) of active arc; real volcanic fronts have one
    every ~50-70 km (Java, the Aleutians), so the zoom adds cones between
    neighbouring active arc volcanoes along the chain: each one's nearest
    active neighbour within ARC_LINK_KM and the nearest on its other side
    (> ARC_LINK_DEG away), a cone every ~ARC_GAP_KM between them, a little
    off the line, a little smaller than the pair (ARC_MINOR of the lower:
    the run's spacing is its coarseness, these stand for volcanoes like
    its own), young and active, on the floor between them. Planet-fixed:
    the same in overlapping zooms of one world (and seed)."""
    idx = [j for j, v in enumerate(V) if v["kind"] == ARC and v["active"] and v["height_m"] >= 20]
    if len(idx) < 2:
        return []
    P = xyz(np.radians([V[j]["lat"] for j in idx]), np.radians([V[j]["lon"] for j in idx]))
    D = np.arccos(np.clip(P @ P.T, -1, 1)) * R_KM
    np.fill_diagonal(D, np.inf)
    edges = set()
    for a in range(len(idx)):
        nb = np.flatnonzero(D[a] < ARC_LINK_KM)
        if not len(nb):
            continue
        nb = nb[np.argsort(D[a, nb])]
        edges.add((min(a, nb[0]), max(a, nb[0])))
        u0 = P[nb[0]] - P[a]
        for b in nb[1:]:  # (the nearest on the other side: a chain, not a cluster)
            u = P[b] - P[a]
            if u @ u0 < np.cos(np.radians(ARC_LINK_DEG)) * np.linalg.norm(u) * np.linalg.norm(u0):
                edges.add((min(a, b), max(a, b)))
                break
    out = []
    for a, b in sorted(edges):
        va, vb = V[idx[a]], V[idx[b]]
        n = int(round(D[a, b] / ARC_GAP_KM)) - 1
        if n < 1:
            continue
        rs = np.random.default_rng([int(seed), idx[a], idx[b], 116])
        side = np.cross(P[a], P[b])
        side /= max(np.linalg.norm(side), 1e-12)
        for k in range(n):
            t = (k + 1 + rs.uniform(-0.2, 0.2)) / (n + 1)
            p = (1 - t) * P[a] + t * P[b] + side * rs.normal(0.0, ARC_OFF_KM) / R_KM
            p /= np.linalg.norm(p)
            H = float(round(min(va["height_m"], vb["height_m"]) * rs.uniform(*ARC_MINOR)))
            f = float(round((1 - t) * va["floor_m"] + t * vb["floor_m"]))
            r = H / ARC_SLOPE / 1000.0
            out.append({"lat": float(np.degrees(np.arcsin(np.clip(p[2], -1, 1)))),
                        "lon": float(np.degrees(np.arctan2(p[1], p[0]))), "kind": ARC,
                        "age": float(min(va["age"], vb["age"])), "active": 1, "top_m": f + H, "floor_m": f,
                        "height_m": H, "radius_km": r, "volume_km3": 2 * np.pi * r * r * H / 1000.0,
                        "reef": 0, "shore_km": 0.0, "minor": True})
    return out


def _shore(kind, H, f):
    """km from the summit to where the (uneroded) cone meets the sea."""
    if f >= 0 or H <= -f:
        return 0.0
    return min(float(np.sqrt(np.log(H / -f))) if kind != ARC else float(np.log(H / -f)), SHORE_MAX)


def form(v: dict) -> str:
    """What the volcano looks like now, in words."""
    arc = v["kind"] == ARC
    if not arc and v["floor_m"] > 0:
        return "active caldera" if v["active"] else "caldera on a lava plain"
    if v["active"]:
        return "active stratovolcano" if arc else "active shield volcano"
    peak = v["floor_m"] + v["height_m"]
    if v["top_m"] > 0:
        if v["reef"] == REEF:
            sh = v["radius_km"] * _shore(v["kind"], v["height_m"], v["floor_m"])
            return "island with a barrier reef" if v["shore_km"] > sh + 3 else "island with a fringing reef"
        return "eroded volcanic island" if v["top_m"] < peak - 200 else "volcanic island"
    if v["reef"] == REEF:
        return "atoll"
    if v["reef"] == DROWNED:
        return "drowned atoll (guyot)"
    return "guyot" if v["top_m"] < peak - 50 else "seamount"


def fields(world: dict, fr, px, py, res: float, sp: float, Pk, seed: int, size_km: float):
    """Per-pixel fields of the volcanoes in or near the region, or None:
      province  0..1, where the terrain is replaced by floor + cones (oceanic hotspot vents)
      floor     the vents' sea floor there (m)
      z         the highest cone there (m; -inf off them), with z_floor (its
                floor) and z_abs (1 near its summit, 0 at its footprint's edge)
      bump      cones elsewhere, to max() with the terrain (m; -inf off them),
                with bump_floor and bump_abs; bump_flat: a continental vent's
                lava plain, on the smooth coarse ground (it fills the hollows)
      pin       young cones' surface, held in the landscape pass (m; nan off them)
      reef      pixels of reef carbonate (rim, lagoon, fringing flat)
      rock      surface.ROCKS id of the volcano under each pixel (0: none)
      bump_minor  the bump there is a minor arc cone (arc_infill: no volume
                of its own in the coarse cells; zoom.py takes it off their land)
      list      the volcanoes drawn, for the zoom's stats (with each one's status: active,
                dormant or extinct, statuses())"""
    V = table(world)
    if not V:
        return None
    V = V + arc_infill(V, seed)  # (minor cones along the active arcs)
    st = statuses(world, V)
    lat = np.array([v["lat"] for v in V])
    lon = np.array([v["lon"] for v in V])
    P = xyz(np.radians(lat), np.radians(lon))
    vx, vy = fr.to_plane(P)
    ahead = P @ fr.c > 0
    half = size_km / 2
    npx = len(px)
    nx = int(round(np.sqrt(npx)))
    xs0, ys0 = px[0], py[0]  # pixel (0, 0) centre: west, north
    floors = []
    out = dict(province=np.zeros(npx), z=np.full(npx, -np.inf), z_floor=np.zeros(npx), z_abs=np.zeros(npx),
               bump_floor=np.zeros(npx), bump_abs=np.zeros(npx), bump_flat=np.zeros(npx, bool),
               bump=np.full(npx, -np.inf), pin=np.full(npx, np.nan), reef=np.zeros(npx, bool),
               rock=np.zeros(npx, np.uint8), bump_minor=np.zeros(npx, bool), list=[])
    S = int(seed) * 1_000_003 + 17
    age_px = np.full(npx, np.inf)  # the age of the edifice drawn at each pixel
    for j, v in enumerate(V):
        kind, H, f, top, r = v["kind"], float(v["height_m"]), float(v["floor_m"]), float(v["top_m"]), float(v["radius_km"])
        if H < 20 or r <= 0 or not ahead[j]:
            continue
        arc = kind == ARC
        cont = (not arc) and f > 0  # a hotspot vent on a continent: a caldera on a lava plain
        reach = r * (np.log(H / 10.0) if arc else np.sqrt(np.log(H / 10.0)))  # km to where it's 10 m high
        if cont:
            reach = PLAIN_R * r * 2.0  # (the plain's lobed, noisy edge, out to ~1.25 x 1.35 x 1.12 PLAIN_R r)
        reach = max(reach, v["shore_km"] + 3.0)
        if abs(vx[j]) > half + reach or abs(vy[j]) > half + reach:
            continue
        prov = (not arc) and f < 0  # a hotspot vent on the sea floor
        # its window of pixels (wider for the province and the floor's interpolation)
        rin = max(reach, 0.9 * sp)  # the province: all of it within rin, fading out over FADE cells
        wr = max(reach, rin + (FADE + 0.05) * sp) if prov else reach
        c0 = int(np.clip(np.floor((vx[j] - wr - xs0) / res), 0, nx - 1))
        c1 = int(np.clip(np.ceil((vx[j] + wr - xs0) / res), 0, nx - 1))
        r0 = int(np.clip(np.floor((ys0 - vy[j] - wr) / res), 0, nx - 1))
        r1 = int(np.clip(np.ceil((ys0 - vy[j] + wr) / res), 0, nx - 1))
        if c1 < c0 or r1 < r0:
            continue
        win = (np.arange(r0, r1 + 1)[:, None] * nx + np.arange(c0, c1 + 1)[None, :]).ravel()
        dx, dy = px[win] - vx[j], py[win] - vy[j]
        rho = np.hypot(dx, dy)
        th = np.arctan2(dy, dx)
        # not quite round: a shield spreads along 2-3 rift zones (Kilauea's
        # East Rift), and lava flows and landslides make its outline lobed
        rs = np.random.default_rng([int(seed), j, int(v["age"] * 10)])
        n_arms = int(rs.integers(2, 4))
        arms = rs.uniform(0, 2 * np.pi) + np.linspace(0, 2 * np.pi, n_arms, endpoint=False) + rs.normal(0, 0.35, n_arms)
        lobe = 0.0 if arc else np.max(np.cos(th[:, None] - arms[None, :]), 1).clip(0) ** 6
        wob = ZK.fbm(np.ascontiguousarray(Pk[win]), max(0.6 * r, 4.0), 3, 0.5, S + 63 + j % 7) / 0.17
        rho_e = rho / (1 + (0.35 if not arc else 0.0) * lobe) * (1 + 0.12 * np.clip(wob, -2, 2))
        crater = np.zeros(len(win), bool)
        if cont:
            relief, crater = _caldera(rho_e, dx, dy, r, H, rs)
            cone = f + relief
        else:
            cone = f + H * (np.exp(-rho_e / r) if arc else np.exp(-(rho_e / r) ** 2))
        peak = f + H
        if top >= 0 and peak > 0:
            # eroded: the part above the sea lowered in proportion
            zz = np.where(cone > 0, cone * min(top / peak, 1.0), cone)
        else:
            zz = np.minimum(cone, top)  # planed flat by the waves, now sunk (or a seamount: top = peak)
        if v["active"] and not cont:
            rc = max(0.08 * r, 1.0 * res) if not arc else max(0.25 * r, res)
            zz = zz - CALDERA_M[1 if arc else 0] * np.exp(-(rho / rc) ** 2)
        elif top > 0 and v["age"] > 0.3 and not cont:
            # radial valleys, deeper with age: noise stretched along the radius
            sh = r * _shore(kind, H, f)
            R0 = max(sh, 6.0)
            pts = np.ascontiguousarray(np.column_stack([R0 * np.cos(th), R0 * np.sin(th), 0.3 * rho])
                                       + 1000.0 * np.array([np.sin(j * 1.7), np.cos(j * 2.3), j % 97]))
            val = np.clip(ZK.fbm(pts, VALLEY_KM, 3, 0.5, S + 61) / 0.17, 0, 1.5)
            m = np.clip(v["age"] / 4.0, 0, 1)
            above = np.clip(zz, 0, None)
            zz = zz - 1.0 * above * (1 - above / max(top, 1.0)) * val * m
        reefpx = np.zeros(len(win), bool)
        if v["reef"] == REEF:
            sh_now = r * _shore(kind, H, f) if top > 0 else 0.0
            rr = max(min(float(v["shore_km"]), SHORE_MAX * r), sh_now, 3.0)
            hw = max(1.0 * res, 1.0)  # half the rim's width (a ring at least 2 px wide)
            n2 = ZK.fbm(np.ascontiguousarray(Pk[win]), 5.0, 2, 0.5, S + 62) / 0.17
            if top > 0 and rr - sh_now < 2 * res + hw:  # fringing reef: a flat out from the shore
                rr = sh_now + max(1.5 * res, 1.5)
                c = np.where(rho_e <= rr, -2.0, -2.0 - (rho_e - rr) * FORE_REEF)
            else:  # barrier reef or atoll: rim, lagoon inside
                lag = -(LAGOON_M + 15.0 * np.clip(n2, -1, 1))
                rim = np.where(n2 > MOTU_NOISE, MOTU_M, -1.0)
                # (the ring follows the island's lobed old shore, not a circle)
                c = np.where(np.abs(rho_e - rr) <= hw, rim,
                             np.where(rho_e < rr, np.minimum(lag, -3.0), -1.0 - (rho_e - rr - hw) * FORE_REEF))
            reefpx = (c >= zz) & (rho_e < rr + hw + 1.0)
            zz = np.maximum(zz, c)
        if prov:
            floors.append((vx[j], vy[j], f))
            out["province"][win] = np.maximum(out["province"][win], _smooth(rin + FADE * sp, rin, rho))
        # Near the summit the cone stands on its own floor (absolute heights:
        # sea level matters for reefs and planed tops); toward the edge of
        # its footprint it sits on whatever ground the zoom has there
        # (zoom.py: z + (1 - abs) * (ground - floor)), so it has no step.
        # (a minor arc cone's floor is only its neighbours' interpolated: it sits
        # on the ground, wherever that is, PW-116)
        absw = _smooth(0.85 * reach, 0.35 * reach, rho) if not (cont or v.get("minor")) else np.zeros(len(win))
        zm = np.where((cone > f + 10) | reefpx, zz, -np.inf)
        key = "z" if prov else "bump"
        # (the highest edifice wins, but a younger caldera sinks into an older
        # one's plain: the new lava doesn't fill it)
        better = (zm > out[key][win]) | (crater & np.isfinite(zm) & (v["age"] < age_px[win]))
        age_px[win] = np.where(better, v["age"], age_px[win])
        out[key][win] = np.where(better, zm, out[key][win])
        out[key + "_floor"][win] = np.where(better, f, out[key + "_floor"][win])
        out[key + "_abs"][win] = np.where(better, np.maximum(absw, reefpx), out[key + "_abs"][win])
        if not prov:
            out["bump_minor"][win] = np.where(better, bool(v.get("minor")), out["bump_minor"][win])
        if not prov:
            out["bump_flat"][win] = np.where(better, cont, out["bump_flat"][win])
        on = zz > f + 30
        if (v["active"] or v["age"] < PIN_MYR) and not v.get("minor"):
            out["pin"][win] = np.where(on, np.fmax(out["pin"][win], zz), out["pin"][win])
        out["rock"][win] = np.where(on, 2 if arc else 1, out["rock"][win])
        out["reef"][win] |= reefpx
        if abs(vx[j]) < half and abs(vy[j]) < half:
            out["list"].append({"lat": v["lat"], "lon": v["lon"], "kind": "arc" if arc else "hotspot",
                                "form": form(v), "active": bool(v["active"]), "status": st[j], "age_myr": v["age"], "top_m": v["top_m"],
                                "height_m": v["height_m"], "x_km": round(float(vx[j]), 1),
                                "y_km": round(float(vy[j]), 1), **({"minor": True} if v.get("minor") else {})})
    if not out["list"] and not np.isfinite(out["z"]).any() and not np.isfinite(out["bump"]).any():
        return None
    # the vents' sea floor, smoothly between them
    out["floor"] = np.full(npx, np.nan)
    if floors:
        fx, fy, ff = (np.array(a, float) for a in zip(*floors))
        on = out["province"] > 0
        fl, _ = ZK.gauss_interp(px[on], py[on], fx, fy, ff[:, None], np.ones((len(ff), 1)), 0.45 * sp)
        out["floor"][on] = fl[:, 0]
    return out


def _caldera(rho_e, dx, dy, r: float, H: float, rs) -> np.ndarray:
    """A continental hotspot vent's relief above its floor (m): a flat lava
    plain PLAIN_R x r across holding the volume of the run's Gaussian
    (pi r^2 H), so PLAIN_R^-2 of its height, and in it an oval caldera
    (CALDERA_R x r, up to CALDERA_OVAL long; Yellowstone ~45 x 85 km) with
    a raised rim, a floor sunk below the plain and a low resurgent dome.
    Returns (relief, inside the caldera's rim)."""
    Rp = PLAIN_R * r
    Hp = H / PLAIN_R**2
    plain = Hp * (1 - _smooth(0.75 * Rp, 1.25 * Rp, rho_e))
    a = rs.uniform(0, np.pi)
    ell = rs.uniform(1.0, CALDERA_OVAL)
    u, w = dx * np.cos(a) + dy * np.sin(a), -dx * np.sin(a) + dy * np.cos(a)
    Rc = CALDERA_R * r
    rc = np.hypot(u / np.sqrt(ell), w * np.sqrt(ell))  # (the same area as a circle of Rc)
    rim = CALDERA_RIM * Hp * np.exp(-((rc - Rc) / (0.15 * Rc)) ** 2)
    sunk = CALDERA_DEPTH * Hp * (1 - _smooth(0.85 * Rc, Rc, rc))
    dome = CALDERA_DOME * Hp * np.exp(-(rc / (0.3 * Rc)) ** 2)
    return plain + rim - sunk + dome, rc < Rc


def _smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0.0, 1.0)
    return t * t * (3 - 2 * t)
