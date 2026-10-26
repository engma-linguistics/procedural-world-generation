# v1-finish-12: the PW-865 bar (no icehouse cap), thermostat off; the plants' light (2026-10-25)

Status: **handed off mid-measurement.** Harness on the ruled bar committed. The thermostat-off draws on
v1-finish-11's physics re-tallied (10 of the L6 set). One physics change committed (the plants' light, section 2),
so the full set (L6 18, L6 2 Gyr 13, L7 8) is being re-run on it: `lane.sh shade`, outputs in the session scratchpad
`v1f12/shade_*`. No pass rate on the final physics yet. Not ready to merge until that set is tallied.

## 1. The bar and the harness
`passrate4.py` (successor of v1-finish-11's passrate3.py). The bar is judged on 300 Myr to the end and per window.
- FAIL: always-icebox/snowball (icehouse share >= 90% or deep ice >= 30% of the time), hellhole (dT median > +10.5 or
  max > +15.5), never-ice (share < 5%). These are passrate3's definitions, unchanged.
- No cap on the icehouse share. The share is reported only.
- Finish checks per draw: true mean -6..+3 C against pre-industrial 13.8; land ice least over the last 12 Myr is
  1-25% of land (also tallied 5-20%, "near Earth's 10%"); wet equatorial lowland trees >= 20%; end pCO2 180-600
  (diagnostic). "bar + hard finish checks" = bar and T, ice and trees.
- Per-draw table and tallies at the end of its output.

Scripts: `launch.sh` (skips draws whose result exists; P6 L6 jobs at once, default 4), `lane.sh PREFIX` (L6 1 Gyr,
then L6 2 Gyr, then L7, serially), `pr.sh`, and the diagnostics `endterms.py`, `srcnoise.py`, `jointco2.py`,
`eqsun.py`, `vegsun.py`.

## 2. Re-tally on v1-finish-11's physics (thermostat off), 10 of 18 L6 1 Gyr draws
`passrate_off_v11physics.txt`. The other 8 L6 draws (`l6c_p`) were started after the section-3 code change and
were stopped and dropped, so they are not in this table.

| seed (dir) | icehouse | deep | dT med | bar | T vs PI | land ice | wet-eq trees | end pCO2 | all |
|---|---|---|---|---|---|---|---|---|---|
| 53669 (c_0) | 94.9 | 33.5 | -2.0 | ICEBOX | +0.9 | 2.3 | 18 | 291 | no |
| 733847 (c_0) | 56.2 | 1.7 | +1.3 | ok | +3.3 | 5.7 | 39 | 766 | no |
| 819014 (c_0) | 86.9 | 22.2 | -0.6 | ok | -0.1 | 8.9 | 32 | 453 | yes |
| 958504 (c_0) | 75.0 | 22.2 | -0.3 | ok | -3.1 | 15.4 | 23 | 264 | yes |
| 53669 (c_m) | 94.9 | 43.2 | -2.0 | ICEBOX | -4.2 | 16.8 | 16 | 243 | no |
| 958504 (c_m) | 59.7 | 1.1 | +0.2 | ok | +0.4 | 8.7 | 30 | 689 | yes |
| 583167 (fix) | 68.2 | 20.5 | +0.0 | ok | -4.7 | 7.4 | 3 | 93 | no |
| 619496 (fix) | 73.3 | 31.2 | -1.9 | ICEBOX (deep) | -4.3 | 16.2 | 20 | 181 | no |
| 639472 (fix) | 42.0 | 12.5 | +2.2 | ok | -5.1 | 6.6 | 13 | 90 | no |
| 957317 (fix) | 42.0 | 17.0 | +1.6 | ok | +3.3 | 3.5 | 23 | 987 | no |

Tallies:
- bar: **7/10**;
- bar plus the hard finish checks: 3/10;
- finish T inside -6..+3: 8/10 (two at +3.3);
- land ice 1-25%: 10/10 (5-20%: 8/10);
- wet-eq trees >= 20%: 5/10;
- end pCO2 in 180-600: 5/10.

The bar is at about 70% on this partial set. The finish checks are what fails, wet-tropics trees most of all.

## 3. Wet tropics: the plants read the sky's cover, not the climate's sunshine (fixed)
With the thermostat off the run ends under today's Sun, so the star's tropical heat is not the cause on these draws.
Two causes remain:
- **CO2 starvation on the two ~90 ppm ends** (583167 3%, 639472 13%). Below ~100 ppm C3 trees cannot carry a forest;
  that part is the CO2, not the plants (section 4).
- **Dim tropics** on the rest (18-23% at 260-990 ppm). The thermostat-on draws show the same thing: 958504 at -0.3 C
  and 254 ppm has 5%. That is PW-808.

PW-808's first check (`eqsun.py`, Earth world 506694, wet equatorial land < 10 deg, > 2000 mm):

| | model cloud | sunshine the plants used | climate's own sunshine | CRU sunshine | NCEP cloud |
|---|---|---|---|---|---|
| wet equatorial land | 0.80-0.82 | 0.21-0.23 | 0.31-0.33 | 0.50-0.52 | 0.64-0.65 |
| subtropical land | 0.32-0.40 | 0.59-0.67 | | 0.68 | 0.31 |

**The mechanism fault.** `climate.clouds` already knows that showers and cumulus shade only `cloud_sun_conv` of the
day, because convection builds in the afternoon and leaves sunny mornings. It stores that sunshine (the
`sunshine_*` layers). But `climate.months` computed the plants' PAR (Angstrom-Prescott) again from the raw cover, so
the plants got two-thirds of the climate's own sunshine in the wet tropics.

**The fix** (commit be00f07):
- `climate.shade(sun_share)` is the cover that `sunshine()` maps onto the climate's sunshine, and `compute` returns it
  as `shade_jul` / `shade_jan`.
- The run (`sim.shade_*`), worlds, the time zoom, zooms (`shade_from_hours` of the world's sunshine layers) and
  `tools/veg_check.py` hand it to the plants.
- The sky's cover still names the montane cloud forests (`vegetation.model(sky=)`).
- No parameter is changed.

Offline on the Earth world (`vegsun.py`, rain held), wet-eq trees, raw cloud -> climate's sunshine:

| case | raw cloud | climate's sunshine |
|---|---|---|
| 280 ppm | 45% | 72% |
| 180 ppm | 26% | 59% |
| 280 ppm, +3 C | 24% | 60% |

Global trees go from 32% to 38%. This answers the warm-tropics and LGM-CO2 sensitivity PW-806 described, in line with
the LGM and Eocene forests (Prentice et al. 2011; Jaramillo et al. 2010).

Checks:
- earth_check is unchanged (main group 71%, exact 34%, log-rain corr 0.648). The vegetation feedback on the climate
  does not move it.
- pytest: 681 pass. Goldens `climate_L4.json` and `sim_L4_s1_60myr.json` are updated on purpose.
- `test_ice_surface_rises_from_the_edge`: its setup climate is now dT - 14 (was -12), so the fixture has >= 3 inner
  ice cells. The assertions are unchanged.
- **scorecard not run yet.**

What is left for PW-808: the climate's sunshine is still 0.31 against CRU's 0.51, and the cover is 0.82 against
NCEP's 0.64. Both are cloud-scheme questions, left to PW-808.

## 4. End pCO2 spread (90-987 ppm): it is the balance's own response, not a numerical lag
`endterms.py`, `srcnoise.py`, `jointco2.py` on the 6 v1-finish-11 draws:
- **The source is smooth.** The tectonic outgassing has lag-1 r 0.97-0.98 at 2 Myr steps, and sd(ln) is 0.2-0.45
  after 300 Myr.
- **The drift's factor adds sd(ln) 0.26-0.40.** Total source sd(ln) is 0.35-0.61. GEOCARB's degassing f_G spans
  ~0.75-1.75 over the Phanerozoic, an sd(ln) of ~0.2-0.25.
- **The swings at the end come from the source.** 583167: the source falls 0.96 -> 0.46 over the last 30 Myr, and
  CO2 goes 533 -> 115 ppm.
- **Not the lag.** Solving CO2 jointly with the climate it gives (GEOCARB's frame; the run uses the 5-Myr-lagged dT
  in the sink) narrows sd(ln pCO2) only 0.95-1.37 -> 0.91-1.32. Rejected; no code change.
- **The gain.** With the planted law, 1/(a + cG) ~ 1.8 e-folds of CO2 per e-fold of source or weatherability.
- **The likely excess.** `climate_drift` (sd 3 C) is documented as standing for outgassing among other things, but
  the model already has explicit tectonic outgassing. The two together vary about twice GEOCARB's degassing. That is
  a judgement call on the drift's size, so it is in the draft `draft-drift-double-counts-degassing.md`; nothing was
  tuned.

## 5. Handoff: what to do next
1. Let `lane.sh shade` finish. If it was killed, relaunch with
   `docs/review/base-climate/v1-finish-12/lane.sh shade`: finished draws are skipped. It runs as one serial lane with
   4 L6 jobs at once (5 numba threads each), then g2, then L7 (2 at once). That is about 1 h, then ~3 h, then ~5 h.
2. Tally: `pr.sh shade`, or `passrate4.py $V/shade_*`.
3. Run `tools/scorecard.py` and commit its line.
4. Bar >= ~70% on L6 18 / L7 8 / 2 Gyr late window: the finish failures that remain are the next work (low-CO2
   ends: the draft). Bar fails: report with numbers, without the thermostat.
