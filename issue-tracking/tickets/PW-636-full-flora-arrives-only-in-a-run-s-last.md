---
id: PW-636
title: Full flora arrives only in a run's last ~15-25%, so showcase moments are squeezed to its end
type: task
status: done
parent: null
milestone: v2
subsystem: surface
effort: s
impact: med
found_by: pw634-bug-hunt
blocked_by: []
relates: [PW-634, PW-434]
refs: [planet/vegetation.py, planet/highlights.py, planet/timeline.py]
created: 2026-10-23
updated: 2026-10-29
---

## Description
The plant groups (`vegetation.GROUPS`, decision 3) appear at Earth's fractions of the span from
`plants_from` to the hard deadline (`group_windows`): flowering trees and shrubs ~0.73, grasses ~0.85,
C4 grasses and succulents ~0.94 (each jittered 0.6-1.3x). In the v1 1 Gyr runs the full flora exists
only from 772-876 Myr on; in the 2 Gyr Earth-like run bf5ee9 from 1636 Myr. Before that a world has
moss/crust in the grass and shrub niches, so no pasture, little foraging or fuel (PW-634).

PW-634's fix makes `highlights.representative_time` (`--at auto`, `planet make`) pick only among frames
once the last group has appeared. That leaves 32-58 candidate frames (128-232 Myr) per 1 Gyr run, and
those frames are the run's end, where sea level runs deepest (the 2026-10-21 health batch: 7 of 8 runs
end at -370..-600 m, PW-434). On the stored runs the new picks sit 30-150 m below the run median in 6 of 9
(still inside the note's band, so not flagged).

The decision: is "the full flora only at the end of the run" what we want? Options:
1. Keep it (evolution is part of the story; showcases are late-run worlds). Nothing to do.
2. Compress the timeline so every group exists by, say, 60-70% of the span (changes `simulate` outputs:
   the serial physics lane's call, re-run goldens).
3. Pick showcases by geography alone and let a pre-grass world be a pre-grass world, labelled in the
   viewer (revert the PW-634 restriction to a nudge).
Recommendation: 1 for v1 (cheapest, already merged), revisit with 2 when PW-434's deep end-of-run sea
level is fixed or if late-run geography turns out atypical.
- [ ] owner picks an option

## Updates
- 2026-10-29: Removed docs/review/base-climate/thermostat-1024/ in cleanup; last present at 9861e2df.
- 2026-10-23: Status todo -> done. Landed in main via thermostat lane 1024 (a99cd2c, merged with fd21d15): FLORA_PACE 0.8; health no signal (12.3 -> 12.0% pooled deep share, 16 seeds).
- 2026-10-23: Thermostat lane 1024 step 2: fd7c174 re-applied on main + PW-680's fixed bed test. 611 passed; health (16 seeds) pooled deep share 12.3 -> 12.0%, icehouse +1.5 +- 9.3 points paired (no signal); golden regenerated; scorecard Earth 71.1%. Green to merge. docs/review/base-climate/thermostat-1024/.
- 2026-10-23: Merge lane 1024 step 5: red on test_bed_settles_under_the_ice (47.1 m vs 46.2 m tolerance, one world, both re-rolled draws); not merged, held on PW-680. Branch worktree-agent-a7d7d62cbdfbcd691 kept.
- 2026-10-23: Held branch worktree-agent-a7d7d62cbdfbcd691 (a3128cc): FLORA_PACE 0.8, C4 at ~0.68 of the run, 63-92 candidate frames. Health quick deepens icehouses (29 -> 43%); to be re-measured on top of PW-646 C (which amplifies sink-side changes ~29%) and PW-643's harness. Merge order: A20, then A22+C, then this.
- 2026-10-23: Built (run lane, branch worktree-agent-a7d7d62cbdfbcd691). `vegetation.FLORA_PACE` = 0.8 scales every
  group's Earth fraction in `group_windows`. GROUPS keeps Earth's numbers, order and spacing. 0.8 rather than
  0.66/0.94 because draws land before the nominal fraction: the stored 1 Gyr runs had C4 at 772-872 Myr (mean ~0.83).
  Windows at 1 Gyr, old -> new (Myr): marsh 46-99 -> 36-79; forests 114-247 -> 91-198; flowering 416-902 -> 333-721;
  grasses 484-950 -> 388-840; C4/succulents 536-950 -> 429-929. On 3 new L6 1 Gyr runs (seeds 7, 13, 101) C4
  arrived at 752, 660, 636 Myr (mean 0.68) and `representative_time` had 63-92 candidate frames (was 32-58). Picks
  780, 772, 844 Myr, all within 30 m of the run's median sea level; the old 1 Gyr picks sat at 844-996. Golden
  `sim_L4_s1_60myr.json` regenerated. Side effect: the quick health sweep runs icier (icehouse 29 -> 43%,
  ice SL after 250 Myr -31 -> -50 m), filed as a draft against the thermostat question (PW-611/PW-576).
- 2026-10-23: Status needs-decision -> todo. Owner 2026-10-24: option 2, compress the flora timeline under the presumption that a world's starting point is much earlier: C4 grasses and succulents at ~66% of the run instead of ~94%, the other groups earlier in proportion. Changes simulate outputs: serial physics lane.
- 2026-10-23: Created from inbox draft draft-flora-arrives-late-in-runs.md (found by pw634-bug-hunt).
