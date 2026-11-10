# Lane 264: herd animals as mounts, packs and draft (PW-1609); authored food fit (PW-1607)

Sources were fetched in this lane (WebFetch/WebSearch, 2026-11-09). Quotes are as the fetch tool relayed them. Anything not found is marked JUDGEMENT.

## 1. PW-1609: what each new herd animal now does

| animal | use | wiring (existing mechanism) | source |
|---|---|---|---|
| camel | riding | `riding` needs_any (techtree.toml) | Wikipedia, Camel train: in Alashan Mongol caravans "every man was provided with a camel to ride"; Dromedary: "prized for its capability to outrun horses in the deserts" |
| reindeer | riding, packs | `riding` needs_any; pack cost | Wikipedia, Reindeer herding (Evenki): "Deer are used for riding and transporting loads" |
| yak | riding, packs, plough | `riding` and `ox_traction` needs_any; pack cost | Wikipedia, Yak: "Yaks transport goods across mountain passes for local farmers and traders"; "They also are used to draw ploughs"; riding only from photo captions (weak: no text on ancient riding) |
| camel | caravans (reach, cost) | pack cost (`trade_flow.PACK`) | Camel train: loads "rarely exceeding 270 pounds (122.5 kg)", stages of 16-40 km, trains across the Sahara and Sahel, the Silk Road and Arabia. Bulliet (1973 Aramco World article, secondary summary seen in a search): camel transport about 20% under wagon transport in Diocletian's price edict. That is `CART / PACK` = 0.035 / 0.028 = 1.25 already in trade_flow (ORBIS: donkey or camel 0.028), so no camel cost was added |
| llama | caravans | pack cost | ethnohistoric ranges compiled at mapaspects.org (Tripcevich, Llama Caravan project; seen in a search): 15-20 km a day, 20-45 kg a head; Wikipedia, Llama: 25-30% of body weight; "the only beasts of burden" of the Inca. A llama carries a third to a quarter of a camel's load, so one PACK cost for all is generous to llama peoples (JUDGEMENT) |
| water buffalo | plough traction | `ox_traction` needs_any | Wikipedia, Water buffalo: "the ideal animals for work in the deep mud of paddy fields", "the living tractor of the East" |

Changes:
- `riding.needs_any` gains `animal_camel`, `animal_yak`, `animal_reindeer`. `ox_traction` takes `animal_cattle` out of `needs` into `needs_any` with `animal_buffalo` and `animal_yak`.
- `riding.earth_needs_any = ["animal_horse"]` (new, techtree._earth_ready): Earth's readiness date for riding stays the horse's. Without it the yak's 7.3 kyr genomic date moved riding's calibrated lag and the horse case of `test_needs_any_one_of_them` fell from 6 of 6 peoples to 2 of 6 at 12 kyr.
- `trade_flow.has_pack(know)`: a people with `pack_animals` or a camel, llama, yak or reindeer herd walks goods at the pack-animal cost (and a camel, llama, yak or reindeer people's arid-edge town is a caravan town, trade_routes). trade_flow VERSION 11.
- The horses good (trade.py) is not widened: camels, llamas, yaks and reindeer already count in the livestock good (`ast` = every herd animal but the dog), and no source was found for a camel or llama trade in the mount sense.

Measured on a fresh dnd run (lineages 56dee1 --tree dnd --tries 1, world dba204, L7, scratch data root, run e10b4b; the stored runs hold only the old five animals):
- Run animals: buffalo, camel, caprine, cattle, dog, fowl, horse, llama, pig, reindeer, yak.
- No people ends up with riding, pack animals or plough traction that it would not have on current main. Where the new herd came first it only made riding available earlier, and the people did not take it up then: the halfling and the orc (camel 3.3 and 3.4 kyr ago, horse 1.9) and the gnome and firbolg (reindeer 1.0 and 2.1, horse 0.3 and 0.4) had a mount herd 0.7-1.7 kyr before the horse, yet the halfling and orc get `riding` only at 0.3 kyr (by contact), and the gnome and firbolg never (riding needs more than a herd). Everyone else with a camel, yak or reindeer herd has the horse first. Every pack-beast people already has `pack_animals` (3.0-5.5 kyr ago) before its first beast (0.6-3.4). No people has `ox_traction` or `plough` at all on this run (cattle, but the chain stops short), so the water buffalo gain has nothing to act on.
- The wiring therefore matters on worlds where a camel, yak or reindeer people has no horse near it, and for a people that gets the herd before inventing or contacting `pack_animals`. Neither case occurs in this run. A second run was not made (a peoples run is ~45 min at L7 and needs a 4 GB parent run copied to scratch).
- Yak and reindeer riding also unlock `riding`'s dependants (cavalry techs, the horses good's need). Camel cavalry is real; yak and reindeer cavalry are not. JUDGEMENT left as is.

## 2. PW-1607: authored food fit

New body keys (spec.BODY_DEFAULT, parse_body):
- `fit`: a table food id -> `thrives | tolerates | poor | harmful`, or `{level, why}`. Wins over the derived row, its rows have `basis = "authored"`, merged key by key down the tree (a child adds to or overrides its parent's table). Food ids are food_fit.FOODS.
- `alcohol_flush`: the share (0..1) with the ALDH2*2 flush. Reads "poor" at half or more, "tolerates" below, with the share in the row. Source: Wikipedia, ALDH2: "about 50% of East Asians are heterozygous" (its lead says ~36% have no working mitochondrial isozyme, and "very few White people" carry it). The 50% threshold is a JUDGEMENT.
- `toxic = ["grapes"]`: the canid marker. A new food class "grapes and raisins" is harmful for it. Merck Veterinary Manual (seen in a search): grapes and raisins cause acute kidney failure in dogs, possibly from tartaric acid (dogs lack certain organic acid transporters); more than one per 4.5 kg of body weight may be a risk. A canid-marked body also counts as a pet-like liver (poor alcohol).
- The viewer's body editor: `fit` is a text field ("alcohol=poor, grapes=harmful"; empty inherits), `alcohol_flush` a select, grapes a toxin check box. Syntax-checked with node only, not opened in a browser.

Presets:
- dnd.toml feline stem: `fit = { alcohol = { level = "poor", why = <owner canon> } }`. Canon: culinary-dnd master reference v3 section 7 and `.claude/skills/setting-canon/SKILL.md`: "Cat peoples barely drink ... Their intoxicant is inhaled: a herb whose active compound works on the scent organ." The tabaxi and leonin inherit it. The row was already "poor" from the cat toxicity marker; now it is authored and says why. The inhaled herb and the "a third feel nothing" share have no food class here and are left to the culinary side.
- No canid people in the dnd preset: the canon cuts gnolls, so no dnd.toml people carries the grapes marker.
- seven_meals.toml untouched (frozen); `test_body_fit_parses_and_inherits` asserts that no Seven Meals line sets a fit, a flush or a canid marker.

Override examples (food_fit.fit): tabaxi alcohol -> poor, authored; a body with `alcohol_flush = 0.5` -> alcohol poor, sourced "aldh2"; a body `toxic = ["alliums", "theobromine", "grapes"]` -> "harmed by cacao, onion and garlic, grapes and raisins".

Tests: tests/test_food_fit.py (`test_authored_fit_flush_and_canid_marker`, `test_body_fit_parses_and_inherits`), tests/test_trade_flow.py (`test_camel_llama_yak_and_reindeer_herds_carry_packs`), tests/test_techtree.py (riding and ox_traction lists).
