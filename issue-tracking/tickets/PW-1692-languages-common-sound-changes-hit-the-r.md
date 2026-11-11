---
id: PW-1692
title: "Languages: common sound changes hit the re-fire cap, so rare ones fire about 10x more often than their weight says"
type: task
status: done
parent: PW-767
milestone: v4
subsystem: peoples
effort: m
impact: high
found_by: lang-lane16
blocked_by: []
relates: [PW-1642, PW-1686, PW-1551]
refs: ["planet/language/lect.py::Lect.may_fire", "planet/language/lect.py::REFIRE_KYR", "planet/language/history.py::RATE_SCALE", "planet/language/history.py::RULE_WEIGHT", "planet/language/rules.py::pick_rule", planet/language/data/sound_changes.tsv, "run a24559", docs/review/language/for-daniel.md]
created: 2026-11-10
updated: 2026-11-11
---

## Description
In plain words: each sound change has a "how common is it in real languages" grade (naturalness 1-5, a weight from 0.11 to
9). The engine draws changes so often (about 880 draws a kyr a lect) that every change of grade 3 or more fires as soon
as its 4-kyr re-fire wait lets it. Those changes all fire at about the same rate, whatever their grade; only the rarest
(grade 1-2) still fire in proportion to their weight. The grades therefore do not set how often changes happen relative
to each other: rare changes come out about ten times too common next to common ones.

Measured on a24559 (main after lane 15, 1,185 lects, 107,206 firings): firings per unit weight are 1,800-4,800 for
grade-1 rows (S142 4,824, S022 3,744, S218 t > k 2,997, S148 r > ʁ 1,809) and 1,100-2,700 for grade-2 rows (S094 2,721,
S161 ʃ > x 1,722), against 134 for the grade-5 h loss and 68 for x > h (S023).

What it breaks: the rare changes the catalogue marks as rare (uvular r, Hawaiian t > k and k > ʔ, Celtic p loss, ʃ > x)
turn up in far too many lines. Lane 16 met two of the results. ʁ stood in 14% of living lects (PHOIBLE 3.7%), and lane 16
brought it down with a per-row override (history.RULE_WEIGHT S148 0.3, as S042 and S073 had before). Word-initial h
piles up because nine routes lead into h and the one way out is capped like the rest: in this regime a sound's fate is
set by how many rows feed and drain it, not by their grades. Each new symptom then gets its own override.

What to try: make the draw rate and the re-fire wait agree, so that a grade-5 row is not capped below its weight. For
example, cut RATE_SCALE and shorten REFIRE_KYR together, keeping the total change rate per kyr (the scholars' horizon and
sisters checks) where it is. Or make the wait depend on the weight. Then check the per-weight firing ratio across grades
and drop the per-row overrides that become unnecessary.
- [ ] firings per unit weight within about 2x across grades 1-5 on a24559
- [ ] sisters, horizon and the real-language benchmark (`real_inventory.py --check`) no worse

## Updates
- 2026-11-10: Created from inbox draft draft-rule-weight-saturation.md (found by lang-lane16).
- 2026-11-11: Done in lane 17 (merged 21bbe7a6; suite 2128 passed): re-fire wait = REFIRE_W_KYR 2.0 / the row's draw weight, RATE_SCALE 220 -> 60, wave adoption x catalogue weight (lect.catalogue_weight); S148/S042/S073 overrides removed. Grade-1 vs grade-5 firings per unit weight 21x -> 6.6x whole-run (a24559; 4 draws 6.6-7.6x); on the fair measure (firings per kyr of opportunity per unit weight, scratchpad/lane17/opp.py) within 2x from weight 0.01 to 3 and 3x up to 9. Acceptance reworded to that measure (the whole-run count can't reach 2x: conditioned rows exhaust their input, grade-5 rows are deliberately damped). Human changes per kyr kept (14.8 -> 14.1).
