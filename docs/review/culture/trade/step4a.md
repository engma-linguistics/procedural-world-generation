# Trade step 4a: craft and luxury goods, a port call's cost, trading towns on the long-haul network (PW-1522, PW-1529, PW-1530; lane 224)

Step 3d: [step3d.md](step3d.md). Code: `planet/lineages/trade.py` (`GOODS`, `MADE`, `SWORDS`; ledger version 3), `planet/lineages/land.py`
(the new `silver` land good), `planet/lineages/trade_flow.py` (`HANDLE`, `DAY_KM`, `LOAD_DAYS`, `UNLOAD_DAYS`, `HARBOUR_DUE`; doc
version 7), `planet/lineages/trade_routes.py` (`GROUPS` gains "craft"; `_hubs`: `trading`), viewer `viewer/globe/trade.js` and the Culinary
brief's trading-towns table. Tests: `tests/test_trade_routes.py` (three new, three adapted). Judge: [step4a/judge.py](step4a/judge.py)
(step 3d's, plus trading towns per era, each good's reach and exporters; `NOCOST=1` skips the cost nudges, as here). Screenshot:
[3e0eb4 at the present, the land-heavy face (45° N 47° E)](step4a_routes_3e0eb4.png).

**Baseline everywhere: main 4667a641** (lane 222), judged with the same script (`--base`: its trade.py, trade_flow.py and
trade_routes.py). Runs 0141d1, 3e0eb4 (D&D) and 07c755 (Seven Meals), L7, 26 frames from 12.5 kyr ago, one judge at a time, land nudge
only (the cost nudges were skipped to keep the machine cool). "No handling" is this lane's code with `HANDLE = False`, on 3e0eb4 only.

## In plain words

- **Nine new goods (PW-1522).** Six are made in towns by specialists: **silk**, **fine cloth** (wool, linen, cotton), **purple and
  indigo dyes**, **glass**, **porcelain**, **weapons and armour**. Three come from the land: **silver** (now its own ore, apart from
  gold), **frankincense and myrrh**, **horses**. Each has a sourced range (section 1): silk, dyes, silver, incense and arms fall off as
  precious goods (they crossed continents), cloth, glass, porcelain and horses as middling ones (they went far mostly by sea, or walked).
  - A made good is made where its know-how is known, by a town's people (the settlement ledger's town share), from inputs on the town's
    cell or anywhere on its culture's land: mulberry farmland for silk, farmland or pasture for cloth, shellfish shores (purple) or
    farmland (indigo) for dyes, fuel for glass and porcelain kilns, iron or copper ore for arms. A town that makes it meets its own want;
    other towns want it. A dwarf or gnome hold wants as a town does (as before) but makes only arms.
  - Still a read-out after the run: nothing feeds back into the history.
- **What travels how far** (people-weighted km of each good's flows between cultures, median; 0141d1 / 3e0eb4 / 07c755):
  silk 810 / 320 / 530 km; dyes 1,300 / 260 / 480; cloth 7,700 / 220 / 6,500; glass 260 / 3,000 / 15; porcelain 0 / none / 15 (nobody on 3e0eb4 knows it); arms 110 / 24 / 0; silver
  920 / 1,200 / 2,800; incense 2,000 / 1,700 / 2,200; horses 5,200 / 4,900 / 6,200. The far tails (the top tenth of each good's flows)
  run 3,500-15,000 km, mostly by sea. Spices, for comparison, 11,800 / 11,600 / 8,100. So the made goods mostly travel hundreds to a few
  thousand km, with a long sea tail, as the literature's silk, glass and porcelain did; arms mostly stay near their smithies, as a good
  wanted where it is made should (the far Ulfberht finds were contraband).
- **Who exports them.** Each made good has 30-70 exporting cultures a run, led by its makers' towns: on 3e0eb4 the dwarves and gnomes
  of the west of Simath (silk, cloth, dyes, glass, arms), on 07c755 the antelope-kin of the south of Thotal and the humans of the east
  of Loshom, on 0141d1 the halflings of the south-east of Razukum and the humans of the south-east of Zibrojur. Incense comes from the
  brass dragons' realms (their kobolds trade it) and the hot-scrub humans; silver from elves, hill giants, half-orcs and hobgoblins on
  ore. Directions follow the know-how, not a rule (section 4 has the tables).
- **The long-haul network grows by a fifth to a quarter** with the new goods: 1,840 / 1,810 / 2,310 stretches an era on average (main
  1,520 / 1,530 / 1,810), 3,600-5,000 at the present. A new colour, "cloth, glass, wares, horses" (craft), carries 1,050-1,640 of the
  present's stretches. Still tree-shaped: 27-36 pieces, ~100-120 junctions, 13-24 loops an era.
- **A port call's cost (PW-1529) is sourced and in, but changes almost nothing.** Loading costs 2 ship-days, unloading 4 (Page 2026,
  from P.Lond. 3.948), at ORBIS's ~100 sea-km per ship-day, plus a 2.5% harbour due on what comes ashore (the Roman portorium). That is
  ~600 sea-km of carrying per call plus the due, against fall-off lengths that let a precious good sail ~12,000-40,000 km. On 3e0eb4
  the long-haul stretches go from 1,808 an era (no handling) to 1,805 (with), spices' median haul from 11,490 to 11,550 km, gold's
  from 2,700 to 2,500. The per-km sea cost and the fall-off length set the reach, not the port. Draft below.
- **Trading towns (PW-1530, ruling A): a long-haul route through the town.** Merchant quarters only in trading towns. Other route towns
  are market towns, drawn as small white rings. At the present: **0141d1 628 → 216 trading towns (+651 market towns); 3e0eb4 805 → 303
  (+752); 07c755 650 → 252 (+729)**. Merchant quarters fall by half to two thirds (462 → 144, 589 → 214, 753 → 267). Per era in
  section 3.
- **Steadiness holds** (land nudge, Jaccard of route stretches, mean over every third frame, min in brackets):
  all routes **0.80 (0.71) / 0.78 (0.72) / 0.75 (0.55)** (main 0.79 (0.68) / 0.80 (0.70) / 0.75 (0.54)); long-haul 0.83 / 0.83 / 0.75
  (main 0.83 / 0.85 / 0.75); local 0.68 / 0.65 / 0.69 (main 0.68 / 0.66 / 0.71). The bar (about 0.7 or above) is met on all three.
  Trading-town steadiness drops a little (0.76 / 0.68 / 0.76, main 0.80 / 0.77 / 0.82): a town flips between trading and market town
  when a long-haul stretch beside it comes and goes.
- **Time:** the derive takes 126 / 135 / 210 s (main 97 / 101 / 148 s on the same machine, the judges one at a time under other lanes'
  load): ~1.35 times main, for 29 goods instead of 20.

## 1. Literature: which made goods went how far, when, and which way

Every source below was fetched for this lane (11-08). Distances marked "[est.]" are this lane's own great-circle or route estimates
between the named ends; no source gives them.

| good | from → to | how far | when | the other way | source |
|---|---|---|---|---|---|
| **silk** | Han China → Palmyra (Syria) | ~7,000 km overland [est.] | Han, 206 BC-AD 220 | Roman glass, silverware, coins east to China | Żuchowska 2013, Światowit 52: "close to 100" of 500 textiles in Palmyra's tower tombs are silk, a group "definitely Chinese textiles – Han damasks and Jin brocades"; "quite a large scale import from China" ([swiatowitwuw.pl](https://swiatowitwuw.pl/numery/52-tom-52-nr-a/from-china-to-palmyra-the-value-of-silk)) |
| **glass** | Syria → Silla, Korea (Hwangnam-daechong ewer); Roman glass cup in an Eastern Han tomb (Guigang, Guangxi); Roman coins and glass beads in Japan | ~8,000 km and more [est.] | 1st-5th c. AD | silk west | [Sino-Roman relations](https://en.wikipedia.org/wiki/Sino-Roman_relations) ("Roman glassware and silverware have been discovered at Chinese archaeological sites"; Hou Hanshu: Rome sends "sea silk, glass, amber, cinnabar"; Parthians kept the silk trade in their hands); [Hwangnam-daechong glassware](https://en.wikipedia.org/wiki/Hwangnam-daechong_Roman_Glassware) (after Lee and Leidy 2013, the Met: "of Syrian origin", buried ~AD 450) |
| **silver, glass, wine, coral out; pepper, cotton and silk cloth, indigo, gems in** | Egypt and the Red Sea ↔ Barbaricum, Barygaza, Muziris (India) | ~4,500-5,000 km by Nile, desert and sea [est.] | ~130 BC-AD 640; 120 ships a year from Myos Hormos under Augustus (Strabo) | the two lists are the two directions | [Indo-Roman trade relations](https://en.wikipedia.org/wiki/Indo-Roman_trade_relations) (the Periplus' lists; Yavana ships "came with gold and returned with pepper"; Pliny: India, China and Arabia take 100 million sesterces a year). The Red Sea's 25% *tetarte* on Indian imports, and the Muziris papyrus' Hermapollon cargo, ~9 million sesterces before the tax: [OpenEdition, "The Roman state and Red Sea trade revenue"](https://books.openedition.org/momeditions/16401?lang=en) |
| **purple dye and purple cloth** | Tyre (Phoenicia); Cyprus a major exporter of purple textiles | across the Mediterranean, Tyre to Italy ~2,300 km by sea [est.] | from ~1200 BC to Byzantium | — | [Tyrian purple](https://en.wikipedia.org/wiki/Tyrian_purple): Theopompus, "purple for dyes fetched its weight in silver at Colophon"; 12,000 murex give 1.4 g of dye (Jacoby 2004) |
| **frankincense and myrrh** | Dhofar and Hadhramaut → Petra → Gaza (and by the Gulf to Babylon and Palmyra) | ~2,400-3,000 km [est.; the fetched page gives none] | 3rd c. BC-2nd c. AD (UNESCO) | — | [Incense trade route](https://en.wikipedia.org/wiki/Incense_trade_route) (Khor Rori → Qana → Shabwa → Najran → Petra → Gaza) |
| **swords and mail** | Rhineland (Ulfberht blades) → Norway, Sweden, Finland, the Baltic; three in Volga Bulgaria | ~1,200 km to Norway, ~3,000 km to the Volga [est.] | 9th-11th c. | — | [Ulfberht swords](https://en.wikipedia.org/wiki/Ulfberht_swords): ~170 known, 44 in Norway; went north "as loot, ransom, or contraband" because the capitularies forbade selling arms to foreigners |
| **(arms bans)** | Frankish lands → Slavs and Avars; → Vikings | — | 805; 864 | — | Capitulary of Thionville, 805: merchants to the Slavs and Avars "are not to take arms and coats of mail to sell", on pain of losing their whole stock ([jassa.org, King's translation](https://www.jassa.org/?p=7319)); Edict of Pîtres, 864: all trade in weapons with the Vikings forbidden, and selling them horses punished by death ([Edict of Pîtres](https://en.wikipedia.org/wiki/Edict_of_P%C3%AEtres), after Gillmor 1988) |
| **porcelain and stoneware** | southern China → the Swahili coast (Changsha wares at Shanga), by way of Southeast Asia, the Gulf (Siraf) and the Red Sea | ~10,000 km by sea [est.] | 9th-15th c. | — | Zhao 2015, Afriques 06 ([openedition](https://journals.openedition.org/afriques/1836?lang=en)): imports "primarily occurred indirectly"; no direct China-Swahili route |
| **horses** | Tibet → Sichuan and Yunnan (tea the other way) | the Sichuan-Tibet section alone "more than a thousand kilometres" | Tang to the Republic | tea west | [Tea Horse Road](https://en.wikipedia.org/wiki/Tea_Horse_Road) |
| **silver (the ore)** | — | — | silver from galena by the 7th c. BC; Laurion ~30 t a year 600-300 BC; Rome's silver mostly from Spain | — | [Silver](https://en.wikipedia.org/wiki/Silver): "Most silver is recovered as a byproduct of lead–zinc, copper and gold mining" (after USGS MCS 2026) |
| **(a craft town's workforce)** | Florence's wool guild, 1338 | — | — | — | Villani via Harsch 2019, MEFRM 131-2 ([openedition](https://journals.openedition.org/mefrm/5545)): wool fed 30,000 of 90,000-120,000 people; Najemy reads ~10,000 wage workers, ~1/6 of working-age adults |

Could not be sourced in this lane (left out of the model's reasoning): Sasanian silver going east; Gujarati cotton at Fustat; the Song
tea and horse agency's rates; Central Asian horses to India; Sidon as a purple town; medieval harbour dues.

**What the model takes from it.**
- The goods that crossed whole continents are light and dear for their weight: silk, purple, silver, incense and arms (swords went
  1,200-3,000 km as contraband). They fall off as **precious** goods (1,200 pack-km), as spices and gold already do.
- Glass, cotton and wool cloth and porcelain also went thousands of km, but by sea and as **middling** cargo: porcelain by the shipload,
  glass and cloth among wine and coral in the Periplus' lists. They fall off as middling goods (433 pack-km), which by ship is still
  ~12,000 km before the 1% cut.
- Horses walk themselves to the market, 1,000 km and more: **middling**.
- Directions come from where the know-how is, not from a rule: silk goes from wherever silk is known to towns that lack it, and glass the
  other way only if the glass-makers are elsewhere.
- The arms bans are not modelled as a rule of their own: a war between two polities already closes their border to all goods
  (trade_flow._polity_state), which is what the capitularies did for arms against the Avars and Vikings. An arms-only ban between
  wary neighbours at peace is a follow-up, not a draft (nothing reads wrong without it).
- Craft output: a town's people make what it knows to make, as a share of its people (the town share), the inputs from its own culture's
  land. Florence had a quarter to a third of its people living off one export craft, so a craft town supplying as many wanting heads as
  it has making heads is within the sourced range; it is the module's existing "like with like" judgement, not a sourced yield.

## 2. A port call's cost (PW-1529)

**Sources (fetched).** ORBIS v1 (Scheidel, Meeks & Weiland 2012, [paper](https://orbis.stanford.edu/orbis2012/ORBIS_v1paper_20120501.pdf))
prices sea carriage from Diocletian's edict at 0.1 denarii per kg of wheat per day under sail, and the model already uses its ~0.001 per
km; it has **no transshipment or harbour cost**. Page 2026 ("Lost in Transit: Reconstructing Transhipment Costs from the Roman Era",
J. Maritime Archaeology 21, [Springer](https://link.springer.com/article/10.1007/s11457-026-09495-5)): the edict "does not include
transhipment fees"; from P.Lond. 3.948, 9.5 t took **2 days to load and 4 to unload**; from P.Oxy. 3.522, harbour operations were
**5-10%** of a voyage's total cost (more on short trips: 51.5% in P.Oxy. 14.1650); the porters' own wages under 1%. The Roman
portorium: a **2.5%** duty on value (the quadragesima; 2% earlier) at a customs boundary ([ostia-antica.org after De Laet
1949](https://www.ostia-antica.org/dict/topics/portorium/presentation/introduction.htm)). The Red Sea's 25% *tetarte* was an imperial
frontier tax; the model's border toll stands for that kind.

**What the model takes.** A ship's day is ~100 sea-km (ORBIS: per day / per km). Where goods leave the land for the sea (a land cell
to a sea cell, by ship) they pay 2 ship-days (200 sea-km of carrying); where they come ashore, 4 ship-days (400 sea-km) and the 2.5%
due, as a share of value like the toll (-L ln(1 - 0.025)). `HANDLE = False` turns it off. 600 sea-km per call is 5-10% of a
6,000-12,000 km voyage's cost, Page's range; a short hop pays a bigger share, as the papyri say.

**What it does (3e0eb4, long-haul stretches per era):**

| kyr ago | main | this lane, no handling | this lane |
|---|---|---|---|
| 8 | 786 | 815 | 787 |
| 6 | 1,504 | 1,689 | 1,672 |
| 4 | 2,056 | 2,599 | 2,549 |
| 2 | 2,983 | 3,666 | 3,649 |
| 0 | 2,883 | 3,973 | 3,851 |
| mean | 1,532 | 1,808 | 1,805 |
| land-nudge steadiness, all / long-haul | 0.80 / 0.85 | 0.80 / 0.85 | 0.78 / 0.83 |

Spices' median haul 11,490 km without, 11,550 km with; gold 2,700 → 2,500 km; grain 738 → 732 km; sea's share of the long-haul
stretches 0.73 → 0.72. **The sourced handling cost is too small to thin the network.** In cost-km a port call is ~21 pack-km plus the
due (~30 for a precious good, ~7 for a bulk one); a precious good's whole budget before the 1% cut is 1,200 x ln 100 ≈ 5,500 pack-km,
which by ship is ~150,000 km. What lets fine goods sail anywhere is ORBIS's cheap sea mile against a fall-off length set from overland
hauls (Kanesh's donkeys). A heavier handling cost would have to be made up; the draft below asks which lever, if any, to pull instead.

## 3. Trading towns per era (PW-1530)

Main: every settlement-ledger town a route of either layer passes is a trading town (in brackets: those on the long-haul network).
This lane: trading towns (a long-haul route through them) + market towns (the local web only); and merchant quarters, main → now.

| kyr ago | 0141d1 main | 0141d1 now | 3e0eb4 main | 3e0eb4 now | 07c755 main | 07c755 now | quarters main → now (0141d1 / 3e0eb4 / 07c755) |
|---|---|---|---|---|---|---|---|
| 8.0 | 0 (0) | 0 + 0 | 51 (23) | 39 + 61 | 47 (27) | 28 + 20 | 0 → 0 / 64 → 45 / 57 → 29 |
| 7.5 | 0 (0) | 0 + 0 | 58 (19) | 37 + 77 | 181 (75) | 77 + 102 | 0 → 0 / 60 → 41 / 214 → 98 |
| 7.0 | 0 (0) | 0 + 0 | 162 (50) | 77 + 185 | 263 (99) | 118 + 185 | 0 → 0 / 161 → 88 / 307 → 132 |
| 6.5 | 88 (61) | 72 + 20 | 257 (86) | 104 + 253 | 309 (124) | 177 + 201 | 69 → 50 / 232 → 103 / 314 → 161 |
| 6.0 | 122 (81) | 98 + 35 | 227 (102) | 154 + 199 | 423 (183) | 251 + 283 | 108 → 58 / 201 → 147 / 502 → 266 |
| 5.5 | 274 (113) | 177 + 156 | 383 (145) | 198 + 293 | 442 (175) | 299 + 351 | 272 → 148 / 332 → 176 / 509 → 345 |
| 5.0 | 301 (120) | 213 + 164 | 405 (160) | 240 + 299 | 471 (168) | 259 + 374 | 268 → 192 / 349 → 203 / 570 → 328 |
| 4.5 | 381 (146) | 212 + 294 | 536 (199) | 240 + 389 | 555 (229) | 347 + 366 | 421 → 205 / 488 → 218 / 692 → 426 |
| 4.0 | 481 (179) | 254 + 323 | 579 (238) | 325 + 417 | 547 (189) | 235 + 456 | 448 → 214 / 495 → 307 / 550 → 209 |
| 3.5 | 525 (168) | 221 + 404 | 635 (195) | 299 + 554 | 638 (225) | 276 + 539 | 481 → 179 / 549 → 310 / 654 → 244 |
| 3.0 | 512 (186) | 276 + 424 | 693 (235) | 308 + 584 | 545 (201) | 278 + 490 | 455 → 217 / 603 → 337 / 545 → 219 |
| 2.5 | 531 (205) | 303 + 411 | 613 (193) | 289 + 556 | 598 (228) | 311 + 594 | 474 → 262 / 526 → 301 / 584 → 259 |
| 2.0 | 609 (229) | 308 + 497 | 740 (256) | 397 + 626 | 637 (198) | 253 + 671 | 516 → 272 / 666 → 378 / 664 → 222 |
| 1.5 | 631 (202) | 287 + 593 | 739 (248) | 387 + 589 | 561 (160) | 234 + 620 | 518 → 251 / 628 → 378 / 668 → 243 |
| 1.0 | 682 (210) | 343 + 618 | 775 (259) | 389 + 651 | 568 (174) | 215 + 697 | 543 → 304 / 576 → 343 / 678 → 226 |
| 0.5 | 669 (156) | 236 + 654 | 793 (238) | 383 + 724 | 620 (214) | 276 + 679 | 554 → 192 / 614 → 301 / 719 → 297 |
| 0.0 | 628 (152) | 216 + 651 | 805 (212) | 303 + 752 | 650 (188) | 252 + 729 | 462 → 144 / 589 → 214 / 753 → 267 |

## 4. Each good's reach and exporters (this lane's code)

Per good and run (0141d1 / 3e0eb4 / 07c755): the people-weighted median and 90th-percentile km of its flows between cultures (tribute
left out), the share of its volume carried 500 km or more, the share by sea, the share of its world-wide lack left unmet (26 eras), and
the two biggest exporters per run with their share of its exports. Spices, gold and grain for comparison.

| good | class | median km (p90) | 500 km+ | by sea | unmet | top exporters |
|---|---|---|---|---|---|---|
| silk | precious | 812 (p90 9,206) / 319 (p90 3,696) / 534 (p90 8,729) | 0.554 / 0.386 / 0.501 | 0.47 / 0.2 / 0.44 | 0.575 / 0.556 / 0.227 | first halflings of the south-east of Razukum 15%, first hobgoblins of the south of Talatos 10%; first dwarves of the west of Simath 17%, first gnomes of the west of Simath 13%; first antelope-kin of the south of Thotal 36%, first humans of the east of Loshom 14% |
| dyes | precious | 1,295 (p90 15,092) / 260 (p90 3,549) / 479 (p90 9,542) | 0.678 / 0.407 / 0.497 | 0.56 / 0.18 / 0.46 | 0.553 / 0.653 / 0.206 | first halflings of the south-east of Razukum 18%, first dragonborn of Luki 9%; first dwarves of the west of Simath 15%, first gnomes of the west of Simath 11%; first antelope-kin of the south of Thotal 36%, first humans of the east of Loshom 12% |
| cloth | middling | 7,737 (p90 11,896) / 216 (p90 5,019) / 6,518 (p90 12,940) | 0.804 / 0.348 / 0.726 | 0.81 / 0.26 / 0.67 | 0.493 / 0.506 / 0.14 | humans of the south-east of Zibrojur 36%, first halflings of the south-east of Razukum 14%; first gnomes of the west of Simath 15%, humans of the east of Trojanel 14%; first humans of the east of Loshom 16%, first antelope-kin of the south of Thotal 11% |
| glass | middling | 258 (p90 5,723) / 2,984 (p90 6,750) / 15 (p90 1,735) | 0.46 / 0.784 / 0.228 | 0.28 / 0.62 / 0.11 | 0.718 / 0.645 / 0.568 | first elves of the north-east of Thotal 27%, humans of the south-east of Zibrojur 11%; first gnomes of the west of Simath 32%, continental gnomes of the west of Simath 30%; first humans of the east of Loshom 24%, first antelope-kin of the south of Thotal 11% |
| porcelain | middling | 0 (p90 4,849) / - / 15 (p90 1,724) | 0.258 / - / 0.206 | 0.24 / - / 0.13 | 0.725 / - / 0.506 | first elves of the north-east of Thotal 19%, humans of the south-west of Talatos 14%; -; first humans of the east of Loshom 34%, half-orcs of the south of Talatos 8% |
| arms | precious | 106 (p90 7,527) / 24 (p90 546) / 0 (p90 88) | 0.274 / 0.157 / 0.027 | 0.28 / 0.03 / 0.02 | 0.424 / 0.489 / 0.668 | first dwarves of the south of Kheko 28%, gnomes of the south-west of Munin 27%; first dwarves of the west of Simath 25%, first gnomes of the west of Simath 16%; first gnomes of Talatos 38%, half-orcs of the west of Luki 8% |
| silver | precious | 920 (p90 2,842) / 1,215 (p90 4,084) / 2,772 (p90 10,006) | 0.724 / 0.837 / 0.864 | 0.29 / 0.36 / 0.67 | 0.581 / 0.735 / 0.404 | first elves of the north-east of Thotal 15%, first hill giants of the east of Luki 15%; first elves of the south of Simath 15%, humans of the east of Trojanel 12%; first half-orcs of the north-east of Ratote 21%, first hobgoblins of the north of Razukum 16% |
| incense | precious | 2,026 (p90 4,815) / 1,712 (p90 5,566) / 2,246 (p90 5,769) | 0.954 / 0.939 / 0.93 | 0.75 / 0.39 / 0.72 | 0.109 / 0.726 / 0.019 | first brass dragons of the south of Munin 28%, first copper dragons of the south of Thotal 22%; first brass dragons of the south of Simath 41%, humans of the east of Trojanel 8%; first brass dragons of the south-east of Munin 53%, half-orcs of the south of Talatos (2) 9% |
| horses | middling | 5,213 (p90 11,215) / 4,922 (p90 12,907) / 6,210 (p90 17,043) | 0.943 / 0.955 / 0.905 | 0.89 / 0.67 / 0.81 | 0.485 / 0.667 / 0.26 | humans of Munin 20%, humans of the south of Brakothom 9%; savanna halflings of the east of Trojanel 24%, first halflings of the east of Trojanel 17%; first humans of the east of Loshom 24%, half-orcs of the west of Luki 18% |
| spices | precious | 11,757 (p90 19,729) / 11,551 (p90 17,630) / 8,094 (p90 18,736) | 0.995 / 0.999 / 0.989 | 0.9 / 0.92 / 0.91 | 0.604 / 0.689 / 0.129 | humans of the south-east of Talatos 19%, first humans of the west of Shakhitrem 14%; first halflings of the east of Trojanel 30%, humans of the east of Trojanel 21%; first humans of the east of Loshom 40%, half-orcs of the south of Talatos (2) 12% |
| gold | precious | 1,012 (p90 5,095) / 2,503 (p90 8,603) / 1,458 (p90 5,900) | 0.621 / 0.88 / 0.83 | 0.41 / 0.53 / 0.46 | 0.558 / 0.437 / 0.179 | first hill giants of the east of Luki 14%, first elves of the north-east of Thotal 10%; first hill giants of Ratal 20%, humans of the east of Trojanel 13%; first humans of the east of Loshom 12%, first lizardfolk of the north of Munin 12% |
| grain | bulk | 1,014 (p90 4,489) / 732 (p90 3,682) / 1,154 (p90 4,377) | 0.748 / 0.765 / 0.833 | 0.44 / 0.24 / 0.61 | 0.535 / 0.486 / 0.349 | first humans of the west of Shakhitrem 10%, first halflings of the south-east of Razukum 9%; humans of the east of Trojanel 21%, first halflings of the east of Trojanel 19%; first hobgoblins of the north of Razukum 15%, first humans of the east of Loshom 12% |

## 5. What changed in the code

- `land.py`: a `silver` land good from the lead-zinc, sulphide (VMS) and epithermal gold-silver ore layers (`_ORES`; "most silver is
  recovered as a byproduct of lead–zinc, copper and gold mining", section 1). The goods cache is keyed on land.py's source, so every
  world's goods are remade once.
- `trade.py` (ledger version 3): nine goods in `GOODS` with their classes; `GATE` and `NEED_GATE` for them (`SWORDS`: bronze, iron and
  steel swords, scale, mail, segmented and plate armour); `MADE` goods in `ledger_at`: surplus = the town share x the input (the cell's,
  or its culture's mean, the larger) x the know gate (dyes: indigo on farmland or purple on shellfish shores, each with its own tech);
  lack = the town's want x (1 - what it can make), and no town wants a made good before some living culture can make it. A mining kind's hold wants as a town does but makes only arms. Incense from hot
  steppe (Köppen BSh) or hot desert hills (BWh, hills ≥ 0.3).
- `trade_flow.py` (doc version 7): `HANDLE`, `DAY_KM`, `LOAD_DAYS`, `UNLOAD_DAYS`, `HARBOUR_DUE` in `_Frame.cost` (on sea edges from a
  land cell, and into one); the doc's constants list them.
- `trade_routes.py`: `GROUPS` gains "craft" (cloth, glass, porcelain, horses); silk, dyes, arms, silver and incense are "precious".
  `_hubs`: a hub is `trading` when the long-haul layer passes it; otherwise its kind is "market town" and it hosts no merchant quarter
  (so no toll is lifted there next era).
- Viewer: a "cloth, glass, wares, horses" colour; market towns as small faint rings; the status line counts trading and market towns;
  the hover card says "market town ... on the local web"; the Culinary brief's trading-towns table marks each town "long-haul" or
  "local".

## 6. Status

- PW-1522: **built.** Nine goods with sourced ranges, made in towns by their know-how, read out after the run. Arms bans are not a rule
  of their own (a war already closes a border to every good); left as an idea, not a draft.
- PW-1529: **built and measured: no effect worth the name** (1,808 → 1,805 long-haul stretches an era on 3e0eb4). Kept, since it is
  sourced and cheap; the lever that would thin the network is a judgement (draft).
- PW-1530: **built** (ruling A). Trading towns 216 / 303 / 252 at the present (main 628 / 805 / 650), market towns 651 / 752 / 729.
- Bars: land-nudge steadiness 0.80 / 0.78 / 0.75 (≥ 0.7 on all three); every new good has a sourced range (section 1).
- Draft (inbox): the long-haul network's size after a sourced port cost (needs-decision: leave it, a sea fall-off of its own, or a
  display bar).
