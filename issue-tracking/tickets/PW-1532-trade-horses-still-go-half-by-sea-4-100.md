---
id: PW-1532
title: "Trade: horses still go half by sea, ~4,100-4,300 km far tenth; source a horse ship's cost"
type: task
status: todo
parent: PW-1498
milestone: v4
subsystem: culture
effort: s
impact: med
found_by: lane 225
blocked_by: []
relates: [PW-1522]
refs: [docs/review/culture/trade/step4c.md, docs/review/culture/trade/step4b.md, "planet/lineages/trade_flow.py::DROVE", "planet/lineages/trade_flow.py::DROVE_GOODS", "planet/lineages/trade_flow.py::_Frame.cost", "run 0141d1", "run 3e0eb4", "run 07c755", "Villehardouin, Treaty of Venice 1201 (Fordham sourcebook)", "Yule, The Book of Ser Marco Polo vol. 2 pp. 404-405 (Wassaf)"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: lane 226 made herds and horses walk. On land they move as droves, at a quarter of a pack animal's cost per km, sourced
from the Texas cattle drives (step4c.md). They no longer take river boats. Horses' median fell to 2,308 / 1,284 / 1,549 km (main
d8152d53: 2,814 / 1,717 / 1,561). But about half of the horse flows still run mainly by sea (0.42-0.49), and the far tenth is
~4,100-4,300 km. The sourced sea case is the Gulf to Ma'bar, ~3,000-3,500 km (Wassaf).

Why it is still open: no fetched source gives a horse ship's freight per head against cargo freight. Lane 226 found:
- the Treaty of Venice of 1201: "four marks per horse and two marks per man" with nine months' food, but no horse value to set that
  against;
- transports of "8 to 20 horses" (taride 20-30), but no cargo tonnage to compare;
- Wassaf: the treasury paid for horses that died, but gives no rate.

A test factor of 3 on sea freight for herds moved horses' far tenth on 3e0eb4 only from 3,598 to 3,285 km, because at sea the hands
(HAND_KM), not the freight, set the reach.

What to try: a sourced per-voyage loss for live animals (deaths at sea as a share of the herd), charged where they are loaded, or a
horse ship's fare against a horse's price from one source and era. Pryor 1982 (Mariner's Mirror 68) and the 19th-century Australian
and New Zealand horse shipments to India are the leads; fetch them. Check horses' median and far tenth against step4b.md section 2.

- [ ] a sourced sea cost (loss or fare against value) for live animals
- [ ] horses' far tenth within ~3,000-3,500 km by sea on the three runs; land-nudge steadiness about 0.75 or above

## Updates
- 2026-11-08: Coordinator 11-08: milestone later/low; needs a sourced horse-ship cost first.
- 2026-11-08: Created from inbox draft draft-trade-herds-walk-ships-dear.md (found by lane 225).
