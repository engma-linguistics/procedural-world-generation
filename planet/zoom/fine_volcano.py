"""Volcano edifices in the nested fine zoom (PW-395).

A parent zoom draws a volcano as a smooth cone (zoom.volcanoes: a concave
exponential stratocone, a Gaussian shield, a caldera on a lava plain) at
its own pixel scale. Bicubic at 25-200 m that is a needle-tipped cone with
nothing on it. The fine zoom adds the edifice's form below the parent's
pixel scale: its relief E here, less E as the parent's pixels see it (E
averaged over each parent pixel, bicubic), so each parent pixel's mean is
unchanged (zoom.fine adds it to the parent's surface and keeps the summit
at top_m exactly):

- stratovolcano (arc): flanks e-folding over r = H / ARC_SLOPE (concave,
  ~31 degrees at the rim, as the run's cone), cut off at a summit crater
  (rim radius ~0.08 r, 0.12-0.6 km; floor ~0.4 x its radius deep when
  active, shallower when dormant or extinct) with a notched rim. Large old
  extinct ones have a summit caldera (~0.3 r) instead.
- shield (oceanic hotspot): the Gaussian dome (near flat at this scale)
  with a steep walled summit caldera when active (shallower when dormant;
  a summit pit crater when extinct) and pit craters along its rift arms.
- continental caldera: the parent's form (it is tens of km across).
- radial gullies (barrancos) on every flank, deepest at mid height,
  deeper with age (active cones are resurfaced) and rain.
- lava flow lobes down the flanks and a few parasitic cinder cones on
  active and dormant volcanoes.

Every random choice is fixed by the volcano's position and the seed, and
noise is sampled in the volcano's own local frame: sibling and nested
fine zooms draw the same edifice.
"""

from __future__ import annotations

import numpy as np

from . import regional as Z
from ..geo import smoothstep
from . import kernels as ZK
from ..tectonics.volcanism import ARC_SLOPE

CRATER_R = (0.08, 0.12, 0.6)  # a stratocone's crater rim radius: x r, min, max km
CRATER_D = {"active": 0.4, "dormant": 0.3, "extinct": 0.15}  # its depth x its rim radius (fresh d/D ~0.2)
CRATER_D_MAX = 300.0  # m: no deeper (a wide crater the parent drew)
CRATER_FLOOR = 0.35  # the flat floor's radius, of the rim's
OLD_CALDERA = (1500.0, 1.0, 0.3, 0.8, 2.5)  # an extinct stratocone at least this high (m) and old (Myr):
# a summit caldera of radius 0.3 r (0.8-2.5 km; Crater Lake, Aso)
SHIELD_CALDERA = (0.08, 0.5, 4.0, 180.0)  # a shield's caldera: x r, min, max km; depth m (Kilauea ~120, Mauna Loa ~180)
CALDERA_WALL_DEG = 60.0  # its walls (cliffs over talus)
GULLY = {"active": 0.2, "dormant": 0.4}  # the gullies' depth by status (extinct: grows with age to 1 at 3 Myr)
GULLY_M = (0.15, 400.0)  # ... x the cone's height, at most m, at mid height for an old volcano
GULLY_WALL_M = 100.0  # m: the deepest gully its width allows at the reference radius R0
GULLY_KM = 1.2  # the gullies' noise wavelength at the cone's mid flank (spacing ~0.6 km: barrancos)
ROUGH_KM = 0.25  # its wavelength (3 octaves, to ~60 m)
RAIN_MM = 1000.0  # the gullies scale with sqrt(rain / this) (0.2-2.5)
FLOWS = {"active": (3, 7), "dormant": (1, 4)}  # lava flow lobes
CONES = {"active": (1, 4), "dormant": (0, 3)}  # parasitic cinder cones (height / base width ~0.18)


def kind_of(v: dict) -> str:
    if v.get("kind") == "arc":
        return "strato"
    return "caldera" if "caldera" in str(v.get("form", "")) else "shield"


def status_of(v: dict) -> str:
    s = v.get("status")
    return s if s in CRATER_D else ("active" if v.get("active") else "extinct")


def params(v: dict, r_km: float | None, rain_mm: float, seed: int, rim_km: float = 0.0,
           base_m: float | None = None) -> dict:
    """The edifice of volcano v (a zoom's volcano entry): its scale (r_km:
    the e-folding radius for a shield; an arc's is H / ARC_SLOPE), the summit
    form, gullies, flows and cones. hold_km: the summit form held through
    the landscape pass; reach_km: how far out it draws. rim_km: the radius
    of a crater the parent already drew (a stratocone's is no smaller);
    base_m: the ground round its foot. An extinct volcano is eroded
    (zoom.volcanoes lowers its part above the sea in proportion): its
    relief is top_m less that ground (or the sea), on the cone's shape."""
    kind, st = kind_of(v), status_of(v)
    H = max(float(v.get("height_m", 0.0)), 50.0)
    age = float(v.get("age_myr", v.get("age", 0.0)) or 0.0)
    r = H / ARC_SLOPE / 1000.0 if kind == "strato" else max(float(r_km or 0.0), 2.0)
    if st == "extinct" and base_m is not None:
        top = float(v["top_m"])
        H = float(np.clip(top - (max(base_m, 0.0) if top > 0 else base_m), 50.0, H))
    key = [int(seed) & 0x7FFFFFFF, int(round((float(v["lat"]) + 90) * 1e4)), int(round((float(v["lon"]) + 360) * 1e4)), 395]
    rs = np.random.default_rng(key)
    p = {"kind": kind, "status": st, "H": H, "r": r, "lat": float(v["lat"]), "lon": float(v["lon"]),
         "seed": int(key[1] * 7 + key[2]) % 1_000_000 + 395_000, "crater_r": 0.0, "crater_d": 0.0,
         "caldera": False, "ell": 1.0, "ell_a": 0.0, "pits": [], "flows": [], "cones": []}
    if kind == "strato":
        lo, hi = CRATER_R[1], CRATER_R[2]
        p["crater_r"] = max(float(np.clip(CRATER_R[0] * r, lo, hi)), float(rim_km))
        p["crater_d"] = min(CRATER_D[st] * p["crater_r"] * 1000.0, CRATER_D_MAX)
        if st == "extinct" and H >= OLD_CALDERA[0] and age >= OLD_CALDERA[1]:
            p["caldera"] = True
            p["crater_r"] = float(np.clip(OLD_CALDERA[2] * r, OLD_CALDERA[3], OLD_CALDERA[4]))
            p["crater_d"] = 0.15 * p["crater_r"] * 1000.0
    elif kind == "shield":
        p["caldera"] = st != "extinct"
        p["crater_r"] = float(np.clip(SHIELD_CALDERA[0] * r, SHIELD_CALDERA[1], SHIELD_CALDERA[2]))
        p["crater_d"] = SHIELD_CALDERA[3] * (1.0 if st == "active" else 0.4)
        if st == "extinct":  # (a summit pit crater)
            p["crater_r"] = float(np.clip(0.1 * p["crater_r"], 0.15, 0.4))
            p["crater_d"] = 0.3 * p["crater_r"] * 1000.0
        p["ell"], p["ell_a"] = float(rs.uniform(1.0, 1.5)), float(rs.uniform(0, np.pi))
        if st != "extinct":  # pit craters along 2-3 rift arms just outside the caldera
            arms = rs.uniform(0, 2 * np.pi) + np.linspace(0, 2 * np.pi, int(rs.integers(2, 4)), endpoint=False)
            for a in arms:
                for _ in range(int(rs.integers(1, 3))):
                    d = p["crater_r"] * rs.uniform(1.3, 3.0)
                    pr = rs.uniform(0.08, 0.3)
                    p["pits"].append((d * np.cos(a), d * np.sin(a), pr, pr * 1000.0 * rs.uniform(0.25, 0.5)))
    # gullies: deeper with age (an active cone is resurfaced by its flows) and rain
    m_age = GULLY.get(st, float(np.clip(age / 3.0, GULLY["dormant"], 1.0)))
    m_rain = float(np.sqrt(np.clip(rain_mm / RAIN_MM, 0.2, 2.5)))
    p["gully_m"] = min(GULLY_M[0] * H, GULLY_M[1]) * m_age * m_rain
    if kind != "caldera":
        on_flank = (p["crater_r"] + 0.1 * r, 1.2 * r) if kind == "strato" else (1.2 * p["crater_r"], 0.6 * r)
        on_flank = (on_flank[0], max(on_flank[1], on_flank[0] + 0.2 * r))  # (a wide crater the parent drew)
        n_flows = int(rs.integers(*FLOWS[st])) if st in FLOWS else 0
        for _ in range(n_flows):
            th = rs.uniform(0, 2 * np.pi)
            r0 = rs.uniform(*on_flank) if rs.uniform() < 0.6 else 1.5 * p["crater_r"]  # (from the summit or a flank vent)
            L = rs.uniform(0.6, 2.0) * r if kind == "strato" else rs.uniform(0.2, 0.6) * r
            w0 = rs.uniform(0.06, 0.15) if kind == "strato" else rs.uniform(0.15, 0.5)
            T = rs.uniform(8.0, 25.0) if kind == "strato" else rs.uniform(3.0, 10.0)
            p["flows"].append((th, r0, L, w0, T, rs.uniform(0, 2 * np.pi), rs.uniform(1.0, 3.0)))
        n_cones = int(rs.integers(*CONES[st])) if st in CONES else 0
        for _ in range(n_cones):
            th = rs.uniform(0, 2 * np.pi)
            d = rs.uniform(0.6, 2.0) * r if kind == "strato" else rs.uniform(0.15, 0.6) * r
            hc = rs.uniform(40.0, 150.0)
            p["cones"].append((d * np.cos(th), d * np.sin(th), hc))
    p["hold_km"] = 1.6 * p["crater_r"] if kind != "caldera" else 0.0
    p["reach_km"] = (5.0 * r) if kind == "strato" else 2.5 * r
    # the landscape pass shapes the ground only from the cone's lower flanks out (above that it is
    # the edifice: the pass's stream-power steps across a 30 degree cone stood as terraces)
    p["free_km"] = (1.2 * r, 2.5 * r) if kind == "strato" else (0.3 * r, 0.8 * r) if kind == "shield" else (0.0, 0.0)
    return p


def _flank(p: dict, rho: np.ndarray) -> np.ndarray:
    """The edifice without its summit form (m above its far base)."""
    H, r, Rr = p["H"], p["r"], p["crater_r"]
    if p["kind"] == "strato":
        return H * np.exp(-np.maximum(rho - Rr, 0.0) / r)
    if p["kind"] == "shield":
        return H * np.exp(-(np.maximum(rho - Rr, 0.0) / r) ** 2)
    return np.zeros_like(rho)


def relief(P: np.ndarray, p: dict) -> np.ndarray:
    """The edifice's relief E (m above its far base) at unit vectors P (n, 3)."""
    n = len(P)
    if p["kind"] == "caldera" or n == 0:
        return np.zeros(n)
    fr = Z.Frame(p["lat"], p["lon"])  # (the volcano's own frame: nested zooms agree)
    x, y = fr.to_plane(P)
    rho, th = np.hypot(x, y), np.arctan2(y, x)
    H, r, Rr, d = p["H"], p["r"], p["crater_r"], p["crater_d"]
    S = p["seed"]
    Pk = np.ascontiguousarray(np.column_stack([x, y, np.zeros(n)]))
    # the outline a little irregular (flows, collapses): the radius wobbles by ~3%
    wob = ZK.fbm(Pk + 50.0, max(r, 1.0), 2, 0.5, S + 1) / 0.17
    rho_e = rho * (1.0 + 0.03 * np.clip(wob, -2, 2))
    z = _flank(p, rho_e)
    # the summit form: a crater (stratocone), a caldera (oval, steep walled) or a pit
    if Rr > 0 and d > 0:
        if p["caldera"] and p["kind"] == "shield":
            a, ell = p["ell_a"], p["ell"]
            u, w = x * np.cos(a) + y * np.sin(a), -x * np.sin(a) + y * np.cos(a)
            rc = np.hypot(u / np.sqrt(ell), w * np.sqrt(ell))
            ww = max(0.06 * Rr, d / 1000.0 / np.tan(np.radians(CALDERA_WALL_DEG)))
            pit = d * (1.0 - smoothstep(Rr - ww, Rr, rc))
        else:
            ww = (0.25 if p["caldera"] else 1.0 - CRATER_FLOOR) * Rr
            pit = d * (1.0 - smoothstep(Rr - ww, Rr, rho_e))
        # the rim notched: lower in places (never higher: top_m is its highest point)
        nt = ZK.fbm(np.ascontiguousarray(np.column_stack([Rr * np.cos(th), Rr * np.sin(th), np.zeros(n)]) + 70.0),
                    max(0.8 * Rr, 0.2), 2, 0.5, S + 2) / 0.17
        notch = 0.3 * d * np.clip(nt, 0, 1.5) * np.exp(-((rho_e - Rr) / (0.5 * Rr)) ** 2)
        z = z - pit - notch
    # radial gullies: troughs along the zero lines of noise stretched down the flank, deepest at mid height
    if p["gully_m"] > 0:
        R0 = r if p["kind"] == "strato" else 0.3 * r
        pts = np.ascontiguousarray(np.column_stack([R0 * np.cos(th), R0 * np.sin(th), 0.25 * rho]) + 90.0)
        ng = ZK.fbm(pts, GULLY_KM, 3, 0.5, S + 3) / 0.17
        v = np.exp(-(ng / 0.35) ** 2)  # (rounded V troughs, broad interfluves)
        # deepest on the lower-mid flank, fading out on the fans at the foot and toward the rim
        fz = np.clip(_flank(p, rho_e) / H, 0.0, 1.0)
        start = smoothstep(Rr, Rr + 0.15 * r, rho_e)
        # no deeper than its walls stand at ~35 degrees (a trough ~0.15 of the spacing wide, which grows
        # down the flank as rho / R0) nor than 0.4 of the cone's height there
        d_max = np.minimum(GULLY_WALL_M * rho / R0, 0.4 * fz * H)
        g = np.minimum(p["gully_m"] * smoothstep(0.03, 0.3, fz) * (1.0 - fz) / 0.7, d_max) * v * start
    else:
        g = np.zeros(n)
    # lava flow lobes: tongues down the flank, steep sided, a lobed front; younger than the gullies
    cover = np.zeros(n)
    for th0, r0, L, w0, T, ph, nw in p["flows"]:
        dth = np.angle(np.exp(1j * (th - th0)))
        s_ = rho - r0
        w_ = w0 + 0.12 * np.maximum(s_, 0.0)
        lat = rho * np.sin(dth) - 0.3 * w_ * np.sin(2 * np.pi * nw * s_ / max(L, 0.1) + ph)
        fwd = (np.cos(dth) > 0) & (s_ > -0.1)
        end = L * (1.0 + 0.1 * np.cos(np.pi * lat / np.maximum(w_, 1e-3)))
        tongue = ((1.0 - smoothstep(0.7 * w_, w_, np.abs(lat))) * smoothstep(-0.1, 0.1, s_)
                  * (1.0 - smoothstep(end - 0.6 * w_, end, s_)))
        tongue = np.where(fwd, tongue, 0.0)
        z = z + T * tongue
        cover = np.maximum(cover, tongue)
    z = z - g * (1.0 - cover)
    # rough ground (blocky flows, scoria, small rills) below the gullies' scale, up to ~5 m
    fz = np.clip(_flank(p, rho_e) / H, 0.0, 1.0)
    z = z + (1.5 + 0.0015 * H * fz) * ZK.fbm(Pk + 110.0, ROUGH_KM, 3, 0.5, S + 4) / 0.17
    # parasitic cinder cones (slopes ~30 degrees, a crater 0.3 x their height deep)
    for cx, cy, hc in p["cones"]:
        dc = np.hypot(x - cx, y - cy)
        rb = hc / 1000.0 / 0.36
        rt = 0.25 * rb
        body = hc * smoothstep(rb, rt, dc)
        cr = 0.3 * hc * (1.0 - smoothstep(0.3 * rt, rt, dc))
        z = z + body - cr
    return z


def parent_view(pa, fr, sel_r: np.ndarray, sel_c: np.ndarray, p: dict, res: float) -> np.ndarray:
    """E averaged over each listed parent pixel (rows sel_r, cols sel_c),
    sampled at least as finely as the fine zoom."""
    k = int(np.clip(np.ceil(pa.rp / res), 2, 24))
    o = (np.arange(k) + 0.5) / k - 0.5
    orr, occ = np.meshgrid(o, o, indexing="ij")
    rr = (sel_r[:, None] + orr.ravel()[None, :]).ravel()
    cc = (sel_c[:, None] + occ.ravel()[None, :]).ravel()
    x, y = pa.plane(rr, cc)
    P = pa.fr.to_sphere(x, y)
    return relief(P, p).reshape(len(sel_r), k * k).mean(1)
