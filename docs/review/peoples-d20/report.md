# Peoples D20: founding, the contest, density (lanes 83 and 83b)

Owner ruling D20, staged; branch `worktree-agent-a6d3459a485a8bc68`. Lane 84's diagnosis (PW-1202 to PW-1207,
docs/review/peoples-why/report.md on main) arrived mid-lane and reshaped stage 3.

## Lane 83b: the kobolds and small trees

### In plain words

- **The kobolds are back** in the full dnd tree: 1.3/2.8/4.3% on seeds 7/10/13 (base 11/9.2/8.8; stage 3 2.4/0.34/5). Across the
  14 dnd runs of the suite they hold 0.45–11%. Four general rules did it, none of them a kobold setting:
  - A people that splits from a megafauna stem (the kobolds and dragonborn, from the dragons) starts where its own country lies, not
    where the dragons' worldwide range happens to draw it.
  - Such a people no longer takes the dragons' numbers for exploring and staying home: those are for solitary fliers.
  - Land that only dragons or giants hold counts as free country for a people's pioneers and long jumps. Before, a dragon's range
    barred them, and dragons are in most mountains.
  - A people that has filled its land sends founders out, as a crowded people does. Before, only crowding by rivals did. So the
    kobolds, alone on their patch of broken country, never left it.
- **Humans:** 61/64/56% on dnd seeds 7/10/13 (base 65/62/73). Over all 7 dnd runs on 4360a3 the median is 59% (base 70); on af2677,
  33% (base 44). Continents led by a people other than humans: 2/2/3 of about 10 (base 4/2/1).
- **The three-people tree (humans, goblins, kobolds) is still ~98% human.** That can't go back to its base of 79–82%, and it shouldn't.
  The base kobolds held 77 Mkm², the dragons' whole range, inherited. Their denning country (your "dense but narrow") is about 17–24
  Mkm² of good land worldwide. At 4 /km², against humans at 10 over ~100 Mkm², all of it would still leave humans near 90%. What's left
  is a draw: on 4360a3 seed 7 the kobolds start on a landmass with a fifth of their country, much of it already held by the archaic
  humans. They can't sail, so they stay there at 0.4%. Draft: `draft-peoples-split-of-a-megafauna-stem-strands.md` (lean: accept).
- **The five-people tree was not a regression.** Humans went down, not up: 60/72% on 4360a3 (base 79/84). But one try on af2677,
  seed 7, has humans at 2.6% and elves at 60%. That comes from the fourth rule: the archaic stem now jumps, so the humans are born
  in another place. Without that rule the same try has humans at 61%, but then the kobolds fall back under 1% in two of three dnd
  seeds. Draft: `draft-peoples-jump-push-moves-cradles.md`.
- **Brittle peoples.** In the full dnd tree, on 4360a3, the stage 3 code's worst per-world swings were dwarves 10×, kenku 15×, orcs 9×,
  goblins 6× and kobolds 27×. Now they are 1.4×, 14×, 4.6×, 2.8× and 25×; gnomes went from 7× to 15×. Against main's base, more peoples
  are brittle (10 in dnd, against 5). That is the cost of D20's one-spot founding: where a people starts decides its fate.
- **Lost:** half-orcs were never born in one Seven Meals run (af2677, seed 13). They are a mixed people of humans and orcs, and those
  two never met there. Draft: `draft-seven-meals-half-orcs-unborn.md`.

### Suite, final code against base (one try per variant; median share %, range over runs)

The full tables are in suite-final.md and suite-base.md (base: main e03eb572, reported with this branch's tool). "Non-human-led" counts
landmasses of 1+ Mkm². n90 is the median number of peoples making 90% of a landmass's people. Mix distance is the people-weighted
distance of a landmass's mix from the world's. Both are new since stage 3, so the base has none (lane 84 measured base: median n90 2,
distance 0.25–0.35).

**dnd** (median share %, range over runs; n runs)

| world | suite | n | human | elf | dwarf | halfling | gnome | kobold | goblin | hobgoblin | orc | dragonborn | kenku | non-human-led landmasses (median of n) | humans <50% | median n90 | mix distance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4360a3 | base | 7 | 70 (62-74) | 0.39 (0.34-0.53) | 0.15 (0.14-0.21) | 5.2 (0.54-10) | 3.9 (1.6-5.7) | 8.8 (5-11) | 0.17 (0.14-0.18) | 1.7 (1.1-3.6) | 1.5 (0.81-1.7) | 2.3 (1.1-4.2) | 4.9 (3-7.2) | 1 of 10 | 2 | - | - |
| 4360a3 | final | 7 | 59 (46-64) | 8.2 (5.1-12) | 0.79 (0.73-1) | 0.97 (0.72-12) | 2.4 (0.69-10) | 4 (0.45-11) | 0.13 (0.085-0.24) | 11 (7.7-19) | 1.3 (0.78-3.6) | 3.1 (2-5.9) | 1.1 (0.093-1.3) | 2 of 10 | 3 | 2 | 0.40 |
| af2677 | base | 7 | 44 (38-65) | 0.49 (0.35-0.62) | 1.7 (0.8-2.8) | 8.9 (0.017-10) | 10 (7.2-11) | 9.4 (2.9-12) | 1.6 (0.97-6.6) | 9.4 (0.032-13) | 1.6 (0.79-2.6) | 6.3 (4.5-7.3) | 6.2 (5.4-8) | 3 of 6 | 4 | - | - |
| af2677 | final | 7 | 33 (12-46) | 9 (6-10) | 2.4 (0.3-4.7) | 21 (0.042-31) | 13 (3-31) | 2.1 (1.4-5.8) | 0.2 (0.0053-0.55) | 6.6 (0.13-29) | 1.3 (0.93-4.6) | 6 (3.4-19) | 0.72 (0.36-0.93) | 4 of 6 | 4 | 3.0 | 0.42 |

**seven_meals** (median share %, range over runs; n runs)

| world | suite | n | human | half_orc | halfling | kobold | dragonborn | goblin | hobgoblin | cervid_folk | lizardfolk | non-human-led landmasses (median of n) | humans <50% | median n90 | mix distance |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4360a3 | base | 5 | 56 (53-68) | 18 (12-20) | 8.7 (6.2-12) | 4.9 (0.038-5.7) | 3.2 (1.6-4.1) | 0.19 (0.061-0.54) | 2 (1.2-2.8) | 3.2 (1.2-4.1) | 0.18 (0.085-0.83) | 1 of 10 | 2 | - | - |
| 4360a3 | final | 5 | 31 (15-37) | 29 (24-38) | 6.1 (1.1-11) | 4 (0.55-5.9) | 6.8 (3-9) | 1.5 (0.49-3.2) | 3.9 (3.4-6.6) | 4.6 (3.7-14) | 4.9 (3.7-8) | 5 of 9 | 7 | 3 | 0.39 |
| af2677 | base | 5 | 53 (52-55) | 15 (14-15) | 14 (11-16) | 4.7 (3.4-6) | 1.8 (1.3-2.4) | 0.65 (0.4-1.2) | 3.5 (3.1-3.6) | 2.9 (2.5-4.2) | 0.84 (0.22-1) | 2 of 6 | 2 | - | - |
| af2677 | final | 5 | 22 (9.8-32) | 19 (0-24) | 17 (3.5-31) | 1.2 (0.49-2.5) | 4.7 (4.3-6.5) | 4.4 (2.8-6.1) | 10 (5.3-16) | 3.2 (2-21) | 4.6 (3.8-13) | 5 of 6 | 6 | 3.0 | 0.28 |

**dnd5** (median share %, range over runs; n runs)

| world | suite | n | human | elf | dwarf | halfling | orc | non-human-led landmasses (median of n) | humans <50% | median n90 | mix distance |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4360a3 | base | 2 | 82 (79-84) | 1.3 (1.2-1.3) | 0.9 (0.84-0.95) | 15 (13-18) | 0.67 (0.62-0.72) | 0 of 10 | 0 | - | - |
| 4360a3 | final | 2 | 66 (60-72) | 19 (19-20) | 4.2 (2.8-5.7) | 9.2 (0.78-18) | 1 (0.76-1.3) | 3 of 10 | 3 | 1.0 | 0.31 |
| af2677 | base | 2 | 73 (70-76) | 0.53 (0.34-0.71) | 0.46 (0.12-0.81) | 25 (23-27) | 1 (1-1) | 0 of 6 | 0 | - | - |
| af2677 | final | 2 | 30 (2.6-57) | 35 (10-60) | 8.1 (0.88-15) | 16 (1.3-30) | 11 (1.7-20) | 3.5 of 6 | 3.5 | 2.0 | 0.20 |

**dnd3** (median share %, range over runs; n runs)

| world | suite | n | human | kobold | goblin | non-human-led landmasses (median of n) | humans <50% | median n90 | mix distance |
|---|---|---|---|---|---|---|---|---|---|
| 4360a3 | base | 2 | 81 (79-82) | 19 (17-21) | 0.29 (0.16-0.42) | 2 of 9.5 | 2 | - | - |
| 4360a3 | final | 2 | 99 (98-99) | 0.89 (0.42-1.4) | 0.6 (0.47-0.73) | 0 of 10 | 0 | 1.0 | 0.02 |
| af2677 | base | 2 | 65 (58-72) | 35 (28-42) | 0.026 (0.024-0.028) | 3.5 of 6 | 3.5 | - | - |
| af2677 | final | 2 | 89 (79-98) | 11 (1.8-21) | 0.013 (0.011-0.016) | 0 of 5.5 | 0 | 1 | 0.10 |

Invariants (82 runs counted): base 3 fail (five_peoples 86% human, late_humans 85–86% human), final 4 fail (dnd3 98–99% human
three times, half-orcs never born once). No crashes.

Swing within one world and family (the brittleness measure, PW-1207), dnd on 4360a3, seeds and jitter:

| people (dnd, 4360a3, 7 runs each) | base: min–max % (swing) | stage 3 | final |
|---|---|---|---|
| human | 62–74 (1.2×) | 37–77 (2.1×) | 46–64 (1.4×) |
| elf | 0.34–0.53 (1.6×) | 4.9–15 (3.1×) | 5.1–12 (2.4×) |
| dwarf | 0.14–0.21 (1.4×) | 0.29–3 (10×) | 0.73–1 (1.4×) |
| halfling | 0.54–10 (19×) | 0.71–8.9 (12×) | 0.72–12 (17×) |
| gnome | 1.6–5.7 (3.5×) | 1.4–10 (7.4×) | 0.69–10 (15×) |
| kobold | 5–11 (2.1×) | 0.19–5 (27×) | 0.45–11 (25×) |
| goblin | 0.14–0.18 (1.3×) | 0.056–0.33 (5.8×) | 0.085–0.24 (2.8×) |
| hobgoblin | 1.1–3.6 (3.2×) | 7.4–19 (2.5×) | 7.7–19 (2.5×) |
| orc | 0.81–1.7 (2.1×) | 0.6–5.3 (8.8×) | 0.78–3.6 (4.6×) |
| dragonborn | 1.1–4.2 (3.8×) | 0.58–2.8 (4.9×) | 2–5.9 (2.9×) |
| kenku | 3–7.2 (2.4×) | 0.11–1.7 (15×) | 0.093–1.3 (14×) |
| tabaxi | 0.73–1 (1.4×) | 0.4–1.6 (3.9×) | 0.58–1.1 (1.8×) |

### dnd per seed (suite variants dnd-s7/10/13)

| run | dir | human | elf | dwarf | halfling | gnome | kobold | goblin | dragonborn | kenku | hobgoblin | orc | top | blocs: n / non-human-led / humans<50% / leaders |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dnd-s10@4360a3 | base | 62 | 0.43 | 0.19 | 10 | 3.9 | 9.2 | 0.16 | 3.1 | 6 | 1.1 | 1.7 | human 62 | 10 / 2 / 4 / dragonborn,human,kobold |
| dnd-s10@4360a3 | final | 64 | 8 | 0.91 | 4.7 | 1.1 | 2.8 | 0.15 | 5.9 | 0.75 | 7.8 | 1.4 | human 64 | 9 / 2 / 2 / dragonborn,hobgoblin,human |
| dnd-s10@af2677 | base | 39 | 0.62 | 1.1 | 9.7 | 10 | 9.4 | 0.97 | 7.2 | 7.3 | 9.4 | 2.6 | human 39 | 6 / 2 / 3 / dragonborn,hobgoblin,human |
| dnd-s10@af2677 | final | 20 | 9.5 | 4.2 | 23 | 3 | 1.5 | 0.21 | 3.4 | 0.71 | 29 | 2.9 | hobgoblin 29 | 6 / 5 / 5 / dragonborn,halfling,hobgoblin,human,orc |
| dnd-s13@4360a3 | base | 73 | 0.39 | 0.15 | 0.54 | 5.7 | 8.8 | 0.17 | 2.3 | 4.1 | 1.9 | 1.2 | human 73 | 10 / 1 / 1 / gnome,human |
| dnd-s13@4360a3 | final | 56 | 8 | 0.75 | 4.4 | 10 | 4.3 | 0.13 | 2.5 | 0.093 | 10 | 0.79 | human 56 | 10 / 3 / 3 / gnome,hobgoblin,human,kobold |
| dnd-s13@af2677 | base | 47 | 0.51 | 0.8 | 10 | 7.2 | 11 | 1.3 | 5.9 | 5.4 | 7.3 | 1.1 | human 47 | 6 / 2 / 4 / halfling,human,kobold |
| dnd-s13@af2677 | final | 37 | 10 | 1.3 | 22 | 14 | 5.1 | 0.2 | 6 | 0.73 | 0.14 | 1.2 | human 37 | 6 / 5 / 5 / dragonborn,firbolg,gnome,halfling,human |
| dnd-s7@4360a3 | base | 65 | 0.53 | 0.21 | 0.62 | 5.6 | 11 | 0.17 | 4.2 | 7.2 | 1.7 | 1.5 | human 65 | 10 / 4 / 4 / dragonborn,gnome,human,kobold |
| dnd-s7@4360a3 | final | 61 | 8.2 | 1 | 0.85 | 3.7 | 1.3 | 0.2 | 3.1 | 1.2 | 15 | 1.2 | human 61 | 10 / 2 / 4 / dragonborn,hobgoblin,human |
| dnd-s7@af2677 | base | 65 | 0.48 | 1.4 | 0.017 | 11 | 8.2 | 1.2 | 4.5 | 5.6 | 0.032 | 0.97 | human 65 | 6 / 3 / 3 / gnome,human,kobold |
| dnd-s7@af2677 | final | 20 | 6 | 2.8 | 14 | 12 | 2.8 | 0.55 | 6.9 | 0.93 | 26 | 4.6 | hobgoblin 26 | 6 / 4 / 4 / gnome,hobgoblin,human,kobold |
| dnd3-s10@4360a3 | base | 79 |  |  |  |  | 21 | 0.16 |  |  |  |  | human 79 | 9 / 2 / 2 / human,kobold |
| dnd3-s10@4360a3 | final | 98 |  |  |  |  | 1.4 | 0.47 |  |  |  |  | human 98 | 10 / 0 / 0 / human |
| dnd3-s10@af2677 | base | 58 |  |  |  |  | 42 | 0.028 |  |  |  |  | human 58 | 6 / 4 / 4 / human,kobold |
| dnd3-s10@af2677 | final | 79 |  |  |  |  | 21 | 0.011 |  |  |  |  | human 79 | 5 / 0 / 0 / human |
| dnd3-s7@4360a3 | base | 82 |  |  |  |  | 17 | 0.42 |  |  |  |  | human 82 | 10 / 2 / 2 / human,kobold |
| dnd3-s7@4360a3 | final | 99 |  |  |  |  | 0.42 | 0.73 |  |  |  |  | human 99 | 10 / 0 / 0 / human |
| dnd3-s7@af2677 | base | 72 |  |  |  |  | 28 | 0.024 |  |  |  |  | human 72 | 6 / 3 / 3 / human,kobold |
| dnd3-s7@af2677 | final | 98 |  |  |  |  | 1.8 | 0.016 |  |  |  |  | human 98 | 6 / 0 / 0 / human |
| dnd5-s10@4360a3 | base | 84 | 1.3 | 0.95 | 13 |  |  |  |  |  |  | 0.72 | human 84 | 10 / 0 / 0 / human |
| dnd5-s10@4360a3 | final | 72 | 20 | 5.7 | 0.78 |  |  |  |  |  |  | 1.3 | human 72 | 10 / 3 / 3 / elf,human |
| dnd5-s10@af2677 | base | 70 | 0.71 | 0.81 | 27 |  |  |  |  |  |  | 1 | human 70 | 6 / 0 / 0 / human |
| dnd5-s10@af2677 | final | 57 | 10 | 0.88 | 30 |  |  |  |  |  |  | 1.7 | human 57 | 6 / 1 / 1 / elf,human |
| dnd5-s7@4360a3 | base | 79 | 1.2 | 0.84 | 18 |  |  |  |  |  |  | 0.62 | human 79 | 10 / 0 / 0 / human |
| dnd5-s7@4360a3 | final | 60 | 19 | 2.8 | 18 |  |  |  |  |  |  | 0.76 | human 60 | 10 / 3 / 3 / elf,human |
| dnd5-s7@af2677 | base | 76 | 0.34 | 0.12 | 23 |  |  |  |  |  |  | 1 | human 76 | 6 / 0 / 0 / human |
| dnd5-s7@af2677 | final | 2.6 | 60 | 15 | 1.3 |  |  |  |  |  |  | 20 | elf 60 | 6 / 6 / 6 / elf,orc |

(blocs: landmasses / led by a non-human people / humans under 50% / leaders.)

## Lane 83: stages 1–3

### In plain words

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

## Kobolds (lane 83's diagnosis; fixed in lane 83b, above)

The kobolds are a split of the dragon stem, which is megafauna with a worldwide range. With one-spot founding they start on one
landmass. On 4360a3 seed 7 that landmass has 334 of their 2004 good cells, while the best landmass has 867. They stay at 96–152 cells
for 150 kyr with no rival anywhere, because they can't cross the sea (sea_share 0.02, and explore 0.3 from the dragons). Then the humans
take most of what they hold. Before, they inherited every scattered piece of the dragons' range. Lane 83b found two more locks: their
jumps went only by crowding (they were never crowded on their own patch), and their pioneers counted dragon-held cells as taken.

## Open judgement calls (drafts in issue-tracking/inbox/)

- `draft-peoples-fit-contest-knobs.md`: FIT_CLIP 3, BREADTH_Q 0.5, martial 1.5.
- `draft-peoples-dnd-density-judgements.md`: halflings, gnomes, hobgoblins, dragonborn and fisher folk, whose numbers have no
  source; hobgoblins now 0.13–29% (median 9.1%) over the suite's dnd runs.
- `draft-peoples-split-of-a-megafauna-stem-strands.md`: the kobolds that still strand (lane 83b rewrote it).
- `draft-peoples-jump-push-moves-cradles.md` (lane 83b): a stem's jumps move where its splits are born; one dnd5 try has humans at 2.6%.
- `draft-seven-meals-half-orcs-unborn.md` (lane 83b): half-orcs never born in one Seven Meals run.
- `draft-peoples-blocs-incumbency-vs-surge.md`: PW-1202 B against your "surge stays".
- `draft-seven-meals-density-by-way.md`: the same density rule for Seven Meals.

## The stage-3 suite

Lane 83b stopped it after 26 of 86 variants, once its own code changes made it stale. Its finished dnd runs are in the brittleness
comparison above. The full suite on the final code is suite-final.md; main's is suite-base.md.
