# Counter-pressures on the peoples: war, epidemics, famine, predation, and the droughts question (lane 82, 2026-10-30)

Design and research only. No model code was changed. Lanes 77, 78 and 79 are still mid-flight in the history code, so nothing here gets built
until they land. Relates to PW-917 (life-history counter-pressures), PW-1108 (settlements sacked and razed), PW-661 (civilization
simulation, v3), PW-1068 (dragon pressure) and PW-1147/1148 (lane 78's growth rates and life stages).

## In plain words

**The drought question.** The owner asked: do climate runs at the finest timescales ever show droughts like the real ones? The answer is no.
- **The climate model makes no droughts of its own.** It computes an average climate. Over the last 30,000 years it is computed every
  2,000 years and blended in between. All droughts come from the recent pass's dice.
- **The dice are too stingy.** They roll about two droughts per 30,000 years for the whole planet. On Earth, one well-recorded region
  sees a drought decades to centuries long every few hundred years. Ours are therefore hundreds of times too rare.
- **Size and depth are Earth-like** (rain cut by a quarter to a half, 1,500–3,000 km across). Our droughts run a little long: 200–800
  years, against 50–300 for the real ones read.
- **When a drought does hit, peoples do not move.** They thin out at the dry edge of their country and fill back in afterwards.
  Nothing makes them pack up for the rivers, or pushes herders into farmers' land, the way the 4,200-year-ago drought did in the Near East.
- **The steppe dry spells of Yamnaya and PIE times** were long, regional and moderate in the steppe records read, not sudden
  catastrophes. Our model would give a given steppe such a drought in the Holocene only about once in 30 worlds.

**War and plague as a thermostat.** Here is the honest finding.
- **Extra deaths keep down slow breeders, not fast ones.** Lane 78's life tables show it plainly. If war kills an extra 0.5% of adults a
  year:
  - humans keep 94% of their numbers;
  - kobolds keep 98%;
  - dwarves keep 86%;
  - elves keep 46%.

  An extra 1% a year of disease, across all ages:
  - humans keep 77%;
  - kobolds keep 93%;
  - dwarves keep 42%;
  - elves die out.

  A naive "war and plague" term would therefore wipe out the elves long before it dented the kobolds. This is textbook ecology: a fast
  breeder is held down by food and land, not by deaths.
- **War deaths fall mostly on young men.** Births depend mostly on women, so war's deaths matter even less than the figures above suggest.
- **What does work is taking away land, briefly or for a while.** Three mechanisms do this:
  - **Plague.** It strikes the densest, most town-bound, best-connected peoples, so mostly the humans. A plague wave halves a people's
    hold on its towns for a century or so. Neighbours move into the gap, and the model's strong first-come advantage (lane 73) lets
    them keep part of it. The humans recover their numbers quickly, but not all their land.
  - **Internal war.** This is Turchin's "secular cycles": crowded farming states fall into civil war and banditry. In crowded country
    it lowers how many people the land can feed (fields abandoned, people pulled back to strongholds).
  - **Famine.** A drought should cut the food the land gives, not just shift where a people is comfortable.
- **"Virgin soil" epidemics cut the other way.** When a crowd-disease people first meets a people that has never had those diseases, the
  newcomers lose up to 90% (the Americas after 1492). That helps the dense farmers spread, the opposite of a thermostat. It belongs in the
  model for story and realism, not as a brake on humans.

**What this design offers.** Every counter-pressure enters at one place, as a cut to a people's carrying capacity on each cell (K). Each
has a per-era dial in the viewer, like the dragon pressure ("how hard"; early and late eras). Each is reported per people as "share lost
to war, plague, famine". Nothing forces a share: a people's numbers fall only where the land is crowded, struck or dry. Lane 78's
min/max share bands remain the owner's direct lever if a share must land in a range.

## (a) The drought answer

### How the model treats droughts today
Read from `planet/lineages/recent.py` and the history (`history/steps.py`, `model.py`, `habitat.py`, `competition.py`) on main 4d05c438.

**What the climate gives.** `climate.py` describes itself as a "toy climate", a mean-state model with no weather and no interannual
variability. The recent pass runs `climate.compute` on the time zoom's frames at least `climate_every` = 2 kyr apart and interpolates
linearly between them (`Pass._climate`, `_rain_at`). Slow changes from orbit and ice can therefore appear. Abrupt century-scale events
cannot.

**The seeded variability** (`RecentParams`, `_variability`):
- **Global noise.** A red-noise global temperature anomaly, sd 0.35 C with a 0.3 kyr memory. Rain scales with it as exp(0.07 dT),
  about ±2.5%: no drought.
- **Regional episodes.** Poisson at `episodes_per_kyr` = 1/6 for the whole planet; 55% are cold spells and 45% droughts.
  - A drought lasts 0.2–0.8 kyr, with 50-year ramps.
  - It is centred on land within 50° of the equator.
  - Its cap has a radius of 1,500–3,000 km, cosine-tapered, so it is at half strength within half the radius.
  - Rain at the centre is ×0.5–0.75.
- **Expected count.** Over a 30 kyr window that is 5 episodes, about 2.25 of them droughts, for the whole planet (our arithmetic from
  the code).

**How the history uses a drought.** The recent steps call `ps.fields(t)` with the variability on. The drought multiplies
`precipitation`, which enters a people's habitat only through its climate fit: `habitat._fit`, a soft window in log2 rain, one octave
wide. That changes K. Then `_advance` sets `p = min(p, K)`.

**What follows from that:**
- **At the dry margin of a people's rain range,** K falls and its presence falls with it, at once.
- **Inside its range,** a ×0.6 rain cut (−0.7 octave) hardly changes the fit.
- **Density is unchanged.** It comes from the static present-day productivity (`prey.people_fields`, "static: the present's land"),
  so a drought never cuts the food a held cell gives.
- **No directed move.** There is no habitat tracking, no pull toward rivers, and crowding (which drives jumps) is not raised.
- **Rivals with drier niches gain room** where the drought people's K fell. Herders against farmers is the one real shuffle the
  model has.
- **After the drought** the people refills by ordinary spread.
- **Settlements** (`settlements.py`) abandon a site as "drought" when rain is 25% or more below its founding rain.
- **The brief** (`brief.py`) lists droughts among a culture's "bad years".

### Real events against our episodes

| Event | Where, how big | How long | Rain change | Source (read) |
|---|---|---|---|---|
| 8.2 ka event | Greenland, Europe; "many parts of the Northern Hemisphere tropics became drier"; multi-continent | "about 150 years" | Greenland −3.3 C within two decades; Europe about −1 C "for a century or more"; tropics drier (methane −10–15%) | NOAA NCEI Paleo Perspective "Post-Glacial Cooling 8,200 Years Ago" (2021), citing Thomas et al. 2007 and Kobashi et al. 2007 |
| 5.9 ka event | N Africa, Arabia | not settled | not read | only secondary summaries found (search results); no figure used |
| Steppe aridity, end of the Atlantic period / early Yamnaya (mid-4th millennium BC) | Cis-Ural steppe | "long arid epoch" (period scale, centuries) | not quantified | Khokhlova et al. 2018, *Eurasian Soil Science* 51:506, via the indo-european.eu summary (abstract and excerpts) |
| 4.2 ka megadrought | "from the Mediterranean to east Asia and Australia", Africa, the Americas; densest in the Mediterranean westerlies belt, Aegean to Iran | 4.2–3.9 ka, "ca. 300-year" (Weiss); 4.3–3.8 ka defined by Bini et al., with timing uncertain | "estimated 30-50% reduction in precipitation delivered by the Mediterranean westerlies" | Weiss 2016, *PAGES Magazine* 24(2):62–63; Bini et al. 2019, *Clim. Past* 15:555 |
| 4.2 ka in the East European steppe | steppe zone | end of the 3rd millennium BC | "climatic fluctuation scale... was not so high"; winter rain down, summer rain up | Borisov et al. 2022 (abstract), *Vestnik VolGU* 21(2) |
| 4.2 ka, contested | N Mesopotamia, three Syrian sites | — | isotopes show "no indication of disruption" | Sołtysiak & Fernandes 2021, *Antiquity* 95:1145 (abstract) |
| Medieval "Stine" megadroughts | California–Nevada | 243 and 178 yr | (PDSI, not rain) | Cook & Seager, "Megadroughts in North America" (JQS manuscript, Lamont), p. ~10 |
| Mississippi Valley megadroughts | Mississippi Valley | 46, 148 and 61 yr, all within AD 900–1400 | (PDSI) | Cook & Seager, as above |
| Dust Bowl | 77% of the coterminous US in 1934 | 7–12 yr by definition | (PDSI) | Cook & Seager, as above |
| **Ours (recent.py)** | one cap of radius 1,500–3,000 km, half strength within 750–1,500 km | 200–800 yr | ×0.5–0.75 at the centre | code |

The verdict follows, with the arithmetic labelled. The land area is a judgement: about 100 Mkm² of Earth-like land within 50° of the
equator.

- **Depth: Earth-like.** ×0.5–0.75 matches Weiss's 30–50% for the strongest well-resolved event.
- **Size: Earth-like for the big ones.** The half-strength core is 1.8–7.1 Mkm², the full cap 7–28 Mkm². That is the westerlies-belt or
  Dust-Bowl scale. Smaller regional megadroughts of about 1,000 km (California–Nevada, the Mississippi Valley) are missing. So is the
  multi-continent synchrony of 4.2 ka and 8.2 ka: we roll one cap at a time.
- **Duration: somewhat long.**
  - Real centennial events in the sources run 46–300 yr; ours 200–800.
  - The upper half of our range (300–800 yr) has no counterpart in what was read.
  - Decade-long droughts (the Dust Bowl, 7–12 yr) are below the century step, so they cannot be habitat events at all.
- **Frequency: far too rare.**
  - **Ours.** About 2.25 droughts per 30 kyr for the whole planet. A given place lies in a drought's core about once per
    (30 / 2.25) / 0.04 ≈ 330 kyr, and inside any cap once per ~80 kyr.
  - **Earth.** One well-recorded region sees a 50–250-year megadrought every ~150–500 yr: three in 500 yr in the Mississippi Valley;
    two in ~500 yr in California–Nevada; 4.2 ka and 3.2 ka within a millennium in the Near East (Weiss 2016).
  - **The gap.** Ours is two to three orders of magnitude too rare. A given steppe has about a 3% chance of a drought core in a 10 kyr
    Holocene (0.75 droughts × 4%), or 12% of being touched at all.
- **Response: missing.**
  - Weiss 2016 describes "habitat-tracking to riparian, paludal and karstic refugia", pastoral nomads (the Amorites) pushed down the
    Euphrates into the cities' farmland, and "warring kingdoms" on resettlement.
  - Our peoples only thin out at their dry margins.
  - Caution: the 4.2 ka collapse narrative is disputed (Sołtysiak & Fernandes 2021; Borisov 2022 for the steppe).

**Answer to the PIE question.**
- **Real.** The steppe dry phases tied to Yamnaya times were regional, centuries long and moderate in the steppe soil records read.
- **Ours.** A drought of that size can appear in a world, but rarely, and it would not shuffle anyone. The only thing that changes is
  where each people's comfort window lies.
- **What would make it work.** A higher drought rate, with shorter and smaller events added (draft
  `draft-recent-droughts-earthlike-rate`), plus droughts that act on food and drive habitat tracking (section d, draft
  `draft-drought-famine-and-habitat-tracking`).

## The shared plug: one cut to carrying capacity, from the life tables

### Where the counter-pressures enter
The history has no population equation. A people's presence p (0..1) on a cell is capped at its habitat K
(`_advance`: `p = min(p, K)`), and its numbers are p × density × area (lane 76, section 1). The physically right entry point is the
sustainable-loss result, N* = K(1 − h/r), applied as a multiplier on K.
- **Formula.** On each cell, each people's K is multiplied by `kept` = r′ / r.
  - r is the people's growth rate under its current mortality schedule (lane 78's `life_history.table`, Euler–Lotka).
  - r′ is the same with the counter-pressure's extra annual mortality added per stage (infancy, childhood, adulthood, elder).
  - r′ / r is exactly 1 − Δr/r, the stage-structured form of 1 − h/r.
- **Floor.** `kept` is never below `COUNTER_FLOOR` (judgement: 0.05). No counter-pressure ends a species; that is the owner's
  never-species-ending line for the dragons (PW-1068), applied to the peoples.
- **Land losses.** Pressures that remove land rather than lives (war-torn fields; famine) multiply K directly.
- **Why K is the right channel.** A lower K lowers p and so the people's load on its rivals (`_load`). The rivals gain room and take
  cells, so a pressure can change who holds the land. With `COEXIST` and the priority effects lane 73 measured, a brief pulse can leave
  a lasting mark. The momentum edge (`surge`) and the hold lapse (`HOLD_MIN`) then work unchanged.
- **Density during a pulse.** A pulse should also lower the people's density in `invasion_weights` for those cells
  (`dens × kept_pulse`). A thinned people then defends its front as a thinner one.

### What lane 78's tables say (scratch `l82/kept.py`, on lane 78's `life_history.py` and `dnd.toml`, read-only)
`kept` = r′ / r for an extra hazard h, with lane 78's stage ends, schedules and breeding classes:

| People (r, %/yr, forager) | war h on adults 0.1 / 0.25 / 0.5 / 1.0 %/yr (stage weights 0.1, 0.3, 1, 0.3) | disease h on all stages 0.25 / 0.5 / 1 / 2 %/yr |
|---|---|---|
| Human (4.40) | 0.99 / 0.97 / 0.94 / 0.88 | 0.94 / 0.89 / 0.77 / 0.55 |
| Kobold (13.4, agrarian schedule) | 1.00 / 0.99 / 0.98 / 0.95 | 0.98 / 0.96 / 0.93 / 0.85 |
| Goblin (13.6) | 1.00 / 0.99 / 0.98 / 0.96 | 0.98 / 0.96 / 0.93 / 0.85 |
| Orc (6.8) | 0.99 / 0.98 / 0.96 / 0.92 | 0.96 / 0.93 / 0.85 / 0.71 |
| Halfling (4.0) | 0.99 / 0.97 / 0.93 / 0.87 | 0.94 / 0.88 / 0.75 / 0.50 |
| Dwarf (1.73) | 0.97 / 0.93 / 0.86 / 0.71 | 0.86 / 0.71 / 0.42 / 0 |
| Gnome (2.0) | 0.97 / 0.93 / 0.87 / 0.74 | 0.88 / 0.75 / 0.50 / 0.01 |
| Elf (0.47) | 0.89 / 0.73 / 0.46 / 0 | 0.47 / 0 / 0 / 0 |

The design rules this table forces:
1. **No uniform mortality term.** It is the slow-breeder trap.
2. **Mortality terms must be self-limiting in the victims' own density.** Only crowded, connected peoples pay.
3. **The levers that actually cap fast breeders act on K:** land lost to war, food lost to drought, and land briefly emptied by plague
   that neighbours take.

Lane 76's report (section 3) gives "humans about 43%" kept at 0.5%/yr, which implies r ≈ 0.9%/yr. Its own table and lane 78's code
give r ≈ 4.3–4.4%/yr, so the kept share is ~89–94%. The text looks like an arithmetic slip (draft `draft-lane76-sustainable-loss-figures`).

### One mixin, one output
- **Code.** `planet/lineages/history/counter.py`, a `CounterMixin`. A `_counter_step(step, env, tags)` at the start of each step, after
  the megafauna pressure, fills `self._kept` (lines × cells). `_advance` multiplies K by `self._kept[k]` right after `_K`.
- **Epochs.**
  - **Deep:** off (no densities then).
  - **Glacial (2 kyr steps):** the equilibrium terms only (war, endemic loads).
  - **Recent (century steps):** everything, pulses included.
- **Output.** Per people per stored frame, `lost` = {war, plague, famine, predation}: the share of its numbers held off by each. These
  are counterfactual shares from each factor alone; together they multiply.
- **Events** ("a plague in the human towns of the X lands, 45% lost", "virgin-soil epidemic among the elves after contact with the
  humans") go into `events`. Settlements (PW-1108) and the brief read them.

## (b) War

### What the literature says
- **Violent death rates, non-state.** Our World in Data's compilation of Keeley 1996, Gat 2006, Bowles 2009, Walker & Bailey 2013 and
  others ("Ethnographic and archaeological evidence on violent deaths", archived 2013) gives 20–1,450 violent deaths per 100,000 a year:
  - the lowest are mobile foragers and Arctic peoples: Andamanese 20, !Kung 42 (29 after state authority), "Eskimos" 100, Tiwi 160;
  - in the middle are highland horticulturalists and tribes: Yanomamo 290, Mae Enga 320, Dugum Dani 480, Goilala 550, Hewa 731;
  - at the top: Dinka 970, Grand Valley Dani and Piegan 1,000, Kato 1,450.
- **Violent death rates, states.** 30–250: Japan 1900–90 30, France 1800s 70, Russia and Germany 1900–90 150–160, Aztec Mexico 250.
- **Shares of deaths.** Non-state shares run 4–60% (ethnographic) and 0–60% (archaeological); state shares <1–5%.
- **Sex split.** War deaths fall heavily on men: Yanomamo 24% of male deaths against 7% of female; Dani 28.5% against 2.4% (same source).
- **Bowles 2009.** About 14% of deaths in his foragers were from intergroup conflict (search summaries of *Science* 324:1293). Fry's
  correction drops two cases (Ache, Hiwi: killed by frontier ranchers), giving about 9%.
- **Fry & Söderberg 2013** (*Science* 341:270; HRAF summary of the abstract). In 21 mobile forager band societies, "the majority of
  lethal aggression... can be classified as homicide. Feuding is common and warfare a definite minority."
- **Gómez et al. 2016** (*Nature*, doi:10.1038/nature19758, read in full).
  - The phylogenetic expectation for humans is 2% of deaths.
  - Prehistoric bands and tribes match it; present-day bands and tribes run higher.
  - "The level of lethal violence in chiefdoms was also higher", from "territorial disputes, population and resource pressures".
  - States are lower: "monopolization of the legitimate use of violence by the state significantly decreases violence".
  - Crucially: "population density... was lower in periods with high levels of lethal violence... High population density is therefore
    probably a consequence of successful pacification, rather than a cause of strife."
- **Turchin 2009** (*Ann. N.Y. Acad. Sci.* 1162:1, read in full).
  - Agrarian populations show "slow oscillations... with periods of roughly two to three centuries".
  - Instability events run 0.6 per decade in growth phases against 3.8 in decline phases (Table 1, seven cycles).
  - Mechanism: when the state is weak, "elevated mortality due to increased crime, banditry, and internal and external warfare",
    refugees, and epidemics spread by vagrancy.
  - Stateless model: dN/dt = rN(1 − N/K) − WN, dW/dt = aN² − bW. War intensity W is fed by density squared and decays slowly.
  - State model: the state's resources S suppress W (−αS), and war lowers carrying capacity, K(W) = k_max − cW.
  - Realistic r of 1–2%/yr gives cycles of ~200 years.

Reading these together:
- **The data do not support "dense peoples fight more" in general.** Density and violence run against each other across history
  (Gómez), because states pacify.
- **They do support:**
  - violence that rises with territorial and population pressure where there is no state (chiefdoms; Turchin's stateless model);
  - lagged internal war in crowded agrarian states when the state fails (Turchin);
  - a large way-of-life difference: mobile foragers lowest; tribal horticulturalists and pastoralists highest; states low and stable.

### Design
Per people k on each held cell, at each glacial and recent step:

- **War hazard (per year):**
  `h_war = H_way × A_k × E(lev) × [ (N / N0)² × G(lev, k) + X × F ]`
  - **N** is the people's density on the cell (p × density, per km²).
  - **N0** is a reference density (judgement: 10 /km², the human farmer default in dnd.toml).
  - **F** is the share of the cell's neighbours held by peoples k is hostile to: the cohabitation matrix under 0.5
    (`compose.cohabitation`), in contact (`corridor` > 0). This is the frontier.
  - **The square** is Turchin's conflict-initiation form.
- **H_way** is the way-of-life base: the violent death rate at reference density with a full hostile frontier. Defaults, from the
  medians of the compiled rows above (a judgement on which rows count):

  | Way | H_way (%/yr) | Rows behind it |
  |---|---|---|
  | forager, fisher_forager, sea_nomad | 0.07 | Andamanese, !Kung, "Eskimo", Tiwi: 20–160 per 100k |
  | horticulturalist, agro_pastoral | 0.5 | Yanomamo, Mae Enga, Dani, Goilala, Hewa: 290–731 |
  | pastoral_nomad, transhumant | 0.8 | Dinka 970, Piegan 1,000 |
  | farmer | 0.12 | French and German rows: 70–160 |
- **A_k** is the culture: ×2 for the `aggressive` trait, ×1 otherwise, and a per-line `war_x` field for authored peoples (default 1).
- **E(lev)** is the era dial: `meta.war_early` at tech level 0 and `meta.war_late` at tech level 1, blended by lane 63's
  `megafauna.tech_level` (ERA_LEVEL), as `press_x` does for the dragons. Choices WAR_X = (0, 0.5, 1, 2, 4); default 1, 1.
- **G(lev, k)** is the state's pacification of internal war: 1 / (1 + STATE_Q × lev × town share). STATE_Q is a judgement (default 3).
  So a renaissance farming people with towns feels its own crowding about four times less than a stateless one at the same density.
  This is Gómez's pacification and Turchin's −αS, without simulating S.
- **X** is the weight of external (frontier) war. Default 0.5 (judgement): mobile foragers' killing is mostly homicide, not war
  (Fry & Söderberg).

**The baseline is already in the life tables.** Lane 78's schedules (Gurven & Kaplan's foragers and forager-horticulturalists, Sweden
1751–59) already include their own peoples' violence. So the extra hazard is the excess over the schedule's own reference:
`h_extra = h_war − h_war(reference)`.
- The reference is the people's way at N = its own density at full habitat, F = 0.5 (a judgement: half a hostile border) and every
  dial at 1.
- `h_extra` is clipped at −h_war(reference). A pacified, sparse people lives slightly longer than the schedule; a crowded, warlike,
  hemmed-in one dies more. This keeps lane 78's r calibrated where nothing unusual is going on.

**Stages and sexes.**
- `h_extra` falls on the life table's stages with weights (infancy 0.1, childhood 0.3, adulthood 1, elder 0.3). This is a judgement:
  raids kill some women, children and elders, but most war deaths are adult men.
- The one-sex life table counts female deaths. Male deaths enter at `MALE_W` = 0.25 (a judgement), since mates limit births only
  weakly. The female share of war dead is ~0.1–0.25 (Yanomamo, Dani, above).
- So the effective adult hazard is about (0.2 + 0.25 × 0.8) ≈ 0.4 × h_extra.
- A search for a demographic source on how male war deaths change growth found none worth citing, so MALE_W stays a judgement. The
  WWI and WWII birth-deficit literature argues the effect is not zero.

**Land lost to war (Turchin's K(W)).** On top of the deaths, war-torn country holds fewer people:
`K × (1 − LAND_Q × min(1, h_war / H_MAX))`, with LAND_Q = 0.3 and H_MAX = 1%/yr. Both are judgements: fields left unworked and
people pulled back to strongholds (Turchin 2009 p. 10: "In a stateless society people can live only in natural strongholds").
- **This is the term that caps a dense people.** It acts on K, so a fast breeder pays it as fully as a slow one.
- It is strongest where `(N / N0)²` is large and there is no state: crowded horticultural and pastoral peoples, and stone-age to
  bronze-age farmers.

**Displacement.**
- Already partly there: a people whose K falls on a frontier is pressed back by the existing competition.
- Phase 2 (PW-661 territory): add the cells a people lost to war in a step to its `crowd`, so crowded losers jump (`_jump`) as refugees.
- Leave out a "winner takes the frontier" bonus. It would reward the biggest people, the opposite of a thermostat.

**Cycles.**
- Turchin's ~200-year cycles are at the century step's Nyquist limit (two steps a period), so this design uses the equilibrium form
  (W = its driver, no lag).
- The cycle's story is kept as seeded "times of troubles": in the recent epoch, a people with h_war above H_MAX / 2 has a chance
  `TROUBLE_PER_KYR` (judgement 2) of a one-step pulse, h ×3.
- The 0.6 against 3.8 events-per-decade contrast (Turchin Table 1) is the size of the swing between calm and troubled phases.

### How it caps humans and kobolds without forcing a share
- **Through `(N / N0)²` and land.**
  - Humans at 10 /km² in their densest farmland, before states, pay the full land loss there.
  - Kobolds at 4 /km² pay (0.4)² = 16% of it.
  - Elves at 1 /km² pay 1%, so the slow breeders are spared by being sparse.
- **No share is set.** A people's numbers fall only where it is crowded and stateless, or ringed by enemies. The `war_early` and
  `war_late` dials are the owner's finger on the scale, per era.
- **Kobolds, honestly.** No plausible war rate keeps kobolds down through deaths. Their r (13%/yr under lane 78's brood class and harsh
  survival) shrugs off any hazard short of famine levels. War caps kobolds only through land, and only where they are crowded. If
  kobolds are too many, the reason is their density or their area; that was not checked here. Their density (or lane 78's share band)
  is the honest lever.

### Spec, settings, defaults
- **Per line:** `war_x` (float, default 1). The `aggressive` trait doubles A.
- **meta:**
  - `war_early`, `war_late` (WAR_X choices, default 1, 1);
  - `war_external` (X, choices 0 / 0.5 / 1, default 0.5).
- **Viewer:** "How warlike are the peoples": one control for the early eras and one for the late, beside the dragon-pressure pair (PW-1068 D14).
- **Constants (params.py):** H_WAY (table above), WAR_N0 10, STATE_Q 3, MALE_W 0.25, WAR_STAGE_W (0.1, 0.3, 1, 0.3), LAND_Q 0.3,
  H_MAX 0.01, TROUBLE_PER_KYR 2, COUNTER_FLOOR 0.05.

**As built (lanes 97, 101, 259; history.counter, params.py).** War-torn land (lane 97) and in-fighting (lane 101) as above, under the
master dial `meta.war`. Lane 259 (PW-1172, PW-1243) added: `war_early` / `war_late` (x meta.war, on war-torn land only), per-line
`war_x` and the `aggressive` x2; times of troubles sized from Turchin 2009 Table 1 instead of TROUBLE_PER_KYR (chance TROUBLE_SHARE
0.41 x dt / TROUBLE_KYR 0.107 kyr a step, x3); refugees on jumps only (the share of a people war drives off in a step adds to its
`_jump_push`); each people's `lost_to` shares, troubles and refugee jumps in the run output and the workbench. Not built, by D31: war
deaths through the life tables (lane 101 measured 0-0.2% of any people). `war_external` stays the constant WAR_EXT. The state term
still reads the farm share in the stand-ins: a town share exists inside the history only with live polities, whose pacification
already reads the ruling state's tier.

**Lane 259b stress suite (PW-1172 bar; world 4360a3, seeds 7/10/13, base + subset families, 12 runs an arm; off = `meta.war` 0, default = 1, x2 = 2; main_def = main at 0289ade6, default).** Slow breeders = elf, dwarf, gnome, drow, sea_elf, firbolg, dragonborn, goliath (mean total share over the 3 seeds of each tree):

| arm | dnd slow breeders | dnd elf | dnd commonest (seeds 7/10/13) | seven_meals slow breeders | seven_meals elf | seven_meals commonest | troubles per run (dnd / seven_meals) | refugee events | brittle peoples (dnd; seven_meals) |
|---|---|---|---|---|---|---|---|---|---|
| off | 20.2% | 8.0% | 28 / 26 / 32% | 10.8% | 1.9% | 31% mean | 0 | 0 | kenku, gnome, halfling, bugbear, drow; orc, bugbear, halfling, goliath |
| default | 19.1% | 7.9% | 28 / 21 / 42% | 8.3% | 1.0% | 34% mean | 44-50 / 83-105 | 0 | kenku, dwarf, bugbear, drow; orc, halfling, bugbear, goliath |
| x2 | 15.6% | 5.8% | 30 / 22 / 38% | 7.1% | 0.45% | 33% mean | 59-81 / 82-104 | 0 | leonin, halfling, bugbear; kobold, orc, bugbear, halfling |
| main_def | 19.2% | 8.3% | 31 / 23 / 43% | 9.2% | 1.1% | 34% mean | 0 | 0 | kenku, dwarf, bugbear, drow; kobold, orc, halfling, bugbear, leonin |

(Small trees dnd3 and dnd5 ran too: 4-6 and 21-29 troubles, no refugees, same pass state as main_def.) Verdicts, each against its baseline:
- **Slow breeders not lower than off: not met.** Default is 1.1 points below off in dnd (within seed noise: elf 7.9 vs 8.0, dwarf up, gnome down) and 2.5 below in seven_meals; x2 is clearly lower (15.6 vs 20.2, 7.1 vs 10.8). Default is level with main_def (19.1 vs 19.2; 8.3 vs 9.2), so the fall from off is mostly the lane 97 / 101 war-torn land and in-fighting that main already has, not this lane's additions.
- **Commonest people's share falls with war: not met.** Median 28% off, 28% default, 30% x2 (dnd); the commonest rises a little when the slow breeders shrink. D31's limits hold in every arm: 75% of runs under 50% in all four arms (the two misses are the small dnd3 trees), 100% of runs with 5+ peoples at or under 70%, worst single run 43%.
- **No new brittle peoples against main_def: met.** Default's dnd set is identical to main_def's; in seven_meals it loses kobold and leonin and gains goliath (swing 10.5x on a 0.02% share, against 6.6x on main_def; goliath is brittle with war off too, so it is seed noise at that size, not this lane's mechanism). No people went extinct that was not already authored-extinct, and no run crashed.
- **Troubles and refugees.** Troubles fire at default (dnd 38-50 a run, seven_meals 83-105) and about 1.4x as often at x2; zero with war off and on main. Refugees fire in none of the 36 war runs: the war-torn loss in a step never reaches half of a founding jump's push. Draft `draft-refugees-never-fire` carries it.

Recommendation: merge. At default the branch is level with main on every measure and adds the dials, the troubles and the lost-to output; the two un-met bars are the design's hope for war, not a regression, and cannot be met by nudging a constant here (lane 101 saw the same on deaths).

## (c) Epidemics

### What the literature says
- **Wolfe, Dunavan & Diamond 2007** (*Nature* 447:279, PMC7095142, read).
  - Crowd diseases need "at least several hundred thousand people in the cases of measles, rubella and pertussis".
  - "Human populations of that size did not exist anywhere in the world until the steep rise in human numbers that began around 11,000
    years ago with the development of agriculture."
  - Temperate crowd diseases mostly convey long-lasting immunity (11 of 15) and are acute (12 of 15).
  - Of the conquest of the Americas: "Far more Native Americans... died of newly introduced Old World diseases" than of wounds;
    "previously unexposed Native American populations had no immunity or resistance".
- **Critical community size.** The concept is Bartlett's (measles in the 1950s; Bartlett 1960, *JRSS A* 123:37, as cited on Wikipedia).
  The often-quoted 250–500 k (Conlan et al. 2009, citing Black 1966) could not be opened (HTTP 404), so only Wolfe's "several hundred
  thousand" is used.
- **The Black Death.** Jedwab, Johnson & Koyama, "The Economic Impact of the Black Death" (2020 working paper of their *J. Econ. Lit.*
  60:132, 2022; read):
  - overall mortality "between 40-60%" (Benedictow), 40% being the population-weighted mean of 274 localities;
  - "Lower in the Low Countries, Central Europe, and Portugal (20-35%)";
  - cities ranged from Milan "comparatively unscathed" to Trento 80%;
  - "repeated reoccurrences of the plague for the subsequent two and a half centuries";
  - "By 1500, on average, cities had recovered to their pre-plague population levels", the recovery "driven by migration";
  - Europe's "overpopulation... facilitated the spread", and the disease had evolved "in isolation from human populations for
    several centuries".
- **The First Pandemic.** It recurred from Justinian (541) "until the mid-8th century" (Jedwab et al.). Mordechai et al. 2019 (*PNAS*
  116:25546, abstract and press) find no clear demographic or economic disruption in the datasets they examined: "an inconsequential
  pandemic?". So pulse mortality should vary widely, and not every pandemic should be a Black Death.
- **Virgin soil, the Americas.** Koch, Brierley, Maslin & Lewis 2019 (*Quat. Sci. Rev.* 207:13; abstract and coverage read) estimate
  60.5 M people in 1492 (IQR 44.8–78.2 M) and a 90% loss (IQR 87–92%) over the following century.
- **Turchin 2009.** Crowds of the displaced "may tip the population density over the epidemiological threshold". Epidemics come with
  the decline phases of secular cycles.

### Design
Three pieces. None adds an endemic load on top of lane 78's schedules, which already carry it: the agrarian schedule is Sweden 1751–59.

**1. Who carries crowd diseases (a state per people).**
- **Carrier.** A people is a carrier once its largest connected crowd reaches `CCS_POP` people: cells at or above `CROWD_DENS` people
  per km², linked by contact corridors.
  - CCS_POP: judgement 300 k, inside Wolfe's "several hundred thousand".
  - CROWD_DENS: judgement 5 /km², village farming.
  - The state is sticky: it fades only if the crowd stays under the CCS for `CARRIER_FADE_KYR` (judgement 2 kyr).
- **Who becomes one.** At L7 a farmed cell at 10 /km² holds ~31 k people, so ten linked cells make a carrier. Every farming people on a
  continent becomes one within centuries of farming; no forager people ever does.
- **Seasoning.** Each non-carrier people gets a seasoning I (0..1) toward each carrier pool. It rises by contact (cells in corridor
  contact) with e-folding `SEASON_GEN` = 4 generations (judgement: a few generations of exchange spread exposure). A carrier is
  seasoned to its own pool.

**2. Virgin-soil epidemics (one-time pulses at first contact).**
- **When.** A carrier's range first comes within corridor contact of a people with I < 0.5 toward it. Contact records the meetings
  (`contacts.py`).
- **Loss.** The naive people takes a pulse `L = virgin_soil × (1 − I)` over the contact component of its range (all its cells
  connected to the contact).
  - `meta.virgin_soil` choices (0, 0.3, 0.6, 0.9).
  - Default 0.6, a judgement under Koch's 90%, which mixes in war, slavery and famine.
  - Spread over `VS_SPAN_YR` = 100 years, the century of Koch et al.: one recent step.
- **Effect.** The pulse is a depletion d on the people's K that recovers (below), and it lowers the people's density in
  `invasion_weights` on those cells.
- **Why it matters.** This is how farmers take a continent's best land from its foragers. The existing competition does the rest.
- **Who it favours.** Virgin soil favours the dense people. That is realistic, but it is not a brake on humans.

**3. Plague pulses (rare, regional, on the carriers' towns).**
- **Rate.** Poisson, `PLAGUE_PER_KYR × P(lev)` for the whole world.
  - `P(lev)` is the era dial: `meta.plague_early` and `meta.plague_late`, choices (0, 0.5, 1, 2, 4), blended by tech level as for war.
  - PLAGUE_PER_KYR is 1.3 from the classical era on: two pandemic eras, the 6th–8th and 14th–18th centuries, in ~1.5 kyr (Jedwab et
    al.). Zero before the bronze age, ramping in through it (judgement).
- **Seed.** A town cell (the densest `CITY_TOP` share of peopled land, as `cities.py` already defines) of a carrier people, drawn by
  population.
- **Reach.** The plague spreads over carrier peoples' cells connected by corridors within `PLAGUE_KM` (judgement 4,000 km: the Black
  Death reached all of Europe from Messina, where "proximity to Messina was a strong predictor" of mortality, Jedwab et al.).
- **Loss on a cell.**
  `L = PLAGUE_LOSS × u × min(1, N / CROWD_DENS) × (0.5 + 0.5 × town)`
  - PLAGUE_LOSS is 0.4: the population-weighted mean of Jedwab et al.
  - u is a per-pandemic severity draw, log-uniform 0.1–1.5 and capped so that L ≤ 0.8. The cap is Trento's 80%; the low end is
    Justinian as read by Mordechai.
  - town is 1 on town cells.
- **The pandemic era.** It lasts `PLAGUE_ERA_YR` = 250 years ("two and a half centuries"). Its recurrences add an all-stage hazard
  `PLAGUE_RECUR_H` = 0.5%/yr (judgement) on the struck cells. With lane 78's tables, that keeps humans at 89% and dwarves at 71% where
  they live in the struck towns.
- **Recovery.** A depletion d on a people's K recovers each step as `d ← d × exp(−dt / (RECOVER_YR / x))`.
  - x is lane 78's growth multiple.
  - RECOVER_YR is 50 (judgement). A 40% dent is then mostly gone in ~150 years for humans, the cities' recovery by 1500 (Jedwab et al.).
    It lasts ~7 times longer for elves.
  - During the dent, the neighbours' room rises and they take cells. Jedwab et al. note recovery came by migration, which in this
    model is the spread of whoever has room.

### How it caps humans without forcing a share
- **Who it reaches.** Plague reaches only carriers with towns, so in practice the dense farming peoples: humans, halflings, dwarves
  with towns, and kobolds only if they are carriers.
- **How much it moves.** Each pandemic era takes 20–80% off those peoples' town cells for a century or two. Their neighbours gain
  ground, and some of it sticks through priority effects.
- **No target.** No share is aimed at: a people loses where it is crowded, connected and urban. The dials scale it per era.
- **The bound.** A world without towns (the stone age, or `plague_*` = 0) never has plague.

### Spec, settings, defaults
- **Per line:** `plague_x` (float, default 1; 0 for peoples that do not sicken, e.g. constructs or undead overlays) and
  `crowd_disease` (true by default; false for a people the owner wants never to be a carrier).
- **meta:** `plague_early`, `plague_late` (default 1, 1) and `virgin_soil` (default 0.6).
- **Viewer:** "How often plagues strike" (early, late) and "How hard first contact hits peoples who never had the crowd diseases".
- **Constants:** CCS_POP 3e5, CROWD_DENS 5, CARRIER_FADE_KYR 2, SEASON_GEN 4, VS_SPAN_YR 100, PLAGUE_PER_KYR 1.3, PLAGUE_KM 4000,
  PLAGUE_LOSS 0.4, PLAGUE_U (0.1, 1.5), PLAGUE_CAP 0.8, PLAGUE_ERA_YR 250, PLAGUE_RECUR_H 0.005, RECOVER_YR 50.

## (d) Other thermostats

**Famine from drought.**
- **The gap.** Today a drought moves a people's comfort window but leaves the food its land gives unchanged (the density's
  productivity is the static present-day field), so a drought never starves anyone.
- **Food.** In a drought, scale K by `(rain / rain_ref)^e_way` on the struck cells:
  - e_way = 1 for farmers on rain-fed land and for pastoralists;
  - 0.5 for foragers;
  - 0.2 for fisher-foragers and for farmers on navigable rivers (`humanuse` river layer);
  - all judgements.
  At ×0.6 rain a rain-fed farming people holds 60% of its numbers in the drought core. This is a K effect, so kobolds pay it too.
- **Habitat tracking.** A drought-struck people gets a temporary habitat pull toward river, lake and spring cells within ~300 km
  (Weiss 2016's "riparian, paludal and karstic refugia"). A pastoral people under drought gets the momentum edge's contest bonus
  against farmers in its way (the Amorites "forcing the tribal groups to seek refugia along and down the Euphrates").
- **Size.** Famine mortality sits in the Great Famine's range: 10–15% in southern England, ~10% in northern France (Wikipedia
  "Great Famine of 1315–1317", citing the *New Cambridge Medieval History* vol. 6). The famine was from rain and cold, not drought. At
  century steps one bad decade is a one-step K dent that recovers like a plague dent.
- **Defaults.** On by default once the drought rate is Earth-like. Without that change there are too few droughts for famine to matter.
- **Dial.** `meta.bad_years` (rare = today, Earth-like, harsh) sets the drought rate in the viewer.

**Predation by dragons.**
- **What exists.** Lane 63's branch (PW-1068) gives the peoples' persecution of dragons a per-era dial (`press_early`/`press_late`,
  tech level from `ERA_LEVEL`).
- **What the owner asked (D16).** Dragons press back: predation on small folk keeps game plentiful.
- **The term.** It belongs in the same `kept` channel. A dragon's annual food need is in `megafauna.meat_need`, its density in
  `local_density`. The share of that need taken from people and their livestock, `PEOPLE_PREY` (judgement 0.1 for chromatics, 0.02 for
  metallics, as D16's temperament split), becomes the small folk's loss on the cell:
  - livestock losses cut K like famine;
  - people eaten enter as a stage hazard weighted to children and elders.
- **Size.** At one dragon per thousands of km², this is a small K effect for numbers, a strong one for story, and self-limiting: more
  dragons where there is more prey.
- **Where it lands.** It belongs with PW-1068 D16, not a new ticket. This design only fixes its entry point and output (`lost.predation`).

## (e) Plugging in, and how the lane 77 stress suite judges each

| Thermostat | Plugs in | Per-era setting (viewer) | Default | Judge (lane 77 `tools/peoples_robust.py`) |
|---|---|---|---|---|
| War (deaths + land) | `CounterMixin._counter_step` → `kept`; K × kept in `_advance` | `war_early`, `war_late`; `war_external` | 1, 1; 0.5 | arms off / default / ×2 (`--params` on WAR_Q) |
| Virgin-soil epidemic | contact events (`contacts.py`) → depletion d | `virgin_soil` | 0.6 | arm 0 / 0.6 / 0.9 |
| Plague pulses | recent epoch: seeded pandemics over carriers' towns → d + era hazard | `plague_early`, `plague_late` | 1, 1 | arms off / default / ×4 |
| Famine | drought episodes → K × (rain ratio)^e; habitat pull | `bad_years` | Earth-like (once that draft lands) | arm on / off, after the drought-rate change |
| Predation | dragon density × PEOPLE_PREY → kept | (PW-1068's settings) | per PW-1068 | PW-1068's own review |

**How a run is judged.** Each arm runs over the base, jitter, subset and authored families on 4360a3 and af2677, as `peoples_robust.py run`
does. Passing means:
1. **Invariants hold.** No crash; MONO_MAX 0.85; no authored people silently extinct.
2. **The slow-breeder trap stays shut.** Every slow people's median share is not lower than in the off arm, beyond seed noise: elf,
   dwarf, gnome, firbolg, half-elf, triton. This is the check the table above makes necessary.
3. **The thermostat is visible.** The commonest people's median share and its median led-cells share fall against off. The size of the
   fall is the owner's call (thresholds belong to the owner): this design expects a few to ~25 percent of its share at default, from
   the land terms.
4. **Brittleness is no worse.** The count of brittle peoples (share swing > SWING = 10× across seeds and jitters) is not higher than off.
5. **The knob family still moves shares** (density ×0.5 and ×2 monotone).
6. **Diagnostics are reported.** Per people, `lost.{war, plague, famine}` and the cells that changed hands within 0.5 kyr after a pulse
   or a first contact. A pulse that flips nothing is invisible and worth flagging.

Following the lane test policy, implementation lanes run the not-slow and area tests, with the full suite once at merge. Physics-style
small screens come first: one world, two seeds, the off and default arms. Then the full suite before merge.

## Order of work and tickets (inbox drafts on this branch)
1. `draft-counterpressure-plug`: the CounterMixin, the `kept` channel, the `lost` output and the floor. It waits for lane 78's life
   history (PW-1148) to merge. Effort m.
2. `draft-war-counterpressure`: war as in (b). Relates PW-917, PW-1108, PW-661. Effort m–l. Has an owner-facing "In plain words".
3. `draft-epidemics-counterpressure`: carriers, virgin soil, plague pulses as in (c). Relates PW-917, PW-1108. Effort l.
4. `draft-recent-droughts-earthlike-rate`: the drought rate and durations, sizes, synchrony (timezoom). Effort s–m.
5. `draft-drought-famine-and-habitat-tracking`: famine and habitat tracking as in (d). Effort m.
6. `draft-owner-thermostats-hit-slow-breeders` (needs-decision): the owner's call on the trade-off in plain words.
7. `draft-lane76-sustainable-loss-figures`: the lane 76 report's kept shares (docs). Effort xs.

PW-1108 (sacked and razed settlements) should read this design's war intensity and plague events once they exist, not invent its own.
PW-661 (v3) keeps polities, conquest and refugees as a system. This design is the demographic floor it would stand on.

## Sources read
- Gómez, Verdú, González-Megías & Méndez 2016, "The phylogenetic roots of human lethal violence", *Nature*, doi:10.1038/nature19758 (PDF, read).
- Our World in Data, "Data review: ethnographic and archaeological evidence on violent deaths" (archived 2013, read): Keeley 1996,
  Gat 2006, Bowles 2009, Walker & Bailey 2013, Knauft 1987 rows.
- Fry & Söderberg 2013, *Science* 341:270, abstract via HRAF (ehc/documents/868); Bowles 2009 and Fry's correction via search summaries.
- Turchin 2009, "Long-term population cycles in human societies", *Ann. N.Y. Acad. Sci.* 1162:1–17 (PDF, read).
- Wolfe, Dunavan & Diamond 2007, "Origins of major human infectious diseases", *Nature* 447:279 (PMC7095142, read).
- Jedwab, Johnson & Koyama 2020, "The Economic Impact of the Black Death" (AEA working-paper PDF of *JEL* 60:132, 2022; read).
- Mordechai et al. 2019, *PNAS* 116:25546 (abstract and press, read).
- Koch, Brierley, Maslin & Lewis 2019, *Quat. Sci. Rev.* 207:13 (abstract and UCL coverage, read).
- Weiss 2016, "Global megadrought, societal collapse and resilience at 4.2–3.9 ka BP across the Mediterranean and west Asia",
  *PAGES Magazine* 24(2):62–63 (PDF, read).
- Bini et al. 2019, "The 4.2 ka BP Event in the Mediterranean region: an overview", *Clim. Past* 15:555 (first 100 k characters read).
- Sołtysiak & Fernandes 2021, *Antiquity* 95:1145 (abstract); Borisov et al. 2022, *Vestnik VolGU* (abstract); Khokhlova et al. 2018,
  *Eurasian Soil Science* 51:506 (via the indo-european.eu summary).
- NOAA NCEI 2021, "Post-Glacial Cooling 8,200 Years Ago" (PDF, read).
- Cook & Seager, "Megadroughts in North America: placing IPCC projections of hydroclimatic change in a long-term paleoclimate context"
  (JQS manuscript, Lamont-Doherty; PDF read).
- Wikipedia, "Great Famine of 1315–1317" (mortality figures and their cited sources); "Critical community size".
- In-repo: lane 76's report (docs/review/peoples-demography/report.md); lane 78's `life_history.py`, `growth.py`, `bands.py` and
  `dnd.toml` (branch worktree-agent-aea184dadb2617d33, read-only); lane 63's `megafauna.py` and `spec.py` (branch
  worktree-agent-ab94f066475a272cc); lane 77's `tools/peoples_robust.py` (branch worktree-agent-aa81760810638efe3).

**Not read / not used:**
- Black 1966 and Bartlett 1957 themselves; Conlan et al. 2009 (404).
- Keeley 1996 and Pinker 2011 directly (only through OWID's compilation).
- Any 5.9 ka primary paper.
- The NSFC Caspian / Yamnaya item (certificate error).
- Robles et al. 2021 (blocked).
- The Lamont Great Famine note (403).

Scratch: `l82/kept.py` (the kept table above), `l82/*.txt` (extracted PDFs).
