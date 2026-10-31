---
title: "In hunters' country dragons lose their food, not their lives: is the peoples' share of the wild herds overstated?"
type: task
status: needs-decision
parent: null
milestone: v2
subsystem: timezoom
effort: m
impact: high
found_by: fun-lane-63
blocked_by: []
relates: [PW-1068, PW-1020, PW-977, PW-967, PW-990]
refs: [planet/lineages/history/megafauna.py, planet/lineages/prey.py, planet/lineages/samples/dnd.toml, docs/review/megafauna/dragon-density/index.html]
---

## Description
**In plain words.** After PW-1068, early peoples hardly hunt dragons themselves. Even so, where hunting peoples live 25,000 years
ago, dragons are still only a few percent as many as in empty land. The cause is the dragons' food. The peoples eat the same wild
herds the dragons live on, and in the model they eat most of them. This happens three ways:
1. The D&D hunting peoples are 10 to 100 times denser than real hunter-gatherers.
2. Every tonne of game they eat comes out of the dragons' own cattle-sized prey.
3. Wherever they live, the wild herds are cut by 60% for good ("overkill").

The owner's worry is the outcome. It reads as the same "too fatal" problem the persecution fix was meant to solve. This ticket asks
which of the three to soften. Nothing was changed in lane 63: none of the three is a plain bug, and each is a judgement.

**How big each part is.** These figures come from the off arm of r3 (world 2a7385, roll 7000), where the peoples neither kill dragons
nor overkill the herds.
- In hunters' country the peoples take 80-84% of the wild herds' yearly surplus, at 25 kyr, 10 kyr and the present. That leaves the
  dragons 3% of the supply, against 16% in empty land.
- So, even before overkill and persecution, dragons in hunters' country have about a fifth of the food they would have alone.
- This hunting is in every arm, including "pressure off". So the paper's "% of pressure-off" figures do not count it; they count
  persecution and overkill on top of it.
- Overkill then cuts the herds to 40%. The peoples' hunt is taken first, capped at what is there. If hunters need 80% of the old
  surplus, they now take all of the 40% that is left, and the dragons' wild food is gone; only the herders' stock and the sea are
  left. That is how a 60% cut to the herds becomes a 96% cut to the dragons. The two channels compound because the hunters eat first.
- The full split by channel, era and way of life is in the dragon-density paper's results (lane 63).

**1. How dense are the hunting peoples?** The game each person needs is `megafauna.meat_need`: half their food as wild game
(`WILD_MEAT` 0.5; UNVERIFIED round number), about 0.32 t of live prey a year. At the dnd sample's densities (people per km2 of full
habitat, before PW-1020's productivity factor), the game they need in t/km2/yr is:

| people | way of life | density | game needed |
|---|---|---|---|
| halflings | forager | 12 | 3.9 |
| gnomes | half forager | 12 | 2.1 |
| goblins | forager | 5 | 1.6 |
| hobgoblins | forager | 4 | 1.3 |
| lizardfolk, tabaxi | forager | 1.5 | 0.48 |
| human arctic hunters | forager | 0.3 | 0.10 |

Real hunter-gatherers are much thinner on the ground:
- Hamilton et al. 2007 (PNAS 104:4765, Table 1, p. 4767): their fit implies 0.03-0.09 per km2 for groups of 25-1000.
- Zhu et al. 2021 (Nat Ecol Evol 5:1536, author manuscript PMC7611941, read as HTML 10-30, no page numbers):
  - their model's mean density is 0.19 per km2 where gathering dominates (hunted food < 40%) and 0.04 per km2 where hunting dominates
    (Fig. 5 caption);
  - the lowest density ever recorded is 0.002 per km2 (Methods);
  - their observed maximum and median are in figures I did not read (UNVERIFIED).
- Tallavaara et al. 2018 (PNAS 115:1232, PMC5819417, read as HTML): density levels off above about 1,360 g/m2/yr of productivity
  (Fig. 2A). Their maximum and median are not given in the text (UNVERIFIED).

So the D&D foragers sit 10-100 times above real ones. That is a fantasy choice: the owner set gnomes at 12 on 10-27. But real
hunters this dense would not live mainly on big game. Zhu's central finding is that a meat-heavy diet goes with low density ("high
fractions of meat in the diet, leading to greatly reduced population density due to trophic inefficiency", Abstract). Their
model's meat share is 55% where hunting dominates and 22% where gathering dominates (Fig. 5 caption). Dense peoples that eat half
their food as big game are the combination real data rule out.

**2. Does the peoples' hunt take the dragons' prey tonne for tonne?** Yes. In `budget` the peoples' game need is taken first and
in full from the same pool (`OFFTAKE` x the wild herds, the cattle-sized herbivores the dragons eat), capped at what is there. Real
hunters take much small and medium game (deer, pigs, hares, birds) that a 3 t dragon would not live on. No share for this is on file.

**3. Does Sandom's overkill fit here?** `prey.OVERKILL` 0.6 cuts the wild herds by 60% wherever small folk press the land fully.
The pressure is 1 - exp(-N / 0.05), so 0.3 people per km2 already counts as nearly full pressure. Sandom et al. 2014 (Proc R Soc B
281:20133254, Fig. 3 p. 5, p. 6, on file) differs from this in three ways:
- (a) It counts the share of big-mammal species lost, not biomass.
- (b) The loss depends on how long the fauna had lived beside hominins: a median of about 0.46 where modern humans were the first
  to arrive, about 0.23 where archaic hominins came before, and near 0 in Africa (at most 13%).
- (c) On this world the peoples evolved in place beside the herds, so Africa is the closer analogue, not first contact. 0.6 is above
  even the first-contact median.

**4. Could dragons press back on the peoples? (owner 10-30, D16: later, not built.)** The idea: dragons prey on small folk, which
keeps the peoples thinner, so game stays plentiful. A subagent searched for evidence that big predators have held human numbers down,
and found none. It read Packer et al. 2005, Hill et al. 2007 and the worldwide review in full; the Sundarbans paper in abstract only:
- Packer et al. 2005 (Nature 436:927, full text):
  - lions "have killed more than 563 Tanzanians since 1990", about 38 a year across the country (our arithmetic);
  - attacks were highest where natural prey was scarce and bush pigs were common, with "no additional effect of human population
    density";
  - attacks rose as the human population grew.
- Hill, Hurtado & Walker 2007 (J Hum Evol 52:443, full text): among Hiwi foragers "no predation deaths were reported despite ... the
  presence of jaguars in the area".
- Bangladesh Sundarbans tigers (Barlow et al., abstract only; which of their papers is UNVERIFIED): "1 396 human deaths were recorded
  over 63 years, or an average of 22 human deaths/year".
- A worldwide review (PMC9888692, full text): 5,440 attacks on people recorded, 1950-2019; no rates and no claim of a limit.
- Treves & Naughton-Treves 1999, Brain 1981 ("The Hunters or the Hunted?") and Hart & Sussman ("Man the Hunted"): not read
  (UNVERIFIED); Brain's case concerns early hominins at Swartkrans.

So the evidence read does not support predators capping human density: the kills are tens a year per region. **Pushback.** What it
does support is the reverse coupling. Big cats turn to people and their animals where wild prey runs short (Packer). That is the
model's existing livestock channel (`STOCK_TOLERABLE`), plus a plausible "dragons raid where the herds are gone". Lean: if built, make
predation on small folk a cost the peoples feel (a reason to persecute; ties to the metallic/chromatic temperament,
draft-dragon-temperament-metallic-chromatic.md), not a cap on their density.

## Options
- **A. A shared-prey share.** Only part of the peoples' game comes from the dragons' size class, e.g. 0.3 to 0.5 (a judgement, no
  source on file). It is simple and local, but it is yet another unsourced number.
- **B. Meat share falls with density, after Zhu 2021.** Thin hunting peoples eat about half their food as game; dense ones eat
  about a fifth, the rest from plants and fish (Zhu's 55% and 22% regimes). The D&D densities stay as the owner set them. Halflings
  and gnomes become gatherers and gardeners, not big-game hunters. This is sourced, and the change goes into `meat_need` alone.
- **C. Overkill follows how long the fauna has lived beside peoples (Sandom 2014).** Native peoples give the African figure (about
  0.1); peoples newly arrived from other planes or continents give the first-contact figure (about 0.46), fading as they settle in.
  This is sourced. It needs an arrival time per line in a cell, or a simpler world-wide value for native peoples.
- **D. Lower the D&D forager densities toward the real ones (0.05-0.5 per km2).** This is the most realistic option, but it
  changes how the D&D world looks, and the densities are the owner's call.
- **E. Leave it.** Dragons are rare where hunters live because the hunters eat their food. That is a defensible story, but it
  gives the 4% result the owner reads as too fatal.

**Lean: B + C.** Both rest on the papers read and keep the owner's densities. Together they should lift the dragons' share in
hunters' country by several times. Re-measure with the paired arms (`docs/review/megafauna/probe.py --no-press`) before calling
it. A stays in reserve if B + C fall short. D is the owner's call.

## Updates
