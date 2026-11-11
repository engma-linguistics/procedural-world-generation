# Flavour profile and food keeping per culture (lane 308)

Two new parts of a culture's cuisine sheet (`planet/lineages/keeping.py`, called from `cuisine.sheet`; brief version 25):

- **Keeping food** (preservation, ferments): which of ten methods a culture uses (drying, smoking, salting and brining, pickling, fermenting milk,
  fermenting grain and fruit, fermenting fish, fermenting vegetables/roots/meat, cellaring and freezing, rendering fat), roughly how much of
  all its food each keeps, and which methods it does not know yet.
- **Flavour**: ten axes, 0 to 1 (salty, sour, savoury/umami, fatty, hot and pungent, smoky, sweet, bitter, funky/fermented, herbal), each with
  its reasons, and a one-line descriptor such as "funky, sour and savoury: a wet-coast brewing-and-raw-food kitchen".

Every weight is an invented judgement, not fitted to a real cuisine and not tuned to any run. Seven Meals was not tuned to: the
"other" run below is a Seven Meals run, read as it came out.

## How it is derived (mechanisms, no per-people fixes)

Each method's weight multiplies four things, and each one shows up as a "because" line:

1. **Technique.** The run's tech tree gates a method: `smoking_drying`; `salting`, `solar_salt` or `salt_mining`; `pickling` or `vinegar`;
   `fermented_dairy`, `cheese` or `fermentation`; `fish_sauce`; `cellaring`, `ice_house` or `storage`; `lard_rendering` or `ghee_butter`.
   If the tree has the tech and the people doesn't know it, the method is listed as "not yet". A tree without that tech doesn't gate it.
2. **Environment.**
   - Lean season: frost months, or months without growth.
   - Aridity (B Köppen share) and damp (precipitation).
   - Cold (coldest month).
   - Salt reach (share of land within 100 km of salt, sea salt, salt mines).
   - The everyday fuel's smoke. Peat smokes best and wood well. Dung barely smokes: culinary-dnd's steppe orcs have "Dung fire → no
     roasting, no smoking". An oil lamp gives no smoke.
3. **What there is to keep.**
   - Farmed grain and garden vegetables (not for a carnivore).
   - Herds, dairy and its lactase share (low lactase means milk is soured).
   - Fish: coast, river runs and lakes.
   - Sea mammals.
   - Fruit and sugar crops.
4. **Body and traits** (spec body keys, so they work on any tree):
   - No fire: no smoking; drying and fermentation take its place.
   - Raw meat: aged meat.
   - Raw meat plus a low bitter sense ("strong stomachs"): strong ferments, and the "raw-food" tag in the descriptor.
   - No sweet sense: fruit goes to vinegar; sweet is 0.
   - No capsaicin pain: chili counts as sweet, not hot.
   - Salt craving: more salting.
   - A den or tunnel people: the ground is its cellar.

How much of all food is kept at all: 8% plus 4.5% per lean month, plus 15% if it farms grain and up to 10% if it herds, plus 5% in a dry land.
That is cut by 30% for foragers outside the cold, and capped at 75%. A people that knows none of the keeping techs eats fresh, with 0%
kept. On these runs that is every dragon culture (sapient hunters off the density ladder).

The viewer's Culinary brief tab, with a culture picked, shows a "Flavour" table and a "Keeping food" table under the sheet. Each row has
its "why" column and a hover. The same lines are in the brief's Markdown, and in its JSON as `cuisine.preservation` and `cuisine.flavour`.

## Coverage on two finished runs

| run | tree | living cultures | with a profile | eat fresh (no keeping techs) |
|---|---|---|---|---|
| a2b637 | D&D peoples (preset) on world dba204 | 273 | 273 | 30 (all dragon cultures) |
| de1cc6 | Seven Meals on world 2762ba | 218 | 218 | 29 (all dragon cultures) |

Leading taste across cultures:

- a2b637: salty 95, fatty 38, smoky 38, umami 32, hot 18, sour 16, sweet 15, herbal 9, funk 6, bitter 6
- de1cc6: salty 68, fatty 42, umami 32, sweet 19, funk 16, sour 15, smoky 13, hot 7, herbal 3, bitter 3

Salty leads most often. Any culture with salt nearby and salting known gets a salty base, and many cultures are coastal. That is a
plausible shape, but it is the first weight to revisit if the profiles feel samey.

## Ten sample cultures (present day)

Inputs are the culture's own land at the present: Köppen, coldest month, frost months, rain, the lead fuels, salt reach, coast fish, ways of
life, dairy and crops. Outputs are the kept share with the top methods (shares of *all* food), and the four strongest tastes with the
descriptor.

| # | run | culture (people) | inputs | kept share and methods | flavour (top axes) and descriptor |
|---|---|---|---|---|---|
| 1 | a2b637 | first goblins of the east of Tobrosal (culture 67, goblin) | Am 68%, Af 29%; coldest month 20.794 C, ~0.0 frost months, 2384 mm; fuel coal 51%, wood 41%; salt within 100 km 0.733; coast fish 0.342; farm 0.735 herd 0.106 wild 0.159; dairy horse/caprine/cattle (lactase 0.11); crops roots, maize, banana, peanut, cane, sweet_potato | ~24% kept: fermenting grain and fruit 7%, fermenting vegetables, roots and meat 6%, fermenting milk 4%, cellaring and freezing 4%; not yet: salting, pickling, fish_sauce | sweet 0.56, funk 0.52, fatty 0.43, bitter 0.34. *sweet, funky and fatty: a tropical farming brewing-and-raw-food kitchen* |
| 2 | a2b637 | steppe orcs of the west of Huramom (culture 268, orc) | BSh 100%; coldest month 12.843 C, ~0.0 frost months, 330 mm; fuel dung 100%; salt within 100 km 1.0; coast fish 0.139; farm 0.855 herd 0.145 wild 0.0; dairy horse/caprine (lactase 0.14); crops wheat, olive, pseudograin, beans, greens, maize | ~56% kept: drying 13%, fermenting grain and fruit 11%, pickling 10%, fermenting milk 7% | salty 0.86, sour 0.72, funk 0.46, fatty 0.43. *salty, sour and funky: a dry farming drying-and-brewing kitchen* |
| 3 | a2b637 | steppe dwarves of Simath, founded 18,000 years ago (culture 457, dwarf) | BSk 72%, BWk 28%; coldest month -2.681 C, ~2.2 frost months, 215 mm; fuel grass 93%, drift 7%; salt within 100 km 0.345; coast fish 0.469; farm 0.991 herd 0.0 wild 0.009; no dairy | ~54% kept: drying 14%, cellaring and freezing 12%, fermenting grain and fruit 11%, rendering fat 5% | salty 0.57, fatty 0.35, bitter 0.3, umami 0.26. *salty, fatty and bitter: a dry farming drying-and-cellar kitchen* |
| 4 | a2b637 | tortles of the south of Kobuth (culture 224, tortle) | Cfa 48%, BSh 42%; coldest month 15.166 C, ~0.0 frost months, 589 mm; fuel drift 80%, coal 20%; salt within 100 km 1.0; coast fish 0.331; farm 0.97 herd 0.012 wild 0.018; no dairy; crops foxtail_millet, oil_seeds | ~29% kept: drying 7%, fermenting grain and fruit 7%, salting and brining 6%, fermenting fish 6% | salty 0.84, umami 0.4, fatty 0.33, funk 0.33. *salty, savoury and fatty: a temperate-coast drying-and-brewing kitchen* |
| 5 | a2b637 | first silver dragons of the west of Simath (culture 56, silver_dragon) | Cwa 19%, BSk 16%; coldest month -1.452 C, ~1.9 frost months, 1000 mm; fuel wood 47%, grass 22%; salt within 100 km 0.139; coast fish 0.589; farm 0.0 herd 0.0 wild 1.0; no dairy; crops pulses, squash, wheat, vine, beans, potato | ~0% kept: none; not yet: drying, smoking, salting, pickling, ferment_dairy, ferment_grain, fish_sauce, ferment_veg, cellaring, rendering | fatty 0.4, umami 0.3, smoky 0.24, herbal 0.15. *fatty, savoury and smoky: a temperate-coast fresh-food kitchen* |
| 6 | de1cc6 | Laaulaah (culture 114, goblin) | Cwa 79%, Cfa 12%; coldest month 14.965 C, ~0.0 frost months, 1713 mm; fuel grass 40%, peat 37%; salt within 100 km 0.31; coast fish 0.6; farm 0.786 herd 0.186 wild 0.028; dairy caprine (lactase 0.13); crops cane, wheat, squash, rice, beans, foxtail_millet | ~36% kept: fermenting grain and fruit 12%, fermenting vegetables, roots and meat 10%, fermenting milk 8%, drying 3%; not yet: salting, pickling, fish_sauce | funk 0.72, sour 0.57, umami 0.33, sweet 0.32. *funky, sour and savoury: a wet-coast brewing-and-raw-food kitchen* |
| 7 | de1cc6 | Sigbtaluu (culture 182, antelope_folk) | Dwa 100%; coldest month -1.617 C, ~1.8 frost months, 1186 mm; fuel dung 56%, peat 26%; salt within 100 km 0.0; coast fish None; farm 0.653 herd 0.347 wild 0.0; no dairy; crops foxtail_millet, wheat, tree_fruit | ~47% kept: fermenting grain and fruit 18%, cellaring and freezing 10%, rendering fat 6%, smoking 5% | sour 0.35, fatty 0.35, smoky 0.29, salty 0.22. *sour, fatty and smoky: a temperate farming brewing-and-cellar kitchen* |
| 8 | de1cc6 | Nuuoyimaa (culture 77, frost_giant) | Dfc 79%, Dwc 8%; coldest month -25.539 C, ~7.6 frost months, 214 mm; fuel dung 38%, heath 38%; salt within 100 km 0.738; coast fish 0.163; farm 0.0 herd 0.0 wild 1.0; no dairy | ~56% kept: salting and brining 12%, rendering fat 12%, drying 9%, fermenting fish 6% | fatty 1.0, salty 0.85, umami 0.67, funk 0.34. *fatty, salty and savoury: a cold river-and-lake salting-and-rendering kitchen* |
| 9 | de1cc6 | Ino (culture 235, lizardfolk) | BWk 92%, BWh 8%; coldest month 5.231 C, ~0.0 frost months, 121 mm; fuel dung 63%, coal 26%; salt within 100 km 0.051; coast fish 0.537; farm 0.991 herd 0.002 wild 0.007; no dairy; crops foxtail_millet, wheat, date_palm | ~60% kept: drying 31%, fermenting grain and fruit 9%, fermenting vegetables, roots and meat 5%, rendering fat 4% | umami 0.5, funk 0.4, sweet 0.32, fatty 0.31. *savoury, funky and sweet: a dry-coast drying-and-brewing kitchen* |
| 10 | de1cc6 | Noaghguf (culture 285, leonin) | Cfa 62%, Cwa 38%; coldest month 23.276 C, ~0.0 frost months, 1317 mm; fuel dung 86%, oil 10%; salt within 100 km 1.0; coast fish 0.542; farm 0.869 herd 0.12 wild 0.011; dairy horse/caprine (lactase 0.01); crops wheat, rice, banana, foxtail_millet, pulses, cane | ~12% kept: salting and brining 3%, fermenting milk 2%, fermenting fish 2%, fermenting grain and fruit 1% | salty 0.72, umami 0.41, herbal 0.35, sour 0.31. *salty, savoury and herbal: a wet-coast salting-and-soured-milk kitchen* |

## Checked against Daniel's notes (../culinary-dnd, read-only)

1. **Goblins: "fermentation and raw foods", not "eating trash".**
   - Notes: the bitter-manioc chain of "grating, pressing, leaching, fermenting, heating" (docs/02-fact-sheets-east-and-south.md:202),
     "Masticated-starch fermentation (chicha mechanism)" and "Nose-to-tail thrift" (:206). The slander "Goblins eat poison and garbage"
     (:216) is what outsiders get wrong.
   - Model: the D&D tree gives goblinoids `raw_meat = true, bitter = "low"` ("scavengers with strong stomachs"), and that body alone turns
     on the leaning. No line names goblins.
   - Seven Meals Laaulaah (row 6): funky 0.72 is its top taste. Its kept food is all ferments: grain and fruit 12%, roots, greens and meat
     10%, milk 8%. Descriptor: "funky, sour and savoury: a wet-coast brewing-and-raw-food kitchen".
   - D&D east-Tobrosal goblins (row 1): two ferments lead their keeping. Funky (0.52) is second only to sweet (0.56), which comes from the
     cane, banana and sweet potato on their land.
   - **Matches in mechanism.** The leaching/detox chain only shows as a reason line ("bitter roots made safe by leaching and souring"). The
     tree's `plant_detox` tech counts only when the people knows it.
2. **Steppe orcs: dung fire, no smoking; dairy soured "by necessity".**
   - Notes: "Dung fire → no roasting, no smoking"; adults digest fresh milk badly, so they are a fermentation culture (master reference:87).
     They "dry curd to rock hardness" (01-fact-sheets:13).
   - Model, D&D steppe orcs of west Huramom (row 2), on 100% dung fuel:
     - Smoky is 0.10, level "none". Smoking isn't among its methods because its weight falls below the floor.
     - Drying leads at 13%, because of a 100% steppe land ("sun and wind dry meat, fruit and curd").
     - Milk is soured (lactase 0.14). Sour is 0.72.
   - **Matches.** This culture farms more than the notes' herding Arha (farm 0.86), so grain ferments and pickles stand beside the dairy.
3. **Frost giants: "Freezing and frozen aging… Fermentation by burial… Rendering"** (docs/frost-giants-fact-sheet.md:54-56). Fuel is fat,
   oil, dung and bone.
   - Model, Seven Meals Nuuoyimaa (row 8): coldest month -25.5 C and ~7.6 frost months.
   - Of all food, it keeps: salting 12%, rendering 12%, frost-drying 9%, fish ferments 7%, cellaring and freezing 6%, buried and soured
     ferments 5%. Fatty is 1.0.
   - **Partly matches.** Rendering and the cold ("frost-drying in the wind", "the winter is the freezer") are there. Burial fermentation
     comes out small, because a hunting people with no garden has little to put in crocks. Salting ranks first because of the salt springs
     on its land, which the notes don't mention.

## Not done here

- The kind leanings come only from the body keys a tree already has (fire, raw_meat, bitter, sweet, capsaicin, salt, diet) and from traits.
  A preset can't yet author a leaning directly, such as the notes' elves who age "on scales nobody else can attempt", or halflings whose
  "preservation is short-horizon". There is an inbox draft for this. (Lane 309: done, the body key `keeping`; see below.)
- PW-1441 (no D&D people knows fermentation) does not show on a2b637 with today's code. Only 30 of its 273 living cultures read "no beer
  or wine yet", and 243 have at least one ferment among their keeping methods. The 30 are the dragon cultures, which know none of the
  keeping techs. One run isn't the "two or three D&D runs" that ticket asks for.


# Lane 309: the kitchen through time, bought-in food, authored leanings (PW-1714, PW-1727, PW-1728)

## Kitchen through time (PW-1714; `planet/lineages/kitchen_time.py`)

A culture's cuisine sheet now carries `through_time`. The brief reads every stored frame from the culture's founding to the era asked
(at most 60, thinned evenly; inside the land-use window a frame each 500 years). At each frame it reads the same things the sheet reads,
on that frame's land: crops and herds known there, ways of life, lead fuel, dairy, bought-in food, and the flavour profile (keeping.py on
that frame's land, salt, fish, fuels and trade). Keeping methods are dated by its people's tech dates (meta.techtree.known), with whom
they were taken from. A change is listed when it holds two frames running (three for the lead fuel and the two leading tastes, which flip
at near-ties). A crop that was on the culture's land before its people knew it reads "another people's, on its land". The viewer's
Culinary brief tab shows a "Kitchen through time" table under Keeping food, with a small grid of the ten tastes frame by frame (darker is
stronger, hover for the date and descriptor). The brief's Markdown has the same lines. Building it adds about 5 to 17 s to a culture's
brief at L7.

Three samples (present day; all lines are the run's, unedited):

- a2b637 (D&D), culture 268, steppe orcs of the west of Huramom: first seen 50,000 years ago as foragers eating fresh; 34,500 drying and
  smoking known (from storm giants); 7,000 takes up herding (93%), the kitchen turns fatty and salty; 6,900 fermenting milk known (from
  humans); 6,400 salting known (worked out by its own people); 5,000 sheep and goats arrive, takes up farming (81%), milks its herds, makes
  cheese, cooks mostly on dung (was drift), the kitchen turns salty and sour; 4,500 pickling; 4,000 wheat and barley (another people's,
  on its land); 3,500 horses arrive, grain bought in from orcs of Huramom; 3,000 fermenting fish known (from tritons); 2,500 grain no
  longer bought in; 1,500 to 500 olives, quinoa, beans, greens, maize, peanuts, tree fruit arrive.
- de1cc6 (Seven Meals), culture 114, Laaulaah (goblin): founded 216,000 years ago; 38,500 drying and smoking (from lizardfolk); 12,000
  fermenting roots and meat (from hill giants) and cellaring; 11,000 takes up farming (81%), salt fish bought in; 10,000 sugar cane
  arrives (its people had tamed it ~12,000 years ago); 9,500 fermenting milk and grain (from hobgoblins); 8,000 sheep and goats; 6,500
  wheat and barley, cooks mostly on dung, the kitchen turns funky and sour (was smoky and herbal); 4,500 salt bought in from Ansiwuḷu;
  3,500 milks its herds, makes cheese; 2,500 beans and rice arrive, salt fish no longer bought in.
- de1cc6, culture 182, Sigbtaluu (antelope folk): 37,000 drying and smoking; 11,000 sheep and goats; 10,500 takes up herding (96%),
  the kitchen turns smoky and fatty; 8,800 fermenting milk, grain and roots (from elves); 8,000 takes up farming (59%); 6,600 salting
  (from tortles); 6,000 foxtail millet arrives, grain bought in; 5,000 horses; 3,500 wheat and barley; present, tree fruit arrives, cooks
  mostly on dung (was peat), the kitchen turns sour and fatty.

Limits: the tech dates are its people's (the whole kind's), not the culture's own; the era picker, conquest doublets and the culture's
own calendar for the step dates (the ticket's other parts) are not in this lane. The brief's dates do follow a chosen calendar.

## Bought-in food in the profile (PW-1727)

keeping.inputs now reads the sheet's own "Bought in" line (brief.trade_reach, bought_in.py): trade only (tribute is not bought), from 1%
of the culture's people supplied and with a giver named. Bought salt raises the salt reach by 2.5x its share, to at most 0.8 (bought salt
is never as cheap as one's own); that moves salting, pickling and the salty axis. Bought spice adds heat (pepper, chili), bitterness (tea,
cacao) or sweetness (vanilla, or chili for a people that feels no capsaicin), by what the givers' fields grow. Bought sugar adds
sweetness, bought oil fat (wine alone adds none), bought salt fish savouriness. Each adds `base + 2.5 x share` up to a cap (heat 0.5,
sweet 0.4, fat 0.3, savoury 0.3). All of these are JUDGEMENT. Each comes with a reason, e.g. "salt far on its own land, but salt bought
in from first hill giants of Ratal (10% of its people supplied)".

At the present, over all living cultures:

| run | living | buys salt | buys spice | profile changed | salting share changed | two leading tastes changed |
|---|---|---|---|---|---|---|
| a2b637 | 273 | 37 | 43 | 114 | 35 | 45 |
| de1cc6 | 218 | 23 | 39 | 95 | 20 | 49 |

Examples: a2b637 goliaths of the west of Simath (culture 446), salty 0.16 -> 0.37 and salting 1.4% -> 3.1% of all food, hot 0 -> 0.21
from pepper bought from humans of the south-west of Tobrosal; de1cc6 Lin̆yei (aarakocra, culture 429), salty 0.04 -> 0.43, salt from
Luazsiw by river (21%), the descriptor "funky, sour and bitter" becomes "sour, salty and funky".

## Authored keeping leanings (PW-1728)

The tree's body key `keeping` (spec.parse_keeping; documented in the dnd.toml header and docs/proposals/lineages.md): keeping method ->
multiplier 0..5, `kept` (how much of all food is kept) and `why`. Applied after the tech gates (a leaning never teaches a tech), with
an "authored for this kind" reason; 0 lists the method as "never done by this kind". Merged key by key down the tree. The workbench body
editor has a "keeping leanings" field. The D&D preset sets, from culinary-dnd's fact sheets:

- elves: kept x1.25, cellaring x1.6, grain and fruit ferments x1.4, crocks x1.3 ("ageing and fermentation on scales nobody else can
  attempt; great cellars of wine aged for decades");
- halflings: kept x0.6, cellaring x0.6, salting x0.7 ("preservation is short-horizon, kept for next week, not next year");
- dragonborn: smoking 0 ("straw and crop-residue fire, fast and hot; steaming and wok cooking").

Seven Meals is frozen and does not set it.

On a fresh D&D run with these leanings (run 12face, world dba204, one try, made under lane 309; scratch, since deleted), at the present,
the mean over the living cultures of each kind, with the leaning and with it removed (same land, same everything else):

| kind | cultures | kept share | cellaring (share of all food) | smoking (share of all food) | cultures that smoke |
|---|---|---|---|---|---|
| elves | 9 | 0.358 (0.286 without) | 0.048 (0.03) | 0.041 (0.04) | 9 (9) |
| halflings | 1 | 0.15 (0.25) | 0 (0) | 0.009 (0.014) | 1 (1) |
| dragonborn | 25 | 0.427 (0.427) | 0.024 (0.023) | 0 (0.016) | 0 (23) |
| humans (no leaning) | 36 | 0.424 | 0.012 | 0.022 | 36 |

Elves keep more and ferment and cellar more; the one living halfling culture keeps 15% of its food, not 25%; no dragonborn culture
smokes ("never done by this kind" in its not-yet list). Elves still smoke: their notes say wood is "abundant, indifferently used", so no
leaning was set there. Halflings are one culture on this run, so their row is a single case.
