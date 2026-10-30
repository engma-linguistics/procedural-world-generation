---
title: "Frozen-over fix: the warm-phase rule clears every frozen world on the screen, but it halves Earth's Greenland at today's climate"
type: task
status: needs-decision
parent: null
milestone: v1
subsystem: climate
effort: m
impact: high
found_by: lane71
blocked_by: []
relates: [PW-464, PW-1115, PW-1095]
refs: [planet/icemass.py, planet/tectonics/earth.py, planet/tectonics/params.py, "branch worktree-agent-ad490796ec6c59e7a f38b7931"]
---

## Description
In plain words. The owner asked whether warm years could melt more ice than cold years save. The model already
works that way: since PW-190, the run averages the melt (not the temperature) over 8 orbital states. But a big
sheet barely feels those states, because its bright surface absorbs little of the extra sunshine. So lane 71 built
three changes:
1. A sheet carried from a cold era keeps only what outlasts the cycle's warm phase. The persistent ice is
   computed under the warmest orbital state and seeds the time-mean sheets (Params.ice_warm_persist; PW-464
   item 3, lite).
2. Melting ice is bare ice and absorbs more of the extra sunshine: 1 - 0.565, from Greenland's bare-ice albedo
   at the onset of ablation (Wehrle et al. 2021, GEUS Bulletin 47; Params.ice_bare_absorb).
3. Melting ice gets a gentler summer lapse rate: about 4 C/km in summer and 9 in winter, the same yearly mean
   (Steffen & Box 2001, GC-Net; icemass.SEASON_LAPSE).
All three together (the "kitchen sink") clear every frozen-over world on the screen. But on today's Earth the
model's Greenland shrinks to less than half. Change 3 alone keeps Greenland but doesn't clear the frozen worlds.
Which to take is a call for the owner.

Screen (7 L6 draws, roll 0.0005, 1 Gyr; the 4 frozen-over draws of lane 67's re-judge plus 3 controls; main =
lane 67's X arm, bit-identical to today's main):

| arm | frozen over | passes | glacial max | peak land ice, median | run's p90 land ice, median |
|---|---|---|---|---|---|
| main | 4/7 | 3/7 | 6 | 0.41 | 0.31 |
| kitchen sink (1+2+3) | 0/7 | 4/7 | 3 | 0.24 | 0.18 |
| seasonal lapse only (3) | 2/7 (619496, plus control 733847 at 0.42) | 1/7 | 5 | 0.37 | 0.25 |

The kitchen sink's 3 fails are 819014 (finish too cold, -4.6 C) and two controls that finish too warm (958504
+6.0, 583167 l6fix +3.6). The lapse arm's fails include finishes of +11.0, +5.8 and +4.1 C. (Too-warm finishes
are their own draft.) The kitchen sink costs ~1.2-1.4x the lapse arm per run (wall, same load), within PW-464's
2x.

Earth (L6):
- The staircase's land ice (% of land), down at 0/-2/-4/-6/-8 then back up at -6/-4/-2/0:

  | rule | down-leg | up-leg | gap at 0 |
  |---|---|---|---|
  | main | 10.0/11.3/14.9/20.5/27.6 | 27.5/26.8/23.1/15.3 | 5.3 |
  | kitchen sink | 8.6/10.5/13.0/19.0/25.8 | 25.1/22.9/14.2/10.3 | 1.8 |
  | lapse only | 9.3/10.9/13.9/18.2/25.6 | 25.5/24.1/20.4/11.7 | 2.4 |

- Started from Earth's real ice at dT 0, Greenland keeps 165 L6 cells on main, 150 with the lapse only, and 68 with
  the kitchen sink. Warm persistence alone gives 75, and bare absorb + lapse gives 74. The persistent ice taken
  over the warm half of the states (Params.ice_warm_persist 0.5) is no better (8.7% of land).
- earth_check (real ice): Antarctica's warmest month -14.0 -> -13.7 C (obs -16.1), its coldest -49.2 -> -49.5;
  Vostok and Summit unchanged; Greenland's warmest month -11.4 -> -11.1. The interiors are untouched, as designed.

Options:
- A. Take the kitchen sink and accept a smaller Greenland on Earth-likes for v1. Then open a follow-up: why the
  model's Greenland can't outlast an rms warm orbit (real Greenland outlasted the Eemian), likely tied to PW-1115.
- B. Take the lapse only (Earth-safe), and accept that frozen-over worlds remain (2/7 on the screen). That fails the
  100% hard bar.
- C. Kitchen sink with a gentler warm phase: weight the warm state by the time a sheet needs to retreat (PW-464
  risk (a)). That's a new judgement constant and needs a source.
Lean: C if a source for the retreat time can be found quickly; otherwise A, since the hard bar is frozen-over
worlds and Earth is a plausibility anchor, not a target. Either way, run the full 18-draw judge and an L7 draw
before merging.
- [ ] Owner/coordinator: A, B or C
