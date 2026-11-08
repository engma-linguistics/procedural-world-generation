# Crop origins and spread: round 1 (lane 157, 2026-11-03)

## In plain words

Daniel asked for the foods to come from somewhere real, and to spread the way Earth's did: New World foods stay out of the Old World until ships cross the ocean and come back again.

**What was wrong.** The crop docstring said "all crops go by canoe". That was not quite what the code did, but the code had a worse problem:
- From 3,000 years before the present, any people with a sailing ship could carry any crop it knew across up to 2,500 km of open sea, onto land held by anyone.
- In the current code, on the Seven Meals world (run bbfba8), beans and chilies crossed 2,286 km of open sea onto the 130 Mkm² supercontinent 2,500 and 2,200 years ago. Maize crossed 1,263 km 1,400 years ago. On Earth that is a Columbian exchange two thousand years early.
- There was no point at which the oceans opened for good either, so the real exchange of the last 500 years was missing as well.

**What Earth shows** (sources in [round1_sources.md](round1_sources.md); the key one is Crowther et al. 2016 PNAS):
- Crops crossed long open sea **with colonists** bringing their own gardens to land they settled. Examples: Lapita, about 3,000 years ago; East Polynesia, 1,000–700 years ago; Madagascar, about 1,200 years ago, 6,000 km from where its crops came from.
- **Between peoples**, crops went over straits and from coast to coast, and stayed minor for centuries.
- Across the open ocean to anyone, crops moved only after 1492. Then it was fast: chili went from Spain to India in under 50 years.
- Exactly one food crossed between the Americas and the Old World before 1492: the sweet potato, carried by Polynesians.

**What I changed** (in `planet/lineages/animals.py`, crops only; the animals are unchanged):
1. Before the ocean-going ships, there are two ways a crop crosses the sea:
   - A seafaring people carries a crop **it has taken up**, in the best boat it can crew, only to a coast **it holds itself**. That is the colonists' case: they take the gardens they keep. Tortles fishing two shores do not carry a farmer's grain between them. Each landmass gets one draw per try, at the best of the chances, so more seafaring peoples do not add up to more voyages.
   - Any people carries a crop to anyone's coast over a strait of at most 300 km. That is the canoe's reach, and it was already in the model.
2. **Ocean-going ships.** In a present of the renaissance or later, from 0.53 kyr before the present (1492), every crop known on a peopled coast reaches every peopled landmass. Uptake still waits on each people's own lag, which already exists (PW-1373 B). In an earlier present, the oceans stay shut to crops.
3. Two first-cultivation dates were wrong and are fixed: **common beans 7.0 → 5.0 kyr** and **quinoa and amaranth 7.0 → 5.0 kyr** (Larson et al. 2014 PNAS Fig. 2).
4. Three foods were added, all dated from Larson et al. 2014 Fig. 2:
   - **soybeans**: a monsoon temperate staple pulse, 5.0 kyr;
   - **cowpeas and other savanna pulses**: a savanna staple pulse, 3.7 kyr;
   - **date palms**: hot dry country with ground water, 6.0 kyr.

   The table now has 36 rows.

New dials: one, `OCEAN_SHIP_KYR = 0.53` (1492, from the same "kyr before the present" convention the crop dates use). `STRANGER_KM` is the existing canoe reach (300 km), not a new number.

**What I did not change, and why:**
- **A keeping class (seed, tuber, fruit).** The sources do not support it as a limit on where crops *grow*. Tubers and cuttings crossed the longest seas with colonists. Perishability limits the trade in *produce*, such as fresh tomatoes before canning, not where a crop is farmed. I found no source showing tuber crops spreading slower overland than seed crops. Adding the class would be a dial without evidence.
- **Day length and season regime** (why maize crept north at 1.3 km/yr and why wheat took 5–6 kyr to reach the summer-rain east). This is real and sourced (Merrill 2009; Liu et al. 2019). The model's crop front only reads temperature and rain windows. It is filed as a draft for later, not done here.
- **Borderline dates left alone.** Tomato might be ~7 kyr, but that rests on one genetic estimate. The flax part of oil seeds would be ~9.5 kyr, but sesame is later and unchecked. Foxtail millet at 10.0 kyr holds if the row also stands for broomcorn millet.

## 1. Audit of the 33 rows

The full per-row table, with each source and where in it the date was found, is in [round1_sources.md §1](round1_sources.md). In brief:
- **OK or fine (within ~1.5 kyr):**
  - grains and pulses: wheat and barley, lentils and peas, rice, sorghum and pearl millet, maize, rye and oats;
  - roots and tubers: potato, roots, banana, sweet potato;
  - tree and vine crops: tree fruit, olive, vine, coconut and oil palm, cacao, peanut, avocado;
  - others: chili, cane, squash, tea.
- **Wrong, now fixed:** common beans (5.0, not 7.0) and quinoa and amaranth (5.0, not 7.0).
- **Borderline, left alone:** tomato, oil seeds (flax) and foxtail millet; reasons above.
- **Not checked this round:** tropical spices, sap sugar and beet, cooking greens, onions and garlic, vanilla, oats.

Daniel's named foods:
- **Present:** chilies, potatoes, olives, maize.
- **Present among the staples:** wheat and barley, rice, millets, sorghum, the tubers.
- **Added:** soybeans, cowpeas, date palms.
- **Still missing, proposed for later:** mung bean (4.0), Old World melons (4.0), breadfruit (≥3.1), and coffee as its own row (0.55, weakly sourced). Citrus, mango, apple, fig, teff, finger millet and buckwheat have no source opened yet.

## 2. What gates spread: Earth against the model

| Earth's gate (source) | In the model before | Now |
|---|---|---|
| Open ocean: colonists carry their gardens; traders reach others' coasts only hop by hop (Crowther 2016; Pawley; Wilmshurst 2011) | any crew-able sailing ship carried any crop up to 2,500 km to anyone, from 3 kyr ago | colonists at their craft's reach; strangers within 300 km |
| Ocean opens after 1492 and crops go global within decades (Nunn & Qian 2010) | never: the reach capped at 2,500 km | every crop known on a coast reaches every peopled landmass from 0.53 kyr, in a renaissance or later present |
| Overland front ~0.6–1.3 km/yr (Pinhasi 2005); maize north 1.3 km/yr (Merrill 2009) | each crop's front, 0.4–1.5 km/yr over peopled land | unchanged |
| Uptake lags: a traded crop stays minor for centuries (Crowther 2016); tomato in China waited ~400 yr (Nunn & Qian) | the take-up lag, 0.4 kyr / propensity (PW-1373 B) | unchanged (it carries the "known but not yet eaten" delay of the new ocean exchange) |
| Climate windows (temperature, rain, height) | each crop's wild and grown range | unchanged |
| Day length, winter- against summer-sown regimes (Liu 2019; FAO 2008 on the short-day Andean potato) | not modelled | not modelled (draft filed) |
| Keeping (produce, not propagules) | not modelled | not modelled (no evidence it limits crop spread) |
| The best-craft-only rule: after 6 kyr only peoples crewing planked boats carried crops at all | a canoe people stopped trading crops over straits once planked boats existed | any canoe people trades over a strait at any date |

## 3. Before and after on the same worlds

**Setup**
- **Baseline:** the same variants on the current code, main at 0a8eb814.
- **Variants:** the lane 77 robust suite's base family, arm `now`: dnd and seven_meals at seeds 7 and 10, on the suite's two L6 worlds, af2677 and 4360a3. That is 8 runs per side.
- **How they ran:** in process (`tools/peoples_robust.py run_one`, plus a probe that keeps the crop facts). Nothing was written under runs/ or worlds/. Both presets have a renaissance present.

"Big landmass" means one of at least 1 Mkm².

| variant | crop sea landings on big landmasses before 0.53 kyr, base → now | of which colonists / strait trade | crop × big-landmass pairs known before 0.53 kyr | pairs known at the present | largest change in a people's share |
|---|---|---|---|---|---|
| dnd s10 @4360a3 | 41 → 15 | 9 / 6 | 96 → 81 | 101 → 312 | 0.004 |
| dnd s7 @4360a3 | 43 → 10 | 6 / 4 | 79 → 61 | 88 → 340 | 0.003 |
| sm s10 @4360a3 | 57 → 23 | 23 / 0 | 115 → 100 | 122 → 298 | 0.024 (humans 0.353 → 0.329) |
| sm s7 @4360a3 | 56 → 28 | 26 / 2 | 117 → 91 | 122 → 340 | 0.007 |
| dnd s10 @af2677 | 14 → 3 | 2 / 1 | 62 → 60 | 66 → 198 | 0.004 |
| dnd s7 @af2677 | 11 → 6 | 6 / 0 | 43 → 47 | 46 → 198 | 0.000 |
| sm s10 @af2677 | 15 → 5 | 3 / 2 | 57 → 56 | 60 → 198 | 0.004 |
| sm s7 @af2677 | 13 → 5 | 4 / 1 | 59 → 53 | 62 → 198 | 0.006 |
| **total** | **250 → 95 (−62%)** | 79 / 16 | **628 → 549 (−13%, with 3 more crops)** | **667 → 2,082** | ≤ 0.024; no people newly dead |

What this shows:
- **Before 1492 (the 0.53 kyr mark), crop crossings of open sea fell by about three fifths.** The ones left are mostly colonists. On 4360a3 they are humans, half-orcs and human seafarers taking their own crops to their own coasts; the rest go over short straits.
  - The baseline's 2,000–2,400 km stranger crossings, such as beans and chilies at 2,286 km 2,500 years ago on Seven Meals, now happen only where one people holds both shores.
- **The crops known on each big landmass before 1492 fell much less (−13%).** Most continents on these two worlds are joined by land, or by straits of 300 km or less, at some time in the recent epochs. Over land, crops still spread freely between peoples, as on Earth. So the "two worlds" separation depends on the world having an ocean between its continents that its peoples have not themselves crossed and settled.
  - On af2677 almost nothing is cut off, because few big landmasses are separated by open ocean.
  - On 4360a3 it is about a fifth.
- **From 1492 on, every crop reaches every big landmass where it can grow**, the Columbian exchange: "known" at the present triples. Each people still takes a new crop up only after its own lag (0.4 kyr / its propensity), so a hunting people that met maize 400 years ago may still not farm it. As on Earth, known is not yet eaten (the tomato in China).
- **Nothing explodes.**
  - The largest change in any people's share is 0.024 (humans in Seven Meals s10 @4360a3).
  - No people dies that lived in the baseline. The dead in both are the same (fire giant, gold dragon, and half-orcs on sm s7 @af2677).
  - Crops feed the farmers only a little more (`grown_mkm2` +5–20%).

The whole robust suite (~145 runs) was not run. This change touches only the crops, and the base family showed share changes at or under 0.024.

Probe scripts (scratch, deleted at the end of the lane): crops_probe.py (runs a base variant and keeps `h.crops`' reach and the sea-landing events), compare.py, pre.py.
