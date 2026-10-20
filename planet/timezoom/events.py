"""What the finished simulation says about itself: where the ice cycles, and the glacial events."""

from __future__ import annotations

import numpy as np

from .. import store as S
from ..grid import Grid
from ..orbit import insolation
from .params import LAYERS


def cycling_ice_sun(g: Grid, area: np.ndarray, frames: list[dict], ice_frames: list, ref_orb) -> dict:
    """Where the ice comes and goes, and the summer sun there (PW-428). The
    cycling ice: cells iced (> 1 m) in the frame with the most ice volume but
    not in the one with the least. Its hemisphere is the one with more of
    that area; its latitude the area-weighted mean there (65 N when no ice
    cycles). Adds each frame's stats["insol_ice_summer_anom"]: the mean
    daily insolation anomaly (W/m2, against the reference orbit) of that
    latitude's two midsummer months (Jun-Jul north, Dec-Jan south), as
    insol_65n_jul_anom is for 65 N. Returns {lat, area_mkm2}."""
    vol = [f["stats"]["ice_volume_mkm3"] for f in frames]
    hi, lo = (S.decode(ice_frames[int(f(vol))], LAYERS["ice"]) for f in (np.argmax, np.argmin))
    cyc = (hi > 1) & (lo <= 1)
    south = float(area[cyc & (g.lat < 0)].sum()) > float(area[cyc & (g.lat >= 0)].sum())
    sel = cyc & ((g.lat < 0) if south else (g.lat >= 0))
    lat_c = float((g.lat[sel] * area[sel]).sum() / area[sel].sum()) if sel.any() else 65.0
    months = [9, 10] if lat_c < 0 else [3, 4]  # (month 0 starts at the March equinox)
    q_ref = insolation(*ref_orb, lat=np.array([lat_c]))[0, months].mean()
    for f in frames:
        s = f["stats"]
        q = insolation(s["obliquity"], s["eccentricity"], s["perihelion"], lat=np.array([lat_c]))[0, months].mean()
        s["insol_ice_summer_anom"] = round(float(q - q_ref), 1)
    return {"lat": round(lat_c, 1), "area_mkm2": round(float(area[sel].sum()) / 1e12, 2)}


def glacial_events(res: dict, g: Grid, min_swing: float = 15.0) -> list[dict]:
    """Glacial maxima and interglacials: turning points of sea level that
    differ from the neighbouring turning points by >= min_swing m."""
    fr = res["frames"]
    sl = np.array([f["stats"]["sea_level_change_m"] for f in fr])
    turns, ext, d = [], 0, 0  # zig-zag: a leg ends once sea level turns back by min_swing
    for i in range(1, len(sl)):
        if d == 0:
            if abs(sl[i] - sl[0]) >= min_swing:
                d, ext = (1 if sl[i] > sl[0] else -1), i
        elif (sl[i] - sl[ext]) * d > 0:
            ext = i
        elif abs(sl[i] - sl[ext]) >= min_swing:
            turns.append((ext, d < 0))
            ext, d = i, -d
    ev = []
    for i, lo in turns:
        ice = S.decode(res["data"]["ice"][i], LAYERS["ice"])
        j = int(np.argmax(ice))
        s = fr[i]["stats"]
        ev.append({"t": fr[i]["t"], "kind": "glacial max" if lo else "interglacial",
                   "text": f"sea level {s['sea_level_change_m']:+.0f} m, land ice {s['ice_pct']}% of the surface, "
                           f"thickest {int(ice[j])} m", "lat": round(float(g.lat[j]), 1),
                   "lon": round(float(g.lon[j]), 1)})
    return ev
