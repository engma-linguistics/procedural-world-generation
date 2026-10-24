# v2-climate-1: PW-790, is the water world's outgassing decline too fast? (2026-10-24)

Branch `worktree-agent-a322772a3ede515e6`, from main 81918ba. A bounded check. Bar, thresholds and assertions are
unchanged, and **nothing under `planet/` changed**. The coordinator asked for analysis only partway through (the
owner wants a clean benchmark machine). The two L7 water-world runs (offsets +6 and +8) and three extra L6 draws
(+7, +7.001, +8.002) were stopped before they finished, so they give no numbers.

## Numbers first

**1. The hot mantle is not what makes the water world an icebox.** I split the CO2 source into its ridge and arc parts
(`srcdiag.py`, L6, star off, offset 0, 1200 Myr). Every row is a 100 Myr window mean.

| run | src 300 | src 700 | src 1000 | src 1000/300 | arc per trench cell, 300 -> 1000 | land 300 -> 1000 | dT 1000 |
|---|---|---|---|---|---|---|---|
| water world, heat_start 2 | 7452 | 5569 | 4941 | **0.66** | 0.18 -> 0.17 (per unit heat) | 13 -> 25% | -8.5 |
| water world, **heat_start 1** (control) | 4516 | 3584 | 2684 | **0.59** | 0.20 -> 0.14 | 13 -> 29% | **-8.5** |
| Earth-like B (seed 12), heat_start 1 | 3274 | 1997 | 2607 | 0.80 (0.61 at 700) | 0.19 -> 0.15 | 33 -> 33% | -0.1 |

- **With no hot mantle at all (heat_start 1), the same recipe is just as cold** at 1000 Myr (dT -8.5). Its
  source also falls by about the same factor (x0.59).
- The arcs carry about 96% of the source. Per trench cell and per unit of heat, their output falls by 20-30% over
  300-1000 Myr in every run, Earth-like included. Plates converge more slowly as the run ages, whatever the
  mantle's heat.
- The x0.35 (about 3x) that v1-finish-8 saw is one draw. Those runs differ only by climate_offset +-0.001, and the
  re-rolled draws give x0.43 / 0.64 / 0.60 / 0.86 / 0.58 over 300-1000 (`srcsum.py` on v1f8's json). This draw
  gives x0.66.
- Over 300-1000 the heat term alone should give x0.68: heat 1.707 -> 1.315 = x0.77, and the arcs scale with
  heat x convergence ~ heat^1.5. The rest is the plate slowdown that the heat_start-1 control shows too, plus chaos.

**2. What does make it cold: the sink reference is fixed while the land is still emerging.** From `relsum.py` on
v1f8's water-world runs:

| run | sink/ref at 100-300 Myr (refs still following) | after the 300 Myr freeze | src/ref at 1000 |
|---|---|---|---|
| water world, star off | 1.29-1.48 | 1.2-1.3 | 0.43 |
| water world, star 0.45 | 1.34-1.46 | 1.5-2.7 | 0.62 |
| Earth-like B | 0.96-1.06 | 1.0-1.3 | 1.00 |

The land grows from 8% to 13% before the freeze and to about 30% by 1 Gyr, so the sink keeps rising. The reference
follows it with an e-folding of about 100 Myr, and at the freeze it is about 30% below the actual sink. That is a
weathering surplus of about 1.3x, and the run carries it into its whole life as cooling. It comes on top of the
real draw-down from the land growing. The Earth-like runs have flat land, so their reference catches up. This is
the spin-up's design (PW-558/559 B): the reference is "the planet's balance once the made-up start has settled". On
a planet whose land is still emerging, that start has not settled by 300 Myr. Filed as a draft, not changed here.

**3. Recipe re-pick, measured (L6, 2 Gyr, code default star 0.45, two draws per offset; `passrate_ww_L6.txt`):**

| climate_offset | 300-2000 icehouse | 300-1000 | 1000-1500 | 1500-2000 | dT median, whole run | max dT | verdict |
|---|---|---|---|---|---|---|---|
| 0 (v1-finish-8, 3 draws) | 86-100% | | | | -4.2..-4.3 | | ICEBOX |
| +4 / +4.001 | 70 / 85% | 27 / 64 | 99 / 100 | 100 / 98 | -0.4 / -1.4 | 7.3 | F, icebox after 1 Gyr |
| +6 / +6.001 | 68 / 67% | 31 / 32 | 100 / 95 | 89 / 87 | +0.5 / +0.5 | 8.7 | F, icebox after 1 Gyr |
| **+8 / +8.001** | **22 / 3%** | 21 / 0 | 24 / 2 | 23 / 9 | +4.7 / +6.2 | 11.8 | **ok / ok (strict: ok / never-ice)** |

- Up to +6, the offset warms the first Gyr into the 5-40% band, but after 1 Gyr the run still ends up an icebox.
  The CO2 term grows from -6..-8 C (300-1000) to -12..-17 C (1500-2000), with the star at +7..+10. The
  thermostat works against the emerging land's sink and the frozen reference's surplus, and the offset doesn't
  change either.
- **+8 is the first offset with a living climate in every window.** Of its two draws, one has 22% icehouse and the
  other is nearly never-ice (3.3%). The hottest window median is +6.7 and the max is 11.8, both under the hellhole
  lines of 10.5 / 15.5. Those dT medians (+4.7 / +6.2) are what the Earth-like 2 Gyr runs show (+4..+8).
- **No L7 check:** both L7 runs were stopped at about 200 Myr. v1-finish-8 found that L7 runs about 1-2 C warmer than
  L6 at 2 Gyr, so +8 at L7 may lean ice-free. +7 is the obvious middle value, and it is untested.

## Literature comparison: is the heat decay too fast?

The model's `earth.heat(t) = 1 + (heat_start - 1) 0.5^(t / 600 Myr)`. With heat_start 2: 1.89 / 1.71 / 1.32 / 1.10
at 100 / 300 / 1000 / 2000 Myr. "Heat" scales plume numbers, arc melt (x heat) and plate speed (x heat^0.5), so the
arc source goes as about heat^1.5 and the ridge source as heat^0.5.

| quantity | model (heat_start 2) | literature |
|---|---|---|
| decay of the excess heat (half-life) | 600 Myr | Radiogenic heat production, from an Earth-like mix (U238 0.39, Th 0.40, K40 0.19, U235 0.02 of today's): the excess halves in about 0.85 Gyr from H = 2 and about 0.65 Gyr from H = 1.5. Heat flow lags production (Urey ratio about 0.2-0.4; Korenaga 2008), so it decays more slowly still. |
| heat 300 -> 1000 Myr | x0.77 | Krissansen-Totton et al. 2018: Q = (1 - t/4.5 Ga)^-n, n of 0-0.73. Over the same step at the fastest n (Q 1.71 -> 1.39), x0.81. Heat production over the same step: x0.80. |
| outgassing 300 -> 1000 Myr, from heat alone | x0.68 (heat^1.5) | outgassing ~ Q^m with m = 1-2 (Krissansen-Totton et al. 2018; spreading ~ Q^2 in Sleep & Zahnle 2001 and Franck et al. 1999): x0.66-0.82 |
| mantle cooling | (not modelled as Tp) | Tp falls about 50-100 K per Gyr since about 2.5-3 Ga (Herzberg, Condie & Korenaga 2010). If heat 2 is about +60-100 K (ridge melt roughly doubles per +100 K, McKenzie & Bickle 1988), then 2 -> 1.32 in 1 Gyr is about 40-70 K per Gyr. That is inside the range. |
| Phanerozoic outgassing | | Varies by tens of percent (GEOCARB's f_SR about 0.8-1.4; Berner 2004). On a near-steady mantle, this is configuration, not secular cooling. The model's heat_start-1 runs vary in the same way: x0.6-1.1 per 300-700 Myr. |

**Verdict: within range.** The 600 Myr half-life is at the fast end. It is about 10-30% faster than the radiogenic
excess, and faster again than a lagging heat flow. But its share of the 300-1000 Myr outgassing decline is x0.68,
inside the literature's x0.66-0.82. A half-life of 850 Myr (the radiogenic value) would make that step x0.73, a
difference of 7%. It would not change the water world, because the heat_start-1 control is just as cold. **I left
the physics alone.** Changing the heat decay would be a fudge aimed at the wrong mechanism.

## Proposal (not applied, for the coordinator)

Option A: re-pick the recipe as a preset change. The water-world preset's `climate_offset` goes from 0 to **+8**,
which is measured above at L6 as 2/2 pass (1/2 strict). It still needs an L7 check: 1-2 draws at L7 over 2 Gyr,
about 70-80 min each. +7 should be tried alongside in case +8 runs ice-free at L7. Five places change together:
- `planet/make.py` PRESETS["water-world"]["set"]
- `tests/test_make.py:22`, which asserts the preset's set: a test, not a threshold, so it moves with the preset
- `README.md:91`
- `docs/coordination.md:57`
- the blurb

I didn't make the change: the coordinator said analysis only, and the rule is no change without its L7 check.

Push-back on offset 8: it is a large made-up warming (the cold recipe is -6, the hothouse +3). It works because it
outweighs a frozen-reference artifact (section 2), which is the real fault. If that draft's fix lands, the water
world's needed offset should shrink, perhaps to about 0. So I would land the reference fix first, or take +8 now
and note it as temporary. The owner's no-temporary-fixes rule leans toward the first.

## Files

- `srcdiag.py`, `run_src.sh`, `decomp.py`: the source split into ridge and arc parts per step (harness only;
  monkeypatches `earth.global_temperature` to record, and doesn't change the run).
- `srcsum.py`, `relsum.py`: source / sink and their ratios to the reference per window, from ice_diag json.
- `launch_ww.sh`: water-world offset draws through `tools/ice_diag.py`.
- `passrate2.py`: v1-finish-8's per-window bar, copied unchanged. `passrate_ww_L6.txt`: the six runs.
- Raw outputs: session scratchpad `v2c1/` (ww_L6_*, ww_h1/ww_h2/eb.json).

No tests, scorecard or earth_check were run. Nothing under `planet/` changed.
