# Trade step 4c: river hauls pay the hands too; herds and horses walk (lane 226; the two inbox drafts from lane 225)

Step 4b: [step4b.md](step4b.md). Code: `planet/lineages/trade_flow.py` (`RIVER_HANDS`, `DROVES`, `DROVE_GOODS`, `DROVE`, and `RIVER_COURSE`,
measured and left off; `_Frame.cost`, `_Frame.cost_of`; doc version 9). Tests: `tests/test_trade_routes.py` (three new), the fixture in
`tests/test_trade_flow.py` gains the world's `downstream`. Judge: step 4a's ([step4a/judge.py](step4a/judge.py)), unchanged, `NOCOST=1`
(the land nudge only), one judge at a time on 4 cores.

**Baseline everywhere: main d8152d53** (lane 225 merged), judged in the same hour on the same machine (0141d1 with this lane's flags off,
3e0eb4 and 07c755 with `--base`, main's three trade files). It reproduces step4b.md's "this lane" column to the km. Runs 0141d1, 3e0eb4
(D&D) and 07c755 (Seven Meals), L7, 26 frames from 12.5 kyr ago.

## In plain words

- **Why spices still went too far.** After lane 225 a sea km cost the merchants' hands, but a river km cost only the boat's freight, which is
  an eighth of a donkey's. So the dear goods moved onto the rivers. On 3e0eb4 the farthest tenth of spice deliveries travelled ~16,400 km,
  ~13,900 km of it by river, and crossed ~25 borders. Each border took its toll, but over that many km the freight was close to free.
- **A second finding.** The model let a boat cross between any two neighbouring cells that both have a navigable river. Two thirds of
  those links do not follow a river: they jump between parallel tributaries or over a watershed, which joins whole basins into
  continent-wide meshes. On 3e0eb4 the biggest such mesh has 4,658 cells; following the rivers' own courses, the biggest basin has 1,797.
- **The fix (built): the hands on rivers too.** A river km now costs middling and dear goods the same share of value as a sea km (one
  e-fold every 3,000 km, lane 225's sourced HAND_KM). Both price chains behind that number ran by river as well as by sea: Pliny's goods
  went up the Nile from Juliopolis to Coptos, and Pearson's pepper went down the Nile to Alexandria. Bulk goods (grain, timber, stone)
  keep freight alone, as at sea.
- **Spices now stay within their sourced reach.** Median 6,918 → 5,265 km on 0141d1, 8,160 → 5,082 on 3e0eb4 and 5,187 → 4,449 on 07c755.
  Far tenth 11,288 → 9,540, 14,611 → 8,677 and 9,675 → 7,577, against ~8,000 km for pepper from Malabar to Rome. The share of spice flows
  carried mainly by river falls from 0.50-0.83 to 0.22-0.29.
- **Following the river's course: measured, left off.** Boats that follow only their own river's course (`RIVER_COURSE`) bound spices
  about as well (far tenth 9,691 / 8,513 / 7,425 km). But they cut herders' grain met on all three runs: 0.0302 → 0.0267, 0.1264 →
  0.0957 and 0.1227 → 0.1035. Grain had been crossing between rivers that way. The flaw is real and the trade-off is a choice, so it is
  drafted for a decision, not merged.
- **Herds and horses walk (built).** Livestock and horses now travel as droves on land, at a quarter of a pack animal's cost per km, over
  any ground, and never by river boat. The number comes from the Texas cattle drives: about $1.25 a head over the trail against $4 by
  rail, for herds worth $2-4 a head in Texas. Horses' median falls from 2,814 → 2,308 km, 1,717 → 1,284 and 1,561 → 1,549, and their far
  tenth from 4,702 → 4,281, 4,221 → 4,097 and 4,259 → 4,311. No horse goes by river any more.
- **What is not fixed: herds still ship.** About half of the horse flows still run mainly by sea, and their far tenth is ~4,100-4,300 km.
  The sourced long sea case is ~3,000-3,500 km, the Gulf to Ma'bar. No fetched source gives a horse ship's freight against a cargo
  ship's. A test factor of 3 on 3e0eb4 moved horses' far tenth only from 3,598 to 3,285 km, because the hands, not the freight, set the
  reach at sea. So no factor was added. The draft stays open with what was found.
- **The bars.**
  - Land-nudge steadiness is 0.776 / 0.766 / 0.745 (main 0.782 / 0.788 / 0.750). The worst frame is 0.67 / 0.71 / 0.68 (main 0.67 /
    0.74 / 0.64).
  - Herders' grain met is 0.0302 / 0.1267 / 0.1203 (main 0.0302 / 0.1264 / 0.1227). On 07c755 that is 0.0024 under main, which is a
    slight miss. Section 3 gives the cause: the long-haul network thins, so fewer merchant quarters lift border tolls. Grain unmet over
    all eras is the same as main's (0.349 against 0.348).
  - The derive takes 54 / 47 / 81 s (main 62 / 72 / 109 s).
- **Timber and firewood** (far tenth ~7,000 km on 0141d1) go by sea, where bulk keeps freight alone. Nothing here touches them
  (7,022 / 7,182 km, main 7,099 / 7,141), so they were not chased.

## 1. Diagnosis (3e0eb4, main d8152d53)

People-weighted over every delivery between cultures, all 26 frames. The km are means over the far tenth (deliveries at or beyond the
good's 90th percentile) by mode, with the borders crossed (script: a patched `_Ledger.record`, kept out of the repo).

| good | median / p90 km | far tenth: km (land / river / sea) | borders | flows mainly by river |
|---|---|---|---|---|
| spices | 7,586 / 14,703 | 16,416 (170 / 13,893 / 2,312) | 24.8 | 0.82 |
| horses | 1,017 / 3,989 | 5,227 (105 / 2,517 / 2,605) | 2.6 | 0.56 |
| livestock | 939 / 4,223 | 5,321 (127 / 3,904 / 1,291) | 2.9 | 0.69 |
| gold | 704 / 2,816 | 4,047 (280 / 3,116 / 645) | 5.3 | 0.63 |
| grain | 547 / 2,503 | 6,164 (122 / 883 / 5,159) | 2.7 | 0.64 |

- Rivers do not carry spices unbroken through one culture: ~25 borders over ~14,000 river km is one border every ~560 km. The tolls are
  charged, but at 10% a border and 1/8 of a donkey's freight per km a precious good still reaches ~14,000 km before its supply falls under
  the 1% floor. So the draft's first idea (rivers held by one culture) is not the cause. What is missing on rivers is the hands.
- The river mesh: of 139,552 directed links between neighbouring navigable cells on 3e0eb4, 50,342 follow a `downstream` link; 16,796
  join different basins (0141d1 and 07c755, which share a world: 146,612, 52,518 and 19,676). With `RIVER_COURSE` alone (no river hands),
  spices' far tenth on 3e0eb4 was still 11,966 km, of which ~10,000 km was by river within one basin. That is not enough on its own.

## 2. Sources (fetched for this lane, 11-08)

**River hauls.** The two chains behind HAND_KM (step4b.md section 1) include river legs:
- Pliny NH 6.26: the Nile from Juliopolis to Coptos, 308 miles.
- Pearson's pepper: by the Red Sea, then overland to Cairo and down the Nile [est. route, step4b.md].

The same relays ran on rivers as at sea. On the Rhine "in 1250 ... there were 12 stations on the Rhine between Mainz and Cologne", and
over 800-1800, 79 places took tolls on the Rhine and its tributaries (Gardner, Gaston & Masson, "Tolling the Rhine in 1254", via
[medievalists.net](https://www.medievalists.net/2012/12/tolling-the-rhine-in-1254-complementary-monopoly-revisited/)). That page gives
no toll as a share of value, and neither did any other page found (the part of [Rhine](https://en.wikipedia.org/wiki/Rhine) read has none). So the river
hands take the sea's sourced rate, and Rhine-style river tolls inside one realm are not a separate charge.

**Droves (land).**
- "the cost of sending cattle over the trail [to Kansas] was about $1.25 per head; the cost of railway is about $4.00 a head" (Lytle, in
  Freeman 1905, p. 660), and "freight charges were three times as great as the expense of a drive" (Osgood 1929, p. 91). Both are quoted
  in "End of the Chisholm Trail", J. Econ. Hist. ([Cambridge](https://www.cambridge.org/core/journals/journal-of-economic-history/article/end-of-the-chisholm-trail/D0B890CAC71DDBC1CCE0EBA832DB317B)),
  which puts the drive at "as much as a thousand miles".
- "could not be sold for more than $2 a head in Texas"; "as much as $40 per head" in the northern markets (1866); "Ten or twelve miles was
  considered a good day's drive" ([Cattle drives in the United States](https://en.wikipedia.org/wiki/Cattle_drives_in_the_United_States)).
  The [Chisholm Trail](https://en.wikipedia.org/wiki/Chisholm_Trail) page gives $4 a head in Texas in 1866.
- Welsh flocks "travelled 20 to 25 days from Wales to London yet lost less than four per cent of their body weight"; "30,000 cattle and
  sheep were driven from Wales to London each year" ([Droving](https://en.wikipedia.org/wiki/Droving)).
- So: $1.25 against $2-4 at the start is 31-63% of the value over ~1,600 km, one e-fold per ~1,700-4,300 km. Against the middling
  fall-off (433 pack-km) that is 0.10-0.25 of a pack animal per km. **DROVE = 0.25** (JUDGEMENT: the dear end). At 0.10, horses' far
  tenth went 7,430 km overland on 3e0eb4 (diagnosis run), past the sourced ~1,000-3,000 km.

**Horses by sea.**
- The Treaty of Venice, 1201 (Villehardouin, [Fordham sourcebook](https://sourcebooks.fordham.edu/source/4cde.asp)): "four marks per
  horse and two marks per man", with "food for nine months for all these horses and men". That is fare and fodder together, and the source
  gives no horse value, so no share of value can be drawn from it.
- 13th-century transports carried "a range from 8 to 20 horses", and taride "20 to 30 horses"
  ([Horse transports in the Middle Ages](https://en.wikipedia.org/wiki/Horse_transports_in_the_Middle_Ages)). No ordinary cargo
  tonnage to compare with was found.
- Wassaf, in Yule's notes to Marco Polo ([vol. 2, p. 404](https://dsr.nii.ac.jp/toyobunko/III-2-F-c-30/V-2/page-hr/0404.html.en)):
  "The price of each horse was fixed from of old at 220 dinars of red gold", and "if any horses should happen to die, the value of them
  should be paid from the royal treasury"; "10,000 horses were annually exported". Deaths on the voyage were common enough to contract
  for, but no rate is given.
- Not found: a per-voyage death rate from a fetched page, or a horse ship's freight per head against cargo.

## 3. Results

Main d8152d53 against this lane, and the variant with `RIVER_COURSE` on (built and measured, left off). 0141d1 / 3e0eb4 / 07c755.

| measure | main d8152d53 | this lane | + river course (off) |
|---|---|---|---|
| land nudge, all routes (worst frame) | 0.782 (0.67) / 0.788 (0.738) / 0.750 (0.642) | 0.776 (0.67) / 0.766 (0.711) / 0.745 (0.681) | 0.795 (0.67) / 0.785 (0.716) / 0.768 (0.699) |
| land nudge, long-haul / local | 0.807 / 0.84 / 0.785; 0.681 / 0.653 / 0.695 | 0.806 / 0.815 / 0.783; 0.676 / 0.643 / 0.682 | 0.824 / 0.833 / 0.807; 0.688 / 0.666 / 0.701 |
| herders' grain met | 0.0302 / 0.1264 / 0.1227 | 0.0302 / 0.1267 / 0.1203 | 0.0267 / 0.0957 / 0.1035 |
| grain unmet (all eras) | 0.535 / 0.487 / 0.348 | 0.536 / 0.487 / 0.349 | 0.560 / 0.509 / 0.371 |
| long-haul stretches an era | 1,546 / 1,472 / 1,467 | 1,384 / 1,358 / 1,232 | 1,410 / 1,340 / 1,315 |
| all routes, stretches an era | 2,162 / 2,143 / 2,145 | 2,010 / 2,027 / 1,909 | 2,009 / 1,976 / 1,962 |
| trading towns at the present | 301 / 520 / 476 | 236 / 310 / 241 | 242 / 347 / 353 |
| derive s | 62 / 72 / 109 | 54 / 47 / 81 | 77 / 53 / 128 |

- On 07c755, herders' grain is 0.0024 below main's. With droves off as well (07c755 only) it is 0.1200, so the dip comes from the river
  hands. Grain's own costs are unchanged (bulk pays no hands). The cause is the thinner long-haul network: fewer trading towns (476 →
  241) means fewer merchant quarters, and fewer quarters lift a border's toll for every good the next era. Grain unmet over all eras is
  unchanged (0.349 against 0.348), and so is the share of herders with any grain (0.543).
- Steadiness: 07c755's mean is 0.745 against main's 0.750, with a better worst frame (0.68 against 0.64). 3e0eb4 loses 0.02.

**Each good's reach** (people-weighted km of its flows between cultures, tribute left out; main d8152d53 → this lane):

| good | median km (0141d1 / 3e0eb4 / 07c755) | far tenth (p90) km | mainly by sea / by river (share of flows) |
|---|---|---|---|
| spices | 6,918 → 5,265 / 8,160 → 5,082 / 5,187 → 4,449 | 11,288 → 9,540 / 14,611 → 8,677 / 9,675 → 7,577 | sea 0.36 → 0.71 / 0.16 → 0.77 / 0.49 → 0.73; river 0.64 → 0.29 / 0.83 → 0.22 / 0.50 → 0.23 |
| horses | 2,814 → 2,308 / 1,717 → 1,284 / 1,561 → 1,549 | 4,702 → 4,281 / 4,221 → 4,097 / 4,259 → 4,311 | sea 0.55 → 0.49 / 0.31 → 0.42 / 0.45 → 0.49; river 0.41 / 0.66 / 0.45 → 0 |
| livestock | 2,227 → 1,972 / 1,437 → 1,264 / 1,677 → 1,566 | 4,718 → 4,595 / 3,810 → 3,704 / 3,917 → 4,036 | sea 0.43 → 0.36 / 0.20 → 0.21 / 0.42 → 0.45; river 0.52 / 0.77 / 0.52 → 0 |
| gold | 889 → 552 / 1,431 → 1,176 / 1,080 → 827 | 2,684 → 2,880 / 3,696 → 3,535 / 3,050 → 2,011 | river 0.77 → 0.53 / 0.74 → 0.57 / 0.87 → 0.68 |
| cloth | 339 → 313 / 153 → 124 / 155 → 94 | 2,041 → 1,890 / 1,768 → 1,373 / 2,399 → 1,509 | river 0.73 → 0.59 / 0.72 → 0.69 / 0.50 → 0.46 |
| salt | 885 → 847 / 905 → 844 / 792 → 738 | 1,761 → 1,717 / 2,273 → 2,590 / 2,437 → 2,381 | |
| oil and wine | 1,004 → 872 / 540 → 525 / 410 → 397 | 3,176 → 3,040 / 2,845 → 2,381 / 4,297 → 3,604 | |
| grain | 1,011 → 1,004 / 736 → 732 / 1,157 → 1,155 | 4,586 → 4,621 / 3,727 → 3,791 / 4,368 → 4,385 | unchanged (bulk) |
| timber | 779 → 762 / 152 → 145 / 1,975 → 1,954 | 7,099 → 7,022 / 2,922 → 2,897 / 4,587 → 4,608 | unchanged (bulk) |

**Against lane 225's ranges** (step4b.md section 2):
- Spices (a few thousand km by median, ~8,000 by far tenth): **in range on 07c755 and 3e0eb4** (7,577 and 8,677 km). On 0141d1 the far
  tenth is 9,540 km, within the draft's ~8,000-10,000. The medians are 4,400-5,300 km.
- Horses (mostly overland ~1,000 km; the sea case ~3,000-3,500 km): **closer, not in range.** The medians are 1,300-2,300 km and the far
  tenth ~4,100-4,300. Flows mainly by sea are still 0.42-0.49.
- Precious and middling goods stay in the ranges step4b.md reached; cloth's far tenth shortens to 1,400-1,900 km.

## 4. What changed in the code

- `trade_flow.py` (doc version 9; the doc's constants list the new ones):
  - `RIVER_HANDS`: in `_Frame.cost`, a river edge (mode 1) also costs `hop x L / HAND_KM[class]` for middling and precious goods, as a
    sea edge does.
  - `DROVES`, `DROVE_GOODS` (livestock, horses), `DROVE = 0.25`: `_Frame` builds a third edge set, "drove". On land it costs the cheaper of
    the carriers' factor and DROVE (x the hills), it has no river boat, and at sea it is as any middling cargo. `_Frame.cost_of(good)`
    picks a good's class, fetch and drove, and `walk` and `_exchange` use it.
  - `RIVER_COURSE` (False): when on, a river edge only joins a cell to its `downstream` cell, either way, downstream cheaper. Off, as
    main.
- Tests: `test_a_boat_follows_its_rivers_course_and_not_across_to_the_next_river`, `test_a_river_km_costs_the_hands_as_a_sea_km_does`,
  `test_herds_and_horses_walk_as_a_drove_and_take_no_boat`.

## 5. Status

- Draft "river hauls past reach": **closed by this lane and deleted.** Spices' far tenth is 7,600-9,500 km, inside the draft's
  ~8,000-10,000 km bar.
- Draft "herds walk, ships dear": **updated, still open.** The droves are built and sourced, and herds take no river boat. The sea cost of
  a horse found no fetched number that converts to a factor, and the far tenth by sea stays ~4,100-4,300 km.
- New draft: following the river's course (built, off) against herders' grain.
- Bars: steadiness 0.776 / 0.766 / 0.745 (≥ ~0.75 on all three, 07c755 at main's level). Herders' grain is equal on 0141d1 and
  3e0eb4 and 0.0024 under main on 07c755 (section 3). The derive is faster than main's.
