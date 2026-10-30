# ice-loop: the run's ice and its own air within a climate update (PW-1050), 2026-10-30

Lane 28. Code: commit fdd9b595 (`climate.compute`'s `reground`, `nest.climate_coarse`'s wrapper,
`earth.ice_air_rounds`, `Params.ice_air_rounds = 4`, 0 = off; diag `air_rounds`).

## The question
Each climate update computes the climate on the ice it inherited from the last update, then lets the ice
settle under that climate. The ice sheets' own cold air (the carried air of PW-336: `icemass.air_mass`,
which cools the summers on and next to a sheet) is the last update's. So a growing sheet always sees the
air of a smaller sheet, and catches up one update at a time. If that is so, how icy a run gets depends on
how often the climate updates, which is a speed setting, not physics.

## Diagnosis (probes only, scripts in the lane's scratchpad: loop.py, loop2.py, frozen.py, follow.py)
Each probe repeats the climate update at a fixed moment: the same ground, the same global temperature
offset dT, so only the ice and its air move.
- **Most of the time the loop is already settled.** At 16 moments it converges within 1-2 updates. The
  "2-3 m of sea level per update" seen earlier is mostly flicker at the sheets' edges (+-0.5-1 m), so the
  per-Myr ice path rises with the cadence for a trivial reason.
- **At the start of an ice age it is not.** Seed 53669 at 700 Myr: repeated updates walk the ice's sea
  level -74, -71.5, -73.8, -77.0, -83.4, -93.2, -96.5 m and it is still growing after 6. With the carried
  air held fixed, it stays at -71 m. So the walk is the carried air, one step per update.
- **The cadence then matters.** With the slow drivers (land, CO2) frozen, cadences of 2, 4 and 8 Myr end
  within a few m of each other, but an onset takes about 3 times longer at 8 Myr. Under a 10 Myr cold dip,
  2 Myr ends on the iced branch (seed 957317: -84 m) and 8 Myr does not (-68 m).
- In the earlier judge (lane 27), every 2 Myr against the default cadence: over 300-990 Myr dT is -1.8 C
  lower, of which the ice's albedo is -0.45, the greenhouse share -0.24 and CO2 -0.93 (noisy). Nothing differs
  before 300 Myr.

## Candidates
1. Re-solve the whole climate on the new ice, to a fixed point. Sound, but costs +30-45% of a run.
2. **(Chosen.)** Re-solve only the carried air: the rest of the climate (sea, rain, clouds, the summer's
   energy split) is held, and the bare ground's temperatures are redone under the new ice's own air, then the
   ice settles again. Up to 4 rounds; it stops once fewer than 1% of the ice cells change, or the ice flips back
   and forth between two states. Estimated +10-15%.
3. Dropped: shift the ground by the climate's expected response between updates and re-settle. It overshoots
   (-58 m against the 2 Myr arm's -33 m on the same state).

On the probe states candidate 2 reaches in one update what the base loop reached in 6 or more:
53669 at 700 Myr: -101.8 m (rounds per update 4, 1, 0, 0, 0, 0); 957317: -42.5 to -44.3 m (2, 1, 1, 0, ...);
819014: -179.7 to -185.5 m (4, 2, 1, 1, 0, 0).

## Earth check
`climate.compute`'s fields are unchanged (the new code only adds the `reground` closure to its result), and
earth_check calls nothing else, so Earth's numbers are bit-identical to main's by construction. (The cache
rebuild is waiting on GPCC, see the inbox draft on the GPCC source id.)

## Judge
Paired judge, v1-finish-16's 18 L6 draws, roll 0.0005. Arms: main (3a58e00d), X (the fix, default cadence),
X2 (the fix, every 2 Myr: climate_every = climate_every_max = 2, the dT trigger off). Frozen code copies,
all three arms run at the same time under one cap, so the run times compare.

### First judge, stopped (10-30, 02:40)
After 4 of X's 18 draws (paired with main): X cost 2.09x main per run (median of 4, and part of that is the load,
which rose from ~110 to ~170 during X's runs). It used 2.76 rounds per update on average, 37% of updates hit the
cap of 4, and 0.1% needed none. A round re-settles the sheets from scratch (~21 passes) and the 1%-of-cells stop
rarely fires, because margins keep shuffling 10-40 cells after the sea level has stopped moving. X2 (every 2 Myr)
was slower still and was stopped with X (coordinator). Ice over 300-990 Myr, on the same 4 draws: the share of
steps below -150 m sea level is 0.21, 0.36, 0.22, 0.31 for X, against 0.03, 0.00, 0.20, 0.00 for main.

**Is the converged loop right?** On the 53669 state at 700 Myr, reground's warm month on the cells the ice
changed moves by -1.05 C; a full climate recomputed on the new ice moves it by -0.99 C. One more settling gives
-77.7 m on reground against -77.3 m on the full climate. So the rounds find what a full re-solve would.

## Option B: the carried air inside the sheets' own passes
`earth.ice_sheets(..., reground=)` re-makes the bare ground under the passes' current ice every AIR_EVERY (8)
passes while the ice moves, and whenever it settles. It stops once the ice settles within AIR_SEA_TOL (0.5 m) of
sea level of its last re-making, at most Params.ice_air_rounds (8) times. The diag records `air_rounds` and
`air_capped`. Without reground (every other caller), ice_sheets is unchanged, bit for bit.

## How strong is the carried air, now that it decides? (note for the owner; probes only: strength.py)
Four states (seeds 53669 at 300 and 700 Myr, 957317 and 819014 at 700 Myr), sheets of 558-3661 cells, mean ice
height 1030-1605 m, mean latitude 64-70 deg. "Carried air" is the bare ground's warm month with the sheet's own
air against without it (reground(ice) - reground(0)).

1. **Size.**
   - Carried air on the ice: -2.4, -4.2, -2.8, -6.3 C in the warm month (the air takes away 14-32% of the summer's
     warmth over the annual mean). On margin ice (< 800 m): -3.4 to -5.8 C. On the first bare ring outside the
     ice: -0.5 to -0.85 C; on rings 2-3: -0.13 to -0.22 C.
   - One more ring of ice at a margin's 408 m cools the next ring out by -0.34 to -0.58 C, and the new ring itself
     by -1.1 to -2.2 C.
   - On top of that, the ice surface's own summer drop below its (already chilled) ground: -11.6 to -14.6 C over
     all the ice, of which the lapse rate times the ice's height is -6.7 to -10.4 C. On margin ice it is -7.1 to
     -8.9 C, of which the lapse rate is -3.0 to -3.9. The rest (~-4 to -5 C) is the thick ice's inversion
     (ICE_COOL 2 C, all year), the surface's own bright-snow damping (LOCAL) and the melting surface's hold.
   - **Physical estimate.** The height part is the lapse rate, which the model has. For the rest, the model's
     own reference (icemass.py's docstring) puts Greenland's ablation zone at ~+3 to +5 C in July, where tundra
     at the same height beside it has ~+8 to +10 C: a ~5 C contrast, and that contrast already includes the
     sheet's own air at its margins. The model's margin ice is ~7.5 to 11 C below its bare ground's summer for
     reasons other than height (carried air plus the surface's own effects, less the ~0.5-0.85 C the next bare
     ring also gets). That is about 1.5-2 times the reference.
   - The absolute numbers point the same way. The outermost ring of ice cells has a warm month of -8 to -12 C,
     and only 2-8% of those cells are above 0 C. Real margins melt in summer.
2. **Plausibly too strong now: yes, at the margins.** The likely cause is that the summer cooling is counted
   twice, not that the air mass is too big. The sheet's carried air damps the air's summer (SUMMER_DAMP x
   air_mass), and the ice surface then adds its own inversion (all year) and bright-surface damping on top of
   that air. While the loop lagged, the margins never fully saw their own air, so the strength was in effect
   fitted with the lag hiding part of it (how much isn't measured).
   - The feedback's gain is near 1 on big sheets: on 819014 (a retreat), each re-making of the air moved the ice
     ~4 m with no sign of slowing over 6 re-makings, so the extent is poorly pinned there.
3. **Candidate knobs** (none tried):
   - (a) split SUMMER_DAMP into the air's and the surface's, or let the surface's own damping and inversion act
     only on the share of the air that isn't the sheet's (x (1 - air_mass)): this removes the double count on
     grounds of soundness, not fit;
   - (b) ICE_COOL applied in summer: an inversion is mostly a winter feature, and over a melting summer surface
     it is weak;
   - (c) SHEET_KM (1000 km, the air mass's footprint) and air_mass's polar ramp (none within 15 deg, in full from
     50 deg);
   - (d) dropped: letting only the frozen share of the ice make cold air (cold_share, as the time zoom does)
     changes nothing here, because the margins' frozen share is 0.98-1.0.
   - Any of these is a retune of PW-336 and goes to the owner.

## (a) The surface's own damping only on the air that isn't the sheet's (coordinator's ruling 10-30: a soundness fix)
**The physical argument.** The air touching an ice cell is a mixture. A share a of it (icemass.sheet_air, the
same share as air_mass, also just off the ice) is the sheet's own air mass: air that has crossed the sheet,
had its summer warmth damped by the bright ice (SUMMER_DAMP x a, in the climate's air), and drained off it. The
rest, 1 - a, has arrived from off the ice. The ice surface's own bright-snow damping (SUMMER_DAMP x LOCAL) is the
same process, the bright ice taking the summer's warmth out of the air over it. Applied to the sheet's own air,
it takes that summer off a second time. So the surface damps only the share 1 - a: sheet_cover(grid, ice, air) =
LOCAL x (1 - air). This applies in the run's ice passes and keyframes, in the diag, and in climate.compute's own
ice surface (so worlds and the time zoom's climates too), and in the zoom's inversion back to the ground
(zoom.ice_ground, so it undoes what the world did). The time zoom's own ice kernel (timezoom/sim.py) still damps
all its air with LOCAL (follow-up draft).
**The inversion is left as it is under (a).** The carried air holds only the summer damping (it relaxes the
summer toward the bare ground's annual mean). It holds none of the thick ice's all-year cooling (ICE_COOL), so
in winter there is no double count. Scaling ICE_COOL by 1 - a would also warm big sheets' winters, and their
plateaus are already ~10 C too warm (climate.ice_surface's note, PW-039). The inversion's summer half is (b).

## (b) The inversion is a winter feature
A surface inversion over an ice sheet comes from the surface's radiative cooling. It is strong in the polar
night and weak at midsummer, when the sun heats the surface and a melting margin is held at 0 C. The katabatic
outflow weakens in summer too. The model had ICE_COOL (2 C on thick ice) in every month. Under (b) it follows the
season with the same annual mean: ICE_COOL x (1 - cos(month's phase from the summer peak)), so none at midsummer
and 2 x ICE_COOL at midwinter (timezoom.kernels.climate_step, shared by the run, the worlds, the zoom and the time
zoom, so they stay one rule).

## (a) and (b) on the same four states (strength.py, rounds_probe.py; B = before either)
| measure | B | B+a | B+a+b |
|---|---|---|---|
| margin ice's summer drop not from height, net of the next bare ring's (C; reference ~5) | 7.4 to 9.2 | 6.3 to 7.8 | 5.0 to 6.6 |
| outermost ice ring's warm month (C) | -8.1 to -12.4 | -7.5 to -11.4 | -6.2 to -10.2 |
| ...share of it above 0 C | 1-9% | 2-10% | 6-15% |

The four states are 53669 at 300 and 700 Myr, 957317 and 819014 at 700 Myr. The fixed point's ice shrinks with
each fix (e.g. 819014: 3651 iced cells under B+a, 3450 under B+a+b).

**The loop's gain on 819014** (a retreat; each value is the ice's sea level in m after one more re-making of the
air, up to 6):
- B: -196.0, -193.2, -189.5, -185.6, -181.1, -177.7, -179.9. Still walking about 4 m per re-making.
- B+a: -199.3, -193.1, -180.0, -178.0, -177.1, -177.1, -177.1. Settled after 4.
- B+a+b: -181.2, -175.4, -172.9, -170.0, -171.7, -169.2, -169.9. Within about 1.5 m from the third.
So (a) alone pins the extent, and (b) brings the margins to about the reference.

## Judge (running, started 10-30 03:46)
Arms: main (3a58e00d, all 18 draws done), F = B+a+b and F2 = F at every 2 Myr (climate_every =
climate_every_max = 2, the dT trigger off), 18 L6 draws each, roll 0.0005. They run as paired.sh under one cap of
11 in the lane's scratchpad (`judge/`, launched by judgeF.sh -> judgeB.sh; frozen code in `code/{main,B,F,F2}`).
B's 4 l6fix draws (`judge/B_*`) are the cost check for B on its own.
Analysis:
- `judge_an.py JUDGE main B F F2`: run cost (paired ratio to main), re-makings per update (`air_rounds`,
  `air_capped`), ice paths over 300-990 Myr;
- `pjudge.py JUDGE main F` and `pjudge.py JUDGE F F2`: passes, end T, measures.
Success: F and F2 agree (the same iceboxes at both cadences, close ice paths). Report passes and end T against
main; passes under ~70% go to the coordinator for the owner, with no tuning.
Still owed before merging: earth_check L6 on the final branch once GPCC is back, with the ice-sheet temperature
lines against main (coordinator); the full time zoom tests after (b).

## Handoff (lane 28, 10-30 ~03:50)
Branch worktree-agent-a2381af405c341835:
- fdd9b595: rounds, superseded;
- dc87e5ee: B;
- ca897435: (a);
- (b) is uncommitted in the working tree (kernels.py plus the docs in icemass.py, climate.py and
  timezoom/params.py, and its test in tests/test_ice_air.py). Its test chain runs via lane28/tests.sh b, into
  t_b_*.txt; commit it once that passes, with the goldens it updated.
- tools/earth_data.py's GPCC fallback is uncommitted. It goes in its own commit with
  issue-tracking/inbox/draft-earth-cache-gpcc-source-id-removed.md once the period is confirmed. GPCC_YEARS is
  still a placeholder, and gpcc_wait.sh retries every 40 min.
- Local branch lane28-coasts (a2c6015a) is the coasts work (PW-998) merged onto main plus the first fix. It needs
  re-merging onto the final PW-1050 branch before its judge, and is held for GPCC.
- The main checkout's data/earth is still empty. lane28/rebuild has the raw ETOPO, Kottek and GFED files, and
  rebuild.sh reruns the build once GPCC is back.

### B's cost check (4 l6fix draws, finished 10-30 ~04:00)
- B's run time against main's on the same draws: 1.14x (median; mean 1.15). The load was ~80-170 during B's runs
  and ~110 during main's.
- Re-makings of the air per update: mean 2.01, max 8. The cap of 8 was hit on 4.1% of updates, and 12% needed
  none. Passes per update: 13.4 against main's 12.6.
- Ice over 300-990 Myr: share of steps below -150 m, median 0.09 (mean 0.16), against main's 18 draws at median
  0.00 (mean 0.09).

### Handoff update (~04:05)
- (b) is committed: b74bd0e2. The judge's frozen F code is identical to it (diff -rq).
- The not-slow suite passes on (a) (737) and on (b) (739). (a)'s area tests passed (32, including the time zoom
  consistency tests).
- (b)'s area tests and the full time zoom tests are still running: lane28/t_b_area.txt.

## PW-1095: the inversion's swing only where the summer melts (lane 57, 10-30)
**Diagnosis.** (b) gave every thick-ice cell the full swing: ICE_COOL x (1 - cos phase), +2 C at midsummer. Its
physical case is a melting surface. A surface held at 0 C can't chill the air above it. A plateau that never melts
has no such limit, so it got a summer that was too warm and a range that was too wide.

**Rule (C1, chosen).** inv = 1 - s cos(phase). Here s is the share of the warmest month's days on which the air
reaching the surface (t_mean + dt_base + half + the peak month's orbital anomaly: before the surface's own damping,
hold and inversion) is above 0 C. The days are scattered by PDD_SIGMA, as in the degree-day melt and
icemass.cold_share. The annual mean is ICE_COOL everywhere. No new constant, and it isn't circular. Dropped: C2,
the same s from the surface's own warm month (a first pass of the year). It runs the kernel twice and lands within
~0.1-0.2 C and ~1 m of C1. The zoom's inverse (icemass.ground_from_surface) now alternates its two bisections,
because the coldest month depends weakly on the warmest through s.

**earth_check** (main 347b4374 / C1; obs NCEP). L6:
- Antarctica warm month -12.3 / -14.0 (-16.1); cold month -50.9 / -49.2 (-48.7).
- Vostok warm month -20.8 / -22.8 (-22.7).
- Land seasonal range at 60-70 / 70-80 / 80-90 S: 36/38/40 / 33/35/36 (23/32/34).
- Greenland warm month -9.8 / -11.4 (-5.0); cold month -48.5 / -46.9 (-33.0).
- Summit warm month -16.3 / -18.3 (-8.1).
- Annual means unchanged.

L7 is the same to within ~0.4 C. Greenland keeps ~0.9 of (b)'s 2.5 C summer gain. Its interior never melts and is
too cold in every season (Summit -10 in summer, -14 in winter), an error in the air, not the inversion (inbox
draft: Greenland's all-season cold bias; coordinator ruling 10-30: no Greenland discriminator).

**Probes** (the 4 states rebuilt from main at roll 0.0005, 4 repeated updates; last update, main / C1):

| state | ice sea level, m | interior (>=1500 m) Tw | interior range | outer ice ring Tw | ring share Tw > 0 |
|---|---|---|---|---|---|
| 53669@300 | -45.9 / -47.4 | -13.4 / -15.0 | 36.9 / 33.1 | -6.4 / -7.7 | 0.22 / 0.19 |
| 53669@700 | -94.0 / -97.3 | -11.3 / -12.7 | 36.6 / 33.1 | -1.6 / -2.0 | 0.47 / 0.46 |
| 957317@700 | -90.4 / -94.0 | -13.0 / -15.2 | 37.6 / 33.7 | -3.1 / -4.1 | 0.32 / 0.25 |
| 819014@700 | -136.2 / -137.7 | -11.6 / -13.3 | 36.6 / 33.0 | -1.9 / -2.6 | 0.44 / 0.40 |

Update cost is the same as main's.

**Judge** (18 L6 draws, roll 0.0005, main 347b4374 vs C1; pjudge.py, lane 57's scratchpad `l57/judge`):
- Passes: main 13/18, C1 14/18 (both 9, main only 4, C1 only 5; McNemar p 1.0).
- Iceboxes: main 8, C1 7. Hellhouses: none.
- End T median: main -0.2, C1 +1.3 C (paired +0.7, CI -4.4..+4.7). Late dT: paired +0.3 (CI -2.2..+2.6).
- Arid share: 21.9 vs 22.3% (paired +0.9, CI -1.5..+2.0).
- Deep-ice share (steps over 300-990 Myr with ice sea level < -150 m): median 0.19 vs 0.12, mean 0.19 vs 0.17.
- Mean ice sea level: paired median -2.0 m (C1 slightly icier, as in the probes).
- Run cost: 0.86x main (load noise).
- Only the source reference "moved" (-0.06, 3/15). That is a small carbon-cycle drift that C1's mechanism doesn't
  predict, so it is read as one of the expected false moves.
- The rest sits within its intervals.
