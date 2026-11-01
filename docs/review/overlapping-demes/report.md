# Overlapping demes (lane 109, PW-1259)

Written by the coordinator from the lane's report (the lane could not write report files). Code: `planet/history/frame.py`,
`planet/output.py` (`write_presence` / `read_presence`), `planet/lineages/demes.py`, `planet/lineages/cultures.py`. Tests:
`tests/test_demes.py`, `tests/test_cultures.py`.

## In plain words

Each people now gets its demes from everywhere it lives, not only where it leads or comes second. So demes overlap: a kobold deme
and a hobgoblin deme can cover the same hills, and a dragon kind's wide demes lie over the peoples below them.

- **What is stored:** every frame now stores each people's presence on every cell where it is established, dragons and giants
  included.
- **Cost:** the table costs 15 MB at L6 (about 5% of a run) and 111 MB at L7. Every people's deme labels add 10 MB and 44 MB.
- **More demes:** on the L6 test run there are 417 demes instead of 381 (316 alive instead of 251). The dragons gain most:
  silver 3→10, copper 6→12, bronze 8→13, red 6→9.
- **Overlap:** 87% of peopled cells hold demes of two or more peoples.
- **A bug the overlap exposed, now fixed:** "adapted" splits read the leading people's learned country. So dragons living over
  human farmland split off demes from the humans' learning.
- **Round 2's rejoin rule is removed.** It changed one culture in 344.
- **Dragon kinds:** each is now one to five living cultures, split where its populations are farther apart than a dragon flies
  (1,500 km). Keeping or folding that is a decision for Daniel.
- **Viewer:** the globe's demes layer has a "whose demes" picker (`?demes_of=ID`). The Cultures tab's map link opens it on that
  culture's people. Hovering a cell lists every deme on it.
- **Old runs** work as before from the two leading peoples. Owner runs need a new peoples run to get overlap; recutting the
  demes isn't enough.

## Format

For each frame and each whole people, the table stores the cells where the people holds at least 12% (in ascending order) and
its share of each cell.

| File | Contents | Type |
|---|---|---|
| `presence_offsets.bin` | frames × (lines + 1) | uint32 |
| `presence_cells.bin` | cell indices | uint16 at L6, uint32 at L7 |
| `presence_share.bin` | share of the cell | uint8 |

The format is described in `meta.presence`. `layers/demes_all.bin` holds every people's deme for each table entry; `demes.bin`
stays the leading people's.

The mean L6 frame holds 28.7k entries on 40,962 cells, which is 86 KB. A top-4 layout would take 330 KB, and bitsets 350 KB
without the share.

## Numbers

| Level | Frames | Entries | Table | demes_all | Share of run |
|---|---|---|---|---|---|
| L6 | 169 | 4.85 M | 14.6 MB | 9.7 MB | about 5% |
| L7 | 169 | 22.1 M | 110.6 MB | 44.2 MB | about 12% of 1.3 GB |

**Demes per people, old → new** (alive now in brackets):

| Group | Demes |
|---|---|
| Dragons | gold 15→18 (7→13), bronze 8→13, green 8→12, copper 6→12, brass 10→11, silver 3→10, blue 7→9, red 6→9 (2→7), white 5→8, black 5→7 |
| Giants | hill 11→12, storm 9→9, frost 9→8, elemental 7→7, cloud 3→4, fire 0→2 |
| Peoples | human 36→29, lizardfolk 27→33, hobgoblin 26→27, elf 29→23, tortle 7→12, bugbear 2→7, kobold 9→7 |
| All | 381→417 (alive 251→316) |

**Cultures, with the rejoin rule on and off** (all / alive):

- Old demes: 317 / 142 either way.
- New demes: 343 / 143 with it, 344 / 143 without. The only change is fire giants, 1 → 2.

**Living cultures per dragon kind (L6):** black 1, blue 2, bronze 2, gold 3, copper 3, red 4, silver 4, brass 4, green 5,
white 5. L7 gives 1–5 per kind as well.

**How much the old record missed.** Below, each kind's cells at the present, and the share of them where it leads:

| Kind | Cells | Leads |
|---|---|---|
| Blue dragon | 1,296 | 4% |
| Gold dragon | 1,850 | 10% |
| Silver dragon | 798 | 10% |
| Copper dragon | 1,204 | 12% |
| Bronze dragon | 1,438 | 12% |
| Red dragon | 502 | 13% |
| Black dragon | 838 | 34% |
| Brass dragon | 2,281 | 39% |
| Green dragon | 1,135 | 45% |
| Hill giant | 1,123 | 30% |
| White dragon | 746 | 70% |
| Cloud giant | 524 | 70% |
| Frost giant | 336 | 81% |
| Storm giant | 684 | 100% |

## Checks

- `planet brief --people red_dragon` and `--people kobold --era 2` list cultures with overlapping shares. For example, red
  dragons live on 86% of their range, hill giants on 30% of it and kenku on 22%.
- A headless screenshot of the viewer picker on the lane's own port showed the red dragons' demes, with no console errors.

**Tests:** the not-slow run passed 892, with 1 skipped. The area runs passed 228.

**Not exercised:** settlements on the scratch run. Settlements don't read the demes.
