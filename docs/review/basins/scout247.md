# PW-054 scout 247, pass 1: where the closed basins go (diagnosis gate)

Branch `worktree-agent-adf822c3ee812eda1` on main 19a9a4f5. Scripts: `docs/review/basins/scout247/`
(read-only measures of stored runs and of Earth's terrain; nothing written to runs/ or worlds/).
"Inland" is health's `inland_pct` throughout: % of ice-free land whose water ends on land in a closed lake,
salt pan or real pit (`tools/health.py`), frames after 50 Myr.

## In plain words
Generated worlds drain about 5-8% of their land inland. Earth drains about 20%. But the model's own river and
lake code, run on Earth's real terrain and the model's own climate for Earth, gets only 11% at L6 and 17% at
L7. So at L6 the generated worlds are about two thirds of what the same code makes of Earth; at L7 (the
showcase level) they are about a third. Earth at L7 is roughly right without help; the generated terrain is what's
short. Its hollows are fewer and shallower than Earth's, and its deserts sit in hollows less often.
The "model gets 21% on Earth" quoted on the ticket was the HydroSHEDS closed basins forced onto the Earth
world (`earth_closed`), not the model.

## 1. Baseline, current main
| what | inland, median of frames (p10-p90) | dry % of land | source |
|---|---|---|---|
| L6 seed 1, 400 Myr | 5.1 (2.7-13.2) | 22.2 | scratch run, main 19a9a4f5 |
| L6 seed 2 | 7.2 (4.3-16.1) | 31.6 | " |
| L6 seed 3199 | 8.2 (4.3-17.9) | 31.5 | " |
| L6 seed 77 | 8.2 (4.7-14.8) | 30.9 | " |
| L6 stored, ea33de / f3e034 (1 Gyr) | 5.6 / 6.2 | 22.3 / 24.5 | runs/ (read-only) |
| L7 stored, December A / B / C (0b3439, 819bdc, a5ae13) | 4.2 / 4.3 / 6.2 | 22-27 | " |
| L7 stored, a19366 (v010-earthlike-a) | 5.6 (2.8-13.2) | 27.5 | " |

The share swings a lot within a run (p10 ~2.5%, p90 ~13-18%): closed basins come and go in tens of Myr.

## 2. The same hydrology on Earth (`earth_open.py`, `earth_variants.py`)
`tools/earth_world.build` (ETOPO terrain, the model's climate), with and without the HydroSHEDS data the Earth
world imposes. "Real closed" = cells where HydroSHEDS drains at least half the cell inland (`earth_closed`).

| Earth | L6 | L7 |
|---|---|---|
| HydroSHEDS real closed, % of ice-free land | 20.5 | 21.3 |
| model, HydroSHEDS closed basins + outlets imposed (the stored Earth world) | 20.5 (raw ends) | - |
| model, terrain + climate only (as a generated world is made) | **10.7** | **16.9** |
| ... share of the real closed area it finds | 42% | 53% |
| ... inland land outside the real closed area (false positives) | 2.1 | 5.5 |
| real closed area lost: not in any hollow of the cell-mean terrain | 5.7 | 3.1 |
| ... in a hollow MIN_DEPTH / MIN_SLOPE fill | 1.1 | 1.3 |
| ... in a kept hollow whose lake spills | 5.1 | 5.5 |
| no outlet cutting (channel 0) | 11.2 | 16.8 |
| lake evaporation x1.3 / runoff x0.7 | 11.3 / 11.4 | 17.5 / 17.6 |

So: the model's hydrology is in Earth's range at L7 (16.9 vs 21.3) and resolution-limited at L6 (~28% of the
real closed area has no hollow at ~110 km cell means). It is insensitive to climate scaling (+-30% on runoff
or lake evaporation moves it < 1 point) and to the outlet cutting. The L6 health envelope's 8% floor and its
note "L6 known ~9.5-11%" fit this; an 18% target at L6 does not.

## 3. Generated terrain against Earth's (`hollows.py`)
A = % of ice-free land whose drainage passes through any hollow of the terrain (priority-flood fill > 1 m);
B = through a hollow the lakes keep (`hydrology._bed`); C = inland. Medians of frames every ~100 Myr.

| | A | B | C | C / B | kept hollow depth, median / area-weighted m | arid land in B's catchments, % of arid land |
|---|---|---|---|---|---|---|
| Earth L6 (ETOPO) | 53 | 44 | 10.7 | 0.24 | 74 / 202 | 47 |
| generated L6 (f3e034, 1 Gyr) | 52 | 36 | 7.4 | 0.21 | 48 / 174 | 30 |
| Earth L7 | 66 | 56 | 16.9 | 0.30 | 66 / 225 | 63 |
| generated L7 (a19366, 1 Gyr) | 58 | 44 | 8.0 | 0.18 | 40 / 188 | 40 |

The generated terrain has ~80% of Earth's kept-hollow catchment, its hollows are ~35% shallower at the
median, and its arid land lies in a hollow's catchment about two thirds as often. At L7 the conversion of
hollows into closed drainage is also lower (0.18 vs 0.30): shallow hollows hold small lakes that spill. In
the generated runs almost all closed drainage is arid: 52-82% of the inland land is desert, and of the hollow
catchments only ~5% of the wet ones stay closed against ~50% of the arid ones.

Where the generated sinks sit (`basin_kinds.py`, % of ice-free land, mean of frames):

| run | arid plain (30-45 km crust, no belt or rift near) | moat / intermontane (>45 km crust within 2 cells) | pit (thin or ocean crust) | rift | wet plain |
|---|---|---|---|---|---|
| L6 s1 / s2 / s3199 / s77 | 3.4 / 4.7 / 5.5 / 5.1 | 1.0 / 1.8 / 1.8 / 1.8 | 1.4 / 1.0 / 0.8 / 1.5 | 0.5 / 0.2 / 0.4 / 0.4 | 1.2 / 0.6 / 0.8 / 1.3 |
| L7 a19366 | 5.2 | 0.6 | 1.4 | 0.6 | 0.5 |

Most closed drainage ends in desert hollows on ordinary continental plains; the belt moats, rifts and
continental pits (PW-171) together give 2-3.5 points.

## 4. Candidates
1. **Two-sided flexure with a forebulge (PW-284 lean B).** Sound, and the forebulge is a rim. Still blocked by
   the crust field: a static swap on stored frames (`flex_static.py`: deflection = root - smooth(root),
   volume kept) lifts belts to 15-44 km and puts 5-100 cells above 9.5 km at FLEX_KM 150 (3-51 at 75 km),
   on both L6 f3e034 and L7 a19366. Needs PW-284's crust smoothing first; not screened.
2. **Hollows no river leaves stay closed however shallow (aridity-limited integration).** `_bed`'s MIN_DEPTH
   (20 m) and MIN_SLOPE (0.1 m/km) stand for channels too small to see that a through-flowing river cuts
   through a shallow rim, or a plain it crosses. A hollow whose own inflow evaporates before its lake reaches
   the rim has no outflowing river to cut that channel: it stays a playa or a terminal lake (Sobel, Hilley &
   Strecker 2003, JGR 108, doi:10.1029/2002JB001883: the large internally drained basins of the Altiplano-Puna,
   Tibet and Tarim persist where aridity keeps rivers from cutting through their rims ([citation record](https://earthref.org/ERR/76048))).
   Pure hydrology, no tuned number. **Screened below.**
3. **Rift-flank rims (PW-135)**: rift flanks raised by flexural unloading would wall rift floors in and damp
   PW-056's one-step outlet switches. Rifts carry only ~0.2-0.6 points of today's closed drainage, so a small
   lever here; worth doing for PW-135/PW-056's own sake.
4. **Intracratonic sag (Chad, Eyre, Congo; PW-242's dynamic topography)**: would make broad shallow hollows
   on the arid plains where most generated closed drainage already ends. Needs a mantle-flow proxy; speculative.

Not candidates: wind deflation (tested on the ticket, no effect), lake evaporation / runoff scaling (Earth
test: < 1 point), the moat's 0.15 share (a calibrated knob, PW-284).

## 5. Screen: candidate 2
`hydrology.DRY_HOLLOWS` (`_dry_hollows`, `_settle`): before `_bed`, run the lake balance once on the
unfiltered ground; each hollow whose lake stays closed gets its lowest cell deepened past the depth test, so
`_bed` keeps it as one basin (dips in its floor still join it as one lake), and that cell gets its own height
back. Everything else as before.

**Earth (terrain + model climate, nothing imposed):**

| | L6 main | L6 candidate | L7 main | L7 candidate |
|---|---|---|---|---|
| inland % | 10.7 | 14.8 | 16.9 | 22.4 |
| share of the real closed area found | 42% | 49% | 53% | 61% |
| inland outside the real closed area | 2.1 | 4.8 | 5.5 | 9.5 |
| ... its mean rain, mm (obs Koppen B share) | 589 (17%) | 441 (36%) | 480 (30%) | 705 (38%) |

At L6 the gain is mostly real closed area found plus semi-arid false positives (36% desert, 441 mm). At L7 it
overshoots the real 21% a little, and the extra false positives are wetter (705 mm mean rain).

**L6 screen, seeds 1 / 2 / 3199 / 77, 400 Myr, frames after 50 Myr, same seeds as the main baseline.**
v2 = the rule as above; v3 = v2 kept only for hollows in drylands (rain < 0.65 x open-water evaporation over
the hollow, the aridity index's drylands bound
([earthmap.org](https://help.earthmap.org/datasets/climate/aridity-index), [JRC World Atlas of Desertification](https://wad.jrc.ec.europa.eu/patternsaridity))).

| | main | v2 | v3 |
|---|---|---|---|
| inland median, per seed | 5.1 / 7.2 / 8.2 / 8.2 | 12.6 / 12.1 / 12.8 / 13.0 | 12.5 / 14.7 / 23.7 / 14.3 |
| inland, mean of seeds | 7.2 | 12.6 | 16.3 |
| inland p10-p90, seed 3199 | 4.3-17.9 | 9.3-34.0 | 17.7-32.3 |
| lakes, % of land (mean) | 0.72 | 0.98 | 0.92 |
| largest lake, median Mkm2 (mean of seeds) | 0.20 | 0.33 | 0.28 |
| giant-lake frames (> 1 Mkm2), % per seed | 4.7 / 2.3 / 14.0 / 4.7 | 0 / 34.9 / 7.0 / 4.7 | 23.3 / 0 / 14.0 / 4.7 |
| land %, crust volume end/start, peaks > 9.5 km | 32.6-33.5, 0.97-0.99, 0 | 32.2-33.3, 0.98-0.995, 0 | 33.1-34.2, 0.985-0.989, 0 |

The giant lakes the rule adds are the PW-300 / PW-430 kind: closed, shallow (median 4-40 m), on flat
hollows under 800-2000 mm of rain (seed 2 v2, seed 1 v3). A broad flat hollow in wet country is "dry" by the
lake balance because a lake spread over all of it evaporates more than its catchment brings, and the
open-water evaporation (~1.8-2 m/yr in the warm humid frames, PW-300's audit) is too high to serve as PET
for the dryland test, so v3 barely filters anything (Earth L6/L7 numbers identical to v2). Seed 3199 under v3
(23.7%, p90 32%) overshoots what the hydrology makes of Earth at L6 (14.8% with the rule). The ice-age
judge flipped both ways between arms (seed 1 icehouse 81% main / 0% v2 / 69% v3; seed 2 0 / 100 / 0): chaotic
divergence, not attributed. Scorecard: not run to completion (stopped when v2 was superseded; nothing lands).

## 6. Recommendation
**Another pass, on candidate 2, not a merge.** The rule is sound in deserts and roughly doubles L6's closed
drainage (7.2 -> 12.6-16.3%, against 10.7-14.8% for the same code on Earth), but it also closes flat wet
hollows into giant shallow lakes. Pass 2, exactly:
1. Restrict "no river leaves" to hollows whose lake at its closed level covers no more than the hollow's
   floor (lake area at balance well short of the hollow's area at the rim) or, more simply, require the
   catchment (not the floor) to be dryland by rain against the climate's land PET, not the lake evaporation.
   Check on Earth L6/L7 first (`earth_variants.py`, ~4 min each): target false positives at or below main's
   (2.1 / 5.5%) and wet false-positive rain below ~500 mm.
2. Then the same 4-seed L6 screen against main (`main` numbers above), watching giant-lake frames and the
   seed-3199 overshoot, and one L7 seed (the bigger gap: stored L7 runs 4-6% against 16.9% for Earth at L7).
3. Scorecard and full judge only before a merge.
The code of pass 1 is in `scout247/pass1.patch` (not applied on the branch).

Also worth correcting on the ticket: "the model gets 21% on Earth" is the HydroSHEDS basins imposed on the
Earth world; the model alone gets 10.7% (L6) / 16.9% (L7).
