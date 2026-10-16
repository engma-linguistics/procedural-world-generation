"""PW-359: what plate motion and resampling (Simulation._resolve) do to
plate interiors, where a rigid plate should only carry its relief along.

    uv run python docs/review/audit/tectonics-night/resample.py <repo> <level> <seed> <myr>

Per step after 50 Myr, on land cells at least 3 cells from any plate
boundary (before and after the move): rms elevation change under resolve,
the share of world cells sampling a plate cell another world cell also
samples (duplicates) and of the plate's owned cells nobody samples (gaps),
local pits (lower than every neighbour) before / after, how many of the
new pits sit on or next to a duplicated or gap-adjacent cell, and closed
hollow volume (priority flood on land) before / after resolve.
"""
import sys

sys.path.insert(0, sys.argv[1])
import planet  # noqa: E402,F401
import numpy as np  # noqa: E402
from planet import kernels  # noqa: E402
from planet.grid import build_grid  # noqa: E402
from planet.geo import R_KM  # noqa: E402
from planet.tectonics import Params, Simulation  # noqa: E402

level, seed, myr = int(sys.argv[2]), int(sys.argv[3]), float(sys.argv[4])
g = build_grid(level)
ckm2 = 4 * np.pi * R_KM ** 2 / g.n
src = np.repeat(np.arange(g.n), np.diff(g.nbr_off))
rows = []


def interior(owner, rings=3):
    same = owner[g.nbr_idx] == owner[src]
    ok = np.logical_and.reduceat(same, g.nbr_off[:-1])
    for _ in range(rings - 1):
        ok = ok & np.logical_and.reduceat(ok[g.nbr_idx], g.nbr_off[:-1])
    return ok


def pits(e):
    lower = np.logical_and.reduceat(e[g.nbr_idx] > e[src], g.nbr_off[:-1])
    return lower & (e > 0)


def hollow(e, kept=False):
    """m of closed hollow per land cell; kept: only the hollows lakes keep
    (hydrology._bed: MIN_DEPTH, MIN_SLOPE), as basins-lakes/hollow_budget.py."""
    land = e > 0
    e = np.asarray(e, float)
    if kept:
        from planet import hydrology
        e = hydrology._bed(g, e, hydrology.MIN_DEPTH, hydrology.MIN_SLOPE)
    sp = kernels.priority_flood(np.asarray(e, float), g.nbr_off, g.nbr_idx, 0.01)[0]
    return np.where(land, np.maximum(sp - e, 0), 0)


real = Simulation._resolve


def resolve(self):
    e0, o0, d0, w0 = self.w_elev.copy(), self.owner.copy(), self.dyn.copy(), self.swell.copy()
    out = real(self)
    if self.t <= 50:
        return out
    e1, o1 = self.w_elev, self.owner
    keep = interior(o0) & interior(o1) & (o0 == o1) & (e0 > 0) & (e1 > 0)
    pl = self.plates
    ref = pl.idx[o1, np.arange(g.n)]
    key = o1 * g.n + ref
    _, inv, cnt = np.unique(key, return_inverse=True, return_counts=True)
    dup = cnt[inv] > 1
    seen = np.zeros_like(pl.owned)
    seen[o1, ref] = True
    gaps = (pl.owned & ~seen).sum() / max(pl.owned.sum(), 1)
    near_dup = np.logical_or.reduceat(dup[g.nbr_idx], g.nbr_off[:-1]) | dup
    p0, p1 = pits(e0) & keep, pits(e1) & keep
    h0, h1 = hollow(e0), hollow(e1)
    h1_nodyn = hollow(e1 - (self.dyn - d0))  # (as if the subsidence term had not been recomputed)
    k0, k1, k1n = hollow(e0, True), hollow(e1, True), hollow(e1 - (self.dyn - d0), True)
    rows.append(dict(
        rms=float(np.sqrt(np.mean((e1 - e0)[keep] ** 2))) if keep.any() else 0.0,
        n=int(keep.sum()), dup=float(dup.mean()), gaps=float(gaps),
        pits0=int(p0.sum()), pits1=int(p1.sum()), new_near_dup=int((p1 & ~p0 & near_dup).sum()),
        new=int((p1 & ~p0).sum()), hol0=float(h0[keep].sum() * ckm2 / 1e3), hol1=float(h1[keep].sum() * ckm2 / 1e3),
        all0=float(h0.sum() * ckm2 / 1e3), all1=float(h1.sum() * ckm2 / 1e3),
        all1_nodyn=float(h1_nodyn.sum() * ckm2 / 1e3),
        bnd0=float(h0[~keep].sum() * ckm2 / 1e3), bnd1=float(h1[~keep].sum() * ckm2 / 1e3),
        k_int=float((k1 - k0)[keep].sum() * ckm2 / 1e3), k_bnd=float((k1 - k0)[~keep].sum() * ckm2 / 1e3),
        k_nodyn=float((k1n - k0).sum() * ckm2 / 1e3)))
    return out


Simulation._resolve = resolve
sim = Simulation(g, seed, Params(flora_end=myr), 2.0)
sim.run(myr)
a = {k: np.array([r[k] for r in rows]) for k in rows[0]}
print(f"L{level} seed {seed} {myr} Myr, {len(rows)} steps after 50 Myr; interior land cells/step {a['n'].mean():.0f}")
print(f"  rms elevation change of interior land under resolve: {a['rms'].mean():.1f} m (median step "
      f"{np.median(a['rms']):.1f})")
print(f"  world cells sampling a duplicated plate cell {a['dup'].mean() * 100:.1f}%, plate cells unsampled "
      f"{a['gaps'].mean() * 100:.1f}%")
print(f"  interior land pits before {a['pits0'].mean():.1f}, after {a['pits1'].mean():.1f}; new per step "
      f"{a['new'].mean():.1f}, of them on/next to a duplicate {a['new_near_dup'].mean():.1f}")
print(f"  interior closed-hollow volume km3 before {a['hol0'].mean():.0f}, after {a['hol1'].mean():.0f} "
      f"(+{(a['hol1'] - a['hol0']).mean():.0f} per step)")
print(f"  all land closed-hollow volume km3: +{(a['all1'] - a['all0']).mean():.0f} per step; outside the "
      f"interiors +{(a['bnd1'] - a['bnd0']).mean():.0f}; with the subsidence term held "
      f"+{(a['all1_nodyn'] - a['all0']).mean():.0f}")
print(f"  kept hollows (the lakes' filter) km3 per step: interiors {a['k_int'].mean():+.0f}, outside "
      f"{a['k_bnd'].mean():+.0f}, all with the subsidence term held {a['k_nodyn'].mean():+.0f}")
