---
title: "Run ice: a flow-consistent (ablation-zone) rule makes the run much icier, so PW-190's decision C can't shrink both the run's ice and the time zoom's spread"
type: task
status: needs-decision
parent: null
subsystem: climate
effort: m
impact: high
found_by: ice
blocked_by: []
relates: [PW-190, PW-189, PW-159, PW-033, PW-031]
refs: [planet/tectonics/earth.py, planet/timezoom.py, planet/timezoom_kernels.py, "run ee65aa"]
---

## Description
PW-190's coordinator decision C was to make the run's ice rule flow-consistent (an ablation
zone), expecting it to fix both the too-large run ice and the time zoom's cold-era spread.
I built it twice on the ice branch and measured it on L6 seeds 3199 and 11 (1 Gyr each,
time zooms of 150 kyr from the 688 Myr keyframe and from the run's coldest moment, all
feedbacks on). The result: consistency works, but it makes the **run** much icier. The
two goals pull in opposite directions, because the time zoom's own mass balance wants
much more ice than the run's rule gives.

What I tried (all with glacial isostasy, PW-189; numbers are from before the PW-215
determinism fix, so they are a little noisy, but the differences are large):

| run ice rule | 3199: run sea_ice min / mean | 3199: time zoom's extra fall | seed 11: run min |
|---|---|---|---|
| main before this branch (PW-102 rule, no isostasy) | -206 / -37 m | -220..-242 m | -449 m (dT -17.8 C) |
| PW-102 rule + isostasy + ice-albedo cap 3 C (**shipped**) | -53 / -20 m | -167..-207 m | -326 m (dT -14) |
| balance rule: time-zoom mass balance, extent closed by snow = melt + calving | -449 / -146 m | -37..-79 m | -583 m |
| same + ice-albedo cap 2-3 C | -334..-388 / -134..-141 m | -117..-179 m | -626 m |
| hybrid: PW-102 accumulation zone + a balance-closed bare-ice ablation fringe | -209 / -90 m | -179..-231 m | -537 m |

The "balance rule" (`surface_balance` with `timezoom_kernels.climate_step` at the mean
orbit, then `ablation_zone`: each sheet spreads ring by ring onto its neighbouring land,
the least-melting cells first, while its snow pays for their melt and calving; Nye
thickness on the pressed bed) makes a time zoom start in balance: its relative fall
drops to -37..-80 m at the same moments. But its sheets are the mean-orbit equilibrium of
the time zoom's physics, which on these planets is 8-15% of the surface in a cold era
(the run's PW-102 rule: 2-5%). The extra ice then cools the run through the ice-albedo
term, which grows the ice further; seed 3199 spends half its history below -100 m.

Why the time zoom wants so much ice: once a sheet exists, its margins stay bright snow
(summer_damp 0.6, melt_hold 0.5 on top of the low snow degree-day factor), so land with
bare-ground summers of ~9 C (median of the cells it spreads onto, 50-77 deg) accumulates
once ice has flowed onto it. Earth's time zoom doesn't show it because Earth's sheets are
ringed by sea (no tundra to spread onto) and Canada has no seed: at the mean orbit with
feedbacks off, Earth stays at 3% (dT 0), 5.3% (dT -1.5, -65 m), 7.3% (dT -3.4, -124 m).
Generated planets have Earth's amount of land poleward of 50 deg (8.7-10% vs Earth's 9.1%),
so it isn't geography.

Options:
- A. Keep what shipped: the run's ice stays the PW-102 rule (the average cycle, LGM-scale:
  -53 m worst on 3199), and a time zoom from a cold moment grows a glacial maximum that is
  ~-170..-240 m below it (absolute ~-200..-260 m, a bit beyond Earth's LGM, -195 m vs ice-free).
  Run and time zoom stay inconsistent: the time zoom never swings back to the run's ice.
- B. Ship the balance rule (consistency, decision C as written): run cold eras -330..-630 m,
  a much icier planet on average, smaller time-zoom swings.
- C. Recalibrate the shared mass balance (the time zoom's bright-snow damping, perhaps a
  stronger margin melt), then use it in both the run (balance rule) and the time zoom, so
  one physics gives the run's average and the time zoom's cycles. Must be checked against
  Earth (PW-033: Earth already glaciates too weakly in full cycles, so the inception side
  must not get weaker). Also the natural home of PW-159 (a snowline from snowfall and
  summer warmth, the same in run and zoom).
- D. Limit the run's cold extremes instead (a real long-term weathering thermostat: the
  model's CO2 baselines learn the current sink, so a cold era is never pushed back), which
  shrinks seed 11's -14..-17 C eras that drive the worst numbers.

Lean: C (with D as a separate climate ticket). A is a fine interim (it is what the
branch ships). The balance-rule code is in the ice branch's history in this agent's
report (earth.surface_balance / ablation_zone), easy to bring back.
- [ ] decide A / B / C (+ D)

Balance-rule code tried (earth.py; replaced ice_sheets' extent step, kept its Nye thickness):

```python
def surface_balance(sim, land, ground, h, bare=False):
    """m of ice/yr each land cell would gain or lose under h m of ice (0: bare), at the mean
    orbit: timezoom_kernels.climate_step with TZParams defaults; bright snow iterated twice."""
    from ..timezoom import BAND_DEG, BAND_LAT, TZParams
    from ..timezoom_kernels import climate_step
    p, g = TZParams(), sim.grid
    t_warm, t_cold, _ = ground
    n, lat = g.n, g.lat
    band = np.clip(((lat + 90) / BAND_DEG).astype(np.int64), 0, len(BAND_LAT) - 1)
    dq, z = np.zeros((len(BAND_LAT), 12)), np.zeros(n)
    f_ice, f_alb = np.clip(h / p.albedo_h, 0, 1), np.clip(h / p.snow_h, 0, 1)
    smb, t_ann, t_w, t_c, p_scale = (np.zeros(n) for _ in range(5))
    bright = np.zeros(n) if bare else np.ones(n)
    for _ in range(1 if bare else 2):
        f_snow = f_alb * (p.bare_share + (1 - p.bare_share) * bright)
        climate_step(land, lat >= 0, 0.5 * (t_warm + t_cold), 0.5 * np.maximum(t_warm - t_cold, 0), sim.p_jul,
                     sim.p_jan, -climate.LAPSE * h, z, z, band, dq, f_ice, f_snow,
                     climate.TUNE["ice_cooling"] * p.albedo_share, p.summer_damp, p.melt_hold, p.pdd_sigma,
                     p.ddf_snow, p.ddf_ice, p.refreeze, p.precip_k, smb, t_ann, t_w, t_c, p_scale)
        bright = np.clip(1 + smb / p.bright_smb, 0, 1)
    return smb

ICE_CALVE = 5e4  # m2/yr lost by calving per m of coast a sheet reaches

def ablation_zone(sim, land, iced, smb, rings=40):
    """Spread each sheet ring by ring onto neighbouring land, cheapest (least melt + calving)
    cells first, while its snow (sum of smb > 0) pays for them."""
    g = sim.grid
    area = sim.cell_area * (R_KM * 1000.0) ** 2
    width = g.spacing * R_KM * 1000.0
    off, idx = g.nbr_off, g.nbr_idx
    src = np.repeat(np.arange(g.n), np.diff(off))
    sea_nb = np.add.reduceat((~land)[idx], off[:-1])
    calve = ICE_CALVE * width * np.minimum(sea_nb, 3) / 2.0 / area
    cost = np.maximum(-smb, 0.0) + calve
    lab, nk = kernels.components(iced, off, idx)
    budget = np.bincount(np.maximum(lab, 0), weights=np.where(iced, smb - calve, 0.0), minlength=nk)
    open_ = budget > 0
    for _ in range(rings):
        nb_lab = np.where(iced[idx], lab[idx], -1)
        cand = np.full(g.n, -1)
        np.maximum.at(cand, src, nb_lab)
        cand = np.where(land & ~iced & (cand >= 0), cand, -1)
        cand = np.where(cand >= 0, np.where(open_[np.maximum(cand, 0)], cand, -1), -1)
        cells = np.flatnonzero(cand >= 0)
        if len(cells) == 0:
            break
        k, c = cand[cells], cost[cells]
        o = np.lexsort((c, k))
        cells, k, c = cells[o], k[o], c[o]
        cum = np.cumsum(c)
        start = np.searchsorted(k, k, side="left")
        before = cum - c - np.where(start > 0, cum[start - 1], 0.0)
        take = before + c <= budget[k]
        cells, k, c = cells[take], k[take], c[take]
        if len(cells) == 0:
            break
        spent = np.bincount(k, weights=c, minlength=nk)
        took = np.bincount(k, minlength=nk)
        ring = np.bincount(cand[cand >= 0], minlength=nk)
        budget -= spent
        open_ &= (took == ring) & (budget > 0)
        iced[cells] = True
        lab[cells] = k
        if not open_.any():
            break
    return iced

# balance rule's extent: acc = land & (surface_balance(h = old ice or the 330 m edge) > 0), grown
# from cells where bare-ground snow survives or old ice stands, then iced = ablation_zone(acc ...).
# hybrid: PW-102's cold & snowy zone as acc, fringe costs from surface_balance(..., bare=True).
```

After merging main (vegclim, PW-215), on the shipped code vs main, 4 L6 seeds x 1 Gyr: run sea level
from ice, worst / mean: 3199 -115 / -37 (main -102 / -23), 11 -289 / -46 (-353 / -53), 2 -281 / -61
(-243 / -49), 21 -133 / -27 (-155 / -28); the worst moments are dT -5..-10 C eras. Time zooms
(150 kyr) from the coldest moment still fall a further -140..-360 m (main -140..-440 m), from 688 Myr
-62..-286 m (main -49..-260 m): the time zoom glaciates harder since the vegclim climate.
