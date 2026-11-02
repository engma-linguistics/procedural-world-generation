# The density ladder: sourced rungs for review (PW-1275, step 1)

Lane 130, 2026-11-02. Step 1 only: the sources and a proposal, for Daniel to rule on. No model code was changed.

## In plain words

- Today each people has its own fixed number of people per km², and humans are set at 10–12 while most D&D peoples are at 0.3.
  That gap (30–40×) is most of why humans swamp the map.
- Your ruling: the number should come from **how a people lives** (foraging, gardening, ploughing, irrigating, herding, fishing),
  **what it knows** (the tech tree's farming steps), and **how rich its land is**. The per-people number shrinks to a small
  "kind factor", 0.8–1.2.
- Below is that ladder, each rung with real published densities. In short:
  foragers **0.01–0.4** (typical 0.1, rich land 0.3); fishing foragers **0.3–2**, rich coasts up to **~9**; gardeners
  **~2–20** (typical 4–10); plough farmers **~2.5–14** in the early bronze age (late bronze age estimates 4.5–63), **~11–18** Roman, **~13** early medieval, **~35** at the
  medieval peak; irrigation farmers **30–240 per km² of watered land** (and their whole country far less); pastoral nomads
  **~0.3–2**; mixed herder-farmers **~1–15** (the weakest rung: modelled capacities and a mixed Mali class). A dwarven hold is a plough or terrace rung for its valleys plus what it trades
  for. Mushrooms add little food: they turn crop waste into a few hundred calories a kilo, a relish, not a staple.
- Every rung rises with land quality: from the poorest to the richest land ~8× for gardeners (Papua New Guinea) and ~14× for
  foragers on the fitted line from poor to rich plant growth (the scatter is wide: medians of the poorest and richest fifths differ ~7.5×).
- What it does to the peoples: humans lose their head start **only where other kinds farm beside them**. Forest orcs (now 2),
  hobgoblins (4) and elves (4) would stand level with human farmers at the same tech; the hunting and herding kinds (tabaxi,
  leonin, goliaths, firbolgs, bugbears, lizardfolk) stay sparse until some of them take up crops or herds. So humans' share
  should fall a lot, but how far depends on question 2 (who gets to farm) more than on any number here.
- One bug found on the way: halflings (12) and gnomes (12) and dwarves (7–8) are not seen as farmers by the model, so they skip
  the "foragers until you farm" cap and ignore their land's quality (inbox draft).

## Where density lives now

- **The number:** `demography.density` per lineage in `planet/lineages/samples/dnd.toml` (and `seven_meals.toml`); trait defaults in
  `planet/lineages/spec.py::DEMOGRAPHY` (agricultural 10, nomadic 0.6, subterranean 3, miner 3, coastal 3, flies 0.6). Read through
  `Lineage.demo("density")`. Current dnd values (way from `spec.WAYS`, food shares from `landuse.shares`):

  | people | way | density /km² | farm / herd / forage share |
  |---|---|---|---|
  | human | farmer | 10 | 1 / 0 / 0 |
  | human_farmer | farmer | 12 | 1 / 0 / 0 |
  | human_herder | transhumant | 3 | 0.15 / 0.85 / 0 |
  | human_nomad, steppe_orc | pastoral_nomad | 0.8 | 0 / 1 / 0 |
  | human_seafarer | fisher_forager | 0.7 | 0 / 0 / 1 |
  | human_arctic | forager | 0.05 | 0 / 0 / 1 |
  | halfling | forager (inherited from archaic_human) | 12 | 0 / 0 / 1 |
  | gnome | – | 12 | 0 / 0 / 0.5 |
  | dwarf, hill_dwarf | – | 7, 8 | 0 / 0 / 0 |
  | goblin, kobold, troglodyte | – | 5, 4, 3 | dens peoples |
  | elf / drow / sea_elf | horticulturalist | 4 / 2 / 1.5 | 0.25–0.5 / 0 / 0.5 |
  | hobgoblin | agro_pastoral | 4 | 0.5 / 0.5 / 0 |
  | forest_orc | farmer | 2 | 0.5 / 0 / 0.25 |
  | dragonborn | – | 2 | – |
  | tabaxi, leonin, bugbear, firbolg, orc, lizardfolk, tortle, aarakocra, kenku, archaic_human | – / forager | 0.3 | forage or herd |
  | goliath, giantkin | – | 0.15, 0.1 | forage |

- **The forager 0.35 entry:** `planet/lineages/history/growth.py::ERA_DENSITY` = {forager 0.35, horticulturalist 5.0}, applied by
  `GrowthMixin._set_era_density`: a people with any farm share lives at most at 0.35 until it takes up a crop, then at most 5 until it
  is mainly farmers with a plough animal (`_note_eras`: AGRARIAN_FARM 0.5), then at its own number. Peoples with farm share 0
  (halflings, gnomes, dwarves, herders, foragers) are never capped.
- **How density feeds population:** `planet/lineages/history/model.py` builds `self.dens` (the number, x a share band's nudge,
  `history/bands.py`) and `self._dmap = dens x F`, F from `planet/lineages/prey.py::people_fields`: per cell
  (layer / reference)^0.75 for the way's farm (total NPP / 330 g C/m²/yr), herd (grazing NPP / 263) and forage (foraging score / 2.83)
  shares; 1 for fishers, sea nomads, and any people with none of those shares (dwarves, gnomes). `history/peoples.py::population`:
  people per cell = presence x density there x cell area. Density also weights the cell mix (`compose.py::compose`, heads not
  ground: "12/km2 farmers beside 2/km2 foragers count 6:1"), land use (`landuse.py`), settlements (`settlements.py`), the specialist
  pool in the tech tree (`techtree.py::density_x`, dens_ref 10), cities and the counter-pressures.
- **The workbench:** `viewer/lineages.html`: the "density /km²" input per people (line ~529, ~703, the table at ~723/740) and the
  results column (~902), with the tooltip "people per km² of full habitat"; no rung is shown.
- **The 10–12 vs 0.3 gap:** human 10 and human_farmer 12 against 0.3 for every D&D hunting people (lane 83, owner D20:
  Binford's upper quartile for foragers). A farming kind other than humans either has a lower number (forest orcs 2, hobgoblins 4,
  elves 4) or is not modelled as farming. With density weighting the mix, a human cell counts 30–40 heads to a tabaxi's one.

## The ladder

Densities are persons per km² of the land the people holds unless marked "per km² cultivated". "Read" says what was actually opened
in this lane (2026-11-02); every number below was taken from that reading, not from memory.

| rung | density range /km² | how it should scale | source, and what was read |
|---|---|---|---|
| **Forager, hunting-led** | median 0.02, middle half 0.01–0.044, top 0.41 | with plant growth, steeply (see below) | Binford 2001 Table 5.01 via D-PLACE (dplace-dataset-binford, var B008, B004 "Hunting"; n=80). Read: the dataset itself, computed here. |
| **Forager, gathering-led** | median 0.12, middle half 0.036–0.33, top 3.9 | with plant growth | same, B004 "Gathering", n=142 |
| **Forager, all 339** | median 0.11, upper quartile 0.34, top tenth 0.67 | log10 density = −4.42 + 1.28 log10 NPP (r 0.55); terrestrial only (fishing < 30%, n=171): slope 1.26 (r 0.47): 0.008 at NPP 100, 0.036 at 330, 0.11 at 800 g C/m²/yr; upper quartile at NPP ≥ 600: 0.37 | same; NPP from the Miami model on D-PLACE ecoClimate T and rain (formula and parameters read in Adams, White & Lenton 2004, Ecol. Model. 177:353, App. A.1, Table B.3). Arctic and boreal (≥ 55°): median 0.016, upper quartile 0.049. Script: `binford_by_npp.py` here. |
| **Fishing / sedentary foragers** | Binford sedentary groups: median 0.41, upper quartile 0.72, top tenth 1.2 (n=103); fishing-led: median 0.25, upper quartile 0.55 (n=117). Northwest Coast 0.1–2 (Haida 0.62–0.96, Chinook 1.49, Puyallup 1.95); California ~0.1–9 (Kawaiisu 0.12, Chumash 8.4–9, E. Pomo 2–6.3) | with the fish and shellfish, not the land's NPP: "very high population densities in small territories at high latitudes" (Kelly p. 46) | Binford via D-PLACE (above; B009 sedentary, B004 fishing). Kelly 2013, *The Lifeways of Hunter-Gatherers* 2nd ed., Table 7-3 pp. 178–181 (persons/100 km²), read as archive.org text (the table runs on to p. 184). Kroeber 1939 Table 9 p. 143 gives far lower area-wide contact totals (California 0.43, Northwest Coast 0.28; why the two differ was not sourced here). |
| **Gardening / swidden** (cultivation, no plough) | Boserup's classes: forest fallow 0–4, bush fallow 4–64, short fallow 16–64. Papua New Guinea, total land: 5 (very low land quality) / 7 / 12 / 20 / 40 (very high), all PNG 9–11; 44 per km² used for farming. First farmers (LBK Rhineland, 51st c. BC): 0.42–0.6 over the whole region, ~6–8.5 inside the settled area (my arithmetic: ~1 house per km² there x 6 or 8.5 a house) | steeply with land quality (PNG ×8 from worst to best); with cropping intensity (PNG: density = 1.15 R + 7.5, R² 0.44, R = Ruthenberg's R-value: years cropped / (cropped + fallow) x 100) | Boserup 1981 p. 23 **read only as quoted** in Pingali & Binswanger 1983, World Bank ARU 1, Table I (the copy reads bush fallow 4–64; the often-quoted 4–16 not confirmed). Bourke & Harwood (eds) 2009, *Food and Agriculture in PNG*, ANU, p. 44 Fig. 1.2.10, p. 45, Table 1.12.1 p. 102, rural densities (read, OAPEN PDF). Zimmermann, Wendt, Frank & Hilpert 2009, *Proc. Prehist. Soc.* 75:1–53, p. 13 and p. 42 n. 4 (read). |
| **Plough farming, rain-fed, by tech** | bronze age: 2.5–14 (Early Bronze Age Greece), 4.5–63.5 (Late Bronze Age Greece; others 25–35, ~30); Roman (iron, villas): 10.8–17.9 (Rhineland west of the Rhine), 20–25.7 in southern Germania inferior (mixed land, military excluded); early medieval England 1086: ~13; England's medieval peak 1315–1348: ~35–36; after the plague 1377: ~19, 1541: ~21 | with land and survey: Roman villas 1.7/km² in a fully surveyed loess key area against 0.2–0.3 in regional studies (×6–8; the paper does not put it down to soil); a ceiling: Broadberry et al. find it "hard to see how a population much above" 4.81 M (England, c. 1348) could have been fed | Renfrew 1972, Lukermann and Angel **read only as quoted** in Butzer 1976 pp. 82–84. Zimmermann et al. 2009 PPS p. 18 (read; the 20–25.7 is their quote of Rothenhöfer 2005). Broadberry, Campbell & van Leeuwen 2011, "English medieval population" (Warwick conference draft; read): 1.71 M (1086), 4.69 M (1315), 4.81 M (1348), 2.50 M (1377), 2.83 M (1541); densities are my arithmetic over England's 132,932 km² (Wikipedia infobox). |
| **Irrigation farming** | per km² **cultivated** (watered) land, Egypt: Nile valley 30 (4000 BC), 75 (3000), 130 (2500), 140 (1800), 180 (1250), 240 (150 BC); delta 10–135; New Kingdom nomes median 172, up to 500; 1882 census 240–280 (2.8 M on 11,600 km² south of Cairo); Libyan oases 444 in 1927 after artesian wells. Boserup's multi-cropping: > 256 | with how much land water reaches: the shaduf (bronze age) added a posited 10–15% of arable, the saqiya (Ptolemaic) as much again; Butzer triples the Greek dry-farming densities for the floodplain and adds "at least 50%" for artificial irrigation | Butzer 1976, *Early Hydraulic Civilization in Egypt*, U Chicago, Table 4 p. 83 ("hypothetical"), pp. 77, 80, 82–84, 97 (read, ISAC PDF). Wet-rice China 1820 (south-east coast 178, Yangzi delta prefectures > 400, Suzhou ~902, not self-fed): Wang & Huang 1999, Bull. Inst. Hist. Philology 70(2), **abstract only**. |
| **Pastoral nomads** | Mongolia: ~0.35 (c. 1911), ~0.54 (1956 census, towns included); Mali's sparse herding zone < 6; Kenya's driest districts: modelled herding-only carrying capacity 1–2; modern Kenyan pastoral counties ~0.6–12 (0.08–1.48 households/km² x an assumed 8 a household, my arithmetic) | with grazing: people ≈ livestock per km² ÷ livestock per person; one estimate Khazanov reports (and calls of little use for generalising): 2–4 standard stock units a head without grain (1 SSU = 10 sheep or goats, 2 cows, 1 camel) | Mongolia: Wikipedia "Mongolia" and "Demographics of Mongolia" (area 1,564,116 km², ~548,000 people c. 1911 from 115,000 monks = 21%; 845,481 in 1956), my arithmetic. Wilson 1986, ILCA Research Report 14, §3 (read, FAO page). Kalff, Downing & Smith 1985, J. Arid Env. 9:173, **abstract only**. Warrier et al. 2024, Ecology & Society 29(1):18, Table 2 (read). Khazanov 1994, *Nomads and the Outside World*, p. 31 (read, archive.org text). |
| **Agro-pastoral / transhumant** | Mali outside the sparse herding zone 6–14 ("the remainder of the country"; its > 14 class is mostly irrigated or intensive farming, not agro-pastoral); Kenya modelled carrying capacity from 1–2 (herds only, driest) to ~200 (maize and beans at 760 mm rain) | steeply with rain: rain-fed crops impossible below ~200 mm and "extremely risky" at 200–400 (Wilson) and dominate by ~760 mm (Kalff) | Wilson 1986 (read). Kalff et al. 1985 (**abstract only**). |
| **Dwarven hold** (fed by grown or traded food) | its valleys' rung (plough or terraces) on the land it farms, plus imports. Terrace country: Ifugao "as high as 155 persons per sq km" in places. A grain-fed town needs ~0.8 ha of arable a head in northern Europe (≤ ~125 per km² of arable) | with the farmland it holds and the trade it can buy; fungi add little: oyster mushrooms give ~1.6 kg fresh per kg dry straw (lab bags), ~33 kcal/100 g, so ~520 kcal per kg of straw against ~1,800–2,600 kcal in a kg of wheat | Worldmark Encyclopedia of Cultures, "Ifugao", via Encyclopedia.com (**tertiary**). Clark 1999, UC Davis Econ 110A notes ch. 4 p. 7 (read; medieval yields, the cheapest diet: "about 2 acres of arable per person"; wheat 800–1,200 kcal/lb). Ramos et al. 2010, Nauka Przyroda Technologie 4(3) (read: P. ostreatus 157.9%, P. eryngii 168.3%). USDA FoodData Central SR Legacy 168580 (oyster, 33 kcal, 89.2 g water) and 169251 (white, 22 kcal) (read via the FDC API). |

### Tech-stage steps the tech tree implies

The tree (`planet/lineages/samples/techtree.toml`) gives these steps on the food track; each maps to a rung or a step within one:

| tech step (era, earliest kyr) | rung it opens or raises | sourced step |
|---|---|---|
| foraging lore, fishing, hooks, nets, weirs (stone age) | forager → fisher-forager where the water is rich | Binford: sedentary and fishing-led medians 12–20× the hunting-led one |
| cultivation (stone age, 11.5), hoe_cultivation, raised_fields | gardening | Boserup forest fallow 0–4; LBK 0.4–0.6 regional |
| herding (11), transhumance, milking | pastoral nomad / agro-pastoral | Mongolia 0.35–0.54; mixed farming: see the agro-pastoral row (weakly sourced) |
| manuring (stone age, 7.9), crop_pulses, crop_rotation (bronze, 7) | shorter fallow: gardening's upper part | Boserup short fallow 16–64 |
| plough + ox_traction (bronze age, 6.5) | plough farming, low | Early Bronze Age Greece 2.5–14; Late Bronze Age 4.5–63.5 |
| irrigation (bronze, 8), shaduf (4.3), noria (classical, 2.3) | irrigation, on watered land only; each lift device +10–15% of arable | Butzer: 30 → 130 → 240 per km² watered |
| terracing (bronze, 5) | plough or garden rung on steep land | Ifugao (tertiary) to 155 |
| iron (classical, 3.3), moldboard_plough (classical, 2.3) | plough farming, middle | Roman Rhineland 11–18 |
| three_field (medieval, 1.2), hay_fodder, scythe | plough farming, high | England 13 (1086) → 35 (1300s) |
| renaissance (dnd's present era) | no new rung sourced; England 1541 is post-plague (21), not a ceiling | – |

### Things the sources agree on

1. **Fishing is its own rung.** Rich-water foragers live 12–20× denser than hunting-led ones (medians) and as densely as early gardeners; they track the
   fish, not the land's NPP (as dense as the first farmers' regional 0.4–0.6, below the gardening rung). The model already gives fishers F = 1 (no land layer); the ladder would give them a water layer instead.
2. **Every rung rises with land quality**, at least as steeply as the model's 0.75 power: foragers' fitted slope is ~1.3 on NPP
   (noisy, r ≈ 0.5), PNG gardeners ×8 from worst to best land. A power near 1 is the sourced lean.
3. **Irrigation numbers are per watered km².** Applied to a whole country they would be far too high: they count only the watered
   land, a small part of any country. Irrigation should lift only
   the cells water can reach (rivers, floodplains), not a people's whole range.
4. **Within one way of life, tech multiplies density several times** (plough: 2.5–14 early bronze age Greece → 11–18 Roman Rhineland →
   13 → 35 medieval England; different regions, so a rough guide), less than the jump from foraging to farming (forager 0.1 →
   gardener ~5: ~50×). Butzer's Egypt, one region, rose 30 → 240 per watered km² over four thousand years (8×).

## What changes for each people

At the same tech, land and way of life, every kind would sit within 0.8–1.2 of the others. Expected shifts (not run; step 2
will measure on `tools/peoples_robust.py`):

- **Humans:** their farmers keep the plough rung (at the renaissance present ~15–35 on good land, more than today's 10–12), so
  human *numbers* need not fall; their *share* falls wherever another kind farms the same land. The 30–40× edge over the 0.3
  kinds goes only where those kinds take up farming or herding. Human foragers, herders, nomads and seafarers move to the same
  rungs as everyone else's (they are already close: 0.05, 3, 0.8, 0.7).
- **Forest orcs** (farmer, 2 → the plough rung): up ~5–10×. **Hobgoblins** (agro-pastoral, 4 → 3–15): about level to ~2× up.
  **Elves** (gardeners, 4 → gardening rung ~2–20 by land): level on average, denser on rich forest soil, sparser on poor.
  **Drow, sea elves** (2, 1.5): up toward the elves.
- **Halflings, gnomes** (12, not seen as farmers): if made farmers, about level with human farmers (the kind factor), but capped
  at forager and gardener density until they farm, so slower early.
- **Dwarves** (7–8 flat): a hold's number would follow its valleys (plough or terrace rung) and its trade, so higher than today
  in rich mountain valleys, much lower on bare peaks. Mushrooms would not make them denser than humans; trade or terraces could.
- **Goblins, kobolds, troglodytes** (5, 4, 3 as den foragers): the forager rung is 0.01–0.4; their dens' density (your D20 "dense
  but narrow") has no human analogue to source. See question 4.
- **Tabaxi, leonin, goliaths, firbolgs, bugbears, lizardfolk, tortles, orcs, kenku, aarakocra** (0.15–0.3): unchanged as foragers
  (0.3 is Binford's upper quartile; leonin and tabaxi a little lower with the kind factor 0.8); up 10–100× for the part of each
  that takes up herding or crops.
- **Dragonborn** (2, no way set): depends on the way they are given.

## Questions for Daniel

1. **What a rung's number means.** (A) the people's *mean* over the land it holds, scaled up and down by land quality (as now);
   (B) its density on the best land, scaled down. Lean **A**: the sources are mostly regional means (Binford, England, PNG totals).
2. **Who changes way of life, and how much.** Your ruling says part of a people shifts with tech. (A) the share of a people on
   each rung follows its land (the farmable cells farm once the people knows cultivation, the rest stay foragers or herders;
   PW-1373 B, 11-02: a people knows a crop once it has stood on a fifth of its land for ~0.4 kyr / its leaning to farm, so hunting
   kinds learn ~10x slower, and the cat-folk lean to herds over crops: hunters-lag.md);
   (B) a fixed share per kind; (C) a share that grows with time since the tech arrived. Lean **A**: it is the land, not the kind,
   that decides who farms, and it makes humans fall only where others really farm.
3. **The land-quality power.** Today 0.75 on (NPP / reference). The sources say ~1 (foragers 1.3, noisy; PNG and Roman soils ×6–8).
   (A) keep 0.75; (B) 1.0 for every rung; (C) per rung (foragers 1.3). Lean **B**: one simple power, closer to the evidence.
4. **Den peoples (goblins, kobolds, troglodytes).** No real people lives as a dense den-forager. (A) forager rung, with the
   kind factor at its 1.2 top (denser but sparse); (B) a "den" rung of ~1–3 (a judgement, marked); (C) give them a way that
   farms or herds. Lean **A**, then **C** for the part of them that farms, as with any people.
5. **Irrigation scope.** (A) the irrigation rung only on cells a river or lake can water (floodplain share), the plough rung
   elsewhere; (B) a flat bonus over a people's whole range. Lean **A** (the numbers are per watered km²).
6. **The dwarven hold.** (A) the hold's density = plough or terrace rung on its own farmed valleys, plus food bought with ore
   and craft (up to a cap, e.g. half its food); mushrooms a small bonus on its crop waste; (B) a fixed hold rung (e.g. 1.5× the
   plough rung, a judgement). Lean **A**: it ties dwarves to their valleys and trade as you ruled, and it is what the sources
   allow; B is simpler.
7. **Renaissance top rung.** No source here for c. 1500–1700 densest regions (Low Countries etc.); England 1541 (21) is after
   the plague. (A) cap the plough rung at the medieval peak, ~35; (B) source an early-modern rung first (inbox draft). Lean **A**
   for now.

## Second check

An independent agent re-opened every source on 2026-11-02 (all PDFs and pages fetched again, except Bourke & Harwood: OAPEN and
the ANU mirror returned 503, so it was checked on the copy downloaded earlier the same day) and recomputed the Binford numbers with
its own code from the D-PLACE files. **Confirmed:** every Binford median, quartile, fit and count; the Miami formula and the D-PLACE
rain unit; Kelly's Table 7-3 figures and the p. 46 quote; Kroeber's Table 9; Pingali & Binswanger's Boserup table (bush fallow
**4–64** in that copy); the PNG regression, 11 and 44 /km² and the 5/7/12/20/40 table; Zimmermann's LBK 0.42, 0.6 ± 0.1 and Roman
10.8–17.9; Broadberry's populations and the England arithmetic; Butzer's Table 4, p. 77, p. 80 and pp. 82–84 figures; the Wang & Huang
abstract; Wilson's density classes and rain limits; the Kalff abstract; Warrier's Table 2; the Mongolia figures; Ifugao 155; Clark's
2 acres and 800–1,200 kcal/lb; Ramos's 157.9% and 168.3%; the USDA kcal and water.

**Corrected after the check** (already changed above):
- Butzer's oases 444 is on p. 97, not p. 89, and is a 1927 figure; Clark's quote is on p. 7, not p. 4.
- California fishers' low end is ~0.1 (Kawaiisu 0.12), not 0.2; Kenya pastoral counties ~0.6–12, not 1.5–12 (the 8 a household is
  this page's assumption, not the paper's); LBK inside the settled area ~6–8.5, not 7–10; the forager productivity span is ~14× on
  the fitted line (the raw medians of the poorest and richest fifths differ only ~7.5×).
- The PNG R is the land-use intensity R-value (how often land is cropped over time), not the share of land cropped.
- Overstatements removed: Rothenhöfer's 20–25.7 is for a mixed region, not "the best loess"; the villa 1.7 vs 0.2–0.3 compares a
  fully surveyed key area with regional studies and is not about soil (dropped as a land-quality example); Wilson's 6–14 class is
  "the remainder of the country" and his > 14 class is mostly irrigated or intensive farming, so neither is labelled agro-pastoral;
  Kalff's 1–2 and ~200 are modelled carrying capacities; Khazanov's 2–4 SSU is an estimate he reports and doubts; Butzer also gives
  Renfrew's **Late** Bronze Age Greece at 4.5–63.5 /km² (others 25–35, ~30), now in the plough rung, and the "tech multiplies ~3×"
  claim is replaced (its numbers came from different regions); the "3–10× too high" for irrigation had no worked basis and is gone;
  "later work revised contact numbers up" (Kroeber vs Kelly) had no source and is gone.

## Not found or not readable

- Zimmermann, Hilpert & Wendt 2009, *Human Biology* 81:357 (the per-period table, Iron Age to 1800): open access on Wayne State
  Digital Commons, but the site blocks automated fetches. Daniel could download it by hand; it would firm up the bronze, iron,
  medieval and c. 1800 steps for central Europe.
- Boserup 1965 and 1981 themselves (lending-only); Carneiro 1960, Conklin, Netting; McEvedy & Jones; Adams 1981; Dyson-Hudson
  1980; Hassan 1981; Kremer 1993 (gives world totals, not densities: not needed).
- Binford 2001 the book (only its Table 5.01 data, via D-PLACE).
