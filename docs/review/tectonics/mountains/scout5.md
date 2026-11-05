# Scout 194 (PW-1446 pass 3 of 3): the height cap re-judged on fresh draws

**In plain words.** Scout 190's fix stops crust thickening once it stands too high (as Tibet does) instead of at a fixed
thickness. On its first 36-draw judge the climate spread widened (sd 1.25 to 1.80 C) and one planet froze over, so it was held.
Scout 193 found no physical reason for that (the carbon thermostat pushes back as hard with lower peaks) and the widening looked
like one unlucky sample (p 0.025). This pass re-judged the fix against today's code (D47, grass roots, yardstick) on 36 fresh L6
draws (two roll rates x 18 seeds/tags). It passes the bar, so it is merged.

## Result (baseline: main, same 36 draws; outputs in scout5/)

| bar | main | cap | verdict |
|---|---|---|---|
| hard failures (frozen over at the end, boiled, ocean loss, CO2 crash) | 0/36 | 0/36 | pass |
| soft pass | 32/36 | 32/36 (29 both, 3 each alone; McNemar p 1.000) | pass |
| late dT range (bar -6..+5) | -2.35..+4.36 | -2.22..+3.67 | pass |
| late dT sd (bar ~1.3-1.7) | 1.78 | 1.36 | pass |
| frozen at some moment after 300 Myr, reported only | 0 | 3 | reported |
| icehouse, reported only | 34 | 36 | reported |

Pooled with scout 190's 36 draws (72 paired): soft 63 vs 61 (McNemar p 0.774), frozen over at the end 0 vs 1, spread (mean |dev|)
1.21 vs 1.29, permutation p 0.647: no difference in spread.

Relief (scout3_hyps over 36 draws, median of draw medians): top cell 8,211 m on main, 6,969 m with the cap; share of land cells
over 7 km 0.16% to 0.00%.

The scorecard (2 seeds, 1 Gyr L6) was run on the merged branch; its earth part was skipped because the worktree had no
data/earth (PW-1474). tools/earth_check.py runs on real Earth geography, which the cap does not touch; it was run on main after the
merge.

Files: scout5/judge.txt, stats.txt, hyps.txt, hard_bar_main.txt, hard_bar_cap.txt; scout5_stats.py.
