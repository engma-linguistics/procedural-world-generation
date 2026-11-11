# Lane 286 (PW-1680): does high ground climb late in a run with Andean shortening and collapse on?

Lane 286, 2026-11-10. Base: main 7dae542a (PW-1497 merged: `andean_shortening` 0.1, `collapse` 30 on by default).
Script: `docs/review/tectonics/mountains/andes_late_series.py` (read-only, per 20-Myr checkpoint).

## In plain words

See "In plain words (summary)" at the end: the late rise is pulses caught by a single-moment reading, not a trend;
no default change.

## 0. Runs and baselines

All L6 runs are `planet simulate --level 6 --myr 1000 --checkpoint-every 20`, under the scratch root
/data/personal/scratch/lane286 (deleted after measuring). Two arms on the same code (7dae542a):

- **on**: main's defaults (Andean shortening 0.1, collapse 30);
- **off**: the same code with `andean_shortening=0 collapse=0`, i.e. main as it was before lane 275b.

These reproduce the scorecard's two runs: the off arm ends seed 2 with land 34.4% (scorecard a626c541 seed 2:
34.4%) and the on arm with 33.4% (scorecard c219720a seed 2: 33.4%), so the measurements below are of the very
runs the ticket's numbers came from, plus checkpoints.

Earth, for the plausibility anchor: ETOPO1 (Amante & Eakins 2009, NOAA NGDC; `tools/earth_data.py`) sampled on
the model's own grid (`data/earth/L6.npz`, `L7.npz`), computed here on bedrock elevation over land:
land above 3 km **2.4%** (L6) / 2.5% (L7), above 4 km **1.5%** (L6) / 1.6% (L7); 2.6% / 1.6% if the Antarctic and
Greenland ice-covered cells are left out. (The ticket's "Earth at L6 ~1.5%" for > 4 km is confirmed.)

## 1. Diagnosis (written before any fix arm)

### 1.1 Is the late rise real?

Per checkpoint (every 20 Myr from 100 Myr), share of land above 3 and 4 km. Medians over windows (scout8.md's bar
reads medians over keyframes; means in brackets):

| seed | arm | >3 km 100-600 | >3 km 600-1000 | >3 km 900-1000 | >4 km 600-1000 | >4 km mean 600-1000 | Andes share of >3 km, 600-1000 |
|---|---|---|---|---|---|---|---|
| 1 | on | 3.62 | 3.36 (mean 4.22) | 2.66 | 1.55 | 1.99 | 25.4 |
| 1 | off | 3.81 | 3.54 (mean 3.28) | 4.58 | 1.69 | 1.46 | 8.9 |
| 2 | on | 1.27 | 3.30 (mean 3.41) | 6.40 | 1.20 | 1.70 | 29.4 |
| 2 | off | 3.64 | 2.67 (mean 2.84) | 3.08 | 1.01 | 1.12 | 12.5 |

- **Medians are not higher late.** Over 600-1000 Myr the on arm's median land above 3 km is 3.36/3.30% against the
  off arm's 3.54/2.67%, and above 4 km 1.55/1.20% against 1.69/1.01% (Earth 1.5%).
- **Means and peaks are.** The on arm's high ground comes in pulses: seed 1 reaches 7.3-7.6% above 3 km at
  740-780 Myr, seed 2 climbs 3.99 -> 8.42% over 900-1000 Myr, then (seed 1) falls back to 1.7% by 940 Myr.
  The mean over 600-1000 Myr above 4 km is 1.99/1.70% against 1.46/1.12%: about +0.5 point, ~1.4x.
- **The scorecard's 1-Gyr "doubling" is a snapshot of a pulse.** Seed 2's 4.86% at 1000 Myr sits on a collision
  pulse that began at ~920 Myr; the off arm had its own at 940-980 Myr (2.3-2.8% above 4 km).

### 1.2 Which belts are high late?

Of the land above 4 km at each checkpoint, 600-1000 Myr (means): "live" = squeezed in the last 20 Myr (collapse
does not act on it); "Andean" = within 5 L6 cells of the continental side of an ocean-continent plate edge and not
within 3 of a continent-continent one (the Andean belt reaches ~7 L6 cells inland, 3 x ANDES_BELT); "collision" =
within 3 cells of a continent-continent plate edge.

| seed | arm | live | Andean | collision | rest (live inland or dead) |
|---|---|---|---|---|---|
| 1 | on | 96% | 17% | 57% | ~26% |
| 1 | off | 53% | 9% | 27% | ~64% |
| 2 | on | 99% | 32% | 52% | ~16% |
| 2 | off | 61% | 6% | 35% | ~59% |

- **Collapse is firing.** With it on, 96-99% of the land above 4 km was squeezed in the last 20 Myr; without it,
  40-47% is dead belts. No old belt is standing.
- **The late high ground is live belts: about half collision, a fifth to a third Andean.** Both are legitimate
  in kind. The Andean part is the change PW-1497 wanted (Andes share of > 3 km land 25-29% late, Earth ~25%).
- **Why the pulses are higher than the off arm's background.** Continental area: the on arm holds it on its
  target (40%: 40.1/40.6% mean late) while the off arm runs above it (42.5/41.6%), with the same crust volume
  (volume/target 1.01-1.04 both), so the on arm's continents are ~0.7-1.5 km thicker on average (35.7/34.9 km
  against 34.2/34.2 km): ~100-200 m higher everywhere, which lifts the tail above 3-4 km most. Andean closing is a
  large new sink of continental area (book `andean.closed`: 59-61 thousand km x L5 cells of crust moved by
  1 Gyr, against subduction erosion's 15-28 thousand), and the area thermostat answers it: on seed 1 its only
  lever (subduction erosion) sits at its floor (x0.20-0.24) from 400 Myr to the end; on seed 2 at x0.5-0.7.
  The area stays on target, so this is the thermostat working, not failing; but the target is now met with no
  slack on seed 1.

### 1.3 Is the cooling a consequence of the high ground?

Per checkpoint the weathering supply (bare ground's erosion, `earth.weathering`'s `supply`; the CO2-independent
driver of the sink), with the share of it from land above 3 km, and the carbon state. Means 600-1000 Myr:

| seed | arm | supply | from > 3 km | co2 (ln vs balance) | dT (C) | land ice % of land | land NPP |
|---|---|---|---|---|---|---|---|
| 1 | on | 847 | 12.4% | +0.63 | +1.3 | 8.4 | 414 |
| 1 | off | 656 | 5.1% | +0.86 | +2.6 | 5.5 | 427 |
| 2 | on | 715 | 10.5% | +0.83 | +1.4 | 8.6 | 454 |
| 2 | off | 661 | 8.4% | +0.43 | +0.1 | 10.0 | 402 |

- **Seed 1: yes.** 29% more weathering supply, two and a half times as much of it from land above 3 km; CO2 lower,
  1.3 C cooler, more land ice. Within the run the cold spells follow the pulses: 740-820 Myr, land above 3 km
  7.2-7.6%, co2 -0.4..0.0, dT -4.2..-5.8 C, land ice 17-20%.
- **Seed 2: no.** 8% more supply, but CO2 is higher and the late window is 1.3 C warmer than the off arm; its
  1000-Myr snapshot (dT -3.2 C, ice 20%, NPP 365) is the start of a cold spell on the 920-1000 pulse.
- So the cooling is the high ground's (more fresh rock eroding fast, the uplift-weathering link the model's sink
  is built on; Raymo & Ruddiman 1992, "Tectonic forcing of late Cenozoic climate", Nature 359:117-122,
  doi:10.1038/359117a0, is the classic statement for Tibet, a contested hypothesis on Earth, checked on nature.com's
  record here), in pulses, not a separate effect. The NPP drop
  in the scorecard (582/503 -> 317/365) is a 1000-Myr snapshot taken in such a cold spell: the late-window mean NPP
  is 414/454 against 427/402.
- The judge's late dT shift (-0.8 C, CI -1.3..+0.5, lane 275b) does not exclude zero; glacial maxima 10 vs 3 of 18
  are cold spells of this kind (land ice >= 25%, Earth's LGM level), which the v1 bar reports but does not fail.

### 1.4 Candidate fixes (written before measuring them)

1. **Nothing (legitimate, within bounds).** Late medians match the off arm and Earth (ETOPO1 > 4 km 1.5%); the
   excess is in live collision and Andean belts; the cooling is the uplift-weathering link, in pulses. To be
   confirmed on seed 6001 and at L7.
2. **`andean_steer = 1`** (built by scout 237, never screened at L6): the area thermostat's factor also steers
   Andean closing, as it steers subduction erosion, since both are the trench's sinks of continental area. When
   area is short (seed 1, thermostat at its floor), closing slows, area recovers and crust thins. Mechanism of the
   model's own budget, not a clamp on height; but it ties a kinematic rate to a global budget, and at the floor
   it would cut Andean shortening to 0.2x, losing the Andes share.
3. **Extensional collapse that returns area** (not built): on Earth a collapsing plateau extends (the Basin and
   Range roughly doubled in width), giving back the area shortening took. In the model collapse is lower-crustal
   flow among continental cells, area-neutral. Letting collapse also widen the continent at its edge would close
   the area loop physically. Larger change; a draft if the evidence calls for it.

## 2. Screens

### 2.1 Third seed (6001), the ticket's checkbox

Same arms, L6, 1 Gyr. Medians of the checkpoints (scout8.md's measure), and means 600-1000 Myr:

| seed | arm | >3 km 600-1000 | >3 km 900-1000 | >4 km 600-1000 | >4 km mean | Andes share | dT | land ice % | NPP |
|---|---|---|---|---|---|---|---|---|---|
| 6001 | on | 1.40 | 1.68 | 0.47 | 0.49 | 28.8 | +1.0 | 6.3 | 442 |
| 6001 | off | 3.31 | 5.33 | 1.19 | 1.34 | 14.4 | -1.4 | 18.9 | 383 |

Over the three seeds (1, 2, 6001), 600-1000 Myr:

| measure | on | off |
|---|---|---|
| land > 3 km, median per seed | 3.36, 3.30, 1.40 (mean **2.69**) | 3.54, 2.67, 3.31 (mean **3.17**) |
| land > 4 km, median per seed | 1.55, 1.20, 0.47 (mean 1.07) | 1.69, 1.01, 1.19 (mean 1.30) |
| land > 4 km, mean per seed | 1.99, 1.70, 0.49 (mean 1.39) | 1.46, 1.12, 1.34 (mean 1.31) |
| land > 3 km, median 900-1000 | 2.66, **6.40**, 1.68 (mean 3.58) | **4.58**, 3.08, **5.33** (mean 4.33) |
| Andes share of > 3 km | 25.4, 29.4, 28.8 | 8.9, 12.5, 14.4 |
| dT (C), mean | +1.3, +1.4, +1.0 (mean +1.2) | +2.6, +0.1, -1.4 (mean +0.4) |
| land ice % of land, mean | 8.4, 8.6, 6.3 (mean 7.8) | 5.5, 10.0, 18.9 (mean 11.5) |

- **No late rise across seeds.** On 600-1000 Myr the on arm passes scout8.md's bar (mean <= 3.0%, no seed above
  3.5%: 2.69%, max 3.36%) and the off arm does not (3.17%, seed 1 3.54%). In the last 100 Myr both arms break it
  on single pulses (on: seed 2; off: seeds 1 and 6001). Seed 6001 goes the other way from seed 2: lower high
  ground and warmer with the mechanism on.
- **No systematic cooling** in these three pairs (on is warmer on two of three seeds, with less ice on average).
  The judge's colder signal (glacial maxima 10 vs 3 of 18, late dT -0.8 C with a CI across 0) is on other seeds
  and a brighter-star setting; it stays as lane 275b measured it. The high ground-to-weathering link is real
  within a run (section 1.3) but which arm has the bigger pulse late is chaos.

### 2.2 Candidate 2: `andean_steer = 1` (seeds 1, 2, L6, 1 Gyr; against the on arm, same seeds)

| seed | >3 km median 600-1000 | >4 km median | Andes share | dT mean | ice % | area thermostat |
|---|---|---|---|---|---|---|
| 1 | 1.80 (on 3.36) | 0.85 (on 1.55) | 24.6 (on 25.4) | +1.9 (on +1.3) | 5.6 (on 8.4) | x0.5-0.8, off its floor |
| 2 | **5.73** (on 3.30) | **2.55** (on 1.20) | 18.7 (on 29.4) | -1.4 (on +1.4) | 17.3 (on 8.6) | x0.3-0.35 |

Rejected: it takes seed 1's area thermostat off its floor and halves its high ground, but nearly doubles seed 2's
and makes it 2.8 C colder. No consistent sign, so it is chaos plus a weaker Andes share, not a fix.

Candidate 3 (extensional collapse returning area) was not built: section 2.1 shows nothing to fix, and the
thermostat holds area on target on all three seeds (seed 1 with no slack).

## 3. L7, seed 2, 1 Gyr, main's defaults (7dae542a; run 8f0042 in the scratch root, deleted)

One run, `--level 7 --checkpoint-every 20`, seed 2 (the seed whose L6 run climbed late). The Andes zone at L7 is
4 cells (scout6_measure's), the attribution zones 10 and 6 cells. Every 100 Myr, then window medians:

| t (Myr) | > 3 km | > 4 km | Andes share of > 3 km | land ice % | land NPP | dT (C) |
|---|---|---|---|---|---|---|
| 200 | 5.48 | 2.26 | 8.2 | 6.7 | - | +3.2 |
| 300 | 3.59 | 2.08 | 27.4 | 2.4 | - | +4.6 |
| 400 | 4.18 | 1.89 | 13.2 | 11.7 | - | +0.3 |
| 500 | 2.22 | 1.11 | 20.7 | 20.9 | - | -3.3 |
| 600 | 4.34 | 1.11 | 14.4 | 10.8 | 337 | +1.6 |
| 700 | 4.33 | 0.83 | 23.5 | 2.2 | 367 | +7.4 |
| 800 | 2.57 | 0.96 | 7.1 | 12.5 | 396 | +1.8 |
| 900 | 2.95 | 1.29 | 21.1 | 3.0 | 508 | +4.8 |
| 1000 | 1.65 | 0.09 | 26.0 | 2.9 | 555 | +4.0 |

| window | > 3 km median | > 4 km median | Andes share (pooled) |
|---|---|---|---|
| 100-600 | 3.69 | 1.95 | 15.5 |
| 600-1000 | 4.33 (mean 4.01) | 1.29 (mean 1.45) | 17.9 |
| 900-1000 | 4.04 | 1.17 | 15.2 |

Late means (600-1000): land ice 9.1% of land, NPP 394 g C/m2/yr, dT +2.5 C; 88% of the land above 4 km live
(collapse working), 44% of it by collisions, 15% Andean.

- **No late climb at L7.** Land above 4 km falls from a median of 1.95% (100-600 Myr) to 1.29% (600-1000) and 1.17%
  (900-1000); the run ends at 0.09%. Earth on the L7 grid: 1.6% (ETOPO1). The highest peak late is 3.35% at 840 Myr.
- **Land above 3 km is high at L7**: median 4.3% late against Earth's 2.5% on the L7 grid, and the L7 continents
  are thicker than L6's (mean continental crust 36.9 km late against 34.9 km on the L6 run of the same seed).
  There is no L7 run without the mechanism to say whether this is PW-1497's or L7's own; L6 shows no such
  difference between arms (section 2.1). Inbox draft `draft-l7-land-above-3km.md`.
- Andes share at L7 is lower than at L6 (18% against 25-29%), on one seed.

## In plain words (summary)

- **The late rise is not a trend; it is mountain-building pulses landing on the measuring moment.** With collapse
  on, high ground comes and goes: a collision raises it for 50-100 Myr, then it comes down. The scorecard reads one
  moment (1000 Myr), and on seed 2 that moment sat on a pulse. Over the last 400 Myr of three test planets, land
  above 3 km is lower with the new physics (2.69% against 3.17%, Earth 2.4%) and land above 4 km about the same
  (1.07% against 1.30% by median, 1.39% against 1.31% by mean; Earth 1.5%).
- **Collapse works**: 96-99% of land above 4 km is in belts being squeezed now (without it 40-47% is dead belts).
- **The cooling** follows the pulses (fresh high ground weathers fast and draws down CO2), but which arm is
  colder late is chance: two of three planets are warmer with the new physics, and on average there is less ice.
  The scorecard's NPP drop is the same snapshot falling in a cold spell.
- **Verdict: legitimate and within bounds; no default change.** The one candidate fix (`andean_steer`) halved
  high ground on one seed and doubled it on the other, so it was dropped.
- **L7 (seed 2, 1 Gyr, today's defaults)**: land above 4 km falls late (median 1.3%, Earth 1.6%), so no
  over-mountainous showcase from this. Land above 3 km is high at L7 (4.3%, Earth 2.5%), cause not yet known.

## Hand-off state

Done. Commits on this lane: the diagnosis (b6ffa840) and this write-up. No code change. Scratch root
/data/personal/scratch/lane286 deleted after measuring (no symlinks were made in it). Drafts:
`draft-scorecard-late-window-medians.md`, `draft-l7-land-above-3km.md`.
