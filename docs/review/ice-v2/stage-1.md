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
| `surface_air` | `rest` | `all` | the ice surface's own effects (`ice_cool`, the local summer damping) act on the share of the air that isn't the sheets' carried air already (`1 - air_mass`), so a big sheet's cooling isn't counted twice |

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
3. Not yet tried (next): see the handoff.

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
