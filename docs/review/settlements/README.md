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

Numbers and the judgement constants: see PW-1011's Updates and `planet/lineages/settlements.py` (CONST).
