# Events for the peoples: droughts, quakes, plagues, culls (lane 85, 2026-10-31)

Design only. No model code was changed. Builds on lane 82's counter-pressures design
(`docs/review/peoples-counterpressures/design.md`, tickets PW-1165 plug, PW-1166 famine, PW-1167 epidemics, PW-1171 drought rate,
PW-1172 war) and answers the owner's asks of 10-31. Read main e03eb572.

## In plain words

**Owner rulings taken as given (10-31):** "virgin soil" epidemics stay off. Portals keep a fixed arrival size for now.

1. **An events system: chance, but chance that changes the world.** Every event is drawn by dice, but the dice say *when* and *how big*.
   *Where* comes from the physics already in the planet: droughts where the climate is semi-arid and touchy, quakes on the plate edges
   the run already has, eruptions at its live volcanoes, plagues in crowded towns. And an event doesn't float free. A drought is a patch
   of the recent climate itself: for its two hundred years the rain the viewer shows, the food the peoples get and the towns that empty
   all read the same lowered rain. So "let's mold the climate round this area, it's a rough half-millennium for them, shame" is
   exactly how it works, whether the dice place it or you do.
2. **Rates come from real records.** A well-recorded region gets a drought decades to centuries long every few hundred years
   (California and Nevada: two, of 212 and 177 years, between 862 and 1299 CE). A Spanish-flu-sized epidemic comes 0.3–1.9% of years.
   Worldwide there are about 14 magnitude-7 earthquakes a year, and a VEI-7 eruption every 500–1,000 years.
3. **Our droughts are far too rare: a region spends 30 to 125 times less of its time in drought than a real one, and sees 100 to
   1,000 times fewer.** Filed as a v2 physics draft.
4. **The brake on fast breeders: you're right that it can be deaths, if they're the right deaths.** Kobolds and goblins already breed
   fast to make up for heavy losses: that's what their "harsh" life table is. Make those losses depend on where they live. Pressed
   against peoples who hate them, they lose more; deep in their own hills, fewer. Half again the usual losses cuts a kobold
   frontier to 65%, double cuts it to 31%. Elves and dwarves don't have those losses, so they aren't touched. On top of that,
   **culling wars**: when goblins crowd a hostile border, the neighbours hunt them down to 40%, and they bounce back. On average it's
   the same dent for any people (about 28% on the culled ground), so slow peoples can't be wiped out by it. Honest limit: where kobolds
   hold a mountain range alone, there's nobody to raid or cull them, and only their density (D20) shrinks them.
5. **Dwarves shrug off plague.** Each people gets a `disease_resist` from 0 to 1, passed down the tree like its body. Dwarves get 0.5:
   half the plague deaths. Resistant peoples still *carry* plague, so dwarven trade roads can bring it to the humans.
6. **Portals, later:** arrivals as a random trickle year by year that averages out to the set number over a few thousand years.
7. **A short paper to write, not to decide yet:** should elves and dwarves have more children, or simply be 2–4% of people?

## Decisions (each: options and a lean)

**E1. Where do events come from?**
1. Pure dice: a rate per kind, placed anywhere on land.
2. Physics-placed dice: the dice set timing and size, and the planet's own fields set the place and the odds there (the climate's
   sensitivity, plate edges, live volcanoes, crowd-disease towns).
3. Fully simulated: weather and ocean modes, fault stress, epidemics as contagion models.

*Lean: 2.* Real megadroughts are mostly the climate's own internal noise. Cook et al. 2016's review says models make them
"through (1) internal atmospheric variability, (2) sea-surface temperatures, and (3) land surface and dust aerosol feedbacks", so
chance is the honest model. Option 3 is v3 or never at century steps.

**E2. How does an event couple back?** Three channels, and nothing else:
- (a) **climate fields**: droughts, cold spells, eruption winters are recent-pass `Episode`s, so the stored frames, the peoples, the
  settlements and the brief all read the same rain;
- (b) **carrying capacity**: plague, famine, war, culls are lane 82's `kept` and depletion `d` on each people's K (PW-1165);
- (c) **the event log**: every event is logged with place, size and who lost what. That's what the viewer and brief show, and what
  the settlements' fall reasons (PW-1108) read.

*Lean: exactly these three.* An event that changes nothing in (a) or (b) is a story item only (most earthquakes, below).

**E3. Brake on fast breeders (updates D22 question 1).**
1. Land, not deaths (lane 82's lean): war-torn fields, plague-emptied towns, drought famine. All act on K.
2. **Raid losses**: the harsh peoples' extra deaths vary with where they live (hostile frontier up, safe heartland down).
3. **Culling wars**: event pulses when a raiding people crowds a hostile border. It's cut to 40% there and bounces back at its own
   pace.
4. A flat extra death rate for everyone. *Rejected:* 1%/yr of extra disease leaves kobolds 92% and elves extinct (table below).

*Lean: 1 + 2 + 3.* Option 1 stays the general thermostat for dense humans; 2 and 3 are the "too many goblins" brake. They're built as one
"raiders" mechanism. Kobold numbers where they hold land alone stay a density question (D20, lever 3).

**E4. Disease resistance.**
1. `disease_resist` (0..1) per line, inherited like the body, scaling plague and epidemic losses by (1 − resist).
2. A `resilient` trait with a fixed 0.5.
3. Lane 82's `plague_x` multiplier (cultural, not inherited).

*Lean: 1, replacing `plague_x`.* Dwarves 0.5, warforged-like constructs 1. It's one field, so the duergar inherit it.

**E5. Portal stream (later; fixed size now, by ruling).**
1. Fixed waves (today).
2. A compound-Poisson trickle per portal with the same long-run total.
3. The trickle with a slow "open / quiet" rhythm (bursty).

*Lean: 2 once D21's numbers are sane, 3 with wandering thinnings.*

**E6. Slow breeders' share.** Not for deciding. See the paper outline at the end; the owner picks once it's written.

## 1. The events system

### Kinds, sources, rates, footprints

Rates are per Earth-like planet unless stated. "Read" means fetched and read by this lane. Lane 82's sources were not re-read and are
marked so.

| Kind | Placed by (physics) | Rate (sourced) | Footprint and length | Couples via |
|---|---|---|---|---|
| Megadrought | recent pass; weighted to where the model's rain is most sensitive (draft below), today uniform on land < 50° | a region in drought decades-to-centuries long every ~150–500 yr; California–Nevada 862–1074 and 1122–1299 CE (Cook et al. 2016, read); "200-300 year" 4.2 ka megadrought, "30-50% reduction in precipitation" (Weiss 2016, read) | radius 500–2,500 km; 10–300 yr (Cook: "durations longer than a decade"); rain ×0.5–0.8 | (a) rain; (b) famine K × (rain ratio)^e (PW-1166) |
| Cold spell | recent pass (as today) | today's rate; no new source read | as today | (a) |
| Eruption winter | live volcanoes of the world's table (`volcanoes`, `active`) | VEI 6 every 50–100 yr, VEI 7 every 500–1,000 yr, "at least 10" VEI-7 in the last 11,700 yr (Wikipedia "Volcanic explosivity index", read) | local: ash K-dent within a few hundred km (UNVERIFIED size, judgement 300 km, 1 step); VEI 7: a global cold spell, size UNVERIFIED, years long so below the century step (story + a 1-step cold Episode) | (a) + (b) local |
| Earthquake | converging plate boundary cells (`plate_boundary` = +1, static in the recent run) | worldwide 2000–2021: ~1.2 M8+ and ~13.8 M7–7.9 a year (USGS "Lists, maps and statistics" table, read; means our arithmetic) | one cell; instant | (c) only, plus a settlement fall reason "earthquake" (PW-1108). Demographically invisible at century steps (judgement) |
| Epidemic / plague | carrier peoples' town cells (lane 82, PW-1167) | Spanish-flu-intensity yearly probability "between 0.27 and 1.9% from 1600 to present"; COVID-like "average recurrence time of 59 y"; 395 epidemics 1600–1945 in their set (Marani et al. 2021, PNAS, read via PMC). Black Death ~40% mean (Jedwab et al., lane 82, not re-read) | lane 82: corridor-connected carriers within 4,000 km | (b) pulse d + era hazard, × (1 − disease_resist) |
| Virgin soil | contacts | **off (owner 10-31)** | n/a | n/a |
| Famine | drought episodes (not its own dice) | follows the drought rate | the drought's cap | (b) |
| War, times of troubles | crowding, frontiers (lane 82, PW-1172) | Turchin's 2–3 century cycles (lane 82, not re-read) | per cell | (b) |
| Cull (new) | raiding peoples crowded on hostile frontiers (section 2) | state-triggered, ×0.5 chance per step | the frontier component | (b) pulse d |

Effects by life stage (the stage weights the K cut is computed with, lane 82's `kept` = r′/r):
- **Disease:** all stages. Gurven & Kaplan 2007 (read, pp. 341–343): "Illness accounts for over half of the deaths in all groups except
  among pre-contact Ache".
- **War:** mostly adult men. Gurven & Kaplan: homicide is "affecting adult males disproportionately". Lane 82's weights stay
  (0.1, 0.3, 1, 0.3).
- **Raids and culls:** heavier on the young. A lair raid kills the brood (judgement weights 0.6, 1, 1, 0.3). Gurven & Kaplan:
  "accidental and violent deaths account for 4–69 percent (average 19 percent) of all deaths".
- **Famine:** infants and elders heavier (judgement 1, 0.5, 0.5, 1; no source read).
- **Migration:** a struck people's lost cells add to its `crowd`, so it jumps (lane 82, phase 2). A drought adds a pull to rivers
  (PW-1166). A cull adds nothing: the hunted don't move, they die and refill.

### Determinism and seeds
- **Draw the schedule up front, place it at run time.** Each kind has its own generator, `default_rng((seed, EVENT_SALT[kind],
  try))`. It draws every event's time and size before the history runs. Placement reads the state at that step (the most crowded
  town, the live volcano). So adding a people never moves a drought, and the same seed always gives the same droughts.
- **Climate events belong to the recent pass's seed** (`RecentParams.seed`, as today), not the tree's. Every tree on one world then
  shares its weather.
- `meta.events_seed` (default: the tree seed) rerolls the luck alone. In the viewer it's a "reroll the bad years" button.
- **Authored events never reroll.** They are:
  - climate ones as `RecentParams.authored` episodes: the recent run is re-saved, which is cheap because the full climates are cached
    in `recent_rain.npz`;
  - peoples ones as `[[event]]` rows (PW-756's anchor table, with the new kinds `plague`, `cull` and `drought`, a place, and
    optionally a `span`).

### How it shows in the viewer (the owner uses the viewer, not the CLI)
- **On the time slider,** an events track: a small mark per event, coloured by kind, and a band for droughts and plague eras.
- **On the map,** the footprints of the events live at the current frame. The rain layer already shows a drought, since the recent
  frames store it. Click one for its line: "Drought over the Kessel lands, 220 years, rain down 40%. The halflings lost 30% and
  fell back to the rivers."
- **In the peoples tab,** "lost to" bars per people: drought, plague, war, culls.
- **Controls:** "Bad years" (rare = today / Earth-like / harsh), "How often plagues strike" (early, late), "How warlike" (lane 82),
  "How hard peoples hunt raiders" (early, late), "Reroll the luck", and **"Place a drought here"** (pick a centre, a radius, years and
  strength). The last one is the owner's "rough half-millennium for them, shame" button.

## 2. Fast breeders: raid losses and culling wars

**Why deaths usually fail, and when they don't.** For any extra hazard, the share a people keeps is r′/r (lane 82). A hazard that
is the same for everyone hits slow breeders first. Recomputed here on `life_history.table` (scratch `l85/s/kept.py`), with r the
forager growth rate per year:

| People | r | +1%/yr all stages | +2% | +4% | hazard = c × own r, c = 0.25 |
|---|---|---|---|---|---|
| human | 4.40% | 0.77 | 0.55 | 0.09 | 0.75 |
| kobold | 13.3% | 0.92 | 0.85 | 0.70 | 0.75 |
| goblin | 13.6% | 0.93 | 0.85 | 0.71 | 0.75 |
| orc | 6.8% | 0.85 | 0.71 | 0.41 | 0.75 |
| dwarf | 1.73% | 0.42 | 0 | 0 | 0.75 |
| elf | 0.47% | 0 | 0 | 0 | 0.75 |

The last column is the key. A hazard proportional to a people's own r costs every people the same share. The owner's picture
("lil' cuties that make up for terrible losses with faster reproduction") is exactly that. Kobolds and goblins have `survival =
"harsh"` (lane 76/78: a quarter reach adulthood, +5%/yr adult deaths), and their fecundity is closed on it. Their high r *is* their
high losses.

**Raid losses (E3 option 2).** On each held cell, scale the harsh excess (the harsh schedule minus the normal one) by a raid factor:
`R = R_SAFE + (R_FRONT − R_SAFE) × F × (1 − town)`. Here F is lane 82's hostile-frontier share (neighbours held by peoples the
cohabitation matrix puts under 0.5), and `town` is 1 on town cells (walls protect). The fecundity stays closed at R = 1, the
reference condition.

| Raid factor R | 0.5 | 1 (today) | 1.5 | 2 |
|---|---|---|---|---|
| kobold kept | >1 (grows faster, capped at K) | 1 | 0.65 | 0.31 |
| goblin kept | >1 | 1 | 0.70 | 0.41 |

- Normal-survival peoples (humans, elves, dwarves) have no harsh excess, so R does nothing to them, by construction.
- Defaults (judgements, to screen): R_SAFE 0.7, R_FRONT 2.0, and `raids` = true for harsh peoples. A line can set `raids = false`
  (a peaceable kobold tree).
- This lives in lane 82's `kept` channel (PW-1165), as a K multiplier per cell.

**Culling wars (E3 option 3).** At a step, a raiding people's frontier component is a cull site when:
- it is crowded (p ≥ 0.8 K);
- it borders hostile peoples (F ≥ 0.3);
- the hostile peoples there outnumber it in people.

With chance 0.5 a step (judgement), the neighbours cull it: a depletion d = 0.6 (cut to 40%) on that component, all stages, weighted
to the young. It recovers as lane 82's `d ← d × exp(−dt / (RECOVER_YR / x))`, and a new cull can come once d < 0.1. That's a sawtooth.
Its time-average is r-neutral: d(t) = 0.6 e^(−t/τ), the next cull at τ ln 6, mean d = 0.6 (5/6) / ln 6 = **0.28 for any people**
(our arithmetic). The pace is what differs:
- kobolds (x ≈ 3, τ ≈ 17 yr) are culled every few decades and bounce back;
- elves (x ≈ 0.11, τ ≈ 450 yr) would be culled once in many centuries, if they ever raided, and they don't.

A fast breeder's sawtooth is quicker than the century step. So the step applies the mean (0.28) and logs one "cull" event. Slow ones
are stepped explicitly. Era dials `cull_early` / `cull_late` (0, 0.5, 1, 2) scale the 0.6 and the chance.

**Comparison with D22's "land, not deaths".**

| | Land (lane 82) | Raid losses + culls |
|---|---|---|
| Who it bites | the crowded and stateless, mostly dense farmers (humans) | the raiding fast breeders where they meet enemies |
| Spares slow peoples | yes (they're sparse) | yes (no harsh excess; the culls are r-neutral and they don't raid) |
| Fits life history | yes | yes: the losses their fecundity already pays for, made local |
| Story | fields abandoned, towns emptied | "too many goblins, hunt 'em down", then the bounce-back |
| Kobolds alone in their range | no effect | no effect (pushback: that's D20 density) |

*Lean: both.* They hit different peoples and share one channel.

## 3. Disease resistance

- **Spec.** `disease_resist = 0.5` on the dwarf `[[lineage]]` row. It's a float 0..1, default 0, added to the inherited body keys
  (like `limits`), so splits and groups carry it unless they set their own. A hybrid takes its parents' mean.
- **What it does.**
  - A plague pulse's loss on a cell is `L × (1 − resist)`, and so is the pandemic era's recurrence hazard. With lane 82's table,
    dwarves in a struck town keep 86% at 0.25%/yr, against 71% unresisted.
  - Famine and war are not touched.
  - Carrier status is unchanged: a resistant crowd still carries the disease. Mild cases travel, which is a plot hook.
  - It does not move any growth rate: the schedules already hold the endemic load.
- **Source of the idea.** 5e's Dwarven Resilience: "You have advantage on saving throws against poison, and you have resistance against
  poison damage" (roll20 compendium, read). Extending it to disease is the owner's call of 10-31, not canon.
- It replaces lane 82's `plague_x`. Undead and constructs: 1.

## 4. Portal arrivals as a stream (sketch, not now)

- **The stream.** An arrival with `founders` N over a stream of S kyr gets a mean of μ = N / S per year. Each portal opens at Poisson
  times, λ a year, and each opening brings a batch: lognormal, sd 1 in log (judgement), with mean μ / λ / portals.
- **Per step.** Over a step of dt years, the count is Poisson(λ dt). The total is drawn as a gamma with that many batches' mean and
  variance (a cheap compound-Poisson draw).
- **How it averages out.** The coefficient of variation over a window T is about sqrt((1 + CV_b²) / (λ T)) (our arithmetic). At
  λ = 0.01 a year and CV_b ≈ 1.3, a century swings ±170% and 5 kyr ±24%: "random per year, standard over longer periods".
- **Founding.** Arrivals pool at their portal until they reach `viable_pop` (500 in dnd), then `found_people` sets them down. A
  trickle never fades as one-family patches.
- **Determinism.** One generator per (seed, plane, portal).
- **Variants.** Bursty (option 3): λ follows the wandering thinnings' open and close, so arrivals cluster while a thinning stands over
  good land.

## 5. Paper outline: are long-lived slow breeders few after conflict?

The question: should elves and dwarves breed more, or be about 2–4% of people?

**For "few":**
- Numbers at full land are density × land, not r (lane 76). But every disturbance (plague, war, drought, culls) costs slow peoples
  more, or longer: lane 82's table, and the recovery time 1/x.
- Lane 73's first-come advantage then lets the fast refillers keep what the slow ones lost. In a disturbed world, slow breeders end up
  on less land.
- Canon describes both as old, declining peoples.

**For "more children":**
- With an elf `breeding` of "mammal" (Rmax 3.5 per generation, like every other mammal; Ginzburg et al. via life_history.py), elf r
  goes from 0.47% to 0.86%/yr. With a fertile window of 100–130 it's 1.09%/yr (scratch, our computation).
- That halves their losses to any pulse and stays inside canon ages. "Slow 2" is lane 76's judgement, not a source.

**The test:** run the lane 77 suite with the events on, elves and dwarves at slow vs mammal breeding, and read their median share
against the owner's 2–4%. Write it up as a short cited note (`docs/review/peoples-slow-breeders/`) before any change.

## Lane plan (after PW-1165's plug merges)

1. **The plug (PW-1165)** first: `planet/lineages/history/counter.py`, `kept` and `d`, the `lost` output.
2. **Events schedule:** `planet/lineages/history/events.py` grows a `schedule(seed, kind, try)` per kind, drawn up front and logged.
   Placement hooks for plague towns (PW-1167), culls, quakes and eruptions:
   - quakes and eruptions read `plate_boundary` (already a static layer of the recent run) and the per-frame `volcanoes` list
     (already in the recent frames);
   - settlements get "earthquake" and "ash" as fall reasons (`settlements.py`).
3. **Raids and culls:** `counter.py`, with the R factor on the harsh excess (via `life_history.table` with a `mortality` override, cached
   by rounded R) and the cull sawtooth. In `spec.py`: `raids` (bool, default true where survival is harsh) and the meta keys
   `cull_early` / `cull_late`.
4. **Disease resistance:** `spec.py` `disease_resist` (inherited body key), used in the plague code. `dnd.toml`: dwarf 0.5.
5. **Authored events:** `RecentParams.authored`, plus `reputation.parse_events` kinds drought / plague / cull. Viewer: events track,
   footprints, "lost to" bars, controls (section 1).
6. **Droughts:** PW-1171 and the physics draft below (climate lane, separate).
7. **Tests** (`tests/test_lineages.py` or a new `tests/test_lineages_events.py`):
   - the same seed gives the same schedule, and adding a people leaves the climate schedule unchanged;
   - R does nothing to normal-survival lines;
   - R = 1.5 / 2 reproduce kept 0.65 / 0.31 for kobolds;
   - the sawtooth mean is 0.28 whatever x is;
   - disease_resist 0.5 halves a pulse;
   - a stream's mean over 50 kyr is within 5% of `founders`.
8. **Judge on `tools/peoples_robust.py`**, arms off / default / ×2 for each of raids, culls and plague, per lane 82's pass list:
   invariants; the slow-breeder trap stays shut (elf, dwarf, gnome medians not below off); kobold and goblin median share falls; the
   brittle count is no worse; and each kind's events land and flip some cells (a pulse that flips nothing is flagged). Lane test
   policy: not-slow and area tests in the lane, the full suite at merge.

## Sources read by this lane
- Cook et al. 2016, "North American megadroughts in the Common Era", *WIREs Clim Change*, doi:10.1002/wcc.394
  (https://ocp.ldeo.columbia.edu/res/div/ocp/drought/PDFS/Cook_etal_2016.pdf; read: abstract, the definition, the section "Megadroughts in the paleoclimate record").
- Weiss 2016, *PAGES Magazine* 24(2):62–63
  (https://leilan.yale.edu/sites/default/files/publications/article-specific/weiss_2016_pagesmagazine_20162_62-63_weiss.pdf).
- Marani et al. 2021, "Intensity and frequency of extreme novel epidemics", *PNAS*
  (https://pmc.ncbi.nlm.nih.gov/articles/PMC8536331).
- USGS Earthquake Hazards, "Lists, Maps, and Statistics", Worldwide Earthquakes 2000–2021 table
  (https://www.usgs.gov/programs/earthquake-hazards/lists-maps-and-statistics).
- Wikipedia, "Volcanic explosivity index" (https://en.wikipedia.org/wiki/Volcanic_explosivity_index), its frequency column.
- Gurven & Kaplan 2007, "Longevity among hunter-gatherers", *PDR* 33:321, causes of death p. 341–343
  (https://gurven.anth.ucsb.edu/sites/secure.lsit.ucsb.edu.anth.d7_gurven/files/sitefiles/papers/GurvenKaplan2007pdr.pdf).
- roll20 5e compendium, Dwarf (https://roll20.net/compendium/dnd5e/Dwarf), Dwarven Resilience.
- Promislow & Harvey 1990, "Living fast and dying young", *J Zool* 220:417. UNVERIFIED: only search summaries were found (high
  mortality goes with early maturity and large litters). It's the idea behind section 2, not a number.
- In-repo: `planet/lineages/recent.py` (variability), `life_history.py`, `history/portals.py`, `history/founding.py`, `spec.py`,
  `reputation.py` (`[[event]]`), `samples/dnd.toml`; lane 82's design. Lane 82's sources (Jedwab, Turchin, Koch, OWID) were not re-read.
