"""PW-831 scout 261: the dry hollows _dry_hollows keeps on Earth (earth_capture.py's pickle), per hollow: cells,
area, depth, catchment rain / PET, the water arriving (routed inflow from outside the hollow), the open-water
deficit over the whole hollow, and the lake at balance. Usage: diag_hollow.py PKL [--obsrain] [LAT LON ...]"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
sys.path.insert(0, str(Path.cwd() / "docs/review/wetlands/scout260"))
import numpy as np
from planet import hydrology as Hy, kernels
from planet.ocean import cell_area_km2
import earth_wet as EWt

cap = []
orig = Hy._dry_hollows


def spy(grid, ground, bed, land, src, loss, rain, pet):
    r = orig(grid, ground, bed, land, src, loss, rain, pet)
    if not cap:
        cap.append((grid, ground, bed, land, src, loss, rain, pet, r))
    return r


Hy._dry_hollows = spy
pts = [float(a) for a in sys.argv[2:] if not a.startswith("--")]
EWt.run(sys.argv[1], label="diag", hook=EWt.obs_rain if "--obsrain" in sys.argv else None)
grid, ground, bed, land, src, loss, rain, pet, keep = cap[0]
A = cell_area_km2(getattr(grid, "base", grid))
sea, rcv, asc = kernels.lake_order(np.where(keep, ground, bed), ~land, grid.nbr_off, grid.nbr_idx)
wet, open_, out_z, pit, catch, basin = kernels.lakes_on(np.where(keep, ground, bed), grid.nbr_off, grid.nbr_idx, src, loss, sea, rcv, asc)
_, down, order = kernels.priority_flood(np.where(keep, ground, bed), ~land, grid.nbr_off, grid.nbr_idx, 0.0)
lab, k = grid.components(keep)
up = Hy._upstream_label(down, order, lab)
q = float(Hy.discharge(grid, np.ones(1))[0])  # m3/s per flow unit per cell
rows = []
fz = kernels.priority_flood(ground, ~land, grid.nbr_off, grid.nbr_idx, 0.0)[0]
for h in range(k):
    m = lab == h
    c = up == h
    out = c & ~m
    qin = src[out].sum() * q  # water arriving from outside (flow units -> m3/s), before any upstream lake losses
    qloc = src[m].sum() * q
    deficit = (loss[m]).sum() * q  # open-water evaporation minus land AET over the whole hollow

    rows.append((A[m].sum(), h, m.sum(), (fz - ground)[m].max(), rain[c].sum() / max(pet[c].sum(), 1e-9),
                 qin, qloc, deficit, wet[m].sum(), grid.lat[m].mean(), grid.lon[m].mean(), c.sum()))
rows.sort(reverse=True)
print("area_km2 id cells depth_m P/PET_catch Qin_m3s Qloc deficit_whole wetcells lat lon catchcells")
for r in rows[:25]:
    print(f"{r[0]:9.0f} {r[1]:4d} {r[2]:4d} {r[3]:6.0f} {r[4]:5.2f} {r[5]:8.0f} {r[6]:7.0f} {r[7]:8.0f} {r[8]:4d} {r[9]:6.1f} {r[10]:7.1f} {r[11]}")
