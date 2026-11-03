# Published ranges as optional random draws (PW-1383, round 1)

Lane 145, 2026-11-03. Daniel, 11-02: "when we have ranges published can we utilize those as a (optionally) random selector for that variable?"

## In plain words

- A new setting, `meta.draw_ranges` (a tick box in the peoples workbench, `draw_ranges = false` in the dnd preset), lets a peoples run
  pick eight of the density ladder's numbers from the ranges their sources publish, instead of using the fixed value. **Off by default,
  and off it changes nothing** (same numbers to the last digit; the golden tests and the whole suite pass unchanged).
- The pick is seeded by the peoples seed (`meta.seed`): the same seed gives the same numbers every time, another seed other numbers.
  The run's `run.json` lists what it drew (`meta.range_draws`).
- Only ranges the write-ups already cite are used; the endpoints are theirs. Where a number has no published range (the forager level, the
  rich-land half point, irrigation, all the judgements) it stays fixed, and `ranges.py` says why next to each.
- Measured on 6 runs of the robust suite (3 seeds x 2 worlds): with draws on, the total number of people moves by -38% to +12%
  against the same seed with fixed values (typically within 10%), the wild-fed share by -22% to +31%, the goblins' and kobolds' ranges
  barely (kobolds) or by 0.6x to 2.8x (goblins, mostly chance: see below).

## The ranges, and where they come from

All in `planet/lineages/ranges.py` (`RANGES`; `FIXED` lists the rest). "Fixed value" is the ladder constant used when the setting is off.

| number (ladder.py) | fixed value | range drawn | draw | source (as written up in ladder.md / rich-foragers.md) |
|---|---|---|---|---|
| forager slope, `FORAGER_POW` | 1.3 | 1.26 - 1.28 | uniform | Binford 2001 Table 5.01 via D-PLACE: terrestrial fit 1.26, all foragers 1.28 |
| fisher top, `FISH_TOP` (/km2 where the fish good is 1) | 1.2 | 0.3 - 2 | log-uniform | fishing foragers 0.3-2 (Binford sedentary and fishing-led; Kelly 2013 Table 7-3, Northwest Coast 0.1-2). California's tail to ~9 left out: one region's whole-range figure |
| gardeners, `GARDEN` (/km2 at NPP 330) | 5 | 2 - 20 | log-uniform | gardeners ~2-20 (Boserup fallow classes; PNG). PNG's 5-40 by land quality is not added: the ladder already scales every rung by NPP |
| plough, bronze, `PLOUGH[0]` | 8 | 2.5 - 14 | log-uniform | Early Bronze Age Greece 2.5-14 (Renfrew, Lukermann, Angel, via Butzer 1976) |
| plough, iron, `PLOUGH[1]` | 14 | 10.8 - 17.9 | log-uniform | Roman Rhineland, west of the Rhine (Zimmermann et al. 2009) |
| plough, medieval, `PLOUGH[2]` | 25 | 13 - 35 | log-uniform | England 1086 ~13 to the 1315-48 peak ~35 (Broadberry, Campbell & van Leeuwen 2011) |
| pastoral nomads, `NOMAD` (/km2 at grazing NPP 263) | 0.8 | 0.35 - 2 | log-uniform | Mongolia ~0.35 (c. 1911) to 0.54 (1956); Kenya's driest districts, modelled, 1-2 |
| rich land takes up farming, `RICH_T` (kyr) | 1.0 | 0.6 - 1.0 | uniform | Yayoi rice to southern Tohoku ~0.6 kyr (Mizoguchi); Ertebolle beside farmers ~1 kyr (Gron) |

The three plough stages share one draw (a position in their ranges), so they stay in order: a world that draws a dense plough draws a
dense bronze, iron and medieval one.

**Fixed: no published range** (reasons in `ranges.py::FIXED`):

- `FORAGER` 0.036 per km2 at the reference land: Binford's spans are across all land qualities, not at one; only the fit's slope is drawn
  (which moves almost nothing: 1.26 against 1.28 changes a cell at 800 NPP by 2%). Draft: source the scatter from the D-PLACE data.
- `RICH_HALF` 3: a judgement on the Calusa case; the 7-16 in the write-up is that case's richness, not a range for the constant.
- `IRR` 30 ... 240 per watered km2: one "hypothetical" series (Butzer Table 4); the delta 10-135, nomes median 172 (up to 500) and the 1882
  census 240-280 are other places and measures.
- `PLOUGH_TOP` 35 (a point, 35-36); `PLOUGH_STEPS`, `IRR_LAG`, `TERRACE_LAG` (tech-tree dates); `FISH_MIN`, `FARM_FULL`, `WATER_*`,
  `DEN_FARM_W`, `RAID_*`, `TRADE_*`, `MUSHROOM_X`, `RICH_POW`, `HERD_POW` (judgements or placeholders); the agro-pastoral rung (no
  constant of its own); the kind factor 0.8-1.2 (an owner ruling); and the den-ground scores in `dens.py` (judgements, `dens/round1.md`).

## How the draw works, and why

- `ranges.draw(seed)`: for each group of names one number u in [0, 1) from `numpy.random.default_rng((seed, 1383, crc32(group)))`; the
  value is `lo + (hi - lo) u` (uniform) or `lo (hi/lo)^u` (log-uniform). Each group has its own generator, so a draw never depends on
  how many other ranges exist or on their order; the same seed always gives the same values.
- **Log-uniform for the densities** (fisher, garden, plough, nomad), whose ranges span 3.5x to 10x: equal chance per doubling, so
  "2-20" is not "mostly near 11". Their geometric means land near the fixed values the ladder already used (fisher 0.77 against 1.2,
  garden 6.3 against 5, nomad 0.84 against 0.8; plough iron 13.9 against 14, medieval 21 against 25, bronze 5.9 against 8). **Uniform
  for the narrow ones** (a slope 1.26-1.28, a time 0.6-1 kyr), where the difference does not matter.
- Seed: the peoples seed (`meta.seed`), not the try seed, so the best-of-N tries of one run all use the same numbers.
- Where it is read: `Ladder.__init__` builds `Ladder.v` from the module constants (the fixed values) and, with the setting on, replaces
  the ranged ones with the draws (`Ladder.drawn`). `Ladder.line` and `rich_keep` read `v`.
- Recorded: `run.json` `meta.draw_ranges` (bool) and `meta.range_draws` ({name: value}, `{}` when off); the tree itself (`meta.tree`)
  carries `draw_ranges`.

## Tests

`tests/test_lineages.py::test_published_ranges_are_optional_seeded_draws`:
- off: `Ladder.drawn == {}`, `Ladder.v` equal to the constants, the density arrays of two builds identical;
- on: every value inside its range, plough stages in order, the same seed gives identical values and identical density arrays, another seed
  other values, and over 40 seeds every name takes more than 30 distinct values, all inside their ranges;
- the run's metadata lists the draws (`range_draws` equals `ranges.draw(seed)` rounded), and is `{}` with `draw_ranges` false in
  `test_history_places_splits_hybrids_templates_and_extinctions`.
Not-slow lineages tests: 136 passed; the full suite: see the end of this page.

## The spread measured

**Baseline:** the dnd preset with the setting off, which on this branch is bit-identical to main 2ba59119, on the same six runs of
`tools/peoples_robust.py` (family base, tree dnd, arm now; seeds 7, 10, 13; worlds 4360a3 and af2677; end of the history, ~1500 AD).
**Drawn:** the same six with `--meta '{"draw_ranges": true}'`. Each seed has its own draw, so these are three draws per world:

| seed | forager slope | fisher top | garden | plough bronze / iron / medieval | nomad | rich_t |
|---|---|---|---|---|---|---|
| 7 | 1.266 | 1.25 | 3.8 | 3.9 / 12.3 / 16.9 | 1.21 | 0.63 |
| 10 | 1.271 | 1.27 | 4.7 | 8.2 / 15.3 / 25.7 | 1.17 | 0.89 |
| 13 | 1.268 | 1.45 | 12.7 | 6.9 / 14.6 / 23.4 | 0.73 | 0.84 |

Ratio drawn / fixed, same seed and world (so the history's own random draws start the same, but the changed densities send it down a
different path; one run each, so treat a single ratio as a sample, not an effect):

| run | total people | wild-fed share of people | humans' share | goblin range (Mkm2) | goblin people | kobold range (Mkm2) | kobold people |
|---|---|---|---|---|---|---|---|
| 4360a3 s7 | 1.07e9 -> 1.07e9 (1.00) | 3.6% -> 3.0% (0.84) | 27.7% -> 31.6% | 5.65 -> 3.34 (0.59) | 3.0e6 -> 1.4e6 | 10.1 -> 10.3 (1.02) | 2.6e6 -> 2.3e6 |
| 4360a3 s10 | 1.09e9 -> 1.15e9 (1.05) | 3.8% -> 3.4% (0.91) | 24.4% -> 29.1% | 1.88 -> 1.78 (0.95) | 1.1e6 -> 0.9e6 | 9.8 -> 10.1 (1.03) | 2.2e6 -> 2.3e6 |
| 4360a3 s13 | 1.32e9 -> 1.45e9 (1.10) | 2.6% -> 3.4% (1.31) | 41.8% -> 32.2% | 0.72 -> 1.99 (2.76) | 0.4e6 -> 0.7e6 | 8.1 -> 8.0 (0.99) | 1.9e6 -> 3.8e6 |
| af2677 s7 | 6.98e8 -> 4.31e8 (0.62) | 3.6% -> 3.8% (1.06) | 3.1% -> 3.7% | 11.2 -> 11.4 (1.02) | 4.4e6 -> 6.2e6 | 27.7 -> 28.5 (1.03) | 1.4e6 -> 1.4e6 |
| af2677 s10 | 1.26e9 -> 1.38e9 (1.10) | 2.4% -> 1.9% (0.78) | 12.3% -> 20.2% | 11.7 -> 11.8 (1.00) | 4.7e6 -> 6.9e6 | 2.4 -> 2.3 (0.97) | 0.4e6 -> 0.3e6 |
| af2677 s13 | 9.93e8 -> 1.12e9 (1.12) | 2.4% -> 3.0% (1.26) | 20.5% -> 18.0% | 4.6 -> 5.2 (1.12) | 1.7e6 -> 1.5e6 | 18.8 -> 18.8 (1.00) | 2.4e6 -> 5.0e6 |

(troglodytes do not live on either world at the end in either arm.)

What it says, in plain words:
- **Total people:** within about +-12% in five of six runs; one run (af2677 seed 7) falls to 0.62x. Across the three seeds, the spread
  (largest minus smallest, over the mean) is 0.31 drawn against 0.21 fixed on 4360a3, 0.98 against 0.57 on af2677. The seeds already
  spread the fixed runs widely (the worlds' histories differ a lot between seeds); the draws widen it a little more.
- **Wild-fed share** (the part of all people living mainly off wild food, from `forage_land`): 2-4% in every run, either arm; the
  drawn/fixed ratio is 0.78 to 1.31, no direction (geometric mean 1.01). The rich-coast holdouts survive whichever rich_t is drawn.
- **Humans' share:** up in four of six (geometric mean x1.11), range 0.77 to 1.64: the largest single mover, and it follows the world
  more than the draw (af2677 seed 10 humans 12% -> 20%).
- **Den kinds:** kobolds' ranges are almost untouched (0.97 to 1.03 of the fixed range) and their people move 0.9x to 2.0x; goblins'
  ranges are within 12% in four runs and 0.59x and 2.76x in two runs (4360a3 seeds 7 and 13), which at these sizes (0.7 to 5.7 Mkm2) is
  the usual small-range chaos (a patch surviving or not), not a ladder effect: the den kinds' densities hardly depend on the drawn
  numbers (forager rung and raids; only the slope is drawn for them).
- **Not isolated:** a changed density changes the whole contest, so a single run's difference is draw plus chaos. With 3 draws per
  world this shows the order of magnitude (tens of percent in people, a few points of share), not which number did it. A one-number-at-a-time
  screen would be a separate piece of work.

## Observations

- With the setting on, the suite's invariants hold in all six runs (the report's own count: 0 failing, 0 crashes, 0 peoples extinct,
  0 over 85% of all people), same as the fixed six.
- Gardening (2-20) and the bronze plough (2.5-14) are drawn separately and overlap: seed 13 draws gardeners 12.7 and bronze ploughmen
  6.9, so a people loses density when it takes the plough. Draft `draft-ranges-rung-order-under-draws.md` (leans: leave it).
- `FORAGER`, `RICH_HALF` and the irrigation steps are the three that matter and have no range; draft
  `draft-ranges-source-the-fixed-ones.md`. The forager level can probably be sourced from the Binford data already in hand.
- The viewer's workbench has the tick box now (`viewer/lineages.html`, beside "growth rates from life history"); the "New planet" form
  makes worlds, not peoples, so needs nothing. Showing the drawn numbers in the workbench is draft `draft-ranges-show-drawn-in-viewer.md`.
- The robust runs: `--meta '{"draw_ranges": true}' --tag draw` runs any family with draws on. Scratch results were not kept.
