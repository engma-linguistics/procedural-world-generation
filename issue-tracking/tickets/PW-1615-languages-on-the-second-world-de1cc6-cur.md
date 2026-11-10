---
id: PW-1615
title: "Languages: on the second world (de1cc6) current code fails three checks a24559 passes: sisters 0.47, overused ⁿt/ᵑk, pronoun loans 0.10"
type: task
status: done
parent: PW-767
milestone: null
subsystem: culture
effort: m
impact: med
found_by: language lane 9 (PW-1566 second seed)
blocked_by: []
relates: [PW-1566, PW-1537]
refs: [planet/language/checks.py, "planet/language/checks.py::living_sizes", "planet/language/checks.py::sister_distant", "planet/language/checks.py::living_overuse", "planet/language/checks.py::borrowability", "planet/language/families.py::horizon_from", "planet/language/inventory.py::_pick_consonants", "planet/language/lexicon.py::loan_factor", "planet/language/lexicon.py::core_repair", "run de1cc6", "run a24559", docs/review/language/calibration.md, "planet/language/checks.py::SIBLING_MIN"]
created: 2026-11-09
updated: 2026-11-09
---

## Description
In plain words: the language checks are tuned on one world (a24559). Lane 9 ran the full language pass on the second
world, de1cc6, with main's code (41c71b12) and with lane 9's code, to confirm the raised-e fix. Both fail three checks
that a24559 passes, so these failures come from the world, not from lane 9:

| check | stored de1cc6 (11-08 code) | main 41c71b12 | lane 9 | pass mark |
| --- | --- | --- | --- | --- |
| sisters recognisable (strict) | 0.537 | 0.474 | 0.488 | > 0.5 |
| overused segments | ᵑk 20%, c̟ 14%, ʁ 12%, ⁿt 11% | ɖ 24%, ⁿt 10% | ⁿt 12.5%, ᵑk 11% | none over 10% and 3x PHOIBLE |
| WOLD pronoun loans | 0.095 | 0.103 | 0.092 | cap 0.08 |
| inventory sizes (human-voiced vowel median) | 7 | 7 | 6 (edge; 6.5 on a first lane-9 pass) | within 2 of 9 |

(The second-voice check also failed on lane 9's first de1cc6 pass, from stone giants who took up an aarakocra language;
fixed in lane 9: a sound a people cannot make at all is nativised in every word.)

**What misleads if never done:** a24559 is the only world the language model is checked on; de1cc6 has fewer living
lects (530 vs 616), and three checks fail there. Either the
model leans on a24559's history, or the checks' marks are tighter than one world's spread.

What I'd try: read which families carry ⁿt and ᵑk on de1cc6 (one family's founder effect would be fine; a rule weight
would not); count sister pairs per family for the strict share (a few big young families can pull it); for pronoun loans,
list the borrowing pairs (a shift-heavy history may borrow pronouns more). Then decide per check
whether it is a model fix or a world that is allowed to differ.
- [ ] a per-check reading of de1cc6 with the cause named
- [ ] each of the three either passes on de1cc6 or has a written reason it may differ there

## Updates
- 2026-11-09: Merged inbox draft draft-language-sisters-one-family.md ("Languages: the 'sisters recognisable' check is one family's story on de1cc6 (229 of 294 pairs); weigh families equally?", found by language lane 10 (PW-1615)).
  In plain words: one check asks whether languages that split up to 2,000 years ago still share enough recognisable
  words (over 0.5 on average). On the second world, de1cc6, it reads 0.49 and fails, but 229 of its 294 sister pairs come
  from one big family that spread by language shift to half-orcs, humans, halflings and others. So the number mostly
  describes that one family's history, not the model.
  
  Lane 10's reading (lane 9's pass output, same code on both worlds):
  
  | | a24559 | de1cc6 |
  | --- | --- | --- |
  | sister pairs; largest family's share | 165; 56 (34%) | 294; 229 (78%) |
  | strict share, pairs parted 0 / 0.5 / 1 / 1.5 / 2 kyr | .81 / .72 / .54 / .52 / .44 | .85 / .67 / .51 / .45 / .36 |
  | pairs parted 1.5-2 kyr | 90 of 165 | 180 of 294 |
  | de1cc6 re-weighted to a24559's age mix | | 0.53 |
  
  So most of the gap is the age mix (a burst of splits 1.5-2 kyr ago in one family); the rest is that family's
  shift-heavy history (its true cognate share at 2 kyr is 0.44 against a24559's 0.58).
  
  Options:
  - **A. Leave the check as is.** de1cc6 counts as an outlier world for this check (the multi-seed bar is ~70%).
  - **B. Weigh families equally:** the check's value is the mean over families of each family's mean sister share
    (the pair mean shown beside it). One family can no longer set the number; small families get noisier.
  - **C. Standardise the age mix:** average the per-bin shares (0, 0.5, 1, 1.5, 2 kyr) with fixed weights.
  
  Lean: A for now; B if a third world fails the same way. B and C change what the check measures, so they are a call for
  the owner, not a lane.
  
  **What misleads if never done:** a lane running a second seed reads a sisters failure as its own regression when it is
  one family's history.
  
  Coordinator call 2026-11-09: leave the check as is (test weighting, not an owner call); de1cc6 reasons recorded here.
- 2026-11-09: Status todo -> done. Lane 10 (lang-lane10): read per check on lane 9's de1cc6 output and on lane 10's own de1cc6 pass (scratch lane10/pass/de1cc6). All three are the world, not a model change: (1) sisters 0.488 / 0.478: 229 of 294 (lane 10: 207 of 266) sister pairs are one family, p234, spread by shift to half-orcs, humans, halflings and others; 180 of 294 pairs parted 1.5-2 kyr ago (a24559: 90 of 165); per-age strict shares sit 0.04-0.08 under a24559's; re-weighted to a24559's age mix de1cc6 reads 0.53 (draft draft-language-sisters-one-family, needs-decision). (2) overused ⁿt/ᵑk (lane 10 also ⁿd 33.5%): founder effects of p94 (tabaxi proto, 21-22 living lects, 18-21 with ⁿt) and p234 (ⁿd in 59 of 85); without p94, ⁿt is 8.5% and ᵑk 7.5%; under them a real draw flaw, prenasal series tails at ~2x PHOIBLE in proto draws (ⁿt 4.3% of human protos vs 1.7%; draft draft-language-prenasal-tail). (3) pronoun loans 0.092 / 0.085: de1cc6 borrows more of everything (median lect loan share 0.37 vs 0.30; 26% of living lects are shift lects vs 16%); pronouns stay at WOLD's ratio to other meanings (pronoun/all-meaning loan share 0.23-0.25 vs WOLD 0.21). For PW-1568: by route, a24559 lane 10 contact 152 / paradigm repair 67; de1cc6 contact 155 / repair 33 / koine ~10; shift lects borrow pronouns at 0.14-0.16 (ratio 0.30-0.34 to their other words) in both worlds, protos and buds at 0.19-0.22; the largest single route is a shift lect borrowing from its own true family (57-74 pronoun words per world). Inventory sizes fail at the edge (consonant tail 0 of 157 above PHOIBLE p95; lane 9 0 of 160); the horizon flips with 16-31 human lects (lane 9 6.5 kyr pass, lane 10 13 kyr fail).
- 2026-11-09: Created from inbox draft draft-language-de1cc6-checks.md (found by language lane 9 (PW-1566 second seed)).
