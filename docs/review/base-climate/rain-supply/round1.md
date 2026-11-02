# Lane 132: rain supply, round 1 (PW-1321, D40 A), 2026-11-02

Status: **stopped after two failed arms and a diagnostic that contradicts plan A's premise. Nothing merged; the
model code is parked as [marine-layer.patch](marine-layer.patch) (off by default; applies to main f765fc4a).** No
seeds or judge were run: no arm got that far.

## In plain words

- Plan A said: the humid coasts are dry because the seas next to them are too dry, so give the sea a proper low
  air layer and they'll get more vapour. **I built that layer and tested it two ways. Both made things worse.**
  The layer doesn't rain, so it carried sea vapour further and the seas themselves rained less. The coasts got
  drier (0.56 -> 0.46 / 0.36 of the observed rain) and the interiors got wetter (1.85 -> 2.03 / 2.06x).
- **Then I checked the premise directly, and it doesn't hold.** I gave the rain the observed air temperatures over
  the seas. That brings the seas' vapour close to observed (Gulf summer 31.6 -> 36.3 mm, obs 39; W Atlantic 25.5 ->
  31.3, obs 32.7). The storm-track seas' winter evaporation also nearly triples (N Atlantic 452 -> 1130 mm, obs 1339).
  **The coasts still get drier, not wetter** (SE USA 720 -> 597, SE China 1062 -> 916, Japan 672 -> 577). The extra
  vapour rains over the sea or is carried on north (NE USA 1534 -> 1623).
- The observed land temperatures in the rain don't help either (SE USA 720 -> 537).
- **So the coasts' deficit isn't how much vapour the seas hold. It's where the arriving vapour rains.** The air crosses
  the coast and passes through (SE USA in summer: 3916 mm in from the south face, 4185 out of the north face). That
  points at the winds and the rain's placement: land friction (fallback B), the convergence ascent (PW-1100) and the
  inflow depth (PW-1099). It doesn't point at the supply. Per the brief, the question for Daniel is now B
  (draft-rain-coasts-are-through-flow-not-supply).
- **Two real supply findings came out of it** (drafts):
  - The rain doesn't see the overturning's warmth. The N Atlantic storm track's winter sea is 4.7 C for the rain
    against 13.1 C after the overturning (NCEP air 8.0). That is most of the storm tracks' missing winter evaporation.
  - The NH subtropical seas are 2-3.5 C too cool in the summer half for the rain (PW-593's small swing plus a cool
    annual mean).
  - Both are real errors. Neither wets the coasts (the swap screens above), so neither is the D40 fix.

## 1. Design (the diagnosis gate)

**What the marine layer is.** Over the oceans the air near the surface is a well-mixed layer under an inversion.
It is ~0.5-0.8 km deep (the sub-cloud layer in the trades; ~0.8 km under stratocumulus), or 1.4-2 km to the top of
the whole trade layer. The sea evaporates into it by the bulk formula. Its air mixes with the drier air above
through entrainment and the updrafts of shallow and deep cumulus. That mixing, not the sea, keeps its humidity
near 0.8 of saturation.

**Sources read** (by a research subagent, full text opened unless noted):

- Fairall et al. (2003), J. Climate 16:571-591, COARE 3.0, section 2b: the surface humidity is 0.98 x
  pure-water saturation. Ce10n is ~1.1-1.2e-3 (Smith 1989 1.2e-3; COARE 3.0 fit 1.15e-3 above 5 m/s). The model's
  `sea_ce` 1.3e-3 is a little high.
- Stevens (2006), Theor. Comput. Fluid Dyn. 20:279-304, sections 4-5:
  - Stratocumulus: surface exchange V ~8 mm/s, depth ~800 m, divergence ~4e-6 /s, so entrainment ~3.2 mm/s.
    That last figure is my arithmetic from his numbers.
  - Trades: entrainment E ~1 cm/s, sub-cloud layer ~500 m (400-800 m), cloud-base mass flux ~2.5 cm/s.
- Chan & Wood (2013), JGR 118:12422, para 32-34 and Fig. 5 (COSMIC): PBL ~2 km over the trades. It is ~1.4 km
  over stratocumulus and the warm pool, and under 1 km at high latitudes. Lidar puts the surface mixed layer below
  1 km everywhere.
- Grossman & Betts (1990), MWR 118:324 (abstract page only): in an extreme cold-air outbreak off the US east coast,
  the sea-air difference reaches 23 K and the latent heat flux 799 W/m2.
- Not opened (403): von Engeln & Teixeira 2013, Large & Yeager 2009. No ICOADS/OAFlux humidity climatology was read.

**Form (`climate.py::_rain`, TUNE `mbl`, `mbl_h`, `mbl_w`, `mbl_w_land`; in the patch).**

- A second vapour field b, the layer near the ground, sits under the column q (the column is what rains). Both are
  carried by the same face transport.
- Over the sea, `sea_uptake` fills b, not q: the bulk exchange's depth is `mbl_h` 500 m.
- b mixes with the column air at the layer's top, which is gamma x q. gamma = exp(-mbl_h q_k LAPSE) = 0.82, from the
  column's own vapour e-folding height. The mixing share per step is w dt / mbl_h, with w = `mbl_w` 7 mm/s over the
  sea (in Stevens' 3-10) and `mbl_w_land` 20 mm/s over land (the sunlit convective layer).
- What crosses goes into q, scaled by mbl_h / `sea_bl_m` (the column's existing fill depth, kept so the column's
  calibration holds).
- Over land, b above what the air can hold goes straight up into q.
- `mbl=2` also lets the showers fire on the layer's moist static energy, and their updrafts lift the layer's air
  into the column at the shower rate.
- The end state carries b (`rain_state["bl"]`; `nest.prolong_rain_state` handles it generically).
- `tools/moisture_budget.py::_probe` and `tools/moisture_regions.py::kernel_inputs` carry the same code, with the
  layer's own tracers. Screens confirm "probe reproduces the model's rain: True".

**Expected effect (design note, before the screens).** In steady state the sea's flux is C_E U w / (C_E U + w) x
(q_s - gamma q). Over a near-saturated storm-track column, the deficit grows from ~0.06 to ~0.23 of q_s. Over the
subtropics it grows from 0.28 to 0.41. So the storm tracks' share of evaporation should rise ~2.6x relative to the
subtropics (observed winter ratio 0.52, model 0.18). The layer's vapour should also reach the coasts in the
onshore flow and vent there. Planned next steps: the inflow (cross-isobar) carries the layer (PW-1099), and the
layer feels land friction (fallback B's physics, in the layer where it belongs).

## 2. Screens

Earth, whole solves. "ec7" is `tools/earth_check.py --level 7`. The cloud and sunshine rows are lane 126's
`tropical-cloud/screen.py` (L7). The sea boxes are `tools/moisture_regions.py --level 6 --no-cf` (P / E / PW against
GPCP / NCEP / NCEP). Interiors 40-60 N is the mean ratio to observed of W Siberia, European Russia, the Great Plains,
Mongolia and Central Asia. Humid coasts is the same for SE USA, the Pampas, India, SE China, Japan and E Australia.
The full table is [screens.md](screens.md). Harness: `ec.sh TAG "TUNE"` (the mbl arms need the patch applied),
`swap.sh TAG SPEC` and `summ.py TAG...`.

| | obs | main | m1 layer | m2 + showers | sw: obs sea air | swnh: obs sea 15-50 N | swland: obs land air 15-50 N | swboth |
|---|---|---|---|---|---|---|---|---|
| B % (Kottek 30.1) | | 24.5 | 28.6 | 31.8 | 25.2 | 23.9 | 25.5 | 25.1 |
| exact / group % | | 37 / 71 | 35 / 69 | 34 / 68 | 35 / 70 | 36 / 70 | 36 / 70 | 36 / 69 |
| log-rain r | | 0.714 | 0.693 | 0.663 | 0.683 | 0.687 | 0.710 | 0.686 |
| land P (GPCC 791) | | 1056 | 1295 | 1211 | 1041 | 1077 | 1052 | 1072 |
| interiors 40-60 N x obs | | 1.85 | 2.03 | 2.06 | 1.85 | 1.96 | 1.90 | 2.01 |
| humid coasts x obs | | 0.56 | 0.46 | 0.36 | 0.45 | 0.52 | 0.53 | 0.48 |
| SE USA | 1329 | 720 | 408 | 243 | 559 | 597 | 537 | 447 |
| Pampas | 943 | 394 | 297 | 177 | 322 | 390 | 395 | 391 |
| SE China | 1460 | 1062 | 1267 | 1039 | 910 | 916 | 868 | 714 |
| Japan | 1683 | 672 | 345 | 344 | 554 | 577 | 732 | 581 |
| W Europe | 903 | 1159 | 1721 | 1591 | 1069 | 1172 | 1171 | 1182 |
| N Atl track Oct-Mar P/E/PW | 1651/1339/15.2 | 1206/452/14.1 | 1225/293/15.7 | 1302/336/15.3 | 1925/1292/13.8 | 1799/1130/13.7 | 1208/451/14.1 | 1803/1131/13.7 |
| Gulf Apr-Sep P/E/PW | 1239/1423/39.0 | 523/1493/31.6 | 316/1593/29.3 | 325/1618/28.8 | 623/1676/36.1 | 673/1796/36.3 | 524/1495/31.6 | 675/1801/36.2 |
| W Atl subtropics Apr-Sep P/E/PW | 1334/1412/32.7 | 555/2017/25.5 | 180/2178/21.7 | 188/2215/21.3 | 607/2254/31.1 | 667/2368/31.3 | 563/2019/25.5 | 672/2372/31.3 |
| warmest month 0-20 / 20-40 / 40-60 (NCEP 26.5 / 25.6 / 18.5) | | 24.8 / 26.0 / 18.3 | 24.6 / 26.0 / 18.2 | 24.8 / 26.2 / 18.3 | 24.8 / 26.1 / 18.2 | 24.8 / 26.0 / 18.2 | 24.8 / 26.0 / 18.3 | 24.8 / 26.1 / 18.2 |
| summer sun 20-40 (CRU 0.669) | | 0.758 | 0.767 | 0.779 | 0.769 | 0.762 | | |

**m1 (strike 1).** The layer doesn't rain, so it carries the sea's vapour further. The sea's column is fed only by
the mixing, so it is drier and rains less: subtropical seas fall to 0.15-0.4x GPCP, the Gulf to 316. The winter
westerlies carry the layer's vapour ashore, where it condenses on the cold land: W Europe 1721. Storm-track
evaporation fell instead of rising, because the column above them stays near saturation (q/qs 0.92). So the layer
under it stays moist too (gamma 0.82 is too mild to dry it), and the global rescaling then takes more from the sea.

**m2 (strike 2).** Letting showers draw on the layer didn't revive the sea's rain. The Gulf's showers still don't
fire, because its summer sea is 2.6 C too cool (below). The coasts fell further (SE USA 243).

**The swap diagnostics (not arms: they ask whether the premise holds).** `sstswap.py` replaces the rain's sea
temperature (`_season_inputs`' sst on open water) with NCEP's 2 m air half-year means + 0.5 C. It touches only the
rain and cloud inputs; the temperature model is unchanged. With SWAP_LAND=1 it also replaces the land's air.

- The seas' vapour and the storm-track evaporation come close to observed, but the humid coasts don't gain. Lane
  120's "the coasts' vapour lives in the subtropical seas next to them" holds for the vapour, but more of it doesn't
  rain on the coast.
- Observed land temperatures (lowering the hot SE USA's qs) don't help the coasts either. They do help the Great
  Plains (767 -> 590) and NE USA (1534 -> 1336).

## 3. Sea temperatures the rain sees (seaair.py, Earth L6, [seaair_L6.txt](seaair_L6.txt))

Half-year means: SST as the rain sees it, the rain's sea air (`tm +- dt`), the final air after the overturning, and
NCEP 2 m air.

| box | half | rain SST | final air | NCEP air |
|---|---|---|---|---|
| N Atlantic storm track | Jul | 10.1 | 15.5 | 14.0 |
| N Atlantic storm track | Jan | 6.7 | 13.1 | 8.0 |
| Gulf of Mexico | Jul | 25.0 | 24.6 | 27.2 |
| W Atlantic subtropics | Jul | 22.1 | 22.9 | 25.0 |
| E Atlantic subtropics | Jul | 19.9 | 20.7 | 23.4 |
| NW Pacific subtropics | Jul | 22.9 | 22.6 | 25.0 |
| Tropical Atlantic | Jul / Jan | 25.7 / 25.8 | 25.2 / 26.1 | 24.9 / 25.4 |

- `compute` runs the rain before the overturning (its comment says so). The N Atlantic's winter rain sea is 6 C
  colder than the finished sea, and 3 C colder than NCEP's air.
- The NH subtropical seas' summers are 2.3-3.5 C cool even after it: PW-593 (the 50 m layer's small NH swing), plus
  a ~2 C cool annual mean.
- The air-sea temperature gap the brief's design hoped to use is ~0 in the model's box means (qsat(air)/qsat(SST)
  0.91-1.0). The cold-air-outbreak chill reaches only ~300 km from the coast (`_winter_air`).

## 4. State at hand-off, and what's next

- **Done:** the design and sources (section 1); the layer coded with its probe (parked patch); screens m1, m2 and
  four swap diagnostics (section 2); the sea-temperature audit (section 3). No model change on the branch, so no
  tests or goldens were needed. The branch carries this folder and the drafts.
- **Strikes:** two arms of A failed (m1, m2). I stopped before a third, because the swap diagnostic shows A's premise
  (the coasts lack supply) is false for Earth. A third arm (the layer carrying the inflow, PW-1099) would rest on the
  same premise. That's an explained stop, not an unexplained side effect.
- **For Daniel (via the coordinator):** fallback B, or better, a round on where the vapour rains (land friction in
  the low layer plus the convergence ascent PW-1100). Draft: draft-rain-coasts-are-through-flow-not-supply.md.
- **Patch:** `git apply docs/review/base-climate/rain-supply/marine-layer.patch`. With `mbl=0` (the default) the
  model is unchanged (`tests/test_rain_transport.py` and `tests/test_golden.py` pass with it applied, 6 passed). The patch also updates the probe and
  the test unpacking.
- Scratch (`.../scratchpad/l132`) deleted at the end. The worktree's private `data/earth/` copy (gitignored) was
  deleted too.

## Files

ec.sh, swap.sh, withtune.py, sstswap.py, seaair.py, summ.py, screens.md, seaair_L6.txt, marine-layer.patch.
