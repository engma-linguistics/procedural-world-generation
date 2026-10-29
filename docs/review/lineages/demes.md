# Demes v0: regional populations and their dated tree (PW-981, fun lane 46, 2026-10-29)

## In plain words
Until now a people was one blob over its whole range: humans on three continents counted as one community. The new
demes pass reads a finished peoples run and cuts each people's land, frame by frame, into regional populations
("demes"). It cuts wherever open sea, hard country (mountains, desert, deep forest, ice) or sheer distance separate
them. It then follows those populations through time: when one splits off, when two fuse, when one dies out, and which
ones touch (of the same people or of others). The result is a dated family tree of regional populations inside each
people, plus a contact record per pair. It is the seed for "the grain-belt humans" as a culture, and later for
languages. Nothing here is linguistic. Demes are only placed and dated.

How to see it:
- **Globe:** open a peoples run and pick the colour layer **demes**. Each deme is a shade of its people's colour. The
  legend lists this frame's largest demes. The hover card gains a "regional population" row: its name, since when, and
  what it came from. Scrub time to watch them split and spread.
- **Workbench:** Tree & timeline, view **species + regional populations**. It needs a run opened in the workbench
  (`lineages.html?run=<id>`, or Results). Each people row gets its demes beneath it: a bar from birth to end, a branch
  from its parent deme (dashed: founded over the sea), † died out, → fused. Hover a bar for the dates. Only demes that
  ever held 150 cells, or are alive now, are drawn.
- **CLI:** `uv run python -m planet demes RUN` adds or redoes the demes of a stored run in place. A new peoples run gets
  them automatically (`output.save`, after the fuels). The pass writes `runs/<id>/demes.json`, `layers/demes.bin` and
  `meta.demes`, and adds a section to run.txt.

![demes on b69f51 at the present](demes-b69f51-globe.png)
![demes on 2cb509 at the present, Shurul and Namo](demes-2cb509-globe.png)
![the workbench timeline, species + regional populations](demes-workbench-tree.png)

## How it cuts (planet/lineages/demes.py)
- **Occupied cells, per frame and people:**
  - the cell's leading people by ground (`peoples_whole`);
  - its leading people by heads (`mix_lead`);
  - its second people by heads, if that people has at least 10% (`mix_second`).
- **Travel cost:**
  - Land uses `crossing.corridor`, the history's own contact value, computed from each frame's land, rain, trees and
    ice and the world's rivers. A cell costs (0.8 / corridor)^0.5 "easy km" per km: 1 on a coast, ~1.3 on open
    lowland, ~2 to 2.3 in desert or mountains, at most 3.
  - Sea up to 150 km wide is crossed at 2 easy km per km, so the people on both shores stay one population. A wider
    gap separates them.
- **Founder chains:**
  - Cells keep the deme they had in the frame before.
  - Newly settled cells take the deme that is cheapest to reach.
  - Land that no path reaches (a long crossing) becomes a new deme if it has at least 40 cells. Its parent is the
    nearest deme of the same people.
  - A new people's first demes take as parent the deme of their tree parent on (or nearest) those cells.
- **Splits:**
  - **Gap:** when a deme's land falls into pieces, the largest piece keeps the id. Every other piece of 40 or more
    cells becomes a new deme. It is dated at the split and keeps the date its land was settled.
  - **Distance:** a deme whose travel-cost diameter passes 7,000 easy km is cut in two between the ends of that
    diameter. The half with the older cells keeps the id.
- **Fusions:** two touching demes of one people fuse when their diameters together come to less than 4,000 easy km.
  The older one keeps its id.
- **Window:** the frames of the last 300 kyr (the glacial zoom and the recent pass; the deep keyframes are Myr apart).
  On b69f51 that is 129 frames.

## Worked example 1: humans on the owner's world (run b69f51, world 2a7385, "Seven Meals")
**Arising and the chain.** Humans appear 200 kyr ago as 21 demes at once, one for each separate piece of the human
stem's land. Each takes its parent from the stem's own demes: human 1 comes from human line 13, human 2 from human
line 6, and so on.

On the southern continent (61°S 72°E), human 2 then breaks up by distance into a chain:
- human 23 buds off at 200 kyr;
- human 29 buds off at 196 kyr;
- human 54 buds off at 26.5 kyr;
- human 70 splits off human 54 along a gap 8 kyr ago (its land was first settled 25 kyr ago);
- human 74 splits off human 29 at 3.5 kyr;
- human 76 buds off human 74 at the present.

Today 60 human demes are alive out of 76. Their present sizes run from 82 to 2,135 cells.

**A sea crossing.** The history logs "humans sail across the sea to the large island at 53°N 22°E (241 km of open sea)"
44 kyr ago. Demes founds a new population there, human 44, 40 kyr ago, with human 17 on the facing coast as its
parent. The ASCII maps show it:
- 44 kyr ago the island is held by another people;
- 40 kyr ago humans lead its north;
- by the present they hold it all, 113 cells.

Human 44 is its own population because 241 km of open sea is more than the 150 km that keeps two shores one
population.

## Worked example 2: a late boat diaspora (run 2cb509, world 3e9e7d, named landmasses)
For 195 kyr, humans here are one deme: human 1 on the north-west of Rejonor, ~170 to 190 lead cells. Then the boat era
cuts them up quickly:
- **human 3** is founded over the sea on Namo 5.0 kyr ago (80 cells at first, 1,150 occupied today);
- **human 7** is founded on Shurul 2.5 kyr ago;
- **human 8** is founded on Humohil 2.0 kyr ago;
- on the islands, human 4 (Tigobrus) and human 5 (Bresam) split from human 1 at 4.0 and 3.5 kyr. Their land was
  first settled 4.5 kyr ago, by the canoe hops that kept them part of human 1 at first.

Shurul's humans then break up along gaps:
- human 6 at 3.0 kyr;
- human 10 and human 12 at 2.0 and 1.5 kyr;
- human 14 at 1.0 kyr.

Sixteen human demes are alive at the present, against 60 on b69f51. On this world humans stayed home until boats, and
the tree shows it.

## What looks right
- Real barriers cut peoples. Sea gaps wider than a strait separate demes, and a strait does not. The dated crossings
  line up with the history's own crossing log within a frame or two (b69f51's island: 44 kyr in the log, 40 kyr in
  demes).
- The founder chains read as stories: "founded over the sea from human 17", "split by a gap from human 6 (its land
  settled 200 kyr ago)". The ancestry goes up into the authored tree (human 1 from human line 13).
- The worlds differ the way their histories differ: 60 human demes on b69f51's big shared continent, 16 on 3e9e7d's
  late diaspora.
- The contact series per deme pair gives "who these humans touched". On b69f51, human 2 has bordered cervid folk 3 for
  200 kyr, and they share 1,053 cells today.

## What doesn't (yet)
- **Flicker.** Most gap splits and fusions are bookkeeping noise. They happen where a pocket is joined to its people by
  a neck one or two cells wide that changes hands between frames. On b69f51 there are 459 gap splits and 389 fusions
  for 809 demes. Of the 497 events of 60+ cells, only 49 had the sea moving next to them. Example: the humans at
  ~51°N 159°W split at 120 kyr, fused at 68 kyr and split again at 32 kyr across such a neck. Small peoples churn most:
  leonin have 62 demes of which 28 died out, orcs 90. Hysteresis would fix it (draft
  `draft-demes-gap-flicker`).
- **Land bridges barely show.** Sea-level changes do open and close gaps, but on b69f51 they are swamped by the flicker
  above. A clean ice-age bridge story waits for the flicker fix (and for PW-902, ranges that follow sea level).
- **Peoples that rarely lead are underseen.** Measured at the present, where full presence is stored: of the cells
  where a people (its groups counted in) has at least 12% presence, demes sees it in 69% on b69f51 (63-73% on ac4c06,
  2cb509 and 3097e3). For many peoples it is far less:

  | people on b69f51 | seen |
  |---|---|
  | orcs | 9% (1,226 of 14,131 cells) |
  | tortles | 3% |
  | deep folk | 3% |
  | leonin | 22% |
  | dragonborn | 37% |
  | aarakocra | 38% |
  | dwarves | 43% (66 of 155) |
  | humans | 100% |

  On 2cb509, leonin and aarakocra are at 4%. Their demes are cut from the few cells they lead. The cheap fix is one
  per-frame bit-flag layer of which peoples are present (draft `draft-demes-full-presence-frames`). It is not done
  here: it touches the history's frame store.
- **Scale is a taste call.** The 7,000 easy-km split gives ~2.4 Mkm² per human deme on b69f51 (draft
  `draft-demes-scale`, needs-decision).
- **Cost.** The pass adds 71-132 s per L7 peoples run, on one core (draft `draft-demes-speed`).
- **Colours.** Neighbouring demes of one people differ only by shade. With 60 human demes, two touching ones can look
  alike. The hover card names them.
- **Arrival dates.** The globe layer shows the leading people's deme only. On 2cb509, human 3 leads 80 cells of Namo
  5 kyr ago, while the history's crossing log names humans' first arrival on Namo at 1.3-1.5 kyr. The log is kept per
  line (humans and each of their groups), and demes reads the whole people, groups counted in, but why the two
  disagree by ~3.5 kyr is not checked yet.
