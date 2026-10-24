# v1-finish-8: PW-780, the brightening star (0.45) on 2 Gyr runs, the recipes, and never-ice (2026-10-24)

Branch `worktree-agent-aa268f8fa4f53889e`, from main f7621ad. A short, bounded check of v1-finish-7's default
(`star_brightening` 0.45 x Gough, `star_age` 0). Bar, thresholds and assertions unchanged.

## Numbers first

All runs go through `tools/ice_diag.py` on the code default unless stated. They are judged by `passrate2.py`: v1-finish-6's
bar (icehouse <= 40%, no always-icebox, no hellhole at median dT > 10.5 or max > 15.5), applied to 300 Myr to the run's end
and, separately, to the windows 300-1000, 1000-1500 and 1500-2000. "Strict" also fails never-ice (icehouse < 5%):
that is the owner's 2026-10-24 reading for Earth-like worlds. Per-run lines are in `passrate_*.txt`.

**1. 2 Gyr Earth-like runs: no hothouse.** The star's raw +10 C (1500-2000 mean) is met by a CO2 term of -4 to -6 C.

| L6, 2 Gyr | 300-2000 icehouse | 300-1000 | 1000-1500 | 1500-2000 | dT med 1500-2000 | max dT |
|---|---|---|---|---|---|---|
| Earth-like B (seed 12), offset 0 / -0.001 / +0.001 | 31 / 12 / 9% | 34 / 4 / 4 | 2 / 34 / 0 | **56** / 0 / 25 | +7.0 / +7.9 / +7.2 | 13.7 |
| showcase 583167 / 619496 / 639472 / 957317 | 28 / 11 / **64** / 16% | 29 / 9 / 69 / 5 | 14 / 18 / 63 / 46 | 41 / 7 / 59 / 3 | +5.5 / +8.2 / +4.3 / +6.0 | 12.9 |

- **L6 2 Gyr, whole run (300-2000):** 6/7 pass, and 6/7 strict too. None is never-ice; no icebox, no hellhole. The
  fail is 639472, which is icy throughout, as it was at 1 Gyr in base.
- **The 1500-2000 window on its own:** 4/7 pass, 2/7 strict. It doesn't drift one way: two draws are ice-free (0%, 3%)
  and three are over 40% (41-59%). The late Gyr spreads both ways.
- **Hellhole:** the hottest median dT in any window is +8.2; the max is 13.7, against the lines of 10.5 / 15.5.

| L7, 2 Gyr (2 draws, the budget) | 300-2000 | 300-1000 | 1000-1500 | 1500-2000 | dT med 1500-2000 | max dT |
|---|---|---|---|---|---|---|
| seed 12 (Earth-like B), offset 0 | **0.9% NEVER-ICE** | 2 | 0 | 0 | +9.1 | 13.7 |
| seed 619496, offset 0 | 12.9% ok | 18 | 19 | **0** | +7.4 | 10.8 |

**L7 is warmer than L6 at 2 Gyr.** At 1500-2000 its dT medians are +9.1 / +7.4, against +7.0..+8.2 for the L6 counterparts,
and both draws are ice-free there. It is not a hellhole: +9.1 is 24 C global, against the 25 C line. The owner gives L7
priority, so **at L7 the 0.45 star's late 2 Gyr drifts toward ice-free, not molten**. That is two draws, a lean only.
Seed 12 at 1500 Myr (the Earth-like B recipe's length) is already never-ice at L7.

**2. The water-world recipe (seed 13, 2 Gyr) is an always-icebox, star or no star.** The star doesn't cause it.

| water world, L6 2 Gyr | 300-2000 icehouse | deep | dT med | CO2 term 1500-2000 |
|---|---|---|---|---|
| star 0.45, offset 0 / +0.001 / -0.001 | 100 / 86 / 93% | 37 / 40 / 32% | -4.3 / -4.2 / -4.2 | -13.3 / -14.1 / -14.1 |
| star off, offset 0 / +0.001 | 93 / 100% | 62 / 59% | -10.1 / -9.9 | -11.4 / -10.9 |

- **Cause:** the raw CO2 source falls ~3x after the 300 Myr frozen reference (9700 / 8200 / 2900 at 100 / 300 / 1000
  Myr: the heat_start 2 mantle cooling). Meanwhile the land emerges (8% to 30%) and the sink grows with it.
- Draft: `draft-water-world-recipe-icebox.md` (needs-decision, lean: check the outgassing curve first).

**3. The cold and hothouse recipes (1 Gyr, L6).**

| recipe | star | 300-1000 icehouse | deep | dT med / max | reads as |
|---|---|---|---|---|---|
| cold (seed 15, tilt 15, offset -6) | off | 97% | 86% | -4.6 / +6.8 | cold world, big sheets |
| cold, offset -6 / -6.001 | 0.45 | 100 / 100% | 92 / 71% | -1.4 / -1.9; +4.7 / +4.1 | **still a cold world** (kept) |
| hothouse (seed 16, tilt 45, offset 5) | off | 0% | 0 | +9.6 / +13.9 | hothouse |
| hothouse, offset 5 / 5.001 | 0.45 | 0 / 0% | 0 | **+12.9 / +10.9; +17.7 / +15.3, HELL** | over the hellhole line |
| hothouse, **offset 3** / 3.001 | 0.45 | 0 / 0% | 0 | +8.1 / +9.4; +11.7 / +13.2 | hothouse again |
| hothouse, offset 2.5 | 0.45 | 0% | 0 | +7.5 / +12.2 | hothouse (milder) |

- **Recipe change:** the hothouse preset's `climate_offset` goes from 5 to **3**. That brings its dT back to the
  star-off +5's (+9.6 median), under the hellhole line. Changed in `planet/make.py` PRESETS, `README.md` and
  `docs/coordination.md`.
- The cold recipe is unchanged. It remains always-icy (the recipe is meant to be), 3 C less cold.

**4. Never-ice under the strict reading (owner, 2026-10-24).**

| set | lenient (v1 bar) | strict (never-ice fails) |
|---|---|---|
| L6 1 Gyr, v1-finish-7's 18 draws at 0.45 (its monkeypatched harness) | 16/18 (89%) | **13/18 (72%)** |
| L7 1 Gyr, v1-finish-7's 8 draws | 7/8 | 7/8 (no never-ice) |
| L6 2 Gyr Earth-like, 7 draws (above), whole run | 6/7 | 6/7 |
| L7 2 Gyr, 2 draws, whole run | 2/2 | **1/2** |

v1-finish-7's README named the wrong seeds as its never-ice draws. They were l6fix 583167 (1.1%), l6fix 957317
(2.8%) and l6c_p 53669 (offset +0.001, 4.5%), all three at 0.45. Re-run on the code path (`ice_diag` with the param,
not the monkeypatch), only 583167 stays never-ice. 53669 lands at 5.1% and 957317 at 11.4%, so two flip on the code
path's < 3% forcing difference.

**5. Does a lower `star_brightening` turn the never-ice draws into passes?** The three draws, L6 1 Gyr, code path:

| rate | 53669 (+0.001) | 583167 | 957317 | dT medians |
|---|---|---|---|---|
| 0.45 | 5.1% ok | **0.0% never** | 11.4% ok | +3.7 / +5.6 / +5.3 |
| 0.2 | 28.4% ok | 59.7% F | 43.8% F | +1.6 / +1.0 / +2.9 |
| 0.1 | 10.8% ok | 12.5% ok | 57.4% F | +2.6 / +3.2 / +2.8 |
| 0 (no star) | 45.5% F | 11.4% ok | 44.9% F | +1.9 / +3.0 / +1.7 |

- **On average, yes:** a slower star cools these warm draws by 2-4 C of dT, and the never-ice one (583167) gets ice
  at every lower rate.
- **Per draw, it isn't controllable:**
  - The icehouse share moves non-monotonically with the rate: 583167 gives 0 / 60 / 12 / 11%; 53669 gives
    5 / 28 / 11 / 46%.
  - Two of the three overshoot into fails (> 40%) at some lower rate.
  - Changing the rate re-rolls the ice history, much as the offset ±0.001 draws do. It doesn't nudge it.
- **Measured strict tally:** 0.45 gives 2/3, 0.2 gives 1/3, 0.1 gives 2/3, 0 gives 1/3. None of the lower rates beats
  0.45 on these three draws.
- **`star_age` can't help.** An older star brightens faster in relative terms (Gough): the 0.45 forcing at 1 Gyr is
  +5.6 / +6.4 / +7.9 C for star_age 0 / 2000 / 4570 Myr. A later start warms the run more.

So the star is a sound per-world knob for "this planet runs warm / cold" (a ~2-4 C shift in dT). It doesn't steer a
given seed into the 5-40% band from a single run. Draft: `draft-star-brightening-per-world-lever.md`.

## What changed

- `planet/make.py`: the hothouse preset's climate_offset goes from 5 to 3. `README.md` and `docs/coordination.md` match.
- PW-564: an Updates line corrects the sensitivity (0.81 C/(W/m2), not 0.6).
- `uv run pytest -q`: 671 passed. Goldens unchanged (no model change).
- `tools/earth_check.py`: Koppen group 71.1%, exact 33.9%, unchanged.
- `tools/scorecard.py`: seed 1 land 33.7%, ice 0.0%, NPP 352; seed 2 land 34.4%, ice 0.1%. Unchanged against v1-finish-7.
  The run appended a line to `docs/scorecard.jsonl`.
- No physics change. The 2 Gyr runs don't overshoot to a hellhole, so neither the thermostat nor the luminosity curve
  needed an option paper. The L7 late-ice-free lean is in the per-world-lever draft.

## Files

- `launch.sh`: the main sweep (2 Gyr water world, Earth-like B and showcase; cold and hothouse).
- `launch_hot.sh`: hothouse offsets. `launch_ww.sh`: water world with the star off. `launch_l7.sh`: the two L7 2 Gyr draws.
- `launch_never.sh`: the never-ice draws at each rate.
- `passrate2.py`: v1-finish-6's bar per window (harness only).
- `passrate_*.txt`: per-run lines.
- Raw outputs: session scratchpad `v1f8/`.
