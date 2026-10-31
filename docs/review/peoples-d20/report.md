# Peoples D20: founding, the contest, density (lane 83)

Owner ruling D20, staged; branch `worktree-agent-a6d3459a485a8bc68`. Lane 84's diagnosis (PW-1202 to PW-1207,
docs/review/peoples-why/report.md on main) arrived mid-lane and reshaped stage 3.

## In plain words

- **Stage 1 (rulings 1–3).** A new people starts at one spot and spreads from there. When a stem people ends, its land lies empty.
  Where two peoples share land, the one the land suits better presses harder, and a specialist presses harder than a generalist.
  On its own, stage 1 did not shrink the humans (dnd, one try each: 65/62/73% before, 76/77/64% after). Elves and dwarves grew
  about ×3, but the kobolds collapsed: they start at one spot, often on a poor landmass they can't leave (see "Kobolds" below).
- **Stage 2 (rulings 4–5).** Each people's number per km² comes from its way of life, with a source. Foragers: 0.3 (Binford's 339
  hunter-gatherer societies). Elves: 4. Dwarves: 7–8. Kobolds and goblins live in dens in broken country. Dwarves and hobgoblins
  contest land 1.5× as hard. Elves rose to 5–10%, hobgoblins to 6–14%, and humans to 52/76/69%.
- **Stage 3 (lane 84's findings).** A people's ways of life (farmers, herders, seafarers...) now share one claim on the land instead of
  stacking about 1.3× on it. And a farming people lives at forager density until it has crops (PW-1205 A, PW-1203 A). Humans:
  **37/64/58%** (base 65/62/73). Elves 8–15%, dwarves 0.3–3%. Continents led by a people other than humans: 1/2/8 of 10
  (base 4/2/1).
- **Not done:** soft share bands (stage 6). Humans are not yet near your 24–28%, but the levers above aren't settled (the kobolds,
  the boats), so bands would paper over them. Also not done: PW-1202 A and B. B is close to a rule you turned down; see the drafts.

## How it was measured

- Stress suite (lane 77, `tools/peoples_robust.py`), one try per variant, on worlds 4360a3 and af2677. Base is main at e03eb572 with
  the "range" arm. The tables below are one try each, so a single seed moves by several points. Judge the direction across seeds, not
  one cell.
- The dnd drives: as `planet lineages 4360a3 --tree dnd.toml` (default tries), seeds 7, 10 and 13.
- Bloc measures (lane 84's, PW-1202): continents of 1+ Mkm², the number human-led, the median count of peoples making 90% of a
  continent's people, and the people-weighted distance of a continent's mix from the world's. Lane 84's base: 6–9 of 10 human-led,
  median 2, distance 0.25–0.35. The suite reports n90 and distance from stage 3 on.

## dnd drives (as the CLI)

| stage | seed | human | elf | dwarf | halfling | gnome | kobold | goblin | hobgoblin | orc | dragonborn | kenku | tabaxi | blocs: human-led / median n90 / mix distance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base | 7 | 70 | 0.34 | 0.13 | 6.8 | 2.5 | 6.6 | 0.12 | 1.4 | 1 | 3.9 | 5.2 | 0.93 | 9 of 10 / - / - |
| base | 10 | 62 | 0.43 | 0.19 | 10 | 3.9 | 9.2 | 0.16 | 1.1 | 1.7 | 3.1 | 6 | 0.75 | 8 of 10 / - / - |
| base | 13 | 67 | 0.26 | 0.6 | 14 | 2.2 | 5.8 | 0.48 | 2 | 0.8 | 1.5 | 3.5 | 0.86 | 9 of 10 / - / - |
| s1 | 7 | 73 | 1.6 | 0.32 | 6.3 | 5.7 | 0.16 | 0.6 | 3.1 | 1.8 | 0.44 | 2.1 | 2.5 | 8 of 9 / - / - |
| s1 | 10 | 55 | 2.8 | 1.1 | 0.89 | 13 | 0.19 | 0.84 | 4.3 | 2.3 | 6.3 | 3.2 | 4.7 | 6 of 10 / - / - |
| s1 | 13 | 83 | 1.1 | 0.25 | 3.5 | 3 | 0.045 | 0.86 | 3 | 1.2 | 0.3 | 0.4 | 1.6 | 10 of 10 / - / - |

## Every stage, one try each (suite runs; blocs: landmasses / led by a non-human / humans under 50% / leaders)

| run | dir | human | elf | dwarf | halfling | gnome | kobold | goblin | dragonborn | kenku | hobgoblin | orc | top | blocs: n / non-human-led / humans<50% / leaders |
| dnd-s10@4360a3 | suite-base | 62 | 0.43 | 0.19 | 10 | 3.9 | 9.2 | 0.16 | 3.1 | 6 | 1.1 | 1.7 | human 62 | 10 / 2 / 4 / dragonborn,human,kobold |
| dnd-s10@4360a3 | suite-s1 | 77 | 1.5 | 0.73 | 3.7 | 2.4 | 0.47 | 0.34 | 2.6 | 1.2 | 2.9 | 2.1 | human 77 | 10 / 0 / 2 / human |
| dnd-s10@4360a3 | suite-s2 | 76 | 6.2 | 0.6 | 4.1 | 2.5 | 0.24 | 0.095 | 2 | 0.08 | 6 | 0.88 | human 76 | 10 / 0 / 1 / human |
| dnd-s10@4360a3 | scr-s3 | 64 | 9.5 | 0.82 | 5.3 | 4.8 | 0.34 | 0.13 | 2.8 | 0.11 | 8.4 | 2 | human 64 | 9 / 1 / 2 / hobgoblin,human |
| dnd-s13@4360a3 | suite-base | 73 | 0.39 | 0.15 | 0.54 | 5.7 | 8.8 | 0.17 | 2.3 | 4.1 | 1.9 | 1.2 | human 73 | 10 / 1 / 1 / gnome,human |
| dnd-s13@4360a3 | suite-s1 | 64 | 1.8 | 0.11 | 0.52 | 17 | 0.83 | 0.76 | 0.13 | 3.4 | 4.4 | 1.2 | human 64 | 10 / 1 / 3 / gnome,human |
| dnd-s13@4360a3 | suite-s2 | 69 | 4.8 | 0.2 | 0.5 | 8.8 | 3.6 | 0.12 | 1.8 | 0.74 | 8.2 | 0.52 | human 69 | 10 / 3 / 3 / gnome,hobgoblin,human |
| dnd-s13@4360a3 | scr-s3 | 58 | 7.6 | 0.29 | 0.71 | 10 | 5 | 0.18 | 2.6 | 1.1 | 10 | 0.6 | human 58 | 10 / 2 / 2 / gnome,hobgoblin,human |
| dnd-s7@4360a3 | suite-base | 65 | 0.53 | 0.21 | 0.62 | 5.6 | 11 | 0.17 | 4.2 | 7.2 | 1.7 | 1.5 | human 65 | 10 / 4 / 4 / dragonborn,gnome,human,kobold |
| dnd-s7@4360a3 | suite-s1 | 76 | 1.6 | 0.59 | 5.1 | 4.6 | 0.15 | 0.45 | 0.31 | 2.7 | 2.3 | 2 | human 76 | 10 / 1 / 2 / gnome,human |
| dnd-s7@4360a3 | suite-s2 | 52 | 10 | 3.8 | 2.3 | 5.4 | 1.8 | 0.25 | 0.6 | 1.2 | 14 | 4.8 | human 52 | 10 / 7 / 8 / aarakocra,elf,gnome,hobgoblin,human,orc,sea_elf |
| dnd-s7@4360a3 | scr-s3 | 37 | 15 | 3 | 3 | 7.2 | 2.4 | 0.33 | 1.7 | 1.7 | 19 | 5.3 | human 37 | 10 / 8 / 8 / aarakocra,elf,gnome,hobgoblin,human,orc,triton |
| dnd-sites1-s7@4360a3 | suite-base | 73 | 0.27 | 0.19 | 0.59 | 1 | 10 | 0.33 | 3.7 | 6.5 | 1.7 | 1.6 | human 73 | 10 / 2 / 2 / human,kobold |
| dnd-sites3-s7@4360a3 | suite-base | 70 | 0.42 | 0.19 | 0.58 | 4.1 | 10 | 0.16 | 3.8 | 6.1 | 1.7 | 1.5 | human 70 | 10 / 3 / 3 / dragonborn,human,kobold |
| dnd3-s10@4360a3 | suite-base | 79 |  |  |  |  | 21 | 0.16 |  |  |  |  | human 79 | 9 / 2 / 2 / human,kobold |
| dnd3-s10@4360a3 | scr-s3 | 99 |  |  |  |  | 0.24 | 0.54 |  |  |  |  | human 99 | 10 / 0 / 0 / human |
| dnd3-s7@4360a3 | suite-base | 82 |  |  |  |  | 17 | 0.42 |  |  |  |  | human 82 | 10 / 2 / 2 / human,kobold |
| dnd3-s7@4360a3 | suite-s1 | 98 |  |  |  |  | 0.69 | 1.5 |  |  |  |  | human 98 | 10 / 0 / 0 / human |
| dnd3-s7@4360a3 | scr-s3 | 99 |  |  |  |  | 0.34 | 1 |  |  |  |  | human 99 | 10 / 0 / 0 / human |
| dnd5-s10@4360a3 | suite-base | 84 | 1.3 | 0.95 | 13 |  |  |  |  |  |  | 0.72 | human 84 | 10 / 0 / 0 / human |
| dnd5-s10@4360a3 | scr-s3 | 72 | 19 | 5.7 | 2.4 |  |  |  |  |  |  | 0.85 | human 72 | 10 / 1 / 1 / elf,human |
| dnd5-s7@4360a3 | suite-base | 79 | 1.2 | 0.84 | 18 |  |  |  |  |  |  | 0.62 | human 79 | 10 / 0 / 0 / human |
| dnd5-s7@4360a3 | suite-s1 | 73 | 1.4 | 1.1 | 24 |  |  |  |  |  |  | 0.93 | human 73 | 10 / 1 / 1 / halfling,human |
| dnd5-s7@4360a3 | scr-s3 | 56 | 9.5 | 3.1 | 31 |  |  |  |  |  |  | 0.67 | human 56 | 10 / 2 / 3 / elf,halfling,human |
| sm-s10@4360a3 | suite-base | 53 | 0.076 | 0.089 | 11 | 0.043 | 4.9 | 0.54 | 3.2 |  | 2.2 | 0.55 | human 53 | 10 / 1 / 2 / half_orc,human |
| sm-s10@4360a3 | suite-s1 | 49 | 0.2 | 0.2 | 4.4 | 0.24 | 0.036 | 1.2 | 2.2 |  | 2.7 | 1.8 | human 49 | 10 / 3 / 4 / aarakocra,half_orc,human |
| sm-s10@4360a3 | suite-s2 | 49 | 0.2 | 0.2 | 4.4 | 0.24 | 0.036 | 1.2 | 2.2 |  | 2.7 | 1.8 | human 49 | 10 / 3 / 4 / aarakocra,half_orc,human |
| sm-s13@4360a3 | suite-base | 62 | 0.12 | 0.094 | 6.2 | 0.025 | 5.7 | 0.35 | 4.1 |  | 1.7 | 0.42 | human 62 | 10 / 1 / 2 / human,kobold |
| sm-s13@4360a3 | suite-s1 | 68 | 0.4 | 0.44 | 2.2 | 0.26 | 0.31 | 0.44 | 2.4 |  | 0.97 | 0.59 | human 68 | 10 / 1 / 2 / cervid_folk,human |
| sm-s13@4360a3 | suite-s2 | 68 | 0.4 | 0.44 | 2.2 | 0.26 | 0.31 | 0.44 | 2.4 |  | 0.97 | 0.59 | human 68 | 10 / 1 / 2 / cervid_folk,human |
| sm-s7@4360a3 | suite-base | 56 | 0.081 | 0.089 | 8.3 | 0.04 | 5.4 | 0.061 | 2.1 |  | 2.8 | 0.47 | human 56 | 10 / 1 / 2 / human,kobold |
| sm-s7@4360a3 | suite-s1 | 41 | 0.075 | 0.12 | 0.29 | 1.3 | 0.12 | 2.7 | 6 |  | 3.5 | 0.8 | human 41 | 9 / 6 / 6 / cervid_folk,dragonborn,half_orc,human,lizardfolk |
| sm-s7@4360a3 | suite-s2 | 41 | 0.075 | 0.12 | 0.29 | 1.3 | 0.12 | 2.7 | 6 |  | 3.5 | 0.8 | human 41 | 9 / 6 / 6 / cervid_folk,dragonborn,half_orc,human,lizardfolk |

(suite-base: main; suite-s1: stage 1; suite-s2: stages 1–2; scr-s3: stages 1–3. dnd3 is humans, goblins and kobolds; dnd5 is humans,
elves, dwarves, halflings and orcs; sm is the Seven Meals tree, which stage 2's densities don't touch.)

## What each stage changed in the code

- **Stage 1.** Fit-weighted load (`competition._fit_w`): weight = clip(S_j/S_k, 1/3, 3), S = fit × breadth^−½ × contest. Fit is
  the habitat before goods, herds and crops, with learned country in; breadth is the fit's sum. Lane 84 found a bare K ratio inert
  (PW-1204), so the breadth cost is the part that bites: a people with a quarter of a rival's breadth presses 2× as hard.
  - One-spot founding is the only founding (polycentric founding and the stem's takeover are removed). A stem ends only at its last
    split, and its land passes to no one (`_end_parent`).
  - A split whose parent is gone founds by the parent's last land (`_last_held`, `_origin_fallback(near=...)`).
  - Density left the contest: INVADE and DENSITY_PUSH are removed.
- **Stage 2.** `contest` is a tree field (default 1; the trait "martial" gives 1.5) and "denning" is a new trait. The densities, in
  `samples/dnd.toml`, each carry a source or a "judgement" note.
- **Stage 3.** Kin (a people and its groups) feel each other in full, before any edge (`competition._compete`'s `qk`, `model._kin`).
  The farming era sets density (`growth.ERA_DENSITY`). The suite adds n90 and mix distance, and judges brittleness on the swing within
  one world and one family (PW-1207).

## Kobolds

The kobolds are a split of the dragon stem, which is megafauna with a worldwide range. With one-spot founding they start on one
landmass. On 4360a3 seed 7 that landmass has 334 of their 2004 good cells, while the best landmass has 867. They stay at 96–152 cells
for 150 kyr with no rival anywhere, because they can't cross the sea (sea_share 0.02 and explore 0.3, from the dragons). Then the humans
take most of what they hold. Before, they inherited every scattered piece of the dragons' range. Hence dnd3 is now 99% human.
Draft: `draft-peoples-split-of-a-megafauna-stem-strands.md` (lean: draw such a split's landmass by its own country).

## Open judgement calls (drafts in issue-tracking/inbox/)

- `draft-peoples-fit-contest-knobs.md`: FIT_CLIP 3, BREADTH_Q 0.5, martial 1.5.
- `draft-peoples-dnd-density-judgements.md`: halflings, gnomes, hobgoblins, dragonborn and fisher folk, whose numbers have no
  source; hobgoblins now 2.6–19%.
- `draft-peoples-split-of-a-megafauna-stem-strands.md`: the kobolds.
- `draft-peoples-blocs-incumbency-vs-surge.md`: PW-1202 B against your "surge stays".
- `draft-seven-meals-density-by-way.md`: the same density rule for Seven Meals.

## Still running when this was written

The full stress suite of stage 3 (88 variants, both worlds) and of base was still running at about 13 min per variant with the box at
load 60. So were the stage-3 dnd drives. Their tables, with the invariants, the per-world swings and the blocs, go in
docs/review/peoples-d20/suite-s3.md once they finish (`tools/peoples_robust.py report --out <dir>`). See handoff.md.
