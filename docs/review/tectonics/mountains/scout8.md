# Scout 240 (PW-1497 pass 3 of 3, last strike): contraction at the long-term rate fails; parked under option B

Scout 240, 2026-11-09 (overnight). Base: main 23ad8b97 merged with scout 237's branch (2856d4d9). Follows
`scout7.md` (pass 2: the mechanism, share 0.4) and `scout6.md` (pass 1: sources, five stand-ins).

## In plain words

- **The idea failed its third and last try.** Scout 237 built a way for a continent's edge to really squeeze up
  where ocean floor dives under it (the Andes' way). At the Andes' present rate it put mountains in the right
  place but made 4-8 times too much high ground. This pass tried the slow, long-term rate (a quarter and an eighth
  of that) on the same three test planets.
- **At the slow rates the mountains no longer go to the right place, and there is still too much high ground.**
  The share of high ground near ocean-continent coasts did not rise (share 0.1: 15.9% on average, main 16.0%;
  share 0.05: 10.8%, below main), while land above 3 km still rose to 1.6-2.3 times main's (mean 5.3% and 3.7%,
  main 2.3%). The one-planet lead from the coarse grid (L5) did not hold on the finer one (L6).
- **So no rate works:** fast enough to make Andes, it makes far too much high ground; slow enough to keep high
  ground near main, it makes no Andes, and still adds high ground inland.
- **Outcome:** PW-1497 is closed under PW-1509 option B: the planets' high ground is mostly collision plateau, a
  known difference from Earth (written into `docs/overview.md` section 7). The mechanism is **removed** from the
  code (it was off by default and nothing used it; it added a per-plate field to every saved state and two
  parameters). Its code is kept as `scout7_andean.patch` (applies to main 23ad8b97) for anyone who tries again.

## 1. Screens

Setup as scout 237: L6, seeds 1, 2, 6001, 600 Myr, `--set andean_shortening=SHARE`, two arms at once with 4
numba threads each, scratch runs (gone with the scratchpad), measured with `scout7_measure.py` (median of ~29
frames with t >= 100 Myr). **Baseline: main on the same seeds and window**, scout 209's numbers (main e6cb463c):
no commit touches `planet/tectonics`, `climate.py`, `surface.py`, `kernels.py`, `grid.py` or `simulation` between
scout 237's base a1db4525 and this one, so main's run here is the same run.

Pass bar, written before any run (scout1 section 6 and scout 237's draft):
- Andes share (high ground >3 km near an ocean-continent margin) mean >= 20% (main 16.0%, Earth ~25%);
- land >3 km no seed above 3.5% and the mean at most 3.0% (main 1.4-2.7%, mean 2.27%);
- land % within 2 points of main on each seed; continental crust median >= 38% (main ~40%);
- then the hard-failure judge and `tools/scorecard.py`.

| arm (seeds 1, 2, 6001) | Andes share of >3 km land | land >2 km | >3 km | >4 km | land % | continental % (median / end) |
|---|---|---|---|---|---|---|
| main (scout7.md) | 11.4, 18.4, 18.2 (mean 16.0) | 6.9, 7.9, 5.7 | 2.7, 2.7, 1.4 (2.27) | 0.75, 0.88, 0.27 | 34.0, 33.3, 34.0 | ~40 |
| share 0.4 (scout 237) | 24.9, 21.7, 23.4 (23.3) | 22.1, 23.5, 20.3 | 12.3, 11.4, 10.6 (11.4) | 5.2, 5.5, 4.7 | 30.5, 30.7, 31.3 | 35.7-36.1 / 37.2-38.1 |
| **share 0.1** | 16.0, 17.0, 14.6 (**15.9**) | 16.4, 8.3, 12.4 | 7.00, 3.83, 4.96 (**5.26**) | 2.90, 1.64, 1.95 | 32.2, 33.0, 31.9 | 38.1-38.4 / 38.8-40.2 |
| **share 0.05** | 8.8, 12.2, 11.4 (**10.8**) | 11.3, 8.9, 9.6 | 3.57, 4.07, 3.49 (**3.71**) | 0.53, 1.43, 0.98 | 32.6, 33.3, 32.8 | 38.3-38.5 / 39.3-41.5 |

Runs (scratch, deleted): share 0.1 `955b60`, `df97e5`, `f8ead7`; share 0.05 `4c0fa4`, `c0fe08`, `def403`.
Top cell 5.4-6.6 km (the PW-1446 cap holds). Continental area held (38% median, as scout 237's 0.4 arm or better).

Both arms fail the first two bars on every seed except share 0.05's land >3 km on seed 6001 (3.49%, on the line).
Judge and scorecard not run: no candidate reached them.

## 2. Why: the belts sit inland and outlive their trench at every rate

- At share 0.4 the margin share rose because contraction was fast enough that a belt was always being built at a
  live trench. At 0.1 and 0.05 a plate's pool closes a cell only every few to tens of Myr, so the belts are
  built rarely, and the crust they hold (the closed cell's whole 35 km column, spread ~290 km behind the forearc
  gap) stays thick long after the trench that made it has moved, died or become a collision. That is what
  `scout7.md` saw (~75% of high ground away from live margins); at the low rates there is simply no new belt at
  the margin to outweigh the old ones inland.
- Each closed cell concentrates ~35 km of crust on to a belt already near 40-50 km, and the model holds thick
  crust up by Airy isostasy, so even a slow trickle builds high ground that only erosion and lower-crust flow
  take down.

## 3. Should old belts wear down or collapse once their trench stops? (step 2, sourced)

Read this pass (fetched):
- Baldwin, Whipple & Tucker 2003, JGR 108(B3), doi:10.1029/2001JB000550 (abstract, umimpact.umt.edu): plain
  stream-power erosion takes a dead orogen's relief down in "1-10 Myr"; Airy rebound of the thick root makes this
  up to ~6x longer, transport-limited channels 2-3x, an erosion threshold ~20x (their example); together they can
  keep residual relief for hundreds of Myr.
- Dewey 1988, Tectonics 7(6), "Extensional collapse of orogens" (read only via the EGU Tectonics division's
  "TS must-read" summary, 2021-06-25, not the paper): collapse is driven by isostatically compensated uplift plus
  slab rollback, triggered by the loss of the lithospheric root, and is the orogen's last stage; the summary
  says erosion alone is too slow to remove an orogen's excess crust. No rates or timing relative to the end of
  convergence given there.

What the model already has: erosion that wears ground faster the higher it is (`erosion_height`: (1 + (h/2 km)^2)
times faster) with Airy isostasy under it, which is Baldwin et al.'s decay; and `crust.flow_and_orogeny`'s
lower-crustal flow, faster the thicker the crust, which is the spreading half of Dewey's collapse. What it lacks
is collapse triggered by root removal or rollback. Adding a decay only for belts whose trench has stopped would be
a targeted fix: collision plateaus would keep the slower decay, and in any case it could only lower the inland
excess; it could not raise the margin share, which at the low rates is not rising in the first place. It was
therefore not built (the scout7.md ruling against a faster-decaying belt stands).

## 4. Outcome

- PW-1497 closed (wontdo, three strikes) under PW-1509 option B: high ground mostly collisional, a known Earth
  difference, now in `docs/overview.md` section 7 (Glossary, "Andean (cordilleran) margin").
- Mechanism removed from `planet/` (back to main's code exactly; goldens unchanged by construction). Kept as
  `docs/review/tectonics/mountains/scout7_andean.patch`.
- What a future attempt would need, if margin ranges ever matter to the peoples or food work: shortening that
  comes in bursts tied to what drives it on Earth (a flat or advancing slab, a wide subduction zone; Schellart
  2008), so belts are built where and while a trench is shortening, not a uniform share of every advance; and a
  root-loss collapse that applies to collision plateaus as well, so the two kinds of high ground decay alike.
