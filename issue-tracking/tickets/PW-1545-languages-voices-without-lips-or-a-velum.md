---
id: PW-1545
title: "Languages: voices without lips or a velum lose the sound changes that would undo their dear substitutes (exits barred by the needs filter)"
type: task
status: todo
parent: PW-767
milestone: later
subsystem: culture
effort: m
impact: med
found_by: lang-dark (dark l and y lane)
blocked_by: []
relates: []
refs: ["planet/language/rules.py::catalogue", "planet/language/rules.py::cost_factor", planet/language/data/sound_changes.tsv, planet/language/data/voice_profiles.toml, "docs/review/language/calibration.md#dark-l-and-y-2026-11-08-lang-dark"]
created: 2026-11-08
updated: 2026-11-08
---

## Description
In plain words: each sound change lists the parts of the mouth it needs (lips, velum, tongue root ...), and a people
whose mouth lacks one never gets that change. That is right for changes that *make* a sound with the missing part, but
the same filter also removes changes that *get rid of* such a sound. Lipless peoples (kobolds, dragonborn, lizardfolk,
tortles, aarakocra, kenku) still have rounded vowels, w, labials and nasals as costly stand-ins (their proto-inventories
are drawn with those costs), yet they cannot lose them by the usual routes. The dark-l lane fixed the two rows behind
the ɫ and y surplus (S074 y > i and S212 ɫ > w now need only the tongue body). The same pattern remains elsewhere.

Barred for lipless voices (kobold catalogue against the human one), among them exits from dear sounds: S067 kʷ > k,
S226 loss of labialization, S027/S028 w loss, S072 m > n / _#, S100 m > ∅ / _#, S065/S066 kʷ gʷ > p b, S194 pf > f,
S196 v > b. Barred for voices without a velum (reptilian line): S141 denasalization, S145 full nasal loss,
nasal.nasal_loss, S081a/b mb nd > mm nn, S084a/b prenasal stops lose the nasal. None of these is over the overused
check today, but nasal vowels, labialized series and prenasals in those lines can only leave by deletion or folding.

What misleads if never done: non-human lines accumulate whatever dear stand-ins a change brings in (as y and ɫ did:
half of all kobold, dragonborn, aarakocra and kenku lects before the fix), and the next new row that makes one will
show up as another overuse failure.
- [x] decide the rule: a row's needs should count only what its *output* requires (a change that removes a gesture needs
  nothing for it), or keep per-row needs and audit the exits above by hand
  *Done (lang-lane5):* `rules.exit_only`: a voice lacking lips, velum or teeth keeps a row whose change, over probe words,
  never adds a gesture of the missing part (counted as its make-cost keys per segment, `rules.ARTICULATOR_KEYS`) and
  takes one away somewhere, or never touches one (the j half of S125). Kept for lipless and velum-less voices: S067,
  S072, S100, S196, S226, S241, S027, S028, S040, S141, S145, S084a/b, S111, nasal.nasal_loss and others (23-32 rows);
  still barred: kʷ > p (S065/066, one gesture for another), p > ɸ, rounding and nasalization rows. Weight still by
  `cost_factor` (an exit from a dear sound gets up to x5).
- [ ] apply, re-run the species harness (scratchpad dark/sph.py: isolated protos per voice) and one full pass
  (harness gone; lane 5's full pass measures labial, nasal, rounded-vowel shares in lipless lines: calibration.md)

## Updates
- 2026-11-08: Created from inbox draft draft-language-missing-articulator-exits.md (found by lang-dark (dark l and y lane)).
