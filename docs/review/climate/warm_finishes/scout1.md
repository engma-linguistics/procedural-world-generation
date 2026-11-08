# Scout 203 (PW-1161 pass 1): do worlds still finish too warm?

**In plain words.** PW-1161 was filed on 10-30, when 5 of lane 67's 18 worlds finished 3.5 to 5.3 C above
pre-industrial, against an allowed band of -6..+3 C. Two things have changed since then. Daniel moved the warm edge to
+5 C (D19, PW-1164). The carbon cycle also got its yardstick, grass-roots and height-cap fixes (D47/PW-1424,
PW-1261, PW-1458, PW-1446). On today's code, 2 of 36 worlds fail on the warm side and 2 fail on the cold side. The
judge passes 32 of 36. None of the warm finishes comes back when the same world is re-run with a tiny code change.
So the warm tail is now inside the bar, and what is left of it is chaos. **Recommendation: close PW-1161.** Its two
real systematic causes already have their own tickets (PW-1158 with PW-1163).

No new sims. Data: scout 194's 72 L6 1 Gyr runs (rolls 0.00025 and 0.00075, 18 seed/tag draws each). I copied them
from `scratchpad/l194/judge/`, read only. The arm `cap` is today's main (fe5b6c76, PW-1446 merged). The arm `main` is
the same code without the height cap. The baseline for every temperature is pre-industrial (13.8 C true mean); for
the CO2 index it is the balance (500 ppm, e-folds). Scripts: `scout1_an.py` (per-draw split, using `tools/judge.py`'s
`judge_draw`, so it gets the same verdicts as the judge), `scout1_tally.py`, `scout1_ts.py`. Outputs are in `scout1/`.

## Against the two-tier bar

| | cap (today's main) | main (no cap) | bar |
|---|---|---|---|
| hard failures (ends frozen, boiled, ocean loss, CO2 crash) | 0/36 | 0/36 | 0 (`hard_bar_cap.txt`, scout 194) |
| soft pass (bar + finish moment) | 32/36 (89%) | 32/36 | ~60-70% |
| warm-side fails | 2/36 | 3/36 | |
| cold-side fails | 2/36 | 1/36 | |
| end T median / mean | +0.11 / +0.19 C | +1.17 / +1.18 C | Earth 0 (anchor) |
| end T p10..p90 | -4.27..+3.40 | -2.67..+5.28 | -6..+5 (D19) |
| end T > +5 / > +3.5 / > +3 | 2 / 3 / 5 | 5 / 9 / 11 | |
| last 10 Myr all above +5 (no moment can be picked) | 1 | 2 | |
| end pCO2 median | 376 ppm | 593 ppm | 180-600 (diagnostic) |
| end land ice median | 8.6% | 7.1% | Earth ~10% |

Compare the ticket's evidence (lane 67, older code, 18 draws): 5/18 over +3.5 (28%). On the cap arm it is 3/36 (8%).
Under the current +5 edge, the cap arm fails 2/36 (6%) on the warm side, and its tails are symmetric (2 warm, 2 cold).
The cap arm's median end is +0.1 C, on Earth's pre-industrial. So there is no warm bias left to fix.

The warm-side fails (cap):
- **583167 l6fix r0.00075**: end +6.7 C, and the whole last 10 Myr sits at +5.8..+6.8, so the finish moment has
  nothing to pick. CO2 index +0.71 (1022 ppm). Land ice 1.4%.
- **53669 l6c_p r0.00075**: end +2.6 C, but it fails the land-ice check, not the temperature check. Land ice is
  0.0-0.6% over the whole window, under the 1% floor (an ice-free warm world). Its window peaks at +4.7.

The finish moment rescues worlds that end above +5: 1 on cap (733847 l6c_0 r0.00075, +6.1 at the end, picked 6 Myr
earlier) and 3 on main. The last 10 Myr span a median 1.4 C on cap (p90 3.1), so this pick moves only the borderline
draws, as lane 80 found (~1 C).

## Why the remaining warm finishes are chaos, not a mechanism

1. **They don't repeat in their twin.** The two arms are the same seed, tag and roll; they differ only by the height
   cap, a small change in relief. The correlation of end T between twins is **-0.07**, and the sd of the twin
   difference is 4.61 C (`tally.txt`). Of the 5 warm-side fails over both arms, none fails warm in its twin. 53669
   l6c_m r0.00025 is +4.9 (fails, no ice) without the cap and -6.3 with it. 583167 l6fix r0.00075 is -2.9 without
   the cap and +6.7 with it. The only draw warm in both arms, 733847 l6c_0 r0.00075 (+6.6 / +6.1), passes in both.
   This matches PW-1424's lane 160 result: two histories from one identical state already differ by 1.4 C sd.
2. **The split is lane 80's, just smaller.** Regressed over the cap arm, end T fits F = ln source - ln erosion supply
   (last 10 Myr, supply against 250-300 Myr) at 6.99 C per e-fold, R2 0.29. Adding the albedo term gives R2 0.79.
   On main it is R2 0.48 and 0.82 (lane 80 on older code: 0.52 / 0.93). The CO2 term and the albedo term carry the
   finish (corr with end T +0.78 and +0.85 on cap). CH4/N2O goes with the albedo term (ghg corr +0.99). Land fraction
   at the end barely matters (corr -0.28; range 32-36%). Luminosity is not a factor: `star` is 0 at the end of every
   run and `star_ctl` is 0.
3. **Per world, the warm finishes are a short source high with ice-free amplification on top** (`ts_warm.txt`):
   - 583167 l6fix r0.00075 cap: the source rises from ln +0.02 to +0.36 over 976-996 Myr, and the CO2 index goes
     +0.29 to +1.04. With land ice down to 1.4-2%, the albedo term is +1.0..+1.1 and CH4/N2O +0.8. This seed's
     drift walk ends at +1.26 C (the source-side random walk standing in for what the model lacks, PW-819, sd 0.8
     C, 40 Myr memory). By drift_source's 0.116 ln-source per C, that is ln +0.15 of the +0.26 source excess. The
     rest is tectonic.
   - 733847 l6c_0 r0.00075: a rebound. 32-37% of land was iced at 860-900 Myr, then the CO2 index went -0.74 to
     +1.14 by 960. A second source rise over 984-996 Myr (ln -0.26 to +0.20) takes the end to +6.1.
   - 53669 l6c_p r0.00075: land ice at or under 2.1% since 840 Myr (0.0-0.6% in the window), albedo term +1.2..+1.3. The CO2 index is falling at
     the end (+0.47 to -0.66 over 980-1000), so the world is cooling (dT lags its target by ~2.3 C at 1000 Myr). It
     fails on its missing ice, not on heat.
   The seed's drift raises the odds a little (corr of drift with end T +0.38 on cap, +0.20 on main) but doesn't
   decide it. Seed 583167, drift +1.26, ends at -2.9..+6.7 over its 8 draws.

So which of the ticket's candidates is it? The cause is the CO2 path (source/supply red variance, PW-1158/PW-1163's
territory), amplified by the ice-albedo and CH4 terms when a warm stretch melts the last land ice. It is not the
weathering law, the luminosity or the land fraction. Its size is now within the bar's spread.

## The ticket's open checkboxes
- *"A written split of each warm finish's end T into CO2 term, albedo term and drift"*: `scout1/an.txt`, every draw
  of both arms (dT, co2_term, albedo_term, ghg, drift, star at the run's end; F, source, supply, rate, area).
- *"A cause (or 'chaos, accept') sent to the coordinator"*: **chaos, accept.** The cause is red source/supply
  variance with ice-albedo and CH4 amplification; it does not reproduce in twins, and it fails 2/36 against a bar
  that passes 32/36.

## Recommendation
Close PW-1161. Keep it shut unless a future judge shows warm-side fails above ~10% or a warm median (> +1.5 C on
36 draws). No fix candidates are put forward, because nothing here is outside the bar. If someone wants a smaller
spread later, the levers in order are:
1. **PW-1158 + PW-1163 together** (the late source decline, about -1.6 C, and the sink reference learnt on bare
   ground, about +1.6 C, per lane 80). This moves the median, not the tail. Fixing one alone would shift the median
   by ~1.5 C and could bring the warm tail back.
2. **PW-1156's CO2 response time.** The CO2 index moves 0.4-0.8 e-folds within 4 Myr of the finish window (e.g.
   733847: +0.22 to +1.27 over 984-996). A slower carbon response would narrow the last-10-Myr spread and both
   tails. That is PW-1156's question, not a warm-finish fix.
Neither belongs in v1, and neither is warranted by this tail.

Not done: L7. The 72 runs are L6 only; the L7 yardstick (PW-1458) is not re-checked here.
