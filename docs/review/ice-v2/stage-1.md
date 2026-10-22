# Ice v2, stage 1: honest margins in the time zoom (PW-555)

2026-10-22, ice v2 lane (branch `worktree-agent-aa70af297efc2b900`, main 4f36c68, then main with PW-549
merged). **The run is untouched**: every change is in the time zoom, behind TZParams whose `'run'`/`'all'`/
`'edge'` values are the run's rules, used by `tests/test_timezoom_consistency.py` until stage 3. Scratch
(not committed): session scratchpad `icev2s1/` (`tzdiag.py` per-step budgets, `airprobe.py`, `grlprobe.py`,
`summ.py`, the job files and logs). Earth baseline: `checkpoint-0.md`, addendum.

## What changed (zoom only)
| TZParams | default (new) | the run's rule | what it is |
|---|---|---|---|
| `margin` | `ramp` | `edge` | a margin cell's balance over the sheet's Nye ramp across its iced share (`icemass.margin_ramp`, PW-460, from 246ef40) instead of its outermost 10 km (408 m) |
| `orbit_resp`, `insol_gain` | `seasons`, 1 | `run` (`INSOL_K` 0.25, `INSOL_SEA` 0.3) | each cell's orbit response from its own seasons (`icemass.seasonal_k`, PW-459, ~0.085 on high-latitude land) |
| `sheet_air` | `cold` | `all` | the sheets' carried air (PW-336) comes from the share of each ice cell's summer its surface stays frozen (`icemass.cold_share`, the PDD spread); a melting margin can't chill the air below it. `climate.compute(ice_cold=)`, `air_mass(cold=)`: default None = the run's, bit-identical |
| `surface_air`, `surface_km` | `fetch`, 500 | `all` | the ice surface's own effects (`ice_cool`, the local summer damping) act on the share of the air touching it that has come over ice for its last ~500 km (`icemass.surface_share`: ~a day's travel, the time a surface layer takes to adjust); air off the bare land or sea beside a margin or a small cap hasn't cooled to the ice's yet (attempt 3 below; replaced attempt 2's `rest`, `1 - air_mass`) |

Also: `finish.orbit_dt` builds a frame's orbit anomaly with the seasonal response; `tools/tz_earth.py`.

## How it was found (the diagnostics)
1. **Re-applied ramp + seasons** reproduce the PW-514 batch's zoom: Earth maxima −144..−178 m at 6.5 C,
   endings give back 0.41–0.74, interglacials keep 16.5–19.1% of land iced.
2. **Per-step budget of the NH ice** (`tzdiag.py`): with the ramp, margin cells are accumulation zones
   (mean +0.1 m/yr at a glacial maximum, −0.3..−0.5 with the edge); ablation is ~5% of accumulation and the
   sea takes the rest. Margin warm month −5 C (edge: −1..−2.6), at an ending only +0.4..+2.7 (edge +5..+7).
3. **Factor separation, Earth, 300 kyr** (first two glacials: max m, give-back, interglacial m):

   | variant | glacial 1 | glacial 2 |
   |---|---|---|
   | main (edge, run k) | −84, 0.87, −7 | −94, 0.64, +6 |
   | ramp + seasons | −145, 0.42, −70 | −169, 0.45, −52 |
   | ramp, run k | −135, 0.74, −26 | −149, 0.54, −3 |
   | edge, seasons | −100, 0.60, −27 | −123, 0.70, −12 |
   | **ramp + seasons, no carried air** | **−98, 0.82, −16** | **−123, 0.86, −7** |
   | iso_tau 1 / 6 kyr | −144, 0.39 / −144, 0.42 | no change |
   | calving ×3 | −122, 0.30, −73 | worse |
   | enhancement 9 (dynamic thinning) | −127, 0.48, −53 | small |
   | insol_gain 2 | −143, 0.55, −57 | −157, 0.60, −13 |

   **The cause is the carried sheet air on the margins** (PW-439), not isostatic lag, the front's outflow
   or dynamic thinning. The ramp margin's surface is 500–1100 m above its bed; the sheet's air takes another
   2.4–4.3 C off its summer (`airprobe.py`: the bare ground under North American margins +0.7 C with it,
   +5.0 without at a maximum; +4.8 / +7.2 at an interglacial). The old 408 m edge hid this by melting
   margins ~3 C too warm; the old 0.25 orbit gain hid it with a 3× summer kick.
4. **A check against a real margin, Greenland today** (`grlprobe.py`, the zoom's year with no anchor): the
   climate's own air over the ice is close to observed (warm month −3.0 C vs −4.2), but the ice rule on top
   takes it to −8.6 (margins −7.1 vs −2.1 observed: 5 C too cold). With neither `ice_cool` nor the local
   damping it is −3.2 (margins −2.0). Earth's `anchor=obs` only cools, so it never corrected this.

## Attempts on the lever (the carried air and the ice surface's air), per the stop rule
1. `sheet_air=cold` alone: Earth interglacial −70 → −65 m. Too small: the frozen interior makes most of the air.
2. **+ `surface_air=rest`** (kept): Greenland margins −7.1 → −6.1 C; Earth below. Endings work on Earth.
3. **`surface_air=fetch`** (kept; stage 1b, below): Greenland margins −6.1 → −3.9 C, inland −8.0 → −6.2, Antarctica
   +4.9 → +3.3 C too warm. A better ice-surface climate, but Earth's interglacial ice doesn't move (below). **The lever
   is spent (3 attempts).**

## Checkpoint 1 (stage-1 code, defaults)
Earth, L6, 600 kyr (`tools/tz_earth.py`):

| cooling | cycles | maxima m | give-back (bar ≥ 0.6) | interglacial ice % land (bar 9–12) | Laurentide | bars |
|---|---|---|---|---|---|---|
| 6.0 C | 98.5–108.5 | −120..−150 | 0.69–0.92 | 12.1–14.2 | 9.9 Mkm2 to 40.7 N | ig ice F |
| **5.5 C** | 98.5–108.5 | **−108..−138** | **0.64–0.91** | **11.9–14.7** | 9.5 to 41.5 N | ig ice F |
| 5.0 C | 98.5–108.5 | −93..−120 | 0.69–0.89 | 12.1–15.0 | 9.2 to 41.5 N | ig ice F |
| 5.5 C, `baseline=obs` | 93.5–113 | −69..−81 | 0.10–0.84 | 11.6–13.7 | 9.1 to 47.6 N | maxima, give-back, ig |
| main, 6.5 C (baseline) | 98.5–108.5 | −84..−104 | 0.65–0.89 | 9.1–11.9 | 8.2 to 42.5 N | cooling |

The moment suite (`tools/tz_mean.py`, 400 kyr; stage-0 moments from the pre-PW-549 main, re-picked below):

| moment | main (checkpoint 0) | ramp + seasons | stage 1 (defaults) |
|---|---|---|---|
| fixture L5 | −116 (tol 53) F | −253 F | −216 (tol 68) F |
| s2 @ 500 (deep) | +79 (29) F | −4 ok | **+9 (15) ok** |
| s1 @ 600 (deep) | +84 (26) F | +39 F | +49 (17) F |
| s5 @ 800 (moderate) | +33 (30) F | −23 F | **−7 (15) ok** |
| s3199 @ 800 (mild) | +11 (16) ok | −27 F | −22 (15) F |
| s21 @ 700 (warm) | −2 ok | −2 ok | −2 ok |
| **within tol** | **2/6** | 2/6 | **3/6** |

Deep moments deglaciate in the zoom (s2 swings 34 m, s5 60 m, s1 66 m, with 3–4 endings each). The
fixture's run ice (EDGE_H rule) is far below what honest margins hold (the zoom grows 216 m): a run-side
gap (stage 3), as PW-460 found.

**The suite re-picked on the new main** (PW-549 changes every run; runs and moments in scratch
`icev2s1/runs/`, L6 1 Gyr, moments every 40 Myr; mean after 100 kyr vs the run's ice, tol):

| moment (state) | run ice | main's zoom rules | stage 1 |
|---|---|---|---|
| s5 @ 420 (deep) | −468 m | +101 (40) F | +52 (15) F |
| s1 @ 780 (deep) | −326 m | +72 (36) F | **−2 (15) ok** |
| s2 @ 660 (moderate) | −140 m | +17 (15) F | **+9 (15) ok** |
| s3199 @ 900 (mild) | −93 m | +35 (22) F | **−10 (15) ok** |
| s21 @ 620 (warm) | −5 m | −2 ok | −3 ok |
| **within tol** | | **1/5** | **4/5** |

Every moment has 4 endings and no backstops. With stage 1 the deep moments start near the middle of their
range (15th–100th pct) instead of always at the glacial edge, and the zoom's swings are 12–58 m.

**Failing test:** `test_timezoom_cycle::test_glacials_grow_ice_and_endings_melt_it_fast` (L4, ~440 km
cells): the first ending keeps 25 of 29 m (bar < 50%). At L4 a margin cell's ramp is 1.2–2.6 km high. The
same moment deglaciates with the edge (0.67) or with no carried air (0.60). Not loosened; see the handoff.

**Stage 1 doesn't pass yet:** Earth meets cycles, maxima, give-back and cooling at 5.5 C (≤ 6 C), the deep
moments deglaciate and the window mean improves (old moments 2/6 → 3/6; new-main moments 1/5 → 4/5), but Earth's interglacials keep 12–15% of land
iced (bar 9–12) and the L4 ending test fails. Not ready to merge.

## Stage 1b (2026-10-22, branch `worktree-agent-a059022acff222eac`, main 1f0fae4 merged)
Scratch: session scratchpad `icev2s1b/` (`termprobe.py` the ice-surface terms one by one on Earth today,
`fetchprobe.py` the iced share by kernel, `marobs.py` the observed margin split into its ice and bare parts,
`endtest.py` the L4 test on any source and any TZParams, `mk_src.py`, `quadprobe.py`, `igprobe.py` / `igana.py` /
`igfinal.py` / `igwhere.py` where the interglacial ice sits, the job files and logs).

### Attempt 3 on the lever: the ice surface's air by its fetch over ice (`surface_air=fetch`, kept)
Earth today, the zoom's year with no anchor (`termprobe.py`). Greenland's ice-surface warm month, by term:

| | margin (obs −2.1; its ice part ~−2.7) | inland (obs −4.9) | Antarctica (obs −14.9) |
|---|---|---|---|
| climate's own air, no local terms | −1.9 | −3.6 | −7.8 |
| `rest` (attempt 2) | −6.1 | −8.0 | −10.0 |
| of which the summer damping | 2.8 C | 3.0 C | 1.3 C |
| of which `ice_cool` | 1.3 C | 1.5 C | 0.8 C |
| **`fetch`, 500 km** | **−3.9** | **−6.2** | **−11.6** |
| `fetch`, 300 km | −4.5 | −7.4 | −12.1 |

Under `rest` Greenland got 0.80 of the local terms and Antarctica 0.43: backwards (its carried air is small on
Greenland, 0.2, and large on Antarctica, 0.57). The iced share within 500 km is Greenland's margins 0.37, inland
0.47, Antarctica's interior 0.75. The observed margin value is the cell's mean over its ice and its bare part
(`marobs.py`: iced share 0.72, bare neighbours −0.6, so the ice part is ~−2.7 C): `fetch` is ~1.2 C too cold there,
1.3 C inland, Antarctica +3.3 (its base bias, PW-039). This meets the Greenland draft's first check.

### Checkpoint 1b (defaults: ramp, seasons, cold, fetch)
Earth, L6, 600 kyr (`tools/tz_earth.py`):

| cooling | maxima m | give-back (≥ 0.6) | interglacial ice % land (9–12) | Laurentide | bars failing |
|---|---|---|---|---|---|
| 6.0 C | −107..−129 | 0.57–0.80 | 12.2–15.7 | 9.5 Mkm2 to 41.5 N | give-back, ig |
| **5.5 C** | **−89..−118** | **0.62–0.82** | **11.8–15.5** | 9.2 to 41.5 N | **ig** |
| 5.0 C | −77..−103 | 0.58–0.84 | 12.0–14.0 | 8.5 to 41.8 N | maxima, give-back, ig |
| 5.5 C setting, `baseline=obs` (4.7 C) | −52..−69 | 0.23–0.85 | 11.4–12.6 | 8.1 to 47.7 N | maxima, give-back, ig |
| 6.0 C setting, `baseline=obs` (5.1 C) | −57..−77 | 0.25–0.75 | 11.5–12.9 | 8.9 to 47.7 N | maxima, give-back, ig |

Cycles 98.5–108.5 kyr everywhere (obs 93.5–113), no backstops.

The moment suite (`tools/tz_mean.py`, 400 kyr; mean after 100 kyr vs the run's ice, tol; area ratio, bar 25%):

| moment | run ice | stage 1 (`rest`) | **stage 1b (`fetch`)** |
|---|---|---|---|
| s5 @ 420 (deep) | −468 m | +52 (15) F, area 1.01 | +69 (19) F, area 0.96 |
| s1 @ 780 (deep) | −326 m | −2 ok, 1.06 | +2 ok, 1.05 |
| s2 @ 660 (moderate) | −140 m | +9 ok, 0.98 | +14 ok, 0.94 |
| s3199 @ 900 (mild) | −93 m | −10 ok, **1.27 F** | −2 ok, 1.15 |
| s21 @ 620 (warm) | −5 m | −3 ok, **1.34 F** | −2 ok, **1.27 F** |
| mean within tol | | 4/5 | 4/5 |
| mean and area | | 2/5 | 3/5 |

The criteria's bar is ≥ 5 of 7 moments with both; the re-picked suite has 5 (no fixture on the new main yet).
s5 @ 420 is the run's deepest state (−468 m) and the zoom gives back 69 m of it in every ending: the run holds more
ice there than honest margins keep (a run-side gap, stage 3).

### The interglacial ice isn't a deglaciation failure: Earth at dT 0 doesn't hold today's ice
Where the interglacial ice beyond today's sits (`igprobe.py`, 5.5 C, at each interglacial's highest sea level,
−12..−31 m): 3.9–10.2 Mkm2, of which Greenland's coast and shelf 1.1–1.3 (half marine-grounded, 1.2–2.0 km thick;
Iceland and Baffin too), Antarctic marine ice 0.5–0.9, North America 1.3–4.2 (the Laurentide's last ~1 km domes),
Eurasia 0.7–3.8. Greenland's and Antarctica's share is the same at every interglacial.

The same zoom with **the index off** (today's climate, only the orbit swinging; `igfinal.py`, Mkm2 of ice, today 14.1):

| | t 2 kyr (Eemian-like summer) | 14 (weak summer) | 46 (strong again) | 200 |
|---|---|---|---|---|
| stage 1b | 14.6 | 18.3 (12.5% of land) | 16.9 (11.5%) | 18.6 (12.6%) |
| stage 1b, `baseline=obs` | | 16.5 (t 20) | 17.2 (t 100) | 17.6 (12.0%) |
| stage 1b, `anchor=none` / `anchor_rings=0` | 14.1 / 14.5 | 17.7 / 18.3 | 16.8 / 17.0 | |
| main's zoom rules (edge, run k, all, all) | 12.7 | 18.9 | **13.9 (9.5%)** | |
| `surface_air=all` (the run's local terms) | | 19.2 (t 20) | 20.1 (t 100) | 21.5 (14.6%) |

With main's rules the ice comes and goes with the orbit at dT 0. With honest margins it grows in the first weak summer
(+0.9 Mkm2 within 2 kyr even under an Eemian-like orbit: Greenland 0.4, North America 0.25) and the next strong
summer doesn't take it back: a precession-scale hysteresis at today's climate. That fixed point, ~11.5–12.6% of land,
is the floor every interglacial lands on, so no deglaciation lever can bring the interglacials to 9–12%.
The extra at dT 0 (t 46): the Canadian Arctic islands (~0.8 Mkm2, observed warm month +1..+2 C at 300 m; real ice
caps cover a fraction of that), Greenland's coastal strip and shelf (~1.0), Alaska and the Coast Mountains, the
Andes and Tibet (~0.5), Scandinavia (0.2 at an observed July +10 C: the base bias, gone with `baseline=obs`).
The start anchor isn't the cause. It is the criteria's recovery bar (today's ice held at dT 0 within 20% of its area):
+20..+32% on stage 1b, fails.

### The base climate (review root cause 5) as the next lever: attempt 1, the decisive form
`baseline=obs` takes every regional bias out on Earth (the delta method), the strongest form this lever can take.
Interglacial ice 11.4–12.9% (better, still failing), and the zoom loses its depth (maxima −52..−77 m at 4.7–5.1 C) and
its give-back (0.23–0.85). The bias explains Scandinavia and part of the Eurasian and North American remnants, not
the dT-0 floor. A partial bias fix can't pass the bar where the full one doesn't, so the lever is not taken further;
the next suspect is below.

### Next suspect: the margin balance at today's climate
On Greenland's margin cells the zoom's balance is +0.20 m/yr (`termprobe.py`, `fetch`), and its sheet spreads onto
its coastal strip and shelf at an Eemian orbit. An ablation zone ~50–150 km wide should make a 110 km margin strip's
mean balance about nil or negative. Suspects, to be measured against an observed surface mass balance (none is in
the repository's Earth data): the ramp's lower point at 0.21 of the iced width (~620 m at L6) never samples the
outer edge; the front rule makes bare land a bright new edge 408 m high; the degree-day factors. This is a new lever,
so it is the owner's call under the stop rule (draft).

### The L4 endings test: not a resolution limit
`tests/test_timezoom_cycle.py::test_glacials_grow_ice_and_endings_melt_it_fast` on the new main (`endtest.py`
reproduces it exactly: extra 60.7 m, left 62.5). The share of the glacial's extra ice left after 15 kyr (bar < 0.5):

| rules | L4 (sim4, ~440 km cells) | L5 (same recipe, seed 1, ~220 km) |
|---|---|---|
| stage 1b (`fetch`) | 1.03 F | 0.83 F |
| stage 1 (`rest`) | 0.98 F | 0.81 F |
| stage 1b with `margin=edge` | 0.36 ok | |
| main's zoom rules | not run | 0.46 ok |

It fails at L5 with the same bar too, by nearly as much. The quadrature of the ramp isn't it either (`quadprobe.py`:
the two-point mean against the exact mean over the ramp: within 0.03–0.18 m/yr at L4, 0.04–0.12 at L5, 0.02–0.09
at L6). The honest margin holds this planet's ice at any of these resolutions, the same thing as Earth's dT-0
floor. Moving the test to L5 wouldn't make it pass; it stays at L4, unchanged and failing.

### Stage 1 status
Not passing: Earth meets cycles, maxima, give-back and cooling at 5.5 C; the interglacial ice (11.8–15.5%), the
window mean with area (3/5), the L4 test and the recovery bar fail. Both stop rules have been hit (the air lever
after 3 attempts, the base climate on its decisive form). Not ready to merge.
