---
id: PW-190
title: Land ice lowers the sea by up to 300+ m on some seeds (about 4x Antarctica's volume)
type: task
status: done
parent: null
subsystem: climate
effort: s
impact: med
found_by: tectsea
blocked_by: []
relates: [PW-053]
refs: [planet/tectonics/earth.py, tools/sealevel.py, planet/timezoom.py, "world 8e71fd", "run ee65aa", "world bcc894", planet/timezoom_kernels.py]
created: 2026-10-14
updated: 2026-10-15
---

## Description
After the ocean-basin part of sea level was smoothed and soft-limited (PW-053,
tectsea), the largest remaining fast sea-level swings on some seeds come from
land ice (`sim.sea_ice = -0.9 x ice volume / ocean area`, earth.update_climate).
`tools/sealevel.py`, L6, 1 Gyr, default params:
- seed 11: sea_ice 0 -> -168 m (140 -> 160 Myr) -> -338 m (220 Myr), back to 0 by
  320 Myr; the largest 20-Myr sea-level change of the run (-280 m at 140-160) is
  158 m ice + 122 m basins;
- seed 2: sea_ice down to -191 m (before the change: -274 m); seed 21 -149 m.
- with the PW-024 plate nudge as well (final tectsea code): seed 2 sea_ice -218 m within
  20 Myr at ~736 Myr (the run's largest 20-Myr sea-level change, -264 m), seed 11 -190 m
  within 20 Myr at ~160 Myr; the ocean-basin part now moves at most 98-140 m in 20 Myr.
-338 m is ~120 M km3 of ice, ~4x Antarctica's, ~1.7x Earth's total at the Last
Glacial Maximum (~-130 m below today, plus ~65 m still in ice). The model's sheets
are meant as the average over ~100 kyr ice-age cycles, which should sit between
interglacial and glacial volume, not well beyond the glacial peak.
Check: sheet thickness (Nye profile with ICE_TAU = 50 kPa, up to 4 km) over a
polar supercontinent; whether the area is plausible (ice_pct then); and whether
ice building to ~-300 m within 40 Myr is the ice following continental drift
(fine) or a runaway in the albedo feedback (ICE_FEEDBACK, ice_albedo).
- [ ] the largest sea_ice on 4 L6 seeds x 1 Gyr understood, and either justified or
  brought to roughly the LGM's scale (~-150..-200 m)

## Updates
- 2026-10-15: Status in-progress -> done. Merged (icemb): planet/icemass.py shared surface mass balance (lying snow tracked monthly; Greenland margins now ablate); flow-consistent run ice rule; time zoom margins and anchors. Time-zoom spreads now -56 to -239 m (was -127 to -321). Run cold eras still large on 2 of 4 seeds: PW-240.
- 2026-10-15: Status todo -> in-progress. Worktree icemb (decision C).
- 2026-10-15: Status in-progress -> todo. Coordinator decision (north star): option C. Recalibrate the shared surface mass balance used by the run and the time zoom (snowline set by snowfall, PW-159; margins must melt where bare-ground summers are ~9 C) so the flow-consistent rule then yields modest run ice AND a small time-zoom spread; ship the balance rule (B) only on top of that. Shipped meanwhile: PW-102 rule + isostasy + ice-albedo cooling capped at 3 C. D (long-term weathering thermostat for -9 to -17 C eras) is a separate ticket.
- 2026-10-15: Merged inbox draft draft-run-ice-flow-consistent-makes-it-icier.md ("Run ice: a flow-consistent (ablation-zone) rule makes the run much icier, so PW-190's decision C can't shrink both the run's ice and the time zoom's spread", found by ice).
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
- 2026-10-15: Status todo -> in-progress. Overnight agent, worktree ice.
- 2026-10-14: Coordinator decision (north star): option C. The run's ice rule gets an ablation zone / becomes flow-consistent here, which fixes both the too-large run ice and the time zoom's cold-era spread (8e71fd: -258 m). Until then A: cold-era finished worlds glaciate hard, as documented in overview 2.14. B (spin-up balance) skipped as a half measure.
- 2026-10-14: Merged inbox draft draft-timezoom-cold-era-spread.md ("Time zoom: cold-era generated worlds still drop ~250 m, because the run's ice has no ablation zone", found by finish).
  After the PW-031 nudge (sea level from the water the ice holds; a run's start counted as the
  cycle average, so half the CO2 / ice-albedo caps), the time zoom of world bcc894 (run e0e21e
  @ 688 Myr, dT -3.3) peaks at -132 m (was -171) and an Earth-like moment (e0e21e @ 592, dT -0.7)
  at -95 m. But world 8e71fd (run ee65aa @ 632 Myr, dT -5.8, LGM-cold, sea already -274 m) still
  reaches -258 m (was -272), and almost all of it is not the feedbacks: with CO2 and ice albedo
  off, and even with the orbit off, it still falls -210 m in 60-80 kyr.
  
  Diagnosis: the main run's ice (PW-102 rule: where summers stay below 1 C and snow beats melt,
  no flow) is all accumulation zone. Every starting ice cell gains (median +0.17 m/yr; the
  start_anchor is zero there), ~10,800 Gt/yr of snow against ~1,700 Gt/yr of melt. The flowing
  sheets must spread until melt and calving balance them: 6.3% -> ~14% of the surface (all land
  poleward of ~55 deg, which the run had partly bare with summers of 2-4 C). Starting warmer over
  the ice (+3 or +6 C over the start sheets) only slows it.
  
  Options:
  - A. Accept: a cold-era moment's ice-age maximum really is far bigger than the run's average
    ice; document it (done in overview 2.14) and let finished worlds show it.
  - B. Balance the start: a sheet-by-sheet temperature correction (two-sided anchor) found by a
    short spin-up, so the start ice neither grows nor shrinks at the mean orbit; cycles then swing
    around the run's ice. ~1 min extra at L7; changes the meaning of the anchor for Earth too.
  - C. Fix the source: make the main run's ice rule flow-consistent (extend it by an ablation
    zone; ties to PW-190's too-thick run ice and PW-189 isostasy). Biggest, but fixes both.
  Lean: C as the real fix (with PW-190), A meanwhile; B only if finished cold-era worlds must look
  moderate soon.
- 2026-10-14: Created from inbox draft draft-ice-sea-level-depth.md (found by tectsea).
