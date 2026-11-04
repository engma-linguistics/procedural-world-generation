# Writing: the D49 gate, and how fast writing spreads (round 1, lane 184)

## In plain words

**The gate (D49, "real states gotta have writing").** A chiefdom now needs only writing's forerunner, proto-writing (pictograms), or
writing itself. Either can be its own people's or a neighbour's. A state or empire needs its own people to know real writing, and so
does a confederation. The result on the three showcase runs:
- Chiefdoms now reach far back: 5,900 years ago on a2b637 (it was 1,400), 6,800 on 0141d1 (3,500) and 7,900 on Seven Meals 07c755
  (6,300).
- States start when their people write: 1,100 years ago on a2b637 (1,400 before, when a neighbour's writing was enough), and about
  the same as before on the other two.
- On a2b637 the dwarves hold a quarter of the settled people and never learned writing in this run. So the present has fewer states
  and empires there: 239, against 347 before.

**The speed of writing.** You suspected writing spreads far, far too slowly. The numbers say it spreads about as fast as on Earth,
and faster in the tail. On the three runs it took 800 to 1,300 years from the first writing to half the settled people. That holds
with the runs as stored and again with today's tech tree. On Earth, writing took about 100 to 900 years to reach Uruk's nearest
neighbours (Susa, Ebla). It took 1,400 to 2,000 years to reach the Bronze-Age edge (Anatolia, Crete, Mycenae) and about 3,500 years
to reach Japan, Aksum or South-East Asia. The Inca never had it. The run that looked empty, a2b637, has a different cause. The
stored run drew its first invention late: 4,500 years after the first people was ready, where Earth took about 3,300. With today's
tech tree, keyed by lane 182, the same history gets writing 3,100 years ago instead of 1,400.

**What is slow, and the choice.** The slow part is the tail. A huge, inward-looking people can sit beside a dozen writing neighbours
for one to two thousand years. The reason is that writing crosses a people's whole country the way farming did, at about 1 km a
year, instead of crossing its towns the way scribes and merchants did. I did not change this, because changing how fast techs
spread is your call. A needs-decision draft lays out three options, A (keep), B (cross the town network) and C (trade speed). It
leans A for now, and B if you want big urban peoples to stop waiting.

**The picture.** In the peoples workbench, open **Technology**, then **Spread** (the last button on the view bar; it starts on
writing). It shows:
- The headline numbers: the first invention, half the settled people, nine in ten, and the last big people.
- A curve of the share of settled people, and of cells with a town, that knew the tech, century by century.
- A table of every people with places: when it first knew the tech and how (invented, or from whom), when it was ready, when it first
  bordered a people who knew it, and how long it waited at the border.
- The cultures, on the right.

"On the globe" goes to the Map view, where each people's land lights up from the moment it knew the tech.

## 1. The D49 gate

`planet/lineages/polities.py` (VERSION 7). It is two constants and three lines:
- `WRITING_TECHS = ("proto_writing", "writing")` is the chiefdom gate. It is unchanged in form: the seat's people or a neighbouring
  people know one of these.
- `STATE_WRITING = "writing"` is the state gate. A seat rises to a state (and so possibly an empire) only when its own people know it.
  A confederation's people must know it too. Before, a confederation passed the same neighbour-lenient check as a chiefdom.

All the numbers below are read from the stored runs with `derive()`, nothing saved. The baseline is main (`polities.py` VERSION 6),
with the same authored invasions.

| run | | first chiefdoms | first states | 4,000 years ago | present (chiefdoms / states / empires / dragon realms) |
|---|---|---|---|---|---|
| a2b637 (D&D) | main | 1,400 ago (drow) | 1,400 ago (goliaths, elves) | 19 dragon realms, nothing else | 1,848 / 174 / 173 / 23 |
| | D49 | 5,900 ago (gnomes) | 1,100 ago (humans) | 3,434 chiefdoms, 19 dragon realms | 2,467 / 83 / 156 / 23 |
| 0141d1 (D&D showcase) | main | 3,500 ago (tortles, humans) | 3,500 ago (humans) | 20 dragon realms | 3,339 / 74 / 152 / 12 |
| | D49 | 6,800 ago (elves, gnomes) | 3,500 ago (humans) | 2,454 chiefdoms, 20 dragon realms | 3,371 / 74 / 152 / 12 |
| 07c755 (Seven Meals) | main | 6,300 ago (antelope-kin) | 5,800 ago (half-orcs) | 2,058 / 63 / 51 / 19 | 2,838 / 54 / 214 / 17 |
| | D49 | 7,900 ago (goblins, hobgoblins) | 5,700 ago (half-orcs) | 2,064 / 64 / 52 / 19 | 2,837 / 54 / 214 / 17 |

**The antelope-kin empire (Seven Meals 07c755).**
- On main, the largest was East of Luki: a chiefdom from 5,900 years ago, an empire 4,500 years ago (1.27 Mkm2), gone by 4,300.
- Under D49 that one does not form. With chiefdoms from proto-writing, the land around it is held earlier by other seats, and the claim
  order shifts.
- The 4,000-year-old antelope-kin empires that remain are West of Luki: 0.78 Mkm2 3,700 years ago, and 0.77 Mkm2 4,000 years ago.
  Both were there on main too.
- The largest antelope-kin empire of the run is unchanged: East of Luki, 1.13 Mkm2, 800 to 200 years ago.
- The first antelope-kin state comes 5,300 years ago, when the oryx folk learn writing. On main it came 5,700 years ago, on a
  neighbour's writing.
- Overall: 1,261 states and empires founded by antelope-kin, against 1,284 on main.

The D&D runs have no antelope-kin.

## 2. The spread view

- **The data:** `planet/lineages/techspread.py::derive(run_dir, tech)`, read from `meta.techtree.known`, `settlements.json` and
  `cultures.json`. It takes a few seconds and is served by `GET /api/techspread?run=&tech=`, which caches the doc in memory and writes
  nothing.
- **The view:** `viewer/techtab.js`, the Spread view.
- **Tests:** `tests/test_techspread.py` (a hand-made run) and `tests/test_techtab_spread_js.py` (node, in the style of
  `test_religiontab_js.py`). The node test checks that a second draw waits for the same fetch, that dates go through NumFmt, and that
  a server error shows its text.
- **The measure:**
  - Settled people are everyone in the ledger's villages, towns and cities (`chief` and `minority` places, not mines). This is the
    like-for-like measure for "state-level or settled societies": foragers have no places and are not counted.
  - The town curve counts cells with a town (the ledger's own size for the time and the holder).
  - "Big" means 1% or more of the settled people at the present (`BIG_SHARE`, a judgement).
- **The globe:** this was already the Map view (the globe's 'technology' layer: first-known per people's land at every stored frame),
  so the Spread view links to it rather than adding another map.

## 3. How fast writing spreads in the model

Each run is counted twice: once as stored, and once with today's tech tree. The runs were made before lane 182 keyed the tech tree's
draws, so `techtree.rebuild` in memory gives a second, independent draw over the same history.

| run | first writing | to half the settled people | to nine in ten | last big people | median wait at the border (taker ready and in touch → took it) |
|---|---|---|---|---|---|
| a2b637 stored | 1,410 ago (kobolds) | 910 years | never: 76% now | goliaths, 1,320 years; dwarves (24%) never | 660 years (100–1,320) |
| a2b637 today | 3,120 ago (leonin) | 920 years | 2,320 years | halflings, 2,230 years | 860 years (170–1,910) |
| 0141d1 stored | 3,600 ago (humans) | 800 years | 2,600 years | bugbears, 3,060 years; goliaths (2%) never | 900 years (250–2,360) |
| 0141d1 today | 4,620 ago (hobgoblins) | 1,230 years | 1,530 years | kenku, 1,730 years | 720 years (370–2,580) |
| 07c755 stored | 6,390 ago (elves) | 1,290 years | 2,090 years | humans, 2,090 years | 830 years (200–1,540) |
| 07c755 today | 4,620 ago (deep folk) | 830 years | 930 years | bugbears, 1,160 years | 620 years (310–1,030) |

Two numbers hold across all six draws:
- **Half the settled people know writing 800 to 1,300 years after the first.**
- **A people that is ready and touches a writer takes it after a median 600 to 900 years.**

The tail varies more: nine in ten after 900 to 2,600 years, or never within the run.

**Before the first invention.** The first invention comes 1,300 to 4,500 years after the first people was ready (it knew tokens,
towns and proto-writing). By then 26 to 42 peoples are ready. Earth's own wait, the anchor the rate is set by, was 3,300 years
(proto-writing about 8,600 years ago, writing 5,300; techtree.toml; the 8,600 date there is marked unverified).

## 4. How fast writing spread on Earth

Dates from the sources below. Where a source gives a range, the time after Uruk is from about 3300 BCE.

| society | writing from | how | about how long after Uruk | source |
|---|---|---|---|---|
| Uruk (proto-cuneiform) | c. 3350–3000 BCE | invented | 0 | Kelley, Cartolano & Ferrara 2025, ANE Today, https://anetoday.org/writing-southwest-asia/ ("first documented c. 3350-3000 BCE") |
| Egypt (Abydos U-j) | glyphs 3400–3200 BCE; tomb c. 3100 BCE | disputed: independent or stimulus | ~0–200 years | The Past, on Dreyer's DAIK excavation, https://the-past.com/shorts/the-picture-desk/the-discovery-of-tomb-u-j ; Wikipedia, History of writing, https://en.wikipedia.org/wiki/History_of_writing |
| Susa (proto-Elamite) | c. 3050–2900 BCE | shares a root with, or loans from, proto-cuneiform | ~200–300 years | Wikipedia, Proto-Elamite script, https://en.wikipedia.org/wiki/Proto-Elamite_script |
| Indus | mature c. 2600–1900 BCE | the idea possibly diffused; the script unrelated | ~700 years | Wikipedia, Indus script, https://en.wikipedia.org/wiki/Indus_script ; Robinson (below): "Indus ~2500" |
| Ebla (Syria) | tablets c. 2500–2250 BCE | borrowed Sumerian cuneiform | ~800 years | Wikipedia, Ebla tablets, https://en.wikipedia.org/wiki/Ebla_tablets |
| Anatolia (Kanesh) | 20th–18th c. BCE | borrowed, by Old Assyrian merchants | ~1,350 years | Wikipedia, Kültepe, https://en.wikipedia.org/wiki/K%C3%BCltepe ("the oldest written documents from Anatolia") |
| Hittites | 17th c. BCE on | borrowed Babylonian cuneiform, likely with captured scribes | ~1,650 years | Wikipedia, Hittite cuneiform, https://en.wikipedia.org/wiki/Hittite_cuneiform |
| Crete | hieroglyphs c. 2100–1700, Linear A c. 1800–1450 BCE | origin not stated | ~1,200–1,500 years | Wikipedia, Bronze Age writing, https://en.wikipedia.org/wiki/Bronze_Age_writing ; Robinson: "Crete: around 1900 BC" |
| Mycenae (Linear B) | c. 1450–1350 BCE | adapted from Linear A | ~1,900 years | Dartmouth, Aegean prehistory, https://sites.dartmouth.edu/aegean-prehistory/?p=659 |
| China (Anyang) | c. 1250 BCE | independent (Bagley), or the idea borrowed (Bottéro) | ~2,050 years | Wikipedia, History of writing; Robinson |
| Mesoamerica | c. 900–600 BCE | independent | — | Wikipedia, Mesoamerican writing systems, https://en.wikipedia.org/wiki/Mesoamerican_writing_systems |
| Aksum (Ge'ez) | royal inscriptions c. 200–230 CE | from South Arabian script | ~3,500 years | Wikipedia, Ge'ez script, https://en.wikipedia.org/wiki/Ge%CA%BDez_script |
| Japan | literacy 4th–5th c. CE | borrowed from China | ~3,600 years | Wikipedia, Japanese writing system, https://en.wikipedia.org/wiki/Japanese_writing_system |
| Ghana (Sahel) | Muslim scribes by 1067/68 CE (al-Bakri) | borrowed Arabic, with Islam | ~4,350 years | Wikipedia, Ghana Empire, https://en.wikipedia.org/wiki/Ghana_Empire |
| Inca | never (khipu records) | — | never | Wikipedia, Inca Empire, https://en.wikipedia.org/wiki/Inca_Empire |
| Great Zimbabwe | none, per de Barros in 1538 | — | never | Wikipedia, Great Zimbabwe, https://en.wikipedia.org/wiki/Great_Zimbabwe |

The overview is A. Robinson's review of S. Houston (ed.), *The First Writing*, Times Higher Education, 24 Feb 2006,
https://timeshighereducation.com/node/83581: Mesopotamia ~3300, Egypt ~3100, Indus ~2500, Crete ~1900, China ~1200 and Mesoamerica ~600
BCE. Writing came after a polity's scale grew, not with it: in the Seshat data, information-processing measures (writing, texts,
money) rise between the scale threshold and the information threshold (Shin et al. 2020, *Nature Communications* 11, "Scale and
information-processing thresholds in Holocene social evolution", https://pmc.ncbi.nlm.nih.gov/articles/PMC7224170/).

**Like for like.** No source I found gives a share of the world's states, or of its settled people, that wrote, century by century.
That is the measure the model reports. My reading is an inference: in 2500 BCE most of the world's city-dwellers lived in Mesopotamia,
Egypt and the Indus. If so, writing reached most urban people within roughly 800 years of Uruk. It then took 1,400 to 2,000 years to
reach the Bronze-Age states at the edge, and more than 3,000 to reach most of the Old World's states. Several large states never had
it. Many of the dates above rest on Wikipedia. Scholarly sources are cited where they were reached.

**Verdict.** The model's half-way time (800 to 1,300 years) is like Earth's. Its tail is faster than Earth's: nine in ten in 900 to
2,600 years, where Earth took over 3,000. So writing is not far too slow in the model. If anything, the model lacks Earth's states
that never wrote.

## 5. Why big peoples wait: the diagnosis

The suspects were the contact rules, the needs, the rate per contact and peoples not touching. Each one in turn:

- **Peoples not touching: no.** Every big people bordered writers. Most bordered a dozen or more, along borders of thousands of km.
- **The needs (tokens, towns, proto-writing): no, for diffusion.** Every taker was ready before the first writing anywhere (section 3).
  The needs gate the *invention*, not the spread.
- **The rate per contact: yes, this is the tail.**
  - `techtree.contact_rate` is a front crossing the taker's country at 1 km a year (Pinhasi et al. 2005's Neolithic wave). The rate
    is 2 ln 2 × v / √(its range).
  - For a 40–74 Mkm2 people (the humans of all three runs) that is 0.16–0.22 per kyr per neighbour. Insularity cuts it further: the
    dwarves of a2b637 (0.75) take at 0.48 of it.
  - Many neighbours make the first arrival come sooner, so the median wait is 600 to 900 years. But a people flips all at once when
    the front reaches its middle. Its towns by a writing border wait for its far countryside.
  - Examples: on 07c755 the humans (36% of the settled people) waited 2,100 years after their first writing neighbour. On a2b637 the
    dwarves have waited 1,300 years and still do not write.
- **The invention, not the spread, is what emptied a2b637.** As stored, the first writing came 4,500 years after the first people
  was ready, with 27 peoples ready. With today's draws it comes 1,850 years after. That is chance on the ramped hazard
  (`h (1 - e^(-h τ))`), not a rule failing.

## 6. Candidates

1. **Keep it** (draft option A). The spread is Earth-like.
2. **Writing crosses the town network** (option B, a mechanism).
   - What: for a tech that needs towns, the front's width is the taker's town footprint, not its whole range. Scribes and merchants
     carried writing between towns: Kanesh learned it from Assyrian merchants, the Hittites probably from captured scribes.
   - What it does: big urban peoples take writing in centuries.
   - Cost: it changes how fast techs spread, so it needs Daniel's say, and new peoples runs.
3. **Trade speed** (option C). The same front, at the 1.2–3.3 km a year that Jordan et al. 2016 measured along favoured corridors.
   This is a dial turn.
4. **Records pull writing in** (the "impetus" reading of PW-1448). A state's need for records raises its people's writing hazard. This
   matches Seshat's ordering, scale first and writing after. It needs states inside the history, so it is lane 183's polities v1, not
   a tech-tree change here.

No fix is built. The model is not slower than Earth, and the only clean speed-up (B) changes the tech tree's spread odds, which is
Daniel's call. The draft is `issue-tracking/inbox/draft-writing-crosses-town-network.md`.

## Reproduce

These are scratch scripts, deleted at the end of the lane:
- The gate numbers: `polities.derive(run, invasions=authored)` on main's `polities.py` and on this lane's.
- The spread: `techspread.derive(run, "writing")`, and with `tt=techtree.rebuild(run)` for today's draws.
- The border waits: `min(ready, in touch) - took it` per contact taker, from the same doc.
