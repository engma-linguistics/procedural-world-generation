# The Technology tab, built (PW-913)

Screenshots of the real tab in the peoples workbench (`viewer/lineages.html`, Technology tab; code in `viewer/techtab.js`), on run **3097e3** (the D&D peoples on world 2a7385, the run the mock-ups in [../techtree-views/](../techtree-views/index.html) used). Taken with a headless Chrome against a test server, 2026-10-29.

The views follow the owner's ruling on the mock-ups (2026-10-29):

| View | Screenshot | What it is |
|---|---|---|
| Tree (the default) | [1-tree.png](1-tree.png), [1-tree-as-seen-by-humans.png](1-tree-as-seen-by-humans.png) | Mock-up view 1, unchanged: eras left to right, tracks as lanes. Hover a tech for its chain and its real-world source (the note at the bottom of the card); click it for who has it. The side panel now also has buttons to see the tech on the map or as a cascade. |
| Timeline | [2-timeline.png](2-timeline.png) | Mock-up view 2: a row per people, a dot per tech it came to; pick a tech to see who gave it to whom. |
| Map | [3-map.png](3-map.png), [3-map-how-long-known.png](3-map-how-long-known.png), [3-map-at-an-event.png](3-map-at-an-event.png), [3-map-bronze.png](3-map-bronze.png) | Mock-up view 3, rebuilt at full detail: the globe viewer itself, embedded, drawing the tech on the run's own cells at every one of the run's 153 stored moments (its own timeline and play button). Same two colour modes ("how it came", "how long known"), stars for inventions, arrows from giver to taker. Clicking an event on the right moves the globe to that moment and turns it to that people. |
| Map, in the full globe viewer | [3-globe-viewer-technology-layer.png](3-globe-viewer-technology-layer.png) | The same thing is a layer of the main viewer: "technology" under Colour by, with a tech picker under the layer buttons ("open on the globe" in the tab goes there). |
| Inventory | [4-inventory.png](4-inventory.png) | Mock-up view 4, unchanged: one people's kit by track, what could come next and why not yet, compared with a second people. |
| Cascade | [5-cascade.png](5-cascade.png) | Mock-up view 5, the "one tech: its cascade" half only. The "all techs: who taught whom" ring is dropped, as asked. |
| Table | [6-table.png](6-table.png) | The tab's old peoples-by-techs grid and its "Firsts" list, kept as a last view (whether to keep it is an open question for the owner). |

The "Firsts" in every view now credit the people that invented a tech when another people got it from them on the same time step (PW-1012): pottery's first in this run is the halflings, 18.8 kyr ago, no longer the firbolgs who learned it from them.

Not in this tab (the rest of PW-913): the default stop around the mid-1400s, a user-chosen earlier stop, uneven pace, catch-up by distance and pockets that resist new techs. Those change the simulation; this lane only shows what the runs already store.
