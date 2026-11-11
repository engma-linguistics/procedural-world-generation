# Languages: what's done, what's open

*Last updated 2026-11-11 (lane 17 merging; finish line filed). [Back to Languages](index.md).*

**Verdict (assessment 11-11, you agreed):** the machinery is essentially complete. What's left is a short finish line, about two weeks of lane time, then it's done and the long tail stays parked. [Assessment](https://claude.ai/artifact/Foz8PcmxBDSu1U3DUeLjXz).

**Finish line (epic PW-1736), roughly in order:**
1. Check every change on several worlds at once, not just a24559.
2. Fix the visible slips: garbled place names, random taboo words, "rr" everywhere, unnamed families, too few given names.
3. Stop borrowing core words like "I", "two" and "mother".
4. Fix sound systems that drift into odd shapes (no /m/, too few aspirates).
5. Bring isolating languages back, along with more gender and classifiers.
6. The names work: names that wear down over time, and feature names.
7. In the viewer: language isolates (your Basque), names on demand, map labels, the settlement view, and the rest of what's now only on one-off pages.

**Waiting on states and empires:** empires spreading their languages (which also means fewer, truer isolates), and state names.

---

## For agents

### Checks on a24559 (lane 16 rebuild, 2026-11-10)
| Check | Value | Target | Pass |
|---|---|---|---|
| proto inventories vs PHOIBLE | C 0.51 / V 0.54 in IQR | medians in PHOIBLE IQR, 35–75% inside | yes |
| sisters recognisable, distant not | siblings 0.5605, cross-family 0.0003 | > 0.5 / < 0.15 | yes |
| scholars' horizon | human 17.0 kyr (16.0 overall) | 6–10 kyr | **no** (accepted; swings 4.5–19 with seed) |
| language shift happened | 148 shifts, 91 living off descent | > 0 | yes |
| long generations change less | human 14.8 rules/kyr | long-lived < 1/3 | yes |
| hubs simpler, isolated richer | 15.5 vs 19.1 | hubs < isolated | yes |
| living inventory sizes vs PHOIBLE | — | medians/quartiles within tolerance | yes |
| living segment frequencies | top-20 overlap 16 | ≥ 12 | yes |
| overused segments | none (worst ɖ 2.4x) | none > 10% and > 3x | yes |
| typology agrees with live grams | 0 clashes | 0 | yes |
| loans follow WOLD borrowability | rho 0.48, pronoun loans 0.063 | rho ≥ 0.3, ≤ 0.08 | yes |
| areal signal | near − far 0.014 | ≥ 0.01 | yes |
| no impossible segments | 0 | 0 | yes |
| second voice only with a syrinx | 0 | 0 | yes |
| loans follow contact kind | — | elite prestige ≥ 1.5x | yes |
| doublets under elite rule | — | ≥ 0.2 | yes |
| word starts vs NorthEuraLex | l 6.5 / h 6.2 / i 4.8 / m 4.1% | p10–p90 per class | yes |

The **real-language benchmark** (PW-1641) is outside `checks.py`. Run `tools/language/real_inventory.py --check`. It seeds protos with real inventories or toolkits and measures what comes out. Its gaps are now-work, per the owner's 11-10 ruling.

### Open tickets
- **Finish line, epic PW-1736 (owner agreed 11-11):**
  - Stories:
    - PW-1737: multi-world, multi-seed check matrix, run concurrently, plus honest checks (horizon on the owner's band, wiring checks labelled, benchmark absolute bars, worker-count determinism, de1cc6 sisters dip).
    - PW-1738: core borrowing (`_renew_cell` order).
    - PW-1739: output slips.
    - PW-1740: living inventories (sinks without sources).
    - PW-1741: isolating languages back, gender, classifiers, Q, gram sources (owner ruling 11-11).
    - PW-1742: isolates in the viewer, relic first.
    - PW-1743: names on demand.
    - PW-1744: viewer catch-up (PW-1644 folded in).
  - Moved under it:
    - PW-1685 (PW-1547 merged in), PW-1656, PW-1655, PW-1639, PW-1632, PW-1633;
    - PW-1647 (step 2 failed in lane 17; next try a coda-loss conspiracy);
    - PW-1642.
  - Related: PW-1659 (settlement view, under PW-856).
  - Suggested lane order:
    1. PW-1737, which every later lane is judged on;
    2. PW-1739 + PW-1738;
    3. PW-1740;
    4. PW-1741;
    5. the names lane (PW-1685/1656);
    6. the viewer lanes (PW-1742/1743/1744/1655/1659).
- **Lane 17 (merging 11-11):** PW-1692 fixed by mechanism (re-fire wait ∝ 1/weight, RATE_SCALE 60, wave adoption × catalogue weight; S148/S042/S073 overrides removed). PW-1646 fixed on the benchmark (harmony.back 51% → 16% of daughters).
- **Blocked on polities (PW-1549):** PW-1652, PW-1643 and PW-1561 are one contact-inputs question (don't touch PW-1561 or `tongues.py`). Also blocked: PW-1651 and PW-1669.
- **`later` tail, parked on purpose:**
  - PW-1553, PW-1554, PW-1543 (now stress only), PW-1541, PW-1620 (PW-1605 merged in);
  - PW-1619, PW-1648, PW-1578 (re-measure after lane 17), PW-1550, PW-1601, PW-1614, PW-1723, PW-1668, PW-1722.
  - PW-767 is the umbrella.
- **Closed 11-11:** PW-1602 (done), PW-983 and PW-1567 (dropped).

To refresh: `grep -rl -E "language|lect" issue-tracking/tickets/ | xargs grep -L "^status: *done"`, or `board.py list --open` and filter on the titles.

### Settled (don't re-ask)
For the rulings, see [decisions.md](../decisions.md) and `language-lane-endgame` in memory. Highlights:
- **Horizon:** about 11 kyr or more is close enough.
- **Spelling guard:** it blocks slurs and rape/whore/slut, not plain swearing.
- **Synthesis:** heavier synthesis is approved.
- **The Common:** shown as Tolkien-style English, with the local names alongside.
- **Contact profiles:** D2.1 B and D2.2 B.
- **Trade numerals:** hundred and up for now.
- **Questions:** wh- part A done; the grid comes later.
- **Benchmark gaps:** these are now-work.
- **Machine:** at most half the machine.
- **Priority:** language is not the biggest need once realistic enough. No new realism lanes unless Daniel asks, but benchmark gaps count as asked.

### Known weak spots (assessment 11-11 has the full list)
- **Horizon:** the scholars' horizon is noisy across seeds.
- **Per-frame lexicon:** Lects keep no per-frame lexicon, which blocks the time-true names in PW-1685. Either store the snapshots per name or re-coin names at the founding frame.
- **Rule weights:** sound-change weights were hand-tuned per rule (`RULE_WEIGHT`) until PW-1692. Watch for regressions to the engine's middle (PW-1642).
- **Second test world:** de1cc6's sisters share has been 0.476–0.513 since lane 16, against 0.53–0.55 before. This is likely a regression, not noise (PW-1737).
- **Contact data:** contact kinds come from derived trade triggers. Nearly all contact counts as trade (PW-1643) until polities land.
