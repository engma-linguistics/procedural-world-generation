# PW-440 handoff: the ice-age cycle in the time zoom (2026-10-20, agent pw440)

**Outcome: the agreed three-mode cycle is built and on by default (`planet/timezoom/cycle.py`); PW-030's
v1 target is not met.** It gives a cold run moment ~100-kyr pacing instead of a rigid cold branch, and
leaves Earth and the between-ice-ages behaviour unchanged, but its endings are slow and partial, Earth's
glacials are too shallow to reach an ending, and run moments still drift far from their start. Five
attempts (stop rule reached).

## What the cycle does
- Modes: between ice ages (bit-identical to `cycle=off`; tested), building (summer sun at the cycling
  latitude below its 40th percentile, with extra ice; only the glacial's clock runs), ending.
- Ending starts: extra ice >= 0.4 x the sheet scale AND summer sun >= a bar falling from the 95th to the
  60th percentile of the planet's own 800-kyr series over 100 kyr (Huybers). Sheet scale = sea-level
  equivalent of 2 km of ice over 10% of the planet's land (Earth 72 m; L6 test runs 82-93 m).
  Cycling latitude = where the extra ice first grows (once it passes 0.1 x scale).
- Inside an ending (ramping in over 3 kyr; only beyond the last interglacial's ice footprint): degree-day
  melt x (1 + 0.8 tanh(extra / scale)) (`kernels.climate_melt`; `climate_step` is it with 1s, so icemass is
  untouched), marine calving x up to 2, CO2 release up to 0.9 x `co2_cool` on top of the volume's CO2,
  at most the extra ice's own drawdown from the interglacial level, not clipped.
- Ends when extra ice < 0.1 x scale (hysteresis); or, if the melt-back stalls (no new low by 2 m for a
  precession period), the next glacial builds from there (judgement call, see draft).
- Backstop: a glacial older than 200 kyr ends at the next sunshine peak; counted in `res["cycle"]`, meta
  `ice_age_cycle`, and run.txt.

## Numbers (L6, 600 kyr, in memory; moments as PW-030's handoff; scripts in the session scratchpad `pw440/`)
| source | swing m | mean m | cycles (swings m) | builds / terms kyr (30 m zig-zag) | 100-kyr power | IG ice % land | endings (kyr) | backstops |
|---|---|---|---|---|---|---|---|---|
| Earth, before | 48 | -14 | 42, 42, 47, 44 | 101, 57, 13 / 105, 33, 104 | 0.08 | 8.4-9.2 | - | - |
| Earth, cycle | 48 | -12 | 43, 36, 47, 32 | 101, 57, 13, 103 / 105, 32, 104 | 0.06 | 8.4-9.2 | 17 (backstop), 43 (stalled) | 1 |
| s400 (seed 11 @ 400), before | 163 | -141 | one build, then a flat cold branch | 123 / - | 0.07 | 10 then 21 | - | - |
| s400, cycle | 147 | -89 | 104, 70, 56, 91, 32, 30, 55 | 52-62 / 16-60 | 0.33 | 10-19 | 6, 31-74 kyr, all stalled with 20-112 m left | 0 |
| seed 2 @ 620, before | 177 | +122 | 35-76 | 9-60 / 17-48 | 0.09 | 11-15 | - | - |
| seed 2 @ 620, cycle | 185 | +137 | 35-71 | 9-63 / 17-62 | 0.22 | 10-13 | 6, 16-42 kyr (3 stalled) | 0 |
| s580 (seed 2 @ 580) | 225 either way: warm drift, no glacial, no ending | | | | | | | |
L4 (tests' sim4, 8 C colder, 240 kyr): endings give back 3.6 and 5.3 m more than the same sunshine
peaks without the cycle over 20 kyr (the test guards > 2 m on average).

Against the done list: (1) swing >= 80 m: single cycles reach 91-104 m on s400, most are 30-70 m; Earth
48 m. (2) builds 52-62 kyr on s400, but endings 30-75 kyr, not ~10. (3) Earth interglacial ice unchanged
(8.4-9.2% of land), glacial maximum unchanged (16.5-19% of land). (4) not met: run moments drift
(s400 mean -89 m; seed 2 @ 620 +137 m; seed 11 @ 260/280/300 +103..+238 m, all in 400 kyr). (5) the
unforced start test passes. (6) pytest green. Backstop: 1 firing in 600 kyr on Earth (its glacials stay
under the ending's extra-ice bar), 0 elsewhere: not the knob that is wrong.

## Attempts
1. Orbital response x up to 1.8 on positive summer anomalies of the extra ice (k_orb): s400's first ending
   (44 kyr, 102 m of extra ice) never finished (sea level -50..-115 m for 550 kyr, "ending" all along).
2. Degree-day melt x up to 1.8 instead: the same. Diagnosis (`where.py`): 51 of s400's 52 m of remaining
   extra ice at 150 kyr is a new 70-80 N sheet with -11 C summers on its surface: it cannot melt.
3. A stalled ending sets the interglacial level to what is left: ratchets the drift (s400 mean -117 m in
   400 kyr, interglacial level -133 m). Reverted.
4. A stalled ending hands over to the next build (kept): s400 gets ~100-kyr cycles (power 0.40).
   Seed 2 @ 620 showed no change at all: its CO2 sat at the warm clip (the moment had lost 100+ m of ice,
   so the release had no headroom) and its cycling ice lay inside the start's footprint (no boost).
5. Footprint = the last interglacial's grounded ice (not the start's), and the CO2 release capped by the
   extra ice's own drawdown instead of the interglacial CO2 level (kept): seed 2 @ 620 100-kyr power
   0.09 -> 0.22; s400 0.33.

## Why the target doesn't land (blockers)
- **Drift (PW-436)** dominates every run moment tried: most lose 100-350 m of ice in the first 50 kyr
  (rectification plus the feedbacks, PW-030's table), s400 grows a polar sheet the run doesn't have.
  The cycle's between-ice-ages rule (all as before) leaves that untouched; criterion 4 needs PW-436.
- **Earth's glacials are 30-45 m** (PW-435): the ending's 29 m bar is barely reached; the cycle can't
  make the 80 m swing there by design (building changes nothing).
- **Endings at the agreed strength are weak** where the extra ice is cold: draft
  `draft-timezoom-ending-strength.md` (needs-decision).

## Also found
- The mantle basis cache (`planet/tectonics/__pycache__/mantle_basis_*.npy`) built during a full pytest
  run differed from a fresh build by up to 0.063, and the L5 envelope test then failed (mean plate speed
  1.91 cm/yr). Draft `draft-mantle-basis-cache-not-reproducible.md`.

## Showcases (real store)
Time zooms (600 kyr, L6, default knobs): Earth `755514`, s400 `7d5027`, seed 2 @ 620 Myr `be3362` (their source runs 82fc14 and 27ea70 live in the PW-030 scratch store, not the real one).
