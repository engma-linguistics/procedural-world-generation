# Settlements v0 (PW-1011): screenshots

The globe viewer with its new "Settlements and ruins" overlay (side panel, Overlays). It is on by default for peoples runs and has no button of its own in the layer list:
- a village is a small dot in its holder's colour;
- a town is a bigger dot with a dark edge;
- a city is a bigger dot again, with a white ring;
- a ruin is a small grey cross.

Hovering a cell lists its places. Each has its tier, its people and size at the slider's moment, when it was founded and by whom, any change of hands, and when and why it was abandoned. The list shows who lives there, with any city-minority quarter.

All shots are from world 4360a3 (seed 6001, L6, made on main 347b4374), D&D tree seed 7, taken 2026-10-30 with headless Chrome against a lane server on port 8791.

| Shot | What |
|---|---|
| [1-before-present.png](1-before-present.png) | main (run d050b2): the same history without the ledger |
| [2-after-present.png](2-after-present.png) | the branch (run 6553f1) at the present: hover on a human city of ~78,000 (humans 52%, halflings 47%), founded ~9.1 kyr ago |
| [3-after-9kyr-ago.png](3-after-9kyr-ago.png) | 9 kyr ago: the first villages |
| [4-after-5kyr-ago.png](4-after-5kyr-ago.png) | 5 kyr ago |
| [5-river-city-3kyr-ago.png](5-river-city-3kyr-ago.png) | a river city of ~41,800 three kyr ago, on the ruins of a village the river left 6.9 kyr ago |
| [6-river-ruin-present.png](6-river-ruin-present.png) | the same cell today: two ruins, both abandoned when "the river moved away" (the city ~2.4 kyr ago), and a new town of ~2,550 on the ruins |
| [7-kenku-town-taken-by-humans.png](7-kenku-town-taken-by-humans.png) | a town of ~5,550 founded by the kenku ~6.7 kyr ago and held by the humans since ~3.7 kyr ago (humans 90%, kenku 10%) |

PW-1106 (fun lane 61), the overlay clutter, same run 6553f1 and cell, taken 2026-10-30 against a lane server on port 8797:

| Shot | What |
|---|---|
| [8-clutter-before-globe.png](8-clutter-before-globe.png) | main: at whole-globe view the villages carpet the land; the hover says "city of the human" |
| [9-clutter-after-globe.png](9-clutter-after-globe.png) | the branch, same view: only cities and city ruins (the owner, 10-30: the town dots were still far too many); the hover says "city of the humans" |
| [10-clutter-after-dist2.3.png](10-clutter-after-dist2.3.png) | `&dist=2.3`: zoomed in, the towns have faded in, the villages not yet |
| [11-clutter-after-dist1.6.png](11-clutter-after-dist1.6.png) | `&dist=1.6`, taken before the town fade and the later village fade: the villages and the village and town ruins in (before the fix, `dist` did nothing when `lat`/`lon` were also given) |

PW-1105 (fun lane 61): a second people's own place, and mines. Run 488d7e (world 4360a3, D&D seed 7), cell 30132 on Gugiki, where a dwarf hold-town of ~10,000 stands beside a human town:

| Shot | What |
|---|---|
| [12-holds-globe.png](12-holds-globe.png) | the default globe view: cities only. The hover lists the human town, the dwarves' own town ("their own place, as a second people here") and a human mine |
| [13-dwarf-holds-dist2.3.png](13-dwarf-holds-dist2.3.png) | `&dist=2.3`: the towns, with the dwarf holds (magenta) along the hills among the human towns |
| [14-dwarf-holds-and-mines-dist1.7.png](14-dwarf-holds-and-mines-dist1.7.png) | `&dist=1.7`: the villages and the mines (diamonds) are in too |
| [15-peoples-tab-places.png](15-peoples-tab-places.png) | the workbench's Peoples tab with run 488d7e (PW-1103): a 'places now' column at the far right of the table, e.g. dwarves "29 towns, 52 villages, 10 mines; 49 among another people; 4 taken from others; 77 ruins" |

Numbers and the judgement constants: see PW-1011's Updates and `planet/lineages/settlements.py` (CONST).
