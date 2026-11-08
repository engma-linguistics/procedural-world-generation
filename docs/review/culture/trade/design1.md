# Trade, design round 1 (PW-1498 phase 2, lane 211)

Read first: [review1.md](review1.md) (the sourced literature review; its section numbers are cited here as R§n).
No model code in this lane. This is a plan in four steps. Each step is useful on its own, and it is built from mechanisms
(goods from the world's own land, costs from transport modes, fall-off with distance) rather than tuned numbers.

## In plain words

Today the model has trade only as a hint. A people's openness (1 − insularity) stands in for how much it trades
(`techtree.trade_of`, ruling D53). Salt is "reached by trade" up to 450 cost-km (`salt_reach.py`). Forager peoples get up to half
their food from farming neighbours (`ladder.BARTER_*`), and dwarven holds buy half their food (`ladder.TRADE_CAP`, a placeholder).
Nothing yet says **what** moves, **from whom to whom**, **how far** or **by what road**.

The plan:
1. **Goods ledger.** For every culture in every era, list what its own land gives in surplus and what it lacks. Examples: salt, metal
   ore, obsidian and flint, timber, grain, herd animals and their wool and milk, dried fish, oil, wine, sugar, spices, furs, gems.
2. **Exchange.** Goods pass between neighbouring cultures and fade with distance. How fast they fade depends on how much value the
   good packs per kilo, and on the cheapest way to carry it in that era: on foot, by pack animal, by cart, by river, along the coast,
   by open sea. How a people exchanges depends on its kind: gifts between forager bands, barter with farmers, markets in towns,
   merchant caravans and ships.
3. **Routes and hubs.** The big flows trace roads on the map. Towns where routes meet or change mode become trading towns: ports,
   river towns, caravan towns on the desert edge.
4. **Effects.** The culinary brief gets each culture's bought-in foods (what, from whom, from how far). Writing, techs and faiths
   spread along the busy routes instead of using the openness stand-in. Trade wealth helps a polity's seat. Finally, the two
   placeholders (hold food, forager barter) read real traded food.

Steps 1-3 are read-outs after the run, like the settlement ledger and the polities. Nothing feeds back into the history until
step 4's last part, and that part is a decision for Daniel (draft D-T1).

## What the model already has (read for this design)

| Need | Already there | Where |
|---|---|---|
| Who lives where, when | presence table per frame; cultures per frame (merges followed) | `output.write_presence`, `cultures.json`, `cuisine.culture_cells` |
| Way of life per cell | farm, herd and wood share of heads, density (eraq, the last ~12 kyr) | `landuse.frame_inputs`, meta.eraq |
| Land goods | ~40 goods 0..1 per cell, planet-relative: fertile, grazing, timber, fuel, ores (gold, iron, copper, tin), gems, salt, salt_rock, fish, shellfish, sea mammals, coal, stone, fantasy metals, sea goods | `land.GOODS`, `seafood.py`, `resources.py` |
| Crops and herds | known and wild crop bit layers per frame (24 crops incl. vine, olive, cane, spices, tea, capsicum); herd animals known | `crops.py`, `crop_defs.py`, `animals.py` |
| Fuels | per-cell fuel shares (wood, charcoal, dung, peat, coal, oil...) | `fuels.py` |
| Salt cost-distance | multi-source cost walk (SPFA) with river and contact-zone discounts, cap 450 cost-km | `salt_reach.py::_spfa` |
| Transport terrain | navigable rivers (`river_nav` 0-3), harbours 0-3, passes | `humanuse.py` |
| Transport and institution techs | trade (100 kyr), canoes (12), pack_animals (7), sails (7), salting (8), markets (5), plank_boats (4.9), weights_measures (4.8), tin_trade, commodity_money (4.5), harbours (4.6), pack_saddle (4.5), roads (4.5), coinage (2.7), navigation (1.0), caravanserais (0.9), ocean ships (Columbian, `animals.ocean_ships`) | `samples/techtree.toml`, `meta.techtree.known` |
| Towns and cities over time | ledger every 100 yr, sizes, site factors (harbour, river, pass), mines and mining colonies | `settlements.py`, `settlements.json` |
| Polities, war, reach | seats, claims, foot-km reach with riding and road factors; war between neighbours | `polities.py` |
| Contacts and openness | first contact, border length and kind of country; insularity, tolerance | `contacts.py`, `attitudes.py`, `techtree.trade_of` |
| Tech spread arms | B (town network), C (trade-contact speed 2.2 km/yr), T (B weighted by trade_of) | `techtree.py` (D52, D53) |
| Faith spread | conversion between neighbours, missionaries, rulers | `gods.FAITH_RULE` |
| Culinary brief | `trade_reach` is null and listed as not modelled; salt reach with trade; miners "sell / buy back" | `brief.py`, `cuisine.py` |

So most inputs exist. What's missing is a **goods table** (what a culture has and wants), a **cost graph** that knows transport modes
by era, and a **flow** between cultures.

## Step 1: the goods ledger (surplus and lack per culture per era)

**What it does.** It maps the existing layers onto about 16 **trade goods** in three value classes. The classes are what decides
how far a good travels (R§6, value per weight):

| Class | Goods (from layers) | Why this class |
|---|---|---|
| bulk (low value/kg) | grain (crops known x farm share x fertile), timber (`timber`), firewood/charcoal (`fuel`, fuels.py), building stone (`stone`), dried fish (`fish`) | moves far only by water (R§6) |
| middling | salt (`salt`, `salt_rock`, works), herd animals and wool, hides, dairy (herd share x animals known), oil and wine (vine, olive crops), dried fruit, sugar (cane), copper and tin ore/ingot (`copper`, `tin`), iron (`iron`), obsidian and flint (`res_obsidian`, `res_flint`), furs (`frost`, forest x foraging), seal oil (`sea_mammals`) | travels a few hundred km overland, much more by water |
| precious (high value/kg) | spices (tropical spice crop, capsicum, tea), gold, gems, shell and coral ornaments (`coral`, `shellfish`), fantasy metals (`mithril`), finished bronze and iron goods, cloth | worth carrying across continents (R§4) |

**Surplus** of good g in a cell is what its producers make beyond their own need: (the good's land value) x (the share of heads that
work it, from eraq) x (a know gate: the tech that unlocks it, e.g. `salting` for salt works, `copper`/`mines` for ore, a crop or
animal known). **Lack** (want) comes from the way of life and the techs known, not from a tuned number:
- farmers want salt, and metal once they know copper and bronze (tin especially: R§3, the "tin problem");
- herders want grain and craft goods (Khazanov: nomads cannot be self-sufficient, R§2);
- foragers want little in bulk, but they want starch and iron where farmers are near (R§2), and ornaments everywhere (R§1);
- towns and cities want grain and fuel from their hinterland (central place, R§5), and precious goods by size (elite demand);
- a cuisine plant (oil, wine, sugar, spice, tea) is wanted where a culture knows a dish or drink that uses it but cannot grow it.
  The first pass of this is a culture that knows `fermentation` or `feasting`. PW-744 lists what is missing.

**Reads:** cultures per frame, eraq, land goods, crop and herd known layers, fuels, techtree.known, settlement ledger.
**Writes:** `trade_goods.json` (per culture per frame: surplus and lack per good, 0..1 and heads-weighted), plus meta.trade.goods.
**Cost:** a per-cell table times ~16 goods over ~25 frames (the last 12.5 kyr at 0.5 kyr), or the ledger's 125 century steps.
This is vector work, so it should be seconds per run at L7, like fuels.py.
**Judged by:** each surplus and lack has to point to its layer, so a reviewer can check it on the globe, with no number tuned. Checks:
salt-poor interiors want salt (they match the brief's existing `salt` reach); tin is lacked by nearly every bronze-knowing culture
and held by few (R§3: tin sources are rare). Steppe herders lack grain.
**Daniel sees:** the culinary brief tab gets a "Has / lacks" line per culture (for example "has salt, wool, horses; lacks grain,
metal"), and a globe layer "Trade goods" (pick a good: surplus green, lack red).

## Step 2: exchange between neighbours (distance decay by mode and era)

**The cost graph.** Each edge between two cells costs (length) x (the cheapest mode open there and then). The mode factors are
the sourced cost ratios per tonne-km (R§6). From ORBIS's Edict-based numbers, with sea = 1: river downstream ~3.4, upstream ~6.8,
pack animal ~28, wagon ~35. China around 1680 gives porter ~75x river. China and England give land : river ~10-11, a check on the
same order. In the model's units, scaled to a pack animal = 1:

| Mode | Cost factor | Opened by | Source |
|---|---|---|---|
| porter (on foot) | ~3 | always | Cheng 2024: porter / pack mule 1.594 / 0.213 ≈ 7.5 (hill-to-flat mule 2.1); ORBIS gives no porter cost; JUDGEMENT within that span |
| pack animal | 1 | `pack_animals` + a pack beast known | ORBIS donkey/camel 0.028 d/kg/km |
| cart on flat open land, or road | ~1 | `wheel` (flat, open); `roads` (held land) | ORBIS wagon 0.035 (carts carry more but are slower); polities' ROAD_X |
| river downstream / upstream | ~0.12 / ~0.25 | `canoes` on `river_nav` >= 1 | ORBIS 0.0034 / 0.0068 |
| coastal and open sea | ~0.04 | `canoes` (one cell offshore), `sails`/`plank_boats` (coasts with harbours), `navigation` / ocean ships (open sea) | ORBIS ~0.001 at ~100 km/day |

The porter factor is the one judgement in the table: China's 7.5 includes hill roads, and forager women carry 20-30 kg against a
donkey's 65-100 kg (R§2, R§6).

The modes, in detail:
- on foot (porters): always open;
- pack animals: `pack_animals` + a pack beast known (donkey-, camel-, llama-like herd animal); cheaper per t-km, longer day ranges (R§6);
- carts and roads: `wheel` (open, flat ground), `roads` (any land the culture holds), as polities' ROAD_X already treats roads;
- river: `canoes` on `river_nav` >= 1, barges on >= 2 (downstream cheaper than up, R§6);
- coast: `canoes` along coasts within one cell, `sails`/`plank_boats` along any coast with harbours, `navigation` or ocean ships for
  open sea (crops.py and animals.py already have the strait / colonist / ocean-ship ladder; reuse it, do not fork it);
- a culture border adds a crossing cost. This is the friction of dealing with strangers, R§5's merchant diasporas. Tolerance
  (attitudes) lowers it. A merchant quarter of the giver's people in the taker's town (a step 3 hook) removes it. A war between
  their polities that century closes it.

This is the same graph and the same multi-source walk as `salt_reach._spfa`. Salt reach becomes one good of the general
pass, and its 450 cost-km cap becomes salt's fall-off length.

**The flow: down-the-line by default, markets and merchants where they exist.** For each good, supply spreads out from the
surplus cells along the cost graph and fades as exp(−cost / L_g). The decay length L_g is set by the good's value class. This
is Renfrew's exponential fall-off beyond the supply zone (R§1), and it shows up in obsidian, shell and Bronze Age goods alike.
A culture's import of g is min(its lack, the supply that reaches it). The exporter is whoever the supply came from, so each
flow has a giver, a taker, a distance and a mode. The mode of exchange is a label from the taker's and giver's kind of society
(R§1-R§5), and the label changes the decay:
- **reciprocity / gift** (forager bands): ornaments and some tools move. Ju/'hoansi hxaro partners live 2-200 km away, about 15
  per adult. Beads reach >300 km over chains (R§1);
- **down-the-line barter** (any neighbours; the default);
- **markets** (towns with `markets`): a town gathers its hinterland's surplus, so bulk food moves into towns. The market's
  reach comes from settled density, not a fixed walk. Skinner rejects walking distance as what sets market areas. His standard
  areas are 41-76 km² for 7,700-11,600 people and ~18 villages, smaller in dense country and larger at the edge (R§5);
- **merchant / long-distance** (`trade` + towns + a carrier mode: caravans after `pack_saddle`/`caravanserais`, ships after
  `sails`/`plank_boats`/`harbours`): the decay of precious and middling goods stretches to the caravan/ship ranges of R§4;
- **tribute** (a polity's seat taking from its claimed land, polities.py): goods move to the capital with no return. Tribute is not
  trade, but it shows on the same map (R§5, tribute vs trade).

L_g is not fitted per world. Each class's decay length comes from the review's sourced distances, in pack-animal km:
- **bulk:** ~100-150. Grain loses about half its value in ~150 km of cart haulage, and Cato's mill lost 39% over 75 miles (R§6).
  By river or sea the same budget reaches 1,000-4,000 km, which matches Rome's grain from Egypt.
- **middling:** ~300-450. Obsidian's supply zone is ~300 km (R§1). Salt's existing cap is 450 cost-km. Most Neolithic axes
  stayed under 200 km and rarely went past 400-500 (R§3).
- **precious:** ~1,000-1,500. Kanesh tin went 1,200 km by donkey. Alpine jade axes went over 1,000 km. Tin and spice went on to
  4,000 km and more by caravan and sea (R§3, R§4).

These are starting values, each with its source. Step 2 then checks the fall-off shape against Renfrew's curve and the gravity
elasticity of ~1.9 (Barjamovic et al.; R§3, R§6), and does not tune to them.

Because cost already counts the mode, one L_g per class covers all eras: the same good goes further when the era's mode is
cheaper. The forager case falls out the same way. Porters at factor ~3 give food a reach of ~40-50 km, which is a day's walk
and matches Kitanishi's camps at 1.5 h against 4-5 h (R§2).

**Reads:** step 1, the cost graph inputs (river_nav, harbour, coast, techs per culture per frame, polities and wars per century),
attitudes. **Writes:** `trade.json`: per frame, flows (giver culture, taker culture, good, amount, mean cost-km, km, main mode,
exchange label), and per-culture imports and exports. **Cost:** one multi-source walk per good per frame. That is ~16 x 25 walks
of the salt-reach kind at L7, probably a minute or two after a run; to be measured in the step's lane.
**Judged by** (sourced, R§):
- fall-off shapes: obsidian-like goods match the supply-zone-then-exponential shape (Renfrew; R§1);
- bulk goods overland stay within the sourced land range and go far only on water (R§6);
- forager imports: at most about half of their food, falling with distance to the farmers (Kitanishi/Bahuchet, already in
  ladder.BARTER_CAP; R§2);
- Bronze Age tin moves more than 1,000 km to bronze-users (Kanesh, Uluburun; R§3);
- spices and gold cross continents only after caravan or ship techs (R§4);
- **stable when nudged:** re-run on the 10% border nudge and a reseeded draw (as PW-1483 did). The top flows per culture should keep
  their giver and good (Jaccard of the top-5 flow sets above ~0.7: a judgement threshold, to be reported, not tuned to).
**Daniel sees:** on the culinary brief's culture sheet, "Bought in: salt from the X (300 km, by river), grain from the Y,
pepper (precious, 2,400 km, by sea and caravan)". In the workbench, a **Trade** tab: per culture, imports and exports by good, by
era, with the exchange kind (gifts, barter, market, merchants, tribute).

## Step 3: routes and hubs on the map

**What it does.** For each flow above a share of the world's total, trace its least-cost path on the step-2 graph (the walk
already has the predecessors) and add its amount to every cell edge it crosses. The edges with high load are the routes. A
town of the ledger on a route is a **trading town** when its throughput ranks high in its region. The kind comes from where the
mode changes (break of bulk): a **port** where sea meets land (harbour), a **river port** at the head of navigation, a **caravan
town** where pack-animal routes leave farmland for desert or steppe (R§4, the Sahel towns and the Silk Road oases), a
**market town** otherwise (R§5). A town with heavy throughput of a foreign culture's goods gets a **merchant quarter** of that
people. That is the minority quarter PW-889 wanted, and it is also Curtin's trade diaspora (R§5), and it makes the border
friction of step 2 cheaper next century.

**Reads:** step 2's flows and paths, the settlement ledger. **Writes:** `trade.json` routes (per era: a list of polylines with
load and leading good class), hub towns (site id, kind, throughput, leading goods, merchant quarters), and a per-cell `trade_load`
layer per frame. **Cost:** path tracing is cheap (seconds). **Judged by:** route and hub counts per continent against the review's
cases (one or a few trunk routes per landmass per era, not a mesh); ports at harbours and caravan towns at desert edges (a check
on the site factors); the nudge test on the route set; and a screenshot review.
**Daniel sees:** on the globe, an Overlays > **Trade routes** box. Lines are drawn wider by load and coloured by leading good
class (food, salt, metal, precious), with the existing time slider. Hub towns get a ring, and the hover card says "river port
of the X: salt down, grain up, merchants of the Y". A deep link `?trade=routes` works as the mines one does.

## Step 4: effects (each its own small piece)

- **4a. Culinary brief** (the end goal, PW-692). The cuisine sheet's staple, drink and fuel lines read the imports:
  wine where the vine doesn't grow but is bought in, a pepper note, salt fish inland, grain eaten by herders, tea along a tea-road.
  This replaces the brief's `trade_reach: null`, closes most of PW-744 and PW-805, and gives PW-984 (food words travel) its
  route: the word for a bought-in food comes from the giver's language along the path. PW-912 (crops spread by trade) is the
  same path with a lag.
- **4b. Spread along routes.** `trade_of(line)` (D53: openness as the stand-in) becomes the culture's measured trade intensity:
  its route load per head, normalised over the world. Arm C's trade-contact speed applies where a route crosses the border, not
  wherever both sides know towns. Faith conversion gets a route weight, the way Islam travelled the trans-Saharan routes (R§4).
  This changes techtree outputs, so it is behind a switch first, as the D52 arms were.
- **4c. Wealth for polities.** A seat's strength (polities `MIL_X` x settled people) gets a trade-wealth term from the throughput
  of its hub towns, and the hemmed-in state gate gets a trade route path (Uruk, R§3: states founding outposts to get what
  their plain lacked). It is behind a switch, judged against the existing state-lifetime and polity-count checks (PW-1447, PW-1449).
- **4d. Feedback into the history** (decision D-T1): the dwarven hold's food (PW-1371) and the foragers' farm food (PW-1405/1406)
  read the step-2 food flows instead of their placeholders. This means the history reads trade during the run, which is the
  only step that does. It needs the goods and cost walk inside the history's step at frame cadence. That is a real cost and a
  stability risk, so it goes last.

## What it does not do (yet)

No prices or money amounts. Money (`commodity_money`, `coinage`) only lowers the friction between strangers and lets markets
form. No individual merchants or ships. No trade wars or blockades beyond "war closes the border". No fantasy transport beyond
the body plans (see D-T3).

## Open calls (inbox drafts)

- **D-T1** readout only, or feed trade back into the history (densities, holds, foragers)? Lean A: readout for steps 1-4c;
  4d later.
- **D-T2** the unit of trade: cultures, cells, or towns? Lean B: cell graph for goods and costs, summed to cultures for the
  sheets; towns only as hubs.
- **D-T3** how fantasy peoples trade: flyers, sea peoples, dragons, underground kinds. Lean: through their body plans and
  the existing goods, with dragons taking tribute, not trading.

## Implementation tickets (inbox drafts, parent PW-1498)

1. Step 1 goods ledger (`planet/lineages/trade.py::goods`, trade_goods.json, brief "has / lacks" line, globe goods layer). m.
2. Step 2 exchange (cost graph by mode and era generalising `salt_reach`, flows, Trade tab). l.
3. Step 3 routes and hubs (paths, hub kinds, merchant quarters, Overlays > Trade routes). m.
4. Step 4a culinary brief imports (bought-in foods in the cuisine sheet; brief `trade_reach` filled). m.
4b, 4c and 4d are filed after step 3 has numbers. They depend on what the route loads look like.
