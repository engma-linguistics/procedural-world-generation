# Ice ages v2: what success means, and the assumptions under it (PW-555, stage 0)

2026-10-21, ice v2 lane. Owner's question: "Something that bothers me about 'failure' and 'success' thus far
seems, though, relative to the last minor ice age we had in the real world? What about the Cryogenian period or
Paleocene-Eocene thermal maximum? [...] so long as there's evidence a planet *can* come out of it [...] A revisit of
what the actual success criteria is and means and times between ages and whatever is probably warranted. What're the
base assumptions that might be off? What *are* the base assumptions?" Also folded in: the owner's note on
Chandler & Sohl (2000) (section 2.4) and on the first 300 Myr being a warm-up (section 3.1).

Measurements: `docs/review/ice-v2/checkpoint-0.md` (the table) and the tools in section 5. No model physics was
changed in this stage.

## Summary for the owner

- **You're right that the old bars were too narrow.** They asked "is every cold era about as shallow as Earth's last
  glacial?" (no worse than −450 m of sea level, and rarely below −430 m). Earth itself fails that: the Cryogenian
  snowballs lasted ~5–60 Myr each, with the sea perhaps several hundred metres lower, and the planet got out of them.
- **The new question is "does this planet behave like a planet?"** Deep, long ice ages are allowed. Ice-free hot
  ages are allowed. What isn't allowed is getting stuck: every cold era must end, within broad time limits taken
  from Earth's record (a deep era within ~150 Myr, a very deep one within ~60 Myr), the planet should spend some but
  not all of its time in icehouses (5–70%), and when it is in an icehouse the 100-kyr ice-age cycles should still look
  right. The first 300 Myr are a warm-up and don't count.
- **What the new measuring tools found on today's main** (`docs/review/ice-v2/checkpoint-0.md`):
  - A default planet spends **~60% of its time in an icehouse** (Earth ~10–30%), because "normal" in the model is
    today's Earth, which is itself in an ice age.
  - **Deep cold eras last as long as the random climate wander stays cold**, 100–400 Myr. The CO2 thermostat barely
    pushes back: under the ice, weathering hardly slows, so CO2 doesn't rise. The CO2 ceiling is never reached.
  - The ice sheets in deep eras aren't "stuck" sheets losing mass: they gain far more snow than they lose. The cold
    climate holds them. On one planet the ice also keeps itself (two states at the same temperature).
  - Old bar: 8 of 10 planets pass. New bar: 5 of 10 (too long in deep cold, or always in an icehouse).
- **The biggest base assumptions I'd change:**
  1. **Today's Earth is the planet's "normal".** dT = 0 is our current ice age, and the thermostat steers back to the
     run's own average, so planets live in icehouses. Earth's long-run normal is several degrees warmer.
  2. **CO2 isn't a stock, and its thermostat barely answers a cold era.** The model sets CO2 from the balance of
     volcanoes and weathering, against baselines that learn over 1000 Myr. Under ice that balance hardly moves, so CO2
     can't "pile up" over millions of years as it did in the Cryogenian. (The ~20× ceiling would matter next, but
     isn't reached today.)
  3. **The ice is always in balance with the climate, and big sheets keep themselves cold by their height.** This is
     the review's root cause, and stage 1–3's job; the run's sheets also gain far more snow than the zoom's flowing
     sheets keep (the zoom loses ~80 m from the run's deep moments).
  4. **Only land ice brightens the planet, and that effect stops at 3 C.** There's no sea-ice brightening, so the
     model can't make a true snowball, though it can make very deep land-ice eras.
  5. **The star never brightens.** Real Sun-like stars brighten ~1% per 100 Myr. That trend is too slow to switch ice
     ages on or off, but it matters over 1–2 Gyr runs.
- **The recovery lever you described can be built honestly** (section 4): an optional planet setting whose strength
  grows with how long and how deep a cold era has lasted, and fades as the planet recovers. Its mild form uses real
  mechanisms: CO2 piling up under the ice, and volcanic dust darkening the ice. Its strong forms (a brighter star, a
  volcanic pulse on demand) are world-builder controls, and the viewer should say so. It becomes a ticket, not code yet.
- **Today's main against both bars** (checkpoint 0): see the table in `docs/review/ice-v2/checkpoint-0.md`.

## 1. Earth's record, as an analogue (not a target)

Earth is one planet with one history. The point here is the *range* a believable planet can show: how cold, how
long, how often, and how it got out. Dates are approximate; the uncertainty is given where it matters.

### 1.1 The cold eras

| era | when | how long | how cold / how much ice | how it ended | main sources |
|---|---|---|---|---|---|
| Pongola | ~2.9 Ga | ? (one diamictite unit) | regional glaciation | unknown | Young et al. 1998 |
| **Huronian** (incl. Makganyene) | ~2.45–2.22 Ga | a ~200 Myr window with 3–4 glaciations; each one's length is unknown (Myr to tens of Myr) | at least one at low latitude (Makganyene, Evans et al. 1997), perhaps a snowball | linked to the rise of oxygen (loss of the methane greenhouse) and its recovery; poorly known | Bekker et al. 2004; Gumsley et al. 2017 |
| "Boring billion" | ~1.8–0.8 Ga | **~1–1.5 Gyr with no accepted glaciation** | — | — | Young 2013 |
| **Sturtian** snowball | 717–661 Ma | **~56–58 Myr** | global sea ice, ice to the equator (paleomagnetic latitudes) | volcanic CO2 built up while ice stopped weathering; meltdown fast (kyr), cap carbonates | Rooney et al. 2015; MacLennan et al. 2018; Hoffman et al. 2017 |
| Cryogenian interlude | 661–~650 Ma | ~10–15 Myr | non-glacial | — | Rooney et al. 2015 |
| **Marinoan** snowball | ~650/645–635 Ma | **~4–15 Myr** | global | as Sturtian | Prave et al. 2016; Rooney et al. 2015 |
| Gaskiers | ~580 Ma | **< 0.34 Myr** | regional, not global | — | Pu et al. 2016 |
| **Early Paleozoic / Hirnantian** | ~460–420 Ma, peak ~445 Ma | ~40 Myr icehouse; the Hirnantian peak ~1 Myr | Gondwana ice sheet; peak volume similar to or above the LGM's; sea level ~50–100+ m lower | CO2 rise, weathering decline | Finnegan et al. 2011; Page et al. 2007 |
| **Late Paleozoic Ice Age** | ~360/340–260 Ma | **~80–100 Myr**, as discrete glacial intervals of 1–8 Myr | Gondwana; sea level cycles of ~20–120 m | CO2 rose (volcanism, weathering changes, the drift of Gondwana off the pole) | Fielding et al. 2008; Montañez & Poulsen 2013; Rygel et al. 2008 |
| Mesozoic greenhouse | ~260–34 Ma | **~220 Myr**, mostly ice-free (maybe brief small ice in the Early Cretaceous) | Cretaceous thermal maximum ~25–30+ C global mean, CO2 ~1000–2000 ppm; sea level +100–250 m (mostly the basins) | — | Scotese et al. 2021; Haq 2014 |
| **PETM** | 56 Ma | onset < 20 kyr; recovery ~120–200 kyr | +5–6 C (range ~4–8) on an already ice-free Earth | weathering and burial drew the carbon back down | McInerney & Wing 2011; Tierney et al. 2022; Zachos et al. 2005 |
| Early Eocene optimum | ~53–49 Ma | a few Myr | ~10–16 C above preindustrial | slow CO2 decline | Inglis et al. 2020 |
| **Cenozoic icehouse** | 34 Ma–now | **34 Myr so far** | Antarctica from 34 Ma; northern sheets from 2.7 Ma; 41-kyr cycles, then 100-kyr cycles after ~1.25–0.7 Ma; LGM sea level −120..−134 m, global mean −6.1 C (5.7–6.5) | ongoing | Westerhold et al. 2020; Lambeck et al. 2014; Tierney et al. 2020 |

### 1.2 What the record says about the whole history
- **Share of time in an icehouse.** Phanerozoic (541 Myr): ~30% if the Early Paleozoic, Late Paleozoic and Cenozoic
  icehouses count in full (~40 + ~90 + 34 Myr), ~15–20% if only their glacial peaks count. Since 2.5 Ga: ~10–20%.
  Uncertainty: large before 1 Ga (gaps in the rock record).
- **Gaps between icehouses: ~60 Myr to ~1.5 Gyr.** EPIA to LPIA ~60–100 Myr; LPIA to the Cenozoic ~220 Myr; the
  Cryogenian to the EPIA ~170 Myr (Gaskiers in between); the Huronian to the Cryogenian ~1.5 Gyr.
- **Icehouse lengths: <1 Myr (Gaskiers) to ~90 Myr (LPIA).** A snowball ~5–60 Myr.
- **How deep.**
  - Ordinary icehouse glacials: sea level −50..−130 m from ice, global mean ~4–7 C below today's.
  - Snowballs: global, with the sea frozen to the equator. How much water the land ice held is poorly known: a starved
    hydrological cycle limits growth (section 2.4), but the eras lasted Myr. Model estimates span a few hundred metres
    to ~1 km of sea level (Hoffman et al. 2017's review discusses this; I treat ~−1000 m as the outside edge, not a
    measured value).
- **How cold eras ended.**
  - Snowballs: the weathering thermostat (Walker et al. 1981) at its extreme. Ice shuts down silicate weathering, the
    volcanoes keep outgassing, and CO2 piles up as a stock for Myr. Estimates of the CO2 needed: ~0.12 bar on an
    energy balance model (Caldeira & Kasting 1992), > 0.2 bar in a GCM without dust (Pierrehumbert 2004), and
    ~0.01–0.1 bar once dust and volcanic ash darken the ice (Abbot & Pierrehumbert 2010; Le Hir et al. 2010). Against
    preindustrial 280 ppm that is **~40–400×, or 3.6–6 e-folds**. Δ17O anomalies in post-Marinoan sulphates support
    very high CO2 (Bao et al. 2008). Once the ice starts to go, the albedo feedback runs backwards and the meltdown
    takes ~kyr; the cap carbonates are the super-greenhouse's weathering burst.
  - Phanerozoic icehouses: slower CO2 changes (volcanism, mountain weathering, plants, continents drifting off or onto
    the poles).
- **Hot eras end too.** The PETM recovered in ~0.2 Myr through weathering. The Mesozoic greenhouse lasted ~220 Myr,
  but it wasn't stuck: temperature and CO2 moved within it.

## 2. Base assumptions of today's ice, climate and sea-level code

Each line: what the code assumes, where, whether it's reasonable, what it costs, and whether it should change. "v2"
means it's in the ice epic's plan; "new" means it should become a ticket (drafted in `issue-tracking/inbox/`).

### 2.1 Global temperature and the carbon cycle

| # | assumption | where | reasonable? | cost | change? |
|---|---|---|---|---|---|
| A0 | **dT = 0 is today's Earth, an icehouse**, and the thermostat's baselines are the run's own means, so the drift and CO2 wander around today's climate | `climate.compute`, `earth.global_temperature`, `params.climate_offset` 0 | as a calibration anchor yes; as the planet's *typical* state no: Earth's Phanerozoic mean is ~5–8 C warmer than today (Scotese et al. 2021) | default planets spend ~60% of their time with ≥ 20 m of ice (checkpoint 0; Earth ~10–30%) and often never have an ice-free era | **new (needs-decision)**: a default `climate_offset` of ~+3..+5 C, or a thermostat baseline that isn't today's climate; or keep icy defaults as a style choice |
| A1 | The planet's climate is **one number, dT** (offset from today's Earth), mapped onto a fixed latitude profile: the tropics move 0.5 × dT, the poles 1.5 × dT. There's no radiation balance. | `climate.compute` (`eq, pole = 27.8 + 0.5 dT ..., -10.4 + 1.5 dT ...`) | yes for a toy climate inside ±10 C of today | no runaway states (snowball, waterbelt), polar amplification fixed in shape | keep; a later research mode at most |
| A2 | dT's target = **drift + CO2 term − ice albedo term + offset**, approached with a 5 Myr lag | `earth.global_temperature` | yes | — | keep; record the terms (done: `diag.py`) |
| A3 | **CO2 isn't a stock.** ln pCO2 = ln(source / sink) / 0.4, with source and sink smoothed over 10 Myr and measured against baselines that learn over 1000 Myr | `earth.global_temperature` | yes at steady state (the weathering thermostat's equilibrium); **no** for long cold eras: real CO2 accumulates at (source − sink) per Myr while ice holds the sink near 0, which is how snowballs end | a cold era's CO2 is capped by today's rate ratio and can't keep rising with the era's age | **new (high)**: a carbon stock with an outgassing − weathering budget; the ratio rule is its steady state |
| A3b | **The thermostat barely answers a cold era**: weathering stops only on iced land (a fifth to a third of it in deep eras) and slows by `exp(0.09 dT)`; the baselines learn over 1000 Myr, so long trends (plants spreading, mountains) leave the sink above its baseline for most of a run | `earth.global_temperature` (`warm`, `REF_MYR`) | partly: real weathering responds similarly per area, but real cold eras also lose runoff and soil CO2, and outgassing doesn't care | checkpoint 0: in 5 of 7 deep eras the CO2 term is ≤ +0.1 C, in 3 it cools by 3–4 C; the CO2 index median is −0.4..−0.9 on most seeds | **new (with A3)** |
| A4 | **CO2 forcing clipped at ±3 e-folds** (`CO2_MAX`, ~20× / 0.05× the baseline) | `earth.py` `CO2_MAX` | no for snowball-like eras: exits need 3.6–6 e-folds (section 1.2). **But on main the clip is never reached** (index −3.6..+1.8, 0% of deep-era steps clipped) | none today; it will bind once A3 lets CO2 build up | **new (with A3)**: raise the ceiling to ~6 e-folds, or replace the hard clip with a log-saturating forcing (CO2's forcing is ~logarithmic up to ~0.1 bar, then grows less) |
| A5 | **Climate sensitivity 3 C per e-fold**, i.e. ~2.1 C per doubling, the same in any climate | `params.co2_sensitivity` | low-ish: IPCC AR6 best 3 C per doubling, likely 2.5–4 (that includes fast feedbacks, which the model folds in); real sensitivity is state-dependent, higher when cold | slower thermostat, shallower hothouses | keep for now; revisit with A3/A4 on the moment suite, not alone |
| A6 | **Ice albedo counts only land ice**, as a tanh that levels off at 3 C (from Earth's 3.1% of the surface) | `earth.global_temperature` `albedo()`; `params.ice_albedo(_max)` | reasonable for Pleistocene-like ice (LGM ~2.5–3 C of albedo forcing). Not for deep eras: sea ice and snow cover have no global albedo, and the cap stops a runaway | the model can't make a snowball; deep land-ice eras happen through the ice rule's hysteresis instead (A11, A12), which is the wrong mechanism | **v2 later / research**: a sea-ice share in the global albedo, then a snowball state with its exit (A3, A4) |
| A7 | **No explicit water vapour or cloud feedback.** Clouds are diagnostic (sunshine, PW-…); their radiative effect and the vapour feedback are folded into `co2_sensitivity` and `ice_albedo` | `climate.py` (clouds after the rain) | yes for a toy model near today's climate | Chandler & Sohl's cold feedbacks (more low cloud, 90% less vapour) are absent, so the onset of a deep era is gentler than a GCM's | keep; note it as a reason onset needs a big push in the model |
| A8 | **The moisture brake is partial.** Global rain is rescaled to `mean_mm × exp(0.03 dT)` (~3%/C, the hydrological sensitivity, Held & Soden 2006: ~2%/K precipitation, ~7%/K vapour). A frozen sea feeds the air only through `leads` = 0.1 of its area (PW-308). The time zoom scales rain by `exp(0.07 dT)` (Clausius-Clapeyron) | `climate.compute` (`wet`, `open_air`); `icemass.PRECIP_K` | mostly: accumulation does fall as the air cools and the sea freezes. But the run (0.03) and zoom (0.07) disagree, and global renormalisation sends the remaining rain to wherever there is open water | at deep cold, snow keeps falling at ~70% of today's global total (dT −10), less than a snowball's near-stop. The hysteresis probe measures snowfall on the ice against dT | **new (med)**: one rain-vs-temperature rule for the run and the zoom; measure the brake with the probe first |
| A9 | **The star never changes.** S0 = 1361 W/m², no main-sequence brightening (~+0.9% per 100 Myr for a Sun-like star now, Gough 1981), no stellar variability | `orbit.py` `S0`; no solar term in dT | for 1–2 Gyr runs: no. A 2 Gyr run spans ~17% of luminosity, ~+30 C of forcing without the thermostat. The thermostat (A3) cancels most of it on Earth (the faint young Sun, Feulner 2012) | missing a slow background trend that would make young planets colder and old ones warmer, and that the thermostat should visibly fight | **new (med)**: a `star_age` / brightening term in dT, planet-relative (the run's own start luminosity); check the thermostat absorbs it |
| A10 | **A random drift** (sd 3 C, 40 Myr memory) stands for every carbon-cycle and ocean process the model lacks | `params.climate_drift(_time)` | yes as a stand-in | it is what pushes planets into cold eras; with A3/A4 it can push them deeper than the CO2 can answer | keep; narrowing it was tried (PW-434 B) and only reshuffled seeds |
| A11 | **Volcanic CO2 comes from new sea floor and arc growth only.** No large igneous provinces, no plume CO2, no metamorphic or carbonate-subduction CO2 | `earth.global_temperature` `source` | partial | no CO2 pulses; LIP pulses help end real cold eras and start hot ones | new (low): plume/LIP CO2 from `volcanism`'s plumes |
| A12 | **No weathering under land ice, and no sea-floor weathering** | `earth.erode` (`weathered`), `global_temperature` | the first: yes (rock flour weathers little in the cold). The second: sea-floor weathering is a real sink, small today, larger in a snowball (Le Hir et al. 2008) | the sink under deep ice is ~0, which helps exits | keep |
| A13 | **Plants from t = 0** by default (`plants_from` 0): GEOCARB's vascular-plant weathering law (`WEATHER_CO2` 0.4) and the NPP factor apply all along | `params.plants_from`, `WEATHER_CO2` | world-building choice; Earth's land plants are ~470 Myr old, and pre-plant weathering is ~pCO2^0.5 | small | keep; note for "early Earth" presets |

### 2.2 The ice

| # | assumption | where | reasonable? | cost | change? |
|---|---|---|---|---|---|
| B1 | **The run's ice is always in balance with its climate**: a fixed point per 4 Myr update, no time, no flow | `earth.ice_sheets` | as an equilibrium approximation yes (sheets answer in ~10–100 kyr) | two ice models (run vs zoom); the review's root cause 1 | **v2 stage 2/3** (option 2 preferred: the run runs the zoom's ice core) |
| B2 | **A sheet survives where each cell's balance at its own height is positive**: no sheet-wide budget, so a sheet in deficit doesn't thin | `earth._ice_pass`, `ablation_zone` | no | cold eras that don't end (root cause 2); `diag.py` now reports the volume of sheets kept in deficit | **v2 stage 1–3** |
| B3 | **Hysteresis by height and carried air** (`air_mass`, PW-336): an old sheet keeps itself cold | `_ice_pass`, `icemass.air_mass` | yes, real (height-mass-balance feedback) | with B2 it becomes rigid | keep; the hysteresis probe measures the loop |
| B4 | **Margins at `EDGE_H` 408 m and one-cell (~110 km at L6) ablation zones** | `icemass.EDGE_H`; the grid | no (the honest cell mean is ~900 m, PW-460) | an error doing a brake's job | **v2 stage 1** (`margin_ramp`) |
| B5 | **The orbit as 8 averaged states** in the run, `insol_k` 0.25 C per W/m² (3× the seasons' 0.08–0.09) | `icemass.balance` (`cycle_dq`), `INSOL_K` | the averaging yes; the gain no (PW-459) | sheets too fragile to the orbit in the zoom | **v2 stage 1** (`seasonal_k`) |
| B6 | **Cycles are scripted** (the glacial index) in the zoom; the run has none | `timezoom/cycle.py` | yes as a v2 driver (owner agreed) | none for v2 | keep (option 4 later) |
| B7 | **The glacial cooling** is 6.5 C × the ice-free snowline land share / 3.5%, at most 1.6× | `cycle.cooling`, `TZParams.glacial_cool/f/cap` | no: it misses the land already iced (PW-538), and 6.5 C is above the LGM's 4.5–6 | warm or iced moments get no ice age | **v2 stage 3** (PW-538 A) |
| B8 | **Base-climate biases decide where the ice grows** (Labrador July +5.5–6 C, Fennoscandia January −18 C, margin snowfall about half of GPCP) | `climate.py` (PW-015/033/458) | not ice-model questions | the model's ice grows at 70–80N | outside the ice epic |

### 2.3 Sea level and measurement

| # | assumption | where | reasonable? | cost | change? |
|---|---|---|---|---|---|
| C1 | **Sea level 0 = the starting ocean floor's mean depth**; the basin term follows the floor's mean depth against it (×0.69 for the floor's load), levelling off at ±400 m | `earth.global_temperature` (`depth_ref`, `SEA_TECT_MAX`) | the reference yes; the drift no (PW-549, another agent) | ±100–300 m offsets that hide or fake cold-era depth | **PW-549**; the tools now report the two terms apart everywhere |
| C2 | **The ice term is −0.9 × the land ice's volume over the ocean's area**, with no marine-ice flotation correction in the run | `earth.update_climate` | close enough (the zoom does flotation) | a few % | keep |
| C3 | **Cold eras judged against the LGM**: worst era ≥ −450 m and ≤ 2% of the time below −430 m (PW-434/449), health's −250 m envelope (PW-240) | `tools/sealevel.py`, `tools/health.py` | no: Earth's own record fails them (section 1) | good planets fail, and fixes chase depth instead of recovery | **this doc, section 3** |
| C4 | **No spin-up in the cold-era check, 50 Myr in health** | `sealevel.py` (`--skip 0`), `health.SPINUP` | the first no | early transients count | 300 Myr for the ice criteria and health (section 3.1) |
| C5 | **Climate every 4 Myr**: spells are resolved to 4 Myr; anything shorter (Gaskiers, the PETM, a Hirnantian peak) is invisible in a run | `params.climate_every` | yes for the run's job; the time zoom covers the short scale | short events can't be judged in the run | keep; judge them in the zoom |

### 2.4 The Chandler & Sohl (2000) points (owner's input)

Chandler & Sohl (2000, JGR, GISS GCM, Varanger ~600 Ma geography) found: no single forcing (6% fainter Sun, CO2 at
40–1260 ppm, ocean heat transport ±50%, 60° obliquity) gave year-round tropical snow; a fainter Sun or 40 ppm CO2 iced
the high and middle latitudes; the combination of a fainter Sun, low CO2 and weaker ocean heat transport froze the
tropical continents; low-latitude ice never formed without high-latitude ice first; the feedbacks were more low cloud,
a brighter surface and much less water vapour (−90% in the worst case; snow and ice cover 68% against 12%); and
accumulation fell as the sea ice spread and the air dried, so a full snowball's ice starves itself.

1. **The self-starving moisture brake: partly there** (A8). Global rain falls ~3% per C, and a frozen sea only feeds
   the air through 10% leads, so snow on the ice does fall in the cold. But the global total is renormalised, so the
   rain left goes wherever there's open sea, and a snowball's near-stop of the hydrological cycle can't happen (the
   model never reaches those temperatures anyway, A1/A6). Measured (checkpoint 0, hysteresis probe): snow per m² of
   ice falls ~3× from dT +6 to −10 (880 → 300 mm/yr), but the sheets' total snow gain *rises* as they spread (10 → 50
   m of sea level per kyr). So at the temperatures the model reaches it doesn't limit depth; it would only near a
   snowball.
2. **Water vapour and low cloud: not explicit** (A7). They are folded into the CO2 sensitivity and the land-ice
   albedo. So onset in the model is gentler than in a GCM and needs the drift and CO2 together.
3. **Stellar luminosity: fixed** (A9). Real brightening (~1% per ~100 Myr) is a slow background trend: it should
   enter dT as a planet-relative term (luminosity against the run's start) and be fought by the thermostat. It is far
   too slow to switch an ice age on or off on Myr scales. A "solar help" lever for onset or recovery is therefore a
   **world-builder control** (a variable star), not Earth-like physics, unless the planet's star is set up as variable
   (a generation-time option: `star_variability`, with its own period and amplitude, shown as such).
4. **Onset needs combined forcings, and ice spreads from the poles first.** Both are good checks on onset:
   - in the run, a cold era should start from a combination (drift + CO2 + albedo, `diag.py` records each term at
     the era's start), not from one term alone, unless the world-builder forced it;
   - ice reaches low latitudes only after high-latitude ice exists: `diag.py` records the ice's lowest latitude per
     update, and the probe per step. A criterion: no update has ice equatorward of 30° at sea level unless ice
     poleward of 60° has existed for at least one update before it (it's cheap; checkpoint 0 reports it).
5. **Later work, with honest uncertainty.**
   - *Agrees:* onset from the high latitudes is universal in energy balance models and GCMs (the ice-albedo
     instability past ~30°, Budyko 1969, Sellers 1969); high obliquity as the cause is now generally disfavoured
     (Donnadieu et al. 2002; Hoffman et al. 2017). A starved hydrology and thin, slow sheets in a hard snowball also
     appear in later GCM/ice studies (Pollard & Kasting 2005; Donnadieu et al. 2003), though sheets still grow over Myr.
   - *Differs or refines:*
     - **How hard onset is varies a lot between models.** With present-day CO2, Voigt & Marotzke (2010, ECHAM5/MPI-OM)
       needed the Sun ~9% fainter for a full snowball, and 6% wasn't enough. Yang, Peltier & Hu (2012, CCSM3) needed
       ~10–11% at 286 ppm, less at low CO2. The ocean's heat transport and sea-ice dynamics matter, and EBMs freeze far
       more easily.
     - **There may be intermediate states:** the "waterbelt / Jormungand" with open tropical sea (Abbot, Voigt & Koll
       2011), and thin-ice "slushball" variants (Pollard & Kasting 2005). They depend on bare sea ice's albedo, and
       their stability is debated.
     - **Exit is harder than EBMs said** (Pierrehumbert 2004: > 0.2 bar CO2 without dust), and dust or ash makes it
       feasible (Abbot & Pierrehumbert 2010).
     - Chandler & Sohl's low-cloud feedback sign is model-dependent (clouds over sea ice remain a large uncertainty in
       GCMs).
   - Net for us: onset of a deep era should need several forcings together; exit should need a big, slow CO2 build-up
     helped by dirty ice. That is what the recovery lever's physical part does (section 4).

## 3. New success criteria (planet-relative, whole history)

### 3.1 Spin-up: the first 300 Myr don't count
Owner, 2026-10-21 (first ~100 Myr, then 300 Myr "the health tool's existing cut"). Early in a run the coupled systems
settle into each other:
- the CO2 baselines learn fast at first (`min(REF_MYR, 10 + t)`), so the thermostat is still finding its feet;
- the climate drift needs ~40 Myr (its memory) to reach its full spread;
- the ice starts from none, the plants spread from a made-up start, and the ocean basins start from a made-up floor.

- **Why 300 Myr.** The short transients (the drift reaching its spread, the first ice) are over by ~100 Myr. 300 Myr also
  covers the CO2 baselines: they learn over `min(REF_MYR, 10 + t)`, so until ~300 Myr they still follow the run's own
  early mean closely, and the thermostat's reference is still moving. On the checkpoint-0 runs the first deep era
  often falls in 100–300 Myr (see the table), which is the warm-up's footprint.
- **Correction.** On main, `tools/health.py`'s cut (`SPINUP`) was 50 Myr, not 300 (its docstring and medians use
  50); and the cold-era check (`tools/sealevel.py`) skipped nothing. Both are now 300 Myr for the ice criteria
  (`tools/ice_criteria.py`, health's ice columns), and health's `SPINUP` is 300 for everything, as the owner asked
  ("use 300 Myr consistently"). That makes health's other envelopes (rivers, lakes, plates) see 300 Myr less too.
- **Cost.** A 1 Gyr run is judged on 700 Myr. Recovery and share bars are about long eras, so 1 Gyr runs still have
  room to see 2–4 icehouses; the long diagnostic runs are 2 Gyr.
- The old bar is still computed as it was (from t = 0), so the two can be compared on the same runs.

### 3.2 Definitions
- **Icehouse:** land ice holding at least 20 m of sea level (about three Greenlands; Earth today ~65 m, the Mesozoic
  ~0). Not a share of the land: the model keeps 1–4% of its land under ice on high tropical plateaus and polar
  mountains at any dT it reaches, which is mountain ice, not an icehouse (checkpoint 0). Spells closer than 8 Myr (two
  updates) are one icehouse.
- **Deep:** sea level from ice below −150 m (beyond any Pleistocene glacial). **Very deep:** below −430 m.
- **Hot:** dT above +8 C (Cretaceous/Eocene-like).
- All on the ice term of sea level (`sea_ice`), never the total. The basin term has its own envelope (C1).

### 3.3 Per-run bars (L6, default parameters, after the 300 Myr spin-up)
| | criterion | why this number |
|---|---|---|
| **N1 recovery** | every deep era ends within 150 Myr; every very deep era within 60 Myr. An era still on at the run's end fails only if it has already run longer | Sturtian ~57 Myr, LPIA ~90 Myr; a planet may sit deep for a long time but must come out |
| **N2 floor** | sea level from ice never below −1000 m | the outside edge of snowball estimates; below that the model is doing something no planet did |
| **N3 icehouse share** | 5–70% of the time in an icehouse, and no single icehouse longer than 300 Myr | Earth ~10–30%; wide, because world variety is the point. A permanently frozen or permanently unglaciated planet is possible but should be a world-builder choice (`climate_offset`), not the default |
| **N4 hot eras end** | dT above +8 C for at most 150 Myr at a time | the Mesozoic greenhouse moved within itself; a planet stuck hot is as wrong as one stuck cold |
| N5 onset from the poles (reported) | no ice equatorward of 30° unless ice poleward of 60° existed the update before | Chandler & Sohl 2000; universal in models |
| reported, not barred | the gaps between icehouses (Earth 60 Myr–1.5 Gyr), each era's length and depth, the time below −150/−430 m, flicker eras (one update long) | to watch, not to tune to |

**Multi-seed bar:** ≥ 70% of seeds pass N1–N4 (the owner's rule). The old bar stays in the tables beside it until
stage 3, so changes can be compared.

### 3.4 Bars that stay (from the review's plan, unchanged)
- **Cycles in an icehouse** (the time zoom, Earth L6, index on): cycles 80–120 kyr; maxima ≤ −80 m at a cooling of
  ≤ 6 C; endings give back ≥ 60% of their glacial excess within 15 kyr; interglacial ice 9–12% of land.
- **The zoom as a window on the run** (PW-467, `tools/tz_mean.py`): the zoom's mean after 100 kyr within max(15 m,
  0.25 × swing) of the run's ice, and its iced area within 25%, on ≥ 5 of the 7 suite moments (≥ 6 with option 2).
- **Recovery on a fixed planet** (`tools/ice_probe.py --stair`): today's Earth ice held at dT 0 within 20% of its
  area; a cold era's extra ice ≥ 80% gone within 2 updates of returning to the dT where it started, and the cold leg's
  ice gone at a dT the run can reach (below +6 C: drift 2 sd + a CO2 term the thermostat gives).
- **Unforced zoom start** < 25 m in 20 kyr (the rule check).
- Scorecard and `earth_check` not worse.

### 3.5 Where main stands (checkpoint 0)
- Old bar 8/10, new bar **5/10** (N1–N2–N4 alone 6/10). Fails: deep eras of 160, 200 and 424 Myr (seeds 2, 1, 99), a
  very deep era of 68 Myr (seed 42), and icehouse share 82–100% (seeds 13, 99).
- Icehouse share (≥ 20 m of ice): 26–100%, median 62%. Earth's ~10–30% sits at the low end: A0.
- 2 Gyr runs: both fail only on an icehouse longer than 300 Myr (352, 400 Myr); every deep era ends.

### 3.6 What changes in practice
- A planet with a 40 Myr era at −600 m that ends passes N1 (it failed the old bar). A planet whose −300 m era never
  ends fails N1 (it passed the old bar). This is the owner's "can it come out of it".
- The old −450 m and 2% numbers move from pass/fail to "reported". Depth is still bounded (N2), and the very deep
  limit (60 Myr) keeps snowball-like eras snowball-short.

## 4. The optional recovery lever (design only; a ticket)

The owner: "the longer a deep ice age goes, the more the subsystems nudge real sim behavior until it's guaranteed to
spring out of it with the nudges eased off as it recovers".

### 4.1 The lever's state
- **Cold-era debt** D (dimensionless), integrated every climate update:
  dD/dt = depth(t) − D / τ_ease, where depth = max(0, −sea_ice − 150 m) / 300 m + max(0, iced land share − 0.25)
  (zero in an ordinary icehouse), and τ_ease ~ 20 Myr. So D grows with how deep and how long, and drains once the
  planet is out.
- **Strength** s = recovery × (1 − exp(−D / D0)), with D0 set so that s reaches ~0.63 × recovery after ~50 Myr at
  −450 m. `recovery` is the generation-time parameter (0 off; 0.3 mild; 1 strong; ≥ 1 "guaranteed").

### 4.2 What it pushes on, in order of honesty
1. **CO2 piling up under the ice (physics).** The fix for A3/A4 is the physics. Until it exists, the lever lets the
   CO2 ceiling rise with s (from 3 e-folds toward 6), and lets the carbon "stock" grow at (source − sink) while the
   sink is held down by ice. This is what ended the Cryogenian, so at s ≤ ~0.5 it is a nudge toward what a real carbon
   cycle would do, not a cheat.
2. **Dusty, darker ice (physics).** Volcanic ash and wind-blown dust collect on long-lived ice and darken it (Abbot &
   Pierrehumbert 2010; Le Hir et al. 2010). It acts as a smaller ice-albedo term (× (1 − 0.5 s)) and more melt on the
   sheets (the degree-day factor × (1 + s)). It's real, and it grows with exposure time, which is exactly the lever's
   shape.
3. **Geothermal heat at the bed (physics, weak).** More basal melt and sliding under thick, old ice. Its effect on
   whole-sheet volume is small; it's included only as a small lever (thinner interiors), not a recovery by itself.
4. **A volcanic pulse (world-builder).** A large igneous province's CO2 at a time the lever picks. Real LIPs happen,
   but not on demand: at s > 0.5 this is a control, and the run's events should name it ("a flood-basalt pulse ended
   the ice age").
5. **A brighter star (world-builder).** Only if the planet's star is set up as variable (section 2.4, point 3);
   otherwise it's a pure control.

**Guarantee.** With `recovery` ≥ 1, the lever's combined push is scaled so that, at s = 1, dT's target is at least
the planet's measured exit dT (from the hysteresis probe, or from the era's own start dT + 3 C). So no era lasts beyond
~2 × D0's timescale. The push eases with D after the exit, so the planet isn't then kicked into a hothouse. A mirror
"onset" lever (for planets that never glaciate) would use the same machinery the other way, and is optional.

### 4.3 Default and display
- **Default: off** until A3/A4 (the carbon stock) and stages 1–3 land, because today it would hide the ice model's
  real failure (B2). After that, **mild (0.3)** by default: physics-only (items 1–2), and planets that can't get out
  get a small push their real carbon cycle would give them anyway.
- **Shown to the user:** a "New planet" option "Ice-age recovery: off / natural (default) / assisted / guaranteed",
  with a one-line note for each saying which parts are physics and which are world-building. In the viewer's
  timeline, a thin band under the temperature curve shows when the lever pushed and by how many C, and the run's
  meta records `recovery` and the lever's total push, so a world made with help says so.

### 4.4 Honest limits
- Items 1–2 are physics with uncertain sizes. Items 4–5 are world-builder controls. The lever is a forcing on dT and
  on the ice's melt, not a reset: the ice still has to melt through the ice model.
- With today's B2 (no sheet-wide budget), even a large dT push may not remove a sheet that holds itself up (PW-460's
  experience: honest margins froze). So the lever can't be judged before stage 1–3.

## 5. Stage 0 tools (built; see `docs/review/ice-v2/checkpoint-0.md` for the numbers)
- `planet/tectonics/diag.py` + `tools/ice_diag.py`: opt-in long-run diagnostics, bit-identical runs. Per step: dT's
  terms, CO2 clipped and unclipped, source and sink, sea level's two parts. Per climate update: every sheet's budget
  (snow, melt, sea, net), the ice kept in deficit, the frozen sea, the snow on the ice, the ice's lowest latitude.
  Optional fields (`--fields`) and moment pickles (`--moments`). `--summary` explains each deep era; `--plot`.
- `tools/ice_criteria.py`: the bars above (old and new) on any `ice_diag` or `sealevel` output; health uses it too.
- `tools/tz_mean.py`: PW-467's window mean against the run on the moment suite.
- `tools/ice_probe.py --stair`: the hysteresis staircase on Earth or any moment.
- Run frame stats now store `sea_ice_m` and `sea_tect_m`; `tools/health.py` has a basin-term envelope and the new ice
  columns; `tools/sealevel.py --run` reads the two parts.

## References
- Abbot, D. S. & Pierrehumbert, R. T. (2010). Mudball: surface dust and Snowball Earth deglaciation. JGR 115, D03104.
- Abbot, D. S., Voigt, A. & Koll, D. (2011). The Jormungand global climate state and implications for Neoproterozoic
  glaciations. JGR 116, D18103.
- Bao, H., Lyons, J. R. & Zhou, C. (2008). Triple oxygen isotope evidence for elevated CO2 after a Neoproterozoic
  glaciation. Nature 453, 504–506.
- Bekker, A. et al. (2004). Dating the rise of atmospheric oxygen. Nature 427, 117–120.
- Budyko, M. I. (1969). The effect of solar radiation variations on the climate of the Earth. Tellus 21, 611–619.
- Caldeira, K. & Kasting, J. F. (1992). Susceptibility of the early Earth to irreversible glaciation caused by
  carbon dioxide clouds. Nature 359, 226–228.
- Chandler, M. A. & Sohl, L. E. (2000). Climate forcings and the initiation of low-latitude ice sheets during the
  Neoproterozoic Varanger glacial interval. JGR 105, 20737–20756.
- Donnadieu, Y. et al. (2002, 2003). Is high obliquity a plausible cause for Neoproterozoic glaciations? GRL 29;
  Ice dynamics of a Snowball Earth, Climate Dynamics / GRL.
- Evans, D. A., Beukes, N. J. & Kirschvink, J. L. (1997). Low-latitude glaciation in the Palaeoproterozoic era.
  Nature 386, 262–266.
- Feulner, G. (2012). The faint young Sun problem. Rev. Geophys. 50, RG2006.
- Fielding, C. R. et al. (2008). The Late Paleozoic Ice Age: a review. GSA Special Paper 441.
- Finnegan, S. et al. (2011). The magnitude and duration of Late Ordovician–Early Silurian glaciation. Science 331,
  903–906.
- Gough, D. O. (1981). Solar interior structure and luminosity variations. Solar Physics 74, 21–34.
- Gumsley, A. P. et al. (2017). Timing and tempo of the Great Oxidation Event. PNAS 114, 1811–1816.
- Haq, B. U. (2014). Cretaceous eustasy revisited. Global and Planetary Change 113, 44–58; Haq & Schutter (2008),
  Science 322, 64–68.
- Held, I. M. & Soden, B. J. (2006). Robust responses of the hydrological cycle to global warming. J. Climate 19.
- Hoffman, P. F. et al. (2017). Snowball Earth climate dynamics and Cryogenian geology-geobiology. Science Advances
  3, e1600983.
- Inglis, G. N. et al. (2020). Global mean surface temperature and climate sensitivity of the EECO, PETM and latest
  Paleocene. Climate of the Past 16, 1953–1968.
- Lambeck, K. et al. (2014). Sea level and global ice volumes from the Last Glacial Maximum to the Holocene. PNAS 111.
- Le Hir, G. et al. (2008, 2010). The snowball Earth aftermath; Snowball Earth termination by dust. EPSL / GRL.
- MacLennan, S. et al. (2018). The arc of the Snowball: U-Pb dates constrain the Islay anomaly and the initiation of
  the Sturtian glaciation. Geology 46, 539–542.
- McInerney, F. A. & Wing, S. L. (2011). The Paleocene-Eocene Thermal Maximum. Annu. Rev. Earth Planet. Sci. 39.
- Montañez, I. P. & Poulsen, C. J. (2013). The Late Paleozoic Ice Age: an evolving paradigm. Annu. Rev. Earth Planet.
  Sci. 41, 629–656.
- Page, A. et al. (2007). Were transgressive black shales a negative feedback modulating glacioeustasy in the Early
  Palaeozoic Icehouse? Geol. Soc. London.
- Pierrehumbert, R. T. (2004). High levels of atmospheric carbon dioxide necessary for the termination of global
  glaciation. Nature 429, 646–649.
- Pollard, D. & Kasting, J. F. (2005). Snowball Earth: a thin-ice solution with flowing sea glaciers. JGR 110.
- Prave, A. R. et al. (2016). Duration and nature of the end-Cryogenian (Marinoan) glaciation. Geology 44, 631–634.
- Pu, J. P. et al. (2016). Dodging snowballs: geochronology of the Gaskiers glaciation. Geology 44, 955–958.
- Rooney, A. D. et al. (2015). A Cryogenian chronology: two long-lasting synchronous Neoproterozoic glaciations.
  Geology 43, 459–462.
- Rygel, M. C. et al. (2008). The magnitude of Late Paleozoic glacioeustatic fluctuations. J. Sed. Res. 78.
- Scotese, C. R. et al. (2021). Phanerozoic paleotemperatures. Earth-Science Reviews 215, 103503.
- Sellers, W. D. (1969). A global climatic model based on the energy balance of the earth-atmosphere system. J. Appl.
  Meteor. 8.
- Tierney, J. E. et al. (2020). Glacial cooling and climate sensitivity revisited. Nature 584, 569–573; Tierney et al.
  (2022), Spatial patterns of climate change across the PETM, PNAS 119.
- Voigt, A. & Marotzke, J. (2010). The transition from the present-day climate to a modern Snowball Earth. Climate
  Dynamics 35, 887–905.
- Walker, J. C. G., Hays, P. B. & Kasting, J. F. (1981). A negative feedback mechanism for the long-term stabilization
  of Earth's surface temperature. JGR 86, 9776–9782.
- Westerhold, T. et al. (2020). An astronomically dated record of Earth's climate and its predictability over the
  last 66 million years. Science 369, 1383–1387.
- Yang, J., Peltier, W. R. & Hu, Y. (2012). The initiation of modern "soft Snowball" and "hard Snowball" climates in
  CCSM3. J. Climate 25.
- Young, G. M. (2013). Precambrian supercontinents, glaciations, atmospheric oxygenation, metazoan evolution and an
  impact that may have changed the second half of Earth history. Geoscience Frontiers 4.
- Zachos, J. C. et al. (2005). Rapid acidification of the ocean during the PETM. Science 308, 1611–1615.

Citations are from my knowledge of the literature and weren't re-checked online in this session; durations and CO2
levels carry the uncertainty ranges given, and a few page numbers may be off.
