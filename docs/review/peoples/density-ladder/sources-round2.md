# Density ladder, sources round 2: irrigation without the plough (PW-1378), den peoples' raiding share (PW-1377)

Lane 138, 2026-11-02. Docs and sources only: no model code changed, no sims. Builds on `ladder.md` (lane 130) and `build.md`
(lane 137); the code is `planet/lineages/ladder.py`.

## In plain words

- **Irrigation does not need the plough.** Every irrigated farming system of the pre-Columbian Americas and of Polynesia was
  worked without plough animals (digging sticks, stone hoes, spades), and the ones with numbers fed as many people per km² of
  watered field as Egypt's Nile at its densest, or more: Aztec chinampas roughly 1,000-1,700 people per km² of chinampa (a
  second-hand estimate), Kaua'i's taro pondfields roughly 600-1,300 (my arithmetic on a modelled harvest), Ifugao rice terraces
  roughly 350-450 people fed per km² of terrace (a model of one village). The ladder's Nile curve runs 30 to 240. So tying
  irrigation to the plough would contradict the sources, and nothing supports a lower rung for non-plough irrigation either.
  **Recommendation: leave it.** If kenku at 10% of people looks wrong for play, the lever is somewhere else (which peoples hold
  the river cells, or how fast hunting and gardening peoples take up crops, the open draft from lane 137), not the plough.
- **Raiding: nothing measured exists that I could read.** No source gives the share of a raiding people's food that came from
  raids, or ties raid frequency to the neighbours' density. What the numbers that do exist say is that raided stock mostly
  went to bridewealth and trade rather than the pot (Nyangatom; Apache), that raiding rebuilt herds after droughts (Turkana),
  and that the fear of raids emptied land: 47% of Turkana district, best grazing included, stood virtually unused in 1982-84.
  **Recommendation: keep RAID_CAP 0.3 and RAID_HALF 5 /km², still marked as judgements.** If anything 0.3 of food is generous.
  One follow-up drafted: raiders should thin the farmers and herders near them, which the ladder does not do.
- Almost every number here is second-hand or rests on a model; each row says how it was read. The papers that would settle
  both questions are paywalled or blocked and are on the wishlist.

## PW-1378: irrigation without the plough

### What the ladder does now

`Ladder.line`: any people that knows cultivation gets the irrigation curve IRR (30, 75, 130, 140, 180, 240 per watered km²,
Butzer 1976 Table 4, Nile valley 4000-150 BC) on the watered share of a cell, IRR_LAG 3.5 kyr after cultivation, whether or not
it has a plough animal (Q5 A limited it only to cells water reaches). A gardener without a plough therefore farms the dry part
of a cell at GARDEN 5 and the watered part at the Nile's number. Butzer's farmers were plough farmers; the question is whether
that matters.

### What the sources say

| case | tools (no plough animal) | people per km² of watered field | people per km² of all land | how it was read |
|---|---|---|---|---|
| Nile valley, Egypt (the ladder's curve, for comparison) | ox plough | 30 (4000 BC) to 240 (150 BC) | far less (Egypt's desert) | Butzer 1976 Table 4, read by lane 130 (`ladder.md`) |
| Aztec chinampas, Basin of Mexico, late Aztec | digging stick (*huictli*, a wooden blade at one end) | ~975-1,670: 117,000-200,000 people on ~12,000 ha at 160 kg maize a head (my division) | not found | Area and people: Etra 2023 (popular article) attributing them to Armillas and Sanders, no publication named: **tertiary**. Area cross-check 9,000-10,000 ha: Crossley 2004 p. 111 (read, full). Tool: Wikipedia "Chinampa" citing Rojas Rabiela 1984 (**secondary**). A higher claim, >=5,000 (at least half a million on 10,000 ha, Torres-Lima et al. 1994 p. 39), seen only quoted in a student blog (Woodard 2011): **tertiary**, not used. |
| Kaua'i, Hawai'i, taro pondfields (*lo'i*), modelled at contact | digging sticks, spades | ~600-1,340 (my arithmetic, below) | not computed (island area not sourced here) | Ladefoged et al. 2009, **abstract only**: Kaua'i "could have supported 58 km² [of intensive agriculture], all as irrigated wetland systems", potential yield ~49k t a year, ~8,400 workers. Conversion: taro corm 13-29% carbohydrate, fresh weight (Onwueme 1999 section 5.1 and Table 3, read, full), at 4 kcal/g and 2,000 kcal/person/day. Assumes the 49k t are fresh taro; the abstract does not say which crop or weight. |
| Ifugao, Philippines, rice terraces (*payo*), modelled village, 1800 | hand tools (the paper does not name them) | ~340-440 people fed per km² of terrace (my arithmetic, below); ~1,010 people living per km² of terrace | ~54 over the village's modelled 2,113 ha (most of it hunting land); ~157 over its 723 ha of non-hunting land | Findley et al. 2022 (read, full main text): Old Kiyyangan Village 852-1,136 people, ~112 ha of terraces (rice at 1,650 kg/ha plus ~15 ha of taro and a 30% surplus); rice "32% of annual diets". 1,136 / 1.12 km² = 1,014 living per km²; x ~0.34 of the diet from the terraces = ~345, x 1.3 with the surplus = ~450. Land shares for all Ifugao (rice terraces 17% of total land, swiddens 15%, woodlots 25%): Dove 1983, a review of Conklin 1980, read through its HRAF abstract (**secondary**). |
| Hohokam, Salt and Gila rivers, Arizona, c. AD 1300 | stone hoes, wooden digging sticks | not found; a modelling convention of 2 ha of canal-watered field per household (Zhu et al. 2018, read) would give ~250-300 at 5-6 people a household, but the household size is my assumption | not found | Canal System 2 "probably capable of irrigating over 10,000 acres" and the tools: Howard, *Hohokam Legacy: Desert Canals* (Pueblo Grande Museum Profiles 12, WaterHistory.org, read). >40,000 people in the Hohokam region c. 1300: Archaeology Southwest, "Pieces of the Puzzle" (read; no citation given). No matched area and population in what I could read. |
| Andes (coastal Peru valleys, highland terraces) | foot plough and hoes (no draft animals) | not found | not found | Billman 2002 (Moche valley irrigation) appeared only as a broken search snippet; not read. Wishlist. |
| East African hill-furrow irrigation (Marakwet, Sonjo) | hoes | not found | not found | Only totals or district averages turned up (Sonjo ~4,500 in six villages per Gray 1963, Kerio valley ~15 /km² overall), both in search snippets; not read, not used. |

### Reading

1. **Irrigation without the plough is the rule outside the Old World, not the exception.** The Americas and Polynesia had no
   plough animals at all, and their irrigated systems were among the densest farming anywhere. Tying irrigation to the plough
   (option A) would forbid what the sources show.
2. **Per watered km² the non-plough cases sit at or above the Nile curve, not below it.** Chinampas ~1,000-1,700 and Kaua'i
   ~600-1,300 against the curve's top of 240. The Ifugao terraces, the one case built from a village-level model, sit at ~350-450
   people fed per km² of terrace. None of these supports a lower rung (option B). They are late, intensive, labour-heavy systems
   (Ifugao terraces need 630 days of work a hectare a year, Conklin 1980 quoted by Findley et al.), and the numbers are uncertain
   by a factor of two at least, so they also do not justify raising IRR (and Earth is a plausibility anchor, not a target).
3. **Over all land the cases look like the ladder's cells.** The Ifugao village at ~54 people per km² of all its land (157
   without its hunting land) brackets the ladder's irrigation-led cells (33-44 people per km² of whole cell, `build.md`).
4. **Where the plough does matter is the dry land.** The ladder already gives a gardener GARDEN 5 on the unwatered part of a cell
   against the plough's 8-25: the plough's advantage is rain-fed, which the sources agree with (Butzer's own densities rise with
   lifting devices, which water more land, not with the plough).

### Recommendation (PW-1378): option C, leave it

Keep irrigation open to every cultivating people on the cells water reaches, at the same curve. The kenku result is a
consequence of where kenku live and that they farm at all, not of a missing plough rule. If the share still looks wrong, the
candidate levers are lane 137's draft on hunting and gardening kinds taking up crops too easily
(PW-1373) or the river-cell settlement order; neither
needs this ticket.

## PW-1377: the den peoples' raiding share

### What the ladder does now

Goblins, kobolds, troglodytes: density = forager x kind 1.2 / (1 - r), r = RAID_CAP x settled / (settled + RAID_HALF), with
settled the farmers' and herders' people per km² within RAID_REACH 2 rings. RAID_CAP 0.3, RAID_HALF 5 /km².

### What the sources say

| source | what it measures | the number | how it was read |
|---|---|---|---|
| Opler 1941 p. 332 (Chiricahua Apache) | raiding against hunting | "raiding approaches hunting in economic significance" (qualitative) | lane 136, `build.md` |
| Encyclopedia of World Cultures 2008, Western Apache | meat share of the diet, raided stock included | ~35% | lane 136, **secondary** |
| Khazanov 1994 pp. 155, 187, 221-222 | raiding as a livelihood | "an important supplementary means of livelihood", "too unreliable" (qualitative) | lane 136 |
| Glowacki & Wrangham 2015, Nyangatom (SW Ethiopia) | raids per man; where the loot goes | young men (non-elders) took part in a mean 2.91 stealth raids in the study period (SE 0.34, n = 91; elders none); captured cattle "generally not kept by the warrior but given to paternal kin" for bridewealth | read, full main text (period length is in the SI, not read) |
| Gila Cliff Dwellings administrative history (NPS, ch. 1), Apache raids in New Spain | livestock taken | "68,000 livestock animals were stolen" in 1771-1776 (region not named in the sentence; the paragraph is on Nueva Vizcaya); "Stolen livestock was the most common Apache trade commodity" | read; **secondary**, its source is an endnote not shown. No Apache headcount, so no per-person share |
| Hendrickson, Armon & Mearns 1998, Turkana (NW Kenya), via ENN Field Exchange 6 summary | land use under the threat of raids; raiding's role | "47 percent of Turkana district - including much of the best grazing land, was virtually unused" in 1982-84 for "the mere threat of raiding" (a 1985 study, unnamed); raiding "has served to rebuild herds after livestock have been killed by drought or seized in raids" | read, the summary only (**secondary**); the paper is on the wishlist |

Not found in anything readable: a share of food or income from raiding for any people; raid frequency against the victims'
density or wealth. Searched for: Apache and Comanche raid takings, Turkana and Pokot raid counts (Schilling et al. 2012, open
access but blocked to the fetcher), Bedouin camel raiding (Sweet 1965, blocked), Mathew & Boyd 2011 (Turkana raids; the
abstract has no counts), Karamoja herd losses (raiding not separated from disease and drought).

### Reading

1. **The one measured-looking food number is still the Western Apache meat share (~35%, raided stock inside it).** The raided
   part of it is smaller. RAID_CAP 0.3 of all food sits at or above anything the sources suggest, not below.
2. **Raided stock was capital, not dinner, in the two cases with numbers:** bridewealth for the Nyangatom, trade goods for the
   Apache. A den people's raiding share as *food* is therefore an upper reading.
3. **Raiding's measured effect is on the victims.** The Turkana figure (47% of a district left unused for fear of raids) is the
   only area number found, and it runs the other way to the ladder: raiders thin the herders near them. The ladder lets den
   peoples gain from settled neighbours without those neighbours losing land. That is a model gap, not a reason to change the
   cap; drafted.
4. **RAID_HALF 5 /km² has no source at all**; nothing ties raid returns to how dense the victims are. Five per km² (a gardening
   village country, `ladder.md`) stays a judgement.

### Recommendation (PW-1377): keep both numbers, still marked as judgements

Keep RAID_CAP 0.3 and RAID_HALF 5. Update the code comment's sources (Glowacki & Wrangham, Hendrickson et al. via ENN) when the
file is next touched; no code change from this lane. If a raid-share number is ever wanted for real, the most promising reads
are the Turkana raid series (Schilling et al. 2012; McCabe 2004) and Sweet 1965, all on the wishlist.

## Second check (every cited number re-opened)

Each number above was re-opened in a second fetch or re-grepped in the downloaded text, after the tables were drafted.

| number | re-opened | result |
|---|---|---|
| Chinampas 9,000-10,000 ha, late Aztec | Crossley 2004 text, p. 111 (local pdftotext) | confirmed ("some 9,000 to 10,000 hectares"); journal line "Historical Geography Volume 32(2004): 111-35" confirmed |
| 12,000 ha, 117,000-200,000 people, 160 kg maize a head, Armillas and Sanders | Etra 2023, second fetch | confirmed; the page names no publication for it (kept as tertiary) |
| 10,000 ha, "at least half a million people" (Torres-Lima et al. 1994: 39) | Woodard 2011 blog, second fetch | confirmed; tertiary, not used in the recommendation |
| digging stick *huictli* | Wikipedia "Chinampa", second fetch | confirmed, citing Baquedano 1993 and Rojas Rabiela 1984 |
| Kaua'i 58 km² irrigated, ~49k t, ~8,400 workers | Ladefoged et al. 2009 abstract, second fetch | confirmed; crop and fresh/dry weight not stated (caveat kept in the table) |
| taro corm 13-29% carbohydrate | Onwueme 1999 text, re-grepped (section 5.1 and Table 3) | confirmed |
| Ifugao 852-1,136 people, ~112 ha, 1,650 kg/ha, 30% surplus, 2,113 ha (hunting 1,390 + other 723), rice 32% of diet | Findley et al. 2022, second fetch | confirmed; the 112 ha includes ~15 ha of taro and the surplus; first fetch's "~13.3 vs 13.4 ha" for 1570 is the paper's own inconsistency, not used |
| 630 days a hectare a year (Conklin 1980) | Findley et al. 2022, first fetch | as quoted by Findley; secondary |
| rice terraces 17%, swiddens 15%, woodlots 25% of total land | Dove 1983 HRAF page, second fetch | confirmed; it is HRAF's abstract of Dove's review of Conklin (secondary) |
| Canal System 2 >10,000 acres; stone hoes, digging sticks | Howard, WaterHistory.org, second fetch | confirmed, with Howard's "probably"; the page gives no population |
| >40,000 people in the Hohokam region c. 1300 | Archaeology Southwest, second fetch | confirmed; no citation on the page (Coalescent Communities Database) |
| 2 ha of irrigated fields per farm (household) | Zhu et al. 2018, second fetch | confirmed; a modelling choice ("For our analysis"); household size not given |
| Nyangatom 2.91 stealth raids, SE 0.34, n = 91 | Glowacki & Wrangham text, re-grepped | confirmed |
| 68,000 livestock 1771-1776; stolen livestock the most common Apache trade commodity | NPS Gila Cliff Dwellings history, second fetch | confirmed; region not named in the sentence, source in an endnote not shown |
| 47% of Turkana district unused 1982-84; raiding rebuilt herds | ENN Field Exchange 6, second fetch | confirmed; the 47% is "a 1985 study" the summary does not name |
| Nile 30-240 per watered km² | `ladder.md` row "Irrigation farming" (lane 130's read of Butzer 1976) | as in ladder.md; not re-read here |

Dropped after the check: Conklin's "250 per km² of cultivable land" for Ifugao (seen only in a search-result snippet of
Acabado's Hukay paper, whose PDF was blocked) and a Hohokam "80,000 people" (a student history page with no source).

## Not readable (wishlist)

Kirch 1994 *The Wet and the Dry* (Futuna and Polynesian irrigation densities); Kurashima, Fortini & Ticktin 2019 (Nature
Sustainability, Hawaiian lo'i production and the people it fed); Ladefoged et al. 2009 full text; Parsons 1976 (chinampas and
Tenochtitlan's food); Conklin 1980 or Acabado's Hukay paper (Ifugao densities); Billman 2002 (Moche valley irrigation and
population); Schilling, Opiyo & Scheffran 2012 (Turkana-Pokot raid counts); Hendrickson, Mearns & Armon 1996 and Hendrickson,
Armon & Mearns 1998 full texts; Sweet 1965 (Bedouin camel raiding). Listed in `docs/references/wishlist.md`.

## Web pages used (not papers, so not in the bibliography)

- Etra, J. 2023, "Chinampas, Calzadas, and Aqueducts: The Ancient Engineering Marvels of Tenochtitlán", The Eye (Huatulco), 29 Jan 2023.
- Woodard, S. 2011, "Chinampa: raised-bed hydrological agriculture", anthrome.wordpress.com, 24 Apr 2011.
- Wikipedia, "Chinampa" (read 2026-11-02).
- Howard, J. B., *Hohokam Legacy: Desert Canals*, Pueblo Grande Museum Profiles 12, on waterhistory.org/histories/hohokam2/.
- Archaeology Southwest, "Pieces of the Puzzle", Puzzle Piece 4 (online exhibit).
- National Park Service, *Gila Cliff Dwellings NM: An Administrative History*, ch. 1 (npshistory.com, updated 2001).
- ENN, *Field Exchange* 6 (Feb 1999), summary of Hendrickson, Armon & Mearns 1998.
