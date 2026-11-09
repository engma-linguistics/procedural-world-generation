# Salt fish inland and grain's sea tail (PW-1573, PW-1572; lane 244)

Code: `planet/lineages/trade.py` (`FISH_NEED`, the `dried_fish` row of `NEED` and `NEED_GATE`; ledger `VERSION` 4) and
`planet/lineages/trade_flow.py` (`SEASON`, `SEASON_KM`, `SEASON_LOAN` in `_Frame.cost`; exchange `VERSION` 10). Tests:
`tests/test_trade.py::test_farmers_and_towns_away_from_fish_want_dried_fish`,
`tests/test_trade_routes.py::test_a_bulk_cargo_pays_a_season_of_capital_per_season_leg_at_sea`. Harness: [bought_in_244/](bought_in_244/)
(`setup.sh` makes a scratch data root of symlinks; `go.sh` runs `h.py` on the four runs, one thread each; `cmp.py` compares; `samp.py`
gives sample cultures).

**Baseline:** main dd82c068, measured with the same harness, the new switches off (`TR.FISH_NEED=False TF.SEASON=False`). Those numbers
match main's code exactly, and lane 235's table in [bought_in.md](bought_in.md). Seven Meals (1e97dd, 07c755) is measured only; nothing
was tuned on it.

## In plain words

- **Salt fish now travels.** Before, nobody wanted dried or salted fish, so it never left the coast. Now towns and farmers away from
  fishing waters want it, if their people keep smoked or salted food. A cell's own fish (sea, river runs, big lakes) meets the want
  first. Cured catch beyond the coast's own want is what goes inland. On the four stored L7 runs, **43 to 74 cultures now buy salt
  fish** (main: none). Most of it goes a few dozen km (median 27-58 km). The far tenth goes 126-373 km, mostly by river and overland, and
  a few cultures get it from 1,000-3,000 km by sea.
- **Grain no longer sails so far.** A bulk cargo now pays a season's capital and risk for every season's leg at sea. Egypt's grain ships
  made one round trip a year, over about 1,000 miles each way. So a grain cargo loses ~18% of its value on a leg like that, on top of
  the freight. The far tenth of grain deliveries falls from **2,260-2,911 km to 1,693-2,355 km**, which is about Egypt to Rome. Rare
  hauls of 5,000-11,000 km remain, at 1-7% of a culture's people (see "Not done").
- Herders' grain changes by -11% to +3% at the present (people-weighted share bought, against main). The sea haul's new cost explains
  that: herders' far grain came by sea.

## 1. Who wants dried and salted fish (PW-1573)

Sources (fetched and read):
- **Barrett, Locker & Roberts 2004**, "The origins of intensive marine fishing in medieval Europe: the English evidence", Proc. R. Soc. B
  271 (https://eprints.whiterose.ac.uk/1317/1/barrettjh1.pdf). The study covers 127 English fish-bone assemblages, AD 600-1600, and
  counts "inland sites" as those "more than 10 km from the coast and not on an estuary".
  - The clearest change came "rapidly around AD 1000 and involved large increases in catches of herring and cod".
  - Its cause: "the concurrent rise of urbanism and human impacts on freshwater ecosystems". The fish revolution "was probably driven by
    Christian fasting regulations, population growth, urbanism and declining freshwater fish resources".
  - "Herring and cod were cured and widely traded by the twelfth century".
- **Orton, Locker, Morris & Barrett 2016**, "Fish for London", in *Cod and Herring* (Oxbow), pp. 205-214
  (https://knowledge.lancashire.ac.uk/id/eprint/16954/).
  - The change "appears initially to have been linked primarily to urban sites, with widespread marine fish consumption at inland
    rural settlements argued to be a slightly later development".
  - Towns "involve a concentration of food consumers rather than producers and hence require a significant hinterland to meet demand.
    Turning to marine resources is one way to expand this resource base."
  - Imports "from northern waters only becoming common during the thirteenth to fourteenth centuries". London's processed cod came most
    likely as "stockfish from the North Atlantic, particularly Norway".
- The epic's review already has the Hanse's "herring and grain for salt; Bergen stockfish for grain" ([review1.md](review1.md)
  section 4).
- Wikipedia's Stockfish and Dried fish pages give only that "dried fish has a storage life of several years". Nothing else from them
  was used.

The rule (trade.py `NEED["dried_fish"]`):
- **Who wants it.** Everyone in a town and everyone who farms, on land. Towns and farmers alike, as the sources say both inland towns and
  inland farms took it up. The want is a share of people, as for salt's farmers; no diet share is sourced.
- **Who does not.** Herders and foragers. The sources are about towns and farms.
- **A people that keeps no smoked or salted food** (knows neither `smoking_drying` nor `salting`) has no want (`NEED_GATE`).
- **Its own waters first.** A cell's fresh fish (`fish`: shelf seas, river runs, big lakes), cured or not, meets its want first:
  lack = max(0, want - fish). This is Barrett's "declining freshwater fish resources": people bought sea fish where their own fish fell
  short.
- **Not modelled: a fasting rule.** The faiths carry no food calendar, so Christian fasting, the main demand in the sources, has no
  counterpart. The want stands for the protein a town's hinterland lacks. Not drafted (no faith in the tree carries a food calendar yet).
- **Supply is unchanged.** The cured catch beyond the cell's own want is the surplus; that rule was already there. Dried fish stays a
  bulk good.

**Obsidian and sea-mammal oil** still have no need. Obsidian: flint is not modelled, so a want of edge stone would be overstated (the
existing note). Seal and whale oil: the only cheap want, lamp oil for northern peoples away from the coast, has no source in the epic's
review. Fetching one was not cheap enough for this lane. Left as a note in trade.py.

## 2. Why long bulk-grain hauls were rare (PW-1572)

Sources (fetched):
- **Wikipedia, Cura Annonae.** Rome's Egyptian grain ships "likely only completed one round trip per year", while "Several round trips
  per year could be accomplished from North Africa or Sicily". The trip took "2,000 to 3,000 merchant voyages annually, with each vessel
  carrying an average of 70,000 kg". Sailing back from Alexandria "took at least a month and on occasion two or more"; "Lionel Casson
  estimated that average time for the voyage was nearly 70 days".
- **warhistory.org, "The Roman grain trade"** (secondary). Alexandria lies "a distance of 1,000 miles" from Rome. "Navigation was
  strongly discouraged from mid-November to early March". Rome needed "800 shiploads of average size ... between spring and autumn".
- **The sea loan** (Dem. 35.10, fetched by lane 225, [step4b.md](step4b.md) section 1): a season's round trip, capital and risk, cost
  22.5% of the cargo (30% late in the season).

The reasoning:
- **The model before.** A bulk cargo paid freight alone at sea, plus one port call (HANDLE). Lane 225's judgement was "one hull, port to
  port" (HAND_KM).
- **A season.** A hull's year is one sailing season. Egypt's leg of ~1,000 miles took the whole season, with the return. A shorter leg
  took a fraction of a season, and Africa and Sicily sent several voyages a year.
- **The cargo's capital and risk** are paid per season, at the sea loan's 22.5%.
- **Spread over the season's laden leg,** that is a share of the cargo's value per km at sea. The value e-folds every
  1,609 km / ln(1.225) ≈ **7,900 km**:
  - ~18% of the value on Egypt's leg;
  - ~47% on a 5,000 km haul;
  - ~72% on a 10,000 km haul (which no one hull could sail in a season anyway).
- **Grain's low value per weight** is what makes the haul short. Freight and port calls are weight, and they are already a large share
  of a cheap good's value: one port call is ~7% of bulk's value against ~2% of a dear good's (FALL_KM). The season's capital adds to
  them. Dear goods already pay their relayed price chains (HAND_KM); they are not charged again.
- **Sea only.** River hauls are short and run through the cultures' land, where the fall-off and the tolls already carry the hands.
  Lane 226 found that river hands cut herders' grain.
- **A mechanism, not a clamp.** Every bulk haul at sea pays it, in proportion. No distance is cut off.

**Tried and dropped: a further port call per season's leg.** In it, a cargo that sails past one season's leg is landed, wintered and
reloaded. That needs the walk's cost to depend on the sea km already sailed on the path. Built into `_walk` and `_seek`, the shared walk
did not finish the first grain walk of one frame in over 3 minutes (main: under 1 s). With a very long leg (no leg ever counted) it ran
as fast as main, so the leg count was the cause. The likely reason is that a cost depending on the path breaks the source-death
re-walk's assumption, that taking a source away lowers no other cost. This was not proven. It was reverted. The per-km season charge above is the part that keeps the walk exact.

## 3. Numbers on the four stored L7 runs

Read-only, from a scratch data root of symlinks. Givers are weighted by share times the taker's people, as lane 235's stats.py.
"Main" here is main dd82c068.

### Salt fish (dried and salted fish)

| run (tree) | era | cultures buying it (main → now) | of which not by tribute | median / far tenth km | max km | roads (share of weight) |
|---|---|---|---|---|---|---|
| 3e0eb4 (D&D) | now | 0 → 74 | 45 | 27 / 170 | 2,958 | tribute 77%, overland 14%, river 5%, sea 4% |
| 3e0eb4 (D&D) | 5 kyr | 0 → 53 | | 41 / 349 | 2,190 | overland 40%, river 40%, tribute 11%, sea 9% |
| a24559 (D&D) | now | 0 → 68 | 50 | 58 / 373 | 2,503 | tribute 62%, overland 18%, river 11%, sea 7% |
| a24559 (D&D) | 5 kyr | 0 → 60 | | 86 / 261 | 1,749 | overland 56%, tribute 43% |
| 1e97dd (Seven Meals) | now | 0 → 43 | 30 | 44 / 127 | 547 | tribute 43%, overland 34%, sea 21% |
| 1e97dd (Seven Meals) | 5 kyr | 0 → 40 | | 64 / 466 | 1,509 | overland 39%, sea 21%, tribute 20%, river 17% |
| 07c755 (Seven Meals) | now | 0 → 56 | 25 | 45 / 126 | 1,076 | tribute 65%, river 23%, overland 11% |
| 07c755 (Seven Meals) | 5 kyr | 0 → 58 | | 264 / 486 | 7,666 | tribute 53%, river 28%, sea 13% |

"Tribute" is the exchange's label for a flow from a ruled culture to its ruler (trade_flow.kind_of); it is not tribute in kind.
Comparison: London's stockfish came from Arctic Norway from the 13th century (Orton et al. 2016), ~2,000 km [est.]. Most salt fish here
goes far less far; it is a bulk good (FALL_KM) and goes overland and by river more than by sea. See draft-trade-dried-fish-class.md.

### Grain

| run | era | median km (main → now) | far tenth km (main → now) | max km (main → now) | share of weight beyond 5,000 km (main → now) |
|---|---|---|---|---|---|
| 3e0eb4 | now | 699 → 694 | 2,738 → 1,693 | 16,376 → 11,252 | 5.1% → 4.0% |
| 3e0eb4 | 5 kyr | 632 → 630 | 1,353 → 1,352 | 6,599 → 6,479 | 0.4% → 0.3% |
| a24559 | now | 460 → 387 | 2,260 → 1,708 | 6,250 → 5,555 | 0.4% → 0.4% |
| a24559 | 5 kyr | 404 → 353 | 2,290 → 2,016 | 12,398 → 10,989 | 8.1% → 1.4% |
| 1e97dd | now | 888 → 765 | 2,911 → 2,355 | 12,341 → 9,746 | 1.3% → 0.5% |
| 1e97dd | 5 kyr | 938 → 825 | 2,465 → 2,382 | 13,856 → 8,434 | 0.6% → 0.3% |
| 07c755 | now | 952 → 699 | 2,299 → 1,873 | 10,522 → 11,008 | 3.2% → 2.8% |
| 07c755 | 5 kyr | 888 → 778 | 2,929 → 1,625 | 19,404 → 12,203 | 5.8% → 0.8% |

Sourced comparison: Egypt to Rome, 1,000 miles (~1,600 km), the farthest regular grain route of the Roman grain supply (above).

**Herders' grain**: the people-weighted share of herders' people (25%+ herding) that buys grain, main → now.
- now: 0.119 → 0.115, 0.037 → 0.033, 0.112 → 0.115, 0.131 → 0.125 (3e0eb4 / a24559 / 1e97dd / 07c755);
- 5 kyr: 0.119 → 0.123, 0.027 → 0.027, 0.120 → 0.110, 0.106 → 0.089.

The largest fall is 07c755 at 5 kyr (-16%, 4 herding cultures), whose far grain came by sea.

**The other goods** (the walk is shared): the sum of every flow's share over all eras is unchanged to within 1% for every non-bulk good.
The bulk goods fall a little, because they pay the season at sea too:
- grain -2% to -3%;
- timber -5% to +1%;
- firewood -4% to +2%;
- stone within ~1%.

The derive takes as long as before: 76-139 s a run against 78-159 s, one thread each.

### Sample cultures (the present)

D&D runs:
- **The kenku of the south of Simath (2)** (3e0eb4) buy salt fish from the tritons of the south of Simath, **977 km by river** (16% of
  their people), and from the dragonborn of Simath, 1,002 km by river.
- **The desert dragonborn of the south-west of Simath** (3e0eb4) buy salt fish from the tritons of the south of Simath, **2,117 km by
  sea** (13%).
- **The temperate elves of the south of Simath** (a24559) buy salt fish from the first tritons of the south of Simath, **1,188 km by
  sea** (10%).
- **The steppe leonin of the north of Tobrosal** (a24559) buy salt fish from the humans of Tobrosal, **144 km overland** (6%), and
  from the tritons of the north-east of Sakur, 1,176 km by sea.
- **The tortles of the south of Simath (2)** (3e0eb4) still get 6.8% of their grain from the dragonborn of Simath, **11,252 km by sea**.
  That is the longest grain row left on the four runs (main: 16,376 km).

Seven Meals runs (measured only):
- **The high mountain kobolds of Hizam** (07c755) buy salt fish from the first cloud giants of Hizam, **643 km by river** (19%), and
  from the first kobolds of the east of Hizam, 704 km.
- **The temperate antelope-kin of the north-west of Beditos (19)** (1e97dd) buy it from the hill giants of the north-west of Beditos,
  **334 km by river** (13%).

## Not done

- **A few grain rows still come from 5,000-11,000 km by sea** (1-7% of a culture's people). The fall-off is exponential, so a big
  enough surplus still reaches a culture with no nearer source, just less of it. A further port call per season's leg would cut this
  more, but the shared walk cannot count legs (section 2). draft-trade-grain-sea-tail-legs.md.
- A fasting rule for salt fish: not drafted (no food calendar in the faiths).
- Dried fish as a middling good (stockfish keeps for years and has lost most of its weight): draft-trade-dried-fish-class.md.
- A want for seal and whale oil: draft-trade-seal-oil-no-want.md.
