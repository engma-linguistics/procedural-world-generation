# Languages: what's done, what's open

*Last updated 2026-11-11 (after lane 16; lane 17 running). [Back to Languages](index.md).*

**Solid:**
- Sound systems and how common each sound is, measured against real languages.
- Related languages that still look related.
- Borrowing that depends on who borrows from whom.
- Language shift.
- Grammar that wears down and renews.
- Names built from each language's own words.
- The Common in English.
- Audio.

**Still off, being worked on (lane 17):**
- Too many languages develop back vowel harmony.
- Too few languages are open-syllable.
- Some rare sound changes fire too often.

**Next (names):**
- Place names should be coined from the founders' words as they were at the founding, then wear down.
- Hills, capes, bays and other features need names.
- Map labels with an English/local toggle.
- A settlement view in the viewer.

**Waiting on states and empires:** empires spreading their language, and names for states.

**Parked as `later`:** a long tail of realism details (pidgins and creoles, stress that changes over time, richer allophony, and so on).

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
- **Lane 17, in progress:**
  - PW-1692: the re-fire cap saturates, which inflates rare rules; then drop the S148/S042/S073 overrides.
  - PW-1646: back vowel harmony.
  - PW-1647: CV share at 5% against 12% in WALS (step-2 script at `docs/review/language/lane16/ed_1647b.py`).
  - PW-1642: lineage tendencies, in progress.
- **Names lane, next:**
  - PW-1685: names from founding-era words, wearing down; cousins counted as heirs; page clarity.
  - PW-1656: feature names.
  - PW-1547: river, peak and old personal names should age through sound change.
- **Owner-facing, after that:**
  - PW-1655: map labels with an English/local toggle.
  - PW-1659: settlement view.
  - PW-1644: doublets shown in the viewer.
  - PW-1722: question-word grid (v5).
  - PW-1632: living capitals unnamed.
- **Blocked on polities (PW-1549):**
  - PW-1652: the Common by reach.
  - PW-1651: saints, conquest renaming, "New X".
  - PW-1669: a contact layer for place names (Danelaw -by).
  - PW-1561: two bilingualism models. Don't touch it or `tongues.py`.
- **v4 realism:**
  - PW-1668: "not" renewed as "not one" in about 40% of languages.
  - PW-1639: single-process pass outside `planet make`.
- **`later` tail:**
  - PW-1553: sound backlog.
  - PW-1554: contact backlog (pidgins, creoles, lingua francas, diglossia).
  - PW-1543: stress.
  - PW-1541: optional grammar stripped.
  - PW-1605 and PW-1620: case-system shares.
  - PW-1619: prenasals.
  - PW-1648: token priors.
  - PW-1578: long-lived rate.
  - PW-1550, PW-1567, PW-1601, PW-1614, PW-1633, PW-1643, PW-1723.
  - PW-983: first-principles phonology experiment.
  - PW-767: historical-linguistics umbrella.
- **Needs decision:** PW-1602, real-world book spellings. o.looks answered "real"; check whether the ticket can close.

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

### Known weak spots (coordinator's view)
- **Horizon:** the scholars' horizon is noisy across seeds.
- **Per-frame lexicon:** Lects keep no per-frame lexicon, which blocks the time-true names in PW-1685. Either store the snapshots per name or re-coin names at the founding frame.
- **Rule weights:** sound-change weights were hand-tuned per rule (`RULE_WEIGHT`) until PW-1692. Watch for regressions to the engine's middle (PW-1642).
- **Second test world:** de1cc6's sisters share dipped to 0.48–0.51 on lane 16's draws (accepted, but fragile).
- **Contact data:** contact kinds come from derived trade triggers. Nearly all contact counts as trade (PW-1643) until polities land.
