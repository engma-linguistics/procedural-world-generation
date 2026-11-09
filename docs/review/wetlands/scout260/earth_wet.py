"""PW-831 scout 260: river discharge through four big wetlands on Earth (terrain + the model's climate;
earth_capture.py's pickle), rerunning hydrology.rivers_and_lakes the way the Earth world does (outlet, closed,
valley), or with nothing imposed (--free, as scout 250's earth_dry.py). Prints each river's profile downstream
of the wetland's inflow gauge and global measures. Usage: earth_wet.py PKL [--free] [--profile]"""
import pickle
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import numpy as np
import planet  # noqa
from planet import hydrology as Hy
from planet import vegetation as V
from planet.grid import build_grid
from planet.geo import is_land

# (name, inflow gauge lat, lon, [(downstream gauge, lat, lon)], observed note)
RIVERS = [
    ("White Nile / Sudd", 5.20, 31.77, [("below Sudd (Lake No, pre-Sobat)", 9.45, 30.6), ("Malakal (+Sobat)", 9.53, 31.65),
                                        ("Khartoum", 15.6, 32.5)]),
    ("Niger / inner delta", 12.87, -7.55, [("Ke-Macina", 13.95, -5.36), ("Dire", 16.27, -3.38), ("Timbuktu", 16.7, -3.0)]),
    ("Okavango", -18.28, 21.78, [("Maun", -19.98, 23.42)]),
    ("Paraguay / Pantanal", -16.07, -57.68, [("Porto Conceicao", -17.1, -57.4), ("Amolar", -18.0, -57.5),
                                             ("Ladario", -19.0, -57.6), ("Porto Murtinho", -21.7, -57.88)]),
]


def nearest(grid, lat, lon, cand):
    la, lo = np.radians(grid.lat), np.radians(grid.lon)
    d = np.arccos(np.clip(np.sin(la) * np.sin(np.radians(lat)) + np.cos(la) * np.cos(np.radians(lat)) * np.cos(lo - np.radians(lon)), -1, 1)) * 6371
    d = np.where(cand, d, np.inf)
    return d


def run(path, free=False, profile=False, label="", hook=None):
    D = pickle.load(open(path, "rb"))
    grid = build_grid(D["level"])
    elev, c, ice = D["elev"], D["c"], D["ice"]
    kw = dict(D["kw"])
    if free:
        kw["outlet"], kw["closed"] = None, None
    if hook:
        c = hook(grid, elev, dict(c), ice, kw) or c
    flow, down, lk = Hy.rivers_and_lakes(grid, elev, c, ice, **kw)
    land = is_land(elev, ice, grid)
    q = Hy.discharge(grid, flow)
    sea = ~land
    mouth = land & (down >= 0) & sea[np.maximum(down, 0)]
    nf = (land & ((ice <= 0) if ice is not None else True)).sum()
    rain_vol = (np.where(land, c["runoff"], 0) / 1000).sum()
    print(f"== {label} L{D['level']}{' free' if free else ''}: to sea {q[mouth].sum()/1e3:.1f} k m3/s "
          f"({100*flow[mouth].sum()/rain_vol:.0f}% of land runoff); inland {100*(lk['endorheic']).sum()/nf:.1f}% ; "
          f"lakes {100*(land&lk['wet']).sum()/land.sum():.2f}% of land")
    s = Hy.seasonal_flow(grid, down, lk["order"], np.where(sea, 0.0, c["runoff"]), lk["wet"], c)
    fw = V.flooded(grid, elev, flow, lk["kind"], dict(precip=c["precip"], pet_y=c["pet"], temp=c["temp"]), ice,
                   flood_ratio=s["flood_ratio"])
    out = {}
    for name, la, lo, gauges in RIVERS:
        d = nearest(grid, la, lo, land)
        cand = d < 1.6 * np.sqrt(4 * np.pi * 6371**2 / grid.n)
        def trace(i):
            p_ = [i]
            while down[p_[-1]] >= 0 and land[down[p_[-1]]] and len(p_) < 400:
                p_.append(int(down[p_[-1]]))
            return np.array(p_)
        # the biggest river near the inflow gauge whose course passes the last downstream gauge (else the biggest)
        cs = np.flatnonzero(cand)[np.argsort(-q[cand])]
        i, P = int(cs[0]), trace(int(cs[0]))
        for j in cs[:30]:
            Pj = trace(int(j))
            if nearest(grid, gauges[-1][1], gauges[-1][2], np.isin(np.arange(grid.n), Pj)).min() < 250:
                i, P = int(j), Pj
                break
        row = [f"{name}: in {q[i]:.0f}"]
        out[name] = {"in": q[i]}
        for g, gla, glo in gauges:
            dg = nearest(grid, gla, glo, np.isin(np.arange(grid.n), P))
            j = int(np.argmin(dg))
            if dg[j] > 250:
                row.append(f"{g}: off path ({dg[j]:.0f} km)")
                continue
            row.append(f"{g} {q[j]:.0f} ({q[j]/max(q[i],1e-9):.2f})")
            out[name][g] = q[j]
        end = P[-1]
        row.append(f"| path ends {grid.lat[end]:.1f},{grid.lon[end]:.1f} {'sea' if (down[end] >= 0 and sea[down[end]]) else 'sink' if lk['sink'][end] else ''}")
        print("  " + "; ".join(row))
        if profile:
            for t, k in enumerate(P[:40]):
                print(f"    {t:2d} {grid.lat[k]:6.1f} {grid.lon[k]:7.1f} z {elev[k]:6.0f} Q {q[k]:7.0f} wet {int(lk['wet'][k])} "
                      f"fl {fw[k]:.2f} P {c['precip'][k]:5.0f} AET {c['aet'][k]:5.0f} R {c['runoff'][k]:5.0f} "
                      f"Eo {c['lake_evap'][k]:5.0f} fill {lk['bed'][k]-elev[k]:5.1f} sw {Hy.wetland_share(grid, elev, lk['bed'], land & ~lk['wet'], flow)[k]:.2f}")
    return out, dict(flow=flow, down=down, lk=lk, fw=fw, grid=grid, c=c, land=land)


def obs_rain(grid, elev, c, ice, kw):
    """the observed rain (GPCC halves, earth_data) through the model's water balance (default Budyko w), on the
    model's temperatures: the wetlands' own climate without the model's rain bias"""
    from tools import earth_data as ED
    from planet import climate as C
    d = ED.earth_on_grid(grid)
    pj, pa = (np.where(np.isfinite(d[k]), d[k], c[m]) for k, m in (("obs_p_jul", "p_jul"), ("obs_p_jan", "p_jan")))
    wb = C.water_balance(grid.lat, c["temp"], c["t_warm"], c["t_cold"], pj, pa)
    c.update(precip=0.5 * (pj + pa), p_jul=pj, p_jan=pa, aet=wb["aet"], runoff=wb["runoff"], pet=wb["pet"])
    return c


VARIANTS = {"main": dict(WETLAND_ET=False, DRY_HOLLOWS=True), "plain": dict(WETLAND_ET=True, WETLAND_MODE="plain"),
            "hollow0.5": dict(WETLAND_ET=True, WETLAND_MODE="hollow", WETLAND_HOLLOW=0.5),
            "hollow1": dict(WETLAND_ET=True, WETLAND_MODE="hollow", WETLAND_HOLLOW=1.0),
            "nodry": dict(WETLAND_ET=False, DRY_HOLLOWS=False),
            "sheet": dict(WETLAND_ET=True, WETLAND_MODE="sheet", WETLAND_N=0.1, WETLAND_H=1.0, DRY_HOLLOWS=True),
            "sheet_n0.2": dict(WETLAND_ET=True, WETLAND_MODE="sheet", WETLAND_N=0.2, WETLAND_H=1.0),
            "sheet_h0.5": dict(WETLAND_ET=True, WETLAND_MODE="sheet", WETLAND_N=0.1, WETLAND_H=0.5)}

if __name__ == "__main__":
    names = [a.removeprefix("--v=") for a in sys.argv if a.startswith("--v=")] or list(VARIANTS)
    for nm in names:
        for kk, v in VARIANTS[nm].items():
            setattr(Hy, kk, v)
        run(sys.argv[1], free="--free" in sys.argv, profile="--profile" in sys.argv, label=nm,
            hook=obs_rain if "--obsrain" in sys.argv else None)
