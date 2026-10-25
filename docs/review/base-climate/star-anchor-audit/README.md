# Star-anchor audit: what assumes "start at the present Sun and brighten forward" (2026-10-24)

Read-only audit lane; no code changed, nothing simulated. Branch from main 005ede8.

The ruling (owner, 2026-10-24; decisions.md, PW-791): **a run's end is "now"**. A run of length T spans the star
ages 4570 − T to 4570 Myr, and plant groups arrive on Earth's calendar counted back from the end (PW-807). Until now
`earth.star_forcing` started the star's clock at age `star_age` = 0, ran it at `star_brightening` = 0.45 × Gough's
rate, and measured the forcing from the run's start. The climate model's dT = 0 is today's Earth with today's Sun.
So every run has started from a present-Sun climate and brightened into the future.

Dates: the star came in at 9852149 (v1-finish-7, PW-761/564) and the hothouse change at 1fa0aeb (v1-finish-8). The
sign-off was 5575985 (v1-signoff, PW-780). All three are 2026-10-24.

## Ranked findings

Risk = how likely the item breaks or misleads once the anchor lands, times how much rides on it.

| # | Item (where) | What it assumes | Kludge or physics? | After the anchor | Risk |
|---|---|---|---|---|---|
| 1 | **Forcing zero point vs the spin-up reference**: `earth.star_forcing` (planet/tectonics/earth.py:50-60, used at :202); refs follow the rates while t < `REF_FREEZE` (:157-160) | Forcing is 0 at t = 0, where the climate's dT = 0 / PCO2_BALANCE calibration (present Sun) applies. The reference learns whatever star the spin-up has and does not push back against it. | Structural assumption (9852149) | **Re-derive.** If the end is zero, a 1 Gyr run spins up at −7.3 C (0.45) or −15.5 C (full Gough) against now. The frozen reference treats that as the balance, so the CO2 never compensates the dim start. If the start stays zero, "now" is not dT = 0 at the end. You have to pick one, and the choice decides every number below. | **Very high** |
| 2 | **`PCO2_BALANCE` 500 ppm** (planet/climate.py:49; 378a927, 2026-10-23, before the star) | The settled carbon cycle rests half a doubling above today's (+1.5 C). It was picked on icehouse share: 45% at today's pCO2, 19% at 500, 0% at 700. Present Sun, no brightening. | **Calibration knob** against the late cooling trend (PW-559 B, PW-708 option C), now stacked with the star, which does the same job | **Re-check.** Under the anchor, the balance holds at a dimmer star, and the post-freeze brightening draws pCO2 below it by the run's end. That is how the old star produced the 87-244 ppm slices (PW-806). Re-derive it so that a present-Sun end lands in Earth's plausible pCO2 range, or measure it and justify it. | **High** |
| 3 | **`star_brightening` 0.45** (planet/tectonics/params.py:81-85) | It is a multiple of Gough's rate from age 0. It was the only rate that flattened the L6 late trend (16/18; the sd of 18 draws can't separate 0.2-0.45). | **Kludge, by its own write-up**: "a chosen star", the owner's lever. It cancels PW-708's late weatherability cooling without the Sun-like overshoot. | **Re-pick.** Near the present age Gough's curve is steeper. At 0.45, anchored: +7.6 C raw over a 1 Gyr run (old +5.6), +15.2 over 2 Gyr (old +11.5). At full Gough, which is the owner's anchor wording: +16.9 C over 1 Gyr, against the old 1.0's +12.8, which already gave 16/18 never-ice. The two 2026-10-24 rulings ("0.45 ok" and "full Gough unless evidence") conflict. | **High** |
| 4 | **Pass-rate evidence and the v1 bar's numbers**: L6 13/18 strict, L7 7/8, the 2 Gyr 1500-2000 window 4/13, the never-ice tallies (PW-780, v1-finish-7/8, v1-signoff, decisions.md:14-15, :23) | All measured on the old star. The windows count forward from the start (300-1000, early/late 300-500 / 600-1000, 1000-1500 / 1500-2000). The 1500-2000 window was there to catch the future-Sun drift. | Measurements (the harness is sound; the bar is the owner's) | **Re-measure everything** on the anchored star. Keep the bar and its thresholds. Under the anchor a run's last ~540 Myr is the Phanerozoic analogue. Add an end-counted window (last 540 Myr) as a reported diagnostic; that is a harness change, not a threshold. | **High** (v1 sign-off rides on it) |
| 5 | **PW-806's diagnosis** (treeless star-warmed worlds; v1-signoff `pco2dist.py`, `wetbelt.py`) | The +4 to +5.4 C slices and the low-pCO2 shares (300-1000: 3-31% below 180 ppm; 1000-2000: 23-82%) come from the old star and the thermostat's draw-down. | Measurement of a real interaction | **Keep the offline, literature-based plant recalibration**: Holocene 280 ppm, LGM, Eocene on Earth's own climate don't depend on the star. **Re-measure the showcase acceptance** ("L7 wet tropics carry forest") after the anchor, and don't tune plants to old-star slices. | **High** (v1 blocker) |
| 6 | **Flora compression**: `FLORA_PACE` 0.8, the `GROUPS` fractions, `group_windows`' deadline D = end − max(16, 5%) (planet/vegetation.py:222-286); `FLORA_END` 1000 (earth.py:267); `plants_from` 0 (params.py:96) | Land plants from t = 0; Earth's ~470 Myr sequence stretched to the run and compressed by 0.8 (a99cd2c, 2026-10-23, PW-636) | **Kludge** (an owner-approved compression) | **Remove** for PW-807. Knock-on: runs longer than ~470 Myr get bare continents first, with weaker weathering (`plants` factor 1.0 against up to 1.75) and erosion 1.6× faster. For runs over ~770 Myr the reference then freezes on bare land, and the plants' arrival is a lasting weathering surplus (cooling). Re-check the CO2 calibration together with #1/#2. | **High** (PW-807 scope) |
| 7 | **`representative_time` / `slice --at auto`** (planet/highlights.py:2685-2780; make.py:250) | It picks after 300 Myr, then limits to frames after the last group arrives. Under the compression that is the last third of the run. | Heuristic (03d7439, 2026-10-14; PW-634; PW-700) | **Re-check.** On the real calendar, C4 grasses arrive at ~30-8 Ma, which leaves 2-7 keyframes (one every 4 Myr). The geographic-typicality medians and PW-700's "warm moment of the icehouse era" then mostly degenerate to "the last frame". PW-807 already puts the owner question. | **Med-high** |
| 8 | **Hothouse preset `climate_offset` 5 → 3** (planet/make.py:65; README.md:92; docs/coordination.md:60; 1fa0aeb) | At 5 the old star's late warming crossed the hellhole line (+12.9 / +10.9 C median) | **Compensation** for the old star, by its own commit message | **Re-pick** after the anchor. Its old +5 at star-off gave +9.6. | Med |
| 9 | **Cold preset −6** (make.py:63) and **water-world +8** (PW-799, v2-climate-1) | Cold: kept on the old star, 3 C less cold than star-off. Water world: +8 measured at 0.45 from age 0, on top of PW-798's frozen-reference surplus (sink/ref 1.5-2.7 with the star on, 1.2-1.3 off). | Cold is a recipe choice. +8 is a compensation (PW-798 lean A should remove it). | **Re-check** the cold recipe. Water world: do PW-798 A first, then the anchor, then re-measure from offset 0. **Do not land +8** on the old star's numbers. | Med |
| 10 | **No run length in `Simulation`**: tests/helpers.py:8, tools/scorecard.py:60 and tools/ice_diag.py:56 pass `flora_end=myr`. tools/sealevel.py:67, tools/supercontinent.py:91 and ~20 tests use `Params()`, which falls back to `FLORA_END` 1000. | The sim doesn't need its end: the star counts from t = 0, and flora's fallback is "a 1000 Myr run". | Plumbing | **Re-check.** An end-anchored star needs the end. Use one run-end parameter for both star and flora, set it in every direct `Simulation` caller and store it in run meta so slices replay. The goldens change on purpose (`--update-golden`). | Med |
| 11 | **Run length bounds**: make.py:113 allows up to 4000 Myr; `simulate --myr` has no bound (planet/__main__.py:502). PW-557 (extend a run 2 → 4 Gyr). | Any length works, because the star starts young. | Plumbing | **Re-check.** T > 4570 gives a negative star age; guard it. At 4 Gyr a full-Gough start is −50 C raw against now (−26 at 0.45). The owner wants such runs habitable, which is PW-791's thermostat job. Extending a run must keep the original anchor (the extension is the "future offset"), not re-anchor its past. | Med |
| 12 | **`star_age`** (params.py:86) | "The planet is as young as its star" at the start | Parameter that the anchor supersedes. v1-finish-8 showed it can't serve as a lever ("an older star brightens faster"). | **Remove** (no backward compatibility). Replace it with the anchor plus the ruled optional future offset. | Low |
| 13 | **`REF_FREEZE` 300 / `REF_MYR` 100** (earth.py:31-35; b35b490, 2026-10-22, before the star) | The made-up start settles by 300 Myr; the reference is that balance | Bookkeeping choice (PW-558/559 B, PW-576), not star-tuned | **Keep the design**, and fold its star interaction into #1. Anchored, the star brightens +2.2 C (0.45) to +4.8 C (full) raw during the spin-up, and the reference absorbs it. PW-798 A (freeze once the land settles) still applies; under PW-807 add "once plants exist"? See #6. | Med (via #1) |
| 14 | **Docs that describe the old star**: params.py:81-86 comment ("counted against the run's start", "a Sun-like 1.0 warms 1 Gyr runs ice-free"); PW-789's proposed help text ("1.0 ... melts out all ice within ~1 Gyr"); make.py:88 `UNSUPPORTED` "star brightness"; coordination.md:60; the overview has **no star section at all** | Old semantics | Docs | **Rewrite** when the anchor lands: an overview climate subsection, the params comment and PW-789's text | Low |
| 15 | **`heat_start` 1 / `heat_halflife` 600** (params.py:124-127; 6caf626, 2026-10-13) | The mantle heat is relative to the run's start, fading in ~600 Myr. Default 1: today's mantle from the start. | Physical choice, independent of the star | **Keep for v1.** Under the anchor a 2-4 Gyr run starts on a 2.5-0.6 Gyr-old planet whose mantle would have been hotter. Later option: derive heat_start from the planet's age at the start. The water world's 2 fits ~2.5 Ga. | Low |

Checked and **not** tied to the star (keep):
- `climate_drift` 3 C / 40 Myr (d7f2036, 2026-10-13; PW-761 B' measured that 2 C doesn't help).
- PW-471's glacial index: the time zoom covers 1 Myr with the run's feedbacks off, and its `glacial_cool` is planet-relative.
- `EARTH_ICE` and `earth_check`/`earth_world` at dT 0 and PCO2_REF 350. These become *more* consistent: the anchored end is the present Sun.
- `orbit.S0` 1361 W/m2. It is a fixed insolation pattern, with the star entering only as a global dT; that is consistent with the end being now.
- `ice_criteria`'s SPINUP 300, HOT 8 C, and the hellhole lines 10.5 / 15.5 C. These are absolute or start-up windows.
- test_ice_diag's `star` term identity and test_co2_stock: structural.

## Notes

**1-2: the zero point is the real decision; the 0.45 follows from it.** Today, three things share one moment: the
climate's dT = 0 (Earth now), the CO2 balance (500 ppm, learnt over 0-300 Myr and then frozen) and the star (forcing
0 at t = 0). The anchor moves the star's "now" to the end, but the other two stay at the start. The spin-up's
reference follows the sink, so a dimmer start is learnt as normal, and the thermostat only answers brightening after
300 Myr (realised ~0.77 passed, CO2 term −0.40 C per C; v1-finish-7). Worked example, 1 Gyr at full Gough with the
end as zero, before any ice-albedo feedback:
- The run starts at −15.5 + 1.5 (the balance's CO2 term) ≈ −14 C.
- During the spin-up it warms by the star's raw +4.8 C uncompensated, because the reference learns it. So it is at
  ≈ −9 C at the freeze.
- After the freeze it warms by ~0.77 × 12.1 C, and ends near dT 0 with pCO2 ≈ 500 × 2^(−0.40 × 12.1 / 3) ≈ 165 ppm.

So it is an icy first half, with PW-806's CO2 starvation still at the end. Ice albedo would make the start colder
still. Physically, the
dim start should be met by *high* CO2, which is the real faint-young-Sun answer. In this model that means the
balance has to be set for the start's star, for example a PCO2_BALANCE derived so that the end (present Sun) sits
near Earth's range. A per-preset offset would not do it. The physics lane should choose this explicitly, not
inherit it.

Forcing numbers (the model's 0.81 C per W/m2 × 238 W/m2, raw before the thermostat; computed offline from earth.py's formula):

| T | old 0.45 rise | anchored 0.45 rise / start vs end | old 1.0 rise | anchored 1.0 rise / start vs end (L0) |
|---|---|---|---|---|
| 500 Myr | +2.7 | +3.8 / −3.7 | +6.2 | +8.4 / −8.1 (0.958) |
| 1 Gyr | +5.6 | +7.6 / −7.3 | +12.8 | +16.9 / −15.5 (0.920) |
| 2 Gyr | +11.5 | +15.2 / −14.1 | +27.5 | +33.7 / −28.7 (0.851) |
| 4 Gyr | +24.4 | +30.3 / −26.2 | +64.2 | +67.4 / −49.9 (0.741) |

The trend at the run's end is +0.79 C per 100 Myr anchored against +0.57 old at 0.45; at full Gough it is +1.83
against +1.37.

**3: the 0.45 is a compensation for a model trend, not a star property.** PW-761's base had icehouse 24% early and
57% late: PW-708's rising weatherability (relief, flora) against the frozen reference. The star was brought in to
cancel that trend. It was picked on pass rate, and Gough's rate is 3-4× too strong for the model's thermostat
(v1-finish-7 section 1). With the anchor, both the trend it must cancel and the forcing curve change. The trend
changes because PW-807 moves plants and their weathering factor late, and the reference may freeze on bare land. The
curve changes because it gets steeper near the present age. Both rulings should go back to the owner with numbers:
"0.45 ok" (provisional, phone) and the anchor's "full Gough unless evidence". PW-791's thermostat lands "only if the
anchored star still leaves runaway worlds", so measure the anchored star alone first.

**4-5: re-measure before acting on old-star conclusions.** Every pass rate since 9852149, the never-ice tallies, the
L7 late-warm lean (PW-789) and PW-806's showcase diagnosis are old-star numbers. PW-806's offline tests on Earth's
climate (280 ppm keeps ~80% of trees; warm tropics forested) are star-independent and stand. Its showcase criterion
does not. The v1 showcase (PW-202 ids in state.md) was made on the old star and needs a remake after the anchor and
PW-807 (outputs are freely deletable).

**6-7: PW-807 and the CO2 calibration are coupled.** The bare-land spin-up plus the reference freeze means that on a
1 Gyr run the reference is learnt on bare land (plants arrive at ~530 Myr), and the plants' arrival then draws CO2
down. The direction is right (the Devonian drawdown), but its size, together with #1's dim start, is unmeasured.
`--at auto`'s gate needs a rule for runs whose full flora exists only in the last ~10-30 Myr. One option: allow
frames once flowering trees exist (~100 Ma), not C4 grasses, as the owner's question in PW-807 suggests.

**8-9: recipe offsets.** The hothouse 5 → 3 is a direct old-star compensation. The water world's +8 is two stacked
compensations: PW-798's surplus and the old star. Re-pick both from offset 0 after the anchor; PW-798 A comes first
for the water world.

**10-11: plumbing.** `flora_end` already shows the pattern: `timeline.simulate` sets it, and some direct callers
forget it. The anchor needs the same thing. One field for both avoids two fallbacks that disagree.

## Inbox drafts filed

- `draft-star-anchor-zero-point-co2-balance.md`: #1, #2, #13 (relates PW-791)
- `draft-star-rate-after-anchor.md`: #3, #12 (relates PW-791, PW-780)
- `draft-remeasure-v1-bar-on-anchored-star.md`: #4, #5 (relates PW-791, PW-806)
- `draft-recipe-offsets-after-anchor.md`: #8, #9 (relates PW-791, PW-799, PW-798)
- `draft-run-end-param-star-and-flora.md`: #10, #11 (relates PW-791, PW-807, PW-557)
- `draft-flora-calendar-co2-and-auto-slice.md`: #6, #7 (relates PW-807)
- `draft-star-docs-after-anchor.md`: #14 (relates PW-791, PW-789)
