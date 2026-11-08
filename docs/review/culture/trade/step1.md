# Trade step 1: the goods ledger (PW-1502, lane 212)

Design: [design1.md](design1.md) step 1. Sources: [review1.md](review1.md) (R§n below). Code: `planet/lineages/trade.py`,
served by `GET /api/trade` (`planet/server.py::trade_doc`), shown in the workbench's Culinary brief tab. Tests: `tests/test_trade.py`.

## In plain words

- Every culture of the last ~12,500 years now has a list of what its own land gives beyond its own needs, and what it needs but
  doesn't have at home. There are twenty goods in three classes: bulk, middling and precious.
- The model reads it after the run, as it reads the polities. It changes nothing in the history or in any run file. A run's runs are
  byte-identical to before, and the goldens do not move.
- On the three judge runs (two D&D, one Seven Meals; numbers below are the share of culture-snapshots, baseline: the same runs on
  current main, which had no ledger at all):
  - herders lack grain in 98-99% of their snapshots (R§2, Khazanov: herders are never self-sufficient);
  - farmers' top lacks are copper, tin and iron, then salt;
  - foragers' top lack is shell and bead ornaments (R§1, hxaro beadwork); foragers living beside farmers also lack starch;
  - tin is the rarest metal. A culture holds spare tin in 0-7 of ~4,500-4,700 trading snapshots per run, and spare copper in
    500-800. Of the cultures that know bronze, 88-97% lack tin (R§3, the "tin problem");
  - farm cultures that the culinary brief calls salt-poor lack salt, almost all of them (97-99%).
- It is stable. A random ±10% nudge to every land value and every cell's people moves a typical number by under 1%, and leaves 99% of
  the "has / lacks" lines the same.
- It is fast: 4-6 s per L7 run, plus ~5 s to open the run, and cached after the first time.
- Daniel sees it in the Peoples workbench: **Culinary brief** tab > pick a people and **one culture** > **Show the brief**. The sheet has
  a new "Has / lacks" line, and below the brief a **Trade: goods** panel shows two tables (Surplus, Lacks) with class and share, and
  how the lacks changed over time. Hover a good to see the layer it comes from.

## What was built

**Goods (20)**, each from a model layer (`trade.GOODS`, the "from" text is shown on hover):

| Class | Goods |
|---|---|
| bulk | grain, timber, firewood and charcoal, building stone, dried and salted fish |
| middling | salt, herd animals (wool, hides, dairy), oil and wine, sugar, copper, tin, iron, obsidian, furs, seal and whale oil |
| precious | spices (spice tree, chili, tea, vanilla, cacao), gold, gems, shell and coral ornaments, mithril and adamant |

The classes follow R§6: "value per weight is the switch". Obsidian is read from volcanic ground. Flint has no layer, so nobody's
*want* of edge stone is written: it would read as a universal lack.

**Per cell, then summed to the culture** (D64 B, cells summed to cultures):
- output = land value (land.GOODS; for crops and herds, the crop or animal known on the cell) x the share of the cell's people who
  work that land (meta.eraq: farm, herd, timber, wild; a deposit counts in full: whoever lives on it digs it) x a know gate (`GATE`:
  e.g. tin needs `bronze` or `tin_trade`, salt for trade needs salt works; a tech the tree lacks is no gate, as with cuisine's
  milking rule);
- need = the share of the cell's people whose way of life wants the good (`NEED`, each entry naming its R§ source): herders and towns
  want grain; farmers and herders want salt and the metals they know; towns want fuel, timber, stone, livestock, furs and fine goods;
  foragers want ornaments, plus starch and salt when farmers live in their cell; farmers who know wine or the oil press want oil and
  wine; farmers who know sugar making want sugar;
- surplus = output beyond need; lack = need not met. Salt's lack uses the brief's own walk to salt (`brief.SALT_TRADED_KM`).
- A culture's number is the mean over its cells, weighted by people (0..1).

The "has" side of the line names the goods the culture has more of than the average culture of its time. Stone and fish lie nearly
everywhere; tin does not.

**Judgements, stated in the code:**
- like-for-like (one producing head against one needing head; no yields or rations are sourced for twenty goods);
- `NEAR_FARM` (1% of a cell's people farming means foragers there live beside farmers; eraq's resolution);
- `SHOW_MIN` (2%, display rounding);
- the giants' rule (below).

**Peoples off the density ladder** (D65, owner 2026-11-07):
- Dragons take tribute, and their kobolds trade for the realm. They keep a ledger row marked `mode: tribute, via: kobolds`, so step 2
  can carry their goods. Their line reads "takes tribute, and its kobolds trade for it: has ...".
- Giants trade or take tribute depending on the kind. Until step 2 sources a rule, a giant kind with a way of life of its own (hill
  giants herd) trades, and one without takes tribute. This is a placeholder, sent to the inbox.
- Neither farms the land under it. Their "wild" share is not a forager band, so it writes no starch, salt or bead want. A realm's
  hoard wants are step 2's.
- `TRIBUTE_ROWS = False` drops their rows.

## Judge (measure only)

Runs:
- 0141d1: D&D, world 899985, L7;
- 3e0eb4: D&D, world dba204, L7;
- 07c755: Seven Meals, world 899985, L7.

Each has 26 frames (12.5 kyr ago to now, every 0.5 kyr). A snapshot is one culture at one frame. A snapshot's way is its largest
share (farm, herd or wild). "Towns" are the snapshots with ≥10% of their people in towns (a judge's cut). "Lacks" is the share of
snapshots that name the good in their top-3 lacks. "Mean" is the mean lack (0..1).

| Way (snapshots, 0141d1 / 3e0eb4 / 07c755) | Most often lacking (named in top 3) | Most in surplus (mean) |
|---|---|---|
| herders (603 / 43 / 70) | grain 99% / 98% / 99%; copper 72% / 95% / 40%; salt 62% / 21% / 69% | stone, herd animals (0.39 / 0.17 / 0.34) |
| farmers (2259 / 2615 / 2570) | copper 81% / 83% / 69%; tin 73% / 40% / 63%; iron 50% / 31% / 34%; salt 31% / 38% / 26% | stone, grain (0.23 / 0.22 / 0.23), gold, dried fish |
| foragers (2028 / 2144 / 1718) | ornaments 93% / 95% / 93%; grain (starch) 17% / 13% / 18% | stone, dried fish, seal oil |
| towns (21 / 230 / 19) | tin and copper 58-91%; salt 29-42%; grain 10-42% | stone, dried fish, gold |
| tribute (dragons, tribute giants: 1455 / 1466 / 1345) | none (wants are step 2's) | gems, obsidian, firewood |

Seven Meals' farmers also lack sugar (39%) and oil and wine (26%): its tree knows sugar making and wine widely.

**Sanity against the review:**
- Herders lack grain. Grain is in their top 3 in 977-992 of every 1,000 herder snapshots, with a mean grain lack of 0.71-0.86 (R§2:
  "specialized and non-autarchic", Khazanov 2019).
- Farmers lack salt where there is no salt. At the present frame, farm cultures' salt lack follows the brief's salt-poor share (land
  more than 300 km from salt), with correlation 0.96 / 0.94 / 0.92. Of the brief's salt-poor farm cultures, 101/102, 82/87 and 98/101
  lack salt at ≥0.1. 30, 19 and 27 cultures that are not salt-poor by the brief's 25% cut still lack some salt (their far corners).
- Tin is rarer than copper (R§3). These counts are trading snapshots with a surplus of at least 0.05; tribute rows are counted
  separately (dragons sitting on tin ground).

  | | 0141d1 | 3e0eb4 | 07c755 |
  |---|---|---|---|
  | snapshots with spare tin | 7 | 0 | 6 |
  | snapshots with spare copper | 504 | 802 | 535 |
  | bronze-knowing snapshots lacking tin | 1928 of 1991 (97%) | 1124 of 1241 (91%) | 1809 of 1914 (95%) |

  This is the review's Bronze Age picture: tin held by very few and needed by nearly all bronze users. In 3e0eb4 no trading culture
  holds tin at all, so step 2's tin has to come from tribute land (via the kobolds) or nowhere.

**Stability (nudge).** Every land value and every cell's people were multiplied by a seeded uniform 1 ± 0.1 and the ledger was re-run.
- Mean absolute change of a surplus or lack: 0.003 on all three runs.
- Median relative change of the values ≥0.05: 0.7-0.8%. The 90th percentile is 2.6-3.0%.
- Jaccard of the "has" top 3, nudged against unnudged: 0.988-0.989. Of the "lacks" top 3: 0.997-0.998.
- `tests/test_trade.py` checks the same on a hand-made world: moving one cell's fertility by 0.04 moves no number by more than 0.03
  and keeps every lacks list.

**Runtime.** derive is 4.1-4.9 s per L7 run (26 frames, ~5,700-6,300 snapshots), plus 4-6 s to open the run (`brief.Ctx`). The doc
is 2.3-2.4 MB of JSON, kept in `.godscache`.

**Not changed.** No history or run file is written. Goldens are untouched. The brief's version went up to 19 for the new sheet line.

## Not done here (drafts)

- The globe layer "Trade goods" (pick a good: surplus green, lack red) from the ticket's list. It is a viewer layer of its own, and
  the cell values it needs are in `trade.cells_at`.
- The giants' trade-or-tribute rule needs a source or an owner rule per kind.
- Flint and chert have no world layer, so obsidian stands for edge stone and no want of it is written.
