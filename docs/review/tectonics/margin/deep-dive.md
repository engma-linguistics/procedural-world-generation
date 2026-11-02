# The margin chain, piece by piece: physics or legacy stand-in? (lane 100e, PW-950, PW-1276)

Daniel asked (2026-11-01) for a wide look: which parts of the chain from eroded rock to land and CO2 are physics, which
are older stand-ins that newer physics may now cover, and what could change, settled code included. Below, each
piece gets what it is, its kind, what covers it now, and what I'd do. The screens are L6, 1 Gyr, seeds 1 and 3, run
through tracediag.py. The baseline is the sea-level fix (`sea`, see below). Late means the 600-1000 Myr mean. Single
seeds swing late dT by +-3 C between arms, so only land, crust and budget rows mean much at two seeds.

## In plain words

- **The area thermostat looked unneeded, but switching it off fails the judge.** With it switched off (`area_gain=0`), the continents still hold about
  40% of the surface (40.1 and 40.2% late, against 40.7 and 41.1% with it). Subduction erosion at its plain rate,
  collisions, rifting and the shredding of thin crust balance it on their own. Late in the run the thermostat was
  only *slowing* subduction erosion (by a quarter to a third). But the paired judge of it off (36 draws, against the
  sea-level fix) failed: 1 frozen-over world (a hard failure), pass 23/36 against 27/36, and the worlds ran colder
  (late dT -0.9 C, within the noise; hot desert -1.3 points, moved). It stays on (`area_gain` removed).
- **The volume thermostat is load-bearing.** Switched off, the continents thin and shrink (mean crust 11.6-13.1
  against 14.2 km over the surface; land 28-32% against 33-35%) and the worlds run 2-6 C warmer. The arcs' plain rate
  makes too little crust for what erosion and subduction take, so the thermostat doubles or triples continental arc
  growth late in the run. It stands in for a crust budget that isn't calibrated. It should be replaced, not removed:
  a separate, sourced job.
- **Arc CO2 already follows the slab** (PW-741). Nothing to change (note-arc-co2.md).
- **Sediment piles becoming continent at 20 km is the weakest piece.** With the creep, over three times as much crust is
  born from sediment late in the run, and much of it is shredded again by the coherence rule (about -40 000 against
  -5 000). That churn steers both thermostats. A pile on ocean floor is sediment on oceanic crust. It should join a
  continent only when it is scraped onto one (accretion at a trench, or collision).
- **Sea level now counts the ocean floor's sediment** (fixed and judged, 72 paired draws: no climate measure moved,
  land -0.6 points, pass 57/72 against 57/72).

## The pieces

| piece | what it does | kind | what newer physics covers | change? |
|---|---|---|---|---|
| area thermostat (`crust.thermostats`, `shrink` on `subduction_erosion`) | scales subduction erosion by e^(4 x log-error + integral) to hold the continental area at `continental_fraction` | legacy stand-in (PW-046/052, when area ran 12% high) | collision and overlap (`resolve`, -116 000 km x cells over 1 Gyr on seed 1), coherence shredding, rifted margins (+42 000), births, and subduction erosion at its nominal rate | **keep**: off failed its judge (1 frozen over, pass 23 vs 27 of 36). It looks redundant for area, but it shapes the climate through the arc and erosion budget it trims |
| volume thermostat (`thermostat` on continental arcs) | scales Andean-arc growth to hold the mean continental thickness at 35 km | stand-in for an uncalibrated crust budget | nothing yet: nominal arcs (`arc_growth` 0.03 km/Myr per cm/yr) fall short of the sinks | keep for v1. Later, replace it with a sourced arc addition rate plus the missing returns (subducted sediment melting into the arc, underplating), and let the volume float |
| arc CO2 | 20 x the arcs' *nominal* growth (slab melt: convergence x trench edges x mantle heat) | physical, since PW-741 | — | none. The late cooling some arms show is late slab flux against the 0-300 Myr reference (PW-1158) |
| sediment born continental at 20 km (`crust.birth_and_cratons`, `BECOMES_CONT_KM`) | any non-hotspot ocean column (arc or sediment pile) at 20 km turns continental | arcs: physical; sediment piles: stand-in | `crust.accrete` already scrapes trench sediment onto the overriding plate; collisions weld margins | **changed** (PW-1292, lane 112, judged: [pw1292-note.md](pw1292-note.md)): sediment piles stay oceanic unless they touch their plate's continental crust, or are accreted. It barely touches the creep's churn, which looks like a flicker at the 20 km bound. A draft, with a screen and a judge. (C, keeping drowned piles out of the area count only, didn't help: land -0.3/-0.2 on main, -1.3/+1.2 with the creep) |
| brink rule (`surface._offshore`) | at the shelf's edge the load drops as a foreset and fills toward shelf level | physical (clinoform progradation, PW-818) | the creep (`slope_k`) relaxes the resulting wall | keep |
| sea level and ocean-floor sediment | the basins' part read the floor's age only | bookkeeping gap | — | **fixed** (`earth.floor_sediment_water`, judged) |
| drowned continental isostasy | continental columns float as in air even under water | approximation | — | low priority (draft-drowned-continental-crust-floats-as-in-air) |
| CO2 source reference | learnt over 0-300 Myr, then frozen (`REF_FREEZE`) | design choice (PW-576) | — | PW-1158's question. Any change to the plate history moves late slab flux against that reference by 5-15% |
| volume counts sediment cover (`vol` = thick x cont) | sediment carried off a continent is lost volume that arcs replace | stand-in | — | goes with the volume thermostat's replacement (old option B) |

## Screens (seed 1 / seed 3, late)

| arm | land % | cont % | mean crust over the surface (km) | late dT (C) | subd. erosion, 600-1000 | cont. arc growth, 600-1000 | born, 600-1000 | coherence, 600-1000 |
|---|---|---|---|---|---|---|---|---|
| sea (sea-level fix, both thermostats) | 33.3 / 34.7 | 40.7 / 41.1 | 14.15 / 14.26 | -1.3 / -1.2 | -14 500 / -13 300 | 26 700 / 27 300 | 13 200 / 14 500 | -6 200 / -4 300 |
| sea, area thermostat off | 33.9 / 34.4 | 40.1 / 40.2 | 14.09 / 14.07 | -2.0 / +1.1 | -18 800 / -19 200 | 32 200 / 31 700 | 17 100 / 12 300 | -3 200 / -5 700 |
| sea, volume thermostat off | 31.7 / 31.0 | 38.3 / 37.3 | 13.07 / 12.94 | +1.7 / +6.0 | -5 600 / -5 000 | 17 600 / 16 200 | 10 200 / 10 900 | -4 200 / -4 000 |
| sea, both off | 28.8 / 28.5 | 35.5 / 33.8 | 11.69 / 11.56 | +5.6 / +3.8 | -20 000 / -20 500 | 16 600 / 15 400 | 10 400 / 8 700 | -8 000 / -5 400 |
| sea + creep | 31.5 / 31.0 | 41.8 / 41.2 | 14.26 / 14.01 | +0.5 / -3.2 | -17 000 / -20 400 | 33 500 / 38 600 | 42 100 / 50 600 | -41 200 / -46 200 |
| sea + creep, area thermostat off | 29.9 / 32.4 | 39.7 / 41.4 | 14.26 / 14.40 | -4.9 / -5.0 | -21 500 / -26 400 | 49 700 / 45 400 | 56 500 / 45 200 | -45 500 / -38 700 |

(km x L5 cells. Creep = `neck_km=200 rise=1 slope_k=1000`.)

Reading:
- With the volume thermostat on, the area holds without the area thermostat. With the volume thermostat off, the area
  thermostat pins subduction erosion at its floor (0.2x) and still loses area. So the two aren't symmetric: the
  volume one carries the budget.
- With the creep, the sediment-birth churn (born +45 000 and coherence -40 000 per 400 Myr) is the largest flux in
  the late budget, ahead of the arcs. That is the piece to fix before the creep goes on by default, more than either
  thermostat.

## What I'm folding in now

1. The sea-level fix: judged, kept.
2. Area thermostat off: judged against `sea` (36 draws, 2 rolls). It failed (table below), so it isn't folded in.
3. Then the creep on top (judge 2), as planned.

Judge, area thermostat off against the sea-level fix (paired medians, B - A, bootstrap 95% CI):
late dT -0.86 [-1.89, +0.46], late CO2 -0.10 [-0.26, +0.12], land -0.29 [-0.73, -0.12] *, hot desert -1.28
[-2.05, -0.37] *, end T -2.2 [-6.0, +1.0]. Pass 27/36 (sea) against 23/36 (off); both 16, sea only 11, off only 7
(McNemar p 0.48). Hard failures: sea 0, off 1 (frozen over in the window).
The volume thermostat's replacement and the sediment-birth rule are drafts (they need sources and a design).

## Judges (L6, v1-finish-16's 18 draws, paired_margin.sh, tools/hard_bar.py + pjudge.py)

Judge 1, sea-level fix against main (code `50f3ab15` + the fix), creep off, 4 rolls (72 paired draws; rolls 3-4 were
added because the 2-roll pass count, 27 against 29, was the only thing that could decide it). Hard failures: main
1 (frozen over), fix 0. Pass 57/72 against 57/72 (both 43, main only 14, fix only 14). Paired medians, fix - main:
late dT +0.34 [-0.96, +1.34], late CO2 +0.03 [-0.13, +0.19], land -0.60 [-0.88, -0.47] *, arid +0.89 [+0.05, +1.36]
*, end T +1.6 [-1.2, +3.6], source and sink references unmoved. L7 earth_check is byte-identical to main's (the fix is
tectonic sea level only). **Passes.**

Judge 2, creep (`neck_km=200 rise=1 slope_k=1000`) on top of the fix, against the fix, 2 rolls (36 paired draws).
Hard failures: 2 frozen over (fix: 0). Pass 30/36 against 27/36 (McNemar p 0.51). Paired medians: late dT -2.55
[-3.52, -0.71] *, late CO2 -0.33 [-0.46, -0.04] *, land -3.00 [-3.29, -2.51] *, arid -3.9 *, hot desert -2.7 *, end
T -2.9 [-4.4, -0.2] *. **Fails** (hard failures, and the climate moved colder). The creep stays off. The land loss and
cooling are the same as round 3c's, so the sea-level fix doesn't cure them. The deep dive points at the sediment-birth
churn as the next thing to fix (draft-sediment-piles-born-continental).
