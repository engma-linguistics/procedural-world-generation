# Tech spread at the present-day finish: is anyone far behind? (PW-1485, D58; scout 206)

Daniel's question (11-07, on D58): by the present-day finish of the tech tree, are many peoples far behind? And does the way
technologies are spread look even vaguely realistic?

**Baseline.** Every number below is main's shipped tree at 330b021b, with own_floor off. The tree was rebuilt in memory over each
stored run's own history. A rebuild with the run's own seed matched the stored tree for every people on all four runs. Each run got
8 draws of the tree's luck: the run's own seed plus the next 7. The Earth figures are the sourced ones in section 4. Script:
[spread1/measure.py](spread1/measure.py). Tables: [spread1/tables.py](spread1/tables.py). Full output:
[spread1/tables_out.md](spread1/tables_out.md).

## In plain words

- **Nobody is waaaay behind, and that is the problem, not the comfort.** Daniel's worry was the opposite of what happens. Take the
  peoples with hands (the dragons are handless and are dealt with separately below). By the present, about 95% of them hold the
  whole core ladder: farming, herding, pottery, copper, bronze, iron, towns, cities, kingship, law and writing. On the dnd worlds
  that is all but one people in 29, and in Seven Meals 45 of 48. Weighted by population it is 98-100%.
- **The spread runs too fast and is the same for every tech.**
  - Writing goes from the first people to 9 peoples in 10 within about 1,000 years (0141d1: 31% of today's peoples 4,000 years
    ago, 91% 3,000 years ago).
  - Copper and kingship do the same. Of the tree's 552 techs, 505 cross a border at exactly the same rate (`spread = 1.0`).
  - So the tree has no "fast tech, slow tech" difference. Crops and iron spread no faster than writing or states, which on Earth
    were famously slow.
- **On Earth, around 1500 CE or the ethnographic present, the picture was very different.**
  - **Farming:** about 1 culture in 5 had no farming at all (20% in Murdock's Ethnographic Atlas).
  - **Metal:** only about half had any metalworking (47%).
  - **States:** only about 1 in 9 was a state, meaning three or more levels of authority above the village (11%).
  - **Overall:** Comin, Easterly and Gong scored countries' technology in 1500 AD. The average was 0.46 on a 0-1 scale. Europe
    scored 0.87, the Americas 0.14 and Oceania 0.12. 78% of the differences between countries were differences between continents.
  - **By people rather than cultures:** foragers were only ~1% of people in 1500, but they held about a third of the land.

  So on Earth most *people* had the core ladder and most *cultures* did not. In our worlds both are near 100%.
- **The pattern we do have is sensible, as far as it goes.**
  - Small and insular peoples are the ones behind (rank correlation with years behind: insularity +0.5 on every run, population
    -0.4 to -0.5).
  - Techs tied to the land spread only where the land allows. The plough reaches 40-54% of peoples and the wheel 33-38%, because
    both need cattle or horses. Timber crafts are missing in the steppe and the desert, and each crop and herd beast stays in its
    own biome.
  - Those are realistic reasons to differ. They just never bite on the big things: writing, states and metal.
- **Who is actually behind, and why** (the causes are in the model):
  - **The dragons** (sapient, handless) hold their 10 body techs and nothing else, since every tool needs hands (PW-987). That is
    by design.
  - **The sea peoples** (merfolk, storm giants) are 10-23 kyr behind. Their countries hold no timber or forage goods, so they have
    no fire-making and no farming.
  - **Isolated peoples** with no neighbour now are behind. Examples: Seven Meals' half-elves (no copper, writing or cities) and
    anja (no copper or iron).
  - **Peoples 3-4 kyr behind on the raw count** are the dwarves, orcs, leonin and antelope folk. They are missing timber-based
    crafts (bark canoes, birch tar, charcoal) because their country has no forest. They are **not** behind on the ladder: they
    have writing, iron and kingship.
- **Why the core is near-universal.** Three mechanisms, all measured:
  1. Every dnd people with hands touches 9 to 37 others today, so no people is cut off the way the Americas or Australia were.
     "No neighbour holding it" is only 3-5% of the techs a people lacks.
  2. Writing, law and kingship cross borders like any other tech. The taker's way of life does not matter. Foragers hold writing
     in 70 of 80 people-draws in Seven Meals, nomads in 15 of 16 on 0141d1. 87-94% of writing's holders took it by contact (dnd
     201 of 215, Seven Meals 184 of 355) or by sharing within the people (Seven Meals 155 of 355).
  3. A people "holds" a tech once any part of it knows it. dnd peoples are huge, at 0.1-550 million people across up to 100
     landmasses. So the fringe that would stay behind inside a people (its Amazonians and Kalahari foragers) is invisible.
- **Verdict.**
  - **PW-1485 (D58): close it.** The own-invention floor would only make this more uniform, so "off" is right.
  - **The spread does not look realistic for the slow techs.** Writing, states and law are near-universal within ~1 kyr. One
    inbox draft offers options: [draft-slow-techs-spread-like-crops.md](../../../../issue-tracking/inbox/draft-slow-techs-spread-like-crops.md).
    My lean is a sourced slow spread for the admin and urban techs, plus "the taker must be settled enough to use it". It is not
    urgent. The fast, land-bound side already looks right.

## 1. How the tree reaches the present

The tree is built over the stored history ([techtree.py](../../../../planet/lineages/techtree.py) docstring). A people invents a tech
at a hazard: rate x culture x pool strength x ramp, per region learner (D55, round 2). It takes a tech from a neighbour while the
two are in contact. The tech moves as a front crossing the taker's country at ~1 km/yr (Pinhasi et al. 2005), x the tech's `spread`
x the border share x openness. Once the front arrives, the taker adopts the tech as soon as it holds the prerequisites, the goods
(unless the tech is `traded`) and a body that can hold the tool. The era cap (`renaissance`) bounds what exists. The present is
0 kyr ago. Nothing in the taker's way of life gates adoption.

## 2. Who holds what at the present

Peoples with hands, the median of 8 draws, with the range over draws in brackets. "Pop" is the share of the living population.
"Wait" is the median time from the world's first find to each holder's date.

| tech | 0141d1 peoples (pop) | 3e0eb4 peoples (pop) | 07c755 Seven Meals peoples (pop) | wait yr (0141d1 / 07c755) | holders who invented it (0141d1) |
|---|---|---|---|---|---|
| cultivation | 97% (100%) | 97% (100%) | 96% (100%) | 1,503 / 1,902 | 12% |
| herding | 97% (100%) | 97% (100%) | 96% (100%) | 1,907 / 1,963 | 39% |
| copper | 97% (100%) | 93% (100%) | 90% (99%) | 855 / 702 | 9% |
| bronze | 97% (100%) | 93% (100%) | 90% (99%) | 575 / 653 | 7% |
| iron | 95% (38-97%) (98%) | 91% (100%) | 90% (99%) | 1,107 / 886 | 7% |
| plough | 40% (82%) | 38% (84%) | 54% (94%) | 1,741 / 1,897 | 31% |
| wheel | 38% (69%) | 33% (82%) | 33% (65%) | 1,398 / 649 | 19% |
| cities | 97% (100%) | 97% (100%) | 94% (100%) | 715 / 556 | 9% |
| kingship | 97% (100%) | 97% (100%) | 94% (100%) | 865 / 440 | 11% |
| law | 97% (3-97%) (100%) | 97% (100%) | 93% (100%) | 1,092 / 681 | 14% |
| writing | 97% (100%) | 97% (100%) | 94% (100%) | 964 / 608 | 5% |
| coinage | 74% (0-97%) (82%) | 90% (94%) | 88% (99%) | 705 / 597 | 10% |
| printing | 88% (0-97%) (95%) | 90% (93%) | 92% (99%) | 1,022 / 673 | 7% |
| gunpowder | 79% (0-86%) (96%) | 78% (89%) | 79% (95%) | 819 / 784 | 6% |

- **Run a2b637 is the same world as 3e0eb4** (dba204). Its tables match 3e0eb4's to within a few years (tables_out.md), so the
  dnd sample is really two worlds.
- **The late techs are all-or-nothing within a draw** (iron 38-97%, law 3-97%, printing 0-97%). Either nobody has found the tech
  yet, or the whole connected world holds it within ~1 kyr.

**Over time** (0141d1: the share of today's peoples with hands holding the tech by that date, median of draws; Earth's first date is
the tree's own sourced `earliest_kyr`):

| tech | Earth's first (kyr ago) | 4 kyr ago | 3 | 2 | 1 | 0.5 | now |
|---|---|---|---|---|---|---|---|
| copper | 6.95 | 57% | 95% | 97% | 97% | 97% | 97% |
| iron | 3.3 | 0% | 0% | 17% | 76% | 90% | 95% |
| kingship | 5.2 | 2% | 45% | 95% | 97% | 97% | 97% |
| writing | 5.3 | 31% | 91% | 97% | 97% | 97% | 97% |
| law | 4.1 | 0% | 9% | 74% | 93% | 97% | 97% |
| printing | 1.3 | 0% | 0% | 2% | 33% | 72% | 88% |

In Seven Meals, writing is at 93% by 4 kyr ago and kingship at 93% by 3 kyr ago. The 0.5 kyr column is the fairest comparison with
Earth's 1500 CE, and there the core ladder is already at 90-97%.

**By era** (pairs of people and tech held, out of the techs the world holds, 0141d1): stone age 87%, bronze age 73%, classical 62%,
medieval 48%, renaissance 54%. Seven Meals: 87, 76, 69, 62, 68%. The younger the tech, the fewer hold it. That is right, but it is
driven by the late, local and goods-bound techs, not by the ladder.

## 3. Who is behind and why

Two measures of how far behind a people is, per draw and then the median:
- **Years behind the world:** the date at which the world as a whole had first found as many techs as this people holds now.
- **Years behind the leader:** the same date read off the leading people's own record.

A "gap" is a tech that some living people holds and this one lacks, although it holds the tech's prerequisites. Each gap is put
under the first obstacle in the model's own order (Calendar.can):
- body: no hands;
- land: no goods, and the tech is not traded;
- stock: a crop or animal the history never gave it;
- own_only: the tech has spread 0;
- no_holder_neighbour: no neighbour holds the tech now;
- front_en_route: a neighbour holds it, but the front has not arrived.

**All gaps, draws pooled:**

| obstacle | 0141d1 | 3e0eb4 | 07c755 |
|---|---|---|---|
| stock (a crop or herd beast of another biome) | 45% | 49% | 55% |
| front en route (a neighbour has it, still arriving) | 35% | 35% | 9% |
| land (goods missing: mostly timber) | 12% | 9% | 21% |
| no neighbour holds it | 5% | 3% | 13% |
| body, own-only, other | 3% | 4% | 2% |

**Furthest behind** (the median over draws; the full lists are in tables_out.md):

| run | people | techs held | behind the world (yr) | the cause in the model |
|---|---|---|---|---|
| 07c755 | merfolk | 79 | 23,300 | sea people: no timber, forage or fertile land in its country, so no fire-making, farming or pottery |
| 0141d1 / 3e0eb4 | storm giant | 102 | 11,773 | the same (lives at sea) |
| 07c755 | half-elf | 118 | 9,918 | a hybrid born 10 kyr ago with no neighbour: 50 of its gaps are "no neighbour holds it"; no copper, writing or cities |
| 07c755 | anja | 293 | 5,126 | a group of orcs with no neighbour; no copper or iron (no ore, and no neighbour to trade with) |
| 0141d1 | dwarf, leonin, orc | 282-320 | 3,300-3,800 | ~33 land gaps, nearly all timber crafts (no forest); they still hold writing, iron and kingship |
| 07c755 | orc, arha, antelope folk, lizard desert | 341-390 | 3,600-4,200 | the same: timber-less steppe and desert |
| all | 10 dragon kinds | 10 | - | handless: tools need hands (PW-987), by design |

**What goes with being behind** (Spearman rank correlation with years behind the world, peoples with hands; positive means more of
it, further behind):

| attribute | 0141d1 | 3e0eb4 | a2b637 | 07c755 |
|---|---|---|---|---|
| insularity | +0.50 | +0.51 | +0.48 | +0.51 |
| log population | -0.36 | -0.47 | -0.54 | -0.40 |
| log area | -0.29 | -0.15 | -0.19 | -0.48 |
| neighbours now | -0.13 | +0.01 | +0.04 | -0.11 |
| land gaps | +0.32 | +0.18 | +0.18 | +0.44 |
| stock gaps | +0.38 | +0.31 | +0.40 | +0.21 |

- **Small and closed peoples lag.** That fits Henrich's and Kline and Boyd's pool-size effect, which the tree builds in through S.
- **The number of neighbours does not matter**, because everyone has many. dnd peoples with hands have 9-37 neighbours now, with
  a median of ~21. The cases where nobody next door holds a tech are rare, except for Seven Meals' handful of contactless groups
  and hybrids.
- **The specialist share s is 0.1 for every people but one**, because all of them hold cities: the top rung of the [[specialists]]
  ladder.

## 4. Earth, for comparison (sources fetched 2026-11-07)

**Ethnographic Atlas** (Murdock 1967; the D-PLACE files, Gray 1999 recoding, 1,291 societies, mostly coded 1800-1950). Shares are
of the societies with data. They were computed from the raw D-PLACE data
(raw.githubusercontent.com/D-PLACE/dplace-data/master/datasets/EA/data.csv, codes.csv and variables.csv).

| Earth (Ethnographic Atlas) | share of cultures | the nearest model figure (dnd 0141d1, peoples with hands) |
|---|---|---|
| no agriculture (EA028 = 1, "Complete absence of agriculture") | 20.3% (241 of 1,188) | cultivation lacking: 3% |
| mostly foraging (EA042 = 1-3) | 23.3% (301 of 1,290) | - (a dnd people has no single way of life, and it does not gate techs) |
| intensive agriculture (EA028 = 5-6) | 28.0% | plough 40% |
| metalwork present (EA055 = 1-4, 9) | 46.5% (453 of 975) | copper and bronze 97%, iron 95% |
| 2+ levels of authority above the community (EA033 = 3-5) | 25.0% | chiefdoms 100% |
| 3+ levels, states (EA033 = 4-5, "Three levels (e.g., states)") | 11.0% (127 of 1,155) | kingship 97% |
| foragers with 2+ levels | 3 of 291 | - |

The Atlas has no writing variable. Writing is in the Standard Cross-Cultural Sample, which was not fetched.

**Comin, Easterly and Gong** (2010, AEJ: Macroeconomics 2(3):65-97; read from the NBER working paper w12657, 2006,
https://www.nber.org/system/files/working_papers/w12657/w12657.pdf).
- **What is scored:** technology adoption in 1500 AD by sector, for military, agriculture, transport, communications (paper,
  books, printing) and industry (iron, steel). Each sector is scaled 0-1.
- **Overall:** 123 countries, mean 0.46, SD 0.32, min 0, max 1. The SD is "64 percent ... of the maximum feasible dispersion".
- **By continent:** Europe 0.87, Asia 0.66, Africa 0.32, America 0.14, Oceania 0.12.
- **Between continents:** the "share of total variance due to the between continent component rises to 78 percent" in 1500 AD.

Our worlds have no "continent left out". In the paper's terms, every dnd people with hands holds iron, paper and printing in most
draws.

**Comin and Hobijn** (2010, "An Exploration of Technology Diffusion", AER 100(5):2031-2059; the abstract at
research.vu.nl/en/publications/an-exploration-of-technology-diffusion/): "on average, countries have adopted technologies 45 years
after their invention". That is for the industrial and modern era. It shows that adoption lags exist even in a connected world, but
it does not set pre-modern speeds.

**The speed of a farming front.** Pinhasi, Fort and Ammerman (2005, PLoS Biology 3(12):e410): "The average rate of the Neolithic
spread over Europe is 0.6-1.3 km/y". The tree uses this for every tech. On Earth it describes farmers moving, not writing.

**Writing invented rarely.** "Four independent inventions of writing are most commonly recognized" (Mesopotamia, Egypt, China,
Mesoamerica; en.wikipedia.org/wiki/History_of_writing, a secondary source). The tree invents writing rarely too, as on Earth: 11 own
inventions among 215 holder-draws on 0141d1 (8 draws, ~1.4 per world), 14 among 355 in Seven Meals. The difference is in the spread.

**Foragers by people and by land.** Svizzero and Tisdell (2015, "The Persistence of Hunting and Gathering Economies", Social
Evolution & History 14(2):3-26, sociostudies.org/journal/articles/363702, citing Zvelebil and Pluciennik 2003): "They formed 1 per
cent of the population in AD 1500" and "occupied fully one third of the globe".

**Not fetched:**
- the share of land under states in 1500;
- a measured spread speed for iron or writing;
- Diamond's axis argument.

None of these is relied on above.

**How to read the comparison.**
- **Units.** A dnd "people" is a macro-people: millions of people across many landmasses. An Atlas society is one ethnic group, so
  a count of peoples is not a count of cultures. Weighted by population, Earth in 1500 was ~99% non-forager. Our ~100% farming is
  then fine, and a large majority of people under states with writing is plausible too. Earth's writing by population was not
  fetched.
- **What is off.** It is the **land and the cultures**: on Earth, a third of the land and a fifth to a quarter of cultures had no
  farming, half had no metal and nine in ten had no state.
- **In our worlds** only the sea peoples, the handless dragons and one or two contactless peoples lack these things.

## 5. Verdict

- **PW-1485: recommend closing it.** D58 A (own_floor off) is right. Turning the floor on would lift the small peoples, the very
  ones whose lag is the most realistic thing here.
- **Realism, partly.**
  - **What looks right:**
    - techs tied to land and stock differ by biome (plough, wheel, crops, herd beasts, timber crafts);
    - small and insular peoples lag;
    - invention is rare and most holders take techs by contact;
    - writing's first date is Earth-like.
  - **What looks off:**
    - the core ladder (metal, cities, kingship, law, writing) is near-universal among peoples with hands within ~1-1.5 kyr of its
      first find;
    - foragers and nomads hold writing;
    - there is no slow-spreading class of techs;
    - the 0.5 kyr-ago state is already ~95% on writing and kingship, where Earth's 1500 CE had 11% of cultures as states.
- **The causes:**
  1. one spread factor for 505 of 552 techs;
  2. adoption gated only by prerequisites, goods and body, never by the taker's way of life or density;
  3. a contact graph with no isolates (9-37 neighbours each);
  4. holding is per people, so a macro-people's backward fringe does not show.
- **Options** are in the draft. It is not v1-blocking: the viewer shows "who knows what", and the answer is merely too generous.

## Files

- [spread1/measure.py](spread1/measure.py): rebuilds each run's tree in memory over N draws. It is read-only on runs/ and never
  writes the goods cache. Usage: `PLANET_DATA=<main checkout> uv run python docs/review/culture/techtree/spread1/measure.py RUN 8
  out.json 8`.
- [spread1/tables.py](spread1/tables.py): the tables (`python tables.py out1.json out2.json ...`).
- [spread1/tables_out.md](spread1/tables_out.md): the full output for 0141d1, 3e0eb4, a2b637 and 07c755, including the per-people
  tables. The 8-draw JSONs (5-9 MB each) were left in scratch and are not committed.
- **Humans-only:** there is no stored humans-only run. Round 1's c1dd46 was a scratch run and is gone. It holds a single people,
  so it says nothing about spread between peoples. It was not re-run.
