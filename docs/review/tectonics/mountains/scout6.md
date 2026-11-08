# Scout 209 (PW-1497 pass 1 of 3): Andes-type ranges, diagnosis and screens

Scout 209, 2026-11-07/08. Code: main e6cb463c; candidate as a patch (`scout6_andean.patch`), not applied.

## In plain words

- **No candidate works; nothing to merge.** I added shortening of the overriding plate behind ocean-continent trenches
  (the Andes' main way of thickening crust), at a sourced rate: a third to all of the overriding plate's advance toward
  the trench, 1 cm/yr or so as in the central Andes. Five ways of paying for that crust were screened on 3 L6 seeds
  over 600 Myr, each against main on the same seeds.
- **Every arm makes far too much high ground, and little of it sits at the margins.** Baseline: main, same seeds, land
  above 3 km 1.4-2.7% (Earth 2.6%). With shortening it is 5-12% (new crust under the volume thermostat), 18% (crust
  taken from the whole overriding plate) or 25-30% (crust taken from the trench edge). The share of that high ground
  near an ocean-continent margin (Earth 25%) moves from 11-18% on main to 11-15% (thermostat arms), 20-22% (edge arm)
  and 34% (whole-plate arm), the last two only by wrecking the continents (land 34% on main falls to 24-28%).
- **Why:** an Andean shortening rate moves ~7x more crust per km of trench than the model's arcs do, and on a fixed grid
  the plate can't lose the area that shortening really costs. Each way of paying for it breaks a budget: new crust
  outruns the volume thermostat (+15% volume), and taking it from the plate thins or drowns the continent. The stacked
  belt also spreads ~300 km inland and outlives the trench that made it, so most of it is counted as interior plateau.
- **Next:** this is a judgement call (one draft): represent plate shortening as real area loss of the overriding plate
  (a large tectonics change, a lane rather than a scout), or accept that the model's high ground is mostly collisional.
  Pass 2 of 3 should not run another rate sweep of this mechanism.

## 1. Diagnosis (written before any run)

### What Earth says (sources fetched this pass)

- **Medvedev, Podladchikov, Handy & Scheuber 2006**, "Controls on the deformation of the Central and Southern Andes
  (10-35 S): insight from thin-sheet numerical modeling", ch. 23 in Oncken et al. (eds), *The Andes*, Springer (PDF from
  the FU Berlin publication page). The central Andes shorten at **1-1.75 cm/yr** today (they cite Oncken et al. ch. 1),
  the southern Andes at **0-0.5 cm/yr**. Taking the undeformed foreland as moving west at **3 cm/yr** (mid-Atlantic-ridge
  frame), "shortening of the Andes accommodates only part of this plate motion, while the other part is taken up by the
  westward motion of the western margin". Along-strike differences are put down to interplate coupling (trench fill,
  erosion, slab age; Lamb & Davis 2003 cited there) and the strength of the Andean lithosphere. Crust is 70 km or more
  under the central Andes.
- **Gotberg, McQuarrie & Carlotto 2010**, GSA Bulletin 122, doi 10.1130/B26477.1. To build a 60-70 km crust under the
  whole plateau from a 35-40 km one takes **240-300 km of shortening**; mapped shortening in southern Peru is 123 km (40%),
  in northern Bolivia 267 km (40%); the gap is closed by along-strike flow of crust and arc magmatism. Shortening
  started ~45-35 Ma, so the long-term mean is ~0.6-0.8 cm/yr.
- **Schellart 2008**, GSA Bulletin 120(11-12), 1441-1454, doi 10.1130/B26360.1 (abstract, ANU research portal). Over the
  world's subduction zones, overriding-plate deformation correlates weakly with most parameters (convergence rate,
  slab age, dip...) and best with **trench velocity**: a retreating trench goes with extension, a stable or advancing
  one with shortening. Orogenesis happens in the centre of wide subduction zones (>= ~4000 km) where the overriding
  plate moves **trenchward at 0-2 cm/yr** (Andes, Japan).
- A search abstract of Oncken et al. says shortening rate has "only a weak link to plate convergence rates"; I could not
  fetch the chapter itself (bot wall), so it is not used beyond Schellart's survey, which says the same.

So: total ~250-300 km over ~40 Myr; rate ~0.6-1.75 cm/yr, i.e. a third to a half of the overriding plate's trenchward
motion, ~10-25% of Nazca-South America convergence; the control is the overriding plate advancing on a trench the slab
pins, not the convergence rate itself.

### What the model does

- At an ocean-continent trench the overriding continent gains crust only from the arc (`crust.arc_growth`, ~0.03
  km/Myr per cm/yr at the source, spread over a ~380 km belt, scaled 0.1-5x by the volume thermostat) and loses it to
  subduction erosion. Per km of trench at 5 cm/yr that is of order 50 km^2/Myr of section. Andean shortening at 1 cm/yr
  of a 35 km crust is 350 km^2/Myr: on Earth the thickening behind the Andean arc is mostly shortening, and the model
  has none.
- The trench is the boundary the overriding plate wins in `plate_kernels.resolve`, so in the model the trench always
  moves with the overriding plate: there is no rollback. The overriding plate's own trenchward speed (mantle frame) is
  the natural Schellart control. No sediment-fill or slab-dip state exists to modulate it.
- Volume: shortening moves crust, it doesn't make it. On a fixed grid the plate can't lose area, so a stacked column
  needs a source. Three ways to pay for it, each a screen arm:
  - **thermo**: new volume, scaled by the volume thermostat like continental arcs. Risk: the thermostat's 0.1 floor
    can't offset a source 5-10x the arcs, so volume (and high ground) grows.
  - **conserve**: the overriding plate's continental crust pays, in proportion to its thickness (the area the plate
    loses, booked as thickness). Risk: whole-plate thinning floods the continent's interior.
  - **budget**: like thermo but with the thermostat's signal unfloored and capped at 1, so shortening stops while the
    continents hold more than their target volume. Risk: the high ground is concentrated volume, so total high ground
    may still rise.
- Other couplings: arc CO2 is `arc_nom` (unthermostatted), so no arm touches the outgassing directly; the PW-1446 height
  cap (`isostasy.max_km`) deletes crust above ~7 km of column, so a belt that piles too fast is clipped (booked as
  flow+cap) and the volume thermostat sees the loss.

### Candidates (rate = share x clip(overriding trenchward speed, 0, convergence), cm/yr; each km stacks a 35 km column)

| arm | share | volume source | expected | risk |
|---|---|---|---|---|
| main | 0 | - | Andes share ~8-18% of >3 km land | - |
| t05 / t10 | 0.5 / 1.0 | new, x volume thermostat | margin belts | volume overshoot past the 0.1 floor |
| c05 | 0.5 | overriding plate's continents | margin belts, volume fixed | interior thinning, lost land |
| b05 / b10 | 0.5 / 1.0 | new, unfloored thermostat <= 1 | margin belts, volume on target | total high ground up by concentration |
| e05 / e10 (round 2) | 0.5 / 1.0 | the trench-edge cell (down to 10 km; drained edges become ocean) | volume kept, plate loses area at its edge | area thermostat can't refill |

Implementation: `crust.andean_shortening` adds to the collisions' `stacked` before `crust.stack_collisions`, so the
belt spreads, folds to orogen rock and flows like a collision belt (one code path).

## 2. Screens

Setup: L6, seeds 1, 2, 6001, 600 Myr, default parameters plus the arm's switch (`scout6_screen.sh`); measured by
`scout6_measure.py` (scout1_margins' Andes measure plus hypsometry, ~29 frames with t >= 100 Myr). Runs were scratch,
under the worktree's exports/ (gone with it). The patch is `scout6_andean.patch` (not applied on the branch).
Baseline in every row: **main on the same seed and window**. Earth L6: >2 / >3 / >4 km = 5.0 / 2.6 / 1.6% of land; the
central Andes are 25% of Earth's land above 3 km (L7).

| arm (seeds) | Andes share of >3 km land | land >2 km | >3 km | >4 km | land % (median) | mean T C (median frames) |
|---|---|---|---|---|---|---|
| main (1, 2, 6001) | 11.4, 18.4, 18.2 | 6.9, 7.9, 5.7 | 2.7, 2.7, 1.4 | 0.75, 0.88, 0.27 | 34.0, 33.3, 34.0 | 17.7, 17.7, 16.2 |
| t05 thermo 0.5 | 14.5, 12.9, 11.9 | 16.4, 15.9, 14.6 | 5.1, 6.9, 6.4 | 1.1, 2.4, 3.0 | 36.6, 36.3, 36.8 | 16.8, 15.4, 15.6 |
| t10 thermo 1.0 | 11.5, 11.2, 11.0 | 18.6, 23.6, 18.9 | 7.8, 12.0, 8.9 | 2.3, 2.6, 1.4 | 37.8, 38.1, 38.8 | 15.5, 13.8, 13.5 |
| b05 budget 0.5 (seed 1) | 14.5 (bit-identical to t05: the thermostat never asked for more than 1) | 16.4 | 5.1 | 1.1 | 36.6 | 16.8 |
| b10 budget 1.0 (seed 1) | 11.0 | 19.4 | 8.6 | 3.6 | - | - |
| c05 conserve 0.5 (seed 1) | 33.5 | 27.2 | 18.2 | 10.6 | 23.5 | 14.7 (end 8.3) |
| e05 edge 0.5 (seed 1) | 20.2 | 38.1 | 25.0 | 14.4 | 27.7 | 16.9 |
| e10 edge 1.0 (seed 1) | 22.3 | 38.9 | 29.9 | 20.6 | 25.2 | 17.4 |

Budgets (seed 1, continental area / mean thickness / volume per cell; main holds 40% / 35 km / 14.0 throughout):
- thermo: volume rises to 15.9-17.5 (+14-25%) by 100-300 Myr, then eases back to 14.9 by 560 Myr; area 41-44%. The
  thermostat (x e^4err, floored at 0.1) can't offset a source several times the arcs, so it settles high.
- conserve: volume held (13-14), but the whole overriding plate thins and its interior floods: land 23.5%.
- edge (added after round 1: the trench-edge cell pays, so the plate loses area at its leading edge): area falls
  40% -> 27-31% and mean thickness rises to 46-50 km; the area thermostat's subduction-erosion lever (floor x0.2)
  can't make the area back. Same volume, piled on less continent.
- Hard failures were not judged (no 1 Gyr ice_diag draws: no arm reached the bar for the judge). The thermostat arms
  run 1-4 C cooler than main on the same seeds (more high ground, more weathering), within the climate's normal spread
  but in the wrong direction for a mechanism meant to be neutral.

Measure check: main's Andes share on these short L6 windows is 11-18%, above scout1's 8-10% (its L6/L7 runs to 1 Gyr).
The share is noisy between seeds (11 vs 18 on main) and 3 seeds are too few to resolve a change of a few points.

## 3. Verdict and next

**Not merge-ready; stopped at the screens** (diagnosis gate: no candidate clearly worked, so no 36-draw judge).
Nothing under planet/ is changed on this branch; the candidate lives in `scout6_andean.patch` for reference.

What the screens say about the mechanism, for whoever picks this up:
1. The rate is not the problem: even half the sourced rate overshoots. The problem is the **volume source**. Real
   shortening costs the overriding plate area at no change in volume; the model's plates are rigid on a fixed grid,
   and each proxy for that area loss (new volume, whole-plate thinning, edge drain) breaks the volume or area
   thermostat. A sound version needs the overriding plate to contract (its cells closing up toward the trench at the
   shortening rate), which is a plate-kinematics change in `plates`/`plate_kernels.resolve`, a lane not a scout.
2. Even where volume held (conserve, edge), the margin share rose only to 20-34% while total high ground rose 7-10x:
   the stacked belt (collision spread, ~300 km) drifts inland with the plate and outlives its trench. A margin belt
   would need its own narrower spread placed behind the arc (the arc's 1.6-cell belt with its forearc gap) and the
   measure would need belts that persist with the trench, not only frames.
3. Arc CO2 (`arc_nom`) was untouched by every arm; the height cap (PW-1446) clipped belts at ~7 km as designed
   (top cells 5.7-6.8 km in all arms); neither was the binding risk. The volume thermostat was (PW-1293).

Draft: `issue-tracking/inbox/draft-andean-shortening-needs-plate-contraction.md` (needs-decision: contract the
overriding plate in a lane, or accept collisional high ground and close PW-1497 as an Earth-only gap).

Sources: Medvedev et al. 2006 (ch. 23 of *The Andes*, Springer; PDF via the FU Berlin page
https://www.geo.fu-berlin.de/geol/fachrichtungen/geologie/mitarbeiter_neu/Professoren/mhandy/Pub-I-b/Medvedev_etal_06.pdf);
Gotberg, McQuarrie & Carlotto 2010, GSA Bull. 122, doi 10.1130/B26477.1
(https://www.sas.rochester.edu/ees/SIREAL/CAUGHTwebsite/Publications/2010/Gotberg_etal2010.pdf);
Schellart 2008, GSA Bull. 120, 1441-1454, doi 10.1130/B26360.1 (abstract:
https://researchportalplus.anu.edu.au/en/publications/overriding-plate-shortening-and-extension-above-subduction-zones-/).
