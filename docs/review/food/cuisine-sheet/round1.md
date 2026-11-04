# Cuisine sheet, round 1 (PW-1391, PW-1312, PW-834, PW-793, PW-1372)

Lane 164, 2026-11-03. Code: `planet/lineages/cuisine.py` (new), `brief.build(..., culture=ID)`, `/api/brief?culture=`,
`planet brief RUN --culture ID`, the brief panel in `viewer/globe/colours.js`. Tests: `tests/test_cuisine.py`.

## In plain words

The culinary brief can now be asked for one **culture** at one era, not only for a whole people. It opens with a short
**cuisine sheet** that answers culinary-dnd's questions for that culture: what it burns, what its staple is, what it drinks,
who eats together, what outsiders get wrong about it, and what it won't eat (its own taboos and its gods'). Every line comes
from one simple rule over what the run already holds, so nudging the run moves a line, never the whole sheet; the culinary
side overrules any of it. Nothing was re-run: the sheet is a read-out of existing runs.

**How Daniel opens it:** Globe, pick a peoples run, open a people in the Peoples panel and press *Culinary brief…* (or open
the panel from any people). A new second drop-down next to the people lists that people's cultures alive at the era shown,
largest first ("whole people" gives the old brief). Pick a culture; type an era in *kyr ago* and press *Show* to read it then
(the culture stays picked if it was alive then; a merged culture shows its heir).

Dairy fixes in the same lane: lactase alone no longer gives a people dairy herds (PW-834); a culture milks only if it herds,
knows milking, keeps a dairy animal and its body milks, so Seven Meals' antelope- and cervid-kin never milk (PW-793, already
in the preset; the sheet honours it); and a herding culture's lactase rises with its years of dairying, so humans who herd
get fresh milk again without an authored number (PW-1372, a placeholder shape).

## The rules (all JUDGEMENT, none claims a real-world number)

| question | rule | reads |
|---|---|---|
| Fuel | the commonest fuel on the culture's land at the era, and how it cooks | fuels.py via the brief (`_fuels`; the era's frame inside the land-use window, else the present) |
| Staple | in the order of its ways of life: staple crops known on its land if it farms (>= 10% of heads), its herd animals if it herds, fish or game if it lives by the wild; an obligate carnivore eats no grain; forbidden foods are left out | ladder farm/herd shares (meta.eraq, heads-weighted over its cells), crop_known / animal_known, techtree, taboos.json |
| Drink | water (scarce in a desert); milk only where it dairies, fresh if its lactase share >= 0.6 else soured; beer and wine from the grain and fruit it farms once it knows fermentation; spirits once it distils; infusions from tea and cacao | dairy rule, techtree known with dates, crops known |
| Who eats together | the main way of life sets the everyday group (forager camp shares the kill; herding household eats from one pot; farming household at its own hearth); cities add cookshops, towns market days; feasting known adds feasts; its own kinship, rank and purity taboos add who may not eat with whom | ladder shares, the settlement ledger (its people's places on its cells), techtree, taboos.json (clan_exogamy, caste_eat, chief_house, chief_food, motherinlaw, fatherinlaw, menses_kitchen, rank_endogamy) |
| What outsiders get wrong | up to three contrasts with its neighbouring cultures (sharing or bordering its cells; peoples of the land before dragons and giants): a taboo on something a neighbour eats, milk drunk or not, a body that tastes differently, a way of life read as poverty, a different fire | the same profile for each neighbour |
| Won't eat | its food taboos, split into its faith's (a god's domain) and its own (purity, identity, symbolic) | taboos.json (present-day), gods.json faiths |

Dragons and giants (the counted megafauna, or a kind with an empty density ladder) do not take the farms and herds of the peoples
under them: they live by hunting and taking (or by their own herds, where the tree says they herd), and eat in small households.

## One sheet per preset (pasted from the runs, read-only)

**D&D, run a2b637** (the only D&D run that parses on today's code), culture 61, present:

```
## Cuisine sheet: first orcs of the north of Tobrosal (orcs), 0 kyr ago

- Fuel: dung (then coal): low slow fires: boiling, stewing and baking in embers
- Staple: wheat and barley, maize, potatoes and other cool tubers (78% of the people farm); the meat and milk of horses, sheep and goats, cattle (17% herd) (never wild swine, hares: a taboo)
- Drink: water; soured and fermented milk (yogurt-, kefir-, kumis-like), not fresh of horses, sheep and goats, cattle; no beer or wine yet (the people does not know fermentation)
- Who eats together: each household eats at its own hearth; the village eats together at harvest and festivals; in their 3 cities many eat bought food: cookshops and stalls feed those without a hearth; they hold feasts: food given away in quantity is how standing is made
- What outsiders get wrong: a guest from humans of the south-west of Tobrosal who brings wild swine gives offence: the first orcs of the north of Tobrosal do not eat it (it belongs to the hunt domain of god of hunt and fertility); first hobgoblins of Tobrosal, who do not milk, take the first orcs of the north of Tobrosal's soured milk for spoiled food; to them it is the everyday food; first hobgoblins of Tobrosal, who cook over coal, expect long hot fires; the first orcs of the north of Tobrosal cook over dung (low slow fires)
- Won't eat:
  - wild swine (everyone; of the faith, the sky faith of first orcs of the north of Tobrosal: it belongs to the hunt domain of god of hunt and fertility)
  - carrion birds (priests; of the faith, the sky faith of first orcs of the north of Tobrosal: it belongs to the death domain of power of smithing)
  - hares (everyone; purity: unclean: chews like a cud-eater but has no split hoof)
- Ways of life: farm 0.776, herd 0.17, wild 0.054; faith: the sky faith of first orcs of the north of Tobrosal
- Neighbours compared: first hobgoblins of Tobrosal (hobgoblin, culture 80), first leonin of Tobrosal (leonin, culture 16), humans of the south-west of Tobrosal (human, culture 293), tritons of the west of Tobrosal (triton, culture 561)
```

**Seven Meals, run 3c1caf** (the showcase; made before the density ladder, see below), culture 475, present:

```
## Cuisine sheet: antelope-kin of the west of Hizam (antelope-kin), 0 kyr ago

- Fuel: wood (then dung, grass): open flame: roasting, grilling, smoking
- Staple: foxtail millet, lentils and peas, wheat and barley (79% of the people farm); fish and shore food and gathered plants (15% live by the wild) (never wild swine, frogs and newts: a taboo)
- Drink: water; barley beer; rye and oat beer; cider and fruit wine; spirits distilled from the beer and wine
- Who eats together: each household eats at its own hearth; the village eats together at harvest and festivals; they hold feasts: food given away in quantity is how standing is made
- What outsiders get wrong: a guest from humans of the west of Hizam who brings wild swine gives offence: the antelope-kin of the west of Hizam do not eat it (it belongs to the hunt domain of god of hunt and fertility); first hobgoblins of the west of Hizam, who cook over dung, expect low slow fires; the antelope-kin of the west of Hizam cook over wood (open flame)
- Won't eat:
  - wild swine (everyone; of its gods: it belongs to the hunt domain of god of hunt and fertility)
  - frogs and newts (everyone; purity: unclean: lives both in the water and on the land)
- Ways of life: farm 0.787, herd 0.067, wild 0.146
- Neighbours compared: humans of the west of Hizam (3) (human, culture 608), humans of the west of Hizam (human, culture 426), first hobgoblins of the west of Hizam (hobgoblin, culture 216), half-orcs of the west of Hizam (half_orc, culture 792)
```

No milk in the antelope-kin's drink: they do not milk (PW-793). At 3 kyr ago the same culture farms only foxtail millet, drinks
millet beer, and has 4 towns with market days.

## What is weak (honest list)

- **D&D drinks no beer:** in a2b637 no people ever learns fermentation, so every D&D sheet says "no beer or wine yet". The sheet
  is right about the run; the run looks wrong (inbox draft).
- **Farming with no crop:** a quarter of a2b637's farmed cells have no growable crop in `crop_known`; such a culture's staple
  reads "farmed food ... which crop is not known here" (inbox draft).
- **The showcase runs are pre-ladder:** b4d502, a24559 and 3c1caf no longer parse with today's spec, so the whole-people brief fails
  on them in the viewer; the culture sheet works because it does not parse the tree. On 3c1caf the ways of life still come from the
  stored land-use shares, and the faith names are missing (its gods.json predates faiths), so taboos read "of its gods" (inbox draft:
  re-run the showcases).
- **Taboos are present-day:** taboos.json is written for living cultures at the present, so an earlier era shows today's taboos, and
  a culture gone by the present shows none.
- **Long names:** culture names are long ("first orcs of the north of Tobrosal"), so the outsiders line is wordy. Names wait for
  the names pass (PW-972).
- The ways-of-life shares are the cell's shares of all heads, weighted by heads, so a culture sharing cells with a bigger farming
  people reads that people's farming. Good enough for a sheet; a per-people ladder layer would fix it.
- Not done from PW-1312: taboo targets from the run's real fisheries and game (point 2), the dog as a culture's taboo (point 3),
  Douglas 1966 from a read copy (point 4). The sheet does drop forbidden foods from the staple and herd lists (point 1).

## Stale samples

The brief_version 7 samples in `docs/review/lineages/showcase-peoples/briefs/9a2aae/` were deleted: their run predates peoples
without groups and no longer parses. The two sheets above are the new samples; regenerate any with
`planet brief RUN --culture ID [--era KYR]`.
