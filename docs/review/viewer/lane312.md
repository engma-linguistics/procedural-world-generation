# Lane 312: the settlement view (PW-1659) and the trade goods layer (PW-1508)

## In plain words

- **Click a town.** With the Settlements overlay on, clicking any place on the globe (a city, town, village, mine or ruin) opens a
  card about it at the time slider's moment. It has these sections: **Names** (the name the run stores, the older places under it,
  the other places in the same cell, which you can click), **People** (size now and a small chart of its size over time, the peoples
  living there and their shares, its own cultures and the ones around it, who founded it, who held it since, wars and walls),
  **Goods made and bought** (what its cell makes beyond its own want and what it lacks, shown as green and red bars, plus each of its
  cultures' "has / lacks" line and the brief's "Bought in" line, and what passes through when it is a trading or market town),
  **Rule** (the state that holds it now and the ones before), **Faith** (the faith each of its cultures holds), **Language** (its
  cultures' own tongues, the other tongues spoken and the trade tongue when the town is on a trade language's network) and
  **History** (one list, oldest first, from the first place on the spot to now). Sections the run cannot fill are hidden.
- **Trade goods layer.** Peoples > *trade goods*. Pick a good in the legend. Green cells make it beyond their own want, red cells
  want it and lack it at home, pale grey cells have people but neither. A deeper colour means a larger share of the cell's people.
  The layer follows the time slider, over the last ~12,500 years (the land-use window, every 500 years).
- Nothing is recomputed that the run already has. The card reads the stored settlements.json and the docs the server already
  derives for other tabs (goods ledger, exchange, polities, gods, tongues). The first click on a run can take a minute or two
  while those docs are made and cached. After that a click takes about a second.
- **Names.** The town names are whatever the run stores, for example "the north-east of Khumatrem". Real place names are lane 311's job.

## What was added

| File | What |
|---|---|
| `planet/lineages/settlement_view.py` (new) | the view's parts (`place_part`, `cell_goods`, `good_map`, `rule_part`, `faith_part`, `tongue_part`, `history`), `build` / `api` for `GET /api/settlement?run=&site=&ago=`, `good_view` for `GET /api/trade?run=&good=&ago=` |
| `planet/server.py` | two routes (+6 lines): `/api/settlement`, and `good=` on `/api/trade` |
| `viewer/globe/settleview.js` (new) | the card (its own popup, built in JS), the click on a place, `?site=<id>` to open one from a link |
| `viewer/globe/tradegoods.js` (new) | the `trade goods` layer: per-cell colours, the legend with the good picker, `?good=` |
| `viewer/globe/layers.js` | the layer's entry and its place in the Peoples menu (+5 lines) |
| `viewer/globe/main.js` | imports settleview.js (+1 line) |
| `tests/test_settlement_view.py` (new) | 8 tests, one per part, on hand-made docs and the goods ledger's six-cell test world |

**No output format changed** and no version was bumped. The module is outside the import closure of `planet.lineages.run`, and
trade.py is untouched, so the peoples' caches (provenance "lineages" scope) and the goods ledger's `.godscache` keys still hold.

## How each section is read

- **Place**: the settlements.json record. Size and tier at the slider follow the viewer's own rules (`settlements.js` popAt / TIER,
  ported as `pop_at` / `tier_at`). The ruins under the town come from the `ruin_of` chain.
- **Cultures in the cell**: `cuisine.culture_cells` at the stored frame nearest the slider (one per people's deme in the cell). The
  town's own cultures are those whose people are in its `who` or hold it. Goods lines, faith and tongues are given for those only.
  The rest are listed as "around it". Before this split, a town that was 100% human was shown holding the faiths of five cultures
  that live in the countryside of its cell.
- **Goods**: `trade.pairs_at` at the land-use frame nearest the slider. A cell's spare or lacking share of a good is the mean over
  the cell's (cell, culture) pairs, the numbers the ledger sums to cultures. A test checks that the cells average back to the
  culture's ledger number. The bought-in line is `bought_in.line` over the exchange doc. The trading town is `trade_routes.frame_view`'s
  hub at the site or cell.
- **Rule**: the polities doc's century maps, unpacked once per run into a (steps x cells) table (int32, about 80 MB at L7 for 126
  steps), then read for the cell. Polity names go through the names slot, as `/api/polities` does.
- **Faith**: `faithmap.faith_of_culture` plus the gods doc's per-culture faith changes. Names come through the names slot.
- **History**: founding, older places, changes of hands, wars, walls, the polities that held the cell, faith changes and the peak.
  Anything older than the first place on the spot is dropped.

## Checked on

Run `de1cc6` (Seven Meals on world 2762ba, L7), a copy in `/data/personal/scratch/lane312` (since deleted), served on port 8812.

| Screenshot | What |
|---|---|
| `lane312/settlement_click.png` | the real click path: the town at the centre of the screen, Settlements on, mouse click → the card (site 29063, a human river port with three older villages under it) |
| `lane312/settlement_site5086.png`, `_full.png` | a city that changed hands six times (site 5086), opened with `?site=5086`; `_full` is the whole card |
| `lane312/trade_goods_tin.png`, `_salt.png`, `_grain.png` | the layer for three goods at the present |

Timings on that run, under a machine load of about 28: the first `/api/settlement` after a server start took about 26 s (the
polities and the other docs were already on the disk cache). The per-good map took about 0.1 s (606 kB, 43,056 peopled cells).

## Not done / notes

- The ticket asks for the trade goods picker "under Overlays". It is a colour layer under Peoples instead, with the picker in its
  legend. That is how the polities and demes layers work, and it keeps index.html, which lanes 311 and 313 are also editing, untouched.
- Not shown yet because the run does not store them: the lects of each town and on-demand names (PW-1742/1743), the governance style
  (PW-1549), and older names with their meanings (PW-1654/1656/1658). The card has a place for each, and they can be added as rows
  when those systems land.
- The card only opens with the Settlements overlay on, so that a click on the globe in other views still just picks a cell.
