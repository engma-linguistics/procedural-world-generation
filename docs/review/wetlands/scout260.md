# PW-831 scout 260, pass 1 (of 3): diagnosis gate for wetland evaporation

Branch `worktree-agent-ac502a6f660c0286b` on main 56bb8692. Scripts: `scout260/`. Scratch (s260) =
`/tmp/claude-1000/-data-personal-repos-procedural-world-generation/43861907-2d55-4b88-96fd-7cf556b60255/scratchpad/s260/`
(deleted after the pass; nothing written to runs/, worlds/ or data/earth).

## In plain words
The model's rivers never lose water on the way through a swamp: a river crossing the Sudd, the inner Niger delta,
the Okavango or the Pantanal leaves with at least what it came in with, plus the local rain. Only lakes evaporate.
In reality the Sudd loses about half the White Nile, the inner Niger delta about 40% of the Niger, and the
Okavango almost all of its river. A first try (the flooded strip beside big rivers evaporates like open water,
its width from how fast a shallow flood sheet flows on that slope) moves the rivers the right way but only a third
of the way, and on Earth the model's own climate is so wet over these swamps that it would not show there anyway.
Side finding: the dry-catchment rule merged for PW-054 closes the inner Niger delta at L7, so the Niger ends in a
desert lake instead of reaching the sea (draft filed).

## Observed values (fetched, not from memory)
| wetland | in | out | loss | source |
|---|---|---|---|---|
| Sudd (Bahr el Jebel) | Mongalla 26.8 km3/yr (~850 m3/s), 1905-60; 50.3 km3 1961-80 | swamp exit 14.2 / 21.4 km3 | 47% / 57.5%; "~55%" (Baecher 2000), "half" | table in chijournal.org/C448 (Sutcliffe & Parks 1987 lineage); en.wikipedia.org/wiki/Sudd |
| inner Niger delta | Ke-Macina + Douna ~1490 m3/s, 1955-96 | Timbuktu ~900 m3/s | ~40% (24-48% by year), 18.7 km3/yr | Mahe et al. 2009, via iahs.info/uploads/dms/16775.26-138-143-344-30-Mahe-et-al-corr.pdf |
| Okavango | Mohembo ~10 km3/yr (2006/07 observed) | Maun Bridge 0.51% of Mohembo; Boro ~2% | 95-98% | Kurugundla, Moleele & Dikgola, water.gov.bw/images/Reports/Okavango_Delta.pdf |
| Pantanal (Paraguay main stem) | Caceres 382 m3/s, Descalvados 437 | Porto Conceicao 341, Porto Murtinho 1555 (after all tributaries) | main stem -22% Descalvados -> Porto Conceicao; no clean basin budget found | ponce.sdsu.edu/hidroviareporttable15.html (EDIBAP 1979 means) |

## Method
`earth_capture.py LEVEL` builds the Earth world (tools/earth_world.build: ETOPO terrain, the model's climate) and
pickles what `hydrology.rivers_and_lakes` is given; `earth_wet.py` reruns only the hydrology (as the Earth world:
outlet, closed basins, valley; `--free`: none imposed, as scout 250) and traces each river downstream from the
biggest river near its inflow gauge whose course passes the last gauge. `--obsrain` swaps in GPCC's half-year rain
(earth_data obs_p_jul / obs_p_jan) through the model's water balance (default Budyko w) on the model's
temperatures: the swamps' real climate without the model's rain bias. Variants are module flags in
`planet/hydrology.py` (WETLAND_ET off by default: main's behaviour is unchanged on this branch).

## Diagnosis (baseline: main 56bb8692)
1. **No wetland loss exists.** Along all four rivers the discharge never falls through a non-lake cell: the
   source term is the local runoff (P - AET >= 0), and only `wet` (lake) cells carry the open-water deficit
   `lake_evap - aet` (`lakes()`: `src - loss * wet`). Earth L7, observed rain: White Nile 2045 m3/s at 5.7 N ->
   2332 at 8.8 N, above the Bahr el Ghazal junction (+14%; observed -47 to -57%); Okavango 781 -> Maun 801 (+3%;
   observed to 0.5-2%); the Niger and Okavango lose water only where a lake forms.
2. **On Earth the model's climate hides the problem.** With the model's own rain the Sudd cells get 2200-2500
   mm/yr (GPCC 750-1000 mm) and the Pantanal 2100-2200 (GPCC ~1200), more than the open-water evaporation
   (1850-2100 mm): a swamp there would gain water. White Nile at the Sudd's inflow 11,900-14,600 m3/s (L7/L6;
   observed ~850), Paraguay at Porto Murtinho 27,000-28,000 (observed 1555). Land runoff reaching the sea
   2.05-2.08 M m3/s against 1.29 M with GPCC rain through the same water balance. Wetland checks on Earth
   need the observed rain (`--obsrain`); the rain bias is PW-228 / PW-015's.
3. **The flooded share is far too small for an inland delta.** `vegetation.floodplain` (the existing wetland
   habitat share, 0.35 x log10(Q / 500 m3/s) / 1.5 x flatness) gives 0.06-0.10 of a cell at the Sudd's
   ~900-2000 m3/s; the real Sudd floods ~30,000-40,000 km2 along ~400 km of river, i.e. most of 3-4 L6 cells.
4. **MIN_SLOPE / MIN_DEPTH are not the lever.** None of the four rivers' cells lies in a hollow `_bed` fills
   (bed - carved ground <= 0 all along at L6 and L7): the swamps are flat through-flowing plains on the cell
   means, not filled pits, so treating filled hollows as swamps (candidate 'hollow') changes nothing on Earth.
   Lowering MIN_SLOPE would make shallow lakes (what PW-430's giant shallow lakes are) rather than swamps.
5. **Interaction with the dry-catchment rule (scout 251).** At L7 the Niger ends in a closed lake in its inner
   delta (14.5-15.0 N, 4.3 W) with the rule on, under the model's climate (2962 m3/s arriving) and under
   observed rain (434 m3/s left); `DRY_HOLLOWS = False` sends it on to the sea (Dire 3219 / 677 m3/s). The rule
   reads the catchment's area-mean P/PET, so an exotic river from wet highlands through the Sahel counts as dry.
   Real: ~60% passes (Timbuktu ~900 m3/s). Draft `draft-dry-hollow-closes-niger-delta.md`. A wetland ET makes
   rivers into such hollows smaller still, so the two should be judged together: a wet-catchment check that
   uses the inflowing discharge would see the wetland losses upstream.

## Candidates
- **A. Floodplain open-water ET ('plain').** Charge `lake_evap - aet` over `vegetation.floodplain`'s share of
  each non-lake land cell, taken from the river (`wetland_share`, in `lakes()`' returned `src`; the run's
  `surface.erode` and the worlds both route over it). Physical and cheap, but the share is calibrated for
  habitat, not inland deltas: too small (diagnosis 3).
- **B. Manning sheet spreading on unconfined flat reaches ('sheet', tried).** The flood spreads as a sheet h deep;
  the width that carries the river's discharge at Manning's speed is W = Q n / (h^5/3 S^1/2), S the cell's slope
  to its lowest neighbour (floor 1e-5), times the cell's flatness (relief < 400 m, as floodplain), capped at 0.75
  of the cell; open-water ET over max(A, B). Low gradient -> wide swamp, and the loss is capped by what the
  river carries. n = 0.1 (Chow 1959: floodplain brush to timber 0.05-0.2), h = 1 m: textbook values, not fitted.
- **C. Inland deltas as swamp basins ('hollow', tried, inert on Earth).** The floors of hollows `_bed` fills as
  plains flood (a share of them) and evaporate. Not where Earth's swamps are on the cell means (diagnosis 4);
  would matter on generated worlds' fresh shallow hollows (PW-430's), as a sink of water rather than a lake.

## Earth results (ratios: discharge out / in along the traced river; baseline: main, same inputs)
Earth world inputs as built (outlet, closed, valley).
| | to sea, k m3/s | White Nile 5.7 N -> 8.8 N (pre-junction) | White Nile Sudd -> Khartoum (ratio) | Okavango -> Maun | Niger | Paraguay Porto Murtinho, m3/s |
|---|---|---|---|---|---|---|
| L6 obs rain, main | 1291 | 882 -> 920 (L6 path) | 4.31 at Lake No | 1.02 | routes west to the Senegal on L6 | 7915 |
| L6 obs rain, A plain | 1254 (-2.9%) | 870 -> | 3.98 | 0.96 | - | 7417 |
| L6 obs rain, B sheet | 1215 (-5.9%) | 867 -> | 3.40 | 0.89 | - | 6884 |
| L6 obs rain, B n 0.2 / h 0.5 | 1189 / 1169 | | 2.84 / 2.30 | 0.73 / 0.51 | - | 6586 / 6272 |
| L7 obs rain, main | 1291 | 2045 -> 2332 (+14%) | 4.93 | 1.03, then a closed lake | ends in a lake at 15.0 N (434 left) | 6042 |
| L7 obs rain, B sheet | 1221 (-5.4%) | 1995 -> 2019 (+1%) | 3.66; 4928 -> 4078 over 9.7-14.3 N (-17%) | 0.90 | ends, 142 left | 5140 (-15%) |
| L7 obs rain free, main / B | 1213 / 1163 | 1785 -> 1845 / 1706 -> 1668 | ends in a sink at 7.7 N | 0.56 / 0.47 | Dire / Ke-Macina 0.88 / 0.65 (obs ~0.6) | 6212 / 5314 |
| L7 model climate, main / B | 2080 / 1993 (-4.2%) | 11,865 in | 5.49 / 5.30 | 1.71 / 1.69 | ends in a sink (rule) | 27,140 / 25,720 |
Inland % and lakes % of land are unchanged by A and B in every Earth case (21.8 / 22.4 / 20.9%; 0.46-0.81%).

Reading: B goes the right way everywhere and does no harm to the inland and lake measures, but at textbook
parameters it gives the Sudd ~0 to -17% where reality is ~-50%, and the Okavango -10% where reality is -98%.
The parameters that would close the gap (n 0.2-0.3, h 0.5 m) are inside the literature ranges but are then a
fit, and the real inland deltas owe their size to a channel that shrinks downstream (the Bahr el Jebel's
capacity is far below its inflow) and to the seasonal pulse, neither of which the cell means carry.

## Generated-world screen (L6, seeds 1 and 77, forked at 200 Myr, 3 re-rolled draws, frames after 200 Myr)
Main (56bb8692) spun each seed to 200 Myr; main and candidate B (`WETLAND_ET = True`, `WETLAND_MODE = "sheet"`,
n 0.1, h 1 m) continued that state to 400 Myr (scout 251's `fork_run.py`, draws = climate_offset 0 / 1e-5 C after the
fork). Two draws each (cut from three: the machine's load passed 30 mid-queue). `scout260/measure.py` = scout 251's
plus the discharge into the sea (sum of flow at river mouths, m3/s, mean over frames).
| run | inland median % (p10-p90) | lakes % of land | largest lake median Mkm2 | giant frames % (t >= 300) | to the sea, k m3/s |
|---|---|---|---|---|---|
| s1 main d0 / d1 | 7.3 (5.3-14.9) / 8.6 (4.8-14.9) | 0.67 / 0.59 | 0.12 / 0.09 | 1.5 (0) / 1.5 (0) | 2938 / 2912 |
| s1 B d0 / d1 | 10.7 (7.1-14.5) / 6.0 (2.3-14.5) | 0.61 / 0.81 | 0.12 / 0.19 | 6.0 (4.7) / 3.0 (0) | 2621 / 2845 |
| s77 main d0 / d1 | 12.3 (5.4-20.7) / 11.9 (2.3-20.7) | 1.47 / 0.92 | 0.87 / 0.19 | 46.3 (39.5) / 20.9 (0) | 2789 / 2826 |
| s77 B d0 / d1 | 15.3 (10.6-23.1) / 15.8 (7.6-23.1) | 1.20 / 1.28 | 0.21 / 0.51 | 22.4 (7.0) / 25.4 (11.6) | 2403 / 2531 |
- **Discharge to the sea falls 6-12%** (seed 1: -6.1% on the draw means, seed 77: -12.1%), more than on Earth
  (-4 to -6%): generated worlds have more wide flat lowland under big rivers. There is no observed global target
  for this at the model's resolution, so it cannot be judged good or bad yet.
- Inland: seed 77 +3.5 points in both draws (12.1 -> 15.6%; drier lowland rivers end sooner), seed 1 inside its
  draw spread (7.9 -> 8.4% mean of medians). Giant-lake frames, lakes %: inside main's draw-to-draw spread (seed 77
  main's own draws 20.9-46.3%). Run time: no difference visible under the machine's load (195-309 s per 200 Myr
  either code; the extra work is one numpy pass per lakes() call).
- Two seeds x two draws (the 1e-5 C draws share their first ~30-50 Myr): a screen, not proof.

## Recommendation
**Pass 2, not merge.** Candidate B is a sound mechanism (open-water evaporation over a flooded area set by the
flow and the slope, capped by what the river carries) and it does no harm to the inland, lake and giant-lake
measures, but at textbook parameters it reaches only a third of the way on the Sudd (0 to -17% against -47 to
-57%) and a tenth on the Okavango (-10% against -98%), while it takes 6-12% off generated worlds' discharge to
the sea with nothing yet to judge that by. Merging it now would be a partial fix (owner: no stopgaps). The code
on this branch is inert (`WETLAND_ET = False`; main's behaviour and goldens unchanged); the coordinator may
take only the docs and the draft.

Pass 2 (one try, then park if it misses): replace the flat sheet by **overbank spill above a channel capacity**:
alluvial channels carry about their mean flow at bankfull where they slope normally, and less on a very low
gradient (Q_bf ~ S^1/2 at fixed width and depth: the Bahr el Jebel's capacity falls far below its inflow through
the Sudd), so the spill = max(Q - Q_bf(S), 0) spreads over the flat plain and evaporates there, with the seasonal
pulse (`seasonal_flow`'s flood_ratio) adding spill in a flood month. Judge on Earth L7 with GPCC rain
(`earth_wet.py --obsrain`): Sudd reach -30% or more, Okavango to Maun -50% or more, Niger (with the dry-hollow
fix) Dire / Ke-Macina 0.5-0.75, and land runoff reaching the sea within 10% of main; then the same 2-seed fork
screen. The Niger draft (`draft-dry-hollow-closes-niger-delta.md`) should land first or together: with wetland
losses, the dry-catchment rule should read the water arriving, not the catchment's mean rain.

Not tried, noted: the ocean's fresh-water budget takes the land's runoff (`wb["runoff"]`), not the routed flow, so
wetland (and lake) evaporation is not removed from what reaches the sea there; small, but a merged B would want
the two to agree.
