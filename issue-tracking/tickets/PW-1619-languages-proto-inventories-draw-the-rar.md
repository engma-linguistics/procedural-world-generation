---
id: PW-1619
title: "Languages: proto inventories draw the rare prenasals (ⁿt, ᵑk, ᵐp, ⁿz, ᶮɟ) at about twice PHOIBLE's rate"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: m
impact: low
found_by: language lane 10 (PW-1615)
blocked_by: []
relates: [PW-1615]
refs: ["planet/language/inventory.py::_pick_consonants", "planet/language/inventory.py::_series_factor", "planet/language/inventory.py::SERIES_FILL", planet/language/data/phoible_series.tsv, "run de1cc6", "run a24559", docs/review/language/calibration.md]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: a language with prenasalised stops (ᵐb ⁿd ᵑɡ) gets the right ones, but also picks up the rare voiceless
ones (ⁿt, ᵑk, ᵐp) about twice as often as real languages do. On the second world, de1cc6, one family that inherited
ⁿt and ᵑk spread to 22 living languages, and the two sounds tripped the "overused sounds" check (12.5% and 11% of
living languages; PHOIBLE 1.7% and 1.8%).

Lane 10 measured 3000-4000 human proto draws on main: a prenasal series in 13.9% of protos (PHOIBLE 12.9%), but
6.4 members where PHOIBLE has 5.7, and every tail member about 2x its conditional share (P(member | prenasal series):
ⁿt 0.26 against 0.13, ᵑk 0.31 / 0.14, ᵐp 0.24 / 0.12, ⁿz 0.30 / 0.14, ᶮɟ 0.27 / 0.12, ⁿdʒ 0.59 / 0.39); the three
voiced members are right (0.85-0.89). Whole draw: ⁿt 4.3%, ᵑk 4.6%, ᵐp 3.8% of protos (PHOIBLE 1.6-1.8%).

Tried and not enough: keying feature economy on prenasality too (ⁿt 4.3 -> 3.7%); odds weights f/(1-f) inside the series
fill, as the vowel draw does (4.3 -> 4.0%); both (3.2%). The excess comes from the free picks after the series fill,
where every member keeps its 1/share boost, so the series overshoots its mean size. A fix probably caps the boosted
free picks at the series' expected size (or drops the boost once the fill is done, which would also lower the
aspirated and ejective series, already under their PHOIBLE sizes: 3.8 vs 4.6 and 4.4 vs 5.9).

**What misleads if never done:** a world where one prenasal family spreads fails the overused-sounds check (de1cc6),
and a reader of any world sees voiceless prenasals about twice as often as real languages have them.
- [ ] P(ⁿt | prenasal series) within ~1.3x of PHOIBLE's 0.13 in a 3000-draw harness, other series' sizes not worse

## Updates
- 2026-11-09: Language wrap-up 11-09: realism polish, parked as later (owner: language good enough to move forward).
- 2026-11-09: Created from inbox draft draft-language-prenasal-tail.md (found by language lane 10 (PW-1615)).
