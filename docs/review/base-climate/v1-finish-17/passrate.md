# v1-finish-17 pass rate: paired main vs final branch

Measurement only, no model code changed. Same 18 L6 1 Gyr draws (v1-finish-16's set: seeds x climate_offset) per code, with
`+0.0005` and `+0.001` added to every climate_offset; plus L7 1 Gyr, 8 draws, final branch only, `+0.001` roll.
Code: `main` = snapshot of main at 4545212 (tracked files only), `final` = this branch at 1d53797.
Pass = bar + checks at the finish moment (`fmtally.py` "bar + moment checks"). Two criteria:
- old: deep-time bar fails icebox, never-ice and hellhouse (the worktree's `fmtally.py`/`passrate4.py`);
- new: bar fails only a hellhouse (main 99d2b33's `fmtally.py`/`passrate4.py`, run from main). Moment checks are identical
  under both tools (same moment-pass counts on every set), so the only difference is the bar.
No SIM SUSPECT line was printed on any set.

## Per-set pass counts

| Set | old criterion | new criterion | bar failures (old) |
|---|---|---|---|
| main, L6 +0.0005 | 12/18 | 16/18 | 5 icebox |
| final, L6 +0.0005 | 14/18 | 16/18 | 3 icebox |
| main, L6 +0.001 | 14/18 | 16/18 | 3 icebox, 1 hellhouse |
| final, L6 +0.001 | 12/18 | 13/18 | 4 icebox |
| final, L7 +0.001 | 6/8 | 8/8 | 1 never-ice, 1 icebox |

(Moment checks alone: main 16/18, 17/18; final 16/18, 13/18; L7 8/8.)

## Pooled L6 rates

Old criterion, all rolls (earlier rolls as given: final 6/18 and 14/18, main 15/18 on original offsets, no main on the +0.0005 roll before this run):

| Code | Rolls | Pooled |
|---|---|---|
| main | original, +0.0005, +0.001 | 41/54 = 76% |
| final | original, +0.0005 (earlier), +0.0005 (this run), +0.001 | 46/72 = 64% |

Only the rolls run here (+0.0005 and +0.001, same rolls for both codes): main 26/36 = 72%, final 26/36 = 72%.
Note the earlier "+0.0005" roll for the final branch (14/18) and this run's +0.0005 (14/18) agree. Main's original-offset 15/18 has no final counterpart
beyond the earlier 6/18, so the pooled rows above are not matched; the matched comparison is the paired one below.

New criterion, rolls run here only (earlier outputs were deleted, not re-tallable): main 32/36 = 89%, final 29/36 = 81%.

L7 (final only): old 7/8 original, 5/8 re-roll, 6/8 here (+0.001); new 8/8 here.

## Paired per-draw differences (L6, same seed and offset)

Counts: both pass / main only / final only / both fail.

| Roll | old | new |
|---|---|---|
| +0.0005 | 9 / 3 / 5 / 1 | 14 / 2 / 2 / 0 |
| +0.001 | 10 / 4 / 2 / 2 | 11 / 5 / 2 / 0 |
| pooled | 19 / 7 / 7 / 3 | 25 / 7 / 4 / 0 |

Draws where the codes differ (draw = tag, seed; "ICEB" = bar icebox, "HELL" = hellhouse, "M NO" = moment checks fail).

New criterion:
- +0.0005: main-only: l6c_0 733847, l6c_p 819014; final-only: l6c_0 53669, l6c_p 733847 (the failing code fails the moment checks in each).
- +0.001: main-only: l6c_p 639472, l6c_p 733847, l6c_p 957317, l6c_p 958504, l6fix 957317; final-only: l6c_m 958504 (main HELL), l6fix 639472.
  All main-only draws are moment-check failures of final.

Old criterion (adds bar-only differences):
- +0.0005: main-only: l6c_0 733847 (final M NO), l6c_0 819014 and l6c_p 819014 (final ICEB); final-only: l6c_0 53669, l6c_p 619496, l6fix 619496, l6fix 639472 (main ICEB), l6c_p 733847.
- +0.001: main-only: l6c_p 733847, l6c_p 957317, l6c_p 958504, l6fix 957317; final-only: l6c_m 958504 (main HELL), l6c_p 583167 (main ICEB).

## Reading

- Paired, the two codes are indistinguishable: 7 vs 7 discordant draws (old), 7 vs 4 (new); an exact sign test gives p about 0.55 on the latter.
  The 6/18 earlier final result is the outlier, not a systematic shortfall; this run's final +0.0005 roll (14/18) matches the earlier 14/18.
- Individual draws flip between codes in both directions, on both ice-bar and moment checks; the same draws flip on different rolls
  (l6c_p 733847 and 958504, l6fix 957317), i.e. chaotic sensitivity of marginal worlds rather than a systematic change.
- Under the new bar the final branch is lower on the +0.001 roll (13/18 vs 16/18), driven by five l6c_p/l6fix moment-check failures
  (three too cold, -6.5 to -10.4 C with 20-45% land ice; two too warm, +5.4 and +6.8 C); on +0.0005 they tie 16/18. Eight draws is too few to call the +0.001 gap signal.
- The new bar lifts both codes by 3-4 draws per set (icebox worlds now pass).
